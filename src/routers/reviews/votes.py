"""Helpful / not-helpful voting on reviews."""

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


