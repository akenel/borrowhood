"""Leaderboard + per-user event stats."""

import calendar as cal_mod
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.dependencies import get_current_user_token, get_user, require_auth, user_throttle
from src.models.event_rsvp import BHEventRSVP, RSVPStatus
from src.models.item import BHItem
from src.models.listing import BHListing, ListingStatus, ListingType
from src.models.user import BHUser
from src.schemas.event_rsvp import RSVPCreate, RSVPInfo, RSVPOut

from ._shared import _check_achievements

router = APIRouter()

@router.get("/leaderboard")
async def get_leaderboard(
    token: Optional[dict] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db),
):
    """Event leaderboard: top attendees, best streaks, top hosts.

    Public endpoint -- anonymous visitors should see the community activity
    without having to log in (social proof on first visit).
    """
    from src.models.user import BHUserPoints

    # Top attendees
    top_attendees_q = await db.execute(
        select(
            BHUser.display_name,
            BHUser.slug,
            BHUser.avatar_url,
            BHUser.badge_tier,
            BHUser.no_show_count,
            BHUserPoints.events_attended,
            BHUserPoints.event_streak,
            BHUserPoints.best_streak,
            BHUserPoints.total_points,
        )
        .join(BHUserPoints, BHUserPoints.user_id == BHUser.id)
        .where(BHUserPoints.events_attended > 0)
        .order_by(BHUserPoints.events_attended.desc())
        .limit(20)
    )
    top_attendees = [
        {
            "display_name": r[0], "slug": r[1], "avatar_url": r[2],
            "badge_tier": r[3].value if r[3] else "newcomer",
            "no_show_count": r[4] or 0,
            "events_attended": r[5] or 0, "event_streak": r[6] or 0,
            "best_streak": r[7] or 0, "total_points": r[8] or 0,
        }
        for r in top_attendees_q.all()
    ]

    # Top streaks (current)
    top_streaks_q = await db.execute(
        select(
            BHUser.display_name, BHUser.slug, BHUser.avatar_url,
            BHUserPoints.event_streak, BHUserPoints.best_streak,
        )
        .join(BHUserPoints, BHUserPoints.user_id == BHUser.id)
        .where(BHUserPoints.event_streak > 0)
        .order_by(BHUserPoints.event_streak.desc())
        .limit(10)
    )
    top_streaks = [
        {"display_name": r[0], "slug": r[1], "avatar_url": r[2],
         "event_streak": r[3] or 0, "best_streak": r[4] or 0}
        for r in top_streaks_q.all()
    ]

    # Top hosts
    top_hosts_q = await db.execute(
        select(
            BHUser.display_name, BHUser.slug, BHUser.avatar_url,
            BHUserPoints.events_hosted, BHUserPoints.total_points,
        )
        .join(BHUserPoints, BHUserPoints.user_id == BHUser.id)
        .where(BHUserPoints.events_hosted > 0)
        .order_by(BHUserPoints.events_hosted.desc())
        .limit(10)
    )
    top_hosts = [
        {"display_name": r[0], "slug": r[1], "avatar_url": r[2],
         "events_hosted": r[3] or 0, "total_points": r[4] or 0}
        for r in top_hosts_q.all()
    ]

    return {
        "top_attendees": top_attendees,
        "top_streaks": top_streaks,
        "top_hosts": top_hosts,
    }


@router.get("/my-stats")
async def get_my_stats(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Current user's event stats, achievements, and rank."""
    user = await get_user(db, token)

    from src.models.user import BHUserPoints
    pts_result = await db.execute(
        select(BHUserPoints).where(BHUserPoints.user_id == user.id)
    )
    pts = pts_result.scalar_one_or_none()

    # Get achievements
    from src.models.achievement import ACHIEVEMENTS, BHAchievement
    ach_result = await db.execute(
        select(BHAchievement).where(BHAchievement.user_id == user.id)
        .order_by(BHAchievement.unlocked_at.desc())
    )
    user_achievements = [
        {
            "key": a.achievement_key,
            "tier": a.tier.value,
            "unlocked_at": a.unlocked_at.isoformat() if a.unlocked_at else None,
            **{k: v for k, v in ACHIEVEMENTS.get(a.achievement_key, {}).items()
               if k in ("name", "name_it", "desc", "desc_it", "icon")},
        }
        for a in ach_result.scalars().all()
    ]

    # Calculate rank (position among all attendees)
    rank = None
    if pts and (pts.events_attended or 0) > 0:
        rank_count = await db.scalar(
            select(func.count()).select_from(BHUserPoints)
            .where(BHUserPoints.events_attended > (pts.events_attended or 0))
        )
        rank = (rank_count or 0) + 1

    # Next achievement to unlock
    unlocked_keys = {a["key"] for a in user_achievements}
    next_achievements = []
    for key, ach in ACHIEVEMENTS.items():
        if key in unlocked_keys:
            continue
        trigger = ach["trigger"]
        current = 0
        if trigger == "events_attended":
            current = pts.events_attended if pts else 0
        elif trigger == "event_streak":
            current = pts.event_streak if pts else 0
        elif trigger == "events_hosted":
            current = pts.events_hosted if pts else 0
        progress = min(100, int((current / ach["threshold"]) * 100)) if ach["threshold"] > 0 else 0
        if progress > 0:
            next_achievements.append({
                "key": key, "name": ach["name"], "name_it": ach["name_it"],
                "icon": ach["icon"], "tier": ach["tier"],
                "progress": progress, "current": current, "target": ach["threshold"],
            })
    next_achievements.sort(key=lambda x: -x["progress"])

    return {
        "events_attended": pts.events_attended if pts else 0,
        "events_hosted": pts.events_hosted if pts else 0,
        "event_streak": pts.event_streak if pts else 0,
        "best_streak": pts.best_streak if pts else 0,
        "total_points": pts.total_points if pts else 0,
        "no_show_count": user.no_show_count or 0,
        "rank": rank,
        "achievements": user_achievements,
        "next_achievements": next_achievements[:5],
    }


