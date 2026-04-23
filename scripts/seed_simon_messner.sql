-- Seed Simon White Di Vinti (existing user update) + Reinhold Messner (new demo user).
-- Idempotent via upserts / WHERE NOT EXISTS.

BEGIN;

-- ============================================================
-- 1. SIMON WHITE DI VINTI
-- Real user who just joined. Update profile fields.
-- ============================================================

UPDATE bh_user SET
    display_name = 'Simon White',
    slug = 'simon-white',
    workshop_name = 'White Hammer',
    workshop_type = 'DOJO'::workshoptype,
    tagline = 'Radiologist by day. Boxer before dawn. Christian, traveled, here to give back.',
    bio = 'I am 36. I read scans for a living -- traded heart surgery for the steady rhythm of the reading room. Twelve years in the ring, four mornings a week on the bag. I travel when I can: Greece, Germany, the Alps. Italian is home, German earned me Bavaria, English opens the rest of the world. Christian, spiritual, quiet about it. I live in Enna. If you want to learn to box, I will teach you -- especially kids. Boxing is how you become a man without becoming a monster.',
    avatar_url = '/static/uploads/avatars/simon-white-v2-54b77242.jpg',
    banner_url = 'https://image.pollinations.ai/prompt/boxing%20gym%20heavy%20bag%20golden%20hour%20sicilian%20gym%20wide%20cinematic?width=1600&height=500&nologo=true',
    city = 'Enna',
    country_code = 'IT',
    latitude = 37.566181,
    longitude = 14.277832,
    offers_training = true,
    offers_custom_orders = false,
    offers_repair = false,
    date_of_birth = '1989-03-15',
    mother_name = 'Angela White',
    updated_at = NOW()
WHERE email = 'simon.divinti3@gmail.com';

-- Languages (remove any existing, then re-insert clean set)
DELETE FROM bh_user_language WHERE user_id = (SELECT id FROM bh_user WHERE email = 'simon.divinti3@gmail.com');
INSERT INTO bh_user_language (id, user_id, language_code, proficiency, created_at, updated_at)
SELECT gen_random_uuid(), u.id, lang, level::cefrlevel, NOW(), NOW()
FROM bh_user u,
     (VALUES ('it', 'NATIVE'), ('en', 'B2'), ('de', 'C1')) AS langs(lang, level)
WHERE u.email = 'simon.divinti3@gmail.com';

-- Skills (clear + insert)
DELETE FROM bh_user_skill WHERE user_id = (SELECT id FROM bh_user WHERE email = 'simon.divinti3@gmail.com');
INSERT INTO bh_user_skill (id, user_id, skill_name, category, self_rating, verified_by_count, years_experience, created_at, updated_at)
SELECT gen_random_uuid(), u.id, sk.name, sk.cat, sk.rating, 0, sk.yrs, NOW(), NOW()
FROM bh_user u,
     (VALUES
        ('Boxing (featherweight)', 'sports', 5, 12),
        ('Coaching kids + teens', 'sports', 4, 3),
        ('Radiology',             'services', 5, 10),
        ('Italian translation',   'creative', 5, 20),
        ('German conversation',   'creative', 4, 8)
     ) AS sk(name, cat, rating, yrs)
WHERE u.email = 'simon.divinti3@gmail.com';

-- Clean up any old items tied to this user (dev-mode reset, not prod-safe for real data)
DELETE FROM bh_item_media WHERE item_id IN (SELECT id FROM bh_item WHERE owner_id = (SELECT id FROM bh_user WHERE email = 'simon.divinti3@gmail.com') AND slug LIKE 'white-hammer-%');
DELETE FROM bh_listing    WHERE item_id IN (SELECT id FROM bh_item WHERE owner_id = (SELECT id FROM bh_user WHERE email = 'simon.divinti3@gmail.com') AND slug LIKE 'white-hammer-%');
DELETE FROM bh_item       WHERE owner_id = (SELECT id FROM bh_user WHERE email = 'simon.divinti3@gmail.com') AND slug LIKE 'white-hammer-%';

