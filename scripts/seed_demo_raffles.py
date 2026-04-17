"""Seed demo raffles for the Season 1 cast.

Creates a mix of raffle states (published, active, drawn) so the
/raffles page looks alive on first visit. Run inside the container:

    docker exec -it borrowhood python3 /app/scripts/seed_demo_raffles.py

Idempotent: checks for existing RAFFLE-type listings before creating.
"""
import asyncio
import random
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "/app")

DEMO_RAFFLES = [
    # (organizer_email, item_name, ticket_price, max_tickets, days_until_draw,
    #  payment_instructions, delivery, description)
    (
        "roccamenanicolo@gmail.com",
        "Jiu-Jitsu Private Lesson Raffle",
        2.00, 25, 7,
        "Pay EUR 2 cash at the dojo or send to PayPal: nic@example.com",
        "pickup",
        "Win a free 1-hour private BJJ lesson with Nic at his dojo in Trapani. All proceeds go to the local youth sports club.",
    ),
    (
        "leonardo@borrowhood.local",
        "Hand-Carved Wooden Chess Set",
        5.00, 20, 10,
        "Pay EUR 5 at the Bottega or bank transfer (details on request).",
        "pickup",
        "Leonardo spent 3 months carving this chess set from Sicilian olive wood. Every piece is unique. Winner picks up at the Bottega.",
    ),
    (
        "sally@borrowhood.local",
        "Sally's Christmas Cookie Box (24 pieces)",
        1.00, 30, 5,
        "Pay Sally EUR 1 cash or via Satispay.",
        "pickup",
        "24 handmade Christmas cookies: gingerbread, amaretti, biscotti, and lemon shortbread. Baked fresh the day before the draw.",
    ),
    (
        "mike@borrowhood.local",
        "Weekend with Mike's Power Drill Set",
        1.50, 10, 3,
        "Pay Mike EUR 1.50 cash at the garage.",
        "pickup",
        "Win a free weekend rental of Mike's complete Bosch drill set. Includes all bits, charger, and carrying case.",
    ),
    (
        "pietro@borrowhood.local",
        "Aerial Photo of Your Property",
        3.00, 15, 14,
        "Pay EUR 3 via PayPal or cash at the coffee shop.",
        "digital",
        "Pietro flies his drone over your property and delivers 5 high-res aerial photos. Great for real estate listings or just showing off your view.",
    ),
    (
        "marco@borrowhood.local",
        "Custom Cutting Board — Your Name Carved",
        2.50, 20, 12,
        "EUR 2.50 cash or bank transfer.",
        "pickup",
        "Marco will carve your name into a handmade olive wood cutting board. The winner gets a personalized kitchen heirloom.",
    ),
    (
        "jake@borrowhood.local",
        "3D-Printed Custom Phone Case",
        1.00, 40, 8,
        "EUR 1 via Revolut or cash.",
        "shipping",
        "Jake designs and 3D-prints a custom phone case in your choice of color. iPhone or Android, any model from the last 3 years.",
    ),
    (
        "nino@borrowhood.local",
        "Free Campervan Weekend (Fri-Sun)",
        5.00, 10, 21,
        "EUR 5 per ticket, cash at the office or bank transfer.",
        "pickup",
        "Win a free weekend with one of Nino's campervans. Friday pickup, Sunday return. Fuel not included. Insurance included. Sicily road trip, anyone?",
    ),
]


async def main():
    from sqlalchemy import select
    from src.database import async_session
    from src.models.user import BHUser
    from src.models.item import BHItem
    from src.models.listing import BHListing, ListingStatus, ListingType
    from src.models.raffle import BHRaffle, RaffleStatus, RaffleDrawType, RaffleDelivery

    async with async_session() as db:
        # Check existing raffle listings
        existing = await db.scalar(
            select(BHListing.id).where(BHListing.listing_type == ListingType.RAFFLE).limit(1)
        )
        if existing:
            print("Raffle listings already exist — skipping seed")
            return

        created = 0
        for (email, item_name, price, max_tickets, days,
             instructions, delivery, description) in DEMO_RAFFLES:

            user = await db.scalar(
                select(BHUser).where(BHUser.email == email).where(BHUser.deleted_at.is_(None))
            )
            if not user:
                print(f"SKIP: user {email} not found")
                continue

            # Create item for the raffle prize
            item = BHItem(
                owner_id=user.id,
                name=item_name,
                description=description,
                category="other",
                condition="new",
                slug=item_name.lower().replace(" ", "-").replace("'", "")[:80],
            )
            db.add(item)
            await db.flush()

            # Create listing
            listing = BHListing(
                item_id=item.id,
                listing_type=ListingType.RAFFLE,
                status=ListingStatus.ACTIVE,
                price=price,
                currency="EUR",
            )
            db.add(listing)
            await db.flush()

            # Create raffle
            draw_date = datetime.now(timezone.utc) + timedelta(days=days)
            raffle = BHRaffle(
                listing_id=listing.id,
                organizer_id=user.id,
                ticket_price=price,
                currency="EUR",
                max_tickets=max_tickets,
                max_tickets_per_user=5,
                draw_type=RaffleDrawType.DATE,
                draw_date=draw_date,
                status=RaffleStatus.PUBLISHED,
                payment_methods=["cash", "paypal"],
                payment_instructions=instructions,
                delivery_method=RaffleDelivery(delivery),
                ticket_hold_hours=48,
                tos_accepted_at=datetime.now(timezone.utc),
            )
            db.add(raffle)
            created += 1
            print(f"  Created: {item_name} by {user.display_name} (draws {draw_date.date()})")

        await db.commit()
        print(f"\nDONE: {created} demo raffles created")


if __name__ == "__main__":
    asyncio.run(main())
