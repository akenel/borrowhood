"""Seed data loader.

Loads seed_data/seed.json into the database.
Creates users, items, listings, teams, and points.
Run once on first startup or via CLI.
"""

import json
import logging
import uuid
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
from src.models.workshop import BHWorkshopMember, TeamRole

logger = logging.getLogger(__name__)

SEED_FILE = Path(__file__).parent.parent.parent / "seed_data" / "seed.json"


def _enum_val(enum_class, value):
    """Safely get enum value."""
    if value is None:
        return None
    return enum_class(value)


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

    await db.commit()
    logger.info("Seed data loaded: %s", counts)
    return counts
