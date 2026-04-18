"""Discovery pages: home, browse, members directory, leaderboard."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.config import settings
from src.database import get_db
from src.dependencies import get_current_user_token, get_user
from src.i18n import detect_language, get_translator, SUPPORTED_LANGUAGES
from src.models.item import ATTRIBUTE_SCHEMAS, BHItem, CATEGORY_GROUPS
from src.models.listing import BHListing, ListingStatus, ListingType
from src.models.rental import BHRental, RentalStatus
from src.models.review import BHReview
from src.models.badge import BADGE_INFO
from src.models.user import BadgeTier, BHUser, WorkshopType

from ._helpers import (
    templates, _ctx, _render, _abs_url, _og_workshop_desc,
    _og_item_desc, _last_seen,
)

router = APIRouter(tags=["pages"])

@router.get("/", response_class=HTMLResponse)
async def home(request: Request,
               db: AsyncSession = Depends(get_db),
               token: Optional[dict] = Depends(get_current_user_token)):
    """Landing page with featured items and stats."""
    listing_count = await db.scalar(
        select(func.count(BHListing.id)).where(BHListing.status == ListingStatus.ACTIVE)
    )
    user_count = await db.scalar(select(func.count(BHUser.id)))
    category_count = await db.scalar(
        select(func.count(func.distinct(BHItem.category)))
    )
    review_count = await db.scalar(select(func.count(BHReview.id)))

    result = await db.execute(
        select(BHItem)
        .options(
            selectinload(BHItem.media),
            selectinload(BHItem.owner),
            selectinload(BHItem.listings),
        )
        .join(BHListing, BHItem.id == BHListing.item_id)
        .where(BHListing.status == ListingStatus.ACTIVE)
        .order_by(BHItem.created_at.desc())
        .limit(6)
    )
    featured_items = result.scalars().unique().all()

    # For logged-in users: compute "next step" for the quick-start strip
    home_user = None
    user_item_count = 0
    user_skill_count = 0
    if token:
        try:
            home_user = await get_user(db, token)
            user_item_count = await db.scalar(
                select(func.count(BHItem.id))
                .where(BHItem.owner_id == home_user.id)
                .where(BHItem.deleted_at.is_(None))
            ) or 0
            from src.models.user import BHUserSkill
            user_skill_count = await db.scalar(
                select(func.count(BHUserSkill.id))
                .where(BHUserSkill.user_id == home_user.id)
                .where(BHUserSkill.deleted_at.is_(None))
            ) or 0
        except Exception:
            home_user = None

    from src.services.activity_feed import get_activity_feed
    activity = await get_activity_feed(db, limit=8)

    ctx = _ctx(request, token,
        listing_count=listing_count or 0,
        user_count=user_count or 0,
        category_count=category_count or 0,
        review_count=review_count or 0,
        featured_items=featured_items,
        home_user=home_user,
        user_item_count=user_item_count,
        user_skill_count=user_skill_count,
        activity=activity,
    )
    return _render("pages/home.html", ctx)



@router.get("/browse", response_class=HTMLResponse)
async def browse(request: Request,
                 q: Optional[str] = None,
                 category: Optional[str] = None,
                 category_group: Optional[str] = None,
                 item_type: Optional[str] = None,
                 listing_type: Optional[str] = None,
                 price_max: Optional[str] = None,  # str -- empty values from live form
                 free_only: Optional[str] = None,  # str -- checkbox sends "true" or absent
                 sort: str = "newest",
                 limit: int = 12,
                 offset: int = 0,
                 db: AsyncSession = Depends(get_db),
                 token: Optional[dict] = Depends(get_current_user_token)):
    # Coerce empty-string query params (from live-submit form) to None/False
    price_max_val: Optional[float] = None
    if price_max:
        try:
            price_max_val = float(price_max)
        except (TypeError, ValueError):
            price_max_val = None
    free_only_val: bool = bool(free_only and free_only.lower() in ("true", "1", "on"))
    # Empty-string coercion for other text params
    q = q or None
    category = category or None
    category_group = category_group or None
    item_type = item_type or None
    listing_type = listing_type or None
    """Browse and search items with filters."""
    # EXISTS avoids JOIN duplicates (items with multiple active listings)
    has_active_listing_clauses = [
        BHListing.item_id == BHItem.id,
        BHListing.status == ListingStatus.ACTIVE,
    ]
    if listing_type:
        has_active_listing_clauses.append(BHListing.listing_type == listing_type)
    if free_only_val:
        # Free = either no price, price=0, or listing_type is giveaway/offer
        from sqlalchemy import or_ as _or
        has_active_listing_clauses.append(
            _or(BHListing.price.is_(None), BHListing.price == 0,
                BHListing.listing_type.in_([ListingType.GIVEAWAY, ListingType.OFFER]))
        )
    elif price_max_val is not None:
        has_active_listing_clauses.append(BHListing.price <= price_max_val)
    has_active_listing = (
        select(BHListing.id)
        .where(*has_active_listing_clauses)
        .exists()
    )
    query = (
        select(BHItem)
        .options(
            selectinload(BHItem.media),
            selectinload(BHItem.owner).selectinload(BHUser.languages),
            selectinload(BHItem.listings),
        )
        .where(has_active_listing)
        .where(BHItem.deleted_at.is_(None))
    )

    if q:
        search_term = f"%{q}%"
        query = query.where(
            BHItem.name.ilike(search_term)
            | BHItem.description.ilike(search_term)
            | (func.similarity(BHItem.name, q) > 0.2)
            | (func.similarity(BHItem.description, q) > 0.15)
        )
    if category:
        query = query.where(BHItem.category == category)
    elif category_group and category_group in CATEGORY_GROUPS:
        cats = CATEGORY_GROUPS[category_group]
        query = query.where(BHItem.category.in_(cats))
    if item_type:
        query = query.where(BHItem.item_type == item_type)

    if sort == "newest":
        query = query.order_by(BHItem.created_at.desc())
    elif sort == "oldest":
        query = query.order_by(BHItem.created_at.asc())
    elif sort == "name_asc":
        query = query.order_by(BHItem.name.asc())

    # Total count with same filters (before limit)
    count_q = (
        select(func.count(BHItem.id))
        .where(has_active_listing)
        .where(BHItem.deleted_at.is_(None))
    )
    if q:
        count_q = count_q.where(
            BHItem.name.ilike(f"%{q}%")
            | BHItem.description.ilike(f"%{q}%")
            | (func.similarity(BHItem.name, q) > 0.2)
            | (func.similarity(BHItem.description, q) > 0.15)
        )
    if category:
        count_q = count_q.where(BHItem.category == category)
    elif category_group and category_group in CATEGORY_GROUPS:
        count_q = count_q.where(BHItem.category.in_(CATEGORY_GROUPS[category_group]))
    if item_type:
        count_q = count_q.where(BHItem.item_type == item_type)
    total_count = await db.scalar(count_q) or 0

    # Clamp limit to valid range
    limit = max(12, min(limit, 48))
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    items = result.scalars().unique().all()

    # Determine which attribute schema to show for the active group
    active_attr_schema = {}
    if category_group and category_group in ATTRIBUTE_SCHEMAS:
        active_attr_schema = ATTRIBUTE_SCHEMAS[category_group]
    elif category:
        for gname, gcats in CATEGORY_GROUPS.items():
            if category in gcats and gname in ATTRIBUTE_SCHEMAS:
                active_attr_schema = ATTRIBUTE_SCHEMAS[gname]
                break

    ctx = _ctx(request, token,
        items=items,
        total_count=total_count,
        category_groups=CATEGORY_GROUPS,
        q=q or "",
        selected_category=category,
        selected_category_group=category_group,
        selected_type=item_type,
        selected_listing_type=listing_type,
        selected_price_max=price_max_val,
        selected_free_only=free_only_val,
        selected_sort=sort,
        selected_limit=limit,
        selected_offset=offset,
        attribute_schema=active_attr_schema,
    )
    return _render("pages/browse.html", ctx)



@router.get("/leaderboard", response_class=HTMLResponse)
async def leaderboard_page(request: Request,
                           token: Optional[dict] = Depends(get_current_user_token)):
    """Event leaderboard: rankings, streaks, achievements."""
    from src.models.achievement import ACHIEVEMENTS
    ctx = _ctx(request, token, achievements=ACHIEVEMENTS)
    return _render("pages/leaderboard.html", ctx)



@router.get("/members", response_class=HTMLResponse)
async def members_directory(
    request: Request,
    q: Optional[str] = None,
    city: Optional[str] = None,
    badge_tier: Optional[str] = None,
    workshop_type: Optional[str] = None,
    service: Optional[str] = None,
    skill: Optional[str] = None,
    language: Optional[str] = None,
    lat: Optional[str] = None,
    lng: Optional[str] = None,
    radius: Optional[str] = None,
    sort: str = "newest",
    limit: int = 12,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    token: Optional[dict] = Depends(get_current_user_token),
):
    """Members directory with search and filters."""
    from sqlalchemy import case

    # Parse lat/lng/radius from strings (HTML forms send empty strings)
    _lat: Optional[float] = None
    _lng: Optional[float] = None
    _radius: float = 25.0
    try:
        if lat:
            _lat = float(lat)
    except (ValueError, TypeError):
        pass
    try:
        if lng:
            _lng = float(lng)
    except (ValueError, TypeError):
        pass
    try:
        if radius:
            _radius = float(radius)
    except (ValueError, TypeError):
        pass
    lat = _lat  # type: ignore[assignment]
    lng = _lng  # type: ignore[assignment]
    radius = _radius  # type: ignore[assignment]

    limit = max(12, min(limit, 48))

    _badge_sort = case(
        (BHUser.badge_tier == BadgeTier.LEGEND, 0),
        (BHUser.badge_tier == BadgeTier.PILLAR, 1),
        (BHUser.badge_tier == BadgeTier.TRUSTED, 2),
        (BHUser.badge_tier == BadgeTier.ACTIVE, 3),
        else_=4,
    )

    from src.models.user import BHUserLanguage, BHUserSkill

    base_where = [BHUser.deleted_at.is_(None)]
    need_skill_join = False
    need_lang_join = False

    if q:
        search_term = f"%{q}%"
        base_where.append(
            BHUser.display_name.ilike(search_term)
            | BHUser.workshop_name.ilike(search_term)
            | BHUser.tagline.ilike(search_term)
        )
    if city:
        base_where.append(BHUser.city.ilike(f"%{city}%"))
    if badge_tier:
        base_where.append(BHUser.badge_tier == badge_tier)
    if workshop_type:
        base_where.append(BHUser.workshop_type == workshop_type)
    # Service offer filter (from Find a Maker links)
    service_filter_map = {
        "repair": BHUser.offers_repair,
        "custom_orders": BHUser.offers_custom_orders,
        "training": BHUser.offers_training,
        "delivery": BHUser.offers_delivery,
        "pickup": BHUser.offers_pickup,
    }
    if service and service in service_filter_map:
        base_where.append(service_filter_map[service].is_(True))
    # Skill filter
    if skill:
        need_skill_join = True
        base_where.append(BHUserSkill.skill_name.ilike(f"%{skill}%"))
    # Language filter
    if language:
        need_lang_join = True
        base_where.append(BHUserLanguage.language_code == language)

    # Build count query with joins if needed
    count_q = select(func.count(func.distinct(BHUser.id)))
    if need_skill_join:
        count_q = count_q.join(BHUserSkill, BHUser.id == BHUserSkill.user_id)
    if need_lang_join:
        count_q = count_q.join(BHUserLanguage, BHUser.id == BHUserLanguage.user_id)
    count_q = count_q.where(*base_where)
    total_count = await db.scalar(count_q) or 0

    query = (
        select(BHUser)
        .options(selectinload(BHUser.languages), selectinload(BHUser.skills))
    )
    if need_skill_join:
        query = query.join(BHUserSkill, BHUser.id == BHUserSkill.user_id)
    if need_lang_join:
        query = query.join(BHUserLanguage, BHUser.id == BHUserLanguage.user_id)
    query = query.where(*base_where)

    if sort == "newest":
        query = query.order_by(BHUser.created_at.desc())
    elif sort == "name_asc":
        query = query.order_by(BHUser.display_name.asc())
    elif sort == "badge_tier":
        query = query.order_by(_badge_sort, BHUser.display_name.asc())
    elif sort == "trust":
        query = query.order_by(BHUser.trust_score.desc().nullslast(), BHUser.display_name.asc())

    # Distance filtering needs post-query (haversine in Python for v1)
    if lat is not None and lng is not None:
        # Fetch more for distance filtering, then trim
        query = query.limit(limit * 4)
    else:
        query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    members = list(result.scalars().unique().all())

    # Post-query distance filter
    if lat is not None and lng is not None:
        from src.services.search import haversine_km
        members_with_dist = []
        for m in members:
            if m.latitude and m.longitude:
                dist = haversine_km(lat, lng, m.latitude, m.longitude,
                                    alt2=m.altitude or 0.0)
                if dist <= radius:
                    members_with_dist.append((m, dist))
            else:
                members_with_dist.append((m, float("inf")))
        if sort == "closest":
            members_with_dist.sort(key=lambda x: x[1])
        total_count = len(members_with_dist)
        members = [m for m, _ in members_with_dist[offset:offset + limit]]

    # Distinct cities for filter dropdown
    cities_result = await db.execute(
        select(func.distinct(BHUser.city))
        .where(BHUser.deleted_at.is_(None))
        .where(BHUser.city.isnot(None))
        .order_by(BHUser.city)
    )
    cities = [r[0] for r in cities_result.all()]

    ctx = _ctx(request, token,
        members=members,
        total_count=total_count,
        cities=cities,
        badge_tiers=[t.value for t in BadgeTier],
        workshop_types=[t.value for t in WorkshopType],
        q=q or "",
        selected_city=city,
        selected_badge=badge_tier,
        selected_workshop_type=workshop_type,
        selected_service=service,
        selected_skill=skill or "",
        selected_language=language or "",
        selected_sort=sort,
        selected_limit=limit,
        selected_offset=offset,
        radius=radius,
    )
    return _render("pages/members.html", ctx)



