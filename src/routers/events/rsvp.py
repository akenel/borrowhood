"""RSVP create/cancel/read/attend/close."""

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


