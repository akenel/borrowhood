"""Telegram notification service.

Sends short, actionable messages to users via BorrowHoodBot.
See RULES.md Section 11 for notification rules.
"""

import logging
from typing import Optional

import httpx

from src.config import settings

logger = logging.getLogger(__name__)

TELEGRAM_API_URL = f"https://api.telegram.org/bot{settings.telegram_bot_token}"


async def send_telegram_message(chat_id: str, text: str) -> bool:
    """Send a Telegram message to a user.

    Returns True if sent successfully, False otherwise.
    Does not raise -- notifications are best-effort.
    """
    if not settings.telegram_enabled or not settings.telegram_bot_token:
        logger.debug("Telegram notifications disabled, skipping message")
        return False

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{TELEGRAM_API_URL}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True,
                },
                timeout=10.0,
            )
            if resp.status_code == 200:
                return True
            logger.warning("Telegram API returned %s: %s", resp.status_code, resp.text)
            return False
    except Exception as e:
        logger.error("Failed to send Telegram message: %s", e)
        return False


async def notify_new_rental_request(
    owner_telegram: Optional[str],
    renter_name: str,
    item_name: str,
    app_url: str,
    rental_id: str,
) -> bool:
    """Notify item owner of a new rental request."""
    if not owner_telegram:
        return False

    text = (
        f"<b>New Rental Request</b>\n\n"
        f"{renter_name} wants to rent your <b>{item_name}</b>.\n\n"
        f'<a href="{app_url}/rentals/{rental_id}">View Request</a>'
    )
    return await send_telegram_message(owner_telegram, text)


async def notify_rental_approved(
    renter_telegram: Optional[str],
    owner_name: str,
    item_name: str,
    app_url: str,
    rental_id: str,
) -> bool:
    """Notify renter that their request was approved."""
    if not renter_telegram:
        return False

    text = (
        f"<b>Rental Approved!</b>\n\n"
        f"{owner_name} approved your request for <b>{item_name}</b>.\n\n"
        f'<a href="{app_url}/rentals/{rental_id}">View Details</a>'
    )
    return await send_telegram_message(renter_telegram, text)


async def notify_new_review(
    reviewee_telegram: Optional[str],
    reviewer_name: str,
    rating: int,
    item_name: str,
    app_url: str,
) -> bool:
    """Notify user they received a new review."""
    if not reviewee_telegram:
        return False

    stars = "★" * rating + "☆" * (5 - rating)
    text = (
        f"<b>New Review</b>\n\n"
        f"{reviewer_name} left you a {stars} review for <b>{item_name}</b>.\n\n"
        f'<a href="{app_url}/workshop/me">View Your Profile</a>'
    )
    return await send_telegram_message(reviewee_telegram, text)
