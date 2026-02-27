# BorrowHood

**"Rent it. Lend it. Share it. Teach it."**

*Free as in freedom. Open source. No platform fees. Forever.*

---

## What Is BorrowHood?

Every garage becomes a rental shop. Every neighbor becomes a supplier. Every kitchen becomes a bakery.

BorrowHood is a community rental, sales, and services platform where people list their underused tools, kitchen gear, equipment, and skills -- and neighbors borrow, rent, buy, or trade. No middlemen. No fees. No algorithm deciding who sees what.

Built from a camper van in Trapani, Sicily, by a Swiss-Canadian whose father was a hand-shovel landscaper for 60 years. His garage had 500 tools. Every neighborhood has a garage like his. BorrowHood connects the people who have stuff with the people who need it.

## The Origin Story

My father Albert was a hand-shovel landscaper in Switzerland from 1960 to 2020. When he passed, those 500 tools sat in his garage collecting dust. His neighbors still needed shovels, rakes, and chainsaws -- they just didn't know where to look. Craigslist is a wasteland. Facebook Marketplace is a data farm. None of them care about your community.

BorrowHood fixes that.

## DEV Weekend Challenge

This project was built for the [DEV Weekend Challenge](https://dev.to/challenges/claude) -- Anthropic Claude Code edition.

**Built with:** Claude Code (Claude Opus 4.6) as co-pilot, coding from a camper van in Sicily.

## Features

### For Users
- **List anything** -- tools, kitchen gear, digital goods, services, spaces, made-to-order items
- **Seven listing types** -- Rent, Sell, Commission, Offer, Service, Training, **Auction**
- **Bilingual** -- Full English + Italian i18n (query param, cookie, Accept-Language detection)
- **Workshop profiles** -- Every user is a shop with skills, languages (CEFR levels), and social links
- **Reputation system** -- Reviews weighted by reviewer badge tier (Newcomer 1x to Legend 10x)
- **Rental state machine** -- Request > Approve > Pickup > Return > Complete (with dispute handling)
- **Auction system** -- Timed bidding with auto-outbid notifications, reserve prices, bid increments
- **Dispute resolution** -- 3-step flow: file, respond, resolve (8 reasons, 7 resolution types)
- **Security deposits** -- Hold at pickup, release on return, forfeit on damage
- **PayPal payments** -- Checkout flow: create order, buyer approves, capture payment, refund
- **Notification bell** -- In-app notifications with 15 event types + optional Telegram forwarding
- **Onboarding wizard** -- 3-step profile setup for new users

### For Developers
- **30+ REST API endpoints** with OpenAPI docs (`/api/docs`)
- **111 automated tests** -- all green
- **13 SQLAlchemy models** with UUID PKs, soft deletes, audit timestamps
- **Keycloak OIDC** -- real enterprise SSO with 6 realm roles and RBAC
- **Idempotency keys** on rental requests (no double-submit)
- **Optimistic locking** on listings (version field)
- **PayPal REST API v2** integration (sandbox + live)
- **Telegram bot** forwarding for notifications

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + SQLAlchemy 2.0 async + asyncpg |
| Auth | Keycloak OIDC (RS256 JWT, 6 roles) |
| Database | PostgreSQL |
| Frontend | Jinja2 SSR + Tailwind CSS (CDN) + Alpine.js (CDN) |
| Fonts | Google Fonts (Inter) via CDN |
| Payments | PayPal REST API v2 (sandbox + live) |
| Tests | pytest + pytest-asyncio (111 tests) |
| Container | Docker (Dockerfile included) |

**No bundled subsets.** Full CDN libraries only. Enterprise-grade, not a toy.

## Architecture

```
Browser
  |
  v
FastAPI (uvicorn)
  |
  +-- Page Routes (Jinja2 SSR) -----> Templates (base.html + pages/)
  |     |
  |     +-- i18n engine (EN/IT) ----> src/locales/{en,it}.json
  |
  +-- API Routes (/api/v1/) --------> JSON responses
  |     |
  |     +-- Items CRUD
  |     +-- Listings CRUD
  |     +-- Rentals (state machine)
  |     +-- Reviews (weighted)
  |     +-- Bids (auction system)
  |     +-- Notifications (bell + Telegram)
  |     +-- Disputes (3-step resolution)
  |     +-- Deposits (hold/release/forfeit)
  |     +-- Payments (PayPal checkout)
  |     +-- Onboarding (profile setup)
  |     +-- Health check
  |
  +-- Auth Routes ------------------> Keycloak OIDC
  |
  +-- SQLAlchemy async -------------> PostgreSQL
        |
        +-- 13 models (UUID PKs, soft deletes)
        +-- Seed data (11 workshops, 20+ items)
```

## Data Model

```
BHUser (every user IS a workshop)
  |-- BHUserLanguage (CEFR levels: A1-C2, Native)
  |-- BHUserSkill (self-declared, community-verified)
  |-- BHUserPoints (reputation tracking)
  |-- BHUserSocialLink (YouTube, Instagram, etc.)
  |-- BHNotification (in-app + Telegram, 15 event types)
  |
  +-- BHItem (tools, equipment, services, spaces)
        |-- BHItemMedia (photos, video embeds)
        +-- BHListing (rent, sell, commission, offer, service, training, AUCTION)
              |-- BHBid (auction bids with auto-outbid)
              +-- BHRental (state machine: pending -> completed)
                    |-- BHReview (weighted by reviewer badge tier)
                    |-- BHDeposit (hold -> release/forfeit)
                    |-- BHPayment (PayPal checkout flow)
                    +-- BHDispute (3-step: file -> respond -> resolve)
```

## API Endpoints

### Public (no auth required)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Health check with DB status |
| GET | `/api/v1/items` | List items (search, filter, sort, paginate) |
| GET | `/api/v1/items/{id}` | Get item by ID |
| GET | `/api/v1/listings` | List listings (filter by item, status, type) |
| GET | `/api/v1/listings/{id}` | Get listing by ID |
| GET | `/api/v1/reviews` | List reviews (filter by user) |
| GET | `/api/v1/reviews/summary/{user_id}` | Review summary (avg, weighted avg, count) |
| GET | `/api/v1/bids/summary` | Auction summary (bids, current price, winner) |

### Authenticated (Keycloak JWT required)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/items` | Create item |
| PATCH | `/api/v1/items/{id}` | Update item (owner only) |
| DELETE | `/api/v1/items/{id}` | Soft-delete item (owner only) |
| POST | `/api/v1/listings` | Create listing on your item |
| PATCH | `/api/v1/listings/{id}` | Update listing (owner only) |
| DELETE | `/api/v1/listings/{id}` | Soft-delete listing (owner only) |
| GET | `/api/v1/rentals` | List your rentals (as renter or owner) |
| GET | `/api/v1/rentals/{id}` | Get rental details |
| POST | `/api/v1/rentals` | Request a rental (idempotency key) |
| PATCH | `/api/v1/rentals/{id}/status` | Transition rental status (state machine) |
| POST | `/api/v1/reviews` | Submit review (completed rentals only) |
| POST | `/api/v1/bids` | Place bid on auction |
| GET | `/api/v1/bids` | List bids for auction |
| POST | `/api/v1/bids/{id}/end` | End auction (owner only) |
| GET | `/api/v1/notifications/summary` | Notification counts (unread badge) |
| GET | `/api/v1/notifications` | List notifications |
| PATCH | `/api/v1/notifications/{id}/read` | Mark notification as read |
| POST | `/api/v1/notifications/read-all` | Mark all as read |
| POST | `/api/v1/disputes` | File a dispute |
| GET | `/api/v1/disputes` | List your disputes |
| GET | `/api/v1/disputes/summary` | Dispute counts |
| PATCH | `/api/v1/disputes/{id}/respond` | Respond to dispute |
| PATCH | `/api/v1/disputes/{id}/resolve` | Resolve dispute |
| POST | `/api/v1/deposits` | Hold deposit |
| GET | `/api/v1/deposits` | List deposits |
| PATCH | `/api/v1/deposits/{id}/release` | Release deposit |
| PATCH | `/api/v1/deposits/{id}/forfeit` | Forfeit deposit |
| POST | `/api/v1/payments/create-order` | Create PayPal order |
| POST | `/api/v1/payments/capture` | Capture PayPal payment |
| POST | `/api/v1/payments/{id}/refund` | Refund payment |
| GET | `/api/v1/payments` | List payments |
| POST | `/api/v1/onboarding/profile` | Setup/update profile |

### Pages
| Path | Description |
|------|-------------|
| `/` | Home page (featured items, stats, origin story) |
| `/browse` | Search + filter items |
| `/items/{slug}` | Item detail with rental request modal |
| `/workshop/{slug}` | Workshop profile |
| `/list` | List a new item (multi-step form) |
| `/dashboard` | User dashboard (items, rentals, requests) |
| `/onboarding` | 3-step onboarding wizard for new users |
| `/terms` | Terms of Service + Community Code of Conduct |
| `/login` | Keycloak OIDC login |
| `/logout` | Clear session + Keycloak logout |

## Quick Start

```bash
# Clone
git clone https://github.com/akenel/borrowhood.git
cd borrowhood

# Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your PostgreSQL and Keycloak URLs

# Run
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Seed test data (debug mode)
curl -X POST http://localhost:8000/api/v1/seed

# Open in browser
open http://localhost:8000
```

## Running Tests

```bash
source .venv/bin/activate
python -m pytest tests/ -v
```

```
111 passed in 2.4s

test_api_items.py        - 10 tests (CRUD, search, auth gates)
test_api_listings.py     -  6 tests (CRUD, filters, auth gates)
test_api_rentals.py      -  4 tests (auth gates on all endpoints)
test_api_reviews.py      -  4 tests (public reads, auth writes)
test_api_notifications.py-  4 tests (summary, list, mark read)
test_api_bids.py         -  4 tests (place, list, summary, end)
test_api_disputes.py     -  5 tests (file, list, respond, resolve)
test_api_deposits.py     -  4 tests (hold, list, release, forfeit)
test_api_payments.py     -  4 tests (create order, capture, refund)
test_api_onboarding.py   -  3 tests (page, steps, auth gate)
test_auth.py             -  6 tests (login redirect, logout, cookie)
test_health.py           -  3 tests (status, timestamp, uptime)
test_i18n.py             - 19 tests (locale loading, detection, completeness)
test_pages.py            - 35 tests (all pages EN/IT, search, 404s)
```

## Internationalization

Full bilingual support: English + Italian.

Language detection chain:
1. `?lang=it` query parameter (highest priority)
2. `bh_lang` cookie (persistent across sessions)
3. `Accept-Language` header (browser default)
4. English (fallback)

The locale completeness test (`test_all_en_keys_exist_in_it`) ensures every English key has an Italian translation. If you add a key to `en.json`, the test will fail until you add it to `it.json`.

## Keycloak Realm

Import `keycloak/borrowhood-realm-dev.json` into your Keycloak instance.

**Roles:** bh-member, bh-lender, bh-moderator, bh-admin, bh-operator, bh-qa-tester

**Test users** (all password: `helix_pass`):
- `angel` -- admin (all roles)
- `sally` -- lender + member
- `nino` -- operator
- `luna` -- moderator
- `anne` -- QA tester

## What Makes BorrowHood Different

1. **No platform fees.** Zero. Not 6.5%. Not 13%. Zero.
2. **Open source.** MIT license. Fork it. Run your own.
3. **Language-aware.** CEFR proficiency levels on every profile. The Italian grandma with A2 English can find the English tourist with B1 Italian.
4. **Reputation that means something.** Reviews weighted by reviewer trust level. A Legend's review counts 10x more than a Newcomer's.
5. **Community-first.** No algorithm. No promoted listings. No dark patterns. Just neighbors helping neighbors.
6. **Seven listing types.** Rent, Sell, Commission, Offer, Service, Training, Auction. Not just "buy or sell."
7. **Real dispute resolution.** 3-step process with 8 reason categories and 7 resolution types. Not "contact support."
8. **PayPal built in.** Create order, capture, refund. No third-party payment plugins.

## Codebase Stats

| Metric | Count |
|--------|-------|
| Python source | ~5,500 lines |
| HTML templates | ~1,600 lines |
| Test code | ~1,100 lines |
| SQLAlchemy models | 13 |
| API endpoints | 33 |
| Automated tests | 111 |
| i18n keys | 200+ (EN + IT) |
| Routers | 11 |

## License

MIT

---

*Built from a camper van in Trapani, Sicily. 2026.*
*"Every neighborhood has a garage like his."*
