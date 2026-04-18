"""Shared helpers for reviews/ package."""

from src.models.review import BHReview


def _enrich_review(review: BHReview) -> dict:
    """Add reviewer display name and avatar to review output."""
    data = {c.key: getattr(review, c.key) for c in review.__table__.columns}
    data["reviewer_name"] = review.reviewer.display_name if review.reviewer else None
    data["reviewer_avatar"] = review.reviewer.avatar_url if review.reviewer else None
    data["reviewer_badge_tier"] = review.reviewer.badge_tier if review.reviewer else None
    return data
