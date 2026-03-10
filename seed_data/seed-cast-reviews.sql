-- Seed reviews for all 14 cast members
-- Creates completed rentals between cast members, then seeds reviews on them
-- Run: ssh root@46.62.138.218 "docker exec -i postgres psql -U helix_user -d borrowhood < /tmp/seed-cast-reviews.sql"

BEGIN;

-- ════════════════════════════════════════════════════════════════
-- STEP 1: Create completed rentals between cast members
-- Each cast member rents from several others
-- ════════════════════════════════════════════════════════════════

-- Cast member IDs (for reference)
-- angel-hq          = a35c7cc7-9e45-410d-a1be-b1bc7d465931  LEGEND
-- annes-qa-lab      = daa0ad6b-67bd-4967-93fc-44d618713691  ACTIVE
-- georges-villa     = 97ef53f7-f409-4fa6-a2ad-ee1b86cf4973  PILLAR
-- jakes-electronics = 7948b667-63dc-4c83-bbdb-963b17ecdc27  TRUSTED
-- johns-cleaning    = b9ed3c47-01a4-462b-ab85-4274267a8ac7  NEWCOMER
-- leonardos-bottega = 6a7de30c-22c7-45f3-9191-16a8572148fc  LEGEND
-- marcos-workshop   = ac3826a7-6ecb-4070-a4bc-e91108cbfb2b  LEGEND
-- marias-garden     = 150fb4dd-2a03-4c17-8bab-1a2cee8b7e07  PILLAR
-- mikes-garage      = cf050b80-d052-4904-b989-10e9ddf07b11  ACTIVE
-- ninos-campers     = beec122b-8950-49d7-8e2c-9eb798d0587a  TRUSTED
-- pietros-drones    = 4ace6543-de50-422e-836d-35e2606b9046  TRUSTED
-- rosas-home        = d2ca621f-87a7-45ce-a84c-06034fe3cdb3  PILLAR
-- sallys-kitchen    = 43248d4a-1cfe-40c3-8fe3-d912a8bc86bf  ACTIVE
-- sofias-bakes      = 77e15081-c09d-4352-bda5-e70fb8d85fa8  NEWCOMER

-- Listing IDs (one per cast member)
-- angel-hq          → 161bfef1-bac0-4f11-8dc4-f4b3e96f2330
-- annes-qa-lab      → ed285069-8c47-49c6-be84-2d77b01baa13
-- georges-villa     → 7a2e4ad3-11f2-43fc-944f-d9dd8145c480
-- jakes-electronics → 42614d7e-6805-4281-8ab7-52777c815d41
-- johns-cleaning    → 4b5316f2-a1d3-4507-a653-aff4a55d6f77
-- leonardos-bottega → ad2c633b-d079-4f4b-8b8e-23ea13f50449
-- marcos-workshop   → 0d57a150-04b8-49ec-a64b-34f4479a077a
-- marias-garden     → 72197f0d-ec1a-4c2f-850d-1698ec058867
-- mikes-garage      → 5c8d43b1-79b5-48d9-bb27-1351e46bde27
-- ninos-campers     → 463cb484-4efe-423f-9d4f-25cdb3755e9b
-- pietros-drones    → b7bd3597-6006-4b1b-94e7-969c36206d53
-- rosas-home        → 2ec8d31b-2f6a-4c67-a6a5-03e84ae75c63
-- sallys-kitchen    → 9f92a5bd-ead0-47bc-a57b-ab37507ee369
-- sofias-bakes      → 22b0496a-96e9-4b27-b9a1-3272a28ecf6c

-- Helper: create a completed rental
-- (id, listing_id, renter_id, status, start_date, end_date)

CREATE TEMP TABLE cast_rentals (
    rental_id UUID DEFAULT gen_random_uuid(),
    listing_id UUID NOT NULL,
    renter_id UUID NOT NULL,
    owner_slug TEXT NOT NULL  -- for tracking who owns the listing
);

