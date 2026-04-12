"""Analytics models: track item views and listing impressions."""

import uuid
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base, BHBase


class BHItemView(BHBase, Base):
    """A page view on an item detail page."""

    __tablename__ = "bh_item_view"

    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_item.id"), nullable=False, index=True
    )
    viewer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=True
    )
