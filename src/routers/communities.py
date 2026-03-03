"""Community API: create, join, leave, manage communities.

Multi-community federation: each deployment can host multiple local communities.
A default community is seeded from config on startup.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from slugify import slugify
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.dependencies import get_user, require_auth
from src.models.community import BHCommunity, BHCommunityMembership, CommunityRole

router = APIRouter(prefix="/api/v1/communities", tags=["communities"])


# --- Schemas ---

class CommunityCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    country_code: Optional[str] = Field(None, max_length=2)
    currency: str = Field(default="EUR", max_length=3)
    timezone: Optional[str] = Field(None, max_length=50)
    tagline: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_km: float = Field(default=25.0, ge=1, le=500)


class CommunityUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    tagline: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_km: Optional[float] = Field(None, ge=1, le=500)


class CommunityOut(BaseModel):
    id: UUID
    name: str
    slug: str
    country_code: Optional[str] = None
    currency: str
    timezone: Optional[str] = None
    tagline: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_km: float
    is_default: bool
    member_count: int = 0
    created_at: str

    class Config:
        from_attributes = True


class MemberOut(BaseModel):
    user_id: UUID
    display_name: str
    role: CommunityRole
    joined_at: str


# --- Endpoints ---

@router.post("", response_model=CommunityOut, status_code=201)
async def create_community(
    data: CommunityCreate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Create a new community. Creator becomes OWNER."""
    user = await get_user(db, token)

    slug = slugify(data.name)
    # Ensure unique slug
    existing = await db.scalar(
        select(BHCommunity.id).where(BHCommunity.slug == slug)
    )
    if existing:
        counter = 1
        while True:
            candidate = f"{slug}-{counter}"
            ex = await db.scalar(
                select(BHCommunity.id).where(BHCommunity.slug == candidate)
            )
            if not ex:
                slug = candidate
                break
            counter += 1

    community = BHCommunity(
        name=data.name,
        slug=slug,
        country_code=data.country_code,
        currency=data.currency,
        timezone=data.timezone,
        tagline=data.tagline,
        description=data.description,
        latitude=data.latitude,
        longitude=data.longitude,
        radius_km=data.radius_km,
        owner_id=user.id,
    )
    db.add(community)
    await db.flush()

    # Auto-join creator as OWNER
    membership = BHCommunityMembership(
        community_id=community.id,
        user_id=user.id,
        role=CommunityRole.OWNER,
    )
    db.add(membership)
    await db.commit()
    await db.refresh(community)

    return CommunityOut(
        id=community.id, name=community.name, slug=community.slug,
        country_code=community.country_code, currency=community.currency,
        timezone=community.timezone, tagline=community.tagline,
        description=community.description, latitude=community.latitude,
        longitude=community.longitude, radius_km=community.radius_km,
        is_default=community.is_default, member_count=1,
        created_at=community.created_at.isoformat(),
    )