-- Reviews FOR Angel (18 reviews_received) -- others rent from Angel and review him
INSERT INTO cast_rentals (listing_id, renter_id, owner_slug) VALUES
('161bfef1-bac0-4f11-8dc4-f4b3e96f2330', '6a7de30c-22c7-45f3-9191-16a8572148fc', 'angel-hq'),  -- Leo reviews Angel
('161bfef1-bac0-4f11-8dc4-f4b3e96f2330', 'ac3826a7-6ecb-4070-a4bc-e91108cbfb2b', 'angel-hq'),  -- Marco reviews Angel
('161bfef1-bac0-4f11-8dc4-f4b3e96f2330', '97ef53f7-f409-4fa6-a2ad-ee1b86cf4973', 'angel-hq'),  -- George reviews Angel
('161bfef1-bac0-4f11-8dc4-f4b3e96f2330', '150fb4dd-2a03-4c17-8bab-1a2cee8b7e07', 'angel-hq'),  -- Maria reviews Angel
('161bfef1-bac0-4f11-8dc4-f4b3e96f2330', 'd2ca621f-87a7-45ce-a84c-06034fe3cdb3', 'angel-hq'),  -- Rosa reviews Angel
('161bfef1-bac0-4f11-8dc4-f4b3e96f2330', 'beec122b-8950-49d7-8e2c-9eb798d0587a', 'angel-hq'),  -- Nino reviews Angel
('161bfef1-bac0-4f11-8dc4-f4b3e96f2330', '4ace6543-de50-422e-836d-35e2606b9046', 'angel-hq'),  -- Pietro reviews Angel
('161bfef1-bac0-4f11-8dc4-f4b3e96f2330', '7948b667-63dc-4c83-bbdb-963b17ecdc27', 'angel-hq'),  -- Jake reviews Angel
('161bfef1-bac0-4f11-8dc4-f4b3e96f2330', '43248d4a-1cfe-40c3-8fe3-d912a8bc86bf', 'angel-hq'),  -- Sally reviews Angel
('161bfef1-bac0-4f11-8dc4-f4b3e96f2330', 'cf050b80-d052-4904-b989-10e9ddf07b11', 'angel-hq'),  -- Mike reviews Angel
('161bfef1-bac0-4f11-8dc4-f4b3e96f2330', 'b9ed3c47-01a4-462b-ab85-4274267a8ac7', 'angel-hq'),  -- Johnny reviews Angel
('161bfef1-bac0-4f11-8dc4-f4b3e96f2330', '77e15081-c09d-4352-bda5-e70fb8d85fa8', 'angel-hq'),  -- Sofia reviews Angel
('161bfef1-bac0-4f11-8dc4-f4b3e96f2330', 'daa0ad6b-67bd-4967-93fc-44d618713691', 'angel-hq');  -- Anne reviews Angel

-- Reviews FOR Leo (18 of 45 -- we seed 18 from cast, rest implied from non-cast)
INSERT INTO cast_rentals (listing_id, renter_id, owner_slug) VALUES
('ad2c633b-d079-4f4b-8b8e-23ea13f50449', 'a35c7cc7-9e45-410d-a1be-b1bc7d465931', 'leonardos-bottega'),  -- Angel
('ad2c633b-d079-4f4b-8b8e-23ea13f50449', 'ac3826a7-6ecb-4070-a4bc-e91108cbfb2b', 'leonardos-bottega'),  -- Marco
('ad2c633b-d079-4f4b-8b8e-23ea13f50449', '97ef53f7-f409-4fa6-a2ad-ee1b86cf4973', 'leonardos-bottega'),  -- George
('ad2c633b-d079-4f4b-8b8e-23ea13f50449', '150fb4dd-2a03-4c17-8bab-1a2cee8b7e07', 'leonardos-bottega'),  -- Maria
('ad2c633b-d079-4f4b-8b8e-23ea13f50449', 'd2ca621f-87a7-45ce-a84c-06034fe3cdb3', 'leonardos-bottega'),  -- Rosa
('ad2c633b-d079-4f4b-8b8e-23ea13f50449', 'beec122b-8950-49d7-8e2c-9eb798d0587a', 'leonardos-bottega'),  -- Nino
('ad2c633b-d079-4f4b-8b8e-23ea13f50449', '4ace6543-de50-422e-836d-35e2606b9046', 'leonardos-bottega'),  -- Pietro
('ad2c633b-d079-4f4b-8b8e-23ea13f50449', '7948b667-63dc-4c83-bbdb-963b17ecdc27', 'leonardos-bottega'),  -- Jake
('ad2c633b-d079-4f4b-8b8e-23ea13f50449', '43248d4a-1cfe-40c3-8fe3-d912a8bc86bf', 'leonardos-bottega'),  -- Sally
('ad2c633b-d079-4f4b-8b8e-23ea13f50449', 'cf050b80-d052-4904-b989-10e9ddf07b11', 'leonardos-bottega'),  -- Mike
('ad2c633b-d079-4f4b-8b8e-23ea13f50449', 'b9ed3c47-01a4-462b-ab85-4274267a8ac7', 'leonardos-bottega'),  -- Johnny
('ad2c633b-d079-4f4b-8b8e-23ea13f50449', '77e15081-c09d-4352-bda5-e70fb8d85fa8', 'leonardos-bottega'),  -- Sofia
('ad2c633b-d079-4f4b-8b8e-23ea13f50449', 'daa0ad6b-67bd-4967-93fc-44d618713691', 'leonardos-bottega');  -- Anne

