"""BorrowHood FastAPI application.

Community rental, sales, and services platform.
"Rent it. Lend it. Share it. Teach it."
"""

import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.config import settings
from src.database import create_tables
from src.routers import health, pages

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

    # Page routers (HTML)
    app.include_router(pages.router)

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
