-- ══════════════════════════════════════════════════════════════
-- EP02 "THE COOKIE RUN" -- Fix broken /media/ image paths
-- Replaces local file paths with Unsplash URLs for EP2 cast
--
-- Run on Hetzner:
--   ssh root@46.62.138.218 "docker exec -i postgres psql -U helix_user -d borrowhood" \
--     < Bro_Kit/16-the-cookie-run/ep2-fix-broken-images.sql
-- ══════════════════════════════════════════════════════════════

BEGIN;

-- ── Step 1: Delete all broken /media/ images for EP2 cast items ──
DELETE FROM bh_item_media
 WHERE url LIKE '/media/%'
   AND item_id IN (
     SELECT i.id FROM bh_item i
     JOIN bh_user u ON i.owner_id = u.id
     WHERE u.email IN (
       'sally@borrowhood.local',
       'pietro@borrowhood.local',
       'sofiaferretti@borrowhood.local',
       'john@borrowhood.local'
     )
   );

-- ── Step 2: Insert correct Unsplash images ──

-- === JOHNNY: Pressure Washer (Karcher K5) ===
INSERT INTO bh_item_media (id, item_id, media_type, url, alt_text, sort_order)
SELECT gen_random_uuid(), i.id, 'PHOTO',
       'https://images.unsplash.com/photo-1621274403997-37aace184f49?w=800&h=600&fit=crop&q=80',
       'Karcher K5 pressure washer - product photo', 0
FROM bh_item i WHERE i.slug = 'pressure-washer-karcher-k5';

INSERT INTO bh_item_media (id, item_id, media_type, url, alt_text, sort_order)
SELECT gen_random_uuid(), i.id, 'PHOTO',
       'https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=800&h=600&fit=crop&q=80',
       'Pressure washing stone patio - before and after', 1
FROM bh_item i WHERE i.slug = 'pressure-washer-karcher-k5';

INSERT INTO bh_item_media (id, item_id, media_type, url, alt_text, sort_order)
SELECT gen_random_uuid(), i.id, 'PHOTO',
       'https://images.unsplash.com/photo-1520340356584-f9917d1eea6f?w=800&h=600&fit=crop&q=80',
       'Pressure washing car in driveway', 2
FROM bh_item i WHERE i.slug = 'pressure-washer-karcher-k5';

INSERT INTO bh_item_media (id, item_id, media_type, url, alt_text, sort_order)
SELECT gen_random_uuid(), i.id, 'PHOTO',
       'https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=800&h=600&fit=crop&q=80',
       'Pressure washing concrete driveway', 3
FROM bh_item i WHERE i.slug = 'pressure-washer-karcher-k5';

-- === JOHNNY: Industrial Carpet Cleaner ===
INSERT INTO bh_item_media (id, item_id, media_type, url, alt_text, sort_order)
SELECT gen_random_uuid(), i.id, 'PHOTO',
       'https://images.unsplash.com/photo-1558317374-067fb5f30001?w=800&h=600&fit=crop&q=80',
       'Industrial Carpet Cleaner - product photo', 0
FROM bh_item i WHERE i.slug = 'industrial-carpet-cleaner';

INSERT INTO bh_item_media (id, item_id, media_type, url, alt_text, sort_order)
SELECT gen_random_uuid(), i.id, 'PHOTO',
       'https://images.unsplash.com/photo-1628177142898-93e36e4e3a50?w=800&h=600&fit=crop&q=80',
       'Deep carpet cleaning in progress - hot water extraction', 1
FROM bh_item i WHERE i.slug = 'industrial-carpet-cleaner';

INSERT INTO bh_item_media (id, item_id, media_type, url, alt_text, sort_order)
SELECT gen_random_uuid(), i.id, 'PHOTO',
       'https://images.unsplash.com/photo-1527515637462-cee1395c688c?w=800&h=600&fit=crop&q=80',
       'Clean carpet result after professional treatment', 2
FROM bh_item i WHERE i.slug = 'industrial-carpet-cleaner';

