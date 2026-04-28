"""Seed Diego Monticciolo as a sim user on La Piazza.

Diego is a real person in Trapani -- Italian special forces veteran,
travel/tourism entrepreneur, born and raised local, English-speaking,
hangs out at Enoteca Civico 11, knows everyone. Angel met him at the
wine bar and Diego sponsored Angel's UniCredit account.

This script populates a *sim* profile so we can show Diego the app with
his own future already built. When Diego logs in fresh with Google,
run the companion `transfer_diego_sim.sql` to flip email + keycloak_id
to his real account -- the entire profile, services, event, raffle,
and help posts come with him.

Safety rails:
- All commercial listings (services, event, raffle) are created in
  DRAFT / PUBLISHED-pending status so strangers cannot book or RSVP
  before Diego approves.
- Help Board posts are OPEN (low risk -- if anyone replies before
  takeover, the reply just sits there; Diego sees it on his first login).
- Notifications disabled (notify_email / notify_telegram both False)
  so nothing tries to email diego-sim@lapiazza.app.

Idempotent: skips if a user with `diego-sim@lapiazza.app` already exists.

Run inside the container:
    docker exec -it borrowhood python3 /app/scripts/seed_diego_sim.py

Or locally if DATABASE_URL points at the dev Postgres:
    cd /home/angel/repos/helixnet/BorrowHood && python3 scripts/seed_diego_sim.py
"""
import asyncio
import shutil
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Path setup -- works both inside container (/app) and from repo root
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, "/app")
sys.path.insert(0, str(REPO_ROOT))


# ── Constants ─────────────────────────────────────────────────────────

DIEGO_EMAIL = "diego-sim@lapiazza.app"
DIEGO_SLUG = "diego-monticciolo"
DIEGO_DISPLAY_NAME = "Diego Monticciolo"

PHOTO_SOURCE = Path("/home/angel/Pictures/Diego/diego.jpg")
PHOTO_DEST = REPO_ROOT / "src" / "static" / "uploads" / "avatars" / "diego-monticciolo.jpg"
AVATAR_URL = "/static/uploads/avatars/diego-monticciolo.jpg"

# Trapani city center
TRAPANI_LAT = 38.0176
TRAPANI_LON = 12.5365

# Enoteca Civico 11 (Diego's hangout, owned by Francesco Rizzo)
ENOTECA_NAME = "Enoteca Civico 11"
ENOTECA_ADDRESS = "Via XXX Gennaio, 11, 91100 Trapani TP, Italia"
ENOTECA_LAT = 38.0177
ENOTECA_LON = 12.5374

DIEGO_TAGLINE = "Trapani concierge. Born here, know everyone. WhatsApp in 60 seconds."

DIEGO_BIO = (
    "Sono Diego, nato e cresciuto a Trapani. Conosco tutti, ogni vicolo, "
    "ogni profumo del porto.\n\n"
    "Veterano delle forze speciali italiane. Ora dedico le mie giornate "
    "a far vivere ai viaggiatori la Sicilia vera -- non i tour da "
    "cartolina, ma la Trapani che respira.\n\n"
    "Servizi: passeggiate guidate (italiano, inglese, dialetto siciliano), "
    "tour del vino a Marsala, gita a Erice in funivia, tramonto alle "
    "saline, transfer aeroporto. Tutto su misura.\n\n"
    "WhatsApp risposta entro 60 secondi quando lavoro.\n\n"
    "---\n\n"
    "I'm Diego, born and raised in Trapani. I know everyone here, every "
    "alley, every scent of the harbor.\n\n"
    "Italian special forces veteran. Now I spend my days showing "
    "travelers the real Sicily -- not the postcard version, but the "
    "Trapani that breathes.\n\n"
    "Services: guided walks (Italian, English, Sicilian dialect), Marsala "
    "wine tours, Erice cable car day trip, sunset at the salt flats, "
    "airport transfers. Everything tailored to you.\n\n"
    "WhatsApp response within 60 seconds when I'm working."
)

