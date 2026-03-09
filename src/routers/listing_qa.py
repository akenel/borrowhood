"""Listing Q&A API.

Public questions and answers on listings.
Buyers ask, sellers answer. Everyone can see.
"""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.dependencies import get_user, require_auth, user_throttle
from src.models.listing import BHListing
from src.models.listing_qa import BHListingQA
from src.models.item import BHItem
from src.schemas.listing_qa import QACreate, QAAnswer, QAOut

router = APIRouter(prefix="/api/v1/listing-qa", tags=["listing-qa"])


def _qa_to_out(qa: BHListingQA) -> QAOut:
    """Convert a BHListingQA with loaded relationships to QAOut."""
    return QAOut(
        id=qa.id,
        listing_id=qa.listing_id,
        asker_id=qa.asker_id,
        question=qa.question,
        answer=qa.answer,
        answered_by_id=qa.answered_by_id,
        answered_at=qa.answered_at,
        created_at=qa.created_at,
        asker_name=qa.asker.display_name if qa.asker else None,
        asker_avatar=qa.asker.avatar_url if qa.asker else None,
        answerer_name=qa.answered_by.display_name if qa.answered_by else None,
    )


@router.get("", response_model=List[QAOut])
async def list_qa(
    listing_id: UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List Q&A for a listing. Public, no auth required."""
    query = (
        select(BHListingQA)
        .where(BHListingQA.listing_id == listing_id)
        .where(BHListingQA.deleted_at.is_(None))
        .options(
            selectinload(BHListingQA.asker),
            selectinload(BHListingQA.answered_by),
        )
        .order_by(BHListingQA.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(query)
    rows = result.scalars().all()
    return [_qa_to_out(qa) for qa in rows]


@router.post("", response_model=QAOut, status_code=201)
async def ask_question(
    data: QACreate,
    token: dict = Depends(require_auth),
    _throttle: dict = Depends(user_throttle("ask_question", 20, 3600)),
    db: AsyncSession = Depends(get_db),
):
    """Ask a question on a listing. Max 20/hour per user."""
    user = await get_user(db, token)

    # Verify listing exists
    listing = await db.get(BHListing, data.listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    qa = BHListingQA(
        listing_id=data.listing_id,
        asker_id=user.id,
        question=data.question,
    )
    db.add(qa)

    # Notify the listing owner
    from src.models.notification import NotificationType
    from src.services.notify import create_notification

    # Load item to get owner
    item = await db.get(BHItem, listing.item_id)
    if item:
        await create_notification(
            db=db,
            user_id=item.owner_id,
            notification_type=NotificationType.SYSTEM,
            title=f"{user.display_name} asked a question on your listing",
            body=data.question[:200],
            link=f"/listings/{data.listing_id}",
            entity_type="listing_qa",
        )

    await db.commit()

    # Reload with relationships for response
    result = await db.execute(
        select(BHListingQA)
        .where(BHListingQA.id == qa.id)
        .options(
            selectinload(BHListingQA.asker),
            selectinload(BHListingQA.answered_by),
        )
    )
    qa = result.scalars().first()
    return _qa_to_out(qa)


@router.patch("/{qa_id}/answer", response_model=QAOut)
async def answer_question(
    qa_id: UUID,
    data: QAAnswer,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Answer a question. Must be the listing owner."""
    user = await get_user(db, token)

    # Load QA entry
    result = await db.execute(
        select(BHListingQA)
        .where(BHListingQA.id == qa_id)
        .where(BHListingQA.deleted_at.is_(None))
        .options(
            selectinload(BHListingQA.asker),
        )
    )
    qa = result.scalars().first()
    if not qa:
        raise HTTPException(status_code=404, detail="Question not found")

    # Verify current user owns the listing's item
    listing_result = await db.execute(
        select(BHListing)
        .where(BHListing.id == qa.listing_id)
        .options(selectinload(BHListing.item))
    )
    listing = listing_result.scalars().first()
    if not listing or not listing.item:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.item.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Only the listing owner can answer questions")

    # Set the answer
    qa.answer = data.answer
    qa.answered_by_id = user.id
    qa.answered_at = datetime.now(timezone.utc)

    # Notify the asker
    from src.models.notification import NotificationType
    from src.services.notify import create_notification

    await create_notification(
        db=db,
        user_id=qa.asker_id,
        notification_type=NotificationType.SYSTEM,
        title=f"{user.display_name} answered your question",
        body=data.answer[:200],
        link=f"/listings/{qa.listing_id}",
        entity_type="listing_qa",
        entity_id=qa.id,
    )

    await db.commit()

    # Reload with relationships for response
    result = await db.execute(
        select(BHListingQA)
        .where(BHListingQA.id == qa.id)
        .options(
            selectinload(BHListingQA.asker),
            selectinload(BHListingQA.answered_by),
        )
    )
    qa = result.scalars().first()
    return _qa_to_out(qa)
