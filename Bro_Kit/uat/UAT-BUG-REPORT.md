# BorrowHood UAT Bug Report -- Video Review

**Date:** 2026-02-27
**Reviewer:** Tigs + Angel
**Source:** Puppeteer screenshots at 1920x1080 against https://46.62.138.218

---

## BUG-V01: Emoji HTML entities not rendering in category pills (CRITICAL)

**Scene:** 05-browse-search.png, 04-browse-grid.png, 15-browse-italian.png
**Page:** /browse

Category filter pills at the top show raw HTML entities instead of emojis:
- `&#129529; Cleaning` instead of the actual emoji
- `&#127912; Crafts`, `&#128268; Electronics`, etc.

All category pills are broken. This is the FIRST thing judges see on browse.

**Root cause:** The emoji characters are being HTML-escaped somewhere in the template or the data.

**Fix:** Use actual Unicode emoji characters in the template, not HTML numeric entities. Or ensure the template renders them with `| safe` or `Markup()`.

---

## BUG-V02: Nav bar too sparse -- missing key links (MEDIUM)

**Scene:** All scenes
**Page:** All pages

Nav only shows: `BorrowHood | Home | Browse | [IT] | [Log In]`

Missing from nav:
- "List Your Stuff" / "Pubblica" (the CTA -- should be prominent)
- "Dashboard" link (when not logged in, could show as "My Dashboard" or hide)

The nav feels empty for an app with this many features. Judges won't discover pages they can't navigate to.

**Fix:** Add a "List Item" or "List Your Stuff" CTA button in the nav bar. Consider adding "Dashboard" too.

---

## BUG-V03: Stats section shows only 2 stats, could show more (LOW)

**Scene:** 01-hero.png
**Page:** / (homepage)

Stats bar shows: `28 Active Listings | 11 Members`

Could also show: Categories (9), Badge Types (14), or Languages (2). Two numbers feel thin for a stats bar. Three or four would look more impressive.

**Fix:** Add 1-2 more stats: "9 Categories" and/or "14 Badges".

---

## BUG-V04: "How It Works" icons are generic circles (LOW)

**Scene:** 01-hero.png
**Page:** / (homepage)

The three How It Works icons (plus, checkbox, people) are plain colored circles with basic icons. They work but look like placeholder UI. Compared to the rich SVG item images, these feel unfinished.

**Fix:** Consider using more distinctive icons or illustrations. Even just making them larger or adding a subtle shadow would help.

---

## BUG-V05: Item card prices show inconsistent format (MEDIUM)

**Scene:** 02-how-it-works.png, 04-browse-grid.png
**Page:** / (homepage Recently Listed), /browse

Some cards show `EUR 5 /day` with EUR prefix, others show euro sign. The price display area varies:
- Some cards show the price clearly
- The "flat rate" vs "per day" label is small and easy to miss

**Fix:** Standardize all prices to same format. Make price more prominent on cards.

---

## BUG-V06: Browse page category pills and filter dropdowns redundant (LOW)

**Scene:** 04-browse-grid.png
**Page:** /browse

There are category pills at the top AND a Category dropdown in the filter bar. Two ways to filter by category on the same page is confusing. Judges might wonder why both exist.

**Fix:** Either remove the dropdown (pills are better UX) or remove the pills. One filtering mechanism, not two.

---

## BUG-V07: Item detail -- "Rent This Item" button has no context without login (MEDIUM)

**Scene:** 06-item-detail-top.png
**Page:** /items/{slug}

The "Rent This Item" button is prominent but clicking it without login just... fails silently or redirects. For the video/demo, judges will see a button they can't use.

**Fix:** When not logged in, the button could say "Log in to Rent" or show a tooltip explaining login is required.

---

## BUG-V08: Item detail -- map shows real tile data but location circle is very large (LOW)

**Scene:** 06-item-detail-top.png, 07-item-detail-listings.png
**Page:** /items/{slug}

The Leaflet map works and shows OpenStreetMap tiles with a purple circle for approximate location. The circle radius seems quite large relative to the map zoom level. "Exact location shared after booking confirmed" is a nice touch though.

