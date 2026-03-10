-- EP2 "The Cookie Run" -- Set banner_url + GPS coordinates for all 14 cast members
-- Run against Hetzner PostgreSQL
-- 2026-03-07

BEGIN;

-- Sally Ferretti
UPDATE bh_user SET
    banner_url = 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1200&h=400&fit=crop',
    latitude = 38.0185, longitude = 12.5145,
    updated_at = NOW()
WHERE slug = 'sallys-kitchen';

-- Mike Ferretti
UPDATE bh_user SET
    banner_url = 'https://images.unsplash.com/photo-1580894894513-541e068a3e2b?w=1200&h=400&fit=crop',
    latitude = 38.0155, longitude = 12.5095,
    updated_at = NOW()
WHERE slug = 'mikes-garage';

-- Angel (Angelo)
UPDATE bh_user SET
    banner_url = 'https://images.unsplash.com/photo-1523531294919-4bcd7c65e216?w=1200&h=400&fit=crop',
    latitude = 38.0773, longitude = 12.6443,
    updated_at = NOW()
WHERE slug = 'angel-hq';

-- Nino Cassisa
UPDATE bh_user SET
    banner_url = 'https://images.unsplash.com/photo-1523987355523-c7b5b0dd90a7?w=1200&h=400&fit=crop',
    latitude = 38.0140, longitude = 12.5230,
    updated_at = NOW()
WHERE slug = 'ninos-campers';

-- Maria Ferretti
UPDATE bh_user SET
    banner_url = 'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=1200&h=400&fit=crop',
    latitude = 38.0160, longitude = 12.5200,
    updated_at = NOW()
WHERE slug = 'marias-garden';

-- Marco Ferretti
UPDATE bh_user SET
    banner_url = 'https://images.unsplash.com/photo-1504148455328-c376907d081c?w=1200&h=400&fit=crop',
    latitude = 38.0178, longitude = 12.5125,
    updated_at = NOW()
WHERE slug = 'marcos-workshop';

-- Jake Ferretti
UPDATE bh_user SET
    banner_url = 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200&h=400&fit=crop',
    latitude = 38.0180, longitude = 12.5120,
    updated_at = NOW()
WHERE slug = 'jakes-electronics';

-- Rosa Ferretti
UPDATE bh_user SET
    banner_url = 'https://images.unsplash.com/photo-1484101403633-562f891dc89a?w=1200&h=400&fit=crop',
    latitude = 38.0170, longitude = 12.5110,
    updated_at = NOW()
WHERE slug = 'rosas-home';

-- George Abela
UPDATE bh_user SET
    banner_url = 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=1200&h=400&fit=crop',
    latitude = 38.0195, longitude = 12.5160,
    updated_at = NOW()
WHERE slug = 'georges-villa';

-- John (Johnny) Abela
UPDATE bh_user SET
    banner_url = 'https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=1200&h=400&fit=crop',
    latitude = 38.0158, longitude = 12.5220,
    updated_at = NOW()
WHERE slug = 'johns-cleaning';

-- Pietro Ferretti
UPDATE bh_user SET
    banner_url = 'https://images.unsplash.com/photo-1473968512647-3e447244af8f?w=1200&h=400&fit=crop',
    latitude = 38.0680, longitude = 12.8200,
    updated_at = NOW()
WHERE slug = 'pietros-drones';

-- Sofia Ferretti
UPDATE bh_user SET
    banner_url = 'https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=1200&h=400&fit=crop',
    latitude = 38.0680, longitude = 12.8200,
    updated_at = NOW()
WHERE slug = 'sofias-bakes';

-- Anne QA
UPDATE bh_user SET
    banner_url = 'https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=1200&h=400&fit=crop',
    latitude = -1.2921, longitude = 36.8219,
    updated_at = NOW()
WHERE slug = 'annes-qa-lab';

-- Leonardo Ferretti
UPDATE bh_user SET
    banner_url = 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=1200&h=400&fit=crop',
    latitude = 38.0175, longitude = 12.5135,
    updated_at = NOW()
WHERE slug = 'leonardos-bottega';

COMMIT;

-- Verification: show all 14 cast members with their new values
SELECT
    slug,
    display_name,
    LEFT(banner_url, 60) || '...' AS banner_url,
    latitude,
    longitude
FROM bh_user
WHERE slug IN (
    'sallys-kitchen', 'mikes-garage', 'angel-hq', 'ninos-campers',
    'marias-garden', 'marcos-workshop', 'jakes-electronics', 'rosas-home',
    'georges-villa', 'johns-cleaning', 'pietros-drones', 'sofias-bakes',
    'annes-qa-lab', 'leonardos-bottega'
)
ORDER BY slug;
