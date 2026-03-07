-- ══════════════════════════════════════════════════════════════
-- EP02 "THE COOKIE RUN" -- Pre-Recording Cleanup
-- Run BEFORE every take on Hetzner:
--
--   ssh root@46.62.138.218 "docker exec -i postgres psql -U helix_user -d borrowhood" \
--     < Bro_Kit/16-the-cookie-run/pre-recording-cleanup.sql
-- ══════════════════════════════════════════════════════════════

BEGIN;

-- ── 1. Ensure all EP2 cast members are active ──

UPDATE bh_user
   SET deleted_at      = NULL,
       account_status   = 'ACTIVE',
       telegram_chat_id = NULL,
       notify_telegram  = false
 WHERE email IN (
   'sally@borrowhood.local',
   'pietro@borrowhood.local',
   'sofiaferretti@borrowhood.local',
   'john@borrowhood.local'
 );

-- Reactivate all their listings
UPDATE bh_listing
   SET status = 'ACTIVE'
 WHERE item_id IN (
         SELECT id FROM bh_item
          WHERE owner_id IN (
            SELECT id FROM bh_user
             WHERE email IN (
               'sally@borrowhood.local',
               'pietro@borrowhood.local',
               'sofiaferretti@borrowhood.local',
               'john@borrowhood.local'
             )
          )
       )
   AND status = 'PAUSED';

-- ── 2. Clean ALL rentals involving EP2 cast (cascade order matters) ──
--    Ghosts from previous takes pile up as duplicates on dashboards.

-- Reviews first
DELETE FROM bh_review
 WHERE rental_id IN (
   SELECT id FROM bh_rental
    WHERE renter_id IN (
      SELECT id FROM bh_user
       WHERE email IN ('sally@borrowhood.local', 'pietro@borrowhood.local',
                       'sofiaferretti@borrowhood.local', 'john@borrowhood.local')
    )
    OR id IN (
      SELECT r.id FROM bh_rental r
      JOIN bh_listing l ON r.listing_id = l.id
      JOIN bh_item i ON l.item_id = i.id
      WHERE i.owner_id IN (
        SELECT id FROM bh_user
         WHERE email IN ('sally@borrowhood.local', 'pietro@borrowhood.local',
                         'sofiaferretti@borrowhood.local', 'john@borrowhood.local')
      )
    )
 );

-- Deposits
DELETE FROM bh_deposit
 WHERE rental_id IN (
   SELECT id FROM bh_rental
    WHERE renter_id IN (
      SELECT id FROM bh_user
       WHERE email IN ('sally@borrowhood.local', 'pietro@borrowhood.local',
                       'sofiaferretti@borrowhood.local', 'john@borrowhood.local')
    )
    OR id IN (
      SELECT r.id FROM bh_rental r
      JOIN bh_listing l ON r.listing_id = l.id
      JOIN bh_item i ON l.item_id = i.id
      WHERE i.owner_id IN (
        SELECT id FROM bh_user
         WHERE email IN ('sally@borrowhood.local', 'pietro@borrowhood.local',
                         'sofiaferretti@borrowhood.local', 'john@borrowhood.local')
      )
    )
 );

-- Disputes
DELETE FROM bh_dispute
 WHERE rental_id IN (
   SELECT id FROM bh_rental
    WHERE renter_id IN (
      SELECT id FROM bh_user
       WHERE email IN ('sally@borrowhood.local', 'pietro@borrowhood.local',
                       'sofiaferretti@borrowhood.local', 'john@borrowhood.local')
    )
    OR id IN (
      SELECT r.id FROM bh_rental r
      JOIN bh_listing l ON r.listing_id = l.id
      JOIN bh_item i ON l.item_id = i.id
      WHERE i.owner_id IN (
        SELECT id FROM bh_user
         WHERE email IN ('sally@borrowhood.local', 'pietro@borrowhood.local',
                         'sofiaferretti@borrowhood.local', 'john@borrowhood.local')
      )
    )
 );

-- Lockbox access
DELETE FROM bh_lockbox_access
 WHERE rental_id IN (
   SELECT id FROM bh_rental
    WHERE renter_id IN (
      SELECT id FROM bh_user
       WHERE email IN ('sally@borrowhood.local', 'pietro@borrowhood.local',
                       'sofiaferretti@borrowhood.local', 'john@borrowhood.local')
    )
    OR id IN (
      SELECT r.id FROM bh_rental r
      JOIN bh_listing l ON r.listing_id = l.id
      JOIN bh_item i ON l.item_id = i.id
      WHERE i.owner_id IN (
        SELECT id FROM bh_user
         WHERE email IN ('sally@borrowhood.local', 'pietro@borrowhood.local',
                         'sofiaferretti@borrowhood.local', 'john@borrowhood.local')
      )
    )
 );