@router.get("", response_model=List[CommunityOut])
async def list_communities(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List all communities with member counts."""
    result = await db.execute(
        select(BHCommunity)
        .where(BHCommunity.deleted_at.is_(None))
        .order_by(BHCommunity.is_default.desc(), BHCommunity.name.asc())
        .offset(offset)
        .limit(limit)
    )
    communities = result.scalars().all()

    out = []
    for c in communities:
        count = await db.scalar(
            select(func.count(BHCommunityMembership.id))
            .where(BHCommunityMembership.community_id == c.id)
        ) or 0
        out.append(CommunityOut(
            id=c.id, name=c.name, slug=c.slug,
            country_code=c.country_code, currency=c.currency,
            timezone=c.timezone, tagline=c.tagline,
            description=c.description, latitude=c.latitude,
            longitude=c.longitude, radius_km=c.radius_km,
            is_default=c.is_default, member_count=count,
            created_at=c.created_at.isoformat(),
        ))
    return out


@router.get("/{slug}", response_model=CommunityOut)
async def get_community(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Get community details by slug."""
    result = await db.execute(
        select(BHCommunity).where(BHCommunity.slug == slug)
    )
    community = result.scalars().first()
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")

    count = await db.scalar(
        select(func.count(BHCommunityMembership.id))
        .where(BHCommunityMembership.community_id == community.id)
    ) or 0

    return CommunityOut(
        id=community.id, name=community.name, slug=community.slug,
        country_code=community.country_code, currency=community.currency,
        timezone=community.timezone, tagline=community.tagline,
        description=community.description, latitude=community.latitude,
        longitude=community.longitude, radius_km=community.radius_km,
        is_default=community.is_default, member_count=count,
        created_at=community.created_at.isoformat(),
    )


@router.post("/{slug}/join")
async def join_community(
    slug: str,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Join a community."""
    user = await get_user(db, token)

    result = await db.execute(
        select(BHCommunity).where(BHCommunity.slug == slug)
    )
    community = result.scalars().first()
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")

    # Check not already a member
    existing = await db.execute(
        select(BHCommunityMembership)
        .where(BHCommunityMembership.community_id == community.id)
        .where(BHCommunityMembership.user_id == user.id)
    )
    if existing.scalars().first():
        raise HTTPException(status_code=409, detail="Already a member")

    membership = BHCommunityMembership(
        community_id=community.id,
        user_id=user.id,
        role=CommunityRole.MEMBER,
    )
    db.add(membership)
    await db.commit()
    return {"status": "joined", "community": community.name}


@router.delete("/{slug}/leave")
async def leave_community(
    slug: str,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Leave a community."""
    user = await get_user(db, token)

    result = await db.execute(
        select(BHCommunity).where(BHCommunity.slug == slug)
    )
    community = result.scalars().first()
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")

    membership_result = await db.execute(
        select(BHCommunityMembership)
        .where(BHCommunityMembership.community_id == community.id)
        .where(BHCommunityMembership.user_id == user.id)
    )
    membership = membership_result.scalars().first()
    if not membership:
        raise HTTPException(status_code=404, detail="Not a member")
    if membership.role == CommunityRole.OWNER:
        raise HTTPException(status_code=400, detail="Owner cannot leave. Transfer ownership first.")

    await db.delete(membership)
    await db.commit()
    return {"status": "left", "community": community.name}


@router.get("/{slug}/members", response_model=List[MemberOut])
async def list_members(
    slug: str,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List members of a community."""
    result = await db.execute(
        select(BHCommunity).where(BHCommunity.slug == slug)
    )
    community = result.scalars().first()
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")

    members_result = await db.execute(
        select(BHCommunityMembership)
        .options(selectinload(BHCommunityMembership.user))
        .where(BHCommunityMembership.community_id == community.id)
        .order_by(BHCommunityMembership.created_at.asc())
        .limit(limit)
    )
    memberships = members_result.scalars().all()

    return [
        MemberOut(
            user_id=m.user_id,
            display_name=m.user.display_name,
            role=m.role,
            joined_at=m.created_at.isoformat(),
        )
        for m in memberships
    ]


@router.patch("/{slug}", response_model=CommunityOut)
async def update_community(
    slug: str,
    data: CommunityUpdate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Update community details. Admin or Owner only."""
    user = await get_user(db, token)

    result = await db.execute(
        select(BHCommunity).where(BHCommunity.slug == slug)
    )
    community = result.scalars().first()
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")

    # Check admin/owner role
    membership_result = await db.execute(
        select(BHCommunityMembership)
        .where(BHCommunityMembership.community_id == community.id)
        .where(BHCommunityMembership.user_id == user.id)
    )
    membership = membership_result.scalars().first()
    if not membership or membership.role not in (CommunityRole.ADMIN, CommunityRole.OWNER):
        raise HTTPException(status_code=403, detail="Admin or Owner role required")

    if data.name is not None:
        community.name = data.name
    if data.tagline is not None:
        community.tagline = data.tagline
    if data.description is not None:
        community.description = data.description
    if data.latitude is not None:
        community.latitude = data.latitude
    if data.longitude is not None:
        community.longitude = data.longitude
    if data.radius_km is not None:
        community.radius_km = data.radius_km

    await db.commit()
    await db.refresh(community)

    count = await db.scalar(
        select(func.count(BHCommunityMembership.id))
        .where(BHCommunityMembership.community_id == community.id)
    ) or 0

    return CommunityOut(
        id=community.id, name=community.name, slug=community.slug,
        country_code=community.country_code, currency=community.currency,
        timezone=community.timezone, tagline=community.tagline,
        description=community.description, latitude=community.latitude,
        longitude=community.longitude, radius_km=community.radius_km,
        is_default=community.is_default, member_count=count,
        created_at=community.created_at.isoformat(),
    )
