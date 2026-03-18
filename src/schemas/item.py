"""Pydantic schemas for item endpoints."""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.models.item import ItemCategory, ItemCondition, ItemType, MediaType


class ItemMediaOut(BaseModel):
    id: UUID
    media_type: MediaType
    url: str
    thumbnail_url: Optional[str] = None
    alt_text: str

    class Config:
        from_attributes = True


class ItemOut(BaseModel):
    """Item detail response."""
    id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    story: Optional[str] = None
    content_language: str
    item_type: ItemType
    category: str
    subcategory: Optional[str] = None
    condition: Optional[ItemCondition] = None
    brand: Optional[str] = None
    tags: Optional[str] = None
    needs_equipment: Optional[str] = None
    compatible_with: Optional[str] = None
    owner_id: UUID
    media: List[ItemMediaOut] = []

    class Config:
        from_attributes = True


class ItemCreate(BaseModel):
    """Create a new item."""
    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    story: Optional[str] = None
    content_language: str = Field(default="en", max_length=5)
    item_type: ItemType
    category: ItemCategory
    subcategory: Optional[str] = Field(None, max_length=50)
    condition: Optional[ItemCondition] = None
    brand: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    age_restricted: bool = False
    safety_notes: Optional[str] = None
    tags: Optional[str] = None
    needs_equipment: Optional[str] = None
    compatible_with: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ItemUpdate(BaseModel):
    """Update an existing item."""
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = None
    story: Optional[str] = None
    content_language: Optional[str] = Field(None, max_length=5)
    category: Optional[ItemCategory] = None
    subcategory: Optional[str] = Field(None, max_length=50)
    condition: Optional[ItemCondition] = None
    brand: Optional[str] = Field(None, max_length=100)
    tags: Optional[str] = None
    needs_equipment: Optional[str] = None
    compatible_with: Optional[str] = None
