"""Background task: auto-attend past events.

When an event's end time (or start + 24h fallback) is more than GRACE_HOURS
ago, any RSVPs still in REGISTERED get promoted to ATTENDED -- generous
default: trust that people who RSVP'd actually showed. The listing is
flipped to EXPIRED and the host's events_hosted counter bumps once.

Hosts who care about accuracy can still call mark_attended / close_event
within the grace window to flag NO_SHOWs explicitly. After the grace
window they get the benefit-of-the-doubt default.

Without this, RSVPs sit in REGISTERED forever, events_attended never
increments, and the leaderboard looks dead.
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import async_session
from src.models.event_rsvp import BHEventRSVP, RSVPStatus
from src.models.item import BHItem
from src.models.listing import BHListing, ListingStatus, ListingType
from src.models.user import BHUserPoints

logger = logging.getLogger("event_attendance")

# Run every 15 minutes
INTERVAL_SECONDS = 900

# Hours to wait past event end (or start + 24h fallback) before auto-attending
GRACE_HOURS = 6
FALLBACK_EVENT_DURATION_HOURS = 24


def _event_cutoff(listing: BHListing) -> datetime | None:
    """When should this event be considered 'done + grace expired'?"""
    if not listing.event_start:
        return None
    end = listing.event_end or (listing.event_start + timedelta(hours=FALLBACK_EVENT_DURATION_HOURS))
    return end + timedelta(hours=GRACE_HOURS)


async def auto_attend_past_events(db: AsyncSession) -> tuple[int, int]:
    """Promote REGISTERED RSVPs on past events to ATTENDED.

    Returns (events_closed, rsvps_promoted).
    """
    now = datetime.now(timezone.utc)

    # Active events with an event_start in the past
    q = (
        select(BHListing)
        .options(selectinload(BHListing.item))
        .where(BHListing.listing_type == ListingType.EVENT)
        .where(BHListing.status == ListingStatus.ACTIVE)
        .where(BHListing.event_start.is_not(None))
        .where(BHListing.event_start < now)
    )
    candidates = (await db.execute(q)).scalars().all()

    events_closed = 0
    rsvps_promoted = 0

    for listing in candidates:
        cutoff = _event_cutoff(listing)
        if not cutoff or cutoff > now:
            continue  # Still in grace window

        # Promote all REGISTERED RSVPs to ATTENDED
        rsvps = (await db.execute(
            select(BHEventRSVP).where(
                BHEventRSVP.listing_id == listing.id,
                BHEventRSVP.status == RSVPStatus.REGISTERED,
            )
        )).scalars().all()

        for rsvp in rsvps:
            rsvp.status = RSVPStatus.ATTENDED
            pts = await db.scalar(
                select(BHUserPoints).where(BHUserPoints.user_id == rsvp.user_id)
            )
            if pts:
                pts.events_attended = (pts.events_attended or 0) + 1
                pts.event_streak = (pts.event_streak or 0) + 1
                pts.total_points = (pts.total_points or 0) + 10
                if pts.event_streak > (pts.best_streak or 0):
                    pts.best_streak = pts.event_streak
            rsvps_promoted += 1

        # Host credit: +1 events_hosted per event, once
        host_id = listing.item.owner_id if listing.item else None
        if host_id:
            host_pts = await db.scalar(
                select(BHUserPoints).where(BHUserPoints.user_id == host_id)
            )
            if host_pts:
                host_pts.events_hosted = (host_pts.events_hosted or 0) + 1
                host_pts.total_points = (host_pts.total_points or 0) + 15

        # Close out the listing
        listing.status = ListingStatus.EXPIRED
        events_closed += 1
        logger.info(
            "Auto-attended event %s: promoted %d RSVPs, host=%s",
            listing.id, len(rsvps), host_id,
        )

    if events_closed:
        await db.commit()
        logger.info(
            "Auto-attend pass: %d events closed, %d RSVPs promoted",
            events_closed, rsvps_promoted,
        )

    return events_closed, rsvps_promoted


async def run_attendance_loop():
    """Background loop -- auto-attends past events every 15 minutes."""
    logger.info("Auto-attendance loop started (interval=%ds)", INTERVAL_SECONDS)
    while True:
        try:
            async with async_session() as db:
                await auto_attend_past_events(db)
        except Exception as e:
            logger.error("Auto-attendance error: %s", e, exc_info=True)
        await asyncio.sleep(INTERVAL_SECONDS)
