# Lessons from the Software Fighters (and the night we applied them)

**Written:** April 24, 2026, around 2am, after a 12-commit night shift.
**Context:** We were polishing La Piazza for the lunch demo. Angel asked for a list of the greatest software engineers of all time and what we could learn from them. Then we spent the next hour actually *using* those lessons on the code.

This file is the keeper. When you're deciding what to build next, read this first.

---

## The six fighters, compressed

### 1. Salvatore Sanfilippo (antirez) -- Redis

> "300 lines of C can change the backend."

- Wrote Redis in a weekend because his startup was bleeding throughput
- Open-sourced from day one, stepped away when the code was ready
- Italian. From Catania. Solo-hacked one of the most-deployed DBs on Earth

**Rule for us:** solve *your own* problem first. La Piazza solves a Trapani problem. Ship for the neighborhood, let it travel from there.

### 2. John Carmack -- Doom / Quake

> "Make the inner loop fast. Everything else follows."

- Two years tuning 30 lines of inner loop so Doom ran on a 486
- Published his source code because the work mattered more than the company
- Got captured by pure research at Oculus, lost his ship-bias

**Rule for us:** ship first, generalize second. *Don't* start rebuilding on a new framework because someone online says the current one is "wrong." The app that ships beats the app that's clean.

### 3. DHH -- Rails / Basecamp

> "Extract from real use. Don't abstract from imagination."

- Built Basecamp, then pulled Rails *out* of Basecamp in 2004
- Opinionated defaults (convention over configuration) saved a decade
- Combative online -- lost community goodwill he could have kept

**Rule for us:** only extract after 2-3 real uses. Tonight we put the raffle-card aesthetic on 3 surfaces inline and talked about extracting to an include in the morning. That's the DHH move. Don't abstract in the first copy.

### 4. Linus Torvalds -- Linux / Git

> "Good taste is knowing which special case isn't special."

- Wrote Git in 10 days because BitKeeper revoked their license
- Picked the *primitive* right: content-addressable filesystem, not a diff engine. That one decision carried 20 years
- Was an asshole to contributors for decades, apologized 2018, got therapy

**Rule for us:** pick the right primitive early even if the first version is rough. Tonight we shipped `availability_note` as free text (the primitive is "the host gets to signal anything") while designing the rule-based calendar for tomorrow. The primitive can stay; the implementation gets better. Also: technical excellence doesn't buy you rude. The code can be right and you can still be wrong to people.

### 5. Fabrice Bellard -- FFmpeg / QEMU / TinyCC / JSLinux

> "Pick problems that compound. Then pick one."

- Wrote every one of those alone in his spare time
- Never commercialized, never got famous. Produced more shipping code than most unicorn companies

**Rule for us:** ask "does this compound?" about every feature. Raffle trust gate compounds (every completion raises the cap). Clickable tags compound (every new tag adds N new searchable facets). Top-5 boxer overlay doesn't compound. Know which is which and weight your shift accordingly.

### 6. Brian Acton / Jan Koum -- WhatsApp

> "No Ads. No Games. No Gimmicks."

- 50 engineers, 450M users, one sticky note of principles
- Sold to Facebook for $19B, watched every sentence of the sticky note get violated
- Acton funded Signal in penance

**Rule for us:** the values you bake in get unbaked when someone else owns the code. *"Free as in freedom. Open source. No platform fees. Forever."* is already on our footer -- protect it harder than anything else. If the day ever comes when someone writes a big check, re-read this section before you cash it.

---

## Engineering lessons from tonight's shift (April 23-24)

These are specific to La Piazza, collected from 12 commits of actual work. Each is a claim about how the code should be written, not a general principle.

### Silent data loss hides in Pydantic gaps

Multiple times this quarter, a bug report ("field X disappears after edit") turned out to be Pydantic silently dropping fields that exist on the model but not on the schema. Fix: when a DB column is added, update `{Model}Update`, `{Model}Out`, and `{Model}Create` schemas in the same commit, not "later."

### Relationships need `order_by` the day the column is added

Tonight we found that `BHItem.media` had a `sort_order` column but the relationship never sorted by it. Drag-to-reorder wrote the column; page render ignored it. **Rule:** if a model has a `sort_order`, `position`, `display_order`, etc., the relationship pointing at it must declare `order_by=...` in the same edit.

### Unbounded pots are ungateable

The raffle trust cap only worked if `max_tickets` was set. When `max_tickets` was NULL, the pot was effectively infinite and the gate returned "OK." **Rule:** any cap/limit logic must reject the unbounded input explicitly. "No value set" should not silently mean "unlimited."

