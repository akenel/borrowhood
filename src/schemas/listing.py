"""Pydantic schemas for listing endpoints."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.models.listing import ListingStatus, ListingType


class ListingOut(BaseModel):
    id: UUID
    item_id: UUID
    listing_type: ListingType
    status: ListingStatus
    price: Optional[float] = None
    price_unit: Optional[str] = None
    currency: str
    deposit: Optional[float] = None
    min_rental_days: Optional[int] = None
    max_rental_days: Optional[int] = None
    delivery_available: bool
    pickup_only: bool
    notes: Optional[str] = None
    return_policy: Optional[str] = None
    auction_end: Optional[datetime] = None
    starting_bid: Optional[float] = None
    bid_increment: Optional[float] = None
    minimum_charge: Optional[float] = None
    per_person_rate: Optional[float] = None
    max_participants: Optional[int] = None
    group_discount_pct: Optional[float] = None
    event_start: Optional[datetime] = None
    event_end: Optional[datetime] = None
    event_venue: Optional[str] = None
    event_address: Optional[str] = None
    event_link: Optional[str] = None
    availability_note: Optional[str] = None

    class Config:
        from_attributes = True


class ListingCreate(BaseModel):
    item_id: UUID
    listing_type: ListingType
    status: Optional[ListingStatus] = None  # None=active, "draft"=save without publishing
    price: Optional[float] = Field(None, ge=0)
    price_unit: Optional[str] = Field(None, max_length=20)
    currency: str = Field(default="EUR", max_length=3)
    deposit: Optional[float] = Field(None, ge=0)
    min_rental_days: Optional[int] = Field(None, ge=1)
    max_rental_days: Optional[int] = Field(None, ge=1)
    delivery_available: bool = False
    pickup_only: bool = True
    notes: Optional[str] = None
    return_policy: Optional[str] = Field(None, max_length=500)
    auction_end: Optional[str] = None  # ISO datetime for auction listings
    starting_bid: Optional[float] = Field(None, ge=0)
    reserve_price: Optional[float] = Field(None, ge=0)
    bid_increment: Optional[float] = Field(None, ge=0)
    minimum_charge: Optional[float] = Field(None, ge=0)
    per_person_rate: Optional[float] = Field(None, ge=0)
    max_participants: Optional[int] = Field(None, ge=1)
    group_discount_pct: Optional[float] = Field(None, ge=0, le=100)
    event_start: Optional[str] = None  # ISO datetime for event listings
    event_end: Optional[str] = None
    event_venue: Optional[str] = Field(None, max_length=200)
    event_address: Optional[str] = Field(None, max_length=500)
    event_link: Optional[str] = Field(None, max_length=1000)
    availability_note: Optional[str] = Field(None, max_length=500)


class ListingUpdate(BaseModel):
    status: Optional[ListingStatus] = None
    price: Optional[float] = Field(None, ge=0)
    price_unit: Optional[str] = Field(None, max_length=20)
    deposit: Optional[float] = Field(None, ge=0)
    delivery_available: Optional[bool] = None
    pickup_only: Optional[bool] = None
    notes: Optional[str] = None
    return_policy: Optional[str] = Field(None, max_length=500)
    auction_end: Optional[str] = None
    starting_bid: Optional[float] = Field(None, ge=0)
    reserve_price: Optional[float] = Field(None, ge=0)
    bid_increment: Optional[float] = Field(None, ge=0)
    minimum_charge: Optional[float] = Field(None, ge=0)
    per_person_rate: Optional[float] = Field(None, ge=0)
    max_participants: Optional[int] = Field(None, ge=1)
    group_discount_pct: Optional[float] = Field(None, ge=0, le=100)
    event_start: Optional[str] = None
    event_end: Optional[str] = None
    event_venue: Optional[str] = Field(None, max_length=200)
    event_address: Optional[str] = Field(None, max_length=500)
    event_link: Optional[str] = Field(None, max_length=1000)
    availability_note: Optional[str] = Field(None, max_length=500)
