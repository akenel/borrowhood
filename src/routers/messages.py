"""In-app messaging API.

Threaded conversations between users, optionally tied to a listing or rental.
"""

from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies import get_user, require_auth, user_throttle
from src.models.message import BHMessage
from src.models.user import BHUser
from src.schemas.message import MessageCreate, MessageOut, MessageSummary, ThreadSummary

router = APIRouter(prefix="/api/v1/messages", tags=["messages"])


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

    # Subquery: latest message id per conversation partner
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

    # Join back to get the actual message row + other user info
    other_id_col = case(
        (BHMessage.sender_id == user.id, BHMessage.recipient_id),
        else_=BHMessage.sender_id,
    )

    query = (
        select(
            BHMessage,
            BHUser.id.label("other_user_id"),
            BHUser.display_name.label("other_user_name"),
            BHUser.avatar_url.label("other_user_avatar"),
        )
        .join(
            latest_sub,
            and_(
                other_id_col == latest_sub.c.other_id,
                BHMessage.created_at == latest_sub.c.max_created,
            ),
        )
        .join(BHUser, BHUser.id == latest_sub.c.other_id)
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
            )
        )

    return threads


@router.get("/thread/{user_id}", response_model=List[MessageOut])
async def get_thread(
    user_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Get all messages with a specific user. Marks unread ones as read."""
    me = await get_user(db, token)

    if user_id == me.id:
        raise HTTPException(status_code=400, detail="Cannot message yourself")

    # Fetch all messages between the two users
    result = await db.execute(
        select(BHMessage)
        .where(
            or_(
                and_(BHMessage.sender_id == me.id, BHMessage.recipient_id == user_id),
                and_(BHMessage.sender_id == user_id, BHMessage.recipient_id == me.id),
            )
        )
        .where(BHMessage.deleted_at.is_(None))
        .order_by(BHMessage.created_at.asc())
    )
    messages = result.scalars().all()

    # Mark unread messages FROM the other user as read
    now = datetime.now(timezone.utc)
    for msg in messages:
        if msg.sender_id == user_id and msg.read_at is None:
            msg.read_at = now

    await db.commit()

    # Load sender info for response
    sender_cache: dict[UUID, BHUser] = {}
    out = []
    for msg in messages:
        if msg.sender_id not in sender_cache:
            sender = await db.get(BHUser, msg.sender_id)
            sender_cache[msg.sender_id] = sender

        sender = sender_cache[msg.sender_id]
        out.append(
            MessageOut(
                id=msg.id,
                sender_id=msg.sender_id,
                recipient_id=msg.recipient_id,
                body=msg.body,
                listing_id=msg.listing_id,
                rental_id=msg.rental_id,
                read_at=msg.read_at,
                created_at=msg.created_at,
                sender_name=sender.display_name if sender else None,
                sender_avatar=sender.avatar_url if sender else None,
            )
        )

    return out


@router.post("", response_model=MessageOut, status_code=201)
async def send_message(
    data: MessageCreate,
    token: dict = Depends(require_auth),
    _throttle: dict = Depends(user_throttle("send_message", 50, 3600)),
    db: AsyncSession = Depends(get_db),
):
    """Send a message to another user. Max 50/hour per user."""
    user = await get_user(db, token)

    if data.recipient_id == user.id:
        raise HTTPException(status_code=400, detail="Cannot message yourself")

    # Verify recipient exists
    recipient = await db.get(BHUser, data.recipient_id)
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")

    message = BHMessage(
        sender_id=user.id,
        recipient_id=data.recipient_id,
        body=data.body,
        listing_id=data.listing_id,
        rental_id=data.rental_id,
    )
    db.add(message)
    await db.flush()

    # Notify recipient
    from src.models.notification import NotificationType
    from src.services.notify import create_notification

    preview = data.body[:100] + ("..." if len(data.body) > 100 else "")
    await create_notification(
        db=db,
        user_id=data.recipient_id,
        notification_type=NotificationType.MESSAGE_RECEIVED,
        title=f"New message from {user.display_name}",
        body=preview,
        link="/messages",
        entity_type="message",
        entity_id=message.id,
    )

    await db.commit()
    await db.refresh(message)

    return MessageOut(
        id=message.id,
        sender_id=message.sender_id,
        recipient_id=message.recipient_id,
        body=message.body,
        listing_id=message.listing_id,
        rental_id=message.rental_id,
        read_at=message.read_at,
        created_at=message.created_at,
        sender_name=user.display_name,
        sender_avatar=user.avatar_url,
    )