-- Reviews FOR Marco (14 of 30)
INSERT INTO cast_rentals (listing_id, renter_id, owner_slug) VALUES
('0d57a150-04b8-49ec-a64b-34f4479a077a', 'a35c7cc7-9e45-410d-a1be-b1bc7d465931', 'marcos-workshop'),
('0d57a150-04b8-49ec-a64b-34f4479a077a', '6a7de30c-22c7-45f3-9191-16a8572148fc', 'marcos-workshop'),
('0d57a150-04b8-49ec-a64b-34f4479a077a', '97ef53f7-f409-4fa6-a2ad-ee1b86cf4973', 'marcos-workshop'),
('0d57a150-04b8-49ec-a64b-34f4479a077a', '150fb4dd-2a03-4c17-8bab-1a2cee8b7e07', 'marcos-workshop'),
('0d57a150-04b8-49ec-a64b-34f4479a077a', 'd2ca621f-87a7-45ce-a84c-06034fe3cdb3', 'marcos-workshop'),
('0d57a150-04b8-49ec-a64b-34f4479a077a', 'beec122b-8950-49d7-8e2c-9eb798d0587a', 'marcos-workshop'),
('0d57a150-04b8-49ec-a64b-34f4479a077a', '4ace6543-de50-422e-836d-35e2606b9046', 'marcos-workshop'),
('0d57a150-04b8-49ec-a64b-34f4479a077a', '7948b667-63dc-4c83-bbdb-963b17ecdc27', 'marcos-workshop'),
('0d57a150-04b8-49ec-a64b-34f4479a077a', '43248d4a-1cfe-40c3-8fe3-d912a8bc86bf', 'marcos-workshop'),
('0d57a150-04b8-49ec-a64b-34f4479a077a', 'cf050b80-d052-4904-b989-10e9ddf07b11', 'marcos-workshop'),
('0d57a150-04b8-49ec-a64b-34f4479a077a', 'b9ed3c47-01a4-462b-ab85-4274267a8ac7', 'marcos-workshop'),
('0d57a150-04b8-49ec-a64b-34f4479a077a', '77e15081-c09d-4352-bda5-e70fb8d85fa8', 'marcos-workshop'),
('0d57a150-04b8-49ec-a64b-34f4479a077a', 'daa0ad6b-67bd-4967-93fc-44d618713691', 'marcos-workshop');

