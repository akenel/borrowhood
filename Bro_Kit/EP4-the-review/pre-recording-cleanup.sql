-- EP4 "The Review" -- Pre-Recording Cleanup
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

-- ============================================================
-- 2. CLEAN ALL REVIEWS (Sofia, Leo, Pietro create reviews live on camera)
-- ============================================================
DELETE FROM bh_review_vote;
DELETE FROM bh_review;

-- ============================================================
-- 3. CLEAN HELP BOARD (Johnny creates the first post live)
-- Delete ALL help posts -- EP4 seed data will repopulate community posts
-- but Johnny's pressure washer post must be created live on camera
-- ============================================================
DELETE FROM bh_help_reply;
DELETE FROM bh_help_media;
DELETE FROM bh_help_upvote;
DELETE FROM bh_help_post;

-- ============================================================
-- 4. ENSURE JOHNNY'S PRESSURE WASHER EXISTS AND IS LISTED
-- The item should already exist from seed data (slug: pressure-washer-karcher-k5)
-- Make sure the listing is ACTIVE
-- ============================================================
UPDATE bh_listing SET status = 'ACTIVE'
WHERE id IN (
  SELECT l.id FROM bh_listing l
  JOIN bh_item i ON l.item_id = i.id
  WHERE i.slug = 'pressure-washer-karcher-k5'
);

-- Verify it exists (will print a row if found)
SELECT 'Pressure washer' AS check, i.slug, i.name, u.display_name AS owner
FROM bh_item i JOIN bh_user u ON i.owner_id = u.id
WHERE i.slug = 'pressure-washer-karcher-k5';

-- ============================================================
-- 5. CLEAN OLD SEEDED COOKIE DELIVERY RENTALS (from EP3 setup)
-- Remove pending/cancelled cookie orders from previous takes
-- ============================================================
DELETE FROM bh_delivery_event WHERE tracking_id IN (
  SELECT dt.id FROM bh_delivery_tracking dt
  JOIN bh_rental r ON dt.rental_id = r.id
  JOIN bh_listing l ON r.listing_id = l.id
  JOIN bh_item i ON l.item_id = i.id
  WHERE i.slug = 'cookie-jar-refill-ooak-cookies-750g'
  AND r.status != 'COMPLETED'
);
DELETE FROM bh_delivery_tracking WHERE rental_id IN (
  SELECT r.id FROM bh_rental r
  JOIN bh_listing l ON r.listing_id = l.id
  JOIN bh_item i ON l.item_id = i.id
  WHERE i.slug = 'cookie-jar-refill-ooak-cookies-750g'
  AND r.status != 'COMPLETED'
);
DELETE FROM bh_review WHERE rental_id IN (
  SELECT r.id FROM bh_rental r
  JOIN bh_listing l ON r.listing_id = l.id
  JOIN bh_item i ON l.item_id = i.id
  WHERE i.slug = 'cookie-jar-refill-ooak-cookies-750g'
  AND r.status != 'COMPLETED'
);
DELETE FROM bh_rental WHERE listing_id IN (
  SELECT l.id FROM bh_listing l JOIN bh_item i ON l.item_id = i.id
  WHERE i.slug = 'cookie-jar-refill-ooak-cookies-750g'
) AND status != 'COMPLETED';

-- Also clean any existing completed cookie delivery rentals we're about to re-create
-- (idempotent re-runs)
DELETE FROM bh_delivery_event WHERE tracking_id IN (
  SELECT dt.id FROM bh_delivery_tracking dt
  JOIN bh_rental r ON dt.rental_id = r.id
  WHERE r.renter_message LIKE '%EP4-seed%'
);
DELETE FROM bh_delivery_tracking WHERE rental_id IN (
  SELECT r.id FROM bh_rental r WHERE r.renter_message LIKE '%EP4-seed%'
);
DELETE FROM bh_review WHERE rental_id IN (
  SELECT r.id FROM bh_rental r WHERE r.renter_message LIKE '%EP4-seed%'
);
DELETE FROM bh_rental WHERE renter_message LIKE '%EP4-seed%';

