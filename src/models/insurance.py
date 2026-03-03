"""Insurance models: policies and claims.

Renters can purchase insurance on rentals. Claims follow a state machine:
FILED -> UNDER_REVIEW -> APPROVED -> PAID_OUT
                      -> DENIED
"""

import enum
import uuid
from typing import Optional

from sqlalchemy import Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, BHBase


class InsuranceStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CLAIMED = "claimed"
    CANCELLED = "cancelled"


class ClaimStatus(str, enum.Enum):
    FILED = "filed"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    DENIED = "denied"
    PAID_OUT = "paid_out"


# Valid claim state transitions
CLAIM_TRANSITIONS = {
    ClaimStatus.FILED: {ClaimStatus.UNDER_REVIEW},
    ClaimStatus.UNDER_REVIEW: {ClaimStatus.APPROVED, ClaimStatus.DENIED},
    ClaimStatus.APPROVED: {ClaimStatus.PAID_OUT},
}


class BHInsurancePolicy(BHBase, Base):
    """An insurance policy covering a rental."""

    __tablename__ = "bh_insurance_policy"

    rental_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_rental.id"), nullable=False, index=True
    )
    holder_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )
    provider: Mapped[str] = mapped_column(String(100), default="BorrowHood Basic")
    policy_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    coverage_amount: Mapped[float] = mapped_column(Float, nullable=False)
    premium: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[InsuranceStatus] = mapped_column(
        Enum(InsuranceStatus), default=InsuranceStatus.ACTIVE, nullable=False
    )

    # Relationships
    holder: Mapped["BHUser"] = relationship(foreign_keys=[holder_id])
    rental: Mapped["BHRental"] = relationship()
    claims: Mapped[list["BHInsuranceClaim"]] = relationship(back_populates="policy")


class BHInsuranceClaim(BHBase, Base):
    """An insurance claim against a policy."""

    __tablename__ = "bh_insurance_claim"

    policy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_insurance_policy.id"), nullable=False, index=True
    )
    claimant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_url: Mapped[Optional[str]] = mapped_column(String(500))
    claim_amount: Mapped[float] = mapped_column(Float, nullable=False)
    approved_amount: Mapped[Optional[float]] = mapped_column(Float)
    status: Mapped[ClaimStatus] = mapped_column(
        Enum(ClaimStatus), default=ClaimStatus.FILED, nullable=False
    )
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    policy: Mapped["BHInsurancePolicy"] = relationship(back_populates="claims")
    claimant: Mapped["BHUser"] = relationship(foreign_keys=[claimant_id])
