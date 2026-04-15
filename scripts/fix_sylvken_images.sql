-- Fix SylvKen's World: all 6 fashion listings using same woodworking placeholder.
-- Replace first-image URL per listing with a unique Pollinations-generated
-- fashion/textile photo matching the actual product.

BEGIN;

-- Helper: find each item + its first-sorted media row, replace URL.
UPDATE bh_item_media m
SET url = 'https://image.pollinations.ai/prompt/elegant%20camel%20wool%20coat%20hanging%20on%20minimal%20wooden%20hanger%20soft%20natural%20light%20fashion%20photography?width=800&height=600&nologo=true'
FROM bh_item i WHERE m.item_id = i.id AND i.slug = 'max-mara-wool-coat-pre-owned-luxury';

UPDATE bh_item_media m
SET url = 'https://image.pollinations.ai/prompt/designer%20cocktail%20dress%20black%20elegant%20hanging%20boutique%20fashion%20photography%20soft%20light?width=800&height=600&nologo=true'
FROM bh_item i WHERE m.item_id = i.id AND i.slug = 'derek-lam-designer-dress-new-with-tags';

UPDATE bh_item_media m
SET url = 'https://image.pollinations.ai/prompt/personal%20stylist%20woman%20helping%20client%20choose%20outfit%20boutique%20mirror%20soft%20warm%20light?width=800&height=600&nologo=true'
FROM bh_item i WHERE m.item_id = i.id AND i.slug = 'personal-styling-consultation-find-your-look';

UPDATE bh_item_media m
SET url = 'https://image.pollinations.ai/prompt/organized%20wardrobe%20closet%20clothes%20on%20wooden%20hangers%20neat%20minimalist%20interior%20photography?width=800&height=600&nologo=true'
FROM bh_item i WHERE m.item_id = i.id AND i.slug = 'wardrobe-declutter-upcycle-service';

UPDATE bh_item_media m
SET url = 'https://image.pollinations.ai/prompt/japanese%20sashiko%20embroidery%20indigo%20boro%20textile%20needle%20thread%20craft%20workshop%20close%20up?width=800&height=600&nologo=true'
FROM bh_item i WHERE m.item_id = i.id AND i.slug = 'japanese-textile-workshop-sashiko-boro';

UPDATE bh_item_media m
SET url = 'https://image.pollinations.ai/prompt/vintage%20designer%20leather%20handbag%20auction%20luxury%20authenticated%20on%20marble%20surface%20soft%20light?width=800&height=600&nologo=true'
FROM bh_item i WHERE m.item_id = i.id AND i.slug = 'vintage-designer-handbag-authenticated-luxury-auction';

-- Verify
SELECT i.slug, m.url
FROM bh_item_media m
JOIN bh_item i ON i.id = m.item_id
JOIN bh_user u ON u.id = i.owner_id
WHERE u.slug = 'sylvkensworld'
ORDER BY i.created_at DESC;

COMMIT;
