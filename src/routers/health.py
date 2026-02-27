"""Health check endpoint.

Returns DB status, app version, and uptime.
Added to smoke test on deploy (RULES.md Section 18).
"""

import time
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db

router = APIRouter(prefix="/api/v1", tags=["health"])

_start_time = time.time()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Application health check."""
    # Check database connectivity
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {e}"

    uptime_seconds = int(time.time() - _start_time)

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "app": "BorrowHood",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": uptime_seconds,
        "checks": {
            "database": db_status,
        },
    }
