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
from src.models.item import BHItem
from src.models.listing import BHListing
from src.models.message import BHMessage
from src.models.rental import BHRental
from src.models.user import BHUser
from src.schemas.message import MessageCreate, MessageOut, MessageSummary, MessageUpdate, ThreadSummary

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
