# BorrowHood Engineering Rules

**No code gets written that violates these rules. No exceptions. No "for now."**

*This is the constitution. CONCEPT.md is what we build. RULES.md is HOW we build it.*

---

## 1. Frontend Stack -- No Shortcuts, No Subsets

| Rule | Standard |
|------|----------|
| CSS | Tailwind CSS via CDN (full build). NEVER a bundled subset. |
| JS | Alpine.js via CDN (full build). NEVER a bundled subset. |
| Fonts | Google Fonts via CDN. NEVER local subsets. |
| Templates | Jinja2 server-rendered. No SPA. No React. No Vue. |
| Icons | Heroicons (SVG inline) or Font Awesome CDN. |
| Base template | ONE base.html. Every page extends it. No orphan pages. |

**Why:** A bundled 20KB Tailwind subset silently broke every nav bar in HelixNet. Hours of debugging for a 5-minute "shortcut." Never again.

---

## 2. Mobile First -- Always

| Rule | Standard |
|------|----------|
| Design order | Mobile -> Tablet -> Desktop. Never the reverse. |
| Breakpoints | Tailwind defaults: `sm:` `md:` `lg:` `xl:` |
| Touch targets | Minimum 44x44px (Apple HIG). No tiny links. |
| Buttons | Full width on mobile (`w-full`), auto on desktop (`md:w-auto`) |
| Navigation | Hamburger menu on mobile, horizontal nav on desktop |
| Forms | Single column on mobile. Always. |
| Tables | Card layout on mobile, table on desktop (`hidden md:table`) |
| Testing | Chrome DevTools mobile view BEFORE desktop view |

**Why:** The tourists scanning QR codes in Trapani are on phones. Not laptops. Phone first or fail first.

---

## 3. Search & Filtering -- Built In From Day One

| Rule | Standard |
|------|----------|
| Every list page | Has a search bar. No exceptions. |
| Search type | Fuzzy search using `ILIKE` + trigram (`pg_trgm`) |
| Filters | Every list has at least: category, distance, language |
| Filter UI | Collapsible filter panel. Visible on desktop, toggle on mobile. |
| URL state | Filters reflected in URL query params (shareable, bookmarkable) |
| Empty state | "No results found" with suggestion to broaden search |
| Pagination | Cursor-based, not offset-based (scales better) |
| Sort | Every list sortable by: newest, closest, price, rating |
| Debounce | Search input debounced 300ms (Alpine.js `x-on:input.debounce`) |

**Why:** A list without search is a wall. Nobody scrolls through 500 items to find a shovel.

### Search Implementation Pattern

```python
# Every list endpoint follows this pattern
@router.get("/items")
async def list_items(
    q: str = None,           # Fuzzy search term
    category: str = None,    # Filter: item category
    item_type: str = None,   # Filter: physical/digital/service/space/made-to-order
    lang: str = None,        # Filter: owner speaks this language
    sort: str = "newest",    # Sort: newest/closest/price_asc/price_desc/rating
    cursor: str = None,      # Pagination cursor
    limit: int = 20,         # Page size (max 50)
):
```

```sql
-- Fuzzy search with pg_trgm (enable extension once)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Search items by name or description
WHERE (name ILIKE '%' || :q || '%' OR description ILIKE '%' || :q || '%')
  AND similarity(name, :q) > 0.1
ORDER BY similarity(name, :q) DESC;
```

---

## 4. Keycloak Auth -- Production Grade From Day One

### 4.1 Realm Architecture

| Rule | Standard |
|------|----------|
| Realm name | `borrowhood` (lowercase, one word) |
| Realm per deployment | ONE realm per instance. Federation = separate realms linked. |
| Admin realm | `master` -- never touch it for app logic |
| Client ID | `borrowhood-web` (confidential client, PKCE) |
| Token format | JWT RS256 (same as HelixNet) |

### 4.2 Authentication -- Non-Negotiable

| Rule | Standard |
|------|----------|
| MFA | REQUIRED from day one. TOTP (Google Authenticator / Authy). |
| Email verification | REQUIRED before first login. No unverified accounts. |
| Password policy | 8+ chars, 1 uppercase, 1 number, 1 special. Keycloak enforced. |
| Brute force protection | ON. 5 failed attempts = 5 min lockout. Keycloak built-in. |
| Session timeout | 30 min idle, 8 hour absolute. |
| Token refresh | Refresh tokens with 30-day expiry. Rotate on use. |
| Login page | Keycloak-themed (BorrowHood branded), NOT custom. |

**Why:** One compromised account in a community trust platform destroys the whole community's trust. MFA is not optional. Email verification is not optional.

### 4.3 Roles & Permissions

| Role | Who | Can Do |
|------|-----|--------|
| `bh-member` | Every activated user | Browse, list items, rent, review, message |
| `bh-verified` | Email + MFA confirmed | All member + create workshops, invite team |
| `bh-helper` | Community-verified | All verified + assist onboarding, flag content |
| `bh-moderator` | Operator-appointed | All helper + suspend users, remove listings |
| `bh-operator` | Angel (or city operator) | All moderator + manage fobs, installers, system config |
| `bh-admin` | Platform admin | Everything. Realm management. Nuclear option. |

**Role assignment flow:**
```
Signup -> bh-member (automatic)
Verify email + enable MFA -> bh-verified (automatic via Keycloak event)
Community vouching (3 verified users) -> bh-helper (manual or automated)
Operator appoints -> bh-moderator
Contract signed -> bh-operator
```

### 4.4 User Auto-Provisioning

| Rule | Standard |
|------|----------|
| Registration | Self-service via Keycloak. No manual account creation. |
| First login sync | On first JWT-authenticated request, create DB user record if missing. |
| Profile sync | Keycloak is source of truth for: email, name, MFA status. |
| App DB stores | Workshop profile, items, reviews, points -- app-specific data. |
| Deactivation | Disable in Keycloak = locked out everywhere. Single switch. |

```python
# Auto-provision pattern: middleware or dependency
async def get_or_create_user(token: dict, db: Session) -> User:
    user = db.query(User).filter(User.keycloak_id == token["sub"]).first()
    if not user:
        user = User(
            keycloak_id=token["sub"],
            email=token["email"],
            display_name=token.get("preferred_username", token["email"]),
        )
        db.add(user)
        db.commit()
    return user
```

### 4.5 Federation Readiness (v3+)

