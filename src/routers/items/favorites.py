"""Item favorites (heart/like)."""

import uuid as uuid_mod
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, File
from pydantic import BaseModel, Field
from slugify import slugify
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.dependencies import get_current_user_token, get_user, require_auth, require_badge_tier, user_throttle
from src.models.item import ATTRIBUTE_SCHEMAS, CATEGORY_GROUPS, BHItem, BHItemFavorite, BHItemMedia, MediaType, get_attribute_schema
from src.models.listing import BHListing, ListingStatus
from src.models.user import BHUser
from src.schemas.item import ItemCreate, ItemOut, ItemUpdate

from ._shared import (
    UPLOAD_DIR,
    ALLOWED_IMAGE_TYPES,
    ALLOWED_VIDEO_TYPES,
    ALLOWED_TYPES,
    MAX_IMAGE_SIZE,
    MAX_VIDEO_SIZE,
    _unique_slug,
)

router = APIRouter()

# ── Item Favorites ──


@router.get("/me/favorites", response_model=List[ItemOut])
async def list_my_item_favorites(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Return full item objects the current user has favorited."""
    user = await get_user(db, token)
    result = await db.execute(
        select(BHItem)
        .join(BHItemFavorite, BHItemFavorite.item_id == BHItem.id)
        .options(selectinload(BHItem.media))
        .where(BHItemFavorite.user_id == user.id)
        .where(BHItem.deleted_at.is_(None))
        .order_by(BHItemFavorite.created_at.desc())
    )
    return result.scalars().unique().all()


@router.get("/me/favorite-ids")
async def list_my_item_favorite_ids(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Return IDs of items the current user has favorited."""
    user = await get_user(db, token)
    result = await db.execute(
        select(BHItemFavorite.item_id).where(BHItemFavorite.user_id == user.id)
    )
    ids = [str(row[0]) for row in result.all()]
    return {"ids": ids}


@router.post("/{item_id}/favorite", status_code=201)
async def add_item_favorite(
    item_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Add an item to favorites."""
    user = await get_user(db, token)

    item = await db.scalar(
        select(BHItem.id).where(BHItem.id == item_id).where(BHItem.deleted_at.is_(None))
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    existing = await db.scalar(
        select(BHItemFavorite.id)
        .where(BHItemFavorite.user_id == user.id)
        .where(BHItemFavorite.item_id == item_id)
    )
    if existing:
        raise HTTPException(status_code=409, detail="Already favorited")

    fav = BHItemFavorite(user_id=user.id, item_id=item_id)
    db.add(fav)
    await db.commit()
    return {"status": "added", "item_id": str(item_id)}


@router.delete("/{item_id}/favorite", status_code=200)
async def remove_item_favorite(
    item_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Remove an item from favorites."""
    user = await get_user(db, token)
    result = await db.execute(
        select(BHItemFavorite)
        .where(BHItemFavorite.user_id == user.id)
        .where(BHItemFavorite.item_id == item_id)
    )
    fav = result.scalars().first()
    if not fav:
        raise HTTPException(status_code=404, detail="Not in favorites")
    await db.delete(fav)
    await db.commit()
    return {"status": "removed", "item_id": str(item_id)}



