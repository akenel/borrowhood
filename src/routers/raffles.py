"""Raffle API: create, publish, buy tickets, draw winner.

Endpoints:
    POST   /api/v1/raffles                         -- create draft raffle
    GET    /api/v1/raffles                         -- browse active raffles
    GET    /api/v1/raffles/mine                    -- my raffles + my tickets
    GET    /api/v1/raffles/{id}                    -- get raffle + live stats
    PATCH  /api/v1/raffles/{id}                    -- edit (draft only)
    POST   /api/v1/raffles/{id}/publish            -- lock + go live
    POST   /api/v1/raffles/{id}/tickets/reserve    -- buy tickets
    POST   /api/v1/raffles/{id}/tickets/{tid}/confirm -- organizer confirms payment
    POST   /api/v1/raffles/{id}/tickets/{tid}/cancel  -- cancel ticket
    GET    /api/v1/raffles/{id}/tickets/mine       -- my tickets for this raffle
    GET    /api/v1/raffles/{id}/tickets            -- organizer: all tickets
    GET    /api/v1/raffles/{id}/pre-draw           -- pre-draw verification stats
    POST   /api/v1/raffles/{id}/draw               -- execute draw
    POST   /api/v1/raffles/{id}/complete           -- mark as completed (post-draw)
    POST   /api/v1/raffles/{id}/cancel             -- cancel entire raffle
    GET    /api/v1/raffles/{id}/stats              -- live stats (public)
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.dependencies import get_current_user_token, get_user, require_auth
from src.models.item import BHItem
from src.models.listing import BHListing, ListingStatus, ListingType
from src.models.raffle import (
    BHRaffle, BHRaffleTicket,
    RAFFLE_MAX_DURATION_DAYS, RAFFLE_MIN_DURATION_HOURS,
    RAFFLE_MIN_TICKET_PRICE_EUR, TICKET_HOLD_HOURS_DEFAULT,
    RaffleDelivery, RaffleDrawType, RaffleStatus, RaffleTicketStatus,
)
from src.services.raffle_engine import (
    completed_raffle_count, execute_draw, max_raffle_value_for,
    pre_draw_check, raffle_stats, validate_raffle_value,
)

router = APIRouter(prefix="/api/v1/raffles", tags=["raffles"])


# ── Schemas ────────────────────────────────────────────────────────────

class RaffleCreate(BaseModel):
    item_id: UUID
    title: str = Field(max_length=200)
    description: Optional[str] = None
    ticket_price: float = Field(ge=0.10)
    currency: str = Field(default="EUR", max_length=3)
    max_tickets: Optional[int] = Field(default=None, ge=1)
    max_tickets_per_user: Optional[int] = Field(default=None, ge=1)
    draw_type: str = Field(default="date")
    draw_date: Optional[datetime] = None
    payment_methods: Optional[list[str]] = None
    payment_instructions: Optional[str] = None
    delivery_method: Optional[str] = None
    shipping_notes: Optional[str] = None
    ticket_hold_hours: int = Field(default=TICKET_HOLD_HOURS_DEFAULT, ge=1, le=168)


class RaffleUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = None
    ticket_price: Optional[float] = Field(default=None, ge=0.10)
    max_tickets: Optional[int] = Field(default=None, ge=1)
    max_tickets_per_user: Optional[int] = Field(default=None, ge=1)
    draw_date: Optional[datetime] = None
    payment_methods: Optional[list[str]] = None
    payment_instructions: Optional[str] = None
    delivery_method: Optional[str] = None
    shipping_notes: Optional[str] = None


class TicketReserve(BaseModel):
    quantity: int = Field(default=1, ge=1, le=50)
    payment_method: Optional[str] = None


class DrawRequest(BaseModel):
    cancel_pending: bool = True


# ── Helpers ────────────────────────────────────────────────────────────

async def _get_raffle(db: AsyncSession, raffle_id: UUID) -> BHRaffle:
    raffle = await db.scalar(
        select(BHRaffle)
        .options(selectinload(BHRaffle.listing).selectinload(BHListing.item))
        .where(BHRaffle.id == raffle_id)
        .where(BHRaffle.deleted_at.is_(None))
    )
    if not raffle:
        raise HTTPException(status_code=404, detail="Raffle not found")
    return raffle


def _raffle_out(raffle: BHRaffle, stats: Optional[dict] = None) -> dict:
    item = raffle.listing.item if raffle.listing else None
    return {
        "id": str(raffle.id),
        "listing_id": str(raffle.listing_id),
        "organizer_id": str(raffle.organizer_id),
        "status": raffle.status.value,
        "title": item.name if item else "",
        "description": item.description if item else "",
        "ticket_price": raffle.ticket_price,
        "currency": raffle.currency,
        "max_tickets": raffle.max_tickets,
        "max_tickets_per_user": raffle.max_tickets_per_user,
        "draw_type": raffle.draw_type.value,
        "draw_date": raffle.draw_date.isoformat() if raffle.draw_date else None,
        "payment_methods": raffle.payment_methods or [],
        "payment_instructions": raffle.payment_instructions,
        "delivery_method": raffle.delivery_method.value if raffle.delivery_method else None,
        "shipping_notes": raffle.shipping_notes,
        "winner_user_id": str(raffle.winner_user_id) if raffle.winner_user_id else None,
        "drawn_at": raffle.drawn_at.isoformat() if raffle.drawn_at else None,
        "draw_seed": raffle.draw_seed,
        "draw_proof_hash": raffle.draw_proof_hash,
        "stats": stats,
    }


# ── CRUD ──────────────────────────────────────────────────────────────

@router.post("", status_code=201)
async def create_raffle(
    data: RaffleCreate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Create a draft raffle. Item must belong to the current user."""
    user = await get_user(db, token)

    # Verify item ownership
    item = await db.scalar(
        select(BHItem).where(BHItem.id == data.item_id).where(BHItem.owner_id == user.id)
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found or not yours")

    # Validate draw trigger
    if data.draw_date is None and data.max_tickets is None:
        raise HTTPException(status_code=400, detail="Either draw_date or max_tickets is required")

    # Validate trust tier
    ok, msg = await validate_raffle_value(db, user.id, data.ticket_price, data.max_tickets)
    if not ok:
        raise HTTPException(status_code=403, detail=msg)

    # Validate draw_type enum
    try:
        draw_type = RaffleDrawType(data.draw_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid draw_type: {data.draw_type}")

    delivery = None
    if data.delivery_method:
        try:
            delivery = RaffleDelivery(data.delivery_method)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid delivery_method: {data.delivery_method}")

    # Create listing
    listing = BHListing(
        item_id=data.item_id,
        listing_type=ListingType.RAFFLE,
        status=ListingStatus.DRAFT,
        price=data.ticket_price,
        currency=data.currency,
        notes=data.description,
    )
    db.add(listing)
    await db.flush()

    # Create raffle
    raffle = BHRaffle(
        listing_id=listing.id,
        organizer_id=user.id,
        ticket_price=data.ticket_price,
        currency=data.currency,
        max_tickets=data.max_tickets,
        max_tickets_per_user=data.max_tickets_per_user,
        draw_type=draw_type,
        draw_date=data.draw_date,
        payment_methods=data.payment_methods,
        payment_instructions=data.payment_instructions,
        delivery_method=delivery,
        shipping_notes=data.shipping_notes,
        ticket_hold_hours=data.ticket_hold_hours,
        status=RaffleStatus.DRAFT,
    )
    db.add(raffle)
    await db.commit()
    await db.refresh(raffle)
    return _raffle_out(raffle)


@router.get("")
async def browse_raffles(
    status: str = Query("active", pattern="^(active|published|drawn|all)$"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    token: Optional[dict] = Depends(get_current_user_token),
):
    """Browse active raffles. Public endpoint."""
    q = (
        select(BHRaffle)
        .options(selectinload(BHRaffle.listing).selectinload(BHListing.item).selectinload(BHItem.media))
        .where(BHRaffle.deleted_at.is_(None))
    )
    if status == "all":
        q = q.where(BHRaffle.status != RaffleStatus.DRAFT)
    else:
        try:
            q = q.where(BHRaffle.status == RaffleStatus(status))
        except ValueError:
            q = q.where(BHRaffle.status == RaffleStatus.ACTIVE)

    q = q.order_by(BHRaffle.draw_date.asc().nullslast()).limit(limit)
    result = await db.execute(q)
    raffles = result.scalars().unique().all()

    out = []
    for r in raffles:
        stats = await raffle_stats(db, r)
        out.append(_raffle_out(r, stats))
    return out


@router.get("/mine")
async def my_raffles(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """My raffles (as organizer) + raffles I have tickets for."""
    user = await get_user(db, token)

    # As organizer
    organized = (await db.execute(
        select(BHRaffle)
        .options(selectinload(BHRaffle.listing).selectinload(BHListing.item))
        .where(BHRaffle.organizer_id == user.id)
        .where(BHRaffle.deleted_at.is_(None))
        .order_by(BHRaffle.created_at.desc())
    )).scalars().unique().all()

    # As ticket holder
    ticket_raffle_ids = (await db.execute(
        select(BHRaffleTicket.raffle_id)
        .where(BHRaffleTicket.user_id == user.id)
        .where(BHRaffleTicket.status.in_([RaffleTicketStatus.RESERVED, RaffleTicketStatus.CONFIRMED]))
    )).scalars().all()

    participating = []
    if ticket_raffle_ids:
        participating = (await db.execute(
            select(BHRaffle)
            .options(selectinload(BHRaffle.listing).selectinload(BHListing.item))
            .where(BHRaffle.id.in_(ticket_raffle_ids))
            .where(BHRaffle.deleted_at.is_(None))
        )).scalars().unique().all()

    return {
        "organized": [_raffle_out(r) for r in organized],
        "participating": [_raffle_out(r) for r in participating],
    }


@router.get("/{raffle_id}")
async def get_raffle(
    raffle_id: UUID,
    db: AsyncSession = Depends(get_db),
    token: Optional[dict] = Depends(get_current_user_token),
):
    """Get raffle details + live stats. Public for non-draft raffles."""
    raffle = await _get_raffle(db, raffle_id)
    if raffle.status == RaffleStatus.DRAFT:
        if not token:
            raise HTTPException(status_code=404, detail="Raffle not found")
        user = await get_user(db, token)
        if raffle.organizer_id != user.id:
            raise HTTPException(status_code=404, detail="Raffle not found")
    stats = await raffle_stats(db, raffle)
    return _raffle_out(raffle, stats)


@router.patch("/{raffle_id}")
async def update_raffle(
    raffle_id: UUID,
    data: RaffleUpdate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Edit a draft raffle. Locked after publish or first ticket."""
    user = await get_user(db, token)
    raffle = await _get_raffle(db, raffle_id)

    if raffle.organizer_id != user.id:
        raise HTTPException(status_code=403, detail="Not your raffle")
    if raffle.status != RaffleStatus.DRAFT:
        raise HTTPException(status_code=403, detail="Raffle is published and locked for editing")

    # Check if any tickets exist
    ticket_count = await db.scalar(
        select(func.count(BHRaffleTicket.id)).where(BHRaffleTicket.raffle_id == raffle.id)
    )
    if ticket_count and ticket_count > 0:
        raise HTTPException(status_code=403, detail="Tickets already issued, cannot edit")

    # Apply updates
    item = raffle.listing.item if raffle.listing else None
    for field, value in data.model_dump(exclude_unset=True).items():
        if field in ("title", "description") and item:
            if field == "title":
                item.name = value
            elif field == "description":
                item.description = value
        elif field == "delivery_method" and value:
            raffle.delivery_method = RaffleDelivery(value)
        elif hasattr(raffle, field):
            setattr(raffle, field, value)
        if field == "ticket_price" and raffle.listing:
            raffle.listing.price = value

    await db.commit()
    await db.refresh(raffle)
    return _raffle_out(raffle)


@router.post("/{raffle_id}/publish")
async def publish_raffle(
    raffle_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Publish a draft raffle. Locks it for editing. Requires TOS acceptance."""
    user = await get_user(db, token)
    raffle = await _get_raffle(db, raffle_id)

    if raffle.organizer_id != user.id:
        raise HTTPException(status_code=403, detail="Not your raffle")
    if raffle.status != RaffleStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Already published")

    # Validate completeness
    if not raffle.draw_date and not raffle.max_tickets:
        raise HTTPException(status_code=400, detail="Set either a draw date or max tickets before publishing")
    if raffle.draw_date and raffle.draw_date < datetime.now(timezone.utc) + timedelta(hours=RAFFLE_MIN_DURATION_HOURS):
        raise HTTPException(status_code=400, detail=f"Draw date must be at least {RAFFLE_MIN_DURATION_HOURS}h from now")

    # Progressive trust check
    ok, msg = await validate_raffle_value(db, user.id, raffle.ticket_price, raffle.max_tickets)
    if not ok:
        raise HTTPException(status_code=403, detail=msg)

    # Record trust tier at publish time
    raffle.organizer_raffle_count = await completed_raffle_count(db, user.id)
    raffle.status = RaffleStatus.PUBLISHED
    raffle.tos_accepted_at = datetime.now(timezone.utc)
    raffle.listing.status = ListingStatus.ACTIVE

    await db.commit()
    return {"status": "published", "raffle_id": str(raffle.id)}


# ── Ticket flow ───────────────────────────────────────────────────────

@router.post("/{raffle_id}/tickets/reserve")
async def reserve_tickets(
    raffle_id: UUID,
    data: TicketReserve,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Reserve tickets. Held for ticket_hold_hours pending payment."""
    user = await get_user(db, token)
    raffle = await _get_raffle(db, raffle_id)

    if raffle.status not in (RaffleStatus.PUBLISHED, RaffleStatus.ACTIVE):
        raise HTTPException(status_code=400, detail="Raffle is not accepting tickets")
    if raffle.organizer_id == user.id:
        raise HTTPException(status_code=400, detail="Organizer cannot buy own raffle tickets")

    # Per-user limit
    if raffle.max_tickets_per_user:
        existing = await db.scalar(
            select(func.coalesce(func.sum(BHRaffleTicket.quantity), 0))
            .where(BHRaffleTicket.raffle_id == raffle.id)
            .where(BHRaffleTicket.user_id == user.id)
            .where(BHRaffleTicket.status.in_([RaffleTicketStatus.RESERVED, RaffleTicketStatus.CONFIRMED]))
        )
        if existing + data.quantity > raffle.max_tickets_per_user:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum {raffle.max_tickets_per_user} tickets per person (you have {existing})"
            )

    # Capacity check
    if raffle.max_tickets:
        sold_and_reserved = (raffle.tickets_sold or 0) + (raffle.tickets_reserved or 0)
        if sold_and_reserved + data.quantity > raffle.max_tickets:
            available = raffle.max_tickets - sold_and_reserved
            raise HTTPException(status_code=400, detail=f"Only {available} tickets remaining")

    # Assign sequential ticket numbers — unnest all existing, find max
    from sqlalchemy import text
    max_result = await db.execute(
        text("""
            SELECT COALESCE(MAX(n), 0)
            FROM (SELECT unnest(ticket_numbers) AS n FROM bh_raffle_ticket WHERE raffle_id = :rid) sub
        """),
        {"rid": str(raffle.id)},
    )
    next_start = max_result.scalar() or 0
    ticket_numbers = list(range(next_start + 1, next_start + 1 + data.quantity))

    ticket = BHRaffleTicket(
        raffle_id=raffle.id,
        user_id=user.id,
        quantity=data.quantity,
        ticket_numbers=ticket_numbers,
        status=RaffleTicketStatus.RESERVED,
        payment_method=data.payment_method,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=raffle.ticket_hold_hours),
    )
    db.add(ticket)
    raffle.tickets_reserved = (raffle.tickets_reserved or 0) + data.quantity

    # Activate raffle on first ticket
    if raffle.status == RaffleStatus.PUBLISHED:
        raffle.status = RaffleStatus.ACTIVE

    await db.commit()
    await db.refresh(ticket)

    return {
        "ticket_id": str(ticket.id),
        "ticket_numbers": ticket.ticket_numbers,
        "quantity": ticket.quantity,
        "status": ticket.status.value,
        "expires_at": ticket.expires_at.isoformat(),
        "payment_instructions": raffle.payment_instructions,
    }


@router.post("/{raffle_id}/tickets/{ticket_id}/confirm")
async def confirm_ticket(
    raffle_id: UUID,
    ticket_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Organizer confirms payment received for a ticket."""
    user = await get_user(db, token)
    raffle = await _get_raffle(db, raffle_id)

    if raffle.organizer_id != user.id:
        raise HTTPException(status_code=403, detail="Only the organizer can confirm tickets")

    ticket = await db.scalar(
        select(BHRaffleTicket)
        .where(BHRaffleTicket.id == ticket_id)
        .where(BHRaffleTicket.raffle_id == raffle.id)
    )
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if ticket.status != RaffleTicketStatus.RESERVED:
        raise HTTPException(status_code=400, detail=f"Ticket is {ticket.status.value}, not reserved")

    ticket.status = RaffleTicketStatus.CONFIRMED
    ticket.confirmed_at = datetime.now(timezone.utc)
    ticket.expires_at = None
    raffle.tickets_reserved = max(0, (raffle.tickets_reserved or 0) - ticket.quantity)
    raffle.tickets_sold = (raffle.tickets_sold or 0) + ticket.quantity

    await db.commit()
    return {"ticket_id": str(ticket.id), "status": "confirmed"}


@router.post("/{raffle_id}/tickets/{ticket_id}/cancel")
async def cancel_ticket(
    raffle_id: UUID,
    ticket_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Cancel a ticket. Buyer can cancel their own; organizer can cancel any."""
    user = await get_user(db, token)
    raffle = await _get_raffle(db, raffle_id)

    ticket = await db.scalar(
        select(BHRaffleTicket)
        .where(BHRaffleTicket.id == ticket_id)
        .where(BHRaffleTicket.raffle_id == raffle.id)
    )
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if ticket.user_id != user.id and raffle.organizer_id != user.id:
        raise HTTPException(status_code=403, detail="Not your ticket")
    if ticket.status not in (RaffleTicketStatus.RESERVED, RaffleTicketStatus.CONFIRMED):
        raise HTTPException(status_code=400, detail=f"Ticket already {ticket.status.value}")

    was_confirmed = ticket.status == RaffleTicketStatus.CONFIRMED
    ticket.status = RaffleTicketStatus.CANCELLED

    if was_confirmed:
        raffle.tickets_sold = max(0, (raffle.tickets_sold or 0) - ticket.quantity)
    else:
        raffle.tickets_reserved = max(0, (raffle.tickets_reserved or 0) - ticket.quantity)

    await db.commit()
    return {"ticket_id": str(ticket.id), "status": "cancelled"}


@router.get("/{raffle_id}/tickets/mine")
async def my_tickets(
    raffle_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Get my tickets for this raffle."""
    user = await get_user(db, token)
    tickets = (await db.execute(
        select(BHRaffleTicket)
        .where(BHRaffleTicket.raffle_id == raffle_id)
        .where(BHRaffleTicket.user_id == user.id)
        .order_by(BHRaffleTicket.created_at.desc())
    )).scalars().all()

    return [
        {
            "id": str(t.id),
            "quantity": t.quantity,
            "ticket_numbers": t.ticket_numbers,
            "status": t.status.value,
            "payment_method": t.payment_method,
            "expires_at": t.expires_at.isoformat() if t.expires_at else None,
            "confirmed_at": t.confirmed_at.isoformat() if t.confirmed_at else None,
        }
        for t in tickets
    ]


@router.get("/{raffle_id}/tickets")
async def all_tickets(
    raffle_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Organizer view: all tickets for this raffle."""
    user = await get_user(db, token)
    raffle = await _get_raffle(db, raffle_id)

    if raffle.organizer_id != user.id:
        raise HTTPException(status_code=403, detail="Only the organizer can view all tickets")

    tickets = (await db.execute(
        select(BHRaffleTicket)
        .options(selectinload(BHRaffleTicket.user))
        .where(BHRaffleTicket.raffle_id == raffle.id)
        .order_by(BHRaffleTicket.created_at.desc())
    )).scalars().all()

    return [
        {
            "id": str(t.id),
            "user_name": t.user.display_name if t.user else "Unknown",
            "user_id": str(t.user_id),
            "quantity": t.quantity,
            "ticket_numbers": t.ticket_numbers,
            "status": t.status.value,
            "payment_method": t.payment_method,
            "expires_at": t.expires_at.isoformat() if t.expires_at else None,
            "confirmed_at": t.confirmed_at.isoformat() if t.confirmed_at else None,
        }
        for t in tickets
    ]


# ── Draw ──────────────────────────────────────────────────────────────

@router.get("/{raffle_id}/pre-draw")
async def pre_draw(
    raffle_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Pre-draw verification. Organizer must review before drawing."""
    user = await get_user(db, token)
    raffle = await _get_raffle(db, raffle_id)
    if raffle.organizer_id != user.id:
        raise HTTPException(status_code=403, detail="Only the organizer can view pre-draw stats")
    return await pre_draw_check(db, raffle)


@router.post("/{raffle_id}/draw")
async def draw_raffle(
    raffle_id: UUID,
    data: DrawRequest = DrawRequest(),
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Execute the draw. Selects a provably fair winner."""
    user = await get_user(db, token)
    raffle = await _get_raffle(db, raffle_id)

    if raffle.organizer_id != user.id:
        raise HTTPException(status_code=403, detail="Only the organizer can draw")
    if raffle.status not in (RaffleStatus.PUBLISHED, RaffleStatus.ACTIVE):
        raise HTTPException(status_code=400, detail=f"Cannot draw — raffle is {raffle.status.value}")

    result = await execute_draw(db, raffle, cancel_pending=data.cancel_pending)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    await db.commit()
    return result


@router.post("/{raffle_id}/complete")
async def complete_raffle(
    raffle_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Mark a drawn raffle as completed. Prize delivered, done."""
    user = await get_user(db, token)
    raffle = await _get_raffle(db, raffle_id)
    if raffle.organizer_id != user.id:
        raise HTTPException(status_code=403, detail="Not your raffle")
    if raffle.status != RaffleStatus.DRAWN:
        raise HTTPException(status_code=400, detail="Raffle must be drawn first")

    raffle.status = RaffleStatus.COMPLETED
    raffle.listing.status = ListingStatus.EXPIRED
    await db.commit()
    return {"status": "completed"}


@router.post("/{raffle_id}/cancel")
async def cancel_raffle(
    raffle_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Cancel entire raffle. All tickets voided."""
    user = await get_user(db, token)
    raffle = await _get_raffle(db, raffle_id)
    if raffle.organizer_id != user.id:
        raise HTTPException(status_code=403, detail="Not your raffle")
    if raffle.status in (RaffleStatus.COMPLETED,):
        raise HTTPException(status_code=400, detail="Cannot cancel a completed raffle")

    raffle.status = RaffleStatus.CANCELLED
    raffle.listing.status = ListingStatus.EXPIRED

    # Void all active tickets
    active_tickets = (await db.execute(
        select(BHRaffleTicket)
        .where(BHRaffleTicket.raffle_id == raffle.id)
        .where(BHRaffleTicket.status.in_([RaffleTicketStatus.RESERVED, RaffleTicketStatus.CONFIRMED]))
    )).scalars().all()
    for t in active_tickets:
        t.status = RaffleTicketStatus.CANCELLED

    await db.commit()
    return {"status": "cancelled", "tickets_voided": len(active_tickets)}


@router.get("/{raffle_id}/stats")
async def get_stats(
    raffle_id: UUID,
    db: AsyncSession = Depends(get_db),
    token: Optional[dict] = Depends(get_current_user_token),
):
    """Live stats for the raffle listing page. Public."""
    raffle = await _get_raffle(db, raffle_id)
    if raffle.status == RaffleStatus.DRAFT:
        raise HTTPException(status_code=404, detail="Raffle not found")
    return await raffle_stats(db, raffle)
