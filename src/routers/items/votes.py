"""Item upvotes (BL-71)."""

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

# ── Item upvotes (BL-71) ──


@router.get("/by-slug/{slug}/vote", status_code=200)
async def get_vote_status(
    slug: str,
    token: Optional[dict] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db),
):
    """Get vote count and whether current user voted."""
    from src.models.item import BHItemVote

    result = await db.execute(
        select(BHItem).where(BHItem.slug == slug).where(BHItem.deleted_at.is_(None))
    )
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    from sqlalchemy import func
    count = await db.scalar(
        select(func.count()).select_from(BHItemVote).where(BHItemVote.item_id == item.id)
    ) or 0

    voted = False
    if token:
        user = await get_user(db, token)
        existing = await db.execute(
            select(BHItemVote)
            .where(BHItemVote.user_id == user.id)
            .where(BHItemVote.item_id == item.id)
        )
        voted = existing.scalars().first() is not None

    return {"voted": voted, "count": count}


@router.post("/by-slug/{slug}/vote", status_code=200)
async def toggle_vote(
    slug: str,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Toggle upvote on an item. Returns new vote count and whether user voted."""
    from src.models.item import BHItemVote

    user = await get_user(db, token)
    result = await db.execute(
        select(BHItem).where(BHItem.slug == slug).where(BHItem.deleted_at.is_(None))
    )
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Check for existing vote
    result = await db.execute(
        select(BHItemVote)
        .where(BHItemVote.user_id == user.id)
        .where(BHItemVote.item_id == item.id)
    )
    existing = result.scalars().first()

    if existing:
        await db.delete(existing)
        voted = False
    else:
        vote = BHItemVote(user_id=user.id, item_id=item.id)
        db.add(vote)
        voted = True

    await db.flush()

    # Get total count
    from sqlalchemy import func
    count = await db.scalar(
        select(func.count()).select_from(BHItemVote).where(BHItemVote.item_id == item.id)
    ) or 0

    await db.commit()
    return {"voted": voted, "count": count}


