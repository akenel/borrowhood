"""HTML page routes: home, browse, item detail, workshop profile.

All pages extend base.html. All use Jinja2 server-side rendering.
Every response includes t() translator and current lang in context.
"""

from typing import Optional

from markupsafe import Markup
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
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

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="src/templates")

# Make datetime.now() available in templates for seasonal tag logic
from datetime import datetime, timezone
templates.env.globals["now"] = datetime.now
templates.env.globals["now_utc"] = lambda: datetime.now(timezone.utc)


def _last_seen(dt, lang="en"):
    """Human-readable 'last seen' from a datetime."""
    if not dt:
        return None
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        from datetime import timezone as tz
        dt = dt.replace(tzinfo=tz.utc)
    delta = now - dt
    minutes = int(delta.total_seconds() / 60)
    it = (lang == "it")
    if minutes < 5:
        return "online ora" if it else "online now"
    if minutes < 60:
        return f"visto {minutes}m fa" if it else f"seen {minutes}m ago"
    hours = minutes // 60
    if hours < 24:
        return f"visto {hours}h fa" if it else f"seen {hours}h ago"
    days = delta.days
    if days == 1:
        return "visto ieri" if it else "seen yesterday"
    if days < 30:
        return f"visto {days}g fa" if it else f"seen {days}d ago"
    months = days // 30
    if months < 12:
        return f"visto {months}m fa" if it else f"seen {months}mo ago"
    years = days // 365
    return f"visto {years}a fa" if it else f"seen {years}y ago"


templates.env.filters["last_seen"] = _last_seen

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


def _abs_url(path: Optional[str]) -> Optional[str]:
    """Convert a relative path to absolute URL for OG tags."""
    if not path:
        return None
    if path.startswith("http"):
        return path
    return f"{settings.app_url}{path}"


def _og_workshop_desc(user) -> str:
    """Build a rich OG description for workshop pages."""
    parts = []
    if user.tagline:
        parts.append(user.tagline)
    if user.city:
        loc = user.city
        if user.state_region:
            loc += f", {user.state_region}"
        if user.country_code:
            loc += f" {user.country_code}"
        parts.append(loc)
    item_count = len([i for i in user.items if not i.deleted_at]) if user.items else 0
    if item_count:
        parts.append(f"{item_count} items listed")
    skill_names = [s.skill_name for s in (user.skills or [])[:3]]
    if skill_names:
        parts.append(" | ".join(skill_names))
    if not parts:
        parts.append(f"{user.display_name} on La Piazza")
    return " — ".join(parts)


