# EP2 "The Cookie Run" -- QA Take Log

Tracks bugs found per take, fixes applied, and deployment status.

---

## Take 1 (2026-03-07)

**Issues found:**
1. Broken Unsplash URL for "Baking with Sofia" (`photo-1486427944344` returned 404)
2. Wrong item slug in script: `sofias-birthday-cookie-box-custom-order` (actual: `sofias-birthday-cookie-box`)
3. Sofia owned cookie cutters -- story says she RENTS them from Sally
4. Broken local image paths on server (`/media/borrowhood/items/...` files missing)

**Fixes applied:**
- Replaced broken Unsplash URL with `photo-1556217477-d325251ece38`
- Fixed cookie box slug in recording script (lines 571, 614)
- Removed Sofia's cookie cutter item from seed.json (she rents Sally's)
- SQL UPDATE server items to valid Unsplash URLs

---

## Take 2 (2026-03-07)

**Issues found:**
1. Wrong item slug `sofias-birthday-cookie-box-custom-order` still in script (missed second reference)
2. Dashboard shows "My Dashboard" with no user identity
3. "Baking with Sofia" item owned by Sofia -- should be Sally's training (she teaches)

**Fixes applied:**
- Fixed all slug references in script
- Added username display to dashboard: `My Dashboard > Sally Thompson`
- Moved "Baking with Sofia" to Sally's ownership, renamed "Baking with Sally", new slug `baking-with-sally-sicilian-cookies`

---

## Take 3 (2026-03-07)

**Issues found:**
1. Button says "Rent This Item" for SELL-type items (Birthday Cookie Box is for sale)
2. Button says "Rent This Item" for SERVICE/TRAINING types
3. Overlay background semi-transparent (previous page bleeds through)
4. Sofia shows "3 items" in script narration (she has 1 after cutter removal)
5. Script tries `Buy This` button click but template says `Rent This Item`
6. No logged-in indicator when visiting other people's workshops

**Fixes applied:**
- Listing-type-aware button text: Buy/Book/Claim/Rent based on `listing_type_val`
- Added i18n keys: `buy_this`, `book_this`, `claim_this`, `login_to_buy`, `login_to_book`, `login_to_claim` (en + it)
- Overlay background fully opaque: `rgba(30,41,59,1.0)`
- Updated Sofia item count narration to "1 item"
- Script button click updated to try "Buy This" then "Rent This"

---

## Take 4 (2026-03-07)

**Issues found:**
1. Screen flashes at ~0:44, ~0:54, ~1:37, ~2:26 -- browser shows previous page content during login transitions
2. Trust score shows 6000%/9500% on workshop pages -- not capped
3. Rental modal says "Rental Request" for SELL items, shows date pickers for purchases
4. No logged-in user indicator on workshop pages

**Fixes applied:**
- `visibleLogin()` now navigates to `about:blank` + 300ms pause before demo-login (fixes all 9 transitions)
- Trust score capped: `{{ [workshop.trust_score * 100, 100] | min | int }}%` in `workshop.html`
- Modal title/button/date-pickers now listing-type-aware via Alpine `listingType` variable
  - "Purchase Request" for sell, "Booking Request" for service/training, "Rental Request" for rent
  - Date pickers hidden for sell and offer types
  - New i18n keys: `purchase.request_title`, `purchase.submit`, `booking.request_title`, `booking.submit` (en + it)
- Added "Viewing as: [username]" badge in workshop breadcrumb for logged-in users

---

## Take 5 (2026-03-07)

**Recording:** Clean run, no script errors. All 39 scenes completed.

**Issues found (voice feedback):**
1. Dashboard lumps everything under "My Rentals" -- purchases, services, skills, sales all look the same
2. No listing type distinction on dashboard cards -- can't tell a rental from a purchase from a service
3. Need to distinguish service provider vs client/customer roles
4. Request modal should adapt more per type (auction=bid, sale=fixed price, service=hourly/flat, rental=dates)

