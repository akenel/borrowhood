"""Account deletion + GDPR data export (Article 20)."""

import json
import uuid as uuid_mod
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy import case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.dependencies import get_current_user_token, get_user, require_auth
from src.models.audit import BHAuditLog
from src.models.deposit import BHDeposit, DepositStatus
from src.models.dispute import BHDispute, DisputeStatus
from src.models.item import BHItem
from src.models.listing import BHListing, ListingStatus
from src.models.rental import BHRental, RentalStatus
from src.models.quote import BHServiceQuote, QuoteStatus
from src.models.telegram import BHTelegramLink
from src.models.user import AccountStatus, BadgeTier, BHUser, BHUserFavorite, WorkshopType
from src.services.search import haversine_km
from src.schemas.user import (
    FavoriteCreate,
    FavoriteOut,
    MemberCardOut,
    PaginatedMembers,
)

from ._shared import UPLOAD_DIR, BANNER_DIR, ALLOWED_AVATAR_TYPES, MAX_AVATAR_SIZE, MAX_BANNER_SIZE, _BADGE_SORT

router = APIRouter()

# ── Account deletion ── must be BEFORE /{user_id} routes ──

# Rental statuses that indicate an active obligation
_ACTIVE_RENTAL_STATUSES = [
    RentalStatus.PENDING,
    RentalStatus.APPROVED,
    RentalStatus.PICKED_UP,
    RentalStatus.RETURNED,
    RentalStatus.DISPUTED,
]