-- Items + listings for Simon
WITH simon AS (SELECT id FROM bh_user WHERE email = 'simon.divinti3@gmail.com'),
     seed(slug, name, item_type, category, description, story, tags, listing_type, price, price_unit, deposit, img_prompt, max_participants) AS (
     VALUES
     -- 1. Rent: boxing pads + gloves
     ('white-hammer-boxing-pad-kit',
      'Boxing Pad & Glove Kit -- rent by the hour',
      'PHYSICAL', 'sports_event',
      'Pair of focus mitts, 14oz gloves, hand wraps. Everything cleaned after each use. Rent by the hour for home sessions or a friend.',
      'Good pads last 3 years if you care for them. Mine are 2 years in and still true.',
      'boxing, gloves, pads, rent, training',
      'RENT', 8.00, 'per_hour', 30.00,
      'boxing focus mitts and gloves worn leather warm light gym',
      NULL),

     -- 2. Service: private coaching
     ('white-hammer-private-coaching',
      'Private Boxing Coaching -- 1-on-1',
      'SERVICE', 'training_service',
      'One hour of proper technique. Stance, footwork, combinations, defense. For adults of any level, kids by arrangement. Enna area.',
      'I was taught right. I teach right. No ego, no gimmicks.',
      'coaching, boxing, private, enna, 1-on-1',
      'SERVICE', 30.00, 'per_hour', NULL,
      'boxing trainer coach holding pads sparring sicilian gym morning',
      1),

     -- 3. Training: 6-week fighters foundation
     ('white-hammer-fighters-foundation',
      'Fighter''s Foundation -- 6 weeks for teens 12-17',
      'SERVICE', 'training_service',
      'Twelve sessions over six weeks. Stance, jab, cross, hook, footwork, defense. Community price to keep it accessible. Parents meet me first.',
      'I started at 24. Wish I had started at 14. Helping kids skip ten years of bad habits.',
      'training, teens, boxing, community, youth, enna',
      'TRAINING', 10.00, 'per_session', NULL,
      'teenage boy hitting boxing bag focused coach watching warm gym',
      8),

     -- 4. Giveaway: free intro + gum shield
     ('white-hammer-free-intro-and-gum-shield',
      'Free "Is this for you?" session + gum shield -- first 20 kids',
      'SERVICE', 'training_service',
      'One hour free. I''ll teach you the basics and give you a gum shield to keep. For kids 12-17 from Enna and nearby. Text me through La Piazza.',
      'Twenty free sessions, twenty gum shields. If boxing is for you, you''ll know in an hour.',
      'free, giveaway, kids, intro, boxing, enna',
      'GIVEAWAY', NULL, 'flat', NULL,
      'kid trying on boxing glove first time smile quiet sicilian gym',
      20),

     -- 5. Raffle: 1 private coaching session (EUR 1 x 10 tickets = EUR 10 pot, newcomer-tier cap)
     ('white-hammer-coaching-raffle',
      'Raffle: 1 Private Coaching Session',
      'SERVICE', 'training_service',
      'One hour private coaching. EUR 1 ticket, 10 tickets total, draw in 2 weeks. Proceeds go back into gear for the community youth program.',
      'Raffling what I do. Simple.',
      'raffle, coaching, boxing, community, enna',
      'RAFFLE', 1.00, 'flat', NULL,
      'boxing gloves hanging raffle tickets warm gym sicilian',
      10)
     ),
     inserted AS (
         INSERT INTO bh_item (id, owner_id, name, slug, description, story, content_language,
                              item_type, category, condition, tags, latitude, longitude, created_at, updated_at)
         SELECT gen_random_uuid(), simon.id, s.name, s.slug, s.description, s.story, 'en',
                s.item_type::itemtype, s.category, 'GOOD'::itemcondition, s.tags,
                37.566181, 14.277832, NOW(), NOW()
         FROM seed s, simon
         RETURNING id, slug
     ),
     _ AS (
         INSERT INTO bh_item_media (id, item_id, url, alt_text, media_type, sort_order, created_at, updated_at)
         SELECT gen_random_uuid(), ii.id,
                'https://image.pollinations.ai/prompt/' || REPLACE(REPLACE(s.img_prompt, ' ', '%20'), ',', '%2C') || '?width=800&height=600&nologo=true',
                s.name, 'PHOTO'::mediatype, 0, NOW(), NOW()
         FROM inserted ii JOIN seed s ON s.slug = ii.slug
         RETURNING 1
     )
     INSERT INTO bh_listing (id, item_id, listing_type, status, price, price_unit, currency,
                             deposit, delivery_available, pickup_only, max_participants, version, created_at, updated_at)
     SELECT gen_random_uuid(), ii.id, s.listing_type::listingtype, 'ACTIVE'::listingstatus,
            s.price, s.price_unit, 'EUR', s.deposit, false, true, s.max_participants, 1, NOW(), NOW()
     FROM inserted ii JOIN seed s ON s.slug = ii.slug;

