"""Users API: members directory listing, single profile, and favorites CRUD.

Public reads for member discovery, auth-gated favorites.
"""

import uuid as uuid_mod
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.dependencies import get_current_user_token, get_user, require_auth
from src.models.user import BadgeTier, BHUser, BHUserFavorite, WorkshopType
from src.services.search import haversine_km

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "static" / "uploads" / "avatars"
ALLOWED_AVATAR_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5 MB
from src.schemas.user import (
    FavoriteCreate,
    FavoriteOut,
    MemberCardOut,
    PaginatedMembers,
)

router = APIRouter(prefix="/api/v1/users", tags=["users"])

# Badge tier sort order: legend first, newcomer last
_BADGE_SORT = case(
    (BHUser.badge_tier == BadgeTier.LEGEND, 0),
    (BHUser.badge_tier == BadgeTier.PILLAR, 1),
    (BHUser.badge_tier == BadgeTier.TRUSTED, 2),
    (BHUser.badge_tier == BadgeTier.ACTIVE, 3),
    else_=4,
)


# ── Avatar upload ──


@router.post("/me/avatar", status_code=200)
async def upload_avatar(
    file: UploadFile = File(...),
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Upload a profile avatar image."""
    if file.content_type not in ALLOWED_AVATAR_TYPES:
        raise HTTPException(status_code=400, detail="File must be JPEG, PNG, or WebP")

    user = await get_user(db, token)

    contents = await file.read()
    if len(contents) > MAX_AVATAR_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 5 MB)")

    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename and "." in file.filename else "jpg"
    if ext not in ("jpg", "jpeg", "png", "webp"):
        ext = "jpg"
    filename = f"{uuid_mod.uuid4().hex}.{ext}"
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    (UPLOAD_DIR / filename).write_bytes(contents)

    user.avatar_url = f"/static/uploads/avatars/{filename}"
    await db.commit()
    return {"status": "ok", "avatar_url": user.avatar_url}


# ── Favorites (auth-gated) ── must be BEFORE /{user_id} routes ──


@router.get("/me/favorites", response_model=List[FavoriteOut])
async def list_my_favorites(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List current user's favorites with nested member cards."""
    user = await get_user(db, token)
    result = await db.execute(
        select(BHUserFavorite)
        .options(
            selectinload(BHUserFavorite.favorite_user)
            .selectinload(BHUser.languages)
        )
        .where(BHUserFavorite.user_id == user.id)
        .order_by(BHUserFavorite.created_at.desc())
    )
    return result.scalars().all()


@router.get("/me/favorite-ids")
async def list_my_favorite_ids(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Return just the IDs of favorited users (for batch heart-state checks)."""
    user = await get_user(db, token)
    result = await db.execute(
        select(BHUserFavorite.favorite_user_id)
        .where(BHUserFavorite.user_id == user.id)
    )
    ids = [str(row[0]) for row in result.all()]
    return {"ids": ids}


# ── Public endpoints ──


@router.get("", response_model=PaginatedMembers)
async def list_members(
    q: Optional[str] = None,
    city: Optional[str] = None,
    badge_tier: Optional[str] = None,
    workshop_type: Optional[str] = None,
    near_lat: Optional[float] = Query(None, ge=-90, le=90),
    near_lng: Optional[float] = Query(None, ge=-180, le=180),
    radius_km: float = Query(25.0, ge=1, le=500),
    sort: str = Query("newest", pattern="^(newest|name_asc|badge_tier|closest)$"),
    limit: int = Query(12, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List/search community members. Public endpoint.

    Proximity search: pass near_lat + near_lng to filter by distance.
    Use sort=closest to order by distance (requires near_lat/near_lng).
    """
    query = (
        select(BHUser)
        .options(selectinload(BHUser.languages))
        .where(BHUser.deleted_at.is_(None))
    )

    if q:
        search_term = f"%{q}%"
        query = query.where(
            BHUser.display_name.ilike(search_term)
            | BHUser.workshop_name.ilike(search_term)
            | BHUser.tagline.ilike(search_term)
        )
    if city:
        query = query.where(BHUser.city.ilike(f"%{city}%"))
    if badge_tier:
        query = query.where(BHUser.badge_tier == badge_tier)
    if workshop_type:
        query = query.where(BHUser.workshop_type == workshop_type)

    # Proximity: pre-filter to members who have coordinates
    use_proximity = near_lat is not None and near_lng is not None
    if use_proximity:
        query = query.where(BHUser.latitude.isnot(None), BHUser.longitude.isnot(None))

    # Sort (DB-level for non-proximity sorts)
    if sort == "newest" and not use_proximity:
        query = query.order_by(BHUser.created_at.desc())
    elif sort == "name_asc":
        query = query.order_by(BHUser.display_name.asc())
    elif sort == "badge_tier":
        query = query.order_by(_BADGE_SORT, BHUser.display_name.asc())

    # For proximity search, fetch more candidates for post-query filtering
    if use_proximity:
        result = await db.execute(query)
        all_candidates = list(result.scalars().unique().all())

        # Haversine distance filter (Python-side, same pattern as item search)
        members_with_dist = []
        for m in all_candidates:
            dist = haversine_km(
                near_lat, near_lng, m.latitude, m.longitude,
                alt2=m.altitude or 0.0,
            )
            if dist <= radius_km:
                members_with_dist.append((m, dist))

        if sort == "closest":
            members_with_dist.sort(key=lambda x: x[1])
        elif sort == "newest":
            members_with_dist.sort(key=lambda x: x[0].created_at, reverse=True)

        total = len(members_with_dist)
        page = members_with_dist[offset : offset + limit]
        members = [m for m, _ in page]
    else:
        # Total count before pagination
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query) or 0

        query = query.offset(offset).limit(limit)
        result = await db.execute(query)
        members = list(result.scalars().unique().all())

    return PaginatedMembers(
        items=members,
        total=total,
        limit=limit,
        offset=offset,
        has_more=(offset + len(members)) < total,
    )


@router.get("/{user_id}", response_model=MemberCardOut)
async def get_member(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a single member card by ID. Public endpoint."""
    result = await db.execute(
        select(BHUser)
        .options(selectinload(BHUser.languages))
        .where(BHUser.id == user_id)
        .where(BHUser.deleted_at.is_(None))
    )
    member = result.scalars().first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


# ── Favorite toggle on specific user ──


@router.post("/{user_id}/favorite", status_code=201)
async def add_favorite(
    user_id: UUID,
    data: FavoriteCreate = FavoriteCreate(),
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Add a user to favorites. Returns 409 if already favorited."""
    user = await get_user(db, token)
    if user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot favorite yourself")

    # Check target exists
    target = await db.scalar(
        select(BHUser.id).where(BHUser.id == user_id).where(BHUser.deleted_at.is_(None))
    )
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    # Check duplicate
    existing = await db.scalar(
        select(BHUserFavorite.id)
        .where(BHUserFavorite.user_id == user.id)
        .where(BHUserFavorite.favorite_user_id == user_id)
    )
    if existing:
        raise HTTPException(status_code=409, detail="Already favorited")

    fav = BHUserFavorite(
        user_id=user.id,
        favorite_user_id=user_id,
        note=data.note,
    )
    db.add(fav)
    await db.commit()
    return {"status": "added", "favorite_user_id": str(user_id)}


@router.delete("/{user_id}/favorite", status_code=200)
async def remove_favorite(
    user_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Remove a user from favorites."""
    user = await get_user(db, token)
    result = await db.execute(
        select(BHUserFavorite)
        .where(BHUserFavorite.user_id == user.id)
        .where(BHUserFavorite.favorite_user_id == user_id)
    )
    fav = result.scalars().first()
    if not fav:
        raise HTTPException(status_code=404, detail="Favorite not found")

    await db.delete(fav)
    await db.commit()
    return {"status": "removed", "favorite_user_id": str(user_id)}
