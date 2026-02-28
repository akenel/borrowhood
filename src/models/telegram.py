"""Telegram account linking model.

Temporary link codes for the deep-link flow that connects
a BorrowHood user account to their Telegram chat ID.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, BHBase


class BHTelegramLink(BHBase, Base):
    """Temporary link codes for Telegram account linking.

    Flow:
    1. User clicks "Link Telegram" on dashboard
    2. Backend creates BHTelegramLink with random code + 10min expiry
    3. User clicks deep link: t.me/BotName?start=LINKCODE
    4. Bot receives /start LINKCODE, looks up this record
    5. Bot sets BHUser.telegram_chat_id, deletes this record
    """

    __tablename__ = "bh_telegram_link"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), unique=True, nullable=False, index=True
    )
    link_code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped["BHUser"] = relationship()
