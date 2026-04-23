# Live Raffle Events -- Design Doc

**Status:** DRAFT -- brain-farted into existence April 23-24 overnight. Morning-shift review + build.
**Predecessor:** Online raffles shipped. Newcomer trust cap = EUR 10 pot. Age-14 floor. Provably-fair draw.
**Net-new idea:** turn the draw itself into a community event. Kids pay at the door to watch. Every kid leaves having seen a show.

---

## The problem with pure-online raffles

Online raffles are transactional:
1. Organizer posts it
2. Ticket holders pay remotely
3. Winner gets a notification
4. Everyone else gets nothing (not even a memory)

Community fundraising isn't supposed to feel like a lottery app. The *gathering* is the point -- the reason a neighborhood raffle at a church festival beats a slot machine is that you show up, you see the ticket pulled, you cheer, you lose, you eat a sandwich, you go home warmer. La Piazza is a town square, not a Vegas lobby.

## The idea

**Simon's "Live Raffle":**
- Posts a raffle whose prize is *performed live*: 1 hour of boxing training
- Splits the prize into **3 × 20-min sessions** -> 3 winners instead of 1
- Kids buy **raffle tickets** online in advance (EUR 0.10 x 20 tickets = EUR 10 pot, newcomer cap)
- Kids ALSO buy **watch tickets** at the door (EUR 0.30 x 30 seats = EUR 9 for the night)
- On draw day: everyone shows up at the gym. Simon pulls tickets. Three kids win, take their 20 minutes one after the other. The other seventeen watch their friends get coached. The thirty door-only kids watch the whole thing.

**Why it's better:**
- Every ticket has value, even losing ones (you get a show)
- Kids who can't afford a full raffle entry can still come watch for 30 cents
- Winning in front of your peers is a bigger prize than the training itself
- Organizer gets venue revenue + raffle revenue, split cleanly
- It's an *event* on the calendar, discoverable by people who would never browse raffles

**Why fighters in particular love it:** boxing culture is public. The gym, the weigh-in, the walkout. A kid who wins a 20-minute session in front of thirty peers has his story for a year. The four other kids who got trained too become his supporting cast.

## The whole night (what the kids actually remember)

The draw is not the event. The draw is 30 seconds in the middle of the event. The event is the night.

```
19:00  Doors open. Kids show up with gloves in hand, nervous, grinning.
       Water's free. Some lean on the ropes, some stretch, some just stare.
19:15  Simon says hi, introduces the gym, thanks the community.
19:30  The draw. Seeds announced, proof hashed, three names pulled.
       Cheering. Losers boo good-naturedly, winners shadowbox to their spot.
19:35  Winner 1: 20 minutes of focus mitts with Simon, live, on the floor.
19:55  Winner 2: 20 minutes.
20:15  Winner 3: 20 minutes.
20:35  Shop talk. Simon sits on a stool, opens it up. "Questions?" The kids
       ask about Mike Tyson, about diet, about fear. Simon answers honest.
21:00  Breakout. Small groups. Some practice what they just learned, some
       watch, some spar (gently, with chaperones). Water and cookies.
22:00  Slow goodbye. Everyone walks out together. On the way home, twenty
       kids dream about Mike Tyson, about winning next time, about hosting
       their own raffle for something they can give the community.
```

**That is the product.** The raffle is the plot device. The agenda is the thing.

Every minute of that night is already something La Piazza supports -- we just need to give organizers a place to *write it down* so attendees know what to expect, and a way to signal the small things (bring your own gloves, water is provided, no shoes on the mat) without having to fit it all into one free-text paragraph.

## Goals

1. **Live + Online variants** -- a raffle declares its format at creation. Same trust cap, same provably-fair draw, different UX.
2. **Multi-winner support** -- prize can be split into N chunks; draw picks N tickets. Works for both formats.
3. **Two separate SKUs for live events:**
   - Raffle ticket = a chance in the draw
   - Watch ticket = a seat in the room
   - Buy either, both, or several. Door ticket holders are RSVPs, not draw participants.
