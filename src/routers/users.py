"""Users API: members directory listing, single profile, and favorites CRUD.

Public reads for member discovery, auth-gated favorites.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.dependencies import get_current_user_token, require_auth
from src.models.user import BadgeTier, BHUser, BHUserFavorite, WorkshopType
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


async def _get_user(db: AsyncSession, keycloak_id: str) -> BHUser:
    """Look up BHUser by Keycloak subject ID."""
    result = await db.execute(
        select(BHUser).where(BHUser.keycloak_id == keycloak_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=403, detail="User not provisioned in BorrowHood")
    return user


# ── Favorites (auth-gated) ── must be BEFORE /{user_id} routes ──


@router.get("/me/favorites", response_model=List[FavoriteOut])
async def list_my_favorites(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List current user's favorites with nested member cards."""
    user = await _get_user(db, token["sub"])
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
    user = await _get_user(db, token["sub"])
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
    sort: str = Query("newest", pattern="^(newest|name_asc|badge_tier)$"),
    limit: int = Query(12, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List/search community members. Public endpoint."""
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

    # Total count before pagination
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    # Sort
    if sort == "newest":
        query = query.order_by(BHUser.created_at.desc())
    elif sort == "name_asc":
        query = query.order_by(BHUser.display_name.asc())
    elif sort == "badge_tier":
        query = query.order_by(_BADGE_SORT, BHUser.display_name.asc())

    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    members = result.scalars().unique().all()

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
    user = await _get_user(db, token["sub"])
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
    user = await _get_user(db, token["sub"])
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
