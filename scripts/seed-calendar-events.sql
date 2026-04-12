-- Calendar seed data: 10 events + 12 RSVPs across April-May 2026
-- Run with: cat seed-calendar-events.sql | ssh root@46.62.138.218 "docker exec -i postgres psql -U helix_user -d borrowhood"

BEGIN;

-- ═══ APRIL EVENTS ═══

-- Mike: Welding Workshop (Apr 15)
INSERT INTO bh_item (id, owner_id, name, slug, content_language, description, category, item_type, condition)
VALUES ('aaaa0001-0000-0000-0000-000000000001', 'cf050b80-d052-4904-b989-10e9ddf07b11',
  'Welding Basics Workshop', 'welding-basics-workshop', 'en',
  'Learn MIG welding fundamentals. Bring safety glasses and gloves. All skill levels welcome. We will cover tack welding, bead running, and basic joint types.',
  'welding', 'SERVICE', 'NEW');
INSERT INTO bh_listing (id, item_id, listing_type, status, currency, delivery_available, pickup_only, version, price, price_unit, max_participants, event_start, event_end, event_venue, event_address)
VALUES ('bbbb0001-0000-0000-0000-000000000001', 'aaaa0001-0000-0000-0000-000000000001',
  'EVENT', 'ACTIVE', 'EUR', false, true, 1, 30, 'flat', 8,
  '2026-04-15 09:00:00+02', '2026-04-15 12:00:00+02',
  'Mike''s Garage', 'Via Fardella 120, Trapani');

-- Sally: Baking Class (Apr 18)
INSERT INTO bh_item (id, owner_id, name, slug, content_language, description, category, item_type, condition)
VALUES ('aaaa0002-0000-0000-0000-000000000002', '43248d4a-1cfe-40c3-8fe3-d912a8bc86bf',
  'Sicilian Cannoli Masterclass', 'sicilian-cannoli-masterclass', 'en',
  'Make authentic Sicilian cannoli from scratch. Ricotta filling, crispy shells, pistachio dust. Take home a dozen. Ingredients included.',
  'kitchen', 'SERVICE', 'NEW');
INSERT INTO bh_listing (id, item_id, listing_type, status, currency, delivery_available, pickup_only, version, price, price_unit, max_participants, event_start, event_end, event_venue, event_address)
VALUES ('bbbb0002-0000-0000-0000-000000000002', 'aaaa0002-0000-0000-0000-000000000002',
  'EVENT', 'ACTIVE', 'EUR', false, true, 1, 25, 'flat', 12,
  '2026-04-18 14:00:00+02', '2026-04-18 17:00:00+02',
  'Sally''s Kitchen', 'Via Garibaldi 45, Trapani');

-- Leo: Woodworking Open Day (Apr 20, FREE)
INSERT INTO bh_item (id, owner_id, name, slug, content_language, description, category, item_type, condition)
VALUES ('aaaa0003-0000-0000-0000-000000000003', '6a7de30c-22c7-45f3-9191-16a8572148fc',
  'Bottega Open Day - Meet the Maker', 'bottega-open-day', 'en',
  'Come visit the Bottega! See Renaissance woodworking techniques in action. Free admission. Coffee and biscotti provided. Bring your curiosity.',
  'woodworking', 'SERVICE', 'NEW');
INSERT INTO bh_listing (id, item_id, listing_type, status, currency, delivery_available, pickup_only, version, max_participants, event_start, event_end, event_venue, event_address)
VALUES ('bbbb0003-0000-0000-0000-000000000003', 'aaaa0003-0000-0000-0000-000000000003',
  'EVENT', 'ACTIVE', 'EUR', false, true, 1, 30,
  '2026-04-20 10:00:00+02', '2026-04-20 16:00:00+02',
  'Bottega di Leonardo', 'Via delle Arti 7, Trapani');

-- Nic: Jiu-Jitsu for Beginners (Apr 22, FREE)
INSERT INTO bh_item (id, owner_id, name, slug, content_language, description, category, item_type, condition)
VALUES ('aaaa0004-0000-0000-0000-000000000004', '9aeed7f2-7fd3-4402-96ce-f46af3af7429',
  'Jiu-Jitsu Fundamentals at D50', 'jiu-jitsu-fundamentals-d50', 'en',
  'Free introductory session. Learn basic positions, escapes, and respect on the mat. Wear comfortable clothes. Ages 14+. Water provided.',
  'sports', 'SERVICE', 'NEW');
INSERT INTO bh_listing (id, item_id, listing_type, status, currency, delivery_available, pickup_only, version, max_participants, event_start, event_end, event_venue, event_address)
VALUES ('bbbb0004-0000-0000-0000-000000000004', 'aaaa0004-0000-0000-0000-000000000004',
  'EVENT', 'ACTIVE', 'EUR', false, true, 1, 20,
  '2026-04-22 17:00:00+02', '2026-04-22 19:00:00+02',
  'D50 Palazzo', 'Via Torrearsa 50, Alcamo');

