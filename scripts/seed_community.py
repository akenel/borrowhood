"""Seed the 'community' category group with rich Sicily-flavored items.

Covers skill_exchange, neighborhood_help, local_food, rides.
Idempotent: skips items whose slug already exists.

Usage (on the UAT server):
    docker exec borrowhood python scripts/seed_community.py

Locally:
    ./scripts/dev-server.sh --test scripts/seed_community.py   # wrong, it's not a test
    BH_DATABASE_URL=... python scripts/seed_community.py
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models.item import BHItem, BHItemMedia, ItemType, ItemCondition, MediaType
from src.models.listing import BHListing, ListingStatus, ListingType
from src.models.user import BHUser


# ── User emails -> slugs ──
USER_EMAILS = {
    "sally": "sally@borrowhood.local",
    "mike": "mike@borrowhood.local",
    "pietro": "pietro@borrowhood.local",
    "nicolo": "nicolo@borrowhood.local",
    "leonardo": "leonardo@borrowhood.local",
    "nino": "nino@borrowhood.local",
    "jake": "jake@borrowhood.local",
    "anne": "anne@borrowhood.local",
    "maria": "maria@borrowhood.local",
    "sofia": "sofiaferretti@borrowhood.local",
    "angel": "angel@borrowhood.local",
}


# ── Items to seed: (owner_key, category, item_type, name, description, story, tags, listing_type, price, price_unit, deposit, image_prompt) ──
COMMUNITY_SEEDS = [
    # ── skill_exchange ──
    ("mike", "skill_exchange", "SERVICE",
     "Trade: Welding lessons for Italian lessons",
     "I'll teach you basic MIG welding if you help me finally speak proper Italian. I've been in Trapani 3 years and still order coffee wrong.",
     "Swapping skills beats swapping money. Two evenings a month, your kitchen or my garage.",
     "skill swap, italian, welding, language exchange",
     "offer", None, "negotiable", None,
     "welding sparks and italian espresso cups old rustic workshop warm light"),

    ("sally", "skill_exchange", "SERVICE",
     "Sourdough starter + weekly baking coaching",
     "Healthy starter from 2024. I'll come help you with your first 3 loaves if you teach me something I don't know (photography? a language? carpentry?).",
     "My nonna taught me. Time to pass it on.",
     "sourdough, baking, skill swap, teaching, food",
     "offer", None, "negotiable", None,
     "sourdough loaf rustic kitchen flour hands warm"),

    ("leonardo", "skill_exchange", "SERVICE",
     "Drawing fundamentals in exchange for gardening help",
     "I'll teach you to draw what you see -- not what you think you see. Three sessions of 2 hours. Need help with my olive grove in return.",
     "Everyone says they can't draw. Everyone is wrong about themselves.",
     "drawing, art, gardening, skill swap, lessons",
     "offer", None, "negotiable", None,
     "artist hands pencil sketching olive tree sicilian morning"),

    ("nicolo", "skill_exchange", "SERVICE",
     "Jiu-jitsu fundamentals for help with my website",
     "Two hours of private BJJ for two hours of web help. I have a dojo site that needs love. You want to know how to escape a mount? Perfect trade.",
     "I can throw people. I can't make a WordPress work.",
     "jiu-jitsu, bjj, web, skill swap, dojo",
     "offer", None, "negotiable", None,
     "jiu jitsu dojo mat silhouette training evening light"),

    ("anne", "skill_exchange", "SERVICE",
     "QA testing tips for any homemade meal",
     "I'll break your app with my Android bare hands. You feed me. Seriously, 1 hour of structured testing + a written report in exchange for dinner.",
     "Bugs taste better than complaints. Let's make the app stronger together.",
     "qa, testing, skill swap, dinner, cooking",
     "offer", None, "negotiable", None,
     "laptop screen testing checklist sicilian kitchen evening"),

    # ── neighborhood_help ──
    ("maria", "neighborhood_help", "SERVICE",
     "Need a hand fixing my squeaky shutters",
     "Persiane siciliane, 70-year-old wood, squeak like crazy. Trade: I bake bread for a week, you bring the WD-40 and an hour of your time.",
     "The sound wakes my grandson. Everything else I can live with.",
     "neighborhood, shutters, help, repair, Paceco",
     "offer", None, "negotiable", None,
     "old sicilian persiane shutters warm morning light"),

    ("pietro", "neighborhood_help", "SERVICE",
     "Drone over your garden -- free aerial photos",
     "Training for a certification. Come catch me on a Saturday morning in the Erice area and I'll take professional overhead shots of your garden/villa -- free, high-res, no strings.",
     "I need practice hours. You get a view of your home nobody else has.",
     "drone, photography, neighborhood, free, aerial",
     "giveaway", None, "flat", None,
     "drone aerial view sicilian villa garden olive trees morning"),

    ("nino", "neighborhood_help", "SERVICE",
     "Airport run for free -- if you're on my route",
     "I drive from Trapani to the airport and back 4x/week. If your flight matches my timing, hop in. Free. Just be on time.",
     "Empty seats are a waste. Fill them up, save petrol together.",
     "airport, rides, neighborhood, transport, free",
     "giveaway", None, "flat", None,
     "camper van sicilian highway dawn empty road"),

    ("angel", "neighborhood_help", "SERVICE",
     "Bike tire patches, nothing fancy, just help",
     "I've patched a lot of bike tires in my life. If yours goes flat in Trapani centro, message me. Bring a soda as thanks.",
     "Started when I was 8. Haven't stopped. The smell of rubber cement is home.",
     "bike, repair, neighborhood, help, cycling",
     "offer", None, "negotiable", None,
     "bike tire repair hands rubber patch afternoon workshop"),

    ("sofia", "neighborhood_help", "SERVICE",
     "Cookie run: I pick up your bakery order Friday",
     "I go to Sofia's Bakes every Friday at 3. If you live in San Vito and can't get there, give me your order by Thursday and I'll drop it on your step.",
     "Best cookies in Sicily. Nobody should miss them over a 20 minute drive.",
     "cookies, neighborhood, delivery, friday, san vito",
     "offer", None, "negotiable", None,
     "cookie bakery basket friday afternoon sicilian village"),

    # ── local_food ──
    ("sally", "local_food", "PHYSICAL",
     "Homemade cannoli -- Thursday batches",
     "I bake 20 shells + ricotta filling every Thursday. EUR 2 each. Pick up from my kitchen. Fill them yourself right before eating, trust me.",
     "My mom's recipe. The shells shatter like old glass. That's the point.",
     "cannoli, food, sicilian, thursday, sally",
     "sell", 2.00, "flat", 0,
     "sicilian cannoli pastry ricotta filling rustic kitchen"),

    ("sofia", "local_food", "PHYSICAL",
     "Sicilian lemons by the kilo -- my garden, zero spray",
     "I have two lemon trees and too many lemons. 1 kg for EUR 2, 3 kg for EUR 5. No pesticides, picked when you order.",
     "Dad planted them in 1987. They've been giving ever since.",
     "lemons, local, food, sicilian, organic",
     "sell", 2.00, "flat", 0,
     "sicilian lemons tree wooden basket rustic garden sunlight"),

    ("maria", "local_food", "PHYSICAL",
     "Fresh sourdough loaves every Saturday",
     "My garden-oven bread, 24h fermentation, local flour. EUR 4 each. Reserve by Friday evening, pick up Saturday morning.",
     "The oven belonged to my grandmother. She used to bake for the village. Now I do.",
     "bread, sourdough, local, saturday, sicilian",
     "sell", 4.00, "flat", 0,
     "sourdough loaf crust wood oven rustic sicilian morning"),

    ("leonardo", "local_food", "PHYSICAL",
     "Olive oil -- 2024 harvest, first cold press",
     "5 liters of my family's olive oil, first cold press, October 2024. EUR 35/5L. You can smell the leaves in it. Bring your own bottle or pay EUR 2 more.",
     "The trees are over 200 years old. The oil tastes like something you remember.",
     "olive oil, local, food, harvest, first press",
     "sell", 35.00, "flat", 0,
     "olive oil bottle pouring amber green sicilian groves"),

    ("angel", "local_food", "PHYSICAL",
     "Black wolf espresso blend -- 250g",
     "I don't roast. But I know a guy. Local Trapani roaster, dark blend, strong, for people who take coffee like Sicilians. EUR 8/250g.",
     "Every package is the same as what I pour at home.",
     "coffee, espresso, local, sicilian, dark",
     "sell", 8.00, "flat", 0,
     "espresso beans dark roast rustic sicilian cafe warm"),

    # ── rides ──
    ("nino", "rides", "SERVICE",
     "Weekly Trapani ↔ Palermo -- Friday return Sunday",
     "I do this trip every weekend. Seats for 3. EUR 15 each, splits the petrol. Leaves Trapani at 9am Friday, back Sunday at 7pm.",
     "Been doing the drive for years. Nice to have company for once.",
     "rides, palermo, weekend, carpool, trapani",
     "offer", 15.00, "flat", None,
     "camper van sicilian highway palermo sunset road"),

    ("andre", "rides", "SERVICE",
     "Early morning airport, any day",
     "Have car, will drive. EUR 30 Trapani city to TPS airport, reasonable hours (04:00 pickup OK). Text me the night before.",
     "I wake up at 3:30 naturally. Might as well earn an espresso doing it.",
     "rides, airport, early, trapani, taxi alternative",
     "offer", 30.00, "flat", None,
     "car headlights sicilian dawn airport road"),

    ("pietro", "rides", "SERVICE",
     "Erice run -- shuttle up the mountain",
     "Tourists always need a lift up. EUR 20 return, 2 seats. I need to go anyway for drone shoots most days.",
     "The cable car is beautiful. My car is faster.",
     "rides, erice, shuttle, mountain, tourists",
     "offer", 20.00, "flat", None,
     "winding road mountain erice sicily car view"),

    ("nicolo", "rides", "SERVICE",
     "Dojo pickup -- students under 16 only",
     "If your kid comes to my BJJ class but you can't drop them off, I can pick up in Trapani centro. Free. Parents and I exchange phones first.",
     "Consistency matters more at 12 than at 30.",
     "rides, kids, dojo, jiu-jitsu, trapani",
     "giveaway", None, "flat", None,
     "car door opening kid with backpack sicilian street afternoon"),

    ("mike", "rides", "SERVICE",
     "Moving help -- small van + strong back",
     "I have a Transit Custom and 30 years of lifting. EUR 40/hour including fuel. Trapani province only.",
     "Moved 200 apartments in Switzerland. Same joints, different sun.",
     "moving, van, help, muscle, trapani",
     "offer", 40.00, "per_hour", None,
     "small white moving van sicilian street boxes loading"),
]


def _pollinations_url(prompt: str) -> str:
    """Generate a Pollinations image URL from a prompt."""
    from urllib.parse import quote
    return f"https://image.pollinations.ai/prompt/{quote(prompt)}?width=800&height=600&nologo=true"


async def run() -> None:
    async for db in get_db():
        # Load users map
        users_result = await db.execute(
            select(BHUser).where(BHUser.email.in_(list(USER_EMAILS.values())))
        )
        users_by_email = {u.email: u for u in users_result.scalars().all()}

        # Ensure andre if present; if missing, fall back to angel
        andre = await db.execute(
            select(BHUser).where(BHUser.email == "andre@borrowhood.local")
        )
        andre_user = andre.scalars().first()
        if andre_user:
            users_by_email["andre@borrowhood.local"] = andre_user

        created = 0
        skipped = 0
        for owner_key, category, item_type, name, description, story, tags, listing_type, price, price_unit, deposit, img_prompt in COMMUNITY_SEEDS:
            email = (
                USER_EMAILS.get(owner_key)
                or ("andre@borrowhood.local" if owner_key == "andre" else None)
            )
            owner = users_by_email.get(email) if email else None
            if not owner:
                # Fall back to angel
                owner = users_by_email.get("angel@borrowhood.local")
            if not owner:
                print(f"!! no owner for {name}, skipping")
                continue

            # Slug from name
            slug_base = (
                name.lower()
                .replace("--", "-")
                .replace("/", "-")
                .replace(":", "")
                .replace(",", "")
                .replace(".", "")
                .replace("'", "")
                .replace("(", "")
                .replace(")", "")
                .replace("?", "")
                .replace("!", "")
                .replace("↔", "to")
                .replace(" ", "-")
            )
            # Strip multiple hyphens
            while "--" in slug_base:
                slug_base = slug_base.replace("--", "-")
            slug_base = slug_base.strip("-")[:100]

            # Check for existing
            existing = await db.execute(
                select(BHItem).where(BHItem.slug == slug_base)
            )
            if existing.scalars().first():
                skipped += 1
                continue

            item = BHItem(
                owner_id=owner.id,
                name=name,
                slug=slug_base,
                description=description,
                story=story,
                content_language="en",
                item_type=ItemType[item_type],
                category=category,
                condition=ItemCondition.GOOD,
                tags=tags,
            )
            db.add(item)
            await db.flush()

            # Add image
            media = BHItemMedia(
                item_id=item.id,
                url=_pollinations_url(img_prompt),
                alt_text=name,
                media_type=MediaType.PHOTO,
                sort_order=0,
            )
            db.add(media)

            # Add listing
            listing = BHListing(
                item_id=item.id,
                listing_type=ListingType[listing_type.upper()],
                status=ListingStatus.ACTIVE,
                price=price,
                price_unit=price_unit,
                currency="EUR",
                deposit=deposit,
                delivery_available=False,
                pickup_only=True,
                version=1,
            )
            db.add(listing)
            created += 1

        await db.commit()
        print(f"== Community seed: created={created}, skipped={skipped} (already existed)")


if __name__ == "__main__":
    asyncio.run(run())
