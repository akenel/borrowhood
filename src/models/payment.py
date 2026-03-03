"""Payment model.

Tracks all monetary transactions: rental payments, deposits, refunds.
Supports PayPal (primary) with extensibility for Stripe later.
"""

import enum
import uuid
from typing import Optional

from sqlalchemy import Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, BHBase


class PaymentProvider(str, enum.Enum):
    PAYPAL = "paypal"
    STRIPE = "stripe"
    MANUAL = "manual"  # Cash, bank transfer, etc.


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"       # Order created, awaiting buyer approval
    COMPLETED = "completed"   # Payment captured
    FAILED = "failed"         # Payment failed
    REFUNDED = "refunded"     # Full refund
    PARTIAL_REFUND = "partial_refund"


class PaymentType(str, enum.Enum):
    RENTAL = "rental"         # Rental fee
    DEPOSIT = "deposit"       # Security deposit
    PURCHASE = "purchase"     # Buy outright
    AUCTION = "auction"       # Auction winning bid
    SERVICE = "service"       # Service fee


class BHPayment(BHBase, Base):
    """A payment transaction."""

    __tablename__ = "bh_payment"

    # Who pays whom
    payer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )
    payee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )

    # What for
    rental_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_rental.id"), index=True
    )
    payment_type: Mapped[PaymentType] = mapped_column(
        Enum(PaymentType), nullable=False
    )

    # Amount
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")

    # Provider
    provider: Mapped[PaymentProvider] = mapped_column(
        Enum(PaymentProvider), default=PaymentProvider.PAYPAL, nullable=False
    )
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False, index=True
    )

    # Provider references
    provider_order_id: Mapped[Optional[str]] = mapped_column(String(200))  # PayPal order ID
    provider_capture_id: Mapped[Optional[str]] = mapped_column(String(200))  # PayPal capture ID
    provider_refund_id: Mapped[Optional[str]] = mapped_column(String(200))

    # Marketplace split (Stripe Connect)
    platform_fee: Mapped[Optional[float]] = mapped_column(Float)
    seller_payout_amount: Mapped[Optional[float]] = mapped_column(Float)

    # Refund tracking
    refund_amount: Mapped[Optional[float]] = mapped_column(Float)
    refund_reason: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    payer: Mapped["BHUser"] = relationship(foreign_keys=[payer_id])
    payee: Mapped["BHUser"] = relationship(foreign_keys=[payee_id])
    rental: Mapped[Optional["BHRental"]] = relationship()
