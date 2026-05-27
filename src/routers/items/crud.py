"""Item list/get/create/update/delete."""

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

@router.get("/", response_model=List[ItemOut])
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
        # Fuzzy search: substring match OR trigram WORD similarity.
        # word_similarity(query, text) scores the query against the best-matching
        # *word* in the text -- so a typo like "cooky" matches "...Cookie..." even
        # in a long product name. Plain similarity() scores the WHOLE string, so a
        # short query scored ~0.1 against a long name and never cleared threshold
        # (that's why "cooky" found nothing). Threshold 0.4 cleanly separates real
        # typos (cooky->cookie 0.67, dril->drill 0.8) from nonsense (zzzxqq -> 0.0).
        query = query.where(
            BHItem.name.ilike(search_term)
            | BHItem.description.ilike(search_term)
            | (func.word_similarity(q, BHItem.name) > 0.4)
            | (func.word_similarity(q, BHItem.description) > 0.4)
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


@router.post("/", response_model=ItemOut, status_code=201)
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
        # BL-178/179: story, tags, safety_notes, age_restricted were silently
        # dropped on first-save. Schema accepted them but the route never
        # copied them to the BHItem instance. PATCH (update) handled them
        # via setattr loop, which is why edit-save worked but create-save
        # quietly lost the AI-generated story + user-set tags.
        story=data.story,
        tags=data.tags,
        age_restricted=data.age_restricted,
        safety_notes=data.safety_notes,
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

    # Regenerate slug when name changes
    if "name" in update_data and update_data["name"] != item.name:
        new_slug = await _unique_slug(db, update_data["name"])
        item.slug = new_slug

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



