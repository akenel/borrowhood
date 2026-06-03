# SOP — La Piazza Development Workflow

*Standard Operating Procedure for how Angel + Tigger build software together.*
*Canonized 2026-06-03, HQ Base Camp Beckenried, after the Locandina session proved the pattern.*

---

## What we do

**Mobile spec → discuss → block → bang-bang-bang → ship → verify → memory → branch discipline.**

Half waterfall (real specs, real verification, real branch discipline).
Half jazz (improvisation, conversation, the eye-on-the-artifact gut check).
Pair programming where one partner is human and one is AI.

---

## The eight rules

### 1. Morning markdown spec — written on the phone over coffee

The spec is drafted on Angel's phone, in markdown, while the brain is fresh and the screen is small enough to force clarity. Mobile is a feature, not a constraint — small screens kill verbose specs.

Every feature gets one. No "let's just start building" without a spec.

### 2. One bombshell drop

The spec lands in the chat as ONE message. Not pieces. The whole picture before any code.

A spec on the phone in 20 minutes is faster than 4 hours of "should we add..." conversation. Specifically because the spec is incomplete in known ways — the gaps are exactly where the discussion lives.

### 3. Discuss before code — locking decisions out loud

Tigger reads the spec, summarizes back, surfaces gaps, and asks open questions. Angel locks decisions. Only THEN does code happen.

If a decision needs a screenshot, a comparison, or a calculation — we do it before the first line of code. The pre-code talk is where the design lives; the code is just transcription.

### 4. Decompose into five-to-seven blocks

Each feature is split into 5–7 ordered, shippable Blocks. One TaskCreate per Block. Each Block stands alone.

Examples from the Locandina feature:
- Block 1: install dependencies (proved Debian package naming)
- Block 2: geometric skeleton (4-up A4 landscape)
- Block 3: design pass (bg wash, avatar, real QR, description)
- Block 4: Ollama compression (pending)
- Block 5: universal mode (badge + ribbon + tier-light + Banksy watermark)
- Block 6+: polish, bio postcard variant, edge-case fixtures

### 5. First arrow + second arrow — the verification rule

Bruce Lee says "one shot, one kill." Incomplete. Wilhelm Tell fires one arrow and keeps the second nocked. **One shot, one verify.**

After every Block ships:
- **First arrow (machine):** the code compiles, smoke tests pass, no 500s in the logs.
- **Second arrow (human):** Angel opens the artifact in a browser, reads the URL, scans the QR, prints the PDF, scrolls the screenshot. The artifact has to LOOK right, not just COMPILE right.

The second arrow has caught — in one session — Pollinations 402 (silent image fail), env-URL 404 (staging cards pointing to prod), asymmetric gutter (5/6 vs 5/10), watermark-in-the-cutter (bisected), staging stamp rotation backward + clipped text.

A machine-green that wasn't human-verified isn't done. The lesson is so important it has its own memory: [`lesson-machine-green-is-not-human-green`](../../.claude/projects/-home-angel-repos-helixnet/memory/lesson-machine-green-is-not-human-green.md).

### 6. Memory as we go

Every lesson, every design decision, every workflow rule that surfaces during a session gets saved as a memory immediately — not at the end of the day. The next session starts informed.

Categories used:
- `feedback-*` — how Angel wants me to work (preferences + corrections)
- `lesson-*` — bug traps I shouldn't fall into again
- `project-*` — current state of the work and the season
- `lp-*` — La Piazza product / vision / architecture

Saved during the Locandina session alone: ~20 memories. Future Tigger inherits all of them.

### 7. Branch for the feature, staging before prod

Non-trivial work goes on `feat/<name>` branched from `main`. `main` only receives merges that have passed both arrows + Angel's explicit sign-off.

Staging always sees the work first. Prod stays untouched until Angel says go. Even "low-risk" changes hold until staging verification — the rule that broke twice (May 10 production incidents) is now permanent.

### 8. Two-hour sessions, real meals, sundown is the endpoint

