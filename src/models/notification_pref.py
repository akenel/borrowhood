"""Per-type notification preferences.

Users can mute specific notification categories while keeping the
global notify_telegram/notify_email toggles on.
"""

import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base, BHBase
from src.models.notification import NotificationType


class BHNotificationPref(BHBase, Base):
    """Per-notification-type preference for a user.

    If no row exists for a (user, type), the default is enabled=True.
    Only rows where the user explicitly toggled a type are stored.
    """

    __tablename__ = "bh_notification_pref"
    __table_args__ = (
        UniqueConstraint("user_id", "notification_type", name="uq_notif_pref_user_type"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )
    notification_type: Mapped[str] = mapped_column(String(50), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
