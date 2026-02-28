"""Seed BorrowHood 9-phase QA testing checklist.

Idempotent: checks if data exists before seeding.
"""

import logging
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.qa import BHTestResult, TestStatus

logger = logging.getLogger("bh.qa_seeding")

# ================================================================
# BorrowHood 9-Phase Testing Checklist (~36 items)
# (phase, phase_name, sort_order, title, description)
# ================================================================
CHECKLIST = [
    # Phase 1: Homepage & Navigation (5 items)
    (1, "Homepage & Navigation", 1, "Open the homepage", "Open the BorrowHood URL and verify the landing page loads"),
    (1, "Homepage & Navigation", 2, "Stats grid visible", "Verify stats grid shows: active listings, workshops, categories, reviews"),
    (1, "Homepage & Navigation", 3, "Featured items display", "Verify up to 6 featured items appear with images and prices"),
    (1, "Homepage & Navigation", 4, "Navigation links work", "Click Home, Browse, List Item -- all navigate correctly"),
    (1, "Homepage & Navigation", 5, "Footer links visible", "Footer shows GitHub, Terms, Privacy links"),

    # Phase 2: Browse & Search (5 items)
    (2, "Browse & Search", 1, "Open browse page", "Navigate to /browse and verify item grid loads"),
    (2, "Browse & Search", 2, "Search by keyword", "Type a search term and verify results filter correctly"),
    (2, "Browse & Search", 3, "Filter by category", "Select a category from dropdown and verify items filter"),
    (2, "Browse & Search", 4, "Sort options work", "Change sort order (newest, oldest, name) and verify"),
    (2, "Browse & Search", 5, "Empty search shows message", "Search for nonsense term and verify empty state message"),

    # Phase 3: Item Detail & Reviews (4 items)
    (3, "Item Detail & Reviews", 1, "View item detail page", "Click an item from browse to open its detail page"),
    (3, "Item Detail & Reviews", 2, "Item info displays", "Verify name, description, condition, category, location shown"),
    (3, "Item Detail & Reviews", 3, "Listings section shows", "Verify active listings with price, type, availability dates"),
    (3, "Item Detail & Reviews", 4, "Owner workshop link works", "Click workshop owner link and verify profile page opens"),

    # Phase 4: Workshop Profiles (4 items)
    (4, "Workshop Profiles", 1, "View workshop profile", "Navigate to /workshop/{slug} and verify profile loads"),
    (4, "Workshop Profiles", 2, "Workshop info displays", "Verify workshop name, type, tagline, bio, avatar/banner"),
    (4, "Workshop Profiles", 3, "Skills and languages show", "Verify skills list and language proficiencies display"),
    (4, "Workshop Profiles", 4, "Workshop items listed", "Verify the workshop's items appear with media"),

    # Phase 5: Keycloak Login (4 items)
    (5, "Keycloak Login", 1, "Click login button", "Click the Login button in navigation bar"),
    (5, "Keycloak Login", 2, "Keycloak login page loads", "Verify redirect to Keycloak login with BorrowHood branding"),
    (5, "Keycloak Login", 3, "Enter credentials and sign in", "Enter test credentials and click Sign In"),
    (5, "Keycloak Login", 4, "Redirect back to app", "Verify redirect back to BorrowHood with user logged in (username shows in nav)"),

    # Phase 6: Dashboard (4 items)
    (6, "Dashboard", 1, "Navigate to dashboard", "Click Dashboard link (visible only when logged in)"),
    (6, "Dashboard", 2, "My items section", "Verify your listed items appear with media and listing status"),
    (6, "Dashboard", 3, "My rentals section", "Verify outgoing rental requests show with status badges"),
    (6, "Dashboard", 4, "Incoming requests section", "Verify incoming rental requests on your items show"),

    # Phase 7: List Item + AI (4 items)
    (7, "List Item + AI", 1, "Open list item page", "Navigate to /list and verify the form loads"),
    (7, "List Item + AI", 2, "Fill out item details", "Enter name, description, category, condition, price"),
    (7, "List Item + AI", 3, "AI description generation", "Test AI-assisted description generation if available"),
    (7, "List Item + AI", 4, "Submit and verify", "Submit the item and verify it appears in browse/dashboard"),

    # Phase 8: Rental Flow (3 items)
    (8, "Rental Flow", 1, "Request a rental", "Click Rent on a listing and submit a rental request"),
    (8, "Rental Flow", 2, "Check rental status", "Verify rental appears in dashboard with pending status"),
    (8, "Rental Flow", 3, "Notification received", "Check notifications bell for rental-related notification"),

    # Phase 9: i18n Bilingual (3 items)
    (9, "i18n Bilingual", 1, "Switch to Italian", "Click IT language toggle and verify page switches to Italian"),
    (9, "i18n Bilingual", 2, "Navigation in Italian", "Verify all nav items display in Italian (Esplora, Bacheca, etc.)"),
    (9, "i18n Bilingual", 3, "Switch back to English", "Click EN toggle and verify everything switches back to English"),
]


async def seed_qa_checklist(db: AsyncSession) -> None:
    """Seed the QA testing checklist. Idempotent -- skips if data exists."""
    count_result = await db.execute(
        select(func.count()).select_from(BHTestResult)
    )
    existing_count = count_result.scalar() or 0

    if existing_count > 0:
        logger.info(f"QA checklist already seeded ({existing_count} items). Skipping.")
        return

    for phase, phase_name, sort_order, title, description in CHECKLIST:
        test_item = BHTestResult(
            phase=phase,
            phase_name=phase_name,
            sort_order=sort_order,
            title=title,
            description=description,
            status=TestStatus.PENDING,
        )
        db.add(test_item)

    await db.flush()
    logger.info(f"QA testing checklist seeded: {len(CHECKLIST)} items across 9 phases")
