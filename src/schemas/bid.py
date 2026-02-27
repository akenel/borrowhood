"""Pydantic schemas for bid/auction endpoints."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.models.bid import BidStatus


class BidOut(BaseModel):
    id: UUID
    listing_id: UUID
    bidder_id: UUID
    amount: float
    currency: str
    status: BidStatus
    is_winning: bool
    created_at: str

    class Config:
        from_attributes = True


class BidCreate(BaseModel):
    listing_id: UUID
    amount: float = Field(..., gt=0)


class AuctionSummary(BaseModel):
    listing_id: UUID
    total_bids: int
    current_price: Optional[float] = None
    winning_bidder_id: Optional[UUID] = None
    auction_end: Optional[str] = None
    reserve_met: bool = True