def _og_item_desc(item, listing=None) -> str:
    """Build a rich OG description for item pages.

    Events:  Apr 22, 5:00 PM · D50 Palazzo, Alcamo · Free · by Nic · Learn basic positions...
    Items:   EUR 120.00 · Training · by Corrado Sassi, Trapani · Learn to sail...
    Date/venue/price come FIRST -- that's what converts clicks.
    """
    parts = []
    is_event = listing and hasattr(listing, 'listing_type') and getattr(listing.listing_type, 'value', '') == 'event'

    if is_event and listing.event_start:
        from datetime import timezone, timedelta
        cest = timezone(timedelta(hours=2))
        start_local = listing.event_start.astimezone(cest)
        parts.append(start_local.strftime('%b %d, %I:%M %p').replace(' 0', ' '))
        if listing.event_end:
            end_local = listing.event_end.astimezone(cest)
            parts[-1] += end_local.strftime(' - %I:%M %p').replace(' 0', ' ')

    if is_event and listing.event_venue:
        venue = listing.event_venue
        if listing.event_address:
            city = listing.event_address.split(',')[-1].strip() if ',' in listing.event_address else listing.event_address
            venue += f", {city}"
        parts.append(venue)

    if listing:
        try:
            price = float(listing.price or 0)
            if price > 0:
                currency = getattr(listing, 'currency', 'EUR') or 'EUR'
                parts.append(f"{currency} {price:.2f}")
            elif is_event:
                parts.append("Free")
        except (TypeError, ValueError):
            if is_event:
                parts.append("Free")
        if not is_event:
            try:
                lt = listing.listing_type
                parts.append(lt.value.replace('_', ' ').title() if hasattr(lt, 'value') else str(lt).replace('_', ' ').title())
            except Exception:
                pass

    if item.owner:
        seller = f"by {item.owner.display_name}"
        if not is_event and item.owner.city:
            seller += f", {item.owner.city}"
        parts.append(seller)
    if item.description:
        used = len(" · ".join(parts))
        remaining = max(60, 200 - used)
        desc = item.description[:remaining].strip()
        if len(item.description) > remaining:
            desc += "..."
        parts.append(desc)
    return " · ".join(parts) if parts else "Available on La Piazza"


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

    # Raffle items redirect to the raffle detail page
    if item.listings:
        for listing in item.listings:
            if listing.listing_type == ListingType.RAFFLE and not listing.deleted_at:
                from src.models.raffle import BHRaffle
                raffle = await db.scalar(
                    select(BHRaffle).where(BHRaffle.listing_id == listing.id)
                )
                if raffle:
                    return RedirectResponse(url=f"/raffles/{raffle.id}", status_code=302)

    # Resolve viewer's badge tier for progressive disclosure
    viewer_tier = "anonymous"
    if token:
        from src.dependencies import get_user as _get_user
        try:
            viewer = await _get_user(db, token)
            viewer_tier = viewer.badge_tier.value
        except Exception:
            pass

    # Compute ownership server-side so keycloak_id never reaches the template
    is_owner = bool(token and item.owner and item.owner.keycloak_id == token.get("sub", ""))

    # Similar items: same category, different item, limit 4
    similar_result = await db.execute(
        select(BHItem)
        .options(selectinload(BHItem.media))
        .where(BHItem.category == item.category)
        .where(BHItem.id != item.id)
        .where(BHItem.deleted_at.is_(None))
        .order_by(func.random())
        .limit(4)
    )
    similar_items = similar_result.scalars().all()

    # Track view (fire-and-forget, don't block page render)
    try:
        from src.models.analytics import BHItemView
        viewer_id = None
        if token:
            try:
                viewer_id = (await get_user(db, token)).id
            except Exception:
                pass
        if not is_owner:
            db.add(BHItemView(item_id=item.id, viewer_id=viewer_id))
            await db.commit()
    except Exception:
        pass

    ctx = _ctx(request, token,
        item=item,
        is_owner=is_owner,
        viewer_tier=viewer_tier,
        similar_items=similar_items,
        og_type="product",
        og_title=f"{item.name} - La Piazza",
        og_description=_og_item_desc(item, item.listings[0] if item.listings else None),
        og_image=_abs_url(item.media[0].url) if item.media else None,
    )
    return _render("pages/item_detail.html", ctx)


