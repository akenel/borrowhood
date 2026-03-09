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
    skill_name: Optional[str] = None
    skill_rating: Optional[int] = None
    reviewer_tier: str
    weight: float
    visible: bool
    photo_urls: Optional[list] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewCreate(BaseModel):
    rental_id: UUID
    reviewee_id: UUID
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = Field(None, max_length=200)
    body: Optional[str] = None
    content_language: str = Field(default="en", max_length=5)
    skill_name: Optional[str] = Field(None, max_length=100)
    skill_rating: Optional[int] = Field(None, ge=1, le=5)