-- ============================================================
-- 6. CREATE SOFIA'S COMPLETED COOKIE ORDERS WITH JOHNNY AS DELIVERY
-- 4 completed rentals of Sofia's cookies, Johnny delivered by bike
-- ============================================================
-- Order 1: Aiko, Johnny bike delivery, 3 days ago
INSERT INTO bh_rental (id, listing_id, renter_id, status, renter_message, created_at, updated_at)
VALUES (
  gen_random_uuid(),
  (SELECT l.id FROM bh_listing l JOIN bh_item i ON l.item_id = i.id WHERE i.slug = 'cookie-jar-refill-ooak-cookies-750g' LIMIT 1),
  (SELECT id FROM bh_user WHERE slug = 'aiko-studio'),
  'COMPLETED',
  'EP4-seed: Cookie delivery by Johnny (bike)',
  NOW() - INTERVAL '3 days',
  NOW() - INTERVAL '3 days'
);

-- Order 2: Alessia, Johnny bike delivery, 5 days ago
INSERT INTO bh_rental (id, listing_id, renter_id, status, renter_message, created_at, updated_at)
VALUES (
  gen_random_uuid(),
  (SELECT l.id FROM bh_listing l JOIN bh_item i ON l.item_id = i.id WHERE i.slug = 'cookie-jar-refill-ooak-cookies-750g' LIMIT 1),
  (SELECT id FROM bh_user WHERE slug = 'alessias-music'),
  'COMPLETED',
  'EP4-seed: Cookie delivery by Johnny (bike)',
  NOW() - INTERVAL '5 days',
  NOW() - INTERVAL '5 days'
);

-- Order 3: Andrea, Johnny bike delivery, 7 days ago
INSERT INTO bh_rental (id, listing_id, renter_id, status, renter_message, created_at, updated_at)
VALUES (
  gen_random_uuid(),
  (SELECT l.id FROM bh_listing l JOIN bh_item i ON l.item_id = i.id WHERE i.slug = 'cookie-jar-refill-ooak-cookies-750g' LIMIT 1),
  (SELECT id FROM bh_user WHERE slug = 'andreas-water'),
  'COMPLETED',
  'EP4-seed: Cookie delivery by Johnny (bike)',
  NOW() - INTERVAL '7 days',
  NOW() - INTERVAL '7 days'
);

-- Order 4: Rosa, Johnny bike delivery, 10 days ago
INSERT INTO bh_rental (id, listing_id, renter_id, status, renter_message, created_at, updated_at)
VALUES (
  gen_random_uuid(),
  (SELECT l.id FROM bh_listing l JOIN bh_item i ON l.item_id = i.id WHERE i.slug = 'cookie-jar-refill-ooak-cookies-750g' LIMIT 1),
  (SELECT id FROM bh_user WHERE slug = 'rosas-home'),
  'COMPLETED',
  'EP4-seed: Cookie delivery by Johnny (bike)',
  NOW() - INTERVAL '10 days',
  NOW() - INTERVAL '10 days'
);

-- ============================================================
-- 7. CREATE DELIVERY TRACKING FOR JOHNNY'S BIKE DELIVERIES
-- Fast 20-minute deliveries (dispatched -> delivered quickly)
-- ============================================================
INSERT INTO bh_delivery_tracking (id, rental_id, delivery_method, status, delivery_notes, delivery_person_name, delivery_person_id, dispatched_at, delivered_at, confirmed_at, auto_confirm_hours, created_at, updated_at)
SELECT
  gen_random_uuid(),
  r.id,
  'human',
  'confirmed',
  'Johnny bike delivery -- cookies warm on arrival',
  'Johnny Abela',
  (SELECT id FROM bh_user WHERE slug = 'johns-cleaning'),
  r.created_at + INTERVAL '10 minutes',
  r.created_at + INTERVAL '30 minutes',
  r.created_at + INTERVAL '35 minutes',
  48,
  r.created_at,
  r.created_at
FROM bh_rental r
WHERE r.renter_message = 'EP4-seed: Cookie delivery by Johnny (bike)';

