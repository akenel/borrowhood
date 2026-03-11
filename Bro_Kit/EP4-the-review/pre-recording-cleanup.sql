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
-- 3b. SEED COMMUNITY HELP BOARD POSTS (pre-existing before Johnny's post)
-- These make the Help Board look alive when the camera arrives.
-- Johnny's pressure washer post is created LIVE on camera (Scene 12).
-- Using fixed UUIDs so replies can reference posts directly (no subquery timing issues).
-- ============================================================

-- Rosa: need help with her garden gate hinge
INSERT INTO bh_help_post (id, author_id, title, body, help_type, category, urgency, status, content_language, reply_count, created_at, updated_at)
VALUES (
  'aaaa0004-e004-4001-a001-000000000001'::uuid,
  (SELECT id FROM bh_user WHERE slug = 'rosas-home'),
  'Garden gate hinge rusted shut -- can''t open it anymore',
  'The hinge on my side garden gate has completely rusted. I can''t open it without the whole frame shaking. It''s a wrought iron gate from the 1970s. Anyone know how to free a seized hinge without replacing the whole thing?',
  'NEED', 'home_improvement', 'NORMAL', 'OPEN', 'en', 1,
  NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days'
);

-- Leo replied to Rosa's gate post (3 days ago)
INSERT INTO bh_help_reply (id, post_id, author_id, body, created_at, updated_at)
VALUES (
  gen_random_uuid(),
  'aaaa0004-e004-4001-a001-000000000001'::uuid,
  (SELECT id FROM bh_user WHERE slug = 'leonardos-bottega'),
  'WD-40 won''t cut it on 50-year-old wrought iron. You need penetrating oil -- PB Blaster or Kroil. Soak it overnight, then tap the pin out with a hammer and punch. I''ve done this on old Bottega shutters. Bring it by if you can''t get the pin out.',
  NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days'
);

-- Aiko: offering calligraphy lessons
INSERT INTO bh_help_post (id, author_id, title, body, help_type, category, urgency, status, content_language, reply_count, created_at, updated_at)
VALUES (
  gen_random_uuid(),
  (SELECT id FROM bh_user WHERE slug = 'aiko-studio'),
  'I can teach Japanese calligraphy -- free for beginners',
  'I have 15 years of experience with brush calligraphy (Shodo). If anyone wants to learn the basics -- brush grip, stroke order, first kanji -- I''m happy to do a 1-hour session for free. You just need a brush and ink (I have extras). Weekends work best.',
  'OFFER', 'art', 'NORMAL', 'OPEN', 'en', 0,
  NOW() - INTERVAL '8 days', NOW() - INTERVAL '8 days'
);

-- Andrea: needs help fixing a leaking faucet
INSERT INTO bh_help_post (id, author_id, title, body, help_type, category, urgency, status, content_language, reply_count, created_at, updated_at)
VALUES (
  'aaaa0004-e004-4001-a002-000000000002'::uuid,
  (SELECT id FROM bh_user WHERE slug = 'andreas-water'),
  'Kitchen faucet dripping non-stop -- landlord says "fix it yourself"',
  'My kitchen faucet has been dripping for 2 weeks. The landlord told me to handle it. I watched 3 YouTube videos and I''m more confused than before. It''s a single-handle mixer. Is this a cartridge thing? Do I need a plumber or can someone walk me through it?',
  'NEED', 'home_improvement', 'NORMAL', 'OPEN', 'en', 1,
  NOW() - INTERVAL '4 days', NOW() - INTERVAL '4 days'
);

-- Mike replied to Andrea's faucet post
INSERT INTO bh_help_reply (id, post_id, author_id, body, created_at, updated_at)
VALUES (
  gen_random_uuid(),
  'aaaa0004-e004-4001-a002-000000000002'::uuid,
  (SELECT id FROM bh_user WHERE slug = 'mikes-garage'),
  'Single-handle mixer = ceramic disc cartridge 99% of the time. Turn off the water under the sink, pop the cap off the handle, unscrew the retaining nut, pull out the cartridge. Take it to the hardware store and match it. EUR 8 part, 15 minutes. Don''t pay a plumber EUR 80 for this.',
  NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days'
);

-- Alessia: resolved post about guitar strings
INSERT INTO bh_help_post (id, author_id, title, body, help_type, category, urgency, status, content_language, reply_count, resolved_by_id, created_at, updated_at)
VALUES (
  gen_random_uuid(),
  (SELECT id FROM bh_user WHERE slug = 'alessias-music'),
  'Where to find nylon guitar strings in Trapani?',
  'I need D''Addario EJ45 nylon strings for my classical guitar. Can''t find them anywhere in the centro. Does anyone know a music shop that stocks them, or has a spare set I could buy?',
  'NEED', 'art', 'LOW', 'RESOLVED', 'en', 0,
  (SELECT id FROM bh_user WHERE slug = 'leonardos-bottega'),
  NOW() - INTERVAL '12 days', NOW() - INTERVAL '10 days'
);

-- George: offering cooking lessons
INSERT INTO bh_help_post (id, author_id, title, body, help_type, category, urgency, status, content_language, reply_count, created_at, updated_at)
VALUES (
  gen_random_uuid(),
  (SELECT id FROM bh_user WHERE slug = 'georges-villa'),
  'Italian cooking basics -- I can host a group at the villa',
  'I''ve been learning Sicilian cooking from my neighbor Carmela for 3 years. Happy to host a small group (4-6 people) at the villa for a pasta-making session. Flour, eggs, and wine provided. Just bring an appetite and a good story.',
  'OFFER', 'services', 'NORMAL', 'OPEN', 'en', 0,
  NOW() - INTERVAL '6 days', NOW() - INTERVAL '6 days'
);

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

-- Fix broken static image URLs (replace with Unsplash)
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=800&h=600&fit=crop&q=80'
WHERE item_id = (SELECT id FROM bh_item WHERE slug = 'pressure-washer-karcher-k5') AND url LIKE '%karcher-k5-product%';
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=800&h=600&fit=crop&q=80'
WHERE item_id = (SELECT id FROM bh_item WHERE slug = 'pressure-washer-karcher-k5') AND url LIKE '%karcher-patio%';
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=800&h=600&fit=crop&q=80'
WHERE item_id = (SELECT id FROM bh_item WHERE slug = 'pressure-washer-karcher-k5') AND url LIKE '%karcher-garden%';
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800&h=600&fit=crop&q=80'
WHERE item_id = (SELECT id FROM bh_item WHERE slug = 'pressure-washer-karcher-k5') AND url LIKE '%karcher-boat%';

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
-- 12. FIX DISPLAY NAMES AND AVATARS
-- ============================================================
UPDATE bh_user SET display_name = 'Sally Thompson'
WHERE slug = 'sallys-kitchen' AND display_name != 'Sally Thompson';

-- Fix missing avatars (shows broken image on Help Board)
UPDATE bh_user SET avatar_url = 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&h=200&fit=crop&crop=face'
WHERE slug = 'andreas-water' AND (avatar_url IS NULL OR avatar_url = '');
UPDATE bh_user SET avatar_url = 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=200&h=200&fit=crop&crop=face'
WHERE slug = 'aiko-studio' AND (avatar_url IS NULL OR avatar_url = '');
UPDATE bh_user SET avatar_url = 'https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=200&h=200&fit=crop&crop=face'
WHERE slug = 'alessias-music' AND (avatar_url IS NULL OR avatar_url = '');

-- Fix cookie listing notes: description says 25 cookies, listing must match
UPDATE bh_listing SET notes = '25 cookies per bag. Various one-of-a-kind shapes. Message me your theme and I''ll bake it fresh.'
WHERE id IN (SELECT l.id FROM bh_listing l JOIN bh_item i ON l.item_id = i.id WHERE i.slug = 'cookie-jar-refill-ooak-cookies-750g');

-- Johnny's bike was claimed by Leo in EP3 -- no longer available
UPDATE bh_listing SET status = 'REMOVED'
WHERE item_id = (SELECT id FROM bh_item WHERE slug = 'johnnys-delivery-bike-broken')
  AND listing_type = 'GIVEAWAY' AND status = 'ACTIVE';

-- Fix 3D printer broken image (Thai food photo instead of printer)
UPDATE bh_item_media SET url = '/static/images/seed/3d-printer-prusa.png'
WHERE url LIKE '%photo-1631515243349%';

-- Fix surfboard broken image (SVG emoji doesn't render in <img> tags)
UPDATE bh_item_media SET url = '/static/images/seed/surfboard.png'
WHERE item_id = (SELECT id FROM bh_item WHERE slug = 'surfboard-76-funboard');

-- Fix camping table broken image (SVG emoji doesn't render in <img> tags)
UPDATE bh_item_media SET url = '/static/images/seed/camping-table.png'
WHERE item_id = (SELECT id FROM bh_item WHERE slug = 'camping-table-4-chairs-set');

-- Fix 3D printing service broken image (SVG emoji doesn't render in <img> tags)
UPDATE bh_item_media SET url = '/static/images/seed/3d-printing-service.png'
WHERE item_id = (SELECT id FROM bh_item WHERE slug = '3d-printing-service-custom-parts');

-- Fix grinding kit broken image (SVG emoji doesn't render in <img> tags)
UPDATE bh_item_media SET url = '/static/images/seed/grinding-kit.png'
WHERE item_id = (SELECT id FROM bh_item WHERE slug = 'lens-grinding-kit-optical-beginner');

-- Fix type set broken image (SVG emoji doesn't render in <img> tags)
UPDATE bh_item_media SET url = '/static/images/seed/type-set.png'
WHERE item_id = (SELECT id FROM bh_item WHERE slug = 'lead-type-set-textura-blackletter');

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

SELECT 'Help posts (should be 6 -- community posts seeded, Johnny creates his live)' AS check, COUNT(*)
FROM bh_help_post;

SELECT 'Reviews (should be 0 -- created live on camera)' AS check, COUNT(*)
FROM bh_review;

SELECT 'Review votes (should be 0)' AS check, COUNT(*)
FROM bh_review_vote;

SELECT 'Stale rentals (should be 0)' AS check, COUNT(*)
FROM bh_rental WHERE status NOT IN ('COMPLETED','DECLINED','CANCELLED');
