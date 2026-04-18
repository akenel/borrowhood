"""HTML page route for the testing dashboard."""

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