-- Rentals (finally)
DELETE FROM bh_rental
 WHERE renter_id IN (
   SELECT id FROM bh_user
    WHERE email IN ('sally@borrowhood.local', 'pietro@borrowhood.local',
                    'sofiaferretti@borrowhood.local', 'john@borrowhood.local')
 )
 OR id IN (
   SELECT r.id FROM bh_rental r
   JOIN bh_listing l ON r.listing_id = l.id
   JOIN bh_item i ON l.item_id = i.id
   WHERE i.owner_id IN (
     SELECT id FROM bh_user
      WHERE email IN ('sally@borrowhood.local', 'pietro@borrowhood.local',
                      'sofiaferretti@borrowhood.local', 'john@borrowhood.local')
   )
 );

-- ── 3. Clean service quotes from EP1 takes ──

DELETE FROM bh_service_quote
 WHERE customer_id IN (
   SELECT id FROM bh_user
    WHERE email IN ('sally@borrowhood.local', 'pietro@borrowhood.local',
                    'sofiaferretti@borrowhood.local', 'john@borrowhood.local')
 );

-- ── 4. Clean audit log entries from previous takes ──

DELETE FROM bh_audit_log
 WHERE user_id IN (
   SELECT id FROM bh_user
    WHERE email IN ('sally@borrowhood.local', 'pietro@borrowhood.local',
                    'sofiaferretti@borrowhood.local', 'john@borrowhood.local')
 );

-- ── 5. Clean notifications from previous takes ──

DELETE FROM bh_notification
 WHERE user_id IN (
   SELECT id FROM bh_user
    WHERE email IN ('sally@borrowhood.local', 'pietro@borrowhood.local',
                    'sofiaferretti@borrowhood.local', 'john@borrowhood.local')
 );

COMMIT;

-- ══════════════════════════════════════════════════════════════
-- Verification queries
-- ══════════════════════════════════════════════════════════════

SELECT '--- EP2 CAST STATUS ---' AS section;
SELECT email, display_name, account_status, deleted_at IS NOT NULL AS is_deleted
  FROM bh_user
 WHERE email IN ('sally@borrowhood.local', 'pietro@borrowhood.local',
                 'sofiaferretti@borrowhood.local', 'john@borrowhood.local');

SELECT '--- ACTIVE LISTINGS PER CAST MEMBER ---' AS section;
SELECT u.display_name, COUNT(*) AS active_listings
  FROM bh_listing l
  JOIN bh_item i ON l.item_id = i.id
  JOIN bh_user u ON i.owner_id = u.id
 WHERE u.email IN ('sally@borrowhood.local', 'pietro@borrowhood.local',
                   'sofiaferretti@borrowhood.local', 'john@borrowhood.local')
   AND l.status = 'ACTIVE'
 GROUP BY u.display_name
 ORDER BY u.display_name;

SELECT '--- SOFIA ITEMS ---' AS section;
SELECT i.name, l.listing_type, l.price, l.status
  FROM bh_listing l
  JOIN bh_item i ON l.item_id = i.id
  JOIN bh_user u ON i.owner_id = u.id
 WHERE u.email = 'sofiaferretti@borrowhood.local'
 ORDER BY i.name;

SELECT '--- JOHNNY ITEMS ---' AS section;
SELECT i.name, l.listing_type, l.price, l.status
  FROM bh_listing l
  JOIN bh_item i ON l.item_id = i.id
  JOIN bh_user u ON i.owner_id = u.id
 WHERE u.email = 'john@borrowhood.local'
 ORDER BY i.name;

SELECT '--- STALE RENTALS (should be 0) ---' AS section;
SELECT COUNT(*) AS stale_rentals
  FROM bh_rental
 WHERE renter_id IN (
   SELECT id FROM bh_user
    WHERE email IN ('sally@borrowhood.local', 'pietro@borrowhood.local',
                    'sofiaferretti@borrowhood.local', 'john@borrowhood.local')
 );

SELECT '--- NOTIFICATIONS (should be 0) ---' AS section;
SELECT COUNT(*) AS notifications
  FROM bh_notification
 WHERE user_id IN (
   SELECT id FROM bh_user
    WHERE email IN ('sally@borrowhood.local', 'pietro@borrowhood.local',
                    'sofiaferretti@borrowhood.local', 'john@borrowhood.local')
 );
