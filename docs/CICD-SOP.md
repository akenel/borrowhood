# CI/CD SOP — La Piazza

*Standard Operating Procedure for shipping changes to La Piazza (BorrowHood).*
*Owner: Tigs + Angel. Established 2026-05-26, Tuesday night, camper south of Como.*

> **The deal:** Angel does UX testing on a base that's already been
> machine-verified. Tigs runs the test suite + console checks and clears
> the obvious issues *before* handing anything over. CI is the net under
> the trapeze — if it's red, nobody performs.

---

## Why this exists

The fear is rational: fix X, break Y, or miss something obvious. Willpower
doesn't solve that — machinery does. This SOP is the machinery. It was
written the night CI came back from 9 days of silent failure and immediately
surfaced a real test gap (pg_trgm search) nobody had noticed.

---

## 1. Before Tigs hands Angel anything to test

Run, in order. Do not say "ready for your eyes" until all pass.

1. **Full test suite** — `pytest -q` from the BorrowHood root.
   - Must be green, OR Tigs states exactly which tests are red and why,
     and whether they're pre-existing vs. caused by this change.
   - Never hand over a change that turned a green test red without saying so.

2. **Console / curl check the touched surface** — for every endpoint or
   page this change affects, hit it and read the **status code**, not just
   "looks right":
   - New/changed API endpoint → `curl -w "%{http_code}"`, confirm 2xx for
     the happy path and the right 4xx for the guard paths (403/400/429).
   - New/changed page → curl it, grep for the element that should render
     (the actual class/text), confirm the conditional fires. Visual
     inspection alone has lied to us repeatedly (the enum-casing bugs).
   - Anything with auth → mint a real token, test as the right + wrong user.

3. **Deploy to prod** following the Deploy SOP (`--env-file uat.env` every
   time — see the HELIX_PUBLIC_HOST gotcha).

4. **Smoke check** — health endpoint + the specific pages/endpoints changed.
   `curl https://lapiazza.app/api/v1/health` must be `healthy`.

5. **Then** tell Angel: "ready — here's what changed and what to look at."

---

## 2. CI is the gate (GitHub Actions, .github/workflows/ci.yml)

- Runs on every push + PR to main.
- Steps: install deps → `scripts/ci_seed.py` (create_tables + run_migrations
  + seed) → `pytest tests/ -v`.
- **A red CI run is a stop sign.** Investigate before building on top.
- **CI must never fail silently.** If a step exits non-zero with no visible
  reason, fix the visibility first (we lost 9 days to a swallowed traceback).
- When CI surfaces a failure, classify it: real bug vs. test-infra gap vs.
  stale assertion. Fix the real ones; update the stale ones; never delete a
  test to make CI green.

---

## 3. Regression discipline

- **When the same bug appears twice, write a test that fails on it.**
  Example: `tests/test_enum_casing_traps.py` exists because the
  uppercase/lowercase enum bug hit 4 times. Now CI blocks its return.
- **When you fix one instance of a pattern, grep for all instances.**
  "If one seal fails, check all the seals." (CLAUDE.md). The casing bug,
  the apostrophe-in-attribute bug, and the field-saved-but-not-displayed
  bug were each a *class*, not a one-off.
- **Every state transition that affects a user must notify that user.**
  Raffle draw, raffle cancel, quote status changes — a silent transition
  is a bug even when the data is correct.

---

## 4. Known traps (check these before debugging deeper)

These have each bitten us. When a symptom matches, check here first.

| Symptom | Likely cause | Fix |
|---|---|---|
| UI action does nothing, prod logs show **zero requests** | client-side: JS syntax error, dead onclick, or stale cache | check the rendered HTML / console, not the backend |
| Raw JavaScript **dumped as text** on the page | apostrophe in a single-quoted `x-data='{...}'` (e.g. "can't") | use full words ("cannot"), or `\|tojson` for i18n |
| A status filter / comparison silently matches nothing | enum `.value` is lowercase but code compares uppercase (or vice versa) | match the enum's real `.value`; see test_enum_casing_traps |
| Field saved but not shown | the display template / page never renders it | the data layer working ≠ the feature working; check the view |
| `func.similarity` / search 500 on a fresh DB | `pg_trgm` extension missing | `CREATE EXTENSION IF NOT EXISTS pg_trgm` in run_migrations |
| PWA shows letter monogram, not the logo | maskable icon has no safe-zone padding | separate `any` + padded `maskable` icons |

---

## 5. What Angel does (the human layer)

- UX-tests on a machine-verified base — finds the things tests can't:
  confusing copy, missing fields, "this feels wrong," real-world flows.
- Reports what he sees; Tigs tunes. Repeat until both are happy.
- Drives the irreversible/outward-facing actions (publish, real money,
  account changes) — Tigs prepares, Angel pulls the trigger.

---

*"The difference between 4-star and 5-star is not intelligence. It's consistency."*
*"Run the tests before you hand it over. Every time. That's the whole SOP."*
