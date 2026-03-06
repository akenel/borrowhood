-- ══════════════════════════════════════════════════════════════
-- EP15 "THE CRASH" -- Pre-Recording Cleanup
-- Run BEFORE every take on Hetzner:
--
--   ssh root@46.62.138.218 "docker exec postgres psql -U helix_user -d borrowhood -f -" \
--     < pre-recording-cleanup.sql
--
-- Or paste into:
--   ssh root@46.62.138.218 "docker exec -i postgres psql -U helix_user -d borrowhood"
-- ══════════════════════════════════════════════════════════════

BEGIN;

-- ── 1. Restore Sally Thompson (may be soft-deleted from EP14 testing) ──

UPDATE bh_user
   SET deleted_at      = NULL,
       account_status   = 'ACTIVE',
       telegram_chat_id = NULL,
       notify_telegram  = false
 WHERE email = 'sally@borrowhood.local';

-- Reactivate Sally's listings that got paused during account deletion
UPDATE bh_listing
   SET status = 'ACTIVE'
 WHERE item_id IN (
         SELECT id FROM bh_item
          WHERE owner_id = (SELECT id FROM bh_user WHERE email = 'sally@borrowhood.local')
       )
   AND status = 'PAUSED';

-- ── 2. Restore Marco Vitale (may be soft-deleted from EP14 testing) ──

UPDATE bh_user
   SET deleted_at      = NULL,
       account_status   = 'ACTIVE',
       telegram_chat_id = NULL,
       notify_telegram  = false
 WHERE email = 'marco@borrowhood.local';

-- Reactivate Marco's listings
UPDATE bh_listing
   SET status = 'ACTIVE'
 WHERE item_id IN (
         SELECT id FROM bh_item
          WHERE owner_id = (SELECT id FROM bh_user WHERE email = 'marco@borrowhood.local')
       )
   AND status = 'PAUSED';

-- ── 3. Ensure Pietro is active with all listings up ──

UPDATE bh_user
   SET deleted_at      = NULL,
       account_status   = 'ACTIVE'
 WHERE email = 'pietro@borrowhood.local';

UPDATE bh_listing
   SET status = 'ACTIVE'
 WHERE item_id IN (
         SELECT id FROM bh_item
          WHERE owner_id = (SELECT id FROM bh_user WHERE email = 'pietro@borrowhood.local')
       )
   AND status = 'PAUSED';

-- ── 4. Clean stale reviews from previous takes ──

DELETE FROM bh_review
 WHERE rental_id IN (
         SELECT id FROM bh_rental
          WHERE status NOT IN ('COMPLETED', 'DECLINED', 'CANCELLED')
       );

-- ── 4b. Clean stale deposits from previous takes ──

DELETE FROM bh_deposit
 WHERE rental_id IN (
         SELECT id FROM bh_rental
          WHERE status NOT IN ('COMPLETED', 'DECLINED', 'CANCELLED')
       );

-- ── 5. Clean stale disputes from previous takes ──

DELETE FROM bh_dispute
 WHERE rental_id IN (
         SELECT id FROM bh_rental
          WHERE status NOT IN ('COMPLETED', 'DECLINED', 'CANCELLED')
       );

-- ── 6. Clean stale lockbox access from previous takes ──

DELETE FROM bh_lockbox_access
 WHERE rental_id IN (
         SELECT id FROM bh_rental
          WHERE status NOT IN ('COMPLETED', 'DECLINED', 'CANCELLED')
       );

-- ── 7. Clean stale rentals from previous takes ──

DELETE FROM bh_rental
 WHERE status NOT IN ('COMPLETED', 'DECLINED', 'CANCELLED');

-- ── 7b. Clean ALL completed rentals between Sally & Pietro from previous takes ──
--    These ghosts pile up across takes and show as duplicates on the dashboard.
--    Cascade: reviews -> deposits -> disputes -> lockbox -> rentals

DELETE FROM bh_review
 WHERE rental_id IN (
         SELECT id FROM bh_rental
          WHERE renter_id IN (SELECT id FROM bh_user WHERE email IN ('sally@borrowhood.local', 'pietro@borrowhood.local'))
       );

DELETE FROM bh_deposit
 WHERE rental_id IN (
         SELECT id FROM bh_rental
          WHERE renter_id IN (SELECT id FROM bh_user WHERE email IN ('sally@borrowhood.local', 'pietro@borrowhood.local'))
       );

DELETE FROM bh_dispute
 WHERE rental_id IN (
         SELECT id FROM bh_rental
          WHERE renter_id IN (SELECT id FROM bh_user WHERE email IN ('sally@borrowhood.local', 'pietro@borrowhood.local'))
       );

DELETE FROM bh_lockbox_access
 WHERE rental_id IN (
         SELECT id FROM bh_rental
          WHERE renter_id IN (SELECT id FROM bh_user WHERE email IN ('sally@borrowhood.local', 'pietro@borrowhood.local'))
       );