-- Event for Simon: Guantoni in Piazza at Università Kore, Enna, next Saturday evening
WITH simon AS (SELECT id FROM bh_user WHERE email = 'simon.divinti3@gmail.com'),
     existing AS (SELECT id FROM bh_item WHERE slug = 'white-hammer-guantoni-in-piazza'),
     inserted_item AS (
         INSERT INTO bh_item (id, owner_id, name, slug, description, story, content_language,
                              item_type, category, condition, tags, latitude, longitude, created_at, updated_at)
         SELECT gen_random_uuid(), simon.id,
                'Guantoni in Piazza -- Boxing Intro at Università Kore',
                'white-hammer-guantoni-in-piazza',
                'Two hours outdoors. Fifteen minutes of warm-up, thirty minutes of basics (stance, jab, guard), then sparring demo with a friend. Free. Bring a water bottle and something to sit on for the warm-down.',
                'I wanted to meet the neighborhood. What better way than the thing I know?',
                'en',
                'SERVICE'::itemtype, 'community_meetup',
                'GOOD'::itemcondition, 'event, boxing, free, enna, community',
                37.571994, 14.262167, NOW(), NOW()
         FROM simon
         WHERE NOT EXISTS (SELECT 1 FROM existing)
         RETURNING id
     ),
     _img AS (
         INSERT INTO bh_item_media (id, item_id, url, alt_text, media_type, sort_order, created_at, updated_at)
         SELECT gen_random_uuid(), ii.id,
                'https://image.pollinations.ai/prompt/outdoor%20boxing%20training%20sunset%20university%20campus%20enna%20sicily?width=800&height=600&nologo=true',
                'Boxing intro outdoors', 'PHOTO'::mediatype, 0, NOW(), NOW()
         FROM inserted_item ii
         RETURNING 1
     )
     INSERT INTO bh_listing (id, item_id, listing_type, status, price, price_unit, currency,
                             deposit, delivery_available, pickup_only, max_participants, version,
                             event_start, event_end, event_venue, event_address, created_at, updated_at)
     SELECT gen_random_uuid(), ii.id, 'EVENT'::listingtype, 'ACTIVE'::listingstatus,
            NULL, 'flat', 'EUR', NULL, false, true, 20, 1,
            (NOW() + INTERVAL '3 days')::date + TIME '18:00:00',
            (NOW() + INTERVAL '3 days')::date + TIME '20:00:00',
            'Università degli Studi di Enna Kore -- Campus outdoor',
            'Cittadella Universitaria, 94100 Enna EN',
            NOW(), NOW()
     FROM inserted_item ii;


-- ============================================================
-- 2. REINHOLD MESSNER -- new demo user
-- Mountain legend, first to summit all 14 8000ers solo+no-O2.
-- ============================================================

