"""Pydantic schemas for QA Testing Dashboard."""

from datetime import datetime
from uuid import UUID
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict

from src.models.qa import TestStatus, BugSeverity, BugStatus, BugCategory


# ================================================================
# Test Result Schemas
# ================================================================
class TestResultUpdate(BaseModel):
    status: TestStatus = Field(..., description="Test result: pass, fail, skip, blocked")
    tester_name: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None)


class TestResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    phase: int
    phase_name: str
    sort_order: int
    title: str
    description: Optional[str] = None
    status: TestStatus
    tester_name: Optional[str] = None
    notes: Optional[str] = None
    executed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# ================================================================
# Bug Report Schemas
# ================================================================
class BugReportCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)
    severity: BugSeverity = Field(default=BugSeverity.MEDIUM)
    category: BugCategory = Field(default=BugCategory.FUNCTIONAL)
    test_result_id: Optional[UUID] = None
    screenshot_data: Optional[str] = None
    browser_info: Optional[str] = Field(None, max_length=200)
    reported_by: str = Field(default="Tester", min_length=1, max_length=100)


class BugReportUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    severity: Optional[BugSeverity] = None
    category: Optional[BugCategory] = None
    status: Optional[BugStatus] = None
    assigned_to: Optional[str] = Field(None, max_length=100)
    git_sha: Optional[str] = Field(None, min_length=7, max_length=40)
    screenshot_data: Optional[str] = None
    comment: Optional[str] = Field(None, min_length=1)
    actor: str = Field(default="Tester", min_length=1, max_length=100)


class BugCommitCreate(BaseModel):
    sha: str = Field(..., min_length=7, max_length=40)
    message: str = Field(..., min_length=3, max_length=200)
    committed_at: Optional[datetime] = None
    actor: str = Field(default="Tigs", min_length=1, max_length=100)


class BugCommitRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sha: str
    message: str
    committed_at: datetime
    created_at: datetime


class BugReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    bug_number: int
    title: str
    description: str
    severity: BugSeverity
    category: Optional[BugCategory] = None
    status: BugStatus
    assigned_to: Optional[str] = None
    git_sha: Optional[str] = None
    test_result_id: Optional[UUID] = None
    screenshot_data: Optional[str] = None
    browser_info: Optional[str] = None
    reported_by: str
    commits: List[BugCommitRead] = []
    created_at: datetime
    updated_at: datetime


class BugActivityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    bug_id: UUID
    activity_type: str
    actor: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    comment: Optional[str] = None
    created_at: datetime


# ================================================================
# Dashboard Summary
# ================================================================
class PhaseProgress(BaseModel):
    phase: int
    phase_name: str
    total: int
    passed: int
    failed: int
    skipped: int
    blocked: int
    pending: int
    percent_complete: float


class DashboardSummary(BaseModel):
    total_tests: int
    passed: int
    failed: int
    skipped: int
    blocked: int
    pending: int
    percent_complete: float
    total_bugs: int
    open_bugs: int
    critical_bugs: int
