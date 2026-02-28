"""Telegram bot for account linking and notifications.

Lightweight long-polling bot using raw httpx -- no extra dependencies.
Runs as an asyncio task inside the FastAPI process.

Commands:
    /start {link_code} - Link Telegram to BorrowHood account
    /start             - Welcome message with instructions
    /status            - Show linked account info
    /unlink            - Clear telegram_chat_id
    /help              - Show available commands
"""

import asyncio
import logging
from datetime import datetime, timezone

import httpx
from sqlalchemy import select

from src.config import settings
from src.database import async_session
from src.models.telegram import BHTelegramLink
from src.models.user import BHUser

logger = logging.getLogger(__name__)

TELEGRAM_API = f"https://api.telegram.org/bot{settings.telegram_bot_token}"


class TelegramBot:
    """Long-polling Telegram bot for account linking."""

    def __init__(self):
        self._stop_event = asyncio.Event()
        self._offset = 0

    async def start(self):
        """Run the bot polling loop. Call as asyncio.create_task(bot.start())."""
        logger.info("Telegram bot polling started")
        self._stop_event.clear()

        async with httpx.AsyncClient(timeout=httpx.Timeout(35.0, connect=10.0)) as client:
            while not self._stop_event.is_set():
                try:
                    updates = await self._get_updates(client)
                    for update in updates:
                        self._offset = update["update_id"] + 1
                        await self._handle_update(client, update)
                except httpx.TimeoutException:
                    continue  # Normal for long polling
                except Exception as e:
                    logger.error("Telegram bot error: %s", e)
                    # Back off on errors to avoid hammering
                    try:
                        await asyncio.wait_for(self._stop_event.wait(), timeout=5.0)
                    except asyncio.TimeoutError:
                        pass

        logger.info("Telegram bot polling stopped")

    async def stop(self):
        """Signal the bot to stop gracefully."""
        self._stop_event.set()

    async def _get_updates(self, client: httpx.AsyncClient) -> list:
        """Fetch new updates using long polling."""
        resp = await client.get(
            f"{TELEGRAM_API}/getUpdates",
            params={"offset": self._offset, "timeout": 30, "allowed_updates": '["message"]'},
        )
        data = resp.json()
        if not data.get("ok"):
            logger.warning("getUpdates failed: %s", data)
            return []
        return data.get("result", [])

    async def _handle_update(self, client: httpx.AsyncClient, update: dict):
        """Route an incoming update to the right handler."""
        message = update.get("message")
        if not message or not message.get("text"):
            return

        text = message["text"].strip()
        chat_id = str(message["chat"]["id"])

        if text.startswith("/start"):
            parts = text.split(maxsplit=1)
            link_code = parts[1].strip() if len(parts) > 1 else None
            await self._handle_start(client, chat_id, link_code)
        elif text == "/status":
            await self._handle_status(client, chat_id)
        elif text == "/unlink":
            await self._handle_unlink(client, chat_id)
        elif text == "/help":
            await self._handle_help(client, chat_id)
        else:
            await self._send(client, chat_id, "Unknown command. Type /help to see available commands.")

    async def _handle_start(self, client: httpx.AsyncClient, chat_id: str, link_code: str | None):
        """Handle /start with optional link code."""
        if not link_code:
            await self._send(
                client,
                chat_id,
                "<b>Welcome to BorrowHood!</b>\n\n"
                "To link your account, use the link button on your BorrowHood dashboard.\n\n"
                "Commands:\n"
                "/status - Check link status\n"
                "/unlink - Unlink your account\n"
                "/help - Show help",
            )
            return

        async with async_session() as db:
            # Look up the link code
            result = await db.execute(
                select(BHTelegramLink).where(BHTelegramLink.link_code == link_code)
            )
            link = result.scalars().first()

            if not link:
                await self._send(client, chat_id, "Invalid or expired link code. Please generate a new link from your dashboard.")
                return

            if link.expires_at < datetime.now(timezone.utc):
                await db.delete(link)
                await db.commit()
                await self._send(client, chat_id, "This link code has expired. Please generate a new link from your dashboard.")
                return

            # Link the account
            user = await db.get(BHUser, link.user_id)
            if not user:
                await self._send(client, chat_id, "User account not found. Please contact support.")
                return

            user.telegram_chat_id = chat_id
            await db.delete(link)
            await db.commit()

            await self._send(
                client,
                chat_id,
                f"Linked! You'll now receive BorrowHood notifications here.\n\n"
                f"Account: <b>{user.display_name}</b>\n\n"
                "Use /unlink to disconnect, or /status to check.",
            )
            logger.info("Telegram linked: user=%s chat_id=%s", user.display_name, chat_id)

    async def _handle_status(self, client: httpx.AsyncClient, chat_id: str):
        """Show linked account info."""
        async with async_session() as db:
            result = await db.execute(
                select(BHUser).where(BHUser.telegram_chat_id == chat_id)
            )
            user = result.scalars().first()

            if user:
                status = "on" if user.notify_telegram else "off"
                await self._send(
                    client,
                    chat_id,
                    f"<b>Linked Account</b>\n\n"
                    f"Name: {user.display_name}\n"
                    f"Notifications: {status}\n\n"
                    "Use /unlink to disconnect.",
                )
            else:
                await self._send(
                    client,
                    chat_id,
                    "No BorrowHood account linked to this Telegram.\n\n"
                    "Use the link button on your BorrowHood dashboard to connect.",
                )

    async def _handle_unlink(self, client: httpx.AsyncClient, chat_id: str):
        """Clear telegram_chat_id for this chat."""
        async with async_session() as db:
            result = await db.execute(
                select(BHUser).where(BHUser.telegram_chat_id == chat_id)
            )
            user = result.scalars().first()

            if user:
                user.telegram_chat_id = None
                await db.commit()
                await self._send(client, chat_id, "Unlinked. You will no longer receive BorrowHood notifications here.")
                logger.info("Telegram unlinked: user=%s", user.display_name)
            else:
                await self._send(client, chat_id, "No account linked to this Telegram.")

    async def _handle_help(self, client: httpx.AsyncClient, chat_id: str):
        """Show available commands."""
        await self._send(
            client,
            chat_id,
            "<b>BorrowHood Bot Commands</b>\n\n"
            "/start - Welcome / link account\n"
            "/status - Check linked account\n"
            "/unlink - Unlink your account\n"
            "/help - Show this message",
        )

    async def _send(self, client: httpx.AsyncClient, chat_id: str, text: str):
        """Send a message to a chat."""
        try:
            await client.post(
                f"{TELEGRAM_API}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True,
                },
            )
        except Exception as e:
            logger.error("Failed to send Telegram message to %s: %s", chat_id, e)


# Module-level singleton
bot = TelegramBot()