| Rule | Standard |
|------|----------|
| User IDs | UUIDs, never auto-increment integers. Globally unique. |
| Realm isolation | Each city = own realm. Cross-realm = Identity Brokering. |
| Identity Brokering | Keycloak built-in. Trapani user logs into Palermo with same account. |
| Duplicate prevention | Keycloak `sub` claim is the global ID. App DB links to it. |
| Data ownership | Each realm's data stays in its own DB. Federation = API calls, not shared DB. |

**Why:** When BorrowHood Palermo launches, we don't merge databases. We federate. Each operator runs their own realm. Keycloak Identity Brokering handles cross-realm login. The architecture must support this from line one.

### 4.6 Google OAuth (v1)

| Rule | Standard |
|------|----------|
| Provider | Google OAuth 2.0 via Keycloak Identity Provider |
| Config | In Keycloak admin, not in app code |
| First login flow | Auto-create user + require MFA setup |
| Email trust | Google-verified emails = trusted (skip email verification) |
| Scope | `openid email profile` -- nothing more |

---

## 5. API Design -- RESTful, Consistent, Predictable

| Rule | Standard |
|------|----------|
| Framework | FastAPI with type hints everywhere |
| URL pattern | `/api/v1/{resource}` (plural nouns) |
| HTTP verbs | GET=read, POST=create, PUT=full update, PATCH=partial, DELETE=remove |
| Status codes | 200=OK, 201=created, 204=no content, 400=bad input, 401=unauth, 403=forbidden, 404=not found, 422=validation |
| Response format | JSON with consistent envelope: `{"data": ..., "meta": {...}}` |
| Validation | Pydantic schemas for ALL inputs. No raw dict access. |
| Errors | Structured: `{"detail": "message", "code": "ERROR_CODE"}` |
| Dates | ISO 8601 UTC everywhere. `2026-02-27T14:30:00Z` |
| IDs | UUIDs (string format in JSON, UUID type in DB) |
| Naming | snake_case for JSON fields. Always. |

### Template Routes (HTML pages)

| Rule | Standard |
|------|----------|
| URL pattern | `/{resource}` (no /api prefix) |
| Template location | `templates/borrowhood/{resource}/` |
| Response | `TemplateResponse` with context dict |
| Auth check | Redirect to Keycloak login if unauthenticated |

---

## 6. Database -- PostgreSQL, No Exceptions

| Rule | Standard |
|------|----------|
| ORM | SQLAlchemy 2.0 style (mapped_column, not Column) |
| Database | Separate PostgreSQL DB: `borrowhood` (not shared with HelixNet) |
| Migrations | Alembic. Every schema change = migration file. No raw ALTER TABLE. |
| Primary keys | UUID, server-generated (`uuid4`) |
| Timestamps | `created_at` and `updated_at` on EVERY table. UTC. Auto-set. |
| Soft delete | `deleted_at` timestamp. Never hard delete user data. |
| Indexes | On every foreign key, every search field, every filter field |
| Naming | snake_case tables and columns. `bh_` prefix for all tables. |
| Constraints | Foreign keys, NOT NULL, CHECK constraints. DB enforces integrity, not just code. |
| Connection pool | SQLAlchemy pool with `pool_size=10`, `max_overflow=20` |

### Table Naming

```
bh_user              -- not "users" or "user"
bh_item              -- not "items"
bh_listing           -- not "listings"
bh_review            -- not "reviews"
bh_rental            -- not "rentals"
bh_user_language     -- junction tables: both entities
bh_user_skill
bh_item_media
```

### Model Pattern

```python
class BHBase:
    """Mixin for all BorrowHood models"""
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
```

---

## 7. i18n -- Internationalization From Line One

| Rule | Standard |
|------|----------|
| v1 languages | English (en), Italian (it) |
| Locale files | `locales/en.json`, `locales/it.json` |
| Key format | Dot notation: `items.search.placeholder`, `nav.home` |
| Template usage | `{{ t('items.search.placeholder') }}` or Alpine.js `x-text` |
| Dynamic content | User-generated text tagged with language code |
| Translate button | On every user-generated text block (v2: LibreTranslate) |
| URL language | Query param `?lang=it` or browser Accept-Language header |
| Fallback | English. If key missing in locale, show English. Never show raw key. |
| Number format | Locale-aware (1,000.00 vs 1.000,00) |
| Date format | Locale-aware (Feb 27 vs 27 Feb) |

### i18n File Structure

```json
{
  "nav": {
    "home": "Home",
    "browse": "Browse",
    "my_workshop": "My Workshop",
    "messages": "Messages",
    "login": "Log In",
    "logout": "Log Out"
  },
  "items": {
    "search": {
      "placeholder": "Search tools, services, spaces...",
      "no_results": "No items found. Try broadening your search.",
      "filters": "Filters"
    }
  }
}
```

---

## 8. UI Components -- Consistent, Accessible, Reusable

### Buttons

```html
<!-- Primary action (submit, create, confirm) -->
<button class="w-full md:w-auto px-6 py-3 bg-indigo-600 text-white
               font-semibold rounded-lg hover:bg-indigo-700
               focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2
               transition-colors min-h-[44px]">
  Create Listing
</button>

<!-- Secondary action (cancel, back) -->
<button class="w-full md:w-auto px-6 py-3 bg-white text-gray-700
               font-semibold rounded-lg border border-gray-300
               hover:bg-gray-50 focus:ring-2 focus:ring-indigo-500
               transition-colors min-h-[44px]">
  Cancel
</button>

<!-- Danger action (delete, deactivate) -->
<button class="w-full md:w-auto px-6 py-3 bg-red-600 text-white
               font-semibold rounded-lg hover:bg-red-700
               focus:ring-2 focus:ring-red-500 focus:ring-offset-2
               transition-colors min-h-[44px]">
  Delete
</button>
```

### Rules for ALL interactive elements

| Rule | Standard |
|------|----------|
| Min touch target | 44x44px (set via `min-h-[44px] min-w-[44px]`) |
| Focus indicator | `focus:ring-2 focus:ring-{color}-500` on everything clickable |
| Hover state | Every button, every link, every card |
| Loading state | Spinner + disabled on form submit (prevent double-click) |
| Disabled state | `opacity-50 cursor-not-allowed` |
| Transitions | `transition-colors` or `transition-all duration-200` |

### Cards (item listings, workshop profiles)

