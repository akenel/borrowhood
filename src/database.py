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
        # 2026-03-03: Stripe Connect marketplace payouts
        "ALTER TABLE bh_user ADD COLUMN IF NOT EXISTS stripe_account_id VARCHAR(200)",
        "ALTER TABLE bh_payment ADD COLUMN IF NOT EXISTS platform_fee FLOAT",
        "ALTER TABLE bh_payment ADD COLUMN IF NOT EXISTS seller_payout_amount FLOAT",
        # 2026-03-03: Multi-community federation
        "ALTER TABLE bh_user ADD COLUMN IF NOT EXISTS default_community_id UUID REFERENCES bh_community(id)",
        "ALTER TABLE bh_item ADD COLUMN IF NOT EXISTS community_id UUID REFERENCES bh_community(id)",
        # 2026-03-08: Review photos (up to 3 URLs per review)
        "ALTER TABLE bh_review ADD COLUMN IF NOT EXISTS photo_urls TEXT[]",
        # 2026-03-08: Activity tracking
        "ALTER TABLE bh_user ADD COLUMN IF NOT EXISTS last_active_at TIMESTAMPTZ",
        # 2026-03-13: Message edit tracking
        "ALTER TABLE bh_message ADD COLUMN IF NOT EXISTS edited_at TIMESTAMPTZ",
        # 2026-04-09: Events feature
        "ALTER TABLE bh_listing ADD COLUMN IF NOT EXISTS event_start TIMESTAMPTZ",
        "ALTER TABLE bh_listing ADD COLUMN IF NOT EXISTS event_end TIMESTAMPTZ",
        "ALTER TABLE bh_listing ADD COLUMN IF NOT EXISTS event_venue VARCHAR(200)",
        "ALTER TABLE bh_listing ADD COLUMN IF NOT EXISTS event_address VARCHAR(500)",
        "ALTER TABLE bh_user ADD COLUMN IF NOT EXISTS organization_description TEXT",
        # 2026-04-11: Online event link
        "ALTER TABLE bh_listing ADD COLUMN IF NOT EXISTS event_link VARCHAR(1000)",
        # 2026-04-09: Index for event date queries
        "CREATE INDEX IF NOT EXISTS idx_listing_event_start ON bh_listing (event_start) WHERE event_start IS NOT NULL",
        # 2026-04-11: Google avatar URLs can be 1000+ chars
        "ALTER TABLE bh_user ALTER COLUMN avatar_url TYPE VARCHAR(2000)",
        # 2026-04-09: No-show tracking
        "ALTER TABLE bh_user ADD COLUMN IF NOT EXISTS no_show_count INTEGER DEFAULT 0",
        # 2026-04-10: Event gamification
        "ALTER TABLE bh_user_points ADD COLUMN IF NOT EXISTS events_attended INTEGER DEFAULT 0",
        "ALTER TABLE bh_user_points ADD COLUMN IF NOT EXISTS events_hosted INTEGER DEFAULT 0",
        "ALTER TABLE bh_user_points ADD COLUMN IF NOT EXISTS event_streak INTEGER DEFAULT 0",
        "ALTER TABLE bh_user_points ADD COLUMN IF NOT EXISTS best_streak INTEGER DEFAULT 0",
        "ALTER TABLE bh_user_points ADD COLUMN IF NOT EXISTS challenges_completed INTEGER DEFAULT 0",
        # 2026-04-15: Featured video on workshop (YouTube/Vimeo/TikTok URL)
        "ALTER TABLE bh_user ADD COLUMN IF NOT EXISTS featured_video_url VARCHAR(500)",
        # 2026-04-17: Raffle vouch privilege (admin-granted, not from badge tier)
        "ALTER TABLE bh_user ADD COLUMN IF NOT EXISTS can_vouch_raffles BOOLEAN DEFAULT FALSE",
        # 2026-04-17: Raffle gamification columns (added after initial table creation)
        "ALTER TABLE bh_raffle ADD COLUMN IF NOT EXISTS verifications_positive INTEGER DEFAULT 0",
        "ALTER TABLE bh_raffle ADD COLUMN IF NOT EXISTS verifications_negative INTEGER DEFAULT 0",
    ]
    # ALTER TYPE ... ADD VALUE -- SQLAlchemy uses enum .name (UPPERCASE) for PG enums
    enum_migrations = [
        "ALTER TYPE notificationtype ADD VALUE IF NOT EXISTS 'MESSAGE_RECEIVED'",
        "ALTER TYPE workshoptype ADD VALUE IF NOT EXISTS 'ARENA'",
        "ALTER TYPE workshoptype ADD VALUE IF NOT EXISTS 'CAMP'",
        "ALTER TYPE workshoptype ADD VALUE IF NOT EXISTS 'DOCK'",
        "ALTER TYPE workshoptype ADD VALUE IF NOT EXISTS 'DOJO'",
        "ALTER TYPE workshoptype ADD VALUE IF NOT EXISTS 'FORGE'",
        "ALTER TYPE workshoptype ADD VALUE IF NOT EXISTS 'FORTRESS'",
        "ALTER TYPE workshoptype ADD VALUE IF NOT EXISTS 'LABORATORY'",
        "ALTER TYPE workshoptype ADD VALUE IF NOT EXISTS 'LODGE'",
        "ALTER TYPE workshoptype ADD VALUE IF NOT EXISTS 'OBSERVATORY'",
        "ALTER TYPE workshoptype ADD VALUE IF NOT EXISTS 'PALACE'",
        "ALTER TYPE workshoptype ADD VALUE IF NOT EXISTS 'PAVILION'",
        "ALTER TYPE workshoptype ADD VALUE IF NOT EXISTS 'STUDY'",
        # 2026-04-09: Events feature
        "ALTER TYPE listingtype ADD VALUE IF NOT EXISTS 'EVENT'",
        "ALTER TYPE itemcategory ADD VALUE IF NOT EXISTS 'WORKSHOP_EVENT'",
        "ALTER TYPE itemcategory ADD VALUE IF NOT EXISTS 'GARAGE_SALE'",
        "ALTER TYPE itemcategory ADD VALUE IF NOT EXISTS 'CONCERT'",
        "ALTER TYPE itemcategory ADD VALUE IF NOT EXISTS 'ART_SHOW'",
        "ALTER TYPE itemcategory ADD VALUE IF NOT EXISTS 'COMMUNITY_MEETUP'",
        "ALTER TYPE itemcategory ADD VALUE IF NOT EXISTS 'SPORTS_EVENT'",
        "ALTER TYPE itemcategory ADD VALUE IF NOT EXISTS 'MARKET'",
        "ALTER TYPE itemcategory ADD VALUE IF NOT EXISTS 'FESTIVAL'",
        "ALTER TYPE rsvpstatus ADD VALUE IF NOT EXISTS 'NO_SHOW'",
        # 2026-04-16: Raffle feature
        "ALTER TYPE listingtype ADD VALUE IF NOT EXISTS 'RAFFLE'",
    ]
    # Fix any previously added lowercase values by renaming to UPPERCASE
    rename_fixes = [
        "ALTER TYPE workshoptype RENAME VALUE 'arena' TO 'ARENA'",
        "ALTER TYPE workshoptype RENAME VALUE 'camp' TO 'CAMP'",
        "ALTER TYPE workshoptype RENAME VALUE 'dock' TO 'DOCK'",
        "ALTER TYPE workshoptype RENAME VALUE 'dojo' TO 'DOJO'",
        "ALTER TYPE workshoptype RENAME VALUE 'forge' TO 'FORGE'",
        "ALTER TYPE workshoptype RENAME VALUE 'fortress' TO 'FORTRESS'",
        "ALTER TYPE workshoptype RENAME VALUE 'laboratory' TO 'LABORATORY'",
        "ALTER TYPE workshoptype RENAME VALUE 'lodge' TO 'LODGE'",
        "ALTER TYPE workshoptype RENAME VALUE 'observatory' TO 'OBSERVATORY'",
        "ALTER TYPE workshoptype RENAME VALUE 'palace' TO 'PALACE'",
        "ALTER TYPE workshoptype RENAME VALUE 'pavilion' TO 'PAVILION'",
        "ALTER TYPE workshoptype RENAME VALUE 'study' TO 'STUDY'",
    ]
    import sqlalchemy as sa
    async with engine.begin() as conn:
        for sql in migrations:
            await conn.execute(sa.text(sql))
    # Enum type extensions need autocommit (PG restriction)
    async with engine.connect() as conn:
        await conn.execution_options(isolation_level="AUTOCOMMIT")
        # First try renaming lowercase -> UPPERCASE (from previous bad migration)
        for sql in rename_fixes:
            try:
                await conn.execute(sa.text(sql))
            except Exception:
                pass  # Value doesn't exist or already uppercase
        # Then add any missing UPPERCASE values
        for sql in enum_migrations:
            try:
                await conn.execute(sa.text(sql))
            except Exception:
                pass  # Already exists
