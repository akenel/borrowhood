"""Account pages: dashboard, orders, messages, delivery tracking."""

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

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request,
                    db: AsyncSession = Depends(get_db),
                    token: Optional[dict] = Depends(get_current_user_token)):
    """User dashboard with items, rentals, and incoming requests."""
    if not token:
        from starlette.responses import RedirectResponse
        return RedirectResponse(url="/login", status_code=302)
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
    if not token:
        from starlette.responses import RedirectResponse
        return RedirectResponse(url="/login", status_code=302)
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
                    selectinload(BHRental.renter),
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



@router.get("/messages", response_class=HTMLResponse)
async def messages_page(request: Request,
                        token: Optional[dict] = Depends(get_current_user_token)):
    """In-app messaging between users."""
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    ctx = _ctx(request, token)
    return _render("pages/messages.html", ctx)



@router.get("/delivery/{rental_id}", response_class=HTMLResponse)
async def delivery_tracking_page(
    rental_id: str,
    request: Request,
    token: Optional[dict] = Depends(get_current_user_token),
):
    """Delivery tracking page with GPS map and timeline."""
    ctx = _ctx(request, token, rental_id=rental_id)
    return _render("pages/delivery_tracking.html", ctx)



