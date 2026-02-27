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

from src.database import get_db
from src.dependencies import get_current_user_token
from src.i18n import detect_language, get_translator, SUPPORTED_LANGUAGES
from src.models.item import BHItem
from src.models.listing import BHListing, ListingStatus
from src.models.user import BHUser

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="src/templates")


def _ctx(request: Request, response: Response, token: Optional[dict] = None, **kwargs) -> dict:
    """Build template context with i18n, lang, and common vars.

    Every page gets: request, user, t(), lang, supported_languages.
    Language detection: ?lang= query param > bh_lang cookie > Accept-Language > default.
    Sets bh_lang cookie when language changes.
    """
    query_lang = request.query_params.get("lang")
    cookie_lang = request.cookies.get("bh_lang")
    accept_lang = request.headers.get("accept-language")

    lang = detect_language(query_lang, cookie_lang, accept_lang)
    t = get_translator(lang)

    # Set cookie if changed via query param
    if query_lang and query_lang != cookie_lang:
        response.set_cookie("bh_lang", lang, max_age=365 * 24 * 3600, samesite="lax")

    ctx = {
        "request": request,
        "user": token,
        "t": t,
        "lang": lang,
        "supported_languages": SUPPORTED_LANGUAGES,
    }
    ctx.update(kwargs)
    return ctx


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, response: Response,
               db: AsyncSession = Depends(get_db),
               token: Optional[dict] = Depends(get_current_user_token)):
    """Landing page with featured items and stats."""
    listing_count = await db.scalar(
        select(func.count(BHListing.id)).where(BHListing.status == ListingStatus.ACTIVE)
    )
    user_count = await db.scalar(select(func.count(BHUser.id)))

    result = await db.execute(
        select(BHItem)
        .options(selectinload(BHItem.media), selectinload(BHItem.owner))
        .join(BHListing, BHItem.id == BHListing.item_id)
        .where(BHListing.status == ListingStatus.ACTIVE)
        .order_by(BHItem.created_at.desc())
        .limit(6)
    )
    featured_items = result.scalars().unique().all()

    ctx = _ctx(request, response, token,
        listing_count=listing_count or 0,
        user_count=user_count or 0,
        featured_items=featured_items,
    )
    return templates.TemplateResponse("pages/home.html", ctx)


@router.get("/browse", response_class=HTMLResponse)
async def browse(request: Request, response: Response,
                 q: Optional[str] = None,
                 category: Optional[str] = None,
                 item_type: Optional[str] = None,
                 sort: str = "newest",
                 db: AsyncSession = Depends(get_db),
                 token: Optional[dict] = Depends(get_current_user_token)):
    """Browse and search items with filters."""
    query = (
        select(BHItem)
        .options(selectinload(BHItem.media), selectinload(BHItem.owner).selectinload(BHUser.languages))
        .join(BHListing, BHItem.id == BHListing.item_id)
        .where(BHListing.status == ListingStatus.ACTIVE)
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

    query = query.limit(50)
    result = await db.execute(query)
    items = result.scalars().unique().all()

    cat_result = await db.execute(
        select(BHItem.category).distinct().where(BHItem.deleted_at.is_(None))
    )
    categories = [row[0] for row in cat_result.all()]

    ctx = _ctx(request, response, token,
        items=items,
        categories=categories,
        q=q or "",
        selected_category=category,
        selected_type=item_type,
        selected_sort=sort,
    )
    return templates.TemplateResponse("pages/browse.html", ctx)


@router.get("/items/{slug}", response_class=HTMLResponse)
async def item_detail(slug: str, request: Request, response: Response,
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
        ctx = _ctx(request, response, token)
        return templates.TemplateResponse("errors/404.html", ctx, status_code=404)

    ctx = _ctx(request, response, token,
        item=item,
        og_title=f"{item.name} - BorrowHood",
        og_description=item.description[:160] if item.description else "Available on BorrowHood",
        og_image=item.media[0].url if item.media else None,
    )
    return templates.TemplateResponse("pages/item_detail.html", ctx)


@router.get("/workshop/{slug}", response_class=HTMLResponse)
async def workshop_profile(slug: str, request: Request, response: Response,
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
        )
        .where(BHUser.slug == slug)
        .where(BHUser.deleted_at.is_(None))
    )
    workshop_owner = result.scalars().first()

    if not workshop_owner:
        ctx = _ctx(request, response, token)
        return templates.TemplateResponse("errors/404.html", ctx, status_code=404)

    ctx = _ctx(request, response, token,
        workshop=workshop_owner,
        og_title=f"{workshop_owner.workshop_name or workshop_owner.display_name} - BorrowHood",
        og_description=workshop_owner.tagline or "Workshop on BorrowHood",
    )
    return templates.TemplateResponse("pages/workshop.html", ctx)