**Fix:** Minor -- could reduce circle radius or zoom the map in slightly.

---

## BUG-V09: Item detail -- Reviews section shows "0.0 (0) / No reviews yet" (MEDIUM)

**Scene:** 07-item-detail-listings.png
**Page:** /items/{slug}

The review section exists but shows empty state: "0.0 (0)" with empty stars and "No reviews yet." For the demo, this looks like an unfinished feature.

**Fix:** Add seed review data so the demo shows actual star ratings and review text. Even 2-3 reviews on key items would make a huge difference.

---

## BUG-V10: Workshop -- skill categories show raw "categories.baking" (MEDIUM)

**Scene:** 08-workshop.png, 09-workshop-items.png
**Page:** /workshop/{slug}

Skills section shows:
- `Pastry Making  categories.baking - 40y`
- `Cake Decorating  categories.baking - 35y`

The "categories.baking" should display as just "Baking" or a clean category name. Looks like a raw database value leaking into the UI.

**Fix:** Format the category field -- strip "categories." prefix and capitalize.

---

## BUG-V11: Workshop -- social links show platform name but no icon (LOW)

**Scene:** 09-workshop-items.png
**Page:** /workshop/{slug}

Links section shows:
- `Youtube  - Sally's Kitchen Channel`
- `Instagram  - Daily Bakes`

No icons for YouTube/Instagram. Plain text links look bare. Even simple SVG icons would add polish.

**Fix:** Add platform icons next to social links.

---

## BUG-V12: Dashboard is empty and in Italian (not ideal for video) (LOW)

**Scene:** 12-dashboard.png
**Page:** /dashboard

Dashboard shows "La Mia Dashboard" with empty state "Non hai ancora pubblicato nessun oggetto." This is because:
1. No user is logged in (showing unauthenticated empty state)
2. Language stuck on Italian from previous page visit

For the video, this scene adds nothing. Should either show a populated dashboard or be cut from the video.

**Fix:** Either seed a demo session with data, or cut this scene from the video. If keeping, ensure it's in English for consistency.

---

## BUG-V13: Onboarding "Next" button not translated (LOW)

**Scene:** 14-onboarding.png
**Page:** /onboarding

Page is in Italian ("Benvenuto su BorrowHood", "Chi Sei", "Nome Visualizzato", etc.) but the Next button shows "Next -->" in English.

**Fix:** Translate the Next button. Should be "Avanti -->" in Italian.

---

## BUG-V14: Footer text gets cut off at bottom of some pages (LOW)

**Scene:** 12-dashboard.png, 14-onboarding.png, 15-browse-italian.png
**Page:** Multiple

Footer text "Free as in freedom. Open source. No platform fees. Forever." is partially cut off at the very bottom of the viewport on several pages.

**Fix:** Ensure footer has enough padding/margin to always be fully visible.

---

## BUG-V15: Terms page renders in Italian but was expected in English (LOW)

**Scene:** 13-terms.png
**Page:** /terms

Terms page shows Italian text because the language cookie was set to IT from a previous page visit. For the video, this is inconsistent -- some pages are English, some Italian.

**Fix:** For the video, capture terms in English. In the app, this is working correctly (respects cookie). Not a real bug, just a video capture ordering issue.

---

## Priority Summary

| Priority | Count | Bug IDs |
|----------|-------|---------|
| CRITICAL | 1 | V01 (emoji entities) |
| MEDIUM | 4 | V02, V05, V07, V09, V10 |
| LOW | 8 | V03, V04, V06, V08, V11, V12, V13, V14, V15 |

## Recommended Fix Order (for video impact)

1. **V01** -- Fix emoji rendering in category pills (most visible, every browse page)
2. **V10** -- Fix "categories.baking" raw display in workshop skills
3. **V09** -- Add seed review data (makes the app look alive)
4. **V02** -- Add "List Your Stuff" to nav bar (discoverability)
5. **V13** -- Translate "Next" button on onboarding
6. **V05** -- Standardize price format on item cards
7. Re-shoot video with fixes applied
