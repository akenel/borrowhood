"""QA Testing Dashboard -- API + HTML routes.

Auth: BorrowHood cookie auth (bh_session). No separate login/callback per module.
No HelixApplication filtering -- single app.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.dependencies import get_current_user_token, require_auth
from src.i18n import detect_language, get_translator, SUPPORTED_LANGUAGES
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

logger = logging.getLogger("bh.qa_router")

# ================================================================
# Router Setup
# ================================================================
router = APIRouter(prefix="/api/v1/testing", tags=["QA Testing"])
html_router = APIRouter(tags=["QA Testing - Web UI"])
templates = Jinja2Templates(directory="src/templates")


def _ctx(request: Request, token: Optional[dict] = None, **kwargs) -> dict:
    """Build template context with i18n (reuse pages.py pattern)."""
    query_lang = request.query_params.get("lang")
    cookie_lang = request.cookies.get("bh_lang")
    accept_lang = request.headers.get("accept-language")
    lang = detect_language(query_lang, cookie_lang, accept_lang)
    t = get_translator(lang)
    set_lang_cookie = query_lang and query_lang != cookie_lang
    ctx = {
        "request": request,
        "user": token,
        "t": t,
        "lang": lang,
        "supported_languages": SUPPORTED_LANGUAGES,
        "_set_lang_cookie": set_lang_cookie,
    }
    ctx.update(kwargs)
    return ctx


def _render(template_name: str, ctx: dict, status_code: int = 200):
    set_cookie = ctx.pop("_set_lang_cookie", False)
    lang = ctx.get("lang", "en")
    response = templates.TemplateResponse(template_name, ctx, status_code=status_code)
    if set_cookie:
        response.set_cookie("bh_lang", lang, max_age=365 * 24 * 3600, samesite="lax")
    return response


# ================================================================
# HTML: Dashboard Page
# ================================================================
@html_router.get("/testing", response_class=HTMLResponse)
async def testing_dashboard(
    request: Request,
    token: dict = Depends(require_auth),
):
    """Render the QA testing dashboard. Requires auth."""
    ctx = _ctx(request, token)
    return _render("pages/testing.html", ctx)


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