```html
<!-- Mobile: full width stack. Desktop: grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <div class="bg-white rounded-lg shadow-sm border border-gray-200
              overflow-hidden hover:shadow-md transition-shadow">
    <img class="w-full h-48 object-cover" src="..." alt="...">
    <div class="p-4">
      <h3 class="font-semibold text-gray-900">Item Name</h3>
      <p class="text-sm text-gray-500 mt-1">Description...</p>
    </div>
  </div>
</div>
```

---

## 9. Forms -- Validated, Accessible, Forgiving

| Rule | Standard |
|------|----------|
| Validation | Client-side (Alpine.js) AND server-side (Pydantic). Both. Always. |
| Error display | Inline below the field, red text, specific message |
| Required fields | Marked with red asterisk `*` + `aria-required="true"` |
| Labels | Every input has a `<label>` with `for=`. No placeholder-only fields. |
| Autocomplete | Use HTML `autocomplete` attributes (name, email, tel, address) |
| Submit button | Full width on mobile. Disabled during submission. Spinner shown. |
| Success feedback | Toast notification (top right, auto-dismiss 5s) |
| Error feedback | Toast (red) + scroll to first error field |
| File upload | Max 5MB per image. Accepted: jpg, png, webp. Preview before upload. |

---

## 10. Images & Media

| Rule | Standard |
|------|----------|
| Storage | Minio (S3-compatible), separate bucket: `borrowhood` |
| Max upload | 5MB per image |
| Formats | Accept: jpg, png, webp. Store as webp (smaller). |
| Thumbnails | Auto-generate: 150x150 (card), 400x300 (detail), original |
| Alt text | REQUIRED on every `<img>`. No empty alt. |
| Lazy loading | `loading="lazy"` on all images below the fold |
| Fallback | Default placeholder image per item type if no photo uploaded |
| Video | YouTube embed only. No video upload. No Minio video storage. |

---

## 11. Telegram Integration

| Rule | Standard |
|------|----------|
| Bot name | `@BorrowHoodBot` (or available variant) |
| Notifications only | Bot sends notifications. NOT a full chat interface. |
| User links | Telegram username stored on profile. Deep link: `t.me/{username}` |
| Events that notify | New rental request, approval, pickup, return, new review, new message |
| Message format | Short, actionable. Include item name, link back to app. |
| Opt-out | Users can disable Telegram notifications in settings |
| No WhatsApp | Telegram only. WhatsApp API costs money. |

---

## 12. Google Integration

| Rule | Standard |
|------|----------|
| Maps | Google Maps Embed API (free tier, no billing required for embeds) |
| Location display | 500m radius circle. NEVER exact address. |
| OAuth | Google Sign-In via Keycloak Identity Provider |
| Calendar | Google Calendar links for rental pickup/return (v2) |
| YouTube | Embed player for how-to videos. No upload API. |
| Analytics | Google Analytics 4 (optional, privacy-respecting) |

---

## 13. Security -- Non-Negotiable

| Rule | Standard |
|------|----------|
| HTTPS | Always. Caddy handles TLS. No HTTP anywhere. |
| CSRF | FastAPI CSRF middleware on all state-changing routes |
| XSS | Jinja2 auto-escaping ON. Never `|safe` on user content. |
| SQL injection | SQLAlchemy parameterized queries only. No raw SQL with f-strings. |
| File upload | Validate MIME type server-side. Never trust client Content-Type. |
| Rate limiting | API: 100 req/min per user. Search: 30 req/min. Login: 5 attempts/5min. |
| Secrets | Environment variables only. Never in code. Never in git. |
| CORS | Strict origin whitelist. No `*` in production. |
| Helmet headers | X-Frame-Options, X-Content-Type-Options, CSP via Caddy |
| Input sanitization | Strip HTML from all text inputs. Markdown allowed in descriptions only. |

---

## 14. Performance -- Fast From Day One

| Rule | Standard |
|------|----------|
| Page load | Under 2 seconds on 3G. Test with Chrome Lighthouse. |
| API response | Under 200ms for list endpoints. Under 100ms for single resource. |
| Database queries | N+1 = bug. Use `joinedload` / `selectinload`. Always. |
| Image optimization | WebP, lazy load, responsive srcset |
| CDN assets | Tailwind, Alpine.js, fonts -- all from CDN (cached globally) |
| Gzip | Caddy auto-compresses. No action needed. |
| Connection pooling | SQLAlchemy pool. PostgreSQL `max_connections` managed. |

---

## 15. Code Quality -- No Excuses

| Rule | Standard |
|------|----------|
| Type hints | On every function signature. Every one. |
| Docstrings | On every public function. Google style. |
| Variable naming | Descriptive. `rental_request` not `rr`. `item_count` not `ic`. |
| File size | Max 300 lines per file. If bigger, split. |
| Function size | Max 50 lines per function. If bigger, extract. |
| Dead code | Delete it. Don't comment it out. Git remembers. |
| TODO comments | Include ticket/issue reference. `# TODO(BH-42): add fuzzy match` |
| Logging | `structlog` or Python `logging`. Never `print()`. |
| Error handling | Specific exceptions. Never bare `except:`. |

---

## 16. Git & Version Control

| Rule | Standard |
|------|----------|
| Branch naming | `feat/description`, `fix/description`, `docs/description` |
| Commit messages | Conventional: `feat: add item search`, `fix: rental date validation` |
| Commit size | Small, atomic. One feature or fix per commit. |
| Main branch | Always deployable. Never push broken code to main. |
| PR required | For anything going to production. Self-review minimum. |

---

## 17. Testing -- If It's Not Tested, It's Broken

| Rule | Standard |
|------|----------|
| Framework | pytest |
| Coverage target | 80% for business logic. Models, routers, services. |
| Test naming | `test_{what}_{scenario}_{expected}` |
| Test data | Fixtures. Never hardcoded IDs. Never depend on seed data. |
| API tests | `TestClient` (FastAPI). Test every endpoint. |
| Auth tests | Test with valid token, expired token, wrong role, no token. |
| Search tests | Test fuzzy match, empty results, filter combinations. |
| No mocks of DB | Use test database. Real queries. Real constraints. |

---

## 18. Deployment & Infrastructure

