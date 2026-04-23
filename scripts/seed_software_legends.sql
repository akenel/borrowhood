-- Software Legends seed -- 6 profiles matching Leo's richness level.
-- Idempotent: each user/item skipped if slug already exists.
--
-- Run on UAT/prod:
--   docker exec -i postgres psql -U helix_user -d borrowhood < seed_software_legends.sql
--
-- Cleanup (if you ever want to undo):
--   DELETE FROM bh_user WHERE slug IN
--     ('antirezs-keybase','carmacks-inner-loop','dhhs-extraction-shop',
--      'linus-kernel-corner','bellards-quiet-forge','actons-sticky-note');
-- (cascades to items, media, listings, languages, skills, points.)

BEGIN;

-- ============================================================
-- 1. Salvatore Sanfilippo -- antirez (Redis, Catania IT)
-- ============================================================
INSERT INTO bh_user (id, keycloak_id, email, display_name, slug, bio, tagline,
                     workshop_name, workshop_type, telegram_username,
                     city, address, country_code, latitude, longitude,
                     date_of_birth, mother_name, father_name,
                     badge_tier, account_status, onboarding_completed,
                     offers_training, offers_custom_orders, offers_repair,
                     avatar_url, banner_url, created_at, updated_at)
SELECT gen_random_uuid(),
       'seed-antirez-' || gen_random_uuid()::text,
       'antirez@borrowhood.local',
       'Salvatore Sanfilippo',
       'antirezs-keybase',
       'Born in Catania, Sicily. Wrote Redis in a weekend in 2009 because my startup was bleeding throughput and I could not wait for someone else to fix it. 300 lines of C turned into one of the most-deployed databases on Earth. I stepped away in 2020 -- the code was done, it did not need me. I write now. Essays, mostly. About code, about retirement, about the difference between making a thing and being the thing. If you are Italian and you are coding alone in a kitchen at 2am, call me. I know the feeling.',
       '300 lines of C can change the backend.',
       'antirez''s Keybase', 'studio'::workshoptype,
       'antirez',
       'Catania', 'Via Etnea, Catania', 'IT', 37.5079, 15.0830,
       '1977-03-14', 'Ignazia Sanfilippo', 'Sebastiano Sanfilippo',
       'legend'::badgetier, 'ACTIVE'::accountstatus, true,
       true, true, false,
       'https://image.pollinations.ai/prompt/oil%20painting%20portrait%20italian%20programmer%20bearded%20glasses%20warm%20light%20sicily?width=400&height=400&nologo=true&seed=101',
       'https://image.pollinations.ai/prompt/catania%20etna%20volcano%20sunset%20sicily%20cityscape?width=1200&height=400&nologo=true&seed=102',
       NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM bh_user WHERE slug = 'antirezs-keybase');

-- Languages + skills + points + items for antirez
WITH u AS (SELECT id FROM bh_user WHERE slug = 'antirezs-keybase')
INSERT INTO bh_user_language (id, user_id, language_code, proficiency, created_at, updated_at)
SELECT gen_random_uuid(), u.id, lang, lvl::ceferlevel, NOW(), NOW()
FROM u, (VALUES ('it','native'), ('en','C2'), ('la','B1')) AS l(lang, lvl)
WHERE NOT EXISTS (SELECT 1 FROM bh_user_language WHERE user_id = u.id AND language_code = l.lang);

WITH u AS (SELECT id FROM bh_user WHERE slug = 'antirezs-keybase')
INSERT INTO bh_user_skill (id, user_id, skill_name, category, self_rating, years_experience, verified_by_count, created_at, updated_at)
SELECT gen_random_uuid(), u.id, sn, cat, rating, yrs, 0, NOW(), NOW()
FROM u, (VALUES
  ('C programming',       'engineering', 5, 30),
  ('Distributed systems', 'engineering', 5, 20),
  ('Technical writing',   'communication', 5, 20),
  ('Reading books on park benches', 'life', 5, 40)
) AS s(sn, cat, rating, yrs)
WHERE NOT EXISTS (SELECT 1 FROM bh_user_skill WHERE user_id = u.id AND skill_name = s.sn);

WITH u AS (SELECT id FROM bh_user WHERE slug = 'antirezs-keybase')
INSERT INTO bh_user_points (id, user_id, total_points, rentals_completed, reviews_given, reviews_received, items_listed, helpful_flags, created_at, updated_at)
SELECT gen_random_uuid(), u.id, 1600, 32, 25, 40, 3, 18, NOW(), NOW()
FROM u WHERE NOT EXISTS (SELECT 1 FROM bh_user_points WHERE user_id = u.id);

