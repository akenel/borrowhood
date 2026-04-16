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
    BHRaffle, BHRaffleTicket, BHRaffleVerification,
    COOLDOWN_DAYS, DRAW_BUFFER_DAYS, ORGANIZER_INACTION_DAYS,
    POINTS_RAFFLE_ORGANIZER_COMPLETE, POINTS_RAFFLE_ORGANIZER_VERIFIED,
    POINTS_RAFFLE_TICKET_PURCHASE, POINTS_RAFFLE_WINNER,
    POINTS_RAFFLE_VERIFICATION, VERIFICATION_CLEAN_THRESHOLD,
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


async def check_one_active_raffle(db: AsyncSession, user_id, exclude_id=None) -> tuple[bool, str]:
    """Ensure organizer has no other active raffle running."""
    q = (
        select(func.count(BHRaffle.id))
        .where(BHRaffle.organizer_id == user_id)
        .where(BHRaffle.status.in_([
            RaffleStatus.DRAFT, RaffleStatus.PUBLISHED, RaffleStatus.ACTIVE, RaffleStatus.DRAWN,
        ]))
        .where(BHRaffle.deleted_at.is_(None))
    )
    if exclude_id:
        q = q.where(BHRaffle.id != exclude_id)
    active = await db.scalar(q) or 0
    if active > 0:
        return False, "You already have an active raffle. Complete or cancel it before starting a new one."
    return True, ""


async def check_raffle_ban(db: AsyncSession, user_id) -> tuple[bool, str]:
    """Block organizers who abandoned 2+ raffles with confirmed ticket holders."""
    abandon_count = await db.scalar(
        select(func.count(BHRaffle.id))
        .where(BHRaffle.organizer_id == user_id)
        .where(BHRaffle.status == RaffleStatus.CANCELLED)
        .where(BHRaffle.tickets_sold > 0)
        .where(BHRaffle.draw_seed.in_(["ABANDONED_PROCESSED", None]))
    ) or 0
    if abandon_count >= RAFFLE_BAN_AFTER_FAILURES:
        return False, (
            f"Your raffle privileges are suspended. You have {abandon_count} "
            f"abandoned raffle(s) with confirmed ticket holders. "
            f"Contact the community to resolve outstanding issues."
        )
    return True, ""


