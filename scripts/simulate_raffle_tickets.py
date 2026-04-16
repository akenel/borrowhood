"""Simulate raffle ticket purchases + confirmations for all demo raffles.

Runs inside the container via SQLAlchemy — no HTTP, no rate limiter.

    docker exec borrowhood python3 /app/scripts/simulate_raffle_tickets.py
"""
import asyncio
import random
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "/app")

# Who buys from whom (organizer can't buy own)
BUYERS = {
    "sally@borrowhood.local": ["mike", "leonardo", "pietro", "sofiaferretti", "john", "nicolo", "nino", "marco"],
    "roccamenanicolo@gmail.com": ["sally", "leonardo", "mike", "sofiaferretti", "marco", "jake"],
    "leonardo@borrowhood.local": ["sally", "mike", "nino", "john", "sofiaferretti", "pietro"],
    "jake@borrowhood.local": ["sally", "pietro", "nicolo", "marco", "mike", "leonardo"],
    "marco@borrowhood.local": ["leonardo", "sally", "nino", "pietro", "sofiaferretti"],
    "pietro@borrowhood.local": ["mike", "nicolo", "sally", "leonardo", "jake"],
    "nino@borrowhood.local": ["mike", "leonardo", "sally", "marco", "sofiaferretti"],
}


async def main():
    from sqlalchemy import select
    from src.database import async_session
    from src.models.user import BHUser
    from src.models.raffle import BHRaffle, BHRaffleTicket, RaffleStatus, RaffleTicketStatus

    async with async_session() as db:
        # Get all active raffles
        raffles = (await db.execute(
            select(BHRaffle)
            .where(BHRaffle.status.in_([RaffleStatus.PUBLISHED, RaffleStatus.ACTIVE]))
            .where(BHRaffle.deleted_at.is_(None))
        )).scalars().all()

        print(f"Found {len(raffles)} active raffles")

        for raffle in raffles:
            # Get organizer email
            organizer = await db.scalar(select(BHUser).where(BHUser.id == raffle.organizer_id))
            if not organizer:
                continue

            buyer_slugs = BUYERS.get(organizer.email, [])
            if not buyer_slugs:
                print(f"  SKIP: no buyers configured for {organizer.email}")
                continue

            # Check if tickets already exist
            existing = await db.scalar(
                select(BHRaffleTicket.id)
                .where(BHRaffleTicket.raffle_id == raffle.id)
                .limit(1)
            )
            if existing:
                print(f"  SKIP: {organizer.display_name}'s raffle already has tickets")
                continue

            print(f"\n  {organizer.display_name}'s raffle (EUR {raffle.ticket_price} x {raffle.max_tickets}):")

            ticket_num = 0
            total_sold = 0
            for slug in buyer_slugs:
                email = f"{slug}@borrowhood.local"
                if slug == "sofiaferretti":
                    email = "sofiaferretti@borrowhood.local"
                elif slug == "nicolo":
                    email = "roccamenanicolo@gmail.com"

                buyer = await db.scalar(
                    select(BHUser).where(BHUser.email == email).where(BHUser.deleted_at.is_(None))
                )
                if not buyer:
                    # Try alternate
                    buyer = await db.scalar(
                        select(BHUser).where(BHUser.slug.ilike(f"%{slug}%")).where(BHUser.deleted_at.is_(None))
                    )
                if not buyer:
                    print(f"    SKIP: {slug} not found")
                    continue

                qty = random.randint(1, min(3, raffle.max_tickets_per_user or 5))
                if total_sold + qty > raffle.max_tickets:
                    qty = raffle.max_tickets - total_sold
                if qty <= 0:
                    break

                ticket_num_start = ticket_num + 1
                ticket_numbers = list(range(ticket_num_start, ticket_num_start + qty))
                ticket_num += qty

                ticket = BHRaffleTicket(
                    raffle_id=raffle.id,
                    user_id=buyer.id,
                    quantity=qty,
                    ticket_numbers=ticket_numbers,
                    status=RaffleTicketStatus.CONFIRMED,
                    payment_method="cash",
                    confirmed_at=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 48)),
                    expires_at=None,
                )
                db.add(ticket)
                total_sold += qty
                print(f"    {buyer.display_name}: {qty} tickets (#{ticket_numbers}) CONFIRMED")

            # Update raffle counters
            raffle.tickets_sold = total_sold
            raffle.tickets_reserved = 0
            if raffle.status == RaffleStatus.PUBLISHED:
                raffle.status = RaffleStatus.ACTIVE

            pct = round(total_sold / raffle.max_tickets * 100) if raffle.max_tickets else 0
            print(f"    TOTAL: {total_sold}/{raffle.max_tickets} sold ({pct}%)")

        await db.commit()
        print("\nDONE: All tickets created and confirmed")


if __name__ == "__main__":
    asyncio.run(main())
