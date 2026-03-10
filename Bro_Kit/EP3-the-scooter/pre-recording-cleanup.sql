-- EP3 "The Scooter" -- Pre-Recording Cleanup
-- Run this BEFORE each take to reset state
-- Usage: docker exec -i postgres psql -U helix_user -d borrowhood < /tmp/pre-recording-cleanup.sql

-- ============================================================
-- 1. CLEAN STALE RENTALS (from previous takes)
-- ============================================================
DELETE FROM bh_dispute WHERE rental_id IN
  (SELECT id FROM bh_rental WHERE status NOT IN ('COMPLETED','DECLINED','CANCELLED'));
DELETE FROM bh_lockbox_access WHERE rental_id IN
  (SELECT id FROM bh_rental WHERE status NOT IN ('COMPLETED','DECLINED','CANCELLED'));
DELETE FROM bh_rental WHERE status NOT IN ('COMPLETED','DECLINED','CANCELLED');

-- Also clean any PENDING rentals from take setup (Sofia's 12 cookie orders, etc.)
-- Keep COMPLETED ones (Mike's 12 seeded earnings)
DELETE FROM bh_rental WHERE status = 'PENDING'
  AND created_at > NOW() - INTERVAL '2 days';

-- Clean CANCELLED welding rentals from previous takes (clutters Mike's dashboard)
DELETE FROM bh_rental WHERE status = 'CANCELLED'
  AND listing_id IN (
    SELECT l.id FROM bh_listing l JOIN bh_item i ON l.item_id = i.id
    WHERE i.slug = 'welding-machine-mig-200a'
  );

-- ============================================================
-- 2. PAUSE SALLY'S SCOOTER LISTING (needs to be activated during recording)
-- ============================================================
UPDATE bh_listing SET status = 'PAUSED'
WHERE id IN (
  SELECT l.id FROM bh_listing l
  JOIN bh_item i ON l.item_id = i.id
  WHERE i.slug = 'sallys-electric-scooter-for-delivery'
  AND l.listing_type = 'RENT'
);

-- ============================================================
-- 3. PAUSE MIKE'S RENT LISTING (keep only TRAINING for course booking)
-- ============================================================
UPDATE bh_listing SET status = 'PAUSED'
WHERE id IN (
  SELECT l.id FROM bh_listing l
  JOIN bh_item i ON l.item_id = i.id
  WHERE i.slug = 'welding-machine-mig-200a'
  AND l.listing_type = 'RENT'
);

-- ============================================================
-- 4. ENSURE JOHNNY'S BIKE IS ACTIVE GIVEAWAY
-- ============================================================
UPDATE bh_listing SET status = 'ACTIVE', listing_type = 'GIVEAWAY'
WHERE id IN (
  SELECT l.id FROM bh_listing l
  JOIN bh_item i ON l.item_id = i.id
  WHERE i.slug = 'johnnys-delivery-bike-broken'
);

-- ============================================================
-- 4. FIX SALLY'S DISPLAY NAME (must be Thompson, not Baker)
-- NOTE: Sally's name in Keycloak was fixed manually via KC admin API.
--       This fixes the BorrowHood DB side. KC fix is persistent.
-- ============================================================
UPDATE bh_user SET display_name = 'Sally Thompson'
WHERE slug = 'sallys-kitchen' AND display_name != 'Sally Thompson';

-- ============================================================
-- 5. FIX PRESSURE WASHER BLANK IMAGE
-- Replace any broken Unsplash URLs for Johnny's pressure washer items
-- ============================================================
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=800&h=600&fit=crop&q=80'
WHERE url = 'https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=800&h=600&fit=crop&q=80'
AND item_id IN (SELECT id FROM bh_item WHERE slug LIKE 'pressure-wash%');

-- Also fix the Karcher product photo if broken
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=800&h=600&fit=crop&q=80'
WHERE url = 'https://images.unsplash.com/photo-1621274403997-37aace184f49?w=800&h=600&fit=crop&q=80'
AND item_id IN (SELECT id FROM bh_item WHERE slug LIKE 'pressure-wash%')
AND NOT EXISTS (
  SELECT 1 FROM bh_item_media m2
  WHERE m2.url = 'https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=800&h=600&fit=crop&q=80'
  AND m2.item_id = bh_item_media.item_id
);

-- ============================================================
-- 6. SEED SOFIA'S 12 COOKIE ORDERS (PENDING, for dashboard scene)
-- ============================================================
-- First, clean old seeded orders
DELETE FROM bh_rental WHERE listing_id IN (
  SELECT l.id FROM bh_listing l
  JOIN bh_item i ON l.item_id = i.id
  WHERE i.slug = 'cookie-jar-refill-ooak-cookies-750g'
) AND status = 'PENDING';

-- Re-create 12 pending orders from various community members
INSERT INTO bh_rental (id, listing_id, renter_id, status, renter_message, created_at, updated_at)
SELECT
  gen_random_uuid(),
  (SELECT l.id FROM bh_listing l JOIN bh_item i ON l.item_id = i.id WHERE i.slug = 'cookie-jar-refill-ooak-cookies-750g' LIMIT 1),
  u.id,
  'PENDING',
  'Would love a cookie box delivery!',
  NOW() - (rn || ' hours')::interval,
  NOW() - (rn || ' hours')::interval
FROM (
  SELECT id, ROW_NUMBER() OVER () as rn FROM bh_user
  WHERE slug NOT IN ('sofias-kitchen', 'admin')
  ORDER BY RANDOM()
  LIMIT 12
) u;

-- ============================================================
-- 7. REMOVE LEO'S FAVORITES ON BIKE (so we can show him favoriting it fresh)
-- ============================================================
DELETE FROM bh_item_favorite WHERE user_id = (SELECT id FROM bh_user WHERE slug = 'leonardos-bottega')
AND item_id = (SELECT id FROM bh_item WHERE slug = 'johnnys-delivery-bike-broken');

-- ============================================================
-- 8. VERIFY (uncomment to check)
-- ============================================================
-- SELECT 'Scooter listing' as check, status FROM bh_listing l JOIN bh_item i ON l.item_id = i.id WHERE i.slug = 'sallys-electric-scooter-for-delivery' AND l.listing_type = 'RENT';
-- SELECT 'Bike listing' as check, status, listing_type FROM bh_listing l JOIN bh_item i ON l.item_id = i.id WHERE i.slug = 'johnnys-delivery-bike-broken';
-- SELECT 'Sally name' as check, display_name FROM bh_user WHERE slug = 'sallys-kitchen';
-- SELECT 'Sofia orders' as check, COUNT(*) FROM bh_rental WHERE listing_id IN (SELECT l.id FROM bh_listing l JOIN bh_item i ON l.item_id = i.id WHERE i.slug = 'cookie-jar-refill-ooak-cookies-750g') AND status = 'PENDING';
-- SELECT 'Stale rentals' as check, COUNT(*) FROM bh_rental WHERE status NOT IN ('COMPLETED','DECLINED','CANCELLED');