**Fixes applied:**
- Added listing type badges (Purchase/Service/Training/Giveaway/Auction/Offer/Rental) to:
  - My Items tab cards (color-coded pill next to status)
  - My Orders tab cards (replaces generic "As Renter" label)
  - Incoming Requests tab cards (replaces generic "As Owner" label)
- Renamed "My Rentals" tab to "My Orders" (en: "My Orders", it: "I Miei Ordini")
- Trust score template: removed erroneous `* 100` multiplication (scores already 0-100 integers)
- Color thresholds fixed: 0.7 -> 70, 0.4 -> 40

**Backlog (larger items for future episodes):**
- Full tab split: separate tabs for Rentals, Purchases, Services, Auctions
- Type-specific request forms: auction=bid+dates, sale=fixed price, service=hourly/flat/negotiable
- Provider vs customer role distinction in UI
- Skills section in dashboard

---

## Between Takes 5 and 6 (2026-03-07)

**Image audit -- all EP2 cast items:**
- Found 52 broken `/media/borrowhood/items/` image paths across 16 EP2 cast items
- These local file paths don't exist on the Hetzner server
- Root cause: old seeding wrote `/media/` paths, `seed_new_items()` doesn't update existing records

**Fixes applied:**
- Replaced all 52 broken images with valid Unsplash URLs via SQL
- Added multiple images per item to show different use cases:
  - Pressure Washer: 4 images (product, patio, car, concrete)
  - Industrial Carpet Cleaner: 3 images
  - Bissell Carpet Cleaner: 3 images
  - Deep Cleaning Service: 3 images
  - Pressure Washing Service: 3 images
- Updated seed.json with matching multi-image arrays (permanent fix)
- Created `ep2-fix-broken-images.sql` for repeatable deployment
- Added `tests/test_seed_data.py` with 12 tests:
  - EP2 cast items must have images (hard fail)
  - No blank URLs, no broken `/media/` paths, valid URL format
  - All media must have alt_text
  - Users have slugs and display names
  - Items have slugs, owners, listings
  - Item owners exist as users
- Test suite: 137 passed, 35 failed (ConnectionRefused = need DB, expected), 1 skipped (advisory)

---

## Commits

| Hash | Description |
|------|-------------|
| `6fe2c0b` | feat: EP2 pre-recording cleanup SQL |
| `fa871c9` | feat: EP2 "The Cookie Run" pre-production -- script, youtube kit, thumbnail |
| `a2fdc66` | fix: EP2 Take 1-4 QA fixes -- listing-type UX, flash prevention, trust cap |
| `01482cc` | fix: trust score display -- scores are 0-100 integers, not 0.0-1.0 floats |
| `644aaa9` | fix: EP2 Take 5 QA -- listing type badges on dashboard, trust score math |

---

## Take 6 (2026-03-07)

**Note:** Skipped -- was actually a buggy run using the old script before Take 7 fixes were deployed.

---

## Take 7 (2026-03-07)

**Recording:** Two runs. First run had stale data from Take 6. Second run clean after pre-recording cleanup.

**Issues found:**
1. Notification bell says "wants to rent your Birthday Cookie Box" -- should say "wants to buy" (SELL item)
2. Notification titles use generic "Rental" language for all listing types (purchases, bookings, claims)
3. Message placeholder in modal still says "rental" for SELL items
4. Residual rentals from previous takes visible in dashboard (stale data, not a code bug)

**Fixes applied:**
- `notify_rental_event()` now accepts `listing_type` parameter and generates type-aware titles:
  - SELL: "wants to buy", "Purchase of..."
  - SERVICE/TRAINING: "wants to book", "Booking of..."
  - GIVEAWAY/OFFER: "wants to claim", "Claim of..."
  - RENT (default): "wants to rent", "Rental of..."
- Both call sites in `rentals.py` (create_rental, update_rental_status) pass `listing_type`
- Modal textarea placeholder adapts per listing type (sell/service/training/rent)
- Added i18n keys: `purchase.message_placeholder`, `booking.message_placeholder` (en + it)
- Updated `dashboard.no_rentals` to "No orders yet." / "Nessun ordine ancora."

