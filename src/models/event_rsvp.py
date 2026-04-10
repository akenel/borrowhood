"""Event RSVP model: tracks registrations for event-type listings."""

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, BHBase


class RSVPStatus(str, enum.Enum):
    REGISTERED = "registered"
    WAITLISTED = "waitlisted"
    CANCELLED = "cancelled"
    ATTENDED = "attended"
    NO_SHOW = "no_show"


class BHEventRSVP(BHBase, Base):
    """A user's registration for an event listing."""

    __tablename__ = "bh_event_rsvp"
    __table_args__ = (
        UniqueConstraint("listing_id", "user_id", name="uq_event_rsvp"),
    )

    listing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_listing.id"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )
    status: Mapped[RSVPStatus] = mapped_column(
        Enum(RSVPStatus), default=RSVPStatus.REGISTERED, nullable=False
    )
    notes: Mapped[Optional[str]] = mapped_column(Text)
    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    listing: Mapped["BHListing"] = relationship()
    user: Mapped["BHUser"] = relationship()
