# La Piazza — Manual UAT Challenge

*The deal (2026-05-27): Angel runs every step. Zero findings = the app is video-ready, we ship a 3-min demo + LinkedIn post. Any bug, broken flow, or cosmetic snag = not ready, we tune first.*

> **Tigs' honest bet:** quotes + raffles got hammered this week and should hold.
> The rest (rentals, sales, events, giveaways, messages, reviews, help, i18n,
> mobile) has NOT been exercised hard recently — that's where leaks likely hide.
> Marked 🛡️ = battle-tested this week. ⚠️ = not recently watched, prime hunting ground.

**How to score:** for each step, mark ✅ pass or 🔴 fail. On any 🔴, screenshot it,
note the step number, and that's a finding. Be picky — overflow, truncation,
untranslated text, a dead link, a console error all count. Open DevTools console
(F12) and watch for red errors the whole time.

**Test accounts (all password `helix_pass`):** akenel (you/organizer), mike,
leonardo, sally, john, george, nino. Use two different logins to test both
sides of any transaction.

---

## 0. First impressions + console hygiene  ⚠️
- [ ] Open `lapiazza.app` logged out. Homepage loads, no layout break, no broken images.
- [ ] Open DevTools (F12) → Console. **Zero red errors** on load. (Yellow warnings ok.)
- [ ] Resize browser narrow (or phone). Homepage + nav still usable, nothing overflows.
- [ ] Click every top-nav + bottom-nav item. Each lands on a real page, no 404.
- [ ] Footer links (GitHub, Terms, Privacy, Legal) all resolve.

## 1. Language / i18n  ⚠️
- [ ] Switch to Italian. Homepage, Browse, a listing, your profile — **no half-translated** pages, no raw `i18n.something` keys showing, no English leaking into IT.
- [ ] Switch back to EN. Setting sticks across page loads.
- [ ] Check a raffle page + a quote page in IT (we added strings this week) — all translated.

## 2. Auth + profile  ⚠️
- [ ] Log in as `mike`. Nav shows your name + avatar (not "Log In").
- [ ] Edit profile: change tagline, add a skill, save. Reload — change persisted.
- [ ] Add a featured video URL, save. Visit your **public** profile (`/workshop/your-slug`) — video player renders.
- [ ] Log out. Nav flips to "Log In". Protected pages (dashboard) redirect to login.
- [ ] Log back in — lands somewhere sane.

## 3. Browse + search  🛡️ (just fixed pg_trgm)
- [ ] Search "cookie" — results contain cookie items, no 500.
- [ ] Search with a typo ("cooky") — fuzzy match still finds it.
- [ ] Search special chars ("a&b", "100%") — no crash, no 500.
- [ ] Filter by a category — only that category shows.
- [ ] Filter by price / free-only — respected.
- [ ] Search something nonsense ("zzzxqq") — clean empty state, not an error.

## 4. List an item (create flow)  ⚠️
- [ ] As mike, create a brand-new item with a photo. Pick a category.
- [ ] List it as **Sell** with a price. Publish. It appears in Browse + your dashboard.
- [ ] Edit it — change price, save. Reflected on the item page.
- [ ] Pause it — drops out of Browse. Re-activate — returns.
- [ ] Try to publish an item with **no photo** — should it warn/block? Note behavior.

## 5. Order-to-Cash: rent or buy something  ⚠️ (barely tested this session)
- [ ] As mike, find an active SELL or RENT item owned by someone else (e.g. george).
- [ ] Go through the buy/rent request flow end to end. Note every screen.
- [ ] Switch to the owner (george). See the incoming request in orders.
- [ ] Owner approves. Buyer pays (off-platform confirm). Owner confirms.
- [ ] Walk it to completion. Does each status transition show + notify both sides?
- [ ] After completion, leave a **review**. Does it appear on the item + the owner's profile?

