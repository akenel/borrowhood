# BorrowHood UAT Bug Report -- Round 2

**Date:** 2026-02-27
**Reviewer:** Tigs + Angel
**Source:** Puppeteer screenshots at 1920x1080 against https://46.62.138.218 (port 443)
**Previous round:** UAT-BUG-REPORT.md (15 bugs, 8 fixed in commit ae65c92)

---

## Scene-by-Scene Review

### Scene 01: Homepage Hero (01-hero.png)
**Status: PASS**
- Hero gradient renders correctly
- Nav shows: BorrowHood | Home | Browse | List Your Stuff | IT | Log In
- Stats bar: 28 Active Listings | 11 Members | 7 Categories | 5 Reviews
- How It Works section visible with 3 icons
- No issues found

### Scene 02: Recently Listed (02-how-it-works.png)
**Status: PASS**
- 6 item cards with AI-generated images
- Prices consistent: €5 per day, €10 per day, €8 flat rate
- Category badges display correctly (Kitchen, Tools)
- Owner names visible
- No issues found

### Scene 03: Origin Story + Footer (03-origin-story.png)
**Status: PASS**
- "The Story" section renders with full text
- Footer shows: BorrowHood | Free as in freedom. Open source. No platform fees. Forever.
- GitHub, Terms, Privacy links visible
- No issues found

### Scene 04: Browse Grid (04-browse-grid.png)
**Status: PASS**
- Category pills show real emoji: Cleaning, Crafts, Electronics, Garden, Kitchen, Sports, Tools
- Search bar, filter dropdowns, and sort all visible
- Item cards render with images, prices, categories, owners
- No issues found

### Scene 05: Browse Search + Filter (05-browse-search.png)
**Status: PASS**
- Search "drill" with Tools filter active
- Single result: Bosch Professional Drill/Driver Set
- €8 per day (+€30 deposit) clearly shown
- Language badges (EN native, DE C1) visible on owner
- No issues found

### Scene 06: Item Detail Top (06-item-detail-top.png)
**Status: PASS**
- Breadcrumb: Home / Browse / Bosch Professional Drill/Driver Set
- AI-generated drill image
- "Log In to Rent" button (V07 fix confirmed working)
- "Contact on Telegram" button
- Listed By: Mike's Garage with owner badges
- Location map with Leaflet
- Description and Compatible With sections
- No issues found

### Scene 07: Item Detail -- Reviews (07-item-detail-listings.png)
**Status: 2 BUGS**

**BUG-R2-01: Review dates show "Invalid Date" (MEDIUM)**
All 3 reviews display "Invalid Date" instead of an actual date.
- "Perfect drill, great neighbor!" -- Invalid Date
- "Solid equipment, easy pickup" -- Invalid Date
- "Heavy duty, does the job" -- Invalid Date

Root cause: Seed data creates reviews with `created_at` set by SQLAlchemy default (server_default=now()), but the template is likely trying to format the date with JavaScript or a Jinja filter that doesn't handle the datetime object correctly.

**BUG-R2-02: Review badge shows raw tier name (LOW)**
Badge labels show lowercase: "trusted", "pillar" instead of "Trusted", "Pillar".
Minor -- capitalize the badge tier display.

### Scene 08: Workshop Profile (08-workshop.png)
**Status: 1 BUG**

**BUG-R2-03: Skills still show "categories.baking" (MEDIUM)**
V10 fix from last round is NOT rendering on the live server.
- Pastry Making -- categories.baking · 40y
- Cake Decorating -- categories.baking · 35y
- Bread Baking -- categories.baking · 30y

Root cause: Either (a) the volume mount didn't pick up the template change, or (b) the fix logic isn't working correctly. Need to verify the deployed template.

### Scene 09: Workshop Items (09-workshop-items.png)
**Status: SAME AS SCENE 08**
Same "categories.baking" bug visible when scrolled down.
Items section looks good -- 3 items with thumbnails (Cookie Cutters, KitchenAid, Recipe Book).

### Scene 10: Italian Homepage (10-italian.png)
**Status: PASS**
- Full Italian translation: "Ogni Garage Diventa un Negozio di Noleggio"
- Nav translated: Esplora, Pubblica Oggetto, Accedi
- Stats translated: Annunci Attivi, Membri, Categorie, Recensioni
- How It Works translated: Pubblica i Tuoi Oggetti, Stabilisci le Tue Condizioni, Connettiti
- No issues found

### Scene 11: List Item Form (11-list-item.png)
**Status: 1 BUG**

**BUG-R2-04: Condition dropdown not translated (LOW)**
Page is in Italian (carried from scene 10 via cookie) but the Condition dropdown shows "Good" instead of Italian equivalent.
All other fields are properly translated.

### Scene 12: Dashboard (12-dashboard.png)
**Status: PASS (for what it shows)**
- Empty state with "Pubblica il Tuo Primo Oggetto" CTA
- Tabs: I Miei Oggetti | I Miei Noleggi | Richieste in Arrivo
- Italian translation working
- This scene is inherently empty (no logged-in user) -- consider removing from video

### Scene 13: Terms Page (13-terms.png)
**Status: PASS**
- Full Italian terms render correctly
- 7 sections visible: Cos'è BorrowHood, Il Tuo Account, Annunci e Transazioni, etc.
- Last updated date shown
- No issues found

### Scene 14: Onboarding (14-onboarding.png)
**Status: PASS**
- "Benvenuto su BorrowHood" with 3-step wizard
- V13 fix confirmed: "Avanti" button (not "Next")
- All fields translated: Nome Visualizzato, Città, Codice Paese, Breve Biografia
- AI Espandi button for bio expansion
- No issues found

### Scene 15: Browse Italian (15-browse-italian.png)
**Status: PASS**
- "Esplora Oggetti" heading
- Category pills translated: Pulizia, Artigianato, Elettronica, Giardino, Cucina, Sport, Attrezzi
- Filter dropdowns translated
- Item cards with prices: €5 a giorno, €10 a giorno
- No issues found

---

## Bug Summary -- Round 2

| ID | Scene | Severity | Description | Status |
|----|-------|----------|-------------|--------|
| R2-01 | 07 | MEDIUM | Review dates show "Invalid Date" | OPEN |
| R2-02 | 07 | LOW | Review badge tier not capitalized | OPEN |
| R2-03 | 08,09 | MEDIUM | Skills still show "categories.baking" | OPEN (V10 fix failed) |
| R2-04 | 11 | LOW | Condition dropdown not translated | OPEN |

## Fix Priority (for video)

1. **R2-01** -- Invalid Date on reviews (most visible, ruins the social proof section)
2. **R2-03** -- categories.baking on workshop (still broken from R1)
3. **R2-02** -- Badge tier capitalization (quick fix)
4. **R2-04** -- Condition dropdown (only visible in Italian)

## Video Optimization Notes

- Scene 12 (Dashboard) adds nothing -- empty state, no logged-in user. CUT from video.
- Scene 10 and 15 both show Italian -- keep 10 (homepage), consider cutting 15 (browse is same as 04).
- Scene 13 (Terms) is okay for showing completeness but low value. Consider cutting.
- Optimal video: 11-12 scenes, ~45 seconds, tighter story.
