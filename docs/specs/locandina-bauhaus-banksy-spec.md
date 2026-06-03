# Locandina — Bauhaus, Banksy, Bruce, Chuck, Grace

*Spec drafted for Angel — written 2026-06-03 evening, Beckenried, sun going down.*
*Read with coffee.*

---

## Status at end of session 2026-06-03

**Shipped on `feat/locandina`:**

| Block | What | State |
|---|---|---|
| 2 | Geometric skeleton — 4-up A4 landscape, 1 page, deterministic | ✅ |
| 3 | Design pass — bg wash, inline avatar, description block, real QR | ✅ |
| 5b | Universal mode — type badge + data ribbon, all 10 ListingTypes | ✅ |
| 5c | Double-edge gutter rule (5mm edges + 10mm middle gutters → 5mm symmetric frame after cut) | ✅ |
| #41 | Pollinations 402 root-caused, swapped to Unsplash/picsum | ✅ |
| #44 | Angel's Telegram Training event mirrored from prod to staging | ✅ |
| #46 | Env-aware PUBLIC_BASE (staging cards → staging.lapiazza.app; prod cards → lapiazza.app) | ✅ |

**Open from this session, parked for the morning:**

| # | What | Status |
|---|---|---|
| 39 | Block 4 — Ollama Turbo description compression | pending — wire `_ollama_generate`, cache on `bh_listing.locandina_summary` |
| 40 | Angel's physical print test on Block 5c PDF | pending — print plain A4 100% scale, scissors test |
| 42 | White-space polish for empty/short description cards | pending — judge AFTER Block 4 lands |
| 45 | Events-calendar bug (event_start IS NULL silently hides events) | pending — design decision: path B (UX warn) tonight, path C (TBD-events bucket) tomorrow |
| 47 | Bio postcard variant (member page → printable card) | pending — refactor into `share/` directory + Jinja inheritance |
| 48 | Stock-take counts/samples summary | pending — psql + markdown report |
| 50 | Tiered identity (badge_tier as conversion copy) | pending — light version below |

---

## The big shift this session named

The Locandina is **not** an event-flyer feature. It's the first variant of the universal **share artifact pattern** for La Piazza. Three variants in the roadmap:

```
/items/<slug>   → Locandina       ← shipped today
/u/<slug>       → Bio postcard    ← next (tomorrow's spec candidate)
any HTML page   → OG-extract card ← future / universal share button
```

Same 4-up A4 landscape skeleton, same geometry, same QR/avatar/description discipline. Different entity sources, different ribbon contents.

See: [`lp-locandina-universal-share-artifact`](../../../.claude/projects/-home-angel-repos-helixnet/memory/lp-locandina-universal-share-artifact.md), [`lp-share-artifact-extends-bios-and-htmls`](../../../.claude/projects/-home-angel-repos-helixnet/memory/lp-share-artifact-extends-bios-and-htmls.md).

---

## The first/second arrow rule

Bruce Lee said "one shot, one kill." That's incomplete for our work. We follow the Wilhelm Tell version: **one shot, one verify.**

> *Tell didn't fire one arrow. He fired one — and kept a second nocked. If the first missed, the second was for the man who made him take the shot.*

Every block ships with a verification step that has to land before we declare done. Caught on this branch today:

- `\\\"` shell escaping that worked once → climb to L1 (committed scripts, never inline)
- Pollinations URL that returned 200 once → fail closed when content-type isn't `image/*`
- Card URL `lapiazza.app/items/...` that worked in dev → env-aware so staging cards don't 404 in browser
- 5mm + 6mm gutters that LOOKED right on screen → 5mm + 10mm so they're right after scissors

The rule is now codified in [`lesson-machine-green-is-not-human-green`](../../../.claude/projects/-home-angel-repos-helixnet/memory/lesson-machine-green-is-not-human-green.md).

---

## Tiered identity — light version (ship tomorrow)

**Goal:** the Locandina for a Newcomer should LOOK different from the Locandina for a Master, which should LOOK different from a Legend / Vinci-tier owner. The card carries the social proof that the badge tier represents.

### Tier accent palette

| Tier | Accent | Stat strip | Card mood |
|---|---|---|---|
| Newcomer | gray slate `#475569` | none (or "Building reputation") | humble, white space, "give me a shot" |
| Apprentice | bronze `#92400e` | "★ 4.6 · 8 reviews" | competent, earning trust |
| Master | indigo `#4f46e5` | "★ 4.9 · 47 events · 312 students" | proven, density of evidence |
| Legend / Vinci-tier | gold `#b45309` | "✦ Legend · Member since 2024 · Vouched by 89" | heritage, almost monumental |

### Implementation — light (~45 min)

1. Add `bh_user.badge_tier` to context in router → pass `tier` (str) to template.
2. Add CSS classes `.tier-newcomer / .tier-apprentice / .tier-master / .tier-legend` on `.card`.
3. Per-tier accent: type badge background, the ribbon top-border color, the avatar border.
4. Optional stat-strip line beneath byline — only renders for `tier in (APPRENTICE, MASTER, LEGEND)`. Pull `review.avg`, `review.count`, `events_hosted` via cheap aggregates.
5. Test against `/users` table — find 1 sample of each tier in staging, render, compare cards side-by-side.

