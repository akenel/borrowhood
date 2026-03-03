"""Seed data loader.

Loads seed_data/seed.json into the database.
Creates users, items, listings, teams, and points.
Run once on first startup or via CLI.
"""

import json
import logging
import uuid
from datetime import date
from pathlib import Path

from slugify import slugify
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.item import BHItem, BHItemMedia, ItemCondition, ItemType, MediaType
from src.models.listing import BHListing, ListingStatus, ListingType
from src.models.rental import BHRental, RentalStatus
from src.models.review import BHReview
from src.models.user import (
    AccountStatus,
    BadgeTier,
    BHUser,
    BHUserLanguage,
    BHUserPoints,
    BHUserSkill,
    BHUserSocialLink,
    CEFRLevel,
    WorkshopType,
)
from src.models.helpboard import BHHelpPost, BHHelpReply, HelpType, HelpStatus, HelpUrgency
from src.models.workshop import BHWorkshopMember, TeamRole

logger = logging.getLogger(__name__)

SEED_FILE = Path(__file__).parent.parent.parent / "seed_data" / "seed.json"


def _enum_val(enum_class, value):
    """Safely get enum value, with fallback mappings for seed data."""
    if value is None:
        return None
    try:
        return enum_class(value)
    except ValueError:
        from src.models.user import CEFRLevel, WorkshopType
        # Map common natural-language proficiency to CEFR
        if enum_class is CEFRLevel:
            _map = {
                "beginner": "A1", "elementary": "A2",
                "intermediate": "B1", "conversational": "B1",
                "upper_intermediate": "B2", "advanced": "C1",
                "fluent": "C2", "proficient": "C2",
            }
            mapped = _map.get(value.lower())
            if mapped:
                return CEFRLevel(mapped)
        # Fallback for any enum: log warning and return None
        logger.warning("Unknown %s value %r -- skipping", enum_class.__name__, value)
        return None


def _parse_date(value):
    """Parse date string (YYYY-MM-DD) to date object."""
    if not value:
        return None
    try:
        parts = value.split("-")
        return date(int(parts[0]), int(parts[1]), int(parts[2]))
    except (ValueError, IndexError):
        return None


