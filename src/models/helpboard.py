"""Help Board model -- community requests and offers.

"I need help with..." or "I can help with..." posts.
Neighbors helping neighbors -- the core of BorrowHood.

Enhanced: item tagging, media (photos/videos), threaded replies,
resolved-by tracking, upvotes.
"""

import enum
import uuid
from typing import Optional

from sqlalchemy import Boolean, Enum, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, BHBase


# 10 MB max for uploads (photos + videos)
MAX_MEDIA_SIZE = 10 * 1024 * 1024

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime"}
ALLOWED_MEDIA_TYPES = ALLOWED_IMAGE_TYPES | ALLOWED_VIDEO_TYPES


class HelpType(str, enum.Enum):
    NEED = "need"       # "I need help with..."
    OFFER = "offer"     # "I can help with..."


class HelpStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class HelpUrgency(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    URGENT = "urgent"


class HelpMediaType(str, enum.Enum):
    PHOTO = "photo"
    VIDEO = "video"


class BHHelpPost(BHBase, Base):
    """A help request or offer on the community board."""

    __tablename__ = "bh_help_post"

    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )
    help_type: Mapped[HelpType] = mapped_column(Enum(HelpType), nullable=False, index=True)
    status: Mapped[HelpStatus] = mapped_column(
        Enum(HelpStatus), default=HelpStatus.OPEN, nullable=False, index=True
    )
    urgency: Mapped[HelpUrgency] = mapped_column(
        Enum(HelpUrgency), default=HelpUrgency.NORMAL, nullable=False
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    content_language: Mapped[str] = mapped_column(String(5), default="en")

    # Location context
    neighborhood: Mapped[Optional[str]] = mapped_column(String(100))

    # Item tagging -- link post to a specific item (optional)
    item_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_item.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Resolved-by -- who helped solve this
    resolved_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id", ondelete="SET NULL"), nullable=True
    )

    # Engagement
    reply_count: Mapped[int] = mapped_column(Integer, default=0)
    upvote_count: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    author: Mapped["BHUser"] = relationship(foreign_keys=[author_id])
    resolved_by: Mapped[Optional["BHUser"]] = relationship(foreign_keys=[resolved_by_id])
    item: Mapped[Optional["BHItem"]] = relationship()
    replies: Mapped[list["BHHelpReply"]] = relationship(
        back_populates="post", cascade="all, delete-orphan"
    )
    media: Mapped[list["BHHelpMedia"]] = relationship(
        back_populates="post", cascade="all, delete-orphan",
        foreign_keys="BHHelpMedia.post_id"
    )
    upvotes: Mapped[list["BHHelpUpvote"]] = relationship(
        back_populates="post", cascade="all, delete-orphan"
    )


class BHHelpReply(BHBase, Base):
    """A reply to a help post. Supports threading via parent_reply_id."""

    __tablename__ = "bh_help_reply"

    post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_help_post.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)

    # Threading -- null means top-level reply
    parent_reply_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_help_reply.id", ondelete="CASCADE"), nullable=True, index=True
    )

    # Engagement
    upvote_count: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    post: Mapped["BHHelpPost"] = relationship(back_populates="replies")
    author: Mapped["BHUser"] = relationship()
    parent: Mapped[Optional["BHHelpReply"]] = relationship(
        remote_side="BHHelpReply.id", foreign_keys=[parent_reply_id]
    )
    children: Mapped[list["BHHelpReply"]] = relationship(
        foreign_keys=[parent_reply_id], cascade="all, delete-orphan",
        overlaps="parent"
    )
    media: Mapped[list["BHHelpMedia"]] = relationship(
        back_populates="reply", cascade="all, delete-orphan",
        foreign_keys="BHHelpMedia.reply_id"
    )


class BHHelpMedia(BHBase, Base):
    """Media attachment for a help post or reply (photo or video, max 10MB)."""

    __tablename__ = "bh_help_media"

    # Polymorphic: belongs to either a post or a reply (one must be set)
    post_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_help_post.id", ondelete="CASCADE"), nullable=True, index=True
    )
    reply_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_help_reply.id", ondelete="CASCADE"), nullable=True, index=True
    )

    uploader_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False
    )

    media_type: Mapped[HelpMediaType] = mapped_column(Enum(HelpMediaType), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)  # bytes
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    alt_text: Mapped[Optional[str]] = mapped_column(String(300))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # Video thumbnail (generated server-side later, or first frame)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Relationships
    post: Mapped[Optional["BHHelpPost"]] = relationship(back_populates="media", foreign_keys=[post_id])
    reply: Mapped[Optional["BHHelpReply"]] = relationship(back_populates="media", foreign_keys=[reply_id])
    uploader: Mapped["BHUser"] = relationship()


class BHHelpUpvote(BHBase, Base):
    """Upvote on a help post. One per user per post."""

    __tablename__ = "bh_help_upvote"

    post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_help_post.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False
    )

    # Relationships
    post: Mapped["BHHelpPost"] = relationship(back_populates="upvotes")

    __table_args__ = (
        UniqueConstraint("post_id", "user_id", name="uq_help_upvote_per_user"),
    )
