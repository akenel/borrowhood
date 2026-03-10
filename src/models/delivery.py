"""Delivery tracking model -- the connective tissue between order and review.

Tracks every step of fulfillment:
  PREPARING → DISPATCHED → IN_TRANSIT → DELIVERED → CONFIRMED
  or: READY_FOR_PICKUP → PICKED_UP → CONFIRMED

Three delivery methods:
  - HUMAN: Johnny brings cookies to your door
  - DRONE: Sofia sends via drone to GPS coordinates
  - LOCKBOX: Item in lockbox, here's your code
  - PICKUP: Come get it yourself
  - MAIL: Traditional post/courier

Each tracking event is an immutable log entry with timestamp,
GPS coordinates, notes, and photos.
"""

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, BHBase


class DeliveryMethod(str, enum.Enum):
    HUMAN = "human"        # Person delivers to door
    DRONE = "drone"        # Drone delivery to coordinates
    LOCKBOX = "lockbox"    # Lockbox pickup with code
    PICKUP = "pickup"      # Buyer comes to seller
    MAIL = "mail"          # Traditional post/courier


class DeliveryStatus(str, enum.Enum):
    # Seller preparing
    PREPARING = "preparing"          # Owner is getting it ready
    # In motion
    DISPATCHED = "dispatched"        # Left the owner (human/drone/mail)
    IN_TRANSIT = "in_transit"        # On the way
    # Arrival
    DELIVERED = "delivered"          # At destination (door/balcony/lockbox/mailbox)
    READY_FOR_PICKUP = "ready_for_pickup"  # Ready at lockbox/location
    # Confirmation
    PICKED_UP = "picked_up"          # Buyer picked it up
    CONFIRMED = "confirmed"          # Buyer confirmed goods received + condition OK
    # Problems
    FAILED = "failed"                # Delivery failed (nobody home, bad weather, drone error)
    RETURNED_TO_SENDER = "returned_to_sender"  # Bounced back
    DAMAGED = "damaged"              # Buyer reports damage on receipt


# Valid delivery status transitions
VALID_DELIVERY_TRANSITIONS = {
    DeliveryStatus.PREPARING: [DeliveryStatus.DISPATCHED, DeliveryStatus.READY_FOR_PICKUP, DeliveryStatus.FAILED],
    DeliveryStatus.DISPATCHED: [DeliveryStatus.IN_TRANSIT, DeliveryStatus.DELIVERED, DeliveryStatus.FAILED],
    DeliveryStatus.IN_TRANSIT: [DeliveryStatus.DELIVERED, DeliveryStatus.FAILED, DeliveryStatus.RETURNED_TO_SENDER],
    DeliveryStatus.DELIVERED: [DeliveryStatus.CONFIRMED, DeliveryStatus.DAMAGED, DeliveryStatus.RETURNED_TO_SENDER],
    DeliveryStatus.READY_FOR_PICKUP: [DeliveryStatus.PICKED_UP, DeliveryStatus.FAILED],
    DeliveryStatus.PICKED_UP: [DeliveryStatus.CONFIRMED, DeliveryStatus.DAMAGED],
    DeliveryStatus.CONFIRMED: [],  # Terminal
    DeliveryStatus.FAILED: [DeliveryStatus.PREPARING, DeliveryStatus.DISPATCHED],  # Retry
    DeliveryStatus.RETURNED_TO_SENDER: [DeliveryStatus.PREPARING],  # Re-send
    DeliveryStatus.DAMAGED: [],  # Terminal -- triggers dispute flow
}


class BHDeliveryTracking(BHBase, Base):
    """Delivery tracking for a rental -- the master record.

    One per rental. Holds current status, delivery method, preferences,
    and destination info.
    """

    __tablename__ = "bh_delivery_tracking"

    rental_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_rental.id", ondelete="CASCADE"),
        nullable=False, unique=True, index=True
    )

    # Delivery method + preferences
    delivery_method: Mapped[DeliveryMethod] = mapped_column(
        Enum(DeliveryMethod), nullable=False
    )
    buyer_preferred_method: Mapped[Optional[str]] = mapped_column(String(20))  # What the buyer wanted
    delivery_notes: Mapped[Optional[str]] = mapped_column(Text)  # "Leave at back door", "Ring bell twice"

    # Current status
    status: Mapped[DeliveryStatus] = mapped_column(
        Enum(DeliveryStatus), default=DeliveryStatus.PREPARING, nullable=False, index=True
    )

    # Destination
    delivery_address: Mapped[Optional[str]] = mapped_column(Text)  # Street address (if applicable)
    delivery_lat: Mapped[Optional[float]] = mapped_column(Float)
    delivery_lng: Mapped[Optional[float]] = mapped_column(Float)

    # Lockbox info (if method = lockbox)
    lockbox_code: Mapped[Optional[str]] = mapped_column(String(20))
    lockbox_location: Mapped[Optional[str]] = mapped_column(Text)

    # Courier/tracking info (if method = mail)
    carrier_name: Mapped[Optional[str]] = mapped_column(String(100))  # "Swiss Post", "DPD"
    tracking_number: Mapped[Optional[str]] = mapped_column(String(100))
    tracking_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Delivery person (if method = human)
    delivery_person_name: Mapped[Optional[str]] = mapped_column(String(200))
    delivery_person_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id")
    )

    # Timestamps
    dispatched_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Auto-confirm deadline (if not confirmed within X hours, auto-confirm)
    auto_confirm_hours: Mapped[int] = mapped_column(Integer, default=48)

    # Relationships
    rental: Mapped["BHRental"] = relationship()
    events: Mapped[list["BHDeliveryEvent"]] = relationship(
        back_populates="tracking", order_by="BHDeliveryEvent.created_at",
        cascade="all, delete-orphan"
    )


class BHDeliveryEvent(BHBase, Base):
    """Immutable log entry for each delivery status change.

    Every transition creates an event. This is the timeline the user sees:
    14:00 - Preparing your order
    14:30 - Johnny picked up your cookies
    14:45 - Johnny is on his way
    15:02 - Delivered to front door
    15:10 - You confirmed receipt -- enjoy!
    """

    __tablename__ = "bh_delivery_event"

    tracking_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_delivery_tracking.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    # What happened
    status: Mapped[DeliveryStatus] = mapped_column(
        Enum(DeliveryStatus), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Who did it
    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id")
    )
    actor_role: Mapped[Optional[str]] = mapped_column(String(20))  # "owner", "renter", "courier", "system"

    # Where (GPS snapshot at time of event)
    event_lat: Mapped[Optional[float]] = mapped_column(Float)
    event_lng: Mapped[Optional[float]] = mapped_column(Float)

    # Evidence (photo of delivery, signature, etc.)
    photo_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Next action hint for the OTHER party
    next_action: Mapped[Optional[str]] = mapped_column(String(200))
    # e.g., "Confirm receipt within 48 hours" or "Pick up from lockbox at Via Roma 5"

    # Relationship
    tracking: Mapped["BHDeliveryTracking"] = relationship(back_populates="events")


def validate_delivery_transition(current: DeliveryStatus, new: DeliveryStatus) -> bool:
    """Check if a delivery status transition is valid."""
    return new in VALID_DELIVERY_TRANSITIONS.get(current, [])
