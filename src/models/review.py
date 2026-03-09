"""Review model with weighted reputation scoring.

Reviews are weighted by reviewer's badge tier:
- Newcomer review = 1x weight
- Active = 2x, Trusted = 5x, Pillar = 8x, Legend = 10x
"""

import uuid
from typing import Optional

from sqlalchemy import CheckConstraint, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, BHBase
from src.models.user import BadgeTier


# Weight multipliers for reputation calculation
REVIEW_WEIGHTS = {
    BadgeTier.NEWCOMER: 1.0,
    BadgeTier.ACTIVE: 2.0,
    BadgeTier.TRUSTED: 5.0,
    BadgeTier.PILLAR: 8.0,
    BadgeTier.LEGEND: 10.0,
}


class BHReview(BHBase, Base):
    """A review left after a completed rental."""

    __tablename__ = "bh_review"

    rental_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_rental.id"), nullable=False, index=True
    )
    reviewer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )
    reviewee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )

    # Rating
    rating: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    title: Mapped[Optional[str]] = mapped_column(String(200))
    body: Mapped[Optional[str]] = mapped_column(Text)
    content_language: Mapped[str] = mapped_column(String(5), default="en")

    # Skill-specific rating (optional)
    skill_name: Mapped[Optional[str]] = mapped_column(String(100))
    skill_rating: Mapped[Optional[int]] = mapped_column(Integer)

    # Weight snapshot (captured at review time for audit)
    reviewer_tier: Mapped[str] = mapped_column(String(20), nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    # Photos (up to 3 URLs)
    photo_urls: Mapped[Optional[list]] = mapped_column(ARRAY(String(500)), default=None)

    # Moderation
    visible: Mapped[bool] = mapped_column(default=True)

    # Relationships
    reviewer: Mapped["BHUser"] = relationship(foreign_keys=[reviewer_id])
    reviewee: Mapped["BHUser"] = relationship(foreign_keys=[reviewee_id])

    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_review_rating_range"),
        CheckConstraint("skill_rating IS NULL OR (skill_rating >= 1 AND skill_rating <= 5)", name="ck_skill_rating_range"),
    )
