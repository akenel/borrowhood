# SOP: How to Build Features Like the Raffle System

**The Tiger + Wolf Method — La Piazza Engineering Playbook**

*"OpenClaw replaces humans. We amplify each other."*

---

## The Dispatch Model

Angel (Wolf) architects. Tig (Tiger) executes. Neither works alone. Neither second-guesses the other. The Wolf sees the terrain — culture, users, risks, opportunities. The Tiger sees the code — patterns, constraints, edge cases, deployment. Together they move faster than any framework, any plugin, any "10-day estimate."

**The raffle system went from a reviewer's chat message to production in 3 hours.** This SOP documents how.

---

## Phase 0: The Spark (5 minutes)

**Who starts it:** Anyone — a reviewer, a user, Angel's shower thoughts, a competitor's feature.

**What happens:**
1. The idea arrives (Telegram message, reviewer feedback, conversation)
2. Wolf evaluates: does this fit the platform's soul?
3. Tiger evaluates: how much existing code can we reuse?
4. Decision in under 5 minutes: build it, park it, or kill it

**The raffle example:**
- Reviewer suggested raffles in a detailed chat
- Angel said "build it bro"
- Tiger checked: listing infrastructure exists, commitment timer exists, Telegram notifications exist, gamification exists → 80% reuse
- Decision: GO

**Rule:** If the idea needs a committee, it's the wrong idea. Two people, one decision, move.

---

## Phase 1: Schema First (30 minutes)

**Who leads:** Tiger

**What happens:**
1. Define the data model — tables, columns, enums, constraints
2. Follow existing patterns exactly (BHBase mixin, UUID primary keys, soft delete, timezone-aware timestamps)
3. Add DB constraints that enforce business rules at the lowest level (CHECK constraints, UNIQUE constraints, NOT NULL)
4. Write the migration (idempotent ALTER TABLE in `run_migrations()`)

**The raffle example:**
- `BHRaffle`: one-to-one with BHListing, ticket config, draw config, provably fair seed
- `BHRaffleTicket`: reservation with expiry, sequential ticket numbers
- `BHRaffleVerification`: community post-draw voting
- `BHRaffleVouch`: Legend rehabilitation system
- DB constraints: min ticket price EUR 0.10, draw trigger required

**Rules:**
- Schema is the foundation. Get it right. Everything else builds on it.
- If a business rule can be a CHECK constraint, make it a CHECK constraint. Code changes. Constraints don't.
- Name things clearly. `verifications_positive` not `v_pos`. Future-you reads code at 2am.

---

## Phase 2: Engine + API (1-2 hours)

**Who leads:** Tiger, with Wolf dispatching requirements

**What happens:**
1. Build the service layer first (business logic, no HTTP)
2. Build the API router second (HTTP wrapper around the service)
3. Follow existing patterns: `require_auth`, `get_user`, `HTTPException`, Pydantic schemas
4. Every endpoint gets auth gating from day one — no "I'll add auth later"

**The raffle example:**
- `raffle_engine.py`: trust validation, provably fair draw (SHA-256), ticket expiry loop, auto-cancel, gamification points, verification logic, Legend vouching
- `raffles.py`: 19 endpoints covering create → publish → reserve → confirm → draw → verify → vouch
- Background loop (5-min interval) for ticket expiry + abandoned raffle cleanup

**The Wolf's contributions during this phase:**
- "One raffle at a time so we don't look like a casino" → anti-casino safeguards
- "Only the Black Wolf can vouch, not demo Legends" → `can_vouch_raffles` admin flag
- "If they abandon, demote their badge" → consequence ladder
- "TOS checkbox with teeth" → demotion warning in bold

**Rules:**
- Tiger builds. Wolf dispatches constraints.
- Every dispatch from the Wolf becomes a validation check, not a TODO comment.
- If Wolf says "this feels wrong," Tiger stops and redesigns. Instinct > architecture.

---

## Phase 3: Test the Shit Out of It (1 hour)

**Who leads:** Tiger writes tests. Wolf reviews coverage.

