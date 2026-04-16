"""Raffle engine: ticket expiry, draw logic, and lifecycle management.

Handles:
  * Ticket reservation expiry (background loop, same pattern as commitment_expiry)
  * Provably fair draw (seed + deterministic winner from confirmed pool)
  * Auto-cancel on organizer inaction post draw_date
  * Progressive trust tier enforcement
  * Pre-draw verification
"""

import asyncio
import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import async_session
from src.models.raffle import (
    BHRaffle, BHRaffleTicket,
    DRAW_BUFFER_DAYS, ORGANIZER_INACTION_DAYS,
    RaffleDrawType, RaffleStatus, RaffleTicketStatus,
    max_raffle_value_for,
)

logger = logging.getLogger("raffle_engine")

EXPIRY_INTERVAL_SECONDS = 300  # 5 minutes


# ── Progressive trust ─────────────────────────────────────────────────

async def completed_raffle_count(db: AsyncSession, user_id) -> int:
    """How many raffles has this organizer completed cleanly?"""
    return await db.scalar(
        select(func.count(BHRaffle.id))
        .where(BHRaffle.organizer_id == user_id)
        .where(BHRaffle.status == RaffleStatus.COMPLETED)
    ) or 0


async def validate_raffle_value(db: AsyncSession, user_id, ticket_price: float, max_tickets: Optional[int]) -> tuple[bool, str]:
    """Check if proposed raffle value is within the organizer's trust tier."""
    if max_tickets is None:
        return True, ""
    total_value = ticket_price * max_tickets
    count = await completed_raffle_count(db, user_id)
    limit = max_raffle_value_for(count)
    if total_value > limit:
        return False, (
            f"Total raffle value EUR {total_value:.2f} exceeds your current limit "
            f"of EUR {limit:.2f} ({count} completed raffles). "
            f"Complete more raffles to unlock higher limits."
        )
    return True, ""


# ── Pre-draw verification ─────────────────────────────────────────────

async def pre_draw_check(db: AsyncSession, raffle: BHRaffle) -> dict:
    """Return verification stats before a draw can proceed."""
    confirmed = await db.scalar(
        select(func.coalesce(func.sum(BHRaffleTicket.quantity), 0))
        .where(BHRaffleTicket.raffle_id == raffle.id)
        .where(BHRaffleTicket.status == RaffleTicketStatus.CONFIRMED)
    )
    reserved = await db.scalar(
        select(func.coalesce(func.sum(BHRaffleTicket.quantity), 0))
        .where(BHRaffleTicket.raffle_id == raffle.id)
        .where(BHRaffleTicket.status == RaffleTicketStatus.RESERVED)
    )
    expired = await db.scalar(
        select(func.coalesce(func.sum(BHRaffleTicket.quantity), 0))
        .where(BHRaffleTicket.raffle_id == raffle.id)
        .where(BHRaffleTicket.status == RaffleTicketStatus.EXPIRED)
    )
    return {
        "confirmed_tickets": confirmed,
        "reserved_tickets": reserved,
        "expired_tickets": expired,
        "can_draw": confirmed > 0,
        "has_pending": reserved > 0,
    }


# ── Provably fair draw ────────────────────────────────────────────────

def generate_draw_seed() -> str:
    """Generate a cryptographic seed for the draw."""
    return secrets.token_hex(32)


def compute_winner(seed: str, confirmed_ticket_ids: list, quantities: list[int]) -> tuple[int, str]:
    """Deterministically select a winner from the ticket pool.

    Expands tickets by quantity (3 tickets = 3 entries), hashes the
    seed with the pool size, and picks the winner index.

    Returns (winner_index_in_expanded_pool, proof_hash).
    """
    pool = []
    for tid, qty in zip(confirmed_ticket_ids, quantities):
        pool.extend([tid] * qty)

    pool_repr = ",".join(str(t) for t in pool)
    proof_input = f"{seed}:{pool_repr}"
    proof_hash = hashlib.sha256(proof_input.encode()).hexdigest()

    # Deterministic index from hash
    winner_index = int(proof_hash[:16], 16) % len(pool)
    return winner_index, proof_hash


async def execute_draw(db: AsyncSession, raffle: BHRaffle, cancel_pending: bool = True) -> dict:
    """Execute the raffle draw. Returns draw result dict.

    If cancel_pending is True, any RESERVED tickets are cancelled first.
    Only CONFIRMED tickets enter the draw pool.
    """
    if raffle.status not in (RaffleStatus.ACTIVE, RaffleStatus.PUBLISHED):
        return {"error": "Raffle is not in a drawable state"}

    # Cancel pending reservations if requested
    if cancel_pending:
        pending = (await db.execute(
            select(BHRaffleTicket)
            .where(BHRaffleTicket.raffle_id == raffle.id)
            .where(BHRaffleTicket.status == RaffleTicketStatus.RESERVED)
        )).scalars().all()
        for ticket in pending:
            ticket.status = RaffleTicketStatus.CANCELLED
        raffle.tickets_reserved -= sum(t.quantity for t in pending)

    # Build confirmed pool
    confirmed = (await db.execute(
        select(BHRaffleTicket)
        .where(BHRaffleTicket.raffle_id == raffle.id)
        .where(BHRaffleTicket.status == RaffleTicketStatus.CONFIRMED)
        .order_by(BHRaffleTicket.created_at)
    )).scalars().all()

    if not confirmed:
        return {"error": "No confirmed tickets — cannot draw"}

    ticket_ids = [str(t.id) for t in confirmed]
    quantities = [t.quantity for t in confirmed]
    total_entries = sum(quantities)

    # Generate seed and draw
    seed = generate_draw_seed()
    winner_idx, proof_hash = compute_winner(seed, ticket_ids, quantities)

    # Map back to winning ticket
    expanded = []
    for t, qty in zip(confirmed, quantities):
        expanded.extend([t] * qty)
    winning_ticket = expanded[winner_idx]

    # Update raffle
    raffle.status = RaffleStatus.DRAWN
    raffle.drawn_at = datetime.now(timezone.utc)
    raffle.winner_user_id = winning_ticket.user_id
    raffle.winner_ticket_id = winning_ticket.id
    raffle.draw_seed = seed
    raffle.draw_proof_hash = proof_hash

    await db.flush()

    return {
        "winner_user_id": str(winning_ticket.user_id),
        "winner_ticket_id": str(winning_ticket.id),
        "total_entries": total_entries,
        "total_tickets": len(confirmed),
        "seed": seed,
        "proof_hash": proof_hash,
        "drawn_at": raffle.drawn_at.isoformat(),
    }


