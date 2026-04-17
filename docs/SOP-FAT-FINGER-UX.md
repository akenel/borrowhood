# SOP: Fat-Finger UX — Mobile Rules for La Piazza

*"If Grandma can't find it and Lego-kid mis-taps it, the design failed."*

---

## The Core Truth

Every human on mobile has fat fingers. The 25-year-old with small hands is the exception, not the rule. Most apps — including Google's — pretend otherwise and ship tiny targets, tight spacing, and hover-dependent menus that don't work on touch.

La Piazza's audience is wider than most: Trapani grandmothers, Canadian tourists, Sicilian shopkeepers, Lego kids raffling off their old sets. **If any one of them hesitates for 2 seconds, we failed.**

---

## The Inventory (before we cut)

### Main Pages (26 HTML templates)

| Category | Pages |
|---|---|
| **Public landing** | home, browse, raffles, calendar, leaderboard, members |
| **Content detail** | item_detail, raffle_detail, workshop, profile |
| **User actions** | list_item, raffle_create, messages, orders, dashboard |
| **Communication** | chat, helpboard |
| **Raffle flow** | raffles, raffle_detail, raffle_create, raffle_guide |
| **Utility** | delivery_tracking, invoice_print, demo_login, legal, terms |
| **Admin/dev** | backlog, testing, onboarding |

### Dashboard Tabs (13 tabs hidden inside /dashboard)

items · renting · requests · history · favorites · analytics · day_summary · invoices · mentorships · saved_searches · disputes · settings · **raffles**

**That's 26 top-level pages + 13 dashboard tabs = 39 "screens" a user can land on.**

### Nav Bar (current state — desktop)

Logo · Browse · Concierge · Help Board · Calendar · Leaderboard · Raffles · Members · Dashboard · **+ List Your Stuff**

Plus right side: Language · Bell · Messages · Orders · Avatar · Logout = **15 clickable items** on the top bar alone.

---

## The Rules (in order of importance)

### Rule 1: 60px or Bigger for Primary Actions
"Buy Tickets", "List Your Stuff", "Publish Raffle", "Reserve", "Draw Winner" — any button where a mis-tap costs the user money, time, or face — must be **min 60px tall**. Secondary actions can be 48px. Tertiary (icon-only, like share buttons) can be 44px but surrounded by 8px of empty space.

### Rule 2: 8px of Air Around Tappable Things
Two buttons touching each other is a mis-tap factory. Every interactive element needs 8px of breathing room from its neighbors. Lists of items: minimum 12px padding per row.

### Rule 3: One Primary Action Per Screen
Grandma hesitation test: show the screen for 2 seconds, hide it, ask "What should you tap?" If she can't answer immediately, there are too many equal-weight buttons. Only ONE button on any screen should be solid-colored and large. Everything else is secondary (outlined, smaller, lighter).

