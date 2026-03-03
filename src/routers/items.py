"""Item CRUD API.

Public reads, auth-gated writes. Items belong to the authenticated user.
Slug auto-generated from name via python-slugify.
"""

import os
import uuid as uuid_mod
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from pydantic import BaseModel, Field
from slugify import slugify
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.dependencies import get_user, require_auth, require_badge_tier
from src.models.item import BHItem, BHItemFavorite, BHItemMedia, MediaType
from src.models.listing import BHListing, ListingStatus
from src.models.user import BHUser
from src.schemas.item import ItemCreate, ItemOut, ItemUpdate

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "static" / "uploads"
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

router = APIRouter(prefix="/api/v1/items", tags=["items"])


async def _unique_slug(db: AsyncSession, base: str) -> str:
    """Generate a unique slug, appending a counter if needed."""
    slug = slugify(base, max_length=200)
    candidate = slug
    counter = 1
    while True:
        exists = await db.scalar(
            select(func.count(BHItem.id)).where(BHItem.slug == candidate)
        )
        if not exists:
            return candidate
        candidate = f"{slug}-{counter}"
        counter += 1


@router.get("", response_model=List[ItemOut])
async def list_items(
    q: Optional[str] = None,
    category: Optional[str] = None,  # accepts ItemCategory values
    item_type: Optional[str] = None,
    sort: str = Query("newest", pattern="^(newest|oldest|name_asc)$"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List items with optional search and filters. Public endpoint."""
    query = (
        select(BHItem)
        .options(selectinload(BHItem.media))
        .where(BHItem.deleted_at.is_(None))
    )

    if q:
        search_term = f"%{q}%"
        query = query.where(
            BHItem.name.ilike(search_term) | BHItem.description.ilike(search_term)
        )
    if category:
        query = query.where(BHItem.category == category)
    if item_type:
        query = query.where(BHItem.item_type == item_type)

    if sort == "newest":
        query = query.order_by(BHItem.created_at.desc())
    elif sort == "oldest":
        query = query.order_by(BHItem.created_at.asc())
    elif sort == "name_asc":
        query = query.order_by(BHItem.name.asc())

    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().unique().all()


@router.get("/{item_id}", response_model=ItemOut)
async def get_item(item_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a single item by ID. Public endpoint."""
    result = await db.execute(
        select(BHItem)
        .options(selectinload(BHItem.media))
        .where(BHItem.id == item_id)
        .where(BHItem.deleted_at.is_(None))
    )
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("", response_model=ItemOut, status_code=201)
async def create_item(
    data: ItemCreate,
    token: dict = Depends(require_badge_tier("active")),
    db: AsyncSession = Depends(get_db),
):
    """Create a new item. Requires ACTIVE badge tier or higher."""
    user = await get_user(db, token)
    slug = await _unique_slug(db, data.name)

    item = BHItem(
        owner_id=user.id,
        name=data.name,
        slug=slug,
        description=data.description,
        content_language=data.content_language,
        item_type=data.item_type,
        category=data.category,
        subcategory=data.subcategory,
        condition=data.condition,
        brand=data.brand,
        model=data.model,
        needs_equipment=data.needs_equipment,
        compatible_with=data.compatible_with,
        latitude=round(data.latitude, 3) if data.latitude else (round(user.latitude, 3) if user.latitude else None),
        longitude=round(data.longitude, 3) if data.longitude else (round(user.longitude, 3) if user.longitude else None),
    )
    db.add(item)
    await db.flush()

    # Check and award badges (e.g., FIRST_LISTING, SUPER_LENDER)
    from src.services.badges import check_and_award_badges
    await check_and_award_badges(db, user.id)

    await db.commit()
    await db.refresh(item)

    # Load media relationship for response
    result = await db.execute(
        select(BHItem).options(selectinload(BHItem.media)).where(BHItem.id == item.id)
    )
    return result.scalars().first()


@router.patch("/{item_id}", response_model=ItemOut)
async def update_item(
    item_id: UUID,
    data: ItemUpdate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Update an item. Only the owner can update."""
    user = await get_user(db, token)

    result = await db.execute(
        select(BHItem)
        .options(selectinload(BHItem.media))
        .where(BHItem.id == item_id)
        .where(BHItem.deleted_at.is_(None))
    )
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not your item")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
async def delete_item(
    item_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete an item. Only the owner can delete."""
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

    from datetime import datetime, timezone
    item.deleted_at = datetime.now(timezone.utc)
    await db.commit()


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
    media = BHItemMedia(
        item_id=item.id,
        url=data.url,
        alt_text=data.alt_text,
        media_type=MediaType(data.media_type) if data.media_type in [e.value for e in MediaType] else MediaType.PHOTO,
        sort_order=0,
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
    """Upload an image file for an item. Only the owner can upload."""
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="File must be JPEG, PNG, WebP, or GIF")

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
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 10 MB)")

    # Save to disk
    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename and "." in file.filename else "jpg"
    if ext not in ("jpg", "jpeg", "png", "webp", "gif"):
        ext = "jpg"
    filename = f"{uuid_mod.uuid4().hex}.{ext}"
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filepath = UPLOAD_DIR / filename
    filepath.write_bytes(contents)

    # Create media record
    media = BHItemMedia(
        item_id=item.id,
        url=f"/static/uploads/{filename}",
        alt_text=f"{item.name} photo",
        media_type=MediaType.PHOTO,
        sort_order=0,
    )
    db.add(media)
    await db.commit()
    await db.refresh(media)
    return media


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
