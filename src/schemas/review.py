"""Pydantic schemas for review endpoints."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ReviewOut(BaseModel):
    id: UUID
    rental_id: UUID
    reviewer_id: UUID
    reviewee_id: UUID
    rating: int
    title: Optional[str] = None
    body: Optional[str] = None
    content_language: str
    # Subcategory ratings
    rating_accuracy: Optional[int] = None
    rating_communication: Optional[int] = None
    rating_value: Optional[int] = None
    rating_timeliness: Optional[int] = None
    would_recommend: Optional[bool] = None
    # Skill
    skill_name: Optional[str] = None
    skill_rating: Optional[int] = None
    # Weight
    reviewer_tier: str
    weight: float
    visible: bool
    photo_urls: Optional[list] = None
    # Owner response
    owner_response: Optional[str] = None
    owner_response_at: Optional[datetime] = None
    # Voting
    helpful_count: int = 0
    not_helpful_count: int = 0
    # Reviewer display info (populated by API)
    reviewer_name: Optional[str] = None
    reviewer_avatar: Optional[str] = None
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReviewCreate(BaseModel):
    rental_id: UUID
    reviewee_id: UUID
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = Field(None, max_length=200)
    body: Optional[str] = None
    content_language: str = Field(default="en", max_length=5)
    # Subcategory ratings
    rating_accuracy: Optional[int] = Field(None, ge=1, le=5)
    rating_communication: Optional[int] = Field(None, ge=1, le=5)
    rating_value: Optional[int] = Field(None, ge=1, le=5)
    rating_timeliness: Optional[int] = Field(None, ge=1, le=5)
    would_recommend: Optional[bool] = None
    # Skill
    skill_name: Optional[str] = Field(None, max_length=100)
    skill_rating: Optional[int] = Field(None, ge=1, le=5)
