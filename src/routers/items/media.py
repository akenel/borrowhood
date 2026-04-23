"""Item media: add/upload/delete/reorder."""

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

class MediaAdd(BaseModel):
    url: str = Field(..., max_length=500)
    alt_text: str = Field(default="Item photo", max_length=200)
    media_type: str = Field(default="photo", max_length=20)


class MediaOut(BaseModel):
    id: UUID
    url: str
    alt_text: str
    media_type: str

    class Config:
        from_attributes = True


@router.post("/{item_id}/media", response_model=MediaOut, status_code=201)
async def add_item_media(
    item_id: UUID,
    data: MediaAdd,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Add a media URL to an item. Only the owner can add media."""
    user = await get_user(db, token)

    result = await db.execute(
        select(BHItem)
        .where(BHItem.id == item_id)
        .where(BHItem.deleted_at.is_(None))
    )
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not your item")

    from src.models.item import MediaType
    max_order = await db.scalar(
        select(func.coalesce(func.max(BHItemMedia.sort_order), -1))
        .where(BHItemMedia.item_id == item.id)
    )
    next_order = (max_order if max_order is not None else -1) + 1
    media = BHItemMedia(
        item_id=item.id,
        url=data.url,
        alt_text=data.alt_text,
        media_type=MediaType(data.media_type) if data.media_type in [e.value for e in MediaType] else MediaType.PHOTO,
        sort_order=next_order,
    )
    db.add(media)
    await db.commit()
    await db.refresh(media)
    return media


@router.post("/{item_id}/upload", response_model=MediaOut, status_code=201)
async def upload_item_image(
    item_id: UUID,
    file: UploadFile = File(...),
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Upload an image or video file for an item. Only the owner can upload."""
    import logging
    _upload_log = logging.getLogger("upload")

    _upload_log.info("Upload attempt: content_type=%s filename=%s", file.content_type, file.filename)

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Supported: JPEG, PNG, WebP, GIF, MP4, WebM")

    is_video = file.content_type in ALLOWED_VIDEO_TYPES

    user = await get_user(db, token)

    result = await db.execute(
        select(BHItem)
        .where(BHItem.id == item_id)
        .where(BHItem.deleted_at.is_(None))
    )
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not your item")

    # Read and validate file size
    contents = await file.read()
    max_size = MAX_VIDEO_SIZE if is_video else MAX_IMAGE_SIZE
    size_label = "50 MB" if is_video else "10 MB"
    if len(contents) > max_size:
        raise HTTPException(status_code=400, detail=f"File too large (max {size_label})")

    # Save to disk
    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename and "." in file.filename else ("mp4" if is_video else "jpg")
    allowed_ext = ("jpg", "jpeg", "png", "webp", "gif", "mp4", "webm", "mov")
    if ext not in allowed_ext:
        ext = "mp4" if is_video else "jpg"
    filename = f"{uuid_mod.uuid4().hex}.{ext}"
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filepath = UPLOAD_DIR / filename
    filepath.write_bytes(contents)

    # Get next sort order (append after existing media)
    max_order = await db.scalar(
        select(func.coalesce(func.max(BHItemMedia.sort_order), -1))
        .where(BHItemMedia.item_id == item.id)
    )
    next_order = (max_order if max_order is not None else -1) + 1

    # Create media record
    media = BHItemMedia(
        item_id=item.id,
        url=f"/static/uploads/{filename}",
        alt_text=f"{item.name} {'video' if is_video else 'photo'}",
        media_type=MediaType.VIDEO if is_video else MediaType.PHOTO,
        sort_order=next_order,
    )
    db.add(media)
    try:
        await db.commit()
        await db.refresh(media)
        _upload_log.info("Upload success: id=%s type=%s", media.id, media.media_type)
        return media
    except Exception as e:
        _upload_log.error("Upload DB error: %s", e, exc_info=True)
        raise


@router.delete("/{item_id}/media/{media_id}", status_code=204)
async def delete_item_media(
    item_id: UUID,
    media_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Delete a media item. Only the owner can delete."""
    user = await get_user(db, token)

    result = await db.execute(
        select(BHItem).where(BHItem.id == item_id).where(BHItem.deleted_at.is_(None))
    )
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not your item")

    media_result = await db.execute(
        select(BHItemMedia).where(BHItemMedia.id == media_id).where(BHItemMedia.item_id == item_id)
    )
    media = media_result.scalars().first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    await db.delete(media)
    await db.commit()


@router.put("/{item_id}/media/reorder", status_code=200)
async def reorder_media(
    item_id: UUID,
    request: Request,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Reorder media. Send array of media IDs in desired order.
    First position (index 0) becomes the cover image.
    Videos cannot be in position 0.
    """
    user = await get_user(db, token)

    result = await db.execute(
        select(BHItem).where(BHItem.id == item_id).where(BHItem.deleted_at.is_(None))
    )
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not your item")

    data = await request.json()
    media_ids = data.get("media_ids", [])
    if not media_ids:
        raise HTTPException(status_code=400, detail="media_ids required")

    # Fetch all media for this item
    media_result = await db.execute(
        select(BHItemMedia).where(BHItemMedia.item_id == item_id)
    )
    media_map = {str(m.id): m for m in media_result.scalars().all()}

    # Validate all IDs belong to this item
    for mid in media_ids:
        if mid not in media_map:
            raise HTTPException(status_code=400, detail=f"Media {mid} not found on this item")

    # Video can't be cover (position 0)
    first_media = media_map.get(media_ids[0])
    if first_media and first_media.media_type.value == "video":
        raise HTTPException(status_code=400, detail="Cover image cannot be a video")

    # Apply sort order
    for i, mid in enumerate(media_ids):
        media_map[mid].sort_order = i

    await db.commit()
    return {"status": "ok", "order": media_ids}



