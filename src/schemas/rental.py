"""Pydantic schemas for rental endpoints."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.models.rental import RentalStatus


class RentalOut(BaseModel):
    id: UUID
    listing_id: UUID
    renter_id: UUID
    status: RentalStatus
    requested_start: Optional[datetime] = None
    requested_end: Optional[datetime] = None
    actual_pickup: Optional[datetime] = None
    actual_return: Optional[datetime] = None
    renter_message: Optional[str] = None
    owner_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RentalCreate(BaseModel):
    listing_id: UUID
    requested_start: Optional[datetime] = None
    requested_end: Optional[datetime] = None
    renter_message: Optional[str] = Field(None, max_length=1000)
    safety_acknowledged: Optional[bool] = False
    idempotency_key: Optional[str] = Field(None, max_length=36)
    participant_count: Optional[int] = Field(None, ge=1, le=200)


class RentalStatusUpdate(BaseModel):
    status: RentalStatus
    message: Optional[str] = Field(None, max_length=1000)
    reason: Optional[str] = Field(None, max_length=500)
