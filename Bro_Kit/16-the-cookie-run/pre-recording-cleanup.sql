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

-- ── 6. Seed Sally's completed order history (EUR 235+ in prior sales) ──
--    These are "past" orders from community members, showing Sally
--    has an established business before EP2 begins.

INSERT INTO bh_rental (id, listing_id, renter_id, status,
       requested_start, requested_end, actual_pickup, actual_return,
       renter_message, created_at, updated_at)
SELECT
    gen_random_uuid(),
    (SELECT l.id FROM bh_listing l
     JOIN bh_item i2 ON l.item_id = i2.id
     WHERE i2.slug = seed.item_slug AND l.listing_type::text = seed.ltype
     LIMIT 1),
    buyer.id,
    'COMPLETED',
    NOW() - (days_ago::text || ' days')::interval,
    NOW() - (days_ago::text || ' days')::interval + interval '1 day',
    NOW() - (days_ago::text || ' days')::interval,
    NOW() - (days_ago::text || ' days')::interval + interval '1 day',
    msg,
    NOW() - (days_ago::text || ' days')::interval,
    NOW() - (days_ago::text || ' days')::interval + interval '1 day'
FROM (VALUES
    -- Cookie Cutter rentals (EUR 5/day each = 25)
    ('professional-cookie-cutter-set-200-pieces', 'RENT',      'marco@borrowhood.local',    45, 'Need cutters for my daughter''s birthday party'),
    ('professional-cookie-cutter-set-200-pieces', 'RENT',      'rosa@borrowhood.local',     38, 'Baking club meeting this weekend'),
    ('professional-cookie-cutter-set-200-pieces', 'RENT',      'chiara@borrowhood.local',   30, 'Christmas cookie shapes please!'),
    ('professional-cookie-cutter-set-200-pieces', 'RENT',      'elena@borrowhood.local',    22, 'Wedding favours baking session'),
    ('professional-cookie-cutter-set-200-pieces', 'RENT',      'nino@borrowhood.local',     16, 'Kids party supplies needed'),
    -- Cookie Cutter training (EUR 15/hr each = 45)
    ('professional-cookie-cutter-set-200-pieces', 'TRAINING',  'giuseppe@borrowhood.local',  40, 'Want to learn cookie decorating'),
    ('professional-cookie-cutter-set-200-pieces', 'TRAINING',  'francesca@borrowhood.local', 28, 'Training for my cafe staff'),
    ('professional-cookie-cutter-set-200-pieces', 'TRAINING',  'maria@borrowhood.local',     12, 'Easter cookies for the family'),
    -- KitchenAid rentals (EUR 10/day each = 30)
    ('kitchenaid-stand-mixer-artisan-5qt',        'RENT',      'carmen@borrowhood.local',    35, 'Making bread all weekend'),
    ('kitchenaid-stand-mixer-artisan-5qt',        'RENT',      'paolo@borrowhood.local',     20, 'Need mixer for pasta dough'),
    ('kitchenaid-stand-mixer-artisan-5qt',        'RENT',      'roberto@borrowhood.local',   10, 'Meringue for the dinner party'),
    -- Recipe Collection sales (EUR 8 flat each = 24)
    ('sallys-secret-cookie-recipe-collection',    'SELL',      'luca@borrowhood.local',      42, 'My nonna will love these recipes'),
    ('sallys-secret-cookie-recipe-collection',    'SELL',      'matteo@borrowhood.local',    25, 'Starting a home bakery, need inspiration'),
    ('sallys-secret-cookie-recipe-collection',    'SELL',      'rosa@borrowhood.local',      15, 'Gift for my sister'),
    -- Pasta Machine rental (EUR 6/day each = 12)
    ('pasta-machine-marcato-atlas-150-ravioli-set','RENT',     'roberto@borrowhood.local',   33, 'Sunday pasta with the family'),
    ('pasta-machine-marcato-atlas-150-ravioli-set','RENT',     'george@borrowhood.local',    18, 'Ravioli night with friends'),
    -- Pasta Machine training (EUR 20/session each = 40)
    ('pasta-machine-marcato-atlas-150-ravioli-set','TRAINING', 'chiara@borrowhood.local',    36, 'Teach me ravioli!'),
    ('pasta-machine-marcato-atlas-150-ravioli-set','TRAINING', 'francesca@borrowhood.local',  8, 'Advanced ravioli class please'),
    -- Baking training (EUR 10/hr each = 30)
    ('baking-with-sally-sicilian-cookies',        'TRAINING',  'carmen@borrowhood.local',    26, 'Saturday class with my daughter'),
    ('baking-with-sally-sicilian-cookies',        'TRAINING',  'jake@borrowhood.local',      14, 'Want to learn Sicilian biscotti'),
    ('baking-with-sally-sicilian-cookies',        'TRAINING',  'giuseppe@borrowhood.local',   6, 'Anniversary cake techniques'),
    -- Scooter rentals (EUR 5/day each = 15)
    ('sallys-electric-scooter-for-delivery',      'RENT',      'matteo@borrowhood.local',    32, 'Quick errand around centro'),
    ('sallys-electric-scooter-for-delivery',      'RENT',      'luca@borrowhood.local',      19, 'Market run and back'),
    ('sallys-electric-scooter-for-delivery',      'RENT',      'paolo@borrowhood.local',      7, 'Delivery to the port'),
    -- Custom pastries commission (EUR 3.50 each = 14)
    ('custom-sicilian-pastries-events',           'COMMISSION','jake@borrowhood.local',      50, 'Need 20 cannoli for office party'),
    ('custom-sicilian-pastries-events',           'COMMISSION','george@borrowhood.local',    34, '30 pastries for dinner party'),
    ('custom-sicilian-pastries-events',           'COMMISSION','elena@borrowhood.local',     21, 'Dessert platter for book club'),
    ('custom-sicilian-pastries-events',           'COMMISSION','marco@borrowhood.local',      5, 'Treats for the neighbourhood BBQ')
) AS seed(item_slug, ltype, buyer_email, days_ago, msg)
JOIN bh_user buyer ON buyer.email = seed.buyer_email;

-- Totals (listing.price per completed rental):
--   Cookie Cutter rent:     5 x  5 =  25
--   Cookie Cutter training: 3 x 15 =  45
--   KitchenAid rent:        3 x 10 =  30
--   Recipe sell:             3 x  8 =  24
--   Pasta rent:              2 x  6 =  12
--   Pasta training:          2 x 20 =  40
--   Baking training:         3 x 10 =  30
--   Scooter rent:            3 x  5 =  15
--   Custom pastries:         4 x 3.5=  14
--   TOTAL:                         = EUR 235.00 (exact)

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

SELECT '--- SALLY COMPLETED ORDERS (earnings history) ---' AS section;
SELECT COUNT(*) AS completed_orders,
       COALESCE(SUM(l.price), 0) AS total_earnings_eur
  FROM bh_rental r
  JOIN bh_listing l ON r.listing_id = l.id
  JOIN bh_item i ON l.item_id = i.id
  JOIN bh_user u ON i.owner_id = u.id
 WHERE u.email = 'sally@borrowhood.local'
   AND r.status = 'COMPLETED';

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
