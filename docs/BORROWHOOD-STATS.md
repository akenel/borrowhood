# BorrowHood -- Project Stats

**Measured March 1, 2026 from live Hetzner UAT server + local source.**

---

## Codebase

| Metric | Count |
|--------|------:|
| Python source files | 75 |
| Python lines of code | 10,430 |
| HTML templates | 18 |
| HTML lines | 6,144 |
| Test files | 23 |
| Test functions | 250 |
| Test lines of code | 2,221 |
| Custom SVG illustrations | 20 |
| Total source files | 241 |
| Total lines of code | ~18,800 |

## Architecture

| Component | Count |
|-----------|------:|
| Database tables (SQLAlchemy) | 31 |
| Enums (typed, no magic strings) | 36 |
| REST API endpoints | 104 |
| Router modules | 23 |
| Schema modules (Pydantic) | 10 |
| Service modules | 12 |
| Jinja2 page templates | 18 |
| i18n translatable strings | 474 (EN + IT) |
| i18n locale sections | 32 |

## Live Data (Hetzner UAT)

| What | Count |
|------|------:|
| Keycloak realm users | 11 |
| App user profiles | 12 |
| Items live | 50 |
| Items in seed bank | 119 |
| Active listings | 50 |
| Item categories | 21 |
| Unique brands | 28 |
| Listing types active | 3 (rent, training, service) |
| Backlog items tracked | 15 |
| QA test cases defined | 36 |

## Listing Breakdown (Live)

| Type | Count | Price Range (EUR) |
|------|------:|-------------------|
| Rent | 40 | 8 -- 60 /day |
| Training | 9 | 15 -- 60 /session |
| Service | 1 | 80 /session |

## Item Categories (Live)

water_sports (5), kitchen (4), camping (3), drones (3), welding (3), furniture (3), computers (3), cycling (3), hand_tools (3), power_tools (2), photography (2), music (2), garden (2), automotive (2), woodworking (2), sports (2), other (2), electronics (1), home_improvement (1), art (1), sewing (1)

## Item Types (Seed Bank)

| Type | Count |
|------|------:|
| Physical goods | 84 |
| Services | 22 |
| Spaces | 8 |
| Made-to-order | 4 |
| Digital | 1 |

## Database Tables (31)

BHUser, BHUserLanguage, BHUserSkill, BHUserPoints, BHUserSocialLink, BHUserFavorite, BHItem, BHItemMedia, BHListing, BHRental, BHBid, BHDeposit, BHDispute, BHReview, BHPayment, BHNotification, BHBadge, BHLockBoxAccess, BHReport, BHTelegramLink, BHContentTranslation, BHWorkshopMember, BHAuditLog, BHHelpPost, BHHelpReply, BHTestResult, BHBugReport, BHBugActivity, BHBugCommit, BHBacklogItem, BHBacklogActivity

## Router Modules (23)

auth, items, listings, rentals, bids, deposits, disputes, payments, reviews, lockbox, badges, notifications, helpboard, onboarding, ai, telegram, qa, backlog, reports, users, pages, health, demo

## Service Modules (12)

seeding (621 lines), ai (382 lines), badges (245 lines), telegram_bot (222 lines), paypal (192 lines), search (118 lines), notify (98 lines), qa_seeding (97 lines), backlog_seeding (97 lines), reputation (90 lines), lockbox (49 lines), notification (48 lines)

## Integrations

| Integration | What It Does |
|-------------|-------------|
| Keycloak OIDC | Login/callback/logout, JWT cookie sessions, RS256 verification, 6 realm roles |
| Telegram bot | Link accounts, receive rental/bid/dispute notifications via Telegram |
| AI (Pollinations) | Generate listing descriptions, item images, skill bios |
| PayPal REST v2 | Create order, buyer approval, capture payment, refund |
| Lockbox | One-time 8-char codes for contactless pickup/return |
| Badge system | Points, tiers (newcomer/trusted/pillar/legend), weighted review scoring |

