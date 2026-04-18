"""Skills CRUD + AI skill suggestions."""

import json
import uuid as uuid_mod
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy import case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.dependencies import get_current_user_token, get_user, require_auth
from src.models.audit import BHAuditLog
from src.models.deposit import BHDeposit, DepositStatus
from src.models.dispute import BHDispute, DisputeStatus
from src.models.item import BHItem
from src.models.listing import BHListing, ListingStatus
from src.models.rental import BHRental, RentalStatus
from src.models.quote import BHServiceQuote, QuoteStatus
from src.models.telegram import BHTelegramLink
from src.models.user import AccountStatus, BadgeTier, BHUser, BHUserFavorite, WorkshopType
from src.services.search import haversine_km
from src.schemas.user import (
    FavoriteCreate,
    FavoriteOut,
    MemberCardOut,
    PaginatedMembers,
)

from ._shared import UPLOAD_DIR, BANNER_DIR, ALLOWED_AVATAR_TYPES, MAX_AVATAR_SIZE, MAX_BANNER_SIZE, _BADGE_SORT

router = APIRouter()

# ── Skills CRUD + AI Suggestions ────────────────────────────────────

from pydantic import BaseModel, Field
from src.models.user import BHUserSkill


class SkillCreate(BaseModel):
    skill_name: str = Field(..., min_length=2, max_length=100)
    category: str = Field(..., max_length=50)
    self_rating: int = Field(default=3, ge=1, le=5)
    years_experience: Optional[int] = Field(None, ge=0, le=60)


class SkillOut(BaseModel):
    id: UUID
    skill_name: str
    category: str
    self_rating: int
    years_experience: Optional[int] = None
    verified_by_count: int = 0

    class Config:
        from_attributes = True


@router.get("/me/skills", response_model=List[SkillOut])
async def list_my_skills(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List current user's skills."""
    user = await get_user(db, token)
    result = await db.execute(
        select(BHUserSkill)
        .where(BHUserSkill.user_id == user.id)
        .where(BHUserSkill.deleted_at.is_(None))
        .order_by(BHUserSkill.created_at)
    )
    return result.scalars().all()


@router.post("/me/skills", response_model=SkillOut, status_code=201)
async def add_skill(
    data: SkillCreate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Add a skill to current user's profile."""
    user = await get_user(db, token)

    # Check for duplicate
    existing = await db.execute(
        select(BHUserSkill)
        .where(BHUserSkill.user_id == user.id)
        .where(func.lower(BHUserSkill.skill_name) == data.skill_name.lower())
        .where(BHUserSkill.deleted_at.is_(None))
    )
    if existing.scalars().first():
        raise HTTPException(status_code=409, detail="Skill already exists")

    skill = BHUserSkill(
        user_id=user.id,
        skill_name=data.skill_name,
        category=data.category,
        self_rating=data.self_rating,
        years_experience=data.years_experience,
    )
    db.add(skill)

    from src.services.badges import check_and_award_badges
    await db.flush()
    await check_and_award_badges(db, user.id)

    await db.commit()
    await db.refresh(skill)
    return skill


@router.post("/me/skills/batch", status_code=201)
async def add_skills_batch(
    request: Request,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Add multiple skills at once (used by AI suggest flow)."""
    user = await get_user(db, token)
    body = await request.json()
    skills_data = body.get("skills", [])
    if not skills_data or len(skills_data) > 10:
        raise HTTPException(status_code=400, detail="Provide 1-10 skills")

    # Get existing skill names for dedup
    existing_result = await db.execute(
        select(func.lower(BHUserSkill.skill_name))
        .where(BHUserSkill.user_id == user.id)
        .where(BHUserSkill.deleted_at.is_(None))
    )
    existing_names = {row[0] for row in existing_result.all()}

    added = []
    for s in skills_data:
        name = s.get("skill_name", "").strip()
        if not name or name.lower() in existing_names:
            continue
        skill = BHUserSkill(
            user_id=user.id,
            skill_name=name,
            category=s.get("category", "other"),
            self_rating=max(1, min(5, s.get("self_rating", 3))),
            years_experience=s.get("years_experience"),
        )
        db.add(skill)
        existing_names.add(name.lower())
        added.append(name)

    if added:
        from src.services.badges import check_and_award_badges
        await db.flush()
        await check_and_award_badges(db, user.id)
        await db.commit()

    return {"added": len(added), "skills": added}


@router.delete("/me/skills/{skill_id}", status_code=200)
async def delete_skill(
    skill_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Remove a skill from current user's profile."""
    user = await get_user(db, token)
    result = await db.execute(
        select(BHUserSkill)
        .where(BHUserSkill.id == skill_id)
        .where(BHUserSkill.user_id == user.id)
    )
    skill = result.scalars().first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    await db.delete(skill)
    await db.commit()
    return {"status": "deleted", "skill_name": skill.skill_name}


@router.post("/me/skills/suggest")
async def suggest_skills(
    request: Request,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """AI-powered skill suggestions from user's bio.

    Accepts optional {bio: "..."} in request body to use unsaved form text.
    Falls back to the saved bio from the database.
    """
    user = await get_user(db, token)

    # Use bio from request body (form field) if provided, else DB
    body = await request.json() if request else {}
    bio_text = (body.get("bio") or "").strip() if body else ""
    if not bio_text:
        bio_text = (user.bio or "").strip()

    if len(bio_text) < 20:
        raise HTTPException(status_code=400, detail="Bio must be at least 20 characters for skill extraction")

    # Get existing skills to avoid duplicates
    existing_result = await db.execute(
        select(BHUserSkill.skill_name)
        .where(BHUserSkill.user_id == user.id)
        .where(BHUserSkill.deleted_at.is_(None))
    )
    existing_skills = [row[0] for row in existing_result.all()]

    from src.services.gemini import suggest_skills_from_bio
    suggestions, provider = await suggest_skills_from_bio(bio_text, existing_skills)

    if not suggestions:
        raise HTTPException(status_code=503, detail="AI service unavailable")

    return {"suggestions": suggestions, "provider": provider}


