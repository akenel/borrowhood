"""In-app messaging between users.

Threaded conversations tied to listings or rentals.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, BHBase


class BHMessage(BHBase, Base):
    """A single message in a conversation thread."""

    __tablename__ = "bh_message"

    sender_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )
    recipient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )

    # Optional context (what's this about?)
    listing_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_listing.id"), nullable=True
    )
    rental_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_rental.id"), nullable=True
    )

    body: Mapped[str] = mapped_column(Text, nullable=False)

    # Read tracking
    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), default=None
    )

    # Relationships
    sender: Mapped["BHUser"] = relationship(foreign_keys=[sender_id])
    recipient: Mapped["BHUser"] = relationship(foreign_keys=[recipient_id])
