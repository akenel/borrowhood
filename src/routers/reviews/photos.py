"""Upload photo evidence attached to a review."""

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



