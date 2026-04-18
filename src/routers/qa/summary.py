"""Dashboard summary + per-phase progress."""

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

# ================================================================
# API: Dashboard Summary
# ================================================================
@router.get("/summary", response_model=DashboardSummary)
async def get_summary(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Overall testing progress stats."""
    result = await db.execute(
        select(
            BHTestResult.status,
            func.count().label("cnt"),
        ).group_by(BHTestResult.status)
    )
    status_counts = {row.status: row.cnt for row in result}

    total = sum(status_counts.values())
    passed = status_counts.get(TestStatus.PASS, 0)
    failed = status_counts.get(TestStatus.FAIL, 0)
    skipped = status_counts.get(TestStatus.SKIP, 0)
    blocked = status_counts.get(TestStatus.BLOCKED, 0)
    pending = status_counts.get(TestStatus.PENDING, 0)
    completed = total - pending
    percent = (completed / total * 100) if total > 0 else 0

    # Bug counts
    total_bugs = await db.scalar(
        select(func.count()).select_from(BHBugReport)
    ) or 0

    open_bugs = await db.scalar(
        select(func.count()).select_from(BHBugReport).where(
            BHBugReport.status.in_([BugStatus.OPEN, BugStatus.IN_PROGRESS])
        )
    ) or 0

    critical_bugs = await db.scalar(
        select(func.count()).select_from(BHBugReport).where(
            and_(
                BHBugReport.severity == BugSeverity.CRITICAL,
                BHBugReport.status.in_([BugStatus.OPEN, BugStatus.IN_PROGRESS]),
            )
        )
    ) or 0

    return DashboardSummary(
        total_tests=total,
        passed=passed,
        failed=failed,
        skipped=skipped,
        blocked=blocked,
        pending=pending,
        percent_complete=round(percent, 1),
        total_bugs=total_bugs,
        open_bugs=open_bugs,
        critical_bugs=critical_bugs,
    )


# ================================================================
# API: Phase Progress
# ================================================================
@router.get("/phases", response_model=list[PhaseProgress])
async def get_phases(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Per-phase progress breakdown."""
    result = await db.execute(
        select(
            BHTestResult.phase,
            BHTestResult.phase_name,
            BHTestResult.status,
            func.count().label("cnt"),
        ).group_by(
            BHTestResult.phase,
            BHTestResult.phase_name,
            BHTestResult.status,
        ).order_by(BHTestResult.phase)
    )

    phases = {}
    for row in result:
        key = row.phase
        if key not in phases:
            phases[key] = {
                "phase": row.phase,
                "phase_name": row.phase_name,
                "total": 0, "passed": 0, "failed": 0,
                "skipped": 0, "blocked": 0, "pending": 0,
            }
        phases[key]["total"] += row.cnt
        if row.status == TestStatus.PASS:
            phases[key]["passed"] += row.cnt
        elif row.status == TestStatus.FAIL:
            phases[key]["failed"] += row.cnt
        elif row.status == TestStatus.SKIP:
            phases[key]["skipped"] += row.cnt
        elif row.status == TestStatus.BLOCKED:
            phases[key]["blocked"] += row.cnt
        elif row.status == TestStatus.PENDING:
            phases[key]["pending"] += row.cnt

    output = []
    for key in sorted(phases.keys()):
        p = phases[key]
        completed = p["total"] - p["pending"]
        pct = (completed / p["total"] * 100) if p["total"] > 0 else 0
        output.append(PhaseProgress(
            phase=p["phase"],
            phase_name=p["phase_name"],
            total=p["total"],
            passed=p["passed"],
            failed=p["failed"],
            skipped=p["skipped"],
            blocked=p["blocked"],
            pending=p["pending"],
            percent_complete=round(pct, 1),
        ))

    return output


# ================================================================
# API: Test Items
# ================================================================


