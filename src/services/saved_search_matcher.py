"""Saved search matcher -- checks new listings against saved searches.

Called when a new listing is activated. Sends notifications to users
whose saved searches match the new listing's item.
"""

import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.item import BHItem, CATEGORY_GROUPS
from src.models.listing import BHListing
from src.models.notification import BHNotification, NotificationType
from src.models.saved_search import BHSavedSearch

logger = logging.getLogger(__name__)


def _matches(search: BHSavedSearch, item: BHItem, listing: BHListing) -> bool:
    """Check if an item+listing matches a saved search's criteria."""

    # Text query match
    if search.query:
        q = search.query.lower()
        name_match = q in (item.name or "").lower()
        desc_match = q in (item.description or "").lower()
        if not name_match and not desc_match:
            return False

    # Category match
    if search.category and item.category != search.category:
        return False

    # Category group match
    if search.category_group:
        group_cats = CATEGORY_GROUPS.get(search.category_group, [])
        if item.category not in group_cats:
            return False

    # Item type match
    if search.item_type and item.item_type != search.item_type:
        return False

    # Price range match
    if listing.price is not None:
        if search.price_min is not None and listing.price < search.price_min:
            return False
        if search.price_max is not None and listing.price > search.price_max:
            return False

    # Attribute filters match (JSONB)
    if search.attribute_filters and item.attributes:
        for key, value in search.attribute_filters.items():
            if key.endswith("_min"):
                attr_name = key[:-4]
                item_val = item.attributes.get(attr_name)
                if item_val is None or item_val < value:
                    return False
            elif key.endswith("_max"):
                attr_name = key[:-4]
                item_val = item.attributes.get(attr_name)
                if item_val is None or item_val > value:
                    return False
            else:
                if item.attributes.get(key) != value:
                    return False

    # Location radius match (haversine approximation)
    if search.latitude and search.longitude and item.latitude and item.longitude:
        radius = search.radius_km or 25
        # Quick approximation: 1 degree lat ~ 111km
        dlat = abs(item.latitude - search.latitude) * 111
        dlng = abs(item.longitude - search.longitude) * 85  # ~85km at 38° latitude
        dist = (dlat**2 + dlng**2) ** 0.5
        if dist > radius:
            return False

    return True


async def check_saved_searches(db: AsyncSession, item: BHItem, listing: BHListing):
    """Check all active saved searches against a new listing. Send notifications for matches."""

    result = await db.execute(
        select(BHSavedSearch)
        .where(BHSavedSearch.notify_enabled.is_(True))
        .where(BHSavedSearch.deleted_at.is_(None))
        .where(BHSavedSearch.user_id != item.owner_id)  # Don't notify the seller
    )
    searches = result.scalars().all()

    matched = 0
    for search in searches:
        if _matches(search, item, listing):
            # Create notification
            notification = BHNotification(
                user_id=search.user_id,
                notification_type=NotificationType.SAVED_SEARCH_MATCH,
                title=f"New match: {item.name}",
                body=f"A new listing matches your saved search \"{search.name}\"",
                link=f"/items/{item.slug}",
                entity_type="item",
                entity_id=item.id,
            )
            db.add(notification)

            # Increment match count
            search.match_count += 1
            matched += 1

            logger.info(
                "Saved search match: search=%s user=%s item=%s",
                search.id, search.user_id, item.id,
            )

    if matched:
        await db.flush()
        logger.info("Matched %d saved searches for item %s", matched, item.slug)
