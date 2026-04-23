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

templates = Jinja2Templates(directory="src/templates")

# Make datetime.now() available in templates for seasonal tag logic
from datetime import datetime, timezone
templates.env.globals["now"] = datetime.now
templates.env.globals["now_utc"] = lambda: datetime.now(timezone.utc)

# Environment awareness for the staging badge
from src.config import settings as _settings
templates.env.globals["environment"] = _settings.environment


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


