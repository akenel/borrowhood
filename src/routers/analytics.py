"""Seller analytics API: views, revenue, conversion metrics per item."""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies import get_user, require_auth
from src.models.analytics import BHItemView
from src.models.item import BHItem
from src.models.listing import BHListing, ListingStatus
from src.models.rental import BHRental, RentalStatus

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

COMPLETED_STATUSES = {RentalStatus.COMPLETED, RentalStatus.PAYMENT_CONFIRMED}


@router.get("/seller-stats")
async def seller_stats(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Per-item analytics: views, orders, revenue for the authenticated user."""
    user = await get_user(db, token)

    items_result = await db.execute(
        select(BHItem.id, BHItem.name, BHItem.slug)
        .where(BHItem.owner_id == user.id)
        .where(BHItem.deleted_at.is_(None))
        .order_by(BHItem.created_at.desc())
    )
    items = items_result.all()

    item_ids = [i[0] for i in items]
    if not item_ids:
        return {"items": [], "summary": {"total_views": 0, "total_orders": 0, "total_revenue": 0}}

    views_result = await db.execute(
        select(BHItemView.item_id, func.count(BHItemView.id))
        .where(BHItemView.item_id.in_(item_ids))
        .group_by(BHItemView.item_id)
    )
    views_map = dict(views_result.all())

    orders_result = await db.execute(
        select(BHListing.item_id, func.count(BHRental.id), func.coalesce(func.sum(BHListing.price), 0))
        .join(BHRental, BHRental.listing_id == BHListing.id)
        .where(BHListing.item_id.in_(item_ids))
        .where(BHRental.status.in_(COMPLETED_STATUSES))
        .group_by(BHListing.item_id)
    )
    orders_map = {}
    revenue_map = {}
    for item_id, count, revenue in orders_result.all():
        orders_map[item_id] = count
        revenue_map[item_id] = float(revenue or 0)

    result_items = []
    total_views = 0
    total_orders = 0
    total_revenue = 0.0
    for item_id, name, slug in items:
        v = views_map.get(item_id, 0)
        o = orders_map.get(item_id, 0)
        r = revenue_map.get(item_id, 0)
        total_views += v
        total_orders += o
        total_revenue += r
        result_items.append({
            "item_id": str(item_id),
            "name": name,
            "slug": slug,
            "views": v,
            "orders": o,
            "revenue": round(r, 2),
            "conversion": round(o / v * 100, 1) if v > 0 else 0,
        })

    result_items.sort(key=lambda x: x["views"], reverse=True)

    return {
        "items": result_items[:20],
        "summary": {
            "total_views": total_views,
            "total_orders": total_orders,
            "total_revenue": round(total_revenue, 2),
            "conversion": round(total_orders / total_views * 100, 1) if total_views > 0 else 0,
        },
    }
