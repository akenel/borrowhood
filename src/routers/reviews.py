"""Review API -- Best-in-class review system.

Combines the best of Amazon, eBay, Etsy, Airbnb:
- Verified transactions only (rental_id required)
- Subcategory ratings (accuracy, communication, value, timeliness)
- Would-recommend flag
- Weighted by reviewer badge tier
- Owner response (locks reviewer editing -- Airbnb pattern)
- Community helpful/not-helpful voting
- Photo evidence (up to 3)
- 90-day review window
- Star distribution in summary
- Sort by: recent, helpful, highest, lowest
- Filter by: star rating
- Reviewer name + avatar in output
"""

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

router = APIRouter(prefix="/api/v1/reviews", tags=["reviews"])


def _enrich_review(review: BHReview) -> dict:
    """Add reviewer display name and avatar to review output."""
    data = {c.key: getattr(review, c.key) for c in review.__table__.columns}
    data["reviewer_name"] = review.reviewer.display_name if review.reviewer else None
    data["reviewer_avatar"] = review.reviewer.avatar_url if review.reviewer else None
    return data


@router.get("", response_model=List[ReviewOut])
async def list_reviews(
    reviewee_id: Optional[UUID] = None,
    reviewer_id: Optional[UUID] = None,
    rating: Optional[int] = Query(None, ge=1, le=5),
    sort: Literal["recent", "helpful", "highest", "lowest"] = "recent",
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List reviews with filters and sorting. Public endpoint."""
    query = (
        select(BHReview)
        .options(selectinload(BHReview.reviewer))
        .where(BHReview.visible == True)
    )

    if reviewee_id:
        query = query.where(BHReview.reviewee_id == reviewee_id)
    if reviewer_id:
        query = query.where(BHReview.reviewer_id == reviewer_id)
    if rating:
        query = query.where(BHReview.rating == rating)

    # Sorting
    if sort == "helpful":
        query = query.order_by(BHReview.helpful_count.desc(), BHReview.created_at.desc())
    elif sort == "highest":
        query = query.order_by(BHReview.rating.desc(), BHReview.created_at.desc())
    elif sort == "lowest":
        query = query.order_by(BHReview.rating.asc(), BHReview.created_at.desc())
    else:  # recent
        query = query.order_by(BHReview.created_at.desc())

    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    reviews = result.scalars().all()
    return [_enrich_review(r) for r in reviews]


@router.get("/summary/{user_id}")
async def review_summary(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """Full review summary: average, weighted average, star distribution, subcategory averages, recommendation rate."""
    reviews = await db.execute(
        select(BHReview)
        .where(BHReview.reviewee_id == user_id)
        .where(BHReview.visible == True)
    )
    all_reviews = reviews.scalars().all()

    if not all_reviews:
        return {
            "user_id": str(user_id), "count": 0,
            "average": None, "weighted_average": None,
            "star_distribution": {"5": 0, "4": 0, "3": 0, "2": 0, "1": 0},
            "subcategory_averages": None,
            "recommend_rate": None,
        }

    total_rating = sum(r.rating for r in all_reviews)
    total_weighted = sum(r.rating * r.weight for r in all_reviews)
    total_weight = sum(r.weight for r in all_reviews)

    # Star distribution
    dist = {str(i): 0 for i in range(1, 6)}
    for r in all_reviews:
        dist[str(r.rating)] += 1

    # Subcategory averages (only from reviews that have them)
    sub_fields = ["rating_accuracy", "rating_communication", "rating_value", "rating_timeliness"]
    sub_avgs = {}
    for field in sub_fields:
        vals = [getattr(r, field) for r in all_reviews if getattr(r, field) is not None]
        sub_avgs[field.replace("rating_", "")] = round(sum(vals) / len(vals), 2) if vals else None

    # Recommendation rate
    recs = [r.would_recommend for r in all_reviews if r.would_recommend is not None]
    rec_rate = round(sum(1 for r in recs if r) / len(recs) * 100) if recs else None

    return {
        "user_id": str(user_id),
        "count": len(all_reviews),
        "average": round(total_rating / len(all_reviews), 2),
        "weighted_average": round(total_weighted / total_weight, 2) if total_weight else None,
        "star_distribution": dist,
        "subcategory_averages": sub_avgs if any(v is not None for v in sub_avgs.values()) else None,
        "recommend_rate": rec_rate,
    }


@router.post("", response_model=ReviewOut, status_code=201)
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


@router.post("/{review_id}/photos", status_code=201)
async def upload_review_photo(
    review_id: UUID,
    file: UploadFile = File(...),
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Upload a photo to an existing review. Max 3 photos, 5MB each."""
    user = await get_user(db, token)

    result = await db.execute(
        select(BHReview).where(BHReview.id == review_id)
    )
    review = result.scalars().first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.reviewer_id != user.id:
        raise HTTPException(status_code=403, detail="Only the reviewer can add photos")

    current_photos = review.photo_urls or []
    if len(current_photos) >= MAX_REVIEW_PHOTOS:
        raise HTTPException(status_code=400, detail=f"Maximum {MAX_REVIEW_PHOTOS} photos per review")

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, and WebP images allowed")

    contents = await file.read()
    if len(contents) > MAX_PHOTO_SIZE:
        raise HTTPException(status_code=413, detail="Photo must be under 5MB")

    REVIEW_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid_mod.uuid4()}_{file.filename}"
    filepath = REVIEW_UPLOAD_DIR / filename
    filepath.write_bytes(contents)

    url = f"/static/uploads/reviews/{filename}"
    review.photo_urls = current_photos + [url]

    await db.commit()
    return {"url": url, "count": len(review.photo_urls)}


