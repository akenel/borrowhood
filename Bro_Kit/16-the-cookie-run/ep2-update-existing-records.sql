-- ══════════════════════════════════════════════════════════════
-- EP02 "THE COOKIE RUN" -- Update Existing Records
-- Run AFTER scp of seed.json, BEFORE container restart.
--
--   ssh root@46.62.138.218 "docker exec -i postgres psql -U helix_user -d borrowhood" \
--     < Bro_Kit/16-the-cookie-run/ep2-update-existing-records.sql
-- ══════════════════════════════════════════════════════════════

BEGIN;

-- ── 1. Update Johnny Abela's user record ──

UPDATE bh_user
   SET workshop_name = 'Johnny''s Runs',
       workshop_type = 'OTHER',
       tagline = 'Cleaning by day, deliveries by bike (when it works)',
       bio = 'Everyone calls me Johnny. Maltese-Sicilian, born in Trapani. I clean houses and businesses -- industrial carpet cleaners, pressure washers, the real stuff. But my real dream is local delivery. I know every street, every shortcut, every doorbell that doesn''t work. Problem is, my bike keeps breaking. Chain snapped twice this month. The frame is bent from that pothole on Via Fardella. One day I''ll get an electric scooter and run a proper delivery service. Until then, I walk. And I clean. And I dream about that scooter.',
       telegram_username = 'johnny_runs',
       offers_delivery = true
 WHERE email = 'john@borrowhood.local';

-- ── 2. Update Sofia Ferretti's user record ──

UPDATE bh_user
   SET workshop_name = 'Sofia''s Bakes',
       workshop_type = 'KITCHEN'
 WHERE email = 'sofiaferretti@borrowhood.local';

-- ── 3. Fix broken image URL on "Baking with Sofia" item ──
-- (Image already local on server -- no fix needed)

COMMIT;

-- ── Verification ──

SELECT '--- JOHNNY ---' AS section;
SELECT display_name, workshop_name, tagline, offers_delivery
  FROM bh_user WHERE email = 'john@borrowhood.local';

SELECT '--- SOFIA ---' AS section;
SELECT display_name, workshop_name, workshop_type
  FROM bh_user WHERE email = 'sofiaferretti@borrowhood.local';

SELECT '--- BAKING IMAGE ---' AS section;
SELECT m.url, m.alt_text
  FROM bh_item_media m
  JOIN bh_item i ON m.item_id = i.id
 WHERE i.slug = 'baking-with-sofia-sicilian-cookies';
