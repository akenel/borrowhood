"""Bug CRUD + activity + commit linking."""

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

@router.post("/bugs", response_model=BugReportRead, status_code=status.HTTP_201_CREATED)
async def create_bug(
    bug: BugReportCreate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """File a new bug report."""
    if bug.test_result_id:
        test_result = await db.execute(
            select(BHTestResult).where(BHTestResult.id == bug.test_result_id)
        )
        if not test_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Linked test item not found")

    max_num = await db.execute(
        select(func.coalesce(func.max(BHBugReport.bug_number), 0))
    )
    next_number = max_num.scalar() + 1

    new_bug = BHBugReport(
        bug_number=next_number,
        title=bug.title,
        description=bug.description,
        severity=bug.severity,
        category=bug.category,
        test_result_id=bug.test_result_id,
        screenshot_data=bug.screenshot_data,
        browser_info=bug.browser_info,
        reported_by=bug.reported_by,
    )
    db.add(new_bug)
    await db.commit()

    result = await db.execute(
        select(BHBugReport)
        .options(selectinload(BHBugReport.commits))
        .where(BHBugReport.id == new_bug.id)
    )
    return result.scalar_one()


@router.get("/bugs", response_model=list[BugReportRead])
async def list_bugs(
    q: Optional[str] = None,
    severity: Optional[str] = None,
    status_filter: Optional[str] = None,
    category: Optional[str] = None,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List all bug reports, newest first. Filter by severity, status, category. Search by q."""
    query = select(BHBugReport).options(selectinload(BHBugReport.commits))

    if q and q.strip():
        term = f"%{q.strip()}%"
        query = query.where(or_(
            BHBugReport.title.ilike(term),
            BHBugReport.description.ilike(term),
        ))

    if severity:
        try:
            query = query.where(BHBugReport.severity == BugSeverity(severity))
        except ValueError:
            pass
    if status_filter:
        try:
            query = query.where(BHBugReport.status == BugStatus(status_filter))
        except ValueError:
            pass
    if category:
        try:
            query = query.where(BHBugReport.category == BugCategory(category))
        except ValueError:
            pass

    query = query.order_by(BHBugReport.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.put("/bugs/{bug_id}", response_model=BugReportRead)
async def update_bug(
    bug_id: UUID,
    update: BugReportUpdate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Update a bug report -- auto-creates activity log entries."""
    result = await db.execute(
        select(BHBugReport)
        .options(selectinload(BHBugReport.commits))
        .where(BHBugReport.id == bug_id)
    )
    bug = result.scalar_one_or_none()
    if not bug:
        raise HTTPException(status_code=404, detail="Bug report not found")

    actor = update.actor or "Tester"
    activities = []

    if update.status is not None and update.status != bug.status:
        activities.append(BHBugActivity(
            bug_id=bug.id,
            activity_type=BugActivityType.STATUS_CHANGE,
            actor=actor,
            old_value=bug.status.value,
            new_value=update.status.value,
        ))
        bug.status = update.status

    if update.assigned_to is not None and update.assigned_to != (bug.assigned_to or ""):
        new_assignee = update.assigned_to if update.assigned_to else None
        activities.append(BHBugActivity(
            bug_id=bug.id,
            activity_type=BugActivityType.ASSIGNED,
            actor=actor,
            old_value=bug.assigned_to,
            new_value=new_assignee,
        ))
        bug.assigned_to = new_assignee

    if update.git_sha is not None and update.git_sha != (bug.git_sha or ""):
        activities.append(BHBugActivity(
            bug_id=bug.id,
            activity_type=BugActivityType.GIT_LINKED,
            actor=actor,
            new_value=update.git_sha if update.git_sha else None,
        ))
        bug.git_sha = update.git_sha if update.git_sha else None

    if update.comment:
        activities.append(BHBugActivity(
            bug_id=bug.id,
            activity_type=BugActivityType.COMMENT,
            actor=actor,
            comment=update.comment,
        ))

    if update.title is not None:
        bug.title = update.title
    if update.description is not None:
        bug.description = update.description
    if update.severity is not None:
        bug.severity = update.severity
    if update.category is not None:
        bug.category = update.category
    if update.screenshot_data is not None:
        bug.screenshot_data = update.screenshot_data

    for activity in activities:
        db.add(activity)

    await db.commit()
    await db.refresh(bug)

    if activities:
        logger.info(f"BUG-{bug.bug_number:03d} updated by {actor}: {len(activities)} activity entries")

    return bug


@router.get("/bugs/{bug_id}/activities", response_model=list[BugActivityRead])
async def get_bug_activities(
    bug_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Get activity log for a bug report."""
    bug_result = await db.execute(
        select(BHBugReport).where(BHBugReport.id == bug_id)
    )
    if not bug_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Bug report not found")

    result = await db.execute(
        select(BHBugActivity)
        .where(BHBugActivity.bug_id == bug_id)
        .order_by(BHBugActivity.created_at.desc())
    )
    return result.scalars().all()


@router.post("/bugs/{bug_id}/commits", response_model=BugCommitRead, status_code=status.HTTP_201_CREATED)
async def add_bug_commit(
    bug_id: UUID,
    commit: BugCommitCreate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Link a git commit to a bug report."""
    bug_result = await db.execute(
        select(BHBugReport).where(BHBugReport.id == bug_id)
    )
    bug = bug_result.scalar_one_or_none()
    if not bug:
        raise HTTPException(status_code=404, detail="Bug report not found")

    existing = await db.execute(
        select(BHBugCommit).where(
            BHBugCommit.bug_id == bug_id,
            BHBugCommit.sha == commit.sha,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"Commit {commit.sha} already linked")

    new_commit = BHBugCommit(
        bug_id=bug_id,
        sha=commit.sha,
        message=commit.message[:200],
        committed_at=commit.committed_at or datetime.now(timezone.utc),
    )
    db.add(new_commit)

    bug.git_sha = commit.sha

    db.add(BHBugActivity(
        bug_id=bug_id,
        activity_type=BugActivityType.GIT_LINKED,
        actor=commit.actor,
        new_value=f"{commit.sha[:7]} {commit.message[:50]}",
    ))

    await db.commit()
    await db.refresh(new_commit)

    logger.info(f"BUG-{bug.bug_number:03d}: commit {commit.sha[:7]} linked by {commit.actor}")
    return new_commit


