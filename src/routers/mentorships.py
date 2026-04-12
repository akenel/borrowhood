"""Mentorship API: propose, accept, log progress, complete."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.dependencies import get_user, require_auth
from src.models.mentorship import BHMentorship, MentorshipStatus, MentorshipType
from src.models.user import BHUser

router = APIRouter(prefix="/api/v1/mentorships", tags=["mentorships"])


class MentorshipCreate(BaseModel):
    other_user_id: UUID
    role: str = Field(pattern="^(mentor|apprentice)$")
    skill_name: str = Field(max_length=100)
    skill_category: str = Field(max_length=50)
    mentorship_type: str = Field(default="apprentice", pattern="^(mentor|apprentice|intern)$")
    goal: Optional[str] = Field(None, max_length=500)


class MentorshipStatusUpdate(BaseModel):
    status: str = Field(pattern="^(active|paused|completed|cancelled)$")


class MentorshipProgress(BaseModel):
    hours: Optional[int] = Field(None, ge=0)
    milestones: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=2000)


class MentorshipOut(BaseModel):
    id: UUID
    mentor_id: UUID
    apprentice_id: UUID
    mentor_name: Optional[str] = None
    mentor_slug: Optional[str] = None
    apprentice_name: Optional[str] = None
    apprentice_slug: Optional[str] = None
    mentorship_type: str
    status: str
    skill_name: str
    skill_category: str
    hours_logged: int
    milestones_completed: int
    goal: Optional[str] = None
    notes: Optional[str] = None


def _to_out(m: BHMentorship) -> dict:
    return {
        "id": m.id,
        "mentor_id": m.mentor_id,
        "apprentice_id": m.apprentice_id,
        "mentor_name": m.mentor.display_name if m.mentor else None,
        "mentor_slug": m.mentor.slug if m.mentor else None,
        "apprentice_name": m.apprentice.display_name if m.apprentice else None,
        "apprentice_slug": m.apprentice.slug if m.apprentice else None,
        "mentorship_type": m.mentorship_type.value,
        "status": m.status.value,
        "skill_name": m.skill_name,
        "skill_category": m.skill_category,
        "hours_logged": m.hours_logged or 0,
        "milestones_completed": m.milestones_completed or 0,
        "goal": m.goal,
        "notes": m.notes,
    }


@router.get("", response_model=List[MentorshipOut])
async def list_mentorships(
    status: Optional[str] = None,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List user's mentorships (as mentor or apprentice)."""
    user = await get_user(db, token)
    query = (
        select(BHMentorship)
        .options(selectinload(BHMentorship.mentor), selectinload(BHMentorship.apprentice))
        .where(or_(BHMentorship.mentor_id == user.id, BHMentorship.apprentice_id == user.id))
        .where(BHMentorship.deleted_at.is_(None))
    )
    if status:
        query = query.where(BHMentorship.status == status)
    query = query.order_by(BHMentorship.created_at.desc())
    result = await db.execute(query)
    return [_to_out(m) for m in result.scalars().all()]


@router.post("", response_model=MentorshipOut, status_code=201)
async def create_mentorship(
    data: MentorshipCreate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Propose a mentorship. Role = your role (mentor or apprentice)."""
    user = await get_user(db, token)
    other = await db.get(BHUser, data.other_user_id)
    if not other or other.deleted_at:
        raise HTTPException(status_code=404, detail="User not found")
    if other.id == user.id:
        raise HTTPException(status_code=400, detail="Cannot mentor yourself")

    if data.role == "mentor":
        mentor_id, apprentice_id = user.id, other.id
    else:
        mentor_id, apprentice_id = other.id, user.id

    m = BHMentorship(
        mentor_id=mentor_id,
        apprentice_id=apprentice_id,
        mentorship_type=MentorshipType(data.mentorship_type),
        status=MentorshipStatus.PROPOSED,
        skill_name=data.skill_name,
        skill_category=data.skill_category,
        goal=data.goal,
    )
    db.add(m)
    await db.commit()
    await db.refresh(m, attribute_names=["mentor", "apprentice"])
    result = await db.execute(
        select(BHMentorship)
        .options(selectinload(BHMentorship.mentor), selectinload(BHMentorship.apprentice))
        .where(BHMentorship.id == m.id)
    )
    return _to_out(result.scalar_one())


@router.patch("/{mentorship_id}/status", response_model=MentorshipOut)
async def update_mentorship_status(
    mentorship_id: UUID,
    data: MentorshipStatusUpdate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Accept, pause, complete, or cancel a mentorship."""
    user = await get_user(db, token)
    result = await db.execute(
        select(BHMentorship)
        .options(selectinload(BHMentorship.mentor), selectinload(BHMentorship.apprentice))
        .where(BHMentorship.id == mentorship_id)
    )
    m = result.scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail="Mentorship not found")
    if m.mentor_id != user.id and m.apprentice_id != user.id:
        raise HTTPException(status_code=403, detail="Not your mentorship")

    m.status = MentorshipStatus(data.status)
    await db.commit()
    await db.refresh(m)
    return _to_out(m)


@router.patch("/{mentorship_id}/progress", response_model=MentorshipOut)
async def log_progress(
    mentorship_id: UUID,
    data: MentorshipProgress,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Log hours, milestones, or notes on a mentorship."""
    user = await get_user(db, token)
    result = await db.execute(
        select(BHMentorship)
        .options(selectinload(BHMentorship.mentor), selectinload(BHMentorship.apprentice))
        .where(BHMentorship.id == mentorship_id)
    )
    m = result.scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail="Mentorship not found")
    if m.mentor_id != user.id and m.apprentice_id != user.id:
        raise HTTPException(status_code=403, detail="Not your mentorship")

    if data.hours is not None:
        m.hours_logged = data.hours
    if data.milestones is not None:
        m.milestones_completed = data.milestones
    if data.notes is not None:
        m.notes = data.notes
    await db.commit()
    await db.refresh(m)
    return _to_out(m)
