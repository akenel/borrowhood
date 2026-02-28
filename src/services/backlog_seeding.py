"""Seed initial BorrowHood backlog items.

Idempotent: checks if data exists before seeding.
"""

import logging
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.backlog import (
    BHBacklogItem, BacklogItemType, BacklogStatus, BacklogPriority,
)

logger = logging.getLogger("bh.backlog_seeding")

# ================================================================
# Seed Data -- real BorrowHood work items
# (item_type, status, priority, title, description, assigned_to, tags)
# ================================================================
SEED_ITEMS = [
    (
        BacklogItemType.FEATURE, BacklogStatus.DONE, BacklogPriority.HIGH,
        "Stats grid on homepage",
        "Show active listings, workshops, categories, reviews count on landing page.",
        "Tigs", "homepage,stats,ui",
    ),
    (
        BacklogItemType.IMPROVEMENT, BacklogStatus.DONE, BacklogPriority.MEDIUM,
        "Review dates and weighted scoring",
        "Add created_at display to reviews and weight scores by reviewer badge tier.",
        "Tigs", "reviews,reputation,scoring",
    ),
    (
        BacklogItemType.FEATURE, BacklogStatus.DONE, BacklogPriority.MEDIUM,
        "Skill categories and proficiency levels",
        "Add UserSkill model with category, self_rating, verified_by_count.",
        "Tigs", "skills,profile,model",
    ),
    (
        BacklogItemType.DEV_TASK, BacklogStatus.DONE, BacklogPriority.HIGH,
        "OIDC authentication with Keycloak",
        "Implement login/callback/logout with JWT cookie session (bh_session).",
        "Tigs", "auth,keycloak,oidc",
    ),
    (
        BacklogItemType.BUG_FIX, BacklogStatus.IN_PROGRESS, BacklogPriority.HIGH,
        "Sync keycloak_id to BHUser on first login",
        "Auto-provision BHUser from Keycloak JWT claims on first authenticated request.",
        "Tigs", "auth,user,sync",
    ),
    (
        BacklogItemType.FEATURE, BacklogStatus.PENDING, BacklogPriority.MEDIUM,
        "AI-generated item images (Pollinations)",
        "Generate placeholder images using Pollinations API when user lists an item without photos.",
        "Tigs", "ai,images,listing",
    ),
    (
        BacklogItemType.FEATURE, BacklogStatus.PENDING, BacklogPriority.MEDIUM,
        "Lockbox one-time pickup/return codes",
        "Generate 8-char alphanumeric codes for contactless item handoff.",
        "Tigs", "lockbox,rental,security",
    ),
    (
        BacklogItemType.DEV_TASK, BacklogStatus.IN_PROGRESS, BacklogPriority.HIGH,
        "Port QA Dashboard + Backlog Board",
        "Port HelixNet QA dashboard and backlog board to BorrowHood for judge demo.",
        "Tigs", "qa,backlog,port",
    ),
]


async def seed_backlog_data(db: AsyncSession) -> None:
    """Seed initial backlog items. Idempotent -- skips if data exists."""
    count_result = await db.execute(
        select(func.count()).select_from(BHBacklogItem)
    )
    existing_count = count_result.scalar() or 0

    if existing_count > 0:
        logger.info(f"Backlog already seeded ({existing_count} items). Skipping.")
        return

    for idx, (item_type, status, priority, title, description, assigned_to, tags) in enumerate(SEED_ITEMS, start=1):
        item = BHBacklogItem(
            item_number=idx,
            item_type=item_type,
            status=status,
            priority=priority,
            title=title,
            description=description,
            assigned_to=assigned_to,
            tags=tags,
            created_by="Angel",
        )
        db.add(item)

    await db.flush()
    logger.info(f"Backlog seeded: {len(SEED_ITEMS)} items")