LANGUAGES = [
    ("it", "native"),
    ("scn", "native"),  # Sicilian dialect
    ("en", "B2"),
]

SKILLS = [
    {"skill_name": "Tour Guiding", "category": "services", "self_rating": 5, "years_experience": 10},
    {"skill_name": "Local Knowledge - Trapani", "category": "services", "self_rating": 5, "years_experience": 50},
    {"skill_name": "English Hospitality", "category": "services", "self_rating": 4, "years_experience": 15},
    {"skill_name": "Italian Special Forces Veteran", "category": "outdoor", "self_rating": 5, "years_experience": 20},
    {"skill_name": "Wine & Food Pairing", "category": "food", "self_rating": 4, "years_experience": 25},
]

# 5 service listings -- all DRAFT for safety
SERVICES = [
    {
        "name": "Trapani Walking Tour (English)",
        "slug": "diego-trapani-walking-tour",
        "description": (
            "Two hours through the historic center of Trapani with a born-local "
            "who speaks fluent English. Hidden corners, real history, the best "
            "espresso stop, and the harbor at golden hour. Small groups (max 6)."
        ),
        "category": "experiences",
        "subcategory": "walking-tour",
        "price": 25.0,
        "price_unit": "per_person",
        "max_participants": 6,
        "minimum_charge": 50.0,
    },
    {
        "name": "Erice Day Trip (Cable Car + Lunch)",
        "slug": "diego-erice-day-trip",
        "description": (
            "Half-day excursion from Trapani to Erice. Cable car up the mountain, "
            "walk the medieval streets, lunch at a family-run trattoria, return "
            "by late afternoon. Hotel pickup, cable car and lunch included."
        ),
        "category": "experiences",
        "subcategory": "day-trip",
        "price": 80.0,
        "price_unit": "per_person",
        "max_participants": 4,
        "minimum_charge": 160.0,
    },
    {
        "name": "Marsala Wine Tour",
        "slug": "diego-marsala-wine-tour",
        "description": (
            "Half-day to Marsala wine country. Two cellar visits including "
            "Tenute Parrinello (family-owned since 1936) and a smaller boutique "
            "cantina. Tastings included, light lunch at the second stop. "
            "Driver-guide, door-to-door from your hotel."
        ),
        "category": "experiences",
        "subcategory": "wine-tour",
        "price": 90.0,
        "price_unit": "per_person",
        "max_participants": 4,
        "minimum_charge": 180.0,
    },
    {
        "name": "Salt Flats Sunset Boat",
        "slug": "diego-saline-sunset-boat",
        "description": (
            "Late afternoon boat ride through the Saline di Trapani as the sun "
            "sets behind the salt mountains and windmills. Two hours on the "
            "water, swimming stop if weather permits, small aperitif on board. "
            "Wooden boat, max 6 people."
        ),
        "category": "experiences",
        "subcategory": "sunset-tour",
        "price": 60.0,
        "price_unit": "per_person",
        "max_participants": 6,
        "minimum_charge": 120.0,
    },
    {
        "name": "Airport Transfer Trapani-Birgi (TPS) -- door to door",
        "slug": "diego-airport-transfer-tps",
        "description": (
            "Door-to-door transfer between Trapani-Birgi airport (TPS) and "
            "anywhere in the Trapani area. Up to 4 passengers, luggage "
            "included. English-speaking driver, fixed price -- no meter "
            "surprises. Late flights welcome (give me 1 hour notice)."
        ),
        "category": "transport",
        "subcategory": "airport-transfer",
        "price": 35.0,
        "price_unit": "flat",
    },
]

