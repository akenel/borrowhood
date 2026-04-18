"""Owner's response to a review (one-time, Airbnb pattern)."""

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