4. **Calendar integration** -- live raffles appear on `/calendar` with the draw date as event time.
5. **Door check-in flow** -- organizer can mark watch-ticket holders as "arrived" (phone-friendly, at the venue).

## Non-goals (v1)

- Live video streaming of the draw (way too much)
- Ticket scalping / transfer (no resale, tickets are non-transferable)
- Complex prize trees (3 different sub-prizes) -- keep it "the prize is split into N equal slices"
- Payment at the door goes through the app -- at-door cash handling stays off-platform (organizer collects, marks arrived)
- Real-time seat map / reserved seating -- first come, first seat

---

## Data model changes

### `bh_raffle` -- new columns

```
raffle_format       varchar(16) not null default 'online'
                    -- 'online' | 'live'

num_winners         smallint not null default 1
                    -- draw picks this many tickets; prize implied split into num_winners equal chunks

live_venue          varchar(200) nullable       -- human-readable, e.g. "Gym Basso, Enna"
live_address        varchar(300) nullable       -- street for directions
live_latitude       numeric nullable            -- for map pin
live_longitude      numeric nullable
live_starts_at      timestamptz nullable        -- doors open / show start
live_ends_at        timestamptz nullable        -- estimated end (for calendar sizing)
live_watch_price    numeric(10,2) nullable      -- EUR, per watch ticket
live_watch_max      integer nullable            -- door capacity (seats)
live_watch_sold     integer not null default 0
```

All `live_*` columns are `nullable` because online raffles don't use them. Check constraint: if `raffle_format = 'live'` then `live_venue`, `live_starts_at`, `live_watch_price`, `live_watch_max` must all be non-null.

### `bh_raffle_watch_ticket` -- new table

Separate SKU. A watch ticket is a seat, not a draw entry. Different table keeps the draw logic untouched.

```
id                 uuid, pk
raffle_id          uuid, fk bh_raffle(id), indexed
buyer_user_id      uuid, fk bh_user(id), nullable  -- null = walk-in cash at door
buyer_name         varchar(200)                     -- for walk-ins who aren't members
quantity           smallint not null default 1
amount_paid_eur    numeric(10,2) not null
payment_method     varchar(50)                      -- 'cash' | 'paypal' | ...
arrived_at         timestamptz nullable             -- organizer check-in
created_at, updated_at, deleted_at
```

### Event structure: `bh_raffle.agenda` (JSONB)

New column on `bh_raffle` for the live variant. Ordered list of agenda items.

```jsonc
[
  { "at": "19:00", "title": "Doors open",            "body": "Water free. Stretch, chat, get ready." },
  { "at": "19:15", "title": "Welcome",               "body": "Simon introduces the gym and the prize." },
  { "at": "19:30", "title": "Live draw",             "body": "Seed and proof published. 3 winners picked." },
  { "at": "19:35", "title": "Winner 1 -- 20 minutes" },
  { "at": "19:55", "title": "Winner 2 -- 20 minutes" },
  { "at": "20:15", "title": "Winner 3 -- 20 minutes" },
  { "at": "20:35", "title": "Shop talk",             "body": "Open Q&A with Simon. Anything goes." },
  { "at": "21:00", "title": "Breakout + sparring",   "body": "Small groups. Practice, watch, spar. Chaperoned." },
  { "at": "22:00", "title": "Close",                 "body": "Walk out together. See you next raffle." }
]
```

Free-form (`at` can be a time or a phase name like "after draw"), but renders as a pretty vertical timeline on the detail page. Blank agenda is fine -- for a 30-minute no-frills raffle, skip it.

### Event structure: `bh_raffle.bring_list` + `provided_list` (TEXT[])

Two plain string arrays, small pills on the detail page. Low-friction for organizers.

```
bring_list:     ['gloves', 'mouthguard', 'water bottle']
provided_list:  ['water', 'towels', 'cookies after']
```

Rendered as two rows of pills under the venue block: "Bring your own:" (amber) and "Provided:" (green). These are the fastest way to answer "do I need to pack anything?" -- which right now is the #1 cause of kids showing up unprepared.

