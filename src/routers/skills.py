"""Skill verification API -- peer endorsement of user skills.

Rules:
- Can't verify your own skill
- One verification per user per skill (unique constraint)
- Verify increments verified_by_count, unverify decrements
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies import get_user, require_auth
from src.models.skill_verification import BHSkillVerification
from src.models.user import BHUserSkill

router = APIRouter(prefix="/api/v1/skills", tags=["skills"])


class VerifyRequest(BaseModel):
    comment: str = ""


class VerificationOut(BaseModel):
    id: UUID
    verifier_id: UUID
    skill_id: UUID
    comment: str | None = None
    created_at: str

    class Config:
        from_attributes = True


@router.post("/{skill_id}/verify", status_code=201)
async def verify_skill(
    skill_id: UUID,
    data: VerifyRequest = VerifyRequest(),
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Verify a neighbor's skill. Can't verify your own."""
    user = await get_user(db, token)

    # Get the skill
    result = await db.execute(
        select(BHUserSkill).where(BHUserSkill.id == skill_id)
    )
    skill = result.scalars().first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    # Can't verify own skill
    if skill.user_id == user.id:
        raise HTTPException(status_code=400, detail="Cannot verify your own skill")

    # Check for existing verification
    existing = await db.execute(
        select(BHSkillVerification)
        .where(BHSkillVerification.verifier_id == user.id)
        .where(BHSkillVerification.skill_id == skill_id)
    )
    if existing.scalars().first():
        raise HTTPException(status_code=409, detail="Already verified this skill")

    verification = BHSkillVerification(
        verifier_id=user.id,
        skill_id=skill_id,
        comment=data.comment or None,
    )
    db.add(verification)

    # Increment count
    skill.verified_by_count += 1

    # Check SKILL_MASTER badge and recalculate trust score
    from src.services.badges import check_and_award_badges
    from src.services.reputation import calculate_trust_score
    await db.flush()
    await check_and_award_badges(db, skill.user_id)
    await calculate_trust_score(db, skill.user_id)

    await db.commit()
    return {"status": "verified", "verified_by_count": skill.verified_by_count}


@router.delete("/{skill_id}/verify")
async def unverify_skill(
    skill_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Remove your verification of a skill."""
    user = await get_user(db, token)

    result = await db.execute(
        select(BHSkillVerification)
        .where(BHSkillVerification.verifier_id == user.id)
        .where(BHSkillVerification.skill_id == skill_id)
    )
    verification = result.scalars().first()
    if not verification:
        raise HTTPException(status_code=404, detail="Verification not found")

    # Decrement count
    skill_result = await db.execute(
        select(BHUserSkill).where(BHUserSkill.id == skill_id)
    )
    skill = skill_result.scalars().first()
    if skill and skill.verified_by_count > 0:
        skill.verified_by_count -= 1

    await db.delete(verification)

    # Recalculate trust score
    if skill:
        from src.services.reputation import calculate_trust_score
        await calculate_trust_score(db, skill.user_id)

    await db.commit()
    return {"status": "unverified", "verified_by_count": skill.verified_by_count if skill else 0}


@router.get("/{skill_id}/verified")
async def check_my_verification(
    skill_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Check if the current user has verified this skill."""
    user = await get_user(db, token)
    result = await db.execute(
        select(BHSkillVerification)
        .where(BHSkillVerification.verifier_id == user.id)
        .where(BHSkillVerification.skill_id == skill_id)
    )
    verification = result.scalars().first()
    return {"verified": verification is not None}


@router.get("/{skill_id}/verifications")
async def list_verifications(
    skill_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """List all verifiers of a skill. Public endpoint."""
    result = await db.execute(
        select(BHSkillVerification)
        .where(BHSkillVerification.skill_id == skill_id)
        .order_by(BHSkillVerification.created_at.desc())
    )
    verifications = result.scalars().all()
    return [
        {
            "id": str(v.id),
            "verifier_id": str(v.verifier_id),
            "comment": v.comment,
            "created_at": v.created_at.isoformat(),
        }
        for v in verifications
    ]