### Rule 4: 16px Body Text Minimum, 18px on Mobile
"Small print" is how old people stop using your app. Anything below 16px is unreadable for anyone over 45. Gray-on-gray compounds it. Use near-black (#111, #1f2937) on white for body text.

### Rule 5: Bottom Tab Bar for Mobile's Core Actions
Thumbs live at the bottom of the screen. Put the 4-5 most-used actions there, always visible, always thumb-reachable. The top of the screen is "navigation" (logo, page title). The bottom is "action" (browse, search, main verbs).

**La Piazza's bottom bar should be:**
```
[ Home ] [ Browse ] [ Raffles ] [ Messages ] [ Profile ]
```

Not 15 items crammed into a hamburger.

### Rule 6: Kill the Hamburger for Primary Nav
Hamburger menus hide features. Users don't find them. Data shows 80% of users never open a hamburger menu on a first visit. Primary navigation stays visible. Secondary stuff can live behind a menu.

### Rule 7: No Hover-Dependent UX
Touch doesn't have hover. Every "reveal on hover" is invisible to 80% of users. Dropdowns must work on click. Tooltips must have an explicit tap-to-reveal.

### Rule 8: Undo Instead of Confirm
Modal "Are you sure?" is fat-finger hell. Two dangerous taps instead of one. The better pattern: do the action, show an "Undo" toast for 5 seconds.
- Gmail deletes emails instantly + shows "Undo"
- La Piazza should do the same for: cancel ticket, cancel raffle, archive message, remove item.

### Rule 9: Forms Over 3 Fields Become Wizards
A 10-field form on mobile looks like a wall. Break into steps. One question per screen, big buttons to move next. "Create Raffle" currently has 8 fields — should be a 4-step wizard (prize → price → draw rules → payment).

### Rule 10: Test at 360px Wide in Portrait
If it works on an iPhone SE or cheap Android in portrait, it works everywhere. Most devs test at 1920×1080 and wonder why users are confused. Chrome DevTools → toggle device toolbar → set to 360×640 → does every screen still work?

---

## The Plan (measure twice, cut once)

### Phase A: Desktop Nav Audit (30 min)
- [ ] Take screenshots of current nav at: 360px, 768px, 1024px, 1280px, 1920px
- [ ] Note overflow, crushed items, invisible items
- [ ] List every item by "how often is it used?" (Browse: every visit. Mentorships: once a month.)

### Phase B: Design the New Top Nav (30 min)
- [ ] Top bar shrinks to: **Logo + hamburger** on anything under 1280px
- [ ] Desktop (1280px+): Logo, Browse, Concierge, Raffles, Calendar, + List Your Stuff (right side). **Only 5 items.** More goes in a "More ▾" dropdown.
- [ ] Right-side utility icons (bell, messages, avatar) stay visible on desktop but collapse into mobile menu on smaller screens

### Phase C: Build the Bottom Tab Bar (1 hour)
- [ ] New component: `bottom_nav.html` included in `base.html` (mobile only, `lg:hidden`)
- [ ] 5 icons: Home · Browse · Raffles · Messages · Profile
- [ ] Each icon 56px min, active state = amber fill + label
- [ ] Sticky bottom: `fixed bottom-0 left-0 right-0 bg-white border-t`
- [ ] Safe area insets for iOS notch phones

### Phase D: CTA Audit (1 hour)
- [ ] Walk through every major page
- [ ] Every primary button → measure. If under 56px → bump to 60px
- [ ] Every secondary button → verify 48px min
- [ ] Every icon button → verify 44px tap area (can have smaller visual icon with padding)

### Phase E: Hamburger Cleanup (30 min)
- [ ] Current mobile menu has ~20 items stacked
- [ ] Group into sections: "Explore" / "My Account" / "Settings"
- [ ] Only show "Explore" by default — "My Account" and "Settings" collapse until tapped

### Phase F: Test (1 hour)
- [ ] DevTools 360×640 portrait
- [ ] Real phone test (Angel's + friend's)
- [ ] Grandma test (if you can rope someone in)
- [ ] Lego-kid test (a 6-year-old trying to buy a raffle ticket)

### Phase G: Iterate (ongoing)
- [ ] Screenshot any confusion
- [ ] Fix in under 15 min
- [ ] Ship

**Total estimated effort: 4-5 hours of focused work.**

---

## Design Tokens (materials)

Before we cut anything, define the primitives:

```css
/* Touch targets */
--tap-primary: 60px    /* Buy tickets, main CTAs */
--tap-secondary: 48px  /* Filter pills, tab buttons */
--tap-icon: 44px       /* Share, heart, close */
--tap-gap: 8px         /* Min space between tappables */

/* Typography */
--text-body: 16px      /* Default body */
--text-body-mobile: 18px  /* Mobile body */
--text-heading: 24px+  /* Page titles */
--text-small: 14px     /* Captions, metadata */
/* never go below 14px, ever */

/* Colors */
--text-primary: #111827   /* near-black, not gray */
--text-secondary: #4b5563 /* gray-600 minimum, not gray-400 */
--border-subtle: #e5e7eb  /* gray-200 for dividers */

/* Breakpoints */
--mobile: 360px         /* design minimum */
--tablet: 768px         /* md: in tailwind */
--desktop: 1024px       /* lg: in tailwind */
--wide: 1280px          /* xl: in tailwind — real desktop */
```

---

## The Grandma Test Checklist

Before shipping any mobile change, ask:

- [ ] Can Grandma's thumb hit every important button without zooming?
- [ ] Can she read every label without squinting?
- [ ] Is there exactly ONE obvious next action on every screen?
- [ ] If she mis-taps, can she undo without panic?
- [ ] Does the thing she wants to do live in the bottom half of the screen?
- [ ] If she hands the phone to Lego-kid, can he complete the task?

If any answer is "no" — don't ship. Redesign.

---

## The Fat-Finger Commandments (laminated, taped to the wall)

1. **60px or bigger for anything that matters.**
2. **8px of air between tappables.**
3. **One primary action per screen.**
4. **16px body text minimum.**
5. **Bottom tab bar on mobile.**
6. **Kill the hamburger for primary nav.**
7. **No hover-dependent UX.**
8. **Undo instead of "Are you sure?"**
9. **Wizards for long forms.**
10. **Test at 360px portrait.**

---

*"Every human has fat fingers. The question is whether your app knows that."*

*Tiger + Wolf, La Piazza, Trapani*
