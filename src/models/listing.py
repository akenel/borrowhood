"""Listing model: how an item is offered (rent, sell, commission, etc.)

One item can have multiple listings (e.g., available for rent AND sale).
"""

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, BHBase


class ListingType(str, enum.Enum):
    RENT = "rent"             # Borrow and return
    SELL = "sell"             # Transfer ownership
    COMMISSION = "commission" # Made-to-order
    OFFER = "offer"           # Free / "make an offer"
    SERVICE = "service"       # "I'll do it for you"
    TRAINING = "training"     # "I'll teach you"
    AUCTION = "auction"       # Timed bidding
    GIVEAWAY = "giveaway"     # Free, take it, no return
    EVENT = "event"           # Workshop, concert, meetup, garage sale
    RAFFLE = "raffle"         # Community fundraising, ticket-based draw


class ListingStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"      # Awaiting moderator approval
    ACTIVE = "active"
    PAUSED = "paused"
    EXPIRED = "expired"
    REMOVED = "removed"  # By moderator


class BHListing(BHBase, Base):
    """A specific offer for an item: type, price, terms."""

    __tablename__ = "bh_listing"

    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_item.id"), nullable=False, index=True
    )

    # Offer details
    listing_type: Mapped[ListingType] = mapped_column(Enum(ListingType), nullable=False, index=True)
    status: Mapped[ListingStatus] = mapped_column(
        Enum(ListingStatus), default=ListingStatus.DRAFT, nullable=False, index=True
    )

    # Pricing (optional -- "make an offer" has no price)
    price: Mapped[Optional[float]] = mapped_column(Float)
    price_unit: Mapped[Optional[str]] = mapped_column(String(20))  # "per_day", "per_hour", "flat", "negotiable"
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    deposit: Mapped[Optional[float]] = mapped_column(Float)

    # Terms
    min_rental_days: Mapped[Optional[int]] = mapped_column(Integer)
    max_rental_days: Mapped[Optional[int]] = mapped_column(Integer)
    available_from: Mapped[Optional[str]] = mapped_column(String(10))  # "2026-03-01"
    available_to: Mapped[Optional[str]] = mapped_column(String(10))    # "2026-09-30" (seasonal)
    delivery_available: Mapped[bool] = mapped_column(default=False)
    pickup_only: Mapped[bool] = mapped_column(default=True)
    delivery_fee: Mapped[Optional[float]] = mapped_column(Float)  # EUR, leave NULL for free delivery
    notes: Mapped[Optional[str]] = mapped_column(Text)
    return_policy: Mapped[Optional[str]] = mapped_column(String(500))  # Seller-defined return terms
    # MVP availability note (free text). Signals preferred hours / days off / vacation.
    # Full rule-based availability will replace this -- see docs/AVAILABILITY-DESIGN.md.
    availability_note: Mapped[Optional[str]] = mapped_column(String(500))

    # BL-001: Structured blackout dates. JSONB shape:
    #   {
    #     "ranges": [{"from": "2026-06-01", "to": "2026-06-30", "reason": "Holidays"}, ...],
    #     "recurring_weekdays": [5, 6]   # Python weekday: Mon=0 ... Sun=6
    #   }
    # Used by is_blocked() helper to gate booking creation.
    blackout_dates: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)

    def is_blocked(self, target_date) -> bool:
        """Return True if target_date (date or ISO string 'YYYY-MM-DD') is blocked.

        A date is blocked when:
        - its weekday (Mon=0..Sun=6) is in blackout_dates.recurring_weekdays, OR
        - it falls within any range in blackout_dates.ranges (inclusive).
        """
        from datetime import date as _date
        bd = self.blackout_dates or {}
        if isinstance(target_date, str):
            target_date = _date.fromisoformat(target_date)
        if target_date.weekday() in bd.get("recurring_weekdays", []):
            return True
        target_iso = target_date.isoformat()
        for r in bd.get("ranges", []):
            f, t = r.get("from"), r.get("to")
            if f and t and f <= target_iso <= t:
                return True
        return False

    # Minimum charge + team pricing (service/training listings)
    minimum_charge: Mapped[Optional[float]] = mapped_column(Float)     # Floor price regardless of hours/days
    per_person_rate: Mapped[Optional[float]] = mapped_column(Float)    # Per-participant rate (training/workshops)
    max_participants: Mapped[Optional[int]] = mapped_column(Integer)   # Group size cap
    group_discount_pct: Mapped[Optional[float]] = mapped_column(Float) # % discount for 3+ people (0-100)

    # Auction fields (only used when listing_type == AUCTION)
    auction_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    starting_bid: Mapped[Optional[float]] = mapped_column(Float)
    reserve_price: Mapped[Optional[float]] = mapped_column(Float)  # Hidden minimum
    bid_increment: Mapped[Optional[float]] = mapped_column(Float, default=1.0)

    # Event fields (only used when listing_type == EVENT)
    event_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    event_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    event_venue: Mapped[Optional[str]] = mapped_column(String(200))   # Venue name
    event_address: Mapped[Optional[str]] = mapped_column(String(500)) # Full address
    event_link: Mapped[Optional[str]] = mapped_column(String(1000))   # Online event URL (Zoom/Meet/YouTube)

    # Human-readable evergreen schedule line for the printed Locandina ("Ogni
    # giovedi 20:00 fino al 1 dicembre"). A full RRULE recurrence engine is
    # deliberately deferred; owner types this verbatim and the flyer prints it.
    schedule_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Version for optimistic locking (Rule 28)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Relationships
    item: Mapped["BHItem"] = relationship(back_populates="listings")
    rentals: Mapped[list["BHRental"]] = relationship(back_populates="listing")
    bids: Mapped[list["BHBid"]] = relationship(back_populates="listing")
