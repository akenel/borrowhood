"""Skill verification model: peer endorsements for user skills.

Each user can verify each skill once. Verifying increments
BHUserSkill.verified_by_count. Self-verification is blocked at the API layer.
"""

import uuid

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, BHBase


class BHSkillVerification(BHBase, Base):
    """A peer verification of a user's skill."""

    __tablename__ = "bh_skill_verification"
    __table_args__ = (
        UniqueConstraint("verifier_id", "skill_id", name="uq_skill_verification"),
    )

    verifier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user_skill.id"), nullable=False, index=True
    )
    comment: Mapped[str] = mapped_column(Text, nullable=True)

    verifier: Mapped["BHUser"] = relationship(foreign_keys=[verifier_id])
    skill: Mapped["BHUserSkill"] = relationship()
