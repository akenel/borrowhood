"""Test configuration and fixtures.

Uses the real database with NullPool to avoid async connection issues.
Seed data must be loaded before running tests.
"""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.config import settings
from src.database import get_db
from src.main import app as _app

# Create a test engine with NullPool -- no connection reuse issues
_test_engine = create_async_engine(
    settings.database_url,
    echo=False,
    poolclass=NullPool,
)
_test_session = async_sessionmaker(_test_engine, class_=AsyncSession, expire_on_commit=False)


async def _get_test_db():
    """Test DB dependency -- uses NullPool engine."""
    async with _test_session() as session:
        try:
            yield session
        finally:
            await session.close()


# Override the DB dependency for all tests
_app.dependency_overrides[get_db] = _get_test_db


@pytest.fixture
async def client():
    """Async test client."""
    async with AsyncClient(
        transport=ASGITransport(app=_app),
        base_url="http://test",
        follow_redirects=False,
    ) as ac:
        yield ac
