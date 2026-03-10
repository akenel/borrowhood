"""Delivery tracking API -- document flow like water.

Endpoints for creating, updating, and viewing delivery tracking
for rentals. Both owner and renter can see the timeline.
Owner drives dispatching; renter drives confirmation.
"""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.dependencies import get_user, require_auth
from src.models.delivery import (
    BHDeliveryTracking, BHDeliveryEvent,
    DeliveryMethod, DeliveryStatus,
    validate_delivery_transition,
)
from src.models.listing import BHListing
from src.models.notification import NotificationType
from src.models.rental import BHRental
from src.services.notify import create_notification

router = APIRouter(prefix="/api/v1/deliveries", tags=["deliveries"])


# --- Schemas ---

class DeliveryTrackingOut(BaseModel):
    id: UUID
    rental_id: UUID
    delivery_method: str
    buyer_preferred_method: Optional[str] = None
    delivery_notes: Optional[str] = None
    status: str
    delivery_address: Optional[str] = None
    delivery_lat: Optional[float] = None
    delivery_lng: Optional[float] = None
    lockbox_code: Optional[str] = None
    lockbox_location: Optional[str] = None
    carrier_name: Optional[str] = None
    tracking_number: Optional[str] = None
    tracking_url: Optional[str] = None
    delivery_person_name: Optional[str] = None
    dispatched_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None
    auto_confirm_hours: int = 48
    events: list = []
    created_at: datetime

    class Config:
        from_attributes = True


class DeliveryEventOut(BaseModel):
    id: UUID
    status: str
    title: str
    description: Optional[str] = None
    actor_role: Optional[str] = None
    event_lat: Optional[float] = None
    event_lng: Optional[float] = None
    photo_url: Optional[str] = None
    next_action: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DeliveryCreate(BaseModel):
    """Owner initiates delivery tracking after approving a rental."""
    rental_id: UUID
    delivery_method: DeliveryMethod
    delivery_notes: Optional[str] = None
    delivery_address: Optional[str] = None
    delivery_lat: Optional[float] = None
    delivery_lng: Optional[float] = None
    lockbox_code: Optional[str] = None
    lockbox_location: Optional[str] = None
    carrier_name: Optional[str] = None
    tracking_number: Optional[str] = None
    tracking_url: Optional[str] = None
    delivery_person_name: Optional[str] = None
    auto_confirm_hours: int = Field(default=48, ge=1, le=168)


class DeliveryStatusUpdate(BaseModel):
    """Update delivery status with optional details."""
    status: DeliveryStatus
    title: Optional[str] = None
    description: Optional[str] = None
    event_lat: Optional[float] = None
    event_lng: Optional[float] = None
    photo_url: Optional[str] = None
    # Optional updates to tracking record
    lockbox_code: Optional[str] = None
    tracking_number: Optional[str] = None
    tracking_url: Optional[str] = None


# --- Status → notification type mapping ---
DELIVERY_NOTIF_MAP = {
    DeliveryStatus.PREPARING: NotificationType.DELIVERY_PREPARING,
    DeliveryStatus.DISPATCHED: NotificationType.DELIVERY_DISPATCHED,
    DeliveryStatus.IN_TRANSIT: NotificationType.DELIVERY_IN_TRANSIT,
    DeliveryStatus.DELIVERED: NotificationType.DELIVERY_DELIVERED,
    DeliveryStatus.READY_FOR_PICKUP: NotificationType.DELIVERY_READY_PICKUP,
    DeliveryStatus.CONFIRMED: NotificationType.DELIVERY_CONFIRMED,
    DeliveryStatus.FAILED: NotificationType.DELIVERY_FAILED,
    DeliveryStatus.DAMAGED: NotificationType.DELIVERY_DAMAGED,
}

