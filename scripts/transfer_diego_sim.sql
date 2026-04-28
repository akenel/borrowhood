-- Transfer Diego's sim profile to his real Keycloak account.
--
-- Run AFTER:
--   1. seed_diego_sim.py has populated the sim user.
--   2. Diego has logged in once with his real Google account
--      (this creates a blank BHUser record with his real email + keycloak_id).
--
-- This script:
--   1. Takes a backup of both user rows + related data (safety net).
--   2. Deletes the blank "real Diego" record (no content -- just an
--      auto-created shell from his first login).
--   3. Flips the sim user's email + keycloak_id to Diego's real values,
--      so all his services / event / raffle / help posts come with him.
--   4. Re-enables email + telegram notifications.
--
-- Usage (interactive, recommended):
--   docker exec -it postgres psql -U helix_user -d borrowhood
--   \set REAL_EMAIL '''diego.real@gmail.com'''
--   \set REAL_KC_ID '''<keycloak-uuid-from-keycloak-admin>'''
--   \i /app/scripts/transfer_diego_sim.sql
--
-- Or one-shot from outside the container:
--   docker exec postgres psql -U helix_user -d borrowhood \
--     -v REAL_EMAIL="'diego.real@gmail.com'" \
--     -v REAL_KC_ID="'<keycloak-uuid>'" \
--     -f /app/scripts/transfer_diego_sim.sql
--
-- Get Diego's real keycloak_id from the bh_user row created on his first
-- login (it'll be the row with his real email and no display_name set,
-- or matching what's in the keycloak admin console for his user).

\set ON_ERROR_STOP on
\set SIM_EMAIL '''diego-sim@lapiazza.app'''


-- ── 0. Sanity check ──────────────────────────────────────────────────

\echo '── Before transfer ──'
SELECT id, email, keycloak_id, display_name, slug, badge_tier
FROM bh_user
WHERE email IN (:SIM_EMAIL, :REAL_EMAIL)
   OR keycloak_id = :REAL_KC_ID;


-- ── 1. Backup the affected rows ──────────────────────────────────────
-- One backup table, idempotent. If you re-run, drop the table first
-- (or rename the existing one with a timestamp).

CREATE TABLE IF NOT EXISTS bh_user_backup_diego AS
    SELECT * FROM bh_user
    WHERE email IN (:SIM_EMAIL, :REAL_EMAIL) OR keycloak_id = :REAL_KC_ID;

\echo 'Backup taken: bh_user_backup_diego'


-- ── 2. Run the transfer in a single transaction ──────────────────────

BEGIN;

-- 2a. Delete the blank "real Diego" shell (the row created by his first
--     login). It has the real email + real keycloak_id but no profile
--     content -- safe to remove.
DELETE FROM bh_user
WHERE email = :REAL_EMAIL
  AND email <> :SIM_EMAIL;

-- 2b. Flip the sim user over to Diego's real identity.
UPDATE bh_user
SET email          = :REAL_EMAIL,
    keycloak_id    = :REAL_KC_ID,
    notify_email   = TRUE,
    notify_telegram = TRUE,
    updated_at     = now()
WHERE email = :SIM_EMAIL;

-- 2c. Confirm exactly one row was updated. If 0 rows changed, something
--     is off (sim user missing? already transferred?) -- abort.
DO $$
DECLARE
    n int;
BEGIN
    SELECT count(*) INTO n FROM bh_user WHERE keycloak_id = :'REAL_KC_ID';
    IF n <> 1 THEN
        RAISE EXCEPTION 'Expected exactly 1 user with keycloak_id %, found %',
            :'REAL_KC_ID', n;
    END IF;
END $$;

COMMIT;


-- ── 3. Verify ───────────────────────────────────────────────────────

\echo '── After transfer ──'
SELECT id, email, keycloak_id, display_name, slug, badge_tier,
       notify_email, notify_telegram
FROM bh_user
WHERE keycloak_id = :REAL_KC_ID;

\echo '── Diego now owns this many resources ──'
SELECT
    (SELECT count(*) FROM bh_item    WHERE owner_id     = (SELECT id FROM bh_user WHERE keycloak_id = :REAL_KC_ID)) AS items,
    (SELECT count(*) FROM bh_listing WHERE item_id IN (SELECT id FROM bh_item WHERE owner_id = (SELECT id FROM bh_user WHERE keycloak_id = :REAL_KC_ID))) AS listings,
    (SELECT count(*) FROM bh_help_post WHERE author_id = (SELECT id FROM bh_user WHERE keycloak_id = :REAL_KC_ID)) AS help_posts,
    (SELECT count(*) FROM bh_raffle  WHERE organizer_id = (SELECT id FROM bh_user WHERE keycloak_id = :REAL_KC_ID)) AS raffles;


-- ── 4. ROLLBACK (if anything looks wrong) ────────────────────────────
-- Run this manually only if you need to undo the transfer:
--
--   BEGIN;
--   DELETE FROM bh_user WHERE keycloak_id = :REAL_KC_ID;
--   INSERT INTO bh_user SELECT * FROM bh_user_backup_diego;
--   COMMIT;
--
-- Then re-attempt the transfer with corrected REAL_EMAIL / REAL_KC_ID.


-- ── 5. Cleanup (run after a successful transfer + manual verification) ─
-- DROP TABLE bh_user_backup_diego;