async def check_cooldown(db: AsyncSession, user_id) -> tuple[bool, str]:
    """Enforce 7-day cooldown between raffle completions."""
    last_completed = await db.scalar(
        select(BHRaffle.updated_at)
        .where(BHRaffle.organizer_id == user_id)
        .where(BHRaffle.status.in_([RaffleStatus.COMPLETED, RaffleStatus.CANCELLED]))
        .order_by(BHRaffle.updated_at.desc())
        .limit(1)
    )
    if last_completed:
        if last_completed.tzinfo is None:
            last_completed = last_completed.replace(tzinfo=timezone.utc)
        days_since = (datetime.now(timezone.utc) - last_completed).days
        if days_since < COOLDOWN_DAYS:
            remaining = COOLDOWN_DAYS - days_since
            return False, (
                f"Cooldown: {remaining} day{'s' if remaining != 1 else ''} remaining "
                f"before you can publish a new raffle. This prevents the platform "
                f"from looking like a casino."
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


async def demote_raffle_abandoners():
    """Demote organizers who abandoned raffles and didn't resolve within 30 days.

    Consequence ladder:
      * Auto-cancel fires at ORGANIZER_INACTION_DAYS (6 days)
      * 30-day grace period to apologize/explain
      * After 30 days: badge demotion + raffle ban flag
      * 2 abandoned raffles = permanently blocked from raffle feature
    """
    from src.models.user import BHUser, BadgeTier
    async with async_session() as db:
        now = datetime.now(timezone.utc)
        grace_cutoff = now - timedelta(days=ORGANIZER_GRACE_DAYS)

        # Find cancelled-by-system raffles (abandoned) past grace period
        # that had confirmed tickets (real participants were let down)
        abandoned = (await db.execute(
            select(BHRaffle)
            .where(BHRaffle.status == RaffleStatus.CANCELLED)
            .where(BHRaffle.tickets_sold > 0)
            .where(BHRaffle.updated_at < grace_cutoff)
            .where(BHRaffle.draw_seed.is_(None))  # Never drew = abandoned, not completed
        )).scalars().all()

        demoted = 0
        for raffle in abandoned:
            user = await db.scalar(select(BHUser).where(BHUser.id == raffle.organizer_id))
            if not user:
                continue

            # Count total abandoned raffles for this user
            abandon_count = await db.scalar(
                select(func.count(BHRaffle.id))
                .where(BHRaffle.organizer_id == user.id)
                .where(BHRaffle.status == RaffleStatus.CANCELLED)
                .where(BHRaffle.tickets_sold > 0)
                .where(BHRaffle.draw_seed.is_(None))
                .where(BHRaffle.updated_at < grace_cutoff)
            ) or 0

            # Demote badge tier (never below NEWCOMER)
            tier_order = [BadgeTier.LEGEND, BadgeTier.PILLAR, BadgeTier.TRUSTED, BadgeTier.ACTIVE, BadgeTier.NEWCOMER]
            current_idx = next((i for i, t in enumerate(tier_order) if t == user.badge_tier), len(tier_order) - 1)
            if current_idx < len(tier_order) - 1:
                new_tier = tier_order[current_idx + 1]
                user.badge_tier = new_tier
                logger.warning(
                    "Demoted %s (%s) from %s to %s due to abandoned raffle %s",
                    user.display_name, user.id, tier_order[current_idx].value, new_tier.value, raffle.id,
                )

            # Mark raffle as processed (set draw_seed to "ABANDONED" to prevent re-processing)
            raffle.draw_seed = "ABANDONED_PROCESSED"
            demoted += 1

        if demoted:
            await db.commit()
            logger.info("Demoted %d raffle abandoners", demoted)
        return demoted


async def run_raffle_expiry_loop():
    """Background loop: expire tickets + cancel abandoned raffles + demote abandoners."""
    logger.info("Raffle expiry loop started (interval=%ds)", EXPIRY_INTERVAL_SECONDS)
    while True:
        try:
            await expire_stale_tickets()
            await auto_cancel_abandoned_raffles()
            await demote_raffle_abandoners()
        except Exception as e:
            logger.error("Raffle expiry error: %s", e, exc_info=True)
        await asyncio.sleep(EXPIRY_INTERVAL_SECONDS)


# ── Gamification: points + verification ───────────────────────────────

async def _award_points(db: AsyncSession, user_id, points: int):
    """Add points to a user's total. Creates BHUserPoints row if missing."""
    from src.models.user import BHUserPoints
    pts = await db.scalar(
        select(BHUserPoints).where(BHUserPoints.user_id == user_id)
    )
    if not pts:
        pts = BHUserPoints(user_id=user_id, total_points=0)
        db.add(pts)
    pts.total_points = (pts.total_points or 0) + points


async def award_ticket_purchase_points(db: AsyncSession, user_id):
    """Buyer earns points when their ticket is confirmed."""
    await _award_points(db, user_id, POINTS_RAFFLE_TICKET_PURCHASE)


async def award_draw_points(db: AsyncSession, raffle: BHRaffle):
    """Award points on draw: organizer + winner."""
    await _award_points(db, raffle.organizer_id, POINTS_RAFFLE_ORGANIZER_COMPLETE)
    if raffle.winner_user_id:
        await _award_points(db, raffle.winner_user_id, POINTS_RAFFLE_WINNER)


async def submit_verification(
    db: AsyncSession,
    raffle: BHRaffle,
    user_id,
    is_fair: bool,
    prize_delivered: Optional[bool] = None,
    comment: Optional[str] = None,
) -> dict:
    """Ticket holder verifies the raffle was fair. Returns verification stats."""
    # Check user had a confirmed ticket
    had_ticket = await db.scalar(
        select(BHRaffleTicket.id)
        .where(BHRaffleTicket.raffle_id == raffle.id)
        .where(BHRaffleTicket.user_id == user_id)
        .where(BHRaffleTicket.status == RaffleTicketStatus.CONFIRMED)
    )
    if not had_ticket:
        return {"error": "Only confirmed ticket holders can verify"}

    # Check not already verified
    existing = await db.scalar(
        select(BHRaffleVerification.id)
        .where(BHRaffleVerification.raffle_id == raffle.id)
        .where(BHRaffleVerification.user_id == user_id)
    )
    if existing:
        return {"error": "Already verified this raffle"}

    # Save verification
    v = BHRaffleVerification(
        raffle_id=raffle.id,
        user_id=user_id,
        is_fair=is_fair,
        prize_delivered=prize_delivered,
        comment=comment,
    )
    db.add(v)

    # Update cached counts
    if is_fair:
        raffle.verifications_positive = (raffle.verifications_positive or 0) + 1
    else:
        raffle.verifications_negative = (raffle.verifications_negative or 0) + 1

    # Award points for submitting a verification (positive or negative)
    await _award_points(db, user_id, POINTS_RAFFLE_VERIFICATION)

    # Check if organizer earns the verified bonus (80%+ positive)
    total_v = (raffle.verifications_positive or 0) + (raffle.verifications_negative or 0)
    if total_v >= 2 and raffle.verification_rate >= VERIFICATION_CLEAN_THRESHOLD * 100:
        # Only award once — check if already awarded by looking at points history
        # Simple approach: award on crossing the threshold for the first time
        if total_v == 2 or (total_v > 2 and raffle.verifications_positive == int(total_v * VERIFICATION_CLEAN_THRESHOLD)):
            await _award_points(db, raffle.organizer_id, POINTS_RAFFLE_ORGANIZER_VERIFIED)
            logger.info("Organizer %s earned verified bonus for raffle %s", raffle.organizer_id, raffle.id)

    await db.flush()

    return {
        "status": "verified",
        "is_fair": is_fair,
        "raffle_verification_rate": raffle.verification_rate,
        "verifications_positive": raffle.verifications_positive,
        "verifications_negative": raffle.verifications_negative,
        "points_earned": POINTS_RAFFLE_VERIFICATION,
    }


def is_cleanly_completed(raffle: BHRaffle) -> bool:
    """Does this raffle count as 'completed cleanly' for trust tier progression?"""
    if raffle.status != RaffleStatus.COMPLETED:
        return False
    total = (raffle.verifications_positive or 0) + (raffle.verifications_negative or 0)
    if total < 1:
        return True  # No verifications yet — benefit of the doubt
    return raffle.verification_rate >= VERIFICATION_CLEAN_THRESHOLD * 100
