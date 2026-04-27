"""Community pages: helpboard, calendar, raffles, chat."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.config import settings
from src.database import get_db
from src.dependencies import get_current_user_token, get_user
from src.i18n import detect_language, get_translator, SUPPORTED_LANGUAGES
from src.models.item import ATTRIBUTE_SCHEMAS, BHItem, CATEGORY_GROUPS
from src.models.listing import BHListing, ListingStatus, ListingType
from src.models.rental import BHRental, RentalStatus
from src.models.review import BHReview
from src.models.badge import BADGE_INFO
from src.models.user import BadgeTier, BHUser, WorkshopType

from ._helpers import (
    templates, _ctx, _render, _abs_url, _og_workshop_desc,
    _og_item_desc, _last_seen, _first_photo_url,
)

router = APIRouter(tags=["pages"])

@router.get("/helpboard", response_class=HTMLResponse)
async def helpboard_page(request: Request,
                         token: Optional[dict] = Depends(get_current_user_token)):
    """Community Help Board page."""
    ctx = _ctx(request, token, category_groups=CATEGORY_GROUPS)
    return _render("pages/helpboard.html", ctx)



@router.get("/calendar", response_class=HTMLResponse)
async def calendar_page(
    request: Request,
    token: Optional[dict] = Depends(get_current_user_token),
):
    """Community calendar with month view and event list."""
    ctx = _ctx(request, token,
        og_title="Community Calendar -- La Piazza",
        og_description="Workshops, meetups, and events happening in your neighborhood. RSVP and join the community.",
        og_image="https://lapiazza.app/static/images/og-default.png",
    )
    return _render("pages/calendar.html", ctx)



@router.get("/raffles", response_class=HTMLResponse)
async def raffles_page(request: Request,
                       token: Optional[dict] = Depends(get_current_user_token)):
    """Raffle browse page."""
    ctx = _ctx(request, token)
    return _render("pages/raffles.html", ctx)



@router.get("/raffles/create", response_class=HTMLResponse)
async def raffle_create_page(request: Request,
                             db: AsyncSession = Depends(get_db),
                             token: Optional[dict] = Depends(get_current_user_token)):
    """Raffle creation form. Requires login."""
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    from src.services.raffle_engine import completed_raffle_count
    from src.models.raffle import max_raffle_value_for, RAFFLE_TRUST_TIERS
    user = await get_user(db, token)
    raffle_count = await completed_raffle_count(db, user.id)
    raffle_cap_eur = max_raffle_value_for(raffle_count)
    # Age 14 min for organizers
    from datetime import date as _date
    age_years = None
    if user.date_of_birth:
        today = _date.today()
        dob = user.date_of_birth if isinstance(user.date_of_birth, _date) else user.date_of_birth.date()
        age_years = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    ctx = _ctx(request, token,
        raffle_completed_count=raffle_count,
        raffle_cap_eur=raffle_cap_eur,
        raffle_tier_table=RAFFLE_TRUST_TIERS,
        user_age_years=age_years,
    )
    return _render("pages/raffle_create.html", ctx)



@router.get("/raffles/guide", response_class=HTMLResponse)
async def raffle_guide(request: Request,
                       token: Optional[dict] = Depends(get_current_user_token)):
    """Raffle guide page — how raffles work, trust tiers, FAQ."""
    ctx = _ctx(request, token)
    return _render("pages/raffle_guide.html", ctx)



@router.get("/raffles/{raffle_id}", response_class=HTMLResponse)
async def raffle_detail_page(raffle_id: str, request: Request,
                             db: AsyncSession = Depends(get_db),
                             token: Optional[dict] = Depends(get_current_user_token)):
    """Raffle detail page with ticket purchase, stats, draw result."""
    from uuid import UUID as PyUUID
    from src.models.raffle import BHRaffle
    from sqlalchemy.orm import selectinload
    from src.models.listing import BHListing
    from src.models.item import BHItem

    try:
        rid = PyUUID(raffle_id)
    except ValueError:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Invalid raffle ID")

    raffle = await db.scalar(
        select(BHRaffle)
        .options(
            selectinload(BHRaffle.listing).selectinload(BHListing.item).selectinload(BHItem.media),
            selectinload(BHRaffle.organizer),
        )
        .where(BHRaffle.id == rid)
        .where(BHRaffle.deleted_at.is_(None))
    )
    if not raffle:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Raffle not found")

    # Only confirmed ticket holders can verify a drawn/completed raffle --
    # gate the Fair/Not-fair UI to them so anonymous viewers don't hit 400s.
    user_had_ticket = False
    if token and raffle.status.value in ("drawn", "completed"):
        from sqlalchemy import func as sa_func
        from src.dependencies import get_user
        from src.models.raffle import BHRaffleTicket, RaffleTicketStatus
        user = await get_user(db, token)
        count = await db.scalar(
            select(sa_func.count(BHRaffleTicket.id))
            .where(BHRaffleTicket.raffle_id == raffle.id)
            .where(BHRaffleTicket.user_id == user.id)
            .where(BHRaffleTicket.status == RaffleTicketStatus.CONFIRMED)
        )
        user_had_ticket = (count or 0) > 0

    # BL-165: rich OG tags so raffle shares get an image + price preview.
    # BHRaffle has no own `title` -- the title is the underlying item.name.
    raffle_image = None
    raffle_title = "Raffle"
    raffle_description = None
    if raffle.listing and raffle.listing.item:
        item = raffle.listing.item
        raffle_title = item.name or raffle_title
        raffle_description = item.description
        raffle_image = _abs_url(_first_photo_url(item.media))  # BL-168: skip videos
    organizer_name = raffle.organizer.display_name if raffle.organizer else "the community"
    ticket_price = float(raffle.ticket_price) if raffle.ticket_price else 0
    og_desc_parts = []
    if ticket_price > 0:
        og_desc_parts.append(f"EUR {ticket_price:.2f} per ticket")
    og_desc_parts.append(f"by {organizer_name}")
    if raffle_description:
        og_desc_parts.append(raffle_description[:140].strip())

    ctx = _ctx(request, token,
        raffle=raffle,
        user_had_ticket=user_had_ticket,
        og_type="product",
        og_title=f"{raffle_title} - La Piazza Raffle",
        og_description=" - ".join(og_desc_parts),
        og_image=raffle_image,  # falls back to og-default.png in base.html when None
    )
    return _render("pages/raffle_detail.html", ctx)



@router.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request,
                    token: Optional[dict] = Depends(get_current_user_token)):
    """AI Concierge chat page. Backend: POST /api/v1/ai/concierge (auth)."""
    if not token:
        from starlette.responses import RedirectResponse
        return RedirectResponse(url="/login", status_code=302)
    ctx = _ctx(request, token)
    return _render("pages/chat.html", ctx)



