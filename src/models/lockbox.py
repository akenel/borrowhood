"""Lock box access code model.

One-time pickup and return codes for contactless item exchange.
Owner generates codes after approving a rental. Renter uses pickup code
to confirm they've taken the item, return code to confirm drop-off.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, BHBase


class BHLockBoxAccess(BHBase, Base):
    """One-time access codes for contactless item exchange."""

    __tablename__ = "bh_lockbox_access"

    rental_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_rental.id"), nullable=False, unique=True, index=True
    )

    # Access codes (8-char alphanumeric, no confusing chars)
    pickup_code: Mapped[str] = mapped_column(String(8), nullable=False, unique=True)
    return_code: Mapped[str] = mapped_column(String(8), nullable=False, unique=True)

    # Code usage tracking
    pickup_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    return_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Lock box info
    location_hint: Mapped[Optional[str]] = mapped_column(String(500))  # "Under the mat on porch"
    instructions: Mapped[Optional[str]] = mapped_column(Text)  # "Combo is 4-7-2-9"

    # Relationship
    rental: Mapped["BHRental"] = relationship(back_populates="lockbox")
