-- Cap Simon's seeded raffles at EUR 10 pot (newcomer tier) and create
-- proper bh_raffle rows so they display on /raffles.
--
-- Why: newcomer cap is EUR 10 (RAFFLE_TRUST_TIERS[0]). Prior seeds created
-- bh_listing rows of type=RAFFLE with unbounded max_tickets, bypassing the
-- gate and orphan of a bh_raffle row. This tune-up is idempotent.
--
-- Run: docker exec postgres psql -U helix_user -d borrowhood < seed_simon_raffles_cap_at_10.sql

BEGIN;

-- 1. Cap self-defense raffle at EUR 0.50 x 20 = EUR 10 (accessible: 20 kids with pocket money)
UPDATE bh_item SET
    description = 'One lucky winner gets the full 4-week Women''s Self-Defense Course, free. EUR 0.50 per ticket, 20 tickets total, draw in 10 days. Every euro goes toward more free seats for young women in Enna. No platform fees, no cuts.'
WHERE slug = 'white-hammer-womens-self-defense-raffle';

UPDATE bh_listing SET price = 0.50, currency = 'EUR', max_participants = 20
WHERE item_id IN (SELECT id FROM bh_item WHERE slug = 'white-hammer-womens-self-defense-raffle')
  AND listing_type = 'RAFFLE';

-- 2. Cap coaching raffle at EUR 1.00 x 10 = EUR 10
--    (was EUR 5 x unbounded; now one session per winner, 10 tickets)
UPDATE bh_item SET
    name = 'Raffle: 1 Private Coaching Session',
    description = 'One hour private coaching. EUR 1 ticket, 10 tickets total, draw in 2 weeks. Proceeds go back into gear for the community youth program.'
WHERE slug = 'white-hammer-coaching-raffle';

UPDATE bh_listing SET price = 1.00, currency = 'EUR', max_participants = 10
WHERE item_id IN (SELECT id FROM bh_item WHERE slug = 'white-hammer-coaching-raffle')
  AND listing_type = 'RAFFLE';

-- 3. Insert bh_raffle rows for each of Simon's raffle listings (idempotent via NOT EXISTS)
--    Newcomer tier is fine: 2 raffles x EUR 10 each is within the EUR 10 per-raffle cap.
WITH simon AS (
    SELECT id FROM bh_user WHERE email = 'simon.divinti3@gmail.com'
),
raffle_listings AS (
    SELECT l.id AS listing_id, l.price, l.max_participants, l.item_id
    FROM bh_listing l
    JOIN bh_item i ON i.id = l.item_id
    WHERE i.owner_id = (SELECT id FROM simon)
      AND l.listing_type = 'RAFFLE'
      AND l.deleted_at IS NULL
)
INSERT INTO bh_raffle (id, listing_id, organizer_id, ticket_price, currency,
                       max_tickets, tickets_sold, tickets_reserved, ticket_hold_hours,
                       draw_type, draw_date, status, payment_methods, payment_instructions,
                       delivery_method, organizer_raffle_count, tos_accepted_at,
                       verifications_positive, verifications_negative,
                       created_at, updated_at)
SELECT gen_random_uuid(),
       rl.listing_id,
       (SELECT id FROM simon),
       rl.price,
       'EUR',
       COALESCE(rl.max_participants, 5),
       0,
       0,
       48,
       'DATE'::raffledrawtype,
       NOW() + INTERVAL '10 days',
       'ACTIVE'::rafflestatus,
       ARRAY['cash','paypal','satispay']::varchar[],
       'Pay Simon in cash at the gym or via PayPal / Satispay. Include your ticket number.',
       'PICKUP'::raffledelivery,
       0,
       NOW(),
       0,
       0,
       NOW(), NOW()
FROM raffle_listings rl
WHERE NOT EXISTS (
    SELECT 1 FROM bh_raffle r WHERE r.listing_id = rl.listing_id
);

-- 4. Summary so we can eyeball it
SELECT i.slug,
       l.price AS ticket_price,
       r.max_tickets,
       (r.ticket_price * r.max_tickets) AS pot_eur,
       r.status
FROM bh_item i
JOIN bh_listing l ON l.item_id = i.id
LEFT JOIN bh_raffle r ON r.listing_id = l.id
WHERE i.owner_id = (SELECT id FROM bh_user WHERE email = 'simon.divinti3@gmail.com')
  AND l.listing_type = 'RAFFLE';

COMMIT;
