"""Dispute model.

3-step dispute resolution:
1. FILED - One party opens a dispute with reason + evidence
2. UNDER_REVIEW - Admin/moderator reviews both sides
3. RESOLVED - Resolution applied (refund, keep deposit, split, etc.)
"""

import enum
import uuid
from typing import Optional

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, BHBase


class DisputeStatus(str, enum.Enum):
    FILED = "filed"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class DisputeReason(str, enum.Enum):
    ITEM_NOT_AS_DESCRIBED = "item_not_as_described"
    ITEM_DAMAGED = "item_damaged"
    ITEM_NOT_RETURNED = "item_not_returned"
    LATE_RETURN = "late_return"
    NO_SHOW = "no_show"
    PAYMENT_ISSUE = "payment_issue"
    SAFETY_CONCERN = "safety_concern"
    OTHER = "other"


class DisputeResolution(str, enum.Enum):
    FULL_REFUND = "full_refund"
    PARTIAL_REFUND = "partial_refund"
    DEPOSIT_FORFEITED = "deposit_forfeited"
    DEPOSIT_RETURNED = "deposit_returned"
    NO_ACTION = "no_action"
    ACCOUNT_WARNING = "account_warning"
    ACCOUNT_SUSPENDED = "account_suspended"


class BHDispute(BHBase, Base):
    """A dispute on a rental transaction."""

    __tablename__ = "bh_dispute"

    rental_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_rental.id"), nullable=False, index=True
    )
    filed_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False
    )

    # Status
    status: Mapped[DisputeStatus] = mapped_column(
        Enum(DisputeStatus), default=DisputeStatus.FILED, nullable=False, index=True
    )
    reason: Mapped[DisputeReason] = mapped_column(
        Enum(DisputeReason), nullable=False
    )

    # Content
    description: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_urls: Mapped[Optional[str]] = mapped_column(Text)  # JSON array of URLs
    filer_contact: Mapped[Optional[str]] = mapped_column(String(200))

    # Response from other party
    response: Mapped[Optional[str]] = mapped_column(Text)
    response_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id")
    )

    # Resolution
    resolution: Mapped[Optional[DisputeResolution]] = mapped_column(Enum(DisputeResolution))
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text)
    resolved_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id")
    )

    # Relationships
    rental: Mapped["BHRental"] = relationship()
    filed_by: Mapped["BHUser"] = relationship(foreign_keys=[filed_by_id])
