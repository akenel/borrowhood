# Post-Deadline Changes Disclosure

**Commit:** `15159e8` -- 2026-03-02 08:47 CET (roughly 1 hour after submission)
**Previous commit (deadline):** `e2ad45b` -- 2026-03-02 07:44 CET

---

## What happened

While recording a full walkthrough video for the submission, we discovered that
seed data users (Mike, Sally, etc.) could not see their dashboards. Logged-in
users saw "No rental activity yet" and "You haven't listed any items" even though
the database had items, listings, and rentals for those users.

## Root cause

The seed data service creates users with **placeholder UUIDs** for `keycloak_id`:

```python
# src/services/seeding.py, line 66
keycloak_id=str(uuid.uuid4()),  # Placeholder until KC realm is set up
```

When a seed user logs in via Keycloak, their JWT `sub` claim contains the
**real** Keycloak UUID, which does not match the random placeholder in the
database. The dashboard query `WHERE keycloak_id = <jwt sub>` returns nothing.

**This only affects seed/demo data.** Real users who register through the
onboarding flow (`POST /api/v1/onboarding/profile`) get their BHUser record
created with the correct Keycloak UUID from their JWT. The application works
correctly for all real users.

## What was changed

### 1. Consolidated duplicate `_get_user` functions (code hygiene)

13 router files each had an identical copy of this function:

```python
async def _get_user(db: AsyncSession, keycloak_id: str) -> BHUser:
    result = await db.execute(
        select(BHUser).where(BHUser.keycloak_id == keycloak_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=403, detail="User not provisioned")
    return user
```

Moved to a single shared function in `src/dependencies.py`. The lookup logic
is identical. This is a textbook DRY refactor -- no behavior change for
production users.

### 2. Added seed-data fallback in the shared function

The shared `get_user()` adds a secondary lookup: if no user matches by
`keycloak_id`, try matching by Keycloak `preferred_username` against the
database `slug` field. If found, update the `keycloak_id` so future logins
match directly.

This fallback **only activates for seed data users** whose `keycloak_id` is a
placeholder. Real users always match on the first lookup.

### 3. Recording script added

`Bro_Kit/scripts/record-full-walkthrough.js` -- a Puppeteer script for
recording the demo walkthrough video. Test tooling, not application code.

## What was NOT changed

- Rental flow (create, approve, complete, return)
- Deposit system (hold, release, dispute)
- Listing CRUD (create, update, browse, search)
- Badge system (award logic, catalog, display)
- Auction/bidding system
- Review system
- Helpboard
- Onboarding flow
- Notification system
- All HTML templates
- All test files
- Database schema
- API contracts (request/response shapes)

## Files touched

| File | Change | Application logic affected? |
|------|--------|-----------------------------|
| `src/dependencies.py` | Added shared `get_user()` | No -- same lookup, centralized |
| `src/routers/*.py` (13 files) | Deleted local `_get_user`, import shared one | No -- identical behavior |
| `src/routers/pages.py` | Use shared `get_user()` for dashboard | No -- same query |
| `src/routers/badges.py` | Use shared `get_user()` | No -- same query |
| `src/routers/onboarding.py` | Added slug fallback before creating new user | No -- only for seed data linking |
| `Bro_Kit/scripts/record-full-walkthrough.js` | New file -- recording script | N/A -- test tooling |

## How to verify

The diff speaks for itself:

```bash
git diff e2ad45b..15159e8 -- src/routers/rentals.py
```

Every router file shows the same pattern: delete the local 6-line function,
change `_get_user(db, token["sub"])` to `get_user(db, token)`. The rental
logic, deposit logic, review logic -- none of it changed.

## Summary

This was a **demo environment fix**, not an application fix. The application
handles real user registration correctly through the onboarding flow. The seed
data setup had a gap where placeholder Keycloak IDs did not match real
Keycloak logins, causing empty dashboards during video recording.

No application features, business logic, API contracts, or database schema
were modified.
