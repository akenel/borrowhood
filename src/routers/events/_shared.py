"""Shared helpers for events/ package."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import BHUser

async def _check_achievements(db: AsyncSession, user_id: UUID):
    """Check if user has unlocked any new achievements based on their stats."""
    from src.models.achievement import ACHIEVEMENTS, BHAchievement
    from src.models.user import BHUserPoints

    pts_result = await db.execute(
        select(BHUserPoints).where(BHUserPoints.user_id == user_id)
    )
    pts = pts_result.scalar_one_or_none()
    if not pts:
        return

    # Get already unlocked
    existing = await db.execute(
        select(BHAchievement.achievement_key).where(
            BHAchievement.user_id == user_id
        )
    )
    unlocked = {row[0] for row in existing.all()}

    # Check user for no-show info (for reliability achievement)
    user = await db.get(BHUser, user_id)

    for key, ach in ACHIEVEMENTS.items():
        if key in unlocked:
            continue

        triggered = False
        trigger = ach["trigger"]

        if trigger == "events_attended" and (pts.events_attended or 0) >= ach["threshold"]:
            triggered = True
        elif trigger == "event_streak" and (pts.event_streak or 0) >= ach["threshold"]:
            triggered = True
        elif trigger == "events_hosted" and (pts.events_hosted or 0) >= ach["threshold"]:
            triggered = True
        elif trigger == "reliability":
            if (pts.events_attended or 0) >= ach["threshold"] and (user.no_show_count or 0) == 0:
                triggered = True
        elif trigger == "comeback":
            if (user.no_show_count or 0) > 0 and (pts.event_streak or 0) >= ach["threshold"]:
                triggered = True

        if triggered:
            db.add(BHAchievement(
                user_id=user_id,
                achievement_key=key,
                tier=ach["tier"],
            ))
            # Bonus points for unlocking
            from src.services.reputation import award_points
            await award_points(db, user_id, ach["points"], f"achievement_{key}")

