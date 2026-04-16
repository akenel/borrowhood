"""Raffle models: community fundraising via ticket-based draws.

A raffle is a listing type where an organizer sells tickets at a fixed
price. When the draw triggers (by date, sellout, or manually), a
provably fair random winner is selected from the confirmed ticket pool.

Progressive trust tiers limit max raffle value based on organizer's
completed-raffle history. La Piazza never touches money — all payments
happen off-platform, same as every other listing type.

Lifecycle:
    draft → published → active → drawn → completed
                      ↘ cancelled

Ticket lifecycle:
    reserved → confirmed → (in draw pool)
             → expired   → (released back)
             → cancelled → (released back)
"""

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, CheckConstraint, DateTime, Enum, Float, ForeignKey,
    Integer, String, Text, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, BHBase


class RaffleStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ACTIVE = "active"
    DRAWN = "drawn"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RaffleDrawType(str, enum.Enum):
    DATE = "date"           # Draw at draw_date
    SOLDOUT = "soldout"     # Draw when max_tickets reached
    MANUAL = "manual"       # Organizer triggers manually


class RaffleDelivery(str, enum.Enum):
    PICKUP = "pickup"
    SHIPPING = "shipping"
    DIGITAL = "digital"


class RaffleTicketStatus(str, enum.Enum):
    RESERVED = "reserved"
    CONFIRMED = "confirmed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


# Progressive trust tiers: max raffle value doubles with each clean completion
RAFFLE_TRUST_TIERS = [
    # (completed_count, max_total_eur)
    (0, 10),
    (1, 20),
    (2, 40),
    (3, 80),
    (4, 160),
    (5, 320),
]
RAFFLE_HARD_CEILING_EUR = 320
RAFFLE_MIN_TICKET_PRICE_EUR = 0.10
RAFFLE_MIN_DURATION_HOURS = 24
RAFFLE_MAX_DURATION_DAYS = 30
TICKET_HOLD_HOURS_DEFAULT = 48
DRAW_BUFFER_DAYS = 3
WINNER_RESPONSE_HOURS = 72
ORGANIZER_INACTION_DAYS = 6


def max_raffle_value_for(completed_count: int) -> float:
    """Return max total raffle value (ticket_price * max_tickets) allowed."""
    for threshold, limit in reversed(RAFFLE_TRUST_TIERS):
        if completed_count >= threshold:
            return min(limit, RAFFLE_HARD_CEILING_EUR)
    return RAFFLE_TRUST_TIERS[0][1]


