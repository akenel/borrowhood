# La Piazza Changelog

All notable changes to La Piazza, week by week.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This file is the **source of truth** — friendly social posts live in `Bro_Kit/whats-new/`.

---

## [Week of April 19–25, 2026]

**75 commits. 25+ user-facing improvements. ~20 bugs squashed.**

### Added
- Type-aware listing flow: `/list?type=event` (or `raffle`, `workshop`) pre-selects the type and adapts the heading (BL-154)
- Calendar persistent filters (Mine / Free / Paid) with smart empty state and adaptive legend (BL-153)
- Calendar grid dot filtering by Mine / Free / Paid; show user name on hover (BL-152)
- Heart + share-channel buttons on event cards (BL-151)
- 8-box OTP-style lockbox code input for pickup and return (BL-157)
- Per-item analytics strip on dashboard: views (30d), favorites, conversations (BL-162)
- Redesigned dashboard My Items cards: bigger thumbs, color-coded type badges, status pills, View / Edit / Delete (BL-161)
- Surface counterparty name on seller's order view ("Sold to X") (BL-160)
- Audience labels on lockbox code blocks ("for the buyer" / "for the seller") (BL-160)
- "Waiting for seller" hint when codes don't exist yet (BL-159)
- RSVP attendee notes — captured and displayed on event detail (BL-143)
- Free-text availability note on listings (MVP)
- Tap-to-cover button for item photos; sort_order respected on read
- Smart empty states across search and browse — echo query, suggest sibling surfaces
- Live Raffle Events design doc + onboarding kit (`docs/LIVE-RAFFLES-DESIGN.md`)
- Software legends seed: 6 founding-developer profiles (antirez, Carmack, DHH, Linus, Bellard, Acton)
- Simon White + Reinhold Messner profiles, with hero images and Simon raffles (BL-146, BL-147)
- 18 community items across skill_exchange / neighborhood_help / local_food / rides (BL-138)
- Boxing-legend GIFs on Simon's items + Women's Self-Defense course + raffle
- Reward loop v1 for feedback: reporter tracking, points, badges, contributor UX
- Contributor score visible in submit success state
- Feedback attachments: photo + voice recording in compose form
- Raffle type added to listing flow with redirect to raffle creator (BL-122)
- Calendar → Events nav rename + tooltips
- Clean desktop nav with avatar dropdown (BL-134)
- Empty-state guard on `/raffles/create` (BL-122)
- Mobile back button on calendar
- Workshop tags clickable everywhere
- Native title hints on user dropdown + clickable sidebar tags
- Iterative client-side image compression (3-tier passes) for feedback widget
- HEIC/HEIF detection client + server with helpful error message

### Changed
- Mobile menu items now all have icons (was only Raffles + Settings)
- Calendar tabs become dropdown on mobile to save space
- Item cards across browse, home, and members adopt raffle-card aesthetic (BL-141)
- Item-detail tags visually obvious as clickable
- Workshop favorite heart moved to Contact block
- Workshop meta row uses flex-wrap to stop horizontal scroll
- Manual Translate button hides when content matches viewer's language
- `Content-Language` header set so browsers stop offering auto-translate
- Auto-translate suppressor on all standalone HTML pages
- Server feedback-upload error message derives `max_mb` from constant + reports actual file size
- Raffle trust gate tightened: Simon (and any new account) capped at €10 pots, age-14 floor, NULL max-tickets rejected
- Brotherhood Run music dropped to 10% volume on videos

### Fixed
- Mobile input + submit button rows wrap on narrow viewports (BL-155)
- Body-level overflow clamp + word-break on long user content (BL-156)
- Bulletproof lockbox verify against stuck spinner: 15s AbortController + 20s watchdog + immediate reload (BL-158)
- Confirm Pickup/Return gated on codes actually existing (BL-159)
- Feedback photo upload: server told the truth about size limits, client compresses iteratively, HEIC handled (BL-148, BL-163)
- Listing edits no longer wipe story / tags / age_restricted / safety_notes on save (BL-129, BL-131, BL-142)
- Raffle creation MissingGreenlet error (BL-134)
- Safari nav overflow (BL-135)
- Calendar event image rendering hardened, SW cache bumped (BL-130a)
- Mobile event cards no longer cram title to "M..." (BL-150)
- Calendar grid dots respect Mine/Free/Paid filter
- Notification drawer on mobile, pricing panel HTML, messages trailing slash
- Edit form no_change mock response includes slug
- Edit form double-quote-in-x-data hotfix
- Helpboard `POST_EAGER` import in posts + summary routers
- Helpboard `author_slug` exposed in post + reply schemas (BL-58)
- Backlog reward hook isolated from main update transaction
- Backlog `now` Jinja global registered (`/backlog` renders again)
- Items: avoid 307 redirect on `POST /api/v1/items` (BL-121)
- Pages: import `Markup` and `json` in item.py edit handler
- AI: import `CATEGORIES` in listing/skills/helpboard modules
- Raffle UX: hide Community Verification UI from non-ticket-holders
- Auth: redirect anon users on private pages
- Dev: pin postgres IP script
- Seed: schema fixes for software legends (columns, enums, emails)
- Seed: Messner images (3 per item, 15 total) + Simon age fix to 30
- Images: stop docker-exec -i from slurping loop stdin in phase 2
- Images: dead-image backfill on item-detail tags

### Security & Trust
- Raffle Trust Gate hardened: €10 cap on new accounts, age-14 floor, validation against NULL max-tickets
- Staging env awareness + badge + safer default `BH_ENVIRONMENT=prod`
- Anon users redirected on private pages

### Tests
- Regression suite for the week's polish work (test_april25_polish.py)
- Mobile overflow regression guards (test_mobile_overflow_guards.py — 13 tests)
- Lockbox code box regression suite (test_lockbox_code_boxes.py — 26 tests)
- Dashboard My Items card regression (test_dashboard_items_card.py — 11 tests)
- Per-item analytics regression (test_dashboard_analytics.py — 11 tests)
- Feedback upload regression (test_feedback_upload.py — 10 tests)

### Docs
- `docs/LESSONS-SOFTWARE-FIGHTERS.md` — morning checklist + lessons from the legends
- `docs/LIVE-RAFFLES-DESIGN.md` — full Live Raffle Events spec
- `docs/AVAILABILITY-DESIGN.md` — full availability feature design
- Staging marked as NOT YET LIVE (only prod exists right now)
