"""Content moderation reports.

See RULES.md Section 31. Report button on every listing, review, and profile.
"""

import enum
import uuid
from typing import Optional

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base, BHBase


class ReportReason(str, enum.Enum):
    SPAM = "spam"
    INAPPROPRIATE = "inappropriate"
    SCAM = "scam"
    HARASSMENT = "harassment"
    OTHER = "other"


class ReportStatus(str, enum.Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    DISMISSED = "dismissed"


class BHReport(BHBase, Base):
    """A content moderation report filed by a user."""

    __tablename__ = "bh_report"

    reporter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "item", "review", "user"
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    reason: Mapped[ReportReason] = mapped_column(Enum(ReportReason), nullable=False)
    detail: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus), default=ReportStatus.PENDING, nullable=False
    )
    moderator_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    moderator_notes: Mapped[Optional[str]] = mapped_column(Text)