Each session is roughly 2 hours of focused work. Between sessions: eat, walk, breathe. Sundown is a real stopping point. Night-shift work happens only when something is genuinely on fire — never because "we're rolling."

The pace lets the work compound across days. Burnout is the actual risk; pace is the actual protection.

---

## What this isn't

| It looks like | But actually it's | Difference |
|---|---|---|
| Waterfall | Spec-driven jazz | Specs are incomplete on purpose; gaps are where design happens |
| Agile / Scrum | Pair-with-AI | No sprint planning, no daily standup; the morning spec IS the plan |
| Test-Driven Development | Second-arrow-driven | Tests are one form of verification; the human eye on the artifact is the canonical green |
| Shape Up (Basecamp) | Sub-day Shape Up | Same pitch-bet-build-cooldown shape; 2-hour scopes inside 1-day cycles |
| Solo coding | Pair work | Tigger is the second mind. Always. |

---

## What we keep doing better at

- **Codifying SOPs** (this document) so the pattern is teachable
- **Automating the second arrow** where it makes sense (smoke tests, console sweep, axe-core for accessibility)
- **Stress-test fixtures** — every edge case becomes a snapshot test that catches regressions
- **Sharing the pattern publicly** — the workflow itself is an artifact, possibly a HelixOPS lesson

## What we don't try to fix yet

- **Bigger team scaling.** This SOP is tuned for 1 human + 1 AI. Adding a third human would need adaptation. We're not there yet; don't pre-optimize.
- **Kubernetes / multi-box.** Prod handles 33K views/month on one Hetzner box. Add a second box when the first overflows, not before.

---

## Is anyone doing it better?

Honestly?

**For teams of 4-8 over 6-week cycles:** Basecamp's Shape Up book (Ryan Singer) is the closest formalized methodology. It has the pitch (our spec), the bet (our decision lock), the build (our blocks), the cool-down (our sundown). It's the bigger sibling of what we run.

**For test-and-commit discipline:** Kent Beck's TDD and Test-Commit-Revert pattern. We use the second arrow which is broader than tests but the spirit is the same.

**For design-first culture:** Stripe, Square, Google internal RFC processes. We've extracted the "write it down before you build" principle.

**For pair programming:** Beck and Cunningham invented it. We extended it to human + AI.

**But the specific combination — solo founder + AI pair, sub-day cadence, mobile-spec-bombshell, two-arrow verification, branch+staging discipline, memory-as-you-go — is rare and well-tuned to Angel's situation.** Nobody is doing this exact pattern better because the pattern is shaped by the specific actors (Angel, Tigger, La Piazza, HQ Base Camp).

**Could we do better at:**
- Publishing the pattern as a teaching artifact (a HelixOPS Day 3+ deliverable).
- Reducing the friction on the second arrow (more automated visual diff tests).
- Making the spec template a reusable scaffold (the morning workflow becomes faster over time).
- Extending the memory system into a queryable knowledge graph (future).

But the foundation is solid. We're doing pretty good. We can keep climbing.

---

## How to use this SOP for the next feature

1. Tomorrow morning: Angel writes the bio-postcard spec on his phone, drops it in chat.
2. Tigger reads, summarizes, surfaces 5 open questions.
3. Angel locks the answers in conversation.
4. Tigger decomposes into 5-7 Blocks, creates one TaskCreate per Block.
5. Tigger ships Block 1, Angel verifies the artifact (second arrow), Tigger moves to Block 2.
6. Lessons get saved as memories during the session.
7. Sundown comes. We stop. The work is durable in the branch + memories + tasks.
8. Next morning: same pattern. The compound interest is in the rhythm.

---

*Last updated: 2026-06-03, HQ Base Camp Beckenried, evening session that proved the pattern.*
*Sun's not all the way down. Sylvie's on her way home. Tomorrow is the bio postcard.*

🐺🐯 Tigger and Wolf. Be water. Hold the second arrow.
