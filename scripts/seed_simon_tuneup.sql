-- Simon White profile tune-up (post-feedback):
--   * Drop Christian line from public bio (fruits speak louder)
--   * Add motto: "find something you love..."
--   * Payment methods
--   * Baseline reputation points (not 0 for a profile we built up)
--   * 3 images per item (cover + 2 variants)

BEGIN;

-- ========== BIO + MOTTO + PAYMENTS ==========

UPDATE bh_user SET
    tagline = 'Find something you love to do and never work a day in your life.',
    bio = 'I am 36. I read scans for a living -- traded heart surgery for the steady rhythm of the reading room. Twelve years in the ring, four mornings a week on the bag. I travel when I can: Greece, Germany, the Alps. Italian is home, German earned me Bavaria, English opens the rest of the world. I live in Enna. If you want to learn to box, I will teach you -- especially kids. Boxing is how you become a man without becoming a monster.',
    accepted_payments = 'cash,paypal,iban,satispay,applepay',
    updated_at = NOW()
WHERE email = 'simon.divinti3@gmail.com';

-- ========== BASELINE REPUTATION POINTS ==========
-- Creating 6 listings + a profile in your first day = real effort. Seed +75.
INSERT INTO bh_user_points (
    id, user_id, total_points, items_listed,
    rentals_completed, reviews_given, reviews_received, helpful_flags,
    created_at, updated_at
)
SELECT gen_random_uuid(), id, 75, 6, 0, 0, 0, 0, NOW(), NOW()
FROM bh_user
WHERE email = 'simon.divinti3@gmail.com'
ON CONFLICT (user_id) DO UPDATE SET
    total_points = GREATEST(bh_user_points.total_points, 75),
    items_listed = GREATEST(bh_user_points.items_listed, 6),
    updated_at = NOW();

-- Bump tier -> ACTIVE so the UI shows something beyond Newcomer
UPDATE bh_user SET badge_tier = 'ACTIVE'::badgetier
WHERE email = 'simon.divinti3@gmail.com' AND badge_tier = 'NEWCOMER'::badgetier;

-- ========== EXTRA IMAGES (2 more per item -> 3 total incl. existing) ==========
-- Delete only sort_order > 0 so cover stays
DELETE FROM bh_item_media
WHERE item_id IN (
    SELECT id FROM bh_item
    WHERE owner_id = (SELECT id FROM bh_user WHERE email = 'simon.divinti3@gmail.com')
) AND sort_order > 0;

INSERT INTO bh_item_media (id, item_id, url, alt_text, media_type, sort_order, created_at, updated_at)
SELECT gen_random_uuid(), ii.id, img.url, ii.name, 'PHOTO'::mediatype, img.pos, NOW(), NOW()
FROM (
    SELECT id, name, slug FROM bh_item
    WHERE owner_id = (SELECT id FROM bh_user WHERE email = 'simon.divinti3@gmail.com')
) ii
JOIN LATERAL (
    VALUES
    -- boxing-pad-kit: alternative angles
    ('white-hammer-boxing-pad-kit', 1, 'https://image.pollinations.ai/prompt/red%20boxing%20gloves%20hanging%20gym%20locker%20warm%20light?width=800&height=600&nologo=true'),
    ('white-hammer-boxing-pad-kit', 2, 'https://images.unsplash.com/photo-1583473848882-f9a5bc7fd2ee?w=800&h=600&fit=crop&q=80'),

    ('white-hammer-private-coaching', 1, 'https://image.pollinations.ai/prompt/boxing%20coach%20holding%20focus%20mitts%20black%20and%20white?width=800&height=600&nologo=true'),
    ('white-hammer-private-coaching', 2, 'https://images.unsplash.com/photo-1549719386-74dfcbf7dbed?w=800&h=600&fit=crop&q=80'),

    ('white-hammer-fighters-foundation', 1, 'https://image.pollinations.ai/prompt/teenage%20boys%20boxing%20class%20lined%20up%20focused%20coach?width=800&height=600&nologo=true'),
    ('white-hammer-fighters-foundation', 2, 'https://images.unsplash.com/photo-1517438322307-e67111335449?w=800&h=600&fit=crop&q=80'),

    ('white-hammer-free-intro-and-gum-shield', 1, 'https://image.pollinations.ai/prompt/child%20trying%20boxing%20glove%20first%20time%20smiling%20warm?width=800&height=600&nologo=true'),
    ('white-hammer-free-intro-and-gum-shield', 2, 'https://images.unsplash.com/photo-1600490722471-ef6d3c34e75a?w=800&h=600&fit=crop&q=80'),

    ('white-hammer-coaching-raffle', 1, 'https://image.pollinations.ai/prompt/boxing%20raffle%20tickets%20golden%20gloves%20warm%20gym?width=800&height=600&nologo=true'),
    ('white-hammer-coaching-raffle', 2, 'https://images.unsplash.com/photo-1555597673-b21d5c935865?w=800&h=600&fit=crop&q=80'),

    ('white-hammer-guantoni-in-piazza', 1, 'https://image.pollinations.ai/prompt/outdoor%20boxing%20training%20sunset%20sicilian%20campus%20crowd?width=800&height=600&nologo=true'),
    ('white-hammer-guantoni-in-piazza', 2, 'https://images.unsplash.com/photo-1530143311094-34d807799e8f?w=800&h=600&fit=crop&q=80')
) AS img(target_slug, pos, url) ON ii.slug = img.target_slug;

COMMIT;

-- summary
SELECT
    u.display_name, u.tagline, u.accepted_payments, u.badge_tier,
    (SELECT total_points FROM bh_user_points p WHERE p.user_id = u.id) AS points,
    (SELECT COUNT(*) FROM bh_item WHERE owner_id = u.id) AS items,
    (SELECT COUNT(*) FROM bh_item_media m JOIN bh_item i ON i.id = m.item_id WHERE i.owner_id = u.id) AS images
FROM bh_user u
WHERE u.email = 'simon.divinti3@gmail.com';
