"""QA Testing Dashboard models -- test checklist + bug reports.

BorrowHood port: uses BHBase+Base, bh_ table names, (str, enum.Enum) pattern.
No HelixApplication -- single app, no multi-app filtering.
"""

import enum
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, Integer, String, Text, ForeignKey, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base, BHBase


# ================================================================
# Enums
# ================================================================
class TestStatus(str, enum.Enum):
    PENDING = "pending"
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    BLOCKED = "blocked"


class BugSeverity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class BugStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    FIXED = "fixed"
    VERIFIED = "verified"
    WONT_FIX = "wont_fix"


class BugCategory(str, enum.Enum):
    FUNCTIONAL = "functional"
    COSMETIC = "cosmetic"
    PERFORMANCE = "performance"
    DATA = "data"
    SECURITY = "security"


class BugActivityType(str, enum.Enum):
    STATUS_CHANGE = "status_change"
    ASSIGNED = "assigned"
    COMMENT = "comment"
    GIT_LINKED = "git_linked"


# ================================================================
# QA Test Result
# ================================================================
class BHTestResult(BHBase, Base):
    """Single test item in the checklist."""

    __tablename__ = "bh_test_result"

    phase: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    phase_name: Mapped[str] = mapped_column(String(100), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[TestStatus] = mapped_column(
        SQLEnum(TestStatus, name="bh_test_status", create_constraint=True,
                values_callable=lambda x: [e.value for e in x]),
        nullable=False, default=TestStatus.PENDING, index=True,
    )
    tester_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    executed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )

    # Relationships
    bug_reports: Mapped[List["BHBugReport"]] = relationship(
        back_populates="test_result", cascade="all, delete-orphan",
    )


# ================================================================
# QA Bug Report
# ================================================================
class BHBugReport(BHBase, Base):
    """Bug filed against BorrowHood."""

    __tablename__ = "bh_bug_report"

    bug_number: Mapped[int] = mapped_column(
        Integer, nullable=False, unique=True, index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[BugSeverity] = mapped_column(
        SQLEnum(BugSeverity, name="bh_bug_severity", create_constraint=True,
                values_callable=lambda x: [e.value for e in x]),
        nullable=False, default=BugSeverity.MEDIUM, index=True,
    )
    category: Mapped[Optional[BugCategory]] = mapped_column(
        SQLEnum(BugCategory, name="bh_bug_category", create_constraint=True,
                values_callable=lambda x: [e.value for e in x]),
        nullable=True, default=BugCategory.FUNCTIONAL, index=True,
    )
    status: Mapped[BugStatus] = mapped_column(
        SQLEnum(BugStatus, name="bh_bug_status", create_constraint=True,
                values_callable=lambda x: [e.value for e in x]),
        nullable=False, default=BugStatus.OPEN, index=True,
    )
    test_result_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_test_result.id"), nullable=True,
    )
    screenshot_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    browser_info: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    reported_by: Mapped[str] = mapped_column(String(100), nullable=False, default="Tester")
    assigned_to: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    git_sha: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)

    # Relationships
    test_result: Mapped[Optional["BHTestResult"]] = relationship(
        back_populates="bug_reports", foreign_keys=[test_result_id],
    )
    activities: Mapped[List["BHBugActivity"]] = relationship(
        back_populates="bug", cascade="all, delete-orphan",
        order_by="BHBugActivity.created_at",
    )
    commits: Mapped[List["BHBugCommit"]] = relationship(
        back_populates="bug", cascade="all, delete-orphan",
        order_by="BHBugCommit.committed_at",
    )


# ================================================================
# QA Bug Activity Log (append-only)
# ================================================================
class BHBugActivity(BHBase, Base):
    """Every status change, assignment, comment -- timestamped."""

    __tablename__ = "bh_bug_activity"

    bug_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_bug_report.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    activity_type: Mapped[BugActivityType] = mapped_column(
        SQLEnum(BugActivityType, name="bh_bug_activity_type", create_constraint=True,
                values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    actor: Mapped[str] = mapped_column(String(100), nullable=False)
    old_value: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    new_value: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationship
    bug: Mapped["BHBugReport"] = relationship(
        back_populates="activities", foreign_keys=[bug_id],
    )


# ================================================================
# QA Bug Commit Tracking
# ================================================================
class BHBugCommit(BHBase, Base):
    """Git commits linked to a bug fix."""

    __tablename__ = "bh_bug_commit"

    bug_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bh_bug_report.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    sha: Mapped[str] = mapped_column(String(40), nullable=False)
    message: Mapped[str] = mapped_column(String(200), nullable=False)
    committed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )

    # Relationship
    bug: Mapped["BHBugReport"] = relationship(
        back_populates="commits", foreign_keys=[bug_id],
    )
