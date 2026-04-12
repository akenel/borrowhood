"""Event RSVP API.

Handles registration, cancellation, attendance tracking, RSVP info,
and calendar feed for event-type listings.
"""

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

router = APIRouter(prefix="/api/v1/events", tags=["events"])


@router.post("/{listing_id}/rsvp", response_model=RSVPOut, status_code=201)
async def create_rsvp(
    listing_id: UUID,
    data: RSVPCreate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
    _throttle=Depends(user_throttle("event_rsvp", 20, 3600)),
):
    """Register for an event. Auto-waitlists if at capacity."""
    user = await get_user(db, token)

    # Verify listing exists, is an event, and is active
    listing = await db.get(BHListing, listing_id)
    if not listing or listing.deleted_at:
        raise HTTPException(status_code=404, detail="Event not found")
    if listing.listing_type != ListingType.EVENT:
        raise HTTPException(status_code=400, detail="This listing is not an event")
    if listing.status != ListingStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Event is not active")

    # Check if already registered
    existing = await db.execute(
        select(BHEventRSVP).where(
            BHEventRSVP.listing_id == listing_id,
            BHEventRSVP.user_id == user.id,
            BHEventRSVP.status.in_([RSVPStatus.REGISTERED, RSVPStatus.WAITLISTED]),
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Already registered for this event")

    # Check capacity
    registered_count = await db.scalar(
        select(func.count()).where(
            BHEventRSVP.listing_id == listing_id,
            BHEventRSVP.status == RSVPStatus.REGISTERED,
        )
    )

    # Short leash: repeat no-shows get auto-waitlisted
    status = RSVPStatus.REGISTERED
    if user.no_show_count >= 2:
        status = RSVPStatus.WAITLISTED  # Earn your spot back
    elif listing.max_participants and registered_count >= listing.max_participants:
        status = RSVPStatus.WAITLISTED

    rsvp = BHEventRSVP(
        listing_id=listing_id,
        user_id=user.id,
        status=status,
        notes=data.notes,
    )
    db.add(rsvp)
    await db.commit()
    await db.refresh(rsvp)
    return rsvp


@router.delete("/{listing_id}/rsvp", status_code=200)
async def cancel_rsvp(
    listing_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Cancel RSVP. Auto-promotes first waitlisted user if applicable."""
    user = await get_user(db, token)

    result = await db.execute(
        select(BHEventRSVP).where(
            BHEventRSVP.listing_id == listing_id,
            BHEventRSVP.user_id == user.id,
            BHEventRSVP.status.in_([RSVPStatus.REGISTERED, RSVPStatus.WAITLISTED]),
        )
    )
    rsvp = result.scalar_one_or_none()
    if not rsvp:
        raise HTTPException(status_code=404, detail="No active RSVP found")

    was_registered = rsvp.status == RSVPStatus.REGISTERED
    rsvp.status = RSVPStatus.CANCELLED

    # Auto-promote first waitlisted if a registered spot opened
    if was_registered:
        waitlisted = await db.execute(
            select(BHEventRSVP)
            .where(
                BHEventRSVP.listing_id == listing_id,
                BHEventRSVP.status == RSVPStatus.WAITLISTED,
            )
            .order_by(BHEventRSVP.registered_at.asc())
            .limit(1)
        )
        next_in_line = waitlisted.scalar_one_or_none()
        if next_in_line:
            next_in_line.status = RSVPStatus.REGISTERED

    await db.commit()
    return {"detail": "RSVP cancelled"}


@router.get("/{listing_id}/rsvp", response_model=RSVPInfo)
async def get_rsvp_info(
    listing_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Get RSVP count, capacity, and current user's status."""
    user = await get_user(db, token)

    listing = await db.get(BHListing, listing_id)
    if not listing or listing.deleted_at:
        raise HTTPException(status_code=404, detail="Event not found")

    registered_count = await db.scalar(
        select(func.count()).where(
            BHEventRSVP.listing_id == listing_id,
            BHEventRSVP.status == RSVPStatus.REGISTERED,
        )
    )

    # Check current user's RSVP
    result = await db.execute(
        select(BHEventRSVP).where(
            BHEventRSVP.listing_id == listing_id,
            BHEventRSVP.user_id == user.id,
            BHEventRSVP.status.in_([RSVPStatus.REGISTERED, RSVPStatus.WAITLISTED]),
        )
    )
    user_rsvp = result.scalar_one_or_none()

    return RSVPInfo(
        count=registered_count,
        capacity=listing.max_participants,
        is_registered=user_rsvp is not None,
        user_status=user_rsvp.status if user_rsvp else None,
    )


@router.patch("/{listing_id}/rsvp/{rsvp_id}/attend", response_model=RSVPOut)
async def mark_attended(
    listing_id: UUID,
    rsvp_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Event owner marks an attendee as having attended."""
    user = await get_user(db, token)

    # Verify ownership via listing -> item -> owner
    listing = await db.get(BHListing, listing_id)
    if not listing or listing.deleted_at:
        raise HTTPException(status_code=404, detail="Event not found")

    from src.models.item import BHItem
    item = await db.get(BHItem, listing.item_id)
    if item.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Only event owner can mark attendance")

    rsvp = await db.get(BHEventRSVP, rsvp_id)
    if not rsvp or rsvp.listing_id != listing_id:
        raise HTTPException(status_code=404, detail="RSVP not found")
    if rsvp.status != RSVPStatus.REGISTERED:
        raise HTTPException(status_code=400, detail="Can only mark registered attendees")

    rsvp.status = RSVPStatus.ATTENDED

    # Award points for showing up (+10)
    from src.services.reputation import award_points
    await award_points(db, rsvp.user_id, 10, "event_attended")

    # Update streak and attendance counter
    from src.models.user import BHUserPoints
    pts_result = await db.execute(
        select(BHUserPoints).where(BHUserPoints.user_id == rsvp.user_id)
    )
    user_pts = pts_result.scalar_one_or_none()
    if user_pts:
        user_pts.events_attended = (user_pts.events_attended or 0) + 1
        user_pts.event_streak = (user_pts.event_streak or 0) + 1
        if user_pts.event_streak > (user_pts.best_streak or 0):
            user_pts.best_streak = user_pts.event_streak
        # Streak bonus: +5 extra for every 3 in a row
        if user_pts.event_streak > 0 and user_pts.event_streak % 3 == 0:
            await award_points(db, rsvp.user_id, 5, "streak_bonus")

    # Check and unlock achievements
    await _check_achievements(db, rsvp.user_id)

    await db.commit()
    await db.refresh(rsvp)
    return rsvp


@router.post("/{listing_id}/close")
async def close_event(
    listing_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Close an event: mark remaining REGISTERED as NO_SHOW, deduct points.

    Call this after the event. Nic checks in the kids who showed up (mark_attended),
    then closes the event. Anyone still REGISTERED = didn't show = loses points.
    """
    user = await get_user(db, token)

    listing = await db.get(BHListing, listing_id)
    if not listing or listing.deleted_at:
        raise HTTPException(status_code=404, detail="Event not found")
    if listing.listing_type != ListingType.EVENT:
        raise HTTPException(status_code=400, detail="Not an event listing")

    from src.models.item import BHItem
    item = await db.get(BHItem, listing.item_id)
    if item.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Only event owner can close the event")

    # Find all RSVPs still REGISTERED (not attended, not cancelled)
    result = await db.execute(
        select(BHEventRSVP).where(
            BHEventRSVP.listing_id == listing_id,
            BHEventRSVP.status == RSVPStatus.REGISTERED,
        )
    )
    no_shows = result.scalars().all()

    no_show_count = 0
    for rsvp in no_shows:
        rsvp.status = RSVPStatus.NO_SHOW
        no_show_count += 1

        # Deduct points (-15) and increment no-show counter
        no_show_user = await db.get(BHUser, rsvp.user_id)
        if no_show_user:
            no_show_user.no_show_count = (no_show_user.no_show_count or 0) + 1
        from src.services.reputation import award_points
        await award_points(db, rsvp.user_id, -15, "event_no_show")

        # Break their streak -- back to zero
        from src.models.user import BHUserPoints
        pts_result = await db.execute(
            select(BHUserPoints).where(BHUserPoints.user_id == rsvp.user_id)
        )
        ns_pts = pts_result.scalar_one_or_none()
        if ns_pts:
            ns_pts.event_streak = 0  # Streak broken. Start over.

    # Update host stats
    from src.models.user import BHUserPoints
    host_pts_result = await db.execute(
        select(BHUserPoints).where(BHUserPoints.user_id == user.id)
    )
    host_pts = host_pts_result.scalar_one_or_none()
    if host_pts:
        host_pts.events_hosted = (host_pts.events_hosted or 0) + 1

    # Check host achievements
    await _check_achievements(db, user.id)

    # Mark event as expired (it's done)
    listing.status = ListingStatus.EXPIRED

    # Count who actually showed up
    attended_count = await db.scalar(
        select(func.count()).where(
            BHEventRSVP.listing_id == listing_id,
            BHEventRSVP.status == RSVPStatus.ATTENDED,
        )
    )

    await db.commit()
    return {
        "detail": "Event closed",
        "attended": attended_count,
        "no_shows": no_show_count,
    }


# ── Achievement checker ──────────────────────────────────────────

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


# ── Leaderboard ──────────────────────────────────────────────────

@router.get("/leaderboard")
async def get_leaderboard(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Event leaderboard: top attendees, best streaks, top hosts."""
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


# ── Calendar feed ───────────────────────────────────────────────

@router.get("/calendar")
async def calendar_events(
    month: int = Query(default=None),
    year: int = Query(default=None),
    db: AsyncSession = Depends(get_db),
    token: Optional[dict] = Depends(get_current_user_token),
):
    """Events for a given month, with RSVP counts and user status.

    Returns events grouped by date for the calendar grid, plus a flat list
    for the event cards below.
    """
    now = datetime.now(timezone.utc)
    if not month:
        month = now.month
    if not year:
        year = now.year

    # Month boundaries (UTC)
    _, last_day = cal_mod.monthrange(year, month)
    start = datetime(year, month, 1, tzinfo=timezone.utc)
    end = datetime(year, month, last_day, 23, 59, 59, tzinfo=timezone.utc)

    # Fetch active event listings in this month range
    result = await db.execute(
        select(BHListing)
        .options(
            selectinload(BHListing.item).selectinload(BHItem.owner),
            selectinload(BHListing.item).selectinload(BHItem.media),
        )
        .where(
            BHListing.listing_type == ListingType.EVENT,
            BHListing.status.in_([ListingStatus.ACTIVE, ListingStatus.EXPIRED]),
            BHListing.event_start.isnot(None),
            BHListing.event_start <= end,
            # Include events that started before month but end during it
            func.coalesce(BHListing.event_end, BHListing.event_start) >= start,
        )
        .order_by(BHListing.event_start.asc())
    )
    listings = result.scalars().unique().all()

    # RSVP counts (registered only)
    listing_ids = [l.id for l in listings]
    rsvp_counts = {}
    if listing_ids:
        counts_result = await db.execute(
            select(BHEventRSVP.listing_id, func.count(BHEventRSVP.id))
            .where(
                BHEventRSVP.listing_id.in_(listing_ids),
                BHEventRSVP.status == RSVPStatus.REGISTERED,
            )
            .group_by(BHEventRSVP.listing_id)
        )
        rsvp_counts = dict(counts_result.all())

    # Current user's RSVPs
    user_rsvps = {}
    if token:
        try:
            user = await get_user(db, token)
            if listing_ids:
                user_rsvp_result = await db.execute(
                    select(BHEventRSVP.listing_id, BHEventRSVP.status)
                    .where(
                        BHEventRSVP.listing_id.in_(listing_ids),
                        BHEventRSVP.user_id == user.id,
                        BHEventRSVP.status.in_([RSVPStatus.REGISTERED, RSVPStatus.WAITLISTED]),
                    )
                )
                user_rsvps = {str(r[0]): r[1].value for r in user_rsvp_result.all()}
        except Exception:
            pass

    # Build response
    events = []
    for listing in listings:
        item = listing.item
        if not item or item.deleted_at:
            continue
        owner = item.owner
        media = item.media
        first_image = None
        if media:
            for m in media:
                if m.media_type and m.media_type.value in ("photo", "PHOTO"):
                    first_image = m.url
                    break

        events.append({
            "id": str(listing.id),
            "item_id": str(item.id),
            "item_slug": item.slug,
            "title": item.name,
            "description": (item.description or "")[:200],
            "event_start": listing.event_start.isoformat() if listing.event_start else None,
            "event_end": listing.event_end.isoformat() if listing.event_end else None,
            "event_venue": listing.event_venue,
            "event_address": listing.event_address,
            "event_link": listing.event_link,
            "price": listing.price,
            "capacity": listing.max_participants,
            "rsvp_count": rsvp_counts.get(listing.id, 0),
            "user_rsvp": user_rsvps.get(str(listing.id)),
            "status": listing.status.value,
            "image": first_image,
            "owner_name": owner.display_name if owner else None,
            "owner_slug": owner.slug if owner else None,
            "owner_avatar": owner.avatar_url if owner else None,
            "day": listing.event_start.day if listing.event_start else None,
        })

    return {
        "year": year,
        "month": month,
        "events": events,
    }
