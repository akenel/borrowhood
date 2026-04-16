"""Test configuration and fixtures.

Uses the real database with NullPool to avoid async connection issues.
Rate limiter is disabled for tests to prevent 429 false failures.
Seed data must be loaded before running tests.

DB-dependent tests are auto-skipped when the database is unreachable.
"""

import asyncio
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.config import settings
from src.database import get_db
from src.main import app as _app
from src.middleware.rate_limit import RateLimitMiddleware

# Create a test engine with NullPool -- no connection reuse issues
_test_engine = create_async_engine(
    settings.database_url,
    echo=False,
    poolclass=NullPool,
)
_test_session = async_sessionmaker(_test_engine, class_=AsyncSession, expire_on_commit=False)


# Check DB availability once at import time
def _check_db():
    """Return True if the database is reachable."""
    async def _probe():
        try:
            async with _test_engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
                return True
        except Exception:
            return False
    try:
        return asyncio.get_event_loop().run_until_complete(_probe())
    except RuntimeError:
        return asyncio.run(_probe())


DB_AVAILABLE = _check_db()


async def _get_test_db():
    """Test DB dependency -- uses NullPool engine."""
    async with _test_session() as session:
        try:
            yield session
        finally:
            await session.close()


# Override the DB dependency for all tests
_app.dependency_overrides[get_db] = _get_test_db

# Disable rate limiter for tests -- prevents 429 false failures
_app.user_middleware = [
    m for m in _app.user_middleware
    if m.cls is not RateLimitMiddleware
]
_app.middleware_stack = _app.build_middleware_stack()


@pytest.fixture
async def client():
    """Async test client with rate limiting disabled."""
    async with AsyncClient(
        transport=ASGITransport(app=_app),
        base_url="http://test",
        follow_redirects=False,
    ) as ac:
        yield ac


@pytest.fixture
async def db_client(client):
    """Test client that requires a live database. Auto-skips if DB unavailable."""
    if not DB_AVAILABLE:
        pytest.skip("Database not reachable")
    yield client


def pytest_collection_modifyitems(items):
    """Auto-skip tests that need a live DB when it's not reachable.

    Any test that uses the `client` fixture AND hits a DB endpoint
    will get OSError. We detect this by checking if the test previously
    failed with OSError and skip proactively based on DB_AVAILABLE.
    """
    if DB_AVAILABLE:
        return  # DB is up, run everything

    # These test files contain tests that hit DB endpoints via the ASGI client.
    # When DB is down, they raise OSError. Skip them cleanly instead.
    db_test_files = {
        "test_api_items.py",
        "test_api_listings.py",
        "test_api_reviews.py",
        "test_api_badges.py",
        "test_api_bids.py",
        "test_api_edge_cases.py",
        "test_raffles.py",
    }

    skip_marker = pytest.mark.skip(reason="Database not reachable -- skipping DB-dependent test")
    for item in items:
        filename = item.path.name if hasattr(item, 'path') else ""
        if filename in db_test_files:
            item.add_marker(skip_marker)
