# Availability & Booking Calendar -- Design Doc

**Status:** DRAFT -- to be implemented morning-shift April 24.
**MVP shipped April 23:** Free-text `availability_note` on each listing (see bh_listing column).

---

## The problem

Users who offer services/rentals/training get booking requests that ignore their real schedule:
- Someone requesting 3am lessons
- Weekend bookings for a host who only works weekdays
- Bookings during a vacation week

The free-text note we shipped tonight signals intent; it doesn't enforce. Time to build real rules.

## Goals

1. **Host sets weekly pattern** — "Tue-Fri 9am-6pm, Sat 10am-2pm" per listing (or per user).
2. **Host sets blackout dates** — "away April 25-30", "no lessons Dec 22-Jan 2".
3. **Booking form respects the rules** — only valid slots are selectable.
4. **Everything timezone-aware** — Simon in Rome, student in London, booked slot shows correctly in both.
5. **Public signal** — item card shows "Next available: Thu 10am" so buyers don't even need to open the booking form to know.

## Non-goals (v1)

- Syncing with Google Calendar / iCal (huge; later)
- Multi-host listings (Simon shares the dojo with Nico)
- Recurring bookings (every Wednesday for 6 weeks)
- Dynamic pricing based on demand

---

## Data model

### New: `bh_availability_rule`

One row = one weekly recurring pattern per listing.

```
id                 uuid, pk
listing_id         uuid, fk bh_listing(id), indexed
weekday            smallint (0=Mon ... 6=Sun)
start_minute       smallint (0..1439) -- minutes since midnight in host's TZ
end_minute         smallint (0..1439)
timezone           varchar(64) -- IANA TZ, e.g. "Europe/Rome"
created_at, updated_at, deleted_at
```

A listing with no rules = "by arrangement, contact host" (current behavior).
A listing with rules = those exact windows are bookable, everything else isn't.

### New: `bh_availability_blackout`

One-off exceptions.

```
id                 uuid, pk
listing_id         uuid, fk bh_listing(id), indexed
user_id            uuid, fk bh_user(id), indexed  -- (shortcut: apply to all user's listings)
start_at           timestamptz
end_at             timestamptz
reason             varchar(200) -- optional, shown to requesters
created_at, updated_at, deleted_at
```

`listing_id` XOR `user_id`: scope the blackout either to a single listing (item-specific vacation) or across everything the user offers (whole-schedule vacation).

### Added: `bh_user.timezone`

```
timezone  varchar(64), default 'Europe/Rome'
```

Used for display when the viewer doesn't have their own TZ yet. New users pick on onboarding.

---

## Frontend

### Edit-listing form

Step 2 (listing terms) gets a new "Availability" block, visible for listing types where it matters: RENT / SERVICE / TRAINING (not for SELL / GIVEAWAY / AUCTION / EVENT / RAFFLE since those have their own time mechanics).

```
[ ] Mon  [09:00] - [18:00]  [+ add slot]
[ ] Tue  [09:00] - [18:00]
[ ] Wed
[ ] Thu  [09:00] - [18:00]
[ ] Fri  [09:00] - [18:00]
[ ] Sat  [10:00] - [14:00]
[ ] Sun

Blackout dates (vacation, off days)
[ April 25 - April 30 ]  [travel]        [x remove]
[ + add blackout ]
```

A small green "copy Mon to Tue-Fri" button for common patterns.

### Booking form

When a user hits "Book this" / "Request this", the picker shows a calendar with unavailable days dimmed + unavailable hours within a day grayed out. Click a green slot -> confirm -> booking request sent.

Timezone banner: "Showing times in your timezone (Europe/Rome). Host is in Europe/Rome." Or "Host is in Europe/Rome; showing in your Europe/London."

### Item card

If the listing has rules: show "Next available: Thu 10:00" with a small calendar icon. Computed server-side so it's cacheable.

If no rules: show nothing (no change from today).

---

## Backend

### New service: `src/services/availability.py`

Pure functions, testable:

```python
def next_available_slot(rules, blackouts, now_tz) -> datetime | None:
    """Walk forward from now until we find a bookable slot."""

def is_slot_available(rules, blackouts, start, end) -> bool:
    """Given a proposed booking, is it within a rule and not in a blackout?"""

def expand_rules_to_month(rules, blackouts, year, month, tz) -> list[Slot]:
    """For the booking picker UI -- return array of bookable slots."""
```

Timezone is the dangerous part. Every datetime stored as UTC; rules stored with host's IANA TZ; rendered in viewer's TZ. The function signatures above make the TZ explicit every time.

### New endpoints

```
GET  /api/v1/listings/{id}/availability
     -> { rules: [...], blackouts: [...], next_slot: "...", host_tz: "..." }

PUT  /api/v1/listings/{id}/availability
     -> upsert rules + blackouts atomically

POST /api/v1/listings/{id}/blackouts
     -> add a single blackout (for vacation-mode "press to block next week")
```

### Booking-side enforcement

`POST /api/v1/rentals` (or wherever booking creation lives): before creating, call `is_slot_available`. If false, return 409 with `{"detail": "Host is not available at that time", "next_slot": "..."}`.

---

## Edge cases worth writing tests for

- Cross-midnight rule (host works 22:00-02:00)
- DST boundary (clock skips/repeats an hour)
- Blackout that straddles a rule (partial block)
- Listing with rules but all days disabled -> should be treated as "no availability"
- Viewer in same TZ vs different TZ -> slot label differs but underlying UTC same
- Rule in UTC while host TZ is different (data migration caution)

---

## Migration path from MVP (free text)

The `availability_note` text field stays alive as a secondary signal even after rules exist. Host can still add a note like "flexible for regulars" or "ask in Italian if possible."

When we ship rules:
- Migrate: no data migration needed (new tables start empty)
- Users with a note see both (note + rule picker below)
- If user sets any rules, UI subtly de-emphasizes the note (still visible but smaller)

---

## Effort estimate (tomorrow morning shift)

- Data model + migration: 30 min
- Service functions + tests: 90 min
- API endpoints: 30 min
- Edit form UI: 60 min
- Booking form UI (respect rules): 60 min
- Item card "next available": 30 min
- End-to-end test as Simon: 30 min

**Total: ~5 hours focused work.** Ship in one clean commit.

---

## Why we shipped the free-text note instead of nothing

Even a textbox saying "Mon-Fri 18:00-21:00, no weekends" is:
1. Zero-risk — no enforcement logic to bug out
2. Immediate relief — prevents the 3am boundary case by social convention
3. Data collection — once users write their hours in free text, we can parse some of them as examples when building the real picker ("oh, lots of people write 'M-F 18-21' — that's our default preset")

The note is the shovel; the rule engine is the bulldozer. Shovel tonight, bulldozer tomorrow.