# ── Raffle stats (live, always recalculated) ──────────────────────────

async def raffle_stats(db: AsyncSession, raffle: BHRaffle) -> dict:
    """Live stats for a raffle listing page."""
    confirmed = await db.scalar(
        select(func.coalesce(func.sum(BHRaffleTicket.quantity), 0))
        .where(BHRaffleTicket.raffle_id == raffle.id)
        .where(BHRaffleTicket.status == RaffleTicketStatus.CONFIRMED)
    )
    reserved = await db.scalar(
        select(func.coalesce(func.sum(BHRaffleTicket.quantity), 0))
        .where(BHRaffleTicket.raffle_id == raffle.id)
        .where(BHRaffleTicket.status == RaffleTicketStatus.RESERVED)
    )
    total = raffle.max_tickets
    available = (total - confirmed - reserved) if total else None
    percent = round((confirmed / total) * 100) if total and total > 0 else 0

    hours_remaining = None
    if raffle.draw_date:
        delta = raffle.draw_date - datetime.now(timezone.utc)
        hours_remaining = max(0, delta.total_seconds() / 3600)

    return {
        "total_tickets": total,
        "tickets_confirmed": confirmed,
        "tickets_reserved": reserved,
        "tickets_available": available,
        "percent_sold": percent,
        "draw_date": raffle.draw_date.isoformat() if raffle.draw_date else None,
        "hours_remaining": round(hours_remaining, 1) if hours_remaining is not None else None,
        "status": raffle.status.value,
    }


# ── Background: ticket expiry + organizer inaction ────────────────────

async def expire_stale_tickets():
    """Expire reserved tickets past their hold window. Release back to pool."""
    async with async_session() as db:
        now = datetime.now(timezone.utc)
        result = await db.execute(
            select(BHRaffleTicket)
            .options(selectinload(BHRaffleTicket.raffle))
            .where(BHRaffleTicket.status == RaffleTicketStatus.RESERVED)
            .where(BHRaffleTicket.expires_at < now)
        )
        expired = result.scalars().all()
        if not expired:
            return 0

        count = 0
        for ticket in expired:
            ticket.status = RaffleTicketStatus.EXPIRED
            if ticket.raffle:
                ticket.raffle.tickets_reserved = max(0, (ticket.raffle.tickets_reserved or 0) - ticket.quantity)
            count += 1
            logger.info("Expired raffle ticket %s (raffle=%s, user=%s, qty=%d)",
                        ticket.id, ticket.raffle_id, ticket.user_id, ticket.quantity)

        await db.commit()
        if count:
            logger.info("Expired %d stale raffle tickets", count)
        return count


async def auto_cancel_abandoned_raffles():
    """Cancel raffles where organizer took no action past the deadline."""
    async with async_session() as db:
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(days=ORGANIZER_INACTION_DAYS)

        # Published/active raffles with draw_date in the past and no draw action
        result = await db.execute(
            select(BHRaffle)
            .where(BHRaffle.status.in_([RaffleStatus.PUBLISHED, RaffleStatus.ACTIVE]))
            .where(BHRaffle.draw_date.is_not(None))
            .where(BHRaffle.draw_date < cutoff)
        )
        abandoned = result.scalars().all()
        if not abandoned:
            return 0

        count = 0
        for raffle in abandoned:
            raffle.status = RaffleStatus.CANCELLED
            # Cancel all remaining tickets
            tickets = (await db.execute(
                select(BHRaffleTicket)
                .where(BHRaffleTicket.raffle_id == raffle.id)
                .where(BHRaffleTicket.status.in_([
                    RaffleTicketStatus.RESERVED, RaffleTicketStatus.CONFIRMED
                ]))
            )).scalars().all()
            for t in tickets:
                t.status = RaffleTicketStatus.CANCELLED
            count += 1
            logger.info("Auto-cancelled abandoned raffle %s (organizer=%s)", raffle.id, raffle.organizer_id)

        await db.commit()
        if count:
            logger.info("Auto-cancelled %d abandoned raffles", count)
        return count


async def run_raffle_expiry_loop():
    """Background loop: expire tickets + cancel abandoned raffles."""
    logger.info("Raffle expiry loop started (interval=%ds)", EXPIRY_INTERVAL_SECONDS)
    while True:
        try:
            await expire_stale_tickets()
            await auto_cancel_abandoned_raffles()
        except Exception as e:
            logger.error("Raffle expiry error: %s", e, exc_info=True)
        await asyncio.sleep(EXPIRY_INTERVAL_SECONDS)
