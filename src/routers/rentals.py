"""Rental request API with state machine transitions.

Flow: PENDING -> APPROVED -> PICKED_UP -> RETURNED -> COMPLETED
Branch: PENDING -> DECLINED | CANCELLED
Branch: any active -> DISPUTED -> COMPLETED | CANCELLED
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.dependencies import require_auth
from src.models.listing import BHListing, ListingType, ListingStatus
from src.models.rental import BHRental, RentalStatus, validate_rental_transition
from src.models.user import BHUser
from src.schemas.rental import RentalCreate, RentalOut, RentalStatusUpdate

router = APIRouter(prefix="/api/v1/rentals", tags=["rentals"])


async def _get_user(db: AsyncSession, keycloak_id: str) -> BHUser:
    result = await db.execute(
        select(BHUser).where(BHUser.keycloak_id == keycloak_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=403, detail="User not provisioned in BorrowHood")
    return user


@router.get("", response_model=List[RentalOut])
async def list_rentals(
    status: Optional[str] = None,
    role: Optional[str] = Query(None, pattern="^(renter|owner)$"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List rentals for the authenticated user (as renter or owner)."""
    user = await _get_user(db, token["sub"])

    query = select(BHRental).options(
        selectinload(BHRental.listing).selectinload(BHListing.item)
    )

    if role == "renter":
        query = query.where(BHRental.renter_id == user.id)
    elif role == "owner":
        query = query.join(BHListing).where(BHListing.item.has(owner_id=user.id))
    else:
        # Both: rentals where user is renter OR owner
        query = query.outerjoin(BHListing).where(
            or_(
                BHRental.renter_id == user.id,
                BHListing.item.has(owner_id=user.id),
            )
        )

    if status:
        query = query.where(BHRental.status == status)

    query = query.order_by(BHRental.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().unique().all()


@router.get("/{rental_id}", response_model=RentalOut)
async def get_rental(
    rental_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Get a single rental. Must be renter or item owner."""
    user = await _get_user(db, token["sub"])

    result = await db.execute(
        select(BHRental)
        .options(selectinload(BHRental.listing).selectinload(BHListing.item))
        .where(BHRental.id == rental_id)
    )
    rental = result.scalars().first()
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")

    # Access check: renter or item owner
    is_renter = rental.renter_id == user.id
    is_owner = rental.listing.item.owner_id == user.id
    if not (is_renter or is_owner):
        raise HTTPException(status_code=403, detail="Not your rental")

    return rental


@router.post("", response_model=RentalOut, status_code=201)
async def create_rental(
    data: RentalCreate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Request a rental on a listing. Requires authentication."""
    user = await _get_user(db, token["sub"])

    # Idempotency check
    if data.idempotency_key:
        existing = await db.execute(
            select(BHRental).where(BHRental.idempotency_key == data.idempotency_key)
        )
        found = existing.scalars().first()
        if found:
            return found

    # Verify listing exists and is active
    result = await db.execute(
        select(BHListing)
        .options(selectinload(BHListing.item))
        .where(BHListing.id == data.listing_id)
        .where(BHListing.deleted_at.is_(None))
    )
    listing = result.scalars().first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.status != "active":
        raise HTTPException(status_code=400, detail="Listing is not active")

    # Can't rent your own items
    if listing.item.owner_id == user.id:
        raise HTTPException(status_code=400, detail="Cannot rent your own item")

    # Giveaway shortcut: auto-set dates to now (no date picking needed)
    from datetime import datetime, timezone
    is_giveaway = listing.listing_type == ListingType.GIVEAWAY
    now = datetime.now(timezone.utc)

    rental = BHRental(
        listing_id=data.listing_id,
        renter_id=user.id,
        status=RentalStatus.PENDING,
        requested_start=now if is_giveaway else data.requested_start,
        requested_end=now if is_giveaway else data.requested_end,
        renter_message=data.renter_message,
        idempotency_key=data.idempotency_key,
    )
    db.add(rental)
    await db.commit()
    await db.refresh(rental)
    return rental


@router.patch("/{rental_id}/status", response_model=RentalOut)
async def update_rental_status(
    rental_id: UUID,
    data: RentalStatusUpdate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Transition rental to a new status. Validates state machine rules.

    Owner actions: approve, decline, confirm return, complete
    Renter actions: cancel, confirm pickup
    Either: dispute
    """
    user = await _get_user(db, token["sub"])

    result = await db.execute(
        select(BHRental)
        .options(selectinload(BHRental.listing).selectinload(BHListing.item))
        .where(BHRental.id == rental_id)
    )
    rental = result.scalars().first()
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")

    is_renter = rental.renter_id == user.id
    is_owner = rental.listing.item.owner_id == user.id
    if not (is_renter or is_owner):
        raise HTTPException(status_code=403, detail="Not your rental")

    # Validate state transition
    if not validate_rental_transition(rental.status, data.status):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition from {rental.status.value} to {data.status.value}",
        )

    # Role-based transition rules
    owner_actions = {RentalStatus.APPROVED, RentalStatus.DECLINED, RentalStatus.COMPLETED}
    renter_actions = {RentalStatus.CANCELLED, RentalStatus.PICKED_UP}
    either_actions = {RentalStatus.DISPUTED, RentalStatus.RETURNED}

    if data.status in owner_actions and not is_owner:
        raise HTTPException(status_code=403, detail="Only the item owner can perform this action")
    if data.status in renter_actions and not is_renter:
        raise HTTPException(status_code=403, detail="Only the renter can perform this action")

    # Apply transition
    rental.status = data.status

    if data.message:
        if is_owner:
            rental.owner_message = data.message
        else:
            rental.renter_message = data.message

    if data.status == RentalStatus.DECLINED and data.reason:
        rental.decline_reason = data.reason
    if data.status == RentalStatus.CANCELLED and data.reason:
        rental.cancel_reason = data.reason

    # Track actual dates
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    if data.status == RentalStatus.PICKED_UP:
        rental.actual_pickup = now
    elif data.status == RentalStatus.RETURNED:
        rental.actual_return = now

    # Giveaway shortcut: APPROVED -> auto-complete, deactivate listing
    is_giveaway = rental.listing.listing_type == ListingType.GIVEAWAY
    if is_giveaway and data.status == RentalStatus.APPROVED:
        rental.status = RentalStatus.COMPLETED
        rental.actual_pickup = now
        rental.actual_return = now
        # Deactivate listing (one claim per giveaway)
        rental.listing.status = ListingStatus.PAUSED

    await db.flush()

    # Award badges on rental completion (or giveaway auto-complete)
    if rental.status == RentalStatus.COMPLETED:
        from src.services.badges import check_and_award_badges
        await check_and_award_badges(db, rental.renter_id)
        await check_and_award_badges(db, rental.listing.item.owner_id)

        # Auto-release any HELD deposit back to renter
        from src.models.deposit import BHDeposit, DepositStatus
        dep_result = await db.execute(
            select(BHDeposit)
            .where(BHDeposit.rental_id == rental.id)
            .where(BHDeposit.status == DepositStatus.HELD)
        )
        deposit = dep_result.scalars().first()
        if deposit:
            deposit.status = DepositStatus.RELEASED
            deposit.released_amount = deposit.amount
            deposit.reason = "Auto-released on rental completion"

    await db.commit()
    await db.refresh(rental)
    return rental