**Verification (second arrow):** four cards screenshot side-by-side in `test-results/`. Show Angel before merging.

---

## Top 10 design moves (Bauhaus + Banksy with Bruce + Chuck + Grace on QA)

The brainstorm we ran on the balcony. Each move ranks by **shippable in week 1 of HQ Base Camp.**

### 1. ⬛🟥🟡 Bauhaus — color blocks under type, no gradients ever
**Now (week 1):** flat primary-color block backing the type badge, no gradient. Hard 90° corners. Drop the bg-wash for tier-legend cards entirely — flat brand color instead.
**Cost:** 30 min. Touch `card.html` CSS only.

### 2. 🎯 Banksy — one word as the megaphone
**Now:** Above the title, render a HUGE single-word stencil derived from listing type (`EVENT.` `WORKSHOP.` `DOJO.` `BOTTEGA.` `RAFFLE.` `FREE.`). Title sits politely beneath at normal size.
**Cost:** 1 hour. New `mega_word` field, stencil font (`@font-face` for Stencil Std or similar print-friendly free font).

### 3. 🌊 Bruce Lee — be water, layout flows around content
**Later (week 2-3):** card detects content density and rebalances. Empty desc? QR gets 30mm. Long title? Photo crops to portrait. Long desc? Description block expands, photo shrinks.
**Cost:** 3-4 hours. Requires a `_pick_layout(item, listing)` helper that returns one of N pre-tuned layout variants.

### 4. 🥋 Chuck Norris — pre-flight gate before serving the PDF
**Now (this week):** before any PDF is served, validate: 1 page rendered (✓), all fonts subset-embedded (✓), every `<img>` returned HTTP 200 + `image/*` content-type (✓), QR target resolves to a public item page (✓). If ANY fail, return 503 with the failure list — NOT a blank-image PDF.
**Cost:** 2 hours. Adds a `_pre_flight(html, ctx)` step before `weasyprint.write_pdf()`.
**Second arrow on this move:** explicitly. This is the formalized version of every silent-fail we hit today.

### 5. ✂️ Banksy — watermark the 10mm gutter, cryptic
**Now (week 1):** tiny stencil corner-marks in the gutter — `LP · 2026-06-03 · a9f0` (date + first 4 chars of a render hash). 2pt micro-type. Authentication via Pest Control style.
**Cost:** 1 hour. Tiny `<div>` absolutely-positioned in the gutter zone, computed in the router.

