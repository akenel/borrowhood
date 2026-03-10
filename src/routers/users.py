"""Users API: members directory listing, single profile, favorites CRUD,
and account deletion.

Public reads for member discovery, auth-gated favorites and account management.
"""

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

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "static" / "uploads" / "avatars"
ALLOWED_AVATAR_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5 MB
from src.schemas.user import (
    FavoriteCreate,
    FavoriteOut,
    MemberCardOut,
    PaginatedMembers,
)

router = APIRouter(prefix="/api/v1/users", tags=["users"])

# Badge tier sort order: legend first, newcomer last
_BADGE_SORT = case(
    (BHUser.badge_tier == BadgeTier.LEGEND, 0),
    (BHUser.badge_tier == BadgeTier.PILLAR, 1),
    (BHUser.badge_tier == BadgeTier.TRUSTED, 2),
    (BHUser.badge_tier == BadgeTier.ACTIVE, 3),
    else_=4,
)


# ── Current user ──


@router.get("/me")
async def get_current_user(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Return the current authenticated user's basic info."""
    user = await get_user(db, token)
    return {
        "id": str(user.id),
        "display_name": user.display_name,
        "slug": user.slug,
        "avatar_url": user.avatar_url,
    }


# ── Avatar upload ──


@router.post("/me/avatar", status_code=200)
async def upload_avatar(
    file: UploadFile = File(...),
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Upload a profile avatar image."""
    if file.content_type not in ALLOWED_AVATAR_TYPES:
        raise HTTPException(status_code=400, detail="File must be JPEG, PNG, or WebP")

    user = await get_user(db, token)

    contents = await file.read()
    if len(contents) > MAX_AVATAR_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 5 MB)")

    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename and "." in file.filename else "jpg"
    if ext not in ("jpg", "jpeg", "png", "webp"):
        ext = "jpg"
    filename = f"{uuid_mod.uuid4().hex}.{ext}"
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    (UPLOAD_DIR / filename).write_bytes(contents)

    user.avatar_url = f"/static/uploads/avatars/{filename}"
    await db.commit()
    return {"status": "ok", "avatar_url": user.avatar_url}


# ── Favorites (auth-gated) ── must be BEFORE /{user_id} routes ──


@router.get("/me/favorites", response_model=List[FavoriteOut])
async def list_my_favorites(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List current user's favorites with nested member cards."""
    user = await get_user(db, token)
    result = await db.execute(
        select(BHUserFavorite)
        .options(
            selectinload(BHUserFavorite.favorite_user)
            .selectinload(BHUser.languages)
        )
        .where(BHUserFavorite.user_id == user.id)
        .order_by(BHUserFavorite.created_at.desc())
    )
    return result.scalars().all()


@router.get("/me/favorite-ids")
async def list_my_favorite_ids(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Return just the IDs of favorited users (for batch heart-state checks)."""
    user = await get_user(db, token)
    result = await db.execute(
        select(BHUserFavorite.favorite_user_id)
        .where(BHUserFavorite.user_id == user.id)
    )
    ids = [str(row[0]) for row in result.all()]
    return {"ids": ids}


# ── Account deletion ── must be BEFORE /{user_id} routes ──

# Rental statuses that indicate an active obligation
_ACTIVE_RENTAL_STATUSES = [
    RentalStatus.PENDING,
    RentalStatus.APPROVED,
    RentalStatus.PICKED_UP,
    RentalStatus.RETURNED,
    RentalStatus.DISPUTED,
]


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

    # ── All clear -- soft-delete ──

    old_status = user.account_status.value if user.account_status else None
    user.deleted_at = datetime.now(timezone.utc)
    user.account_status = AccountStatus.DEACTIVATED
    user.telegram_chat_id = None
    user.notify_telegram = False

    # Pause all active listings owned by user
    active_listings = await db.execute(
        select(BHListing)
        .join(BHItem, BHListing.item_id == BHItem.id)
        .where(BHItem.owner_id == user.id)
        .where(BHListing.status == ListingStatus.ACTIVE)
    )
    for listing in active_listings.scalars().all():
        listing.status = ListingStatus.PAUSED

    # Clean up pending Telegram link codes
    pending_links = await db.execute(
        select(BHTelegramLink).where(BHTelegramLink.user_id == user.id)
    )
    for link in pending_links.scalars().all():
        await db.delete(link)

    # Audit trail
    db.add(BHAuditLog(
        user_id=user.id,
        action="account_deleted",
        entity_type="user",
        entity_id=user.id,
        old_value=json.dumps({"account_status": old_status}),
        new_value=json.dumps({"account_status": "deactivated"}),
    ))

    await db.commit()

    # Clear the httponly session cookie so the user is logged out
    response = JSONResponse(content={"status": "deleted"})
    response.delete_cookie("bh_session")
    return response


# ── Public endpoints ──


@router.get("", response_model=PaginatedMembers)
async def list_members(
    q: Optional[str] = None,
    city: Optional[str] = None,
    badge_tier: Optional[str] = None,
    workshop_type: Optional[str] = None,
    near_lat: Optional[float] = Query(None, ge=-90, le=90),
    near_lng: Optional[float] = Query(None, ge=-180, le=180),
    radius_km: float = Query(25.0, ge=1, le=500),
    sort: str = Query("newest", pattern="^(newest|name_asc|badge_tier|closest)$"),
    limit: int = Query(12, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List/search community members. Public endpoint.

    Proximity search: pass near_lat + near_lng to filter by distance.
    Use sort=closest to order by distance (requires near_lat/near_lng).
    """
    query = (
        select(BHUser)
        .options(selectinload(BHUser.languages))
        .where(BHUser.deleted_at.is_(None))
    )

    if q:
        search_term = f"%{q}%"
        query = query.where(
            BHUser.display_name.ilike(search_term)
            | BHUser.workshop_name.ilike(search_term)
            | BHUser.tagline.ilike(search_term)
        )
    if city:
        query = query.where(BHUser.city.ilike(f"%{city}%"))
    if badge_tier:
        query = query.where(BHUser.badge_tier == badge_tier)
    if workshop_type:
        query = query.where(BHUser.workshop_type == workshop_type)

    # Proximity: pre-filter to members who have coordinates
    use_proximity = near_lat is not None and near_lng is not None
    if use_proximity:
        query = query.where(BHUser.latitude.isnot(None), BHUser.longitude.isnot(None))

    # Sort (DB-level for non-proximity sorts)
    if sort == "newest" and not use_proximity:
        query = query.order_by(BHUser.created_at.desc())
    elif sort == "name_asc":
        query = query.order_by(BHUser.display_name.asc())
    elif sort == "badge_tier":
        query = query.order_by(_BADGE_SORT, BHUser.display_name.asc())

    # For proximity search, fetch more candidates for post-query filtering
    if use_proximity:
        result = await db.execute(query)
        all_candidates = list(result.scalars().unique().all())

        # Haversine distance filter (Python-side, same pattern as item search)
        members_with_dist = []
        for m in all_candidates:
            dist = haversine_km(
                near_lat, near_lng, m.latitude, m.longitude,
                alt2=m.altitude or 0.0,
            )
            if dist <= radius_km:
                members_with_dist.append((m, dist))

        if sort == "closest":
            members_with_dist.sort(key=lambda x: x[1])
        elif sort == "newest":
            members_with_dist.sort(key=lambda x: x[0].created_at, reverse=True)

        total = len(members_with_dist)
        page = members_with_dist[offset : offset + limit]
        members = [m for m, _ in page]
    else:
        # Total count before pagination
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query) or 0

        query = query.offset(offset).limit(limit)
        result = await db.execute(query)
        members = list(result.scalars().unique().all())

    return PaginatedMembers(
        items=members,
        total=total,
        limit=limit,
        offset=offset,
        has_more=(offset + len(members)) < total,
    )


@router.get("/{user_id}", response_model=MemberCardOut)
async def get_member(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a single member card by ID. Public endpoint."""
    result = await db.execute(
        select(BHUser)
        .options(selectinload(BHUser.languages))
        .where(BHUser.id == user_id)
        .where(BHUser.deleted_at.is_(None))
    )
    member = result.scalars().first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


# ── Favorite toggle on specific user ──


@router.post("/{user_id}/favorite", status_code=201)
async def add_favorite(
    user_id: UUID,
    data: FavoriteCreate = FavoriteCreate(),
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Add a user to favorites. Returns 409 if already favorited."""
    user = await get_user(db, token)
    if user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot favorite yourself")

    # Check target exists
    target = await db.scalar(
        select(BHUser.id).where(BHUser.id == user_id).where(BHUser.deleted_at.is_(None))
    )
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    # Check duplicate
    existing = await db.scalar(
        select(BHUserFavorite.id)
        .where(BHUserFavorite.user_id == user.id)
        .where(BHUserFavorite.favorite_user_id == user_id)
    )
    if existing:
        raise HTTPException(status_code=409, detail="Already favorited")

    fav = BHUserFavorite(
        user_id=user.id,
        favorite_user_id=user_id,
        note=data.note,
    )
    db.add(fav)
    await db.commit()
    return {"status": "added", "favorite_user_id": str(user_id)}


@router.delete("/{user_id}/favorite", status_code=200)
async def remove_favorite(
    user_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Remove a user from favorites."""
    user = await get_user(db, token)
    result = await db.execute(
        select(BHUserFavorite)
        .where(BHUserFavorite.user_id == user.id)
        .where(BHUserFavorite.favorite_user_id == user_id)
    )
    fav = result.scalars().first()
    if not fav:
        raise HTTPException(status_code=404, detail="Favorite not found")

    await db.delete(fav)
    await db.commit()
    return {"status": "removed", "favorite_user_id": str(user_id)}
