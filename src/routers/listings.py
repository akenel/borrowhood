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
from src.dependencies import get_user, require_auth, require_badge_tier, require_role, user_throttle
from src.models.item import BHItem
from src.models.listing import BHListing, ListingStatus, ListingType
from src.models.user import BHUser
from src.schemas.listing import ListingCreate, ListingOut, ListingUpdate

# Roles that bypass pending review (listings go straight to active)
_MODERATOR_ROLES = {"bh-admin", "bh-operator", "bh-moderator"}

router = APIRouter(prefix="/api/v1/listings", tags=["listings"])


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
        valid_statuses = {s.value for s in ListingStatus}
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status '{status}'. Must be one of: {', '.join(sorted(valid_statuses))}")
        query = query.where(BHListing.status == status)
    if listing_type:
        valid_types = {t.value for t in ListingType}
        if listing_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid listing_type '{listing_type}'. Must be one of: {', '.join(sorted(valid_types))}")
        query = query.where(BHListing.listing_type == listing_type)

    query = query.order_by(BHListing.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/moderation/pending", response_model=List[ListingOut])
async def list_pending_listings(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    token: dict = Depends(require_role("bh-moderator")),
    db: AsyncSession = Depends(get_db),
):
    """List all pending listings awaiting review. Moderator only."""
    result = await db.execute(
        select(BHListing)
        .where(BHListing.status == ListingStatus.PENDING)
        .where(BHListing.deleted_at.is_(None))
        .order_by(BHListing.created_at.asc())
        .offset(offset)
        .limit(limit)
    )
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
    _throttle: dict = Depends(user_throttle("create_listing", 20, 3600)),
    db: AsyncSession = Depends(get_db),
):
    """Create a listing on an item you own. Requires authentication."""
    user = await get_user(db, token)

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

    # Auction listings require TRUSTED tier
    if data.listing_type == ListingType.AUCTION:
        from src.dependencies import _TIER_ORDER
        user_level = _TIER_ORDER.get(user.badge_tier.value, 0)
        if user_level < _TIER_ORDER["trusted"]:
            raise HTTPException(
                status_code=403,
                detail="Badge tier 'trusted' required to create auction listings.",
            )

    # Parse auction_end from ISO string if provided
    auction_end_dt = None
    if data.auction_end:
        from datetime import datetime, timezone
        auction_end_dt = datetime.fromisoformat(data.auction_end.replace("Z", "+00:00"))

    # Determine listing status on create:
    # - Draft stays draft (user wants to save without publishing)
    # - Moderators/admins go straight to active
    # - Everyone else goes to pending (awaiting review)
    user_roles = set(token.get("realm_access", {}).get("roles", []))
    is_moderator = bool(user_roles & _MODERATOR_ROLES)

    if data.status == ListingStatus.DRAFT:
        create_status = ListingStatus.DRAFT
    elif is_moderator:
        create_status = ListingStatus.ACTIVE
    else:
        create_status = ListingStatus.PENDING

    listing = BHListing(
        item_id=data.item_id,
        listing_type=data.listing_type,
        status=create_status,
        price=data.price,
        price_unit=data.price_unit,
        currency=data.currency,
        deposit=data.deposit,
        min_rental_days=data.min_rental_days,
        max_rental_days=data.max_rental_days,
        delivery_available=data.delivery_available,
        pickup_only=data.pickup_only,
        notes=data.notes,
        auction_end=auction_end_dt,
        starting_bid=data.starting_bid,
        reserve_price=data.reserve_price,
        bid_increment=data.bid_increment,
        minimum_charge=data.minimum_charge,
        per_person_rate=data.per_person_rate,
        max_participants=data.max_participants,
        group_discount_pct=data.group_discount_pct,
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
    user = await get_user(db, token)

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
    user = await get_user(db, token)

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


# Valid status transitions for listing owners
# draft→pending (publish for review), pending→draft (withdraw)
# active→paused, paused→active (vacation mode)
_ALLOWED_TRANSITIONS = {
    ListingStatus.DRAFT: {ListingStatus.PENDING},
    ListingStatus.PENDING: {ListingStatus.DRAFT},
    ListingStatus.ACTIVE: {ListingStatus.PAUSED},
    ListingStatus.PAUSED: {ListingStatus.ACTIVE},
}

# Moderators can also do these transitions
_MOD_TRANSITIONS = {
    ListingStatus.DRAFT: {ListingStatus.PENDING, ListingStatus.ACTIVE},
    ListingStatus.PENDING: {ListingStatus.ACTIVE, ListingStatus.REMOVED, ListingStatus.DRAFT},
    ListingStatus.ACTIVE: {ListingStatus.PAUSED, ListingStatus.REMOVED},
    ListingStatus.PAUSED: {ListingStatus.ACTIVE},
    ListingStatus.REMOVED: {ListingStatus.ACTIVE},  # Re-approve after removal
}


@router.patch("/{listing_id}/status")
async def change_listing_status(
    listing_id: UUID,
    request: dict,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Change listing status (publish draft, pause, resume). Owner or moderator."""
    user = await get_user(db, token)
    new_status_str = request.get("status")
    if not new_status_str:
        raise HTTPException(status_code=400, detail="Missing 'status' field")

    try:
        new_status = ListingStatus(new_status_str)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {new_status_str}")

    result = await db.execute(
        select(BHListing)
        .options(selectinload(BHListing.item))
        .where(BHListing.id == listing_id)
        .where(BHListing.deleted_at.is_(None))
    )
    listing = result.scalars().first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    user_roles = set(token.get("realm_access", {}).get("roles", []))
    is_moderator = bool(user_roles & _MODERATOR_ROLES)

    # Moderators can change any listing; owners can only change their own
    if not is_moderator and listing.item.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not your listing")

    # Use moderator transitions if caller is a mod, else owner transitions
    transitions = _MOD_TRANSITIONS if is_moderator else _ALLOWED_TRANSITIONS
    allowed = transitions.get(listing.status, set())
    if new_status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot change from '{listing.status.value}' to '{new_status.value}'"
        )

    listing.status = new_status
    listing.version += 1
    await db.commit()
    await db.refresh(listing)
    return {"status": listing.status.value, "id": str(listing.id)}


@router.post("/pause-all")
async def pause_all_listings(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Pause all active listings for the current user. Vacation mode."""
    user = await get_user(db, token)

    result = await db.execute(
        select(BHListing)
        .join(BHItem, BHListing.item_id == BHItem.id)
        .where(BHItem.owner_id == user.id)
        .where(BHListing.status == ListingStatus.ACTIVE)
        .where(BHListing.deleted_at.is_(None))
    )
    listings = result.scalars().all()
    count = 0
    for listing in listings:
        listing.status = ListingStatus.PAUSED
        listing.version += 1
        count += 1
    await db.commit()
    return {"paused": count}


@router.post("/resume-all")
async def resume_all_listings(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Resume all paused listings for the current user."""
    user = await get_user(db, token)

    result = await db.execute(
        select(BHListing)
        .join(BHItem, BHListing.item_id == BHItem.id)
        .where(BHItem.owner_id == user.id)
        .where(BHListing.status == ListingStatus.PAUSED)
        .where(BHListing.deleted_at.is_(None))
    )
    listings = result.scalars().all()
    count = 0
    for listing in listings:
        listing.status = ListingStatus.ACTIVE
        listing.version += 1
        count += 1
    await db.commit()
    return {"resumed": count}