## 6. Service quotes  🛡️ (hardened this week)
- [ ] As mike, request a quote on a SERVICE listing (e.g. akenel's handyman/masonry).
- [ ] As the provider, see it in Orders → Quotes. Submit a quote (price/hours/deposit).
- [ ] As mike, see the QUOTED card with Accept/Decline + the money box.
- [ ] Accept → Mark Deposit Paid → (provider) Start Work → Mark Balance Paid → Complete.
- [ ] Confirm each transition notifies the other party (check the bell).
- [ ] On a second quote, test **Decline** with a reason from the modal. Provider sees the reason.

## 7. Raffles — full lifecycle  🛡️ (hardened this week)
- [ ] As akenel, create a raffle on an item **with a photo**, set draw date + max tickets, publish.
- [ ] Confirm the facts box shows draw date / total tickets / max per person.
- [ ] As 3 different users, buy 1 ticket each. Counts move (reserved → available drops).
- [ ] Hit the per-person cap — blocked with a clear message.
- [ ] As akenel, organizer panel: Mark Paid each → counts go to "sold".
- [ ] Trigger Draw → winner shown + Seed/Proof. Run the Copy verify command in a terminal → "VERIFIED".
- [ ] Winner + losers get bell notifications.
- [ ] Mark Complete → raffle COMPLETED. Dashboard shows "Completed" (not "Expired").
- [ ] On a different raffle, test **Cancel** → tickets voided + buyers notified.
- [ ] Share a raffle to WhatsApp/Telegram (append `?v=N`) → wolf/prize image preview shows.

## 8. Events  ⚠️ (not watched this session)
- [ ] Find or create an EVENT listing. RSVP as mike. See it in your orders/RSVPs.
- [ ] As the organizer, see the attendee list. Cancel RSVP — removed.

## 9. Giveaways  ⚠️
- [ ] Find a GIVEAWAY (free) item. Claim it as mike. Owner sees the claim. Walk it through.

## 10. Messages  ⚠️
- [ ] From a listing or quote, message the other party. They receive it (bell + inbox).
- [ ] Reply from the other account. Thread shows both sides in order.
- [ ] Check for any apostrophe/special-char message breaking the thread display.

## 11. Help board  ⚠️
- [ ] Post a help request. It appears on the board. Reply from another account. Upvote it.

## 12. Notifications sweep  ⚠️
- [ ] Through all the above, the bell count is accurate.
- [ ] Each notification, when clicked, links to the right page (not a 404 or wrong item).
- [ ] Body text is informative (not just "Work started" with no context).

## 13. Dashboard  🛡️ (status pills just fixed)
- [ ] My Items: every listing shows the correct status pill (raffles show real raffle state).
- [ ] Stats (earnings, completed, active) look plausible.
- [ ] My Raffles tab lists organized + participating correctly.

## 14. Mobile / PWA  🛡️ (wolf icon + manifest just fixed)
- [ ] On Android: uninstall the old home-screen icon, reinstall from browser.
- [ ] New icon is the **wolf** (not the LP monogram).
- [ ] App opens standalone (no browser chrome), nav works, no layout breaks on the phone.
- [ ] (Fred's Play Protect warning may linger until Google re-mints — note if it's gone.)

## 15. Cosmetic + polish sweep  ⚠️ (the picky pass)
Walk the app one more time, hunting only for ugly:
- [ ] Any text overflowing its box, awkward truncation, or overlap.
- [ ] Any broken/missing image or stretched avatar.
- [ ] Any button that looks disabled but isn't (or vice versa).
- [ ] Any inconsistent spacing, color, or alignment between similar cards.
- [ ] Any raw template artifact (`{{ }}`, `i18n.x`, "None", `[object Object]`).
- [ ] Any dead/placeholder link.

---

## Scorecard

- **0 findings** → Tigs wins the bet. App is video-ready. We make the 3-min demo + LinkedIn post.
- **Any finding** → not ready. Screenshot + step number for each. We tune, then re-run the affected sections.

*Honest note from Tigs: I'm rooting for you to find things. Every bug you catch here is one a stranger doesn't catch on launch day. A clean sweep means the app is genuinely solid — and then the video is earned, not hoped for.*
