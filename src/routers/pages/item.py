"""Item-related pages: detail, edit, list-a-new-item form."""

import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from markupsafe import Markup
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



@router.get("/list", response_class=HTMLResponse)
async def list_item_page(request: Request,
                         token: Optional[dict] = Depends(get_current_user_token)):
    """Form to list a new item. Requires authentication."""
    if not token:
        from starlette.responses import RedirectResponse
        return RedirectResponse(url="/login", status_code=302)
    ctx = _ctx(request, token, category_groups=CATEGORY_GROUPS)
    return _render("pages/list_item.html", ctx)



