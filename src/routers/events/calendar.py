"""Calendar feed for the monthly grid."""

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


