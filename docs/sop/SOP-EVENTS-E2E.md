# SOP: Events Feature E2E -- Lessons Learned

**Dates:** April 10-12, 2026  
**Team:** Angel (Captain, Tester) + Tig (Pilot, Developer)  
**Result:** Events system fully operational -- create, edit, RSVP, leaderboard, gamification

---

## What We Built

| Component | Status |
|-----------|--------|
| EVENT listing type (9th type) | DONE |
| 8 event categories | DONE |
| RSVP with auto-waitlist | DONE |
| No-show penalty system | DONE |
| 15 unlockable achievements | DONE |
| Leaderboard page (3 tabs) | DONE |
| Streak tracking + bonus points | DONE |
| Feedback button (every page) | DONE |
| Session timeout warning | DONE |
| Silent token refresh | DONE |
| Personalized delete warning | DONE |
| Online event link | DONE |
| Font size control (A+/A-) | DONE |
| Workshop messaging | DONE |
| Tags display on items | DONE |
| Event attributes card | DONE |

## Total Commits: 45+
## Total Tests: 639 passed, 0 failed

---

## The Apostrophe War (Critical Lesson)

### The Problem
Any item name with an apostrophe (e.g., "Marcello's Garage Sale") broke Alpine.js on the entire page. RSVP button, share button, translate button -- all dead.

### Root Cause
Jinja2 template rendering + Alpine.js expression parsing + HTML entity decoding create a triple-escape nightmare:

1. Jinja renders `{{ item.name }}` as `Marcello&#39;s` (HTML-escaped apostrophe)
2. Browser parses `&#39;` back to literal `'` in HTML attributes
3. Alpine parses the attribute value as JavaScript
4. The `'` breaks any JS string it appears inside

### Where It Hit (7 separate locations found and fixed)
1. `@click="bhShare('{{ item.name }}', ...)"` -- item_detail.html
2. `@click="doShare('{{ item.name }}', ...)"` -- browse.html
3. `@click="bhShare('{{ workshop.display_name }}', ...)"` -- workshop.html
4. `@click="bhShare('{{ profile_user.display_name }}', ...)"` -- profile.html
5. `onclick="navigator.share({title:'{{ item.name|e }}', ...})"` -- item_detail.html
6. `x-text="... '{{ t('events.waitlisted') }}' ..."` -- item_detail.html RSVP button
7. `x-text="... '{{ t('feedback.created') }}' ..."` -- base.html feedback panel

### The Fix Pattern
**NEVER put dynamic text inside Alpine expressions or onclick handlers.**

Instead:
```html
<!-- BAD: text in expression -->
<button @click="share('{{ item.name }}')">

<!-- GOOD: text in data attribute -->
<button @click="share($el.dataset.name)" data-name="{{ item.name | e }}">
```

For conditional text:
```html
<!-- BAD: t() in x-text -->
<span x-text="loading ? '{{ t('sending') }}' : '{{ t('send') }}'">

<!-- GOOD: x-show/x-if with static Jinja -->
<template x-if="loading"><span>{{ t('sending') }}</span></template>
<template x-if="!loading"><span>{{ t('send') }}</span></template>
```

### The Rule
**If the text comes from user input, database, or i18n -- it MUST go in a data attribute or static HTML, NEVER inside a JavaScript expression in an HTML attribute.**

### Test Guard
`test_april11_night_session.py::TestAlpineSafety` scans all x-text and @click attributes for t() calls. If someone adds a new one, the test catches it.

---

## The Event Edit Round-Trip Bug

### Problem
Event dates, venue, and address disappeared after saving in edit mode.

### Root Cause
TWO separate data loading paths:
1. `<script>` block set `window._editListingPrices['event']` with event data
2. Alpine's `init()` in `x-data` overwrote `listingPrices` with empty defaults

Alpine runs AFTER the script block, so the event fields always reset to empty.

### Fix
Added event field copying to the Alpine `init()` function -- the one that actually wins.

### Lesson
**If two code paths set the same data, only the last one matters. Don't set it twice.**

---

## The GDPR Delete Cascade

### Problem
DELETE /api/v1/users/me returned 500.

### Root Cause (3 layers)
1. **Missing tables:** `bh_saved_search`, `bh_item_vote` not in cleanup list
2. **Failed transactions:** PostgreSQL aborts entire transaction on any error. `try/except pass` doesn't help. Fix: `db.begin_nested()` (savepoints)
3. **Orphaned data:** Other users' replies, bids, rentals on the deleted user's posts/items still referenced them

### Fix
- Added all missing FK tables
- Used savepoints for each cleanup statement
- Added cascade cleanup: delete OTHER users' data on THIS user's posts/items before deleting the posts

### Lesson
**When you add a new model with a user FK, add it to the GDPR cleanup list. Always.**

---

## The rem vs px Font Scaling Disaster

### Problem
Font size A+/A- made the entire app unusable on mobile.

### Root Cause
Changing `html { font-size }` scales ALL Tailwind classes because Tailwind uses `rem` for everything -- padding, margins, widths, heights, gaps, not just text.

### Fix
CSS `data-text-scale` attribute on `<body>` that targets ONLY text elements:
```css
body[data-text-scale="24"] :is(p,span,a,li,h1,...) { font-size: 150% !important; }
```

### Lesson
**Never change root font-size in a Tailwind app. Target text elements specifically.**

---

## The Session Token Expiry

### Problem
User looks logged in (nav shows name) but API calls return 401. Page shows "logged in" but clicking Save/RSVP fails silently.

### Root Cause
Access token expires (60min) but the page was loaded when it was still valid. The rendered HTML shows "logged in" but the cookie is stale.

### Fix
Store refresh token in `bh_refresh` cookie. When access token fails JWT decode, the dependency uses the refresh token to silently get a new access token from Keycloak. Middleware sets the new cookies on the response.

### Lesson
**Always implement token refresh. A user should NEVER be silently logged out while actively using the app.**

---

## Team Process That Worked

1. **Angel tests on real devices (Fairphone, Firefox, Chrome)** -- finds bugs I can't find in code review
2. **Tig deploys fast** -- commit -> push -> pull -> recreate in one command chain
3. **Console errors shared immediately** -- Angel pastes the error, Tig traces it
4. **Screenshots with every bug report** -- visual context is worth 1000 words
5. **Fix -> Deploy -> Verify loop** -- never batch fixes, deploy each one and verify
6. **Tests after every session** -- 639 tests guard everything we built
7. **Memory notes after every session** -- context survives across conversations

## What We'd Do Differently

1. **Test on mobile BEFORE deploying UI changes** -- the font scaling disaster cost 2 hours
2. **Audit all Alpine expressions when adding new templates** -- the apostrophe war was 8 rounds
3. **Add new models to GDPR cleanup immediately** -- not after the 500 error
4. **Use debug tools proactively** -- the Alpine debug detector found the bug in 1 deploy after 6 rounds of guessing

---

*"If one seal fails, check all the seals."*  
*"NEVER say fixed without verifying the output."*  
*"The difference between 4-star and 5-star is not intelligence. It's consistency."*
