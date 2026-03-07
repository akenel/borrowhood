"""Unified notification service.

Creates in-app notifications and optionally forwards to Telegram.
All notification creation goes through this service -- single source of truth.
"""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.notification import BHNotification, NotificationType
from src.services.notification import send_telegram_message

logger = logging.getLogger(__name__)


async def create_notification(
    db: AsyncSession,
    user_id: UUID,
    notification_type: NotificationType,
    title: str,
    body: Optional[str] = None,
    link: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[UUID] = None,
    telegram_chat_id: Optional[str] = None,
) -> Optional[BHNotification]:
    """Create an in-app notification and optionally send to Telegram.

    This is the single entry point for all notifications in the system.
    """
    # Check per-type preference (if user muted this type, skip entirely)
    from sqlalchemy import select
    from src.models.notification_pref import BHNotificationPref
    pref = await db.scalar(
        select(BHNotificationPref.enabled)
        .where(BHNotificationPref.user_id == user_id)
        .where(BHNotificationPref.notification_type == notification_type.value)
    )
    if pref is False:
        logger.debug("Notification type %s muted for user %s", notification_type.value, user_id)
        return None

    notification = BHNotification(
        user_id=user_id,
        notification_type=notification_type,
        title=title,
        body=body,
        link=link,
        entity_type=entity_type,
        entity_id=entity_id,
    )
    db.add(notification)

    # Auto-fetch telegram_chat_id from user record if not explicitly provided
    if not telegram_chat_id:
        from src.models.user import BHUser
        user = await db.get(BHUser, user_id)
        if user and user.notify_telegram and user.telegram_chat_id:
            telegram_chat_id = user.telegram_chat_id

    # Best-effort Telegram forwarding
    if telegram_chat_id:
        telegram_text = f"<b>{title}</b>"
        if body:
            telegram_text += f"\n\n{body}"
        if link:
            telegram_text += f'\n\n<a href="{link}">View</a>'

        sent = await send_telegram_message(telegram_chat_id, telegram_text)
        notification.telegram_sent = sent

    await db.flush()
    return notification


async def notify_rental_event(
    db: AsyncSession,
    user_id: UUID,
    notification_type: NotificationType,
    item_name: str,
    other_party_name: str,
    rental_id: UUID,
    listing_type: Optional[str] = None,
    telegram_chat_id: Optional[str] = None,
):
    """Convenience wrapper for rental/purchase/booking notifications."""
    # Determine action verb based on listing type
    lt = listing_type.lower() if listing_type else "rent"
    if lt == "sell":
        verb_request = "buy"
        verb_past = "Purchase"
    elif lt in ("service", "training"):
        verb_request = "book"
        verb_past = "Booking"
    elif lt == "giveaway":
        verb_request = "claim"
        verb_past = "Claim"
    elif lt == "offer":
        verb_request = "claim"
        verb_past = "Claim"
    else:
        verb_request = "rent"
        verb_past = "Rental"

    titles = {
        NotificationType.RENTAL_REQUEST: f"{other_party_name} wants to {verb_request} your {item_name}",
        NotificationType.RENTAL_APPROVED: f"Your {verb_past.lower()} request for {item_name} was approved",
        NotificationType.RENTAL_DECLINED: f"Your {verb_past.lower()} request for {item_name} was declined",
        NotificationType.RENTAL_PICKED_UP: f"{item_name} has been picked up",
        NotificationType.RENTAL_RETURNED: f"{item_name} has been returned",
        NotificationType.RENTAL_COMPLETED: f"{verb_past} of {item_name} is complete",
        NotificationType.RENTAL_CANCELLED: f"{verb_past} of {item_name} was cancelled",
    }

    title = titles.get(notification_type, f"{verb_past} update for {item_name}")

    return await create_notification(
        db=db,
        user_id=user_id,
        notification_type=notification_type,
        title=title,
        link=f"/dashboard",
        entity_type="rental",
        entity_id=rental_id,
        telegram_chat_id=telegram_chat_id,
    )
