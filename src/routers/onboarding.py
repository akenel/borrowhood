"""Onboarding API.

Handles new user profile setup after first Keycloak login.
Creates/updates user profile, workshop details, and languages in one shot.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from slugify import slugify
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies import require_auth
from src.models.user import (
    AccountStatus,
    BadgeTier,
    BHUser,
    BHUserLanguage,
    CEFRLevel,
    WorkshopType,
)

router = APIRouter(prefix="/api/v1/onboarding", tags=["onboarding"])


class LanguageIn(BaseModel):
    language_code: str = Field(..., max_length=5)
    proficiency: str = Field(default="B2", max_length=10)


class ProfileSetup(BaseModel):
    display_name: str = Field(..., min_length=2, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    country_code: Optional[str] = Field(None, max_length=2)
    bio: Optional[str] = Field(None, max_length=500)
    telegram_username: Optional[str] = Field(None, max_length=50)
    workshop_name: Optional[str] = Field(None, max_length=100)
    workshop_type: Optional[str] = Field(None, max_length=20)
    tagline: Optional[str] = Field(None, max_length=200)
    languages: List[LanguageIn] = []


async def _unique_slug(db: AsyncSession, base: str) -> str:
    """Generate unique slug from display name."""
    slug = slugify(base)
    counter = 0
    candidate = slug
    while True:
        existing = await db.scalar(
            select(BHUser.id).where(BHUser.slug == candidate)
        )
        if not existing:
            return candidate
        counter += 1
        candidate = f"{slug}-{counter}"


@router.post("/profile")
async def setup_profile(
    profile: ProfileSetup,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Create or update user profile during onboarding."""
    keycloak_id = token["sub"]
    email = token.get("email", "")
    username = token.get("preferred_username", "")

    # Check if user already exists by keycloak_id
    result = await db.execute(
        select(BHUser).where(BHUser.keycloak_id == keycloak_id)
    )
    user = result.scalars().first()

    # Fallback: link seed user by slug on first KC login
    if not user and username:
        result = await db.execute(
            select(BHUser).where(BHUser.slug == username)
        )
        user = result.scalars().first()
        if user:
            user.keycloak_id = keycloak_id

    if user:
        # Update existing
        user.display_name = profile.display_name
        user.city = profile.city
        user.country_code = profile.country_code
        user.bio = profile.bio
        user.telegram_username = profile.telegram_username
        if profile.workshop_name:
            user.workshop_name = profile.workshop_name
        if profile.workshop_type:
            try:
                user.workshop_type = WorkshopType(profile.workshop_type)
            except ValueError:
                pass
        if profile.tagline:
            user.tagline = profile.tagline
    else:
        # Create new
        slug = await _unique_slug(db, profile.display_name)
        workshop_type = None
        if profile.workshop_type:
            try:
                workshop_type = WorkshopType(profile.workshop_type)
            except ValueError:
                pass

        user = BHUser(
            keycloak_id=keycloak_id,
            email=email,
            display_name=profile.display_name,
            slug=slug,
            city=profile.city,
            country_code=profile.country_code,
            bio=profile.bio,
            telegram_username=profile.telegram_username,
            workshop_name=profile.workshop_name,
            workshop_type=workshop_type,
            tagline=profile.tagline,
            account_status=AccountStatus.ACTIVE,
            badge_tier=BadgeTier.NEWCOMER,
        )
        db.add(user)
        await db.flush()

    # Update languages
    if profile.languages:
        # Delete existing
        existing_langs = await db.execute(
            select(BHUserLanguage).where(BHUserLanguage.user_id == user.id)
        )
        for lang in existing_langs.scalars().all():
            await db.delete(lang)

        # Add new
        for lang in profile.languages:
            if lang.language_code:
                try:
                    proficiency = CEFRLevel(lang.proficiency)
                except ValueError:
                    proficiency = CEFRLevel.B2

                db.add(BHUserLanguage(
                    user_id=user.id,
                    language_code=lang.language_code,
                    proficiency=proficiency,
                ))

    await db.flush()

    # Check badges (WORKSHOP_PRO, MULTILINGUAL, EARLY_ADOPTER)
    from src.services.badges import check_and_award_badges
    await check_and_award_badges(db, user.id)

    await db.commit()
    return {"status": "ok", "user_id": str(user.id), "slug": user.slug}
