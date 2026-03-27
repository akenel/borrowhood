"""Item CRUD API.

Public reads, auth-gated writes. Items belong to the authenticated user.
Slug auto-generated from name via python-slugify.
"""

import os
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

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "static" / "uploads"
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime"}
ALLOWED_TYPES = ALLOWED_IMAGE_TYPES | ALLOWED_VIDEO_TYPES
MAX_IMAGE_SIZE = 10 * 1024 * 1024   # 10 MB
MAX_VIDEO_SIZE = 50 * 1024 * 1024   # 50 MB

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
    category_group: Optional[str] = None,  # "vehicles", "property", "jobs" etc.
    item_type: Optional[str] = None,
    sort: str = Query("newest", pattern="^(newest|oldest|name_asc)$"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    # Attribute filters (JSONB) -- pass as query params like attr_fuel_type=diesel
    request: Request = None,
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
        # Fuzzy search: trigram similarity OR substring match
        from sqlalchemy import text as sa_text
        query = query.where(
            BHItem.name.ilike(search_term)
            | BHItem.description.ilike(search_term)
            | (func.similarity(BHItem.name, q) > 0.2)
            | (func.similarity(BHItem.description, q) > 0.15)
        )
    if category:
        query = query.where(BHItem.category == category)
    if category_group and category_group in CATEGORY_GROUPS:
        cats = CATEGORY_GROUPS[category_group]
        query = query.where(BHItem.category.in_(cats))
    if item_type:
        query = query.where(BHItem.item_type == item_type)

    # JSONB attribute filters: ?attr_fuel_type=diesel&attr_bedrooms=3
    if request:
        from sqlalchemy import cast, text as sa_text
        for key, value in request.query_params.items():
            if key.startswith("attr_"):
                attr_name = key[5:]  # strip "attr_" prefix
                # Try numeric comparison for range filters
                if key.endswith("_min"):
                    attr_name = attr_name[:-4]
                    try:
                        val = int(value)
                        query = query.where(
                            cast(BHItem.attributes[attr_name].as_string(), Integer) >= val
                        )
                    except (ValueError, TypeError):
                        pass
                elif key.endswith("_max"):
                    attr_name = attr_name[:-4]
                    try:
                        val = int(value)
                        query = query.where(
                            cast(BHItem.attributes[attr_name].as_string(), Integer) <= val
                        )
                    except (ValueError, TypeError):
                        pass
                else:
                    # Exact match
                    query = query.where(
                        BHItem.attributes[attr_name].as_string() == value
                    )

    if sort == "newest":
        query = query.order_by(BHItem.created_at.desc())
    elif sort == "oldest":
        query = query.order_by(BHItem.created_at.asc())
    elif sort == "name_asc":
        query = query.order_by(BHItem.name.asc())

    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().unique().all()


# ── Attribute schemas (must be BEFORE /{item_id} to avoid UUID conflict) ──


@router.get("/attribute-schema/{category}")
async def get_category_attributes(category: str):
    """Return the attribute field definitions for a category.
    Frontend uses this to render dynamic form fields."""
    schema = get_attribute_schema(category)
    return {"category": category, "fields": schema}


@router.get("/attribute-schemas")
async def get_all_attribute_schemas():
    """Return all attribute schemas and category groups."""
    return {
        "schemas": ATTRIBUTE_SCHEMAS,
        "groups": CATEGORY_GROUPS,
    }


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
    token: dict = Depends(require_badge_tier("newcomer")),
    _throttle: dict = Depends(user_throttle("create_item", 10, 3600)),
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
        attributes=data.attributes,
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


import logging
import re

_wa_log = logging.getLogger("borrowhood.whatsapp")


@router.post("/by-slug/{slug}/whatsapp-connect")
async def whatsapp_connect(
    slug: str,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Return a wa.me link for the item's owner. Authenticated only.

    The seller's phone number is never in the page HTML -- only revealed
    via this authenticated API call, with an audit log entry.
    """
    user = await get_user(db, token)

    result = await db.execute(
        select(BHItem)
        .options(selectinload(BHItem.owner))
        .where(BHItem.slug == slug)
        .where(BHItem.deleted_at.is_(None))
    )
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if not item.owner or not item.owner.whatsapp_number:
        raise HTTPException(status_code=404, detail="Seller has no WhatsApp number")

    if item.owner.id == user.id:
        raise HTTPException(status_code=400, detail="Cannot contact yourself")

    # Sanitize number: digits only (strip +, spaces, dashes)
    digits = re.sub(r"[^\d]", "", item.owner.whatsapp_number)
    # Pre-filled message with item context
    msg = f"Hi, I'm interested in your listing: {item.name}"
    from urllib.parse import quote
    url = f"https://wa.me/{digits}?text={quote(msg)}"

    # Audit log
    _wa_log.info(
        "WhatsApp connect: buyer=%s requested seller=%s number for item=%s (%s)",
        user.id, item.owner.id, item.id, item.slug,
    )

    return {"url": url, "item": item.name}


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
