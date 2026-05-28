"""Pydantic schemas for messaging endpoints."""

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ShareAddressRequest(BaseModel):
    """Share the sender's profile address with the recipient in a 1:1 thread.

    'exact' = full street address + precise coords.
    'approx' = no street_line; coordinates blurred to 500m (see location_privacy).
    hide_after_days = if set, the recipient sees "[address hidden]" past that mark.
    """
    recipient_id: UUID
    mode: Literal["exact", "approx"] = "exact"
    hide_after_days: Optional[int] = Field(None, ge=1, le=90)


class MessageCreate(BaseModel):
    recipient_id: UUID
    body: str = Field(..., min_length=1, max_length=5000)
    listing_id: Optional[UUID] = None
    rental_id: Optional[UUID] = None


class MessageUpdate(BaseModel):
    body: str = Field(..., min_length=1, max_length=5000)


class MessageOut(BaseModel):
    id: UUID
    sender_id: UUID
    recipient_id: UUID
    body: str
    message_type: str = "text"
    listing_id: Optional[UUID] = None
    rental_id: Optional[UUID] = None
    offered_price: Optional[float] = None
    offer_status: Optional[str] = None
    offer_round: Optional[int] = None
    expires_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    edited_at: Optional[datetime] = None
    created_at: datetime
    sender_name: Optional[str] = None
    sender_avatar: Optional[str] = None
    body_meta: Optional[dict] = None  # structured payload (e.g. address_share)

    class Config:
        from_attributes = True


class ThreadSummary(BaseModel):
    other_user_id: UUID
    other_user_name: str
    other_user_avatar: Optional[str] = None
    last_message: str
    last_message_at: datetime
    unread_count: int
    listing_id: Optional[UUID] = None
    rental_id: Optional[UUID] = None


class MessageSummary(BaseModel):
    unread: int


# ── Offer schemas ──


class OfferCreate(BaseModel):
    listing_id: UUID
    offered_price: float = Field(..., gt=0, le=100000)
    message: str = Field("", max_length=500)


class CounterOffer(BaseModel):
    offered_price: float = Field(..., gt=0, le=100000)
    message: str = Field("", max_length=500)