-- === JOHNNY: Carpet Cleaner (Bissell ProHeat 2X) ===
INSERT INTO bh_item_media (id, item_id, media_type, url, alt_text, sort_order)
SELECT gen_random_uuid(), i.id, 'PHOTO',
       'https://images.unsplash.com/photo-1558317374-067fb5f30001?w=800&h=600&fit=crop&q=80',
       'Bissell ProHeat 2X carpet cleaner', 0
FROM bh_item i WHERE i.slug = 'carpet-cleaner-bissell-proheat-2x';

INSERT INTO bh_item_media (id, item_id, media_type, url, alt_text, sort_order)
SELECT gen_random_uuid(), i.id, 'PHOTO',
       'https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=800&h=600&fit=crop&q=80',
       'Carpet cleaning in living room', 1
FROM bh_item i WHERE i.slug = 'carpet-cleaner-bissell-proheat-2x';

INSERT INTO bh_item_media (id, item_id, media_type, url, alt_text, sort_order)
SELECT gen_random_uuid(), i.id, 'PHOTO',
       'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800&h=600&fit=crop&q=80',
       'Professional cleaning results on upholstery', 2
FROM bh_item i WHERE i.slug = 'carpet-cleaner-bissell-proheat-2x';

-- === JOHNNY: Deep Cleaning Service ===
INSERT INTO bh_item_media (id, item_id, media_type, url, alt_text, sort_order)
SELECT gen_random_uuid(), i.id, 'PHOTO',
       'https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=800&h=600&fit=crop&q=80',
       'Professional deep cleaning service in modern apartment', 0
FROM bh_item i WHERE i.slug = 'deep-cleaning-service-move-in-out';

INSERT INTO bh_item_media (id, item_id, media_type, url, alt_text, sort_order)
SELECT gen_random_uuid(), i.id, 'PHOTO',
       'https://images.unsplash.com/photo-1584820927498-cfe5211fd8bf?w=800&h=600&fit=crop&q=80',
       'Kitchen deep cleaning -- sparkling countertops', 1
FROM bh_item i WHERE i.slug = 'deep-cleaning-service-move-in-out';

INSERT INTO bh_item_media (id, item_id, media_type, url, alt_text, sort_order)
SELECT gen_random_uuid(), i.id, 'PHOTO',
       'https://images.unsplash.com/photo-1527515637462-cee1395c688c?w=800&h=600&fit=crop&q=80',
       'Bathroom deep cleaning -- tiles and grout', 2
FROM bh_item i WHERE i.slug = 'deep-cleaning-service-move-in-out';

-- === PIETRO: DJI Mavic 3 Pro ===
INSERT INTO bh_item_media (id, item_id, media_type, url, alt_text, sort_order)
SELECT gen_random_uuid(), i.id, 'PHOTO',
       'https://images.unsplash.com/photo-1507582020474-9a35b7d455d9?w=800&h=600&fit=crop&q=80',
       'DJI Mavic 3 Pro hovering over coast', 0
FROM bh_item i WHERE i.slug = 'dji-mavic-3-pro-fly-more-combo';

INSERT INTO bh_item_media (id, item_id, media_type, url, alt_text, sort_order)
SELECT gen_random_uuid(), i.id, 'PHOTO',
       'https://images.unsplash.com/photo-1473968512647-3e447244af8f?w=800&h=600&fit=crop&q=80',
       'Drone controller and Fly More accessories', 1
FROM bh_item i WHERE i.slug = 'dji-mavic-3-pro-fly-more-combo';

INSERT INTO bh_item_media (id, item_id, media_type, url, alt_text, sort_order)
SELECT gen_random_uuid(), i.id, 'PHOTO',
       'https://images.unsplash.com/photo-1508614589041-895b88991e3e?w=800&h=600&fit=crop&q=80',
       'Aerial view of Sicilian coastline from drone', 2
FROM bh_item i WHERE i.slug = 'dji-mavic-3-pro-fly-more-combo';

