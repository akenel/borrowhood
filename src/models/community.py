"""Community models: multi-community federation.

Each BorrowHood instance can host multiple communities.
Users join communities, items belong to communities.
A default community is seeded from config on startup.
"""

import enum
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, BHBase


class CommunityRole(str, enum.Enum):
    MEMBER = "member"
    ADMIN = "admin"
    OWNER = "owner"


class BHCommunity(BHBase, Base):
    """A local community on the BorrowHood platform."""

    __tablename__ = "bh_community"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    country_code: Mapped[Optional[str]] = mapped_column(String(2))
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    timezone: Mapped[Optional[str]] = mapped_column(String(50))
    tagline: Mapped[Optional[str]] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Location center
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    radius_km: Mapped[float] = mapped_column(Float, default=25.0)

    # Flags
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    # Owner (creator)
    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=True
    )

    # Relationships
    memberships: Mapped[List["BHCommunityMembership"]] = relationship(
        back_populates="community", cascade="all, delete-orphan"
    )


class BHCommunityMembership(BHBase, Base):
    """A user's membership in a community."""

    __tablename__ = "bh_community_membership"

    community_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_community.id"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )
    role: Mapped[CommunityRole] = mapped_column(
        Enum(CommunityRole), default=CommunityRole.MEMBER, nullable=False
    )

    # Relationships
    community: Mapped["BHCommunity"] = relationship(back_populates="memberships")
    user: Mapped["BHUser"] = relationship()
