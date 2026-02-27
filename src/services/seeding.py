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

    counts = {"users": 0, "items": 0, "listings": 0, "teams": 0}
    user_map = {}  # slug -> user object

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

    await db.commit()
    logger.info("Seed data loaded: %s", counts)
    return counts