-- Add delivery events for bike deliveries
INSERT INTO bh_delivery_event (id, tracking_id, status, title, description, actor_id, actor_role, created_at, updated_at)
SELECT
  gen_random_uuid(),
  dt.id,
  'dispatched',
  'Johnny picked up cookies from Sofia',
  'Cookies packaged and loaded onto bike. En route!',
  (SELECT id FROM bh_user WHERE slug = 'johns-cleaning'),
  'courier',
  dt.dispatched_at,
  dt.dispatched_at
FROM bh_delivery_tracking dt
JOIN bh_rental r ON dt.rental_id = r.id
WHERE r.renter_message = 'EP4-seed: Cookie delivery by Johnny (bike)';

INSERT INTO bh_delivery_event (id, tracking_id, status, title, description, actor_id, actor_role, created_at, updated_at)
SELECT
  gen_random_uuid(),
  dt.id,
  'delivered',
  'Cookies delivered to front door',
  'Delivered warm. Customer confirmed happy.',
  (SELECT id FROM bh_user WHERE slug = 'johns-cleaning'),
  'courier',
  dt.delivered_at,
  dt.delivered_at
FROM bh_delivery_tracking dt
JOIN bh_rental r ON dt.rental_id = r.id
WHERE r.renter_message = 'EP4-seed: Cookie delivery by Johnny (bike)';

INSERT INTO bh_delivery_event (id, tracking_id, status, title, description, actor_role, created_at, updated_at)
SELECT
  gen_random_uuid(),
  dt.id,
  'confirmed',
  'Delivery confirmed by customer',
  'Receipt confirmed. Order complete.',
  'renter',
  dt.confirmed_at,
  dt.confirmed_at
FROM bh_delivery_tracking dt
JOIN bh_rental r ON dt.rental_id = r.id
WHERE r.renter_message = 'EP4-seed: Cookie delivery by Johnny (bike)';

-- ============================================================
-- 8. CREATE LEO'S COMPLETED COOKIE ORDER (DRONE DELIVERY -- the bad one)
-- 3-star review order: cookies great, drone delivery terrible
-- ============================================================
INSERT INTO bh_rental (id, listing_id, renter_id, status, renter_message, created_at, updated_at)
VALUES (
  gen_random_uuid(),
  (SELECT l.id FROM bh_listing l JOIN bh_item i ON l.item_id = i.id WHERE i.slug = 'cookie-jar-refill-ooak-cookies-750g' LIMIT 1),
  (SELECT id FROM bh_user WHERE slug = 'leonardos-bottega'),
  'COMPLETED',
  'EP4-seed: Cookie delivery by drone (the bad one)',
  NOW() - INTERVAL '4 days',
  NOW() - INTERVAL '4 days'
);

-- Drone delivery tracking: dispatched -> delivered with 3hr gap (cookies cold!)
INSERT INTO bh_delivery_tracking (id, rental_id, delivery_method, status, delivery_notes, dispatched_at, delivered_at, confirmed_at, auto_confirm_hours, created_at, updated_at)
SELECT
  gen_random_uuid(),
  r.id,
  'drone',
  'confirmed',
  'Drone dropped cookies on balcony. 3 hours later they were cold.',
  r.created_at + INTERVAL '10 minutes',
  r.created_at + INTERVAL '3 hours 10 minutes',
  r.created_at + INTERVAL '3 hours 30 minutes',
  48,
  r.created_at,
  r.created_at
FROM bh_rental r
WHERE r.renter_message = 'EP4-seed: Cookie delivery by drone (the bad one)';

-- Drone delivery events
INSERT INTO bh_delivery_event (id, tracking_id, status, title, description, actor_role, created_at, updated_at)
SELECT
  gen_random_uuid(),
  dt.id,
  'dispatched',
  'Drone dispatched with cookies',
  'Sofia packaged cookies for drone delivery. Drone launched.',
  'system',
  dt.dispatched_at,
  dt.dispatched_at
FROM bh_delivery_tracking dt
JOIN bh_rental r ON dt.rental_id = r.id
WHERE r.renter_message = 'EP4-seed: Cookie delivery by drone (the bad one)';