async def seed_database(db: AsyncSession) -> dict:
    """Load seed data into database. Returns counts of created entities."""

    # Check if already seeded
    existing = await db.scalar(select(BHUser.id).limit(1))
    if existing:
        logger.info("Database already seeded, skipping")
        return {"status": "already_seeded"}

    with open(SEED_FILE) as f:
        data = json.load(f)

    counts = {"users": 0, "items": 0, "listings": 0, "teams": 0, "rentals": 0, "reviews": 0}
    user_map = {}  # slug -> user object
    listing_map = {}  # item_slug -> first listing object

    # Create users
    for u in data["users"]:
        user = BHUser(
            keycloak_id=str(uuid.uuid4()),  # Placeholder until KC realm is set up
            email=u["email"],
            display_name=u["display_name"],
            slug=u["slug"],
            date_of_birth=_parse_date(u.get("date_of_birth")),
            mother_name=u.get("mother_name"),
            father_name=u.get("father_name"),
            workshop_name=u.get("workshop_name"),
            workshop_type=_enum_val(WorkshopType, u.get("workshop_type")),
            tagline=u.get("tagline"),
            bio=u.get("bio"),
            telegram_username=u.get("telegram_username"),
            city=u.get("city"),
            country_code=u.get("country_code"),
            latitude=u.get("latitude"),
            longitude=u.get("longitude"),
            offers_delivery=u.get("offers_delivery", False),
            offers_pickup=u.get("offers_pickup", False),
            offers_training=u.get("offers_training", False),
            offers_custom_orders=u.get("offers_custom_orders", False),
            offers_repair=u.get("offers_repair", False),
            account_status=AccountStatus.ACTIVE,
            badge_tier=_enum_val(BadgeTier, u.get("badge_tier", "newcomer")),
        )
        db.add(user)
        await db.flush()
        user_map[u["slug"]] = user

        # Languages
        for lang in u.get("languages", []):
            db.add(BHUserLanguage(
                user_id=user.id,
                language_code=lang["language_code"],
                proficiency=_enum_val(CEFRLevel, lang["proficiency"]),
            ))

        # Skills
        for skill in u.get("skills", []):
            db.add(BHUserSkill(
                user_id=user.id,
                skill_name=skill["skill_name"],
                category=skill["category"],
                self_rating=skill.get("self_rating", 3),
                years_experience=skill.get("years_experience"),
            ))

        # Social links
        for link in u.get("social_links", []):
            db.add(BHUserSocialLink(
                user_id=user.id,
                platform=link["platform"],
                url=link["url"],
                label=link.get("label"),
            ))

        # Points
        pts = u.get("points")
        if pts:
            db.add(BHUserPoints(
                user_id=user.id,
                total_points=pts.get("total_points", 0),
                rentals_completed=pts.get("rentals_completed", 0),
                reviews_given=pts.get("reviews_given", 0),
                reviews_received=pts.get("reviews_received", 0),
                items_listed=pts.get("items_listed", 0),
                helpful_flags=pts.get("helpful_flags", 0),
            ))

        counts["users"] += 1

    # Create items and listings
    for item_data in data["items"]:
        owner = user_map.get(item_data["owner_slug"])
        if not owner:
            logger.warning("Owner %s not found, skipping item %s", item_data["owner_slug"], item_data["name"])
            continue

        item = BHItem(
            owner_id=owner.id,
            name=item_data["name"],
            slug=item_data["slug"],
            description=item_data.get("description"),
            story=item_data.get("story"),
            content_language=item_data.get("content_language", "en"),
            item_type=_enum_val(ItemType, item_data["item_type"]),
            category=item_data["category"],
            subcategory=item_data.get("subcategory"),
            condition=_enum_val(ItemCondition, item_data.get("condition")),
            brand=item_data.get("brand"),
            model=item_data.get("model"),
            needs_equipment=item_data.get("needs_equipment"),
            compatible_with=item_data.get("compatible_with"),
            latitude=owner.latitude,
            longitude=owner.longitude,
        )
        db.add(item)
        await db.flush()

        # Media
        for media in item_data.get("media", []):
            db.add(BHItemMedia(
                item_id=item.id,
                media_type=_enum_val(MediaType, media["media_type"]),
                url=media["url"],
                alt_text=media["alt_text"],
            ))

        # Listings
        for listing in item_data.get("listings", []):
            listing_obj = BHListing(
                item_id=item.id,
                listing_type=_enum_val(ListingType, listing["listing_type"]),
                status=ListingStatus.ACTIVE,
                price=listing.get("price"),
                price_unit=listing.get("price_unit"),
                currency=listing.get("currency", "EUR"),
                deposit=listing.get("deposit"),
                min_rental_days=listing.get("min_rental_days"),
                max_rental_days=listing.get("max_rental_days"),
                delivery_available=listing.get("delivery_available", False),
                pickup_only=listing.get("pickup_only", True),
                notes=listing.get("notes"),
            )
            db.add(listing_obj)
            await db.flush()
            if item_data["slug"] not in listing_map:
                listing_map[item_data["slug"]] = (listing_obj, owner)
            counts["listings"] += 1

        counts["items"] += 1

    # Create teams
    for team in data.get("teams", []):
        owner = user_map.get(team["workshop_owner_slug"])
        member = user_map.get(team["member_slug"])
        if owner and member:
            db.add(BHWorkshopMember(
                workshop_owner_id=owner.id,
                member_id=member.id,
                role=_enum_val(TeamRole, team["role"]),
                invite_message=team.get("invite_message"),
                accepted=team.get("accepted", False),
            ))
            counts["teams"] += 1

    # Create seed rentals and reviews (makes the app look alive)
    seed_reviews = [
        {
            "item_slug": "bosch-professional-drill-driver-set",
            "renter_slug": "sallys-kitchen",
            "rating": 5,
            "title": "Perfect drill, great neighbor!",
            "body": "Mike's drill set is professional grade. He even included extra bits and showed me how to use the torque settings. Will definitely rent again.",
        },
        {
            "item_slug": "bosch-professional-drill-driver-set",
            "renter_slug": "marias-garden",
            "rating": 4,
            "title": "Solid equipment, easy pickup",
            "body": "Used this for a garden fence project. Powerful drill, batteries lasted all day. Pickup and return were smooth via lockbox.",
        },
        {
            "item_slug": "professional-cookie-cutter-set-200-pieces",
            "renter_slug": "mikes-garage",
            "rating": 5,
            "title": "My daughter loved these!",
            "body": "200 shapes is no joke. We made cookies for the whole block. Sally had them perfectly organized by theme. Amazing collection.",
        },
        {
            "item_slug": "kitchenaid-stand-mixer-artisan-5qt",
            "renter_slug": "marias-garden",
            "rating": 5,
            "title": "Made bread like a pro",
            "body": "First time using a stand mixer. Sally's KitchenAid is immaculate. The dough hook attachment changed my life. My focaccia finally came out right.",
        },
        {
            "item_slug": "floor-jack-jack-stands-3-ton",
            "renter_slug": "sallys-kitchen",
            "rating": 4,
            "title": "Heavy duty, does the job",
            "body": "Needed this for an oil change on the van. Professional quality. Mike even dropped it off at my place. Only 4 stars because the instructions were a bit unclear.",
        },
    ]

    all_users = list(user_map.values())
    for rev_data in seed_reviews:
        listing_info = listing_map.get(rev_data["item_slug"])
        renter = user_map.get(rev_data["renter_slug"])
        if not listing_info or not renter:
            continue

        listing_obj, owner = listing_info

        # Skip if renter is the owner
        if renter.id == owner.id:
            continue

        # Create a completed rental
        rental = BHRental(
            listing_id=listing_obj.id,
            renter_id=renter.id,
            status=RentalStatus.COMPLETED,
            renter_message="Would love to borrow this!",
        )
        db.add(rental)
        await db.flush()
        counts["rentals"] += 1

        # Create the review
        weight = {
            BadgeTier.NEWCOMER: 1.0, BadgeTier.ACTIVE: 2.0, BadgeTier.TRUSTED: 5.0,
            BadgeTier.PILLAR: 8.0, BadgeTier.LEGEND: 10.0,
        }.get(renter.badge_tier, 1.0)

        review = BHReview(
            rental_id=rental.id,
            reviewer_id=renter.id,
            reviewee_id=owner.id,
            rating=rev_data["rating"],
            title=rev_data["title"],
            body=rev_data["body"],
            reviewer_tier=renter.badge_tier.value,
            weight=weight,
        )
        db.add(review)
        counts["reviews"] += 1

    # Create help board posts and replies
    help_posts = [
        {
            "author_slug": "mikes-garage",
            "help_type": "need",
            "urgency": "urgent",
            "title": "Need someone to help move a lathe -- too heavy for one person",
            "body": "I bought a used wood lathe (about 120kg) and need help moving it from a van into my garage. It's on a pallet. Two strong people + a furniture dolly should do it. Can offer beer and pizza after. This Saturday morning if possible.",
            "category": "power_tools",
            "neighborhood": "Bonagia",
            "content_language": "en",
            "status": "open",
            "replies": [
                {"author_slug": "sallys-kitchen", "body": "My husband can help! He moved our fridge last week. Saturday works. What time?"},
                {"author_slug": "marias-garden", "body": "I have a furniture dolly you can borrow. DM me on Telegram."},
            ],
        },
        {
            "author_slug": "sallys-kitchen",
            "help_type": "offer",
            "urgency": "normal",
            "title": "Free baking lessons for beginners -- sourdough, focaccia, cookies",
            "body": "I've been baking for 20 years and I'd love to teach. I have all the equipment in my kitchen. Groups of 2-3 people max. You bring the ingredients (I'll tell you what to buy), I teach you the technique. Weekday afternoons work best for me.",
            "category": "kitchen",
            "neighborhood": "Centro Storico",
            "content_language": "en",
            "status": "open",
            "replies": [
                {"author_slug": "mikes-garage", "body": "My daughter would LOVE this. She's 14 and obsessed with the British Bake Off. Can she come?"},
            ],
        },
        {
            "author_slug": "marias-garden",
            "help_type": "need",
            "urgency": "normal",
            "title": "Looking for someone to help prune olive trees (4 trees)",
            "body": "I have 4 olive trees in my yard that haven't been pruned in 2 years. They're getting wild. I have the tools (loppers, hand saw) but I don't know the proper technique. Would love someone experienced to show me how or do it together.",
            "category": "garden",
            "neighborhood": "Xiare",
            "content_language": "en",
            "status": "open",
            "replies": [
                {"author_slug": "angel-hq", "body": "Ho potato ulivi per 40 anni. Posso aiutarti sabato. Porta guanti buoni. / I've been pruning olives for 40 years. I can help Saturday. Bring good gloves."},
            ],
        },
        {
            "author_slug": "marcos-workshop",
            "help_type": "offer",
            "urgency": "low",
            "title": "Posso insegnare la saldatura base -- MIG e ad arco",
            "body": "Saldatore in pensione, 35 anni di esperienza. Se qualcuno vuole imparare la saldatura base (MIG o ad arco), ho l'attrezzatura e lo spazio nel mio laboratorio. Sessioni di 2 ore, gratis per i vicini. Portate solo i guanti da lavoro.",
            "category": "power_tools",
            "neighborhood": "Trapani Sud",
            "content_language": "it",
            "status": "open",
            "replies": [],
        },
        {
            "author_slug": "jakes-electronics",
            "help_type": "need",
            "urgency": "normal",
            "title": "Need help setting up a Raspberry Pi weather station",
            "body": "I bought all the sensors (BME280, rain gauge, anemometer) but I'm stuck on the wiring and the Python code. Anyone in the neighborhood good with electronics and basic coding? Happy to share the data with the community once it's running.",
            "category": "electronics",
            "neighborhood": "Bonagia",
            "content_language": "en",
            "status": "in_progress",
            "replies": [
                {"author_slug": "mikes-garage", "body": "I've done a couple of Pi projects. The BME280 is straightforward -- I2C bus, 4 wires. Want to come by my garage Wednesday evening?"},
                {"author_slug": "jakes-electronics", "body": "That would be amazing! I'll bring the Pi and all the sensors. What time works?"},
            ],
        },
        {
            "author_slug": "rosas-home",
            "help_type": "need",
            "urgency": "normal",
            "title": "Cerco qualcuno che possa aiutarmi a montare una libreria IKEA",
            "body": "Ho comprato una libreria BILLY/OXBERG e non ho gli attrezzi giusti. Mi serve un trapano e qualcuno con un po' di pazienza. Offro caffe e dolci siciliani!",
            "category": "furniture",
            "neighborhood": "Centro",
            "content_language": "it",
            "status": "open",
            "replies": [
                {"author_slug": "mikes-garage", "body": "I have the drill and all the bits. IKEA furniture is my specialty -- I've assembled about 50 of them. Free Saturday afternoon?"},
            ],
        },
        {
            "author_slug": "sallys-kitchen",
            "help_type": "offer",
            "urgency": "low",
            "title": "Offering free cooking equipment for community events",
            "body": "I have 3 large stock pots (20L each), serving trays, and a portable gas burner that I'm happy to lend for neighborhood events, block parties, or fundraisers. Just give me a few days notice so I can clean everything.",
            "category": "kitchen",
            "neighborhood": "Centro Storico",
            "content_language": "en",
            "status": "open",
            "replies": [],
        },
        {
            "author_slug": "lunas-studio",
            "help_type": "need",
            "urgency": "urgent",
            "title": "Urgent: need a sewing machine for a costume repair -- event tomorrow!",
            "body": "My daughter's dance recital costume ripped along the seam. I need a sewing machine for about 30 minutes tonight or early tomorrow morning. It's a simple straight stitch repair. Can anyone help?",
            "category": "art",
            "neighborhood": "Bonagia",
            "content_language": "en",
            "status": "resolved",
            "replies": [
                {"author_slug": "marias-garden", "body": "I have a Singer! Come over anytime tonight. Via Roma 15, ring the top bell."},
                {"author_slug": "lunas-studio", "body": "THANK YOU Maria!! Fixed it in 10 minutes. You saved the show!"},
            ],
        },
    ]

    counts["help_posts"] = 0
    counts["help_replies"] = 0
    for post_data in help_posts:
        author = user_map.get(post_data["author_slug"])
        if not author:
            continue
        post = BHHelpPost(
            author_id=author.id,
            help_type=HelpType(post_data["help_type"]),
            status=HelpStatus(post_data["status"]),
            urgency=HelpUrgency(post_data["urgency"]),
            title=post_data["title"],
            body=post_data.get("body"),
            category=post_data["category"],
            content_language=post_data.get("content_language", "en"),
            neighborhood=post_data.get("neighborhood"),
            reply_count=len(post_data.get("replies", [])),
        )
        db.add(post)
        await db.flush()
        counts["help_posts"] += 1

        for reply_data in post_data.get("replies", []):
            reply_author = user_map.get(reply_data["author_slug"])
            if not reply_author:
                continue
            reply = BHHelpReply(
                post_id=post.id,
                author_id=reply_author.id,
                body=reply_data["body"],
            )
            db.add(reply)
            counts["help_replies"] += 1

    await db.commit()
    logger.info("Seed data loaded: %s", counts)
    return counts