@router.get("/items/{slug}/edit", response_class=HTMLResponse)
async def edit_item_page(slug: str, request: Request,
                         db: AsyncSession = Depends(get_db),
                         token: Optional[dict] = Depends(get_current_user_token)):
    """Edit item page -- same form as list_item but pre-filled."""
    if not token:
        from starlette.responses import RedirectResponse
        return RedirectResponse(url="/login", status_code=302)

    result = await db.execute(
        select(BHItem)
        .options(
            selectinload(BHItem.media),
            selectinload(BHItem.listings),
        )
        .where(BHItem.slug == slug)
        .where(BHItem.deleted_at.is_(None))
    )
    item = result.scalars().first()
    if not item:
        ctx = _ctx(request, token)
        return _render("errors/404.html", ctx, status_code=404)

    # Verify ownership
    user = await get_user(db, token)
    if item.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not your item")

    import json
    # Build existing media list for the template
    existing_media = [{"id": str(m.id), "url": m.url, "alt_text": m.alt_text} for m in (item.media or [])]
    # Build existing listings for the template
    existing_listings = []
    for l in (item.listings or []):
        if not l.deleted_at:
            existing_listings.append({
                "id": str(l.id),
                "listing_type": l.listing_type.value,
                "status": l.status.value,
                "price": float(l.price) if l.price else 0,
                "price_unit": l.price_unit or "flat",
                "deposit": float(l.deposit) if l.deposit else 0,
                "currency": l.currency or "EUR",
                "min_rental_days": l.min_rental_days,
                "max_rental_days": l.max_rental_days,
                "delivery_available": l.delivery_available,
                "pickup_only": l.pickup_only,
                "notes": l.notes or "",
                "return_policy": l.return_policy or "",
                "minimum_charge": float(l.minimum_charge) if l.minimum_charge else None,
                "per_person_rate": float(l.per_person_rate) if l.per_person_rate else None,
                "max_participants": l.max_participants,
                "group_discount_pct": float(l.group_discount_pct) if l.group_discount_pct else None,
                "event_start": l.event_start.isoformat() if l.event_start else None,
                "event_end": l.event_end.isoformat() if l.event_end else None,
                "event_venue": l.event_venue or "",
                "event_address": l.event_address or "",
                "event_link": l.event_link or "",
            })

    ctx = _ctx(request, token,
        edit_mode=True,
        edit_item=item,
        edit_item_id=str(item.id),
        edit_media_json=Markup(json.dumps(existing_media)),
        edit_listings_json=Markup(json.dumps(existing_listings)),
        category_groups=CATEGORY_GROUPS,
    )
    return _render("pages/list_item.html", ctx)