DELETE FROM bh_rental
 WHERE renter_id IN (SELECT id FROM bh_user WHERE email IN ('sally@borrowhood.local', 'pietro@borrowhood.local'));

-- ── 8. Clean stale service quotes from EP14 takes ──
--    (Sally's active quote that blocks account deletion)

DELETE FROM bh_service_quote
 WHERE customer_id = (SELECT id FROM bh_user WHERE email = 'sally@borrowhood.local')
   AND status NOT IN ('COMPLETED', 'CANCELLED', 'DECLINED', 'DISPUTED');

-- ── 9. Recreate Sally's active service quote (needed for Act 2 story) ──
--    Sally requested Marco's furniture repair service -- accepted but not started.
--    This is the quote that blocks her account deletion.

-- Only insert if Sally has no active quotes (idempotent)
INSERT INTO bh_service_quote (
  id, customer_id, provider_id, listing_id,
  request_description, status, currency, quote_valid_days,
  labor_hours, labor_rate, materials_cost, total_amount,
  created_at, updated_at
)
SELECT
  gen_random_uuid(),
  (SELECT id FROM bh_user WHERE email = 'sally@borrowhood.local'),
  (SELECT id FROM bh_user WHERE email = 'marco@borrowhood.local'),
  l.id,
  'Antique oak dining table with wobbly leg and scratches. Repair and refinish.',
  'ACCEPTED', 'EUR', 7,
  4.0, 25.0, 35.0, 135.0,
  NOW() - INTERVAL '2 days',
  NOW() - INTERVAL '1 day'
FROM bh_listing l
JOIN bh_item i ON l.item_id = i.id
WHERE i.slug = 'restauro-mobili-antichi-falegname'
  AND l.listing_type = 'SERVICE'
  AND NOT EXISTS (
    SELECT 1 FROM bh_service_quote sq
     WHERE sq.customer_id = (SELECT id FROM bh_user WHERE email = 'sally@borrowhood.local')
       AND sq.status NOT IN ('COMPLETED', 'CANCELLED', 'DECLINED', 'DISPUTED')
  )
LIMIT 1;

-- ── 10. Clean audit log entries from previous takes ──

DELETE FROM bh_audit_log
 WHERE action = 'account_deleted'
   AND user_id = (SELECT id FROM bh_user WHERE email = 'sally@borrowhood.local');

COMMIT;

-- ── Verification queries ──

SELECT '--- USER STATUS ---' AS section;
SELECT email, display_name, account_status, deleted_at IS NOT NULL AS is_deleted
  FROM bh_user
 WHERE email IN ('sally@borrowhood.local', 'marco@borrowhood.local', 'pietro@borrowhood.local');

SELECT '--- ACTIVE LISTINGS ---' AS section;
SELECT u.display_name, COUNT(*) AS active_listings
  FROM bh_listing l
  JOIN bh_item i ON l.item_id = i.id
  JOIN bh_user u ON i.owner_id = u.id
 WHERE u.email IN ('sally@borrowhood.local', 'marco@borrowhood.local', 'pietro@borrowhood.local')
   AND l.status = 'ACTIVE'
 GROUP BY u.display_name;

SELECT '--- PIETRO DRONE LISTINGS ---' AS section;
SELECT i.name, l.listing_type, l.price, l.deposit, l.status
  FROM bh_listing l
  JOIN bh_item i ON l.item_id = i.id
  JOIN bh_user u ON i.owner_id = u.id
 WHERE u.email = 'pietro@borrowhood.local'
   AND i.category = 'drones'
 ORDER BY i.name, l.listing_type;

SELECT '--- SALLY ACTIVE QUOTES ---' AS section;
SELECT sq.status, sq.total_amount, sq.request_description
  FROM bh_service_quote sq
 WHERE sq.customer_id = (SELECT id FROM bh_user WHERE email = 'sally@borrowhood.local')
   AND sq.status NOT IN ('COMPLETED', 'CANCELLED', 'DECLINED', 'DISPUTED');

SELECT '--- STALE RENTALS (should be 0) ---' AS section;
SELECT COUNT(*) AS stale_rentals
  FROM bh_rental
 WHERE status NOT IN ('COMPLETED', 'DECLINED', 'CANCELLED');

SELECT '--- STALE DEPOSITS (should be 0) ---' AS section;
SELECT COUNT(*) AS stale_deposits
  FROM bh_deposit
 WHERE rental_id IN (
         SELECT id FROM bh_rental
          WHERE status NOT IN ('COMPLETED', 'DECLINED', 'CANCELLED')
       );

SELECT '--- GHOST RENTALS sally+pietro (should be 0) ---' AS section;
SELECT COUNT(*) AS ghost_rentals
  FROM bh_rental
 WHERE renter_id IN (SELECT id FROM bh_user WHERE email IN ('sally@borrowhood.local', 'pietro@borrowhood.local'));
