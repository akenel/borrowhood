"""Item CRUD API.

Public reads, auth-gated writes. Items belong to the authenticated user.
Slug auto-generated from name via python-slugify.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from slugify import slugify
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.dependencies import require_auth
from src.models.item import BHItem, BHItemMedia
from src.models.listing import BHListing, ListingStatus
from src.models.user import BHUser
from src.schemas.item import ItemCreate, ItemOut, ItemUpdate

router = APIRouter(prefix="/api/v1/items", tags=["items"])


async def _get_user(db: AsyncSession, keycloak_id: str) -> BHUser:
    """Look up BHUser by Keycloak subject ID."""
    result = await db.execute(
        select(BHUser).where(BHUser.keycloak_id == keycloak_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=403, detail="User not provisioned in BorrowHood")
    return user


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
    category: Optional[str] = None,
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
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Create a new item. Requires authentication."""
    user = await _get_user(db, token["sub"])
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
        latitude=data.latitude or user.latitude,
        longitude=data.longitude or user.longitude,
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
    user = await _get_user(db, token["sub"])

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
    user = await _get_user(db, token["sub"])

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
