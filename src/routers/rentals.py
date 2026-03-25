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

    # Safety acknowledgment check (BL-102)
    item = listing.item
    has_safety_info = item.age_restricted or item.safety_notes or item.needs_equipment
    if has_safety_info and not data.safety_acknowledged:
        raise HTTPException(
            status_code=400,
            detail="This item has safety requirements. You must acknowledge them before booking."
        )

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
        safety_acknowledged=data.safety_acknowledged or False,
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


# ═══════════════════════════════════════════════════════════════
# COMMITMENT FLOW -- "I Want This" → "I Paid" → "Confirm Payment"
# ═══════════════════════════════════════════════════════════════

from pydantic import BaseModel, Field
from src.models.item import BHItem


class CommitRequest(BaseModel):
    listing_id: UUID
    message: str = Field("", max_length=500)
    commitment_hours: int = Field(48, ge=1, le=168)  # Default 48h, max 7 days


class MarkPaidRequest(BaseModel):
    payment_method: str = Field(..., max_length=30)  # "paypal", "iban", "cash", etc.
    note: str = Field("", max_length=500)


@router.post("/commit", status_code=201)
async def commit_to_listing(
    data: CommitRequest,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Buyer commits to a listing. Starts the commitment timer.
    The listing shows as 'pending payment' to others.
    """
    user = await get_user(db, token)

    # Get listing with item
    result = await db.execute(
        select(BHListing)
        .options(selectinload(BHListing.item))
        .where(BHListing.id == data.listing_id)
        .where(BHListing.deleted_at.is_(None))
    )
    listing = result.scalars().first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.status != ListingStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Listing is not active")
    if listing.item.owner_id == user.id:
        raise HTTPException(status_code=400, detail="Cannot commit to your own listing")

    # Check no existing active commitment on this listing
    existing = await db.execute(
        select(BHRental)
        .where(BHRental.listing_id == data.listing_id)
        .where(BHRental.status.in_([
            RentalStatus.COMMITTED, RentalStatus.BUYER_PAID, RentalStatus.PAYMENT_CONFIRMED
        ]))
    )
    if existing.scalars().first():
        raise HTTPException(status_code=409, detail="This listing already has an active commitment")

    from datetime import timedelta
    expires = datetime.now(timezone.utc) + timedelta(hours=data.commitment_hours)

    rental = BHRental(
        listing_id=data.listing_id,
        renter_id=user.id,
        status=RentalStatus.COMMITTED,
        renter_message=data.message or None,
        commitment_expires_at=expires,
    )
    db.add(rental)
    await db.flush()

    # Notify seller
    await notify_rental_event(
        db=db,
        user_id=listing.item.owner_id,
        notification_type=NotificationType.RENTAL_REQUEST,
        item_name=listing.item.name,
        other_party_name=user.display_name,
        rental_id=rental.id,
        listing_type=listing.listing_type.value,
    )

    await db.commit()

    return {
        "status": "committed",
        "rental_id": str(rental.id),
        "expires_at": expires.isoformat(),
        "message": f"You have {data.commitment_hours} hours to complete payment."
    }


@router.post("/{rental_id}/i-paid", status_code=200)
async def mark_as_paid(
    rental_id: UUID,
    data: MarkPaidRequest,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Buyer marks the order as paid. Specifies payment method used."""
    user = await get_user(db, token)

    result = await db.execute(
        select(BHRental)
        .options(selectinload(BHRental.listing).selectinload(BHListing.item))
        .where(BHRental.id == rental_id)
    )
    rental = result.scalars().first()
    if not rental:
        raise HTTPException(status_code=404, detail="Order not found")
    if rental.renter_id != user.id:
        raise HTTPException(status_code=403, detail="Only the buyer can mark as paid")
    if rental.status != RentalStatus.COMMITTED:
        raise HTTPException(status_code=400, detail=f"Cannot mark as paid from {rental.status.value} status")

    # Check if expired
    if rental.commitment_expires_at and rental.commitment_expires_at < datetime.now(timezone.utc):
        rental.status = RentalStatus.EXPIRED
        await db.commit()
        raise HTTPException(status_code=410, detail="Commitment has expired")

    rental.status = RentalStatus.BUYER_PAID
    rental.payment_method_used = data.payment_method
    rental.buyer_paid_at = datetime.now(timezone.utc)

    # Notify seller
    item = rental.listing.item
    await notify_rental_event(
        db=db,
        user_id=item.owner_id,
        notification_type=NotificationType.SYSTEM,
        item_name=item.name,
        other_party_name=user.display_name,
        rental_id=rental.id,
        listing_type=rental.listing.listing_type.value,
    )

    await db.commit()

    return {
        "status": "buyer_paid",
        "payment_method": data.payment_method,
        "message": "Payment marked! The seller has been notified to confirm."
    }


@router.post("/{rental_id}/confirm-payment", status_code=200)
async def confirm_payment(
    rental_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Seller confirms they received payment."""
    user = await get_user(db, token)

    result = await db.execute(
        select(BHRental)
        .options(selectinload(BHRental.listing).selectinload(BHListing.item))
        .where(BHRental.id == rental_id)
    )
    rental = result.scalars().first()
    if not rental:
        raise HTTPException(status_code=404, detail="Order not found")

    item = rental.listing.item
    if item.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Only the seller can confirm payment")
    if rental.status != RentalStatus.BUYER_PAID:
        raise HTTPException(status_code=400, detail=f"Cannot confirm payment from {rental.status.value} status")

    rental.status = RentalStatus.PAYMENT_CONFIRMED
    rental.payment_confirmed_at = datetime.now(timezone.utc)

    # Notify buyer
    await notify_rental_event(
        db=db,
        user_id=rental.renter_id,
        notification_type=NotificationType.SYSTEM,
        item_name=item.name,
        other_party_name=user.display_name,
        rental_id=rental.id,
        listing_type=rental.listing.listing_type.value,
    )

    await db.commit()

    return {
        "status": "payment_confirmed",
        "message": "Payment confirmed! Arrange pickup or delivery with the buyer."
    }


@router.post("/{rental_id}/complete", status_code=200)
async def complete_order(
    rental_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Either party marks the order as complete (item delivered/picked up)."""
    user = await get_user(db, token)

    result = await db.execute(
        select(BHRental)
        .options(selectinload(BHRental.listing).selectinload(BHListing.item))
        .where(BHRental.id == rental_id)
    )
    rental = result.scalars().first()
    if not rental:
        raise HTTPException(status_code=404, detail="Order not found")

    item = rental.listing.item
    is_buyer = rental.renter_id == user.id
    is_seller = item.owner_id == user.id
    if not is_buyer and not is_seller:
        raise HTTPException(status_code=403, detail="Not your order")

    if rental.status not in (RentalStatus.PAYMENT_CONFIRMED, RentalStatus.PICKED_UP):
        raise HTTPException(status_code=400, detail=f"Cannot complete from {rental.status.value} status")

    rental.status = RentalStatus.COMPLETED

    # Notify the other party
    other_id = item.owner_id if is_buyer else rental.renter_id
    await notify_rental_event(
        db=db,
        user_id=other_id,
        notification_type=NotificationType.SYSTEM,
        item_name=item.name,
        other_party_name=user.display_name,
        rental_id=rental.id,
        listing_type=rental.listing.listing_type.value,
    )

    await db.commit()

    return {
        "status": "completed",
        "message": "Order completed! Don't forget to leave a review."
    }