async def seed_new_users(db: AsyncSession) -> dict:
    """Add any users from seed.json that don't already exist (by slug).

    Safe to call on every startup -- only inserts missing users.
    Must run BEFORE seed_new_items() so new item owners exist.
    """
    with open(SEED_FILE) as f:
        data = json.load(f)

    # Get existing user slugs AND emails (protect against partial seeds)
    result = await db.execute(select(BHUser.slug, BHUser.email))
    existing = {(row[0], row[1]) for row in result.all()}
    existing_slugs = {s for s, e in existing}
    existing_emails = {e for s, e in existing}

    if not existing_slugs:
        logger.info("No users in DB -- run full seed first")
        return {"status": "no_users"}

    added = 0
    skipped = 0
    for u in data["users"]:
        if u["slug"] in existing_slugs or u["email"] in existing_emails:
            continue

        user = BHUser(
            keycloak_id=str(uuid.uuid4()),
            email=u["email"],
            display_name=u["display_name"],
            slug=u["slug"],
            date_of_birth=_parse_date(u.get("date_of_birth")),
            mother_name=u.get("mother_name"),
            father_name=u.get("father_name"),
            workshop_name=u.get("workshop_name"),
            workshop_type=_enum_val(WorkshopType, u.get("workshop_type")),
            tagline=u.get("tagline"),
            bio=u.get("bio"),
            telegram_username=u.get("telegram_username"),
            city=u.get("city"),
            country_code=u.get("country_code"),
            latitude=u.get("latitude"),
            longitude=u.get("longitude"),
            offers_delivery=u.get("offers_delivery", False),
            offers_pickup=u.get("offers_pickup", False),
            offers_training=u.get("offers_training", False),
            offers_custom_orders=u.get("offers_custom_orders", False),
            offers_repair=u.get("offers_repair", False),
            account_status=AccountStatus.ACTIVE,
            badge_tier=_enum_val(BadgeTier, u.get("badge_tier", "newcomer")),
        )
        db.add(user)
        await db.flush()

        for lang in u.get("languages", []):
            db.add(BHUserLanguage(
                user_id=user.id,
                language_code=lang["language_code"],
                proficiency=_enum_val(CEFRLevel, lang["proficiency"]),
            ))

        for skill in u.get("skills", []):
            db.add(BHUserSkill(
                user_id=user.id,
                skill_name=skill["skill_name"],
                category=skill["category"],
                self_rating=skill.get("self_rating", 3),
                years_experience=skill.get("years_experience"),
            ))

        for link in u.get("social_links", []):
            db.add(BHUserSocialLink(
                user_id=user.id,
                platform=link["platform"],
                url=link["url"],
                label=link.get("label"),
            ))

        pts = u.get("points")
        if pts:
            db.add(BHUserPoints(
                user_id=user.id,
                total_points=pts.get("total_points", 0),
                rentals_completed=pts.get("rentals_completed", 0),
                reviews_given=pts.get("reviews_given", 0),
                reviews_received=pts.get("reviews_received", 0),
                items_listed=pts.get("items_listed", 0),
                helpful_flags=pts.get("helpful_flags", 0),
            ))

        added += 1
        logger.info("Seeded new user: %s (%s)", u["display_name"], u["slug"])

    if added:
        await db.commit()

    logger.info("Incremental user seed: %d new users added (%d already existed)", added, len(existing_slugs))
    return {"new_users": added, "existing_users": len(existing_slugs)}


