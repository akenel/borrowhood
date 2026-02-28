"""Telegram account linking API.

Allows users to link/unlink their Telegram account and toggle notifications.
The actual linking happens via the Telegram bot (deep-link flow).
"""

import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import get_db
from src.dependencies import require_auth
from src.models.telegram import BHTelegramLink
from src.models.user import BHUser

router = APIRouter(prefix="/api/v1/telegram", tags=["telegram"])


async def _get_user(db: AsyncSession, keycloak_id: str) -> BHUser:
    result = await db.execute(
        select(BHUser).where(BHUser.keycloak_id == keycloak_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=403, detail="User not provisioned")
    return user


# --- Schemas ---

class TelegramLinkResponse(BaseModel):
    url: str
    expires_in_seconds: int


class TelegramStatusResponse(BaseModel):
    linked: bool
    notify_telegram: bool
    telegram_username: str | None = None


class TelegramToggleRequest(BaseModel):
    enabled: bool


class TelegramToggleResponse(BaseModel):
    notify_telegram: bool


# --- Endpoints ---

@router.post("/link", response_model=TelegramLinkResponse)
async def generate_link(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Generate a Telegram deep link URL for account linking.

    Creates a temporary link code (10 min expiry) and returns a t.me URL.
    If a pending link already exists, it is replaced.
    """
    if not settings.telegram_enabled or not settings.telegram_bot_name:
        raise HTTPException(status_code=503, detail="Telegram linking not available")

    user = await _get_user(db, token["sub"])

    # Delete any existing pending link for this user
    result = await db.execute(
        select(BHTelegramLink).where(BHTelegramLink.user_id == user.id)
    )
    existing = result.scalars().first()
    if existing:
        await db.delete(existing)
        await db.flush()

    # Create new link code
    link_code = secrets.token_urlsafe(16)  # ~22 chars, URL-safe
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    link = BHTelegramLink(
        user_id=user.id,
        link_code=link_code,
        expires_at=expires_at,
    )
    db.add(link)
    await db.commit()

    url = f"https://t.me/{settings.telegram_bot_name}?start={link_code}"
    return TelegramLinkResponse(url=url, expires_in_seconds=600)


@router.get("/status", response_model=TelegramStatusResponse)
async def get_status(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Check if the user's Telegram account is linked."""
    user = await _get_user(db, token["sub"])
    return TelegramStatusResponse(
        linked=bool(user.telegram_chat_id),
        notify_telegram=user.notify_telegram,
        telegram_username=user.telegram_username,
    )


@router.delete("/link")
async def unlink(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Unlink Telegram account."""
    user = await _get_user(db, token["sub"])

    if not user.telegram_chat_id:
        raise HTTPException(status_code=400, detail="Telegram not linked")

    user.telegram_chat_id = None

    # Also clean up any pending link codes
    result = await db.execute(
        select(BHTelegramLink).where(BHTelegramLink.user_id == user.id)
    )
    pending = result.scalars().first()
    if pending:
        await db.delete(pending)

    await db.commit()
    return {"status": "unlinked"}


@router.patch("/toggle", response_model=TelegramToggleResponse)
async def toggle_notifications(
    data: TelegramToggleRequest,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Toggle Telegram notifications on or off."""
    user = await _get_user(db, token["sub"])
    user.notify_telegram = data.enabled
    await db.commit()
    return TelegramToggleResponse(notify_telegram=user.notify_telegram)