---

## Take 8 (2026-03-07)

**Recording:** Clean run. All 39 scenes completed. No script errors.

**Issues found:**
1. Duplicate incoming request on Sofia's dashboard (7:58) -- two identical cookie box purchase requests from Pietro. Root cause: script clicked submit button (fires Alpine submitRental), then 500ms later called submitRental() again as "safety net". Race condition: first request completed before guard checked `submitting` flag.

**Fixes applied:**
- Removed duplicate submitRental() safety net call from recording script (lines 694-706)
- Button click alone is sufficient -- Alpine handles the form submission

**Backlog (from voice feedback):**
- Tab notification badges: show count on "Incoming Requests (2)", "Favorites (1)" etc.
- Favorites as notifications: when someone favorites a workshop, owner should see it
- Card transitions: 0.5s fade-in/fade-out on story cards instead of instant cut

---

## Take 9 (2026-03-07)

**Recording:** Cleanest take yet. All 39 scenes, no script errors, no duplicate requests. Starts 1:04, ends 11:18 raw.

**Issues found (voice feedback):**
1. Minor login flash at ~1:46-1:49 (known, about:blank helps but doesn't eliminate 100%)
2. Storyline gap: Sofia shows up at Sally's kitchen but we never see her book the class -- needs a scene
3. "friend" should be "friends" (plural) on the 5 Boxes card

**Script changes needed for Take 10:**
- Add scene: Sofia books Sally's baking training (fills the gap, no flashbacks)
- Leonardo da Vinci cameo setup: Leo claims Johnny's free bike, pays EUR 5-10 for delivery, Johnny delivers using lockbox code. Seeds EP3 intro + drop-off lockbox use case.
- Fix "friend" -> "friends" on 5 Boxes card
- The 5 cookie buyers need to be real cast members (Johnny, Leo, etc.) or acknowledged off-screen

**Backlog (from PbP feedback):**
- Dashboard "My Items" activity summary (recent activity, score changes, favorites, recommendations)
- Tab notification badges (from Take 8 backlog)
- Favorites as notifications (from Take 8 backlog)
- Card fade transitions 0.5s (from Take 8 backlog)

---

## Take 10 (2026-03-07)

**Recording:** Scene 9c (Sofia books Sally's class) failed -- WARN: "Book This" not found.
Root cause: route was `/item/slug` but correct route is `/items/slug`. Rest of episode ran clean.

**Issues found:**
1. Scene 9c route wrong: `/item/` should be `/items/` (404, button never rendered)
2. Workshop avatars show letter initials instead of faces -- viewers can't follow who's who
3. Workshop banners are generic purple gradients -- no visual identity per character
4. Cast members have no real street addresses or precise GPS (all generic 38.018, 12.537)
5. Story: the 5 friends / 5 addresses need to map to real cast members
6. Story: Sally's scooter purchase should be prepped for EP3

**Fixes applied:**
- Route fix: `/item/` -> `/items/` for baking training page
- Avatars: Unsplash portrait photos for all 14 demo cast (seed.json + SQL deployed)
- Banners: Unsplash landscape photos matching each workshop type
- Real Trapani addresses + precise GPS coords for all 14 cast
- Sally's Electric Scooter added as PAUSED RENT listing (EP3 ready)
- Card overlay transitions: 0.5s fade-in and fade-out on all story cards
- 5 delivery addresses mapped to cast: Pietro (Via Roma), Sally (Via Garibaldi), Leonardo (Via Torrearsa), Nino (Piazza Mercato), Maria (Via Fardella)

---

## Take 11 (2026-03-07)

**Recording:** All scenes completed. Banners, avatars, GPS deployed. Card fades working.

**Issues found (voice feedback #1):**
1. My Items tab has no activity summary per item (no "5 sold", "3 completed" counts)
2. Sally's avatar shows young woman -- should be older lady (cookie queen, 20 years baking)
3. "Listed by" section on item detail shows initial letter, not avatar photo
4. Tab notification badges still missing on dashboard tabs
5. Cookie buyers need to be nailed down to cast members (already mapped in Take 10)

**Issues found (voice feedback #2 -- STORY REVISION):**
6. Sofia doesn't buy anything herself -- Pietro buys both gifts as birthday present:
   - Gift 1: Rents Sally's cookie cutters for Sofia (weekend)
   - Gift 2: Books Sally's baking class for Sofia (Saturday)
   - Sofia goes to Sally's with the cutters, takes the lesson
7. Script needs to show Pietro buying two things from Sally, not Sofia booking

**Issues found (card review):**
8. Sofia character card says "She got 200 cookie cutters for her birthday" -- WRONG, Pietro rented them
9. "5 BOXES" card says "Two neighbors. A teacher. Her best friend." -- doesn't match mapped cast
10. "THE DEAL" card says "Aerial Photography & Video" but Sofia is using it for delivery
11. "EPILOGUE" card says "Sally has the money to fix it" -- ambiguous (scooter, not bike repair)

**Fixes applied:**
- Story revision: Scene 6 now has Pietro (not Sally) renting cookie cutters + booking baking class
- Scene 9c removed (Sofia booking class) -- Pietro already did it in Scene 6e
- Scene 7 overlay: "THE BIRTHDAY GIFT" replaces "THE MENTORSHIP" (shows both gifts)
- Scene 7b added: Sally sees Pietro's incoming requests
- Sofia character card: "Uncle Pietro rented Sally's cookie cutters for her birthday"
- "5 BOXES" card: names match cast (Pietro, Sally, Leonardo, Nino, Maria)
- "THE DEAL" card: "Aerial Photography & Delivery" + "Sofia books Pietro's drone for cookie delivery"
- "EPILOGUE" card: "Sally has the money for a scooter" (not "fix it")
- "HER FIRST LISTING" card: "Uncle Pietro gave her the tools"
- "THE FIRST BAKE" card: "Uncle Pietro rented them. He also booked the class."
- Sally avatar: changed to older woman (photo-1544005313) in seed.json + SQL
- "Listed by" on item detail: shows avatar_url image if available, falls back to initial
- Dashboard tab badges: count pills on My Items, My Orders, Incoming Requests tabs

**Backlog:**
- My Items activity summary per item (sold count, rental count, etc.)
- Favorites as notifications

---

## Take 12 (2026-03-08)

**Raw:** `raw-takes/Take 12 - s1 ep2 - THE COOKIE RUN OBS_2026-03-08 02-09-50.mp4`
**Duration:** 1:00 to 11:26 (10m26s)

**Issues found:**
1. Scene 6d: "Rent This" button not found -- cookie cutter has TRAINING listing first, shows "Book This Service"
2. Scooter images dead (both Unsplash URLs return 404) -- no image on scooter page at 9:59
3. Cookie box says "Custom Order" -- should say weight/count
4. Baking training says "2 hours" -- should be full day course (8am-6pm)
5. Scooter pricing unclear -- needs half-day/full-day model (EUR 5/4hrs, EUR 10/day)
6. Pietro's rental message doesn't specify pickup date/time

**Fixes applied:**
1. Script: added `|| clickWithRing('Book This')` fallback + `'Book'` in submit button search
2. Scooter: replaced 2 dead Unsplash URLs with 4 working ones in seed.json + Hetzner DB
3. Cookie box: renamed to "750g, ~75 cookies, various sizes and shapes" in seed.json + DB
4. Baking training: updated to "Full day course: 8am to 6pm. Next class: Saturday March 7, 2026" in seed.json + DB
5. Scooter: updated description with "EUR 5 per half-day (4 hours), EUR 10 full day" in seed.json + DB
6. Script: Pietro's message now says "Pickup Friday March 6 at 6pm please"
7. Cookie cutter listing order: RENT before TRAINING (swapped created_at in DB)
8. Script: hardcoded dates to 2026-03-06 / 2026-03-07 (real dates)

**Status:** All fixes deployed. Ready for Take 13.

---
