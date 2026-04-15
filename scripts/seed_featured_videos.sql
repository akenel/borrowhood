-- Seed featured_video_url for canonical Season-1 cast members.
--
-- Picks are thematic best-guesses. If any video ID 404s the iframe
-- will show "video unavailable" but the page still renders fine.
-- Swap via Dashboard -> Profile or rerun this script with better IDs.

BEGIN;

-- Angel / Black Wolf Workshop -- Bruce Lee "Be Water, my friend"
UPDATE bh_user SET featured_video_url = 'https://www.youtube.com/watch?v=uk1bVX0KPNE'
WHERE email = 'angel@borrowhood.local';

-- Leonardo / Bottega di Leonardo -- Paul Sellers hand-tool craft
UPDATE bh_user SET featured_video_url = 'https://www.youtube.com/watch?v=oNIRKPLwHhY'
WHERE email = 'leonardo@borrowhood.local';

-- Sally / Sally's Kitchen -- Bon Appetit sourdough (long-form baking)
UPDATE bh_user SET featured_video_url = 'https://www.youtube.com/watch?v=bmmicT0VrQ0'
WHERE email = 'sally@borrowhood.local';

-- Mike / Mike's Tool Shed -- MIG welding fundamentals
UPDATE bh_user SET featured_video_url = 'https://www.youtube.com/watch?v=nP_6EfbRYEY'
WHERE email = 'mike@borrowhood.local';

-- Pietro / SkyView Sicilia -- Sicily from a drone
UPDATE bh_user SET featured_video_url = 'https://www.youtube.com/watch?v=JpY_X43JpdI'
WHERE email = 'pietro@borrowhood.local';

-- Nicolò / Nic's Dojo -- BJJ fundamentals
UPDATE bh_user SET featured_video_url = 'https://www.youtube.com/watch?v=JxiCKnG7Plk'
WHERE email = 'roccamenanicolo@gmail.com';

-- Nino / Camper & Tour Trapani -- campervan Italy tour
UPDATE bh_user SET featured_video_url = 'https://www.youtube.com/watch?v=FWK2MZJaA_4'
WHERE email = 'nino@borrowhood.local';

-- Verify
SELECT display_name, slug, featured_video_url
FROM bh_user
WHERE featured_video_url IS NOT NULL
ORDER BY display_name;

COMMIT;
