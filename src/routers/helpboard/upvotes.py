"""Upvote toggle on help posts."""

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

# ── Upvote ──

@router.post("/posts/{post_id}/upvote")
async def toggle_upvote(
    post_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Toggle upvote on a post. Upvote if not yet, remove if already upvoted."""
    user = await get_user(db, token)

    # Verify post exists
    post_result = await db.execute(
        select(BHHelpPost).where(BHHelpPost.id == post_id, BHHelpPost.deleted_at.is_(None))
    )
    post = post_result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Check existing upvote
    existing = await db.execute(
        select(BHHelpUpvote).where(
            BHHelpUpvote.post_id == post_id,
            BHHelpUpvote.user_id == user.id,
        )
    )
    vote = existing.scalars().first()

    if vote:
        await db.delete(vote)
        post.upvote_count = max(0, post.upvote_count - 1)
        action = "removed"
    else:
        db.add(BHHelpUpvote(post_id=post_id, user_id=user.id))
        post.upvote_count += 1
        action = "upvoted"

    await db.commit()
    return {"action": action, "upvote_count": post.upvote_count}



