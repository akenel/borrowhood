"""Review list + summary (public reads)."""

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




