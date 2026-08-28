# Backlog Module — Community Engagement Design

**Status:** Draft 1
**Author:** Angel + Tigs (Claude Opus 4.7)
**Date:** 2026-05-23
**Task ref:** #31

---

## TL;DR

The Backlog (BL) module today supports **submission** (via `/helpboard` feedback form) and **admin status updates** (status pill on the BL detail panel). It does NOT support the things needed to make BL a real two-way street with users:

- Users can't see WHAT fixed their issue (no surface for `resolution_sha` / `resolution_note` even after task #30 wired the API).
- Users can't edit their own items (typos, more detail, attached evidence).
- No comment thread for discussion or clarification.
- No "me too" / upvote signal.
- No notifications when items they filed change status.
- Auth path for new users is rough — first-time visitors face Keycloak login pages with no warm onboarding.

Angel's framing (2026-05-23 morning):

> "we need the bl to work properly end to end so its not just for me but to invite users to properly fix issues and add features they want"

This document sketches the design for making BL a real community engagement surface, not just an internal bug tracker.

---

## What's working today (don't break)

- **Submission via `/helpboard` feedback form** — anonymous OK, attaches `session_report.json` + optional screenshot, lands in `bh_backlog_item` as `[Feedback] ...`
- **Item list view** at `/backlog` — table + filters, search by title
- **Detail panel** — title, description, type/priority/status pills, status change buttons (Pending / In Progress / On Hold / Blocked / Done), attachments, activity tab
- **Activity trail** — append-only log of status changes, priority changes, assignment changes, comments
- **API** — `/api/v1/backlog/items` (list, get, create, update, delete), `/items/{id}/activities`, `/summary`
- **Auth** — Keycloak OIDC, `borrowhood-web` client, roles include `bh-qa-tester` for QA dashboard access
- **Resolution fields** (post-#30) — `resolution_sha` + `resolution_note` persist via PUT, activity log captures them

## The gaps (sized roughly)

| # | Gap | Why it matters | Size |
|---|---|---|---|
| 1 | UI doesn't surface `resolution_sha` / `resolution_note` on done items | Users who filed a bug can't see "what fixed it" — robs them of closure + understanding | S — frontend only |
| 2 | Users can't edit their own items | Typos stay forever; can't add detail after thinking more; can't attach better evidence | M — needs ownership model + UI |
| 3 | No comment thread | Discussion happens in user's head or in DMs Angel never sees — loss of context | M — needs API + UI |
| 4 | No "me too" / upvote | Can't tell which items 1 person cares about vs 50 people | M — needs new table + UI |
| 5 | No notifications when "my" item changes | Users file and forget — no pull-back to the platform | M — leverage existing `bh_notification` table |
| 6 | Anonymous submissions are the default | Users have no continuity, can't track their own items | S — encourage login during submission flow |
| 7 | Rough auth for new visitors | First-time users hit Keycloak login form, no warm welcome | M — magic-link via Resend (already wired) |
| 8 | No public RSS / Atom feed of "what shipped" | People who care want a pull surface, not just push | XS — single endpoint |

---

## Proposed user stories

### Reader (anyone, no account)
- I can browse all backlog items.
- I can read full descriptions, attachments, activity history, and **resolution info** (what commit fixed it, what the developer said).
- I can subscribe to an RSS feed of "items shipped this week."

### Filer (signed in)
- I can submit a new item from `/helpboard` AND from a "Report a bug" link inside the app.
- I can see all items I've filed in "My Items" view.
- I get notified (in-app + optionally Telegram) when status changes on my items.
- I can edit my own items if they're still `pending` — to fix typos, add detail, attach screenshots.
- I can withdraw (soft-delete) my own items if I no longer care.
- I can comment on any item (mine or others').

### Maintainer (currently: Angel, future: trusted contributors)
- I can change status / priority / assignee on any item.
- I can record `resolution_sha` + `resolution_note` when shipping a fix.
- I can leave a comment that's clearly marked as "maintainer reply."
- I can pin important items to the top of the list.

### Champion (super-engaged user)
- I can upvote ("me too") items I care about.
- I can see items sorted by "most upvoted" to focus on what the community wants.
- I can subscribe to specific items (notifications even if I didn't file them).

---

## Scope: in / out / later

### In scope for first cut (Draft 1 → ship in 3-4 PRs over ~2 weeks)

| PR | What | Effort |
|---|---|---|
| **A** | Surface `resolution_sha` + `resolution_note` in BL detail UI (done items get a "How it was fixed" section with commit link to github) | ~2h |
| **B** | Comment thread on BL items + API + UI (uses existing `bh_backlog_activity.COMMENT` type) | ~4h |
| **C** | "Edit my own item" — backend ownership check + frontend edit form for pending items | ~3-4h |
| **D** | "My Items" view + in-app notifications when status changes on filed items (uses `bh_notification` table) | ~4-5h |

### Out of scope for first cut (later iterations)

- Upvote / "me too" — needs new table, UI, sort change
- Public RSS feed — XS but defer until first cut proves engagement
- Magic-link email auth via Resend — useful but distinct project, possibly its own design doc
- Pin to top — admin-only feature, low priority
- Trusted-contributor role (non-Angel maintainers) — requires Keycloak role mapping, governance

### Pre-existing concerns (file separately, don't bundle)

- BL filed against `borrowhood_staging` realm (BL-2 lives in staging DB) but conversations span prod/staging. Cross-realm BL visibility? OR consolidate to prod only?
- Anonymous filer attribution — currently "Anonymous" — should we capture device fingerprint, IP, or just leave?

---

## Data model changes needed

```
bh_backlog_item                       (existing, additive only)
  + reporter_user_id  uuid?           [exists, currently sometimes-set]
  + edit_lock         enum?           [new -- prevents edits after status changes from pending]

bh_backlog_activity                   (existing, no schema change needed)
  -- COMMENT activity type already supports threaded discussion

bh_backlog_upvote                     (NEW table, future)
  id, item_id, user_id, created_at
  UNIQUE(item_id, user_id)

bh_notification                       (existing, just add new event types)
  + BACKLOG_STATUS_CHANGED
  + BACKLOG_COMMENT_RECEIVED
```

Migrations needed: 1 new table (later), 2 new notification enum values (now if we ship PR D).

---

## API additions

```
GET    /api/v1/backlog/items/mine          ← items I filed (auth)
PATCH  /api/v1/backlog/items/{id}/comment  ← add a comment (auth)
DELETE /api/v1/backlog/items/{id}          ← already exists, add ownership check (auth)
PUT    /api/v1/backlog/items/{id}          ← exists, add ownership-or-admin check
GET    /api/v1/backlog/feed.atom           ← RSS feed of done items (no auth, later)
POST   /api/v1/backlog/items/{id}/upvote   ← later
```

---

## UI sketches (ASCII)

### BL detail panel — DONE item (post PR A)

```
┌─────────────────────────────────────────────────────────────┐
│ BL-192  [Feedback] cancelled raffles cluttering /raffles    │
│ Status: ◉ Done   Priority: high   Type: bug-fix             │
├─────────────────────────────────────────────────────────────┤
│ User Feedback                                               │
│ "I see a lot of cancelled Raffles we should clear those... │
│  ─ From: Anonymous (mobile)                                 │
├─────────────────────────────────────────────────────────────┤
│ ★ How it was fixed                          ← NEW           │
│   Commit: b50d48c (github.com/akenel/borrowhood/...)        │
│   Note:   Shipped 2026-05-23 via PR #1. One-line filter     │
│           swap in src/routers/raffles.py:279. Contract test │
│           added. Staging-verified before prod deploy.       │
├─────────────────────────────────────────────────────────────┤
│ Attachments (2): session_report.json, Screenshot.png        │
├─────────────────────────────────────────────────────────────┤
│ Discussion (PR B)                                           │
│  alice: thanks for flagging this  · 2h ago                  │
│  angel: fixed, sorry about the noise · 1h ago               │
│  [ Add comment ____________________ ]    [ Post ]           │
├─────────────────────────────────────────────────────────────┤
│ Activity ▼                                                  │
│  john   changed status pending → done       12:16 UTC       │
│  angel  resolved at commit b50d48c          12:30 UTC       │
└─────────────────────────────────────────────────────────────┘
```

### "My Items" view (PR D)

```
┌──────────────────────────────────────────────────────────┐
│ My Backlog Items                          + Report new   │
├──────────────────────────────────────────────────────────┤
│ BL-193  pending   I was just looking at the README...    │
│ BL-2    DONE      AI draft timed out  (fixed 2 days ago) │
│ BL-178  pending   maps don't load on iOS                 │
└──────────────────────────────────────────────────────────┘
```

---

## Auth + ownership model

**Current state:** Any logged-in user with the right Keycloak role can update any item. No item-level ownership.

**Proposed:**
- `reporter_user_id` (already in schema, often null for anonymous) becomes the "owner" for edit purposes.
- Edit window: only while `status == pending`. Once a maintainer moves it to `in_progress`, edits are locked except for the assigned maintainer.
- Admin override: `bh-admin` role can edit anytime.
- Anonymous filers can't edit (no user_id to check ownership against) — they need to log in to claim.

---

## Open questions

1. **How do anonymous filers reclaim their items?** Options: (a) capture email at submission, send a magic link to associate later, (b) browser-fingerprint association (creepy), (c) just don't — anonymous = forever anonymous.
2. **Are comments threaded or flat?** Flat is simpler. Threaded is what GitHub does. Recommend flat for v1.
3. **Per-user notification settings or global?** Recommend global on/off for v1, per-item granularity later.
4. **Cross-realm visibility:** BL items live in app-specific DBs (borrowhood, borrowhood_staging). Should the prod BL show staging-filed items? Currently no.
5. **Public-facing URL for BL items?** Right now `/backlog/{id}` requires auth. Should `done` items be publicly readable so we can share `lapiazza.app/backlog/192` as a "look what we shipped" link?

---

## Milestones

| Milestone | What | When |
|---|---|---|
| **M0 — TODAY (done)** | Task #30: API exposes `resolution_sha` + `resolution_note`. Foundation laid. | ✅ 2026-05-23 |
| **M1 — PR A** | Surface resolution info in UI (done items get "How it was fixed" section) | Next session |
| **M2 — PR B** | Comment thread (API + UI, flat threading) | Within 1 week |
| **M3 — PR C** | Edit-own-item (ownership check + edit form for pending items) | Within 2 weeks |
| **M4 — PR D** | My Items view + status-change notifications | Within 3 weeks |
| **M5 — design 2** | Re-evaluate after real usage — what's missing? upvote? auth polish? | After M4 |

---

## Success metrics

After M1-M4 ship and 30 days pass:
- **% of filed items that get a comment** (engagement signal)
- **% of bug-type items where reporter sees the fix** (closure signal)
- **# of returning filers** (people who file > 1 item over time)
- **Time-to-first-status-change** (responsiveness signal)

Baseline today: probably 0% on comments, ~0% on closure (no UI to see fix), small N on returning filers.

---

## Risks

- **Scope creep.** "Just one more feature" is the easy trap. Stick to M1-M4 then stop and re-evaluate.
- **Authentication friction.** If we add ownership checks but the auth flow is rough, users won't bother logging in to claim items. Magic-link auth via Resend is the bigger unblock — file as separate design doc.
- **Schema migration drift.** Adding `bh_backlog_upvote` table is later, but when we do, the existing seed_database CI failure (task #26) might bite us again. Investigate #26 BEFORE M4 ships.

---

## Open for review

This is **Draft 1**. Review with the same stage-based loop we used for LP CLI:
- Stage 1: read, leave per-section notes
- Stage 2: Tigs folds notes in → Draft 2
- Stage 3: structural review (sample wireframes for each PR's UI)
- Stage 4: locked design, build approval

But — per LP CLI lesson — don't over-design before any code ships. Recommend ship M1 (smallest, highest visual impact) BEFORE locking the rest. Iterate.

---

*"The backlog is the handshake between the people building the platform and the people using it. Make it feel like a conversation, not a complaint box."*