-- ============================================================
-- 2. John Carmack (Doom, Quake, Oculus)
-- ============================================================
INSERT INTO bh_user (id, keycloak_id, email, display_name, slug, bio, tagline,
                     workshop_name, workshop_type, telegram_username,
                     city, country_code, latitude, longitude,
                     date_of_birth, mother_name, father_name,
                     badge_tier, account_status, onboarding_completed,
                     offers_training, offers_custom_orders, offers_repair,
                     avatar_url, banner_url, created_at, updated_at)
SELECT gen_random_uuid(),
       'seed-carmack-' || gen_random_uuid()::text,
       'carmack@borrowhood.local',
       'John Carmack',
       'carmacks-inner-loop',
       'Kansas kid. Built my first game engine in high school. Founded id Software in 1991 with a handful of pizza-fueled programmers. Wrote Commander Keen, Wolfenstein 3D, Doom, Quake -- each one a little further into the 3D rabbit hole. The BSP tree idea in Doom came to me in bed at 2am. I spent two years tuning 30 lines of inner loop because on a 486, those 30 lines were the difference between 15 and 35 frames per second. Now I work on AI. Probably too much of it. The simple rule I keep forgetting and re-learning: ship it, then generalize. The thing nobody can ship is not a thing.',
       'Make the inner loop fast. Everything else follows.',
       'Carmack''s Inner Loop', 'studio'::workshoptype,
       NULL,
       'Plano, TX', 'US', 33.0198, -96.6989,
       '1970-08-20', 'Inga Mae Carmack', 'Stan Carmack',
       'legend'::badgetier, 'ACTIVE'::accountstatus, true,
       true, false, false,
       'https://image.pollinations.ai/prompt/oil%20painting%20portrait%20american%20programmer%20long%20hair%20glasses%20focused%20stare?width=400&height=400&nologo=true&seed=201',
       'https://image.pollinations.ai/prompt/retro%20crt%20monitors%20green%20phosphor%20code%20terminal%20programmer%20workshop?width=1200&height=400&nologo=true&seed=202',
       NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM bh_user WHERE slug = 'carmacks-inner-loop');

WITH u AS (SELECT id FROM bh_user WHERE slug = 'carmacks-inner-loop')
INSERT INTO bh_user_language (id, user_id, language_code, proficiency, created_at, updated_at)
SELECT gen_random_uuid(), u.id, lang, lvl::ceferlevel, NOW(), NOW()
FROM u, (VALUES ('en','native')) AS l(lang, lvl)
WHERE NOT EXISTS (SELECT 1 FROM bh_user_language WHERE user_id = u.id AND language_code = l.lang);

WITH u AS (SELECT id FROM bh_user WHERE slug = 'carmacks-inner-loop')
INSERT INTO bh_user_skill (id, user_id, skill_name, category, self_rating, years_experience, verified_by_count, created_at, updated_at)
SELECT gen_random_uuid(), u.id, sn, cat, 5, yrs, 0, NOW(), NOW()
FROM u, (VALUES
  ('3D graphics',         'engineering', 40),
  ('C / assembly tuning', 'engineering', 40),
  ('Rocketry',            'engineering', 20),
  ('Machine learning',    'engineering', 8)
) AS s(sn, cat, yrs)
WHERE NOT EXISTS (SELECT 1 FROM bh_user_skill WHERE user_id = u.id AND skill_name = s.sn);

WITH u AS (SELECT id FROM bh_user WHERE slug = 'carmacks-inner-loop')
INSERT INTO bh_user_points (id, user_id, total_points, rentals_completed, reviews_given, reviews_received, items_listed, helpful_flags, created_at, updated_at)
SELECT gen_random_uuid(), u.id, 1900, 20, 18, 52, 3, 30, NOW(), NOW()
FROM u WHERE NOT EXISTS (SELECT 1 FROM bh_user_points WHERE user_id = u.id);

-- ============================================================
-- 3. DHH - David Heinemeier Hansson (Rails, Basecamp)
-- ============================================================
INSERT INTO bh_user (id, keycloak_id, email, display_name, slug, bio, tagline,
                     workshop_name, workshop_type, telegram_username,
                     city, country_code, latitude, longitude,
                     date_of_birth, mother_name, father_name,
                     badge_tier, account_status, onboarding_completed,
                     offers_training, offers_custom_orders, offers_repair,
                     avatar_url, banner_url, created_at, updated_at)
