"""Deposit model.

Tracks security deposits on rentals:
- HELD: Deposit collected at rental start
- RELEASED: Returned to renter after successful return
- FORFEITED: Kept by owner due to damage/loss (via dispute resolution)
- PARTIAL_RELEASE: Partial return (damage deducted)
"""

import enum
import uuid
from typing import Optional

from sqlalchemy import Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, BHBase


class DepositStatus(str, enum.Enum):
    HELD = "held"
    RELEASED = "released"
    FORFEITED = "forfeited"
    PARTIAL_RELEASE = "partial_release"


class BHDeposit(BHBase, Base):
    """A security deposit on a rental."""

    __tablename__ = "bh_deposit"

    rental_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_rental.id"), nullable=False, unique=True, index=True
    )
    payer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False
    )
    recipient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False
    )

    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    status: Mapped[DepositStatus] = mapped_column(
        Enum(DepositStatus), default=DepositStatus.HELD, nullable=False, index=True
    )

    # Release/forfeit details
    released_amount: Mapped[Optional[float]] = mapped_column(Float)
    forfeited_amount: Mapped[Optional[float]] = mapped_column(Float)
    reason: Mapped[Optional[str]] = mapped_column(Text)

    # Payment reference (PayPal transaction ID)
    payment_ref: Mapped[Optional[str]] = mapped_column(String(200))
    refund_ref: Mapped[Optional[str]] = mapped_column(String(200))

    # Relationships
    rental: Mapped["BHRental"] = relationship()
    payer: Mapped["BHUser"] = relationship(foreign_keys=[payer_id])
    recipient: Mapped["BHUser"] = relationship(foreign_keys=[recipient_id])
