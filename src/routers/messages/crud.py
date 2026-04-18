"""Send, edit, delete a message."""

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

@router.post("/", response_model=MessageOut, status_code=201)
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

    # If rental_id is provided, verify sender is renter or item owner
    if data.rental_id:
        rental = await db.get(BHRental, data.rental_id)
        if not rental:
            raise HTTPException(status_code=404, detail="Order not found")
        listing = await db.get(BHListing, rental.listing_id)
        item = await db.get(BHItem, listing.item_id) if listing else None
        owner_id = item.owner_id if item else None
        if user.id != rental.renter_id and user.id != owner_id:
            raise HTTPException(status_code=403, detail="Not authorized for this order")

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
        edited_at=message.edited_at,
        created_at=message.created_at,
        sender_name=user.display_name,
        sender_avatar=user.avatar_url,
    )


@router.patch("/{message_id}", response_model=MessageOut)
async def edit_message(
    message_id: UUID,
    data: MessageUpdate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Edit a message body. Only the sender can edit, and only within 15 minutes."""
    user = await get_user(db, token)

    msg = await db.get(BHMessage, message_id)
    if not msg or msg.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Message not found")

    if msg.sender_id != user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own messages")

    # 15-minute edit window
    now = datetime.now(timezone.utc)
    age_seconds = (now - msg.created_at).total_seconds()
    if age_seconds > 900:
        raise HTTPException(status_code=403, detail="Messages can only be edited within 15 minutes")

    msg.body = data.body
    msg.edited_at = now
    await db.commit()
    await db.refresh(msg)

    return MessageOut(
        id=msg.id,
        sender_id=msg.sender_id,
        recipient_id=msg.recipient_id,
        body=msg.body,
        listing_id=msg.listing_id,
        rental_id=msg.rental_id,
        read_at=msg.read_at,
        edited_at=msg.edited_at,
        created_at=msg.created_at,
        sender_name=user.display_name,
        sender_avatar=user.avatar_url,
    )


@router.delete("/{message_id}", status_code=200)
async def delete_message(
    message_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a message. Only the sender can delete."""
    user = await get_user(db, token)

    msg = await db.get(BHMessage, message_id)
    if not msg or msg.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Message not found")

    if msg.sender_id != user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own messages")

    msg.deleted_at = datetime.now(timezone.utc)
    await db.commit()

    return {"status": "deleted", "id": str(message_id)}


# ═══════════════════════════════════════════════════════════════
# OFFERS -- structured price negotiation via messages
# Max 3 rounds, 48-hour expiry, accept creates order
# ═══════════════════════════════════════════════════════════════

from src.schemas.message import CounterOffer, OfferCreate