-- === PIETRO: DJI Mini 4 Pro ===
INSERT INTO bh_item_media (id, item_id, media_type, url, alt_text, sort_order)
SELECT gen_random_uuid(), i.id, 'PHOTO',
       'https://images.unsplash.com/photo-1507582020474-9a35b7d455d9?w=800&h=600&fit=crop&q=80',
       'DJI Mini 4 Pro - compact drone in hand', 0
FROM bh_item i WHERE i.slug = 'dji-mini-4-pro-beginner-friendly';

INSERT INTO bh_item_media (id, item_id, media_type, url, alt_text, sort_order)
SELECT gen_random_uuid(), i.id, 'PHOTO',
       'https://images.unsplash.com/photo-1473968512647-3e447244af8f?w=800&h=600&fit=crop&q=80',
       'Mini drone flying over olive grove', 1
FROM bh_item i WHERE i.slug = 'dji-mini-4-pro-beginner-friendly';

-- === PIETRO: FPV Racing Drone Kit ===
INSERT INTO bh_item_media (id, item_id, media_type, url, alt_text, sort_order)
SELECT gen_random_uuid(), i.id, 'PHOTO',
       'https://images.unsplash.com/photo-1507582020474-9a35b7d455d9?w=800&h=600&fit=crop&q=80',
       'FPV racing drones with goggles and controller', 0
FROM bh_item i WHERE i.slug = 'fpv-racing-drone-kit-2-drones';

INSERT INTO bh_item_media (id, item_id, media_type, url, alt_text, sort_order)
SELECT gen_random_uuid(), i.id, 'PHOTO',
       'https://images.unsplash.com/photo-1473968512647-3e447244af8f?w=800&h=600&fit=crop&q=80',
       'FPV drone mid-flight at speed', 1
FROM bh_item i WHERE i.slug = 'fpv-racing-drone-kit-2-drones';

INSERT INTO bh_item_media (id, item_id, media_type, url, alt_text, sort_order)
SELECT gen_random_uuid(), i.id, 'PHOTO',
       'https://images.unsplash.com/photo-1508614589041-895b88991e3e?w=800&h=600&fit=crop&q=80',
       'DJI FPV goggles - first person view', 2
FROM bh_item i WHERE i.slug = 'fpv-racing-drone-kit-2-drones';

-- === PIETRO: Drone Pilot License Prep Course ===
INSERT INTO bh_item_media (id, item_id, media_type, url, alt_text, sort_order)
SELECT gen_random_uuid(), i.id, 'PHOTO',
       'https://images.unsplash.com/photo-1508614589041-895b88991e3e?w=800&h=600&fit=crop&q=80',
       'Drone Pilot License Prep Course -- training session', 0
FROM bh_item i WHERE i.slug = 'drone-pilot-license-prep-eu';

-- === PIETRO: Drone Repair & Tune-Up Service ===
INSERT INTO bh_item_media (id, item_id, media_type, url, alt_text, sort_order)
SELECT gen_random_uuid(), i.id, 'PHOTO',
       'https://images.unsplash.com/photo-1579829366248-204fe8413f31?w=800&h=600&fit=crop&q=80',
       'Drone Repair & Tune-Up -- components on workbench', 0
FROM bh_item i WHERE i.slug = 'drone-repair-tune-up-service';

-- === SALLY: Professional Cookie Cutter Set ===
INSERT INTO bh_item_media (id, item_id, media_type, url, alt_text, sort_order)
SELECT gen_random_uuid(), i.id, 'PHOTO',
       'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=800&h=600&fit=crop&q=80',
       'Professional Cookie Cutter Set (200 pieces)', 0
FROM bh_item i WHERE i.slug = 'professional-cookie-cutter-set-200-pieces';

-- === SALLY: Pasta Machine ===
INSERT INTO bh_item_media (id, item_id, media_type, url, alt_text, sort_order)
SELECT gen_random_uuid(), i.id, 'PHOTO',
       'https://images.unsplash.com/photo-1556761223-4c4282c73f77?w=800&h=600&fit=crop&q=80',
       'Pasta Machine (Marcato Atlas 150 + Ravioli Set)', 0