-- Angel: La Piazza Community Meetup (Apr 25, FREE)
INSERT INTO bh_item (id, owner_id, name, slug, content_language, description, category, item_type, condition)
VALUES ('aaaa0005-0000-0000-0000-000000000005', 'a35c7cc7-9e45-410d-a1be-b1bc7d465931',
  'La Piazza Community Meetup', 'la-piazza-community-meetup', 'en',
  'Monthly community gathering. Meet your neighbors, share ideas, demo new features. Pizza and drinks on us. Everyone welcome.',
  'spaces', 'SERVICE', 'NEW');
INSERT INTO bh_listing (id, item_id, listing_type, status, currency, delivery_available, pickup_only, version, max_participants, event_start, event_end, event_venue, event_address)
VALUES ('bbbb0005-0000-0000-0000-000000000005', 'aaaa0005-0000-0000-0000-000000000005',
  'EVENT', 'ACTIVE', 'EUR', false, true, 1, 50,
  '2026-04-25 18:00:00+02', '2026-04-25 21:00:00+02',
  'Pizza Planet', 'Via Asmara 35, Bonagia (TP)');

-- Pietro: Drone Photography Workshop (Apr 27)
INSERT INTO bh_item (id, owner_id, name, slug, content_language, description, category, item_type, condition)
VALUES ('aaaa0006-0000-0000-0000-000000000006', '4ace6543-de50-422e-836d-35e2606b9046',
  'Drone Photography Over Erice', 'drone-photography-erice', 'en',
  'Fly drones and capture aerial photos of Erice castle and the salt pans. Bring your own drone or use ours. Registration required for flight clearance.',
  'drones', 'PHYSICAL', 'NEW');
INSERT INTO bh_listing (id, item_id, listing_type, status, currency, delivery_available, pickup_only, version, price, price_unit, max_participants, event_start, event_end, event_venue, event_address)
VALUES ('bbbb0006-0000-0000-0000-000000000006', 'aaaa0006-0000-0000-0000-000000000006',
  'EVENT', 'ACTIVE', 'EUR', false, true, 1, 15, 'flat', 6,
  '2026-04-27 07:00:00+02', '2026-04-27 10:00:00+02',
  'Erice Cable Car Base', 'Via Capua, Trapani');

-- Sally: Sunday Farmers Market (Apr 13, past)
INSERT INTO bh_item (id, owner_id, name, slug, content_language, description, category, item_type, condition)
VALUES ('aaaa0007-0000-0000-0000-000000000007', '43248d4a-1cfe-40c3-8fe3-d912a8bc86bf',
  'Sunday Farmers Market Stand', 'sunday-farmers-market', 'en',
  'Fresh produce, homemade jams, and baked goods. Come early for the best picks. Family friendly.',
  'kitchen', 'SERVICE', 'NEW');
INSERT INTO bh_listing (id, item_id, listing_type, status, currency, delivery_available, pickup_only, version, event_start, event_end, event_venue, event_address)
VALUES ('bbbb0007-0000-0000-0000-000000000007', 'aaaa0007-0000-0000-0000-000000000007',
  'EVENT', 'ACTIVE', 'EUR', false, true, 1,
  '2026-04-13 07:00:00+02', '2026-04-13 13:00:00+02',
  'Piazza Mercato', 'Piazza Mercato del Pesce, Trapani');

-- ═══ MAY EVENTS ═══

-- Mike: Advanced Welding (May 3)
INSERT INTO bh_item (id, owner_id, name, slug, content_language, description, category, item_type, condition)
VALUES ('aaaa0008-0000-0000-0000-000000000008', 'cf050b80-d052-4904-b989-10e9ddf07b11',
  'Advanced Welding - TIG Techniques', 'advanced-welding-tig', 'en',
  'For graduates of the basics workshop. TIG welding on aluminum and stainless steel. Must have completed Welding Basics first.',
  'welding', 'SERVICE', 'NEW');
INSERT INTO bh_listing (id, item_id, listing_type, status, currency, delivery_available, pickup_only, version, price, price_unit, max_participants, event_start, event_end, event_venue, event_address)
VALUES ('bbbb0008-0000-0000-0000-000000000008', 'aaaa0008-0000-0000-0000-000000000008',
  'EVENT', 'ACTIVE', 'EUR', false, true, 1, 45, 'flat', 6,
  '2026-05-03 09:00:00+02', '2026-05-03 13:00:00+02',
  'Mike''s Garage', 'Via Fardella 120, Trapani');

-- Leo: Renaissance Drawing (May 10, FREE)
INSERT INTO bh_item (id, owner_id, name, slug, content_language, description, category, item_type, condition)
VALUES ('aaaa0009-0000-0000-0000-000000000009', '6a7de30c-22c7-45f3-9191-16a8572148fc',
  'Renaissance Drawing Techniques', 'renaissance-drawing', 'en',
  'Learn perspective, shading, and anatomical sketching the way Leonardo taught his apprentices. Paper and charcoal provided. All levels.',
  'art', 'SERVICE', 'NEW');
