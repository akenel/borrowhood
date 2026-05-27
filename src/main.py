"""BorrowHood FastAPI application.

Community rental, sales, and services platform.
"Rent it. Lend it. Share it. Teach it."
"""

import asyncio
import logging

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import async_session, create_tables, get_db
from src.middleware.rate_limit import RateLimitMiddleware
from src.routers import ai, analytics, auth, badges, bids, communities, delivery, deposits, disputes, events, health, helpboard, insurance, invoices, items, listing_qa, listings, lockbox, mentorships, messages, notifications, onboarding, pages, payments, raffles, rentals, reports, reviews, saved_searches, service_quotes, skills, telegram, translation, users
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

    # Rate limiting (BL-089) -- 120 reads/min, 20 writes/min per IP
    app.add_middleware(RateLimitMiddleware, read_limit=120, write_limit=20, window_seconds=60)

    # Silent token refresh middleware -- sets new cookies when token is refreshed
    from starlette.middleware.base import BaseHTTPMiddleware

    class TokenRefreshMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            response = await call_next(request)
            # If the dependency refreshed the token, update the cookies
            if hasattr(request.state, "new_access_token") and request.state.new_access_token:
                response.set_cookie(
                    "bh_session",
                    request.state.new_access_token,
                    max_age=getattr(request.state, "token_expires_in", 3600),
                    httponly=True,
                    samesite="lax",
                    secure=not settings.debug,
                )
                if getattr(request.state, "new_refresh_token", None):
                    response.set_cookie(
                        "bh_refresh",
                        request.state.new_refresh_token,
                        max_age=getattr(request.state, "refresh_expires_in", 7200),
                        httponly=True,
                        samesite="lax",
                        secure=not settings.debug,
                    )
            return response

    app.add_middleware(TokenRefreshMiddleware)

    # Content-Language header -- tells Chrome/Firefox the page language so
    # browser auto-translate doesn't offer to translate to the same language.
    # Combined with <html translate="no"> this is the strongest server-side
    # signal we can give. User-side: people whose browser is set to a different
    # language still control via "always translate this site" preference.
    class ContentLanguageMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            response = await call_next(request)
            ctype = response.headers.get("content-type", "")
            if "text/html" in ctype.lower() and "content-language" not in {k.lower() for k in response.headers.keys()}:
                lang_cookie = request.cookies.get("bh_lang")
                lang = lang_cookie if lang_cookie in ("en", "it") else "en"
                response.headers["Content-Language"] = lang
            return response

    app.add_middleware(ContentLanguageMiddleware)

    # JSON-only error middleware for /api/v1/* (April 27 incident lesson):
    # When the DB went into recovery mode, AI endpoints returned an HTML
    # 500 page; the frontend tried to JSON.parse() it and surfaced a
    # cryptic "Unexpected token 'I'... is not valid JSON" toast. Now any
    # unhandled exception under /api/v1/* gets a JSON response the client
    # can show as a normal toast. Implemented as middleware (not an
    # @app.exception_handler) because BaseHTTPMiddleware swallows
    # downstream exceptions before FastAPI's handler chain runs.
    from fastapi.responses import JSONResponse, HTMLResponse

    class JsonErrorMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            try:
                return await call_next(request)
            except Exception as exc:
                logger.exception(
                    "Unhandled %s on %s: %s",
                    type(exc).__name__, request.url.path, exc,
                )
                if request.url.path.startswith("/api/v1/"):
                    return JSONResponse(
                        status_code=500,
                        content={"detail": "Server is temporarily unavailable. Please try again."},
                    )
                return HTMLResponse(
                    status_code=500,
                    content="<h1>Something went wrong</h1><p>We're looking into it. <a href='/'>Back to La Piazza</a></p>",
                )

    app.add_middleware(JsonErrorMiddleware)

    # Task #32: force browsers to revalidate /static/* via etag instead of
    # caching aggressively. Without this header, prod responses had no
    # Cache-Control at all, so Firefox heuristically cached JS for hours --
    # the M2 comment-thread deploy (2026-05-23) shipped, the HTML page
    # reloaded fine, but the JS was still the pre-deploy version, and the
    # button silently stayed disabled. "no-cache, must-revalidate" means
    # browsers can use their cache but MUST send If-None-Match first; the
    # server returns 304 if unchanged (cheap) or 200 with new bytes if
    # deployed. Zero risk of stale code surviving a deploy.
    class StaticCacheControlMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            response = await call_next(request)
            if request.url.path.startswith("/static/"):
                response.headers["Cache-Control"] = "no-cache, must-revalidate"
            return response

    app.add_middleware(StaticCacheControlMiddleware)

    # Favicon at root (browsers request /favicon.ico directly)
    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon():
        return FileResponse("src/static/favicon.ico", media_type="image/x-icon")

    # PWA manifest at root, served with the correct content-type. StaticFiles
    # serves /static/manifest.json as application/json, but Chrome's WebAPK
    # minter wants application/manifest+json -- a wrong type contributes to a
    # non-compliant WebAPK (Fred's "built for older Android" Play Protect
    # warning). Serving from a dedicated route guarantees the right header.
    @app.get("/manifest.webmanifest", include_in_schema=False)
    @app.get("/manifest.json", include_in_schema=False)
    async def manifest():
        return FileResponse("src/static/manifest.json", media_type="application/manifest+json")

    # Static files
    app.mount("/static", StaticFiles(directory="src/static"), name="static")

    # API routers
    app.include_router(health.router)
    app.include_router(items.router)
    app.include_router(listings.router)
    app.include_router(events.router)
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
    app.include_router(delivery.router)
    app.include_router(reports.router)
    app.include_router(helpboard.router)
    app.include_router(skills.router)
    app.include_router(saved_searches.router)
    app.include_router(invoices.router)
    app.include_router(invoices.view_router)
    app.include_router(users.router)
    app.include_router(service_quotes.router)
    app.include_router(telegram.router)
    app.include_router(translation.router)
    app.include_router(insurance.router)
    app.include_router(communities.router)
    app.include_router(listing_qa.router)
    app.include_router(messages.router)
    app.include_router(mentorships.router)
    app.include_router(raffles.router)
    app.include_router(analytics.router)

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

        # Schema setup runs on EVERY env, not just debug. (2026-05-27: staging
        # runs BH_DEBUG=false, so run_migrations() -- which CREATEs the pg_trgm
        # extension fuzzy search needs -- never ran there, and /browse?q=... 500'd
        # while prod (debug=true) was fine. Gating idempotent migrations behind
        # debug let staging silently drift from the schema. Decoupled so every
        # env self-heals. create_all + run_migrations are both idempotent;
        # prod already ran them via debug=true, so prod behavior is unchanged.)
        await create_tables()
        logger.info("Database tables created/verified")
        from src.database import run_migrations
        try:
            await run_migrations()
            logger.info("Schema migrations applied")
        except Exception:
            logger.exception("run_migrations failed -- continuing startup")

        # Seeding stays debug-only (don't reseed real envs on every boot).
        if settings.debug:
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

        # Start commitment expiry background task
        from src.services.commitment_expiry import run_expiry_loop
        app.state.expiry_task = asyncio.create_task(run_expiry_loop())
        logger.info("Commitment expiry loop started")

        # Start event auto-attendance background task
        from src.services.event_attendance import run_attendance_loop
        app.state.attendance_task = asyncio.create_task(run_attendance_loop())
        logger.info("Event auto-attendance loop started")

        # Start raffle ticket expiry background task
        from src.services.raffle_engine import run_raffle_expiry_loop
        app.state.raffle_expiry_task = asyncio.create_task(run_raffle_expiry_loop())
        logger.info("Raffle expiry loop started")

    @app.on_event("shutdown")
    async def shutdown():
        logger.info("BorrowHood shutting down...")
        # Stop expiry loop
        if hasattr(app.state, "expiry_task"):
            app.state.expiry_task.cancel()
            logger.info("Commitment expiry loop stopped")
        # Stop auto-attendance loop
        if hasattr(app.state, "attendance_task"):
            app.state.attendance_task.cancel()
            logger.info("Event auto-attendance loop stopped")
        # Stop raffle expiry loop
        if hasattr(app.state, "raffle_expiry_task"):
            app.state.raffle_expiry_task.cancel()
            logger.info("Raffle expiry loop stopped")
        # Stop Telegram bot if running
        if hasattr(app.state, "telegram_bot_task"):
            from src.services.telegram_bot import bot
            await bot.stop()
            app.state.telegram_bot_task.cancel()
            logger.info("Telegram bot stopped")

    return app


app = create_app()
