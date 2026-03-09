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
    # ================================================================
    # BL-077 through BL-088: Competitive gap features (March 8, 2026)
    # ================================================================
    (
        BacklogItemType.FEATURE, BacklogStatus.DONE, BacklogPriority.CRITICAL,
        "In-app messaging -- buyer/seller chat",
        "Threaded conversations between users. Thread list inbox, real-time polling, chat bubbles, unread badge in nav. Tied to listings/rentals.",
        "Tigs", "messaging,chat,marketplace",
    ),
    (
        BacklogItemType.FEATURE, BacklogStatus.DONE, BacklogPriority.HIGH,
        "Review photos -- upload images with reviews",
        "Up to 3 photos per review (JPEG/PNG/WebP, 5MB max). PostgreSQL ARRAY column, upload endpoint, gallery display.",
        "Tigs", "reviews,photos,ugc",
    ),
    (
        BacklogItemType.FEATURE, BacklogStatus.DONE, BacklogPriority.MEDIUM,
        "Recently viewed items -- browsing history strip",
        "localStorage-based tracking, horizontal scroll strip on item detail page. Zero DB overhead, pure client-side.",
        "Tigs", "browse,ux,history",
    ),
    (
        BacklogItemType.FEATURE, BacklogStatus.DONE, BacklogPriority.HIGH,
        "Listing Q&A -- public questions and answers",
        "Buyers ask questions on listings, sellers answer publicly. Visible to all. Notifications on new questions and answers.",
        "Tigs", "listings,qa,marketplace",
    ),
    (
        BacklogItemType.FEATURE, BacklogStatus.DONE, BacklogPriority.MEDIUM,
        "Saved items / Wishlist (favorites)",
        "Heart icon on listings, localStorage favorites list, dedicated favorites page.",
        "Tigs", "favorites,wishlist,ux",
    ),
    (
        BacklogItemType.FEATURE, BacklogStatus.DONE, BacklogPriority.HIGH,
        "Full order history page",
        "All past purchases, rentals, sales. Filter by role/status/sort. Pagination. Lifetime earnings header.",
        "Tigs", "orders,history,marketplace",
    ),
    (
        BacklogItemType.FEATURE, BacklogStatus.PENDING, BacklogPriority.MEDIUM,
        "Seller dashboard with earnings analytics",
        "Revenue charts, top items, rental frequency, monthly breakdown. React-style dashboard for power sellers.",
        "Tigs", "dashboard,analytics,seller",
    ),
    (
        BacklogItemType.FEATURE, BacklogStatus.DONE, BacklogPriority.LOW,
        "Social sharing previews (Open Graph meta tags)",
        "OG image, title, description for items and workshops. Rich previews on WhatsApp, Telegram, Facebook. Implemented in base.html.",
        "Tigs", "seo,sharing,social",
    ),
    (
        BacklogItemType.IMPROVEMENT, BacklogStatus.PENDING, BacklogPriority.MEDIUM,
        "Advanced search -- filters, autocomplete, suggestions",
        "Price range slider, condition filter, distance sort, typeahead suggestions from item names.",
        "Tigs", "search,browse,ux",
    ),
    (
        BacklogItemType.FEATURE, BacklogStatus.PENDING, BacklogPriority.MEDIUM,
        "Multi-image listings (up to 10 photos per item)",
        "Gallery carousel on item detail. Drag-to-reorder. Thumbnail strip. Zoom on click.",
        "Tigs", "listings,photos,gallery",
    ),
    (
        BacklogItemType.IMPROVEMENT, BacklogStatus.DONE, BacklogPriority.MEDIUM,
        "Email notifications for key events",
        "Keycloak handles verification + password reset emails via MailHog. App notifications via Telegram bot.",
        "Tigs", "notifications,email,comms",
    ),
    (
        BacklogItemType.FEATURE, BacklogStatus.PENDING, BacklogPriority.LOW,
        "Rental calendar / availability picker",
        "Visual calendar showing booked dates. Date range picker for rental requests. Prevents double-booking.",
        "Tigs", "rentals,calendar,availability",
    ),
    # ================================================================
    # BL-089 through BL-095: Security & anti-sabotage (March 8, 2026)
    # From voice recording: "safe fair play"
    # ================================================================
    (
        BacklogItemType.DEV_TASK, BacklogStatus.DONE, BacklogPriority.HIGH,
        "Rate limiting -- FastAPI middleware",
        "120 req/min GET, 20 req/min POST per IP + per-user throttle (messages 50/hr, items 10/hr, listings 20/hr, Q&A 20/hr, reports 10/hr). Zero dependencies.",
        "Tigs", "security,rate-limit,middleware",
    ),
    (
        BacklogItemType.DEV_TASK, BacklogStatus.PENDING, BacklogPriority.HIGH,
        "Cloudflare DNS + DDoS protection",
        "Free tier: L3/L4 DDoS protection, bot detection, SSL. Put in front of Traefik. Requires real domain name.",
        "Angel", "security,cloudflare,infrastructure",
    ),
    (
        BacklogItemType.FEATURE, BacklogStatus.DONE, BacklogPriority.HIGH,
        "Email verification on signup",
        "Keycloak verifyEmail=true + MailHog SMTP on Hetzner. New users must verify email. GitHub/Google OAuth users auto-verified (trustEmail=true).",
        "Tigs", "security,auth,email",
    ),
    (
        BacklogItemType.FEATURE, BacklogStatus.PENDING, BacklogPriority.MEDIUM,
        "hCaptcha on registration",
        "Privacy-respecting CAPTCHA (not Google). Blocks automated signups and bot accounts.",
        "Tigs", "security,captcha,auth",
    ),
    (
        BacklogItemType.FEATURE, BacklogStatus.PENDING, BacklogPriority.MEDIUM,
        "Account age gate for reviews",
        "New accounts cannot leave reviews for 48 hours. Prevents day-one reputation bombing attacks.",
        "Tigs", "security,reviews,trust",
    ),
    (
        BacklogItemType.DEV_TASK, BacklogStatus.PENDING, BacklogPriority.MEDIUM,
        "Auto IP ban on repeated rate limit violations",
        "Track IPs that trigger rate limits >5 times in 10 minutes. Auto-ban for 24h. Log to audit trail.",
        "Tigs", "security,ip-ban,automation",
    ),
    (
        BacklogItemType.DEV_TASK, BacklogStatus.DONE, BacklogPriority.HIGH,
        "Real domain name + Let's Encrypt SSL",
        "borrowhood.duckdns.org (DuckDNS free). Caddy auto-provisions Let's Encrypt TLS. Geolocation works. Google OAuth unblocked.",
        "Angel+Tigs", "infrastructure,domain,ssl",
    ),
    # ================================================================
    # BL-096 through BL-097: Revenue & monetization (March 8, 2026)
    # From voice recording: "ads and affiliates"
    # ================================================================
    (
        BacklogItemType.FEATURE, BacklogStatus.PENDING, BacklogPriority.LOW,
        "Affiliate program -- footer partner links",
        "Non-intrusive affiliate links at bottom of pages. Quality partners only (e.g. Manufactum). Revenue share tracking.",
        "Angel", "revenue,affiliates,monetization",
    ),
    (
        BacklogItemType.FEATURE, BacklogStatus.PENDING, BacklogPriority.LOW,
        "Seller promoted listings / premium placement",
        "Sellers pay for featured placement on browse page. Internal advertisers like Nino (Camper & Tour). Revenue source.",
        "Angel", "revenue,advertising,marketplace",
    ),
    # ================================================================
    # BL-098: Activity tracking (March 8, 2026) -- DONE
    # From voice recording: "extra activity"
    # ================================================================
    (
        BacklogItemType.FEATURE, BacklogStatus.DONE, BacklogPriority.MEDIUM,
        "Last seen / online indicator on profiles",
        "Shows 'online now', 'seen 5m ago', 'seen 2d ago' on member cards and workshop pages. Stamps last_active_at on every auth request.",
        "Tigs", "activity,profiles,ux",
    ),
    (
        BacklogItemType.FEATURE, BacklogStatus.DONE, BacklogPriority.MEDIUM,
        "Telegram/email communication channel icons",
        "Show TG icon (sky blue) and email icon on member cards and workshop pages. Indicates preferred contact method.",
        "Tigs", "comms,telegram,profiles",
    ),
    # ================================================================
    # BL-100: Geolocation fallback (March 8, 2026) -- DONE
    # ================================================================
    (
        BacklogItemType.BUG_FIX, BacklogStatus.DONE, BacklogPriority.MEDIUM,
        "Geolocation fallback to Trapani when browser denies permission",
        "Browser denies navigator.geolocation on HTTP/bare IP (no HTTPS domain). "
        "Added Trapani centro (38.017, 12.514) as fallback in members.html and onboarding.html. "
        "Permanent fix: BL-095 (real domain + Let's Encrypt SSL).",
        "Tigs", "geolocation,fallback,ux",
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