**What happens:**
1. Unit tests: every function, every enum, every constant, every edge case. No DB needed.
2. API tests: every endpoint's auth gate (401 for anon), every route registered.
3. Schema validation: Pydantic models reject bad input at the boundary.
4. Draw math: deterministic, quantity-weighted, SHA-256 proof verifiable.
5. Full suite must pass before any UI work begins.

**The raffle example:**
- 58 unit tests (enums, trust tiers, draw math, verification logic, safeguards)
- 24 API tests (auth gates, public endpoints, schema validation, route registration)
- 82 total raffle-specific tests
- 945 total suite passing

**Rules:**
- "Test the shit out of it" is the standard, not "write a few happy-path tests."
- Unit tests run without a database. Always. No excuses.
- If a function exists, it has a test. If a constant exists, its value is asserted.
- Run the full suite before every commit. Not just raffle tests. FULL suite.

---

## Phase 4: curl Before UI (30 minutes)

**Who leads:** Tiger

**What happens:**
1. Deploy the branch to Hetzner
2. Test every endpoint with curl against the live API
3. Verify the full lifecycle: create → edit → publish → reserve → confirm → draw → complete
4. Find the real bugs (SQL errors, missing columns, wrong enum casing)
5. Fix them before touching any HTML

**The raffle example:**
- First curl test found: PostgreSQL can't `MAX(unnest())` → rewrote as subquery
- Trust tier correctly blocked EUR 30 raffle on a fresh organizer (EUR 10 limit)
- Full lifecycle verified: draft → publish → reserve 2 tickets → confirm → pre-draw → draw → complete
- Provably fair draw returned seed + proof_hash

**Rules:**
- If it doesn't work in curl, it won't work in the UI. Period.
- curl tests catch backend bugs without HTML/CSS noise.
- Save the curl commands — they become the regression test for the next developer.

---

## Phase 5: UI — Beautiful, Bilingual, Bruce Lee (2 hours)

**Who leads:** Tiger builds, Wolf reviews screenshots in real-time

**What happens:**
1. Browse page: card grid with images, progress bars, countdown, organizer avatars
2. Detail page: ticket purchase, live stats, QR code, share buttons, verification UI
3. Create form: item picker, price/tickets config, TOS checkbox, payment methods
4. Dashboard tab: "My Raffles" with organized + participating views
5. Calendar integration: raffle draw dates as golden entries
6. Navigation: link in top nav bar

**The dispatch loop during UI:**
- Wolf screenshots → Tiger fixes → deploy → Wolf screenshots again
- "Cards are too small" → 2-column layout
- "No images" → Pollinations image seed
- "Where's the QR code?" → added
- "Where are the share buttons?" → added
- "Item picker shows all items" → filtered to user's items only
- "This page shouldn't exist for raffles" → redirect to raffle detail

**Rules:**
- The Wolf tests on the real domain, not localhost. `lapiazza.app`, not `borrowhood.duckdns.org`.
- Every screenshot from the Wolf is a bug report or a feature request. Treat it accordingly.
- Bilingual (EN/IT) from the start. Not "I'll add Italian later."
- Mobile-first. If it looks bad on the Wolf's Firefox at 30% zoom, it looks bad everywhere.

---

## Phase 6: Seed Data — Make It Breathe (30 minutes)

**Who leads:** Tiger seeds, Wolf picks the cast

