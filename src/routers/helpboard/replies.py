"""Threaded replies on help posts (create, update, delete)."""

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

# ── Replies (threaded) ──

@router.get("/posts/{post_id}/replies")
async def list_replies(post_id: UUID, db: AsyncSession = Depends(get_db)):
    """List replies for a post as a threaded tree. Public endpoint."""
    result = await db.execute(
        select(BHHelpReply)
        .where(BHHelpReply.post_id == post_id, BHHelpReply.deleted_at.is_(None))
        .options(selectinload(BHHelpReply.author), selectinload(BHHelpReply.media))
        .order_by(BHHelpReply.created_at.asc())
    )
    flat = result.scalars().unique().all()
    return _build_reply_tree(flat)


@router.post("/posts/{post_id}/replies", status_code=status.HTTP_201_CREATED)
async def create_reply(
    post_id: UUID,
    data: HelpReplyCreate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Reply to a help post. Set parent_reply_id for threading."""
    user = await get_user(db, token)

    # Verify post exists
    post_result = await db.execute(
        select(BHHelpPost).where(BHHelpPost.id == post_id, BHHelpPost.deleted_at.is_(None))
    )
    post = post_result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Validate parent reply if threading
    if data.parent_reply_id:
        parent_result = await db.execute(
            select(BHHelpReply).where(
                BHHelpReply.id == data.parent_reply_id,
                BHHelpReply.post_id == post_id,
                BHHelpReply.deleted_at.is_(None),
            )
        )
        if not parent_result.scalars().first():
            raise HTTPException(status_code=400, detail="Parent reply not found in this post")

    reply = BHHelpReply(
        post_id=post_id,
        author_id=user.id,
        body=data.body,
        parent_reply_id=data.parent_reply_id,
    )
    db.add(reply)
    post.reply_count += 1
    await db.flush()

    # Notify the post author (unless replying to own post)
    if post.author_id != user.id:
        from src.models.notification import NotificationType
        from src.services.notify import create_notification
        await create_notification(
            db=db,
            user_id=post.author_id,
            notification_type=NotificationType.SYSTEM,
            title=f"{user.display_name} replied to your post: {post.title}",
            link="/helpboard",
            entity_type="helpboard",
            entity_id=post.id,
        )

    # If threading, also notify the parent reply author
    if data.parent_reply_id:
        parent_result = await db.execute(
            select(BHHelpReply).where(BHHelpReply.id == data.parent_reply_id)
        )
        parent_reply = parent_result.scalars().first()
        if parent_reply and parent_reply.author_id != user.id and parent_reply.author_id != post.author_id:
            from src.models.notification import NotificationType
            from src.services.notify import create_notification
            await create_notification(
                db=db,
                user_id=parent_reply.author_id,
                notification_type=NotificationType.SYSTEM,
                title=f"{user.display_name} replied to your comment on: {post.title}",
                link="/helpboard",
                entity_type="helpboard",
                entity_id=post.id,
            )

    await db.commit()

    # Reload with relationships
    result = await db.execute(
        select(BHHelpReply).where(BHHelpReply.id == reply.id)
        .options(selectinload(BHHelpReply.author), selectinload(BHHelpReply.media))
    )
    reply = result.scalars().first()
    return _enrich_reply(reply)




@router.patch("/replies/{reply_id}", response_model=HelpReplyOut)
async def update_reply(
    reply_id: UUID,
    data: HelpReplyUpdate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Edit a reply. Author only."""
    user = await get_user(db, token)
    result = await db.execute(
        select(BHHelpReply)
        .options(selectinload(BHHelpReply.author), selectinload(BHHelpReply.media))
        .where(BHHelpReply.id == reply_id, BHHelpReply.deleted_at.is_(None))
    )
    reply = result.scalars().first()
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")
    if reply.author_id != user.id:
        raise HTTPException(status_code=403, detail="Only the author can edit")
    reply.body = data.body
    await db.commit()
    await db.refresh(reply)
    return _enrich_reply(reply)


@router.delete("/replies/{reply_id}", status_code=204)
async def delete_reply(
    reply_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a reply. Author only."""
    user = await get_user(db, token)
    result = await db.execute(
        select(BHHelpReply).where(BHHelpReply.id == reply_id, BHHelpReply.deleted_at.is_(None))
    )
    reply = result.scalars().first()
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")
    if reply.author_id != user.id:
        raise HTTPException(status_code=403, detail="Only the author can delete")
    from datetime import datetime, timezone
    reply.deleted_at = datetime.now(timezone.utc)
    # Decrement reply count on post
    post_result = await db.execute(select(BHHelpPost).where(BHHelpPost.id == reply.post_id))
    post = post_result.scalars().first()
    if post and post.reply_count > 0:
        post.reply_count -= 1
    await db.commit()