SELECT gen_random_uuid(),
       'seed-dhh-' || gen_random_uuid()::text,
       'dhh@borrowhood.local',
       'David Heinemeier Hansson',
       'dhhs-extraction-shop',
       'Danish. Built Basecamp, then extracted Rails from it in 2004. That is the move: build a real product, notice the patterns, pull the framework out of the product. Do NOT sit down to build a framework. Shipped It Does Not Have to be Crazy at Work, Rework, Remote -- opinionated books that made a bunch of managers mad because they removed excuses. Race cars on weekends. Yell on the internet sometimes and regret it, sometimes do not. The principle I live by: convention over configuration. If you need to configure it, you probably have not decided yet.',
       'Extract from real use. Do not abstract from imagination.',
       'DHH''s Extraction Shop', 'studio'::workshoptype,
       'dhh',
       'Marbella', 'ES', 36.5099, -4.8860,
       '1979-10-15', 'Gerd Heinemeier', 'Ole Hansson',
       'legend'::badgetier, 'ACTIVE'::accountstatus, true,
       true, true, false,
       'https://image.pollinations.ai/prompt/oil%20painting%20portrait%20danish%20programmer%20black%20glasses%20confident%20smile%20mediterranean?width=400&height=400&nologo=true&seed=301',
       'https://image.pollinations.ai/prompt/le%20mans%20race%20car%20track%20afternoon%20sun%20stockholm?width=1200&height=400&nologo=true&seed=302',
       NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM bh_user WHERE slug = 'dhhs-extraction-shop');

WITH u AS (SELECT id FROM bh_user WHERE slug = 'dhhs-extraction-shop')
INSERT INTO bh_user_language (id, user_id, language_code, proficiency, created_at, updated_at)
SELECT gen_random_uuid(), u.id, lang, lvl::ceferlevel, NOW(), NOW()
FROM u, (VALUES ('da','native'), ('en','C2'), ('es','B2')) AS l(lang, lvl)
WHERE NOT EXISTS (SELECT 1 FROM bh_user_language WHERE user_id = u.id AND language_code = l.lang);

WITH u AS (SELECT id FROM bh_user WHERE slug = 'dhhs-extraction-shop')
INSERT INTO bh_user_skill (id, user_id, skill_name, category, self_rating, years_experience, verified_by_count, created_at, updated_at)
SELECT gen_random_uuid(), u.id, sn, cat, 5, yrs, 0, NOW(), NOW()
FROM u, (VALUES
  ('Ruby on Rails',        'engineering', 20),
  ('Writing opinionated books', 'communication', 15),
  ('Le Mans racing',       'sports', 12),
  ('Calling out nonsense', 'communication', 25)
) AS s(sn, cat, yrs)
WHERE NOT EXISTS (SELECT 1 FROM bh_user_skill WHERE user_id = u.id AND skill_name = s.sn);

WITH u AS (SELECT id FROM bh_user WHERE slug = 'dhhs-extraction-shop')
INSERT INTO bh_user_points (id, user_id, total_points, rentals_completed, reviews_given, reviews_received, items_listed, helpful_flags, created_at, updated_at)
SELECT gen_random_uuid(), u.id, 1750, 28, 35, 48, 3, 25, NOW(), NOW()
FROM u WHERE NOT EXISTS (SELECT 1 FROM bh_user_points WHERE user_id = u.id);

-- ============================================================
-- 4. Linus Torvalds (Linux, Git)
-- ============================================================
INSERT INTO bh_user (id, keycloak_id, email, display_name, slug, bio, tagline,
                     workshop_name, workshop_type, telegram_username,
                     city, country_code, latitude, longitude,
                     date_of_birth, mother_name, father_name,
                     badge_tier, account_status, onboarding_completed,
                     offers_training, offers_custom_orders, offers_repair,
                     avatar_url, banner_url, created_at, updated_at)
SELECT gen_random_uuid(),
       'seed-linus-' || gen_random_uuid()::text,
       'linus@borrowhood.local',
       'Linus Torvalds',
       'linus-kernel-corner',
       'Finnish kid. Wrote a little kernel in 1991 because Minix was not free. Did not plan to run the world''s compute infrastructure. That just happened. Wrote Git in ten days in 2005 because BitKeeper revoked our license -- I needed source control, and I picked the primitive I wanted: a content-addressable file system, not a diff engine. The primitive turned out to be right. That is most of what picking the right primitive early gets you: twenty years of people still using your thing. I have been an asshole to contributors. I stepped back in 2018 and got therapy. I am working on being better. The code can be right and the person can be wrong -- both are real.',
       'Good taste is knowing which special case is not special.',
       'Linus''s Kernel Corner', 'studio'::workshoptype,
       NULL,
       'Portland, OR', 'US', 45.5152, -122.6784,
       '1969-12-28', 'Anna Torvalds', 'Nils Torvalds',
       'legend'::badgetier, 'ACTIVE'::accountstatus, true,
       true, false, true,
       'https://image.pollinations.ai/prompt/oil%20painting%20portrait%20finnish%20programmer%20round%20glasses%20thoughtful%20gray%20hair?width=400&height=400&nologo=true&seed=401',
       'https://image.pollinations.ai/prompt/oregon%20forest%20pine%20trees%20overcast%20cabin%20warm%20light?width=1200&height=400&nologo=true&seed=402',
       NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM bh_user WHERE slug = 'linus-kernel-corner');

