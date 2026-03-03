"""Service quote model -- quoting workflow for repairs, training, custom orders.

State machine:
  REQUESTED -> QUOTED -> ACCEPTED -> IN_PROGRESS -> COMPLETED
           \-> DECLINED                         \-> DISPUTED
  Any active state -> CANCELLED (by either party)

A customer requests a quote on a service listing, the provider responds
with pricing, the customer accepts or declines.
"""

import enum
import uuid
from typing import Optional

from sqlalchemy import Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, BHBase


class QuoteStatus(str, enum.Enum):
    REQUESTED = "requested"       # Customer asked for a quote
    QUOTED = "quoted"             # Provider sent pricing
    ACCEPTED = "accepted"         # Customer accepted the quote
    DECLINED = "declined"         # Customer declined
    IN_PROGRESS = "in_progress"   # Work underway
    COMPLETED = "completed"       # Work done
    CANCELLED = "cancelled"       # Either party cancelled
    DISPUTED = "disputed"         # Escalated to dispute


# Valid transitions: current_status -> set of allowed next statuses
VALID_QUOTE_TRANSITIONS = {
    QuoteStatus.REQUESTED: {QuoteStatus.QUOTED, QuoteStatus.CANCELLED},
    QuoteStatus.QUOTED: {QuoteStatus.ACCEPTED, QuoteStatus.DECLINED, QuoteStatus.CANCELLED},
    QuoteStatus.ACCEPTED: {QuoteStatus.IN_PROGRESS, QuoteStatus.CANCELLED},
    QuoteStatus.IN_PROGRESS: {QuoteStatus.COMPLETED, QuoteStatus.DISPUTED, QuoteStatus.CANCELLED},
    QuoteStatus.COMPLETED: {QuoteStatus.DISPUTED},
    QuoteStatus.DECLINED: set(),
    QuoteStatus.CANCELLED: set(),
    QuoteStatus.DISPUTED: set(),
}


class BHServiceQuote(BHBase, Base):
    """A service quote between a customer and a provider."""

    __tablename__ = "bh_service_quote"

    # Parties
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )
    provider_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )
    listing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_listing.id"), nullable=False, index=True
    )

    # Status
    status: Mapped[QuoteStatus] = mapped_column(
        Enum(QuoteStatus), default=QuoteStatus.REQUESTED, nullable=False, index=True
    )

    # Customer request
    request_description: Mapped[str] = mapped_column(Text, nullable=False)

    # Provider quote
    quote_description: Mapped[Optional[str]] = mapped_column(Text)
    labor_hours: Mapped[Optional[float]] = mapped_column(Float)
    labor_rate: Mapped[Optional[float]] = mapped_column(Float)
    materials_cost: Mapped[Optional[float]] = mapped_column(Float)
    total_amount: Mapped[Optional[float]] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    deposit_required: Mapped[Optional[float]] = mapped_column(Float)
    estimated_days: Mapped[Optional[int]] = mapped_column(Integer)
    quote_valid_days: Mapped[int] = mapped_column(Integer, default=7)

    # Communication
    customer_message: Mapped[Optional[str]] = mapped_column(Text)
    provider_message: Mapped[Optional[str]] = mapped_column(Text)
    decline_reason: Mapped[Optional[str]] = mapped_column(Text)
    cancel_reason: Mapped[Optional[str]] = mapped_column(Text)

    # Idempotency
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(100), unique=True)

    # Relationships
    customer: Mapped["BHUser"] = relationship(foreign_keys=[customer_id])
    provider: Mapped["BHUser"] = relationship(foreign_keys=[provider_id])
    listing: Mapped["BHListing"] = relationship()