# --- Status → human-readable title + next action ---
STATUS_MESSAGES = {
    DeliveryStatus.PREPARING: {
        "title": "Preparing your order",
        "next_action": "We'll notify you when it's on its way",
    },
    DeliveryStatus.DISPATCHED: {
        "title": "{method} delivery started",
        "next_action": "Your order is on its way to you",
    },
    DeliveryStatus.IN_TRANSIT: {
        "title": "On the way to you",
        "next_action": "Almost there -- keep an eye out",
    },
    DeliveryStatus.DELIVERED: {
        "title": "Delivered to {location}",
        "next_action": "Please confirm receipt within {hours} hours",
    },
    DeliveryStatus.READY_FOR_PICKUP: {
        "title": "Ready for pickup",
        "next_action": "Pick up at {location}. Code: {code}",
    },
    DeliveryStatus.PICKED_UP: {
        "title": "Picked up",
        "next_action": "Please confirm the item is in good condition",
    },
    DeliveryStatus.CONFIRMED: {
        "title": "Receipt confirmed",
        "next_action": "All done -- leave a review to share your experience",
    },
    DeliveryStatus.FAILED: {
        "title": "Delivery failed",
        "next_action": "The seller will arrange a new delivery attempt",
    },
    DeliveryStatus.RETURNED_TO_SENDER: {
        "title": "Returned to sender",
        "next_action": "Contact the seller to arrange redelivery",
    },
    DeliveryStatus.DAMAGED: {
        "title": "Damage reported",
        "next_action": "A dispute has been filed -- we'll help resolve this",
    },
}


def _build_event_title(status: DeliveryStatus, tracking: BHDeliveryTracking, custom_title: str = None) -> str:
    """Build a human-readable event title."""
    if custom_title:
        return custom_title
    template = STATUS_MESSAGES.get(status, {}).get("title", status.value)
    method_names = {"human": "Personal", "drone": "Drone", "lockbox": "Lockbox", "pickup": "Pickup", "mail": "Mail"}
    return template.format(
        method=method_names.get(tracking.delivery_method.value, tracking.delivery_method.value),
        location=tracking.delivery_address or tracking.lockbox_location or "destination",
        code=tracking.lockbox_code or "---",
        hours=tracking.auto_confirm_hours,
    )


def _build_next_action(status: DeliveryStatus, tracking: BHDeliveryTracking) -> str:
    """Build the next action hint."""
    template = STATUS_MESSAGES.get(status, {}).get("next_action", "")
    return template.format(
        location=tracking.delivery_address or tracking.lockbox_location or "the specified location",
        code=tracking.lockbox_code or "---",
        hours=tracking.auto_confirm_hours,
    )


# --- Endpoints ---

