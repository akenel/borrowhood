"""Saved Search API -- save search criteria, get notified on matches.

Auth-gated. Each user can have up to 20 saved searches.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies import get_user, require_auth
from src.models.saved_search import BHSavedSearch

router = APIRouter(prefix="/api/v1/saved-searches", tags=["saved-searches"])

MAX_SAVED_SEARCHES = 20


class SavedSearchCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    query: Optional[str] = Field(None, max_length=200)
    category: Optional[str] = Field(None, max_length=50)
    category_group: Optional[str] = Field(None, max_length=50)
    item_type: Optional[str] = Field(None, max_length=20)
    price_min: Optional[float] = Field(None, ge=0)
    price_max: Optional[float] = Field(None, ge=0)
    attribute_filters: Optional[dict] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_km: Optional[int] = Field(None, ge=1, le=200)


class SavedSearchOut(BaseModel):
    id: UUID
    name: str
    query: Optional[str] = None
    category: Optional[str] = None
    category_group: Optional[str] = None
    item_type: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    attribute_filters: Optional[dict] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_km: Optional[int] = None
    notify_enabled: bool = True
    match_count: int = 0

    class Config:
        from_attributes = True


@router.get("", response_model=List[SavedSearchOut])
async def list_saved_searches(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List current user's saved searches."""
    user = await get_user(db, token)
    result = await db.execute(
        select(BHSavedSearch)
        .where(BHSavedSearch.user_id == user.id)
        .where(BHSavedSearch.deleted_at.is_(None))
        .order_by(BHSavedSearch.created_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=SavedSearchOut, status_code=201)
async def create_saved_search(
    data: SavedSearchCreate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Save a search with criteria. Max 20 per user."""
    user = await get_user(db, token)

    count = await db.scalar(
        select(func.count(BHSavedSearch.id))
        .where(BHSavedSearch.user_id == user.id)
        .where(BHSavedSearch.deleted_at.is_(None))
    )
    if count >= MAX_SAVED_SEARCHES:
        raise HTTPException(status_code=400, detail=f"Maximum {MAX_SAVED_SEARCHES} saved searches")

    search = BHSavedSearch(
        user_id=user.id,
        name=data.name,
        query=data.query,
        category=data.category,
        category_group=data.category_group,
        item_type=data.item_type,
        price_min=data.price_min,
        price_max=data.price_max,
        attribute_filters=data.attribute_filters,
        latitude=data.latitude,
        longitude=data.longitude,
        radius_km=data.radius_km,
    )
    db.add(search)
    await db.commit()
    await db.refresh(search)
    return search


@router.delete("/{search_id}", status_code=200)
async def delete_saved_search(
    search_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Delete a saved search."""
    user = await get_user(db, token)
    result = await db.execute(
        select(BHSavedSearch)
        .where(BHSavedSearch.id == search_id)
        .where(BHSavedSearch.user_id == user.id)
    )
    search = result.scalars().first()
    if not search:
        raise HTTPException(status_code=404, detail="Saved search not found")
    await db.delete(search)
    await db.commit()
    return {"status": "deleted", "name": search.name}


@router.patch("/{search_id}/toggle", status_code=200)
async def toggle_notifications(
    search_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Toggle notifications on/off for a saved search."""
    user = await get_user(db, token)
    result = await db.execute(
        select(BHSavedSearch)
        .where(BHSavedSearch.id == search_id)
        .where(BHSavedSearch.user_id == user.id)
    )
    search = result.scalars().first()
    if not search:
        raise HTTPException(status_code=404, detail="Saved search not found")
    search.notify_enabled = not search.notify_enabled
    await db.commit()
    return {"notify_enabled": search.notify_enabled}