async def seed_new_items(db: AsyncSession) -> dict:
    """Add any items from seed.json that don't already exist (by slug).

    Safe to call on every startup -- only inserts missing items.
    Preserves all existing data (bugs, rentals, reviews, favorites).
    """
    with open(SEED_FILE) as f:
        data = json.load(f)

    # Build user lookup by slug
    result = await db.execute(select(BHUser))
    all_users = result.scalars().all()
    user_map = {u.slug: u for u in all_users}

    if not user_map:
        logger.info("No users in DB -- run full seed first")
        return {"status": "no_users"}

    # Get existing item slugs
    result = await db.execute(select(BHItem.slug))
    existing_slugs = {row[0] for row in result.all()}

    added = 0
    for item_data in data["items"]:
        if item_data["slug"] in existing_slugs:
            continue

        owner = user_map.get(item_data["owner_slug"])
        if not owner:
            logger.warning("Owner %s not found, skipping item %s", item_data["owner_slug"], item_data["name"])
            continue

        item = BHItem(
            owner_id=owner.id,
            name=item_data["name"],
            slug=item_data["slug"],
            description=item_data.get("description"),
            story=item_data.get("story"),
            content_language=item_data.get("content_language", "en"),
            item_type=_enum_val(ItemType, item_data["item_type"]),
            category=item_data["category"],
            subcategory=item_data.get("subcategory"),
            condition=_enum_val(ItemCondition, item_data.get("condition")),
            brand=item_data.get("brand"),
            model=item_data.get("model"),
            needs_equipment=item_data.get("needs_equipment"),
            compatible_with=item_data.get("compatible_with"),
            latitude=owner.latitude,
            longitude=owner.longitude,
        )
        db.add(item)
        await db.flush()

        for media in item_data.get("media", []):
            db.add(BHItemMedia(
                item_id=item.id,
                media_type=_enum_val(MediaType, media["media_type"]),
                url=media["url"],
                alt_text=media["alt_text"],
            ))

        for listing in item_data.get("listings", []):
            db.add(BHListing(
                item_id=item.id,
                listing_type=_enum_val(ListingType, listing["listing_type"]),
                status=ListingStatus.ACTIVE,
                price=listing.get("price"),
                price_unit=listing.get("price_unit"),
                currency=listing.get("currency", "EUR"),
                deposit=listing.get("deposit"),
                min_rental_days=listing.get("min_rental_days"),
                max_rental_days=listing.get("max_rental_days"),
                delivery_available=listing.get("delivery_available", False),
                pickup_only=listing.get("pickup_only", True),
                notes=listing.get("notes"),
            ))

        added += 1
        logger.info("Seeded new item: %s", item_data["slug"])

    if added:
        await db.commit()

    logger.info("Incremental seed: %d new items added (%d already existed)", added, len(existing_slugs))
    return {"new_items": added, "existing_items": len(existing_slugs)}