@router.post("", response_model=DeliveryTrackingOut, status_code=201)
async def create_delivery_tracking(
    data: DeliveryCreate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Owner creates delivery tracking after approving a rental."""
    user = await get_user(db, token)

    # Verify rental exists and user is the owner
    result = await db.execute(
        select(BHRental)
        .options(selectinload(BHRental.listing).selectinload(BHListing.item))
        .where(BHRental.id == data.rental_id)
    )
    rental = result.scalars().first()
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")
    if rental.listing.item.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Only the item owner can create delivery tracking")

    # Check no tracking exists yet
    existing = await db.execute(
        select(BHDeliveryTracking).where(BHDeliveryTracking.rental_id == data.rental_id)
    )
    if existing.scalars().first():
        raise HTTPException(status_code=409, detail="Delivery tracking already exists for this rental")

    tracking = BHDeliveryTracking(
        rental_id=data.rental_id,
        delivery_method=data.delivery_method,
        delivery_notes=data.delivery_notes,
        delivery_address=data.delivery_address,
        delivery_lat=data.delivery_lat,
        delivery_lng=data.delivery_lng,
        lockbox_code=data.lockbox_code,
        lockbox_location=data.lockbox_location,
        carrier_name=data.carrier_name,
        tracking_number=data.tracking_number,
        tracking_url=data.tracking_url,
        delivery_person_name=data.delivery_person_name,
        auto_confirm_hours=data.auto_confirm_hours,
        status=DeliveryStatus.PREPARING,
    )
    db.add(tracking)
    await db.flush()

    # Create initial event
    event = BHDeliveryEvent(
        tracking_id=tracking.id,
        status=DeliveryStatus.PREPARING,
        title=_build_event_title(DeliveryStatus.PREPARING, tracking),
        description=data.delivery_notes,
        actor_id=user.id,
        actor_role="owner",
        next_action=_build_next_action(DeliveryStatus.PREPARING, tracking),
    )
    db.add(event)

    # Notify the renter
    await create_notification(
        db=db,
        user_id=rental.renter_id,
        notification_type=NotificationType.DELIVERY_PREPARING,
        title=f"{user.display_name} is preparing your order",
        body=_build_next_action(DeliveryStatus.PREPARING, tracking),
        link=f"/dashboard",
        entity_type="delivery",
        entity_id=tracking.id,
    )

    await db.commit()
    # Re-fetch with events
    result = await db.execute(
        select(BHDeliveryTracking)
        .options(selectinload(BHDeliveryTracking.events))
        .where(BHDeliveryTracking.id == tracking.id)
    )
    return result.scalars().first()


@router.get("/{rental_id}", response_model=DeliveryTrackingOut)
async def get_delivery_tracking(
    rental_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Get delivery tracking for a rental. Both owner and renter can view."""
    user = await get_user(db, token)

    result = await db.execute(
        select(BHDeliveryTracking)
        .options(selectinload(BHDeliveryTracking.events))
        .where(BHDeliveryTracking.rental_id == rental_id)
    )
    tracking = result.scalars().first()
    if not tracking:
        raise HTTPException(status_code=404, detail="No delivery tracking for this rental")

    # Verify user is a participant
    rental_result = await db.execute(
        select(BHRental)
        .options(selectinload(BHRental.listing).selectinload(BHListing.item))
        .where(BHRental.id == rental_id)
    )
    rental = rental_result.scalars().first()
    if rental.renter_id != user.id and rental.listing.item.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not your rental")

    return tracking


@router.get("/{rental_id}/events", response_model=List[DeliveryEventOut])
async def get_delivery_events(
    rental_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Get delivery timeline events for a rental."""
    user = await get_user(db, token)

    # Verify tracking exists and user is participant
    result = await db.execute(
        select(BHDeliveryTracking).where(BHDeliveryTracking.rental_id == rental_id)
    )
    tracking = result.scalars().first()
    if not tracking:
        raise HTTPException(status_code=404, detail="No delivery tracking for this rental")

    rental_result = await db.execute(
        select(BHRental)
        .options(selectinload(BHRental.listing).selectinload(BHListing.item))
        .where(BHRental.id == rental_id)
    )
    rental = rental_result.scalars().first()
    if rental.renter_id != user.id and rental.listing.item.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not your rental")

    events = await db.execute(
        select(BHDeliveryEvent)
        .where(BHDeliveryEvent.tracking_id == tracking.id)
        .order_by(BHDeliveryEvent.created_at.asc())
    )
    return events.scalars().all()


@router.patch("/{rental_id}/status", response_model=DeliveryTrackingOut)
async def update_delivery_status(
    rental_id: UUID,
    data: DeliveryStatusUpdate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Update delivery status. Owner dispatches; renter confirms.

    Owner can: PREPARING→DISPATCHED, DISPATCHED→IN_TRANSIT→DELIVERED, READY_FOR_PICKUP
    Renter can: CONFIRMED, DAMAGED, PICKED_UP
    """
    user = await get_user(db, token)

    result = await db.execute(
        select(BHDeliveryTracking)
        .options(selectinload(BHDeliveryTracking.events))
        .where(BHDeliveryTracking.rental_id == rental_id)
    )
    tracking = result.scalars().first()
    if not tracking:
        raise HTTPException(status_code=404, detail="No delivery tracking for this rental")

    rental_result = await db.execute(
        select(BHRental)
        .options(selectinload(BHRental.listing).selectinload(BHListing.item))
        .where(BHRental.id == rental_id)
    )
    rental = rental_result.scalars().first()

    is_renter = rental.renter_id == user.id
    is_owner = rental.listing.item.owner_id == user.id
    if not (is_renter or is_owner):
        raise HTTPException(status_code=403, detail="Not your rental")

    # Validate transition
    if not validate_delivery_transition(tracking.status, data.status):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition from {tracking.status.value} to {data.status.value}"
        )

    # Role-based rules
    owner_statuses = {
        DeliveryStatus.DISPATCHED, DeliveryStatus.IN_TRANSIT,
        DeliveryStatus.DELIVERED, DeliveryStatus.READY_FOR_PICKUP,
        DeliveryStatus.RETURNED_TO_SENDER, DeliveryStatus.PREPARING,
    }
    renter_statuses = {
        DeliveryStatus.CONFIRMED, DeliveryStatus.DAMAGED, DeliveryStatus.PICKED_UP,
    }

    if data.status in owner_statuses and not is_owner:
        raise HTTPException(status_code=403, detail="Only the owner can perform this delivery action")
    if data.status in renter_statuses and not is_renter:
        raise HTTPException(status_code=403, detail="Only the buyer can confirm or report delivery")

    # Update tracking record
    now = datetime.now(timezone.utc)
    tracking.status = data.status

    if data.status == DeliveryStatus.DISPATCHED:
        tracking.dispatched_at = now
    elif data.status in (DeliveryStatus.DELIVERED, DeliveryStatus.READY_FOR_PICKUP):
        tracking.delivered_at = now
    elif data.status in (DeliveryStatus.CONFIRMED, DeliveryStatus.PICKED_UP):
        tracking.confirmed_at = now

    # Update optional fields if provided
    if data.lockbox_code:
        tracking.lockbox_code = data.lockbox_code
    if data.tracking_number:
        tracking.tracking_number = data.tracking_number
    if data.tracking_url:
        tracking.tracking_url = data.tracking_url

    # Create timeline event
    event = BHDeliveryEvent(
        tracking_id=tracking.id,
        status=data.status,
        title=_build_event_title(data.status, tracking, data.title),
        description=data.description,
        actor_id=user.id,
        actor_role="owner" if is_owner else "renter",
        event_lat=data.event_lat,
        event_lng=data.event_lng,
        photo_url=data.photo_url,
        next_action=_build_next_action(data.status, tracking),
    )
    db.add(event)

    # Notify the other party
    notif_type = DELIVERY_NOTIF_MAP.get(data.status)
    if notif_type:
        notify_user_id = rental.listing.item.owner_id if is_renter else rental.renter_id
        item_name = rental.listing.item.name if rental.listing and rental.listing.item else "Item"

        # Build notification body with next action
        notif_title = _build_event_title(data.status, tracking, data.title)
        notif_body = _build_next_action(data.status, tracking)

        # Special messages for specific statuses
        if data.status == DeliveryStatus.DELIVERED:
            notif_title = f"Your {item_name} has been delivered"
            notif_body = f"Please confirm receipt within {tracking.auto_confirm_hours} hours"
        elif data.status == DeliveryStatus.READY_FOR_PICKUP:
            notif_title = f"Your {item_name} is ready for pickup"
            if tracking.lockbox_code:
                notif_body = f"Lockbox code: {tracking.lockbox_code}. Location: {tracking.lockbox_location or tracking.delivery_address or 'See details'}"
        elif data.status == DeliveryStatus.CONFIRMED:
            notif_title = f"Receipt confirmed for {item_name}"
            notif_body = "Transaction complete -- leave a review to share your experience"
        elif data.status == DeliveryStatus.DAMAGED:
            notif_title = f"Damage reported for {item_name}"
            notif_body = data.description or "The buyer has reported damage on receipt"

        await create_notification(
            db=db,
            user_id=notify_user_id,
            notification_type=notif_type,
            title=notif_title,
            body=notif_body,
            link="/dashboard",
            entity_type="delivery",
            entity_id=tracking.id,
        )

    await db.commit()

    # Re-fetch with events
    result = await db.execute(
        select(BHDeliveryTracking)
        .options(selectinload(BHDeliveryTracking.events))
        .where(BHDeliveryTracking.id == tracking.id)
    )
    return result.scalars().first()