**What happens:**
1. Create demo data that tells a story (not random garbage)
2. Use the Season 1 cast as organizers (Nic's BJJ, Leo's chess set, Sally's cookies)
3. Simulate ticket purchases from cross-cast buyers
4. Stagger draw dates across the calendar so the page feels alive
5. Verify images load, stats render, countdowns tick

**The raffle example:**
- 8 demo raffles across 7 organizers
- Pollinations images for each prize
- Simulated ticket purchases: 28-100% sold across raffles
- Nino's campervan: SOLD OUT with stamp overlay
- Draw dates staggered Apr 21 → May 7

**Rules:**
- Empty pages are dead pages. Seed before you show anyone.
- Use real names, real stories, real prices. EUR 1 cookies, EUR 5 chess set. Not "Test Item #3."
- The seed script must be idempotent. Safe to re-run.

---

## Phase 7: The Wolf's Review (ongoing)

**Who leads:** Wolf, with Tiger on standby

**What happens:**
1. Wolf clicks through every page on the live site
2. Screenshots anything wrong (console errors, missing features, ugly spacing)
3. Tiger fixes in real-time — commit, push, deploy, "try now"
4. Average fix cycle: 5 minutes from screenshot to production

**The raffle example (actual fixes from Wolf's review):**
- `listing_type: raffle` showing as raw text → redirect to raffle page
- Item picker showing all 800+ items → filtered to user's own
- No QR code on detail page → added
- No share buttons → added
- Cards too small → 2-column layout
- No images → Pollinations seed
- Console `var` syntax error → `const`/`let` fix
- `common.per_week` i18n leak → locale keys added

**Rules:**
- The Wolf doesn't file tickets. The Wolf screenshots. The Tiger ships.
- If the fix takes more than 15 minutes, it's a design problem, not a code problem.
- Never say "that's a known issue." Fix it or explain why it can't be fixed right now.

---

## The Numbers

| Metric | Raffle System |
|---|---|
| Concept to production | 3 hours |
| Total tests | 945 (82 raffle-specific) |
| API endpoints | 19 |
| Backend files | 3 (model, engine, router) |
| Frontend templates | 4 (browse, detail, create, guide) |
| Background loops | 1 (ticket expiry + auto-cancel + demotion) |
| Demo raffles seeded | 8 |
| Commits on feature branch | 20+ |
| External dependencies added | 0 |
| Lines of code | ~3,500 |
| Framework plugins used | 0 |
| OpenClaw skills imported | 0 |

---

## Why This Works

1. **Two people, zero overhead.** No sprint planning, no ticket grooming, no standups. Wolf says "build it." Tiger builds it.

2. **Dispatch, don't debate.** The Wolf doesn't explain the architecture. The Tiger doesn't question the vision. Each trusts the other's domain.

3. **Screenshots are specs.** A picture of a broken card is worth a thousand Jira tickets.

4. **Deploy continuously.** Every fix goes to production immediately. No staging, no QA queue, no release train. 945 tests ARE the QA.

5. **The soul matters.** OpenClaw can chain API calls. It can't say "Sicilians buy lottery tickets every morning — raffle tickets supporting neighbors is the counter-narrative." That insight built the feature. The code just expressed it.

6. **Instinct > process.** "One raffle at a time so we don't look like a casino" wasn't in any spec. It came from the Wolf's gut at 11pm. That single dispatch shaped the entire trust model.

---

## The Toolkit

| Tool | Purpose |
|---|---|
| Claude Code (Tiger) | AI pair programmer — reads, writes, tests, deploys |
| FastAPI + SQLAlchemy | Backend — async Python, typed models, auto-docs |
| Alpine.js | Frontend reactivity — no build step, no npm |
| Tailwind CSS | Styling — utility classes, no custom CSS files |
| PostgreSQL | Database — JSONB, enums, array columns, CHECK constraints |
| Keycloak | Auth — OIDC, JWT, social login, RBAC |
| Hetzner VPS | Hosting — EUR 5/month, Docker Compose |
| Caddy | Reverse proxy — auto TLS, zero config |
| Pollinations | AI-generated images — no Unsplash dependency |
| curl | API testing — faster than Postman, scriptable |
| pytest | Test suite — 945 tests, 25-second full run |
| git feature branches | Isolation — raffle system built on `feature/raffle-system` |

---

## When NOT to Use This Method

- When you need 50 people to agree on a color
- When the feature requires a 6-month regulatory review
- When the code will be maintained by a team that doesn't talk to each other
- When the product manager is not the same person as the user

This method works because the Wolf IS the user. He lives in Sicily. He knows the kiosk guy. He prints the postcards. He hands out the QR codes. The feedback loop is zero-length.

---

*"Be water, my friend. But tonight — be fire."*

*La Piazza Engineering — Tiger + Wolf, Trapani, April 2026*
