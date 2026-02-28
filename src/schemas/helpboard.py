"""Pydantic schemas for the Help Board."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.models.helpboard import HelpStatus, HelpType, HelpUrgency


class HelpPostCreate(BaseModel):
    help_type: HelpType
    title: str = Field(..., min_length=5, max_length=200)
    body: Optional[str] = None
    category: str = Field(..., max_length=50)
    urgency: HelpUrgency = HelpUrgency.NORMAL
    neighborhood: Optional[str] = Field(None, max_length=100)
    content_language: str = Field(default="en", max_length=5)


class HelpPostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    author_id: UUID
    help_type: HelpType
    status: HelpStatus
    urgency: HelpUrgency
    title: str
    body: Optional[str] = None
    category: str
    content_language: str
    neighborhood: Optional[str] = None
    reply_count: int
    created_at: datetime


class HelpReplyCreate(BaseModel):
    body: str = Field(..., min_length=1, max_length=2000)


class HelpReplyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    post_id: UUID
    author_id: UUID
    body: str
    created_at: datetime
