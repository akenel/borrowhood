"""Review API with weighted reputation scoring.

Reviews can only be left after a completed rental.
Weight is calculated from the reviewer's badge tier at review time.
"""

from pathlib import Path
from typing import List, Optional
from uuid import UUID
import uuid as uuid_mod

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.dependencies import get_user, require_auth
from src.models.item import BHItem
from src.models.listing import BHListing
from src.models.rental import BHRental, RentalStatus
from src.models.review import BHReview, REVIEW_WEIGHTS
from src.models.user import BHUser, BadgeTier
from src.schemas.review import ReviewCreate, ReviewOut

router = APIRouter(prefix="/api/v1/reviews", tags=["reviews"])


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
    await db.refresh(review)
    return review


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
