"""BorrowHood FastAPI application.

Community rental, sales, and services platform.
"Rent it. Lend it. Share it. Teach it."
"""

import asyncio
import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import async_session, create_tables, get_db
from src.routers import ai, auth, badges, bids, communities, deposits, disputes, health, helpboard, insurance, items, listing_qa, listings, lockbox, messages, notifications, onboarding, pages, payments, rentals, reports, reviews, service_quotes, skills, telegram, translation, users
from src.routers import qa as qa_router_mod
from src.routers import backlog as backlog_router_mod
from src.services.seeding import seed_database, seed_new_users, seed_new_items, seed_default_community
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
    app.include_router(skills.router)
    app.include_router(users.router)
    app.include_router(service_quotes.router)
    app.include_router(telegram.router)
    app.include_router(translation.router)
    app.include_router(insurance.router)
    app.include_router(communities.router)
    app.include_router(listing_qa.router)
    app.include_router(messages.router)

    # Demo login (debug only)
    if settings.debug:
        from src.routers import demo
        app.include_router(demo.router)

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
            # Run lightweight migrations (ADD COLUMN IF NOT EXISTS)
            from src.database import run_migrations
            await run_migrations()
            logger.info("Schema migrations applied")
            # Add any new users and items from seed.json that don't exist yet
            from sqlalchemy.ext.asyncio import AsyncSession
            async with async_session() as db:
                user_result = await seed_new_users(db)
                logger.info("Incremental user seed: %s", user_result)
                result = await seed_new_items(db)
                logger.info("Incremental item seed: %s", result)
                community_result = await seed_default_community(db)
                logger.info("Default community seed: %s", community_result)

        # Start Telegram bot if configured (skip placeholder tokens)
        if (settings.telegram_enabled
                and settings.telegram_bot_token
                and settings.telegram_bot_token not in ("", "SET_ON_SERVER")):
            from src.services.telegram_bot import bot
            app.state.telegram_bot_task = asyncio.create_task(bot.start())
            logger.info("Telegram bot started")
        elif settings.telegram_enabled:
            logger.warning("Telegram enabled but bot token not configured -- bot not started")

    @app.on_event("shutdown")
    async def shutdown():
        logger.info("BorrowHood shutting down...")
        # Stop Telegram bot if running
        if hasattr(app.state, "telegram_bot_task"):
            from src.services.telegram_bot import bot
            await bot.stop()
            app.state.telegram_bot_task.cancel()
            logger.info("Telegram bot stopped")

    return app


app = create_app()