class BHRaffle(BHBase, Base):
    """Raffle details — one-to-one with a RAFFLE-type BHListing."""

    __tablename__ = "bh_raffle"

    listing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_listing.id"), nullable=False, unique=True, index=True
    )
    organizer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )

    # Ticket config
    ticket_price: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    max_tickets: Mapped[Optional[int]] = mapped_column(Integer)
    max_tickets_per_user: Mapped[Optional[int]] = mapped_column(Integer)
    tickets_sold: Mapped[int] = mapped_column(Integer, default=0)
    tickets_reserved: Mapped[int] = mapped_column(Integer, default=0)
    ticket_hold_hours: Mapped[int] = mapped_column(Integer, default=TICKET_HOLD_HOURS_DEFAULT)

    # Draw config
    draw_type: Mapped[RaffleDrawType] = mapped_column(
        Enum(RaffleDrawType), default=RaffleDrawType.DATE, nullable=False
    )
    draw_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[RaffleStatus] = mapped_column(
        Enum(RaffleStatus), default=RaffleStatus.DRAFT, nullable=False, index=True
    )

    # Payment (off-platform, organizer-managed)
    payment_methods: Mapped[Optional[list]] = mapped_column(ARRAY(String(50)))
    payment_instructions: Mapped[Optional[str]] = mapped_column(Text)

    # Delivery
    delivery_method: Mapped[Optional[RaffleDelivery]] = mapped_column(Enum(RaffleDelivery))
    shipping_notes: Mapped[Optional[str]] = mapped_column(Text)

    # Draw result
    winner_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=True
    )
    winner_ticket_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    drawn_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Provably fair draw — seed published before draw, verifiable after
    draw_seed: Mapped[Optional[str]] = mapped_column(String(128))
    draw_proof_hash: Mapped[Optional[str]] = mapped_column(String(128))

    # Progressive trust: organizer's completed raffle count at publish time
    organizer_raffle_count: Mapped[int] = mapped_column(Integer, default=0)

    # TOS acknowledgement
    tos_accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    # Verification stats (cached, rebuilt from BHRaffleVerification)
    verifications_positive: Mapped[int] = mapped_column(Integer, default=0)
    verifications_negative: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    listing: Mapped["BHListing"] = relationship()
    organizer: Mapped["BHUser"] = relationship(foreign_keys=[organizer_id])
    winner: Mapped[Optional["BHUser"]] = relationship(foreign_keys=[winner_user_id])
    tickets: Mapped[list["BHRaffleTicket"]] = relationship(
        back_populates="raffle", cascade="all, delete-orphan"
    )
    verifications: Mapped[list["BHRaffleVerification"]] = relationship(
        back_populates="raffle", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "ticket_price >= 0.10",
            name="ck_raffle_min_ticket_price",
        ),
        CheckConstraint(
            "(draw_date IS NOT NULL) OR (max_tickets IS NOT NULL)",
            name="ck_raffle_draw_trigger_required",
        ),
    )

    @property
    def verification_rate(self) -> float:
        total = self.verifications_positive + self.verifications_negative
        if total == 0:
            return 0.0
        return round(self.verifications_positive / total * 100, 1)


class BHRaffleTicket(BHBase, Base):
    """A ticket (or batch of tickets) purchased by a user for a raffle."""

    __tablename__ = "bh_raffle_ticket"

    raffle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_raffle.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )

    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    ticket_numbers: Mapped[Optional[list]] = mapped_column(ARRAY(Integer))

    status: Mapped[RaffleTicketStatus] = mapped_column(
        Enum(RaffleTicketStatus), default=RaffleTicketStatus.RESERVED, nullable=False, index=True
    )
    payment_method: Mapped[Optional[str]] = mapped_column(String(50))

    # Reservation expiry
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    raffle: Mapped["BHRaffle"] = relationship(back_populates="tickets")
    user: Mapped["BHUser"] = relationship()

    __table_args__ = (
        CheckConstraint("quantity >= 1", name="ck_ticket_min_quantity"),
    )


class BHRaffleVerification(BHBase, Base):
    """Post-draw community verification: was this raffle fair?

    Every confirmed ticket holder can verify once. Their vote feeds
    into the organizer's trust profile and determines whether the
    raffle counts as "completed cleanly" for progressive tier unlocks.
    """

    __tablename__ = "bh_raffle_verification"

    raffle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_raffle.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True,
    )

    # The vote
    is_fair: Mapped[bool] = mapped_column(Boolean, nullable=False)
    prize_delivered: Mapped[Optional[bool]] = mapped_column(Boolean)
    comment: Mapped[Optional[str]] = mapped_column(String(500))

    # Relationships
    raffle: Mapped["BHRaffle"] = relationship(back_populates="verifications")
    user: Mapped["BHUser"] = relationship()

    __table_args__ = (
        UniqueConstraint("raffle_id", "user_id", name="uq_raffle_verification_per_user"),
    )


# ── Points awards ──────────────────────────────────────────────────────

POINTS_RAFFLE_ORGANIZER_COMPLETE = 25      # Organizer ran a clean raffle
POINTS_RAFFLE_ORGANIZER_VERIFIED = 15      # Bonus when 80%+ positive verifications
POINTS_RAFFLE_TICKET_PURCHASE = 3          # Buyer confirmed ticket
POINTS_RAFFLE_WINNER = 10                  # Winner bonus
POINTS_RAFFLE_VERIFICATION = 5             # Participant submitted a verification
VERIFICATION_CLEAN_THRESHOLD = 0.80        # 80% positive = "completed cleanly"
