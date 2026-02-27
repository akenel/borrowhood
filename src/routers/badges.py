"""Badge API: view earned badges, trigger badge check.

Badges are awarded automatically based on milestones.
This router lets users view their badges and manually trigger recalculation.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies import require_auth
from src.models.badge import BHBadge, BadgeCode, BADGE_INFO
from src.models.user import BHUser
from src.services.badges import check_and_award_badges

router = APIRouter(prefix="/api/v1/badges", tags=["badges"])


class BadgeOut(BaseModel):
    id: UUID
    badge_code: str
    name: str
    description: str
    icon: str
    color: str
    reason: str | None = None
    earned_at: str


@router.get("", response_model=List[BadgeOut])
async def list_my_badges(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List all badges earned by the authenticated user."""
    user_result = await db.execute(
        select(BHUser).where(BHUser.keycloak_id == token.get("sub", ""))
    )
    user = user_result.scalars().first()
    if not user:
        raise HTTPException(status_code=403, detail="User not provisioned")

    result = await db.execute(
        select(BHBadge)
        .where(BHBadge.user_id == user.id)
        .order_by(BHBadge.created_at.desc())
    )
    badges = result.scalars().all()

    return [
        BadgeOut(
            id=b.id,
            badge_code=b.badge_code.value,
            name=BADGE_INFO.get(b.badge_code, {}).get("name", b.badge_code.value),
            description=BADGE_INFO.get(b.badge_code, {}).get("description", ""),
            icon=BADGE_INFO.get(b.badge_code, {}).get("icon", "star"),
            color=BADGE_INFO.get(b.badge_code, {}).get("color", "gray"),
            reason=b.reason,
            earned_at=b.created_at.isoformat(),
        )
        for b in badges
    ]


@router.get("/user/{user_id}", response_model=List[BadgeOut])
async def list_user_badges(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """List badges for a specific user. Public endpoint."""
    result = await db.execute(
        select(BHBadge)
        .where(BHBadge.user_id == user_id)
        .order_by(BHBadge.created_at.desc())
    )
    badges = result.scalars().all()

    return [
        BadgeOut(
            id=b.id,
            badge_code=b.badge_code.value,
            name=BADGE_INFO.get(b.badge_code, {}).get("name", b.badge_code.value),
            description=BADGE_INFO.get(b.badge_code, {}).get("description", ""),
            icon=BADGE_INFO.get(b.badge_code, {}).get("icon", "star"),
            color=BADGE_INFO.get(b.badge_code, {}).get("color", "gray"),
            reason=b.reason,
            earned_at=b.created_at.isoformat(),
        )
        for b in badges
    ]


@router.post("/check")
async def check_badges(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Trigger badge check for current user. Returns newly awarded badges."""
    user_result = await db.execute(
        select(BHUser).where(BHUser.keycloak_id == token.get("sub", ""))
    )
    user = user_result.scalars().first()
    if not user:
        raise HTTPException(status_code=403, detail="User not provisioned")

    awarded = await check_and_award_badges(db, user.id)
    await db.commit()

    return {
        "checked": True,
        "new_badges": [
            {
                "badge_code": b.badge_code.value,
                "name": BADGE_INFO.get(b.badge_code, {}).get("name", b.badge_code.value),
            }
            for b in awarded
        ],
    }


@router.get("/catalog")
async def badge_catalog():
    """List all available badges and how to earn them. Public endpoint."""
    return [
        {
            "code": code.value,
            "name": info["name"],
            "description": info["description"],
            "icon": info["icon"],
            "color": info["color"],
        }
        for code, info in BADGE_INFO.items()
    ]