-- Create user (skip if already exists)
INSERT INTO bh_user (
    id, keycloak_id, email, display_name, slug,
    workshop_name, workshop_type, tagline, bio, avatar_url, banner_url,
    city, country_code, latitude, longitude, altitude,
    account_status, badge_tier,
    notify_telegram, notify_email,
    offers_training, offers_custom_orders, offers_repair,
    created_at, updated_at
)
SELECT
    gen_random_uuid(), 'messner-demo', 'messner@borrowhood.local',
    'Reinhold Messner', 'messner-mountain-hut',
    'Messner Mountain Hut', 'LODGE'::workshoptype,
    'All 14 eight-thousanders. First without oxygen. Still walking.',
    'If you do not risk the summit, you do not know the valley. I have lent my gear to beginners for forty years -- ask me anything about mountains, not everything needs a rope. Happy to lend, happy to teach, not happy to see a rookie on K2.',
    '/static/uploads/avatars/messner-46914e9e.jpg',
    'https://image.pollinations.ai/prompt/dolomites%20sunrise%20alpine%20peaks%20wide%20cinematic%20panorama?width=1600&height=500&nologo=true',
    'Sulden (IT)', 'IT', 46.517, 10.583, 1880,
    'ACTIVE'::accountstatus, 'LEGEND'::badgetier,
    false, false,
    true, false, true,
    NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM bh_user WHERE email = 'messner@borrowhood.local');

-- Languages
DELETE FROM bh_user_language WHERE user_id = (SELECT id FROM bh_user WHERE email = 'messner@borrowhood.local');
INSERT INTO bh_user_language (id, user_id, language_code, proficiency, created_at, updated_at)
SELECT gen_random_uuid(), u.id, lang, level::cefrlevel, NOW(), NOW()
FROM bh_user u,
     (VALUES ('de', 'NATIVE'), ('it', 'C2'), ('en', 'C1')) AS langs(lang, level)
WHERE u.email = 'messner@borrowhood.local';

-- Skills
DELETE FROM bh_user_skill WHERE user_id = (SELECT id FROM bh_user WHERE email = 'messner@borrowhood.local');
INSERT INTO bh_user_skill (id, user_id, skill_name, category, self_rating, verified_by_count, years_experience, created_at, updated_at)
SELECT gen_random_uuid(), u.id, sk.name, sk.cat, sk.rating, sk.verified, sk.yrs, NOW(), NOW()
FROM bh_user u,
     (VALUES
        ('Alpine climbing',       'sports', 5, 40, 14),
        ('Mountain navigation',   'sports', 5, 50, 30),
        ('High-altitude medicine','services', 4, 20, 30),
        ('Expedition planning',   'services', 5, 30, 40),
        ('Public speaking',       'creative', 5, 10, 25)
     ) AS sk(name, cat, rating, verified, yrs)
WHERE u.email = 'messner@borrowhood.local';

-- Items for Messner (skip if already exists)
DELETE FROM bh_item_media WHERE item_id IN (SELECT id FROM bh_item WHERE owner_id = (SELECT id FROM bh_user WHERE email = 'messner@borrowhood.local'));
DELETE FROM bh_listing    WHERE item_id IN (SELECT id FROM bh_item WHERE owner_id = (SELECT id FROM bh_user WHERE email = 'messner@borrowhood.local'));
DELETE FROM bh_item       WHERE owner_id = (SELECT id FROM bh_user WHERE email = 'messner@borrowhood.local');

