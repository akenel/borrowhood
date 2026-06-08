"""Who viewed your item -- the owner-only audience panel.

FULL traceability for logged-in MEMBERS (the community graph: who, when, how often -- so the
owner can say hi and invite them in). AGGREGATE-ONLY for anonymous viewers (we count strangers,
we never unmask them). Authenticity/community, not surveillance.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies import get_user, require_auth
from src.models.analytics import BHItemView
from src.models.item import BHItem
from src.models.user import BHUser

router = APIRouter()


@router.get("/{item_id}/viewers")
async def item_viewers(item_id: UUID, token: dict = Depends(require_auth),
                       db: AsyncSession = Depends(get_db)):
    item = await db.get(BHItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="item not found")
    user = await get_user(db, token)
    if not user or item.owner_id != user.id:
        raise HTTPException(status_code=403, detail="only the owner can see who viewed this")

    total = await db.scalar(
        select(func.count()).select_from(BHItemView).where(BHItemView.item_id == item_id)) or 0
    anonymous = await db.scalar(
        select(func.count()).select_from(BHItemView).where(
            BHItemView.item_id == item_id, BHItemView.viewer_id.is_(None))) or 0

    rows = (await db.execute(
        select(BHUser.display_name, BHUser.slug, BHUser.avatar_url,
               func.count(BHItemView.id).label("views"),
               func.min(BHItemView.created_at).label("first_seen"),
               func.max(BHItemView.created_at).label("last_seen"))
        .join(BHUser, BHUser.id == BHItemView.viewer_id)
        .where(BHItemView.item_id == item_id)
        .group_by(BHUser.id, BHUser.display_name, BHUser.slug, BHUser.avatar_url)
        .order_by(func.max(BHItemView.created_at).desc()))).all()
    members = [{
        "name": r.display_name or "A neighbour",
        "slug": r.slug,
        "avatar": r.avatar_url,
        "views": r.views,
        "first_seen": r.first_seen.isoformat() if r.first_seen else None,
        "last_seen": r.last_seen.isoformat() if r.last_seen else None,
    } for r in rows]

    return {"item_id": str(item_id), "total": total, "anonymous": anonymous,
            "member_count": len(members), "members": members}