## Pages (18)

| Page | Alpine.js Bindings | Auth Required |
|------|-----------:|:---:|
| home | 20 | No |
| browse | 14 | No |
| members | 16 | No |
| terms | -- | No |
| helpboard | 20 | No |
| item_detail | 45 | No |
| workshop | 14 | No |
| dashboard | 62 | Yes |
| profile | 6 | Yes |
| list_item | 33 | Yes |
| onboarding | 19 | Yes |
| testing | 49 | Yes |
| backlog | 34 | Yes |
| demo_login | 4 | No |
| 404 error | -- | No |
| 500 error | -- | No |
| base layout | 20 | -- |
| workshop export | -- | Yes |

## User Profiles (Live)

| Name | Workshop | City | Badge Tier |
|------|----------|------|------------|
| Sara Ferretti | Pedala Sicilia | Castellammare del Golfo | trusted |
| Andrea Ferretti | Blu Trapani Watersports | Custonaci | trusted |
| Fabio Ferretti | Avventura Sicilia | San Vito lo Capo | trusted |
| Pietro Ferretti | SkyView Sicilia | Scopello | trusted |
| Vittorio Ferretti | -- | Bonagia | pillar |
| Marco Ferretti | -- | Alcamo | pillar |
| Giovanni Ferretti | -- | Castellammare del Golfo | trusted |
| Matteo Bruno | -- | Erice | trusted |
| Sofia Ferraro | -- | Trapani | trusted |
| Elena Rossi | -- | Trapani | newcomer |
| Lorenzo Ferretti | -- | Favignana | newcomer |
| Valentina Serra | -- | Trapani | newcomer |

## Infrastructure

| Service | Version/Detail |
|---------|---------------|
| Runtime | Python 3.12 |
| Framework | FastAPI + Uvicorn |
| ORM | SQLAlchemy 2.0 async + asyncpg |
| Database | PostgreSQL 17.6 |
| Auth | Keycloak (OIDC, RS256 JWT) |
| Cache | Redis 7 |
| Queue | RabbitMQ 3.13 |
| Object Storage | MinIO |
| Reverse Proxy | Caddy 2 (TLS) |
| Container | Docker |
| Server | Hetzner CX32 (4 vCPU, 8 GB RAM) |
| Monthly cost | EUR 7.59 |

## Test Coverage by Module

| Test File | Tests | What It Covers |
|-----------|------:|----------------|
| test_models_and_services | 41 | Model creation, enums, service logic |
| test_pages | 34 | All pages EN/IT, auth redirects, 404s |
| test_business_logic | 31 | Rental flows, deposits, disputes, auctions |
| test_api_edge_cases | 27 | Bad input, missing fields, boundary values |
| test_rental_state_machine | 26 | All state transitions, invalid transitions |
| test_i18n | 20 | Locale loading, detection, key completeness |
| test_api_items | 10 | CRUD, search, filter, auth gates |
| test_auth | 6 | Login redirect, logout, cookie handling |
| test_api_listings | 6 | CRUD, filters, auth gates |
| test_api_ai | 5 | Image gen, listing gen, skill bio gen |
| test_api_disputes | 5 | File, list, respond, resolve, summary |
| test_api_lockbox | 5 | Generate, verify, status |
| test_api_bids | 4 | Place, list, summary, end auction |
| test_api_deposits | 4 | Hold, list, release, forfeit |
| test_api_notifications | 4 | Summary, list, mark read, read-all |
| test_api_payments | 4 | Create order, capture, refund, list |
| test_api_rentals | 4 | Auth gates on all endpoints |
| test_api_reviews | 4 | Public reads, auth writes |
| test_api_badges | 4 | Catalog, check, user badges |
| test_health | 3 | Status, timestamp, uptime |
| test_api_onboarding | 3 | Page, steps, auth gate |
| **Total** | **250** | |

---

*Measured from source code and live Hetzner UAT deployment.*
*No numbers rounded up. No vanity metrics. Just what's there.*