class OwnerResponseCreate(BaseModel):
    """Owner's response to a review. Locks the review from further editing."""
    body: str = Field(..., min_length=1, max_length=2000)


@router.post("/{review_id}/respond", response_model=ReviewOut)
async def respond_to_review(
    review_id: UUID,
    data: OwnerResponseCreate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Owner responds to a review. One response allowed, can be edited. Locks reviewer editing."""
    user = await get_user(db, token)

    result = await db.execute(
        select(BHReview).options(selectinload(BHReview.reviewer)).where(BHReview.id == review_id)
    )
    review = result.scalars().first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.reviewee_id != user.id:
        raise HTTPException(status_code=403, detail="Only the reviewed person can respond")

    review.owner_response = data.body
    review.owner_response_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(review)
    return _enrich_review(review)


class ReviewVoteCreate(BaseModel):
    """Vote on whether a review is helpful."""
    helpful: bool


@router.post("/{review_id}/vote", status_code=200)
async def vote_on_review(
    review_id: UUID,
    data: ReviewVoteCreate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Vote a review as helpful or not helpful. One vote per user, can change."""
    user = await get_user(db, token)

    # Check review exists
    result = await db.execute(
        select(BHReview).where(BHReview.id == review_id)
    )
    review = result.scalars().first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    # Can't vote on your own review
    if review.reviewer_id == user.id:
        raise HTTPException(status_code=400, detail="Cannot vote on your own review")

    # Check for existing vote
    existing = await db.execute(
        select(BHReviewVote)
        .where(BHReviewVote.review_id == review_id)
        .where(BHReviewVote.user_id == user.id)
    )
    vote = existing.scalars().first()

    if vote:
        if vote.helpful == data.helpful:
            # Same vote again = remove it (toggle off)
            old_helpful = vote.helpful
            await db.delete(vote)
            if old_helpful:
                review.helpful_count = max(0, review.helpful_count - 1)
            else:
                review.not_helpful_count = max(0, review.not_helpful_count - 1)
            await db.commit()
            return {"action": "removed", "helpful_count": review.helpful_count, "not_helpful_count": review.not_helpful_count}
        else:
            # Changing vote
            if vote.helpful:
                review.helpful_count = max(0, review.helpful_count - 1)
                review.not_helpful_count += 1
            else:
                review.not_helpful_count = max(0, review.not_helpful_count - 1)
                review.helpful_count += 1
            vote.helpful = data.helpful
            await db.commit()
            return {"action": "changed", "helpful_count": review.helpful_count, "not_helpful_count": review.not_helpful_count}
    else:
        # New vote
        new_vote = BHReviewVote(review_id=review_id, user_id=user.id, helpful=data.helpful)
        db.add(new_vote)
        if data.helpful:
            review.helpful_count += 1
        else:
            review.not_helpful_count += 1
        await db.commit()
        return {"action": "voted", "helpful_count": review.helpful_count, "not_helpful_count": review.not_helpful_count}


@router.get("/{review_id}/my-vote")
async def get_my_vote(
    review_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Get the current user's vote on a review (if any)."""
    user = await get_user(db, token)
    result = await db.execute(
        select(BHReviewVote)
        .where(BHReviewVote.review_id == review_id)
        .where(BHReviewVote.user_id == user.id)
    )
    vote = result.scalars().first()
    if not vote:
        return {"voted": False, "helpful": None}
    return {"voted": True, "helpful": vote.helpful}
