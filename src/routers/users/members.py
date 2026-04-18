"""Public member listing + single-member profile (no auth)."""

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

# ── Public endpoints ──


@router.get("/", response_model=PaginatedMembers)
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