# Help Board posts -- OPEN, low risk (no commercial commitment)
HELP_POSTS = [
    {
        "help_type": "offer",
        "urgency": "low",
        "title": "Visiting Trapani? Free local advice from a born-and-raised guide",
        "body": (
            "If you're heading to Trapani and you want to skip the tourist "
            "traps, ask me anything. Where to eat real cous cous (not the "
            "fake stuff), which beach is best on a windy day, how to time "
            "the salt flats sunset, where the locals drink. No charge, just "
            "drop a question in the replies. I respond fast.\n\n"
            "Se venite a Trapani e volete evitare le trappole turistiche, "
            "chiedete pure. Ristoranti veri, spiagge giuste, orari delle "
            "saline, dove bevono i trapanesi. Risposta gratis, scrivete "
            "nei commenti."
        ),
        "category": "experiences",
        "neighborhood": "Centro Storico",
        "content_language": "en",
        "status": "open",
    },
    {
        "help_type": "offer",
        "urgency": "low",
        "title": "English-speaking concierge / fixer in Trapani -- happy to help with bookings",
        "body": (
            "Born and raised in Trapani, fluent English, deep network in "
            "town (taxis, restaurants, boats, hotels, mechanics). If you're "
            "stuck and need someone to translate, recommend, or arrange "
            "something locally, message me. Free for small things, paid for "
            "longer engagements -- but always honest about which is which."
        ),
        "category": "services",
        "neighborhood": "Trapani Centro",
        "content_language": "en",
        "status": "open",
    },
    {
        "help_type": "need",
        "urgency": "normal",
        "title": "Looking for a partner driver / English-speaking guide for peak summer",
        "body": (
            "August gets busy and I can't be in two places at once. Looking "
            "for a reliable Trapani-based driver or guide with good English "
            "to refer overflow work to. Must be punctual, presentable, and "
            "know the Trapani / Erice / Marsala area. Reply or DM if "
            "interested.\n\n"
            "Cerco un autista o guida di Trapani con buon inglese per "
            "agosto. Puntualità e presenza obbligatorie."
        ),
        "category": "services",
        "neighborhood": "Trapani",
        "content_language": "en",
        "status": "open",
    },
]


# ── Main ──────────────────────────────────────────────────────────────

