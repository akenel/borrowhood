"""Summary endpoint + posts-by-item cross-link."""

import uuid as uuid_mod
from pathlib import Path
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, File, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.dependencies import get_current_user_token, get_user, require_auth

from src.models.helpboard import (
    ALLOWED_MEDIA_TYPES, ALLOWED_IMAGE_TYPES, MAX_MEDIA_SIZE,
    BHHelpPost, BHHelpReply, BHHelpMedia, BHHelpUpvote,
    HelpMediaType, HelpStatus, HelpType,
)
from src.models.item import BHItem
from src.models.user import BHUser
from src.schemas.helpboard import (
    HelpPostCreate, HelpPostOut, HelpPostUpdate, HelpMediaOut,
    HelpReplyCreate, HelpReplyOut, HelpReplyUpdate, PaginatedPosts, ResolvePost,
    HelpDraftRequest, HelpDraftResponse,
)

from ._shared import UPLOAD_DIR, _enrich_post, _enrich_reply, _build_reply_tree

router = APIRouter()

# ── Summary ──

@router.get("/summary")
async def helpboard_summary(db: AsyncSession = Depends(get_db)):
    """Summary stats for the help board."""
    total = await db.scalar(
        select(func.count()).select_from(BHHelpPost).where(BHHelpPost.deleted_at.is_(None))
    )
    open_count = await db.scalar(
        select(func.count()).select_from(BHHelpPost).where(
            BHHelpPost.deleted_at.is_(None), BHHelpPost.status == HelpStatus.OPEN
        )
    )
    needs = await db.scalar(
        select(func.count()).select_from(BHHelpPost).where(
            BHHelpPost.deleted_at.is_(None), BHHelpPost.help_type == HelpType.NEED
        )
    )
    offers = await db.scalar(
        select(func.count()).select_from(BHHelpPost).where(
            BHHelpPost.deleted_at.is_(None), BHHelpPost.help_type == HelpType.OFFER
        )
    )
    resolved = await db.scalar(
        select(func.count()).select_from(BHHelpPost).where(
            BHHelpPost.deleted_at.is_(None), BHHelpPost.status == HelpStatus.RESOLVED
        )
    )
    return {
        "total": total or 0,
        "open": open_count or 0,
        "needs": needs or 0,
        "offers": offers or 0,
        "resolved": resolved or 0,
    }


# ── Posts by item (for item detail cross-link) ──

@router.get("/items/{item_id}/posts")
async def posts_for_item(
    item_id: UUID,
    limit: int = Query(5, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Get help board posts tagged to a specific item. For item detail pages."""
    result = await db.execute(
        select(BHHelpPost)
        .where(BHHelpPost.item_id == item_id, BHHelpPost.deleted_at.is_(None))
        .options(*POST_EAGER)
        .order_by(BHHelpPost.created_at.desc())
        .limit(limit)
    )
    posts = result.scalars().unique().all()
    return [_enrich_post(p) for p in posts]