-- Reviews FOR George (13 of 25)
INSERT INTO cast_rentals (listing_id, renter_id, owner_slug) VALUES
('7a2e4ad3-11f2-43fc-944f-d9dd8145c480', 'a35c7cc7-9e45-410d-a1be-b1bc7d465931', 'georges-villa'),
('7a2e4ad3-11f2-43fc-944f-d9dd8145c480', '6a7de30c-22c7-45f3-9191-16a8572148fc', 'georges-villa'),
('7a2e4ad3-11f2-43fc-944f-d9dd8145c480', 'ac3826a7-6ecb-4070-a4bc-e91108cbfb2b', 'georges-villa'),
('7a2e4ad3-11f2-43fc-944f-d9dd8145c480', '150fb4dd-2a03-4c17-8bab-1a2cee8b7e07', 'georges-villa'),
('7a2e4ad3-11f2-43fc-944f-d9dd8145c480', 'd2ca621f-87a7-45ce-a84c-06034fe3cdb3', 'georges-villa'),
('7a2e4ad3-11f2-43fc-944f-d9dd8145c480', 'beec122b-8950-49d7-8e2c-9eb798d0587a', 'georges-villa'),
('7a2e4ad3-11f2-43fc-944f-d9dd8145c480', '4ace6543-de50-422e-836d-35e2606b9046', 'georges-villa'),
('7a2e4ad3-11f2-43fc-944f-d9dd8145c480', '7948b667-63dc-4c83-bbdb-963b17ecdc27', 'georges-villa'),
('7a2e4ad3-11f2-43fc-944f-d9dd8145c480', '43248d4a-1cfe-40c3-8fe3-d912a8bc86bf', 'georges-villa'),
('7a2e4ad3-11f2-43fc-944f-d9dd8145c480', 'cf050b80-d052-4904-b989-10e9ddf07b11', 'georges-villa'),
('7a2e4ad3-11f2-43fc-944f-d9dd8145c480', 'b9ed3c47-01a4-462b-ab85-4274267a8ac7', 'georges-villa'),
('7a2e4ad3-11f2-43fc-944f-d9dd8145c480', '77e15081-c09d-4352-bda5-e70fb8d85fa8', 'georges-villa'),
('7a2e4ad3-11f2-43fc-944f-d9dd8145c480', 'daa0ad6b-67bd-4967-93fc-44d618713691', 'georges-villa');

-- Reviews FOR Maria (13 of 25)
INSERT INTO cast_rentals (listing_id, renter_id, owner_slug) VALUES
('72197f0d-ec1a-4c2f-850d-1698ec058867', 'a35c7cc7-9e45-410d-a1be-b1bc7d465931', 'marias-garden'),
('72197f0d-ec1a-4c2f-850d-1698ec058867', '6a7de30c-22c7-45f3-9191-16a8572148fc', 'marias-garden'),
('72197f0d-ec1a-4c2f-850d-1698ec058867', 'ac3826a7-6ecb-4070-a4bc-e91108cbfb2b', 'marias-garden'),
('72197f0d-ec1a-4c2f-850d-1698ec058867', '97ef53f7-f409-4fa6-a2ad-ee1b86cf4973', 'marias-garden'),
('72197f0d-ec1a-4c2f-850d-1698ec058867', 'd2ca621f-87a7-45ce-a84c-06034fe3cdb3', 'marias-garden'),
('72197f0d-ec1a-4c2f-850d-1698ec058867', 'beec122b-8950-49d7-8e2c-9eb798d0587a', 'marias-garden'),
('72197f0d-ec1a-4c2f-850d-1698ec058867', '4ace6543-de50-422e-836d-35e2606b9046', 'marias-garden'),
('72197f0d-ec1a-4c2f-850d-1698ec058867', '7948b667-63dc-4c83-bbdb-963b17ecdc27', 'marias-garden'),
('72197f0d-ec1a-4c2f-850d-1698ec058867', '43248d4a-1cfe-40c3-8fe3-d912a8bc86bf', 'marias-garden'),
('72197f0d-ec1a-4c2f-850d-1698ec058867', 'cf050b80-d052-4904-b989-10e9ddf07b11', 'marias-garden'),
('72197f0d-ec1a-4c2f-850d-1698ec058867', 'b9ed3c47-01a4-462b-ab85-4274267a8ac7', 'marias-garden'),
('72197f0d-ec1a-4c2f-850d-1698ec058867', '77e15081-c09d-4352-bda5-e70fb8d85fa8', 'marias-garden'),
('72197f0d-ec1a-4c2f-850d-1698ec058867', 'daa0ad6b-67bd-4967-93fc-44d618713691', 'marias-garden');

