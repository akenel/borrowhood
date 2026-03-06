"""HTML page routes: home, browse, item detail, workshop profile.

All pages extend base.html. All use Jinja2 server-side rendering.
Every response includes t() translator and current lang in context.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.config import settings
from src.database import get_db
from src.dependencies import get_current_user_token, get_user
from src.i18n import detect_language, get_translator, SUPPORTED_LANGUAGES
from src.models.item import BHItem, CATEGORY_GROUPS
from src.models.listing import BHListing, ListingStatus
from src.models.rental import BHRental
from src.models.review import BHReview
from src.models.badge import BADGE_INFO
from src.models.user import BadgeTier, BHUser, WorkshopType

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="src/templates")

# Make datetime.now() available in templates for seasonal tag logic
from datetime import datetime
templates.env.globals["now"] = datetime.now

# Location privacy: 500m blur for public display
from src.services.location_privacy import blur_coordinates
templates.env.globals["blur"] = blur_coordinates

# Language code -> flag emoji mapping (available in all templates as lang_flags)
templates.env.globals["lang_flags"] = {
    "de": "\U0001f1e9\U0001f1ea", "en": "\U0001f1ec\U0001f1e7",
    "es": "\U0001f1ea\U0001f1f8", "fr": "\U0001f1eb\U0001f1f7",
    "it": "\U0001f1ee\U0001f1f9", "mt": "\U0001f1f2\U0001f1f9",
    "zh": "\U0001f1e8\U0001f1f3", "pt": "\U0001f1f5\U0001f1f9",
    "ja": "\U0001f1ef\U0001f1f5", "ar": "\U0001f1e6\U0001f1ea",
    "ru": "\U0001f1f7\U0001f1fa", "nl": "\U0001f1f3\U0001f1f1",
    "tr": "\U0001f1f9\U0001f1f7", "ko": "\U0001f1f0\U0001f1f7",
    "pl": "\U0001f1f5\U0001f1f1", "sv": "\U0001f1f8\U0001f1ea",
    "da": "\U0001f1e9\U0001f1f0", "fi": "\U0001f1eb\U0001f1ee",
    "no": "\U0001f1f3\U0001f1f4", "el": "\U0001f1ec\U0001f1f7",
    "ro": "\U0001f1f7\U0001f1f4", "hr": "\U0001f1ed\U0001f1f7",
    "hu": "\U0001f1ed\U0001f1fa", "cs": "\U0001f1e8\U0001f1ff",
    "uk": "\U0001f1fa\U0001f1e6", "hi": "\U0001f1ee\U0001f1f3",
}


def _ctx(request: Request, token: Optional[dict] = None, **kwargs) -> dict:
    """Build template context with i18n, lang, and common vars.

    Every page gets: request, user, t(), lang, supported_languages, _set_lang_cookie.
    Language detection: ?lang= query param > bh_lang cookie > Accept-Language > default.
    """
    query_lang = request.query_params.get("lang")
    cookie_lang = request.cookies.get("bh_lang")
    accept_lang = request.headers.get("accept-language")

    lang = detect_language(query_lang, cookie_lang, accept_lang)
    t = get_translator(lang)

    # Flag for routes to set cookie on the actual response
    set_lang_cookie = query_lang and query_lang != cookie_lang

    ctx = {
        "request": request,
        "user": token,
        "t": t,
        "lang": lang,
        "supported_languages": SUPPORTED_LANGUAGES,
        "debug": settings.debug,
        "_set_lang_cookie": set_lang_cookie,
    }
    ctx.update(kwargs)
    return ctx


def _render(template_name: str, ctx: dict, status_code: int = 200):
    """Render template and set lang cookie if needed."""
    set_cookie = ctx.pop("_set_lang_cookie", False)
    lang = ctx.get("lang", "en")
    response = templates.TemplateResponse(template_name, ctx, status_code=status_code)
    if set_cookie:
        response.set_cookie("bh_lang", lang, max_age=365 * 24 * 3600, samesite="lax")
    return response


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

    ctx = _ctx(request, token,
        listing_count=listing_count or 0,
        user_count=user_count or 0,
        category_count=category_count or 0,
        review_count=review_count or 0,
        featured_items=featured_items,
    )
    return _render("pages/home.html", ctx)


@router.get("/browse", response_class=HTMLResponse)
async def browse(request: Request,
                 q: Optional[str] = None,
                 category: Optional[str] = None,
                 item_type: Optional[str] = None,
                 sort: str = "newest",
                 limit: int = 12,
                 offset: int = 0,
                 db: AsyncSession = Depends(get_db),
                 token: Optional[dict] = Depends(get_current_user_token)):
    """Browse and search items with filters."""
    # EXISTS avoids JOIN duplicates (items with multiple active listings)
    has_active_listing = (
        select(BHListing.id)
        .where(BHListing.item_id == BHItem.id)
        .where(BHListing.status == ListingStatus.ACTIVE)
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
            BHItem.name.ilike(search_term) | BHItem.description.ilike(search_term)
        )
    if category:
        query = query.where(BHItem.category == category)
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
            BHItem.name.ilike(f"%{q}%") | BHItem.description.ilike(f"%{q}%")
        )
    if category:
        count_q = count_q.where(BHItem.category == category)
    if item_type:
        count_q = count_q.where(BHItem.item_type == item_type)
    total_count = await db.scalar(count_q) or 0

    # Clamp limit to valid range
    limit = max(12, min(limit, 48))
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    items = result.scalars().unique().all()

    ctx = _ctx(request, token,
        items=items,
        total_count=total_count,
        category_groups=CATEGORY_GROUPS,
        q=q or "",
        selected_category=category,
        selected_type=item_type,
        selected_sort=sort,
        selected_limit=limit,
        selected_offset=offset,
    )
    return _render("pages/browse.html", ctx)


@router.get("/items/{slug}", response_class=HTMLResponse)
async def item_detail(slug: str, request: Request,
                      db: AsyncSession = Depends(get_db),
                      token: Optional[dict] = Depends(get_current_user_token)):
    """Item detail page with listings, owner info, and location map."""
    result = await db.execute(
        select(BHItem)
        .options(
            selectinload(BHItem.media),
            selectinload(BHItem.owner).selectinload(BHUser.languages),
            selectinload(BHItem.listings),
        )
        .where(BHItem.slug == slug)
        .where(BHItem.deleted_at.is_(None))
    )
    item = result.scalars().first()

    if not item:
        ctx = _ctx(request, token)
        return _render("errors/404.html", ctx, status_code=404)

    # Resolve viewer's badge tier for progressive disclosure
    viewer_tier = "anonymous"
    if token:
        from src.dependencies import get_user as _get_user
        try:
            viewer = await _get_user(db, token)
            viewer_tier = viewer.badge_tier.value
        except Exception:
            pass

    ctx = _ctx(request, token,
        item=item,
        viewer_tier=viewer_tier,
        og_title=f"{item.name} - BorrowHood",
        og_description=item.description[:160] if item.description else "Available on BorrowHood",
        og_image=item.media[0].url if item.media else None,
    )
    return _render("pages/item_detail.html", ctx)


@router.get("/workshop/{slug}", response_class=HTMLResponse)
async def workshop_profile(slug: str, request: Request,
                           db: AsyncSession = Depends(get_db),
                           token: Optional[dict] = Depends(get_current_user_token)):
    """Workshop profile page with owner info, items, and reviews."""
    result = await db.execute(
        select(BHUser)
        .options(
            selectinload(BHUser.languages),
            selectinload(BHUser.skills),
            selectinload(BHUser.social_links),
            selectinload(BHUser.items).selectinload(BHItem.media),
            selectinload(BHUser.points),
        )
        .where(BHUser.slug == slug)
        .where(BHUser.deleted_at.is_(None))
    )
    workshop_owner = result.scalars().first()

    if not workshop_owner:
        ctx = _ctx(request, token)
        return _render("errors/404.html", ctx, status_code=404)

    # Fetch badges separately (backref not available for eager loading)
    from src.models.badge import BHBadge
    badge_result = await db.execute(
        select(BHBadge).where(BHBadge.user_id == workshop_owner.id)
    )
    user_badges = badge_result.scalars().all()

    # Resolve viewer's badge tier for progressive disclosure
    viewer_tier = "anonymous"
    if token:
        from src.dependencies import get_user as _get_user
        try:
            viewer = await _get_user(db, token)
            viewer_tier = viewer.badge_tier.value
        except Exception:
            pass

    ctx = _ctx(request, token,
        workshop=workshop_owner,
        workshop_badges=user_badges,
        badge_info=BADGE_INFO,
        viewer_tier=viewer_tier,
        og_title=f"{workshop_owner.workshop_name or workshop_owner.display_name} - BorrowHood",
        og_description=workshop_owner.tagline or "Workshop on BorrowHood",
    )
    return _render("pages/workshop.html", ctx)


@router.get("/workshop/{slug}/export", response_class=HTMLResponse)
async def export_workshop(slug: str, request: Request,
                          db: AsyncSession = Depends(get_db),
                          token: Optional[dict] = Depends(get_current_user_token)):
    """Export workshop as standalone HTML page (one-click download)."""
    from datetime import date
    result = await db.execute(
        select(BHUser)
        .options(
            selectinload(BHUser.languages),
            selectinload(BHUser.skills),
            selectinload(BHUser.social_links),
            selectinload(BHUser.items).selectinload(BHItem.media),
            selectinload(BHUser.items).selectinload(BHItem.listings),
        )
        .where(BHUser.slug == slug)
        .where(BHUser.deleted_at.is_(None))
    )
    workshop_owner = result.scalars().first()

    if not workshop_owner:
        return Response("Workshop not found", status_code=404)

    lang = detect_language(request)
    items = [i for i in workshop_owner.items if not i.deleted_at]
    html = templates.TemplateResponse("export/workshop.html", {
        "request": request,
        "workshop": workshop_owner,
        "items": items,
        "lang": lang,
        "export_date": date.today().isoformat(),
    })
    filename = f"{slug}-borrowhood-export.html"
    html.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    return html


@router.get("/list", response_class=HTMLResponse)
async def list_item_page(request: Request,
                         token: Optional[dict] = Depends(get_current_user_token)):
    """Form to list a new item. Requires authentication (enforced client-side)."""
    ctx = _ctx(request, token, category_groups=CATEGORY_GROUPS)
    return _render("pages/list_item.html", ctx)


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request,
                    db: AsyncSession = Depends(get_db),
                    token: Optional[dict] = Depends(get_current_user_token)):
    """User dashboard with items, rentals, and incoming requests."""
    items = []
    item_count = 0
    renter_rentals = []
    owner_rentals = []

    if token:
        try:
            db_user = await get_user(db, token)
        except Exception:
            db_user = None

        if db_user:
            # User's items (capped at 12 for initial load)
            item_count = await db.scalar(
                select(func.count(BHItem.id))
                .where(BHItem.owner_id == db_user.id)
                .where(BHItem.deleted_at.is_(None))
            ) or 0

            items_result = await db.execute(
                select(BHItem)
                .options(selectinload(BHItem.media), selectinload(BHItem.listings))
                .where(BHItem.owner_id == db_user.id)
                .where(BHItem.deleted_at.is_(None))
                .order_by(BHItem.created_at.desc())
                .limit(12)
            )
            items = items_result.scalars().unique().all()

            # Rentals as renter
            renter_result = await db.execute(
                select(BHRental)
                .options(
                    selectinload(BHRental.listing).selectinload(BHListing.item)
                )
                .where(BHRental.renter_id == db_user.id)
                .order_by(BHRental.created_at.desc())
                .limit(20)
            )
            renter_rentals = renter_result.scalars().unique().all()

            # Rentals on user's items (incoming requests)
            owner_result = await db.execute(
                select(BHRental)
                .options(
                    selectinload(BHRental.listing).selectinload(BHListing.item)
                )
                .join(BHListing)
                .join(BHItem, BHListing.item_id == BHItem.id)
                .where(BHItem.owner_id == db_user.id)
                .order_by(BHRental.created_at.desc())
                .limit(20)
            )
            owner_rentals = owner_result.scalars().unique().all()

    ctx = _ctx(request, token,
        items=items,
        item_total=item_count,
        renter_rentals=renter_rentals,
        owner_rentals=owner_rentals,
    )
    return _render("pages/dashboard.html", ctx)


@router.get("/onboarding", response_class=HTMLResponse)
async def onboarding_page(request: Request,
                          token: Optional[dict] = Depends(get_current_user_token)):
    """Onboarding wizard for new users."""
    ctx = _ctx(request, token)
    return _render("pages/onboarding.html", ctx)


@router.get("/profile", response_class=HTMLResponse)
async def profile(request: Request,
                  db: AsyncSession = Depends(get_db),
                  token: Optional[dict] = Depends(get_current_user_token)):
    """User profile page with stats, badges, languages, skills."""
    profile_user = None
    languages = []
    skills = []
    stats = {"items": 0, "rentals": 0, "reviews": 0, "points": 0}

    if token:
        try:
            linked_user = await get_user(db, token)
            # Re-fetch with eager-loaded relations
            result = await db.execute(
                select(BHUser)
                .options(
                    selectinload(BHUser.languages),
                    selectinload(BHUser.skills),
                    selectinload(BHUser.points),
                )
                .where(BHUser.id == linked_user.id)
            )
            profile_user = result.scalars().first()
        except Exception:
            profile_user = None

        if profile_user:
            languages = profile_user.languages
            skills = profile_user.skills

            # Count stats
            item_count = await db.scalar(
                select(func.count(BHItem.id))
                .where(BHItem.owner_id == profile_user.id)
                .where(BHItem.deleted_at.is_(None))
            ) or 0

            rental_count = await db.scalar(
                select(func.count(BHRental.id))
                .where(BHRental.renter_id == profile_user.id)
            ) or 0

            from src.models.review import BHReview
            review_count = await db.scalar(
                select(func.count(BHReview.id))
                .where(BHReview.reviewer_id == profile_user.id)
            ) or 0

            pts = profile_user.points
            stats = {
                "items": item_count,
                "rentals": rental_count,
                "reviews": review_count,
                "points": pts.total_points if pts else 0,
            }

    ctx = _ctx(request, token,
        profile_user=profile_user,
        languages=languages,
        skills=skills,
        stats=stats,
    )
    return _render("pages/profile.html", ctx)


@router.get("/helpboard", response_class=HTMLResponse)
async def helpboard_page(request: Request,
                         token: Optional[dict] = Depends(get_current_user_token)):
    """Community Help Board page."""
    ctx = _ctx(request, token, category_groups=CATEGORY_GROUPS)
    return _render("pages/helpboard.html", ctx)


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
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    radius: float = 25.0,
    sort: str = "newest",
    limit: int = 12,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    token: Optional[dict] = Depends(get_current_user_token),
):
    """Members directory with search and filters."""
    from sqlalchemy import case

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


@router.get("/demo-login", response_class=HTMLResponse)
async def demo_login_page(
    request: Request,
    token: Optional[dict] = Depends(get_current_user_token),
):
    """One-click demo login page. Debug mode only."""
    if not settings.debug:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Not found")

    _av = "/static/images/avatars"
    demo_users = [
        {"username": "angel", "display_name": "Angel", "workshop": "The Black Wolf Workshop", "roles": "admin, operator, moderator, lender", "badge": "legend", "color": "amber", "avatar": f"{_av}/angel.jpg"},
        {"username": "nino", "display_name": "Nino Cassisa", "workshop": "Camper & Tour Trapani", "roles": "operator, moderator, lender", "badge": "pillar", "color": "purple", "avatar": f"{_av}/nino.svg"},
        {"username": "leonardo", "display_name": "Leonardo da Vinci", "workshop": "Bottega di Leonardo", "roles": "moderator, lender", "badge": "legend", "color": "amber", "avatar": f"{_av}/leonardo.svg"},
        {"username": "sally", "display_name": "Sally Baker", "workshop": "Sally's Kitchen", "roles": "lender", "badge": "trusted", "color": "emerald", "avatar": f"{_av}/sally.svg"},
        {"username": "mike", "display_name": "Mike Kenel", "workshop": "Mike's Tool Shed", "roles": "lender", "badge": "pillar", "color": "purple", "avatar": f"{_av}/mike.svg"},
        {"username": "marco", "display_name": "Marco Moretti", "workshop": "Bottega del Legno", "roles": "lender", "badge": "active", "color": "blue", "avatar": f"{_av}/marco.svg"},
        {"username": "pietro", "display_name": "Pietro Ferretti", "workshop": "SkyView Sicilia", "roles": "lender", "badge": "active", "color": "blue", "avatar": f"{_av}/pietro.svg"},
        {"username": "jake", "display_name": "Jake Chen", "workshop": "Jake's Maker Space", "roles": "lender", "badge": "active", "color": "blue", "avatar": f"{_av}/jake.svg"},
        {"username": "george", "display_name": "George Clooney", "workshop": "Villa Oleandra", "roles": "lender", "badge": "pillar", "color": "purple", "avatar": f"{_av}/george.svg"},
        {"username": "john", "display_name": "John Abela", "workshop": "John's Cleaning Corner", "roles": "lender", "badge": "newcomer", "color": "gray", "avatar": f"{_av}/john.svg"},
        {"username": "maria", "display_name": "Maria Ferretti", "workshop": None, "roles": "lender", "badge": "newcomer", "color": "gray", "avatar": f"{_av}/maria.svg"},
        {"username": "sofiaferretti", "display_name": "Sofia Ferretti", "workshop": None, "roles": "member", "badge": "newcomer", "color": "gray", "avatar": f"{_av}/sofia.svg"},
        {"username": "rosa", "display_name": "Rosa Ferretti", "workshop": None, "roles": "member only", "badge": "newcomer", "color": "gray", "avatar": f"{_av}/rosa.svg"},
        {"username": "anne", "display_name": "Anne Muthoni", "workshop": None, "roles": "qa-tester", "badge": "active", "color": "blue", "avatar": f"{_av}/anne.svg"},
    ]

    ctx = _ctx(request, token, demo_users=demo_users)
    return _render("pages/demo_login.html", ctx)


@router.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request,
                    token: Optional[dict] = Depends(get_current_user_token)):
    """AI Concierge chat page. Backend: POST /api/v1/ai/concierge."""
    ctx = _ctx(request, token)
    return _render("pages/chat.html", ctx)


@router.get("/terms", response_class=HTMLResponse)
async def terms(request: Request,
                token: Optional[dict] = Depends(get_current_user_token)):
    """Terms of Service and Community Code of Conduct."""
    ctx = _ctx(request, token)
    return _render("pages/terms.html", ctx)