FROM bh_item i WHERE i.slug = 'pasta-machine-marcato-atlas-150-ravioli-set';

-- === SALLY: Commercial Kitchen ===
INSERT INTO bh_item_media (id, item_id, media_type, url, alt_text, sort_order)
SELECT gen_random_uuid(), i.id, 'PHOTO',
       'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800&h=600&fit=crop&q=80',
       'Professional commercial kitchen with stainless steel equipment', 0
FROM bh_item i WHERE i.slug = 'commercial-kitchen-event-catering';

-- === SALLY: Custom Sicilian Pastries ===
INSERT INTO bh_item_media (id, item_id, media_type, url, alt_text, sort_order)
SELECT gen_random_uuid(), i.id, 'PHOTO',
       'https://images.unsplash.com/photo-1551024506-0bccd828d307?w=800&h=600&fit=crop&q=80',
       'Assortment of Sicilian cannoli and pastries on display', 0
FROM bh_item i WHERE i.slug = 'custom-sicilian-pastries-events';

-- === SALLY: Cookie Recipe Collection ===
INSERT INTO bh_item_media (id, item_id, media_type, url, alt_text, sort_order)
SELECT gen_random_uuid(), i.id, 'PHOTO',
       'https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=800&h=600&fit=crop&q=80',
       'Sally''s Secret Cookie Recipe Collection', 0
FROM bh_item i WHERE i.slug = 'sallys-secret-cookie-recipe-collection';

-- === SALLY: Bread Maker ===
INSERT INTO bh_item_media (id, item_id, media_type, url, alt_text, sort_order)
SELECT gen_random_uuid(), i.id, 'PHOTO',
       'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800&h=600&fit=crop&q=80',
       'Fresh baked bread from bread maker', 0
FROM bh_item i WHERE i.slug = 'bread-maker-panasonic-free';

INSERT INTO bh_item_media (id, item_id, media_type, url, alt_text, sort_order)
SELECT gen_random_uuid(), i.id, 'PHOTO',
       'https://images.unsplash.com/photo-1555932450-31a8aec2adf1?w=800&h=600&fit=crop&q=80',
       'Bread loaves fresh from oven', 1
FROM bh_item i WHERE i.slug = 'bread-maker-panasonic-free';

-- === SOFIA: Birthday Cookie Box ===
-- Delete any existing broken media first (already handled above),
-- then insert the correct URL
INSERT INTO bh_item_media (id, item_id, media_type, url, alt_text, sort_order)
SELECT gen_random_uuid(), i.id, 'PHOTO',
       'https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=800&h=600&fit=crop&q=80',
       'Sofia''s Birthday Cookie Box - fresh baked cookies', 0
FROM bh_item i WHERE i.slug = 'sofias-birthday-cookie-box'
  AND NOT EXISTS (SELECT 1 FROM bh_item_media m WHERE m.item_id = i.id AND m.url LIKE 'https://%');

COMMIT;

-- ══════════════════════════════════════════════════════════════
-- Verification: Show all EP2 cast items and their images
-- ══════════════════════════════════════════════════════════════

SELECT '--- EP2 CAST IMAGES (should ALL be https://) ---' AS section;
SELECT u.display_name, i.name, m.url, m.sort_order
  FROM bh_item_media m
  JOIN bh_item i ON m.item_id = i.id
  JOIN bh_user u ON i.owner_id = u.id
 WHERE u.email IN ('sally@borrowhood.local', 'pietro@borrowhood.local',
                   'sofiaferretti@borrowhood.local', 'john@borrowhood.local')
 ORDER BY u.display_name, i.name, m.sort_order;

SELECT '--- BROKEN IMAGES REMAINING (should be 0) ---' AS section;
SELECT COUNT(*) AS broken_images
  FROM bh_item_media m
  JOIN bh_item i ON m.item_id = i.id
  JOIN bh_user u ON i.owner_id = u.id
 WHERE u.email IN ('sally@borrowhood.local', 'pietro@borrowhood.local',
                   'sofiaferretti@borrowhood.local', 'john@borrowhood.local')
   AND m.url LIKE '/media/%';
