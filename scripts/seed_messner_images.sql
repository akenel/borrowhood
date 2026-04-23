-- Curated image set for Reinhold Messner's items.
-- 3 images per item, mix of Unsplash + Pollinations with seeded prompts.

BEGIN;

DELETE FROM bh_item_media
WHERE item_id IN (
    SELECT id FROM bh_item WHERE owner_id = (SELECT id FROM bh_user WHERE email = 'messner@borrowhood.local')
);

INSERT INTO bh_item_media (id, item_id, url, alt_text, media_type, sort_order, created_at, updated_at)
SELECT gen_random_uuid(), ii.id, img.url, ii.name, 'PHOTO'::mediatype, img.pos, NOW(), NOW()
FROM (
    SELECT id, name, slug FROM bh_item
    WHERE owner_id = (SELECT id FROM bh_user WHERE email = 'messner@borrowhood.local')
) ii
JOIN LATERAL (
    VALUES
    -- ORIGINAL ICE AXE (K2 1978)
    ('messner-ice-axe-original', 0,
     'https://images.unsplash.com/photo-1519681393784-d120267933ba?w=800&h=600&fit=crop&q=80'),
    ('messner-ice-axe-original', 1,
     'https://image.pollinations.ai/prompt/vintage%20ice%20axe%20worn%20wood%20handle%20climbing%20museum%20display%20soft%20light%20cinematic%20still%20life%20photography?width=800&height=600&nologo=true&seed=301'),
    ('messner-ice-axe-original', 2,
     'https://image.pollinations.ai/prompt/mountaineering%20ice%20axe%20k2%20expedition%20black%20and%20white%20history%20documentary?width=800&height=600&nologo=true&seed=302'),

    -- DOLOMITES 1-DAY GUIDE
    ('messner-dolomites-1day-guide', 0,
     'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&h=600&fit=crop&q=80'),
    ('messner-dolomites-1day-guide', 1,
     'https://image.pollinations.ai/prompt/dolomites%20sunrise%20alpine%20ridge%20two%20hikers%20climbing%20cinematic%20wide%20panorama?width=800&height=600&nologo=true&seed=303'),
    ('messner-dolomites-1day-guide', 2,
     'https://images.unsplash.com/photo-1472396961693-142e6e269027?w=800&h=600&fit=crop&q=80'),

    -- EXPEDITION BOOTS KOFLACH 42
    ('messner-expedition-boots-42', 0,
     'https://image.pollinations.ai/prompt/vintage%20red%20koflach%20mountaineering%20plastic%20double%20boots%20worn%20expedition%20gear%20studio%20photography?width=800&height=600&nologo=true&seed=304'),
    ('messner-expedition-boots-42', 1,
     'https://images.unsplash.com/photo-1520975661595-6453be3f7070?w=800&h=600&fit=crop&q=80'),
    ('messner-expedition-boots-42', 2,
     'https://image.pollinations.ai/prompt/expedition%20mountaineering%20boots%20in%20snow%20aconcagua%20denali%20gear%20shot%20warm%20light?width=800&height=600&nologo=true&seed=305'),

    -- TALK AT YOUR SCHOOL
    ('messner-talk-at-your-school', 0,
     'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=800&h=600&fit=crop&q=80'),
    ('messner-talk-at-your-school', 1,
     'https://image.pollinations.ai/prompt/older%20mountaineer%20speaking%20to%20group%20of%20school%20children%20classroom%20warm%20afternoon%20light%20documentary?width=800&height=600&nologo=true&seed=306'),
    ('messner-talk-at-your-school', 2,
     'https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=800&h=600&fit=crop&q=80'),

    -- YAK-WOOL BLANKET (Zanskar)
    ('messner-yak-wool-blanket', 0,
     'https://image.pollinations.ai/prompt/hand%20woven%20yak%20wool%20blanket%20natural%20tones%20himalayan%20monastery%20folded%20neat%20studio%20warm?width=800&height=600&nologo=true&seed=307'),
    ('messner-yak-wool-blanket', 1,
     'https://images.unsplash.com/photo-1544967082-d9d25d867d66?w=800&h=600&fit=crop&q=80'),
    ('messner-yak-wool-blanket', 2,
     'https://image.pollinations.ai/prompt/textured%20wool%20blanket%20himalayan%20craftsmanship%20texture%20closeup%20earthy%20tones?width=800&height=600&nologo=true&seed=308')
) AS img(target_slug, pos, url) ON ii.slug = img.target_slug;

-- Simon age fix: 30 not 36 (correct DOB = 1995-03-15 for 30 on 2026-04-23)
UPDATE bh_user SET
    date_of_birth = '1995-03-15',
    bio = 'I am 30. I read scans for a living -- traded heart surgery for the steady rhythm of the reading room. Twelve years in the ring, four mornings a week on the bag. I travel when I can: Greece, Germany, the Alps. Italian is home, German earned me Bavaria, English opens the rest of the world. I live in Enna. If you want to learn to box, I will teach you -- especially kids. Boxing is how you become a man without becoming a monster.',
    updated_at = NOW()
WHERE email = 'simon.divinti3@gmail.com';

COMMIT;

-- Verify
SELECT i.slug, COUNT(m.*) AS images
FROM bh_item i LEFT JOIN bh_item_media m ON m.item_id = i.id
WHERE i.owner_id = (SELECT id FROM bh_user WHERE email = 'messner@borrowhood.local')
GROUP BY i.slug ORDER BY i.slug;

SELECT display_name, date_of_birth,
       EXTRACT(YEAR FROM AGE(NOW(), date_of_birth))::int AS age
FROM bh_user WHERE email = 'simon.divinti3@gmail.com';