-- Reviews FOR Rosa (13 of 35)
INSERT INTO cast_rentals (listing_id, renter_id, owner_slug) VALUES
('2ec8d31b-2f6a-4c67-a6a5-03e84ae75c63', 'a35c7cc7-9e45-410d-a1be-b1bc7d465931', 'rosas-home'),
('2ec8d31b-2f6a-4c67-a6a5-03e84ae75c63', '6a7de30c-22c7-45f3-9191-16a8572148fc', 'rosas-home'),
('2ec8d31b-2f6a-4c67-a6a5-03e84ae75c63', 'ac3826a7-6ecb-4070-a4bc-e91108cbfb2b', 'rosas-home'),
('2ec8d31b-2f6a-4c67-a6a5-03e84ae75c63', '97ef53f7-f409-4fa6-a2ad-ee1b86cf4973', 'rosas-home'),
('2ec8d31b-2f6a-4c67-a6a5-03e84ae75c63', '150fb4dd-2a03-4c17-8bab-1a2cee8b7e07', 'rosas-home'),
('2ec8d31b-2f6a-4c67-a6a5-03e84ae75c63', 'beec122b-8950-49d7-8e2c-9eb798d0587a', 'rosas-home'),
('2ec8d31b-2f6a-4c67-a6a5-03e84ae75c63', '4ace6543-de50-422e-836d-35e2606b9046', 'rosas-home'),
('2ec8d31b-2f6a-4c67-a6a5-03e84ae75c63', '7948b667-63dc-4c83-bbdb-963b17ecdc27', 'rosas-home'),
('2ec8d31b-2f6a-4c67-a6a5-03e84ae75c63', '43248d4a-1cfe-40c3-8fe3-d912a8bc86bf', 'rosas-home'),
('2ec8d31b-2f6a-4c67-a6a5-03e84ae75c63', 'cf050b80-d052-4904-b989-10e9ddf07b11', 'rosas-home'),
('2ec8d31b-2f6a-4c67-a6a5-03e84ae75c63', 'b9ed3c47-01a4-462b-ab85-4274267a8ac7', 'rosas-home'),
('2ec8d31b-2f6a-4c67-a6a5-03e84ae75c63', '77e15081-c09d-4352-bda5-e70fb8d85fa8', 'rosas-home'),
('2ec8d31b-2f6a-4c67-a6a5-03e84ae75c63', 'daa0ad6b-67bd-4967-93fc-44d618713691', 'rosas-home');

-- Reviews FOR Nino (13 of 18)
INSERT INTO cast_rentals (listing_id, renter_id, owner_slug) VALUES
('463cb484-4efe-423f-9d4f-25cdb3755e9b', 'a35c7cc7-9e45-410d-a1be-b1bc7d465931', 'ninos-campers'),
('463cb484-4efe-423f-9d4f-25cdb3755e9b', '6a7de30c-22c7-45f3-9191-16a8572148fc', 'ninos-campers'),
('463cb484-4efe-423f-9d4f-25cdb3755e9b', 'ac3826a7-6ecb-4070-a4bc-e91108cbfb2b', 'ninos-campers'),
('463cb484-4efe-423f-9d4f-25cdb3755e9b', '97ef53f7-f409-4fa6-a2ad-ee1b86cf4973', 'ninos-campers'),
('463cb484-4efe-423f-9d4f-25cdb3755e9b', '150fb4dd-2a03-4c17-8bab-1a2cee8b7e07', 'ninos-campers'),
('463cb484-4efe-423f-9d4f-25cdb3755e9b', 'd2ca621f-87a7-45ce-a84c-06034fe3cdb3', 'ninos-campers'),
('463cb484-4efe-423f-9d4f-25cdb3755e9b', '4ace6543-de50-422e-836d-35e2606b9046', 'ninos-campers'),
('463cb484-4efe-423f-9d4f-25cdb3755e9b', '7948b667-63dc-4c83-bbdb-963b17ecdc27', 'ninos-campers'),
('463cb484-4efe-423f-9d4f-25cdb3755e9b', '43248d4a-1cfe-40c3-8fe3-d912a8bc86bf', 'ninos-campers'),
('463cb484-4efe-423f-9d4f-25cdb3755e9b', 'cf050b80-d052-4904-b989-10e9ddf07b11', 'ninos-campers'),
('463cb484-4efe-423f-9d4f-25cdb3755e9b', 'b9ed3c47-01a4-462b-ab85-4274267a8ac7', 'ninos-campers'),
('463cb484-4efe-423f-9d4f-25cdb3755e9b', '77e15081-c09d-4352-bda5-e70fb8d85fa8', 'ninos-campers'),
('463cb484-4efe-423f-9d4f-25cdb3755e9b', 'daa0ad6b-67bd-4967-93fc-44d618713691', 'ninos-campers');

