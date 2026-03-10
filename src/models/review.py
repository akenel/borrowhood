"""Review model with weighted reputation scoring.

Reviews are weighted by reviewer's badge tier:
- Newcomer review = 1x weight
- Active = 2x, Trusted = 5x, Pillar = 8x, Legend = 10x
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, CheckConstraint, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
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

# Review window: 90 days after rental completion
REVIEW_WINDOW_DAYS = 90


class BHReview(BHBase, Base):
    """A review left after a completed rental.

    Features modeled after the best of Amazon, eBay, Etsy, Airbnb:
    - Verified transaction (rental_id required)
    - Subcategory ratings (accuracy, communication, value, timeliness)
    - Would-recommend flag
    - Weighted by reviewer badge tier
    - Owner response (locks reviewer editing -- Airbnb pattern)
    - Community helpful/not-helpful voting
    - Photo evidence
    - 90-day review window
    """

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

    # Overall rating
    rating: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    title: Mapped[Optional[str]] = mapped_column(String(200))
    body: Mapped[Optional[str]] = mapped_column(Text)
    content_language: Mapped[str] = mapped_column(String(5), default="en")

    # Subcategory ratings (1-5, optional -- Airbnb-style)
    rating_accuracy: Mapped[Optional[int]] = mapped_column(Integer)     # Was it as described?
    rating_communication: Mapped[Optional[int]] = mapped_column(Integer) # Was communication clear?
    rating_value: Mapped[Optional[int]] = mapped_column(Integer)         # Worth the price?
    rating_timeliness: Mapped[Optional[int]] = mapped_column(Integer)    # On time? Punctual?

    # Would recommend (binary -- powerful trust signal)
    would_recommend: Mapped[Optional[bool]] = mapped_column(Boolean)

    # Skill-specific rating (optional)
    skill_name: Mapped[Optional[str]] = mapped_column(String(100))
    skill_rating: Mapped[Optional[int]] = mapped_column(Integer)

    # Weight snapshot (captured at review time for audit)
    reviewer_tier: Mapped[str] = mapped_column(String(20), nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    # Photos (up to 3 URLs)
    photo_urls: Mapped[Optional[list]] = mapped_column(ARRAY(String(500)), default=None)

    # Owner response (one reply from the reviewee)
    # Once owner responds, reviewer editing is LOCKED (Airbnb pattern)
    owner_response: Mapped[Optional[str]] = mapped_column(Text)
    owner_response_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Community voting
    helpful_count: Mapped[int] = mapped_column(Integer, default=0)
    not_helpful_count: Mapped[int] = mapped_column(Integer, default=0)

    # Moderation
    visible: Mapped[bool] = mapped_column(default=True)

    # Relationships
    reviewer: Mapped["BHUser"] = relationship(foreign_keys=[reviewer_id])
    reviewee: Mapped["BHUser"] = relationship(foreign_keys=[reviewee_id])

    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_review_rating_range"),
        CheckConstraint("skill_rating IS NULL OR (skill_rating >= 1 AND skill_rating <= 5)", name="ck_skill_rating_range"),
        CheckConstraint("rating_accuracy IS NULL OR (rating_accuracy >= 1 AND rating_accuracy <= 5)", name="ck_rating_accuracy_range"),
        CheckConstraint("rating_communication IS NULL OR (rating_communication >= 1 AND rating_communication <= 5)", name="ck_rating_communication_range"),
        CheckConstraint("rating_value IS NULL OR (rating_value >= 1 AND rating_value <= 5)", name="ck_rating_value_range"),
        CheckConstraint("rating_timeliness IS NULL OR (rating_timeliness >= 1 AND rating_timeliness <= 5)", name="ck_rating_timeliness_range"),
    )


class BHReviewVote(BHBase, Base):
    """Track helpful/not-helpful votes on reviews. One vote per user per review."""

    __tablename__ = "bh_review_vote"

    review_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_review.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )
    helpful: Mapped[bool] = mapped_column(nullable=False)  # True = helpful, False = not helpful

    __table_args__ = (
        UniqueConstraint("review_id", "user_id", name="uq_review_vote_per_user"),
    )
