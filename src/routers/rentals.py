"""Rental request API with state machine transitions.

Flow: PENDING -> APPROVED -> PICKED_UP -> RETURNED -> COMPLETED
Branch: PENDING -> DECLINED | CANCELLED
Branch: any active -> DISPUTED -> COMPLETED | CANCELLED
"""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.dependencies import get_user, require_auth
from src.models.listing import BHListing, ListingType, ListingStatus
from src.models.notification import NotificationType
from src.models.rental import BHRental, RentalStatus, validate_rental_transition
from src.models.user import BHUser
from src.schemas.rental import RentalCreate, RentalOut, RentalStatusUpdate
from src.services.notify import notify_rental_event

router = APIRouter(prefix="/api/v1/rentals", tags=["rentals"])


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
    user = await get_user(db, token)

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
    user = await get_user(db, token)

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
    user = await get_user(db, token)

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

    # Can't rent/buy/book your own items
    if listing.item.owner_id == user.id:
        verb = {
            ListingType.SELL: "buy", ListingType.GIVEAWAY: "claim",
            ListingType.OFFER: "claim", ListingType.SERVICE: "book",
            ListingType.TRAINING: "book", ListingType.COMMISSION: "order",
        }.get(listing.listing_type, "rent")
        raise HTTPException(status_code=400, detail=f"Cannot {verb} your own item")

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
    await db.flush()

    # Notify item owner about the request
    await notify_rental_event(
        db=db,
        user_id=listing.item.owner_id,
        notification_type=NotificationType.RENTAL_REQUEST,
        item_name=listing.item.name,
        other_party_name=user.display_name,
        rental_id=rental.id,
        listing_type=listing.listing_type.value if listing.listing_type else None,
    )

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
    user = await get_user(db, token)

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
    renter_actions = {RentalStatus.PICKED_UP}
    either_actions = {RentalStatus.DISPUTED, RentalStatus.RETURNED, RentalStatus.CANCELLED}

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

    # Auto-release deposit on cancellation (refund)
    if rental.status == RentalStatus.CANCELLED:
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
            deposit.reason = "Auto-released on cancellation -- full refund"

    # Notify the other party about the status change
    status_to_type = {
        RentalStatus.APPROVED: NotificationType.RENTAL_APPROVED,
        RentalStatus.DECLINED: NotificationType.RENTAL_DECLINED,
        RentalStatus.PICKED_UP: NotificationType.RENTAL_PICKED_UP,
        RentalStatus.RETURNED: NotificationType.RENTAL_RETURNED,
        RentalStatus.COMPLETED: NotificationType.RENTAL_COMPLETED,
        RentalStatus.CANCELLED: NotificationType.RENTAL_CANCELLED,
    }
    notif_type = status_to_type.get(rental.status)
    if notif_type:
        notify_user_id = rental.listing.item.owner_id if is_renter else rental.renter_id
        await notify_rental_event(
            db=db,
            user_id=notify_user_id,
            notification_type=notif_type,
            item_name=rental.listing.item.name,
            other_party_name=user.display_name,
            rental_id=rental.id,
            listing_type=rental.listing.listing_type.value if rental.listing.listing_type else None,
        )

    await db.commit()
    await db.refresh(rental)
    return rental


@router.get("/{rental_id}/calendar")
async def rental_calendar(
    rental_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Download .ics calendar file for a rental's dates."""
    user = await get_user(db, token)

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

    item_name = rental.listing.item.name
    now = datetime.now(timezone.utc)
    dtstart = rental.requested_start or now
    dtend = rental.requested_end or dtstart

    def _ics_dt(dt) -> str:
        return dt.strftime("%Y%m%dT%H%M%SZ")

    ics = (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "PRODID:-//BorrowHood//Rental//EN\r\n"
        "BEGIN:VEVENT\r\n"
        f"UID:{rental.id}@borrowhood\r\n"
        f"DTSTAMP:{_ics_dt(now)}\r\n"
        f"DTSTART:{_ics_dt(dtstart)}\r\n"
        f"DTEND:{_ics_dt(dtend)}\r\n"
        f"SUMMARY:BorrowHood: {item_name}\r\n"
        f"DESCRIPTION:Rental of {item_name} via BorrowHood. Status: {rental.status.value}.\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )

    return PlainTextResponse(
        content=ics,
        media_type="text/calendar",
        headers={"Content-Disposition": f'attachment; filename="rental-{rental.id}.ics"'},
    )
