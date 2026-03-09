"""Public Q&A on listings.

Buyers ask questions, sellers answer publicly. Visible to all.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, BHBase


class BHListingQA(BHBase, Base):
    """A question-answer pair on a listing."""

    __tablename__ = "bh_listing_qa"

    listing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_listing.id"), nullable=False, index=True
    )
    asker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )

    question: Mapped[str] = mapped_column(Text, nullable=False)

    # Answer (filled in by listing owner)
    answer: Mapped[Optional[str]] = mapped_column(Text, default=None)
    answered_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=True
    )
    answered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=None)

    # Relationships
    asker: Mapped["BHUser"] = relationship(foreign_keys=[asker_id])
    answered_by: Mapped["BHUser"] = relationship(foreign_keys=[answered_by_id])