INSERT INTO bh_delivery_event (id, tracking_id, status, title, description, actor_role, created_at, updated_at)
SELECT
  gen_random_uuid(),
  dt.id,
  'delivered',
  'Drone dropped package on balcony',
  'Like a seagull dropping a fish. Cookies landed on the balcony railing.',
  'system',
  dt.delivered_at,
  dt.delivered_at
FROM bh_delivery_tracking dt
JOIN bh_rental r ON dt.rental_id = r.id
WHERE r.renter_message = 'EP4-seed: Cookie delivery by drone (the bad one)';

INSERT INTO bh_delivery_event (id, tracking_id, status, title, description, actor_role, next_action, created_at, updated_at)
SELECT
  gen_random_uuid(),
  dt.id,
  'confirmed',
  'Leo confirmed receipt (3 hours late, cookies cold)',
  'Cookies arrived cold. Quality was fine but delivery was terrible.',
  'renter',
  'Consider leaving a review',
  dt.confirmed_at,
  dt.confirmed_at
FROM bh_delivery_tracking dt
JOIN bh_rental r ON dt.rental_id = r.id
WHERE r.renter_message = 'EP4-seed: Cookie delivery by drone (the bad one)';

-- ============================================================
-- 9. ENSURE MIKE'S WORKSHOP IS ACTIVE WITH WELDING/SAFETY COURSES
-- ============================================================
-- Mike's welding machine training listing should be ACTIVE
UPDATE bh_listing SET status = 'ACTIVE'
WHERE id IN (
  SELECT l.id FROM bh_listing l
  JOIN bh_item i ON l.item_id = i.id
  WHERE i.slug = 'welding-machine-mig-200a'
  AND l.listing_type = 'TRAINING'
);

-- Verify Mike's workshop
SELECT 'Mike workshop' AS check, u.display_name, u.workshop_name, u.workshop_type
FROM bh_user u WHERE u.slug = 'mikes-garage';

-- ============================================================
-- 10. ENSURE LEO'S BOTTEGA WORKSHOP IS ACTIVE
-- ============================================================
SELECT 'Leo workshop' AS check, u.display_name, u.workshop_name, u.workshop_type
FROM bh_user u WHERE u.slug = 'leonardos-bottega';

-- ============================================================
-- 11. ENSURE GEORGE EXISTS (for breadcrumb cameo scene)
-- ============================================================
SELECT 'George exists' AS check, u.display_name, u.slug
FROM bh_user u WHERE u.slug = 'georges-villa';

-- ============================================================
-- 12. FIX SALLY'S DISPLAY NAME (consistency from EP3)
-- ============================================================
UPDATE bh_user SET display_name = 'Sally Thompson'
WHERE slug = 'sallys-kitchen' AND display_name != 'Sally Thompson';

-- ============================================================
-- 13. VERIFY COUNTS
-- ============================================================
SELECT 'Completed cookie rentals (Johnny bike)' AS check, COUNT(*)
FROM bh_rental WHERE renter_message = 'EP4-seed: Cookie delivery by Johnny (bike)';

SELECT 'Completed cookie rental (Leo drone)' AS check, COUNT(*)
FROM bh_rental WHERE renter_message = 'EP4-seed: Cookie delivery by drone (the bad one)';

SELECT 'Delivery tracking records' AS check, COUNT(*)
FROM bh_delivery_tracking dt
JOIN bh_rental r ON dt.rental_id = r.id
WHERE r.renter_message LIKE 'EP4-seed%';

SELECT 'Delivery events' AS check, COUNT(*)
FROM bh_delivery_event de
JOIN bh_delivery_tracking dt ON de.tracking_id = dt.id
JOIN bh_rental r ON dt.rental_id = r.id
WHERE r.renter_message LIKE 'EP4-seed%';

SELECT 'Help posts (should be 0 -- Johnny creates first one live)' AS check, COUNT(*)
FROM bh_help_post;

SELECT 'Reviews (should be 0 -- created live on camera)' AS check, COUNT(*)
FROM bh_review;

SELECT 'Review votes (should be 0)' AS check, COUNT(*)
FROM bh_review_vote;

SELECT 'Stale rentals (should be 0)' AS check, COUNT(*)
FROM bh_rental WHERE status NOT IN ('COMPLETED','DECLINED','CANCELLED');
