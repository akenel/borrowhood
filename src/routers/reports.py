"""Content moderation reports API.

RULES.md Section 31: Report button on every listing, review, and profile.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies import require_auth
from src.models.report import BHReport, ReportStatus
from src.schemas.report import ReportCreate, ReportRead

logger = logging.getLogger("bh.reports")

router = APIRouter(prefix="/api/v1/reports", tags=["Reports"])


@router.post("", response_model=ReportRead, status_code=status.HTTP_201_CREATED)
async def create_report(
    report: ReportCreate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """File a content moderation report."""
    reporter_id = token.get("sub")
    if not reporter_id:
        raise HTTPException(status_code=401, detail="Missing user identity")

    # Prevent duplicate reports from same user on same entity
    existing = await db.scalar(
        select(func.count()).select_from(BHReport).where(
            BHReport.reporter_id == reporter_id,
            BHReport.entity_type == report.entity_type,
            BHReport.entity_id == report.entity_id,
            BHReport.status == ReportStatus.PENDING,
        )
    )
    if existing:
        raise HTTPException(status_code=409, detail="You already reported this")

    new_report = BHReport(
        reporter_id=reporter_id,
        entity_type=report.entity_type,
        entity_id=report.entity_id,
        reason=report.reason,
        detail=report.detail,
    )
    db.add(new_report)
    await db.commit()
    await db.refresh(new_report)

    logger.info("Report filed: %s %s by %s reason=%s", report.entity_type, report.entity_id, reporter_id, report.reason)
    return new_report
