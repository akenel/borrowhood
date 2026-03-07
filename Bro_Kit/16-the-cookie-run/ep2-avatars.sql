-- EP2 Avatar Update: Add portrait photos for 14 demo cast members
-- Run: ssh root@46.62.138.218 "docker exec -i postgres psql -U helix_user -d borrowhood" < Bro_Kit/16-the-cookie-run/ep2-avatars.sql

BEGIN;

UPDATE bh_user SET avatar_url = 'https://images.unsplash.com/photo-1594744803329-e58b31de8bf5?w=200&h=200&fit=crop&crop=face' WHERE slug = 'sallys-kitchen';
UPDATE bh_user SET avatar_url = 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&crop=face' WHERE slug = 'mikes-garage';
UPDATE bh_user SET avatar_url = 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200&h=200&fit=crop&crop=face' WHERE slug = 'angel-hq';
UPDATE bh_user SET avatar_url = 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=200&h=200&fit=crop&crop=face' WHERE slug = 'ninos-campers';
UPDATE bh_user SET avatar_url = 'https://images.unsplash.com/photo-1580489944761-15a19d654956?w=200&h=200&fit=crop&crop=face' WHERE slug = 'marias-garden';
UPDATE bh_user SET avatar_url = 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&h=200&fit=crop&crop=face' WHERE slug = 'marcos-workshop';
UPDATE bh_user SET avatar_url = 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=200&h=200&fit=crop&crop=face' WHERE slug = 'jakes-electronics';
UPDATE bh_user SET avatar_url = 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=200&h=200&fit=crop&crop=face' WHERE slug = 'rosas-home';
UPDATE bh_user SET avatar_url = 'https://images.unsplash.com/photo-1504257432389-52343af06ae3?w=200&h=200&fit=crop&crop=face' WHERE slug = 'georges-villa';
UPDATE bh_user SET avatar_url = 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=200&h=200&fit=crop&crop=face' WHERE slug = 'johns-cleaning';
UPDATE bh_user SET avatar_url = 'https://images.unsplash.com/photo-1531891437562-4301cf35b7e4?w=200&h=200&fit=crop&crop=face' WHERE slug = 'pietros-drones';
UPDATE bh_user SET avatar_url = 'https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?w=200&h=200&fit=crop&crop=face' WHERE slug = 'sofias-bakes';
UPDATE bh_user SET avatar_url = 'https://images.unsplash.com/photo-1531123897727-8f129e1688ce?w=200&h=200&fit=crop&crop=face' WHERE slug = 'annes-qa-lab';
UPDATE bh_user SET avatar_url = 'https://images.unsplash.com/photo-1552058544-f2b08422138a?w=200&h=200&fit=crop&crop=face' WHERE slug = 'leonardos-bottega';

COMMIT;

-- Verify
SELECT slug, display_name, LEFT(avatar_url, 60) AS avatar FROM bh_user
WHERE slug IN ('sallys-kitchen','mikes-garage','angel-hq','ninos-campers','marias-garden',
'marcos-workshop','jakes-electronics','rosas-home','georges-villa','johns-cleaning',
'pietros-drones','sofias-bakes','annes-qa-lab','leonardos-bottega')
ORDER BY display_name;
