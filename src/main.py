"""BorrowHood FastAPI application.

Community rental, sales, and services platform.
"Rent it. Lend it. Share it. Teach it."
"""

import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import create_tables, get_db
from src.routers import ai, auth, badges, bids, deposits, disputes, health, helpboard, items, listings, lockbox, notifications, onboarding, pages, payments, rentals, reports, reviews
from src.routers import qa as qa_router_mod
from src.routers import backlog as backlog_router_mod
from src.services.seeding import seed_database
from src.services.qa_seeding import seed_qa_checklist
from src.services.backlog_seeding import seed_backlog_data

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title=settings.app_name,
        description="Community rental, sales, and services platform. No fees. Open source.",
        version="1.0.0",
        docs_url="/api/docs" if settings.debug else None,
        redoc_url="/api/redoc" if settings.debug else None,
    )

    # Static files
    app.mount("/static", StaticFiles(directory="src/static"), name="static")

    # API routers
    app.include_router(health.router)
    app.include_router(items.router)
    app.include_router(listings.router)
    app.include_router(rentals.router)
    app.include_router(reviews.router)
    app.include_router(notifications.router)
    app.include_router(bids.router)
    app.include_router(deposits.router)
    app.include_router(disputes.router)
    app.include_router(onboarding.router)
    app.include_router(payments.router)
    app.include_router(badges.router)
    app.include_router(ai.router)
    app.include_router(lockbox.router)
    app.include_router(reports.router)
    app.include_router(helpboard.router)

    # Auth routers (login/logout/callback)
    app.include_router(auth.router)

    # QA + Backlog API routers
    app.include_router(qa_router_mod.router)
    app.include_router(backlog_router_mod.router)

    # QA + Backlog HTML routers
    app.include_router(qa_router_mod.html_router)
    app.include_router(backlog_router_mod.html_router)

    # Page routers (HTML)
    app.include_router(pages.router)

    # Seed endpoint (debug only)
    @app.post("/api/v1/seed")
    async def seed(db: AsyncSession = Depends(get_db)):
        """Load seed data into database. Debug mode only."""
        if not settings.debug:
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="Seeding disabled in production")
        result = await seed_database(db)
        await seed_qa_checklist(db)
        await seed_backlog_data(db)
        await db.commit()
        return {"status": "ok", "counts": result}

    @app.on_event("startup")
    async def startup():
        logger.info("BorrowHood starting up...")
        if settings.debug:
            await create_tables()
            logger.info("Database tables created/verified")

    @app.on_event("shutdown")
    async def shutdown():
        logger.info("BorrowHood shutting down...")

    return app


app = create_app()