WITH messner AS (SELECT id FROM bh_user WHERE email = 'messner@borrowhood.local'),
     seed(slug, name, item_type, category, description, story, tags, listing_type, price, price_unit, deposit, img_prompt) AS (
     VALUES
     ('messner-ice-axe-original',
      'Original ice axe -- my 1978 K2 climb',
      'PHYSICAL', 'camping',
      'Not for sale. On loan for museum display, school talks, or serious climbers who want to hold the piece. Free. Treat it like your first child.',
      'Sharpened with a file in Kathmandu. Up K2 with me in 1978 without oxygen. Still in one piece. Just.',
      'ice axe, alpine, history, K2, museum',
      'GIVEAWAY', NULL, 'flat', NULL,
      'vintage alpine ice axe worn wood handle mountain museum soft light'),

     ('messner-dolomites-1day-guide',
      'One-day Dolomites guiding -- for the serious',
      'SERVICE', 'camping',
      'I am 80 and still going. If you can walk 8 hours and carry 10 kilos, I can walk with you one day in the Dolomites. Not a beginner route. Ask first.',
      'Mountains do not care about your ego. That is why we go.',
      'dolomites, hiking, guide, alpine, sulden',
      'SERVICE', 150.00, 'per_day', NULL,
      'reinhold messner dolomites guide sunrise two hikers alpine ridge cinematic'),

     ('messner-expedition-boots-42',
      'Koflach expedition boots -- size 42',
      'PHYSICAL', 'camping',
      'My old Koflach doubles. Size 42. Stiff, warm, tall. Good for any 6000+ peak. EUR 80/week rent or EUR 250 outright. Deposit EUR 150 for rent.',
      'Took me up Aconcagua and Denali. They have rust nowhere because I cared for them.',
      'boots, expedition, koflach, mountain, rent',
      'RENT', 80.00, 'per_week', 150.00,
      'vintage red koflach mountaineering boots worn expedition gear'),

     ('messner-talk-at-your-school',
      'Talk at your school -- donation only',
      'SERVICE', 'education',
      'I will come to your school for an hour. Stories, slides, questions. No fee. A donation to mountain rescue is appreciated. EU and UK only, you pay travel.',
      'Kids get mountains more than adults. They have not forgotten how to look up.',
      'school, talk, education, mountain, free',
      'GIVEAWAY', NULL, 'flat', NULL,
      'reinhold messner speaking to kids classroom warm afternoon'),

     ('messner-yak-wool-blanket',
      'Yak-wool blanket -- from the Zanskar valley',
      'PHYSICAL', 'outdoor',
      'Hand-woven in Zanskar, 2004. Smells like the monastery. Stays warm in any weather. EUR 60.',
      'Gift from a monk who would not accept money. I gave him a compass. Fair trade.',
      'blanket, wool, yak, nepal, outdoor',
      'SELL', 60.00, 'flat', NULL,
      'hand woven yak wool blanket warm natural tones himalayan monastery')
     ),
     inserted AS (
         INSERT INTO bh_item (id, owner_id, name, slug, description, story, content_language,
                              item_type, category, condition, tags, latitude, longitude, altitude, created_at, updated_at)
         SELECT gen_random_uuid(), messner.id, s.name, s.slug, s.description, s.story, 'en',
                s.item_type::itemtype, s.category, 'GOOD'::itemcondition, s.tags,
                46.517, 10.583, 1880, NOW(), NOW()
         FROM seed s, messner
         RETURNING id, slug
     ),
     _ AS (
         INSERT INTO bh_item_media (id, item_id, url, alt_text, media_type, sort_order, created_at, updated_at)
         SELECT gen_random_uuid(), ii.id,
                'https://image.pollinations.ai/prompt/' || REPLACE(REPLACE(s.img_prompt, ' ', '%20'), ',', '%2C') || '?width=800&height=600&nologo=true',
                s.name, 'PHOTO'::mediatype, 0, NOW(), NOW()
         FROM inserted ii JOIN seed s ON s.slug = ii.slug
         RETURNING 1
     )
     INSERT INTO bh_listing (id, item_id, listing_type, status, price, price_unit, currency,
                             deposit, delivery_available, pickup_only, version, created_at, updated_at)
     SELECT gen_random_uuid(), ii.id, s.listing_type::listingtype, 'ACTIVE'::listingstatus,
            s.price, s.price_unit, 'EUR', s.deposit, false, true, 1, NOW(), NOW()
     FROM inserted ii JOIN seed s ON s.slug = ii.slug;

COMMIT;

-- Summary
SELECT
    u.display_name,
    u.slug,
    u.workshop_name,
    u.city,
    (SELECT COUNT(*) FROM bh_item i WHERE i.owner_id = u.id) AS items,
    (SELECT COUNT(*) FROM bh_user_skill s WHERE s.user_id = u.id) AS skills,
    (SELECT COUNT(*) FROM bh_user_language l WHERE l.user_id = u.id) AS langs
FROM bh_user u
WHERE u.email IN ('simon.divinti3@gmail.com', 'messner@borrowhood.local');
