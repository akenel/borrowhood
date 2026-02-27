"""Fuzzy search and filtering service.

Uses ILIKE for v1. pg_trgm trigram index for v2.
See RULES.md Section 3 for search rules.
"""

import math
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.item import BHItem, ItemType
from src.models.listing import BHListing, ListingStatus
from src.models.user import BHUser, BHUserLanguage


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance between two points in km (Haversine formula).

    Good enough for neighborhood-scale distances (<50km).
    """
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlng / 2) ** 2
    )
    return R * 2 * math.asin(math.sqrt(a))


async def search_items(
    db: AsyncSession,
    q: Optional[str] = None,
    category: Optional[str] = None,
    item_type: Optional[ItemType] = None,
    language: Optional[str] = None,
    user_lat: Optional[float] = None,
    user_lng: Optional[float] = None,
    radius_km: float = 10.0,
    sort: str = "newest",
    limit: int = 20,
    offset: int = 0,
) -> List[BHItem]:
    """Search items with fuzzy matching, filters, and distance sorting."""

    query = (
        select(BHItem)
        .options(
            selectinload(BHItem.media),
            selectinload(BHItem.owner).selectinload(BHUser.languages),
        )
        .join(BHListing, BHItem.id == BHListing.item_id)
        .where(BHListing.status == ListingStatus.ACTIVE)
        .where(BHItem.deleted_at.is_(None))
    )

    # Fuzzy text search
    if q:
        search_pattern = f"%{q}%"
        query = query.where(
            BHItem.name.ilike(search_pattern)
            | BHItem.description.ilike(search_pattern)
        )

    # Category filter
    if category:
        query = query.where(BHItem.category == category)

    # Item type filter
    if item_type:
        query = query.where(BHItem.item_type == item_type)

    # Language filter: find items whose owner speaks this language
    if language:
        query = query.join(BHUser, BHItem.owner_id == BHUser.id).join(
            BHUserLanguage, BHUser.id == BHUserLanguage.user_id
        ).where(BHUserLanguage.language_code == language)

    # Sorting
    if sort == "newest":
        query = query.order_by(BHItem.created_at.desc())
    elif sort == "oldest":
        query = query.order_by(BHItem.created_at.asc())
    elif sort == "name_asc":
        query = query.order_by(BHItem.name.asc())
    elif sort == "name_desc":
        query = query.order_by(BHItem.name.desc())

    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    items = list(result.scalars().unique().all())

    # Post-query distance filtering and sorting (Haversine in Python for v1)
    if user_lat is not None and user_lng is not None:
        items_with_distance = []
        for item in items:
            item_lat = item.latitude or item.owner.latitude
            item_lng = item.longitude or item.owner.longitude
            if item_lat and item_lng:
                dist = haversine_km(user_lat, user_lng, item_lat, item_lng)
                if dist <= radius_km:
                    items_with_distance.append((item, dist))
            else:
                items_with_distance.append((item, float("inf")))

        if sort == "closest":
            items_with_distance.sort(key=lambda x: x[1])

        items = [item for item, _ in items_with_distance]

    return items
