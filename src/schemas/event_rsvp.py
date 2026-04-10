"""Pydantic schemas for event RSVP endpoints."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from src.models.event_rsvp import RSVPStatus


class RSVPCreate(BaseModel):
    notes: Optional[str] = None


class RSVPOut(BaseModel):
    id: UUID
    listing_id: UUID
    user_id: UUID
    status: RSVPStatus
    notes: Optional[str] = None
    registered_at: datetime

    class Config:
        from_attributes = True


class RSVPInfo(BaseModel):
    """Public RSVP info for an event listing."""
    count: int
    capacity: Optional[int] = None
    is_registered: bool = False
    user_status: Optional[RSVPStatus] = None