| Rule | Standard |
|------|----------|
| Container | Docker. One Dockerfile. Multi-stage build. |
| Compose | Added to Hetzner `docker-compose.uat.yml` |
| Database | Separate PostgreSQL DB on same Hetzner instance |
| Keycloak | Separate realm on same Keycloak instance |
| Minio | Separate bucket on same Minio instance |
| Health check | `/api/v1/health` -- returns DB status, Keycloak status, uptime |
| Smoke test | Added to `scripts/smoke-test.sh` |
| Logs | Structured JSON. Ship to stdout. Docker handles the rest. |
| Backup | PostgreSQL pg_dump daily. Minio bucket versioning. |

---

## 19. Accessibility -- Everyone Uses BorrowHood

| Rule | Standard |
|------|----------|
| ARIA labels | On every interactive element without visible text |
| Keyboard navigation | Tab through every form. Enter to submit. Escape to close modals. |
| Color contrast | WCAG 2.1 AA minimum (4.5:1 for text) |
| Screen readers | Semantic HTML: `<nav>`, `<main>`, `<article>`, `<aside>` |
| Skip link | "Skip to content" link as first focusable element |
| Alt text | Every image. Descriptive. Not "image.jpg". |
| Focus management | When modal opens, focus moves to modal. When closed, returns. |

---

## 20. File & Folder Structure

```
BorrowHood/
├── CONCEPT.md                    # Product specification (DO NOT EDIT during build)
├── RULES.md                      # This file (engineering constitution)
├── src/
│   ├── __init__.py
│   ├── main.py                   # FastAPI app factory
│   ├── config.py                 # Settings (env vars, Pydantic BaseSettings)
│   ├── database.py               # SQLAlchemy engine, session, base
│   ├── dependencies.py           # FastAPI dependencies (auth, db, current_user)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py               # BH User, UserLanguage, UserSkill, UserPoints
│   │   ├── item.py               # Item, ItemMedia
│   │   ├── listing.py            # Listing
│   │   ├── rental.py             # Rental
│   │   ├── review.py             # Review
│   │   ├── workshop.py           # WorkshopMember
│   │   └── message.py            # Message
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── item.py
│   │   ├── listing.py
│   │   ├── rental.py
│   │   └── review.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── health.py             # /api/v1/health
│   │   ├── user.py               # /api/v1/users
│   │   ├── item.py               # /api/v1/items
│   │   ├── listing.py            # /api/v1/listings
│   │   ├── rental.py             # /api/v1/rentals
│   │   ├── review.py             # /api/v1/reviews
│   │   └── search.py             # /api/v1/search (unified fuzzy search)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── search.py             # Fuzzy search + filtering logic
│   │   ├── reputation.py         # Points calculation, badge assignment
│   │   ├── notification.py       # Telegram bot notifications
│   │   └── seeding.py            # Seed data loader
│   ├── templates/
│   │   ├── base.html             # Master template (nav, footer, i18n, CDN links)
│   │   ├── components/           # Reusable partials (cards, forms, search bar)
│   │   ├── pages/
│   │   │   ├── home.html
│   │   │   ├── browse.html
│   │   │   ├── item_detail.html
│   │   │   ├── workshop.html
│   │   │   ├── profile.html
│   │   │   └── rental.html
│   │   └── errors/
│   │       ├── 404.html
│   │       └── 500.html
│   ├── static/
│   │   ├── css/                  # Custom CSS (minimal -- Tailwind handles most)
│   │   └── images/               # App logos, default placeholders
│   └── locales/
│       ├── en.json
│       └── it.json
├── tests/
│   ├── conftest.py               # Fixtures, test DB, test client
│   ├── test_items.py
│   ├── test_search.py
│   ├── test_rentals.py
│   ├── test_reviews.py
│   └── test_auth.py
├── alembic/                      # Database migrations
│   ├── alembic.ini
│   └── versions/
├── Dockerfile
├── requirements.txt
├── .env.example                  # Template (never commit real .env)
└── seed_data/
    └── seed.json                 # 11 users, items, listings
```

---

## 21. URL Design -- Decide Once, Never Change

| Rule | Standard |
|------|----------|
| Item URLs | `/items/{slug}` -- human-readable, SEO-friendly |
| Workshop URLs | `/workshop/{username}` -- same as Telegram handle |
| API URLs | `/api/v1/items/{uuid}` -- UUIDs for machine-to-machine |
| Slug source | Auto-generated from item name: "Sally's Cookie Cutter" -> `sallys-cookie-cutter` |
| Slug uniqueness | Append `-2`, `-3` if duplicate. DB unique constraint. |
| Non-Latin slugs | Transliterate: "Fresa da legno" -> `fresa-da-legno` (use `python-slugify`) |
| Canonical URL | `<link rel="canonical">` on every page. Prevents duplicate content. |
| Trailing slashes | Never. `/items/shovel` not `/items/shovel/` |
| Old URLs | If slug changes, 301 redirect from old slug. Never break links. |

**Why:** If we start with UUID URLs and switch to slugs later, every template link, every shared URL, every bookmark breaks. Choose slugs NOW.

```python
# Slug generation pattern (use python-slugify)
from slugify import slugify

def generate_unique_slug(name: str, db: Session, model) -> str:
    base_slug = slugify(name, max_length=80)
    slug = base_slug
    counter = 2
    while db.query(model).filter(model.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug
```

---

## 22. State Machines -- Every Entity Has a Lifecycle

**If you don't define states and transitions, you get spaghetti if/else everywhere.**

### Rental States

```
                    ┌─────────┐
                    │ PENDING │ ← Renter requests
                    └────┬────┘
                         │
              ┌──────────┼──────────┐
              ▼                     ▼
        ┌──────────┐         ┌──────────┐
        │ APPROVED │         │ DECLINED │ (terminal)
        └────┬─────┘         └──────────┘
             │
             ▼
        ┌──────────┐
        │ PICKED_UP│ ← Both parties confirm
        └────┬─────┘
             │
             ▼
        ┌──────────┐
        │ RETURNED │ ← Both parties confirm
        └────┬─────┘
             │
             ▼
        ┌──────────┐
        │ COMPLETED│ ← Reviews exchanged (terminal)
        └──────────┘

Side transitions from any active state:
  → CANCELLED (by either party, with reason)
  → DISPUTED  (escalated to moderator)
```

### Listing States

```
DRAFT → ACTIVE → PAUSED → ACTIVE (toggle)
                → EXPIRED (auto, after 90 days inactive)
                → REMOVED (by moderator, with reason)
```

### User Account States

```
REGISTERED → VERIFIED (email confirmed) → ACTIVE (MFA enabled)
           → SUSPENDED (by moderator)   → ACTIVE (reinstated)
           → DEACTIVATED (by user)      → ACTIVE (user returns)
           → BANNED (by admin, terminal -- only admin can reverse)
```

