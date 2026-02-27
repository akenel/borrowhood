"""Rental model with state machine transitions.

See RULES.md Section 22 for the complete state diagram.
"""

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, BHBase


class RentalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DECLINED = "declined"
    PICKED_UP = "picked_up"
    RETURNED = "returned"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


# Valid state transitions (Section 22)
VALID_RENTAL_TRANSITIONS = {
    RentalStatus.PENDING: [RentalStatus.APPROVED, RentalStatus.DECLINED, RentalStatus.CANCELLED],
    RentalStatus.APPROVED: [RentalStatus.PICKED_UP, RentalStatus.CANCELLED, RentalStatus.DISPUTED],
    RentalStatus.PICKED_UP: [RentalStatus.RETURNED, RentalStatus.DISPUTED],
    RentalStatus.RETURNED: [RentalStatus.COMPLETED, RentalStatus.DISPUTED],
    RentalStatus.COMPLETED: [],
    RentalStatus.DECLINED: [],
    RentalStatus.CANCELLED: [],
    RentalStatus.DISPUTED: [RentalStatus.COMPLETED, RentalStatus.CANCELLED],
}


class BHRental(BHBase, Base):
    """A rental transaction between a renter and an item owner."""

    __tablename__ = "bh_rental"

    listing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_listing.id"), nullable=False, index=True
    )
    renter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )

    # Status (state machine)
    status: Mapped[RentalStatus] = mapped_column(
        Enum(RentalStatus), default=RentalStatus.PENDING, nullable=False, index=True
    )

    # Dates
    requested_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    requested_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    actual_pickup: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    actual_return: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Communication
    renter_message: Mapped[Optional[str]] = mapped_column(Text)
    owner_message: Mapped[Optional[str]] = mapped_column(Text)
    cancel_reason: Mapped[Optional[str]] = mapped_column(Text)
    decline_reason: Mapped[Optional[str]] = mapped_column(Text)

    # Idempotency (Rule 28 -- prevent double submit)
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(36), unique=True)

    # Relationships
    listing: Mapped["BHListing"] = relationship(back_populates="rentals")
    renter: Mapped["BHUser"] = relationship(foreign_keys=[renter_id])


def validate_rental_transition(current: RentalStatus, new: RentalStatus) -> bool:
    """Check if a state transition is valid per the state machine."""
    return new in VALID_RENTAL_TRANSITIONS.get(current, [])
