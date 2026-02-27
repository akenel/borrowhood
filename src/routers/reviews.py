"""Review API with weighted reputation scoring.

Reviews can only be left after a completed rental.
Weight is calculated from the reviewer's badge tier at review time.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies import require_auth
from src.models.rental import BHRental, RentalStatus
from src.models.review import BHReview, REVIEW_WEIGHTS
from src.models.user import BHUser, BadgeTier
from src.schemas.review import ReviewCreate, ReviewOut

router = APIRouter(prefix="/api/v1/reviews", tags=["reviews"])


async def _get_user(db: AsyncSession, keycloak_id: str) -> BHUser:
    result = await db.execute(
        select(BHUser).where(BHUser.keycloak_id == keycloak_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=403, detail="User not provisioned in BorrowHood")
    return user


@router.get("", response_model=List[ReviewOut])
async def list_reviews(
    reviewee_id: Optional[UUID] = None,
    reviewer_id: Optional[UUID] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List reviews with optional filters. Public endpoint."""
    query = select(BHReview).where(BHReview.visible == True)

    if reviewee_id:
        query = query.where(BHReview.reviewee_id == reviewee_id)
    if reviewer_id:
        query = query.where(BHReview.reviewer_id == reviewer_id)

    query = query.order_by(BHReview.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/summary/{user_id}")
async def review_summary(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get review summary for a user: average rating, count, weighted average."""
    reviews = await db.execute(
        select(BHReview)
        .where(BHReview.reviewee_id == user_id)
        .where(BHReview.visible == True)
    )
    all_reviews = reviews.scalars().all()

    if not all_reviews:
        return {"user_id": str(user_id), "count": 0, "average": None, "weighted_average": None}

    total_rating = sum(r.rating for r in all_reviews)
    total_weighted = sum(r.rating * r.weight for r in all_reviews)
    total_weight = sum(r.weight for r in all_reviews)

    return {
        "user_id": str(user_id),
        "count": len(all_reviews),
        "average": round(total_rating / len(all_reviews), 2),
        "weighted_average": round(total_weighted / total_weight, 2) if total_weight else None,
    }


@router.post("", response_model=ReviewOut, status_code=201)
async def create_review(
    data: ReviewCreate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Submit a review after a completed rental. Requires authentication."""
    user = await _get_user(db, token["sub"])

    # Verify rental exists and is completed
    result = await db.execute(
        select(BHRental).where(BHRental.id == data.rental_id)
    )
    rental = result.scalars().first()
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")
    if rental.status != RentalStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Can only review completed rentals")

    # Must be participant in the rental
    if rental.renter_id != user.id:
        raise HTTPException(status_code=403, detail="Only the renter can leave a review")

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
        skill_name=data.skill_name,
        skill_rating=data.skill_rating,
        reviewer_tier=user.badge_tier.value,
        weight=weight,
    )
    db.add(review)

    # Update reviewee's reputation points
    reviewee_points = await db.execute(
        select(BHUser).where(BHUser.id == data.reviewee_id)
    )
    reviewee = reviewee_points.scalars().first()
    if reviewee and reviewee.points:
        reviewee.points.reviews_received += 1
        reviewee.points.total_points += int(data.rating * weight)

    # Update reviewer's reputation points
    if user.points:
        user.points.reviews_given += 1
        user.points.total_points += 5  # 5 pts for giving a review

    await db.flush()

    # Check and award badges for both parties
    from src.services.badges import check_and_award_badges
    await check_and_award_badges(db, user.id)
    await check_and_award_badges(db, data.reviewee_id)

    await db.commit()
    await db.refresh(review)
    return review