### Rules

| Rule | Standard |
|------|----------|
| State field | Enum column, NOT free text. `rental_status = Column(Enum(RentalStatus))` |
| Transitions | Validated in code. No jumping from PENDING to RETURNED. |
| History | Every state change creates an audit trail entry. |
| Who changed it | `changed_by` user ID on every transition. |
| Timestamp | `changed_at` on every transition. |

```python
# State transition validation pattern
VALID_RENTAL_TRANSITIONS = {
    RentalStatus.PENDING: [RentalStatus.APPROVED, RentalStatus.DECLINED, RentalStatus.CANCELLED],
    RentalStatus.APPROVED: [RentalStatus.PICKED_UP, RentalStatus.CANCELLED, RentalStatus.DISPUTED],
    RentalStatus.PICKED_UP: [RentalStatus.RETURNED, RentalStatus.DISPUTED],
    RentalStatus.RETURNED: [RentalStatus.COMPLETED, RentalStatus.DISPUTED],
    RentalStatus.COMPLETED: [],  # terminal
    RentalStatus.DECLINED: [],   # terminal
    RentalStatus.CANCELLED: [],  # terminal
    RentalStatus.DISPUTED: [RentalStatus.COMPLETED, RentalStatus.CANCELLED],  # moderator resolves
}

def transition_rental(rental: Rental, new_status: RentalStatus, changed_by: UUID):
    if new_status not in VALID_RENTAL_TRANSITIONS[rental.status]:
        raise InvalidStateTransition(f"Cannot go from {rental.status} to {new_status}")
    old_status = rental.status
    rental.status = new_status
    # audit trail entry created automatically
```

---

## 23. Audit Trail -- Every Important Action Logged

