"""Database engine, session factory, and base model.

Uses SQLAlchemy 2.0 async patterns with PostgreSQL.
"""

import uuid
from datetime import datetime
from typing import AsyncGenerator, Optional

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=10,
    max_overflow=20,
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class BHBase:
    """Mixin for all BorrowHood models.

    Provides id (UUID), created_at, updated_at, and deleted_at (soft delete).
    Every BorrowHood table inherits this. No exceptions.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yields an async database session."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """Create all tables. Used for initial setup and testing."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def run_migrations():
    """Run lightweight schema migrations.

    Adds columns that create_all won't add to existing tables.
    Each statement is idempotent (ADD COLUMN IF NOT EXISTS).
    """
    migrations = [
        # 2026-03-03: identity fields for legends seed
        "ALTER TABLE bh_user ADD COLUMN IF NOT EXISTS date_of_birth DATE",
        "ALTER TABLE bh_user ADD COLUMN IF NOT EXISTS mother_name VARCHAR(200)",
        "ALTER TABLE bh_user ADD COLUMN IF NOT EXISTS father_name VARCHAR(200)",
        # 2026-03-03: ToS acceptance tracking
        "ALTER TABLE bh_user ADD COLUMN IF NOT EXISTS tos_accepted_at TIMESTAMPTZ",
        # 2026-03-03: minimum charge + team pricing for service/training listings
        "ALTER TABLE bh_listing ADD COLUMN IF NOT EXISTS minimum_charge FLOAT",
        "ALTER TABLE bh_listing ADD COLUMN IF NOT EXISTS per_person_rate FLOAT",
        "ALTER TABLE bh_listing ADD COLUMN IF NOT EXISTS max_participants INTEGER",
        "ALTER TABLE bh_listing ADD COLUMN IF NOT EXISTS group_discount_pct FLOAT",
        # 2026-03-03: Wave 2 legend workshop types
        "ALTER TYPE workshoptype ADD VALUE IF NOT EXISTS 'arena'",
        "ALTER TYPE workshoptype ADD VALUE IF NOT EXISTS 'camp'",
        "ALTER TYPE workshoptype ADD VALUE IF NOT EXISTS 'dock'",
        "ALTER TYPE workshoptype ADD VALUE IF NOT EXISTS 'dojo'",
        "ALTER TYPE workshoptype ADD VALUE IF NOT EXISTS 'forge'",
        "ALTER TYPE workshoptype ADD VALUE IF NOT EXISTS 'fortress'",
        "ALTER TYPE workshoptype ADD VALUE IF NOT EXISTS 'laboratory'",
        "ALTER TYPE workshoptype ADD VALUE IF NOT EXISTS 'lodge'",
        "ALTER TYPE workshoptype ADD VALUE IF NOT EXISTS 'observatory'",
        "ALTER TYPE workshoptype ADD VALUE IF NOT EXISTS 'palace'",
        "ALTER TYPE workshoptype ADD VALUE IF NOT EXISTS 'pavilion'",
        "ALTER TYPE workshoptype ADD VALUE IF NOT EXISTS 'study'",
    ]
    async with engine.begin() as conn:
        for sql in migrations:
            await conn.execute(__import__("sqlalchemy").text(sql))
