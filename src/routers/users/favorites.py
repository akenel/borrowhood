"""Favorites CRUD (auth-gated). Register BEFORE /{user_id} routes."""

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




