# SOP: BorrowHood Season Bible & Cast Management

**SOP-VID-003** | Notion Motion Pictures | v1.0 | 2026-03-06

---

## Purpose

Ensure every BorrowHood video season has a consistent cast, storyline continuity, and production pipeline. Prevent continuity errors across episodes. The pilot sets the rules -- every episode follows them.

---

## 1. Cast Management

### The Rule

**Every character mentioned by name in any episode MUST exist in all three places:**

| Layer | File | What It Does |
|-------|------|-------------|
| Keycloak realm JSON | `keycloak/borrowhood-realm-dev.json` | Auth -- user can log in |
| Seed data | `seed_data/seed.json` | Profile, skills, items, points |
| Demo-login cast list | `src/routers/pages.py` (demo_users) | Visible on the cast/login page |

If a character is in ONE layer but not all THREE, it will break. No exceptions.

### Adding a New Cast Member

1. **Seed data first** -- add full user block to `seed.json` (slug, email, bio, skills, points)
2. **Keycloak second** -- add user block to realm JSON (username, email, password, roles, groups)
3. **Demo-login third** -- add entry to `demo_users` list in `pages.py`
4. **Verify** -- `python3 -c "import json; json.load(open('seed.json'))"` + same for realm JSON
5. **Deploy** -- rebuild platform container, Keycloak imports realm on startup

### Username Conflicts

Check for email collisions BEFORE creating. Example: `sofia@borrowhood.local` was taken by Sofia Ferraro (photographer). Sofia Ferretti (Pietro's niece) uses `sofiaferretti@borrowhood.local`.

### Cast Roster (Season 1 -- Trapani)

| # | Username | Character | Badge | Role | Arc |
|---|----------|-----------|-------|------|-----|
| 1 | angel | Angelo Kenel | legend | admin | The Black Wolf, platform creator |
| 2 | nino | Nino Cassisa | pillar | operator | Camper & Tour, community backbone |
| 3 | leonardo | Leonardo da Vinci | legend | moderator | The original maker, dispute wisdom |
| 4 | sally | Sally Thompson | trusted | lender | Cookie queen, mentor to Sofia |
| 5 | mike | Mike Kenel | pillar | lender | Tool shed, 500 inherited tools |
| 6 | marco | Marco Moretti | active | lender | Furniture repair, manages Rosa's profile |
| 7 | pietro | Pietro Ferretti | active | lender | Drone pilot, Sofia's uncle |
| 8 | jake | Jake Chen | active | lender | Maker space, 3D printing |
| 9 | george | George Clooney | pillar | lender | Villa Oleandra cameo, espresso |
| 10 | john | John Abela | newcomer | lender | Johnny -- broken bike, local delivery |
| 11 | maria | Maria Ferretti | newcomer | lender | Family connection |
| 12 | sofiaferretti | Sofia Ferretti | newcomer | member | Pietro's niece, 17, baking apprentice |
| 13 | rosa | Rosa Ferretti | newcomer | member | 84yo nonna, Marco manages her profile |
| 14 | anne | Anne Muthoni | active | qa-tester | Quality gate |

---

## 2. Storyline Continuity

### The Syd Field Rule

**Know the ending before you write the pilot.**

Every character on the cast page has a REASON to be there. That reason is their arc -- their journey across the season. Document it BEFORE recording the pilot.

### Season 1 Story Arcs

| Arc | Characters | Episodes | Summary |
|-----|-----------|----------|---------|
| The Crash | Sally, Pietro | EP1 (pilot) | Drone rental, crash, dispute, resolution, peace offering |
| The Cookie Run | Sally, Pietro, Sofia, Johnny | EP2 | Cookie delivery by drone. Sofia's first bake. Johnny's broken bike. |
| The Scooter | Johnny, Sally | EP3-4 | Sally's cookie profits buy Johnny an electric scooter |
| The Apprentice | Sofia, Sally, Pietro | EP2-5 | Sofia learns baking from Sally, drone flying from Pietro |
| The Cameos | George, Leonardo | EP3-4 | George lends espresso machine. Leonardo moderates a dispute. |
| The Partnership | Sally, Pietro | EP5+ | Drone cookie delivery business launches |

### Continuity Checklist (Before Recording)

- [ ] Every name mentioned in the script exists on the cast page
- [ ] Full names used (not "my niece" -- say "my niece Sofia")
- [ ] No contradictions with previous episodes
- [ ] New characters added to all 3 layers (KC, seed, pages.py)
- [ ] Mentorship relationships seeded if applicable
- [ ] Backlog items created for future arcs planted in this episode

---

## 3. Episode Production Pipeline

### Pre-Production

1. Write script (Puppeteer recording script)
2. Review cast -- does this episode need new characters?
3. Add characters to all 3 layers if needed
4. Create backlog items for seeds planted in this episode
5. Run pre-recording cleanup SQL
6. Verify demo-login shows all cast members

### Recording

7. OBS Screen Capture (NOT Window Capture)
8. Run recording script on Hetzner
9. Play 10 seconds immediately after -- verify browser content visible

### Post-Production

10. Trim raw footage (re-encode, NOT copy)
11. Brotherhood Run at 40%, fade in 3s, fade out 5s
12. Final merge
13. Thumbnail (1280x720)
14. YouTube kit (metadata, description, tags)

### The Final Card Rule

Every episode ends with THE QUESTION -- not a checklist, not a summary.

- Dark background (#0f172a)
- Setup lines: name each character and their situation
- THE QUESTION in gold (#FCD34D), 72px, bold
- "to be continued" in small caps, faded
- 16 seconds hold
- Brotherhood Run fades out over this card

---

## 4. Mentorship System

### Model: `src/models/mentorship.py`

Three types:
- **Mentor** -- ongoing teaching relationship
- **Apprentice** -- formal long-term skill building
- **Intern** -- short-term project-based learning

Five statuses: proposed -> active -> paused -> completed / cancelled

### Season 1 Mentorships (Seeded)

| Mentor | Apprentice | Type | Skill | Status |
|--------|-----------|------|-------|--------|
| Sally Thompson | Sofia Ferretti | apprentice | Baking | active |
| Pietro Ferretti | Sofia Ferretti | apprentice | Drone Piloting | proposed |
| John Abela | Sofia Ferretti | intern | Local Delivery | proposed |

---

## 5. Backlog for Video Series

Use the BorrowHood backlog system (`/backlog`) with these tags:

- `video` -- video production tasks
- `season1` -- Season 1 specific
- `storyline` -- character arc / story planning
- `pilot` -- pilot episode specific
- `mentorship` -- mentorship feature work
- `planning` -- future season planning

Backlog items BL-057 through BL-066 cover Season 1 planning.

---

## 6. Season Boundaries

| Season | Realm | Location | Cast | Status |
|--------|-------|----------|------|--------|
| Season 1 | borrowhood | Trapani, Sicily | 14 members | In Production |
| Season 2 | TBD | TBD | New cast | BL-066 (planning) |

Each season gets its own Keycloak realm, seed data, and cast. Same platform. Same format. Different world.

---

*"The pilot plants every seed. The season grows them. The finale harvests."*