| Rule | Standard |
|------|----------|
| What to log | State changes, create/delete, permission changes, login, moderation actions |
| What NOT to log | Reads, searches, page views (that's analytics, not audit) |
| Table | `bh_audit_log` -- append-only, never UPDATE, never DELETE |
| Fields | `id, timestamp, user_id, action, entity_type, entity_id, old_value, new_value, ip_address` |
| Retention | Forever. Audit logs are legal records. |
| Access | Operators and admins only. Never expose to regular users. |

```python
class BHAuditLog(Base):
    __tablename__ = "bh_audit_log"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    timestamp: Mapped[datetime] = mapped_column(server_default=func.now())
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("bh_user.id"))
    action: Mapped[str]         # "rental.status_change", "item.created", "user.suspended"
    entity_type: Mapped[str]    # "rental", "item", "user"
    entity_id: Mapped[uuid.UUID]
    old_value: Mapped[Optional[str]]  # JSON string
    new_value: Mapped[Optional[str]]  # JSON string
    ip_address: Mapped[Optional[str]]
```

---

## 24. UI States -- Every Page Has Four Faces

**Every page, every component, every list can be in one of 4 states. Design ALL FOUR before writing HTML.**

| State | What the User Sees |
|-------|--------------------|
| **Loading** | Skeleton placeholder (gray pulsing blocks). Never a blank white screen. |
| **Data** | The normal view with real content. |
| **Empty** | Friendly message + call to action. "No items yet. Create your first listing!" |
| **Error** | Red banner with human message + retry button. Never a stack trace. |

### Implementation

```html
<!-- Alpine.js state management pattern -->
<div x-data="{ state: 'loading', items: [], error: '' }" x-init="fetchItems()">

  <!-- LOADING -->
  <template x-if="state === 'loading'">
    <div class="animate-pulse space-y-4">
      <div class="h-48 bg-gray-200 rounded-lg"></div>
      <div class="h-4 bg-gray-200 rounded w-3/4"></div>
    </div>
  </template>

  <!-- EMPTY -->
  <template x-if="state === 'data' && items.length === 0">
    <div class="text-center py-12">
      <svg class="mx-auto h-12 w-12 text-gray-400">...</svg>
      <h3 class="mt-2 text-sm font-semibold text-gray-900">No items</h3>
      <p class="mt-1 text-sm text-gray-500">Get started by creating your first listing.</p>
      <a href="/items/new" class="mt-4 inline-flex ...">Create Listing</a>
    </div>
  </template>

  <!-- DATA -->
  <template x-if="state === 'data' && items.length > 0">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <template x-for="item in items" :key="item.id">
        <!-- item card -->
      </template>
    </div>
  </template>

  <!-- ERROR -->
  <template x-if="state === 'error'">
    <div class="rounded-lg bg-red-50 p-4">
      <p class="text-sm text-red-800" x-text="error"></p>
      <button @click="fetchItems()" class="mt-2 text-sm text-red-600 underline">Try again</button>
    </div>
  </template>
</div>
```

### Empty State Messages (i18n keys)

| Page | Empty Message | CTA |
|------|---------------|-----|
| Browse | "No items in your area yet. Be the first!" | "Create Listing" |
| My Items | "You haven't listed anything yet." | "Add Your First Item" |
| Rentals | "No rental history yet." | "Browse Items" |
| Reviews | "No reviews yet. Complete a rental to leave one!" | "Browse Items" |
| Messages | "No messages yet." | "Browse Items" |
| Workshop Members | "You're the only member. Invite someone!" | "Invite Member" |

---

## 25. Brand Identity -- BorrowHood Visual DNA

**Decide colors ONCE. Use Tailwind color names. Never raw hex in templates.**

### Color Palette

| Role | Tailwind Class | Hex | Usage |
|------|---------------|-----|-------|
| Primary | `indigo-600` | #4F46E5 | Buttons, links, active states |
| Primary hover | `indigo-700` | #4338CA | Button hover |
| Primary light | `indigo-50` | #EEF2FF | Backgrounds, badges |
| Success | `emerald-600` | #059669 | Completed, approved, verified |
| Warning | `amber-500` | #F59E0B | Pending, attention needed |
| Danger | `red-600` | #DC2626 | Delete, declined, errors |
| Text primary | `gray-900` | #111827 | Headings, body text |
| Text secondary | `gray-500` | #6B7280 | Descriptions, metadata |
| Text muted | `gray-400` | #9CA3AF | Placeholders, disabled |
| Background | `gray-50` | #F9FAFB | Page background |
| Card background | `white` | #FFFFFF | Cards, modals |
| Border | `gray-200` | #E5E7EB | Card borders, dividers |

### Typography

| Element | Classes |
|---------|---------|
| Page title | `text-2xl font-bold text-gray-900` |
| Section heading | `text-lg font-semibold text-gray-900` |
| Card title | `text-base font-semibold text-gray-900` |
| Body text | `text-sm text-gray-700` |
| Caption/meta | `text-xs text-gray-500` |
| Badge text | `text-xs font-medium` |

### Spacing Convention

| Context | Value |
|---------|-------|
| Page padding | `p-4 md:p-6 lg:p-8` |
| Card padding | `p-4` |
| Section gap | `space-y-6` |
| Grid gap | `gap-4` |
| Form field gap | `space-y-4` |
| Inline element gap | `space-x-2` |

### Badge Styles (reputation tiers)

| Tier | Classes |
|------|---------|
| Newcomer | `bg-gray-100 text-gray-700` |
| Active | `bg-blue-100 text-blue-700` |
| Trusted | `bg-emerald-100 text-emerald-700` |
| Pillar | `bg-purple-100 text-purple-700` |
| Legend | `bg-amber-100 text-amber-700` |

---

## 26. Toast Notifications -- Consistent Feedback

```html
<!-- Toast container (in base.html, always present) -->
<div id="toast-container"
     class="fixed top-4 right-4 z-50 space-y-2"
     x-data="toastStore()"
     @toast.window="addToast($event.detail)">
  <template x-for="toast in toasts" :key="toast.id">
    <div class="rounded-lg p-4 shadow-lg max-w-sm transition-all duration-300"
         :class="{
           'bg-emerald-50 text-emerald-800 border border-emerald-200': toast.type === 'success',
           'bg-red-50 text-red-800 border border-red-200': toast.type === 'error',
           'bg-amber-50 text-amber-800 border border-amber-200': toast.type === 'warning',
           'bg-blue-50 text-blue-800 border border-blue-200': toast.type === 'info'
         }">
      <p class="text-sm font-medium" x-text="toast.message"></p>
    </div>
  </template>
</div>
```

| Rule | Standard |
|------|----------|
| Success | Green, auto-dismiss 5 seconds |
| Error | Red, stays until dismissed (click X) |
| Warning | Amber, auto-dismiss 8 seconds |
| Info | Blue, auto-dismiss 5 seconds |
| Position | Top right, stacked vertically |
| Max visible | 3 toasts. Older ones dismissed when 4th arrives. |
| Animation | Slide in from right, fade out |
| Mobile | Full width, top of screen |

---

## 27. Auth Redirects & Session Management

| Rule | Standard |
|------|----------|
| Login redirect | After login, return to the page they were trying to access (`?redirect_uri=`) |
| Post-action redirect | After create -> item detail page. After delete -> list page. |
| Logout | Clear session + redirect to home. |
| Multiple devices | Allowed. Keycloak handles multi-session. |
| Force logout | If account suspended/banned, invalidate ALL sessions via Keycloak admin API. |
| Token in cookie | HttpOnly, Secure, SameSite=Lax. Never in localStorage. |
| Session cookie name | `bh_session` |

### Protected Route Pattern

```python
# FastAPI dependency -- every protected route uses this
async def require_auth(request: Request) -> dict:
    token = request.cookies.get("bh_session")
    if not token:
        login_url = f"{KEYCLOAK_URL}/realms/borrowhood/protocol/openid-connect/auth"
        redirect_uri = quote(str(request.url))
        raise HTTPException(status_code=307,
            headers={"Location": f"{login_url}?redirect_uri={redirect_uri}&client_id=borrowhood-web&response_type=code"})
    return verify_and_decode_jwt(token)

async def require_role(role: str):
    async def check(user: dict = Depends(require_auth)):
        if role not in user.get("realm_access", {}).get("roles", []):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return check
```

---

## 28. Concurrency & Data Integrity

**Two people try to rent the same item. Only one wins. The DB decides, not the code.**

| Rule | Standard |
|------|----------|
| Double booking | Prevented by DB constraint: unique active rental per item. |
| Optimistic locking | `version` column on items/listings. UPDATE WHERE version = N. |
| Double form submit | Disabled button + idempotency key in hidden field. |
| Race condition | Use `SELECT ... FOR UPDATE` when checking availability before creating rental. |

```python
# Prevent double-booking pattern
async def create_rental(item_id: UUID, renter_id: UUID, db: Session):
    # Lock the item row -- nobody else can read-for-update until we commit
    item = db.query(Item).filter(Item.id == item_id).with_for_update().first()
    if not item:
        raise NotFound("Item not found")

    # Check no active rental exists
    active = db.query(Rental).filter(
        Rental.item_id == item_id,
        Rental.status.in_([RentalStatus.PENDING, RentalStatus.APPROVED, RentalStatus.PICKED_UP])
    ).first()
    if active:
        raise Conflict("This item is already rented")

    rental = Rental(item_id=item_id, renter_id=renter_id, status=RentalStatus.PENDING)
    db.add(rental)
    db.commit()
    return rental
```

```html
<!-- Idempotency key pattern (prevent double form submit) -->
<form method="POST" x-data="{ submitting: false }">
  <input type="hidden" name="idempotency_key" value="{{ uuid4() }}">
  <button type="submit"
          :disabled="submitting"
          @click="submitting = true"
          :class="{ 'opacity-50 cursor-not-allowed': submitting }">
    <span x-show="!submitting">Rent This Item</span>
    <span x-show="submitting" class="flex items-center">
      <svg class="animate-spin h-4 w-4 mr-2">...</svg> Processing...
    </span>
  </button>
</form>
```

---

## 29. Soft Delete Cascading

**When something is soft-deleted, what happens to everything attached to it?**

| Entity Deleted | What Happens to Children |
|---------------|-------------------------|
| User deactivated | Items set to PAUSED. Active rentals stay active (must complete). Profile hidden from search. |
| User banned | Items set to REMOVED. Active rentals auto-cancelled with "user banned" reason. Profile deleted from search. |
| Item soft-deleted | Active listings set to REMOVED. Pending rentals auto-declined. Completed rentals/reviews preserved. |
| Listing expired | Item stays. Listing can be re-activated. |
| Review reported | Hidden from public. Visible to moderator. Still counts in aggregate until moderator decides. |

**Rule:** Never orphan data. Every cascade is explicitly defined. No surprises.

---

## 30. Open Graph & SEO -- Shared Links Look Professional

**When a judge shares your listing on Twitter/Slack/Discord, it should look good.**

```html
<!-- In base.html <head> -->
<meta property="og:site_name" content="BorrowHood">
<meta property="og:type" content="{{ og_type | default('website') }}">
<meta property="og:title" content="{{ og_title | default('BorrowHood') }}">
<meta property="og:description" content="{{ og_description | default('Rent it. Lend it. Share it. Teach it.') }}">
<meta property="og:image" content="{{ og_image | default('/static/images/og-default.png') }}">
<meta property="og:url" content="{{ request.url }}">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{{ og_title | default('BorrowHood') }}">
<meta name="twitter:description" content="{{ og_description | default('Rent it. Lend it. Share it. Teach it.') }}">
<meta name="twitter:image" content="{{ og_image | default('/static/images/og-default.png') }}">

<!-- SEO basics -->
<meta name="description" content="{{ meta_description | default('Community rental platform. No fees. Open source.') }}">
<link rel="canonical" href="{{ canonical_url | default(request.url) }}">
```

| Page | og:title | og:image |
|------|----------|----------|
| Home | "BorrowHood - Your Neighborhood Rental Platform" | Brand banner |
| Item detail | "{item_name} - Available on BorrowHood" | Item's first photo |
| Workshop | "{workshop_name} on BorrowHood" | Workshop banner |
| Browse | "Browse Items Near You - BorrowHood" | Brand banner |

---

## 31. Content Moderation -- Minimum Viable Safety

| Rule | Standard |
|------|----------|
| Report button | On every listing, every review, every user profile |
| Report reasons | Spam, Inappropriate, Scam, Harassment, Other (free text) |
| Report queue | Operator dashboard: `/operator/reports` |
| Auto-hide | Item/review hidden after 3 reports from different users. Moderator reviews. |
| Moderator actions | Dismiss report, Remove content, Warn user, Suspend user |
| Appeal | Suspended users can email operator. No in-app appeal (v1). |
| Banned words | Configurable list. Flag (don't block) listings containing them. |

```python
class BHReport(Base):
    __tablename__ = "bh_report"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    reporter_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("bh_user.id"))
    entity_type: Mapped[str]    # "item", "review", "user"
    entity_id: Mapped[uuid.UUID]
    reason: Mapped[str]         # "spam", "inappropriate", "scam", "harassment", "other"
    detail: Mapped[Optional[str]]
    status: Mapped[str] = mapped_column(default="pending")  # pending, reviewed, dismissed
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
```

---

## 32. Environment Configuration

### Required Environment Variables

```bash
# .env.example -- copy to .env, fill in real values

# App
BH_APP_NAME=BorrowHood
BH_APP_URL=https://46.62.138.218
BH_SECRET_KEY=change-me-to-random-64-chars
BH_DEBUG=false
BH_LOG_LEVEL=INFO

# Database
BH_DATABASE_URL=postgresql+asyncpg://borrowhood:password@postgres:5432/borrowhood

# Keycloak
BH_KC_URL=https://keycloak.helix.local
BH_KC_REALM=borrowhood
BH_KC_CLIENT_ID=borrowhood-web
BH_KC_CLIENT_SECRET=change-me
BH_KC_ADMIN_USER=admin
BH_KC_ADMIN_PASSWORD=change-me

# Minio
BH_MINIO_URL=minio:9000
BH_MINIO_ACCESS_KEY=change-me
BH_MINIO_SECRET_KEY=change-me
BH_MINIO_BUCKET=borrowhood

# Telegram
BH_TELEGRAM_BOT_TOKEN=change-me
BH_TELEGRAM_ENABLED=true

# Google
BH_GOOGLE_MAPS_API_KEY=change-me
```

### Config Pattern

```python
from pydantic_settings import BaseSettings

class BHSettings(BaseSettings):
    app_name: str = "BorrowHood"
    app_url: str = "http://localhost:8000"
    secret_key: str
    debug: bool = False
    log_level: str = "INFO"
    database_url: str
    kc_url: str
    kc_realm: str = "borrowhood"
    kc_client_id: str = "borrowhood-web"
    kc_client_secret: str
    minio_url: str
    minio_bucket: str = "borrowhood"
    telegram_bot_token: str = ""
    telegram_enabled: bool = False
    google_maps_api_key: str = ""

    class Config:
        env_prefix = "BH_"
        env_file = ".env"
```

---

## 33. Distance & Geo -- Location Without Leaking Addresses

| Rule | Standard |
|------|----------|
| Storage | `latitude` + `longitude` columns (float). NOT PostGIS (YAGNI for v1). |
| Precision | 3 decimal places stored (111m accuracy). Fuzzy enough, useful enough. |
| Display | 500m radius circle on Google Maps embed. Never pin. Never address. |
| Distance calc | Haversine formula in Python. Good enough for <50km radius. |
| Sort by distance | Calculate in SQL: `ORDER BY haversine(user_lat, user_lng, item_lat, item_lng)` |
| Default radius | 10km. User can expand to 25km, 50km, "Anywhere". |
| User location | Browser geolocation API (with permission). Manual city entry as fallback. |

```python
# Haversine distance (km) -- good enough for neighborhood scale
import math

def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
    return R * 2 * math.asin(math.sqrt(a))
```

---

## 34. Listing Lifecycle & Expiry

| Rule | Standard |
|------|----------|
| Draft support | YES. Users can save incomplete listings as drafts. |
| Auto-expire | Listings inactive for 90 days auto-set to EXPIRED. |
| Renewal | One-click reactivate from EXPIRED. No re-entry. |
| Seasonal items | "Available: May-September" field. Auto-pause outside season. |
| Max active listings | 50 per user (prevent spam hoarding). Operator can increase. |
| Duplicate detection | Warn (not block) if title is >80% similar to existing listing by same user. |

---

## 35. Confirmation Dialogs -- Before Destructive Actions

| Action | Confirmation Required? | Pattern |
|--------|----------------------|---------|
| Delete item | YES - modal with "Type item name to confirm" |
| Cancel rental | YES - modal with reason dropdown |
| Decline rental | YES - modal with reason + optional message |
| Deactivate account | YES - modal explaining consequences + password re-entry |
| Leave workshop team | YES - simple "Are you sure?" modal |
| Remove team member | YES - modal explaining what happens to their contributions |
| Report content | NO - just submit (low risk action) |
| Create/edit | NO - just save |

```html
<!-- Confirmation modal pattern -->
<div x-data="{ open: false }" x-cloak>
  <button @click="open = true" class="...">Delete Item</button>
  <div x-show="open" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
    <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
      <h3 class="text-lg font-semibold text-gray-900">Delete this item?</h3>
      <p class="mt-2 text-sm text-gray-500">This will remove the listing and all associated data. Active rentals will be cancelled.</p>
      <div class="mt-4 flex flex-col sm:flex-row gap-2 sm:justify-end">
        <button @click="open = false" class="...">Cancel</button>
        <button @click="deleteItem(); open = false" class="... bg-red-600 text-white">Delete</button>
      </div>
    </div>
  </div>
</div>
```

---

## 36. Navigation & Orientation

| Rule | Standard |
|------|----------|
| Breadcrumbs | On every page below home. `Home > Browse > Item Name` |
| Active nav item | Highlighted in nav bar. User always knows where they are. |
| Back button | Browser back works naturally. No JS history tricks. |
| 404 page | Friendly, with search bar and link to home. Branded. |
| 500 page | "Something went wrong" with retry + home link. No stack trace. |
| Loading indicator | Global progress bar at top of page (thin indigo line) on navigation. |

### Nav Structure

```
Desktop: [Logo] [Home] [Browse] [My Workshop] [Messages] [Profile ▼] [Lang ▼]
Mobile:  [☰] [Logo] [🔔] [Profile]
         └── Slide-out: Home, Browse, My Workshop, Messages, Settings, Logout
```

---

## 37. Background Jobs

| Rule | Standard |
|------|----------|
| v1 approach | FastAPI `BackgroundTasks` (in-process). No Celery. No RabbitMQ. YAGNI. |
| What runs in background | Telegram notifications, image thumbnail generation, email via Keycloak |
| Failure handling | Log error + retry once. If second attempt fails, log and move on. |
| v2 consideration | If volume demands it, move to RabbitMQ + worker. The code pattern stays the same. |

```python
from fastapi import BackgroundTasks

@router.post("/rentals")
async def create_rental(..., background_tasks: BackgroundTasks):
    rental = await rental_service.create(...)
    background_tasks.add_task(notify_owner_new_rental, rental)
    background_tasks.add_task(log_audit_trail, "rental.created", rental.id)
    return rental
```

---

## 38. Browser Support

| Rule | Standard |
|------|----------|
| Minimum | Chrome 90+, Firefox 90+, Safari 14+, Edge 90+ |
| No IE | Internet Explorer is dead. Don't waste a single line on it. |
| ES modules | Allowed. No Babel transpilation needed. |
| CSS Grid/Flexbox | Full support in all target browsers. Use freely. |
| Test on | Chrome mobile (Android), Safari mobile (iOS), Chrome desktop |

---

## 39. Caching

| Rule | Standard |
|------|----------|
| v1 approach | HTTP cache headers only. No Redis cache layer. YAGNI. |
| Static assets | `Cache-Control: public, max-age=31536000` (1 year, CDN versioned) |
| API responses | `Cache-Control: no-store` on authenticated endpoints |
| HTML pages | `Cache-Control: no-cache` (revalidate every request) |
| ETags | FastAPI middleware for conditional responses on list endpoints |
| v2 | Redis cache for search results, user profiles, hot listings. Architecture ready, implementation deferred. |

---

## 40. Data Export -- One-Click Sovereignty

**From CONCEPT.md: every user can export their entire presence as a static site.**

| Rule | Standard |
|------|----------|
| Format | ZIP file containing: static HTML site + images + JSON data |
| Contents | Profile page, all items with photos, all reviews (given and received), rental history |
| Trigger | Settings page: "Export My Data" button |
| Processing | Background task. Telegram notification when ready. Download link valid 7 days. |
| GDPR compliant | Export includes ALL personal data. Satisfies GDPR Article 20 (data portability). |
| Delete account | After export, user can request full deletion. 30-day grace period, then hard delete. |

---

## 41. Operator Dashboard

**The operator (Angel) needs a command center. Not a fancy BI tool. A working dashboard.**

| Widget | What It Shows |
|--------|---------------|
| Active users | Count + trend (this week vs last week) |
| Active listings | Count by category |
| Pending rentals | List with quick-approve/decline buttons |
| Report queue | Unresolved reports with priority sort |
| Recent signups | Last 10, with verification status |
| Fob inventory (v2) | Unactivated, activated, shipped counts |
| System health | DB size, uptime, error rate last 24h |

**URL:** `/operator/dashboard` (requires `bh-operator` role)

---

## The Golden Rules (Print This)

1. **Mobile first.** Every page works on a phone before it works on a laptop.
2. **Search everything.** Every list has fuzzy search and filters. No exceptions.
3. **Full libraries.** CDN Tailwind, CDN Alpine.js, CDN fonts. Never subsets.
4. **MFA from day one.** No unverified users. No weak passwords. No excuses.
5. **UUIDs everywhere.** Ready for federation. Ready for scale.
6. **i18n from line one.** Every string in locale files. Never hardcode text.
7. **Verify before claiming done.** Open it. Click it. Test it. Then say "done."
8. **44px touch targets.** If grandma can't tap it, it's broken.
9. **No raw SQL. No bare except. No print().** Professional code or no code.
10. **The seal inspection rule.** If one thing breaks, check everything like it.
11. **Four states per page.** Loading, data, empty, error. Design all four. Always.
12. **Slugs in URLs.** Human-readable from day one. Never expose UUIDs to users.
13. **State machines.** Every entity has defined states and valid transitions. No spaghetti.
14. **Audit everything important.** Append-only log. Every state change. Every moderation action.
15. **Prevent double-booking.** DB-level locking. Idempotency keys on forms. Disabled submit buttons.
16. **Report button on everything.** Flag spam, scams, harassment. Operator reviews.
17. **Soft delete cascades.** Define what happens to children BEFORE deleting parents.
18. **OG tags on every page.** Shared links must look professional. Non-negotiable for the contest.
19. **Confirmation before destruction.** Delete, cancel, deactivate = modal. Create, edit = just save.
20. **YAGNI but READY.** Don't build Redis caching. But design so you CAN add it without rewriting.

---

*"Rules without code is a dream. Code without rules is a nightmare."*
*-- BorrowHood Engineering Constitution, v1.1, February 27, 2026*
*41 sections. 0 shortcuts. Every seal checked.*
