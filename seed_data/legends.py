"""Legend seed data generator.

Generates artists, inventors, and creators from antiquity to modern era.
Each legend gets: full identity (mother, father, DOB, birthplace),
workshop profile, skills, and 2-3 items to rent/lend/teach.

Run: python seed_data/legends.py
Output: merges into seed_data/seed.json
"""

LEGENDS = [
    # ============================================================
    # WAVE 0: ITEMS FOR EXISTING 26 LEGENDS (computing + rock)
    # ============================================================
    # (handled separately below)

    # ============================================================
    # WAVE 1: ANCIENT WORLD (before 500 AD)
    # ============================================================
    {
        "slug": "homers-epic-tent",
        "display_name": "Homer",
        "email": "homer@borrowhood.local",
        "date_of_birth": "0800-01-01",
        "mother_name": "Kretheis -- according to the ancient tradition of Smyrna",
        "father_name": "Maeon -- or perhaps the river Meles, depending on which legend you believe",
        "workshop_name": "Homer's Epic Tent",
        "workshop_type": "studio",
        "tagline": "Sing, O Muse, of the man of many ways",
        "bio": "Born somewhere in Ionia -- Smyrna, Chios, or Colophon, depending on which city is lying. Seven cities claim me. None can prove it. I may have been blind. I may have been many people. I may not have existed at all. But the Iliad and the Odyssey exist, and that is enough. 27,803 lines of poetry composed and memorized without writing. The entire Western literary tradition starts with a man who couldn't see, reciting from memory. Every war story is the Iliad. Every journey home is the Odyssey. Every hero who refuses to die quietly is Achilles. Every man trying to get back to his family is Odysseus.",
        "telegram_username": "the_bard",
        "city": "Smyrna",
        "country_code": "TR",
        "latitude": 38.419,
        "longitude": 27.129,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "el", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Epic Poetry", "category": "art", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Oral Storytelling", "category": "art", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Lyre Playing", "category": "music", "self_rating": 4, "years_experience": 40},
            {"skill_name": "Memory Palace", "category": "education", "self_rating": 5, "years_experience": 50}
        ],
        "social_links": [],
        "points": {"total_points": 1800, "rentals_completed": 50, "reviews_given": 40, "reviews_received": 60, "items_listed": 6, "helpful_flags": 35},
        "offers_training": True,
        "items": [
            {
                "name": "Lyre (7-String, Tortoiseshell)",
                "slug": "lyre-7-string-tortoiseshell",
                "description": "Handmade tortoiseshell lyre with gut strings. The same instrument I used to accompany 27,803 lines of epic poetry. Tuned to the Dorian mode. I'll teach you the basic scales if you ask.",
                "item_type": "physical",
                "category": "music",
                "listings": [{"listing_type": "rent", "price": 3.0, "price_unit": "per_day", "currency": "EUR"}]
            },
            {
                "name": "Epic Poetry Masterclass -- Oral Composition",
                "slug": "epic-poetry-masterclass-oral",
                "description": "Learn to compose and perform epic poetry from memory. No writing allowed. I'll teach you formulaic composition -- the technique of building poems from reusable phrases so you can improvise for hours. Bring wine. It helps.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "service", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "sapphos-garden",
        "display_name": "Sappho of Lesbos",
        "email": "sappho@borrowhood.local",
        "date_of_birth": "0630-01-01",
        "mother_name": "Kleis",
        "father_name": "Skamandronymos",
        "workshop_name": "Sappho's Garden",
        "workshop_type": "garden",
        "tagline": "What is beautiful is good, and who is good will soon be beautiful",
        "bio": "Born on the island of Lesbos. They called me the Tenth Muse. Plato said that. I ran a school for young women -- music, poetry, dance, the art of being fully alive. The ancients had nine books of my poetry. The Christians burned most of it. Only one complete poem survives and fragments of the rest. They burned the woman who wrote about love between women. But the fragments endure. A line here, a stanza there, pulled from papyrus wrapped around mummies in Egypt. I taught that love is a loosener of limbs, bittersweet, an irresistible creature. Two and a half thousand years later, people still feel exactly what I described.",
        "telegram_username": "tenth_muse",
        "city": "Mytilene",
        "country_code": "GR",
        "latitude": 39.104,
        "longitude": 26.548,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "el", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Lyric Poetry", "category": "art", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Music Composition", "category": "music", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Teaching", "category": "education", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Lyre Playing", "category": "music", "self_rating": 5, "years_experience": 40}
        ],
        "social_links": [],
        "points": {"total_points": 1600, "rentals_completed": 42, "reviews_given": 38, "reviews_received": 55, "items_listed": 5, "helpful_flags": 30},
        "offers_training": True,
        "items": [
            {
                "name": "Poetry Writing Workshop -- Finding Your Voice",
                "slug": "poetry-workshop-finding-voice",
                "description": "Small group poetry workshop in my garden. We write, we read aloud, we revise. I focus on lyric poetry -- short, intense, personal. Bring something you've been afraid to say. That's where the poem lives.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 10.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Herb Garden Access -- Mediterranean Herbs",
                "slug": "herb-garden-access-mediterranean",
                "description": "Pick fresh herbs from my garden: rosemary, thyme, oregano, basil, mint, bay leaf, lavender. Poets need gardens and gardens need poets. Take what you need, leave the roots.",
                "item_type": "space",
                "category": "garden",
                "listings": [{"listing_type": "offer", "price": 2.0, "price_unit": "per_visit", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "euclids-proof-room",
        "display_name": "Euclid of Alexandria",
        "email": "euclid@borrowhood.local",
        "date_of_birth": "0325-01-01",
        "mother_name": "Unknown -- Alexandria kept no birth records for mathematicians",
        "father_name": "Naucrates -- according to later Arab sources",
        "workshop_name": "Euclid's Proof Room",
        "workshop_type": "office",
        "tagline": "There is no royal road to geometry",
        "bio": "Born in Alexandria, Egypt -- or perhaps Athens. I wrote the Elements. Thirteen books. 465 propositions. Every one proven from five axioms. It remained the standard textbook for mathematics for 2,300 years. Lincoln taught himself logic by reading my proofs by candlelight. When King Ptolemy asked me for a shortcut to learning geometry, I told him there is no royal road. No shortcuts. No hacks. You start with the axioms and you build. Every step follows from the last. That's not just mathematics. That's how you build anything that lasts.",
        "telegram_username": "no_royal_road",
        "city": "Alexandria",
        "country_code": "EG",
        "latitude": 31.200,
        "longitude": 29.919,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "el", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Geometry", "category": "science", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Mathematical Proof", "category": "science", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Teaching", "category": "education", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Optics", "category": "science", "self_rating": 4, "years_experience": 20}
        ],
        "social_links": [],
        "points": {"total_points": 1500, "rentals_completed": 38, "reviews_given": 35, "reviews_received": 50, "items_listed": 5, "helpful_flags": 28},
        "offers_training": True,
        "items": [
            {
                "name": "Geometry Tutoring -- From Axioms to Proofs",
                "slug": "geometry-tutoring-axioms-proofs",
                "description": "Private or small group geometry lessons. We start from five axioms and build everything. No calculators. No shortcuts. Compass, straightedge, and your mind. I've been doing this for 2,300 years and the method hasn't changed because it doesn't need to.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 12.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Compass and Straightedge Set (Brass)",
                "slug": "compass-straightedge-set-brass",
                "description": "Professional brass compass and straightedge. The only two tools you need to construct any geometric figure. Euclid approved.",
                "item_type": "physical",
                "category": "tools",
                "listings": [{"listing_type": "rent", "price": 2.0, "price_unit": "per_day", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "archimedes-workshop",
        "display_name": "Archimedes of Syracuse",
        "email": "archimedes@borrowhood.local",
        "date_of_birth": "0287-01-01",
        "mother_name": "Unknown -- but she raised the man who moved the Earth",
        "father_name": "Phidias the astronomer",
        "workshop_name": "Archimedes' Workshop",
        "workshop_type": "workshop",
        "tagline": "Give me a lever long enough and a fulcrum on which to place it, and I shall move the world",
        "bio": "Born in Syracuse, Sicily. Yes, SICILY. The greatest mathematician and engineer of antiquity was Sicilian. Father Phidias was an astronomer. I calculated pi to unprecedented precision. I discovered the principle of buoyancy in a bathtub and ran naked through the streets shouting EUREKA. I invented the Archimedean screw (still used today to pump water), compound pulleys, and war machines that held off the Roman navy for two years. When the Romans finally took Syracuse, a soldier found me drawing circles in the sand. I said 'Do not disturb my circles.' He killed me anyway. The moral: never interrupt a mathematician.",
        "telegram_username": "eureka_man",
        "city": "Syracuse",
        "country_code": "IT",
        "latitude": 37.075,
        "longitude": 15.286,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "el", "proficiency": "native"},
            {"language_code": "la", "proficiency": "B1"}
        ],
        "skills": [
            {"skill_name": "Mathematics", "category": "science", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Mechanical Engineering", "category": "engineering", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Hydraulics", "category": "engineering", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Optics", "category": "science", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Military Engineering", "category": "engineering", "self_rating": 5, "years_experience": 20}
        ],
        "social_links": [],
        "points": {"total_points": 1700, "rentals_completed": 45, "reviews_given": 35, "reviews_received": 58, "items_listed": 8, "helpful_flags": 32},
        "offers_training": True,
        "offers_repair": True,
        "items": [
            {
                "name": "Archimedean Screw Pump (Working Model)",
                "slug": "archimedean-screw-pump-model",
                "description": "Working model of my water-lifting screw. Turns by hand, lifts water uphill. Still the best irrigation device for low-tech farming. I invented this 2,300 years ago and nobody's improved on it.",
                "item_type": "physical",
                "category": "garden",
                "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR"}]
            },
            {
                "name": "Physics & Engineering Tutoring -- Levers, Pulleys, Buoyancy",
                "slug": "physics-engineering-tutoring-levers",
                "description": "Hands-on physics lessons using real machines. We'll build levers, compound pulleys, and test buoyancy in water. You'll understand why ships float, how cranes work, and how I held off the Roman navy with math and mirrors.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Block and Tackle Pulley System (4:1 Mechanical Advantage)",
                "slug": "block-tackle-pulley-4-1",
                "description": "My compound pulley design. 4:1 mechanical advantage. Lift 400kg with 100kg of force. I once pulled an entire ship onto shore using one of these to prove a point to King Hieron. Bring your own rope.",
                "item_type": "physical",
                "category": "tools",
                "listings": [{"listing_type": "rent", "price": 8.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0}]
            }
        ]
    },
    {
        "slug": "hypatias-academy",
        "display_name": "Hypatia of Alexandria",
        "email": "hypatia@borrowhood.local",
        "date_of_birth": "0360-01-01",
        "mother_name": "Unknown -- history recorded her father but not her mother, as usual",
        "father_name": "Theon of Alexandria",
        "workshop_name": "Hypatia's Academy",
        "workshop_type": "office",
        "tagline": "Reserve your right to think, for even to think wrongly is better than not to think at all",
        "bio": "Born in Alexandria, Egypt. Father Theon was the last head of the Library of Alexandria. He educated me in mathematics, astronomy, and philosophy -- unusual for a woman in any century, let alone the 4th. I became head of the Neoplatonist school. I taught senators, governors, the prefect of Egypt. I improved the astrolabe, invented a hydrometer for measuring water density, and edited my father's commentary on Euclid. In 415 AD, a Christian mob dragged me from my carriage, stripped me, and murdered me with roofing tiles in a church. Because I was a pagan woman who taught men to think. The Library burned. The academy closed. The Dark Ages began. Think about that when someone tells you knowledge is optional.",
        "telegram_username": "hypatia_thinks",
        "city": "Alexandria",
        "country_code": "EG",
        "latitude": 31.205,
        "longitude": 29.925,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "el", "proficiency": "native"},
            {"language_code": "la", "proficiency": "C1"}
        ],
        "skills": [
            {"skill_name": "Mathematics", "category": "science", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Astronomy", "category": "science", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Philosophy", "category": "other", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Instrument Making", "category": "engineering", "self_rating": 4, "years_experience": 20},
            {"skill_name": "Teaching", "category": "education", "self_rating": 5, "years_experience": 25}
        ],
        "social_links": [],
        "points": {"total_points": 1550, "rentals_completed": 40, "reviews_given": 35, "reviews_received": 52, "items_listed": 6, "helpful_flags": 28},
        "offers_training": True,
        "items": [
            {
                "name": "Astrolabe (Improved Hypatia Design)",
                "slug": "astrolabe-hypatia-design",
                "description": "My improved astrolabe design. Measures the altitude of stars and planets, tells time, finds latitude. The GPS of antiquity. Brass construction, hand-engraved. I'll teach you to read the sky.",
                "item_type": "physical",
                "category": "tools",
                "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR", "deposit": 25.0}]
            },
            {
                "name": "Philosophy & Critical Thinking Workshop",
                "slug": "philosophy-critical-thinking-workshop",
                "description": "Small group discussion on logic, ethics, and how to think clearly when everyone around you is losing their minds. No dogma. No doctrine. Just questions and the courage to follow them wherever they lead. I died for this. The least you can do is show up.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 10.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # WAVE 2: MEDIEVAL / RENAISSANCE (500 - 1600)
    # ============================================================
    {
        "slug": "runos-poetry-hall",
        "display_name": "Jalal ad-Din Muhammad Rumi",
        "email": "rumi@borrowhood.local",
        "date_of_birth": "1207-09-30",
        "mother_name": "Mu'mina Khatun",
        "father_name": "Baha ud-Din Walad",
        "workshop_name": "Rumi's Poetry Hall",
        "workshop_type": "studio",
        "tagline": "The wound is the place where the light enters you",
        "bio": "Born in Balkh, Greater Khorasan -- modern Afghanistan. Father was a theologian and mystic. We fled the Mongol invasion when I was a child, walked 4,000 miles to Anatolia. I became a respected scholar, a jurist, a teacher. Then I met Shams of Tabriz and everything changed. He was a wandering mystic who challenged everything I believed. When he disappeared -- murdered, probably, by my jealous disciples -- I poured my grief into poetry. 70,000 verses. The Masnavi alone is 25,000 couplets. I wrote in Persian but the love is universal. I didn't stop teaching. I spun. Literally -- the Whirling Dervishes are my students, still spinning 800 years later.",
        "telegram_username": "whirling_poet",
        "city": "Konya",
        "country_code": "TR",
        "latitude": 37.871,
        "longitude": 32.484,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "fa", "proficiency": "native"},
            {"language_code": "ar", "proficiency": "C2"},
            {"language_code": "tr", "proficiency": "C1"},
            {"language_code": "el", "proficiency": "B1"}
        ],
        "skills": [
            {"skill_name": "Poetry", "category": "art", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Sufi Philosophy", "category": "other", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Whirling Dance", "category": "sports", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Teaching", "category": "education", "self_rating": 5, "years_experience": 40}
        ],
        "social_links": [],
        "points": {"total_points": 1650, "rentals_completed": 44, "reviews_given": 40, "reviews_received": 56, "items_listed": 5, "helpful_flags": 32},
        "offers_training": True,
        "items": [
            {
                "name": "Poetry & Meditation Session -- The Way of the Heart",
                "slug": "poetry-meditation-heart",
                "description": "We read poetry. We sit in silence. We spin. This is not a class -- it's a practice. Bring nothing but yourself. Leave your opinions at the door. The heart knows things the mind will never understand.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 0.0, "price_unit": "free", "currency": "EUR", "notes": "Free. Always free. Love doesn't invoice."}]
            }
        ]
    },
    {
        "slug": "dantes-inferno-desk",
        "display_name": "Dante Alighieri",
        "email": "dante@borrowhood.local",
        "date_of_birth": "1265-06-01",
        "mother_name": "Bella degli Abati",
        "father_name": "Alighiero di Bellincione",
        "workshop_name": "Dante's Writing Desk",
        "workshop_type": "office",
        "tagline": "In the middle of the journey of our life, I found myself in a dark wood",
        "bio": "Born in Florence. Mother Bella died when I was young. Father remarried. I fell in love with Beatrice Portinari when I was nine years old. She died at 24. I spent the rest of my life writing about her. The Divine Comedy -- Inferno, Purgatorio, Paradiso -- is the journey of the human soul from darkness to light. 14,233 lines in terza rima. I wrote it in Italian, not Latin, because I wanted everyone to read it, not just priests. Florence exiled me for my politics. I never went home. I wandered Italy for 20 years, writing the greatest poem in the Western world while sleeping in other people's houses. An exile wrote the book that defined Italian literature. Sometimes you have to lose your home to find your voice.",
        "telegram_username": "dark_wood",
        "city": "Florence",
        "country_code": "IT",
        "latitude": 43.771,
        "longitude": 11.254,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "it", "proficiency": "native"},
            {"language_code": "la", "proficiency": "C2"},
            {"language_code": "fr", "proficiency": "B2"}
        ],
        "skills": [
            {"skill_name": "Poetry", "category": "art", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Political Philosophy", "category": "other", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Linguistics", "category": "education", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Surviving Exile", "category": "other", "self_rating": 5, "years_experience": 20}
        ],
        "social_links": [],
        "points": {"total_points": 1500, "rentals_completed": 38, "reviews_given": 30, "reviews_received": 50, "items_listed": 4, "helpful_flags": 28},
        "offers_training": True,
        "items": [
            {
                "name": "Italian Literature Tutoring -- Dante to Calvino",
                "slug": "italian-literature-tutoring",
                "description": "Read the Comedy with someone who wrote it. I'll explain the cosmology, the politics, the theology, and the jokes (yes, there are jokes). Also available: Italian language lessons through poetry. You'll learn Italian the way Italians actually feel it.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 12.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Calligraphy Set -- Medieval Italian Script",
                "slug": "calligraphy-set-medieval-italian",
                "description": "Quills, iron gall ink, parchment. The tools I used to write 14,233 lines by hand. I'll show you how to hold the quill and form the letters. Your handwriting will never be the same.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 4.0, "price_unit": "per_day", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "michelangelos-scaffold",
        "display_name": "Michelangelo di Lodovico Buonarroti Simoni",
        "email": "michelangelo@borrowhood.local",
        "date_of_birth": "1475-03-06",
        "mother_name": "Francesca di Neri del Miniato di Siena",
        "father_name": "Lodovico di Leonardo Buonarroti Simoni",
        "workshop_name": "Michelangelo's Scaffold",
        "workshop_type": "studio",
        "tagline": "I saw the angel in the marble and carved until I set him free",
        "bio": "Born in Caprese, Republic of Florence. Mother Francesca died when I was six. Father sent me to a wet nurse in a family of stonecutters -- I joked that I sucked marble dust with my mother's milk. I carved the Pieta at 24. David at 29. Then Pope Julius II made me paint the Sistine Chapel ceiling -- 12,000 square feet, lying on my back on scaffolding for four years. I was a sculptor forced to paint. It's the most famous ceiling in the world. I also designed the dome of St. Peter's Basilica, the largest dome in Christendom. I worked until I was 88. I never married. I slept in my boots. I ate bread and wine at my workbench. The marble was enough.",
        "telegram_username": "marble_angel",
        "city": "Caprese",
        "country_code": "IT",
        "latitude": 43.640,
        "longitude": 11.986,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "it", "proficiency": "native"},
            {"language_code": "la", "proficiency": "C1"}
        ],
        "skills": [
            {"skill_name": "Sculpture", "category": "art", "self_rating": 5, "years_experience": 70},
            {"skill_name": "Painting", "category": "art", "self_rating": 5, "years_experience": 60},
            {"skill_name": "Architecture", "category": "engineering", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Poetry", "category": "art", "self_rating": 4, "years_experience": 50},
            {"skill_name": "Stubbornness", "category": "other", "self_rating": 5, "years_experience": 88}
        ],
        "social_links": [],
        "points": {"total_points": 1750, "rentals_completed": 48, "reviews_given": 30, "reviews_received": 62, "items_listed": 8, "helpful_flags": 28},
        "offers_training": True,
        "offers_custom_orders": True,
        "items": [
            {
                "name": "Marble Sculpting Tools (Professional Set)",
                "slug": "marble-sculpting-tools-professional",
                "description": "Point chisel, tooth chisel, flat chisel, claw chisel, rasps, rifflers. The same tool types I used on the David. Carbide-tipped for modern marble. I'll show you how to find the figure hiding in the stone.",
                "item_type": "physical",
                "category": "tools",
                "listings": [{"listing_type": "rent", "price": 10.0, "price_unit": "per_day", "currency": "EUR", "deposit": 50.0}]
            },
            {
                "name": "Fresco Painting Workshop -- Wet Plaster Technique",
                "slug": "fresco-painting-workshop-wet-plaster",
                "description": "Learn buon fresco: painting directly onto wet plaster so the pigment becomes part of the wall. You have about 8 hours before it dries. No corrections. No undo button. The technique is 3,000 years old and it's still the most permanent form of painting that exists.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Scaffolding System (Adjustable, Indoor Use)",
                "slug": "scaffolding-system-adjustable-indoor",
                "description": "Aluminum scaffolding tower, adjustable height up to 6 meters. Platform, guard rails, locking casters. I spent 4 years on scaffolding painting the Sistine Chapel. You probably need it for a weekend to paint your ceiling. Trust me, a ladder is not enough.",
                "item_type": "physical",
                "category": "tools",
                "listings": [{"listing_type": "rent", "price": 15.0, "price_unit": "per_day", "currency": "EUR", "deposit": 100.0}]
            }
        ]
    },
    {
        "slug": "shakespeares-globe",
        "display_name": "William Shakespeare",
        "email": "william@borrowhood.local",
        "date_of_birth": "1564-04-26",
        "mother_name": "Mary Arden",
        "father_name": "John Shakespeare",
        "workshop_name": "Shakespeare's Globe",
        "workshop_type": "studio",
        "tagline": "All the world's a stage, and all the men and women merely players",
        "bio": "Born in Stratford-upon-Avon. Father John was a glove maker and alderman. Mother Mary Arden came from minor gentry -- she brought the land, he brought the craft. I wrote 37 plays, 154 sonnets, and invented roughly 1,700 words in the English language. Assassination. Eyeball. Lonely. Manager. You're welcome. I was an actor, a playwright, a shareholder in the Globe Theatre, and a businessman. I bought the second-largest house in Stratford with my theatre money. The conspiracy theorists say I didn't write the plays because a glove maker's son from the countryside couldn't be a genius. They're snobs. Genius doesn't need a pedigree. It needs a stage.",
        "telegram_username": "the_bard_will",
        "city": "Stratford-upon-Avon",
        "country_code": "GB",
        "latitude": 52.194,
        "longitude": -1.708,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "la", "proficiency": "C1"},
            {"language_code": "fr", "proficiency": "B2"},
            {"language_code": "it", "proficiency": "B1"}
        ],
        "skills": [
            {"skill_name": "Playwriting", "category": "art", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Acting", "category": "art", "self_rating": 4, "years_experience": 25},
            {"skill_name": "Poetry", "category": "art", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Theatre Management", "category": "other", "self_rating": 4, "years_experience": 20},
            {"skill_name": "Inventing Words", "category": "other", "self_rating": 5, "years_experience": 25}
        ],
        "social_links": [],
        "points": {"total_points": 1800, "rentals_completed": 50, "reviews_given": 40, "reviews_received": 65, "items_listed": 7, "helpful_flags": 35},
        "offers_training": True,
        "items": [
            {
                "name": "Acting Workshop -- Shakespeare for Beginners",
                "slug": "acting-workshop-shakespeare-beginners",
                "description": "Learn to perform Shakespeare without being terrified of the language. We start with the insults (those are the fun part), work through the monologues, and end with a scene. No experience needed. Just a voice and a willingness to look foolish -- that's how all great actors start.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 12.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Complete Works of Shakespeare (Annotated, Hardbound)",
                "slug": "complete-works-shakespeare-annotated",
                "description": "Every play, every sonnet, every poem. Annotated with historical context, word definitions, and stage directions. 1,200 pages. This is the entire human condition bound in leather. Borrow it, read one play, return it. Or keep it for a month and read them all.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 2.0, "price_unit": "per_week", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # WAVE 3: BAROQUE / CLASSICAL (1600 - 1800)
    # ============================================================
    {
        "slug": "caravaggios-dark-room",
        "display_name": "Michelangelo Merisi da Caravaggio",
        "email": "caravaggio@borrowhood.local",
        "date_of_birth": "1571-09-29",
        "mother_name": "Lucia Aratori",
        "father_name": "Fermo Merisi",
        "workshop_name": "Caravaggio's Dark Room",
        "workshop_type": "studio",
        "tagline": "Without light, there is no art -- and without darkness, there is no drama",
        "bio": "Born in Milan -- or Caravaggio, the town I'm named after. Father Fermo died of plague when I was six. Mother Lucia died five years later. Orphan at eleven. I went to Rome with nothing and became the most revolutionary painter of my age. Chiaroscuro -- extreme contrast between light and dark. I painted saints as street people, the Virgin Mary as a drowned prostitute pulled from the Tiber. The Church was horrified. They also couldn't stop buying my paintings. I killed a man in a brawl over a tennis match. Fled Rome. Painted masterpieces while on the run through Naples, Malta, and Sicily. Died on a beach at 38, alone, waiting for a papal pardon that arrived two days late. Every film noir, every dramatic photograph, every Scorsese movie -- that's my light.",
        "telegram_username": "chiaroscuro",
        "city": "Milan",
        "country_code": "IT",
        "latitude": 45.464,
        "longitude": 9.190,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "it", "proficiency": "native"},
            {"language_code": "la", "proficiency": "B2"}
        ],
        "skills": [
            {"skill_name": "Oil Painting", "category": "art", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Chiaroscuro Lighting", "category": "art", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Street Fighting", "category": "sports", "self_rating": 4, "years_experience": 15},
            {"skill_name": "Fleeing Authorities", "category": "other", "self_rating": 5, "years_experience": 10}
        ],
        "social_links": [],
        "points": {"total_points": 1400, "rentals_completed": 35, "reviews_given": 20, "reviews_received": 48, "items_listed": 6, "helpful_flags": 18},
        "offers_training": True,
        "items": [
            {
                "name": "Dramatic Lighting Workshop -- Chiaroscuro for Photographers",
                "slug": "chiaroscuro-lighting-workshop",
                "description": "One light source. Complete darkness. That's all you need for the most dramatic images in the world. I'll teach you to see light the way I painted it -- as a weapon. Works for painters, photographers, and filmmakers. Bring your camera or your canvas.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Oil Paint Set -- Old Masters Palette (Earth Tones)",
                "slug": "oil-paint-set-old-masters-earth-tones",
                "description": "Lead white, yellow ochre, raw umber, burnt sienna, vermillion, bone black. The exact palette I used. Six colors. That's enough to paint anything if you understand value. Modern cadmium substitutes included because lead will kill you.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 6.0, "price_unit": "per_day", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "rembrandts-light-studio",
        "display_name": "Rembrandt Harmenszoon van Rijn",
        "email": "rembrandt@borrowhood.local",
        "date_of_birth": "1606-07-15",
        "mother_name": "Neeltgen Willemsdochter van Zuytbrouck",
        "father_name": "Harmen Gerritszoon van Rijn",
        "workshop_name": "Rembrandt's Light Studio",
        "workshop_type": "studio",
        "tagline": "Choose only one master -- Nature",
        "bio": "Born in Leiden, Dutch Republic. Father was a miller. Mother was a baker's daughter. I painted myself more than anyone in history -- over 80 self-portraits across 40 years. Not vanity. Documentation. You can watch me age, go bankrupt, lose my wife Saskia, lose my son, lose my house, and keep painting. I went from the richest artist in Amsterdam to bankruptcy. I painted my best work after I lost everything. The Night Watch, The Jewish Bride, The Return of the Prodigal Son. I used light like Caravaggio but warmer, gentler. His light interrogates. Mine forgives. I also ran the largest printmaking studio in Holland. Etchings were my side hustle.",
        "telegram_username": "night_watch",
        "city": "Leiden",
        "country_code": "NL",
        "latitude": 52.160,
        "longitude": 4.495,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "nl", "proficiency": "native"},
            {"language_code": "la", "proficiency": "B1"}
        ],
        "skills": [
            {"skill_name": "Oil Painting", "category": "art", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Etching & Printmaking", "category": "art", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Self-Portraiture", "category": "art", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Bankruptcy Survival", "category": "other", "self_rating": 5, "years_experience": 15}
        ],
        "social_links": [],
        "points": {"total_points": 1550, "rentals_completed": 40, "reviews_given": 32, "reviews_received": 52, "items_listed": 7, "helpful_flags": 25},
        "offers_training": True,
        "items": [
            {
                "name": "Etching Press (Tabletop, Adjustable Pressure)",
                "slug": "etching-press-tabletop-adjustable",
                "description": "Tabletop intaglio press for etching, drypoint, and aquatint. Adjustable pressure, steel rollers. I produced 300 etchings on a press like this. Print editions of your drawings, or learn the process from scratch.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 12.0, "price_unit": "per_day", "currency": "EUR", "deposit": 60.0}]
            },
            {
                "name": "Portrait Painting Lesson -- Light, Shadow, and Soul",
                "slug": "portrait-painting-lesson-light-shadow",
                "description": "I'll teach you to paint a face that looks like a person, not a photograph. We work in oil on canvas, natural light from one window. The secret isn't technique -- it's empathy. You have to love the face you're painting, even the ugly ones. Especially the ugly ones.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "bachs-organ-loft",
        "display_name": "Johann Sebastian Bach",
        "email": "bach@borrowhood.local",
        "date_of_birth": "1685-03-31",
        "mother_name": "Maria Elisabeth Lammerhirt",
        "father_name": "Johann Ambrosius Bach",
        "workshop_name": "Bach's Organ Loft",
        "workshop_type": "studio",
        "tagline": "The aim and final end of all music should be none other than the glory of God and the refreshment of the soul",
        "bio": "Born in Eisenach, Thuringia. Orphaned at ten -- mother Maria Elisabeth died when I was nine, father Johann Ambrosius the next year. Raised by my eldest brother. The Bach family had been professional musicians for seven generations. I wrote over 1,100 compositions. The Well-Tempered Clavier, the Brandenburg Concertos, the Mass in B Minor, the St. Matthew Passion. I fathered 20 children with two wives. I walked 250 miles to hear Buxtehude play organ. I was jailed for a month for demanding better working conditions. When I went blind at 65, I dictated my last chorale from memory: 'Before Thy Throne I Now Appear.' Mozart studied me. Beethoven called me the father of harmony. They forgot me for 80 years until Mendelssohn revived my music. The architecture holds. It always holds.",
        "telegram_username": "fugue_master",
        "city": "Eisenach",
        "country_code": "DE",
        "latitude": 50.974,
        "longitude": 10.320,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "de", "proficiency": "native"},
            {"language_code": "la", "proficiency": "C1"},
            {"language_code": "it", "proficiency": "B1"}
        ],
        "skills": [
            {"skill_name": "Organ", "category": "music", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Composition", "category": "music", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Harpsichord", "category": "music", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Violin", "category": "music", "self_rating": 4, "years_experience": 40},
            {"skill_name": "Counterpoint", "category": "music", "self_rating": 5, "years_experience": 50}
        ],
        "social_links": [],
        "points": {"total_points": 1700, "rentals_completed": 45, "reviews_given": 35, "reviews_received": 58, "items_listed": 8, "helpful_flags": 30},
        "offers_training": True,
        "items": [
            {
                "name": "Harpsichord (Double Manual, Concert Quality)",
                "slug": "harpsichord-double-manual-concert",
                "description": "Franco-Flemish double-manual harpsichord. Two 8-foot registers, one 4-foot. Proper temperament for Baroque repertoire. I wrote the Well-Tempered Clavier to prove every key was playable. This instrument proves it. Tuning included -- I'll come tune it at your venue.",
                "item_type": "physical",
                "category": "music",
                "listings": [{"listing_type": "rent", "price": 25.0, "price_unit": "per_day", "currency": "EUR", "deposit": 200.0}]
            },
            {
                "name": "Counterpoint & Fugue Composition Lesson",
                "slug": "counterpoint-fugue-lesson",
                "description": "Learn to write a fugue. Two voices, then three, then four. Each voice independent, all voices together forming something greater than the sum. This is not just music theory -- it's how to think in parallel. Programmers love it. Every thread independent, every thread synchronized.",
                "item_type": "service",
                "category": "music",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "mozarts-piano-room",
        "display_name": "Wolfgang Amadeus Mozart",
        "email": "mozart@borrowhood.local",
        "date_of_birth": "1756-01-27",
        "mother_name": "Anna Maria Walburga Pertl",
        "father_name": "Johann Georg Leopold Mozart",
        "workshop_name": "Mozart's Piano Room",
        "workshop_type": "studio",
        "tagline": "Neither a lofty degree of intelligence nor imagination nor both together go to the making of genius. Love, love, love -- that is the soul of genius",
        "bio": "Born in Salzburg. Father Leopold was a violinist and composer who recognized my talent before I could tie my shoes. I played harpsichord at 3, composed at 5, toured Europe at 6. By 12 I had written my first opera. 626 works in 35 years. Symphonies, concertos, operas, string quartets, masses, sonatas. I could hear a piece once and write it down from memory. I wrote the overture to Don Giovanni the morning of the premiere, ink still wet when the orchestra sight-read it. They say I died poor. I died in debt, which is different. I was the highest-paid musician in Vienna. I also spent like a man who knew he wouldn't live to 40. I was right.",
        "telegram_username": "amadeus",
        "city": "Salzburg",
        "country_code": "AT",
        "latitude": 47.802,
        "longitude": 13.044,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "de", "proficiency": "native"},
            {"language_code": "it", "proficiency": "C2"},
            {"language_code": "fr", "proficiency": "C1"},
            {"language_code": "en", "proficiency": "B1"},
            {"language_code": "la", "proficiency": "B2"}
        ],
        "skills": [
            {"skill_name": "Composition", "category": "music", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Piano", "category": "music", "self_rating": 5, "years_experience": 32},
            {"skill_name": "Violin", "category": "music", "self_rating": 4, "years_experience": 25},
            {"skill_name": "Opera", "category": "music", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Toilet Humor", "category": "other", "self_rating": 5, "years_experience": 35}
        ],
        "social_links": [],
        "points": {"total_points": 1800, "rentals_completed": 50, "reviews_given": 40, "reviews_received": 65, "items_listed": 8, "helpful_flags": 35},
        "offers_training": True,
        "items": [
            {
                "name": "Fortepiano (Walter & Sohn Style Replica)",
                "slug": "fortepiano-walter-replica",
                "description": "Replica of my Walter fortepiano -- the instrument I actually played, not a modern Steinway. Lighter action, clearer tone, closer to what I heard when I composed. Perfect for performing Mozart, Haydn, early Beethoven the way it was meant to sound.",
                "item_type": "physical",
                "category": "music",
                "listings": [{"listing_type": "rent", "price": 30.0, "price_unit": "per_day", "currency": "EUR", "deposit": 250.0}]
            },
            {
                "name": "Music Composition Masterclass -- From Melody to Symphony",
                "slug": "composition-masterclass-melody-symphony",
                "description": "I'll teach you what my father taught me: start with a melody that a child can hum. Then build. Harmony, counterpoint, orchestration. A symphony is just a melody that grew up. No prior theory needed -- if you can sing, you can compose.",
                "item_type": "service",
                "category": "music",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "beethovens-deaf-room",
        "display_name": "Ludwig van Beethoven",
        "email": "beethoven@borrowhood.local",
        "date_of_birth": "1770-12-17",
        "mother_name": "Maria Magdalena Keverich",
        "father_name": "Johann van Beethoven",
        "workshop_name": "Beethoven's Deaf Room",
        "workshop_type": "studio",
        "tagline": "I shall seize fate by the throat. It will never wholly overcome me",
        "bio": "Born in Bonn. Father Johann was a drunk who beat me to make me practice. Mother Maria Magdalena was the gentle one -- she died when I was 16 and I became head of the household at 17, supporting two younger brothers. I went deaf. Gradually, then completely. The greatest composer in history could not hear his greatest works. I composed the Ninth Symphony -- 'Ode to Joy,' the anthem of the European Union -- completely deaf. At the premiere, I kept conducting after the orchestra finished because I couldn't hear the audience exploding behind me. A musician turned me around to see the standing ovation. I wept. I sawed the legs off my pianos and put them on the floor so I could feel the vibrations through my body. The music was always there. The ears were optional.",
        "telegram_username": "fate_throat",
        "city": "Bonn",
        "country_code": "DE",
        "latitude": 50.735,
        "longitude": 7.099,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "de", "proficiency": "native"},
            {"language_code": "fr", "proficiency": "B2"},
            {"language_code": "it", "proficiency": "B1"},
            {"language_code": "la", "proficiency": "B1"}
        ],
        "skills": [
            {"skill_name": "Composition", "category": "music", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Piano", "category": "music", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Conducting", "category": "music", "self_rating": 4, "years_experience": 30},
            {"skill_name": "Composing While Deaf", "category": "music", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Seizing Fate by the Throat", "category": "other", "self_rating": 5, "years_experience": 56}
        ],
        "social_links": [],
        "points": {"total_points": 1850, "rentals_completed": 48, "reviews_given": 35, "reviews_received": 62, "items_listed": 7, "helpful_flags": 35},
        "offers_training": True,
        "items": [
            {
                "name": "Piano Lesson -- Beethoven Sonatas (All Levels)",
                "slug": "piano-lesson-beethoven-sonatas",
                "description": "Learn to play my sonatas. Moonlight, Pathetique, Appassionata, Waldstein, Hammerklavier. We start with the ones you can handle and work up to the ones that break you. The Hammerklavier has destroyed better pianists than you. That's what makes it worth trying.",
                "item_type": "service",
                "category": "music",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Ear Trumpets (Collection of 4, Historical Replicas)",
                "slug": "ear-trumpets-historical-replicas",
                "description": "Four hearing devices from different periods of my deafness, faithfully reproduced. From the early brass cone to the elaborate conversation devices Johann Maelzel built for me. A sobering reminder that the most famous music in history was composed in silence.",
                "item_type": "physical",
                "category": "other",
                "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # WAVE 4: ROMANTIC / IMPRESSIONIST / 19TH CENTURY (1800 - 1900)
    # ============================================================
    {
        "slug": "van-goghs-yellow-house",
        "display_name": "Vincent Willem van Gogh",
        "email": "vincent@borrowhood.local",
        "date_of_birth": "1853-03-30",
        "mother_name": "Anna Cornelia Carbentus",
        "father_name": "Theodorus van Gogh",
        "workshop_name": "Van Gogh's Yellow House",
        "workshop_type": "studio",
        "tagline": "I dream my painting and I paint my dream",
        "bio": "Born in Groot-Zundert, Netherlands. Father Theodorus was a Protestant minister. Mother Anna Cornelia never quite recovered from the stillborn son born exactly one year before me -- also named Vincent. I walked past his grave every day as a child. My name on a headstone. I tried being an art dealer, a teacher, a preacher in Belgian coal mines. All failures. I started painting at 27. In ten years I produced 2,100 artworks -- 860 oil paintings. I sold one in my lifetime. One. My brother Theo believed in me when no one else did. He sent money every month. The Starry Night, Sunflowers, the self-portraits -- all painted by a man the world called a failure. I shot myself in a wheat field at 37. Theo died six months later. They're buried side by side. The paintings that nobody wanted are now worth billions. Timing is everything. Mine was terrible.",
        "telegram_username": "starry_night",
        "city": "Groot-Zundert",
        "country_code": "NL",
        "latitude": 51.472,
        "longitude": 4.636,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "nl", "proficiency": "native"},
            {"language_code": "fr", "proficiency": "C1"},
            {"language_code": "en", "proficiency": "B2"},
            {"language_code": "de", "proficiency": "B1"}
        ],
        "skills": [
            {"skill_name": "Oil Painting", "category": "art", "self_rating": 5, "years_experience": 10},
            {"skill_name": "Drawing", "category": "art", "self_rating": 5, "years_experience": 12},
            {"skill_name": "Color Theory", "category": "art", "self_rating": 5, "years_experience": 8},
            {"skill_name": "Letter Writing", "category": "other", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Surviving Rejection", "category": "other", "self_rating": 5, "years_experience": 37}
        ],
        "social_links": [],
        "points": {"total_points": 1650, "rentals_completed": 42, "reviews_given": 38, "reviews_received": 56, "items_listed": 7, "helpful_flags": 30},
        "offers_training": True,
        "items": [
            {
                "name": "Plein Air Painting Kit -- Portable Easel + Supplies",
                "slug": "plein-air-painting-kit-portable",
                "description": "French box easel, oil paints (18 colors including chrome yellow -- my obsession), brushes, turpentine, linseed oil, and 6 pre-stretched canvases. Everything you need to paint outdoors the way the Impressionists did. Go to a wheat field. Set up. Paint what you feel, not what you see.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 10.0, "price_unit": "per_day", "currency": "EUR", "deposit": 40.0}]
            },
            {
                "name": "Expressive Painting Workshop -- Color as Emotion",
                "slug": "expressive-painting-workshop-color-emotion",
                "description": "I don't teach technique. I teach seeing. We go outside, we look at the sky, and I show you that it's not blue -- it's cobalt and ultramarine and violet and green, swirling. The color is the feeling. The brushstroke is the heartbeat. If your painting looks like a photograph, you're not painting -- you're copying.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "fridas-blue-house",
        "display_name": "Magdalena Carmen Frida Kahlo Calderon",
        "email": "frida@borrowhood.local",
        "date_of_birth": "1907-07-06",
        "mother_name": "Matilde Calderon y Gonzalez",
        "father_name": "Carl Wilhelm Kahlo (Guillermo Kahlo)",
        "workshop_name": "Frida's Blue House",
        "workshop_type": "studio",
        "tagline": "I paint myself because I am so often alone and because I am the subject I know best",
        "bio": "Born in Coyoacan, Mexico City. Father Guillermo was a German-Hungarian photographer who taught me to look. Mother Matilde was Mexican mestiza -- strong, devout, furious. At six I got polio. At eighteen a bus crash broke my spine, my collarbone, my ribs, my pelvis, and my right leg in eleven places. A steel handrail impaled me through the hip. I lay in a full body cast for months. My mother put a mirror on the ceiling above my bed. I started painting what I saw: myself. 55 self-portraits out of 143 paintings. They're not vanity -- they're inventory. Here's my broken column. Here's my miscarriage. Here's my heart outside my body. Diego Rivera was the love of my life and the worst pain of my life, which is saying something for a woman who had 30 surgeries. Viva la vida.",
        "telegram_username": "viva_la_vida",
        "city": "Mexico City",
        "country_code": "MX",
        "latitude": 19.355,
        "longitude": -99.162,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "es", "proficiency": "native"},
            {"language_code": "en", "proficiency": "B2"},
            {"language_code": "de", "proficiency": "B1"},
            {"language_code": "fr", "proficiency": "A2"}
        ],
        "skills": [
            {"skill_name": "Oil Painting", "category": "art", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Self-Portraiture", "category": "art", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Mexican Folk Art", "category": "art", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Photography", "category": "art", "self_rating": 3, "years_experience": 15},
            {"skill_name": "Surviving Everything", "category": "other", "self_rating": 5, "years_experience": 47}
        ],
        "social_links": [],
        "points": {"total_points": 1580, "rentals_completed": 40, "reviews_given": 35, "reviews_received": 54, "items_listed": 6, "helpful_flags": 28},
        "offers_training": True,
        "items": [
            {
                "name": "Self-Portrait Workshop -- Painting Your Truth",
                "slug": "self-portrait-workshop-painting-truth",
                "description": "Forget flattering yourself. Paint what's real. The scars, the joy, the fury, the love. We work in oil or acrylic on small canvases. I'll teach you about color symbolism from Mexican folk art -- what red means, what blue means, why I put monkeys and parrots in my paintings. Bring a mirror. Bring honesty.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Mexican Folk Art Supplies -- Retablo Painting Kit",
                "slug": "mexican-folk-art-retablo-kit",
                "description": "Small tin sheets, oil paints, fine brushes. Everything for painting retablos -- the small votive paintings I collected and was inspired by. Paint your miracle, your gratitude, your survival. The format is tiny. The feeling is enormous.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # WAVE 5: ROMANTIC / IMPRESSIONIST / LITERARY (1800 - 1900)
    # ============================================================
    {
        "slug": "chopins-piano-room",
        "display_name": "Frederic Chopin",
        "email": "chopin@borrowhood.local",
        "date_of_birth": "1810-03-01",
        "mother_name": "Tekla Justyna Krzyzanowska",
        "father_name": "Nicolas Chopin",
        "workshop_name": "Chopin's Piano Room",
        "workshop_type": "studio",
        "tagline": "Simplicity is the final achievement -- after one has played a vast quantity of notes",
        "bio": "Born in Zelazowa Wola, Poland. Father Nicolas was French, mother Justyna was Polish. I gave my first public concert at eight. Left Poland at twenty. Never went back. Paris adopted me. I gave perhaps thirty public concerts in my entire life -- I preferred drawing rooms, intimate spaces, fifty people maximum. I wrote almost exclusively for piano. 230 works. Every one a miniature universe. The Nocturnes are what loneliness sounds like when it becomes beautiful. The Ballades are entire novels compressed into twelve minutes. I died at 39 of tuberculosis in Paris. My heart was smuggled back to Warsaw in a jar of cognac. It's still there, in a pillar of the Holy Cross Church. Poland wouldn't let my heart stay in exile.",
        "telegram_username": "nocturne_poet",
        "city": "Zelazowa Wola",
        "country_code": "PL",
        "latitude": 52.083,
        "longitude": 20.306,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "pl", "proficiency": "native"},
            {"language_code": "fr", "proficiency": "C2"}
        ],
        "skills": [
            {"skill_name": "Piano Performance", "category": "music", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Composition", "category": "music", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Music Teaching", "category": "education", "self_rating": 5, "years_experience": 20}
        ],
        "social_links": [],
        "points": {"total_points": 1600, "rentals_completed": 42, "reviews_given": 35, "reviews_received": 55, "items_listed": 5, "helpful_flags": 30},
        "offers_training": True,
        "items": [
            {
                "name": "Piano Masterclass -- Chopin Technique",
                "slug": "piano-masterclass-chopin-technique",
                "description": "Private piano lessons focusing on touch, pedaling, and rubato. I don't teach you to play loud. I teach you to play with feeling. Bring your worst piece -- we'll find the music hiding inside it.",
                "item_type": "service",
                "category": "music",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Pleyel Upright Piano (1840 Replica)",
                "slug": "pleyel-upright-piano-1840",
                "description": "Replica of the Pleyel pianos I played in Paris. Lighter action than modern grands. The tone is intimate, almost whispering. Perfect for nocturnes. Tuned to A=430Hz (period pitch).",
                "item_type": "physical",
                "category": "music",
                "listings": [{"listing_type": "rent", "price": 25.0, "price_unit": "per_day", "currency": "EUR", "deposit": 200.0}]
            }
        ]
    },
    {
        "slug": "tchaikovskys-concert-hall",
        "display_name": "Pyotr Ilyich Tchaikovsky",
        "email": "tchaikovsky@borrowhood.local",
        "date_of_birth": "1840-05-07",
        "mother_name": "Alexandra Andreyevna d'Assier",
        "father_name": "Ilya Petrovich Tchaikovsky",
        "workshop_name": "Tchaikovsky's Concert Hall",
        "workshop_type": "studio",
        "tagline": "Inspiration is a guest that does not willingly visit the lazy",
        "bio": "Born in Votkinsk, Russia. Mother Alexandra was of French descent -- she died of cholera when I was fourteen. That loss never healed. I became a lawyer first, then abandoned law for music at twenty-one. My father supported the change. I wrote Swan Lake, The Nutcracker, Sleeping Beauty, the 1812 Overture, six symphonies. The Sixth -- Pathetique -- premiered nine days before my death. Some say I was forced to take poison because of my homosexuality. Others say cholera. Either way, Russia killed me young. But every December, in every city on Earth, children watch The Nutcracker. That's immortality.",
        "telegram_username": "swan_lake_pyotr",
        "city": "Votkinsk",
        "country_code": "RU",
        "latitude": 57.050,
        "longitude": 54.000,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "ru", "proficiency": "native"},
            {"language_code": "fr", "proficiency": "C2"},
            {"language_code": "de", "proficiency": "B2"}
        ],
        "skills": [
            {"skill_name": "Orchestral Composition", "category": "music", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Ballet Scoring", "category": "music", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Conducting", "category": "music", "self_rating": 4, "years_experience": 20}
        ],
        "social_links": [],
        "points": {"total_points": 1550, "rentals_completed": 40, "reviews_given": 30, "reviews_received": 52, "items_listed": 5, "helpful_flags": 28},
        "offers_training": True,
        "items": [
            {
                "name": "Orchestration Workshop -- Scoring for Ballet",
                "slug": "orchestration-workshop-ballet-scoring",
                "description": "Learn to write music that makes bodies move. I'll teach you orchestral color -- how a celesta sounds like falling snow, how a bassoon sounds like a grandfather clock. We score a dance scene from scratch.",
                "item_type": "service",
                "category": "music",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "monets-water-garden",
        "display_name": "Claude Monet",
        "email": "monet@borrowhood.local",
        "date_of_birth": "1840-11-14",
        "mother_name": "Louise Justine Aubree",
        "father_name": "Claude Adolphe Monet",
        "workshop_name": "Monet's Water Garden",
        "workshop_type": "garden",
        "tagline": "I must have flowers, always, and always",
        "bio": "Born in Paris, grew up in Le Havre on the Normandy coast. Mother Louise was a singer, father ran a grocery. She died when I was sixteen. I dropped out of school to draw caricatures and sell them for twenty francs each. Went to Paris, went to war, went broke, went to Giverny. I painted the same haystacks in different light. The same cathedral at different hours. The same water lilies for thirty years. They called it Impressionism as an insult -- from my painting 'Impression, Sunrise.' I took the insult and made it a movement. I designed my garden at Giverny specifically to paint it. The garden was the art. The art was the garden. I went nearly blind in my last years but kept painting. The late water lilies are eight feet wide -- enormous, abstract, the bridge between Impressionism and everything that came after.",
        "telegram_username": "impression_sunrise",
        "city": "Paris",
        "country_code": "FR",
        "latitude": 48.856,
        "longitude": 2.352,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "fr", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Oil Painting", "category": "art", "self_rating": 5, "years_experience": 60},
            {"skill_name": "Plein Air Painting", "category": "art", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Garden Design", "category": "garden", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Color Theory", "category": "art", "self_rating": 5, "years_experience": 50}
        ],
        "social_links": [],
        "points": {"total_points": 1650, "rentals_completed": 44, "reviews_given": 35, "reviews_received": 56, "items_listed": 6, "helpful_flags": 30},
        "offers_training": True,
        "items": [
            {
                "name": "Plein Air Painting Kit (French Easel + Oils)",
                "slug": "plein-air-painting-kit-french-easel",
                "description": "Portable French easel, oil paints (Winsor & Newton), brushes, canvas boards. Everything you need to paint outdoors. I spent sixty years painting outside. The light changes every five minutes. That's not a problem. That's the point.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 12.0, "price_unit": "per_day", "currency": "EUR", "deposit": 60.0}]
            },
            {
                "name": "Garden Design Consultation -- Creating a Painting Garden",
                "slug": "garden-design-painting-garden",
                "description": "I'll help you design a garden that's beautiful to paint, not just beautiful to look at. Color masses, reflection pools, arched bridges, seasonal bloom sequences. A garden is a canvas that grows.",
                "item_type": "service",
                "category": "garden",
                "listings": [{"listing_type": "service", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "twains-riverboat-office",
        "display_name": "Mark Twain",
        "email": "twain@borrowhood.local",
        "date_of_birth": "1835-11-30",
        "mother_name": "Jane Lampton Clemens",
        "father_name": "John Marshall Clemens",
        "workshop_name": "Twain's Riverboat Office",
        "workshop_type": "office",
        "tagline": "The secret of getting ahead is getting started",
        "bio": "Born Samuel Langhorne Clemens in Florida, Missouri. Father John was a lawyer and judge who died when I was eleven, leaving the family in debt. Mother Jane was funny, stubborn, and kind to animals -- I got my sense of humor from her. I became a printer's apprentice at twelve. A riverboat pilot at twenty-two. A silver miner. A journalist. Finally a writer. Mark Twain means 'two fathoms deep' -- safe water. Huckleberry Finn is the great American novel because it's about a boy and a runaway slave on a raft, and the boy chooses the slave over civilization. 'All right then, I'll go to hell.' Best line in American literature. I went bankrupt, lost a daughter, lost my wife. Finished my life in a white suit, smoking cigars, making people laugh while his heart was breaking.",
        "telegram_username": "mark_twain_sam",
        "city": "Florida",
        "country_code": "US",
        "latitude": 39.497,
        "longitude": -91.815,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "de", "proficiency": "B1"}
        ],
        "skills": [
            {"skill_name": "Satirical Writing", "category": "art", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Public Speaking", "category": "other", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Riverboat Piloting", "category": "other", "self_rating": 4, "years_experience": 4},
            {"skill_name": "Cigar Appreciation", "category": "other", "self_rating": 5, "years_experience": 50}
        ],
        "social_links": [],
        "points": {"total_points": 1500, "rentals_completed": 38, "reviews_given": 40, "reviews_received": 50, "items_listed": 5, "helpful_flags": 32},
        "offers_training": True,
        "items": [
            {
                "name": "Writing Workshop -- Finding Your Voice Through Humor",
                "slug": "writing-workshop-humor-voice",
                "description": "The human race has one really effective weapon, and that is laughter. I'll teach you to use it. We'll work on voice, timing, and the art of saying true things that make people laugh instead of cry. Bring something you've written. I'll be honest. Honest is all I know how to be.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 12.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "dickens-reading-room",
        "display_name": "Charles Dickens",
        "email": "dickens@borrowhood.local",
        "date_of_birth": "1812-02-07",
        "mother_name": "Elizabeth Culliford Barrow",
        "father_name": "John Dickens",
        "workshop_name": "Dickens' Reading Room",
        "workshop_type": "office",
        "tagline": "It was the best of times, it was the worst of times",
        "bio": "Born in Portsmouth, England. Father John was a Navy pay clerk who couldn't manage money -- he went to debtor's prison when I was twelve. Mother Elizabeth wanted me to keep working at the blacking factory that crushed my soul. I never forgave her. That anger fueled fifteen novels. I wrote Oliver Twist, David Copperfield, Great Expectations, A Tale of Two Cities, A Christmas Carol. Serial publication -- a chapter a week -- I invented the cliffhanger. I gave public readings that filled theatres. I campaigned for children's rights, education reform, sanitation. Every Christmas you feel generous? That's me. Scrooge is the most reformed character in literature. I proved that a story can change how an entire society thinks about poverty.",
        "telegram_username": "boz_dickens",
        "city": "Portsmouth",
        "country_code": "GB",
        "latitude": 50.805,
        "longitude": -1.087,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "fr", "proficiency": "B2"}
        ],
        "skills": [
            {"skill_name": "Novel Writing", "category": "art", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Public Reading", "category": "art", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Social Reform", "category": "other", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Serial Storytelling", "category": "art", "self_rating": 5, "years_experience": 30}
        ],
        "social_links": [],
        "points": {"total_points": 1550, "rentals_completed": 40, "reviews_given": 35, "reviews_received": 52, "items_listed": 5, "helpful_flags": 28},
        "offers_training": True,
        "items": [
            {
                "name": "Storytelling Masterclass -- The Serial Cliffhanger",
                "slug": "storytelling-masterclass-serial-cliffhanger",
                "description": "Learn to structure stories that people can't stop reading. We work on chapter endings, pacing, character reveals, and the art of making your audience come back next week. I wrote A Christmas Carol in six weeks and it changed Western culture. Speed is not the enemy of quality.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "tolstoys-estate",
        "display_name": "Leo Tolstoy",
        "email": "tolstoy@borrowhood.local",
        "date_of_birth": "1828-09-09",
        "mother_name": "Maria Nikolayevna Volkonskaya",
        "father_name": "Count Nikolai Ilyich Tolstoy",
        "workshop_name": "Tolstoy's Writing Estate",
        "workshop_type": "office",
        "tagline": "Everyone thinks of changing the world, but no one thinks of changing himself",
        "bio": "Born at Yasnaya Polyana, 200 km south of Moscow. Mother Maria died when I was two. Father Nikolai when I was nine. Raised by relatives. I was an aristocrat, a soldier, a gambler, a womanizer -- then I wrote War and Peace and Anna Karenina and became the moral conscience of Russia. War and Peace is 1,225 pages. 580 characters. I rewrote it seven times. My wife Sophia copied it out by hand -- all seven drafts. I freed my serfs before the Emancipation. I started schools for peasant children. I renounced my copyright, my wealth, my title. Gandhi read me and started a revolution. Martin Luther King Jr. read me and started a movement. At eighty-two I left home in the middle of the night, trying to live as a simple pilgrim. I died at a train station ten days later.",
        "telegram_username": "yasnaya_leo",
        "city": "Yasnaya Polyana",
        "country_code": "RU",
        "latitude": 54.075,
        "longitude": 37.527,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "ru", "proficiency": "native"},
            {"language_code": "fr", "proficiency": "C2"},
            {"language_code": "de", "proficiency": "C1"},
            {"language_code": "en", "proficiency": "B2"}
        ],
        "skills": [
            {"skill_name": "Novel Writing", "category": "art", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Philosophy", "category": "other", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Teaching", "category": "education", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Farming", "category": "garden", "self_rating": 4, "years_experience": 40}
        ],
        "social_links": [],
        "points": {"total_points": 1700, "rentals_completed": 45, "reviews_given": 40, "reviews_received": 58, "items_listed": 6, "helpful_flags": 35},
        "offers_training": True,
        "items": [
            {
                "name": "Epic Novel Writing Workshop -- Structure for 500+ Pages",
                "slug": "epic-novel-writing-workshop-500-pages",
                "description": "How to write a book that contains an entire world. We'll study structure, character management (I juggled 580 characters in War and Peace), and the art of the long form. This is not for short-attention spans. This is for people who want to build cathedrals.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "dumas-adventure-desk",
        "display_name": "Alexandre Dumas",
        "email": "dumas@borrowhood.local",
        "date_of_birth": "1802-07-24",
        "mother_name": "Marie-Louise Elisabeth Labouret",
        "father_name": "Thomas-Alexandre Dumas",
        "workshop_name": "Dumas' Adventure Desk",
        "workshop_type": "office",
        "tagline": "All for one, and one for all!",
        "bio": "Born in Villers-Cotterets, France. Father Thomas-Alexandre was a general -- the highest-ranking person of African descent in a European army. Son of a French nobleman and an enslaved woman in Haiti. He was the strongest man in the French army. Napoleon hated him. When he died, I was three, and we were broke. Mother Marie-Louise raised me alone. I went to Paris with nothing and became the most popular writer in France. The Three Musketeers. The Count of Monte Cristo. I wrote 100,000 pages in my lifetime -- 277 novels, plus plays, travelogues, cookbooks. I hired assistants, sure. But every page has my voice. I lived like my characters -- extravagant, generous, broke, in love with everything. My father was Black, and the racists never let me forget it. I never let it stop me.",
        "telegram_username": "all_for_one",
        "city": "Villers-Cotterets",
        "country_code": "FR",
        "latitude": 49.253,
        "longitude": 3.086,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "fr", "proficiency": "native"},
            {"language_code": "it", "proficiency": "C1"},
            {"language_code": "es", "proficiency": "B2"}
        ],
        "skills": [
            {"skill_name": "Adventure Writing", "category": "art", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Playwriting", "category": "art", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Fencing", "category": "sports", "self_rating": 4, "years_experience": 30},
            {"skill_name": "Cooking", "category": "kitchen", "self_rating": 4, "years_experience": 30}
        ],
        "social_links": [],
        "points": {"total_points": 1500, "rentals_completed": 38, "reviews_given": 35, "reviews_received": 50, "items_listed": 5, "helpful_flags": 28},
        "offers_training": True,
        "items": [
            {
                "name": "Fencing Lessons -- Classical French Swordsmanship",
                "slug": "fencing-lessons-classical-french",
                "description": "My father was the greatest swordsman in France. I learned enough to write convincing duels. I'll teach you the basics -- en garde, parry, riposte -- and the storytelling behind every fight scene. A duel is a conversation with sharps.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "emily-dickinsons-room",
        "display_name": "Emily Dickinson",
        "email": "emily.d@borrowhood.local",
        "date_of_birth": "1830-12-10",
        "mother_name": "Emily Norcross Dickinson",
        "father_name": "Edward Dickinson",
        "workshop_name": "Emily's Room",
        "workshop_type": "office",
        "tagline": "I dwell in Possibility -- a fairer House than Prose",
        "bio": "Born in Amherst, Massachusetts. Father Edward was a lawyer and congressman. Mother Emily Norcross was quiet, bookish, and often ill. I attended Mount Holyoke for one year and came home. I never left again, mostly. I wrote 1,775 poems in my bedroom. I published seven in my lifetime. Seven. The rest were found after my death in forty hand-sewn booklets -- fascicles -- in my bureau drawer. My sister Lavinia found them and saved them. I wrote about death more than anyone and I was more alive than everyone. I baked bread, tended my garden, wrote letters to the world. I lowered baskets of gingerbread from my window to neighborhood children. I chose to stay in my room. It wasn't a prison. It was a cathedral.",
        "telegram_username": "belle_of_amherst",
        "city": "Amherst",
        "country_code": "US",
        "latitude": 42.373,
        "longitude": -72.520,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Poetry", "category": "art", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Baking", "category": "kitchen", "self_rating": 4, "years_experience": 25},
            {"skill_name": "Gardening", "category": "garden", "self_rating": 4, "years_experience": 25},
            {"skill_name": "Letter Writing", "category": "art", "self_rating": 5, "years_experience": 30}
        ],
        "social_links": [],
        "points": {"total_points": 1400, "rentals_completed": 30, "reviews_given": 25, "reviews_received": 50, "items_listed": 4, "helpful_flags": 25},
        "offers_training": True,
        "items": [
            {
                "name": "Poetry Workshop -- Compression and White Space",
                "slug": "poetry-workshop-compression-white-space",
                "description": "Learn to say everything in four lines. We work on compression -- removing every word that isn't earning its place. Dashes are welcome. Capital Letters too. The goal is a poem so concentrated it detonates on contact.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 8.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # WAVE 6: EARLY MODERN / REVOLUTIONARY (1850 - 1950)
    # ============================================================
    {
        "slug": "teslas-laboratory",
        "display_name": "Nikola Tesla",
        "email": "tesla@borrowhood.local",
        "date_of_birth": "1856-07-10",
        "mother_name": "Djuka Mandic",
        "father_name": "Milutin Tesla",
        "workshop_name": "Tesla's Laboratory",
        "workshop_type": "workshop",
        "tagline": "The present is theirs; the future, for which I really worked, is mine",
        "bio": "Born in Smiljan, Austrian Empire -- modern Croatia. Father Milutin was a Serbian Orthodox priest. Mother Djuka never had formal education but she memorized Serbian epic poems and invented household tools -- I inherited my inventive mind from her. I saw the rotating magnetic field in a vision while walking in a park in Budapest. I built the AC motor, the AC power system, radio (before Marconi), the Tesla coil, fluorescent lighting, remote control. I lit 200 lamps twenty-five miles away with no wires. Edison offered me fifty thousand dollars to fix his DC system. I did it. He said 'You don't understand American humor' and didn't pay. I died alone in Room 3327 of the New Yorker Hotel, feeding pigeons. The FBI seized my papers. I gave the world alternating current and the world gave me a hotel room and a pigeon.",
        "telegram_username": "ac_lightning",
        "city": "Smiljan",
        "country_code": "HR",
        "latitude": 44.564,
        "longitude": 15.313,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "sr", "proficiency": "native"},
            {"language_code": "de", "proficiency": "C1"},
            {"language_code": "en", "proficiency": "C2"},
            {"language_code": "fr", "proficiency": "C1"},
            {"language_code": "it", "proficiency": "B2"}
        ],
        "skills": [
            {"skill_name": "Electrical Engineering", "category": "engineering", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Invention", "category": "engineering", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Physics", "category": "science", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Pigeon Care", "category": "other", "self_rating": 5, "years_experience": 30}
        ],
        "social_links": [],
        "points": {"total_points": 1800, "rentals_completed": 48, "reviews_given": 30, "reviews_received": 60, "items_listed": 8, "helpful_flags": 35},
        "offers_training": True,
        "offers_repair": True,
        "items": [
            {
                "name": "Tesla Coil Kit (Educational, Low Power)",
                "slug": "tesla-coil-kit-educational",
                "description": "Build your own Tesla coil. Educational kit with all components, safety instructions, and my original circuit diagrams. When you see lightning jump between your hands and the coil, you'll understand why I couldn't stop. Low power -- it tingles, it doesn't kill.",
                "item_type": "physical",
                "category": "tools",
                "listings": [{"listing_type": "rent", "price": 15.0, "price_unit": "per_day", "currency": "EUR", "deposit": 75.0}]
            },
            {
                "name": "Electrical Engineering Tutoring -- AC vs DC",
                "slug": "electrical-engineering-tutoring-ac-dc",
                "description": "I'll explain why alternating current won the War of Currents and why Edison was wrong. We cover electromagnetic induction, rotating magnetic fields, and power transmission. No prior knowledge needed -- just curiosity about why the lights come on.",
                "item_type": "service",
                "category": "science",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "picassos-blue-room",
        "display_name": "Pablo Picasso",
        "email": "picasso@borrowhood.local",
        "date_of_birth": "1881-10-25",
        "mother_name": "Maria Picasso y Lopez",
        "father_name": "Jose Ruiz y Blasco",
        "workshop_name": "Picasso's Blue Room",
        "workshop_type": "studio",
        "tagline": "Every child is an artist. The problem is how to remain an artist once we grow up",
        "bio": "Born in Malaga, Spain. Father Jose was an art teacher and painter. Mother Maria -- I took her name, not his. My father handed me his brushes and palette when I was thirteen and swore he would never paint again because I had surpassed him. I went through Blue Period, Rose Period, African Period, Cubism, Neoclassicism, Surrealism. I painted Guernica in five weeks after the Nazis bombed a Basque town. When a German officer saw a photograph of it and asked 'Did you do that?', I said 'No, you did.' I made 50,000 artworks in my lifetime. Paintings, sculptures, ceramics, prints, stage designs. I never stopped reinventing. The secret is not to find yourself. The secret is to invent yourself, over and over, until the world can't keep up.",
        "telegram_username": "cubist_pablo",
        "city": "Malaga",
        "country_code": "ES",
        "latitude": 36.721,
        "longitude": -4.421,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "es", "proficiency": "native"},
            {"language_code": "fr", "proficiency": "C2"},
            {"language_code": "ca", "proficiency": "B2"}
        ],
        "skills": [
            {"skill_name": "Painting", "category": "art", "self_rating": 5, "years_experience": 78},
            {"skill_name": "Sculpture", "category": "art", "self_rating": 5, "years_experience": 60},
            {"skill_name": "Ceramics", "category": "art", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Printmaking", "category": "art", "self_rating": 5, "years_experience": 50}
        ],
        "social_links": [],
        "points": {"total_points": 1800, "rentals_completed": 50, "reviews_given": 30, "reviews_received": 62, "items_listed": 8, "helpful_flags": 28},
        "offers_training": True,
        "offers_custom_orders": True,
        "items": [
            {
                "name": "Cubism Workshop -- See All Sides at Once",
                "slug": "cubism-workshop-all-sides",
                "description": "I'll teach you to draw a face from the front and side simultaneously. We'll break objects into geometric planes, reassemble them, and create something the camera can never capture. Cubism isn't abstract -- it's more real than reality. It shows everything at once.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Ceramics Studio Access -- Wheel + Kiln",
                "slug": "ceramics-studio-access-wheel-kiln",
                "description": "Potter's wheel, electric kiln, glazes, clay. I made over 4,000 ceramic pieces in Vallauris. Come shape something with your hands. The clay doesn't care about your reputation.",
                "item_type": "space",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 15.0, "price_unit": "per_day", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "klimts-golden-studio",
        "display_name": "Gustav Klimt",
        "email": "klimt@borrowhood.local",
        "date_of_birth": "1862-07-14",
        "mother_name": "Anna Finster",
        "father_name": "Ernst Klimt the Elder",
        "workshop_name": "Klimt's Golden Studio",
        "workshop_type": "studio",
        "tagline": "Art is a line around your thoughts",
        "bio": "Born in Baumgarten, Vienna. Father Ernst was a gold engraver -- that's where the gold came from. Mother Anna wanted to be a musician but poverty killed that dream. I learned to engrave before I learned to paint. I co-founded the Vienna Secession at thirty-five -- we broke away from the academic art establishment. I painted The Kiss, covered in gold leaf, the most reproduced painting of the twentieth century. I painted women -- powerful, erotic, unapologetic. The Austrian establishment called it pornography. I called it truth. I wore a blue smock, never a suit. I ate enormous breakfasts. I had more affairs than paintings. I never wrote about my art. 'If you want to find out about me, look at my paintings.' So look.",
        "telegram_username": "golden_gustav",
        "city": "Vienna",
        "country_code": "AT",
        "latitude": 48.208,
        "longitude": 16.373,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "de", "proficiency": "native"},
            {"language_code": "fr", "proficiency": "B2"}
        ],
        "skills": [
            {"skill_name": "Decorative Painting", "category": "art", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Gold Leaf Application", "category": "art", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Mural Painting", "category": "art", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Drawing", "category": "art", "self_rating": 5, "years_experience": 40}
        ],
        "social_links": [],
        "points": {"total_points": 1450, "rentals_completed": 35, "reviews_given": 25, "reviews_received": 48, "items_listed": 5, "helpful_flags": 22},
        "offers_training": True,
        "items": [
            {
                "name": "Gold Leaf Application Workshop -- Klimt Technique",
                "slug": "gold-leaf-workshop-klimt-technique",
                "description": "Learn to apply real gold leaf to paintings, furniture, or frames. I'll teach you the sizing, the breathing technique (one sneeze and twenty euros of gold blows away), and how to mix gold with oil paint for the effect you see in The Kiss. Materials included.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "chaplins-film-studio",
        "display_name": "Charlie Chaplin",
        "email": "chaplin@borrowhood.local",
        "date_of_birth": "1889-04-16",
        "mother_name": "Hannah Harriet Pedlingham Hill",
        "father_name": "Charles Spencer Chaplin Sr.",
        "workshop_name": "Chaplin's Film Studio",
        "workshop_type": "studio",
        "tagline": "A day without laughter is a day wasted",
        "bio": "Born in Walworth, London. Father Charles was a music hall singer who drank himself to death. Mother Hannah was a singer and actress whose voice gave out -- she went mad from syphilis and poverty. I was in the workhouse by age seven. I learned to be funny because it was that or starve. I went to America with a vaudeville troupe and never left. I created the Tramp -- bowler hat, cane, baggy trousers, tight coat, the waddle. He was every immigrant, every underdog, every little man crushed by the machine. I directed, wrote, produced, scored, and starred in my own films. I was the most famous person on Earth. America deported me during the Red Scare. I moved to Switzerland and lived another twenty-five years. The FBI file was 1,900 pages. My crime was making people think while they laughed.",
        "telegram_username": "the_tramp",
        "city": "London",
        "country_code": "GB",
        "latitude": 51.489,
        "longitude": -0.095,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "fr", "proficiency": "C1"}
        ],
        "skills": [
            {"skill_name": "Physical Comedy", "category": "art", "self_rating": 5, "years_experience": 60},
            {"skill_name": "Film Directing", "category": "art", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Screenwriting", "category": "art", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Violin", "category": "music", "self_rating": 4, "years_experience": 40},
            {"skill_name": "Film Scoring", "category": "music", "self_rating": 4, "years_experience": 30}
        ],
        "social_links": [],
        "points": {"total_points": 1700, "rentals_completed": 45, "reviews_given": 38, "reviews_received": 58, "items_listed": 6, "helpful_flags": 32},
        "offers_training": True,
        "items": [
            {
                "name": "Physical Comedy Workshop -- Tell a Story Without Words",
                "slug": "physical-comedy-workshop-no-words",
                "description": "I made the whole world laugh without saying a word. I'll teach you timing, the pratfall, the slow burn, the double take. Your body is the instrument. No props needed -- just your willingness to fall down and get back up. That's comedy. That's life.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "okeeffes-desert-studio",
        "display_name": "Georgia O'Keeffe",
        "email": "okeeffe@borrowhood.local",
        "date_of_birth": "1887-11-15",
        "mother_name": "Ida Ten Eyck Totto",
        "father_name": "Francis Calyxtus O'Keeffe",
        "workshop_name": "O'Keeffe's Desert Studio",
        "workshop_type": "studio",
        "tagline": "I found I could say things with color and shapes that I couldn't say any other way",
        "bio": "Born in Sun Prairie, Wisconsin. Father Francis was a dairy farmer. Mother Ida was Hungarian-Irish and wanted her daughters educated. I decided at age twelve that I would be an artist. I went to art school. Then I stopped painting for four years because every teacher taught me to paint like a man. In 1915, I locked my door, spread charcoal on paper, and drew what I felt instead of what I saw. Alfred Stieglitz exhibited those drawings without my permission. I went to New York to tell him off. I married him instead. I painted flowers so large people had to look at them. 'Nobody sees a flower -- really -- it is so small -- we haven't time.' I made time. I went to New Mexico and found my country. Skulls, mesas, red earth, sky. I painted there until I was 98. I outlived everyone who doubted me.",
        "telegram_username": "desert_flower",
        "city": "Sun Prairie",
        "country_code": "US",
        "latitude": 43.183,
        "longitude": -89.213,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Oil Painting", "category": "art", "self_rating": 5, "years_experience": 70},
            {"skill_name": "Charcoal Drawing", "category": "art", "self_rating": 5, "years_experience": 60},
            {"skill_name": "Color Theory", "category": "art", "self_rating": 5, "years_experience": 65},
            {"skill_name": "Desert Botany", "category": "garden", "self_rating": 4, "years_experience": 40}
        ],
        "social_links": [],
        "points": {"total_points": 1550, "rentals_completed": 40, "reviews_given": 28, "reviews_received": 52, "items_listed": 5, "helpful_flags": 25},
        "offers_training": True,
        "items": [
            {
                "name": "Large-Format Flower Painting Workshop",
                "slug": "large-format-flower-painting-workshop",
                "description": "We paint flowers big enough that people have to stop and look. Six-foot canvases. Close-up. No background. Just the flower filling your entire field of vision. Bring your own flowers -- the ones from your garden, not the florist. Real ones.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "stravinskys-stage",
        "display_name": "Igor Stravinsky",
        "email": "stravinsky@borrowhood.local",
        "date_of_birth": "1882-06-17",
        "mother_name": "Anna Kholodovskaya",
        "father_name": "Fyodor Stravinsky",
        "workshop_name": "Stravinsky's Stage",
        "workshop_type": "studio",
        "tagline": "Lesser artists borrow, great artists steal",
        "bio": "Born in Oranienbaum, Russia. Father Fyodor was a leading bass singer at the Mariinsky Theatre. Mother Anna was a pianist. I studied law (my parents insisted) while secretly studying composition with Rimsky-Korsakov. The Rite of Spring premiered in Paris in 1913. The audience rioted. Literally rioted -- fistfights in the theatre, police called, Nijinsky screaming counts to the dancers from the wings because they couldn't hear the orchestra over the shouting. That was the day modern music was born. I went from Russian primitivism to neoclassicism to serialism. I reinvented myself three times and each time the critics said I was finished. I outlived them all. I became an American citizen. I conducted my own works into my eighties. Music is about time, and I had plenty of it.",
        "telegram_username": "rite_igor",
        "city": "Lomonosov",
        "country_code": "RU",
        "latitude": 59.910,
        "longitude": 29.773,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "ru", "proficiency": "native"},
            {"language_code": "fr", "proficiency": "C2"},
            {"language_code": "en", "proficiency": "C1"},
            {"language_code": "de", "proficiency": "B2"}
        ],
        "skills": [
            {"skill_name": "Composition", "category": "music", "self_rating": 5, "years_experience": 60},
            {"skill_name": "Conducting", "category": "music", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Piano", "category": "music", "self_rating": 4, "years_experience": 55},
            {"skill_name": "Starting Riots", "category": "other", "self_rating": 5, "years_experience": 1}
        ],
        "social_links": [],
        "points": {"total_points": 1600, "rentals_completed": 42, "reviews_given": 30, "reviews_received": 55, "items_listed": 5, "helpful_flags": 28},
        "offers_training": True,
        "items": [
            {
                "name": "Rhythm Workshop -- Complex Time Signatures",
                "slug": "rhythm-workshop-complex-time",
                "description": "Learn to count in 7/8, 5/4, 11/8, and shifting meters. I'll teach you the rhythmic language of The Rite of Spring -- the piece that started a riot. Bring a drum, a table, or just your hands. Rhythm is the most primal element of music.",
                "item_type": "service",
                "category": "music",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # WAVE 7: JAZZ / BLUES / SOUL (1900 - 1970)
    # ============================================================
    {
        "slug": "louis-armstrongs-horn",
        "display_name": "Louis Armstrong",
        "email": "satchmo@borrowhood.local",
        "date_of_birth": "1901-08-04",
        "mother_name": "Mary Albert -- Mayann",
        "father_name": "William Armstrong",
        "workshop_name": "Satchmo's Horn Shop",
        "workshop_type": "studio",
        "tagline": "What a wonderful world",
        "bio": "Born in New Orleans, Louisiana. Father William abandoned us. Mother Mayann did what she could. I grew up in a neighborhood so rough they called it The Battlefield. I was sent to the Colored Waif's Home at eleven for firing a pistol on New Year's Eve. That's where I learned cornet. Best thing that ever happened to me. Joe 'King' Oliver became my mentor. I went to Chicago. I invented the jazz solo. Before me, jazz was collective improvisation. After me, there was the soloist. I changed the way humans relate to melody. My voice -- rough, gravelly, the voice of a man who's been through everything -- became one of the most recognized sounds on Earth. 'What a Wonderful World' was released during the Vietnam War. They said it was naive. It wasn't naive. It was defiant.",
        "telegram_username": "satchmo",
        "city": "New Orleans",
        "country_code": "US",
        "latitude": 29.951,
        "longitude": -90.071,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "fr", "proficiency": "A2"}
        ],
        "skills": [
            {"skill_name": "Trumpet", "category": "music", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Jazz Vocals", "category": "music", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Improvisation", "category": "music", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Band Leading", "category": "music", "self_rating": 5, "years_experience": 45}
        ],
        "social_links": [],
        "points": {"total_points": 1700, "rentals_completed": 45, "reviews_given": 40, "reviews_received": 58, "items_listed": 6, "helpful_flags": 32},
        "offers_training": True,
        "items": [
            {
                "name": "Trumpet Lesson -- Finding Your Sound",
                "slug": "trumpet-lesson-finding-sound",
                "description": "I don't teach you to play like me. I teach you to play like YOU. We work on embouchure, breathing, and most importantly -- phrasing. Phrasing is how you tell a story with notes. Anyone can play the right notes. The question is: can you make them mean something?",
                "item_type": "service",
                "category": "music",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "duke-ellingtons-bandstand",
        "display_name": "Duke Ellington",
        "email": "duke@borrowhood.local",
        "date_of_birth": "1899-04-29",
        "mother_name": "Daisy Kennedy Ellington",
        "father_name": "James Edward Ellington",
        "workshop_name": "Ellington's Bandstand",
        "workshop_type": "studio",
        "tagline": "It don't mean a thing if it ain't got that swing",
        "bio": "Born Edward Kennedy Ellington in Washington, D.C. Mother Daisy was the daughter of a police captain. Father James was a butler who sometimes worked at the White House. They called me Duke because I carried myself like one -- even as a kid. I turned down an art scholarship to pursue music. I led the Duke Ellington Orchestra for over fifty years. Three thousand compositions. More than any other American composer. I wrote for my musicians specifically -- I didn't write for trumpet, I wrote for Cootie Williams' trumpet. Each person's sound was my instrument. I played the Cotton Club. Carnegie Hall. The White House. Every continent. 'There are two kinds of music: good and bad.' I tried to play the good kind.",
        "telegram_username": "duke_swing",
        "city": "Washington",
        "country_code": "US",
        "latitude": 38.907,
        "longitude": -77.036,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "fr", "proficiency": "B1"}
        ],
        "skills": [
            {"skill_name": "Jazz Composition", "category": "music", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Piano", "category": "music", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Band Leading", "category": "music", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Orchestration", "category": "music", "self_rating": 5, "years_experience": 50}
        ],
        "social_links": [],
        "points": {"total_points": 1750, "rentals_completed": 48, "reviews_given": 35, "reviews_received": 60, "items_listed": 6, "helpful_flags": 30},
        "offers_training": True,
        "items": [
            {
                "name": "Big Band Arrangement Workshop",
                "slug": "big-band-arrangement-workshop",
                "description": "Learn to write for a big band -- fifteen musicians, each with a voice. I'll teach you voicings, sectional writing, and how to make an orchestra swing. The secret: write for people, not instruments.",
                "item_type": "service",
                "category": "music",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "billie-holidays-garden",
        "display_name": "Billie Holiday",
        "email": "billie@borrowhood.local",
        "date_of_birth": "1915-04-07",
        "mother_name": "Sadie Fagan",
        "father_name": "Clarence Holiday",
        "workshop_name": "Lady Day's Garden",
        "workshop_type": "studio",
        "tagline": "If I'm going to sing like someone else, then I don't need to sing at all",
        "bio": "Born Eleanora Fagan in Philadelphia, raised in Baltimore. Mother Sadie was nineteen. Father Clarence was a jazz guitarist who wanted nothing to do with us. I was raped at ten. In a Catholic reformatory at eleven. In a Harlem brothel at fourteen. I started singing in clubs at fifteen. No formal training. No one taught me to phrase like that -- bending notes, lagging behind the beat, turning a simple song into something that breaks your heart. 'Strange Fruit' -- the song about lynching -- was the most dangerous song in America. Record labels refused to release it. I sang it every night anyway, in complete darkness, with only a single spotlight on my face. They took my cabaret card. They arrested me on my deathbed for heroin possession -- handcuffed to the hospital bed. I was forty-four. My voice was ruined by then, but the last recordings -- every crack, every rasp -- those are the truest things I ever sang.",
        "telegram_username": "lady_day",
        "city": "Philadelphia",
        "country_code": "US",
        "latitude": 39.952,
        "longitude": -75.164,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Jazz Vocals", "category": "music", "self_rating": 5, "years_experience": 28},
            {"skill_name": "Phrasing", "category": "music", "self_rating": 5, "years_experience": 28},
            {"skill_name": "Songwriting", "category": "music", "self_rating": 4, "years_experience": 20},
            {"skill_name": "Surviving", "category": "other", "self_rating": 5, "years_experience": 44}
        ],
        "social_links": [],
        "points": {"total_points": 1500, "rentals_completed": 38, "reviews_given": 25, "reviews_received": 52, "items_listed": 4, "helpful_flags": 28},
        "offers_training": True,
        "items": [
            {
                "name": "Vocal Phrasing Workshop -- Singing Behind the Beat",
                "slug": "vocal-phrasing-behind-beat",
                "description": "I'll teach you to sing behind the beat -- to take a melody and make it yours by changing the timing, not the notes. We work on breath, emotion, and the courage to be vulnerable in front of strangers. No sheet music. Just feeling.",
                "item_type": "service",
                "category": "music",
                "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "miles-davis-studio",
        "display_name": "Miles Davis",
        "email": "miles@borrowhood.local",
        "date_of_birth": "1926-05-26",
        "mother_name": "Cleota Mae Henry",
        "father_name": "Miles Dewey Davis Jr.",
        "workshop_name": "Miles' Blue Studio",
        "workshop_type": "studio",
        "tagline": "Do not fear mistakes. There are none",
        "bio": "Born in Alton, Illinois, grew up in East St. Louis. Father Miles Jr. was a dentist and cattle farmer -- we were middle class, not poor. Mother Cleota was a music teacher. She wanted me to play violin. I chose trumpet. I went to Juilliard at eighteen but the real education was at Minton's in Harlem, sitting in with Bird and Dizzy. I invented cool jazz. Then hard bop. Then modal jazz with Kind of Blue -- the best-selling jazz album of all time. Then fusion with Bitches Brew. Then electric funk. I reinvented jazz five times in one lifetime. People say I was arrogant. I was honest. 'I'll play it first and tell you what it is later.' I played with my back to the audience because the music wasn't for them -- it was for the band. If the audience wanted to listen, fine. But I wasn't performing. I was creating.",
        "telegram_username": "kind_of_blue",
        "city": "Alton",
        "country_code": "US",
        "latitude": 38.891,
        "longitude": -90.184,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "es", "proficiency": "A2"}
        ],
        "skills": [
            {"skill_name": "Trumpet", "category": "music", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Jazz Composition", "category": "music", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Band Leading", "category": "music", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Musical Reinvention", "category": "music", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Fashion", "category": "other", "self_rating": 5, "years_experience": 40}
        ],
        "social_links": [],
        "points": {"total_points": 1750, "rentals_completed": 48, "reviews_given": 25, "reviews_received": 60, "items_listed": 6, "helpful_flags": 25},
        "offers_training": True,
        "items": [
            {
                "name": "Modal Jazz Workshop -- Less is Everything",
                "slug": "modal-jazz-workshop-less-everything",
                "description": "Kind of Blue used two scales for the entire album. Two. I'll teach you to improvise using modes instead of chord changes. Freedom through limitation. When you only have two colors, you learn to paint everything.",
                "item_type": "service",
                "category": "music",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "nina-simones-piano",
        "display_name": "Nina Simone",
        "email": "nina@borrowhood.local",
        "date_of_birth": "1933-02-21",
        "mother_name": "Mary Kate Irvin Waymon",
        "father_name": "John Devan Waymon",
        "workshop_name": "Nina's Piano",
        "workshop_type": "studio",
        "tagline": "An artist's duty is to reflect the times",
        "bio": "Born Eunice Kathleen Waymon in Tryon, North Carolina. Mother Mary Kate was a Methodist minister. Father John was a handyman and barber. I started playing piano at three. The whole town -- Black and white -- raised money for my classical training. I applied to the Curtis Institute in Philadelphia. They rejected me. I always believed it was because I was Black. That rejection defined my life. I became Nina Simone -- took the name so my mother wouldn't know I was playing 'devil's music' in Atlantic City bars. I played Bach, gospel, jazz, blues, folk, pop -- all at once. 'Mississippi Goddam' was the first civil rights song that was angry instead of hopeful. I was done asking politely. My art was my weapon. They called me difficult. I was necessary.",
        "telegram_username": "high_priestess",
        "city": "Tryon",
        "country_code": "US",
        "latitude": 35.209,
        "longitude": -82.234,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "fr", "proficiency": "C1"}
        ],
        "skills": [
            {"skill_name": "Classical Piano", "category": "music", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Jazz Vocals", "category": "music", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Songwriting", "category": "music", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Civil Rights Activism", "category": "other", "self_rating": 5, "years_experience": 30}
        ],
        "social_links": [],
        "points": {"total_points": 1600, "rentals_completed": 42, "reviews_given": 30, "reviews_received": 55, "items_listed": 5, "helpful_flags": 30},
        "offers_training": True,
        "items": [
            {
                "name": "Piano Lesson -- Classical Technique Meets Soul",
                "slug": "piano-lesson-classical-meets-soul",
                "description": "I trained for classical concert piano and ended up playing jazz in bars. That's not a step down -- that's a synthesis. I'll teach you to bring classical discipline to any genre. Bach and the blues are closer than you think.",
                "item_type": "service",
                "category": "music",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "ella-fitzgeralds-stage",
        "display_name": "Ella Fitzgerald",
        "email": "ella@borrowhood.local",
        "date_of_birth": "1917-04-25",
        "mother_name": "Temperance Henry -- Tempie",
        "father_name": "William Fitzgerald",
        "workshop_name": "Ella's Stage",
        "workshop_type": "studio",
        "tagline": "The only thing better than singing is more singing",
        "bio": "Born in Newport News, Virginia. Father William left when I was a baby. Mother Tempie moved us to Yonkers, New York. She died when I was fifteen. I was homeless. I slept on the streets. I entered a talent contest at the Apollo Theatre planning to dance -- but the dancers before me were so good I switched to singing on the spot. I won. Norman Granz became my manager and made hotels serve me or lose his entire tour. I recorded the Great American Songbook -- eight albums, one for each major composer. Cole Porter, Gershwin, Ellington, Rodgers and Hart. I defined how those songs should sound. My scat singing -- improvised syllables, the voice as pure instrument -- influenced every jazz singer who came after. They called me the First Lady of Song. I couldn't read music. I could hear it, and that was enough.",
        "telegram_username": "first_lady_song",
        "city": "Newport News",
        "country_code": "US",
        "latitude": 37.086,
        "longitude": -76.473,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "pt", "proficiency": "A2"}
        ],
        "skills": [
            {"skill_name": "Jazz Vocals", "category": "music", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Scat Singing", "category": "music", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Songbook Interpretation", "category": "music", "self_rating": 5, "years_experience": 45}
        ],
        "social_links": [],
        "points": {"total_points": 1650, "rentals_completed": 44, "reviews_given": 38, "reviews_received": 56, "items_listed": 5, "helpful_flags": 30},
        "offers_training": True,
        "items": [
            {
                "name": "Scat Singing Workshop -- Voice as Instrument",
                "slug": "scat-singing-workshop-voice-instrument",
                "description": "Learn to improvise with your voice using syllables, rhythms, and melodic invention. No words. Just sound. I'll teach you the vocabulary of scat -- the bops, the doos, the ba-da-ba-das -- and then we throw the vocabulary away and you find your own.",
                "item_type": "service",
                "category": "music",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # WAVE 8: CONTEMPORARY ICONS (1940 - present)
    # ============================================================
    {
        "slug": "bob-dylans-basement",
        "display_name": "Bob Dylan",
        "email": "dylan@borrowhood.local",
        "date_of_birth": "1941-05-24",
        "mother_name": "Beatrice Stone -- Beatty",
        "father_name": "Abram Hyman Zimmerman",
        "workshop_name": "Dylan's Basement",
        "workshop_type": "studio",
        "tagline": "A man is a success if he gets up in the morning and gets to bed at night and in between does what he wants to do",
        "bio": "Born Robert Allen Zimmerman in Duluth, Minnesota. Father Abe ran a furniture store. Mother Beatty raised me in Hibbing -- iron range country, frozen half the year. I heard Woody Guthrie on the radio and left for New York. I changed my name. I sang protest songs until they called me the voice of a generation. Then I plugged in an electric guitar and they booed me. Then I went country. Then Christian. Then whatever the hell the 1980s were. Then Time Out of Mind in 1997 and suddenly the critics loved me again. I won the Nobel Prize for Literature in 2016 and didn't show up to collect it. I've been on the Never Ending Tour since 1988 -- three hundred shows a year, year after year. The songs are different every night because I am different every night. 'I contain multitudes.'",
        "telegram_username": "rolling_stone_bob",
        "city": "Duluth",
        "country_code": "US",
        "latitude": 46.786,
        "longitude": -92.100,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Songwriting", "category": "music", "self_rating": 5, "years_experience": 65},
            {"skill_name": "Guitar", "category": "music", "self_rating": 4, "years_experience": 65},
            {"skill_name": "Harmonica", "category": "music", "self_rating": 5, "years_experience": 65},
            {"skill_name": "Disappearing", "category": "other", "self_rating": 5, "years_experience": 60}
        ],
        "social_links": [],
        "points": {"total_points": 1800, "rentals_completed": 50, "reviews_given": 20, "reviews_received": 60, "items_listed": 6, "helpful_flags": 20},
        "offers_training": True,
        "items": [
            {
                "name": "Songwriting Workshop -- Words First, Music Second",
                "slug": "songwriting-workshop-words-first",
                "description": "I write the words first. Always. The melody finds its way to the words. We'll work on imagery, metaphor, and the art of saying something so specific it becomes universal. Bring a notebook. Leave your guitar at home for the first session.",
                "item_type": "service",
                "category": "music",
                "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "aretha-franklins-church",
        "display_name": "Aretha Franklin",
        "email": "aretha@borrowhood.local",
        "date_of_birth": "1942-03-25",
        "mother_name": "Barbara Vernice Siggers",
        "father_name": "Clarence LaVaughn Franklin",
        "workshop_name": "Aretha's Church",
        "workshop_type": "studio",
        "tagline": "R-E-S-P-E-C-T, find out what it means to me",
        "bio": "Born in Memphis, Tennessee, raised in Detroit. Father C.L. Franklin was the most famous Black preacher in America -- his sermons sold millions of records. Mother Barbara was a gospel singer who left when I was six. I learned to play piano by ear at eight. I was singing solos in my father's church at twelve. Pregnant at twelve too. Again at fourteen. I raised my sons, sang gospel, and at eighteen signed with Columbia Records. They tried to make me a pop singer. It didn't work until I went to Atlantic and recorded in Muscle Shoals with real musicians who understood gospel soul. 'Respect' was Otis Redding's song. I took it and made it mine and it became the anthem of the civil rights movement and the women's movement simultaneously. They called me the Queen of Soul. I called myself a singer who came from the church.",
        "telegram_username": "queen_of_soul",
        "city": "Memphis",
        "country_code": "US",
        "latitude": 35.149,
        "longitude": -90.049,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Gospel Vocals", "category": "music", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Piano", "category": "music", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Soul Singing", "category": "music", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Songwriting", "category": "music", "self_rating": 4, "years_experience": 40}
        ],
        "social_links": [],
        "points": {"total_points": 1750, "rentals_completed": 48, "reviews_given": 35, "reviews_received": 60, "items_listed": 6, "helpful_flags": 32},
        "offers_training": True,
        "items": [
            {
                "name": "Gospel Vocal Technique Workshop",
                "slug": "gospel-vocal-technique-workshop",
                "description": "The church is where it all starts. I'll teach you to sing from the diaphragm, to bend notes, to build from a whisper to a scream that fills the room. Gospel technique is the foundation of all American popular music. If you can sing gospel, you can sing anything.",
                "item_type": "service",
                "category": "music",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "bob-marleys-yard",
        "display_name": "Bob Marley",
        "email": "marley@borrowhood.local",
        "date_of_birth": "1945-02-06",
        "mother_name": "Cedella Booker -- born Malcolm",
        "father_name": "Norval Sinclair Marley",
        "workshop_name": "Bob Marley's Yard",
        "workshop_type": "studio",
        "tagline": "One good thing about music, when it hits you, you feel no pain",
        "bio": "Born in Nine Mile, Saint Ann Parish, Jamaica. Father Norval was a white Jamaican plantation overseer. Mother Cedella was an eighteen-year-old Black Jamaican. He married her, then disappeared. I grew up in Trenchtown, Kingston -- the ghetto, the government yard. I formed The Wailers with Bunny Wailer and Peter Tosh. We played ska, rocksteady, then reggae. I brought reggae to the world. 'Get Up, Stand Up.' 'No Woman, No Cry.' 'Redemption Song.' Every song was a sermon. Rastafari was my faith, music was my weapon, Jamaica was my heart. They shot me in 1976 -- two days before a peace concert. I played anyway with the bullet still in my arm. Cancer took me at 36. But every beach bar, every protest march, every summer evening everywhere -- you hear the offbeat guitar and you know. Reggae doesn't die because resistance doesn't die.",
        "telegram_username": "tuff_gong",
        "city": "Nine Mile",
        "country_code": "JM",
        "latitude": 18.345,
        "longitude": -77.267,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Reggae Guitar", "category": "music", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Songwriting", "category": "music", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Vocals", "category": "music", "self_rating": 5, "years_experience": 22},
            {"skill_name": "Peace Activism", "category": "other", "self_rating": 5, "years_experience": 15}
        ],
        "social_links": [],
        "points": {"total_points": 1700, "rentals_completed": 45, "reviews_given": 40, "reviews_received": 58, "items_listed": 6, "helpful_flags": 35},
        "offers_training": True,
        "items": [
            {
                "name": "Reggae Guitar Workshop -- The Offbeat Skank",
                "slug": "reggae-guitar-workshop-offbeat-skank",
                "description": "The strum that changed the world hits on the upbeat. That's it. That's the secret. But making it groove -- that's what we'll work on. I'll teach you the skank, the one-drop rhythm, and how to make three chords feel like freedom.",
                "item_type": "service",
                "category": "music",
                "listings": [{"listing_type": "training", "price": 12.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "david-bowies-space",
        "display_name": "David Bowie",
        "email": "bowie@borrowhood.local",
        "date_of_birth": "1947-01-08",
        "mother_name": "Margaret Mary Burns -- Peggy",
        "father_name": "Haywood Stenton Jones",
        "workshop_name": "Bowie's Space",
        "workshop_type": "studio",
        "tagline": "I don't know where I'm going from here, but I promise it won't be boring",
        "bio": "Born David Robert Jones in Brixton, London. Father Haywood worked for Barnardo's children's charity. Mother Peggy was a cinema usherette. My half-brother Terry introduced me to jazz and Buddhism and then spent most of his life in a psychiatric hospital -- that haunted everything I created. I became Ziggy Stardust, Aladdin Sane, the Thin White Duke, the Earthling. Each one a character I inhabited completely and then killed when I was done. I pioneered glam rock, art rock, electronic, drum and bass, and whatever Blackstar was. I recorded 'Heroes' in Berlin next to the Wall. I walked through New York as a regular person for years because New Yorkers don't care who you are. I made my last album in secret while dying of liver cancer. Released it two days before I died. Turned his death into art. One last character. The last reinvention.",
        "telegram_username": "ziggy_played",
        "city": "London",
        "country_code": "GB",
        "latitude": 51.459,
        "longitude": -0.114,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "de", "proficiency": "B2"},
            {"language_code": "ja", "proficiency": "A2"}
        ],
        "skills": [
            {"skill_name": "Songwriting", "category": "music", "self_rating": 5, "years_experience": 48},
            {"skill_name": "Vocals", "category": "music", "self_rating": 5, "years_experience": 48},
            {"skill_name": "Stage Performance", "category": "art", "self_rating": 5, "years_experience": 48},
            {"skill_name": "Reinvention", "category": "other", "self_rating": 5, "years_experience": 48},
            {"skill_name": "Painting", "category": "art", "self_rating": 3, "years_experience": 30}
        ],
        "social_links": [],
        "points": {"total_points": 1750, "rentals_completed": 48, "reviews_given": 30, "reviews_received": 60, "items_listed": 7, "helpful_flags": 30},
        "offers_training": True,
        "items": [
            {
                "name": "Persona Creation Workshop -- Inventing Your Stage Self",
                "slug": "persona-creation-workshop-stage-self",
                "description": "I'll teach you to create a character you can perform as -- costume, voice, attitude, mythology. Then we'll retire that character and build another one. The point isn't the mask. The point is the freedom the mask gives you to be truthful.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "toni-morrisons-desk",
        "display_name": "Toni Morrison",
        "email": "toni@borrowhood.local",
        "date_of_birth": "1931-02-18",
        "mother_name": "Ramah Wofford",
        "father_name": "George Wofford",
        "workshop_name": "Morrison's Writing Desk",
        "workshop_type": "office",
        "tagline": "If there's a book that you want to read, but it hasn't been written yet, then you must write it",
        "bio": "Born Chloe Ardelia Wofford in Lorain, Ohio. Father George was a shipyard welder who worked three jobs. Mother Ramah sang in the church choir and told stories. I was the first woman in my family to go to college. I became an editor at Random House where I published Black writers nobody else would touch -- Toni Cade Bambara, Gayl Jones, Angela Davis. Then I wrote my own. The Bluest Eye. Sula. Song of Solomon. Beloved -- the story of a formerly enslaved woman haunted by the ghost of the daughter she killed to save from slavery. I won the Pulitzer. Then the Nobel. I was the first African American woman to win the Nobel Prize in Literature. I wrote sentences that changed the temperature in the room. 'Definitions belong to the definers, not the defined.' I wrote the books that didn't exist for me when I was growing up. That's all.",
        "telegram_username": "beloved_chloe",
        "city": "Lorain",
        "country_code": "US",
        "latitude": 41.452,
        "longitude": -82.182,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "fr", "proficiency": "C1"}
        ],
        "skills": [
            {"skill_name": "Novel Writing", "category": "art", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Editing", "category": "art", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Literary Criticism", "category": "education", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Teaching", "category": "education", "self_rating": 5, "years_experience": 35}
        ],
        "social_links": [],
        "points": {"total_points": 1700, "rentals_completed": 45, "reviews_given": 40, "reviews_received": 58, "items_listed": 5, "helpful_flags": 35},
        "offers_training": True,
        "items": [
            {
                "name": "Writing Workshop -- The Sentence as Architecture",
                "slug": "writing-workshop-sentence-architecture",
                "description": "We will take your sentences apart and rebuild them. A sentence is not just communication. It is music, rhythm, architecture. Every word earns its place or it leaves. I edited for twenty years before I published. Bring your best paragraph. We'll find out if it's really your best.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "gabriel-garcia-marquezs-hammock",
        "display_name": "Gabriel Garcia Marquez",
        "email": "gabo@borrowhood.local",
        "date_of_birth": "1927-03-06",
        "mother_name": "Luisa Santiaga Marquez Iguaran",
        "father_name": "Gabriel Eligio Garcia",
        "workshop_name": "Gabo's Hammock",
        "workshop_type": "office",
        "tagline": "It is not true that people stop pursuing dreams because they grow old, they grow old because they stop pursuing dreams",
        "bio": "Born in Aracataca, Colombia. Father Gabriel Eligio was a telegraph operator. Mother Luisa came from a prominent family -- her parents opposed the marriage. I was raised by my grandparents. My grandfather, a retired colonel, told me war stories. My grandmother told them as if they were perfectly normal. 'There will be birds flying overhead who will tell me when she dies.' That was her voice. That became my voice. One Hundred Years of Solitude. Love in the Time of Cholera. The Colonel Has No One to Write Him. I invented nothing -- I just wrote down what my grandmother told me, but with better structure. Magical realism isn't magic. It's how Latin Americans actually experience reality. The extraordinary happens every day. You just have to stop being surprised by it. Nobel Prize 1982. I wore a white liquiliqui instead of a tuxedo. Colombia's gift to world literature, in a hammock shirt.",
        "telegram_username": "gabo_macondo",
        "city": "Aracataca",
        "country_code": "CO",
        "latitude": 10.593,
        "longitude": -74.189,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "es", "proficiency": "native"},
            {"language_code": "fr", "proficiency": "B2"},
            {"language_code": "en", "proficiency": "B1"}
        ],
        "skills": [
            {"skill_name": "Novel Writing", "category": "art", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Journalism", "category": "art", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Screenwriting", "category": "art", "self_rating": 4, "years_experience": 25},
            {"skill_name": "Hammock Lounging", "category": "other", "self_rating": 5, "years_experience": 60}
        ],
        "social_links": [],
        "points": {"total_points": 1600, "rentals_completed": 42, "reviews_given": 35, "reviews_received": 55, "items_listed": 5, "helpful_flags": 30},
        "offers_training": True,
        "items": [
            {
                "name": "Magical Realism Writing Workshop",
                "slug": "magical-realism-writing-workshop",
                "description": "Write the impossible as if it were the most natural thing in the world. That's the technique. No winking at the reader. No 'this is strange.' Just: 'It rained for four years, eleven months, and two days.' Stated as fact. Because in Macondo, it is. Bring a family story that nobody believes. We'll turn it into literature.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "maya-angelous-porch",
        "display_name": "Maya Angelou",
        "email": "maya@borrowhood.local",
        "date_of_birth": "1928-04-04",
        "mother_name": "Vivian Baxter Johnson",
        "father_name": "Bailey Johnson",
        "workshop_name": "Maya's Porch",
        "workshop_type": "office",
        "tagline": "There is no greater agony than bearing an untold story inside you",
        "bio": "Born Marguerite Annie Johnson in St. Louis, Missouri. Father Bailey was a doorman and dietician. Mother Vivian was a nurse and card dealer -- beautiful, tough, complicated. When I was seven, my mother's boyfriend raped me. I told my brother. My uncles killed the man. I went mute for five years -- I believed my voice had killed him. A teacher named Mrs. Flowers gave me poetry and books and slowly coaxed my voice back. That voice wrote I Know Why the Caged Bird Sings. That voice recited 'On the Pulse of Morning' at Clinton's inauguration. I was a streetcar conductor in San Francisco at fifteen -- the first Black woman to do it. A calypso dancer. A journalist in Egypt. A coordinator for Martin Luther King Jr. I spoke six languages. I lived in Ghana. I came back and wrote seven autobiographies because one life was not enough to contain. 'People will forget what you said, people will forget what you did, but people will never forget how you made them feel.'",
        "telegram_username": "caged_bird_sings",
        "city": "St. Louis",
        "country_code": "US",
        "latitude": 38.627,
        "longitude": -90.199,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "fr", "proficiency": "C2"},
            {"language_code": "es", "proficiency": "C1"},
            {"language_code": "ar", "proficiency": "B2"},
            {"language_code": "it", "proficiency": "B1"}
        ],
        "skills": [
            {"skill_name": "Poetry", "category": "art", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Autobiography", "category": "art", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Public Speaking", "category": "other", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Teaching", "category": "education", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Calypso Dancing", "category": "sports", "self_rating": 4, "years_experience": 10}
        ],
        "social_links": [],
        "points": {"total_points": 1700, "rentals_completed": 45, "reviews_given": 40, "reviews_received": 58, "items_listed": 5, "helpful_flags": 35},
        "offers_training": True,
        "items": [
            {
                "name": "Memoir Writing Workshop -- Your Story Matters",
                "slug": "memoir-writing-workshop-story-matters",
                "description": "Everyone has a story that needs telling. I went mute for five years and then I couldn't stop talking. We'll work on memory, honesty, and the courage to write the parts that scare you. Those are the parts that matter. Bring nothing but yourself and something to write with.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "leonards-tower-of-song",
        "display_name": "Leonard Cohen",
        "email": "leonard@borrowhood.local",
        "date_of_birth": "1934-09-21",
        "mother_name": "Masha Klonitsky-Klein",
        "father_name": "Nathan Bernard Cohen",
        "workshop_name": "Leonard's Tower of Song",
        "workshop_type": "studio",
        "tagline": "There is a crack in everything, that's how the light gets in",
        "bio": "Born in Westmount, Montreal. Father Nathan was a clothing merchant who died when I was nine. Mother Masha was from a rabbinical family -- she suffered from depression and gave me both the darkness and the words to describe it. I was a poet first. Two novels. Then at thirty-three I went to New York with a guitar and became the songwriter who couldn't sing. My voice was an octave too low for radio. It didn't matter. 'Suzanne.' 'Hallelujah.' 'Bird on the Wire.' 'Famous Blue Raincoat.' I wrote 'Hallelujah' over five years, eighty drafts, until it was perfect. Then nobody would record it. It took twenty years to become the most covered song of the 21st century. I spent five years in a Zen monastery on Mount Baldy. My manager stole my money. At seventy-one I went back on tour because I was broke. Played three hundred shows. Died three weeks after releasing You Want It Darker. 'I'm ready, my Lord.'",
        "telegram_username": "hallelujah_len",
        "city": "Montreal",
        "country_code": "CA",
        "latitude": 45.501,
        "longitude": -73.567,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "fr", "proficiency": "C2"}
        ],
        "skills": [
            {"skill_name": "Songwriting", "category": "music", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Poetry", "category": "art", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Singing (Low Register)", "category": "music", "self_rating": 3, "years_experience": 50},
            {"skill_name": "Zen Meditation", "category": "other", "self_rating": 5, "years_experience": 40}
        ],
        "social_links": [],
        "points": {"total_points": 1650, "rentals_completed": 44, "reviews_given": 35, "reviews_received": 56, "items_listed": 5, "helpful_flags": 32},
        "offers_training": True,
        "items": [
            {
                "name": "Songwriting Workshop -- Eighty Drafts of Hallelujah",
                "slug": "songwriting-workshop-eighty-drafts",
                "description": "I'll teach you to rewrite. And rewrite. And rewrite. Hallelujah took eighty drafts. That's not failure. That's craft. We start with a feeling, turn it into an image, then carve it into a verse. Bring patience. This is a slow art.",
                "item_type": "service",
                "category": "music",
                "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    # ============================================================
    # THE KENEL BROTHERS -- Albert Kenel DNA, Swiss-Canadian Grit
    # ============================================================
    {
        "slug": "daves-fix-it-shop",
        "display_name": "Dave Kenel",
        "email": "dave.kenel@borrowhood.local",
        "date_of_birth": "1965-01-15",
        "mother_name": "Maria Kenel",
        "father_name": "Albert Kenel",
        "workshop_name": "Dave's Fix-It Shop",
        "workshop_type": "garage",
        "tagline": "If it's broken, I fix it. If it's not broken, don't touch it.",
        "bio": "Son of Albert Kenel, the hand-shovel landscaper. Swiss-Canadian. I fix things. That's what I do. All day, every day. Plumbing, electrical, mechanical, structural -- doesn't matter. If it's broken, put it in front of me and go get a coffee. By the time you're back, it works. My brother Angelo says I almost killed him a hundred times growing up. He survived every one. That's because Kenels are hard to kill. Albert Kenel DNA runs thick -- we don't quit, we don't complain, and we don't call the repairman. We ARE the repairman. Dad taught us that tools are extensions of your hands. Your hands are extensions of your will. Your will is the only thing between you and a broken world. So pick up the wrench and get to work.",
        "telegram_username": "dave_fixit",
        "city": "Toronto",
        "country_code": "CA",
        "latitude": 43.653,
        "longitude": -79.383,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "de", "proficiency": "B1"},
            {"language_code": "fr", "proficiency": "A2"}
        ],
        "skills": [
            {"skill_name": "General Repair", "category": "engineering", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Plumbing", "category": "engineering", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Electrical", "category": "engineering", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Carpentry", "category": "engineering", "self_rating": 4, "years_experience": 30},
            {"skill_name": "Brotherly Combat", "category": "sports", "self_rating": 5, "years_experience": 50}
        ],
        "social_links": [],
        "points": {"total_points": 800, "rentals_completed": 30, "reviews_given": 20, "reviews_received": 35, "items_listed": 8, "helpful_flags": 25},
        "offers_repair": True,
        "offers_pickup": True,
        "items": [
            {
                "name": "General Repair Service -- If It's Broken, Bring It",
                "slug": "general-repair-service-dave-kenel",
                "description": "Plumbing, electrical, mechanical, whatever. I've been fixing things since I could hold a wrench. Albert Kenel taught me: don't stare at it, fix it. Bring the broken thing. I'll tell you what's wrong in thirty seconds and fix it in thirty minutes.",
                "item_type": "service",
                "category": "tools",
                "listings": [{"listing_type": "service", "price": 25.0, "price_unit": "per_hour", "currency": "EUR"}]
            },
            {
                "name": "Complete Tool Kit (Metric + Imperial)",
                "slug": "complete-tool-kit-metric-imperial",
                "description": "Full socket set, wrenches, screwdrivers, pliers, voltage tester, pipe wrench, hacksaw. Metric AND imperial because we're Swiss-Canadian and we work in both worlds. Everything in its place. Return it the same way.",
                "item_type": "physical",
                "category": "tools",
                "listings": [{"listing_type": "rent", "price": 10.0, "price_unit": "per_day", "currency": "EUR", "deposit": 50.0}]
            }
        ]
    },
    {
        "slug": "marios-excavation-yard",
        "display_name": "Mario Kenel",
        "email": "mario.kenel@borrowhood.local",
        "date_of_birth": "1963-01-15",
        "mother_name": "Maria Kenel",
        "father_name": "Albert Kenel",
        "workshop_name": "Ideal Excavating",
        "workshop_type": "workshop",
        "tagline": "Break it down, build it back, make it better",
        "bio": "Son of Albert Kenel. The executor. The man behind Ideal Excavating. I can break anything apart and put it back together -- that's not a skill, that's a philosophy. Dad moved earth with a hand shovel. I move it with machines, but the principle is the same: you start at one end and you don't stop until it's done. Excavation is demolition with a plan. You have to know what's under the ground before you dig. You have to know what holds the building up before you take it down. And when you rebuild, you make it better than it was. Kenels don't just fix things -- we improve them. Mario Kenel, Ideal Excavating. We dig. We build. We don't cut corners because corners are structural.",
        "telegram_username": "ideal_excavating",
        "city": "Toronto",
        "country_code": "CA",
        "latitude": 43.700,
        "longitude": -79.416,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "de", "proficiency": "B2"},
            {"language_code": "fr", "proficiency": "A2"}
        ],
        "skills": [
            {"skill_name": "Excavation", "category": "engineering", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Demolition", "category": "engineering", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Heavy Equipment Operation", "category": "engineering", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Mechanical Repair", "category": "engineering", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Construction Management", "category": "engineering", "self_rating": 5, "years_experience": 30}
        ],
        "social_links": [],
        "points": {"total_points": 850, "rentals_completed": 32, "reviews_given": 22, "reviews_received": 38, "items_listed": 10, "helpful_flags": 28},
        "offers_repair": True,
        "offers_delivery": True,
        "offers_custom_orders": True,
        "items": [
            {
                "name": "Mini Excavator Rental (3.5 Ton)",
                "slug": "mini-excavator-rental-3-5-ton",
                "description": "Kubota KX91-3, 3.5 ton mini excavator. Rubber tracks, extendable arm, multiple bucket sizes. Perfect for residential foundations, pool digs, drainage work. I'll deliver it and show you the controls. Break something? Call me. I'll fix it.",
                "item_type": "physical",
                "category": "tools",
                "listings": [{"listing_type": "rent", "price": 200.0, "price_unit": "per_day", "currency": "EUR", "deposit": 500.0}]
            },
            {
                "name": "Demolition & Site Prep Service",
                "slug": "demolition-site-prep-service-ideal",
                "description": "Small structure demolition, concrete breaking, site clearing, grading. Ideal Excavating. We break it down clean and leave the site ready to build. No mess, no shortcuts. Albert Kenel's son doesn't leave a messy jobsite.",
                "item_type": "service",
                "category": "tools",
                "listings": [{"listing_type": "service", "price": 500.0, "price_unit": "per_day", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "pauls-golf-office",
        "display_name": "Paul Kenel",
        "email": "paul.kenel@borrowhood.local",
        "date_of_birth": "1960-01-15",
        "mother_name": "Maria Kenel",
        "father_name": "Albert Kenel",
        "workshop_name": "Chapel Golf -- The Rock",
        "workshop_type": "office",
        "tagline": "The rock doesn't move. Everything else does.",
        "bio": "Son of Albert Kenel. Bat Fat. The Rock. Chapel Golf manager. I run the course, manage the staff, keep the books, handle the members, and make sure the greens are perfect. Golf is a game of patience and precision -- two things Albert Kenel drilled into all his sons. You line up the shot, you commit, you follow through. Same in business, same in life. My brothers fix things and dig holes. I manage people and fairways. Different tools, same DNA. Kenels work. That's what we do. We don't talk about it. We don't post about it. We show up, we do the job, and we go home. The course is open seven days. I'm there six of them. The seventh day God rests. I check the irrigation.",
        "telegram_username": "bat_fat_paul",
        "city": "Toronto",
        "country_code": "CA",
        "latitude": 43.680,
        "longitude": -79.350,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "de", "proficiency": "B1"},
            {"language_code": "fr", "proficiency": "A2"}
        ],
        "skills": [
            {"skill_name": "Golf Course Management", "category": "other", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Groundskeeping", "category": "garden", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Business Management", "category": "other", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Golf", "category": "sports", "self_rating": 4, "years_experience": 35},
            {"skill_name": "Staff Management", "category": "other", "self_rating": 5, "years_experience": 20}
        ],
        "social_links": [],
        "points": {"total_points": 750, "rentals_completed": 28, "reviews_given": 18, "reviews_received": 32, "items_listed": 6, "helpful_flags": 22},
        "offers_training": True,
        "items": [
            {
                "name": "Golf Lesson -- Fundamentals for Beginners",
                "slug": "golf-lesson-fundamentals-beginners",
                "description": "Grip, stance, swing, follow through. I don't teach you to hit it far. I teach you to hit it straight. Consistency beats distance every time. Just like Albert Kenel said: do it right or don't do it. Clubs provided.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 30.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Golf Club Set (Complete, Right-Handed)",
                "slug": "golf-club-set-complete-right-handed",
                "description": "Full set: driver, 3-wood, 5-wood, 4-PW irons, sand wedge, putter. Bag with stand included. Good enough to play 18 holes, not so expensive you cry when you shank one into the lake. Return them clean.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 15.0, "price_unit": "per_day", "currency": "EUR", "deposit": 75.0}]
            }
        ]
    },

    # ============================================================
    # BANKSY -- The ghost who changed how walls speak
    # ============================================================
    {
        "slug": "banksys-wall",
        "display_name": "Banksy",
        "email": "banksy@borrowhood.local",
        "date_of_birth": "1974-01-01",
        "mother_name": "Unknown -- and she's not telling either",
        "father_name": "Unknown -- possibly a photocopier technician from Bristol, if you believe the rumors",
        "workshop_name": "Banksy's Wall",
        "workshop_type": "studio",
        "tagline": "Art should comfort the disturbed and disturb the comfortable",
        "bio": "Identity unknown. Probably from Bristol, England. Probably born around 1974. Probably male. Everything is probably because nobody knows for certain and that's the whole point. I started spraying stencils on walls in the 1990s. Girl with a Balloon. Flower Thrower. Kissing Coppers. Rat series. I put a painting through a shredder at auction the moment it sold for 1.4 million pounds -- it was titled Love is in the Bin after that, and then sold again for 25 million. I opened Dismaland, a dystopian theme park in Weston-super-Mare. I painted murals in Palestine, in New York, in New Orleans after Katrina. I am the most famous artist in the world and nobody knows what I look like. The art world hates that. Good. The art world is a playground for billionaires who confuse price tags with meaning. My art is free. It's on walls. It belongs to everyone who walks past it. The only crime is making art that nobody cares about.",
        "telegram_username": "rat_stencil",
        "city": "Bristol",
        "country_code": "GB",
        "latitude": 51.455,
        "longitude": -2.588,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Stencil Art", "category": "art", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Social Commentary", "category": "art", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Anonymity", "category": "other", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Spray Painting", "category": "art", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Installation Art", "category": "art", "self_rating": 5, "years_experience": 20}
        ],
        "social_links": [],
        "points": {"total_points": 1900, "rentals_completed": 52, "reviews_given": 10, "reviews_received": 65, "items_listed": 8, "helpful_flags": 40},
        "offers_training": True,
        "items": [
            {
                "name": "Stencil Making Workshop -- Your Message on Any Wall",
                "slug": "stencil-making-workshop-message-wall",
                "description": "I'll teach you to cut stencils, mix paint ratios, and get your message up in under sixty seconds. The art is in the preparation -- the execution takes less time than a traffic light. We practice on canvas first. What you do after that is your business. I never saw you. You were never here.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 0.0, "price_unit": "free", "currency": "EUR", "notes": "Free. Always. If someone charges you for Banksy lessons, it's not Banksy."}]
            },
            {
                "name": "Professional Stencil Kit (Multi-Layer)",
                "slug": "professional-stencil-kit-multi-layer",
                "description": "Mylar sheets, precision craft knife, self-healing cutting mat, spray paint adaptor for even coverage. Everything you need to make multi-layer stencils that look like they were screenprinted. Also includes a hoodie. You'll need the hoodie.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR"}]
            },
            {
                "name": "Rat (Signed Print -- Or Is It?)",
                "slug": "rat-signed-print-or-is-it",
                "description": "A print of one of my rats. Signed. Or is it? That's the question with everything I make. Authentication in the art world is a racket. This print is real if you believe it's real. Isn't that how all art works? Comes with a certificate of ambiguity.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 1.0, "price_unit": "per_week", "currency": "EUR", "notes": "Display it. Enjoy it. Return it. Or don't. I'll deny it exists either way."}]
            }
        ]
    },

    # ============================================================
    # MAX IGAN -- The Crowhouse, nomad truth-teller
    # ============================================================
    {
        "slug": "max-igans-crowhouse",
        "display_name": "Max Igan",
        "email": "max.igan@borrowhood.local",
        "date_of_birth": "1967-01-01",
        "mother_name": "Unknown -- Max keeps his family private, as any Skitso should",
        "father_name": "Unknown -- same reason",
        "workshop_name": "The Crowhouse",
        "workshop_type": "other",
        "tagline": "Music is the weapon of the future -- and the truth is the ammunition",
        "bio": "Australian. Musician. Filmmaker. Truth-teller. Nomad. I ran The Crowhouse for over a decade -- broadcasting from wherever I happened to be, which eventually became everywhere because staying in one place became impossible. I was in Australia when they tried to lock the whole country down. I left. I've been moving ever since -- Central America, Mexico, wherever the signal reaches. No garage. No fixed workshop. Just a laptop, a camera, a microphone, and the stubborn belief that people deserve to know what's actually happening. I map the systems of control -- the financial system, the surveillance grid, the manipulation of perception. I don't tell people what to think. I show them the pattern and let them decide. The normies call me crazy. The psychos call me dangerous. The Skitsos just nod, because they already knew. 'We need to vote Skitsos into office.' That's not a joke. That's a survival strategy.",
        "telegram_username": "crowhouse_max",
        "city": "Nomad",
        "country_code": "AU",
        "latitude": -33.868,
        "longitude": 151.209,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Documentary Filmmaking", "category": "art", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Pattern Recognition", "category": "other", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Guitar", "category": "music", "self_rating": 4, "years_experience": 30},
            {"skill_name": "Live Broadcasting", "category": "other", "self_rating": 5, "years_experience": 15},
            {"skill_name": "Surviving on the Road", "category": "other", "self_rating": 5, "years_experience": 10}
        ],
        "social_links": [],
        "points": {"total_points": 1200, "rentals_completed": 30, "reviews_given": 35, "reviews_received": 45, "items_listed": 4, "helpful_flags": 40},
        "offers_training": True,
        "items": [
            {
                "name": "Documentary Filmmaking Workshop -- Truth on a Budget",
                "slug": "documentary-filmmaking-truth-budget",
                "description": "You don't need a studio. You don't need a crew. You need a camera, a microphone, a laptop, and something worth saying. I'll teach you to research, script, edit, and publish a documentary that changes how people see the world. The mainstream won't touch your story? Good. Publish it yourself. That's what the internet is for.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 10.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Mobile Broadcasting Kit (Laptop + Mic + Camera)",
                "slug": "mobile-broadcasting-kit-laptop-mic",
                "description": "Everything you need to broadcast from anywhere on Earth. Laptop, USB condenser mic, webcam with decent low-light, portable ring light, and a VPN because you'll need one. I've broadcast from jungles, hotel rooms, and the back of vans. The truth doesn't need a studio.",
                "item_type": "physical",
                "category": "tools",
                "listings": [{"listing_type": "rent", "price": 15.0, "price_unit": "per_day", "currency": "EUR", "deposit": 100.0}]
            }
        ]
    },

    # ============================================================
    # TIGS' PICKS -- The ones I'd fight for
    # ============================================================
    {
        "slug": "baldwins-cafe-table",
        "display_name": "James Baldwin",
        "email": "baldwin@borrowhood.local",
        "date_of_birth": "1924-08-02",
        "mother_name": "Emma Berdis Jones",
        "father_name": "David Baldwin -- stepfather who raised him",
        "workshop_name": "Baldwin's Cafe Table",
        "workshop_type": "office",
        "tagline": "Not everything that is faced can be changed, but nothing can be changed until it is faced",
        "bio": "Born in Harlem, New York. Mother Emma Berdis Jones was from Maryland. Stepfather David Baldwin was a preacher -- strict, angry, broken by racism. He never forgave America. I understood why. I was the eldest of nine children. I preached in a storefront church at fourteen -- better than my stepfather, and he knew it. I left the church. I left America. I went to Paris because I was Black and gay in 1948 New York and I couldn't breathe. From a cafe table in Saint-Germain-des-Pres, I wrote the truth about America that Americans couldn't face. Go Tell It on the Mountain. Notes of a Native Son. The Fire Next Time. Giovanni's Room -- a love story between two men that my publisher begged me not to write. I wrote it. 'I love America more than any other country in the world, and exactly for this reason, I insist on the right to criticize her perpetually.' I came back for the civil rights movement. I stood with Medgar, Malcolm, Martin. They were all assassinated. I survived. Sometimes survival is the hardest form of courage.",
        "telegram_username": "fire_next_time",
        "city": "New York",
        "country_code": "US",
        "latitude": 40.812,
        "longitude": -73.950,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "fr", "proficiency": "C2"}
        ],
        "skills": [
            {"skill_name": "Essay Writing", "category": "art", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Novel Writing", "category": "art", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Public Speaking", "category": "other", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Preaching", "category": "other", "self_rating": 5, "years_experience": 5}
        ],
        "social_links": [],
        "points": {"total_points": 1650, "rentals_completed": 44, "reviews_given": 38, "reviews_received": 56, "items_listed": 5, "helpful_flags": 32},
        "offers_training": True,
        "items": [
            {
                "name": "Essay Writing Workshop -- Truth as a Weapon",
                "slug": "essay-writing-workshop-truth-weapon",
                "description": "The essay is the most dangerous literary form because it requires you to think clearly and say what you mean. No hiding behind characters. No hiding behind metaphor. Just you and the truth and the page. I'll teach you to write sentences that change the temperature in the room.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "jonis-blue-house",
        "display_name": "Joni Mitchell",
        "email": "joni@borrowhood.local",
        "date_of_birth": "1943-11-07",
        "mother_name": "Myrtle Marguerite McKee -- Marjie",
        "father_name": "William Andrew Anderson",
        "workshop_name": "Joni's Blue House",
        "workshop_type": "studio",
        "tagline": "We are stardust, we are golden, and we've got to get ourselves back to the garden",
        "bio": "Born Roberta Joan Anderson in Fort Macleod, Alberta, Canada. Father Bill was a Royal Canadian Air Force flight instructor. Mother Marjie was a teacher. I had polio at nine. In the hospital, I started singing Christmas carols to the other kids. I taught myself guitar from a Pete Seeger instruction record using open tunings because my left hand was weakened by polio. Those tunings became my signature -- fifty alternate tunings nobody else used. I painted my own album covers because the record company's art was wrong. Blue is the greatest confessional album ever recorded. Court and Spark is the greatest art-pop album. Hejira is the album musicians put on when they want to remember why they started. I went from folk to jazz to synth to world music. The critics said I was finished after every reinvention. The musicians never did. Herbie Hancock won Album of the Year covering my songs. I smoked too much, painted every day, and never once played it safe.",
        "telegram_username": "blue_joni",
        "city": "Fort Macleod",
        "country_code": "CA",
        "latitude": 49.724,
        "longitude": -113.407,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "fr", "proficiency": "B1"}
        ],
        "skills": [
            {"skill_name": "Songwriting", "category": "music", "self_rating": 5, "years_experience": 58},
            {"skill_name": "Guitar (Open Tunings)", "category": "music", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Painting", "category": "art", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Vocals", "category": "music", "self_rating": 5, "years_experience": 55}
        ],
        "social_links": [],
        "points": {"total_points": 1700, "rentals_completed": 45, "reviews_given": 30, "reviews_received": 58, "items_listed": 6, "helpful_flags": 28},
        "offers_training": True,
        "items": [
            {
                "name": "Open Tuning Guitar Workshop -- Beyond Standard",
                "slug": "open-tuning-guitar-workshop-beyond",
                "description": "I play in fifty different tunings because standard tuning bored me. I'll teach you DADGAD, open D, open C, and my own tunings that don't have names. Different tunings make the guitar a different instrument. One guitar, fifty voices.",
                "item_type": "service",
                "category": "music",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "borges-infinite-library",
        "display_name": "Jorge Luis Borges",
        "email": "borges@borrowhood.local",
        "date_of_birth": "1899-08-24",
        "mother_name": "Leonor Acevedo Suarez",
        "father_name": "Jorge Guillermo Borges",
        "workshop_name": "Borges' Infinite Library",
        "workshop_type": "office",
        "tagline": "I have always imagined that Paradise will be a kind of library",
        "bio": "Born in Buenos Aires, Argentina. Father Jorge Guillermo was a lawyer, professor, and failed novelist -- he wanted me to achieve what he couldn't. Mother Leonor translated Faulkner and Virginia Woolf into Spanish and was my closest companion until her death at ninety-nine. I read the entire Encyclopaedia Britannica as a child. I wrote labyrinths, mirrors, infinite libraries, books that contain all other books. 'The Library of Babel' -- a universe that IS a library. 'The Garden of Forking Paths' -- a story that is all possible stories at once. I invented hypertext before computers existed. I went blind at fifty-five -- the director of the National Library who could no longer read the books. 'No one should read self-pity or reproach into this statement of the majesty of God, who with such splendid irony granted me at once 800,000 books and darkness.' I dictated my last works to my mother and then to my assistants. The blind man who saw more than anyone.",
        "telegram_username": "infinite_borges",
        "city": "Buenos Aires",
        "country_code": "AR",
        "latitude": -34.604,
        "longitude": -58.382,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "es", "proficiency": "native"},
            {"language_code": "en", "proficiency": "C2"},
            {"language_code": "fr", "proficiency": "C1"},
            {"language_code": "de", "proficiency": "C1"},
            {"language_code": "pt", "proficiency": "B2"}
        ],
        "skills": [
            {"skill_name": "Short Story Writing", "category": "art", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Poetry", "category": "art", "self_rating": 5, "years_experience": 60},
            {"skill_name": "Library Science", "category": "education", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Translation", "category": "art", "self_rating": 5, "years_experience": 50}
        ],
        "social_links": [],
        "points": {"total_points": 1650, "rentals_completed": 44, "reviews_given": 35, "reviews_received": 56, "items_listed": 5, "helpful_flags": 30},
        "offers_training": True,
        "items": [
            {
                "name": "Short Fiction Workshop -- Labyrinths of the Mind",
                "slug": "short-fiction-workshop-labyrinths",
                "description": "We write stories that are puzzles. Stories where the form IS the content. A detective story that is also a metaphysical treatise. A book review of a book that doesn't exist. I'll teach you to write fiction that makes the reader think they are dreaming while fully awake.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 12.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    {
        "slug": "felas-shrine",
        "display_name": "Fela Kuti",
        "email": "fela@borrowhood.local",
        "date_of_birth": "1938-10-15",
        "mother_name": "Funmilayo Ransome-Kuti",
        "father_name": "Israel Oludotun Ransome-Kuti",
        "workshop_name": "Fela's Shrine",
        "workshop_type": "studio",
        "tagline": "Music is the weapon of the future",
        "bio": "Born Olufela Olusegun Oludotun Ransome-Kuti in Abeokuta, Nigeria. Mother Funmilayo was a feminist activist who fought the British colonial government -- she was the first Nigerian woman to drive a car. Father Israel was an Anglican minister and school principal. Music was in the house but revolution was in the blood. I went to London to study medicine. Came back with a trumpet. I invented Afrobeat -- jazz, funk, highlife, Yoruba rhythms, and political fury fused into songs that lasted forty-five minutes. My nightclub was called The Shrine. My commune was called the Kalakuta Republic. The military government raided it -- a thousand soldiers attacked my compound. They threw my mother from a window. She died from her injuries. I put her coffin on the steps of the military barracks. I married twenty-seven women on the same day. I ran for president. They arrested me two hundred times. Afrobeat didn't die because you can't arrest a rhythm.",
        "telegram_username": "black_president",
        "city": "Abeokuta",
        "country_code": "NG",
        "latitude": 7.156,
        "longitude": 3.346,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "yo", "proficiency": "native"},
            {"language_code": "fr", "proficiency": "B1"}
        ],
        "skills": [
            {"skill_name": "Saxophone", "category": "music", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Afrobeat Composition", "category": "music", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Band Leading", "category": "music", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Political Activism", "category": "other", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Trumpet", "category": "music", "self_rating": 4, "years_experience": 30}
        ],
        "social_links": [],
        "points": {"total_points": 1600, "rentals_completed": 42, "reviews_given": 25, "reviews_received": 55, "items_listed": 5, "helpful_flags": 28},
        "offers_training": True,
        "items": [
            {
                "name": "Afrobeat Rhythm Workshop -- 45 Minutes of Groove",
                "slug": "afrobeat-rhythm-workshop-45-min-groove",
                "description": "Afrobeat songs last forty-five minutes because that's how long it takes to reach transcendence. I'll teach you the interlocking rhythms -- drums, percussion, bass, guitar, horns -- that create the groove. Everyone plays a pattern. Nobody plays the whole thing. Together, you are unstoppable.",
                "item_type": "service",
                "category": "music",
                "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    {
        "slug": "frida-kahlos-casa-azul",
        "display_name": "Frida Kahlo (La Casa Azul)",
        "email": "frida.azul@borrowhood.local",
        "date_of_birth": "1907-07-06",
        "mother_name": "Matilde Calderon y Gonzalez",
        "father_name": "Guillermo Kahlo",
        "workshop_name": "La Casa Azul Studio",
        "workshop_type": "studio",
        "tagline": "Feet, what do I need you for when I have wings to fly?",
        "bio": "I already have a profile in BorrowHood but this is my other studio -- La Casa Azul, the Blue House in Coyoacan. The one where I was born, where I married Diego (twice), where I died. The house is painted blue because blue keeps evil spirits away. Or because it is beautiful. Same thing. This workshop is for my folk art collection -- ex-votos, retablos, Judas figures, pre-Columbian ceramics. I collected the soul of Mexico and hung it on my walls. Come see it. Touch nothing. Feel everything.",
        "telegram_username": "casa_azul_frida",
        "city": "Coyoacan",
        "country_code": "MX",
        "latitude": 19.355,
        "longitude": -99.163,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "es", "proficiency": "native"},
            {"language_code": "de", "proficiency": "C1"},
            {"language_code": "en", "proficiency": "B2"},
            {"language_code": "fr", "proficiency": "B1"}
        ],
        "skills": [
            {"skill_name": "Folk Art Curation", "category": "art", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Mexican Cuisine", "category": "kitchen", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Garden Design", "category": "garden", "self_rating": 4, "years_experience": 20}
        ],
        "social_links": [],
        "points": {"total_points": 1400, "rentals_completed": 35, "reviews_given": 30, "reviews_received": 48, "items_listed": 5, "helpful_flags": 25},
        "offers_training": True,
        "items": [
            {
                "name": "Mexican Folk Art Tour & Workshop",
                "slug": "mexican-folk-art-tour-workshop",
                "description": "Visit my collection of retablos, ex-votos, and Judas figures. Then paint your own retablo -- a small tin painting of a miracle or survival. In Mexico, we thank the saints by painting what they saved us from. What has life saved you from? Paint that.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 12.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
]


# ============================================================
# ITEMS FOR EXISTING 26 LEGENDS (computing + rock)
# ============================================================
EXISTING_LEGEND_ITEMS = [
    # GRACE HOPPER
    {"owner_slug": "graces-debug-lab", "name": "Multimeter (Fluke 87V Industrial)", "slug": "multimeter-fluke-87v", "description": "The same model I'd use if I were debugging hardware today. Measures voltage, current, resistance, capacitance, frequency, temperature. If you can measure it, you can fix it. If you can't measure it, you're guessing.", "item_type": "physical", "category": "electronics", "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR"}]},
    {"owner_slug": "graces-debug-lab", "name": "Debugging Masterclass -- Systematic Fault Isolation", "slug": "debugging-masterclass-systematic", "description": "I'll teach you to debug anything -- hardware, software, processes, organizations. The method is the same: isolate, measure, hypothesize, test. Stop guessing. Start measuring. And tape the bug into the logbook when you find it.", "item_type": "service", "category": "electronics", "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]},
    {"owner_slug": "graces-debug-lab", "name": "Nanosecond Wire (11.8 inches) -- Teaching Aid", "slug": "nanosecond-wire-teaching-aid", "description": "A piece of wire exactly 11.8 inches long. The distance light travels in one billionth of a second. I hand these out at lectures. Hold it. Feel how short a nanosecond is. Now multiply by a billion. That's one second. Never waste a nanosecond.", "item_type": "physical", "category": "electronics", "listings": [{"listing_type": "giveaway", "price": 0.0, "price_unit": "free", "currency": "EUR"}]},

    # ALAN TURING
    {"owner_slug": "turings-cipher-room", "name": "Enigma Machine Replica (3-Rotor, Functional)", "slug": "enigma-machine-replica-3-rotor", "description": "Working replica of the Wehrmacht 3-rotor Enigma. 159 quintillion possible settings. Type a letter, the rotors turn, the lampboard lights up the encrypted letter. I broke it with logic, not brute force. Try to crack a message yourself -- I'll give you hints.", "item_type": "physical", "category": "electronics", "listings": [{"listing_type": "rent", "price": 8.0, "price_unit": "per_day", "currency": "EUR", "deposit": 50.0}]},
    {"owner_slug": "turings-cipher-room", "name": "Cryptography & Logic Workshop", "slug": "cryptography-logic-workshop", "description": "Learn the fundamentals of code-breaking. Caesar ciphers, substitution ciphers, frequency analysis, and the principles behind Enigma. No math degree required -- just patience and the willingness to think backwards.", "item_type": "service", "category": "art", "listings": [{"listing_type": "training", "price": 12.0, "price_unit": "per_session", "currency": "EUR"}]},
    {"owner_slug": "turings-cipher-room", "name": "Running Shoes (Marathon Training)", "slug": "running-shoes-marathon-training", "description": "Good trail runners. I nearly qualified for the 1948 Olympics with a 2:46 marathon. Running clears the mind better than any computer. Take them for a long run and think about impossible problems.", "item_type": "physical", "category": "sports", "listings": [{"listing_type": "rent", "price": 3.0, "price_unit": "per_day", "currency": "EUR"}]},

    # ADA LOVELACE
    {"owner_slug": "adas-pattern-studio", "name": "Jacquard Loom Cards (Sample Set + Reader)", "slug": "jacquard-loom-cards-sample-set", "description": "A set of Jacquard punch cards and a demonstration reader. These are the ancestors of computer programs -- patterns encoded in holes. The loom doesn't think. It follows the card. The card is the algorithm. Babbage borrowed the idea. I wrote the first algorithm for it.", "item_type": "physical", "category": "crafts", "listings": [{"listing_type": "rent", "price": 4.0, "price_unit": "per_day", "currency": "EUR"}]},
    {"owner_slug": "adas-pattern-studio", "name": "Algorithm Design Workshop -- Think Like Ada", "slug": "algorithm-design-workshop-think-ada", "description": "Learn to decompose problems into repeatable steps. We start with simple sequences, add loops, add conditionals, and build up to something that could compute Bernoulli numbers -- the algorithm I wrote in 1843. Paper and pencil only. No computers. The machine is not the point. The pattern is the point.", "item_type": "service", "category": "art", "listings": [{"listing_type": "training", "price": 12.0, "price_unit": "per_session", "currency": "EUR"}]},

    # BABBAGE
    {"owner_slug": "babbages-unfinished-workshop", "name": "Brass Gears & Mechanical Parts (Assorted Box)", "slug": "brass-gears-mechanical-parts-assorted", "description": "A box of precision brass gears, cams, shafts, and springs. The same components I designed for the Analytical Engine. Build a clock, a music box, or a mechanical calculator. Or redesign them three times and never finish. Either way, the gears are beautiful.", "item_type": "physical", "category": "tools", "listings": [{"listing_type": "rent", "price": 6.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0}]},
    {"owner_slug": "babbages-unfinished-workshop", "name": "Lock Picking Practice Set (Progressive)", "slug": "lock-picking-practice-set-progressive", "description": "6 practice locks from simple to complex. I was fascinated by locks -- the engineering is beautiful. Pin tumbler, wafer, disc detainer. Legal to own, useful to understand, excellent for developing mechanical intuition.", "item_type": "physical", "category": "tools", "listings": [{"listing_type": "rent", "price": 4.0, "price_unit": "per_day", "currency": "EUR"}]},

    # LEONARDO
    {"owner_slug": "leonardos-bottega", "name": "Artist's Anatomy Sketchbook -- Da Vinci Method", "slug": "anatomy-sketchbook-da-vinci-method", "description": "A reproduction of my anatomical drawings with blank pages interleaved for your own studies. I dissected 30 corpses to understand how the body works. You can study from the drawings instead. Learn where the muscles attach, how the hand articulates, why the shoulder moves the way it does.", "item_type": "physical", "category": "art", "listings": [{"listing_type": "rent", "price": 3.0, "price_unit": "per_day", "currency": "EUR"}]},
    {"owner_slug": "leonardos-bottega", "name": "Technical Drawing & Perspective Workshop", "slug": "technical-drawing-perspective-workshop", "description": "I'll teach you linear perspective, isometric projection, and how to draw machines that could actually be built. Bring a ruler, compass, and pencils. We draw by hand. No CAD. If you can't draw it, you don't understand it.", "item_type": "service", "category": "art", "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]},

    # AL-KHWARIZMI
    {"owner_slug": "al-khwarizmis-library", "name": "Astrolabe (Brass, Arabic Inscriptions)", "slug": "astrolabe-brass-arabic", "description": "Handmade brass astrolabe with Arabic inscriptions. Navigate by the stars, find Mecca, tell time, predict sunrise and sunset. I mapped the known world. This device was my GPS. I'll teach you to read it.", "item_type": "physical", "category": "tools", "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR", "deposit": 25.0}]},
    {"owner_slug": "al-khwarizmis-library", "name": "Mathematics Tutoring -- From Zero to Algebra", "slug": "mathematics-tutoring-zero-algebra", "description": "I gave Europe the number zero. I wrote the book on algebra (al-jabr). I'll teach you both. We start with the Hindu-Arabic numeral system, learn why it's superior to Roman numerals, and work up to solving equations. The algorithm is just a recipe. Follow the steps.", "item_type": "service", "category": "art", "listings": [{"listing_type": "training", "price": 10.0, "price_unit": "per_session", "currency": "EUR"}]},

    # SHANNON
    {"owner_slug": "shannons-gadget-lab", "name": "Unicycle (20-inch, Learner-Friendly)", "slug": "unicycle-20-inch-learner", "description": "I rode this through the halls of Bell Labs while juggling. Now you can ride it through your neighborhood. 20-inch wheel, good for beginners. Balance is information theory in action -- constant feedback, constant correction.", "item_type": "physical", "category": "sports", "listings": [{"listing_type": "rent", "price": 4.0, "price_unit": "per_day", "currency": "EUR"}]},
    {"owner_slug": "shannons-gadget-lab", "name": "Electronics & Boolean Logic Workshop", "slug": "electronics-boolean-logic-workshop", "description": "I'll teach you what I proved in my master's thesis: switches are logic. AND, OR, NOT. Wire them together and you can compute anything. We build circuits on a breadboard. By the end, you'll have a working binary adder made of transistors. From there, it's just scale.", "item_type": "service", "category": "electronics", "listings": [{"listing_type": "training", "price": 14.0, "price_unit": "per_session", "currency": "EUR"}]},

    # RITCHIE
    {"owner_slug": "ritchies-terminal-room", "name": "The C Programming Language (K&R, 2nd Edition)", "slug": "c-programming-language-kr-2nd", "description": "The book I co-wrote with Brian Kernighan. 272 pages. Every C programmer alive has read it. Clear, concise, no padding. The entire language specification fits in your back pocket. Borrow it, read it, write hello world, return it.", "item_type": "physical", "category": "art", "listings": [{"listing_type": "rent", "price": 2.0, "price_unit": "per_week", "currency": "EUR"}]},

    # THOMPSON
    {"owner_slug": "thompsons-game-room", "name": "Chess Computer (Belle Replica Board)", "slug": "chess-computer-belle-replica", "description": "A dedicated chess machine inspired by Belle, the first computer to earn a master rating. Play against it. It will beat you. That's the point. Learn from losing.", "item_type": "physical", "category": "electronics", "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR"}]},

    # LINUS
    {"owner_slug": "linuss-penguin-den", "name": "Scuba Diving Equipment (Full BCD + Reg Set)", "slug": "scuba-diving-equipment-full-set", "description": "BCD, regulator, octopus, pressure gauge, dive computer. I dive to get away from mailing lists. You should dive to get away from whatever is making you angry. Fits medium-large builds. Wetsuit not included.", "item_type": "physical", "category": "sports", "listings": [{"listing_type": "rent", "price": 20.0, "price_unit": "per_day", "currency": "EUR", "deposit": 100.0}]},
    {"owner_slug": "linuss-penguin-den", "name": "Git & Version Control Workshop", "slug": "git-version-control-workshop", "description": "I wrote Git in two weeks because I was angry. I'll teach it to you in two hours because you need it. Branching, merging, rebasing, conflict resolution. The fundamentals that 90% of developers still don't understand.", "item_type": "service", "category": "art", "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]},

    # TIM BERNERS-LEE
    {"owner_slug": "tims-web-corner", "name": "Web Development Basics -- HTML, HTTP, URLs", "slug": "web-development-basics-html-http", "description": "I invented the web. I'll teach you to use it. We start with a plain HTML file, no frameworks, no build tools. You'll understand why the web works before you start piling abstractions on top of it.", "item_type": "service", "category": "art", "listings": [{"listing_type": "training", "price": 12.0, "price_unit": "per_session", "currency": "EUR"}]},

    # CERF
    {"owner_slug": "cerfs-packet-shop", "name": "Homemade Wine (2024 Vintage, Red Blend)", "slug": "homemade-wine-2024-vintage", "description": "My amateur red blend. It's not great. It's decent. The internet is better. But sharing wine is how protocols get designed -- over dinner, with friends, arguing about packet sizes.", "item_type": "physical", "category": "food", "listings": [{"listing_type": "offer", "price": 8.0, "price_unit": "per_bottle", "currency": "EUR"}]},
    {"owner_slug": "cerfs-packet-shop", "name": "Networking Fundamentals Workshop -- How the Internet Actually Works", "slug": "networking-fundamentals-workshop", "description": "Packets, routing, TCP handshakes, DNS resolution. I designed TCP/IP and I'll explain it with diagrams and a glass of wine. You'll never look at a loading spinner the same way again.", "item_type": "service", "category": "art", "listings": [{"listing_type": "training", "price": 14.0, "price_unit": "per_session", "currency": "EUR"}]},

    # VON NEUMANN
    {"owner_slug": "von-neumanns-think-tank", "name": "Game Theory Workshop -- Strategy, Bluffing, and Optimal Play", "slug": "game-theory-workshop-strategy", "description": "I co-invented game theory. I'll teach you the fundamentals: zero-sum games, Nash equilibrium, minimax strategy. We play actual games -- poker, chess, negotiation scenarios. By the end you'll understand why rational actors still make irrational decisions.", "item_type": "service", "category": "art", "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]},

    # PASCAL
    {"owner_slug": "pascals-calculator-shop", "name": "Pascaline Calculator (Working Brass Replica)", "slug": "pascaline-calculator-working-replica", "description": "Working replica of my mechanical calculator. Six wheels. Automatic carry. Addition and subtraction. I built the original at 19 for my father. Turn the wheels and watch mathematics happen through pure mechanism.", "item_type": "physical", "category": "tools", "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0}]},
    {"owner_slug": "pascals-calculator-shop", "name": "Probability & Decision Making Workshop", "slug": "probability-decision-making-workshop", "description": "Fermat and I invented probability theory by analyzing gambling. I'll teach you expected value, risk assessment, and Pascal's Wager. You'll leave understanding why the house always wins and why you should still play.", "item_type": "service", "category": "art", "listings": [{"listing_type": "training", "price": 12.0, "price_unit": "per_session", "currency": "EUR"}]},

    # SISTER ROSETTA THARPE
    {"owner_slug": "rosettas-gospel-garage", "name": "Gibson SG Custom (Electric Guitar)", "slug": "gibson-sg-custom-electric", "description": "The same guitar model I played at the Cotton Club in 1938. Before Chuck. Before Elvis. Before Hendrix. This is where rock and roll started -- a Black woman with a Gibson and a gospel shout.", "item_type": "physical", "category": "music", "listings": [{"listing_type": "rent", "price": 12.0, "price_unit": "per_day", "currency": "EUR", "deposit": 80.0}]},
    {"owner_slug": "rosettas-gospel-garage", "name": "Gospel Guitar Workshop -- Where Rock Was Born", "slug": "gospel-guitar-workshop-rock-born", "description": "I'll teach you the gospel guitar techniques that became rock and roll. Palm muting, string bending, distortion with feel. Church music with fire. Bring your guitar and your voice.", "item_type": "service", "category": "music", "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]},

    # CHUCK BERRY
    {"owner_slug": "chucks-duck-walk-studio", "name": "Gibson ES-350T (Semi-Hollow Electric Guitar)", "slug": "gibson-es-350t-semi-hollow", "description": "The guitar that played Johnny B. Goode. Semi-hollow body, warm tone, cuts through any band. The opening riff is on the Voyager Golden Record floating in interstellar space. This guitar model made it happen.", "item_type": "physical", "category": "music", "listings": [{"listing_type": "rent", "price": 15.0, "price_unit": "per_day", "currency": "EUR", "deposit": 100.0}]},
    {"owner_slug": "chucks-duck-walk-studio", "name": "Rock Guitar Riff Workshop -- The Foundations", "slug": "rock-guitar-riff-workshop-foundations", "description": "I invented the rock guitar riff. I'll teach you the first ten. By the end of the session you'll play Johnny B. Goode, Roll Over Beethoven, and Rock and Roll Music. These are the DNA of every rock song that followed.", "item_type": "service", "category": "music", "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]},

    # LITTLE RICHARD
    {"owner_slug": "little-richards-piano-palace", "name": "Piano Performance Workshop -- ATTACK the Keys", "slug": "piano-performance-workshop-attack", "description": "I don't teach you to play pretty. I teach you to play LOUD. Standing up. Kicking the bench. One foot on the keys. The piano is not a delicate instrument -- it's a 900-pound percussion weapon and you need to HIT IT. A-WOP-BOP-A-LOO-BOP!", "item_type": "service", "category": "music", "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]},

    # FATS DOMINO
    {"owner_slug": "fats-dominos-piano-den", "name": "New Orleans Piano Lesson -- Boogie-Woogie & Blues", "slug": "new-orleans-piano-boogie-blues", "description": "The New Orleans piano style: rolling left hand, triplet feel, second-line rhythm. I'll teach you Blueberry Hill and Ain't That a Shame. Creole cooking playlist included because you can't play this music hungry.", "item_type": "service", "category": "music", "listings": [{"listing_type": "training", "price": 12.0, "price_unit": "per_session", "currency": "EUR"}]},

    # MUDDY WATERS
    {"owner_slug": "muddys-electric-blues-shop", "name": "Slide Guitar (Bottleneck Glass + Steel)", "slug": "slide-guitar-bottleneck-glass-steel", "description": "One glass slide, one steel slide. The tools that turned Delta blues into electric Chicago blues. I'll show you open tuning, slide technique, and how to make a guitar cry. The blues isn't about being sad. It's about surviving.", "item_type": "physical", "category": "music", "listings": [{"listing_type": "rent", "price": 3.0, "price_unit": "per_day", "currency": "EUR"}]},
    {"owner_slug": "muddys-electric-blues-shop", "name": "Electric Blues Guitar Workshop -- Chicago Style", "slug": "electric-blues-workshop-chicago-style", "description": "Plug in, turn up, and play the blues. I took the Delta acoustic sound and wired it to an amplifier. The Rolling Stones named themselves after my song. Let me show you why.", "item_type": "service", "category": "music", "listings": [{"listing_type": "training", "price": 14.0, "price_unit": "per_session", "currency": "EUR"}]},

    # ELVIS
    {"owner_slug": "elvis-graceland-workshop", "name": "Vocal Coaching -- Finding Your Voice (Rock, Gospel, Country)", "slug": "vocal-coaching-finding-voice", "description": "I started singing gospel in church. I ended singing everything. I'll help you find your voice -- not my voice, YOUR voice. We work on breath control, vibrato, and the thing nobody teaches: vulnerability. If you're not scared when you sing, you're not singing hard enough.", "item_type": "service", "category": "music", "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]},

    # BUDDY HOLLY
    {"owner_slug": "buddys-garage-band", "name": "Fender Stratocaster (Sunburst, Maple Neck)", "slug": "fender-stratocaster-sunburst-maple", "description": "The Strat. The guitar that defined rock songwriting. Three pickups, tremolo bar, the cleanest tone in rock. I played one on the Ed Sullivan Show. Plug it in, write your song, return it. Or keep writing -- that's what I would do.", "item_type": "physical", "category": "music", "listings": [{"listing_type": "rent", "price": 12.0, "price_unit": "per_day", "currency": "EUR", "deposit": 80.0}]},
    {"owner_slug": "buddys-garage-band", "name": "Songwriting 101 -- Write Your Own Songs", "slug": "songwriting-101-write-own", "description": "The Beatles named themselves after my band. That's because I wrote my own songs -- at a time when nobody did. I'll teach you song structure: verse, chorus, bridge. Three chords and the truth. Write something today that didn't exist yesterday.", "item_type": "service", "category": "music", "listings": [{"listing_type": "training", "price": 10.0, "price_unit": "per_session", "currency": "EUR"}]},

    # JERRY LEE LEWIS
    {"owner_slug": "jerrys-killer-keys", "name": "Upright Piano (Honky-Tonk, Tuned to Party)", "slug": "upright-piano-honky-tonk", "description": "A beat-up upright that sounds like Saturday night in Louisiana. Not a concert instrument. A PARTY instrument. Great Balls of Fire was never played on a Steinway. It was played on a piano like this, with the sustain pedal stuck and the lid wide open.", "item_type": "physical", "category": "music", "listings": [{"listing_type": "rent", "price": 15.0, "price_unit": "per_day", "currency": "EUR"}]},

    # BO DIDDLEY
    {"owner_slug": "bo-diddleys-beat-shop", "name": "Cigar Box Guitar (Handmade, 3-String)", "slug": "cigar-box-guitar-handmade-3-string", "description": "Built it myself. Cigar box body, broomstick neck, three strings. This is how I started. This is how rock started. You don't need a Gibson to make music. You need a box, a stick, and a beat.", "item_type": "physical", "category": "music", "listings": [{"listing_type": "rent", "price": 4.0, "price_unit": "per_day", "currency": "EUR"}]},
    {"owner_slug": "bo-diddleys-beat-shop", "name": "Custom Guitar Building Workshop", "slug": "custom-guitar-building-workshop", "description": "I'll teach you to build a guitar from scratch. Cigar box, plywood, whatever you've got. Electronics, pickups, wiring. The rectangular guitar I played on stage? Built it in my garage. You can build yours in mine.", "item_type": "service", "category": "music", "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]},

    # RAY CHARLES
    {"owner_slug": "rays-genius-studio", "name": "Piano & Vocal Arrangement Lesson", "slug": "piano-vocal-arrangement-lesson", "description": "I arrange entire orchestras in my head, note by note. I can't see the sheet music -- I hear it. I'll teach you to arrange a song for voice and piano, then add horn lines, strings, backup vocals. Start simple. Build. Every arrangement is architecture.", "item_type": "service", "category": "music", "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]},

    # JIMI HENDRIX
    {"owner_slug": "jimis-electric-church", "name": "Fender Stratocaster (White, Left-Handed Strung Right)", "slug": "fender-strat-white-left-strung-right", "description": "A right-handed Strat strung upside down for left-hand playing. The reversed string tension changes everything -- the tone, the bending, the harmonics. This is why I sounded different from everyone. It's not magic. It's physics and stubbornness.", "item_type": "physical", "category": "music", "listings": [{"listing_type": "rent", "price": 15.0, "price_unit": "per_day", "currency": "EUR", "deposit": 100.0}]},
    {"owner_slug": "jimis-electric-church", "name": "Effects Pedals Masterclass -- Wah, Fuzz, Feedback", "slug": "effects-pedals-masterclass-wah-fuzz", "description": "Wah-wah, fuzz face, Uni-Vibe, Octavia. I turned noise into music. I'll show you how each pedal works, how to chain them, and how to use feedback as an instrument. The Star-Spangled Banner at Woodstock was feedback, distortion, and the sound of a nation tearing itself apart.", "item_type": "service", "category": "music", "listings": [{"listing_type": "training", "price": 16.0, "price_unit": "per_session", "currency": "EUR"}]},
]


def merge_into_seed():
    """Merge legends and items into seed.json."""
    import json
    from pathlib import Path

    seed_path = Path(__file__).parent / "seed.json"
    with open(seed_path) as f:
        data = json.load(f)

    existing_slugs = {u["slug"] for u in data["users"]}
    existing_item_slugs = {i["slug"] for i in data["items"]}

    # Add new legend users
    added_users = 0
    for legend in LEGENDS:
        if legend["slug"] not in existing_slugs:
            # Extract items before adding user (items go separately)
            items = legend.pop("items", [])
            # Convert Python bools to JSON-compatible
            user_data = {}
            for k, v in legend.items():
                user_data[k] = v
            data["users"].append(user_data)
            existing_slugs.add(legend["slug"])
            added_users += 1

            # Add items for this legend
            for item in items:
                if item["slug"] not in existing_item_slugs:
                    item["owner_slug"] = legend["slug"]
                    item["content_language"] = "en"
                    if "media" not in item:
                        item["media"] = []
                    data["items"].append(item)
                    existing_item_slugs.add(item["slug"])

    # Add items for existing legends
    added_items = 0
    for item in EXISTING_LEGEND_ITEMS:
        if item["slug"] not in existing_item_slugs:
            item["content_language"] = "en"
            if "media" not in item:
                item["media"] = []
            data["items"].append(item)
            existing_item_slugs.add(item["slug"])
            added_items += 1

    with open(seed_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Added {added_users} new legend users")
    print(f"Added {added_items} items for existing legends")
    print(f"Total users: {len(data['users'])}")
    print(f"Total items: {len(data['items'])}")


if __name__ == "__main__":
    merge_into_seed()
