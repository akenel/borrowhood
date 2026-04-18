"""Media upload for posts and replies (photos + videos, 10MB max)."""

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

# ── Media Upload ──

@router.post("/posts/{post_id}/media", response_model=HelpMediaOut, status_code=status.HTTP_201_CREATED)
async def upload_post_media(
    post_id: UUID,
    file: UploadFile = File(...),
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Upload a photo or video (max 10MB) to a help post. Author only."""
    user = await get_user(db, token)

    # Verify post exists and user is author
    result = await db.execute(
        select(BHHelpPost).where(BHHelpPost.id == post_id, BHHelpPost.deleted_at.is_(None))
    )
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != user.id:
        raise HTTPException(status_code=403, detail="Only the author can upload media")

    media = await _save_media(file, user.id, db, post_id=post_id)
    return media




@router.post("/replies/{reply_id}/media", response_model=HelpMediaOut, status_code=status.HTTP_201_CREATED)
async def upload_reply_media(
    reply_id: UUID,
    file: UploadFile = File(...),
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Upload a photo or video (max 10MB) to a reply. Author only."""
    user = await get_user(db, token)

    # Verify reply exists and user is author
    result = await db.execute(
        select(BHHelpReply).where(BHHelpReply.id == reply_id, BHHelpReply.deleted_at.is_(None))
    )
    reply = result.scalars().first()
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")
    if reply.author_id != user.id:
        raise HTTPException(status_code=403, detail="Only the author can upload media")

    media = await _save_media(file, user.id, db, reply_id=reply_id)
    return media


@router.delete("/media/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media(
    media_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Delete a media attachment. Author only."""
    user = await get_user(db, token)
    result = await db.execute(
        select(BHHelpMedia).where(BHHelpMedia.id == media_id)
    )
    media = result.scalars().first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    if media.uploader_id != user.id:
        raise HTTPException(status_code=403, detail="Only the uploader can delete media")
    # Delete file from disk
    filepath = Path(media.url.lstrip("/"))
    if filepath.exists():
        filepath.unlink()
    await db.delete(media)
    await db.commit()


async def _save_media(
    file: UploadFile,
    uploader_id,
    db: AsyncSession,
    post_id: UUID = None,
    reply_id: UUID = None,
) -> BHHelpMedia:
    """Validate, save to disk, create DB record."""
    if file.content_type not in ALLOWED_MEDIA_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File must be an image (JPEG/PNG/WebP/GIF) or video (MP4/WebM/MOV). Got: {file.content_type}"
        )

    contents = await file.read()
    if len(contents) > MAX_MEDIA_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 10 MB)")

    # Determine type
    media_type = HelpMediaType.VIDEO if file.content_type in ALLOWED_IMAGE_TYPES.__class__() and file.content_type not in ALLOWED_IMAGE_TYPES else HelpMediaType.PHOTO
    if file.content_type.startswith("video/"):
        media_type = HelpMediaType.VIDEO
    else:
        media_type = HelpMediaType.PHOTO

    # Save to disk
    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename and "." in file.filename else "bin"
    safe_exts = {"jpg", "jpeg", "png", "webp", "gif", "mp4", "webm", "mov"}
    if ext not in safe_exts:
        ext = "bin"
    filename = f"{uuid_mod.uuid4().hex}.{ext}"
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filepath = UPLOAD_DIR / filename
    filepath.write_bytes(contents)

    media = BHHelpMedia(
        post_id=post_id,
        reply_id=reply_id,
        uploader_id=uploader_id,
        media_type=media_type,
        url=f"/static/uploads/helpboard/{filename}",
        filename=file.filename or filename,
        file_size=len(contents),
        content_type=file.content_type,
        alt_text=None,
        sort_order=0,
    )
    db.add(media)
    await db.commit()
    await db.refresh(media)
    return media



