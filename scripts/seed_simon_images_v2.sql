-- Replace Simon's item images with a stronger curated set.
-- Pollinations with cinematic prompts + hand-picked Unsplash photos we know render well.

BEGIN;

DELETE FROM bh_item_media
WHERE item_id IN (
    SELECT id FROM bh_item WHERE owner_id = (SELECT id FROM bh_user WHERE email = 'simon.divinti3@gmail.com')
);

INSERT INTO bh_item_media (id, item_id, url, alt_text, media_type, sort_order, created_at, updated_at)
SELECT gen_random_uuid(), ii.id, img.url, ii.name, 'PHOTO'::mediatype, img.pos, NOW(), NOW()
FROM (
    SELECT id, name, slug FROM bh_item
    WHERE owner_id = (SELECT id FROM bh_user WHERE email = 'simon.divinti3@gmail.com')
) ii
JOIN LATERAL (
    VALUES
    -- BOXING PAD & GLOVE KIT (rent)
    ('white-hammer-boxing-pad-kit', 0,
     'https://images.unsplash.com/photo-1583473848882-f9a5bc7fd2ee?w=800&h=600&fit=crop&q=80'),
    ('white-hammer-boxing-pad-kit', 1,
     'https://image.pollinations.ai/prompt/professional%20red%20boxing%20gloves%20on%20wooden%20gym%20bench%20cinematic%20warm%20low%20key%20photography%2035mm%20film?width=800&height=600&nologo=true&seed=201'),
    ('white-hammer-boxing-pad-kit', 2,
     'https://images.unsplash.com/photo-1552674605-db6ffd4facb5?w=800&h=600&fit=crop&q=80'),

    -- PRIVATE COACHING 1-on-1
    ('white-hammer-private-coaching', 0,
     'https://images.unsplash.com/photo-1549719386-74dfcbf7dbed?w=800&h=600&fit=crop&q=80'),
    ('white-hammer-private-coaching', 1,
     'https://image.pollinations.ai/prompt/boxing%20trainer%20holding%20focus%20mitts%20for%20a%20student%20punch%20black%20and%20white%20documentary%20photography%20dramatic%20contrast?width=800&height=600&nologo=true&seed=202'),
    ('white-hammer-private-coaching', 2,
     'https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=800&h=600&fit=crop&q=80'),

    -- FIGHTER''S FOUNDATION (teen 6-week)
    ('white-hammer-fighters-foundation', 0,
     'https://images.unsplash.com/photo-1517438322307-e67111335449?w=800&h=600&fit=crop&q=80'),
    ('white-hammer-fighters-foundation', 1,
     'https://image.pollinations.ai/prompt/group%20of%20focused%20teenagers%20boxing%20training%20in%20line%20coach%20watching%20sicilian%20gym%20morning%20light?width=800&height=600&nologo=true&seed=203'),
    ('white-hammer-fighters-foundation', 2,
     'https://images.unsplash.com/photo-1574680096145-d05b474e2155?w=800&h=600&fit=crop&q=80'),

    -- FREE INTRO + GUM SHIELD (kids)
    ('white-hammer-free-intro-and-gum-shield', 0,
     'https://image.pollinations.ai/prompt/young%20kid%20pulling%20on%20boxing%20gloves%20first%20time%20focused%20smile%20gym%20warm%20window%20light%20documentary?width=800&height=600&nologo=true&seed=204'),
    ('white-hammer-free-intro-and-gum-shield', 1,
     'https://images.unsplash.com/photo-1594737625785-a6cbdabd333c?w=800&h=600&fit=crop&q=80'),
    ('white-hammer-free-intro-and-gum-shield', 2,
     'https://image.pollinations.ai/prompt/coach%20holding%20mitt%20down%20for%20small%20child%20first%20jab%20lesson%20warm%20encouragement%20gym?width=800&height=600&nologo=true&seed=205'),

    -- COACHING RAFFLE
    ('white-hammer-coaching-raffle', 0,
     'https://image.pollinations.ai/prompt/boxing%20gloves%20hanging%20on%20a%20ring%20rope%20with%20raffle%20tickets%20in%20foreground%20warm%20dramatic%20light%20fundraiser?width=800&height=600&nologo=true&seed=206'),
    ('white-hammer-coaching-raffle', 1,
     'https://images.unsplash.com/photo-1544717684-1243da23b545?w=800&h=600&fit=crop&q=80'),
    ('white-hammer-coaching-raffle', 2,
     'https://image.pollinations.ai/prompt/closeup%20of%20boxing%20gloves%20ring%20rope%20empty%20ring%20soft%20golden%20hour%20light?width=800&height=600&nologo=true&seed=207'),

    -- GUANTONI IN PIAZZA (event)
    ('white-hammer-guantoni-in-piazza', 0,
     'https://image.pollinations.ai/prompt/outdoor%20boxing%20demo%20at%20italian%20university%20campus%20sunset%20crowd%20of%20students%20watching%20two%20boxers%20sparring%20cinematic?width=800&height=600&nologo=true&seed=208'),
    ('white-hammer-guantoni-in-piazza', 1,
     'https://images.unsplash.com/photo-1530143311094-34d807799e8f?w=800&h=600&fit=crop&q=80'),
    ('white-hammer-guantoni-in-piazza', 2,
     'https://image.pollinations.ai/prompt/young%20boxer%20shadowboxing%20at%20italian%20piazza%20sunset%20audience%20silhouette%20dramatic?width=800&height=600&nologo=true&seed=209')
) AS img(target_slug, pos, url) ON ii.slug = img.target_slug;

COMMIT;

SELECT i.slug, COUNT(*) AS images FROM bh_item_media m JOIN bh_item i ON i.id = m.item_id
WHERE i.owner_id = (SELECT id FROM bh_user WHERE email = 'simon.divinti3@gmail.com')
GROUP BY i.slug ORDER BY i.slug;