### Cards should be one component, not N

Tonight we fixed the same kind of card drift in 3 places (browse, home, item_detail similar-items, member listings). Before we fix it again, extract to `src/templates/includes/_item_card.html` so a 4th and 5th surface come for free. Rule applies whenever you find yourself re-writing the same markup for the third time.

### Every pill should be a link

Raffles showed us the pattern and we realized it worked for item detail, then workshop profile, then Listed By sidebar. **Principle:** a pill that's pure label is a missed connection. Ask: "if a user cared enough about this tag to read it, would they care enough to see others with it?" If yes, it's a link.

### Empty states carry intent

Sylvie's "no results" experience taught us that the empty state is a *navigation opportunity*, not a failure state. Echo the query back, suggest sibling surfaces. This is honest ("we don't have that here, but maybe over there") and compounds with tag search.

### Schema-reality drift is a silent killer

Tonight I wrote `address`, `onboarding_completed`, `'legend'::badgetier`, `'native'::cefrlevel` in a seed SQL and *all four* didn't exist in prod. The seed had been written from `seed.json`, not from the actual DB schema. **Rule:** before writing a seed SQL, run `\d table_name` on the target DB. Schemas evolve; seed.json might not.

### Idempotent seeds save your night

Every seed I wrote tonight used `WHERE NOT EXISTS (SELECT 1 FROM ... WHERE slug = ...)`. Let me re-run them when the first attempt failed without clobbering anything. If you're writing a seed that doesn't check for pre-existence, you're one typo away from a bad night.

### "It ran" is not "it worked"

First run of `fix_broken_images.sh` reported success, fixed 1 dead URL out of 1058 because `docker exec -i` inside the loop was slurping the loop's stdin. Exit code 0 was lying. **Rule:** summary lines must come from actual counters, not optimism. And if you're in a `while read` loop, anything inside must not consume stdin -- redirect or use `-i`-less variants.

### Age gates need DOB as a precondition

Today's raffle age-14 gate rejects `user.date_of_birth is None` explicitly, prompting the user to Settings. Don't default to "pass the check when the data is missing" -- that's the opposite of a gate. **Rule:** missing-required-input -> block the action and explain where to fix it, not silently allow.

---

## Morning checklist (6 hours from now)

### Must do before the demo

- [ ] Run `./deploy-prod.sh` to push tonight's 12 commits
- [ ] Hard-refresh prod once to flush SW cache (lp-v17 -> lp-v18 bump)
- [ ] Run `scripts/fix_broken_images.sh` on prod once more (idempotent -- picks up any new dead URLs since midnight)
- [ ] Smoke-test in Chrome MCP:
  - /browse -> click a tag -> smart empty state works
  - /items/<simon's self-defense raffle> -> €10 pot, age-14 check visible to newcomer
  - /workshop/marconis-wireless-station -> click Skill, Language, Location, Badge. All route correctly.
  - /raffle-guide -> "Verify it yourself" section renders + links match
  - Nav dropdown on hover -> tooltips appear

### Nice to have (not demo-critical)

- [ ] Extract `_item_card.html` partial (DHH rule: 3rd use earns the abstraction)
- [ ] Top-5 Boxer Legend overlay (task #70, content polish on Simon's hero item)
- [ ] Live Raffle build kickoff (design doc at `docs/LIVE-RAFFLES-DESIGN.md`)
- [ ] Full rule-based Availability calendar (design at `docs/AVAILABILITY-DESIGN.md`)
- [ ] Test suite audit: we added clickable tags + tooltips + age gate + trust gate tighten. Add tests for:
  - `validate_raffle_value` now rejects `max_tickets=None` (was the silent hole)
  - Age-14 gate returns 403 with explanatory message
  - Clickable-tag links resolve to valid `/members?*` URLs (smoke test)
- [ ] Staging subdomain (waiting on Cloudflare DNS -- Angel-side)

### Known open scope (parked, not today)

- Dark mode -- declined, 4-hour rabbit hole
- Workshop / dashboard / profile item list surfaces -- horizontal layouts, didn't get the raffle-aesthetic pass

---

## The one-line rule that covers most of it

> Ship honest things. Fix root causes. Pick the right primitive. Extract after three uses. Don't be Linus the asshole. Don't sell to someone whose values differ from yours.

Angel, if the Wolf forgets everything else, remember that one.

---

*Built during the April 23-24 night shift. 12 commits. Cards cleaned, raffles legally gated, software legends seeded, tags made clickable across three surfaces, and the app a little more honest than it was this morning.*