### Prize split math

With `num_winners = 3` and a "1 hour of training" prize:
- The BHItem prize stays single ("1 Hour of Boxing Coaching")
- The raffle record declares split = 3
- Draw picks 3 distinct winning tickets
- Organizer redeems live as three 20-minute sessions (off-platform, honor system)

We do NOT try to encode prize-sub-units in the data model. That's organizer-side trust.

---

## Frontend

### Raffle create form

Add a radio at the top of the form, right under item picker:

```
[ ] Online raffle       -- default, what we have today
[x] Live raffle event   -- kids pay at the door to watch the draw
```

When "Live" is picked, new fields appear:

```
Venue name:         [_________________]   (required)
Venue address:      [_________________]
Draw / show date:   [__________ __:__]    (required)
Estimated end:      [__________ __:__]
Watch ticket price: [EUR _____]            (required, min 0.10)
Door capacity:      [___]                  (required, 1-200)
Number of winners:  [1|2|3|...]            (default 1, max 10)

Bring your own:     [gloves] [water bottle] [+ add]     (pill input)
Provided:           [water] [towels] [+ add]            (pill input)

Agenda (optional, makes the night readable):
[19:00] [Doors open]        [Water free. Stretch.]       [x]
[19:30] [Live draw]          [3 winners picked live.]    [x]
[+ add agenda item]
```

