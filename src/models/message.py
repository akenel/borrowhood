"""In-app messaging between users.

Threaded conversations tied to listings or rentals.
Supports structured offers (make offer, counter, accept, decline).
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, BHBase

import enum


class MessageType(str, enum.Enum):
    TEXT = "text"
    OFFER = "offer"
    COUNTER = "counter"
    ACCEPT = "accept"
    DECLINE = "decline"


class OfferStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    COUNTERED = "countered"
    DECLINED = "declined"
    EXPIRED = "expired"


class BHMessage(BHBase, Base):
    """A single message in a conversation thread."""

    __tablename__ = "bh_message"

    sender_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )
    recipient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )

    # Optional context (what's this about?)
    listing_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_listing.id"), nullable=True
    )
    rental_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_rental.id"), nullable=True
    )

    body: Mapped[str] = mapped_column(Text, nullable=False)

    # Message type: text (default), offer, counter, accept, decline
    message_type: Mapped[str] = mapped_column(
        String(20), default="text", server_default="text", nullable=False
    )

    # Offer fields (only populated for offer/counter/accept messages)
    offered_price: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    offer_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    offer_round: Mapped[Optional[int]] = mapped_column(default=None, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), default=None
    )

    # Read tracking
    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), default=None
    )

    # Edit tracking
    edited_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), default=None
    )

    # Relationships
    sender: Mapped["BHUser"] = relationship(foreign_keys=[sender_id])
    recipient: Mapped["BHUser"] = relationship(foreign_keys=[recipient_id])
