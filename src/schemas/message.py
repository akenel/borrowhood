"""Pydantic schemas for messaging endpoints."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


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
    listing_id: Optional[UUID] = None
    rental_id: Optional[UUID] = None
    read_at: Optional[datetime] = None
    edited_at: Optional[datetime] = None
    created_at: datetime
    sender_name: Optional[str] = None
    sender_avatar: Optional[str] = None

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