Tier banner stays the same (raffle-ticket pot vs cap). Door revenue NOT counted toward the cap -- footnote explains why (it's seat revenue, not draw pot).

**Agenda templates** -- one click to pre-fill common shapes so newcomers don't stare at a blank box:
- "Sports demo night" (the Simon layout above)
- "Raffle + short talk" (just doors / draw / Q&A / close)
- "Raffle + party" (doors / draw / food / music)

The organizer can then edit any row. Templates are client-side only, no backend storage.

### Raffle detail page (live variant)

Four new blocks in the card, top-to-bottom:

1. **"Live at the gym" block** -- venue name + address + map pin + doors-open time
2. **"Bring / Provided" pill rows** -- amber pills for bring, green pills for provided, two-row layout, skippable if both empty
3. **Event agenda timeline** -- vertical timeline with time on the left, title + body on the right. Mobile-friendly, tap to expand body. Collapsible if more than 6 items.
4. **Watch ticket block** -- buy a seat for EUR X, separate from the raffle entry. Count of seats remaining. Door will accept cash too.

Already-handled blocks (ticket purchase, provably-fair proof) stay unchanged.

### Calendar

Live raffles already work through the existing event-like pipeline if we mark them with a start time. Add them to `/calendar` feed with `type = 'live-raffle'` so the filter chip can toggle them.

### Item card (grid)

A "LIVE" ribbon badge on the card when `raffle_format = 'live'`, sitting next to (or replacing) the "ACTIVE" status dot. Bright red. Unmissable on `/raffles` and `/browse`.

### Check-in flow

When the live event starts, organizer opens a mobile-first **/raffles/{id}/checkin** page:

- List of sold watch tickets (name or anonymous "Walk-in #12")
- Tap row -> mark `arrived_at = NOW()` (green)
- Big "Walk-in + cash" button at top -> +1 walk-in, prompts amount, marks arrived
- Live count: "Arrived: 14 / 30 sold"

After the show, organizer clicks "Draw now". N winners announced. Provably-fair proof published same as online. Winners redeem prize on the spot.

---

## Backend

### Service changes (`src/services/raffle_engine.py`)

```python
def execute_draw(raffle, num_winners=1) -> list[BHRaffleTicket]:
    """Pick num_winners distinct tickets using provably-fair seed+pool hash.

    Rather than picking one ticket by index, we seed a deterministic PRNG
    and draw without replacement num_winners times.
    """
```

Current draw returns a single winner; expand to N with the same seed (so proof still verifies). Document the updated verification formula in `/raffle-guide` -- for N winners, the pool order and the SHA-256 stays the same, but the verification picks N indices instead of 1.

### New endpoints

```
POST /api/v1/raffles/{id}/watch-tickets
     -> buy N watch tickets (authenticated buyer or anonymous walk-in)

POST /api/v1/raffles/{id}/watch-tickets/{tid}/arrived
     -> organizer-only, marks ticket as arrived

GET  /api/v1/raffles/{id}/checkin
     -> organizer-only, returns sold watch tickets + arrival state

PATCH /api/v1/raffles/{id}
     -> include num_winners, live_* fields in allowed updates (before published)
```

### Trust gate (unchanged)

Pot cap stays based on `ticket_price x max_tickets`. Watch ticket revenue is outside the cap for the reason documented in the create form: door money buys an immediate deliverable (seat at the show).

Age-14 floor stays. Applies to organizer only; attendees/buyers can be any age (parent-chaperoned events implied).

---

## Edge cases worth writing tests for

- Live raffle with `num_winners > max_tickets` -- should reject at validation
- Live raffle whose `live_starts_at` is before the raffle's `draw_date` -- coordinate or reject
- Organizer cancels day-of -- refund all raffle tickets AND all pre-sold watch tickets
- Walk-in cash ticket created after check-in page is opened -- list auto-refreshes
- Multi-winner draw where not enough confirmed tickets exist (num_winners > confirmed tickets) -- fall back to drawing fewer winners, announce the shortfall on the proof line
- Venue capacity exceeded via walk-ins (organizer counts 32 heads, only 30 sold) -- log but don't block, organizer is on the hook for safety
- Time-zone: `live_starts_at` stored UTC, rendered in venue TZ (Europe/Rome for Simon)

---

## Migration path

All new columns are nullable or have defaults. Existing raffles get `raffle_format = 'online'` and `num_winners = 1`. No backfill needed. `bh_raffle_watch_ticket` is a brand-new table.

One UX note: the online/live radio defaults to **online** so anyone re-creating an old-style raffle doesn't accidentally get the live flow.

---

## Why this respects the trust system we just built

- Newcomer cap still binds the raffle pot (EUR 10 for Simon)
- Age-14 floor still gates organizers
- Provably-fair draw still verifiable (same SHA-256, just picks N indices)
- Watch tickets are a separate revenue stream for a separate deliverable, not a workaround

The live variant scales the *social* value without scaling the *financial risk*. A kid buying a 30-cent door ticket is paying for something they receive immediately (entertainment). There's no promise to break. The only thing under the trust cap is the stuff that could go wrong (the prize never being delivered), and that's still capped at EUR 10 until Simon earns his way up.

---

## Effort estimate

- Data model + migration + check constraint: 45 min
- Draw service multi-winner rewrite + tests: 60 min
- Watch-ticket table, model, service: 45 min
- 4 new endpoints + Pydantic schemas: 45 min
- Raffle create form (radio + conditional live fields): 60 min
- Raffle detail page (live blocks + watch ticket buy): 45 min
- Check-in page (mobile-first list): 45 min
- Calendar integration (show live raffles): 15 min
- "LIVE" card badge + style updates: 15 min
- End-to-end Simon-as-organizer walkthrough: 30 min

**Total: ~7 hours focused work.** Ship in one branch, one PR.

---

## Open questions for the morning review

1. **Cash walk-ins:** do we want them recorded (helps organizer accounting) or are they off-platform entirely? Draft assumes recorded.
2. **Refunds on cancel:** partial? full? who decides? Draft assumes full refund, organizer absorbs processing.
3. **Multi-winner draw order:** is it 1st winner first, 2nd winner second, etc, with the 1st winner getting "best" slot? Or random order? Draft assumes first-drawn-first.
4. **Watch ticket for the organizer:** does Simon need one? No -- he's the host. Edge case: co-hosts?
5. **"Everybody's a winner" consolation:** a signed token / NFT / physical stamp for every attendee, as a memory? Nice-to-have, out of scope for v1.

---

*Angel's quote from the midnight brain-fart: "for fighters they would love it and everybodies a winner baby"*
