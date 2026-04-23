-- Community category seed: skill_exchange / neighborhood_help / local_food / rides
-- Idempotent via ON CONFLICT DO NOTHING on slug.
-- Run on UAT:
--   docker exec postgres psql -U helix_user -d borrowhood -f /seed_community.sql
-- (mount the file first via: docker cp scripts/seed_community.sql postgres:/seed_community.sql)

BEGIN;

-- CTE that maps a row per item with its owner email and the image prompt
WITH seed(owner_email, category, item_type, name, slug, description, story, tags, listing_type, price, price_unit, deposit, img_prompt) AS (
    VALUES
    -- skill_exchange
    ('mike@borrowhood.local', 'skill_exchange', 'SERVICE',
     'Trade: Welding lessons for Italian lessons', 'trade-welding-lessons-for-italian-lessons',
     'I will teach you basic MIG welding if you help me finally speak proper Italian. I have been in Trapani 3 years and still order coffee wrong.',
     'Swapping skills beats swapping money. Two evenings a month, your kitchen or my garage.',
     'skill swap, italian, welding, language exchange',
     'OFFER', NULL, 'negotiable', NULL,
     'welding sparks and italian espresso cups old rustic workshop warm light'),

    ('sally@borrowhood.local', 'skill_exchange', 'SERVICE',
     'Sourdough starter + weekly baking coaching', 'sourdough-starter-weekly-baking-coaching',
     'Healthy starter from 2024. I will come help you with your first 3 loaves if you teach me something I do not know (photography? a language? carpentry?).',
     'My nonna taught me. Time to pass it on.',
     'sourdough, baking, skill swap, teaching, food',
     'OFFER', NULL, 'negotiable', NULL,
     'sourdough loaf rustic kitchen flour hands warm'),

    ('leonardo@borrowhood.local', 'skill_exchange', 'SERVICE',
     'Drawing fundamentals for gardening help', 'drawing-fundamentals-for-gardening-help',
     'I will teach you to draw what you see, not what you think you see. Three sessions of 2 hours. Need help with my olive grove in return.',
     'Everyone says they cannot draw. Everyone is wrong about themselves.',
     'drawing, art, gardening, skill swap, lessons',
     'OFFER', NULL, 'negotiable', NULL,
     'artist hands pencil sketching olive tree sicilian morning'),

    ('nicolo@borrowhood.local', 'skill_exchange', 'SERVICE',
     'Jiu-jitsu fundamentals for help with my website', 'jiu-jitsu-for-help-with-my-website',
     'Two hours of private BJJ for two hours of web help. I have a dojo site that needs love. You want to know how to escape a mount? Perfect trade.',
     'I can throw people. I cannot make a WordPress work.',
     'jiu-jitsu, bjj, web, skill swap, dojo',
     'OFFER', NULL, 'negotiable', NULL,
     'jiu jitsu dojo mat silhouette training evening light'),

    ('anne@borrowhood.local', 'skill_exchange', 'SERVICE',
     'QA testing tips for a homemade meal', 'qa-testing-tips-for-a-homemade-meal',
     'I will break your app with my Android bare hands. You feed me. Seriously: 1 hour structured testing + written report in exchange for dinner.',
     'Bugs taste better than complaints. Let us make the app stronger together.',
     'qa, testing, skill swap, dinner, cooking',
     'OFFER', NULL, 'negotiable', NULL,
     'laptop screen testing checklist sicilian kitchen evening'),

    -- neighborhood_help
    ('maria@borrowhood.local', 'neighborhood_help', 'SERVICE',
     'Need a hand fixing my squeaky shutters', 'need-a-hand-fixing-my-squeaky-shutters',
     'Persiane siciliane, 70-year-old wood, squeak like crazy. Trade: I bake bread for a week, you bring the WD-40 and an hour of your time.',
     'The sound wakes my grandson. Everything else I can live with.',
     'neighborhood, shutters, help, repair, Paceco',
     'OFFER', NULL, 'negotiable', NULL,
     'old sicilian persiane shutters warm morning light'),

    ('pietro@borrowhood.local', 'neighborhood_help', 'SERVICE',
     'Free drone aerial photos of your garden', 'free-drone-aerial-photos-of-your-garden',
     'Training for a certification. Catch me Saturday mornings in the Erice area and I will take overhead shots of your garden or villa. Free, high-res, no strings.',
     'I need practice hours. You get a view of your home nobody else has.',
     'drone, photography, neighborhood, free, aerial',
     'GIVEAWAY', NULL, 'flat', NULL,
     'drone aerial view sicilian villa garden olive trees morning'),

    ('nino@borrowhood.local', 'neighborhood_help', 'SERVICE',
     'Airport run for free if you are on my route', 'airport-run-for-free-if-you-are-on-my-route',
     'I drive Trapani to the airport and back 4x a week. If your flight matches my timing, hop in. Free. Just be on time.',
     'Empty seats are a waste. Fill them up, save petrol together.',
     'airport, rides, neighborhood, transport, free',
     'GIVEAWAY', NULL, 'flat', NULL,
     'camper van sicilian highway dawn empty road'),

    ('angel@borrowhood.local', 'neighborhood_help', 'SERVICE',
     'Bike tire patches in Trapani centro', 'bike-tire-patches-in-trapani-centro',
     'I have patched a lot of bike tires in my life. If yours goes flat in Trapani centro, message me. Bring a soda as thanks.',
     'Started when I was 8. Have not stopped. The smell of rubber cement is home.',
     'bike, repair, neighborhood, help, cycling',
     'OFFER', NULL, 'negotiable', NULL,
     'bike tire repair hands rubber patch afternoon workshop'),

    ('sofiaferretti@borrowhood.local', 'neighborhood_help', 'SERVICE',
     'Cookie run -- I pick up your bakery order Friday', 'cookie-run-i-pick-up-your-bakery-order-friday',
     'I go to Sofia Bakes every Friday at 3. If you live in San Vito and cannot get there, give me your order by Thursday and I will drop it on your step.',
     'Best cookies in Sicily. Nobody should miss them over a 20 minute drive.',
     'cookies, neighborhood, delivery, friday, san vito',
     'OFFER', NULL, 'negotiable', NULL,
     'cookie bakery basket friday afternoon sicilian village'),

    -- local_food
    ('sally@borrowhood.local', 'local_food', 'PHYSICAL',
     'Homemade cannoli -- Thursday batches', 'homemade-cannoli-thursday-batches',
     'I bake 20 shells + ricotta filling every Thursday. EUR 2 each. Pick up from my kitchen. Fill them yourself right before eating, trust me.',
     'My mom recipe. The shells shatter like old glass. That is the point.',
     'cannoli, food, sicilian, thursday, sally',
     'SELL', 2.00, 'flat', 0,
     'sicilian cannoli pastry ricotta filling rustic kitchen'),

    ('sofiaferretti@borrowhood.local', 'local_food', 'PHYSICAL',
     'Sicilian lemons by the kilo from my garden', 'sicilian-lemons-by-the-kilo',
     'Two lemon trees with too many lemons. 1 kg for EUR 2, 3 kg for EUR 5. No pesticides, picked when you order.',
     'Dad planted them in 1987. They have been giving ever since.',
     'lemons, local, food, sicilian, organic',
     'SELL', 2.00, 'flat', 0,
     'sicilian lemons tree wooden basket rustic garden sunlight'),

    ('maria@borrowhood.local', 'local_food', 'PHYSICAL',
     'Fresh sourdough loaves every Saturday', 'fresh-sourdough-loaves-every-saturday',
     'My garden-oven bread, 24h fermentation, local flour. EUR 4 each. Reserve by Friday evening, pick up Saturday morning.',
     'The oven belonged to my grandmother. She used to bake for the village. Now I do.',
     'bread, sourdough, local, saturday, sicilian',
     'SELL', 4.00, 'flat', 0,
     'sourdough loaf crust wood oven rustic sicilian morning'),

    ('leonardo@borrowhood.local', 'local_food', 'PHYSICAL',
     'Family olive oil -- 2024 first cold press', 'family-olive-oil-2024-first-cold-press',
     '5 liters from my family trees, first cold press, October 2024. EUR 35 for 5L. You can smell the leaves in it. Bring your bottle or add EUR 2.',
     'The trees are over 200 years old. The oil tastes like something you remember.',
     'olive oil, local, food, harvest, first press',
     'SELL', 35.00, 'flat', 0,
     'olive oil bottle pouring amber green sicilian groves'),

    ('angel@borrowhood.local', 'local_food', 'PHYSICAL',
     'Black wolf espresso blend 250g', 'black-wolf-espresso-blend-250g',
     'I do not roast. But I know a guy. Local Trapani roaster, dark blend, strong, for people who take coffee like Sicilians. EUR 8 / 250g.',
     'Every package is the same as what I pour at home.',
     'coffee, espresso, local, sicilian, dark',
     'SELL', 8.00, 'flat', 0,
     'espresso beans dark roast rustic sicilian cafe warm'),

    -- rides
    ('nino@borrowhood.local', 'rides', 'SERVICE',
     'Weekly Trapani to Palermo -- Friday + Sunday', 'weekly-trapani-to-palermo-friday-sunday',
     'I do this trip every weekend. 3 seats. EUR 15 each, splits the petrol. Leaves Trapani 9am Friday, back Sunday 7pm.',
     'Been doing the drive for years. Nice to have company for once.',
     'rides, palermo, weekend, carpool, trapani',
     'OFFER', 15.00, 'flat', NULL,
     'camper van sicilian highway palermo sunset road'),

    ('pietro@borrowhood.local', 'rides', 'SERVICE',
     'Erice shuttle up the mountain', 'erice-shuttle-up-the-mountain',
     'Tourists always need a lift up. EUR 20 return, 2 seats. I need to go anyway for drone shoots most days.',
     'The cable car is beautiful. My car is faster.',
     'rides, erice, shuttle, mountain, tourists',
     'OFFER', 20.00, 'flat', NULL,
     'winding road mountain erice sicily car view'),

    ('nicolo@borrowhood.local', 'rides', 'SERVICE',
     'Dojo pickup for kids under 16', 'dojo-pickup-for-kids-under-16',
     'If your kid comes to my BJJ class but you cannot drop them off, I can pick up in Trapani centro. Free. Parents and I exchange phones first.',
     'Consistency matters more at 12 than at 30.',
     'rides, kids, dojo, jiu-jitsu, trapani',
     'GIVEAWAY', NULL, 'flat', NULL,
     'car door opening kid with backpack sicilian street afternoon'),

    ('mike@borrowhood.local', 'rides', 'SERVICE',
     'Moving help -- small van + strong back', 'moving-help-small-van-strong-back',
     'I have a Transit Custom and 30 years of lifting. EUR 40/hour including fuel. Trapani province only.',
     'Moved 200 apartments in Switzerland. Same joints, different sun.',
     'moving, van, help, muscle, trapani',
     'OFFER', 40.00, 'per_hour', NULL,
     'small white moving van sicilian street boxes loading'),

    ('jake@borrowhood.local', 'rides', 'SERVICE',
     'Late-night ride home from a meetup', 'late-night-ride-home-from-a-meetup',
     'Anyone going home after the monthly La Piazza meetup -- I can swing through San Vito, Trapani centro, Paceco. Text me from the bar.',
     'Nobody should walk home alone after midnight. Not on my watch.',
     'rides, late night, community, meetup, safety',
     'GIVEAWAY', NULL, 'flat', NULL,
     'headlights empty sicilian road midnight peaceful')
),
-- Insert items (skip if slug exists)
inserted_items AS (
    INSERT INTO bh_item (
        id, owner_id, name, slug, description, story, content_language,
        item_type, category, condition, tags, created_at, updated_at
    )
    SELECT
        gen_random_uuid(), u.id, s.name, s.slug, s.description, s.story, 'en',
        s.item_type::itemtype, s.category, 'GOOD'::itemcondition, s.tags, NOW(), NOW()
    FROM seed s
    JOIN bh_user u ON u.email = s.owner_email AND u.deleted_at IS NULL
    WHERE NOT EXISTS (SELECT 1 FROM bh_item existing WHERE existing.slug = s.slug)
    RETURNING id, slug
),
-- Add media for new items
_ AS (
    INSERT INTO bh_item_media (id, item_id, url, alt_text, media_type, sort_order, created_at, updated_at)
    SELECT gen_random_uuid(), ii.id,
           'https://image.pollinations.ai/prompt/' || REPLACE(REPLACE(s.img_prompt, ' ', '%20'), ',', '%2C') || '?width=800&height=600&nologo=true',
           s.name, 'PHOTO'::mediatype, 0, NOW(), NOW()
    FROM inserted_items ii
    JOIN seed s ON s.slug = ii.slug
    RETURNING 1
)
-- Add listings for new items
INSERT INTO bh_listing (
    id, item_id, listing_type, status, price, price_unit, currency,
    deposit, delivery_available, pickup_only, version, created_at, updated_at
)
SELECT gen_random_uuid(), ii.id, s.listing_type::listingtype, 'ACTIVE'::listingstatus,
       s.price, s.price_unit, 'EUR', s.deposit, false, true, 1, NOW(), NOW()
FROM inserted_items ii
JOIN seed s ON s.slug = ii.slug;

COMMIT;

SELECT category, COUNT(*) FROM bh_item WHERE category IN ('skill_exchange','neighborhood_help','local_food','rides') GROUP BY category ORDER BY category;
