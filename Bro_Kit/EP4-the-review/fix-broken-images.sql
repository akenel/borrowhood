-- EP4 Image Fix -- Replace all broken /media/ and /static/images/ paths with Unsplash URLs
-- These paths point to files that don't exist on the Hetzner server.
-- Each category gets a relevant Unsplash photo. Items with multiple images get varied photos.
-- Usage: docker exec -i postgres psql -U helix_user -d borrowhood < fix-broken-images.sql

-- ============================================================
-- CATEGORY-BASED BULK FIX (by row number within each item)
-- Photo 1 = hero shot, Photo 2 = detail, Photo 3 = context
-- ============================================================

-- Art items
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'art' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-00%');
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'art' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-01%');
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'art' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-02%');

-- Electronics
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'electronics' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-00%');
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1550009158-9ebf69173e03?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'electronics' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-01%');
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1588508065123-287b28e013da?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'electronics' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-02%');

-- Services
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1521791136064-7986c2920216?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'services' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-00%');
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'services' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-01%');
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'services' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-02%');

-- Kitchen
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'kitchen' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-00%');
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1585515320310-259814833e62?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'kitchen' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-01%');
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1590794056226-79ef3a8147e1?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'kitchen' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-02%');
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1574269909862-7e1d70bb8078?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'kitchen' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-03%');

-- Power tools
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1572981779307-38b8cabb2407?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'power_tools' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-00%');
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1504148455328-c376907d081c?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'power_tools' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-01%');
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1530124566582-a45a7e3f4b5e?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'power_tools' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-02%');

-- Repairs
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1621905251189-08b45d6a269e?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'repairs' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-00%');
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1581783898377-1c85bf937427?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'repairs' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-01%');
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1590479773265-7464e5d48118?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'repairs' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-02%');

-- Garden
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'garden' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-00%');
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'garden' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-01%');
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1591857177580-dc82b9ac4e1e?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'garden' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-02%');

-- Training/workshop services
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'training_service' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-00%');
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'training_service' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-01%');
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1531482615713-2afd69097998?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'training_service' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-02%');

-- Custom orders
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1452587925148-ce544e77e70d?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'custom_orders' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-00%');
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'custom_orders' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-01%');
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'custom_orders' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-02%');

-- Vehicles
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'vehicles' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-00%');
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1558981285-6f0c94958bb6?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'vehicles' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-01%');
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'vehicles' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-02%');

-- Spaces
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'spaces' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-00%');
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'spaces' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-01%');
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1462826303086-329426d1aef5?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'spaces' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-02%');

-- Sports
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1461896836934-bd45ba8a0420?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'sports' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-00%');
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1517649763962-0c623066013b?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'sports' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-01%');
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1535131749006-b7f58c99034b?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'sports' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-02%');

-- Home improvement
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'home_improvement' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-00%');
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1484154218962-a197022b5858?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'home_improvement' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-01%');
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1523413363574-c30aa1c2a516?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'home_improvement' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-02%');

-- Technology
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'technology' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-00%');
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'technology' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-01%');

-- 3D printing
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1631279470960-37f80bf4ee31?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = '3d_printing' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-00%');
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = '3d_printing' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-01%');

-- Water sports (surfboard, SUP, kayak)
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1502680390548-bdbac40ce065?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'water_sports' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-00%');
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1455729552457-5c322b5e8531?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'water_sports' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-01%');
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'water_sports' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%') AND m.url LIKE '%photo-02%');

-- Remaining categories (crafts, fashion, experiences, transport, cleaning, outdoor, cycling)
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'crafts' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%'));
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1558171813-01ed3d751f97?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'fashion' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%'));
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1528605248644-14dd04022da1?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'experiences' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%'));
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'transport' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%'));
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1563453392212-326f5e854473?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'cleaning' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%'));
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'outdoor' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%'));
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1541625602330-2277a4c46182?w=800&h=600&fit=crop&q=80'
WHERE id IN (SELECT m.id FROM bh_item_media m JOIN bh_item i ON m.item_id = i.id WHERE i.category = 'cycling' AND (m.url LIKE '/media/%' OR m.url LIKE '/static/%'));

-- ============================================================
-- SPECIFIC ITEM OVERRIDES (items that need recognizable photos)
-- ============================================================

-- George's surfboard
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1502680390548-bdbac40ce065?w=800&h=600&fit=crop&q=80'
WHERE item_id = (SELECT id FROM bh_item WHERE slug = 'surfboard-76-funboard') AND url LIKE '%photo-00%';
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1531722569936-825d3dd91b15?w=800&h=600&fit=crop&q=80'
WHERE item_id = (SELECT id FROM bh_item WHERE slug = 'surfboard-76-funboard') AND url LIKE '%photo-01%';
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1455729552457-5c322b5e8531?w=800&h=600&fit=crop&q=80'
WHERE item_id = (SELECT id FROM bh_item WHERE slug = 'surfboard-76-funboard') AND url LIKE '%photo-02%';

-- Johnny's pressure washing SERVICE (different from his K5 pressure washer which is already fixed)
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=800&h=600&fit=crop&q=80'
WHERE item_id = (SELECT id FROM bh_item WHERE slug = 'pressure-washing-service-patios') AND url LIKE '%karcher-patio%';
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=800&h=600&fit=crop&q=80'
WHERE item_id = (SELECT id FROM bh_item WHERE slug = 'pressure-washing-service-patios') AND url LIKE '%karcher-garden%';
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800&h=600&fit=crop&q=80'
WHERE item_id = (SELECT id FROM bh_item WHERE slug = 'pressure-washing-service-patios') AND url LIKE '%karcher-boat%';

-- KitchenAid mixer (Sally's)
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1594631252845-29fc4cc8cde9?w=800&h=600&fit=crop&q=80'
WHERE item_id = (SELECT id FROM bh_item WHERE slug = 'kitchenaid-stand-mixer-artisan-5qt') AND url LIKE '%mixer.png';
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1574269909862-7e1d70bb8078?w=800&h=600&fit=crop&q=80'
WHERE item_id = (SELECT id FROM bh_item WHERE slug = 'kitchenaid-stand-mixer-artisan-5qt') AND url LIKE '%mixer-2%';
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800&h=600&fit=crop&q=80'
WHERE item_id = (SELECT id FROM bh_item WHERE slug = 'kitchenaid-stand-mixer-artisan-5qt') AND url LIKE '%mixer-3%';
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1585515320310-259814833e62?w=800&h=600&fit=crop&q=80'
WHERE item_id = (SELECT id FROM bh_item WHERE slug = 'kitchenaid-stand-mixer-artisan-5qt') AND url LIKE '%mixer-4%';

-- ============================================================
-- CATCH-ALL: Any remaining broken paths
-- ============================================================
UPDATE bh_item_media SET url = 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=800&h=600&fit=crop&q=80'
WHERE url LIKE '/media/%' OR url LIKE '/static/images/seed/%' OR url LIKE '/static/images/items/%';

-- ============================================================
-- VERIFY
-- ============================================================
SELECT 'Remaining broken /media/ paths' AS check, COUNT(*) FROM bh_item_media WHERE url LIKE '/media/%';
SELECT 'Remaining broken /static/ paths' AS check, COUNT(*) FROM bh_item_media WHERE url LIKE '/static/images/%';
SELECT 'Total images with Unsplash URLs' AS check, COUNT(*) FROM bh_item_media WHERE url LIKE '%unsplash%';
