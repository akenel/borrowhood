"""Help Board model -- community requests and offers.

"I need help with..." or "I can help with..." posts.
Neighbors helping neighbors -- the core of BorrowHood.
"""

import enum
import uuid
from typing import Optional

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, BHBase


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

    # Engagement
    reply_count: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    author: Mapped["BHUser"] = relationship()
    replies: Mapped[list["BHHelpReply"]] = relationship(
        back_populates="post", cascade="all, delete-orphan"
    )


class BHHelpReply(BHBase, Base):
    """A reply to a help post."""

    __tablename__ = "bh_help_reply"

    post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_help_post.id"), nullable=False, index=True
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    post: Mapped["BHHelpPost"] = relationship(back_populates="replies")
    author: Mapped["BHUser"] = relationship()