-- Reviews FOR Pietro (9)
INSERT INTO cast_rentals (listing_id, renter_id, owner_slug) VALUES
('b7bd3597-6006-4b1b-94e7-969c36206d53', 'a35c7cc7-9e45-410d-a1be-b1bc7d465931', 'pietros-drones'),
('b7bd3597-6006-4b1b-94e7-969c36206d53', '6a7de30c-22c7-45f3-9191-16a8572148fc', 'pietros-drones'),
('b7bd3597-6006-4b1b-94e7-969c36206d53', 'ac3826a7-6ecb-4070-a4bc-e91108cbfb2b', 'pietros-drones'),
('b7bd3597-6006-4b1b-94e7-969c36206d53', '97ef53f7-f409-4fa6-a2ad-ee1b86cf4973', 'pietros-drones'),
('b7bd3597-6006-4b1b-94e7-969c36206d53', '150fb4dd-2a03-4c17-8bab-1a2cee8b7e07', 'pietros-drones'),
('b7bd3597-6006-4b1b-94e7-969c36206d53', 'd2ca621f-87a7-45ce-a84c-06034fe3cdb3', 'pietros-drones'),
('b7bd3597-6006-4b1b-94e7-969c36206d53', '43248d4a-1cfe-40c3-8fe3-d912a8bc86bf', 'pietros-drones'),
('b7bd3597-6006-4b1b-94e7-969c36206d53', 'cf050b80-d052-4904-b989-10e9ddf07b11', 'pietros-drones'),
('b7bd3597-6006-4b1b-94e7-969c36206d53', 'b9ed3c47-01a4-462b-ab85-4274267a8ac7', 'pietros-drones');

-- Reviews FOR Jake (5)
INSERT INTO cast_rentals (listing_id, renter_id, owner_slug) VALUES
('42614d7e-6805-4281-8ab7-52777c815d41', 'a35c7cc7-9e45-410d-a1be-b1bc7d465931', 'jakes-electronics'),
('42614d7e-6805-4281-8ab7-52777c815d41', '6a7de30c-22c7-45f3-9191-16a8572148fc', 'jakes-electronics'),
('42614d7e-6805-4281-8ab7-52777c815d41', 'ac3826a7-6ecb-4070-a4bc-e91108cbfb2b', 'jakes-electronics'),
('42614d7e-6805-4281-8ab7-52777c815d41', '4ace6543-de50-422e-836d-35e2606b9046', 'jakes-electronics'),
('42614d7e-6805-4281-8ab7-52777c815d41', 'beec122b-8950-49d7-8e2c-9eb798d0587a', 'jakes-electronics');

