"""Pydantic schemas for the Help Board."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.models.helpboard import HelpMediaType, HelpStatus, HelpType, HelpUrgency


# ── Post schemas ──

class HelpPostCreate(BaseModel):
    help_type: HelpType
    title: str = Field(..., min_length=5, max_length=200)
    body: Optional[str] = None
    category: str = Field(..., max_length=50)
    urgency: HelpUrgency = HelpUrgency.NORMAL
    neighborhood: Optional[str] = Field(None, max_length=100)
    content_language: str = Field(default="en", max_length=5)
    item_id: Optional[UUID] = None  # tag a specific item


class HelpMediaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    media_type: HelpMediaType
    url: str
    filename: str
    file_size: int
    content_type: str
    alt_text: Optional[str] = None
    thumbnail_url: Optional[str] = None
    sort_order: int = 0
    created_at: datetime


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
    item_id: Optional[UUID] = None
    resolved_by_id: Optional[UUID] = None
    reply_count: int
    upvote_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    # Enriched fields (set by router)
    author_name: Optional[str] = None
    author_slug: Optional[str] = None
    author_avatar: Optional[str] = None
    resolved_by_name: Optional[str] = None
    item_name: Optional[str] = None
    item_slug: Optional[str] = None
    media: list[HelpMediaOut] = []
    user_upvoted: bool = False


class PaginatedPosts(BaseModel):
    items: list[HelpPostOut]
    total: int
    limit: int
    offset: int
    has_more: bool


# ── Reply schemas ──

class HelpReplyCreate(BaseModel):
    body: str = Field(..., min_length=1, max_length=2000)
    parent_reply_id: Optional[UUID] = None  # for threading


class HelpReplyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    post_id: UUID
    author_id: UUID
    body: str
    parent_reply_id: Optional[UUID] = None
    upvote_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    # Enriched
    author_name: Optional[str] = None
    author_slug: Optional[str] = None
    author_avatar: Optional[str] = None
    media: list[HelpMediaOut] = []
    children: list["HelpReplyOut"] = []


# ── Edit schemas ──

class HelpReplyUpdate(BaseModel):
    body: str = Field(..., min_length=1, max_length=2000)

class HelpPostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    body: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    urgency: Optional[HelpUrgency] = None
    neighborhood: Optional[str] = Field(None, max_length=100)
    item_id: Optional[UUID] = None


# ── Resolve schema ──

class ResolvePost(BaseModel):
    resolved_by_id: Optional[UUID] = None  # if omitted, author self-resolves


# ── AI Draft schema ──

class HelpDraftRequest(BaseModel):
    """Ask AI to draft a help post from a short description."""
    description: str = Field(..., min_length=5, max_length=500)
    help_type: HelpType = HelpType.NEED
    language: str = Field(default="en", max_length=5)


class HelpDraftResponse(BaseModel):
    title: str = ""
    body: str = ""
    category: str = ""
    urgency: str = "normal"
    estimated_value: Optional[float] = None
    value_explanation: str = ""
    suggestions: list[str] = []
    ai_provider: str = ""
