"""Saved search model -- users save search criteria and get notified on matches.

"Tell me when a 2-bedroom apartment under EUR 500/mo appears in Trapani."
"""

import uuid
from typing import Optional

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, BHBase


class BHSavedSearch(BHBase, Base):
    """A saved search with criteria. Checked when new listings are created."""

    __tablename__ = "bh_saved_search"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )

    # Search label (user-facing name)
    name: Mapped[str] = mapped_column(String(200), nullable=False)

    # Search criteria
    query: Mapped[Optional[str]] = mapped_column(String(200))  # text search
    category: Mapped[Optional[str]] = mapped_column(String(50))
    category_group: Mapped[Optional[str]] = mapped_column(String(50))
    item_type: Mapped[Optional[str]] = mapped_column(String(20))

    # Price range
    price_min: Mapped[Optional[float]] = mapped_column(Float)
    price_max: Mapped[Optional[float]] = mapped_column(Float)

    # Attribute filters (JSONB -- e.g. {"bedrooms_min": 2, "fuel_type": "diesel"})
    attribute_filters: Mapped[Optional[dict]] = mapped_column(JSON, default=None)

    # Location radius
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    radius_km: Mapped[Optional[int]] = mapped_column(Integer, default=25)

    # Notification control
    notify_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    match_count: Mapped[int] = mapped_column(Integer, default=0)

    # Relationship
    user: Mapped["BHUser"] = relationship()
