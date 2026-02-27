"""Bid model for auction listings.

Users place bids on AUCTION-type listings. Each bid records the amount,
the bidder, and whether it's the current winning bid.
"""

import enum
import uuid
from typing import Optional

from sqlalchemy import Boolean, Enum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, BHBase


class BidStatus(str, enum.Enum):
    ACTIVE = "active"         # Current valid bid
    OUTBID = "outbid"         # Superseded by a higher bid
    WON = "won"               # Auction ended, this bid won
    CANCELLED = "cancelled"   # Bidder withdrew (if allowed)
    RESERVE_NOT_MET = "reserve_not_met"  # Auction ended below reserve


class BHBid(BHBase, Base):
    """A bid on an auction listing."""

    __tablename__ = "bh_bid"

    listing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_listing.id"), nullable=False, index=True
    )
    bidder_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )

    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    status: Mapped[BidStatus] = mapped_column(
        Enum(BidStatus), default=BidStatus.ACTIVE, nullable=False, index=True
    )
    is_winning: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    listing: Mapped["BHListing"] = relationship(back_populates="bids")
    bidder: Mapped["BHUser"] = relationship()
