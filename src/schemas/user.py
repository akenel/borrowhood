"""Pydantic schemas for user endpoints."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from src.models.user import AccountStatus, BadgeTier, CEFRLevel, WorkshopType


class UserLanguageOut(BaseModel):
    language_code: str
    proficiency: CEFRLevel

    class Config:
        from_attributes = True


class UserSkillOut(BaseModel):
    skill_name: str
    category: str
    self_rating: int
    verified_by_count: int

    class Config:
        from_attributes = True


class UserSocialLinkOut(BaseModel):
    platform: str
    url: str
    label: Optional[str] = None

    class Config:
        from_attributes = True


class UserOut(BaseModel):
    """Public user/workshop profile."""
    id: UUID
    display_name: str
    slug: str
    workshop_name: Optional[str] = None
    workshop_type: Optional[WorkshopType] = None
    tagline: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    banner_url: Optional[str] = None
    telegram_username: Optional[str] = None
    city: Optional[str] = None
    country_code: Optional[str] = None
    badge_tier: BadgeTier
    languages: List[UserLanguageOut] = []
    skills: List[UserSkillOut] = []
    social_links: List[UserSocialLinkOut] = []

    class Config:
        from_attributes = True


class MemberCardOut(BaseModel):
    """Lightweight member card for directory listings."""
    id: UUID
    display_name: str
    slug: str
    workshop_name: Optional[str] = None
    workshop_type: Optional[WorkshopType] = None
    tagline: Optional[str] = None
    avatar_url: Optional[str] = None
    city: Optional[str] = None
    country_code: Optional[str] = None
    badge_tier: BadgeTier
    languages: List[UserLanguageOut] = []

    class Config:
        from_attributes = True


class PaginatedMembers(BaseModel):
    """Paginated response for members directory."""
    items: List[MemberCardOut]
    total: int
    limit: int
    offset: int
    has_more: bool


class FavoriteCreate(BaseModel):
    """Create a favorite with optional note."""
    note: Optional[str] = Field(None, max_length=200)


class FavoriteOut(BaseModel):
    """Favorite with nested member card."""
    id: UUID
    favorite_user_id: UUID
    note: Optional[str] = None
    created_at: datetime
    favorite_user: MemberCardOut

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    """Fields a user can update on their own profile."""
    display_name: Optional[str] = Field(None, max_length=100)
    workshop_name: Optional[str] = Field(None, max_length=100)
    workshop_type: Optional[WorkshopType] = None
    tagline: Optional[str] = Field(None, max_length=200)
    bio: Optional[str] = None
    telegram_username: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    country_code: Optional[str] = Field(None, max_length=2)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    notify_telegram: Optional[bool] = None
    notify_email: Optional[bool] = None


class UserLanguageCreate(BaseModel):
    language_code: str = Field(..., max_length=5)
    proficiency: CEFRLevel
