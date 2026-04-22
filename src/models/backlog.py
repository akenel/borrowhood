"""Unified Backlog models -- one board for all BorrowHood work.

BorrowHood port: uses BHBase+Base, bh_ table names, (str, enum.Enum) pattern.
No HelixApplication -- single app. Replaced CAMPER_JOB/BUSINESS_OPS with FEATURE/IMPROVEMENT.
"""

import enum
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Date, DateTime, Float, Integer, String, Text, ForeignKey, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, BHBase


# ================================================================
# Enums
# ================================================================
class BacklogItemType(str, enum.Enum):
    DEV_TASK = "dev_task"
    BUG_FIX = "bug_fix"
    FEATURE = "feature"
    IMPROVEMENT = "improvement"


class BacklogStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    BLOCKED = "blocked"
    DONE = "done"
    ARCHIVED = "archived"


class BacklogPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BacklogActivityType(str, enum.Enum):
    STATUS_CHANGE = "status_change"
    ASSIGNED = "assigned"
    PRIORITY_CHANGE = "priority_change"
    COMMENT = "comment"


class FeedbackMediaType(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    SCREEN_CAPTURE = "screen_capture"
    SESSION_REPORT = "session_report"


ALLOWED_FEEDBACK_MIME_TYPES = {
    "image/jpeg", "image/png", "image/webp", "image/gif",
    "video/mp4", "video/webm", "video/quicktime",
    "application/pdf",
    "application/json",
}

MAX_FEEDBACK_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


# ================================================================
# Backlog Item
# ================================================================
class BHBacklogItem(BHBase, Base):
    """Single work item on the Kanban board."""

    __tablename__ = "bh_backlog_item"

    item_number: Mapped[int] = mapped_column(
        Integer, nullable=False, unique=True, index=True,
    )
    item_type: Mapped[BacklogItemType] = mapped_column(
        SQLEnum(BacklogItemType, name="bh_backlog_item_type", create_constraint=True,
                values_callable=lambda x: [e.value for e in x]),
        nullable=False, default=BacklogItemType.DEV_TASK, index=True,
    )
    status: Mapped[BacklogStatus] = mapped_column(
        SQLEnum(BacklogStatus, name="bh_backlog_status", create_constraint=True,
                values_callable=lambda x: [e.value for e in x]),
        nullable=False, default=BacklogStatus.PENDING, index=True,
    )
    priority: Mapped[BacklogPriority] = mapped_column(
        SQLEnum(BacklogPriority, name="bh_backlog_priority", create_constraint=True,
                values_callable=lambda x: [e.value for e in x]),
        nullable=False, default=BacklogPriority.MEDIUM, index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    assigned_to: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    due_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    estimated_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    blocked_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_by: Mapped[str] = mapped_column(String(100), nullable=False, default="Angel")
    reporter_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )
    reporter_rewarded_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    resolution_sha: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    resolution_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    activities: Mapped[List["BHBacklogActivity"]] = relationship(
        back_populates="item", cascade="all, delete-orphan",
        order_by="BHBacklogActivity.created_at",
    )
    media: Mapped[List["BHFeedbackMedia"]] = relationship(
        back_populates="item", cascade="all, delete-orphan",
        order_by="BHFeedbackMedia.created_at",
    )


# ================================================================
# Backlog Activity Log (append-only)
# ================================================================
class BHBacklogActivity(BHBase, Base):
    """Every status change, assignment, comment -- timestamped."""

    __tablename__ = "bh_backlog_activity"

    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_backlog_item.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    activity_type: Mapped[BacklogActivityType] = mapped_column(
        SQLEnum(BacklogActivityType, name="bh_backlog_activity_type", create_constraint=True,
                values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    actor: Mapped[str] = mapped_column(String(100), nullable=False)
    old_value: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    new_value: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationship
    item: Mapped["BHBacklogItem"] = relationship(
        back_populates="activities", foreign_keys=[item_id],
    )


# ================================================================
# Feedback Media (screenshots, clips, docs, session reports)
# ================================================================
class BHFeedbackMedia(BHBase, Base):
    """Attachment on a backlog item. Images/video/PDF uploaded by the
    reporter, plus the auto-captured session-report JSON."""

    __tablename__ = "bh_feedback_media"

    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_backlog_item.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    media_type: Mapped[FeedbackMediaType] = mapped_column(
        SQLEnum(FeedbackMediaType, name="bh_feedback_media_type", create_constraint=True,
                values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    uploader: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    item: Mapped["BHBacklogItem"] = relationship(
        back_populates="media", foreign_keys=[item_id],
    )
