"""User-facing pages: profile, workshop, /@username redirect, onboarding."""

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



