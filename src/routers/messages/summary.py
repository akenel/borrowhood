"""Message summary + thread listing."""

from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies import get_user, require_auth, user_throttle
from src.models.item import BHItem
from src.models.listing import BHListing
from src.models.message import BHMessage
from src.models.rental import BHRental
from src.models.user import BHUser
from src.schemas.message import MessageCreate, MessageOut, MessageSummary, MessageUpdate, ThreadSummary

router = APIRouter()

@router.get("/summary", response_model=MessageSummary)
async def message_summary(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Return unread message count for nav badge."""
    user = await get_user(db, token)

    result = await db.execute(
        select(func.count())
        .select_from(BHMessage)
        .where(BHMessage.recipient_id == user.id)
        .where(BHMessage.read_at.is_(None))
        .where(BHMessage.deleted_at.is_(None))
    )
    unread = result.scalar() or 0
    return MessageSummary(unread=unread)


@router.get("/threads", response_model=List[ThreadSummary])
async def list_threads(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List conversation threads (inbox view).

    Returns one entry per conversation partner with the latest message
    and unread count.
    """
    user = await get_user(db, token)

    # Determine the "other" user in each message
    other_id = case(
        (BHMessage.sender_id == user.id, BHMessage.recipient_id),
        else_=BHMessage.sender_id,
    )

    # Subquery: latest message created_at per conversation partner
    latest_sub = (
        select(
            other_id.label("other_id"),
            func.max(BHMessage.created_at).label("max_created"),
        )
        .where(
            or_(
                BHMessage.sender_id == user.id,
                BHMessage.recipient_id == user.id,
            )
        )
        .where(BHMessage.deleted_at.is_(None))
        .group_by(other_id)
        .subquery()
    )

    # Second subquery: get the actual message ID for each latest message
    # Using DISTINCT ON to get exactly one row per conversation partner
    other_id_col = case(
        (BHMessage.sender_id == user.id, BHMessage.recipient_id),
        else_=BHMessage.sender_id,
    )

    latest_msg_sub = (
        select(
            func.distinct(latest_sub.c.other_id).label("other_id"),
            BHMessage.id.label("msg_id"),
        )
        .join(
            latest_sub,
            and_(
                other_id_col == latest_sub.c.other_id,
                BHMessage.created_at >= latest_sub.c.max_created,
            ),
        )
        .where(BHMessage.deleted_at.is_(None))
        .where(
            or_(
                BHMessage.sender_id == user.id,
                BHMessage.recipient_id == user.id,
            )
        )
        .subquery()
    )

    query = (
        select(
            BHMessage,
            BHUser.id.label("other_user_id"),
            BHUser.display_name.label("other_user_name"),
            BHUser.avatar_url.label("other_user_avatar"),
        )
        .join(latest_msg_sub, BHMessage.id == latest_msg_sub.c.msg_id)
        .join(BHUser, BHUser.id == latest_msg_sub.c.other_id)
        .where(BHMessage.deleted_at.is_(None))
        .order_by(BHMessage.created_at.desc())
    )

    result = await db.execute(query)
    rows = result.all()

    threads = []
    for row in rows:
        msg = row[0]
        other_user_id = row[1]
        other_user_name = row[2]
        other_user_avatar = row[3]

        # Count unread from this partner
        unread_result = await db.execute(
            select(func.count())
            .select_from(BHMessage)
            .where(BHMessage.sender_id == other_user_id)
            .where(BHMessage.recipient_id == user.id)
            .where(BHMessage.read_at.is_(None))
            .where(BHMessage.deleted_at.is_(None))
        )
        unread_count = unread_result.scalar() or 0

        threads.append(
            ThreadSummary(
                other_user_id=other_user_id,
                other_user_name=other_user_name,
                other_user_avatar=other_user_avatar,
                last_message=msg.body[:200],
                last_message_at=msg.created_at,
                unread_count=unread_count,
                listing_id=msg.listing_id,
                rental_id=msg.rental_id,
            )
        )

    return threads




