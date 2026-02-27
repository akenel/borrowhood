"""Listing CRUD API.

Listings are offers on items (rent, sell, commission, etc.).
One item can have multiple listings. Only the item owner can manage listings.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.dependencies import require_auth
from src.models.item import BHItem
from src.models.listing import BHListing, ListingStatus
from src.models.user import BHUser
from src.schemas.listing import ListingCreate, ListingOut, ListingUpdate

router = APIRouter(prefix="/api/v1/listings", tags=["listings"])


async def _get_user(db: AsyncSession, keycloak_id: str) -> BHUser:
    result = await db.execute(
        select(BHUser).where(BHUser.keycloak_id == keycloak_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=403, detail="User not provisioned in BorrowHood")
    return user


@router.get("", response_model=List[ListingOut])
async def list_listings(
    item_id: Optional[UUID] = None,
    status: Optional[str] = None,
    listing_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List listings with optional filters. Public endpoint."""
    query = select(BHListing).where(BHListing.deleted_at.is_(None))

    if item_id:
        query = query.where(BHListing.item_id == item_id)
    if status:
        query = query.where(BHListing.status == status)
    if listing_type:
        query = query.where(BHListing.listing_type == listing_type)

    query = query.order_by(BHListing.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{listing_id}", response_model=ListingOut)
async def get_listing(listing_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a single listing by ID. Public endpoint."""
    result = await db.execute(
        select(BHListing)
        .where(BHListing.id == listing_id)
        .where(BHListing.deleted_at.is_(None))
    )
    listing = result.scalars().first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


@router.post("", response_model=ListingOut, status_code=201)
async def create_listing(
    data: ListingCreate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Create a listing on an item you own. Requires authentication."""
    user = await _get_user(db, token["sub"])

    # Verify ownership
    result = await db.execute(
        select(BHItem)
        .where(BHItem.id == data.item_id)
        .where(BHItem.deleted_at.is_(None))
    )
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not your item")

    listing = BHListing(
        item_id=data.item_id,
        listing_type=data.listing_type,
        status=ListingStatus.ACTIVE,
        price=data.price,
        price_unit=data.price_unit,
        currency=data.currency,
        deposit=data.deposit,
        min_rental_days=data.min_rental_days,
        max_rental_days=data.max_rental_days,
        delivery_available=data.delivery_available,
        pickup_only=data.pickup_only,
        notes=data.notes,
    )
    db.add(listing)
    await db.commit()
    await db.refresh(listing)
    return listing


@router.patch("/{listing_id}", response_model=ListingOut)
async def update_listing(
    listing_id: UUID,
    data: ListingUpdate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Update a listing. Only the item owner can update."""
    user = await _get_user(db, token["sub"])

    result = await db.execute(
        select(BHListing)
        .options(selectinload(BHListing.item))
        .where(BHListing.id == listing_id)
        .where(BHListing.deleted_at.is_(None))
    )
    listing = result.scalars().first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.item.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not your listing")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(listing, field, value)

    listing.version += 1
    await db.commit()
    await db.refresh(listing)
    return listing


@router.delete("/{listing_id}", status_code=204)
async def delete_listing(
    listing_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a listing. Only the item owner can delete."""
    user = await _get_user(db, token["sub"])

    result = await db.execute(
        select(BHListing)
        .options(selectinload(BHListing.item))
        .where(BHListing.id == listing_id)
        .where(BHListing.deleted_at.is_(None))
    )
    listing = result.scalars().first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.item.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not your listing")

    from datetime import datetime, timezone
    listing.deleted_at = datetime.now(timezone.utc)
    await db.commit()