-- Reviews FOR Mike (5 -- he had 0 but he's active now after EP3)
INSERT INTO cast_rentals (listing_id, renter_id, owner_slug) VALUES
('5c8d43b1-79b5-48d9-bb27-1351e46bde27', 'a35c7cc7-9e45-410d-a1be-b1bc7d465931', 'mikes-garage'),
('5c8d43b1-79b5-48d9-bb27-1351e46bde27', '6a7de30c-22c7-45f3-9191-16a8572148fc', 'mikes-garage'),
('5c8d43b1-79b5-48d9-bb27-1351e46bde27', 'ac3826a7-6ecb-4070-a4bc-e91108cbfb2b', 'mikes-garage'),
('5c8d43b1-79b5-48d9-bb27-1351e46bde27', '4ace6543-de50-422e-836d-35e2606b9046', 'mikes-garage'),
('5c8d43b1-79b5-48d9-bb27-1351e46bde27', 'beec122b-8950-49d7-8e2c-9eb798d0587a', 'mikes-garage');

-- Reviews FOR Sally (5 of seeded 2, upgrading since she has many completed rentals)
INSERT INTO cast_rentals (listing_id, renter_id, owner_slug) VALUES
('9f92a5bd-ead0-47bc-a57b-ab37507ee369', 'a35c7cc7-9e45-410d-a1be-b1bc7d465931', 'sallys-kitchen'),
('9f92a5bd-ead0-47bc-a57b-ab37507ee369', '6a7de30c-22c7-45f3-9191-16a8572148fc', 'sallys-kitchen'),
('9f92a5bd-ead0-47bc-a57b-ab37507ee369', 'ac3826a7-6ecb-4070-a4bc-e91108cbfb2b', 'sallys-kitchen'),
('9f92a5bd-ead0-47bc-a57b-ab37507ee369', '97ef53f7-f409-4fa6-a2ad-ee1b86cf4973', 'sallys-kitchen'),
('9f92a5bd-ead0-47bc-a57b-ab37507ee369', '150fb4dd-2a03-4c17-8bab-1a2cee8b7e07', 'sallys-kitchen');

-- Reviews FOR Johnny (3)
INSERT INTO cast_rentals (listing_id, renter_id, owner_slug) VALUES
('4b5316f2-a1d3-4507-a653-aff4a55d6f77', 'a35c7cc7-9e45-410d-a1be-b1bc7d465931', 'johns-cleaning'),
('4b5316f2-a1d3-4507-a653-aff4a55d6f77', '43248d4a-1cfe-40c3-8fe3-d912a8bc86bf', 'johns-cleaning'),
('4b5316f2-a1d3-4507-a653-aff4a55d6f77', 'cf050b80-d052-4904-b989-10e9ddf07b11', 'johns-cleaning');

-- Reviews FOR Sofia (3)
INSERT INTO cast_rentals (listing_id, renter_id, owner_slug) VALUES
('22b0496a-96e9-4b27-b9a1-3272a28ecf6c', '43248d4a-1cfe-40c3-8fe3-d912a8bc86bf', 'sofias-bakes'),
('22b0496a-96e9-4b27-b9a1-3272a28ecf6c', '97ef53f7-f409-4fa6-a2ad-ee1b86cf4973', 'sofias-bakes'),
('22b0496a-96e9-4b27-b9a1-3272a28ecf6c', 'beec122b-8950-49d7-8e2c-9eb798d0587a', 'sofias-bakes');

-- Reviews FOR Anne (3)
INSERT INTO cast_rentals (listing_id, renter_id, owner_slug) VALUES
('ed285069-8c47-49c6-be84-2d77b01baa13', 'a35c7cc7-9e45-410d-a1be-b1bc7d465931', 'annes-qa-lab'),
('ed285069-8c47-49c6-be84-2d77b01baa13', '6a7de30c-22c7-45f3-9191-16a8572148fc', 'annes-qa-lab'),
('ed285069-8c47-49c6-be84-2d77b01baa13', 'ac3826a7-6ecb-4070-a4bc-e91108cbfb2b', 'annes-qa-lab');

-- ════════════════════════════════════════════════════════════════
-- STEP 2: Insert completed rentals from temp table
-- ════════════════════════════════════════════════════════════════

INSERT INTO bh_rental (id, listing_id, renter_id, status, requested_start, requested_end, renter_message, created_at, updated_at)
SELECT
    cr.rental_id,
    cr.listing_id,
    cr.renter_id,
    'COMPLETED',
    (CURRENT_DATE - (30 + (random()*60)::int)),
    (CURRENT_DATE - (1 + (random()*25)::int)),
    'Great experience, thanks!',
    NOW() - interval '30 days' * random(),
    NOW() - interval '5 days' * random()
FROM cast_rentals cr;

-- ════════════════════════════════════════════════════════════════
-- STEP 3: Insert reviews linked to those rentals
-- ════════════════════════════════════════════════════════════════

-- Review titles and bodies (realistic variety)
CREATE TEMP TABLE review_templates (idx SERIAL, title TEXT, body TEXT, rating INT);
INSERT INTO review_templates (title, body, rating) VALUES
('Excellent experience', 'Everything was exactly as described. Communication was fast and friendly. Would rent again without hesitation.', 5),
('Highly recommended', 'Professional from start to finish. The item was in perfect condition and the pickup was smooth.', 5),
('Great service', 'Very responsive and helpful. Made the whole process easy. Five stars well deserved.', 5),
('Fantastic!', 'Above and beyond what I expected. The quality was outstanding and the owner was incredibly kind.', 5),
('Very good', 'Solid experience overall. Item was clean, well-maintained, and returned process was simple.', 4),
('Good value', 'Fair pricing for what you get. Everything worked as expected. Would use again.', 4),
('Really happy', 'Met at the agreed time, item was ready to go. No issues whatsoever. Thank you!', 5),
('Smooth transaction', 'Quick responses, clear instructions, and the item worked perfectly. Great neighbor!', 5),
('Super helpful', 'Not only was the item great but they also showed me how to use it properly. Real community spirit.', 5),
('Would rent again', 'Trustworthy and professional. The whole BorrowHood experience was exactly what I hoped for.', 5),
('Perfect condition', 'Item looked brand new. Carefully maintained. You can tell the owner cares about quality.', 5),
('Friendly and reliable', 'Always on time, always friendly. This is what sharing economy should be.', 5),
('Nice experience', 'Good overall. Minor delay on pickup but everything else was perfect.', 4),
('Solid', 'Does what it says. Clean item, fair price, easy process. Would recommend to neighbors.', 4),
('Amazing quality', 'I was impressed by how well everything was organized. Clear instructions, clean item, great communication.', 5);

-- Insert reviews: one per rental, reviewer = renter, reviewee = owner
INSERT INTO bh_review (id, rental_id, reviewer_id, reviewee_id, rating, title, body, content_language, reviewer_tier, weight, visible, created_at, updated_at)
SELECT
    gen_random_uuid(),
    cr.rental_id,
    cr.renter_id,
    i.owner_id,
    rt.rating,
    rt.title,
    rt.body,
    'en',
    reviewer.badge_tier,
    CASE reviewer.badge_tier
        WHEN 'NEWCOMER' THEN 1.0
        WHEN 'ACTIVE' THEN 2.0
        WHEN 'TRUSTED' THEN 5.0
        WHEN 'PILLAR' THEN 8.0
        WHEN 'LEGEND' THEN 10.0
        ELSE 1.0
    END,
    true,
    NOW() - interval '1 day' * (random()*30)::int,
    NOW() - interval '1 day' * (random()*5)::int
FROM cast_rentals cr
JOIN bh_listing l ON l.id = cr.listing_id
JOIN bh_item i ON i.id = l.item_id
JOIN bh_user reviewer ON reviewer.id = cr.renter_id
JOIN review_templates rt ON rt.idx = 1 + (hashtext(cr.rental_id::text) % 15 + 15) % 15;

-- ════════════════════════════════════════════════════════════════
-- STEP 4: Update reviews_received counts to match actual rows
-- ════════════════════════════════════════════════════════════════

UPDATE bh_user_points p
SET reviews_received = sub.cnt
FROM (
    SELECT reviewee_id, COUNT(*) as cnt
    FROM bh_review
    WHERE visible = true AND deleted_at IS NULL
    GROUP BY reviewee_id
) sub
WHERE p.user_id = sub.reviewee_id;

-- Also set to 0 for cast members with no reviews
UPDATE bh_user_points p
SET reviews_received = 0
FROM bh_user u
WHERE p.user_id = u.id
AND u.id NOT IN (SELECT reviewee_id FROM bh_review WHERE visible = true AND deleted_at IS NULL)
AND u.slug IN ('angel-hq','ninos-campers','leonardos-bottega','sallys-kitchen','mikes-garage','marcos-workshop','pietros-drones','jakes-electronics','georges-villa','johns-cleaning','marias-garden','sofias-bakes','rosas-home','annes-qa-lab');

COMMIT;

-- Verification
SELECT u.display_name,
       p.reviews_received as points_count,
       (SELECT COUNT(*) FROM bh_review r WHERE r.reviewee_id = u.id AND r.visible = true) as actual_reviews,
       (SELECT ROUND(AVG(r.rating)::numeric, 1) FROM bh_review r WHERE r.reviewee_id = u.id) as avg_rating
FROM bh_user u
JOIN bh_user_points p ON p.user_id = u.id
WHERE u.slug IN ('angel-hq','ninos-campers','leonardos-bottega','sallys-kitchen','mikes-garage','marcos-workshop','pietros-drones','jakes-electronics','georges-villa','johns-cleaning','marias-garden','sofias-bakes','rosas-home','annes-qa-lab')
ORDER BY actual_reviews DESC;
