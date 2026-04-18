"""Make/accept/counter/decline offer messages."""

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
from src.schemas.message import (
    CounterOffer,
    MessageCreate,
    MessageOut,
    MessageSummary,
    MessageUpdate,
    OfferCreate,
    ThreadSummary,
)

router = APIRouter()

@router.post("/offers", response_model=MessageOut, status_code=201)
async def make_offer(
    data: OfferCreate,
    token: dict = Depends(require_auth),
    _throttle: dict = Depends(user_throttle("make_offer", 20, 3600)),
    db: AsyncSession = Depends(get_db),
):
    """Make a price offer on a listing. Creates an offer message in the thread."""
    user = await get_user(db, token)

    listing = await db.get(BHListing, data.listing_id)
    if not listing or listing.status.value not in ("active", "listed"):
        raise HTTPException(status_code=404, detail="Listing not found or not active")

    item = await db.get(BHItem, listing.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if item.owner_id == user.id:
        raise HTTPException(status_code=400, detail="Cannot make an offer on your own listing")

    # Check for existing pending offer from this user on this listing
    existing = await db.execute(
        select(BHMessage)
        .where(BHMessage.sender_id == user.id)
        .where(BHMessage.listing_id == data.listing_id)
        .where(BHMessage.message_type.in_(["offer", "counter"]))
        .where(BHMessage.offer_status == "pending")
        .where(BHMessage.deleted_at.is_(None))
    )
    if existing.scalars().first():
        raise HTTPException(status_code=409, detail="You already have a pending offer on this listing")

    from datetime import timedelta
    body = data.message or f"I'd like to offer €{data.offered_price:.2f} for this item."
    expires = datetime.now(timezone.utc) + timedelta(hours=48)

    message = BHMessage(
        sender_id=user.id,
        recipient_id=item.owner_id,
        listing_id=data.listing_id,
        body=body,
        message_type="offer",
        offered_price=data.offered_price,
        offer_status="pending",
        offer_round=1,
        expires_at=expires,
    )
    db.add(message)
    await db.flush()

    from src.models.notification import NotificationType
    from src.services.notify import create_notification
    await create_notification(
        db=db,
        user_id=item.owner_id,
        notification_type=NotificationType.MESSAGE_RECEIVED,
        title=f"New offer from {user.display_name}",
        body=f"€{data.offered_price:.2f} on {item.name}",
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
        message_type=message.message_type,
        listing_id=message.listing_id,
        offered_price=float(message.offered_price) if message.offered_price else None,
        offer_status=message.offer_status,
        offer_round=message.offer_round,
        expires_at=message.expires_at,
        created_at=message.created_at,
        sender_name=user.display_name,
        sender_avatar=user.avatar_url,
    )


@router.post("/offers/{message_id}/accept")
async def accept_offer(
    message_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Accept an offer. Only the listing owner can accept."""
    user = await get_user(db, token)

    msg = await db.get(BHMessage, message_id)
    if not msg or msg.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Offer not found")
    if msg.message_type not in ("offer", "counter"):
        raise HTTPException(status_code=400, detail="This message is not an offer")
    if msg.offer_status != "pending":
        raise HTTPException(status_code=400, detail=f"Offer already {msg.offer_status}")
    if msg.recipient_id != user.id:
        raise HTTPException(status_code=403, detail="Only the recipient can accept an offer")

    # Check expiry
    if msg.expires_at and msg.expires_at < datetime.now(timezone.utc):
        msg.offer_status = "expired"
        await db.commit()
        raise HTTPException(status_code=410, detail="Offer has expired")

    msg.offer_status = "accepted"

    # Send acceptance message
    accept_msg = BHMessage(
        sender_id=user.id,
        recipient_id=msg.sender_id,
        listing_id=msg.listing_id,
        body=f"Offer accepted! €{msg.offered_price:.2f} -- let's make it happen.",
        message_type="accept",
        offered_price=msg.offered_price,
        offer_status="accepted",
        offer_round=msg.offer_round,
    )
    db.add(accept_msg)

    from src.models.notification import NotificationType
    from src.services.notify import create_notification
    await create_notification(
        db=db,
        user_id=msg.sender_id,
        notification_type=NotificationType.MESSAGE_RECEIVED,
        title="Your offer was accepted!",
        body=f"€{msg.offered_price:.2f} accepted -- check your messages",
        link="/messages",
        entity_type="message",
        entity_id=msg.id,
    )

    await db.commit()
    return {"status": "accepted", "price": float(msg.offered_price)}


@router.post("/offers/{message_id}/counter", response_model=MessageOut)
async def counter_offer(
    message_id: UUID,
    data: CounterOffer,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Counter an offer with a new price. Max 3 rounds."""
    user = await get_user(db, token)

    msg = await db.get(BHMessage, message_id)
    if not msg or msg.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Offer not found")
    if msg.message_type not in ("offer", "counter"):
        raise HTTPException(status_code=400, detail="This message is not an offer")
    if msg.offer_status != "pending":
        raise HTTPException(status_code=400, detail=f"Offer already {msg.offer_status}")
    if msg.recipient_id != user.id:
        raise HTTPException(status_code=403, detail="Only the recipient can counter an offer")

    current_round = msg.offer_round or 1
    if current_round >= 3:
        raise HTTPException(status_code=400, detail="Maximum 3 negotiation rounds reached. Accept, decline, or walk away.")

    # Mark original as countered
    msg.offer_status = "countered"

    from datetime import timedelta
    body = data.message or f"How about €{data.offered_price:.2f}?"
    expires = datetime.now(timezone.utc) + timedelta(hours=48)

    counter_msg = BHMessage(
        sender_id=user.id,
        recipient_id=msg.sender_id,
        listing_id=msg.listing_id,
        body=body,
        message_type="counter",
        offered_price=data.offered_price,
        offer_status="pending",
        offer_round=current_round + 1,
        expires_at=expires,
    )
    db.add(counter_msg)
    await db.flush()

    from src.models.notification import NotificationType
    from src.services.notify import create_notification
    await create_notification(
        db=db,
        user_id=msg.sender_id,
        notification_type=NotificationType.MESSAGE_RECEIVED,
        title=f"Counter-offer from {user.display_name}",
        body=f"€{data.offered_price:.2f} -- round {current_round + 1} of 3",
        link="/messages",
        entity_type="message",
        entity_id=counter_msg.id,
    )

    await db.commit()
    await db.refresh(counter_msg)

    return MessageOut(
        id=counter_msg.id,
        sender_id=counter_msg.sender_id,
        recipient_id=counter_msg.recipient_id,
        body=counter_msg.body,
        message_type=counter_msg.message_type,
        listing_id=counter_msg.listing_id,
        offered_price=float(counter_msg.offered_price) if counter_msg.offered_price else None,
        offer_status=counter_msg.offer_status,
        offer_round=counter_msg.offer_round,
        expires_at=counter_msg.expires_at,
        created_at=counter_msg.created_at,
        sender_name=user.display_name,
        sender_avatar=user.avatar_url,
    )


@router.post("/offers/{message_id}/decline")
async def decline_offer(
    message_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Decline an offer."""
    user = await get_user(db, token)

    msg = await db.get(BHMessage, message_id)
    if not msg or msg.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Offer not found")
    if msg.message_type not in ("offer", "counter"):
        raise HTTPException(status_code=400, detail="This message is not an offer")
    if msg.offer_status != "pending":
        raise HTTPException(status_code=400, detail=f"Offer already {msg.offer_status}")
    if msg.recipient_id != user.id:
        raise HTTPException(status_code=403, detail="Only the recipient can decline an offer")

    msg.offer_status = "declined"

    decline_msg = BHMessage(
        sender_id=user.id,
        recipient_id=msg.sender_id,
        listing_id=msg.listing_id,
        body="Thanks for the offer, but I'll pass this time.",
        message_type="decline",
        offered_price=msg.offered_price,
        offer_status="declined",
        offer_round=msg.offer_round,
    )
    db.add(decline_msg)

    from src.models.notification import NotificationType
    from src.services.notify import create_notification
    await create_notification(
        db=db,
        user_id=msg.sender_id,
        notification_type=NotificationType.MESSAGE_RECEIVED,
        title="Offer declined",
        body=f"Your €{msg.offered_price:.2f} offer was declined",
        link="/messages",
        entity_type="message",
        entity_id=msg.id,
    )

    await db.commit()
    return {"status": "declined"}


