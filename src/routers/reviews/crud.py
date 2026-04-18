"""Create + update review (owner-only edits, locked after response)."""

from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Literal, Optional
from uuid import UUID
import uuid as uuid_mod

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.dependencies import get_user, require_auth
from src.models.item import BHItem
from src.models.listing import BHListing
from src.models.rental import BHRental, RentalStatus
from src.models.review import BHReview, BHReviewVote, REVIEW_WEIGHTS, REVIEW_WINDOW_DAYS
from src.models.user import BHUser, BadgeTier
from src.schemas.review import ReviewCreate, ReviewOut

from ._shared import _enrich_review

router = APIRouter()

async def create_review(
    data: ReviewCreate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Submit a review after a completed rental. 90-day window enforced."""
    user = await get_user(db, token)
    # Eagerly load points for reputation update
    await db.execute(
        select(BHUser).options(selectinload(BHUser.points)).where(BHUser.id == user.id)
    )

    # Verify rental exists and is completed
    result = await db.execute(
        select(BHRental)
        .options(selectinload(BHRental.listing).selectinload(BHListing.item))
        .where(BHRental.id == data.rental_id)
    )
    rental = result.scalars().first()
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")
    if rental.status != RentalStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Can only review completed rentals")

    # Enforce 90-day review window
    if rental.updated_at:
        deadline = rental.updated_at + timedelta(days=REVIEW_WINDOW_DAYS)
        if datetime.now(timezone.utc) > deadline:
            raise HTTPException(
                status_code=400,
                detail=f"Review window has closed ({REVIEW_WINDOW_DAYS} days after completion)"
            )

    # Must be participant in the rental (renter OR item owner)
    owner_id = rental.listing.item.owner_id if rental.listing and rental.listing.item else None
    if rental.renter_id != user.id and owner_id != user.id:
        raise HTTPException(status_code=403, detail="Only rental participants can leave a review")

    # Prevent duplicate reviews
    existing = await db.execute(
        select(BHReview)
        .where(BHReview.rental_id == data.rental_id)
        .where(BHReview.reviewer_id == user.id)
    )
    if existing.scalars().first():
        raise HTTPException(status_code=409, detail="Already reviewed this rental")

    # Calculate weight from reviewer's current badge tier
    weight = REVIEW_WEIGHTS.get(user.badge_tier, 1.0)

    review = BHReview(
        rental_id=data.rental_id,
        reviewer_id=user.id,
        reviewee_id=data.reviewee_id,
        rating=data.rating,
        title=data.title,
        body=data.body,
        content_language=data.content_language,
        rating_accuracy=data.rating_accuracy,
        rating_communication=data.rating_communication,
        rating_value=data.rating_value,
        rating_timeliness=data.rating_timeliness,
        would_recommend=data.would_recommend,
        skill_name=data.skill_name,
        skill_rating=data.skill_rating,
        reviewer_tier=user.badge_tier.value,
        weight=weight,
    )
    db.add(review)

    # Update reviewee's reputation points (eagerly load points)
    reviewee_result = await db.execute(
        select(BHUser).options(selectinload(BHUser.points)).where(BHUser.id == data.reviewee_id)
    )
    reviewee = reviewee_result.scalars().first()
    if reviewee and reviewee.points:
        reviewee.points.reviews_received += 1
        reviewee.points.total_points += int(data.rating * weight)

    # Update reviewer's reputation points
    if user.points:
        user.points.reviews_given += 1
        user.points.total_points += 5  # 5 pts for giving a review

    await db.flush()

    # Notify the reviewee
    from src.models.notification import NotificationType
    from src.services.notify import create_notification
    await create_notification(
        db=db,
        user_id=data.reviewee_id,
        notification_type=NotificationType.REVIEW_RECEIVED,
        title=f"{user.display_name} left you a {data.rating}-star review",
        body=data.title or "",
        link="/dashboard",
        entity_type="review",
    )

    # Check and award badges for both parties
    from src.services.badges import check_and_award_badges
    await check_and_award_badges(db, user.id)
    await check_and_award_badges(db, data.reviewee_id)

    # Recalculate trust score for the reviewee (bad reviews lower it)
    from src.services.reputation import calculate_trust_score
    await calculate_trust_score(db, data.reviewee_id)

    await db.commit()
    # Re-fetch with reviewer relationship for enrichment
    result = await db.execute(
        select(BHReview).options(selectinload(BHReview.reviewer)).where(BHReview.id == review.id)
    )
    review = result.scalars().first()
    return _enrich_review(review)


class ReviewUpdate(BaseModel):
    """Update an existing review. Blocked if owner has responded (Airbnb pattern)."""
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = Field(None, max_length=200)
    body: Optional[str] = None
    content_language: str = Field(default="en", max_length=5)
    rating_accuracy: Optional[int] = Field(None, ge=1, le=5)
    rating_communication: Optional[int] = Field(None, ge=1, le=5)
    rating_value: Optional[int] = Field(None, ge=1, le=5)
    rating_timeliness: Optional[int] = Field(None, ge=1, le=5)
    would_recommend: Optional[bool] = None


@router.put("/{review_id}", response_model=ReviewOut)
async def update_review(
    review_id: UUID,
    data: ReviewUpdate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Edit an existing review. LOCKED if owner has responded (Airbnb pattern)."""
    user = await get_user(db, token)

    result = await db.execute(
        select(BHReview).options(selectinload(BHReview.reviewer)).where(BHReview.id == review_id)
    )
    review = result.scalars().first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.reviewer_id != user.id:
        raise HTTPException(status_code=403, detail="Only the reviewer can edit their review")

    # Airbnb pattern: owner response locks editing
    if review.owner_response:
        raise HTTPException(
            status_code=403,
            detail="This review is locked because the owner has responded. "
                   "Contact support if you need to make changes."
        )

    old_rating = review.rating
    review.rating = data.rating
    review.title = data.title
    review.body = data.body
    review.content_language = data.content_language
    review.rating_accuracy = data.rating_accuracy
    review.rating_communication = data.rating_communication
    review.rating_value = data.rating_value
    review.rating_timeliness = data.rating_timeliness
    review.would_recommend = data.would_recommend

    # Recalculate trust score if rating changed
    if old_rating != data.rating:
        from src.services.reputation import calculate_trust_score
        await calculate_trust_score(db, review.reviewee_id)

    await db.commit()
    await db.refresh(review)
    return _enrich_review(review)


REVIEW_UPLOAD_DIR = Path(__file__).resolve().parent.parent / "static" / "uploads" / "reviews"
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_REVIEW_PHOTOS = 3
MAX_PHOTO_SIZE = 5 * 1024 * 1024  # 5 MB




