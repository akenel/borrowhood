"""Telegram notification service.

Sends short, actionable messages to users via BorrowHoodBot.
See RULES.md Section 11 for notification rules.
"""

import logging

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