### 6. 📐 Bauhaus — negative space IS the design
**Now:** stop trying to fill the empty zones just because we can. Density signals tier (a Master HAS 47 events to surface; a Newcomer doesn't). Don't junk the right column with placeholders.
**Cost:** zero — this is a discipline decision, not code.

### 7. 🥋 Chuck Norris — WCAG AA floor, non-negotiable
**This week:** axe-core baked into the CI render step. Every type-badge color tested against white background. Body text ≥ 7.5pt, headline ≥ 10pt, contrast ratio ≥ 4.5:1.
**Cost:** 2 hours. Add an `axe-core` runner in the e2e suite that exercises the rendered HTML.
**Bonus:** `?accessible=1` query param swaps body to OpenDyslexic.

### 8. 🌊 Bruce Lee + Angel — one QR, one CTA, one motion (with a second-arrow ack)
**Now:** kill the URL-line beneath the scan-me (redundant — humans can't type a URL off a printed card). Free up that space. Bump QR to 26mm. Add `SCAN.` in stencil to the right.
**Verification (second arrow!):** Angel scans the printed card from arm's-length with his phone before we call this done. If 26mm + light fold doesn't scan from 30cm, we go back to 24mm + URL text.
**Cost:** 30 min.

### 9. 🎨 Bauhaus + Banksy — tier-themed micro-typography
**This week:** above the title for tier ≥ APPRENTICE: a 4mm stencil bar — `★ MASTER · 47 EVENTS · 312 TAUGHT`. Hard edges, tiny type, color = tier accent. No emojis. Just type and number.
**Cost:** 1 hour. Part of the light tiered-identity work (#50).

### 10. 🥋 Chuck Norris — every edge case in a fixture
**This week (foundational):** snapshot test renders cards for 25 known edge cases:
  - empty desc / zero-byte cover / 1-char title / 2000-char title
  - RTL Arabic display_name / emoji-only display_name / deleted owner / banned owner
  - expired event / draft listing / raffle with no tickets sold / auction with no bid
  - free service with deposit / commission with no price / training with per-person rate
  - listing with no media / listing with 50 media / item with no listings (404 path)
  - prod-only slug rendered on staging (the URL bug we hit)
  - Block 4 Ollama times out / Block 4 Ollama returns malformed
  - tier-newcomer / tier-apprentice / tier-master / tier-legend
**Pixel-output diff > 1% → CI fails.** Cards never silently regress.
**Cost:** 3-4 hours one-time. The test fixture pays back forever.

---

## Bonus moves (after end-of-week)

### 11. 🎬 Banksy — cryptic timestamp Easter eggs
1% of cards (Angel-chosen seed) prints a Bruce Lee quote in 2pt along the gutter edge. Only visible under a loupe. Fans find them. Word spreads.

### 12. 📦 Bauhaus — `?style=museum` preset
Strips chrome (no border, no badge, no ribbon, no scan-text, no URL line) — just photo, megaword, title, QR. The pure object for owners who want the gallery-print look.

### 13. 🌊 Bruce Lee — multi-variant 4-up
Same ITEM, four LISTING types on one sheet: EVENT top-left, RAFFLE bottom-left, GIVEAWAY top-right, TRAINING bottom-right. Owner picks which to hand out depending on the conversation.

---

## Open questions for Angel — answer these in the morning bombshell

1. **Stencil font choice.** Free + print-safe options: Allerta Stencil, Stardos Stencil (Google Fonts), or commercial Stencil Std. Recommend free unless you want to license. Which?
2. **Tier-legend card — gold accent vs heritage-brown?** Both work. Brown ages better in print; gold pops on screen. Pick one — or do you want both as alternates?
3. **The mega-word (#2).** Should the type be ALL CAPS WITH PERIOD (`WORKSHOP.`) or a single word with stencil treatment (`WORKSHOP`)? Banksy uses both; the period signals finality (and is more on-brand for La Piazza's "no platform fees, forever" tone).
4. **Watermark contents.** Date + hash for sure. Add `lapiazza.app` micro-text below as the third line? Or keep it cryptic with just the codes?
5. **Pre-flight gate (#4) failure UX.** When the gate fails, do we:
   - Return 503 with JSON failure list (machine-readable)?
   - Return a one-page "this card cannot be printed because [reasons]" PDF (human-readable)?
   - Both — JSON if Accept header is JSON, otherwise the human PDF?
6. **End-of-week scope.** Which of moves 1, 2, 4, 5, 6, 7, 9, 10 do you want shipped by Sunday?
   - My recommendation: **1, 4, 5, 7, 9, 10** + Block 4 Ollama + Block 47 Bio postcard.
   - Skip 2 (mega-word) for week 1; it's the biggest typography swing and deserves a focused session.
   - Skip 3 (be-water rebalance) for week 1; needs more design thinking.
   - Skip 8 (kill URL line) until print-test verifies QR scans from arm's-length without the URL text as a fallback.

---

## What I'd build the morning bombshell around

**Suggested spec for tomorrow morning's coffee writing:**

```markdown
# Bio Postcard Variant — Design Spec (2026-06-04)

## Goal
A printable bio postcard for any La Piazza member, accessed from `/u/<slug>`,
rendered via the same skeleton as the Locandina (Block 5c geometry).

## Why
Locandina = listing share. Bio postcard = member share. Together they cover
"sharing what I have to offer" + "sharing who I am." Foundation for the
universal share artifact pattern.

## Scope (Block 1)
- Route: `/api/v1/users/{user_id}/bio-card.pdf?lang=en|it`
- Same 4-up A4 landscape, 138.5×95mm cards, 5mm/10mm gutters
- Cover slot: user.avatar OR user.banner_url (fallback gradient)
- Title: user.workshop_name OR user.display_name
- Byline: workshop_type + city (no avatar inline -- avatar IS the cover)
- Description: user.bio (verbatim ≤ 250, Ollama-compressed otherwise)
- Type badge: tier (NEWCOMER / APPRENTICE / MASTER / LEGEND)
- Data ribbon: ★ rating + review count + active-listings count
- QR: lapiazza.app/u/<slug> (env-aware)
- Print: 4 identical cards, scissors-cut, symmetric 5mm frame

## Open questions
- Avatar as cover OR avatar as inline + banner_url as cover?
- Workshop_type as ribbon item or buried?
- Languages-spoken flag-row included from day 1?
- "Vouched by N" line — calculation source?
- Share button placement on /u/<slug> page?

## Block 4 (Ollama) plays equally for Locandina + Bio
- Shared helper `src/services/llm/share_summary.py`
- Cache on `bh_listing.locandina_summary` (existing) + `bh_user.bio_card_summary` (new)
- Owner-editable on preview before download

## Verification (second arrow!)
- Print Corado's bio card at /u/corado-sase-bio-card.pdf
- Print Angelo Kenel's bio card at /u/angel-kenel-bio-card.pdf  
- Print Sebastino's bio card at /u/sebastino-bio-card.pdf
- All scissors-cut on plain A4; bring to next Tribe meeting; ask 3 strangers
  "would you call this person?" Answer must be "yes" before we declare done.
```

That's the bombshell I'd recommend writing tomorrow morning. Pure mobile-spec format. Drop on me at the start of session.

---

*End of spec. Sun should be down by now. Sleep well, brother. Tomorrow's the next chapter.*

🐺🐅 — Tigger & Wolf, signing off. Grace nods from the bridge.