WITH u AS (SELECT id FROM bh_user WHERE slug = 'linus-kernel-corner')
INSERT INTO bh_user_language (id, user_id, language_code, proficiency, created_at, updated_at)
SELECT gen_random_uuid(), u.id, lang, lvl::ceferlevel, NOW(), NOW()
FROM u, (VALUES ('fi','native'), ('sv','C1'), ('en','C2')) AS l(lang, lvl)
WHERE NOT EXISTS (SELECT 1 FROM bh_user_language WHERE user_id = u.id AND language_code = l.lang);

WITH u AS (SELECT id FROM bh_user WHERE slug = 'linus-kernel-corner')
INSERT INTO bh_user_skill (id, user_id, skill_name, category, self_rating, years_experience, verified_by_count, created_at, updated_at)
SELECT gen_random_uuid(), u.id, sn, cat, 5, yrs, 0, NOW(), NOW()
FROM u, (VALUES
  ('Linux kernel',         'engineering', 33),
  ('Distributed version control', 'engineering', 20),
  ('Picking the right primitive', 'engineering', 30),
  ('Scuba diving',         'sports', 15)
) AS s(sn, cat, yrs)
WHERE NOT EXISTS (SELECT 1 FROM bh_user_skill WHERE user_id = u.id AND skill_name = s.sn);

WITH u AS (SELECT id FROM bh_user WHERE slug = 'linus-kernel-corner')
INSERT INTO bh_user_points (id, user_id, total_points, rentals_completed, reviews_given, reviews_received, items_listed, helpful_flags, created_at, updated_at)
SELECT gen_random_uuid(), u.id, 2000, 15, 12, 80, 3, 45, NOW(), NOW()
FROM u WHERE NOT EXISTS (SELECT 1 FROM bh_user_points WHERE user_id = u.id);

-- ============================================================
-- 5. Fabrice Bellard (FFmpeg, QEMU, TinyCC, JSLinux)
-- ============================================================
INSERT INTO bh_user (id, keycloak_id, email, display_name, slug, bio, tagline,
                     workshop_name, workshop_type, telegram_username,
                     city, country_code, latitude, longitude,
                     date_of_birth, mother_name, father_name,
                     badge_tier, account_status, onboarding_completed,
                     offers_training, offers_custom_orders, offers_repair,
                     avatar_url, banner_url, created_at, updated_at)
SELECT gen_random_uuid(),
       'seed-bellard-' || gen_random_uuid()::text,
       'bellard@borrowhood.local',
       'Fabrice Bellard',
       'bellards-quiet-forge',
       'French. I wrote FFmpeg in 2000 because I wanted to play with video codecs. It turned out to be the thing that runs every video on the internet. I wrote QEMU in 2003 because I wanted to understand how CPUs really work. It turned out to be how we run every virtual machine. I wrote TinyCC (a 300KB C compiler) and JSLinux (a Linux that runs in your browser tab) because I was bored one weekend. I do not want to be famous. I do not want to sell companies. I want to pick problems that compound forever and then work on them quietly. The world needs more quiet forges.',
       'Pick problems that compound. Then pick one.',
       'Bellard''s Quiet Forge', 'studio'::workshoptype,
       NULL,
       'Paris', 'FR', 48.8566, 2.3522,
       '1972-05-17', 'Madeleine Bellard', 'Pierre Bellard',
       'legend'::badgetier, 'ACTIVE'::accountstatus, true,
       true, false, false,
       'https://image.pollinations.ai/prompt/oil%20painting%20portrait%20french%20programmer%20short%20hair%20quiet%20intensity%20library%20background?width=400&height=400&nologo=true&seed=501',
       'https://image.pollinations.ai/prompt/paris%20bookshelf%20old%20books%20desk%20green%20lamp%20warm%20quiet?width=1200&height=400&nologo=true&seed=502',
       NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM bh_user WHERE slug = 'bellards-quiet-forge');