async def main():
    import importlib
    import pkgutil
    from sqlalchemy import select
    from src.database import async_session
    # Register every model module so SQLAlchemy can resolve FKs at flush
    # time (BHUser FKs to bh_community, etc., and not every model file is
    # exposed through src/models/__init__.py).
    import src.models as _models_pkg
    for _, _modname, _ in pkgutil.iter_modules(_models_pkg.__path__):
        importlib.import_module(f"src.models.{_modname}")
    from src.models.user import (
        AccountStatus, BadgeTier, BHUser, BHUserLanguage, BHUserPoints,
        BHUserSkill, CEFRLevel, WorkshopType,
    )
    from src.models.item import BHItem, ItemCondition, ItemType
    from src.models.listing import BHListing, ListingStatus, ListingType
    from src.models.helpboard import (
        BHHelpPost, HelpStatus, HelpType, HelpUrgency,
    )
    from src.models.raffle import (
        BHRaffle, RaffleDelivery, RaffleDrawType, RaffleStatus,
    )

    async with async_session() as db:
        # Idempotency check
        existing = await db.scalar(
            select(BHUser).where(BHUser.email == DIEGO_EMAIL)
        )
        if existing:
            print(f"User {DIEGO_EMAIL} already exists (slug={existing.slug}). Skipping.")
            return

        # Copy avatar
        if PHOTO_SOURCE.exists():
            PHOTO_DEST.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(PHOTO_SOURCE, PHOTO_DEST)
            print(f"Avatar copied: {PHOTO_DEST}")
        else:
            print(f"WARNING: photo not found at {PHOTO_SOURCE} -- avatar_url will still be set")

        # ── Create Diego user ──────────────────────────────────────────
        diego = BHUser(
            keycloak_id=str(uuid.uuid4()),  # placeholder until Diego's real KC id
            email=DIEGO_EMAIL,
            display_name=DIEGO_DISPLAY_NAME,
            slug=DIEGO_SLUG,
            workshop_name="Sicily Concierge",
            workshop_type=WorkshopType.LODGE,
            tagline=DIEGO_TAGLINE,
            bio=DIEGO_BIO,
            avatar_url=AVATAR_URL,
            city="Trapani",
            state_region="Sicilia",
            country_code="IT",
            latitude=TRAPANI_LAT,
            longitude=TRAPANI_LON,
            account_status=AccountStatus.ACTIVE,
            badge_tier=BadgeTier.ACTIVE,
            offers_pickup=True,           # airport transfers
            offers_training=False,
            offers_repair=False,
            offers_custom_orders=True,    # tailored experiences
            seller_type="personal",
            accepted_payments="cash,paypal,iban",
            notify_email=False,           # sim mailbox -- no notifications anywhere
            notify_telegram=False,
            tos_accepted_at=datetime.now(timezone.utc),
        )
        db.add(diego)
        await db.flush()
        print(f"Created user: {diego.display_name} (slug={diego.slug}, id={diego.id})")

        # Languages
        for code, prof in LANGUAGES:
            db.add(BHUserLanguage(
                user_id=diego.id,
                language_code=code,
                proficiency=CEFRLevel(prof),
            ))

        # Skills
        for s in SKILLS:
            db.add(BHUserSkill(
                user_id=diego.id,
                skill_name=s["skill_name"],
                category=s["category"],
                self_rating=s["self_rating"],
                years_experience=s.get("years_experience"),
            ))

        # Points (start at zero)
        db.add(BHUserPoints(user_id=diego.id, total_points=0))

        # ── Service listings (DRAFT) ───────────────────────────────────
        for svc in SERVICES:
            item = BHItem(
                owner_id=diego.id,
                name=svc["name"],
                slug=svc["slug"],
                description=svc["description"],
                content_language="en",
                item_type=ItemType.SERVICE,
                category=svc["category"],
                subcategory=svc.get("subcategory"),
                latitude=TRAPANI_LAT,
                longitude=TRAPANI_LON,
            )
            db.add(item)
            await db.flush()

            listing = BHListing(
                item_id=item.id,
                listing_type=ListingType.SERVICE,
                status=ListingStatus.DRAFT,         # safety -- not visible publicly
                price=svc["price"],
                price_unit=svc["price_unit"],
                currency="EUR",
                pickup_only=False,
                delivery_available=True,            # mobile concierge
                minimum_charge=svc.get("minimum_charge"),
                max_participants=svc.get("max_participants"),
                notes="Confirm details over WhatsApp before booking.",
            )
            db.add(listing)
            print(f"  Service (DRAFT): {svc['name']} -- EUR {svc['price']:.2f} {svc['price_unit']}")

        # ── May 1 Event @ Enoteca Civico 11 (DRAFT, pending Francesco) ─
        event_item = BHItem(
            owner_id=diego.id,
            name="Aperitivo & La Piazza Demo @ Enoteca Civico 11",
            slug="diego-may1-aperitivo-civico11",
            description=(
                "Festa del Lavoro aperitivo at Enoteca Civico 11. Stop by, meet "
                "Diego, taste a glass of local wine, and see how La Piazza "
                "works for travelers and locals alike. No agenda -- just good "
                "wine, real conversation, and a quick demo for anyone curious. "
                "Hosted with the blessing of Francesco Rizzo (Civico 11)."
            ),
            content_language="en",
            item_type=ItemType.SERVICE,
            category="festival",
            latitude=ENOTECA_LAT,
            longitude=ENOTECA_LON,
        )
        db.add(event_item)
        await db.flush()

        # May 1, 2026 -- 19:00 to 22:00 Europe/Rome (UTC+2 in May)
        event_start = datetime(2026, 5, 1, 17, 0, 0, tzinfo=timezone.utc)  # 19:00 local
        event_end = datetime(2026, 5, 1, 20, 0, 0, tzinfo=timezone.utc)    # 22:00 local

        event_listing = BHListing(
            item_id=event_item.id,
            listing_type=ListingType.EVENT,
            status=ListingStatus.DRAFT,             # PUBLISH only after Francesco's blessing
            price=0.0,                               # free entry
            currency="EUR",
            event_start=event_start,
            event_end=event_end,
            event_venue=ENOTECA_NAME,
            event_address=ENOTECA_ADDRESS,
            notes=(
                "Free aperitivo, drinks at standard Civico 11 prices. "
                "Walk-ins welcome. RSVPs help us tell Francesco how many "
                "stools to put out."
            ),
            max_participants=30,
        )
        db.add(event_listing)
        print(f"  Event (DRAFT): May 1 aperitivo @ {ENOTECA_NAME}")

        # ── Raffle: Day Trip Tour (DRAFT, ticket EUR 0.50 x 20 = EUR 10 cap) ─
        raffle_item = BHItem(
            owner_id=diego.id,
            name="Erice Day Trip Raffle (for two)",
            slug="diego-raffle-erice-day-trip",
            description=(
                "Win a free Erice day trip for two -- cable car, "
                "medieval streets, lunch at a trattoria, hotel pickup. "
                "Normally EUR 160 (2 people). Ticket EUR 0.50 -- think of "
                "it as putting your name in a hat at the cafe. Winner picks "
                "the date once we connect on WhatsApp."
            ),
            content_language="en",
            item_type=ItemType.SERVICE,
            category="experiences",
            latitude=TRAPANI_LAT,
            longitude=TRAPANI_LON,
        )
        db.add(raffle_item)
        await db.flush()

        raffle_listing = BHListing(
            item_id=raffle_item.id,
            listing_type=ListingType.RAFFLE,
            status=ListingStatus.DRAFT,
            price=0.50,
            currency="EUR",
        )
        db.add(raffle_listing)
        await db.flush()

        # Newcomer trust tier: max 10 EUR total raffle value
        # 0.50 * 20 = 10.00 -- right at the cap
        raffle = BHRaffle(
            listing_id=raffle_listing.id,
            organizer_id=diego.id,
            ticket_price=0.50,
            currency="EUR",
            max_tickets=20,
            max_tickets_per_user=3,
            draw_type=RaffleDrawType.DATE,
            draw_date=datetime.now(timezone.utc) + timedelta(days=21),
            status=RaffleStatus.DRAFT,
            payment_methods=["cash", "paypal"],
            payment_instructions=(
                "Pay EUR 0.50 cash at Enoteca Civico 11 (tell Diego or "
                "Francesco) or PayPal -- ask Diego for the link on WhatsApp."
            ),
            delivery_method=RaffleDelivery.PICKUP,
            ticket_hold_hours=72,
            tos_accepted_at=datetime.now(timezone.utc),
        )
        db.add(raffle)
        print(f"  Raffle (DRAFT): Erice Day Trip for two -- 20 tickets at EUR 0.50")

        # ── Help Board posts (OPEN -- low risk) ────────────────────────
        for hp in HELP_POSTS:
            post = BHHelpPost(
                author_id=diego.id,
                help_type=HelpType(hp["help_type"]),
                status=HelpStatus(hp["status"]),
                urgency=HelpUrgency(hp["urgency"]),
                title=hp["title"],
                body=hp["body"],
                category=hp["category"],
                content_language=hp["content_language"],
                neighborhood=hp.get("neighborhood"),
            )
            db.add(post)
            print(f"  Help post ({hp['help_type']}): {hp['title'][:60]}...")

        await db.commit()
        print()
        print("=" * 60)
        print(f"DONE: Diego sim seeded.")
        print(f"  User:  {DIEGO_DISPLAY_NAME} ({DIEGO_EMAIL})")
        print(f"  Slug:  /u/{DIEGO_SLUG}")
        print(f"  Id:    {diego.id}")
        print()
        print("Next steps:")
        print("  1. Preview as admin: /u/diego-monticciolo")
        print("  2. Show Diego on his phone (services in DRAFT; toggle ACTIVE")
        print("     when he sees them and approves).")
        print("  3. Get Francesco's blessing for the May 1 event before")
        print("     publishing it.")
        print("  4. When Diego logs in fresh with Google, run:")
        print("     scripts/transfer_diego_sim.sql (set REAL_EMAIL +")
        print("     REAL_KEYCLOAK_ID at top before running).")


if __name__ == "__main__":
    asyncio.run(main())
