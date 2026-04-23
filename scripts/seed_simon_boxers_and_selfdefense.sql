-- Simon: Boxing legend GIFs as supplemental images + new Women's Self-Defense course + raffle.

BEGIN;

-- ========================================
-- 1. Attach boxing-legend GIFs to existing items (position 3+, after the
--    curated cover + 2 variants we already have)
-- ========================================
-- Each item gets 2 legend GIFs (different boxers) to give the cards life.
INSERT INTO bh_item_media (id, item_id, url, alt_text, media_type, sort_order, created_at, updated_at)
SELECT gen_random_uuid(), ii.id, img.url, 'Boxing legend -- ' || ii.name, 'PHOTO'::mediatype, img.pos, NOW(), NOW()
FROM (
    SELECT id, name, slug FROM bh_item
    WHERE owner_id = (SELECT id FROM bh_user WHERE email = 'simon.divinti3@gmail.com')
) ii
JOIN LATERAL (
    VALUES
    ('white-hammer-boxing-pad-kit',            3, '/static/uploads/simon-boxers/boxer_1.gif'),
    ('white-hammer-boxing-pad-kit',            4, '/static/uploads/simon-boxers/boxer_5.gif'),
    ('white-hammer-private-coaching',          3, '/static/uploads/simon-boxers/boxer_2.gif'),
    ('white-hammer-private-coaching',          4, '/static/uploads/simon-boxers/boxer_9.gif'),
    ('white-hammer-fighters-foundation',       3, '/static/uploads/simon-boxers/boxer_3.gif'),
    ('white-hammer-fighters-foundation',       4, '/static/uploads/simon-boxers/boxer_10.gif'),
    ('white-hammer-free-intro-and-gum-shield', 3, '/static/uploads/simon-boxers/boxer_4.gif'),
    ('white-hammer-free-intro-and-gum-shield', 4, '/static/uploads/simon-boxers/boxer_6.gif'),
    ('white-hammer-coaching-raffle',           3, '/static/uploads/simon-boxers/boxer_7.gif'),
    ('white-hammer-coaching-raffle',           4, '/static/uploads/simon-boxers/boxer_8.gif'),
    ('white-hammer-guantoni-in-piazza',        3, '/static/uploads/simon-boxers/boxer_5.gif'),
    ('white-hammer-guantoni-in-piazza',        4, '/static/uploads/simon-boxers/boxer_1.gif')
) AS img(target_slug, pos, url) ON ii.slug = img.target_slug
ON CONFLICT DO NOTHING;

-- ========================================
-- 2. Women's Self-Defense Course (training) + Raffle version
-- ========================================

-- Clear any prior attempts
DELETE FROM bh_item_media WHERE item_id IN (SELECT id FROM bh_item WHERE slug IN ('white-hammer-womens-self-defense', 'white-hammer-womens-self-defense-raffle'));
DELETE FROM bh_listing    WHERE item_id IN (SELECT id FROM bh_item WHERE slug IN ('white-hammer-womens-self-defense', 'white-hammer-womens-self-defense-raffle'));
DELETE FROM bh_item       WHERE slug IN ('white-hammer-womens-self-defense', 'white-hammer-womens-self-defense-raffle');