WITH u AS (SELECT id FROM bh_user WHERE slug = 'bellards-quiet-forge')
INSERT INTO bh_user_language (id, user_id, language_code, proficiency, created_at, updated_at)
SELECT gen_random_uuid(), u.id, lang, lvl::ceferlevel, NOW(), NOW()
FROM u, (VALUES ('fr','native'), ('en','C2')) AS l(lang, lvl)
WHERE NOT EXISTS (SELECT 1 FROM bh_user_language WHERE user_id = u.id AND language_code = l.lang);

WITH u AS (SELECT id FROM bh_user WHERE slug = 'bellards-quiet-forge')
INSERT INTO bh_user_skill (id, user_id, skill_name, category, self_rating, years_experience, verified_by_count, created_at, updated_at)
SELECT gen_random_uuid(), u.id, sn, cat, 5, yrs, 0, NOW(), NOW()
FROM u, (VALUES
  ('Video codecs',         'engineering', 25),
  ('CPU emulation',        'engineering', 20),
  ('Compiler design',      'engineering', 28),
  ('Pi computation records', 'engineering', 15)
) AS s(sn, cat, yrs)
WHERE NOT EXISTS (SELECT 1 FROM bh_user_skill WHERE user_id = u.id AND skill_name = s.sn);

WITH u AS (SELECT id FROM bh_user WHERE slug = 'bellards-quiet-forge')
INSERT INTO bh_user_points (id, user_id, total_points, rentals_completed, reviews_given, reviews_received, items_listed, helpful_flags, created_at, updated_at)
SELECT gen_random_uuid(), u.id, 1850, 12, 8, 35, 3, 22, NOW(), NOW()
FROM u WHERE NOT EXISTS (SELECT 1 FROM bh_user_points WHERE user_id = u.id);

-- ============================================================
-- 6. Brian Acton (WhatsApp, Signal)
-- ============================================================
INSERT INTO bh_user (id, keycloak_id, email, display_name, slug, bio, tagline,
                     workshop_name, workshop_type, telegram_username,
                     city, country_code, latitude, longitude,
                     date_of_birth, mother_name, father_name,
                     badge_tier, account_status, onboarding_completed,
                     offers_training, offers_custom_orders, offers_repair,
                     avatar_url, banner_url, created_at, updated_at)
SELECT gen_random_uuid(),
       'seed-acton-' || gen_random_uuid()::text,
       'acton@borrowhood.local',
       'Brian Acton',
       'actons-sticky-note',
       'American. Yahoo engineer for twelve years. Co-founded WhatsApp with Jan Koum in 2009 after we both got rejected from Facebook and Twitter. Wrote one rule on a sticky note next to the desk: "No Ads. No Games. No Gimmicks." Ran the whole thing on that rule. Fifty engineers, four hundred and fifty million users. Sold to Facebook in 2014 for nineteen billion dollars and watched them violate every sentence of the sticky note one by one. Walked away in 2017. Used the payout to fund Signal -- encrypted messaging with no ads, no corporate owner, just the rule. Lesson I keep: the values you bake in get unbaked when someone else owns the code.',
       'No Ads. No Games. No Gimmicks.',
       'Acton''s Sticky Note', 'studio'::workshoptype,
       NULL,
       'Palo Alto, CA', 'US', 37.4419, -122.1430,
       '1972-02-17', 'Pamela Acton', 'Robert Acton',
       'legend'::badgetier, 'ACTIVE'::accountstatus, true,
       true, false, false,
       'https://image.pollinations.ai/prompt/oil%20painting%20portrait%20american%20software%20engineer%20beard%20silver%20hair%20quiet%20california?width=400&height=400&nologo=true&seed=601',
       'https://image.pollinations.ai/prompt/sticky%20note%20desk%20no%20ads%20no%20games%20no%20gimmicks%20handwritten?width=1200&height=400&nologo=true&seed=602',
       NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM bh_user WHERE slug = 'actons-sticky-note');

WITH u AS (SELECT id FROM bh_user WHERE slug = 'actons-sticky-note')
INSERT INTO bh_user_language (id, user_id, language_code, proficiency, created_at, updated_at)
SELECT gen_random_uuid(), u.id, lang, lvl::ceferlevel, NOW(), NOW()
FROM u, (VALUES ('en','native')) AS l(lang, lvl)
WHERE NOT EXISTS (SELECT 1 FROM bh_user_language WHERE user_id = u.id AND language_code = l.lang);

WITH u AS (SELECT id FROM bh_user WHERE slug = 'actons-sticky-note')
INSERT INTO bh_user_skill (id, user_id, skill_name, category, self_rating, years_experience, verified_by_count, created_at, updated_at)
SELECT gen_random_uuid(), u.id, sn, cat, 5, yrs, 0, NOW(), NOW()
FROM u, (VALUES
  ('Scaling messaging systems', 'engineering', 20),
  ('Protecting values under pressure', 'leadership', 25),
  ('Saying no to bad money', 'leadership', 20),
  ('Ultimate frisbee',       'sports', 30)
) AS s(sn, cat, yrs)
WHERE NOT EXISTS (SELECT 1 FROM bh_user_skill WHERE user_id = u.id AND skill_name = s.sn);