@router.get("/me/delete-preview")
async def delete_preview(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Show the user exactly what they'll lose if they delete their account."""
    user = await get_user(db, token)

    # Count everything they have
    from src.models.user import BHUserPoints, BHUserSkill, BHUserSocialLink
    from src.models.helpboard import BHHelpPost, BHHelpReply
    from src.models.review import BHReview

    item_count = await db.scalar(
        select(func.count()).select_from(BHItem).where(BHItem.owner_id == user.id)
    ) or 0
    listing_count = await db.scalar(
        select(func.count()).select_from(BHListing)
        .where(BHListing.item_id.in_(select(BHItem.id).where(BHItem.owner_id == user.id)))
    ) or 0
    from src.models.message import BHMessage
    message_count = await db.scalar(
        select(func.count()).select_from(BHMessage)
        .where(or_(BHMessage.sender_id == user.id, BHMessage.recipient_id == user.id))
    ) or 0
    review_count = await db.scalar(
        select(func.count()).select_from(BHReview).where(BHReview.reviewer_id == user.id)
    ) or 0
    helppost_count = await db.scalar(
        select(func.count()).select_from(BHHelpPost).where(BHHelpPost.author_id == user.id)
    ) or 0
    skill_count = await db.scalar(
        select(func.count()).select_from(BHUserSkill).where(BHUserSkill.user_id == user.id)
    ) or 0

    pts_result = await db.execute(
        select(BHUserPoints).where(BHUserPoints.user_id == user.id)
    )
    pts = pts_result.scalar_one_or_none()

    return {
        "display_name": user.display_name or user.username,
        "badge_tier": user.badge_tier.value if user.badge_tier else "newcomer",
        "total_points": pts.total_points if pts else 0,
        "events_attended": pts.events_attended if pts else 0,
        "best_streak": pts.best_streak if pts else 0,
        "items": item_count,
        "listings": listing_count,
        "messages": message_count,
        "reviews": review_count,
        "help_posts": helppost_count,
        "skills": skill_count,
        "member_since": user.created_at.strftime("%B %Y") if user.created_at else "unknown",
    }


@router.delete("/me", status_code=200)
async def delete_my_account(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete the current user's account.

    Blocked if user has active rentals (as renter or owner), held deposits,
    or open disputes. Sets deleted_at, deactivates account, pauses listings,
    clears Telegram link.
    """
    user = await get_user(db, token)
    blockers = []

    # Check 1: active rentals as renter
    renter_count = await db.scalar(
        select(func.count())
        .select_from(BHRental)
        .where(BHRental.renter_id == user.id)
        .where(BHRental.status.in_(_ACTIVE_RENTAL_STATUSES))
    )
    if renter_count:
        blockers.append(f"{renter_count} active rental(s) as renter")

    # Check 2: active rentals as item owner (rental -> listing -> item -> owner)
    owner_count = await db.scalar(
        select(func.count())
        .select_from(BHRental)
        .join(BHListing, BHRental.listing_id == BHListing.id)
        .join(BHItem, BHListing.item_id == BHItem.id)
        .where(BHItem.owner_id == user.id)
        .where(BHRental.status.in_(_ACTIVE_RENTAL_STATUSES))
    )
    if owner_count:
        blockers.append(f"{owner_count} active rental(s) as item owner")

    # Check 3: held deposits (payer or recipient)
    deposit_count = await db.scalar(
        select(func.count())
        .select_from(BHDeposit)
        .where(or_(BHDeposit.payer_id == user.id, BHDeposit.recipient_id == user.id))
        .where(BHDeposit.status == DepositStatus.HELD)
    )
    if deposit_count:
        blockers.append(f"{deposit_count} held deposit(s)")

    # Check 4: open disputes
    dispute_count = await db.scalar(
        select(func.count())
        .select_from(BHDispute)
        .where(BHDispute.filed_by_id == user.id)
        .where(BHDispute.status.in_([DisputeStatus.FILED, DisputeStatus.UNDER_REVIEW]))
    )
    if dispute_count:
        blockers.append(f"{dispute_count} open dispute(s)")

    # Check 5: active service quotes (as customer or provider)
    _active_quote_statuses = [
        QuoteStatus.REQUESTED, QuoteStatus.QUOTED,
        QuoteStatus.ACCEPTED, QuoteStatus.IN_PROGRESS,
    ]
    quote_count = await db.scalar(
        select(func.count())
        .select_from(BHServiceQuote)
        .where(or_(
            BHServiceQuote.customer_id == user.id,
            BHServiceQuote.provider_id == user.id,
        ))
        .where(BHServiceQuote.status.in_(_active_quote_statuses))
    )
    if quote_count:
        blockers.append(f"{quote_count} active service quote(s)")

    if blockers:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete account: {'; '.join(blockers)}. "
            "Resolve these before deleting your account.",
        )

    # ── All clear -- full delete (GDPR compliant) ──

    old_status = user.account_status.value if user.account_status else None
    uid = user.id
    keycloak_id = user.keycloak_id

    # Step 1: Delete from Keycloak so email can be re-used
    try:
        import httpx
        from src.config import settings
        kc_base = settings.kc_url.replace("https://", "http://keycloak:8080").split("/realms")[0] if "keycloak" not in settings.kc_url else settings.kc_url
        # Get admin token
        async with httpx.AsyncClient() as client:
            token_resp = await client.post(
                "http://keycloak:8080/realms/master/protocol/openid-connect/token",
                data={"grant_type": "password", "client_id": "admin-cli",
                      "username": "helix_user", "password": "helix_pass"},
            )
            if token_resp.status_code == 200:
                admin_token = token_resp.json()["access_token"]
                # Find KC user by keycloak_id
                if keycloak_id:
                    await client.delete(
                        f"http://keycloak:8080/admin/realms/borrowhood/users/{keycloak_id}",
                        headers={"Authorization": f"Bearer {admin_token}"},
                    )
    except Exception:
        pass  # Don't block deletion if KC cleanup fails

    # Step 2: Clean up all foreign key references
    from sqlalchemy import text as sa_text
    cleanup_tables = [
        "DELETE FROM bh_event_rsvp WHERE user_id = :uid",
        "DELETE FROM bh_achievement WHERE user_id = :uid",
        "DELETE FROM bh_saved_search WHERE user_id = :uid",
        "DELETE FROM bh_item_vote WHERE user_id = :uid",
        "DELETE FROM bh_help_upvote WHERE user_id = :uid",
        # Delete everything ON the user's help posts (other users' replies, media, upvotes)
        "DELETE FROM bh_help_upvote WHERE post_id IN (SELECT id FROM bh_help_post WHERE author_id = :uid)",
        "DELETE FROM bh_help_media WHERE reply_id IN (SELECT id FROM bh_help_reply WHERE post_id IN (SELECT id FROM bh_help_post WHERE author_id = :uid))",
        "DELETE FROM bh_help_media WHERE post_id IN (SELECT id FROM bh_help_post WHERE author_id = :uid)",
        "DELETE FROM bh_help_reply WHERE post_id IN (SELECT id FROM bh_help_post WHERE author_id = :uid)",
        # Delete user's own replies and media on other posts
        "DELETE FROM bh_help_media WHERE uploader_id = :uid",
        "DELETE FROM bh_help_reply WHERE author_id = :uid",
        "DELETE FROM bh_listing_qa WHERE asker_id = :uid OR answered_by_id = :uid",
        "DELETE FROM bh_message WHERE sender_id = :uid OR recipient_id = :uid",
        "UPDATE bh_help_post SET resolved_by_id = NULL WHERE resolved_by_id = :uid",
        "DELETE FROM bh_help_post WHERE author_id = :uid",
        "DELETE FROM bh_skill_verification WHERE verifier_id = :uid",
        "DELETE FROM bh_mentorship WHERE mentor_id = :uid OR apprentice_id = :uid",
        "DELETE FROM bh_delivery_event WHERE actor_id = :uid",
        "DELETE FROM bh_delivery_tracking WHERE delivery_person_id = :uid",
        "DELETE FROM bh_insurance_claim WHERE claimant_id = :uid",
        "DELETE FROM bh_insurance_policy WHERE holder_id = :uid",
        "DELETE FROM bh_community_membership WHERE user_id = :uid",
        "DELETE FROM bh_item_favorite WHERE user_id = :uid",
        "DELETE FROM bh_service_quote WHERE customer_id = :uid OR provider_id = :uid",
        "DELETE FROM bh_telegram_link WHERE user_id = :uid",
        "DELETE FROM bh_payment WHERE payer_id = :uid OR payee_id = :uid",
        "UPDATE bh_dispute SET resolved_by_id = NULL WHERE resolved_by_id = :uid",
        "UPDATE bh_dispute SET response_by_id = NULL WHERE response_by_id = :uid",
        "DELETE FROM bh_dispute WHERE filed_by_id = :uid",
        "DELETE FROM bh_deposit WHERE payer_id = :uid OR recipient_id = :uid",
        "DELETE FROM bh_review_vote WHERE user_id = :uid",
        "DELETE FROM bh_review WHERE reviewer_id = :uid",
        "UPDATE bh_review SET reviewee_id = NULL WHERE reviewee_id = :uid",
        "DELETE FROM bh_bid WHERE bidder_id = :uid",
        "DELETE FROM bh_rental WHERE renter_id = :uid",
        "DELETE FROM bh_badge WHERE user_id = :uid",
        "DELETE FROM bh_notification WHERE user_id = :uid",
        "DELETE FROM bh_notification_pref WHERE user_id = :uid",
        "DELETE FROM bh_user_points WHERE user_id = :uid",
        "DELETE FROM bh_user_social_link WHERE user_id = :uid",
        "DELETE FROM bh_user_skill WHERE user_id = :uid",
        "DELETE FROM bh_user_language WHERE user_id = :uid",
        "DELETE FROM bh_user_favorite WHERE user_id = :uid OR favorite_user_id = :uid",
        "DELETE FROM bh_report WHERE reporter_id = :uid",
        "DELETE FROM bh_workshop_member WHERE workshop_owner_id = :uid OR member_id = :uid",
        # Clean up everything ON the user's items/listings (other users' bids, rentals, reviews, etc.)
        "DELETE FROM bh_event_rsvp WHERE listing_id IN (SELECT id FROM bh_listing WHERE item_id IN (SELECT id FROM bh_item WHERE owner_id = :uid))",
        "DELETE FROM bh_bid WHERE listing_id IN (SELECT id FROM bh_listing WHERE item_id IN (SELECT id FROM bh_item WHERE owner_id = :uid))",
        "DELETE FROM bh_rental WHERE listing_id IN (SELECT id FROM bh_listing WHERE item_id IN (SELECT id FROM bh_item WHERE owner_id = :uid))",
        "DELETE FROM bh_listing_qa WHERE item_id IN (SELECT id FROM bh_item WHERE owner_id = :uid)",
        "DELETE FROM bh_service_quote WHERE listing_id IN (SELECT id FROM bh_listing WHERE item_id IN (SELECT id FROM bh_item WHERE owner_id = :uid))",
        "DELETE FROM bh_item_vote WHERE item_id IN (SELECT id FROM bh_item WHERE owner_id = :uid)",
        "DELETE FROM bh_item_favorite WHERE item_id IN (SELECT id FROM bh_item WHERE owner_id = :uid)",
        "UPDATE bh_review SET item_id = NULL WHERE item_id IN (SELECT id FROM bh_item WHERE owner_id = :uid)",
        "DELETE FROM bh_item_media WHERE item_id IN (SELECT id FROM bh_item WHERE owner_id = :uid)",
        "DELETE FROM bh_listing WHERE item_id IN (SELECT id FROM bh_item WHERE owner_id = :uid)",
        "DELETE FROM bh_item WHERE owner_id = :uid",
        "DELETE FROM bh_community WHERE owner_id = :uid",
    ]
    for sql in cleanup_tables:
        try:
            async with db.begin_nested():
                await db.execute(sa_text(sql), {"uid": uid})
        except Exception:
            pass  # Savepoint rolled back -- table may not exist yet

    # Step 3: Audit trail before deletion
    db.add(BHAuditLog(
        user_id=uid,
        action="account_deleted",
        entity_type="user",
        entity_id=uid,
        old_value=json.dumps({"account_status": old_status}),
        new_value=json.dumps({"account_status": "deleted"}),
    ))

    # Step 4: Hard delete the user
    await db.execute(sa_text("DELETE FROM bh_user WHERE id = :uid"), {"uid": uid})

    await db.commit()

    # Clear the httponly session cookie so the user is logged out
    response = JSONResponse(content={"status": "deleted"})
    response.delete_cookie("bh_session")
    return response



# ── GDPR Data Export (Article 20) ──


@router.get("/me/export")
async def export_my_data(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Download all personal data as JSON. GDPR Article 20 -- right to data portability."""
    user = await get_user(db, token)

    # Profile
    profile = {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "display_name": user.display_name,
        "slug": user.slug,
        "tagline": user.tagline,
        "bio": user.bio,
        "city": user.city,
        "country_code": user.country_code,
        "workshop_name": user.workshop_name,
        "workshop_type": user.workshop_type.value if user.workshop_type else None,
        "seller_type": user.seller_type,
        "business_name": user.business_name,
        "vat_number": user.vat_number,
        "avatar_url": user.avatar_url,
        "banner_url": user.banner_url,
        "whatsapp_number": user.whatsapp_number,
        "accepted_payments": user.accepted_payments,
        "badge_tier": user.badge_tier.value if user.badge_tier else None,
        "trust_score": user.trust_score,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }

    # Items
    item_result = await db.execute(
        select(BHItem).where(BHItem.owner_id == user.id).where(BHItem.deleted_at.is_(None))
    )
    items = [
        {"id": str(i.id), "name": i.name, "slug": i.slug, "description": i.description,
         "category": i.category, "condition": i.condition, "created_at": i.created_at.isoformat() if i.created_at else None}
        for i in item_result.scalars().all()
    ]

    # Rentals (as buyer)
    from src.models.rental import BHRental
    rental_result = await db.execute(
        select(BHRental).where(BHRental.renter_id == user.id)
    )
    rentals = [
        {"id": str(r.id), "status": r.status.value, "renter_message": r.renter_message,
         "payment_method": r.payment_method_used,
         "created_at": r.created_at.isoformat() if r.created_at else None}
        for r in rental_result.scalars().all()
    ]

    # Messages (sent)
    from src.models.message import BHMessage
    msg_result = await db.execute(
        select(BHMessage).where(BHMessage.sender_id == user.id).where(BHMessage.deleted_at.is_(None))
    )
    messages = [
        {"id": str(m.id), "body": m.body, "message_type": m.message_type,
         "created_at": m.created_at.isoformat() if m.created_at else None}
        for m in msg_result.scalars().all()
    ]

    # Reviews (written)
    from src.models.review import BHReview
    review_result = await db.execute(
        select(BHReview).where(BHReview.reviewer_id == user.id)
    )
    reviews = [
        {"id": str(rv.id), "rating": rv.rating, "title": rv.title, "body": rv.body,
         "created_at": rv.created_at.isoformat() if rv.created_at else None}
        for rv in review_result.scalars().all()
    ]

    # Social links
    social_result = await db.execute(
        select(BHUserSocialLink).where(BHUserSocialLink.user_id == user.id)
    )
    social_links = [
        {"platform": s.platform, "url": s.url, "label": s.label}
        for s in social_result.scalars().all()
    ]

    export = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "platform": "LaPiazza.app",
        "profile": profile,
        "items_listed": items,
        "orders": rentals,
        "messages_sent": messages,
        "reviews_written": reviews,
        "social_links": social_links,
    }

    from fastapi.responses import JSONResponse
    return JSONResponse(
        content=export,
        headers={"Content-Disposition": "attachment; filename=lapiazza-my-data.json"},
    )




