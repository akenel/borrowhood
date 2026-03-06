"""Mentorship models: mentor/apprentice/intern relationships.

A mentorship connects two users around a specific skill.
The mentor teaches, the apprentice learns.
Interns are short-term (project-based), apprentices are ongoing.

Season 1 arcs:
  - Sally mentors Sofia in baking
  - Pietro mentors Sofia in drone flying
  - John (Johnny) takes Sofia as delivery intern
"""

import enum
import uuid
from typing import Optional

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, BHBase


class MentorshipType(str, enum.Enum):
    MENTOR = "mentor"          # Ongoing teaching relationship
    APPRENTICE = "apprentice"  # Formal skill-building (long-term)
    INTERN = "intern"          # Short-term project-based learning


class MentorshipStatus(str, enum.Enum):
    PROPOSED = "proposed"      # One side asked
    ACTIVE = "active"          # Both agreed
    PAUSED = "paused"          # On hold
    COMPLETED = "completed"    # Goal achieved
    CANCELLED = "cancelled"    # Didn't work out


class BHMentorship(BHBase, Base):
    """A mentorship relationship between two users.

    The mentor teaches a skill. The apprentice/intern learns.
    Tracks hours logged, milestones, and the skill category.
    """

    __tablename__ = "bh_mentorship"

    # Who teaches
    mentor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )
    # Who learns
    apprentice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_user.id"), nullable=False, index=True
    )

    # What kind of relationship
    mentorship_type: Mapped[MentorshipType] = mapped_column(
        Enum(MentorshipType), default=MentorshipType.APPRENTICE, nullable=False
    )
    status: Mapped[MentorshipStatus] = mapped_column(
        Enum(MentorshipStatus), default=MentorshipStatus.PROPOSED, nullable=False
    )

    # What skill
    skill_name: Mapped[str] = mapped_column(String(100), nullable=False)
    skill_category: Mapped[str] = mapped_column(String(50), nullable=False)

    # Progress
    hours_logged: Mapped[int] = mapped_column(Integer, default=0)
    milestones_completed: Mapped[int] = mapped_column(Integer, default=0)
    goal: Mapped[Optional[str]] = mapped_column(Text)  # "Bake 100 cookies", "Solo drone flight"
    notes: Mapped[Optional[str]] = mapped_column(Text)  # Mentor's notes on progress

    # Relationships
    mentor: Mapped["BHUser"] = relationship(foreign_keys=[mentor_id])
    apprentice: Mapped["BHUser"] = relationship(foreign_keys=[apprentice_id])
