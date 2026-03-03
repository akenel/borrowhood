#!/usr/bin/env python3
"""Warrior legend seed data for BorrowHood.

34 historical warriors, each with a workshop full of weapons, armor,
and training services they lend, rent, and teach.

Run: python3 seed_data/legends_warriors.py
Output: merges into seed_data/seed.json
"""

LEGENDS_WARRIORS = [
    # ============================================================
    # 1. SPARTACUS (~111-71 BC) - Gladiator rebel, Thrace/Capua
    # ============================================================
    {
        "slug": "spartacus-arena",
        "display_name": "Spartacus",
        "email": "spartacus@borrowhood.local",
        "date_of_birth": "0111-01-01",
        "mother_name": "Unknown -- lost to the slave records of Thrace",
        "father_name": "Unknown -- a free Thracian before Rome took everything",
        "workshop_name": "Spartacus Arena",
        "workshop_type": "arena",
        "tagline": "A free man dies only once. A slave dies every day.",
        "bio": "Born in Thrace, enslaved by Rome, trained as a gladiator at the ludus of Batiatus in Capua. I escaped with 70 gladiators and a handful of kitchen knives. Within two years, 70 became 120,000. We defeated nine Roman armies. Crixus was my brother in arms -- a Gaul with more fury than sense, but loyal to the last. Tip: The first weapon is courage. The second is organization. A mob is not an army -- train your people, feed your people, give them something worth fighting for. Rome crucified 6,000 of us along the Appian Way. They thought that would end the idea. It didn't. Every revolution since carries my name.",
        "telegram_username": "the_gladiator",
        "city": "Capua",
        "country_code": "IT",
        "latitude": 41.106,
        "longitude": 14.213,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "la", "proficiency": "C1"},
            {"language_code": "el", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Gladiatorial Combat", "category": "sports", "self_rating": 5, "years_experience": 15},
            {"skill_name": "Military Leadership", "category": "education", "self_rating": 5, "years_experience": 5},
            {"skill_name": "Guerrilla Tactics", "category": "education", "self_rating": 5, "years_experience": 5},
            {"skill_name": "Survival Skills", "category": "outdoor", "self_rating": 5, "years_experience": 20}
        ],
        "social_links": [],
        "points": {"total_points": 2000, "rentals_completed": 55, "reviews_given": 40, "reviews_received": 65, "items_listed": 7, "helpful_flags": 38},
        "offers_training": True,
        "items": [
            {
                "name": "Gladiator Combat Training -- Arena Fundamentals",
                "slug": "gladiator-combat-training-arena",
                "description": "One-on-one combat training with wooden practice weapons. Gladius technique, shield work, footwork, reading your opponent. Tip: Never attack first. Let them commit, then make them pay for it. We train until your body remembers what your mind forgets under pressure.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Roman Gladius & Scutum (Training Replicas)",
                "slug": "roman-gladius-scutum-training",
                "description": "Weighted wooden gladius and full-size scutum shield replica. The gladius is 24 inches -- short, brutal, designed for close work. The shield is your real weapon -- it creates the opening. The sword just finishes the job.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 6.0, "price_unit": "per_day", "currency": "EUR", "deposit": 25.0}]
            },
            {
                "name": "Leadership Under Pressure Workshop -- Small Group",
                "slug": "leadership-under-pressure-workshop",
                "description": "Small group (max 8). How to lead when everything is against you. No resources, no title, no authority -- just the trust of the people next to you. We use historical scenarios and modern case studies. Tip: People follow courage, not rank.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Survival Kit (Roman Field Pack Recreation)",
                "slug": "survival-kit-roman-field-pack",
                "description": "Recreation of what a Roman soldier carried: canteen, fire kit, rope, blade, dried rations pouch, wool blanket. 30 pounds of everything you need and nothing you don't. I will show you how to make camp with just this.",
                "item_type": "physical",
                "category": "outdoor",
                "listings": [{"listing_type": "rent", "price": 8.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0}]
            },
            {
                "name": "Escape & Evasion Tactics -- Guerrilla Warfare Seminar",
                "slug": "escape-evasion-guerrilla-seminar",
                "description": "Half-day seminar on guerrilla tactics. How 70 escaped slaves outran and outfought professional legions. Route selection, foraging, decoy camps, fighting withdrawal. Tip: Speed is armor. If they cannot find you, they cannot kill you.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # 2. LEONIDAS I (~540-480 BC) - King of Sparta, Thermopylae
    # ============================================================
    {
        "slug": "leonidas-hot-gates",
        "display_name": "Leonidas I",
        "email": "leonidas@borrowhood.local",
        "date_of_birth": "0540-01-01",
        "mother_name": "Unknown -- Spartan records kept lineage through kings, not mothers",
        "father_name": "Anaxandridas II -- King of Sparta, Agiad dynasty",
        "workshop_name": "The Hot Gates Phalanx School",
        "workshop_type": "arena",
        "tagline": "Come and take them.",
        "bio": "King of Sparta, Agiad dynasty. I held Thermopylae with 300 Spartans and 7,000 allied Greeks against Xerxes and over a million Persians. We held for three days. When Ephialtes betrayed the mountain pass, I sent the allies home and stayed with my 300. We knew we were dead. We fought anyway. Gorgo, my queen, was worth ten generals -- when a woman from Attica asked why Spartan women ruled their men, she said: Because only Spartan women give birth to men. Tip: A narrow front negates numerical superiority. Choose your ground, force the enemy to fight on your terms, not his. Terrain is a weapon -- use it.",
        "telegram_username": "molon_labe",
        "city": "Sparta",
        "country_code": "GR",
        "latitude": 37.074,
        "longitude": 22.430,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "el", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Hoplite Combat", "category": "sports", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Phalanx Tactics", "category": "education", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Physical Conditioning", "category": "sports", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Defensive Strategy", "category": "education", "self_rating": 5, "years_experience": 25}
        ],
        "social_links": [],
        "points": {"total_points": 2200, "rentals_completed": 60, "reviews_given": 30, "reviews_received": 75, "items_listed": 6, "helpful_flags": 45},
        "offers_training": True,
        "items": [
            {
                "name": "Spartan Hoplite Shield & Dory Spear -- Training Set",
                "slug": "spartan-aspis-dory-training-set",
                "description": "Full-weight bronze-faced aspis (36 inches, 15 pounds) and 8-foot dory spear replica. The aspis protects the man to your left -- that is the foundation of the phalanx. You fight for your brother, not yourself.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 8.0, "price_unit": "per_day", "currency": "EUR", "deposit": 40.0}]
            },
            {
                "name": "Phalanx Formation Workshop -- Team Combat Drills",
                "slug": "phalanx-formation-workshop",
                "description": "Group session (8-16 people). Learn the Spartan phalanx -- shield wall, spear discipline, advance and retreat as one body. Tip: The phalanx is not a formation. It is a contract. Every man protects the man beside him. Break the contract and the line breaks.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 12.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Spartan Agoge Fitness Program -- 12-Week Conditioning",
                "slug": "spartan-agoge-fitness-program",
                "description": "The agoge started at age 7. Yours starts today. Running, wrestling, cold water immersion, minimal food, maximum effort. Twelve weeks of progressive conditioning based on actual Spartan training methods. Tip: Comfort is the enemy of capability.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Xiphos Short Sword (Bronze Replica)",
                "slug": "xiphos-short-sword-bronze-replica",
                "description": "Leaf-shaped xiphos, 24-inch blade, bronze construction. The backup weapon when the dory breaks. Designed for the crush of close combat where the spear is too long. I used mine at Thermopylae after my spear shattered on the second day.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0}]
            },
            {
                "name": "Defensive Strategy Masterclass -- Hold the Line",
                "slug": "defensive-strategy-masterclass-hold-line",
                "description": "Classroom and field session on defensive warfare. Terrain selection, chokepoint exploitation, force multipliers. Case studies: Thermopylae, Masada, Rorke's Drift. Tip: The defender chooses the ground. The attacker pays the price. Make them pay dearly.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 16.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # 3. ALEXANDER THE GREAT (356-323 BC) - Conqueror, Pella
    # ============================================================
    {
        "slug": "alexanders-war-tent",
        "display_name": "Alexander the Great",
        "email": "alexander@borrowhood.local",
        "date_of_birth": "0356-07-20",
        "mother_name": "Olympias -- princess of Epirus, devotee of Dionysus, kept snakes in her bed",
        "father_name": "Philip II -- King of Macedon, who built the army I inherited",
        "workshop_name": "Alexander's War Tent",
        "workshop_type": "camp",
        "tagline": "There is nothing impossible to him who will try.",
        "bio": "Born in Pella, Macedon. Tutored by Aristotle. Tamed Bucephalus at 12 when grown men could not. By 30, I had conquered from Greece to India -- the largest empire the world had seen. Gaugamela, Issus, the Siege of Tyre, the Hindu Kush. Hephaestion was my closest companion, my Patroclus. I never lost a battle in 15 years. Tip: Speed and audacity win more than numbers. At Gaugamela, I charged Darius directly through the center while his flanks were still deploying. Cut the head off the snake. My men followed me because I bled with them -- always first through the breach.",
        "telegram_username": "son_of_ammon",
        "city": "Pella",
        "country_code": "GR",
        "latitude": 40.762,
        "longitude": 22.524,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "el", "proficiency": "native"},
            {"language_code": "fa", "proficiency": "B2"}
        ],
        "skills": [
            {"skill_name": "Cavalry Tactics", "category": "sports", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Siege Warfare", "category": "education", "self_rating": 5, "years_experience": 15},
            {"skill_name": "Strategic Planning", "category": "education", "self_rating": 5, "years_experience": 15},
            {"skill_name": "Horseback Riding", "category": "sports", "self_rating": 5, "years_experience": 25}
        ],
        "social_links": [],
        "points": {"total_points": 2500, "rentals_completed": 70, "reviews_given": 35, "reviews_received": 80, "items_listed": 8, "helpful_flags": 50},
        "offers_training": True,
        "items": [
            {
                "name": "Companion Cavalry Training -- Mounted Combat",
                "slug": "companion-cavalry-mounted-combat",
                "description": "Mounted combat on horseback with xyston lance and kopis sword. The Companions were the finest cavalry in the ancient world -- we shattered the Persian line at Gaugamela with a wedge charge at gallop. Tip: The horse is not transport. The horse is a weapon. Learn to fight as one creature.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Macedonian Sarissa (18-foot Pike Replica)",
                "slug": "macedonian-sarissa-pike-replica",
                "description": "Full-length sarissa pike, 18 feet, cornel wood shaft with iron head and bronze butt-spike. Five ranks of sarissas project beyond the front line -- nothing wants to charge into that. Counterweight at the butt for one-handed use when the crush begins.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 7.0, "price_unit": "per_day", "currency": "EUR", "deposit": 35.0}]
            },
            {
                "name": "Campaign Planning Workshop -- Logistics of Conquest",
                "slug": "campaign-planning-logistics-conquest",
                "description": "Half-day workshop on campaign logistics. How I moved 50,000 men from Greece to India across deserts, mountains, and rivers. Supply lines, foraging, forced marches, river crossings. Tip: Amateurs talk tactics. Professionals talk logistics. An army that cannot eat cannot fight.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Kopis Sword & Pelte Shield (Cavalry Set)",
                "slug": "kopis-sword-pelte-cavalry-set",
                "description": "Curved kopis blade and small pelte shield. The kopis curves forward -- the weight at the tip means gravity does the work on a downward slash from horseback. This is what the Companions carried after the lance broke. Brutal and efficient.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 7.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0}]
            },
            {
                "name": "Siege Engineering Seminar -- Breaking Walls",
                "slug": "siege-engineering-breaking-walls",
                "description": "The Siege of Tyre took seven months. I built a causeway across the sea to reach an island fortress. Rams, towers, torsion catapults, mining tunnels. Every wall has a weakness. Your job is to find it before your supplies run out.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # 4. HANNIBAL BARCA (247-183 BC) - Carthage/Tunisia
    # ============================================================
    {
        "slug": "hannibals-war-camp",
        "display_name": "Hannibal Barca",
        "email": "hannibal@borrowhood.local",
        "date_of_birth": "0247-01-01",
        "mother_name": "Unknown -- Carthaginian records were destroyed when Rome burned the city",
        "father_name": "Hamilcar Barca -- who made me swear eternal enmity to Rome at age nine",
        "workshop_name": "Hannibal's War Camp",
        "workshop_type": "camp",
        "tagline": "I will either find a way or make one.",
        "bio": "Born in Carthage, raised in Iberia, swore hatred of Rome as a child. I crossed the Alps with 37 war elephants, 50,000 infantry, and 9,000 cavalry -- it had never been done. At Cannae, I encircled and destroyed eight Roman legions -- 70,000 men in a single afternoon. The double envelopment is still taught at every military academy on Earth. Maharbal told me I knew how to win a victory but not how to use one. Scipio Africanus studied my tactics and beat me at Zama with my own methods. Tip: The greatest victory is the battle you win before it starts -- through deception, position, and the enemy's own assumptions.",
        "telegram_username": "barca_thunder",
        "city": "Tunis",
        "country_code": "TN",
        "latitude": 36.806,
        "longitude": 10.182,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "ar", "proficiency": "native"},
            {"language_code": "la", "proficiency": "C1"},
            {"language_code": "el", "proficiency": "B2"}
        ],
        "skills": [
            {"skill_name": "Battle Strategy", "category": "education", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Cavalry Tactics", "category": "sports", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Mountain Warfare", "category": "outdoor", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Deception Tactics", "category": "education", "self_rating": 5, "years_experience": 30}
        ],
        "social_links": [],
        "points": {"total_points": 2400, "rentals_completed": 65, "reviews_given": 38, "reviews_received": 78, "items_listed": 7, "helpful_flags": 48},
        "offers_training": True,
        "items": [
            {
                "name": "Double Envelopment Strategy Workshop -- Cannae Method",
                "slug": "double-envelopment-cannae-method",
                "description": "The battle of Cannae, 216 BC. I let Rome push through my center while my wings closed like a jaw. 70,000 Romans died in one afternoon. Sand table exercises and field simulations. Tip: Invite the enemy to attack where you are weakest. That is where the trap lives.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Iberian Falcata Sword (Reproduction)",
                "slug": "iberian-falcata-sword-reproduction",
                "description": "Curved Iberian falcata. The forward curve concentrates force at impact -- it cuts through bronze armor like leather. My Iberian cavalry used these at Cannae to devastating effect. Includes scabbard and maintenance kit.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 6.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0}]
            },
            {
                "name": "Alpine Survival & Mountain Crossing Workshop",
                "slug": "alpine-survival-mountain-crossing",
                "description": "I took an army over the Alps in autumn. We lost half our men to cold, rockslides, and hostile Gauls. Mountain travel, cold weather survival, route finding, and keeping morale when everything falls apart. Tip: Vinegar on hot rocks splits boulders. Sometimes the path must be made, not found.",
                "item_type": "service",
                "category": "outdoor",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Numidian Cavalry Javelin Set (5 Light Javelins)",
                "slug": "numidian-cavalry-javelin-set",
                "description": "Five light throwing javelins in the Numidian style. My riders under Maharbal would harass Roman columns for days -- throwing, retreating, throwing again. No armor, no shield, just speed and accuracy.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR", "deposit": 20.0}]
            },
            {
                "name": "War Elephant Tactics -- Psychological Warfare Seminar",
                "slug": "war-elephant-psychological-warfare",
                "description": "How to deploy elephants as terror weapons. Mahout positioning, formation breaking, countering elephant charges. The elephant is a psychological weapon first, physical second. Most armies break before the elephant reaches them. Also covers countermeasures -- Rome eventually learned to open lanes and let them through.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # 5. JULIUS CAESAR (100-44 BC) - Roman general, Rome
    # ============================================================
    {
        "slug": "caesars-war-room",
        "display_name": "Julius Caesar",
        "email": "caesar@borrowhood.local",
        "date_of_birth": "0100-07-12",
        "mother_name": "Aurelia Cotta -- the woman who raised an empire-breaker in a Subura slum",
        "father_name": "Gaius Julius Caesar -- died when I was 16, left me a name and nothing else",
        "workshop_name": "Caesar's War Room",
        "workshop_type": "fortress",
        "tagline": "Veni, vidi, vici.",
        "bio": "Born to a patrician family with a famous name and empty pockets. Kidnapped by pirates at 25 -- told them their ransom was too low, raised it myself, then came back and crucified them. Conquered Gaul in eight years. Crossed the Rubicon with one legion and took Rome. Defeated Pompey at Pharsalus. Cleopatra became my ally and lover in Alexandria. Tip: Speed is everything. At Pharsalus, my veterans charged uphill into Pompey's cavalry and aimed for their faces -- pretty boys who had never been cut. They broke. I was stabbed 23 times on the Ides of March. Brutus was there. Et tu, Brute.",
        "telegram_username": "divus_julius",
        "city": "Rome",
        "country_code": "IT",
        "latitude": 41.902,
        "longitude": 12.496,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "la", "proficiency": "native"},
            {"language_code": "el", "proficiency": "C1"}
        ],
        "skills": [
            {"skill_name": "Military Command", "category": "education", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Siege Engineering", "category": "education", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Political Strategy", "category": "education", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Sword Combat", "category": "sports", "self_rating": 4, "years_experience": 25}
        ],
        "social_links": [],
        "points": {"total_points": 2600, "rentals_completed": 72, "reviews_given": 45, "reviews_received": 85, "items_listed": 8, "helpful_flags": 52},
        "offers_training": True,
        "items": [
            {
                "name": "Roman Legion Tactics Workshop -- Command & Control",
                "slug": "roman-legion-tactics-command-control",
                "description": "How to command a Roman legion: manipular formations, signal systems, camp construction, forced marches. My legions marched 25 miles in five hours, then built a fortified camp before dinner. Tip: Discipline is not cruelty. It is the reason 5,000 men can defeat 50,000.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Roman Legionary Kit (Lorica + Gladius + Pilum)",
                "slug": "roman-legionary-kit-full",
                "description": "Complete legionary equipment: segmented plate armor, short gladius, two pila javelins, curved scutum shield. 60 pounds of gear. My men marched with this plus rations and camp stakes. They called themselves Marius' Mules.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 12.0, "price_unit": "per_day", "currency": "EUR", "deposit": 60.0}]
            },
            {
                "name": "Field Fortification Workshop -- Build a Roman Camp",
                "slug": "field-fortification-roman-camp",
                "description": "Hands-on workshop building a Roman marching camp. Ditch, rampart, palisade, gates, interior layout. At Alesia I built two walls -- one facing in to trap Vercingetorix, one facing out to stop his relief army. Tip: If you can build, you can hold. If you can hold, you can win.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Political Rhetoric & Persuasion Seminar",
                "slug": "political-rhetoric-persuasion-seminar",
                "description": "I wrote the Gallic Wars while fighting them. Clear writing is clear thinking. Public speaking, written persuasion, political maneuvering. Cicero was better with words. I was better with timing. Tip: Write in the third person. It makes you sound inevitable.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Centurion's Vine Staff (Vitis) & Pugio Dagger",
                "slug": "centurion-vitis-pugio-dagger",
                "description": "The vine staff was the centurion's badge of office and disciplinary tool. The pugio was the last-resort dagger. Cassius used one on me. Authentic reproductions for historical reenactment and display.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR", "deposit": 20.0}]
            }
        ]
    },

    # ============================================================
    # 6. BOUDICCA (30-61 AD) - Celtic warrior queen, Britain
    # ============================================================
    {
        "slug": "boudiccas-war-chariot",
        "display_name": "Boudicca",
        "email": "boudicca@borrowhood.local",
        "date_of_birth": "0030-01-01",
        "mother_name": "Unknown -- the Romans erased our women from history, but we remember",
        "father_name": "Unknown -- Iceni nobility, a man who raised a queen to fight empires",
        "workshop_name": "Boudicca's War Chariot",
        "workshop_type": "camp",
        "tagline": "It is not as a woman descended from noble ancestry, but as one of the people that I am avenging lost freedom.",
        "bio": "Queen of the Iceni tribe in eastern Britain. When my husband Prasutagus died, Rome took everything. They flogged me and assaulted my daughters. That was the last time Rome made that mistake in Britain. I united the Iceni, Trinovantes, and a dozen tribes. We burned Camulodunum, Londinium, and Verulamium. 80,000 Romans and collaborators died. Suetonius Paulinus caught us on open ground and his legions broke our charge. Tip: Rage is fuel, not strategy. I had the numbers but not the discipline. Burn hot, but think cold.",
        "telegram_username": "iceni_queen",
        "city": "Colchester",
        "country_code": "GB",
        "latitude": 51.889,
        "longitude": 0.904,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Chariot Warfare", "category": "sports", "self_rating": 5, "years_experience": 15},
            {"skill_name": "Tribal Leadership", "category": "education", "self_rating": 5, "years_experience": 10},
            {"skill_name": "Spear Combat", "category": "sports", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Horseback Riding", "category": "sports", "self_rating": 5, "years_experience": 25}
        ],
        "social_links": [],
        "points": {"total_points": 1900, "rentals_completed": 50, "reviews_given": 35, "reviews_received": 60, "items_listed": 6, "helpful_flags": 40},
        "offers_training": True,
        "items": [
            {
                "name": "Celtic War Chariot Driving Experience",
                "slug": "celtic-war-chariot-driving",
                "description": "Two-horse chariot, wicker-and-oak frame. My charioteers galloped along the yoke pole and threw javelins at speed. Tip: The chariot is mobile infantry -- ride to the fight, dismount, fight, ride away.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 28.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Celtic Longsword & Round Shield (Iron Age Replicas)",
                "slug": "celtic-longsword-round-shield-replicas",
                "description": "Iron Age Celtic longsword (30-inch blade for slashing) and lime-wood round shield with iron boss. The Celts fought with fury and individual skill. The Romans fought with system. Both have their place. Weighted for training.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 7.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0}]
            },
            {
                "name": "Uprising Leadership Workshop -- Building a Coalition",
                "slug": "uprising-leadership-coalition-building",
                "description": "How to unite fractious tribes against a common enemy. Managing egos, distributing resources, maintaining alliance cohesion. Tip: People join a cause for different reasons. Give each tribe their reason. But give them ONE leader and ONE plan.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 16.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Celtic Javelin Set (3 Throwing Spears)",
                "slug": "celtic-javelin-set-throwing-spears",
                "description": "Three light throwing javelins, ash shafts with iron heads. Balanced for distance and accuracy. I will teach you the overhand and sidearm throws that my warriors used to open every engagement.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 4.0, "price_unit": "per_day", "currency": "EUR", "deposit": 15.0}]
            }
        ]
    },

    # ============================================================
    # 7. SUN TZU (~544-496 BC) - Art of War, Qi state China
    # ============================================================
    {
        "slug": "sun-tzus-strategy-pavilion",
        "display_name": "Sun Tzu",
        "email": "suntzu@borrowhood.local",
        "date_of_birth": "0544-01-01",
        "mother_name": "Unknown -- the family records of Qi are silent on mothers",
        "father_name": "Sun Wu -- a minor noble of Qi, military lineage",
        "workshop_name": "Sun Tzu's Strategy Pavilion",
        "workshop_type": "pavilion",
        "tagline": "The supreme art of war is to subdue the enemy without fighting.",
        "bio": "Born Sun Wu in Qi during the Warring States period. I served King Helu of Wu as military advisor. When the king doubted my methods, I trained his concubines into soldiers and beheaded two of his favorites when they laughed during drill. He stopped doubting. The Art of War is 13 chapters studied by every general since -- Napoleon, Giap, Schwarzkopf. Tip: All warfare is based on deception. When able, feign inability. When near, make them believe you are far. The battle is won before it begins, in the mind of the commander.",
        "telegram_username": "master_sun",
        "city": "Linzi",
        "country_code": "CN",
        "latitude": 36.811,
        "longitude": 118.318,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "zh", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Military Strategy", "category": "education", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Intelligence Gathering", "category": "education", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Leadership Philosophy", "category": "education", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Terrain Analysis", "category": "outdoor", "self_rating": 5, "years_experience": 30}
        ],
        "social_links": [],
        "points": {"total_points": 2800, "rentals_completed": 80, "reviews_given": 50, "reviews_received": 90, "items_listed": 6, "helpful_flags": 60},
        "offers_training": True,
        "items": [
            {
                "name": "The Art of War Masterclass -- 13 Chapters Deep",
                "slug": "art-of-war-masterclass-13-chapters",
                "description": "Intensive study of all 13 chapters. Not the motivational poster version. Terrain, espionage, fire attacks, the use of spies. Each chapter is a weapon. Most people read Chapter 1 and think they understand war. They do not. Tip: Know yourself, know your enemy. A thousand battles, a thousand victories.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Chinese Jian Sword (Bronze, Warring States Style)",
                "slug": "chinese-jian-sword-warring-states",
                "description": "Double-edged bronze jian, 28-inch blade. The gentleman's weapon of ancient China. Balanced for both thrust and cut. I carried one, though I preferred to win without drawing it.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 6.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0}]
            },
            {
                "name": "Strategic Thinking for Business -- Sun Tzu Applied",
                "slug": "strategic-thinking-business-sun-tzu",
                "description": "Art of War applied to business competition, negotiation, and market strategy. Deception, positioning, intelligence. Every CEO who read my book only understood half. Tip: The best victories are the ones your competitor does not realize they lost until it is too late.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "War Table Sand Map (Campaign Simulation Kit)",
                "slug": "war-table-sand-map-simulation",
                "description": "Traditional Chinese sand table for war gaming. Sculpt terrain, place forces, simulate campaigns. Includes miniature infantry, cavalry, and fortification markers. Better than any screen -- you feel the terrain with your hands.",
                "item_type": "physical",
                "category": "education",
                "listings": [{"listing_type": "rent", "price": 10.0, "price_unit": "per_day", "currency": "EUR", "deposit": 40.0}]
            },
            {
                "name": "Espionage & Intelligence Workshop -- The Five Types of Spies",
                "slug": "espionage-intelligence-five-spies",
                "description": "Chapter 13: the use of spies. Local, inside, converted, doomed, living. Intelligence wins wars before the first arrow flies. Information gathering, disinformation, counter-intelligence with historical and modern examples.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # 8. GENGHIS KHAN (1162-1227) - Mongol Empire
    # ============================================================
    {
        "slug": "genghis-khans-ger",
        "display_name": "Genghis Khan",
        "email": "genghis@borrowhood.local",
        "date_of_birth": "1162-01-01",
        "mother_name": "Hoelun -- kidnapped bride who raised me after my father was poisoned",
        "father_name": "Yesugei -- chief of the Kiyad, poisoned by Tatars when I was nine",
        "workshop_name": "The Great Khan's Ger",
        "workshop_type": "camp",
        "tagline": "I am the punishment of God. If you had not committed great sins, God would not have sent a punishment like me.",
        "bio": "Born Temujin on the Onon River, clutching a blood clot -- the sign of a conqueror. Father murdered when I was nine. I killed my half-brother over a fish. Was captured and wore a cangue. From nothing, I united every Mongol tribe, then conquered half the known world. China, Persia, Russia, Central Asia -- the largest contiguous empire ever. Subutai and Jebe could fight any terrain, any weather. Tip: Loyalty is earned by sharing hardship. I ate the same food as my riders. Promote by merit, not birth. The son of a slave can command if he can lead.",
        "telegram_username": "great_khan",
        "city": "Ulaanbaatar",
        "country_code": "MN",
        "latitude": 47.922,
        "longitude": 106.917,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "mn", "proficiency": "native"},
            {"language_code": "zh", "proficiency": "B1"}
        ],
        "skills": [
            {"skill_name": "Mounted Archery", "category": "sports", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Empire Building", "category": "education", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Steppe Survival", "category": "outdoor", "self_rating": 5, "years_experience": 60},
            {"skill_name": "Horseback Riding", "category": "sports", "self_rating": 5, "years_experience": 55}
        ],
        "social_links": [],
        "points": {"total_points": 3000, "rentals_completed": 85, "reviews_given": 30, "reviews_received": 95, "items_listed": 9, "helpful_flags": 55},
        "offers_training": True,
        "items": [
            {
                "name": "Mounted Archery Training -- Shoot From the Saddle",
                "slug": "mounted-archery-shoot-from-saddle",
                "description": "Mongol children ride at three, shoot at five. Mounted archery at walk, trot, and canter. Composite recurve, thumb draw, the Parthian shot. Tip: Do not aim. Become the arrow. Your body knows the trajectory.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 30.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Mongol Composite Recurve Bow & Quiver (30 Arrows)",
                "slug": "mongol-composite-recurve-bow-quiver",
                "description": "Laminated horn-sinew-wood composite bow, 160-pound draw. Effective range 350 yards. Comes with 30 arrows -- armor-piercing, broad-head, and whistling signal arrows. I will string it for you. Most people cannot.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 10.0, "price_unit": "per_day", "currency": "EUR", "deposit": 50.0}]
            },
            {
                "name": "Steppe Survival Workshop -- Live Off the Land",
                "slug": "steppe-survival-live-off-land",
                "description": "Three-day outdoor survival. How the Mongol army traveled without supply lines. Dried meat under the saddle, fermented mare's milk, hunting on the move. Tip: A Mongol rider carries 10 days of food in two saddlebags. Learn to need less.",
                "item_type": "service",
                "category": "outdoor",
                "listings": [{"listing_type": "training", "price": 35.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Mongol Deel Robe & Leather Armor Set",
                "slug": "mongol-deel-robe-leather-armor",
                "description": "Traditional deel robe (silk-lined wool) plus lamellar leather armor. The silk undershirt wrapped around arrowheads on impact, making them easier to pull out. Every layer serves a purpose.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 8.0, "price_unit": "per_day", "currency": "EUR", "deposit": 35.0}]
            },
            {
                "name": "Empire Administration Seminar -- Yasa Law & Governance",
                "slug": "empire-administration-yasa-law",
                "description": "I conquered the world and governed it. The Yasa established religious freedom, diplomatic immunity, meritocracy, and a continental postal relay. Tip: Conquer with the sword, govern with the law. An empire held only by fear will not survive its founder.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # 9. JOAN OF ARC (1412-1431) - Maid of Orleans
    # ============================================================
    {
        "slug": "joans-banner-hall",
        "display_name": "Joan of Arc",
        "email": "joan@borrowhood.local",
        "date_of_birth": "1412-01-06",
        "mother_name": "Isabelle Romee -- walked barefoot to Rome on pilgrimage",
        "father_name": "Jacques d'Arc -- farmer and minor village official of Domremy",
        "workshop_name": "Joan's Banner Hall",
        "workshop_type": "fortress",
        "tagline": "I am not afraid. I was born to do this.",
        "bio": "A peasant girl from Domremy who heard Saints Michael, Catherine, and Margaret at age 13. They told me to drive the English from France and crown the Dauphin at Reims. I was 17 when I convinced a king to give me an army. Broke the Siege of Orleans in nine days after seven months of English control. La Hire and Gilles de Rais fought at my side -- rough men who knelt before a teenage girl because she was right. Tip: Conviction is the ultimate weapon. I could not read or write or hold a sword. But I knew what needed doing. The Burgundians sold me. The English burned me at Rouen. I was 19. Five hundred years later, they made me a saint.",
        "telegram_username": "la_pucelle",
        "city": "Domremy-la-Pucelle",
        "country_code": "FR",
        "latitude": 48.443,
        "longitude": 5.675,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "fr", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Inspirational Leadership", "category": "education", "self_rating": 5, "years_experience": 3},
            {"skill_name": "Siege Warfare", "category": "education", "self_rating": 5, "years_experience": 2},
            {"skill_name": "Horseback Riding", "category": "sports", "self_rating": 4, "years_experience": 3},
            {"skill_name": "Banner Bearing", "category": "sports", "self_rating": 5, "years_experience": 2}
        ],
        "social_links": [],
        "points": {"total_points": 2100, "rentals_completed": 45, "reviews_given": 55, "reviews_received": 70, "items_listed": 6, "helpful_flags": 50},
        "offers_training": True,
        "items": [
            {
                "name": "Inspirational Leadership Workshop -- Lead Without Authority",
                "slug": "inspirational-leadership-without-authority",
                "description": "I had no rank, no education, no training. I led because I believed and they saw it. How to lead with nothing but conviction. Speaking to crowds, rallying morale, hard decisions. Tip: Do not ask people to follow you. Walk toward the danger and see who comes.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Joan's Banner (Replica -- Fleur-de-lis on White)",
                "slug": "joans-banner-fleur-de-lis-replica",
                "description": "Full-size replica of my war banner -- white linen, painted angels, fleur-de-lis, JHESUS MARIA. I carried this instead of a sword. I told the court: I loved my banner forty times more than my sword. The banner never killed anyone. It gave men something to follow.",
                "item_type": "physical",
                "category": "education",
                "listings": [{"listing_type": "rent", "price": 4.0, "price_unit": "per_day", "currency": "EUR", "deposit": 15.0}]
            },
            {
                "name": "Plate Armor Fitting & Movement Training",
                "slug": "plate-armor-fitting-movement",
                "description": "15th century plate armor training. Move, fight, mount a horse, get up from the ground in 50 pounds of steel. Tip: Armor does not make you slow. Bad armor makes you slow. Good armor moves with you.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "French Arming Sword (15th Century Replica)",
                "slug": "french-arming-sword-15th-century",
                "description": "Single-handed arming sword, cruciform hilt, 32-inch blade. Standard Hundred Years War knight's weapon. I rarely drew mine -- my banner was my weapon. But I trained daily. Balanced for one-handed use with shield or on horseback.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 6.0, "price_unit": "per_day", "currency": "EUR", "deposit": 25.0}]
            }
        ]
    },

    # ============================================================
    # 10. SALADIN (1137-1193) - Ayyubid sultan, Tikrit
    # ============================================================
    {
        "slug": "saladins-citadel",
        "display_name": "Saladin",
        "email": "saladin@borrowhood.local",
        "date_of_birth": "1137-01-01",
        "mother_name": "Unknown -- the chroniclers recorded only my father's line",
        "father_name": "Najm ad-Din Ayyub -- governor of Baalbek, Kurdish soldier who served Zengi",
        "workshop_name": "Saladin's Citadel",
        "workshop_type": "fortress",
        "tagline": "I warn you against shedding blood, indulging in it and making a habit of it, for blood never sleeps.",
        "bio": "Born in Tikrit, Kurdish blood, raised in Damascus. United Egypt and Syria, recaptured Jerusalem from the Crusaders at Hattin in 1187. Richard the Lionheart called me the greatest prince in the world. When Richard fell ill, I sent my physician and fruit packed in snow from Mount Hermon. When I took Jerusalem, there was no massacre -- unlike the Crusaders who waded through blood in 1099. Tip: Victory without honor is defeat. Treat prisoners well and enemies will surrender. Treat them badly and they fight to the death. Mercy is the most powerful weapon in the long war.",
        "telegram_username": "sultan_salah",
        "city": "Tikrit",
        "country_code": "IQ",
        "latitude": 34.600,
        "longitude": 43.679,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "ar", "proficiency": "native"},
            {"language_code": "ku", "proficiency": "native"},
            {"language_code": "fa", "proficiency": "C1"}
        ],
        "skills": [
            {"skill_name": "Cavalry Command", "category": "sports", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Siege Warfare", "category": "education", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Diplomacy", "category": "education", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Swordsmanship", "category": "sports", "self_rating": 5, "years_experience": 30}
        ],
        "social_links": [],
        "points": {"total_points": 2300, "rentals_completed": 62, "reviews_given": 50, "reviews_received": 72, "items_listed": 7, "helpful_flags": 55},
        "offers_training": True,
        "items": [
            {
                "name": "Saracen Cavalry Training -- Desert Horsemanship",
                "slug": "saracen-cavalry-desert-horsemanship",
                "description": "Arabian horse riding, hit-and-run tactics, desert warfare. At Hattin I cut the Crusaders off from water and let the sun finish the job. Tip: In the desert, water is strategy. Control the wells, control the battle.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 24.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Damascus Steel Scimitar (Museum-Grade Replica)",
                "slug": "damascus-steel-scimitar-replica",
                "description": "Curved scimitar forged in the Damascus tradition. The legendary steel held an edge that could split a silk scarf dropped on the blade. The curve follows the arc of a horseman's arm -- perfect for mounted slashing.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 8.0, "price_unit": "per_day", "currency": "EUR", "deposit": 40.0}]
            },
            {
                "name": "Chivalry & Diplomacy Seminar -- The Warrior's Honor",
                "slug": "chivalry-diplomacy-warriors-honor",
                "description": "How to wage war without losing your humanity. Prisoner treatment, negotiation under pressure, trust with enemies. I sent Richard ice when he had fever. He sent me horses. We tried to kill each other for three years and parted with respect. Tip: Your reputation arrives before your army.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 16.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Mamluk Chain Mail & Conical Helmet Set",
                "slug": "mamluk-chainmail-helmet-set",
                "description": "Riveted chain mail hauberk and conical helmet with nasal guard. Lighter than Crusader plate, better in the heat, flexible enough for mounted archery. My Mamluks wore gear like this at Hattin.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 10.0, "price_unit": "per_day", "currency": "EUR", "deposit": 45.0}]
            },
            {
                "name": "Desert Navigation & Survival -- Water, Sun, Sand",
                "slug": "desert-navigation-survival-course",
                "description": "Finding water in the desert. Reading sun and stars. Building shelter from heat. My army marched from Egypt to Palestine through the Sinai -- if you cannot survive the desert, you cannot fight in it.",
                "item_type": "service",
                "category": "outdoor",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # 11. RICHARD THE LIONHEART (1157-1199) - Crusader king
    # ============================================================
    {
        "slug": "richards-crusader-keep",
        "display_name": "Richard the Lionheart",
        "email": "richard@borrowhood.local",
        "date_of_birth": "1157-09-08",
        "mother_name": "Eleanor of Aquitaine -- the most powerful woman in medieval Europe",
        "father_name": "Henry II -- King of England, who I rebelled against twice",
        "workshop_name": "Richard's Crusader Keep",
        "workshop_type": "fortress",
        "tagline": "I am born of a rank which recognizes no superior but God.",
        "bio": "King of England, Duke of Normandy, Duke of Aquitaine, Count of Anjou. I spent six months in England during my ten-year reign. The rest I spent fighting -- the Third Crusade, the siege of Acre, the march to Jaffa. Saladin was the most honorable enemy I ever faced. At Arsuf, I held the Hospitallers back until the Saracen cavalry was fully committed, then unleashed the charge that broke their line. My mother Eleanor ran England while I was gone -- better than most kings. Tip: A castle is a weapon, not a hiding place. I designed Chateau Gaillard with concentric walls and flanking towers. Philip Augustus spent a year taking it. Build to fight from, not to cower in.",
        "telegram_username": "coeur_de_lion",
        "city": "Oxford",
        "country_code": "GB",
        "latitude": 51.752,
        "longitude": -1.258,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "fr", "proficiency": "native"},
            {"language_code": "en", "proficiency": "B2"},
            {"language_code": "la", "proficiency": "C1"}
        ],
        "skills": [
            {"skill_name": "Sword Combat", "category": "sports", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Siege Warfare", "category": "education", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Castle Design", "category": "education", "self_rating": 5, "years_experience": 15},
            {"skill_name": "Horseback Riding", "category": "sports", "self_rating": 5, "years_experience": 30}
        ],
        "social_links": [],
        "points": {"total_points": 2150, "rentals_completed": 58, "reviews_given": 42, "reviews_received": 68, "items_listed": 6, "helpful_flags": 44},
        "offers_training": True,
        "items": [
            {
                "name": "Crusader Longsword & Heater Shield Training",
                "slug": "crusader-longsword-heater-shield",
                "description": "Full-weight cruciform longsword and heater shield. The longsword is 40 inches of straight double-edged steel, designed for mounted and foot combat. The heater shield replaced the kite shield -- lighter, better for mounted lance work. I will teach you the cross-guard parry that saved my life at Jaffa.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Full Plate & Mail Crusader Armor Set",
                "slug": "full-plate-mail-crusader-armor",
                "description": "Chain mail hauberk over padded gambeson, with plate reinforcement at shoulders and knees. Great helm with cross visor. About 55 pounds total. I wore heavier at Arsuf in desert heat. If you can fight in this, you can fight in anything.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 14.0, "price_unit": "per_day", "currency": "EUR", "deposit": 60.0}]
            },
            {
                "name": "Castle Design & Fortification Workshop",
                "slug": "castle-design-fortification-workshop",
                "description": "Concentric walls, flanking towers, murder holes, killing grounds. I designed Chateau Gaillard in Normandy -- three baileys, each commanding the one below. Philip took it by climbing through the latrine chute. Tip: Design for the attack you cannot imagine, not the one you expect.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "English Longbow (Yew, 120lb Draw)",
                "slug": "english-longbow-yew-120lb",
                "description": "Six-foot yew longbow, 120-pound draw weight. The weapon that would later destroy French chivalry at Crecy and Agincourt. Even in my time, English and Welsh archers were devastating. I was killed by a crossbow bolt at Chalus -- never underestimate ranged weapons.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 7.0, "price_unit": "per_day", "currency": "EUR", "deposit": 35.0}]
            }
        ]
    },

    # ============================================================
    # 12. WILLIAM WALLACE (1270-1305) - Scottish freedom
    # ============================================================
    {
        "slug": "wallaces-highland-forge",
        "display_name": "William Wallace",
        "email": "wallace@borrowhood.local",
        "date_of_birth": "1270-01-01",
        "mother_name": "Margaret Crawford -- daughter of Sir Reginald Crawford, Sheriff of Ayr",
        "father_name": "Alan Wallace -- a minor Scottish knight from Elderslie",
        "workshop_name": "Wallace's Highland Forge",
        "workshop_type": "forge",
        "tagline": "Every man dies. Not every man really lives.",
        "bio": "Born a minor knight's son in Elderslie, Scotland. When Edward Longshanks tried to erase Scotland, I stood up. Killed the English Sheriff of Lanark, then raised an army of common men. At Stirling Bridge, we destroyed a professional English army by letting them cross half-way and then cutting them in two. Andrew Moray fought beside me and died of wounds after -- Scotland lost a great man that day. Edward captured me through betrayal, hanged me, drew me, and quartered me. My limbs were displayed in four cities as a warning. Tip: Fight where the enemy is weakest, not where he is strongest. At Stirling, the bridge was the weapon. The English defeated themselves by crowding onto it.",
        "telegram_username": "braveheart_true",
        "city": "Elderslie",
        "country_code": "GB",
        "latitude": 55.838,
        "longitude": -4.501,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "fr", "proficiency": "B2"},
            {"language_code": "la", "proficiency": "B1"}
        ],
        "skills": [
            {"skill_name": "Claymore Combat", "category": "sports", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Guerrilla Warfare", "category": "education", "self_rating": 5, "years_experience": 10},
            {"skill_name": "Highland Survival", "category": "outdoor", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Rebellion Leadership", "category": "education", "self_rating": 5, "years_experience": 10}
        ],
        "social_links": [],
        "points": {"total_points": 1850, "rentals_completed": 48, "reviews_given": 40, "reviews_received": 62, "items_listed": 5, "helpful_flags": 42},
        "offers_training": True,
        "items": [
            {
                "name": "Scottish Claymore (Two-Handed Greatsword)",
                "slug": "scottish-claymore-greatsword",
                "description": "66-inch two-handed claymore, the weapon of the Scottish Highlands. Designed for sweeping cuts that clear a path through armored men. My own claymore was reportedly taller than most men. The reach advantage against sword-and-shield is decisive if you have the strength.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 8.0, "price_unit": "per_day", "currency": "EUR", "deposit": 35.0}]
            },
            {
                "name": "Highland Guerrilla Tactics Workshop",
                "slug": "highland-guerrilla-tactics-workshop",
                "description": "Hit-and-run from the hills. Ambush techniques, using terrain to negate cavalry, scorched earth defense. How common men with farm tools beat professional knights. Tip: You do not need to win the war in one battle. You need to make the occupation too expensive to maintain.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 16.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Scottish Targe Shield & Dirk Set",
                "slug": "scottish-targe-shield-dirk",
                "description": "Round targe shield (20 inches, studded leather over wood) and 12-inch dirk dagger. The Highlander's backup weapons. The targe catches the blade, the dirk finishes the work. I will teach you the off-hand techniques that made Highland warriors feared in close quarters.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR", "deposit": 25.0}]
            },
            {
                "name": "Freedom & Resistance Seminar -- Leading the Impossible",
                "slug": "freedom-resistance-leading-impossible",
                "description": "When the cause is impossible, how do you lead? Recruitment, morale, operating without resources or official support. Case studies from Scotland, Ireland, the American colonies, and modern resistance movements. Tip: The cause outlives the man. I died badly. Scotland still became free.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 14.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # 13. MIYAMOTO MUSASHI (1584-1645) - Book of Five Rings
    # ============================================================
    {
        "slug": "musashis-dojo",
        "display_name": "Miyamoto Musashi",
        "email": "musashi@borrowhood.local",
        "date_of_birth": "1584-01-01",
        "mother_name": "Omasa -- died when I was young, leaving me to the sword",
        "father_name": "Shinmen Munisai -- a martial artist who taught me my first techniques",
        "workshop_name": "Musashi's Niten Dojo",
        "workshop_type": "dojo",
        "tagline": "Do not seek to follow in the footsteps of the wise. Seek what they sought.",
        "bio": "Born in Harima Province, Japan. Fought my first duel at thirteen and killed a man. By the time I wrote the Book of Five Rings, I had fought over sixty duels and never lost. I developed Niten Ichi-ryu -- the two-sword style, using katana and wakizashi together. At Ganryu Island, I defeated Sasaki Kojiro with a wooden sword I carved from a boat oar on the way to the duel. I arrived late on purpose. Kojiro threw his scabbard away in anger -- I told him he had already lost. Tip: The way of the warrior is the way of the pen and the sword. I painted, I sculpted, I wrote. A swordsman who knows only the sword knows nothing.",
        "telegram_username": "niten_ichi",
        "city": "Himeji",
        "country_code": "JP",
        "latitude": 34.837,
        "longitude": 134.694,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "ja", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Kenjutsu (Sword)", "category": "sports", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Two-Sword Style", "category": "sports", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Martial Philosophy", "category": "education", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Ink Painting", "category": "art", "self_rating": 4, "years_experience": 25}
        ],
        "social_links": [],
        "points": {"total_points": 2700, "rentals_completed": 75, "reviews_given": 45, "reviews_received": 88, "items_listed": 7, "helpful_flags": 58},
        "offers_training": True,
        "items": [
            {
                "name": "Katana & Wakizashi Training Set (Bokken -- Wooden)",
                "slug": "katana-wakizashi-bokken-set",
                "description": "Two wooden training swords -- full-length bokken (katana) and short bokken (wakizashi). I killed Sasaki Kojiro with wood. Steel is a privilege, not a right. Master the fundamentals with these before you touch a live blade. Tip: The sword is an extension of your center. Move from the hips, not the arms.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR", "deposit": 20.0}]
            },
            {
                "name": "Niten Ichi-ryu Workshop -- Two-Sword Fighting",
                "slug": "niten-ichiryu-two-sword-workshop",
                "description": "My school: long sword in one hand, short sword in the other. Most swordsmen use two hands on one blade. I use one hand on each. The long sword attacks, the short sword defends and creates openings. It requires years. We start today. Tip: Do not grip the sword tightly. Hold it like a bird -- firm enough it cannot escape, gentle enough you do not crush it.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Book of Five Rings Study Group -- Strategy & Philosophy",
                "slug": "book-of-five-rings-study-group",
                "description": "Earth, Water, Fire, Wind, Void. Five books, each covering a different aspect of combat and life. We read, discuss, and practice. The Earth book is foundation. Water is adaptability. Fire is initiative. Wind is understanding others. Void is the state beyond technique. Most people never reach Void.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 16.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Live Blade Katana (Shinken -- Advanced Students Only)",
                "slug": "live-blade-katana-shinken",
                "description": "Folded steel katana, razor edge, 28-inch blade. For advanced students who have completed bokken training. I lend this only after watching you train. If you grip too tight, swing too wild, or show fear of the blade, it stays in my rack. A sharp sword in unskilled hands is a danger to its owner.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 15.0, "price_unit": "per_day", "currency": "EUR", "deposit": 80.0}]
            },
            {
                "name": "Meditation & Ink Painting Session -- The Way Beyond the Sword",
                "slug": "meditation-ink-painting-session",
                "description": "I painted birds, landscapes, and Bodhidharma with the same focus I used to kill men. The brush and the sword follow the same path -- presence, economy, commitment. One stroke, no correction. This session combines zazen meditation with sumi-e ink painting.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 14.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # 14. SHAKA ZULU (1787-1828) - Zulu Kingdom
    # ============================================================
    {
        "slug": "shakas-kraal",
        "display_name": "Shaka Zulu",
        "email": "shaka@borrowhood.local",
        "date_of_birth": "1787-07-01",
        "mother_name": "Nandi -- the woman they called 'the wasp', exiled with me but never broken",
        "father_name": "Senzangakhona kaJama -- chief of the Zulu who disowned me before birth",
        "workshop_name": "Shaka's Kraal",
        "workshop_type": "camp",
        "tagline": "Strike an enemy once and for all. Let him cease to exist as a tribe or he will live to fly at your throat again.",
        "bio": "Born illegitimate, exiled as a child with my mother Nandi. We survived on the charity of other clans. I grew into the greatest military innovator Africa has ever produced. I took a small Zulu clan and built it into an empire of 250,000 warriors. I replaced the long throwing assegai with the iklwa -- a short stabbing spear for close combat. I invented the bull horn formation: chest engages, horns encircle. Dingiswayo mentored me, Mzilikazi was my lieutenant before he broke away. Tip: The weapon does not matter. The willingness to close the distance matters. Everyone can throw a spear from far away. The warrior is the one who gets close enough to smell his enemy's fear. My own brothers assassinated me in 1828. Even kings die at home.",
        "telegram_username": "zulu_thunder",
        "city": "Eshowe",
        "country_code": "ZA",
        "latitude": -28.892,
        "longitude": 31.462,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "zu", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Close Combat", "category": "sports", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Military Innovation", "category": "education", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Formation Tactics", "category": "education", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Physical Conditioning", "category": "sports", "self_rating": 5, "years_experience": 30}
        ],
        "social_links": [],
        "points": {"total_points": 2050, "rentals_completed": 52, "reviews_given": 38, "reviews_received": 64, "items_listed": 6, "helpful_flags": 40},
        "offers_training": True,
        "items": [
            {
                "name": "Iklwa Stabbing Spear & Isihlangu Shield Set",
                "slug": "iklwa-spear-isihlangu-shield",
                "description": "The iklwa -- named for the sucking sound it makes when pulled from a body. Short-hafted, broad-bladed, designed for close combat behind the cowhide isihlangu shield. The shield hooks the enemy's shield aside, the iklwa goes in underneath. I changed warfare in Africa with this weapon.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 6.0, "price_unit": "per_day", "currency": "EUR", "deposit": 25.0}]
            },
            {
                "name": "Impi Formation Drill -- Bull Horn Tactics",
                "slug": "impi-formation-bull-horn-tactics",
                "description": "Group training (12-20 people). The bull horn formation: the chest pins the enemy, the left and right horns encircle. The loins wait in reserve facing away so they do not grow anxious. Commands by runner. We drill barefoot -- I threw away my warriors' sandals. Tip: A warrior who cannot run 50 miles cannot fight.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 14.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Zulu Warrior Fitness -- Barefoot Conditioning",
                "slug": "zulu-warrior-fitness-barefoot",
                "description": "Barefoot running, shield drills, stick fighting, distance marches. My impis covered 50 miles in a day on bare feet and arrived ready to fight. Modern shoes made your feet weak. This program fixes that. Tip: Pain is information. Listen to it, then decide what to do with it.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 12.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Military Innovation Seminar -- Rethinking Your Weapons",
                "slug": "military-innovation-rethinking-weapons",
                "description": "How to look at an existing weapon, tactic, or system and make it fundamentally better. I took a throwing spear and made it a stabbing spear. I took sandals off warriors and made them faster. Innovation is not invention -- it is seeing what everyone sees and thinking what no one thinks.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # 15. SITTING BULL (1831-1890) - Lakota leader
    # ============================================================
    {
        "slug": "sitting-bulls-lodge",
        "display_name": "Sitting Bull",
        "email": "sittingbull@borrowhood.local",
        "date_of_birth": "1831-01-01",
        "mother_name": "Her-Holy-Door -- a woman of the Hunkpapa Lakota",
        "father_name": "Returns Again -- a Hunkpapa chief who saw the buffalo path in his son",
        "workshop_name": "Sitting Bull's Sacred Lodge",
        "workshop_type": "lodge",
        "tagline": "Let us put our minds together and see what life we can make for our children.",
        "bio": "Born Jumping Badger near the Grand River in Lakota territory. I earned the name Sitting Bull through courage in battle. Holy man, war chief, and the leader who united the Lakota, Cheyenne, and Arapaho at the Little Bighorn. I did not fight that day -- I had performed the Sun Dance and received the vision of soldiers falling into our camp upside down. Crazy Horse led the charge that destroyed Custer's command. Tip: A leader's greatest weapon is unity. Separately, each tribe could be defeated. Together, we were invincible. I fled to Canada with my people rather than surrender our way of life. When I returned, they put me in a traveling show with Buffalo Bill. They shot me at Standing Rock in 1890 to prevent another Ghost Dance uprising.",
        "telegram_username": "tatanka_iyotake",
        "city": "Mobridge",
        "country_code": "US",
        "latitude": 45.537,
        "longitude": -100.428,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "B2"}
        ],
        "skills": [
            {"skill_name": "Horseback Riding", "category": "sports", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Archery", "category": "sports", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Spiritual Leadership", "category": "education", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Plains Survival", "category": "outdoor", "self_rating": 5, "years_experience": 50}
        ],
        "social_links": [],
        "points": {"total_points": 1950, "rentals_completed": 50, "reviews_given": 45, "reviews_received": 60, "items_listed": 5, "helpful_flags": 48},
        "offers_training": True,
        "items": [
            {
                "name": "Plains Horseback Riding -- Bareback & War Pony",
                "slug": "plains-horseback-bareback-war-pony",
                "description": "Bareback riding on the open plains. No saddle, no stirrups -- just you and the horse. The Lakota were among the finest horsemen on Earth. Knee signals, voice commands, shooting from horseback. Tip: The horse must trust you before it will carry you into danger. Earn the trust first.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Lakota Bow & Arrow Set (Sinew-Backed, 20 Arrows)",
                "slug": "lakota-bow-arrow-sinew-backed",
                "description": "Short sinew-backed bow, 45-pound draw, optimized for mounted use. Twenty dogwood arrows with iron and flint points. This is what we hunted buffalo with from horseback at full gallop -- one arrow could pass through a buffalo at close range.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 7.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0}]
            },
            {
                "name": "Plains Survival & Tracking Workshop",
                "slug": "plains-survival-tracking-workshop",
                "description": "Reading tracks, finding water on the open plains, building shelter from materials at hand, fire making. My people lived on these plains for thousands of years without a single building. The land provides everything if you know how to ask. Tip: Listen more than you look. The wind carries information.",
                "item_type": "service",
                "category": "outdoor",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "War Bonnet & Ceremonial Shield (Display Replicas)",
                "slug": "war-bonnet-ceremonial-shield-display",
                "description": "Eagle feather war bonnet and painted buffalo hide shield. Each feather represents an act of bravery. These are display replicas for education and ceremony -- the originals were sacred. Handle with respect or do not handle them at all.",
                "item_type": "physical",
                "category": "education",
                "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0}]
            }
        ]
    },

    # ============================================================
    # 16. GERONIMO (1829-1909) - Apache leader
    # ============================================================
    {
        "slug": "geronimos-canyon-camp",
        "display_name": "Geronimo",
        "email": "geronimo@borrowhood.local",
        "date_of_birth": "1829-06-16",
        "mother_name": "Juana -- a Bedonkohe Apache woman who taught me the old ways",
        "father_name": "Taklishim (The Gray One) -- a Bedonkohe Apache chief",
        "workshop_name": "Geronimo's Canyon Camp",
        "workshop_type": "camp",
        "tagline": "I was born on the prairies where the wind blew free and there was nothing to break the light of the sun.",
        "bio": "Born Goyahkla in No-Doyohn Canyon, Apache territory. Mexican soldiers killed my mother, my wife Alope, and my three children in a raid on our camp in 1851. I fought for thirty years after that. The Mexicans gave me the name Geronimo because they cried out to Saint Jerome when I charged them. With never more than 38 warriors, I evaded 5,000 American troops and 3,000 Mexican soldiers for years in the Sierra Madre. Naiche, son of Cochise, rode with me. Tip: Know your terrain better than your enemy knows his maps. Every canyon, every water source, every hidden trail. The land is your greatest ally. I surrendered in 1886 -- the last hostile Native American leader. They never let me go home.",
        "telegram_username": "goyahkla",
        "city": "Willcox",
        "country_code": "US",
        "latitude": 32.253,
        "longitude": -109.832,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "B1"}
        ],
        "skills": [
            {"skill_name": "Desert Survival", "category": "outdoor", "self_rating": 5, "years_experience": 60},
            {"skill_name": "Guerrilla Warfare", "category": "education", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Tracking", "category": "outdoor", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Horseback Riding", "category": "sports", "self_rating": 5, "years_experience": 55}
        ],
        "social_links": [],
        "points": {"total_points": 1800, "rentals_completed": 46, "reviews_given": 30, "reviews_received": 55, "items_listed": 5, "helpful_flags": 35},
        "offers_training": True,
        "items": [
            {
                "name": "Desert Guerrilla Tactics Workshop",
                "slug": "desert-guerrilla-tactics-workshop",
                "description": "How 38 warriors evaded 8,000 soldiers for years. Water caching, trail deception, ambush sites, disappearing into terrain. The Apache did not fight battles -- we fought a war of movement. Tip: Never be where they expect you. Move at night, rest by day, leave false trails. Make them chase ghosts.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Apache Bow & War Club Set",
                "slug": "apache-bow-war-club-set",
                "description": "Short mulberry bow and stone-headed war club. The Apache bow is compact -- made for horseback and tight canyon fights. The war club is last resort, close quarters. Light enough to carry all day, deadly enough to end any argument.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR", "deposit": 20.0}]
            },
            {
                "name": "Advanced Tracking & Counter-Tracking",
                "slug": "advanced-tracking-counter-tracking",
                "description": "Reading sign on rock, sand, and hardpan. Aging tracks by moisture and wind. Counter-tracking -- how to move without leaving sign. I could track a man across bare rock by the scuff marks and disturbed pebbles. Tip: Everything that moves leaves evidence. Your job is to see what others walk past.",
                "item_type": "service",
                "category": "outdoor",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Desert Survival Intensive -- 48 Hours With Nothing",
                "slug": "desert-survival-intensive-48hr",
                "description": "Two days in the desert with a knife and the clothes on your back. Finding water from plants, catching small game, building shade shelters, navigating by stars and landmarks. The Chiricahua Apache lived in this desert for centuries. If you listen to the land, it will keep you alive.",
                "item_type": "service",
                "category": "outdoor",
                "listings": [{"listing_type": "training", "price": 30.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # 17. ATTILA THE HUN (406-453) - Scourge of God
    # ============================================================
    {
        "slug": "attilas-war-tent",
        "display_name": "Attila the Hun",
        "email": "attila@borrowhood.local",
        "date_of_birth": "0406-01-01",
        "mother_name": "Unknown -- the Huns kept no written records of their women",
        "father_name": "Mundzuk -- a Hunnic chieftain, brother of kings Octar and Ruga",
        "workshop_name": "Attila's War Tent",
        "workshop_type": "camp",
        "tagline": "There, where I have passed, the grass will never grow again.",
        "bio": "Born into Hunnic royalty in the plains of Pannonia. Shared the throne with my brother Bleda until I no longer wished to share. The Romans called me Flagellum Dei -- the Scourge of God. I held the Western and Eastern Roman Empires to ransom simultaneously. At the Catalaunian Plains, Aetius and the Visigoths stopped my advance into Gaul -- the only real defeat of my career. Honoria, sister of the Western Emperor, sent me her ring and asked me to rescue her from an arranged marriage. I used it as a claim to half the empire. Tip: Fear is cheaper than battle. I sent ambassadors ahead of my army to describe what we would do. Most cities opened their gates. The ones that did not became the examples for the next city. I died on my wedding night -- a nosebleed drowned me in my own blood while I slept drunk.",
        "telegram_username": "scourge_of_god",
        "city": "Budapest",
        "country_code": "HU",
        "latitude": 47.497,
        "longitude": 19.040,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "hu", "proficiency": "native"},
            {"language_code": "la", "proficiency": "B2"},
            {"language_code": "el", "proficiency": "B1"}
        ],
        "skills": [
            {"skill_name": "Mounted Archery", "category": "sports", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Psychological Warfare", "category": "education", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Empire Administration", "category": "education", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Horseback Riding", "category": "sports", "self_rating": 5, "years_experience": 40}
        ],
        "social_links": [],
        "points": {"total_points": 2250, "rentals_completed": 60, "reviews_given": 25, "reviews_received": 70, "items_listed": 6, "helpful_flags": 35},
        "offers_training": True,
        "items": [
            {
                "name": "Hunnic Horse Archery -- Ride & Shoot",
                "slug": "hunnic-horse-archery-ride-shoot",
                "description": "The Huns were born in the saddle. Composite bow from horseback, forward and backward shooting, feigned retreat with volley fire. Tip: The feigned retreat is the deadliest tactic in cavalry warfare. Pretend to flee, let them chase in disorder, then turn and destroy them. It requires discipline to run and courage to turn.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 26.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Hunnic Composite Bow & Bone-Tipped Arrows",
                "slug": "hunnic-composite-bow-bone-arrows",
                "description": "Asymmetric Hunnic composite recurve bow with bone siyahs (ear reinforcements). Smaller than the Mongol bow, faster to draw, devastating at close range from horseback. Includes 20 bone-tipped arrows. The bone tip splinters inside the wound -- a cruelty, but effective.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 9.0, "price_unit": "per_day", "currency": "EUR", "deposit": 40.0}]
            },
            {
                "name": "Psychological Warfare Masterclass -- Break Them Before Battle",
                "slug": "psychological-warfare-masterclass",
                "description": "How to defeat an enemy before the first arrow flies. Reputation management, terror as strategy, negotiation from strength, making examples. Case studies: my campaigns against Rome, Sherman's March, modern information warfare. Tip: The cheapest victory is the one where the enemy surrenders without a fight.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Hunnic Lasso & Cavalry Lance Set",
                "slug": "hunnic-lasso-cavalry-lance",
                "description": "Braided leather lasso and 10-foot cavalry lance. The Huns used the lasso to pull riders from horses and drag infantry from shield walls. The lance was for the charge. I will teach you mounted lasso throwing -- harder than it looks, devastating when it works.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 6.0, "price_unit": "per_day", "currency": "EUR", "deposit": 25.0}]
            }
        ]
    },

    # ============================================================
    # 18. VERCINGETORIX (82-46 BC) - Gallic chieftain
    # ============================================================
    {
        "slug": "vercingetorix-gallic-stronghold",
        "display_name": "Vercingetorix",
        "email": "vercingetorix@borrowhood.local",
        "date_of_birth": "0082-01-01",
        "mother_name": "Unknown -- Arverni nobility, but Rome recorded only her son's defiance",
        "father_name": "Celtillus -- an Arverni nobleman executed by his own people for seeking the kingship",
        "workshop_name": "Vercingetorix's Gallic Stronghold",
        "workshop_type": "fortress",
        "tagline": "I did not take up arms for private reasons, but for our common freedom.",
        "bio": "Born in Auvergne, son of a murdered chieftain. I united the fractious Gallic tribes against Caesar -- the only man who ever made Rome fear Gaul again. At Gergovia, I defeated Caesar's legions in open battle -- one of his only defeats. I pioneered scorched earth against Rome, burning Gallic towns to deny Caesar supplies. At Alesia, Caesar besieged me and I held. But my relief army failed. I surrendered to spare my warriors. I rode out on my finest horse, threw my weapons at Caesar's feet, and sat in silence. Caesar kept me in chains for six years, paraded me through Rome, then strangled me in a dungeon. Tip: Scorched earth is the hardest decision a leader makes. I burned my own people's homes to starve the enemy. It works, but the people you saved will hate you for the homes you burned.",
        "telegram_username": "arverni_king",
        "city": "Clermont-Ferrand",
        "country_code": "FR",
        "latitude": 45.777,
        "longitude": 3.087,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "fr", "proficiency": "native"},
            {"language_code": "la", "proficiency": "B2"}
        ],
        "skills": [
            {"skill_name": "Coalition Warfare", "category": "education", "self_rating": 5, "years_experience": 8},
            {"skill_name": "Scorched Earth Tactics", "category": "education", "self_rating": 5, "years_experience": 5},
            {"skill_name": "Cavalry Combat", "category": "sports", "self_rating": 5, "years_experience": 15},
            {"skill_name": "Siege Defense", "category": "education", "self_rating": 5, "years_experience": 5}
        ],
        "social_links": [],
        "points": {"total_points": 1750, "rentals_completed": 44, "reviews_given": 35, "reviews_received": 56, "items_listed": 5, "helpful_flags": 38},
        "offers_training": True,
        "items": [
            {
                "name": "Gallic Cavalry Charge Training",
                "slug": "gallic-cavalry-charge-training",
                "description": "The Gallic cavalry was the finest in pre-Roman Europe. Charge tactics, wheeling formations, pursuit and withdrawal. I will teach you to control a warhorse at full gallop in formation. Tip: The charge is not about speed. It is about mass, timing, and the nerve to hold formation until impact.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Gallic Longsword & Chainmail (La Tene Style)",
                "slug": "gallic-longsword-chainmail-la-tene",
                "description": "La Tene style longsword (30-inch blade) and early chain mail shirt. The Gauls invented chain mail -- Rome copied it from us. The sword is designed for slashing from horseback. Longer than the Roman gladius, but less effective in tight formation. Choose your weapon for your fight.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 8.0, "price_unit": "per_day", "currency": "EUR", "deposit": 35.0}]
            },
            {
                "name": "Scorched Earth Strategy Seminar -- Denial Operations",
                "slug": "scorched-earth-strategy-seminar",
                "description": "When to burn your own land to starve the enemy. The hardest strategic decision. Case studies: my campaign against Caesar, Russia against Napoleon, Russia against Hitler. Tip: Scorched earth works when your enemy's supply line is longer than yours. It fails when your people lose faith before the enemy loses food.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 16.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Gallic Carnyx War Horn (Replica)",
                "slug": "gallic-carnyx-war-horn-replica",
                "description": "Bronze carnyx -- the tall war horn with the animal head that towered above our battle lines. The sound carried for miles and terrified Roman horses. A psychological weapon and a signal instrument. I will teach you to play it. Your neighbors will hate you.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR", "deposit": 25.0}]
            }
        ]
    },

    # ============================================================
    # 19. RAGNAR LOTHBROK (~795-865) - Viking legend
    # ============================================================
    {
        "slug": "ragnars-longship",
        "display_name": "Ragnar Lothbrok",
        "email": "ragnar@borrowhood.local",
        "date_of_birth": "0795-01-01",
        "mother_name": "Unknown -- the sagas name my wives, not my mother",
        "father_name": "Sigurd Ring -- a legendary Swedish king, if you believe the sagas",
        "workshop_name": "Ragnar's Longship",
        "workshop_type": "dock",
        "tagline": "How the little piggies will grunt when they hear how the old boar suffered.",
        "bio": "Born in Scandinavia, if I existed at all -- the sagas disagree on everything except my fame. I raided Paris in 845, sailing 120 longships up the Seine while King Charles trembled behind his walls. He paid me 7,000 pounds of silver to leave. I came back. My sons -- Ivar the Boneless, Bjorn Ironside, Sigurd Snake-in-the-Eye, and Ubba -- became greater raiders than I ever was. Lagertha was my first wife, a shieldmaiden who fought beside me. King Aella of Northumbria threw me into a pit of vipers. My sons invaded England to avenge me and carved the Danelaw from Saxon land. Tip: Strike where they are weak, withdraw before they are strong, return when they have relaxed. The longship is the weapon -- it goes where armies cannot.",
        "telegram_username": "lothbrok_raider",
        "city": "Stockholm",
        "country_code": "SE",
        "latitude": 59.329,
        "longitude": 18.069,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "sv", "proficiency": "native"},
            {"language_code": "en", "proficiency": "B1"}
        ],
        "skills": [
            {"skill_name": "Viking Combat", "category": "sports", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Naval Warfare", "category": "education", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Seamanship", "category": "outdoor", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Axe Combat", "category": "sports", "self_rating": 5, "years_experience": 30}
        ],
        "social_links": [],
        "points": {"total_points": 2100, "rentals_completed": 56, "reviews_given": 32, "reviews_received": 66, "items_listed": 6, "helpful_flags": 42},
        "offers_training": True,
        "items": [
            {
                "name": "Viking Axe & Round Shield Training",
                "slug": "viking-axe-round-shield-training",
                "description": "Bearded axe and lime-wood round shield. The axe hooks shields aside, the rim of your own shield is a weapon. Viking combat is aggressive, mobile, and brutal. Tip: The axe does not need a sharp edge to break bones. Weight and leverage do the work. Fight with the shield, kill with the axe.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Dane Axe (Two-Handed, 5-Foot Haft)",
                "slug": "dane-axe-two-handed",
                "description": "The great Dane axe -- a 5-foot hafted weapon that could split a man from shoulder to hip. No shield when you carry this. Your reach is your defense. The Varangian Guard used these in Constantinople. Weighted training replica, hickory haft.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 7.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0}]
            },
            {
                "name": "Viking Navigation Workshop -- Stars, Sunstones & Currents",
                "slug": "viking-navigation-stars-sunstones",
                "description": "How the Norse navigated the open Atlantic without compass or sextant. Sunstones (calcite crystals) to find the sun on cloudy days, star patterns, wave reading, bird sighting. I sailed from Scandinavia to Paris to the Mediterranean. Tip: The sea has patterns. Learn them and the ocean is a road, not a barrier.",
                "item_type": "service",
                "category": "outdoor",
                "listings": [{"listing_type": "training", "price": 16.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Viking Shield Wall Drill -- Group Combat",
                "slug": "viking-shield-wall-drill-group",
                "description": "Group training (8-16). The Viking shield wall: overlapping shields, spears over the top, axes hooking from the sides. When the wall holds, nothing breaks through. When it breaks, everyone dies. Tip: The man who steps back first kills the man beside him. Hold the wall.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 14.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Viking Seax Knife & Leather Tool Roll",
                "slug": "viking-seax-knife-leather-tool-roll",
                "description": "Large seax knife (12-inch single-edge blade) and leather roll with fire steel, whetstone, and bone needles. The seax was tool, weapon, and eating knife in one. Every Norseman carried one. Mine has a pattern-welded blade -- the maker's signature in the steel.",
                "item_type": "physical",
                "category": "outdoor",
                "listings": [{"listing_type": "rent", "price": 4.0, "price_unit": "per_day", "currency": "EUR", "deposit": 20.0}]
            }
        ]
    },

    # ============================================================
    # 20. EL CID (1043-1099) - Spanish warrior
    # ============================================================
    {
        "slug": "el-cids-castle",
        "display_name": "El Cid",
        "email": "elcid@borrowhood.local",
        "date_of_birth": "1043-01-01",
        "mother_name": "Unknown -- minor Castilian nobility",
        "father_name": "Diego Lainez -- a knight in the court of Ferdinand I of Castile",
        "workshop_name": "El Cid's Castle",
        "workshop_type": "fortress",
        "tagline": "God, what a fine vassal -- if only he had a worthy lord.",
        "bio": "Born Rodrigo Diaz de Vivar near Burgos. They called me El Cid -- from the Arabic al-sayyid, the lord. I served Castile, was exiled by King Alfonso, then conquered Valencia on my own with a private army of Christians and Muslims alike. I never lost a battle. My wife Jimena held Valencia after my death -- they strapped my corpse to Babieca my warhorse and rode me out the gates to terrify the besieging Almoravids. It worked. Tip: Loyalty to a cause outlasts loyalty to a king. Alfonso exiled me twice. I served Castile anyway. My army included Moors and Christians because I judged men by their sword arm, not their prayers.",
        "telegram_username": "el_campeador",
        "city": "Burgos",
        "country_code": "ES",
        "latitude": 42.344,
        "longitude": -3.697,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "es", "proficiency": "native"},
            {"language_code": "ar", "proficiency": "B2"},
            {"language_code": "la", "proficiency": "C1"}
        ],
        "skills": [
            {"skill_name": "Sword Combat", "category": "sports", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Cavalry Tactics", "category": "sports", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Siege Warfare", "category": "education", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Mercenary Command", "category": "education", "self_rating": 5, "years_experience": 20}
        ],
        "social_links": [],
        "points": {"total_points": 2050, "rentals_completed": 54, "reviews_given": 40, "reviews_received": 66, "items_listed": 5, "helpful_flags": 43},
        "offers_training": True,
        "items": [
            {
                "name": "Tizona & Colada (Replica Swords of El Cid)",
                "slug": "tizona-colada-replica-swords",
                "description": "Replicas of my two legendary swords. Tizona -- the firebrand, taken from King Bucar of Morocco. Colada -- won in single combat. Both are straight double-edged blades, 36 inches, designed for mounted and foot combat. A knight carries two swords because battles are long and edges dull.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 10.0, "price_unit": "per_day", "currency": "EUR", "deposit": 45.0}]
            },
            {
                "name": "Reconquista Cavalry Training -- Lance & Sword",
                "slug": "reconquista-cavalry-lance-sword",
                "description": "Mounted combat in the Iberian style. Lance charge, transition to sword, fighting in mixed Christian-Muslim forces. The Reconquista lasted 700 years -- we learned from the Moors as much as we fought them. Tip: Your enemy is also your teacher. Study what defeats you.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 24.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Mercenary Leadership Workshop -- Building a Free Company",
                "slug": "mercenary-leadership-free-company",
                "description": "How to build, supply, and command a private army. Recruitment, pay structure, loyalty management, negotiating with patrons. I conquered Valencia with a freelance army because no king would give me one. Tip: Pay your men on time, every time. A soldier who trusts your purse will trust your orders.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Spanish Jinete Light Cavalry Kit",
                "slug": "spanish-jinete-light-cavalry-kit",
                "description": "Jinete riding gear: light leather armor, round adarga shield, short javelin set, and Moorish-style light saddle. The jinete style -- adopted from the Moors -- used speed and javelins instead of heavy charge. Perfect for skirmishing and pursuit.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 9.0, "price_unit": "per_day", "currency": "EUR", "deposit": 40.0}]
            }
        ]
    },

    # ============================================================
    # 21. TOMOE GOZEN (1157-1247) - Female samurai
    # ============================================================
    {
        "slug": "tomoes-war-pavilion",
        "display_name": "Tomoe Gozen",
        "email": "tomoe@borrowhood.local",
        "date_of_birth": "1157-01-01",
        "mother_name": "Unknown -- the chronicles recorded my valor, not my lineage",
        "father_name": "Nakahara Kaneto -- a samurai of Shinano Province",
        "workshop_name": "Tomoe's War Pavilion",
        "workshop_type": "dojo",
        "tagline": "A warrior worth a thousand, ready to confront a demon or a god, mounted or on foot.",
        "bio": "Born in Shinano Province, Japan. The Tale of the Heike describes me as remarkably beautiful with white skin and long hair -- and a warrior worth a thousand men. I served Minamoto no Yoshinaka during the Genpei War, riding beside him as captain of his vanguard. At the Battle of Awazu in 1184, when Yoshinaka's forces were reduced to five riders, I was still fighting. I charged into the enemy, dragged the strongest warrior from his horse, pinned him against my saddle, and took his head. Yoshinaka ordered me to flee so his name would not be shamed by dying beside a woman. I rode away with the severed head as my trophy. Tip: They will try to define you by what you are instead of what you do. Let your actions answer. I took heads on the battlefield. That is my definition.",
        "telegram_username": "tomoe_warrior",
        "city": "Nagano",
        "country_code": "JP",
        "latitude": 36.232,
        "longitude": 138.181,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "ja", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Mounted Combat", "category": "sports", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Archery (Yumi)", "category": "sports", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Naginata", "category": "sports", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Horseback Riding", "category": "sports", "self_rating": 5, "years_experience": 35}
        ],
        "social_links": [],
        "points": {"total_points": 2000, "rentals_completed": 52, "reviews_given": 44, "reviews_received": 64, "items_listed": 5, "helpful_flags": 46},
        "offers_training": True,
        "items": [
            {
                "name": "Naginata Training -- The Warrior Woman's Weapon",
                "slug": "naginata-training-warrior-woman",
                "description": "The naginata -- a curved blade on a long pole, the traditional weapon of the onna-bugeisha (female warrior). Sweeping cuts, thrusts, and the devastating ankle strikes that unhorse mounted samurai. I will teach you the kata and free sparring. Tip: Reach defeats strength. Keep them at naginata distance and they cannot touch you with a sword.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Yumi Longbow (Japanese, Asymmetric, 7-foot)",
                "slug": "yumi-longbow-japanese-asymmetric",
                "description": "Traditional Japanese yumi, 7 feet tall, bamboo and wood laminate. The asymmetric grip (held at the lower third) allows shooting from horseback. My mounted archery was accurate at 100 yards at full gallop. The yumi requires years to master -- start with standing shots.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 8.0, "price_unit": "per_day", "currency": "EUR", "deposit": 35.0}]
            },
            {
                "name": "Samurai Mounted Archery (Yabusame) Training",
                "slug": "samurai-mounted-archery-yabusame",
                "description": "Yabusame: mounted archery at gallop, hitting targets on a narrow lane. Sacred Shinto practice and deadly combat skill. Draw, release, recover -- all while controlling the horse with your knees. I will start you at a walk. The gallop comes when the horse says you are ready.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 28.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "O-Yoroi Samurai Armor Set (Display & Training)",
                "slug": "o-yoroi-samurai-armor-set",
                "description": "Full o-yoroi great armor -- lamellar plates, silk lacing, iron kabuto helmet with menpo face guard. Designed for mounted archery. The wide shoulder guards deflect arrows from above. Heavy but magnificent. I wore armor like this when I took heads at Awazu.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 14.0, "price_unit": "per_day", "currency": "EUR", "deposit": 70.0}]
            }
        ]
    },

    # ============================================================
    # 22. KHALID IBN AL-WALID (585-642) - Sword of Allah
    # ============================================================
    {
        "slug": "khalids-command-tent",
        "display_name": "Khalid ibn al-Walid",
        "email": "khalid@borrowhood.local",
        "date_of_birth": "0585-01-01",
        "mother_name": "Lubaba bint al-Harith -- of the Banu Hilal",
        "father_name": "al-Walid ibn al-Mughira -- chief of the Banu Makhzum clan of the Quraysh",
        "workshop_name": "Khalid's Command Tent",
        "workshop_type": "camp",
        "tagline": "I have fought in so many battles that there is no spot on my body that does not have a scar from a sword or arrow.",
        "bio": "Born in Mecca to the Quraysh tribe. I fought against the Prophet Muhammad at Uhud -- my cavalry charge nearly won the battle for the Meccans. Then I converted to Islam and became the Sword of Allah. I never lost a battle in over 100 engagements against the Byzantines, Persians, and rebel Arab tribes. At Yarmouk, I destroyed the Byzantine army with 40,000 men against their 100,000. I crossed the Syrian Desert in 6 days with my entire army -- a march the Romans said was impossible. Abu Bakr and Umar trusted me with everything. Tip: Initiative is the most valuable resource in war. While the enemy deliberates, act. While they deploy, strike. The commander who moves first controls the tempo. I died in my bed, covered in scars, and I wept that no battle had taken me.",
        "telegram_username": "sword_of_allah",
        "city": "Mecca",
        "country_code": "SA",
        "latitude": 21.389,
        "longitude": 39.858,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "ar", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Cavalry Command", "category": "sports", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Desert Warfare", "category": "education", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Rapid Maneuver", "category": "education", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Sword Combat", "category": "sports", "self_rating": 5, "years_experience": 40}
        ],
        "social_links": [],
        "points": {"total_points": 2450, "rentals_completed": 68, "reviews_given": 42, "reviews_received": 82, "items_listed": 6, "helpful_flags": 52},
        "offers_training": True,
        "items": [
            {
                "name": "Arabian Cavalry Tactics -- Speed & Initiative",
                "slug": "arabian-cavalry-speed-initiative",
                "description": "Light cavalry on Arabian horses -- the fastest, most enduring mounts in the world. Flanking attacks, pursuit, feigned retreat, desert crossing at forced march. At Yarmouk, my cavalry reserves struck the Byzantine flank at the decisive moment. Tip: Reserves are not idle men. They are the hammer you hold behind your back.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 26.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Arabian Saif Sword (Curved, Early Islamic Period)",
                "slug": "arabian-saif-sword-early-islamic",
                "description": "Early Islamic saif -- gently curved, 34-inch blade, ideal for mounted combat. Lighter than the European longsword, faster in the draw. I broke nine swords at Uhud in a single battle. A warrior needs a blade that matches his speed.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 7.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0}]
            },
            {
                "name": "Desert Crossing & Forced March Workshop",
                "slug": "desert-crossing-forced-march",
                "description": "I crossed the Syrian Desert in 6 days -- 500 miles through waterless waste with an army. Water caching, camel logistics, march discipline, heat management. The Byzantines thought the desert protected their flank. They were wrong. Tip: The impossible route is undefended because the enemy thinks no one can take it.",
                "item_type": "service",
                "category": "outdoor",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Early Islamic Lamellar Armor & Round Shield",
                "slug": "early-islamic-lamellar-armor-shield",
                "description": "Iron lamellar armor with leather backing, and a round steel shield. Lighter than Byzantine cataphract armor but sufficient against arrows and sword cuts. Designed for speed, not siege. My men could ride all day in this and fight at the end of it.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 9.0, "price_unit": "per_day", "currency": "EUR", "deposit": 40.0}]
            },
            {
                "name": "Battle Tempo Masterclass -- Controlling the Fight",
                "slug": "battle-tempo-masterclass-controlling-fight",
                "description": "How to dictate the pace of a battle. When to attack, when to feint, when to commit reserves. In over 100 battles, I never let the enemy choose the moment of decision. Tip: The commander who controls the tempo controls the outcome. Make them react to you, never the reverse.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # 23. TECUMSEH (1768-1813) - Shawnee leader
    # ============================================================
    {
        "slug": "tecumsehs-council-fire",
        "display_name": "Tecumseh",
        "email": "tecumseh@borrowhood.local",
        "date_of_birth": "1768-03-01",
        "mother_name": "Methoataske -- a Creek woman who raised warriors",
        "father_name": "Puckeshinwau -- a Shawnee war chief killed at Point Pleasant",
        "workshop_name": "Tecumseh's Council Fire",
        "workshop_type": "lodge",
        "tagline": "A single twig breaks, but the bundle of twigs is strong.",
        "bio": "Born near present-day Chillicothe, Ohio. My father was killed fighting the settlers, my brother Chiksika was killed fighting the settlers, and I spent my life trying to unite all Native nations into one confederacy strong enough to stop the American advance. I traveled from the Great Lakes to the Gulf of Mexico, speaking to every tribe. Tenskwatawa, my brother the Prophet, provided the spiritual fire. William Henry Harrison, my enemy, admitted I was the greatest leader the tribes had ever produced. At the Battle of the Thames in 1813, my British allies ran while my warriors stood. I died fighting. Tip: Unity is the only weapon against a stronger enemy. Separately, each tribe falls. Together, we could have held the line. I failed because I could not convince them all in time.",
        "telegram_username": "shooting_star",
        "city": "Chillicothe",
        "country_code": "US",
        "latitude": 39.333,
        "longitude": -83.000,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "C1"}
        ],
        "skills": [
            {"skill_name": "Diplomacy", "category": "education", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Guerrilla Warfare", "category": "education", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Public Speaking", "category": "education", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Woodland Survival", "category": "outdoor", "self_rating": 5, "years_experience": 35}
        ],
        "social_links": [],
        "points": {"total_points": 1900, "rentals_completed": 48, "reviews_given": 50, "reviews_received": 62, "items_listed": 5, "helpful_flags": 48},
        "offers_training": True,
        "items": [
            {
                "name": "Coalition Building Masterclass -- Uniting the Divided",
                "slug": "coalition-building-uniting-divided",
                "description": "How to build a coalition from groups who distrust each other. Travel, listen, speak their language (literally and figuratively), find common ground. I visited over 30 tribes in 3 years. Tip: Do not ask them to join your cause. Show them it is already their cause. The enemy is coming for all of us.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Shawnee War Tomahawk & Trade Knife Set",
                "slug": "shawnee-war-tomahawk-trade-knife",
                "description": "Forged iron tomahawk (throwing and hand combat) and trade knife in leather sheath. The tomahawk is balanced for both throwing and fighting. The trade knife is the everyday tool of the woodlands. I will teach you the standing throw at 15 paces and the fighting grip for close work.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR", "deposit": 20.0}]
            },
            {
                "name": "Woodland Warfare & Ambush Tactics",
                "slug": "woodland-warfare-ambush-tactics",
                "description": "Fighting in the eastern forests. Ambush placement, tree-line defense, river crossing interdiction. The Shawnee were masters of woodland warfare -- we knew every trail, every crossing, every blind turn. Tip: In the forest, the defender is invisible and the attacker is blind. Make the forest your ally.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 16.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Oratory & Persuasion Workshop -- Speak to Move Nations",
                "slug": "oratory-persuasion-speak-move-nations",
                "description": "My speeches are still quoted 200 years later. I spoke to warriors, chiefs, governors, and generals. Every audience is different. Learn to read the room, find the emotional truth, and deliver it with the force of a war cry. Tip: Speak from the heart and the words will take care of themselves.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 14.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # 24. ZHUGE LIANG (181-234) - Chinese strategist
    # ============================================================
    {
        "slug": "zhuge-liangs-hidden-pavilion",
        "display_name": "Zhuge Liang",
        "email": "zhugeliang@borrowhood.local",
        "date_of_birth": "0181-01-01",
        "mother_name": "Lady Zhang -- died when I was young, leaving me to books and stars",
        "father_name": "Zhuge Gui -- a minor official of Langya Commandery",
        "workshop_name": "Zhuge Liang's Hidden Pavilion",
        "workshop_type": "pavilion",
        "tagline": "An enlightened ruler does not worry about people not knowing him; he worries about not knowing people.",
        "bio": "Born in Yangdu during the collapse of the Han Dynasty. Liu Bei visited my thatched cottage three times before I agreed to serve him -- the Three Visits that became legend. I was 26. I gave him the Longzhong Plan: ally with Sun Quan, take the Southlands, capture the West, then reclaim the North. I invented the repeating crossbow, designed the wooden ox transport system, and used the Empty Fort Strategy -- sitting on the walls playing the qin while Sima Yi's army approached. He retreated, convinced it was a trap. It was. The trap was his own fear. Tip: The greatest strategist makes the enemy defeat himself. Control information, shape perception, and let your opponent's assumptions become his prison. I served Shu Han faithfully until I died of exhaustion at Wuzhang Plains, still planning the northern campaign.",
        "telegram_username": "sleeping_dragon",
        "city": "Nanyang",
        "country_code": "CN",
        "latitude": 33.004,
        "longitude": 112.529,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "zh", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Grand Strategy", "category": "education", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Military Engineering", "category": "education", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Diplomacy", "category": "education", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Deception Tactics", "category": "education", "self_rating": 5, "years_experience": 25}
        ],
        "social_links": [],
        "points": {"total_points": 2600, "rentals_completed": 72, "reviews_given": 48, "reviews_received": 85, "items_listed": 6, "helpful_flags": 58},
        "offers_training": True,
        "items": [
            {
                "name": "Grand Strategy Seminar -- The Longzhong Plan Method",
                "slug": "grand-strategy-longzhong-plan",
                "description": "How to assess a strategic landscape and create a multi-year plan. Alliance building, resource assessment, timing, and the patience to wait for conditions to ripen. I planned Liu Bei's rise from a homeless refugee to Emperor of Shu Han. Tip: Strategy is not a single move. It is a sequence of moves that each make the next one possible.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Repeating Crossbow (Zhuge Nu Replica)",
                "slug": "repeating-crossbow-zhuge-nu-replica",
                "description": "My improvement on the repeating crossbow -- a gravity-fed magazine holding 10 bolts, fired by pumping the lever. Less accurate than a standard crossbow but devastating in volley fire. A line of these could stop a cavalry charge. Working replica, safe bolts for target practice.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 8.0, "price_unit": "per_day", "currency": "EUR", "deposit": 35.0}]
            },
            {
                "name": "The Art of Deception -- Empty Fort & Beyond",
                "slug": "art-of-deception-empty-fort",
                "description": "When Sima Yi came with 150,000 troops and I had 100 men, I opened the gates, sat on the wall, and played my qin. He retreated. The lesson: a strong reputation is a weapon. Your enemy's fear of what you might do is more powerful than what you actually can do. This workshop covers deception operations across history.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Guqin (Seven-String Zither) -- Strategy & Music",
                "slug": "guqin-seven-string-zither",
                "description": "The instrument I played on the empty walls. The guqin is 3,000 years old -- the scholar's instrument, played for meditation and clarity. I played it before every battle. Music orders the mind the way strategy orders the battlefield. Includes stand and tuning guide.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 6.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0}]
            },
            {
                "name": "Military Engineering Workshop -- Build What You Need",
                "slug": "military-engineering-build-what-you-need",
                "description": "The wooden ox, the repeating crossbow, fire weapons, pontoon bridges. How to solve military problems with engineering. I built transport systems for mountain supply lines that kept Shu Han's armies fed in impossible terrain. Tip: The engineer wins more battles than the swordsman. The swordsman fights the battle. The engineer decides whether there will be one.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # 25. HUA MULAN (~412-502) - Legendary female warrior
    # ============================================================
    {
        "slug": "mulans-training-ground",
        "display_name": "Hua Mulan",
        "email": "mulan@borrowhood.local",
        "date_of_birth": "0412-01-01",
        "mother_name": "Lady Hua -- a weaver who prayed every night for her daughter's safe return",
        "father_name": "Hua Hu -- an aging veteran too sick to answer the conscription call",
        "workshop_name": "Mulan's Training Ground",
        "workshop_type": "camp",
        "tagline": "The male hare hops and skips, the female hare has misty eyes. But when they run side by side, who can tell which is which?",
        "bio": "My father's name appeared on the conscription list. He was old and sick. My brother was a child. So I bought a horse at the east market, a saddle at the west market, a bridle at the south market, and a whip at the north market. I dressed as a man and rode to war in my father's place. Twelve years I served. I fought alongside men who never knew. The Khan offered me a minister's post. I asked only for a fast horse to ride home. When my comrades visited and saw me in women's clothes, they were shocked. I had marched, fought, and bled beside them for twelve years. Tip: Competence has no gender. When the arrow flies, it does not ask who loosed it. Train harder than anyone in the room and your secret, whatever it is, becomes irrelevant.",
        "telegram_username": "hua_mulan",
        "city": "Luoyang",
        "country_code": "CN",
        "latitude": 34.620,
        "longitude": 112.454,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "zh", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Sword Combat", "category": "sports", "self_rating": 5, "years_experience": 12},
            {"skill_name": "Horseback Riding", "category": "sports", "self_rating": 5, "years_experience": 15},
            {"skill_name": "Archery", "category": "sports", "self_rating": 5, "years_experience": 14},
            {"skill_name": "Disguise & Fieldcraft", "category": "outdoor", "self_rating": 5, "years_experience": 12}
        ],
        "social_links": [],
        "points": {"total_points": 1850, "rentals_completed": 47, "reviews_given": 42, "reviews_received": 58, "items_listed": 5, "helpful_flags": 44},
        "offers_training": True,
        "items": [
            {
                "name": "Chinese Dao Sword & Crossbow Training",
                "slug": "chinese-dao-crossbow-training",
                "description": "The dao -- single-edged, slightly curved, the workhorse of the Chinese military for a thousand years. Combined with crossbow marksmanship for both mounted and foot combat. I used these for twelve years in the field. Tip: Consistency beats brilliance. Practice the same cut ten thousand times until it is perfect, then practice it ten thousand more.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Chinese Dao Sword (Northern Wei Style)",
                "slug": "chinese-dao-sword-northern-wei",
                "description": "Single-edged dao, 32-inch blade, ring pommel. The standard infantry sword of the Northern Wei period. Optimized for cutting from horseback -- the slight curve pulls the blade through the target. I carried one for twelve years and it never failed me.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 6.0, "price_unit": "per_day", "currency": "EUR", "deposit": 25.0}]
            },
            {
                "name": "Fieldcraft & Camouflage Workshop -- Hide in Plain Sight",
                "slug": "fieldcraft-camouflage-hide-plain-sight",
                "description": "I hid my identity for twelve years among men who slept, ate, and fought beside me. This workshop covers physical camouflage, behavioral adaptation, gray man technique, and operating in environments where you do not belong. Tip: People see what they expect to see. Give them what they expect.",
                "item_type": "service",
                "category": "outdoor",
                "listings": [{"listing_type": "training", "price": 16.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Horse Selection & Care Workshop",
                "slug": "horse-selection-care-workshop",
                "description": "How to choose, care for, and bond with a war horse. Hoof inspection, feeding on campaign, recognizing lameness, field veterinary basics. My horse carried me through twelve years of war. Your horse is your life. Treat it better than you treat yourself.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 14.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # 26. HARRIET TUBMAN (1822-1913) - Underground Railroad warrior
    # ============================================================
    {
        "slug": "tubmans-safe-house",
        "display_name": "Harriet Tubman",
        "email": "tubman@borrowhood.local",
        "date_of_birth": "1822-03-01",
        "mother_name": "Harriet Greene (Rit) -- an enslaved woman who fought to keep her children",
        "father_name": "Ben Ross -- an enslaved timber worker who taught me the stars and the forest",
        "workshop_name": "Tubman's Safe House",
        "workshop_type": "lodge",
        "tagline": "I freed a thousand slaves. I could have freed a thousand more if only they knew they were slaves.",
        "bio": "Born Araminta Ross on a plantation in Dorchester County, Maryland. An overseer fractured my skull with a two-pound iron weight when I was twelve -- I had seizures and visions for the rest of my life. I escaped in 1849 and returned to the South thirteen times to lead over 300 people to freedom on the Underground Railroad. I carried a pistol -- pointed forward at slave catchers, backward at anyone who wanted to turn back. During the Civil War, I led the Combahee River Raid -- the first woman to lead an armed assault in American history. We freed 750 enslaved people in one night. Tip: Know every path, every safe house, every river crossing. Plan the route before you walk it. And never, ever turn back. The only direction is forward.",
        "telegram_username": "moses_conductor",
        "city": "Cambridge",
        "country_code": "US",
        "latitude": 38.563,
        "longitude": -76.079,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Escape & Evasion", "category": "outdoor", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Navigation (Stars)", "category": "outdoor", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Network Operations", "category": "education", "self_rating": 5, "years_experience": 15},
            {"skill_name": "Combat Leadership", "category": "education", "self_rating": 5, "years_experience": 10}
        ],
        "social_links": [],
        "points": {"total_points": 2200, "rentals_completed": 58, "reviews_given": 55, "reviews_received": 75, "items_listed": 5, "helpful_flags": 60},
        "offers_training": True,
        "items": [
            {
                "name": "Night Navigation Workshop -- Follow the North Star",
                "slug": "night-navigation-follow-north-star",
                "description": "Navigating by stars, moss, river direction, and landmarks in total darkness. I moved hundreds of people through swamps and forests at night with no map. The North Star was our compass. The drinking gourd song was our code. Tip: Move when the dogs cannot track -- in rain, through water, downwind. The night is your friend if you know her.",
                "item_type": "service",
                "category": "outdoor",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Underground Railroad Seminar -- Building Resistance Networks",
                "slug": "underground-railroad-resistance-networks",
                "description": "How to build and operate a clandestine network. Safe houses, codes, route planning, compartmentalization (each station knows only the next), vetting members. The Railroad operated for decades under the noses of slavers and federal marshals. Tip: Trust is your most valuable and most dangerous resource. Verify before you trust.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Civil War Field Medicine Kit",
                "slug": "civil-war-field-medicine-kit",
                "description": "Reproduction of a Civil War medical kit: bandages, tourniquets, herbal remedies, splint materials, suture kit. I served as a nurse before I led raids. Patching wounds in the field with no anesthesia and no hospital. These tools are replicas for training in field medicine basics.",
                "item_type": "physical",
                "category": "outdoor",
                "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR", "deposit": 20.0}]
            },
            {
                "name": "Courage Under Fire -- Leadership When Failure Means Death",
                "slug": "courage-under-fire-leadership-workshop",
                "description": "When the penalty for failure is death -- for you and everyone depending on you. Decision making under extreme pressure, keeping groups calm, dealing with fear and doubt. I never lost a single passenger on the Railroad. Tip: Fear is natural. Paralysis is not. Decide and move. A wrong decision made quickly is better than a right decision made too late.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 16.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # 27. SIMON BOLIVAR (1783-1830) - The Liberator
    # ============================================================
    {
        "slug": "bolivars-command-post",
        "display_name": "Simon Bolivar",
        "email": "bolivar@borrowhood.local",
        "date_of_birth": "1783-07-24",
        "mother_name": "Maria de la Concepcion Palacios y Blanco -- Creole aristocracy of Caracas",
        "father_name": "Juan Vicente Bolivar y Ponte -- one of the wealthiest men in Venezuela",
        "workshop_name": "Bolivar's Command Post",
        "workshop_type": "fortress",
        "tagline": "The art of victory is learned in defeat.",
        "bio": "Born to wealth in Caracas, educated in Europe, radicalized by revolution. I liberated Venezuela, Colombia, Ecuador, Peru, and Bolivia from Spanish rule -- five nations. I crossed the Andes in the rainy season with 2,500 men over a 13,000-foot pass. A third of them died of cold and altitude. The survivors descended on the Spanish garrison at Boyaca and destroyed them. Jose Antonio Paez was my greatest cavalry commander, Sucre my finest general. Manuela Saenz saved my life from assassins -- literally fought them off while I escaped through a window. Tip: Never stop after the first defeat. I was beaten, exiled, came back, was beaten again, came back again. The revolution failed five times before it succeeded. Persistence is the weapon empires cannot defeat.",
        "telegram_username": "el_libertador",
        "city": "Caracas",
        "country_code": "VE",
        "latitude": 10.500,
        "longitude": -66.917,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "es", "proficiency": "native"},
            {"language_code": "fr", "proficiency": "C1"},
            {"language_code": "en", "proficiency": "B2"}
        ],
        "skills": [
            {"skill_name": "Revolutionary Leadership", "category": "education", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Mountain Warfare", "category": "outdoor", "self_rating": 5, "years_experience": 15},
            {"skill_name": "Cavalry Tactics", "category": "sports", "self_rating": 4, "years_experience": 15},
            {"skill_name": "Political Strategy", "category": "education", "self_rating": 5, "years_experience": 20}
        ],
        "social_links": [],
        "points": {"total_points": 2350, "rentals_completed": 63, "reviews_given": 48, "reviews_received": 76, "items_listed": 5, "helpful_flags": 50},
        "offers_training": True,
        "items": [
            {
                "name": "Revolutionary Leadership Intensive -- From Defeat to Victory",
                "slug": "revolutionary-leadership-defeat-to-victory",
                "description": "How to lead a revolution when the revolution keeps failing. Rebuilding after defeat, maintaining support during exile, coming back stronger. I lost everything multiple times and rebuilt each time. Tip: Your cause must be bigger than your ego. The revolution is not about you. The moment it becomes about you, you have already lost.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Andes Mountain Crossing Expedition Training",
                "slug": "andes-mountain-crossing-expedition",
                "description": "High-altitude mountain warfare. Acclimatization, cold weather movement, river fording, maintaining combat effectiveness at altitude. I crossed a 13,000-foot pass in the wet season. A third of my army died. The rest won independence for a continent. Tip: The mountain does not care about your cause. Respect it or it kills you.",
                "item_type": "service",
                "category": "outdoor",
                "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Spanish Colonial Cavalry Saber",
                "slug": "spanish-colonial-cavalry-saber",
                "description": "Curved cavalry saber, standard issue for the Wars of Liberation. Light, fast, designed for the slashing attacks of llanero plainsmen cavalry. Paez and his llaneros could ride circles around Spanish regulars. The saber is their signature weapon.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 7.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0}]
            },
            {
                "name": "Nation-Building Workshop -- What Comes After the Revolution",
                "slug": "nation-building-after-revolution",
                "description": "Winning the war is the easy part. Building a nation from the wreckage is where most revolutions fail. Constitutions, governance, unifying factions that only agreed on the enemy. I freed five nations and watched them fracture. Tip: Plan for peace while you fight the war, or the peace will be worse than the war.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # 28. CRAZY HORSE (1840-1877) - Lakota war leader
    # ============================================================
    {
        "slug": "crazy-horses-war-lodge",
        "display_name": "Crazy Horse",
        "email": "crazyhorse@borrowhood.local",
        "date_of_birth": "1840-01-01",
        "mother_name": "Rattle Blanket Woman -- an Oglala Lakota who died when I was young",
        "father_name": "Crazy Horse (also named Waglula) -- a holy man who gave me his name after my first battle",
        "workshop_name": "Crazy Horse's War Lodge",
        "workshop_type": "lodge",
        "tagline": "My lands are where my dead lie buried.",
        "bio": "Born near Bear Butte in the Black Hills, light-skinned with curly hair -- the wasicu (whites) sometimes mistook me for one of their own. I never signed a treaty. I never lived on a reservation. I never allowed a photograph. At the Fetterman Fight, I decoyed 81 soldiers into an ambush where 2,000 warriors waited. At the Little Bighorn, while Sitting Bull held the camp, I led the charge that surrounded and destroyed Custer's 7th Cavalry. Gall hit them from the south, I hit them from the north. It was over in an hour. Tip: The decoy is the most dangerous role. You must be brave enough to stand in front of the enemy alone, skilled enough to survive, and trusted enough that your warriors hold their position until the trap springs. I surrendered at Fort Robinson and was bayoneted in the guardhouse. They killed me while pretending to arrest me.",
        "telegram_username": "tashunka_witko",
        "city": "Rapid City",
        "country_code": "US",
        "latitude": 44.080,
        "longitude": -103.231,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "B1"}
        ],
        "skills": [
            {"skill_name": "Mounted Combat", "category": "sports", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Decoy Tactics", "category": "education", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Archery", "category": "sports", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Plains Warfare", "category": "education", "self_rating": 5, "years_experience": 20}
        ],
        "social_links": [],
        "points": {"total_points": 1950, "rentals_completed": 50, "reviews_given": 28, "reviews_received": 65, "items_listed": 5, "helpful_flags": 42},
        "offers_training": True,
        "items": [
            {
                "name": "Decoy & Ambush Tactics Workshop",
                "slug": "decoy-ambush-tactics-workshop",
                "description": "The decoy lures, the ambush kills. How to draw an enemy into a position of your choosing. Terrain selection, patience, the courage to stand alone in front of the enemy. At the Fetterman Fight, I taunted 81 soldiers into chasing me over a ridge where 2,000 warriors waited. Tip: The decoy who panics gets his friends killed. Be calm. Trust the plan.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Lakota War Lance & Coup Stick",
                "slug": "lakota-war-lance-coup-stick",
                "description": "10-foot war lance with iron point and eagle feather decorations, plus a coup stick. Counting coup -- touching an enemy in battle without killing him -- was the highest act of bravery. Killing was easy. Touching was courage. I counted coup many times before I started fighting for survival.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 6.0, "price_unit": "per_day", "currency": "EUR", "deposit": 25.0}]
            },
            {
                "name": "Mounted Combat Training -- Fight From the Horse",
                "slug": "mounted-combat-fight-from-horse",
                "description": "Bareback mounted combat with lance, bow, and war club. The Lakota fought from horseback as naturally as walking. Hanging off the side of the horse as a shield, shooting under the neck, the full-speed charge. Tip: Your war paint is your identity. I painted a lightning bolt on my face and hail spots on my body. The enemy should know who is coming for them.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 24.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Plains War Shield (Buffalo Hide, Painted)",
                "slug": "plains-war-shield-buffalo-hide",
                "description": "Thick buffalo hide shield, heat-shrunk and painted with personal medicine symbols. At proper thickness, buffalo hide stops arrows and can deflect a musket ball at distance. The painting is not decoration -- it is protection medicine. This is a training replica. Respect the tradition.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR", "deposit": 25.0}]
            }
        ]
    },

    # ============================================================
    # 29. CLEOPATRA VII (69-30 BC) - Egyptian pharaoh/strategist
    # ============================================================
    {
        "slug": "cleopatras-war-council",
        "display_name": "Cleopatra VII",
        "email": "cleopatra@borrowhood.local",
        "date_of_birth": "0069-01-01",
        "mother_name": "Cleopatra V Tryphaena -- though the records are disputed",
        "father_name": "Ptolemy XII Auletes -- the Flute Player, a weak king who taught me what not to be",
        "workshop_name": "Cleopatra's War Council",
        "workshop_type": "palace",
        "tagline": "I will not be triumphed over.",
        "bio": "Last active ruler of the Ptolemaic Kingdom of Egypt. I spoke nine languages. I was the first Ptolemy in 300 years to learn Egyptian. My brother tried to kill me. I smuggled myself to Caesar rolled in a carpet and won his alliance in one night. When Caesar was murdered, I allied with Mark Antony -- lover, partner, and co-commander. Together we controlled the eastern Mediterranean. At Actium, Octavian's fleet destroyed ours. Antony died on my lap. I chose the asp over Roman chains. Octavian wanted to parade me through Rome. I denied him that. Tip: Alliances are weapons. Choose them wisely, maintain them ruthlessly, and never be the weaker partner. I used every tool available -- intellect, charm, wealth, naval power. The person who tells you that using charm is weakness has never held an empire together with it.",
        "telegram_username": "last_pharaoh",
        "city": "Alexandria",
        "country_code": "EG",
        "latitude": 31.200,
        "longitude": 29.919,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "el", "proficiency": "native"},
            {"language_code": "ar", "proficiency": "C1"},
            {"language_code": "la", "proficiency": "C1"},
            {"language_code": "fa", "proficiency": "B2"}
        ],
        "skills": [
            {"skill_name": "Strategic Alliances", "category": "education", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Naval Command", "category": "education", "self_rating": 4, "years_experience": 10},
            {"skill_name": "Political Strategy", "category": "education", "self_rating": 5, "years_experience": 22},
            {"skill_name": "Diplomacy", "category": "education", "self_rating": 5, "years_experience": 22}
        ],
        "social_links": [],
        "points": {"total_points": 2300, "rentals_completed": 60, "reviews_given": 52, "reviews_received": 74, "items_listed": 5, "helpful_flags": 50},
        "offers_training": True,
        "items": [
            {
                "name": "Strategic Alliance Building -- Power Through Partnership",
                "slug": "strategic-alliance-power-partnership",
                "description": "How to identify, secure, and maintain alliances when you are not the strongest power. I allied with the two most powerful Romans of the age -- Caesar and Antony -- and kept Egypt independent for 20 years. Tip: Never enter an alliance as the supplicant. Bring value. I brought the wealth of Egypt. What do you bring?",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Egyptian Khopesh Sword (Bronze, Ceremonial & Combat)",
                "slug": "egyptian-khopesh-sword-bronze",
                "description": "The sickle-sword of Egypt. Curved blade for hooking shields and trapping weapons. The pharaohs carried these into battle for 2,000 years. Bronze blade, gold-inlaid hilt. Both a weapon and a symbol of royal power. My guards carried them at Actium.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 8.0, "price_unit": "per_day", "currency": "EUR", "deposit": 35.0}]
            },
            {
                "name": "Naval Strategy Seminar -- Mediterranean Sea Power",
                "slug": "naval-strategy-mediterranean-sea-power",
                "description": "From the Ptolemaic fleet to Actium. Trireme tactics, fleet logistics, coastal defense, the strategic value of Egypt's position. At Actium we had 230 warships. We lost because Agrippa was a better admiral than our commanders. Tip: Control the sea and you control the trade. Control the trade and you control the wealth. Control the wealth and you control everything.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Multilingual Negotiation Workshop -- Speak Their Language",
                "slug": "multilingual-negotiation-speak-their-language",
                "description": "I spoke nine languages and used every one of them in negotiations. Speaking a person's language is the fastest way to their trust. This workshop covers negotiation tactics, cultural reading, and why the interpreter should be you, not someone you hired. Tip: The person who controls the translation controls the conversation.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # 30. TOKUGAWA IEYASU (1543-1616) - Unified Japan
    # ============================================================
    {
        "slug": "tokugawas-castle",
        "display_name": "Tokugawa Ieyasu",
        "email": "ieyasu@borrowhood.local",
        "date_of_birth": "1543-01-31",
        "mother_name": "Odai no Kata -- a woman of the Mizuno clan, taken from me as a political hostage",
        "father_name": "Matsudaira Hirotada -- a minor lord who traded me as a hostage at age six",
        "workshop_name": "Tokugawa's Castle",
        "workshop_type": "fortress",
        "tagline": "The strong manly ones in life are those who understand the meaning of the word patience.",
        "bio": "Born Matsudaira Takechiyo. I was a hostage from age six to fifteen. I watched. I learned. I waited. While Oda Nobunaga conquered and Toyotomi Hideyoshi unified, I built alliances and bided my time. When Hideyoshi died, I struck. At Sekigahara in 1600, the greatest battle in Japanese history, I defeated the Western Army through a combination of bribery, treachery, and tactical brilliance -- half the enemy switched sides mid-battle because I had bought them months before. I established the Tokugawa Shogunate, which brought 250 years of peace to Japan. Tip: Patience is the deadliest strategy. Let your rivals exhaust themselves. The last man standing does not need to be the strongest -- only the most patient. As I said: after the victory, tighten your helmet straps.",
        "telegram_username": "eastern_shogun",
        "city": "Okazaki",
        "country_code": "JP",
        "latitude": 34.951,
        "longitude": 137.176,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "ja", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Political Strategy", "category": "education", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Castle Warfare", "category": "education", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Alliance Management", "category": "education", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Swordsmanship", "category": "sports", "self_rating": 4, "years_experience": 40}
        ],
        "social_links": [],
        "points": {"total_points": 2550, "rentals_completed": 70, "reviews_given": 55, "reviews_received": 82, "items_listed": 6, "helpful_flags": 55},
        "offers_training": True,
        "items": [
            {
                "name": "The Art of Patience -- Strategic Waiting Workshop",
                "slug": "art-of-patience-strategic-waiting",
                "description": "How to win by waiting. When to act and when to hold. Reading the political landscape, building position without exposing yourself, striking at the decisive moment. Nobunaga seized the rice cake, Hideyoshi cooked it, I ate it. Tip: If you cannot wait, you cannot win. The patient warrior outlasts the bold one.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Tachi & Tanto Sword Set (Edo Period Style)",
                "slug": "tachi-tanto-sword-set-edo",
                "description": "Long tachi sword (blade-down mounting, cavalry style) and tanto short blade. The tachi predates the katana -- designed for mounted combat with a longer, more curved blade. The tanto is the samurai's constant companion, used for everything from combat to seppuku. Proper handling instruction included.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 12.0, "price_unit": "per_day", "currency": "EUR", "deposit": 55.0}]
            },
            {
                "name": "Japanese Castle Design Seminar -- Defensive Architecture",
                "slug": "japanese-castle-design-defensive-architecture",
                "description": "Concentric baileys, stone walls, murder holes, and the famous curved walls that prevent climbing and deflect cannonballs. Edo Castle was my masterwork. This seminar covers Japanese castle design from the Sengoku period through the Edo period. Tip: A castle should make the attacker solve ten problems to reach you. Each problem costs him men.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Tanegashima Matchlock Musket (Replica)",
                "slug": "tanegashima-matchlock-musket-replica",
                "description": "Japanese matchlock musket, based on Portuguese originals that arrived in 1543 -- the year I was born. Within 50 years, Japan had more firearms than any country in Europe. At Sekigahara, guns decided the battle. This replica fires black powder blanks for demonstration.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 10.0, "price_unit": "per_day", "currency": "EUR", "deposit": 45.0}]
            },
            {
                "name": "Sekigahara Battle Study -- Winning Before the Fight",
                "slug": "sekigahara-battle-study-winning-before",
                "description": "A detailed analysis of the Battle of Sekigahara, 1600. How I spent months before the battle buying defections, planting doubts, and ensuring that half the enemy army would betray their commander on the field. When the fight started, the outcome was already decided. Tip: The battle is the last resort of the strategist. If you must fight, you have already failed at something.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # 31. ACHILLES (~1250 BC) - Trojan War hero
    # ============================================================
    {
        "slug": "achilles-war-camp",
        "display_name": "Achilles",
        "email": "achilles@borrowhood.local",
        "date_of_birth": "1250-01-01",
        "mother_name": "Thetis -- a sea goddess who dipped me in the River Styx and missed my heel",
        "father_name": "Peleus -- King of the Myrmidons, a mortal who married a goddess",
        "workshop_name": "Achilles' War Camp",
        "workshop_type": "arena",
        "tagline": "I say no wealth is worth my life.",
        "bio": "Born in Phthia, son of Peleus and the sea nymph Thetis. She held me by the heel and dipped me in the Styx to make me invulnerable -- all except that heel. My mother tried to hide me among women to keep me from Troy. Odysseus found me. At Troy, I was the greatest warrior on either side. I killed Hector and dragged his body behind my chariot for twelve days. Patroclus was my soul -- when Hector killed him wearing my armor, something broke in me that rage filled. Priam came alone at night to beg for his son's body. An old king kneeling before the man who killed his boy. I gave Hector back. Tip: Rage makes you powerful and stupid in equal measure. I refused to fight because Agamemnon insulted me, and Patroclus died for my pride. Channel your anger or it will consume you and everyone you love.",
        "telegram_username": "swift_achilles",
        "city": "Volos",
        "country_code": "GR",
        "latitude": 39.362,
        "longitude": 22.944,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "el", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Spear Combat", "category": "sports", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Sword Combat", "category": "sports", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Shield Fighting", "category": "sports", "self_rating": 5, "years_experience": 18},
            {"skill_name": "Physical Conditioning", "category": "sports", "self_rating": 5, "years_experience": 25}
        ],
        "social_links": [],
        "points": {"total_points": 2400, "rentals_completed": 65, "reviews_given": 30, "reviews_received": 80, "items_listed": 6, "helpful_flags": 45},
        "offers_training": True,
        "items": [
            {
                "name": "Myrmidon Combat Training -- Elite Warrior Conditioning",
                "slug": "myrmidon-combat-elite-conditioning",
                "description": "Training as the Myrmidons trained. Spear, sword, shield, and body conditioning that would make Olympians weep. The Myrmidons were the most feared unit at Troy -- not because of numbers but because every single warrior was exceptional. Tip: An elite unit is not fifty good fighters. It is fifty fighters who trust each other with their lives.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Pelian Ash Spear (Replica of Achilles' Spear)",
                "slug": "pelian-ash-spear-achilles-replica",
                "description": "The Pelian ash spear -- cut from a tree on Mount Pelion by the centaur Chiron. No other Greek at Troy could wield it. This replica is 9 feet of ash with a bronze head. Heavy, meant for a warrior who fights from the front. I killed Hector with a spear like this, through the gap in his throat armor.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 7.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0}]
            },
            {
                "name": "Single Combat Workshop -- The Duel",
                "slug": "single-combat-duel-workshop",
                "description": "One-on-one combat with spear, sword, and shield. The Homeric duel: trash talk, javelin throw, close with swords, finish the job. I fought the greatest warriors of Troy in single combat and never lost. Tip: Study your opponent before you fight him. Watch how he moves, which foot he leads with, where his shield drops.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Bronze Cuirass & Greaves (Mycenaean Style)",
                "slug": "bronze-cuirass-greaves-mycenaean",
                "description": "Beaten bronze cuirass (breastplate and backplate), bronze greaves, and boar's tusk helmet. Mycenaean warrior gear from the age of heroes. The bronze is functional -- it stops a blade. The boar's tusk helmet took hundreds of tusks to make. Wear it and feel what my warriors wore on the plains of Troy.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 12.0, "price_unit": "per_day", "currency": "EUR", "deposit": 55.0}]
            },
            {
                "name": "Rage Management for Warriors -- Channel the Fire",
                "slug": "rage-management-warriors-channel-fire",
                "description": "My rage nearly lost the war for the Greeks. When I withdrew, the Trojans almost burned the ships. When I returned, I was unstoppable but reckless. This workshop teaches how to use anger as fuel without letting it drive. Tip: The warrior who fights in cold blood wins. The warrior who fights in hot blood fights well but makes mistakes that cost lives.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 16.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # 32. VLAD III DRACULA (1431-1476) - Wallachian defender
    # ============================================================
    {
        "slug": "vlads-fortress",
        "display_name": "Vlad III Dracula",
        "email": "vlad@borrowhood.local",
        "date_of_birth": "1431-11-01",
        "mother_name": "Cneajna of Moldavia -- a princess who married into the House of Draculesti",
        "father_name": "Vlad II Dracul -- member of the Order of the Dragon, hence Dracula: son of the Dragon",
        "workshop_name": "Vlad's Fortress",
        "workshop_type": "fortress",
        "tagline": "I have killed men and women, old and young. I have done it for Wallachia.",
        "bio": "Born in Sighisoara, Transylvania. My father was inducted into the Order of the Dragon -- hence Dracul (Dragon) and I am Dracula, son of the Dragon. The Ottomans held me hostage as a boy alongside my brother Radu. I learned Turkish, court politics, and hatred. When Sultan Mehmed II sent envoys who refused to remove their turbans, I had the turbans nailed to their heads. I impaled 20,000 Ottoman prisoners and lined the road to my capital with them. Mehmed, the conqueror of Constantinople, turned his army around when he saw the forest of stakes. Tip: Deterrence is the most efficient form of defense. Make the cost of attacking you so horrifying that no rational enemy will attempt it. My methods were brutal, but Wallachia survived between the Ottoman Empire and Hungary because both sides feared crossing my land. I was murdered by boyars, possibly Ottomans. My head was sent to Constantinople.",
        "telegram_username": "son_of_dragon",
        "city": "Sighisoara",
        "country_code": "RO",
        "latitude": 46.219,
        "longitude": 24.796,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "ro", "proficiency": "native"},
            {"language_code": "tr", "proficiency": "C1"},
            {"language_code": "la", "proficiency": "B2"}
        ],
        "skills": [
            {"skill_name": "Psychological Warfare", "category": "education", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Guerrilla Warfare", "category": "education", "self_rating": 5, "years_experience": 15},
            {"skill_name": "Fortress Defense", "category": "education", "self_rating": 5, "years_experience": 15},
            {"skill_name": "Sword Combat", "category": "sports", "self_rating": 5, "years_experience": 25}
        ],
        "social_links": [],
        "points": {"total_points": 1800, "rentals_completed": 45, "reviews_given": 20, "reviews_received": 58, "items_listed": 5, "helpful_flags": 30},
        "offers_training": True,
        "items": [
            {
                "name": "Night Raid Tactics Workshop -- Strike in the Dark",
                "slug": "night-raid-tactics-strike-dark",
                "description": "In 1462, I attacked the Ottoman camp at night with 7,000 men against 90,000. We rode through the camp killing anyone we could reach, aiming for Mehmed's tent. We did not get Mehmed, but the terror was devastating. Night raids require total discipline and intimate knowledge of the terrain. Tip: In darkness, confusion is your weapon. The enemy fights his own shadows.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Wallachian Kilij Sword & Buckler",
                "slug": "wallachian-kilij-sword-buckler",
                "description": "Curved kilij saber -- Ottoman-influenced, adopted by Wallachian cavalry. Combined with a small steel buckler for parrying. The curve is deeper than a scimitar, designed for devastating draw cuts. My cavalry carried these on raids behind Ottoman lines.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 7.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0}]
            },
            {
                "name": "Deterrence Strategy Seminar -- The Cost of Crossing You",
                "slug": "deterrence-strategy-seminar-cost",
                "description": "How to make yourself too dangerous to attack. Reputation building, calculated displays of power, escalation control. I kept Wallachia independent between two empires through pure deterrence. The Ottomans had ten times my numbers but feared my land. Tip: You do not need to be the strongest. You need to be the most expensive to defeat.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Mountain Fortress Defense Workshop",
                "slug": "mountain-fortress-defense-workshop",
                "description": "Poenari Castle sits on a cliff above the Arges River. To reach it, attackers must climb 1,480 steps while my archers shoot down. This workshop covers mountain fortress selection, supply management, escape routes, and making the terrain fight for you.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 16.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # 33. LAKSHMIBAI (1828-1858) - Rani of Jhansi
    # ============================================================
    {
        "slug": "lakshmibais-fort",
        "display_name": "Lakshmibai",
        "email": "lakshmibai@borrowhood.local",
        "date_of_birth": "1828-11-19",
        "mother_name": "Bhagirathi Bai -- who died when I was four, leaving me among warriors",
        "father_name": "Moropant Tambe -- a court advisor who raised me like a warrior, not a lady",
        "workshop_name": "Lakshmibai's Fort",
        "workshop_type": "fortress",
        "tagline": "I shall not surrender my Jhansi.",
        "bio": "Born Manikarnika in Varanasi. My father raised me at the court of Peshwa Baji Rao II, where I learned horse riding, sword fighting, and martial arts alongside the boys. I married the Maharaja of Jhansi. When he died, the British invoked the Doctrine of Lapse and tried to annex my kingdom. I refused. When the Indian Rebellion of 1857 erupted, I fortified Jhansi and fought the British army with 14,000 defenders. General Hugh Rose called me the most dangerous of all rebel leaders. When the walls fell, I escaped with my son strapped to my back, fighting through British lines on horseback. Tantia Tope and Nana Sahib were my allies in the rebellion. Tip: Prepare for the siege before the enemy arrives. I stockpiled food, weapons, and gunpowder while the British were still debating. When they came, Jhansi was ready. I died fighting at Gwalior, sword in hand, reins in teeth, son on my back.",
        "telegram_username": "rani_of_jhansi",
        "city": "Varanasi",
        "country_code": "IN",
        "latitude": 25.318,
        "longitude": 83.011,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "hi", "proficiency": "native"},
            {"language_code": "mr", "proficiency": "native"},
            {"language_code": "en", "proficiency": "B1"}
        ],
        "skills": [
            {"skill_name": "Sword Combat", "category": "sports", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Horseback Riding", "category": "sports", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Siege Defense", "category": "education", "self_rating": 5, "years_experience": 5},
            {"skill_name": "Military Leadership", "category": "education", "self_rating": 5, "years_experience": 5}
        ],
        "social_links": [],
        "points": {"total_points": 2050, "rentals_completed": 53, "reviews_given": 45, "reviews_received": 67, "items_listed": 5, "helpful_flags": 48},
        "offers_training": True,
        "items": [
            {
                "name": "Indian Cavalry Sword & Shield Training",
                "slug": "indian-cavalry-sword-shield-training",
                "description": "Tulwar sword and dhal shield -- the weapons of Maratha cavalry. The tulwar has a distinctive disc pommel that locks the hand in place for powerful cuts. The dhal is a round steel shield, light enough for mounted use. I rode into battle with both, my son strapped to my back. Tip: The sword follows the horse. Learn to ride first, fight second.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Tulwar Sword & Dhal Shield Set (Maratha Style)",
                "slug": "tulwar-sword-dhal-shield-maratha",
                "description": "Steel tulwar with disc pommel and 30-inch curved blade, plus round steel dhal shield with four bosses. The Maratha fighting style uses the shield offensively -- the bosses punch, the rim strikes. The tulwar delivers devastating draw cuts. A complete Indian warrior's kit.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 8.0, "price_unit": "per_day", "currency": "EUR", "deposit": 35.0}]
            },
            {
                "name": "Siege Preparation Workshop -- Ready Before They Come",
                "slug": "siege-preparation-ready-before-they-come",
                "description": "How to prepare a position for siege before the enemy arrives. Stockpiling, fortification, water security, morale planning, escape route preparation. I prepared Jhansi while the British debated. When they arrived, we held for weeks against artillery. Tip: The siege is won or lost before the first cannon fires. What you do not stockpile today, you will die without tomorrow.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Women Warriors of India -- History & Training Seminar",
                "slug": "women-warriors-india-history-seminar",
                "description": "From the Rani of Jhansi to the Rani Durgavati, from Kittur Chennamma to Ahilyabai Holkar. Indian women have led armies, defended kingdoms, and fought empires for centuries. This seminar covers their stories and the martial traditions they practiced. I am not the exception. I am part of a long line.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 14.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # 34. SAMORI TURE (1830-1900) - West African empire builder
    # ============================================================
    {
        "slug": "samoris-war-council",
        "display_name": "Samori Ture",
        "email": "samori@borrowhood.local",
        "date_of_birth": "1830-01-01",
        "mother_name": "Masorona Kamara -- captured and enslaved, which set me on the warrior's path",
        "father_name": "Lafiya Ture -- a Dyula trader from Manyambaladugu",
        "workshop_name": "Samori's War Council",
        "workshop_type": "camp",
        "tagline": "A nation that does not manufacture its own weapons is a nation in chains.",
        "bio": "Born to a Dyula trading family in Manyambaladugu, in what is now Guinea. When my mother was captured by a rival kingdom, I enlisted in their army to be near her. I rose through the ranks, won her freedom, then built my own army and conquered an empire stretching from Guinea to Ivory Coast. I fought the French for 16 years -- longer than any other African leader. I was the first African military leader to manufacture modern firearms locally, building blacksmith workshops that reverse-engineered European rifles. When the French pushed me from one territory, I built a new empire further east. Tip: Self-sufficiency is survival. If your weapons come from your enemy's supplier, you are already defeated. I built my own guns, trained my own blacksmiths, and maintained my own supply chain. The French captured me by trickery in 1898. I died in exile in Gabon.",
        "telegram_username": "almamy_samori",
        "city": "Kankan",
        "country_code": "GN",
        "latitude": 10.386,
        "longitude": -9.305,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "fr", "proficiency": "B2"}
        ],
        "skills": [
            {"skill_name": "Military Manufacturing", "category": "education", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Empire Building", "category": "education", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Guerrilla Warfare", "category": "education", "self_rating": 5, "years_experience": 16},
            {"skill_name": "Cavalry Tactics", "category": "sports", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Firearms", "category": "sports", "self_rating": 5, "years_experience": 20}
        ],
        "social_links": [],
        "points": {"total_points": 2100, "rentals_completed": 55, "reviews_given": 40, "reviews_received": 68, "items_listed": 5, "helpful_flags": 45},
        "offers_training": True,
        "items": [
            {
                "name": "Weapons Manufacturing Workshop -- Build Your Own Arsenal",
                "slug": "weapons-manufacturing-build-arsenal",
                "description": "How I reverse-engineered European rifles and built a local arms industry from blacksmith shops. Metallurgy, pattern analysis, toolmaking, quality control. My gunsmiths produced reliable copies of French Gras rifles in village forges. Tip: Any technology can be replicated if you understand the principles. Do not worship the tool -- understand it, then build your own.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "West African Cavalry Saber & Leather Shield",
                "slug": "west-african-cavalry-saber-shield",
                "description": "Mandinka cavalry saber and leather-covered wicker shield. My sofa (warrior) cavalry was the backbone of the Wassoulou Empire. Light, fast, armed with sabers and locally-made muskets. The shield stops arrows and deflects glancing sword cuts -- it is not meant to take a direct hit.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 6.0, "price_unit": "per_day", "currency": "EUR", "deposit": 25.0}]
            },
            {
                "name": "Anti-Colonial Resistance Seminar -- 16 Years Against France",
                "slug": "anti-colonial-resistance-16-years",
                "description": "How I fought the French empire for sixteen years with local resources. Scorched earth, strategic retreat, rebuilding in new territory, diplomatic maneuvering with the British. When France took my western empire, I built a new one further east. Tip: If you cannot hold the ground, take the people and the knowledge. Territory can be reconquered. Dead men cannot.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Supply Chain Independence Workshop -- Self-Sufficiency",
                "slug": "supply-chain-independence-self-sufficiency",
                "description": "Building a self-sufficient military supply chain. Local manufacturing, resource management, trade network building, reducing dependence on external suppliers. The French tried to starve me of weapons. I built my own factories. Tip: Every dependency is a vulnerability. Every skill you outsource is a throat your enemy can cut.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Locally-Made Flintlock Musket (Wassoulou Replica)",
                "slug": "locally-made-flintlock-wassoulou-replica",
                "description": "A replica of the muskets my blacksmiths produced. Hand-forged barrel, wooden stock, flintlock mechanism. Not as refined as a French Gras but it fires, it kills, and it was made by African hands in an African forge. That is the point. Non-firing display replica for education.",
                "item_type": "physical",
                "category": "education",
                "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR", "deposit": 20.0}]
            }
        ]
    },
]


def merge_into_seed():
    """Merge warrior legends into seed.json."""
    import json
    from pathlib import Path

    seed_path = Path(__file__).parent / "seed.json"
    with open(seed_path) as f:
        data = json.load(f)

    existing_slugs = {u["slug"] for u in data["users"]}
    existing_item_slugs = {i["slug"] for i in data["items"]}

    added_users = 0
    for legend in LEGENDS_WARRIORS:
        if legend["slug"] not in existing_slugs:
            items = legend.pop("items", [])
            user_data = {}
            for k, v in legend.items():
                user_data[k] = v
            data["users"].append(user_data)
            existing_slugs.add(legend["slug"])
            added_users += 1

            for item in items:
                if item["slug"] not in existing_item_slugs:
                    item["owner_slug"] = legend["slug"]
                    item["content_language"] = "en"
                    if "media" not in item:
                        item["media"] = []
                    data["items"].append(item)
                    existing_item_slugs.add(item["slug"])

    with open(seed_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Warriors: Added {added_users} warrior legend users")
    print(f"Warriors: Total users now: {len(data['users'])}")
    print(f"Warriors: Total items now: {len(data['items'])}")


if __name__ == "__main__":
    merge_into_seed()
