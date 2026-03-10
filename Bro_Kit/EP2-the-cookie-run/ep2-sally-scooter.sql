-- EP2 "The Cookie Run" -- Sally's electric scooter item + listing + media
-- Run against Hetzner PostgreSQL
-- 2026-03-07

BEGIN;

-- Step 1: Insert the item (owned by Sally)
WITH sally AS (
    SELECT id FROM bh_user WHERE slug = 'sallys-kitchen'
),
new_item AS (
    INSERT INTO bh_item (
        id, owner_id, name, slug, description,
        item_type, category, condition,
        brand, model, content_language,
        created_at, updated_at
    )
    SELECT
        gen_random_uuid(),
        sally.id,
        'Electric Scooter (Used -- Perfect for Deliveries)',
        'sallys-electric-scooter-for-delivery',
        'Used Xiaomi electric scooter, 30km range, perfect for local deliveries.',
        'PHYSICAL',
        'vehicles',
        'GOOD',
        'Xiaomi',
        'Mi Electric Scooter',
        'en',
        NOW(), NOW()
    FROM sally
    RETURNING id
),

-- Step 2: Insert the listing (RENT, PAUSED, 5.00 EUR/day)
new_listing AS (
    INSERT INTO bh_listing (
        id, item_id, listing_type, status,
        price, price_unit, currency,
        pickup_only, delivery_available,
        version,
        created_at, updated_at
    )
    SELECT
        gen_random_uuid(),
        new_item.id,
        'RENT',
        'PAUSED',
        5.00,
        'per_day',
        'EUR',
        true,
        false,
        1,
        NOW(), NOW()
    FROM new_item
    RETURNING id
),

-- Step 3: Insert media 1
media_1 AS (
    INSERT INTO bh_item_media (
        id, item_id, media_type, url, alt_text, sort_order,
        created_at, updated_at
    )
    SELECT
        gen_random_uuid(),
        new_item.id,
        'PHOTO',
        'https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=800',
        'Electric scooter for urban delivery',
        0,
        NOW(), NOW()
    FROM new_item
    RETURNING id
)

-- Step 4: Insert media 2
INSERT INTO bh_item_media (
    id, item_id, media_type, url, alt_text, sort_order,
    created_at, updated_at
)
SELECT
    gen_random_uuid(),
    new_item.id,
    'PHOTO',
    'https://images.unsplash.com/photo-1604868189955-89cf4e3dbff2?w=800',
    'Electric scooter parked on Mediterranean street',
    1,
    NOW(), NOW()
FROM new_item;

COMMIT;

-- Verification: show the new item, listing, and media
SELECT
    i.slug AS item_slug,
    i.name AS item_name,
    i.category,
    i.condition,
    l.listing_type,
    l.status,
    l.price,
    l.currency,
    (SELECT COUNT(*) FROM bh_item_media m WHERE m.item_id = i.id) AS media_count
FROM bh_item i
LEFT JOIN bh_listing l ON l.item_id = i.id
WHERE i.slug = 'sallys-electric-scooter-for-delivery';