WITH u AS (SELECT id FROM bh_user WHERE slug = 'actons-sticky-note')
INSERT INTO bh_user_points (id, user_id, total_points, rentals_completed, reviews_given, reviews_received, items_listed, helpful_flags, created_at, updated_at)
SELECT gen_random_uuid(), u.id, 1700, 18, 22, 40, 3, 28, NOW(), NOW()
FROM u WHERE NOT EXISTS (SELECT 1 FROM bh_user_points WHERE user_id = u.id);

-- ============================================================
-- Items (3 per legend = 18 total). Reusable seed function pattern.
-- ============================================================
-- Each item: insert bh_item, bh_item_media (Pollinations), bh_listing.

DO $$
DECLARE
  r RECORD;
  item_id UUID;
BEGIN
  FOR r IN
    -- (owner_slug, item_slug, name, category, description, story, tags, listing_type, price, price_unit, img_prompt_seed, img_prompt)
    SELECT * FROM (VALUES
      -- antirez
      ('antirezs-keybase', 'redis-internals-bootcamp', 'Redis Internals Bootcamp -- 4 sessions',
       'tools_services', 'Four 90-minute sessions. We read Redis source together -- event loop, key expiration, the AOF. You walk away able to find a memory leak in anybody''s C code. Bring a laptop and a kitchen light.',
       'I wish I had this when I was 22. So I made it.', 'redis, c, database, systems, internals',
       'TRAINING', 20.00, 'per_session', 111, 'terminal%20with%20redis%20code%20warm%20light%20espresso%20cup'),
      ('antirezs-keybase', 'hackers-delight-annotated', 'Hacker''s Delight (annotated -- my margin notes)',
       'books_media', 'My personal copy of Hacker''s Delight by Henry S. Warren Jr. Every bit-twiddling trick I ever used came from here. My margins are covered in Italian swear words where a theorem surprised me. Handle carefully.',
       'A book teaches you a technique. A book with another engineer''s annotations teaches you a mind.', 'book, algorithms, bits, programming',
       'RENT', 3.00, 'per_day', 112, 'old%20annotated%20programming%20book%20pencil%20notes%20warm%20library'),
      ('antirezs-keybase', 'solo-hacker-setup-tour', 'Solo-Hacker Setup Tour -- Vim + tmux + why I never used an IDE',
       'tools_services', 'One hour. I show you my 2009 editor config. We argue about keybindings. You leave with a setup that lets you ship features without your hands ever leaving the home row.',
       'The tool shapes the hand. Pick tools that fit your hand.', 'vim, tmux, linux, productivity',
       'SERVICE', 15.00, 'per_session', 113, 'vim%20terminal%20keyboard%20tmux%20panes%20warm%20night%20cafe'),
      -- carmack
      ('carmacks-inner-loop', 'quake-engine-tour', 'Quake Engine Source Tour -- 2 hours, commented',
       'tools_services', 'We walk through the Quake engine line by line. BSP trees, visibility, collision, the network code. You will see why the game shipped on a Pentium 75 and still looked like magic.',
       'If you want to understand 3D graphics, read the code that invented them.', 'game engine, 3d, c, carmack, optimization',
       'SERVICE', 40.00, 'per_session', 211, 'quake%20green%20monster%20crt%20screen%20coding%20dark%20room'),
      ('carmacks-inner-loop', 'paul-sellers-hand-plane', 'Paul Sellers Hand Plane (no power tools allowed)',
       'power_tools', 'No, it is not a power tool. It is a Stanley #4 bench plane that has made three dining tables. Paul Sellers convinced me that quiet work is better. Sharpening whetstone included. I will show you how to rock the plane on pickup.',
       'Turns out the same focus that ships a rendering engine also flattens a board.', 'woodworking, hand tool, plane, stanley',
       'RENT', 5.00, 'per_day', 212, 'vintage%20stanley%20hand%20plane%20wood%20shavings%20workshop%20warm%20light'),
      ('carmacks-inner-loop', 'inner-loop-consult', 'Inner-Loop Consult -- I make your hot path fast',
       'tools_services', 'One hour on a video call. You show me your profiler output. I tell you what 30 lines to rewrite. Works for graphics, numerics, sim, game loops. Does NOT work for web backends -- that is a different sport.',
       'The hot path is 3 percent of your code and 97 percent of your wall clock. Fix the 3 percent.', 'performance, optimization, c, gpu, consulting',
       'SERVICE', 50.00, 'per_session', 213, 'flame%20graph%20profiler%20screen%20code%20terminal%20dark%20workshop'),
      -- dhh
      ('dhhs-extraction-shop', 'extraction-workshop', 'Framework Extraction Workshop -- pull a library out of your real app',
       'tools_services', 'Three sessions. Bring a real codebase. We find the patterns worth extracting, pull them into a gem, and ship both the product AND the library. The Basecamp-to-Rails move, but on your code.',
       'You can''t abstract something you''ve never built. Build it. Then pull out what repeats.', 'ruby, rails, architecture, extraction, libraries',
       'TRAINING', 25.00, 'per_session', 311, 'ruby%20rails%20code%20editor%20orange%20gem%20logo%20warm%20workshop'),
      ('dhhs-extraction-shop', 'rework-signed', 'Rework -- signed, scribbled in',
       'books_media', 'My own working copy of Rework (2010). I wrote it with Jason. The margin notes are my regrets and upgrades -- things we''d change ten years on. Read them before you argue with the book.',
       'A book is the beginning of a conversation, not the end of one.', 'book, business, rework, signed',
       'RENT', 2.00, 'per_day', 312, 'signed%20book%20rework%20desk%20coffee%20warm%20light'),
      ('dhhs-extraction-shop', 'rails-code-review', 'Rails Code Review -- I will tell you the truth',
       'tools_services', 'One hour. Push a branch, walk through it with me. I will be honest. Some people cry. Some people ship better code the next day. Most do both.',
       'Convention over configuration is not a rule. It is an apology for your future self.', 'ruby, rails, code review, mentorship',
       'SERVICE', 30.00, 'per_session', 313, 'ruby%20code%20review%20pair%20programming%20warm%20screen'),
      -- linus
      ('linus-kernel-corner', 'git-first-principles', 'Git From First Principles -- it is just a content-addressable filesystem',
       'tools_services', 'Two hours. We rebuild Git from scratch: blobs, trees, commits, refs. By the end you will stop being scared of rebase and merge and know what a detached HEAD actually is.',
       'I wrote it in ten days. You can understand it in two hours.', 'git, version control, cli, systems',
       'TRAINING', 20.00, 'per_session', 411, 'git%20branch%20graph%20terminal%20tree%20structure%20dark'),
      ('linus-kernel-corner', 'kernel-patch-review-free', 'Kernel Patch Review -- free, and I promise to be kind',
       'tools_services', 'Email me your kernel patch. I will review it. I owe the community this one. You get honest feedback. Free. You do not even have to say thank you. But it will be kind -- that is the deal I made in 2018 and I am keeping it.',
       'Good code review is a gift. I was bad at it for years. I am getting better.', 'linux, kernel, code review, open source',
       'GIVEAWAY', NULL, 'flat', 412, 'linux%20penguin%20tux%20code%20terminal%20finnish%20forest'),
      ('linus-kernel-corner', 'old-xps-13-linux', 'Old Dell XPS 13 -- my personal patch set, arch installed',
       'electronics', 'My retired 2017 XPS 13. Arch, kernel 6.8 with my own patch set, suspend works, webcam works, trackpad is set up the way I like it. Boots in 3 seconds. If you want to see how I use a computer, borrow this for a weekend.',
       'A tool shaped by years of use has more to teach than a tool just bought.', 'laptop, linux, arch, dell, xps',
       'RENT', 8.00, 'per_day', 413, 'dell%20xps%20laptop%20linux%20terminal%20arch%20desk%20night'),
      -- bellard
      ('bellards-quiet-forge', 'ffmpeg-from-scratch', 'FFmpeg From Scratch -- 2 hours, from fopen to H.264',
       'tools_services', 'We read the original FFmpeg source. I walk you through the demuxer, the codec, the filter graph, and the mux. By the end you will understand why every video on the internet passes through this code.',
       'I wrote it because I wanted to understand video. It turned out everyone wanted to understand it.', 'ffmpeg, video, codec, c, systems',
       'TRAINING', 15.00, 'per_session', 511, 'ffmpeg%20command%20line%20video%20pipeline%20colors%20terminal'),
      ('bellards-quiet-forge', 'qemu-emulator-tour', 'QEMU Emulator Tour -- How I Emulated x86 in C',
       'tools_services', 'One session. The dynamic translator, the TCG, the device model, the memory map. After this you will know how VMs actually work, not just how to run one.',
       'Emulation is understanding reduced to code. If you can emulate it you understand it.', 'qemu, emulation, vm, x86, c',
       'SERVICE', 20.00, 'per_session', 512, 'qemu%20virtual%20machine%20cpu%20diagram%20terminal%20dark'),
      ('bellards-quiet-forge', 'tinycc-source', 'TinyCC Source Bundle -- a 300KB C compiler',
       'tools_services', 'The TinyCC source bundled with my notes on why each module is structured the way it is. Free. Read it. Learn. Compile it. Fork it. Do not thank me.',
       'Small enough to understand. Useful enough to matter. The sweet spot.', 'compiler, c, tinycc, source, free',
       'GIVEAWAY', NULL, 'flat', 513, 'source%20code%20tinycc%20c%20compiler%20listing%20warm%20terminal'),
      -- acton
      ('actons-sticky-note', 'messenger-scale-talk', 'Scaling a Messenger to 450M Users with 50 Engineers',
       'tools_services', 'One-hour talk. What we did. What we did NOT do (hint: most of it). Erlang decisions, database decisions, the sticky note. Also: how I said no to ads for five years.',
       'A small team that says no twenty times a day ships better than a big team that says yes.', 'scaling, architecture, erlang, messaging',
       'TRAINING', 30.00, 'per_session', 611, 'whatsapp%20servers%20erlang%20code%20minimalist%20setup'),
      ('actons-sticky-note', 'original-sticky-note', 'The Original No Ads Sticky Note (framed)',
       'art_decor', 'The literal sticky note. Yellow, faded, my handwriting. "No Ads. No Games. No Gimmicks." Framed in a simple black frame. Borrowable for a week so you can put it on your own desk and remember.',
       'A promise on paper outlives a promise in a slide deck.', 'sticky note, framed, values, no ads',
       'RENT', 5.00, 'per_day', 612, 'yellow%20sticky%20note%20handwritten%20no%20ads%20no%20games%20no%20gimmicks%20black%20frame'),
      ('actons-sticky-note', 'signal-strategy-consult', 'Signal Strategy Consult -- free, just fund Signal instead',
       'tools_services', 'One hour. Bring your encrypted-messaging question. I will not charge you. If you can, donate the fee to the Signal Foundation. That was the whole point of the second act.',
       'If you can fix the thing you regret, you are lucky. Fix it.', 'signal, messaging, encryption, foundation, strategy',
       'GIVEAWAY', NULL, 'flat', 613, 'signal%20app%20logo%20blue%20encrypted%20messenger%20minimalist')
    ) AS t(owner_slug, item_slug, name, category, description, story, tags, listing_type, price, price_unit, img_seed, img_prompt)
  LOOP
    -- Skip if item already exists
    IF NOT EXISTS (SELECT 1 FROM bh_item WHERE slug = r.item_slug) THEN
      INSERT INTO bh_item (id, owner_id, name, slug, description, story, content_language,
                           item_type, category, condition, tags, latitude, longitude, created_at, updated_at)
      SELECT gen_random_uuid(), u.id, r.name, r.item_slug, r.description, r.story, 'en',
             CASE WHEN r.listing_type IN ('TRAINING','SERVICE','GIVEAWAY') THEN 'SERVICE' ELSE 'PHYSICAL' END::itemtype,
             r.category, 'GOOD'::itemcondition, r.tags,
             u.latitude, u.longitude, NOW(), NOW()
      FROM bh_user u WHERE u.slug = r.owner_slug
      RETURNING id INTO item_id;

      -- Image
      INSERT INTO bh_item_media (id, item_id, url, alt_text, media_type, sort_order, created_at, updated_at)
      VALUES (gen_random_uuid(), item_id,
              'https://image.pollinations.ai/prompt/' || r.img_prompt || '?width=800&height=600&nologo=true&seed=' || r.img_seed,
              r.name, 'PHOTO'::mediatype, 0, NOW(), NOW());

      -- Listing
      INSERT INTO bh_listing (id, item_id, listing_type, status, price, price_unit, currency,
                              deposit, delivery_available, pickup_only, version, created_at, updated_at)
      VALUES (gen_random_uuid(), item_id, r.listing_type::listingtype, 'ACTIVE'::listingstatus,
              r.price, r.price_unit, 'EUR', NULL, false, true, 1, NOW(), NOW());
    END IF;
  END LOOP;
END $$;

-- Summary
SELECT u.slug, u.display_name, u.tagline,
       (SELECT COUNT(*) FROM bh_item WHERE owner_id = u.id) AS items
FROM bh_user u
WHERE u.slug IN ('antirezs-keybase','carmacks-inner-loop','dhhs-extraction-shop',
                 'linus-kernel-corner','bellards-quiet-forge','actons-sticky-note')
ORDER BY u.display_name;

COMMIT;
