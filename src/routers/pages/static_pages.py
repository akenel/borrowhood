"""Static/utility pages: demo-login, terms, legal, robots, sitemap."""

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



@router.get("/why-lapiazza", response_class=HTMLResponse)
async def why_lapiazza(request: Request,
                       token: Optional[dict] = Depends(get_current_user_token)):
    """Why La Piazza: the honest case for a fee-free neighborhood marketplace."""
    ctx = _ctx(request, token)
    return _render("pages/why_lapiazza.html", ctx)



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
    urls.append(("https://lapiazza.app/why-lapiazza", "monthly", "0.7"))
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


