"""Current user endpoints: /me, profile update, social links, avatar, banner, WhatsApp."""

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
        "tagline": user.tagline or "",
        "bio": user.bio or "",
        "city": user.city or "",
        "state_region": user.state_region or "",
        "postal_code": user.postal_code or "",
        "address_line": user.address_line or "",
        "country_code": user.country_code or "",
        "latitude": user.latitude,
        "longitude": user.longitude,
        "workshop_name": user.workshop_name or "",
        "workshop_type": user.workshop_type.value if user.workshop_type else "",
        "whatsapp_number": user.whatsapp_number or "",
        "accepted_payments": user.accepted_payments or "",
        "seller_type": user.seller_type or "personal",
        "business_name": user.business_name or "",
        "vat_number": user.vat_number or "",
        "offers_delivery": user.offers_delivery,
        "offers_pickup": user.offers_pickup,
        "offers_training": user.offers_training,
        "offers_custom_orders": user.offers_custom_orders,
        "offers_repair": user.offers_repair,
        "notify_email": user.notify_email,
        "notify_telegram": user.notify_telegram,
        "featured_video_url": user.featured_video_url or "",
    }


# ── Profile update ──


@router.patch("/me", status_code=200)
async def update_me(
    request: Request,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Update current user profile fields."""
    user = await get_user(db, token)
    data = await request.json()

    # Allowed fields
    allowed = {
        "display_name", "tagline", "bio",
        "city", "state_region", "postal_code", "address_line", "country_code",
        "workshop_name", "workshop_type",
        "latitude", "longitude",
        "seller_type", "business_name", "vat_number",
        "accepted_payments",
        "offers_delivery", "offers_pickup", "offers_training",
        "offers_custom_orders", "offers_repair",
        "notify_telegram", "notify_email",
        "featured_video_url",
    }

    # Fields backed by Postgres enums -- must convert string to enum or None
    from src.models.user import WorkshopType
    enum_map = {
        "workshop_type": WorkshopType,
        "seller_type": None,  # handled below
    }

    # Validate featured_video_url -- only accept known providers
    if "featured_video_url" in data:
        raw = data.get("featured_video_url")
        if raw in (None, ""):
            data["featured_video_url"] = None
        else:
            from src.services.video_embed import is_supported_video_url
            if not is_supported_video_url(raw):
                raise HTTPException(
                    status_code=400,
                    detail="Video URL must be from YouTube, Vimeo, or TikTok",
                )

    for field, value in data.items():
        if field in allowed:
            if field in enum_map:
                if not value or value == "":
                    value = None
                elif enum_map[field]:
                    try:
                        value = enum_map[field](value)
                    except ValueError:
                        # Try uppercase (DB enum is uppercase)
                        try:
                            value = enum_map[field](value.upper())
                        except (ValueError, AttributeError):
                            value = None
            setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return {"status": "ok"}


# ── Social Links ──

from src.models.user import BHUserSocialLink

ALLOWED_PLATFORMS = {
    "instagram", "linkedin", "twitter", "tiktok", "youtube",
    "facebook", "github", "website", "telegram", "whatsapp",
}


@router.get("/me/social-links")
async def get_social_links(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's social links."""
    user = await get_user(db, token)
    result = await db.execute(
        select(BHUserSocialLink).where(BHUserSocialLink.user_id == user.id)
    )
    links = result.scalars().all()
    return [{"platform": l.platform, "url": l.url, "label": l.label} for l in links]


@router.put("/me/social-links")
async def update_social_links(
    request: Request,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Replace all social links. Send array of {platform, url, label?}."""
    user = await get_user(db, token)
    data = await request.json()

    if not isinstance(data, list):
        raise HTTPException(status_code=400, detail="Expected array of links")
    if len(data) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 social links")

    # Delete existing
    existing = await db.execute(
        select(BHUserSocialLink).where(BHUserSocialLink.user_id == user.id)
    )
    for link in existing.scalars().all():
        await db.delete(link)

    # Add new
    for item in data:
        platform = (item.get("platform") or "").lower().strip()
        url = (item.get("url") or "").strip()
        if not platform or not url:
            continue
        if platform not in ALLOWED_PLATFORMS:
            continue
        # Basic URL validation
        if not url.startswith("http://") and not url.startswith("https://") and platform != "whatsapp" and platform != "telegram":
            url = "https://" + url
        db.add(BHUserSocialLink(
            user_id=user.id,
            platform=platform,
            url=url,
            label=item.get("label"),
        ))

    await db.commit()
    return {"status": "ok"}


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


# ── Banner upload ──


@router.post("/me/banner", status_code=200)
async def upload_banner(
    file: UploadFile = File(...),
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Upload a profile banner image."""
    if file.content_type not in ALLOWED_AVATAR_TYPES:
        raise HTTPException(status_code=400, detail="File must be JPEG, PNG, or WebP")

    user = await get_user(db, token)

    contents = await file.read()
    if len(contents) > MAX_BANNER_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 10 MB)")

    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename and "." in file.filename else "jpg"
    if ext not in ("jpg", "jpeg", "png", "webp"):
        ext = "jpg"
    filename = f"{uuid_mod.uuid4().hex}.{ext}"
    BANNER_DIR.mkdir(parents=True, exist_ok=True)
    (BANNER_DIR / filename).write_bytes(contents)

    user.banner_url = f"/static/uploads/banners/{filename}"
    await db.commit()
    return {"status": "ok", "banner_url": user.banner_url}


# ── WhatsApp number ──


@router.put("/me/whatsapp", status_code=200)
async def update_whatsapp(
    request: Request,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Save or clear the user's WhatsApp number."""
    data = await request.json()
    user = await get_user(db, token)
    raw = (data.get("whatsapp_number") or "").strip()
    # Basic sanitization: keep only digits, spaces, + and -
    if raw:
        import re
        cleaned = re.sub(r"[^\d\s+\-]", "", raw)
        user.whatsapp_number = cleaned if cleaned else None
    else:
        user.whatsapp_number = None
    await db.commit()
    return {"status": "ok", "whatsapp_number": user.whatsapp_number}