-- ITEM A: Course (training listing)
WITH simon AS (SELECT id FROM bh_user WHERE email = 'simon.divinti3@gmail.com'),
     ins AS (
         INSERT INTO bh_item (id, owner_id, name, slug, description, story, content_language,
                              item_type, category, condition, tags, latitude, longitude, created_at, updated_at)
         SELECT gen_random_uuid(), simon.id,
                'Women''s Self-Defense Course -- 4 weeks, Enna',
                'white-hammer-womens-self-defense',
                'Four 90-minute sessions designed for women, by a boxer who has spent 12 years learning what strikes land and what does not. Practical, repeatable moves you can use in the street, in the carpark, in the elevator. No ego, no tough-guy nonsense. Small group (max 8). You will leave able to defend yourself from the most common grabs and attacks -- and knowing when to run, when to shout, and when to fight.',
                'Every woman I know has a story about a moment she wished she had known what to do. This course is the answer to that moment. My sister asked me to run one. I said yes. Now I am opening it up.',
                'en',
                'SERVICE'::itemtype, 'training_service',
                'GOOD'::itemcondition,
                'self-defense, women, safety, training, boxing, enna, course',
                37.566181, 14.277832, NOW(), NOW()
         FROM simon
         RETURNING id
     ),
     _i AS (
         INSERT INTO bh_item_media (id, item_id, url, alt_text, media_type, sort_order, created_at, updated_at)
         SELECT gen_random_uuid(), ins.id, url, 'Women''s Self-Defense Course', 'PHOTO'::mediatype, pos, NOW(), NOW()
         FROM ins, (VALUES
             (0, 'https://images.unsplash.com/photo-1591258370814-01609b341790?w=800&h=600&fit=crop&q=80'),
             (1, 'https://image.pollinations.ai/prompt/women%20self%20defense%20class%20practical%20training%20instructor%20warm%20gym%20documentary?width=800&height=600&nologo=true&seed=401'),
             (2, 'https://images.unsplash.com/photo-1549060279-7e168fcee0c2?w=800&h=600&fit=crop&q=80'),
             (3, '/static/uploads/simon-boxers/boxer_5.gif'),
             (4, '/static/uploads/simon-boxers/boxer_3.gif')
         ) AS m(pos, url)
     )
     INSERT INTO bh_listing (id, item_id, listing_type, status, price, price_unit, currency,
                             deposit, delivery_available, pickup_only, max_participants,
                             per_person_rate, minimum_charge, version, created_at, updated_at)
     SELECT gen_random_uuid(), ins.id, 'TRAINING'::listingtype, 'ACTIVE'::listingstatus,
            20.00, 'per_session', 'EUR', NULL, false, true, 8,
            NULL, NULL, 1, NOW(), NOW()
     FROM ins;


-- ITEM B: Raffle off one free spot (community-friendly)
WITH simon AS (SELECT id FROM bh_user WHERE email = 'simon.divinti3@gmail.com'),
     ins AS (
         INSERT INTO bh_item (id, owner_id, name, slug, description, story, content_language,
                              item_type, category, condition, tags, latitude, longitude, created_at, updated_at)
         SELECT gen_random_uuid(), simon.id,
                'Raffle: Free seat in the Women''s Self-Defense Course',
                'white-hammer-womens-self-defense-raffle',
                'One lucky winner gets the full 4-week Women''s Self-Defense Course, free. EUR 3 per ticket, draw in 10 days. Proceeds (every euro of them) go toward more free seats for young women in Enna who cannot afford it. No platform fees, no cuts.',
                'The best thing you can do with a raffle is give away what was never really yours. Someone taught me to defend myself. I am passing it on.',
                'en',
                'SERVICE'::itemtype, 'training_service',
                'GOOD'::itemcondition,
                'raffle, self-defense, women, community, enna, fundraiser',
                37.566181, 14.277832, NOW(), NOW()
         FROM simon
         RETURNING id
     ),
     _i AS (
         INSERT INTO bh_item_media (id, item_id, url, alt_text, media_type, sort_order, created_at, updated_at)
         SELECT gen_random_uuid(), ins.id, url, 'Self-Defense raffle', 'PHOTO'::mediatype, pos, NOW(), NOW()
         FROM ins, (VALUES
             (0, 'https://image.pollinations.ai/prompt/women%20self%20defense%20raffle%20gym%20community%20fundraiser%20empowerment%20warm%20light?width=800&height=600&nologo=true&seed=402'),
             (1, 'https://images.unsplash.com/photo-1591258370814-01609b341790?w=800&h=600&fit=crop&q=80'),
             (2, '/static/uploads/simon-boxers/boxer_4.gif'),
             (3, '/static/uploads/simon-boxers/boxer_9.gif')
         ) AS m(pos, url)
     )
     INSERT INTO bh_listing (id, item_id, listing_type, status, price, price_unit, currency,
                             deposit, delivery_available, pickup_only, max_participants, version, created_at, updated_at)
     SELECT gen_random_uuid(), ins.id, 'RAFFLE'::listingtype, 'ACTIVE'::listingstatus,
            3.00, 'flat', 'EUR', NULL, false, true, NULL, 1, NOW(), NOW()
     FROM ins;

COMMIT;

-- Summary
SELECT i.slug, l.listing_type, l.price, l.price_unit, COUNT(m.*) AS imgs
FROM bh_item i
LEFT JOIN bh_listing l ON l.item_id = i.id
LEFT JOIN bh_item_media m ON m.item_id = i.id
WHERE i.owner_id = (SELECT id FROM bh_user WHERE email = 'simon.divinti3@gmail.com')
GROUP BY i.slug, l.listing_type, l.price, l.price_unit
ORDER BY i.created_at DESC;