@router.get("/@{username}", response_class=HTMLResponse)
async def at_username_redirect(username: str, db: AsyncSession = Depends(get_db)):
    """/@username vanity URL -- redirects to workshop profile page."""
    from starlette.responses import RedirectResponse
    # Try username match first
    result = await db.execute(
        select(BHUser).where(BHUser.username == username).where(BHUser.deleted_at.is_(None))
    )
    user = result.scalars().first()
    # Fall back to slug match
    if not user:
        result = await db.execute(
            select(BHUser).where(BHUser.slug == username).where(BHUser.deleted_at.is_(None))
        )
        user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return RedirectResponse(url=f"/workshop/{user.slug}", status_code=302)


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
            selectinload(BHUser.items).selectinload(BHItem.listings),
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

    # Fetch mentorships (as mentor or apprentice)
    from src.models.mentorship import BHMentorship, MentorshipStatus
    from sqlalchemy import or_
    mentor_result = await db.execute(
        select(BHMentorship)
        .options(selectinload(BHMentorship.apprentice), selectinload(BHMentorship.mentor))
        .where(or_(BHMentorship.mentor_id == workshop_owner.id, BHMentorship.apprentice_id == workshop_owner.id))
        .where(BHMentorship.status.in_([MentorshipStatus.ACTIVE, MentorshipStatus.COMPLETED]))
        .order_by(BHMentorship.created_at.desc())
    )
    mentorships = mentor_result.scalars().unique().all()

    # Resolve viewer's badge tier for progressive disclosure
    viewer_tier = "anonymous"
    if token:
        from src.dependencies import get_user as _get_user
        try:
            viewer = await _get_user(db, token)
            viewer_tier = viewer.badge_tier.value
        except Exception:
            pass

    # Featured video -- parse once server-side so the template stays dumb
    from src.services.video_embed import parse_video_url
    video_embed, video_provider = parse_video_url(workshop_owner.featured_video_url)

    ctx = _ctx(request, token,
        workshop=workshop_owner,
        workshop_badges=user_badges,
        mentorships=mentorships,
        badge_info=BADGE_INFO,
        viewer_tier=viewer_tier,
        video_embed=video_embed,
        video_provider=video_provider,
        og_title=f"{workshop_owner.workshop_name or workshop_owner.display_name} - La Piazza",
        og_description=_og_workshop_desc(workshop_owner),
        og_image=_abs_url(workshop_owner.banner_url or workshop_owner.avatar_url),
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
    earnings_total = 0.0
    completed_count = 0
    db_user = None

    if token:
        try:
            db_user = await get_user(db, token)
        except Exception:
            db_user = None

        if db_user:
            # User's items (all -- personal dashboards are small)
            items_result = await db.execute(
                select(BHItem)
                .options(selectinload(BHItem.media), selectinload(BHItem.listings))
                .where(BHItem.owner_id == db_user.id)
                .where(BHItem.deleted_at.is_(None))
                .order_by(BHItem.created_at.desc())
            )
            items = list(items_result.scalars().unique().all())
            item_count = len(items)

            # Sort: active listings first, then paused, pending, draft, no-listing last
            def _item_sort_key(it):
                statuses = {l.status for l in (it.listings or []) if not l.deleted_at}
                if ListingStatus.ACTIVE in statuses:
                    return 0
                if ListingStatus.PAUSED in statuses:
                    return 1
                if ListingStatus.PENDING in statuses:
                    return 2
                if ListingStatus.DRAFT in statuses:
                    return 3
                return 4
            items.sort(key=_item_sort_key)

            # Rentals as renter
            renter_result = await db.execute(
                select(BHRental)
                .options(
                    selectinload(BHRental.listing).selectinload(BHListing.item).selectinload(BHItem.owner),
                    selectinload(BHRental.renter),
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
                    selectinload(BHRental.listing).selectinload(BHListing.item).selectinload(BHItem.owner),
                    selectinload(BHRental.renter),
                )
                .join(BHListing)
                .join(BHItem, BHListing.item_id == BHItem.id)
                .where(BHItem.owner_id == db_user.id)
                .order_by(BHRental.created_at.desc())
                .limit(20)
            )
            owner_rentals = owner_result.scalars().unique().all()

            # Earnings from completed orders (sum of listing prices)
            earnings_row = await db.execute(
                select(
                    func.coalesce(func.sum(BHListing.price), 0),
                    func.count(BHRental.id),
                )
                .select_from(BHRental)
                .join(BHListing, BHRental.listing_id == BHListing.id)
                .join(BHItem, BHListing.item_id == BHItem.id)
                .where(BHItem.owner_id == db_user.id)
                .where(BHRental.status == RentalStatus.COMPLETED)
            )
            row = earnings_row.one()
            earnings_total = float(row[0])
            completed_count = row[1]

    # Count ITEMS by their listing status for the dashboard header
    # An item is "active" if ANY of its listings are active, etc.
    active_count = paused_count = draft_count = pending_count = 0
    if token and db_user:
        for item in items:
            statuses = {l.status for l in (item.listings or []) if not l.deleted_at}
            if ListingStatus.ACTIVE in statuses:
                active_count += 1
            elif ListingStatus.PENDING in statuses:
                pending_count += 1
            elif ListingStatus.PAUSED in statuses:
                paused_count += 1
            elif ListingStatus.DRAFT in statuses:
                draft_count += 1

    ctx = _ctx(request, token,
        items=items,
        item_total=item_count,
        renter_rentals=renter_rentals,
        owner_rentals=owner_rentals,
        earnings_total=earnings_total,
        completed_count=completed_count,
        db_user_id=str(db_user.id) if token and db_user else "",
        active_count=active_count,
        pending_count=pending_count,
        paused_count=paused_count,
        draft_count=draft_count,
    )
    return _render("pages/dashboard.html", ctx)


@router.get("/orders", response_class=HTMLResponse)
async def orders_page(
    request: Request,
    tab: str = "orders",
    status: Optional[str] = None,
    role: Optional[str] = None,
    sort: str = "newest",
    limit: int = 24,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    token: Optional[dict] = Depends(get_current_user_token),
):
    """Full order history -- all rentals as buyer and seller."""
    orders = []
    total_count = 0
    earnings_total = 0.0
    reviewed_rental_ids = set()

    if token:
        try:
            db_user = await get_user(db, token)
        except Exception:
            db_user = None

        if db_user:
            # Build base query
            base = (
                select(BHRental)
                .options(
                    selectinload(BHRental.listing).selectinload(BHListing.item).selectinload(BHItem.media),
                    selectinload(BHRental.listing).selectinload(BHListing.item).selectinload(BHItem.owner),
                )
            )

            # Role filter
            if role == "buyer":
                base = base.where(BHRental.renter_id == db_user.id)
            elif role == "seller":
                base = base.join(BHListing, BHRental.listing_id == BHListing.id).join(
                    BHItem, BHListing.item_id == BHItem.id
                ).where(BHItem.owner_id == db_user.id)
            else:
                # Both: renter OR item owner
                base = base.outerjoin(BHListing, BHRental.listing_id == BHListing.id).outerjoin(
                    BHItem, BHListing.item_id == BHItem.id
                ).where(
                    (BHRental.renter_id == db_user.id) | (BHItem.owner_id == db_user.id)
                )

            # Status filter
            if status:
                try:
                    status_enum = RentalStatus(status.upper())
                    base = base.where(BHRental.status == status_enum)
                except ValueError:
                    pass

            # Count
            from sqlalchemy import func as sqla_func
            count_q = select(sqla_func.count()).select_from(base.subquery())
            total_count = await db.scalar(count_q) or 0

            # Sort
            if sort == "oldest":
                base = base.order_by(BHRental.created_at.asc())
            else:
                base = base.order_by(BHRental.created_at.desc())

            base = base.offset(offset).limit(limit)
            result = await db.execute(base)
            orders = result.scalars().unique().all()

            # Which rentals has this user already reviewed?
            from src.models.review import BHReview
            reviewed_result = await db.execute(
                select(BHReview.rental_id).where(BHReview.reviewer_id == db_user.id)
            )
            reviewed_rental_ids = {row[0] for row in reviewed_result}

            # Lifetime earnings
            earnings_row = await db.execute(
                select(func.coalesce(func.sum(BHListing.price), 0))
                .select_from(BHRental)
                .join(BHListing, BHRental.listing_id == BHListing.id)
                .join(BHItem, BHListing.item_id == BHItem.id)
                .where(BHItem.owner_id == db_user.id)
                .where(BHRental.status == RentalStatus.COMPLETED)
            )
            earnings_total = float(earnings_row.scalar() or 0)

    # Fetch service quotes for Quotes tab
    quotes = []
    if token and db_user and tab == "quotes":
        from src.models.quote import BHServiceQuote, QuoteStatus
        from sqlalchemy.orm import selectinload as sinload
        q = (
            select(BHServiceQuote)
            .options(
                sinload(BHServiceQuote.listing).selectinload(BHListing.item).selectinload(BHItem.media),
                sinload(BHServiceQuote.listing).selectinload(BHListing.item).selectinload(BHItem.owner),
                sinload(BHServiceQuote.customer),
                sinload(BHServiceQuote.provider),
            )
        )
        if role == "customer":
            q = q.where(BHServiceQuote.customer_id == db_user.id)
        elif role == "provider":
            q = q.where(BHServiceQuote.provider_id == db_user.id)
        else:
            q = q.where(
                (BHServiceQuote.customer_id == db_user.id) | (BHServiceQuote.provider_id == db_user.id)
            )
        if status:
            try:
                q = q.where(BHServiceQuote.status == QuoteStatus(status.upper()))
            except ValueError:
                pass
        q = q.order_by(BHServiceQuote.created_at.desc()).limit(limit).offset(offset)
        result = await db.execute(q)
        quotes = result.scalars().unique().all()

    ctx = _ctx(request, token,
        orders=orders,
        quotes=quotes,
        total_count=total_count,
        earnings_total=earnings_total,
        viewer_user_id=db_user.id if token and db_user else None,
        reviewed_rental_ids=reviewed_rental_ids if token and db_user else set(),
        selected_tab=tab,
        selected_status=status,
        selected_role=role,
        selected_sort=sort,
        selected_limit=limit,
        selected_offset=offset,
    )
    return _render("pages/orders.html", ctx)


@router.get("/payments/success", response_class=HTMLResponse)
async def payment_success(
    request: Request,
    token: Optional[str] = None,
    PayerID: Optional[str] = None,
):
    """PayPal return page after buyer approves. Auto-captures via JS."""
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html><head><title>Payment Processing - La Piazza</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; background: #f9fafb; }}
        .card {{ background: white; border-radius: 12px; padding: 32px; max-width: 400px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .spinner {{ width: 40px; height: 40px; border: 3px solid #e5e7eb; border-top-color: #6366f1; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 16px; }}
        @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
        .success {{ color: #059669; font-size: 48px; }}
        .error {{ color: #dc2626; }}
        h2 {{ margin: 8px 0; color: #111827; }}
        p {{ color: #6b7280; font-size: 14px; }}
        a {{ color: #6366f1; text-decoration: none; font-weight: 600; }}
    </style></head>
    <body>
    <div class="card" id="status">
        <div class="spinner"></div>
        <h2>Processing Payment...</h2>
        <p>Please wait while we confirm your payment.</p>
    </div>
    <script>
    (async function() {{
        // Read payment info from sessionStorage (set before redirect)
        var paymentId = sessionStorage.getItem('pp_payment_id');
        var orderId = sessionStorage.getItem('pp_order_id');
        var el = document.getElementById('status');

        if (!paymentId || !orderId) {{
            el.innerHTML = '<div class="success">&#10003;</div><h2>Payment Complete</h2><p>Your payment has been processed.</p><p><a href="/orders">Go to Orders</a></p>';
            return;
        }}

        try {{
            var resp = await fetch('/api/v1/payments/capture', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ payment_id: paymentId, paypal_order_id: orderId }})
            }});
            if (resp.ok) {{
                sessionStorage.removeItem('pp_payment_id');
                sessionStorage.removeItem('pp_order_id');
                el.innerHTML = '<div class="success">&#10003;</div><h2>Payment Successful!</h2><p>The seller has been notified.</p><p><a href="/orders">Go to Orders</a></p>';
            }} else {{
                var err = await resp.json();
                throw new Error(err.detail || 'Capture failed');
            }}
        }} catch(e) {{
            el.innerHTML = '<div class="error">&#10007;</div><h2>Payment Issue</h2><p>' + e.message + '</p><p><a href="/orders">Back to Orders</a></p>';
        }}
    }})();
    </script>
    </body></html>
    """)


@router.get("/payments/cancel", response_class=HTMLResponse)
async def payment_cancel(request: Request):
    """PayPal return page when buyer cancels."""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html><head><title>Payment Cancelled - La Piazza</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; background: #f9fafb; }
        .card { background: white; border-radius: 12px; padding: 32px; max-width: 400px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        h2 { margin: 8px 0; color: #111827; }
        p { color: #6b7280; font-size: 14px; }
        a { display: inline-block; margin-top: 16px; padding: 10px 24px; background: #6366f1; color: white; border-radius: 8px; text-decoration: none; font-weight: 600; }
    </style></head>
    <body>
    <div class="card">
        <div style="font-size: 48px; color: #9ca3af;">&#8617;</div>
        <h2>Payment Cancelled</h2>
        <p>No charge was made. You can try again from your orders page.</p>
        <a href="/orders">Back to Orders</a>
    </div>
    </body></html>
    """)


@router.get("/messages", response_class=HTMLResponse)
async def messages_page(request: Request,
                        token: Optional[dict] = Depends(get_current_user_token)):
    """In-app messaging between users."""
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    ctx = _ctx(request, token)
    return _render("pages/messages.html", ctx)


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
                    selectinload(BHUser.social_links),
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
        is_owner=True if profile_user else False,
        is_own_profile=True if profile_user else False,
        user_bio=profile_user.bio if profile_user else "",
    )
    return _render("pages/profile.html", ctx)


@router.get("/helpboard", response_class=HTMLResponse)
async def helpboard_page(request: Request,
                         token: Optional[dict] = Depends(get_current_user_token)):
    """Community Help Board page."""
    ctx = _ctx(request, token, category_groups=CATEGORY_GROUPS)
    return _render("pages/helpboard.html", ctx)


@router.get("/leaderboard", response_class=HTMLResponse)
async def leaderboard_page(request: Request,
                           token: Optional[dict] = Depends(get_current_user_token)):
    """Event leaderboard: rankings, streaks, achievements."""
    from src.models.achievement import ACHIEVEMENTS
    ctx = _ctx(request, token, achievements=ACHIEVEMENTS)
    return _render("pages/leaderboard.html", ctx)


@router.get("/delivery/{rental_id}", response_class=HTMLResponse)
async def delivery_tracking_page(
    rental_id: str,
    request: Request,
    token: Optional[dict] = Depends(get_current_user_token),
):
    """Delivery tracking page with GPS map and timeline."""
    ctx = _ctx(request, token, rental_id=rental_id)
    return _render("pages/delivery_tracking.html", ctx)


@router.get("/calendar", response_class=HTMLResponse)
async def calendar_page(
    request: Request,
    token: Optional[dict] = Depends(get_current_user_token),
):
    """Community calendar with month view and event list."""
    ctx = _ctx(request, token,
        og_title="Community Calendar -- La Piazza",
        og_description="Workshops, meetups, and events happening in your neighborhood. RSVP and join the community.",
        og_image="https://lapiazza.app/static/images/icon-192.png",
    )
    return _render("pages/calendar.html", ctx)


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


@router.get("/demo-login", response_class=HTMLResponse)
async def demo_login_page(
    request: Request,
    token: Optional[dict] = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db),
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
        {"username": "sally", "display_name": "Sally Thompson", "workshop": "Sally's Kitchen", "roles": "lender", "badge": "trusted", "color": "emerald", "avatar": f"{_av}/sally.svg"},
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
        {"username": "nicolo", "display_name": "Nicol\u00f2 Roccamena", "workshop": "Nic's Dojo", "roles": "ambassador, lender", "badge": "active", "color": "rose", "avatar": f"{_av}/nicolo.svg"},
    ]

    # Use real avatar_url from DB so demo login matches profile pages
    emails = [f"{du['username']}@borrowhood.local" for du in demo_users]
    result = await db.execute(
        select(BHUser.email, BHUser.avatar_url)
        .where(BHUser.email.in_(emails))
        .where(BHUser.deleted_at.is_(None))
    )
    avatar_map = {row[0].split("@")[0]: row[1] for row in result.all() if row[1]}
    for du in demo_users:
        if du["username"] in avatar_map:
            du["avatar"] = avatar_map[du["username"]]

    ctx = _ctx(request, token, demo_users=demo_users)
    return _render("pages/demo_login.html", ctx)


@router.get("/raffles", response_class=HTMLResponse)
async def raffles_page(request: Request,
                       token: Optional[dict] = Depends(get_current_user_token)):
    """Raffle browse page."""
    ctx = _ctx(request, token)
    return _render("pages/raffles.html", ctx)


@router.get("/raffles/create", response_class=HTMLResponse)
async def raffle_create_page(request: Request,
                             token: Optional[dict] = Depends(get_current_user_token)):
    """Raffle creation form. Requires login."""
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    ctx = _ctx(request, token)
    return _render("pages/raffle_create.html", ctx)


@router.get("/raffles/guide", response_class=HTMLResponse)
async def raffle_guide(request: Request,
                       token: Optional[dict] = Depends(get_current_user_token)):
    """Raffle guide page — how raffles work, trust tiers, FAQ."""
    ctx = _ctx(request, token)
    return _render("pages/raffle_guide.html", ctx)


@router.get("/raffles/{raffle_id}", response_class=HTMLResponse)
async def raffle_detail_page(raffle_id: str, request: Request,
                             db: AsyncSession = Depends(get_db),
                             token: Optional[dict] = Depends(get_current_user_token)):
    """Raffle detail page with ticket purchase, stats, draw result."""
    from uuid import UUID as PyUUID
    from src.models.raffle import BHRaffle
    from sqlalchemy.orm import selectinload
    from src.models.listing import BHListing
    from src.models.item import BHItem

    try:
        rid = PyUUID(raffle_id)
    except ValueError:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Invalid raffle ID")

    raffle = await db.scalar(
        select(BHRaffle)
        .options(
            selectinload(BHRaffle.listing).selectinload(BHListing.item).selectinload(BHItem.media),
            selectinload(BHRaffle.organizer),
        )
        .where(BHRaffle.id == rid)
        .where(BHRaffle.deleted_at.is_(None))
    )
    if not raffle:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Raffle not found")

    ctx = _ctx(request, token, raffle=raffle)
    return _render("pages/raffle_detail.html", ctx)


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


@router.get("/legal", response_class=HTMLResponse)
async def legal_notice(request: Request,
                       token: Optional[dict] = Depends(get_current_user_token)):
    """Legal notice / Imprint (required by Italian and EU law)."""
    ctx = _ctx(request, token)
    return _render("pages/legal.html", ctx)


@router.get("/googled3f2ccce2b1f34d3.html", response_class=Response)
async def google_verification():
    """Google Search Console verification file."""
    return Response(content="google-site-verification: googled3f2ccce2b1f34d3.html", media_type="text/html")


@router.get("/robots.txt", response_class=Response)
async def robots_txt():
    """Robots.txt for search engine crawlers."""
    content = """User-agent: *
Allow: /
Disallow: /api/
Disallow: /auth/
Disallow: /admin/
Disallow: /demo-login

Sitemap: https://lapiazza.app/sitemap.xml
"""
    return Response(content=content, media_type="text/plain")


@router.get("/sitemap.xml", response_class=Response)
async def sitemap_xml(db: AsyncSession = Depends(get_db)):
    """Dynamic sitemap for search engines."""
    from datetime import datetime

    urls = []
    # Static pages
    urls.append(("https://lapiazza.app/", "daily", "1.0"))
    urls.append(("https://lapiazza.app/browse", "daily", "0.9"))
    urls.append(("https://lapiazza.app/members", "daily", "0.8"))
    urls.append(("https://lapiazza.app/helpboard", "daily", "0.7"))
    urls.append(("https://lapiazza.app/terms", "monthly", "0.3"))

    # Items
    result = await db.execute(
        select(BHItem.slug, BHItem.updated_at)
        .where(BHItem.deleted_at.is_(None))
        .order_by(BHItem.updated_at.desc())
        .limit(500)
    )
    for slug, updated in result:
        lastmod = updated.strftime("%Y-%m-%d") if updated else ""
        urls.append((f"https://lapiazza.app/items/{slug}", "weekly", "0.7"))

    # Workshops
    result = await db.execute(
        select(BHUser.slug, BHUser.updated_at)
        .where(BHUser.deleted_at.is_(None))
        .where(BHUser.slug.isnot(None))
        .order_by(BHUser.updated_at.desc())
        .limit(500)
    )
    for slug, updated in result:
        lastmod = updated.strftime("%Y-%m-%d") if updated else ""
        urls.append((f"https://lapiazza.app/workshop/{slug}", "weekly", "0.6"))

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for url, freq, priority in urls:
        xml += f'  <url><loc>{url}</loc><changefreq>{freq}</changefreq><priority>{priority}</priority></url>\n'
    xml += '</urlset>'

    return Response(content=xml, media_type="application/xml")
