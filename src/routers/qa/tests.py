"""Test result list / update / reset."""

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.dependencies import get_current_user_token, require_auth
from src.models.qa import (
    BHTestResult, TestStatus,
    BHBugReport, BugSeverity, BugStatus, BugCategory,
    BHBugActivity, BugActivityType,
    BHBugCommit,
)
from src.schemas.qa import (
    TestResultUpdate, TestResultRead,
    BugReportCreate, BugReportUpdate, BugReportRead, BugActivityRead,
    BugCommitCreate, BugCommitRead,
    DashboardSummary, PhaseProgress,
)

from ._shared import router, html_router, templates, logger, _ctx, _render

@router.get("/tests", response_model=list[TestResultRead])
async def list_tests(
    phase: Optional[int] = None,
    status_filter: Optional[str] = None,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List all test items. Filter by phase or status."""
    query = select(BHTestResult)

    if phase is not None:
        query = query.where(BHTestResult.phase == phase)
    if status_filter:
        try:
            ts = TestStatus(status_filter)
            query = query.where(BHTestResult.status == ts)
        except ValueError:
            pass

    query = query.order_by(BHTestResult.phase, BHTestResult.sort_order)
    result = await db.execute(query)
    return result.scalars().all()


@router.put("/tests/{test_id}", response_model=TestResultRead)
async def update_test(
    test_id: UUID,
    update: TestResultUpdate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Mark a test as pass/fail/skip/blocked."""
    result = await db.execute(
        select(BHTestResult).where(BHTestResult.id == test_id)
    )
    test = result.scalar_one_or_none()
    if not test:
        raise HTTPException(status_code=404, detail="Test item not found")

    test.status = update.status
    if update.tester_name is not None:
        test.tester_name = update.tester_name
    if update.notes is not None:
        test.notes = update.notes
    test.executed_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(test)
    return test


@router.post("/tests/reset", status_code=status.HTTP_200_OK)
async def reset_all_tests(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Reset all tests to pending for a new test cycle."""
    result = await db.execute(select(BHTestResult))
    tests = result.scalars().all()
    for test in tests:
        test.status = TestStatus.PENDING
        test.tester_name = None
        test.notes = None
        test.executed_at = None

    await db.commit()
    return {"message": f"Reset {len(tests)} tests to pending"}


# ================================================================
# API: Bug Reports
# ================================================================


