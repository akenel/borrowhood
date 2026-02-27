"""HTML page routes: home, browse, item detail, workshop profile.

All pages extend base.html. All use Jinja2 server-side rendering.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.dependencies import get_current_user_token
from src.models.item import BHItem
from src.models.listing import BHListing, ListingStatus
from src.models.user import BHUser

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="src/templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: AsyncSession = Depends(get_db),
               token: Optional[dict] = Depends(get_current_user_token)):
    """Landing page with featured items and stats."""
    # Count active listings
    listing_count = await db.scalar(
        select(func.count(BHListing.id)).where(BHListing.status == ListingStatus.ACTIVE)
    )
    user_count = await db.scalar(select(func.count(BHUser.id)))

    # Get recent items with their media
    result = await db.execute(
        select(BHItem)
        .options(selectinload(BHItem.media), selectinload(BHItem.owner))
        .join(BHListing, BHItem.id == BHListing.item_id)
        .where(BHListing.status == ListingStatus.ACTIVE)
        .order_by(BHItem.created_at.desc())
        .limit(6)
    )
    featured_items = result.scalars().unique().all()

    return templates.TemplateResponse("pages/home.html", {
        "request": request,
        "user": token,
        "listing_count": listing_count or 0,
        "user_count": user_count or 0,
        "featured_items": featured_items,
        "og_title": "BorrowHood - Your Neighborhood Rental Platform",
        "og_description": "Rent it. Lend it. Share it. Teach it. No fees. Open source.",
    })


@router.get("/browse", response_class=HTMLResponse)
async def browse(request: Request,
                 q: Optional[str] = None,
                 category: Optional[str] = None,
                 item_type: Optional[str] = None,
                 lang: Optional[str] = None,
                 sort: str = "newest",
                 db: AsyncSession = Depends(get_db),
                 token: Optional[dict] = Depends(get_current_user_token)):
    """Browse and search items with filters."""
    query = (
        select(BHItem)
        .options(selectinload(BHItem.media), selectinload(BHItem.owner))
        .join(BHListing, BHItem.id == BHListing.item_id)
        .where(BHListing.status == ListingStatus.ACTIVE)
        .where(BHItem.deleted_at.is_(None))
    )

    # Fuzzy search
    if q:
        search_term = f"%{q}%"
        query = query.where(
            BHItem.name.ilike(search_term) | BHItem.description.ilike(search_term)
        )

    # Filters
    if category:
        query = query.where(BHItem.category == category)
    if item_type:
        query = query.where(BHItem.item_type == item_type)

    # Sort
    if sort == "newest":
        query = query.order_by(BHItem.created_at.desc())
    elif sort == "oldest":
        query = query.order_by(BHItem.created_at.asc())
    elif sort == "name_asc":
        query = query.order_by(BHItem.name.asc())

    # Limit for v1 (cursor pagination in v2)
    query = query.limit(50)

    result = await db.execute(query)
    items = result.scalars().unique().all()

    # Get distinct categories for filter dropdown
    cat_result = await db.execute(
        select(BHItem.category).distinct().where(BHItem.deleted_at.is_(None))
    )
    categories = [row[0] for row in cat_result.all()]

    return templates.TemplateResponse("pages/browse.html", {
        "request": request,
        "user": token,
        "items": items,
        "categories": categories,
        "q": q or "",
        "selected_category": category,
        "selected_type": item_type,
        "selected_sort": sort,
        "og_title": "Browse Items - BorrowHood",
    })


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
        return templates.TemplateResponse("errors/404.html", {
            "request": request, "user": token
        }, status_code=404)

    return templates.TemplateResponse("pages/item_detail.html", {
        "request": request,
        "user": token,
        "item": item,
        "og_title": f"{item.name} - BorrowHood",
        "og_description": item.description[:160] if item.description else "Available on BorrowHood",
        "og_image": item.media[0].url if item.media else None,
    })


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
        )
        .where(BHUser.slug == slug)
        .where(BHUser.deleted_at.is_(None))
    )
    workshop_owner = result.scalars().first()

    if not workshop_owner:
        return templates.TemplateResponse("errors/404.html", {
            "request": request, "user": token
        }, status_code=404)

    return templates.TemplateResponse("pages/workshop.html", {
        "request": request,
        "user": token,
        "workshop": workshop_owner,
        "og_title": f"{workshop_owner.workshop_name or workshop_owner.display_name} - BorrowHood",
        "og_description": workshop_owner.tagline or "Workshop on BorrowHood",
    })
