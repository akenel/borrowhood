"""Per-thread reads (by counterpart user or by rental/order)."""

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
                edited_at=msg.edited_at,
                created_at=msg.created_at,
                sender_name=sender.display_name if sender else None,
                sender_avatar=sender.avatar_url if sender else None,
            )
        )

    return out


@router.get("/order/{rental_id}", response_model=List[MessageOut])
async def get_order_thread(
    rental_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Get all messages for a specific order/transaction.

    Auth: Must be the renter or the item owner.
    """
    me = await get_user(db, token)

    # Verify rental exists and user is authorized
    rental = await db.get(BHRental, rental_id)
    if not rental:
        raise HTTPException(status_code=404, detail="Order not found")

    # Get the item owner via listing -> item
    listing = await db.get(BHListing, rental.listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    item = await db.get(BHItem, listing.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if me.id != rental.renter_id and me.id != item.owner_id:
        raise HTTPException(status_code=403, detail="Not authorized for this order")

    # Fetch messages for this rental
    result = await db.execute(
        select(BHMessage)
        .where(BHMessage.rental_id == rental_id)
        .where(BHMessage.deleted_at.is_(None))
        .order_by(BHMessage.created_at.asc())
    )
    messages = result.scalars().all()

    # Mark unread messages as read
    now = datetime.now(timezone.utc)
    for msg in messages:
        if msg.recipient_id == me.id and msg.read_at is None:
            msg.read_at = now
    await db.commit()

    # Build response
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
                edited_at=msg.edited_at,
                created_at=msg.created_at,
                sender_name=sender.display_name if sender else None,
                sender_avatar=sender.avatar_url if sender else None,
            )
        )

    return out