INSERT INTO bh_listing (id, item_id, listing_type, status, currency, delivery_available, pickup_only, version, max_participants, event_start, event_end, event_venue, event_address)
VALUES ('bbbb0009-0000-0000-0000-000000000009', 'aaaa0009-0000-0000-0000-000000000009',
  'EVENT', 'ACTIVE', 'EUR', false, true, 1, 15,
  '2026-05-10 10:00:00+02', '2026-05-10 13:00:00+02',
  'Bottega di Leonardo', 'Via delle Arti 7, Trapani');

-- Nic: Beach Cleanup (May 17, FREE)
INSERT INTO bh_item (id, owner_id, name, slug, content_language, description, category, item_type, condition)
VALUES ('aaaa0010-0000-0000-0000-000000000010', '9aeed7f2-7fd3-4402-96ce-f46af3af7429',
  'Trapani Beach Cleanup', 'trapani-beach-cleanup', 'en',
  'Help us clean up the coastline. Bags and gloves provided. Meet at the parking lot. Refreshments after. Community service hours available for students.',
  'camping', 'SERVICE', 'NEW');
INSERT INTO bh_listing (id, item_id, listing_type, status, currency, delivery_available, pickup_only, version, max_participants, event_start, event_end, event_venue, event_address)
VALUES ('bbbb0010-0000-0000-0000-000000000010', 'aaaa0010-0000-0000-0000-000000000010',
  'EVENT', 'ACTIVE', 'EUR', false, true, 1, 40,
  '2026-05-17 08:00:00+02', '2026-05-17 12:00:00+02',
  'Lido Paradiso', 'Lungomare Dante Alighieri, Trapani');

-- ═══ RSVPs ═══

-- Sally + Leo -> Mike's welding
INSERT INTO bh_event_rsvp (id, listing_id, user_id, status) VALUES
  (gen_random_uuid(), 'bbbb0001-0000-0000-0000-000000000001', '43248d4a-1cfe-40c3-8fe3-d912a8bc86bf', 'REGISTERED'),
  (gen_random_uuid(), 'bbbb0001-0000-0000-0000-000000000001', '6a7de30c-22c7-45f3-9191-16a8572148fc', 'REGISTERED');

-- Johnny -> Sally's cannoli
INSERT INTO bh_event_rsvp (id, listing_id, user_id, status) VALUES
  (gen_random_uuid(), 'bbbb0002-0000-0000-0000-000000000002', 'b9ed3c47-01a4-462b-ab85-4274267a8ac7', 'REGISTERED');

-- Mike + Nic -> Leo's open day
INSERT INTO bh_event_rsvp (id, listing_id, user_id, status) VALUES
  (gen_random_uuid(), 'bbbb0003-0000-0000-0000-000000000003', 'cf050b80-d052-4904-b989-10e9ddf07b11', 'REGISTERED'),
  (gen_random_uuid(), 'bbbb0003-0000-0000-0000-000000000003', '9aeed7f2-7fd3-4402-96ce-f46af3af7429', 'REGISTERED');

-- Johnny + Sally -> Nic's jiu-jitsu
INSERT INTO bh_event_rsvp (id, listing_id, user_id, status) VALUES
  (gen_random_uuid(), 'bbbb0004-0000-0000-0000-000000000004', 'b9ed3c47-01a4-462b-ab85-4274267a8ac7', 'REGISTERED'),
  (gen_random_uuid(), 'bbbb0004-0000-0000-0000-000000000004', '43248d4a-1cfe-40c3-8fe3-d912a8bc86bf', 'REGISTERED');

-- Sally + Leo + Mike + Nic -> Community meetup
INSERT INTO bh_event_rsvp (id, listing_id, user_id, status) VALUES
  (gen_random_uuid(), 'bbbb0005-0000-0000-0000-000000000005', '43248d4a-1cfe-40c3-8fe3-d912a8bc86bf', 'REGISTERED'),
  (gen_random_uuid(), 'bbbb0005-0000-0000-0000-000000000005', '6a7de30c-22c7-45f3-9191-16a8572148fc', 'REGISTERED'),
  (gen_random_uuid(), 'bbbb0005-0000-0000-0000-000000000005', 'cf050b80-d052-4904-b989-10e9ddf07b11', 'REGISTERED'),
  (gen_random_uuid(), 'bbbb0005-0000-0000-0000-000000000005', '9aeed7f2-7fd3-4402-96ce-f46af3af7429', 'REGISTERED');

-- Pietro -> drone workshop
INSERT INTO bh_event_rsvp (id, listing_id, user_id, status) VALUES
  (gen_random_uuid(), 'bbbb0006-0000-0000-0000-000000000006', '4ace6543-de50-422e-836d-35e2606b9046', 'REGISTERED');

COMMIT;
