"""Inventor & Scientist legends for BorrowHood.

34 historical inventors and scientists, each with a workshop full of
items to lend, rent, or teach. Mix of physical equipment and services
(lab demos, tutoring, workshops, mentoring).

Run: python seed_data/legends_inventors.py
Output: merges into seed_data/seed.json
"""

LEGENDS_INVENTORS = [
    # ============================================================
    # 1. THOMAS EDISON (1847-1931)
    # ============================================================
    {
        "slug": "edisons-menlo-park",
        "display_name": "Thomas Alva Edison",
        "email": "edison@borrowhood.local",
        "date_of_birth": "1847-02-11",
        "mother_name": "Nancy Matthews Elliott",
        "father_name": "Samuel Ogden Edison Jr.",
        "workshop_name": "Edison's Menlo Park Lab",
        "workshop_type": "laboratory",
        "tagline": "Genius is one percent inspiration and ninety-nine percent perspiration",
        "bio": "Born in Milan, Ohio. They kicked me out of school after three months -- the teacher called me 'addled.' My mother homeschooled me. Best thing that ever happened. I set up my first lab at age 10 in the basement. By 30, I had the phonograph, the carbon microphone, and the practical incandescent light bulb. 1,093 patents. Tip: I didn't fail 1,000 times to make the light bulb. I found 1,000 ways that don't work. Each failure is data. Document everything. My notebooks fill 3,500 pages. The difference between an inventor and a dreamer is the notebook. I hired Nikola Tesla once. He was brilliant. We disagreed about everything. AC vs DC. He was right about that one. Don't tell him I said so.",
        "telegram_username": "wizard_menlo",
        "city": "Milan",
        "country_code": "US",
        "latitude": 41.403,
        "longitude": -82.607,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Electrical Engineering", "category": "electronics", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Prototyping", "category": "tools", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Patent Writing", "category": "education", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Laboratory Management", "category": "education", "self_rating": 5, "years_experience": 40}
        ],
        "social_links": [],
        "points": {"total_points": 2400, "rentals_completed": 65, "reviews_given": 50, "reviews_received": 75, "items_listed": 9, "helpful_flags": 45},
        "offers_training": True,
        "items": [
            {
                "name": "Invention Workshop -- From Idea to Prototype",
                "slug": "invention-workshop-idea-to-prototype",
                "description": "Bring me your idea. Any idea. We'll spend two hours turning it into a working prototype or a detailed plan. I've done this 1,093 times. Tip: Start with the problem, not the solution. Who has this problem? How bad is it? How much would they pay to make it go away? If the answer is 'a lot,' build it. If the answer is 'not much,' find a different problem.",
                "item_type": "service",
                "category": "tools",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Phonograph (Cylinder Type, Working Replica)",
                "slug": "phonograph-cylinder-working-replica",
                "description": "Working replica of my 1877 phonograph. Speak into the horn, turn the crank, it records your voice on a tin foil cylinder. Then play it back. The first time I heard my own voice played back, I knew the world had changed. You will too.",
                "item_type": "physical",
                "category": "electronics",
                "listings": [{"listing_type": "rent", "price": 10.0, "price_unit": "per_day", "currency": "EUR", "deposit": 50.0}]
            },
            {
                "name": "Electrical Wiring & Circuits Workshop",
                "slug": "electrical-wiring-circuits-workshop",
                "description": "Hands-on workshop: wire a circuit from scratch. Series, parallel, switches, fuses. We build a working lamp by the end. Tip: Always check the circuit BEFORE you connect power. I lost part of my hearing to an accident. Learn from my mistakes, not my losses.",
                "item_type": "service",
                "category": "electronics",
                "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Inventor's Notebook (Leather Bound, Grid Pages)",
                "slug": "inventors-notebook-leather-grid",
                "description": "Leather-bound notebook with grid pages. Date every entry. Sketch every idea. Have someone witness each page. This is how patents start. This is how Edison's Menlo Park worked -- 40 notebooks a year, every experiment documented.",
                "item_type": "physical",
                "category": "tools",
                "listings": [{"listing_type": "offer", "price": 5.0, "price_unit": "per_unit", "currency": "EUR"}]
            },
            {
                "name": "Patent Writing Crash Course -- Protect Your Ideas",
                "slug": "patent-writing-crash-course",
                "description": "Small group (max 4). I'll teach you how to write a patent application: claims, specifications, drawings. The patent is the inventor's sword and shield. Without it, your idea belongs to whoever copies it first. I learned this the hard way with the movie camera.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # 2. ALEXANDER GRAHAM BELL (1847-1922)
    # ============================================================
    {
        "slug": "bells-speaking-machine",
        "display_name": "Alexander Graham Bell",
        "email": "bell@borrowhood.local",
        "date_of_birth": "1847-03-03",
        "mother_name": "Eliza Grace Symonds",
        "father_name": "Alexander Melville Bell",
        "workshop_name": "Bell's Speaking Machine Lab",
        "workshop_type": "laboratory",
        "tagline": "When one door closes, another opens; but we often look so long at the closed door that we do not see the one which has been opened for us",
        "bio": "Born in Edinburgh, Scotland. My mother was nearly deaf. My father invented Visible Speech, a phonetic alphabet for the deaf. I grew up surrounded by the science of sound. Moved to Canada at 23, then Boston to teach deaf students. That's where I met Thomas Watson. On March 10, 1876: 'Mr. Watson, come here. I want to see you.' The telephone. Tip: The best inventions come from empathy. I didn't set out to build a telephone. I set out to help deaf people communicate. The telephone was a side effect. Also founded the National Geographic Society. Also worked on hydrofoils. Also pioneered metal detectors -- tried to find the bullet in President Garfield. It didn't work because the bed had metal springs. Always check your assumptions.",
        "telegram_username": "mr_watson",
        "city": "Edinburgh",
        "country_code": "GB",
        "latitude": 55.953,
        "longitude": -3.189,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Acoustics", "category": "electronics", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Deaf Education", "category": "education", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Electrical Engineering", "category": "electronics", "self_rating": 4, "years_experience": 35},
            {"skill_name": "Public Speaking", "category": "education", "self_rating": 5, "years_experience": 40}
        ],
        "social_links": [],
        "points": {"total_points": 2200, "rentals_completed": 60, "reviews_given": 45, "reviews_received": 70, "items_listed": 8, "helpful_flags": 40},
        "offers_training": True,
        "items": [
            {
                "name": "Telephone Prototype (Working Replica, 1876 Model)",
                "slug": "telephone-prototype-1876-replica",
                "description": "Working replica of the original electromagnetic telephone. Two units connected by wire. Speak into one, listen on the other. The sound quality is terrible by modern standards. But the first time you hear a voice come through that wire, you'll understand why I shouted for Watson.",
                "item_type": "physical",
                "category": "electronics",
                "listings": [{"listing_type": "rent", "price": 12.0, "price_unit": "per_day", "currency": "EUR", "deposit": 60.0}]
            },
            {
                "name": "Acoustics & Sound Science Workshop",
                "slug": "acoustics-sound-science-workshop",
                "description": "Two-hour hands-on session. We'll build a simple acoustic device, learn about frequency, amplitude, resonance, and why your voice sounds different on a recording. Tip: Sound is just vibration. If you understand vibration, you understand everything from music to earthquakes to how dolphins navigate.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Sign Language & Communication Tutoring",
                "slug": "sign-language-communication-tutoring",
                "description": "One-on-one tutoring in communication methods for the deaf and hard of hearing. My father's Visible Speech system, basic sign language, lip reading techniques. My mother couldn't hear me speak, but she could feel the vibrations of my voice through her hand on my throat. Communication finds a way.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Tuning Fork Set (Scientific Grade, 8-Piece)",
                "slug": "tuning-fork-set-scientific-8pc",
                "description": "Eight precision tuning forks covering one full octave. Essential for acoustics experiments, hearing tests, and understanding resonance. Strike one near a piano and watch the matching string vibrate in sympathy. That's how the telephone works -- sympathetic vibration converted to electrical signal.",
                "item_type": "physical",
                "category": "electronics",
                "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR", "deposit": 25.0}]
            },
            {
                "name": "Public Speaking Masterclass -- Voice & Persuasion",
                "slug": "public-speaking-voice-persuasion",
                "description": "Small group (max 6). I spent my life studying the human voice -- how it works, how it persuades, how it fails. I'll teach you projection, pacing, and the one trick that separates a good speaker from a great one: silence. The pause before the point is more powerful than the point itself.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # 3. ORVILLE WRIGHT (1871-1948)
    # ============================================================
    {
        "slug": "orvilles-wind-tunnel",
        "display_name": "Orville Wright",
        "email": "orville@borrowhood.local",
        "date_of_birth": "1871-08-19",
        "mother_name": "Susan Catherine Koerner",
        "father_name": "Milton Wright",
        "workshop_name": "Orville's Wind Tunnel Workshop",
        "workshop_type": "workshop",
        "tagline": "If we worked on the assumption that what is accepted as true really is true, there would be little hope for advance",
        "bio": "Born in Dayton, Ohio. Never graduated high school. Neither did Wilbur. We ran a bicycle shop -- the Wright Cycle Company. Bicycles taught us everything we needed: balance, lightweight structures, chain-driven mechanisms. On December 17, 1903, at Kitty Hawk, I flew for 12 seconds. 120 feet. The entire distance was shorter than a modern Boeing 747. Wilbur and I built our own wind tunnel from a starch box and a fan. We tested over 200 wing shapes. Everyone else was guessing. We measured. Tip: Build the test rig before you build the thing. Langley had government funding and a catapult. We had a bicycle shop and a headwind. We won because we tested more and assumed less.",
        "telegram_username": "wright_flyer",
        "city": "Dayton",
        "country_code": "US",
        "latitude": 39.758,
        "longitude": -84.192,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Aeronautics", "category": "engineering", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Wind Tunnel Testing", "category": "engineering", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Bicycle Mechanics", "category": "tools", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Woodworking", "category": "tools", "self_rating": 4, "years_experience": 25}
        ],
        "social_links": [],
        "points": {"total_points": 2100, "rentals_completed": 55, "reviews_given": 40, "reviews_received": 65, "items_listed": 7, "helpful_flags": 38},
        "offers_training": True,
        "items": [
            {
                "name": "Wind Tunnel (Tabletop, Educational Model)",
                "slug": "wind-tunnel-tabletop-educational",
                "description": "Scaled replica of the wind tunnel Wilbur and I built from a starch box. Test wing shapes, measure lift and drag. We tested 200 airfoils in two months with a rig like this. Every aircraft flying today traces back to data from this box. Includes smoke wand for flow visualization.",
                "item_type": "physical",
                "category": "engineering",
                "listings": [{"listing_type": "rent", "price": 15.0, "price_unit": "per_day", "currency": "EUR", "deposit": 75.0}]
            },
            {
                "name": "Aerodynamics Workshop -- Why Things Fly",
                "slug": "aerodynamics-workshop-why-things-fly",
                "description": "Hands-on session. We'll build and test paper gliders, balsa models, and wing sections. You'll learn Bernoulli's principle the way it actually works (not the oversimplified textbook version). Tip: Lift isn't magic. It's geometry plus airspeed. Get the angle of attack wrong and the wing stalls. I learned that at Kitty Hawk in ways that bruised.",
                "item_type": "service",
                "category": "engineering",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Bicycle Repair & Mechanics Clinic",
                "slug": "bicycle-repair-mechanics-clinic",
                "description": "Bring your bicycle. We'll strip it down and rebuild it together. Chains, gears, bearings, brakes, wheel truing. The bicycle is the most efficient machine ever built -- more miles per calorie than any vehicle. Wilbur and I ran a bike shop for a decade before we ever touched an airplane. The skills transfer perfectly.",
                "item_type": "service",
                "category": "tools",
                "listings": [{"listing_type": "service", "price": 12.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Model Aircraft Kit (Balsa Wood, Rubber Band Powered)",
                "slug": "model-aircraft-kit-balsa-rubber",
                "description": "Complete balsa wood kit to build a flying model aircraft. Rubber band motor, tissue covering, adjustable tail surfaces. Takes about 4 hours to build, flies for 30-45 seconds. It's the same principle as the Flyer -- just smaller and less terrifying.",
                "item_type": "physical",
                "category": "engineering",
                "listings": [{"listing_type": "offer", "price": 8.0, "price_unit": "per_unit", "currency": "EUR"}]
            },
            {
                "name": "Prototyping Workshop -- Test Before You Build",
                "slug": "prototyping-workshop-test-before-build",
                "description": "Small group (max 4). Bring your design idea. We'll build a quick scale model and test it. The Wright method: never build the full-size version until the model works. Langley spent $50,000 of government money and his aircraft crashed into the Potomac. We spent under $1,000 and flew. The difference was testing.",
                "item_type": "service",
                "category": "engineering",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # 4. WILBUR WRIGHT (1867-1912)
    # ============================================================
    {
        "slug": "wilburs-drafting-room",
        "display_name": "Wilbur Wright",
        "email": "wilbur@borrowhood.local",
        "date_of_birth": "1867-04-16",
        "mother_name": "Susan Catherine Koerner",
        "father_name": "Milton Wright",
        "workshop_name": "Wilbur's Drafting & Design Room",
        "workshop_type": "workshop",
        "tagline": "It is possible to fly without motors, but not without knowledge and skill",
        "bio": "Born in Millville, Indiana. I was the quiet one. Orville was the optimist. I was the one who stayed up until 3am checking the math. A hockey stick to the face at 18 knocked out my front teeth and killed my plans for Yale. Instead, I read. Everything. Lilienthal, Chanute, Langley, Cayley -- every paper on flight ever written. I found errors in Lilienthal's lift tables. Published data, accepted for decades, and it was wrong. We had to start from scratch with our own wind tunnel. Tip: Never trust published data without verifying it yourself. The experts had the wrong numbers for 30 years and nobody checked. Wing warping -- my idea. I watched a twisted bicycle tube box and saw how you could control roll. Three-axis control: pitch, roll, yaw. That's what nobody else had figured out.",
        "telegram_username": "wing_warper",
        "city": "Millville",
        "country_code": "US",
        "latitude": 39.988,
        "longitude": -85.397,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Aeronautical Engineering", "category": "engineering", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Technical Drawing", "category": "tools", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Data Analysis", "category": "education", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Research Methodology", "category": "education", "self_rating": 5, "years_experience": 20}
        ],
        "social_links": [],
        "points": {"total_points": 2050, "rentals_completed": 52, "reviews_given": 42, "reviews_received": 62, "items_listed": 7, "helpful_flags": 36},
        "offers_training": True,
        "items": [
            {
                "name": "Technical Drawing & Drafting Workshop",
                "slug": "technical-drawing-drafting-workshop",
                "description": "Learn to draw precise engineering plans by hand. T-square, compass, protractor, French curves. Before CAD, this is how every machine was designed. I drew every component of the 1903 Flyer by hand, to scale. If you can draw it accurately, you can build it accurately. If you can't draw it, you don't understand it well enough.",
                "item_type": "service",
                "category": "tools",
                "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Drafting Table & Instrument Set (Professional)",
                "slug": "drafting-table-instrument-set-pro",
                "description": "Full-size drafting table with parallel rule, plus a complete set of drawing instruments: compasses, dividers, ruling pens, French curves, triangles. The same setup I used to design the Flyer. Everything fits in a leather roll for transport.",
                "item_type": "physical",
                "category": "tools",
                "listings": [{"listing_type": "rent", "price": 8.0, "price_unit": "per_day", "currency": "EUR", "deposit": 40.0}]
            },
            {
                "name": "Research Methods Seminar -- How to Verify Anything",
                "slug": "research-methods-verify-anything",
                "description": "Small group (max 4). I'll teach you how to read a scientific paper critically, spot flawed data, and design your own verification experiments. Lilienthal's lift tables were wrong. Smeaton's coefficient was wrong. Published, peer-reviewed, cited for decades -- and wrong. If Orville and I had trusted the experts, we'd still be in the bicycle shop.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Kite Building Workshop -- Control Surfaces",
                "slug": "kite-building-control-surfaces",
                "description": "Build a biplane kite with working control surfaces. We tested our wing-warping concept on kites before we ever risked our necks in a glider. You'll learn about roll, pitch, and yaw -- the three axes that every pilot controls. Also great fun on a windy beach.",
                "item_type": "service",
                "category": "engineering",
                "listings": [{"listing_type": "training", "price": 12.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Chanute-Wright Correspondence (Facsimile Collection)",
                "slug": "chanute-wright-correspondence-facsimile",
                "description": "Bound facsimile of the correspondence between Octave Chanute and the Wright brothers, 1900-1910. Hundreds of letters detailing every step of our research. This is how engineering was done before email. Read it and learn how to ask the right questions of the right people.",
                "item_type": "physical",
                "category": "education",
                "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # 5. MARIE CURIE (1867-1934)
    # ============================================================
    {
        "slug": "curies-radiation-lab",
        "display_name": "Marie Sklodowska Curie",
        "email": "curie@borrowhood.local",
        "date_of_birth": "1867-11-07",
        "mother_name": "Bronislawa Sklodowska",
        "father_name": "Wladyslaw Sklodowski",
        "workshop_name": "Curie's Radiation Laboratory",
        "workshop_type": "laboratory",
        "tagline": "Nothing in life is to be feared, it is only to be understood",
        "bio": "Born Maria Sklodowska in Warsaw, Poland, under Russian occupation. Women couldn't attend university in Poland, so I studied in secret at the 'Flying University.' Moved to Paris at 24 with almost nothing. Lived in a freezing garret, sometimes too poor to eat. Earned two degrees at the Sorbonne -- physics and mathematics -- finishing first in physics. Married Pierre Curie, a brilliant physicist in his own right. Together we discovered polonium (named for my homeland) and radium. First woman to win a Nobel Prize. First person to win two Nobel Prizes, in two different sciences. Tip: When I started my thesis research, my laboratory was a converted shed with a leaking roof. Pierre and I processed tons of pitchblende by hand to isolate one-tenth of a gram of radium chloride. Persistence is not glamorous. It is shoveling ore in a drafty shed for four years. My notebooks are still radioactive. They will be for another 1,500 years.",
        "telegram_username": "madame_curie",
        "city": "Warsaw",
        "country_code": "PL",
        "latitude": 52.230,
        "longitude": 21.012,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "pl", "proficiency": "native"},
            {"language_code": "fr", "proficiency": "native"},
            {"language_code": "ru", "proficiency": "fluent"},
            {"language_code": "de", "proficiency": "conversational"}
        ],
        "skills": [
            {"skill_name": "Radiochemistry", "category": "science", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Physics", "category": "science", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Laboratory Technique", "category": "science", "self_rating": 5, "years_experience": 35},
            {"skill_name": "X-Ray Technology", "category": "science", "self_rating": 5, "years_experience": 20}
        ],
        "social_links": [],
        "points": {"total_points": 2800, "rentals_completed": 70, "reviews_given": 55, "reviews_received": 85, "items_listed": 10, "helpful_flags": 50},
        "offers_training": True,
        "items": [
            {
                "name": "Radiation Science Workshop -- Safely Understanding Radioactivity",
                "slug": "radiation-science-workshop-safe",
                "description": "Two-hour session with safe demonstration materials. Cloud chambers to see particle tracks, Geiger counters to measure background radiation, mineral samples that glow under UV. You'll understand alpha, beta, and gamma radiation and why each behaves differently. Tip: Radioactivity is natural. You're surrounded by it. The banana you ate this morning was radioactive. Fear comes from ignorance. Understanding comes from measurement.",
                "item_type": "service",
                "category": "science",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Geiger Counter (Professional Grade, Calibrated)",
                "slug": "geiger-counter-professional-calibrated",
                "description": "Professional-grade Geiger-Muller counter, recently calibrated. Detects alpha, beta, and gamma radiation. Includes headphones for the characteristic clicking sound. When Pierre and I first heard the clicks from our radium sample, we knew we had something the world had never seen.",
                "item_type": "physical",
                "category": "science",
                "listings": [{"listing_type": "rent", "price": 15.0, "price_unit": "per_day", "currency": "EUR", "deposit": 100.0}]
            },
            {
                "name": "Chemistry Lab Fundamentals -- Precision & Safety",
                "slug": "chemistry-lab-fundamentals-precision",
                "description": "Small group (max 4). Proper lab technique: titration, crystallization, fractional precipitation, safe handling of chemicals. I'll teach you the way I learned at the Sorbonne -- hands on, precise, no shortcuts. You will weigh to four decimal places. You will label every beaker. You will keep a proper lab notebook. Sloppiness in a lab kills people. I should know.",
                "item_type": "service",
                "category": "science",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Cloud Chamber (Wilson Type, Desktop)",
                "slug": "cloud-chamber-wilson-desktop",
                "description": "Desktop cloud chamber that makes radioactive particle tracks visible. Pour in isopropyl alcohol, cool the base, and watch cosmic rays and natural radiation leave vapor trails in real time. It's like seeing the invisible forces that pass through your body every second. Mesmerizing and educational.",
                "item_type": "physical",
                "category": "science",
                "listings": [{"listing_type": "rent", "price": 10.0, "price_unit": "per_day", "currency": "EUR", "deposit": 50.0}]
            },
            {
                "name": "Women in Science Mentoring -- Breaking Through",
                "slug": "women-in-science-mentoring-session",
                "description": "One-on-one mentoring for women and girls pursuing science. When I applied for a lab position, I was told there was no room for a woman. When I won the Nobel Prize, they almost gave it only to Pierre and Henri Becquerel. Pierre insisted my name be included. Find allies. Document everything. Let the work speak. The work always speaks loudest.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 0.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # 6. GALILEO GALILEI (1564-1642)
    # ============================================================
    {
        "slug": "galileos-observatory",
        "display_name": "Galileo Galilei",
        "email": "galileo@borrowhood.local",
        "date_of_birth": "1564-02-15",
        "mother_name": "Giulia Ammannati",
        "father_name": "Vincenzo Galilei",
        "workshop_name": "Galileo's Observatory & Workshop",
        "workshop_type": "observatory",
        "tagline": "E pur si muove -- And yet it moves",
        "bio": "Born in Pisa, Italy. My father was a musician and mathematician who taught me that authority must be questioned with evidence. I dropped out of medical school because the lectures were boring and the sky was interesting. Built my first telescope at 45 -- not invented it, improved it. Pointed it at Jupiter and saw four moons orbiting. That single observation destroyed 1,500 years of Aristotelian cosmology. The Earth is not the center. The Church put me on trial. I recanted under threat of torture. They say I muttered 'And yet it moves' as I left the courtroom. Tip: Measure everything. Time a pendulum with your pulse. Roll balls down inclined planes and count. Nature doesn't lie, but authorities do. My friend Kepler understood. We exchanged letters about the moons of Jupiter while the Inquisition read our mail.",
        "telegram_username": "stargazer_pisa",
        "city": "Pisa",
        "country_code": "IT",
        "latitude": 43.723,
        "longitude": 10.397,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "it", "proficiency": "native"},
            {"language_code": "la", "proficiency": "fluent"}
        ],
        "skills": [
            {"skill_name": "Astronomy", "category": "science", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Telescope Making", "category": "tools", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Physics", "category": "science", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Scientific Method", "category": "education", "self_rating": 5, "years_experience": 45}
        ],
        "social_links": [],
        "points": {"total_points": 2600, "rentals_completed": 68, "reviews_given": 48, "reviews_received": 80, "items_listed": 8, "helpful_flags": 44},
        "offers_training": True,
        "items": [
            {
                "name": "Telescope (Galilean Refractor, Brass, 20x)",
                "slug": "telescope-galilean-refractor-brass-20x",
                "description": "Brass refractor telescope, 20x magnification -- same power as the one I used to discover Jupiter's moons. Two lenses in a tube. Simple, elegant, world-changing. Point it at Jupiter on a clear night. You'll see the four Galilean moons. Then you'll understand why the Church was afraid.",
                "item_type": "physical",
                "category": "science",
                "listings": [{"listing_type": "rent", "price": 12.0, "price_unit": "per_day", "currency": "EUR", "deposit": 60.0}]
            },
            {
                "name": "Astronomy Night -- Planets, Moons & Stars",
                "slug": "astronomy-night-planets-moons-stars",
                "description": "Evening observation session (weather permitting). I'll show you Jupiter's moons, Saturn's rings, the craters of our Moon, and the phases of Venus. Bring warm clothes. Tip: Your eyes need 20 minutes to adapt to the dark. No phone screens. Learn the constellations first, then use the telescope. Context before magnification.",
                "item_type": "service",
                "category": "science",
                "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Scientific Method Workshop -- Question Everything",
                "slug": "scientific-method-workshop-question",
                "description": "Small group (max 6). Hands-on experiments: pendulums, inclined planes, falling objects. We'll replicate my actual experiments from the 1600s. You'll learn to form hypotheses, design experiments, collect data, and draw conclusions. Aristotle said heavy objects fall faster than light ones. I proved him wrong. You'll prove him wrong too, with your own hands.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Lens Grinding Kit (Optical, Beginner)",
                "slug": "lens-grinding-kit-optical-beginner",
                "description": "Everything you need to grind and polish your own optical lens. Glass blanks, grinding compounds, polishing pitch, a simple grinding jig. I ground my own lenses in Padua. It takes patience and steady hands. The reward is a lens that you made, that sees what no human eye can see alone.",
                "item_type": "physical",
                "category": "tools",
                "listings": [{"listing_type": "rent", "price": 8.0, "price_unit": "per_day", "currency": "EUR", "deposit": 35.0}]
            },
            {
                "name": "Physics Tutoring -- Motion, Gravity & Forces",
                "slug": "physics-tutoring-motion-gravity-forces",
                "description": "One-on-one tutoring in classical mechanics. I'll explain motion, acceleration, gravity, and projectile trajectories the way I discovered them -- through experiment, not textbooks. We'll use inclined planes, pendulums, and water clocks. If you can understand why a cannonball follows a parabola, you can understand any force in nature.",
                "item_type": "service",
                "category": "science",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # 7. JOHANNES GUTENBERG (1400-1468)
    # ============================================================
    {
        "slug": "gutenbergs-print-shop",
        "display_name": "Johannes Gutenberg",
        "email": "gutenberg@borrowhood.local",
        "date_of_birth": "1400-01-01",
        "mother_name": "Else Wyrich",
        "father_name": "Friele Gensfleisch zur Laden",
        "workshop_name": "Gutenberg's Print Shop",
        "workshop_type": "workshop",
        "tagline": "God suffers in the multitude of souls whom His word can not reach -- religious truth is imprisoned in a small number of manuscript books",
        "bio": "Born Johannes Gensfleisch zur Laden zum Gutenberg in Mainz, Germany. My family were patricians who worked the ecclesiastical mint -- I grew up around metalwork, presses, and precision. The printing press wasn't one invention. It was six: movable type, oil-based ink, the hand mould for casting type, a type metal alloy (lead-tin-antimony), an adapted wooden screw press, and a method for aligning text in justified columns. Each piece existed separately. I combined them. The Gutenberg Bible, 1455. 180 copies. It took three years to print what would have taken a scribe 20 years to copy once. Tip: The real invention is the system, not any single part. Johann Fust, my financier, sued me and took my press. I died poor. Fust got rich. Protect your business relationships as carefully as your inventions. Ask Edison about Tesla.",
        "telegram_username": "movable_type",
        "city": "Mainz",
        "country_code": "DE",
        "latitude": 50.000,
        "longitude": 8.271,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "de", "proficiency": "native"},
            {"language_code": "la", "proficiency": "fluent"}
        ],
        "skills": [
            {"skill_name": "Letterpress Printing", "category": "tools", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Metalworking", "category": "tools", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Typography", "category": "art", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Ink Making", "category": "tools", "self_rating": 5, "years_experience": 25}
        ],
        "social_links": [],
        "points": {"total_points": 2500, "rentals_completed": 62, "reviews_given": 46, "reviews_received": 78, "items_listed": 8, "helpful_flags": 42},
        "offers_training": True,
        "items": [
            {
                "name": "Letterpress Printing Workshop -- Set Type, Pull Prints",
                "slug": "letterpress-workshop-set-type-pull",
                "description": "Hands-on letterpress session. Pick individual lead type from the case, compose a line, lock it in the chase, ink the form, and pull a print. You'll leave with a hand-printed broadside. Tip: Set type mirror-image, left to right becomes right to left. The first time everyone gets it backwards. That's why we call it 'mind your p's and q's' -- they're mirror images in the type case.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Tabletop Printing Press (Working Replica)",
                "slug": "tabletop-printing-press-replica",
                "description": "Working replica of a 15th-century screw press, scaled to tabletop size. Wooden frame, iron screw, leather ink balls. Comes with a starter set of lead type (Textura blackletter) and oil-based ink. Print your own pages. The same mechanism that ended the Dark Ages, now in your kitchen.",
                "item_type": "physical",
                "category": "tools",
                "listings": [{"listing_type": "rent", "price": 18.0, "price_unit": "per_day", "currency": "EUR", "deposit": 90.0}]
            },
            {
                "name": "Typography & Book Design Masterclass",
                "slug": "typography-book-design-masterclass",
                "description": "Small group (max 4). Learn the anatomy of type: baseline, x-height, ascender, descender, serif, counter. Learn leading, kerning, and justification. I'll show you why the Gutenberg Bible is still considered one of the most beautiful printed books 570 years later. Spoiler: it's the margins.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Lead Type Set (Textura Blackletter, Complete Alphabet)",
                "slug": "lead-type-set-textura-blackletter",
                "description": "Complete alphabet in Textura blackletter -- the typeface of the Gutenberg Bible. Upper and lower case, numbers, punctuation. Cast in traditional type metal (lead-tin-antimony). Each piece hand-finished. Handle with care; lead is toxic. Wash your hands after use. I didn't know that part.",
                "item_type": "physical",
                "category": "tools",
                "listings": [{"listing_type": "rent", "price": 10.0, "price_unit": "per_day", "currency": "EUR", "deposit": 50.0}]
            },
            {
                "name": "Ink Making Workshop -- Oil-Based, From Scratch",
                "slug": "ink-making-workshop-oil-based",
                "description": "Make your own oil-based printing ink from linseed oil, soot, and pigments. Water-based ink was fine for stamps but terrible for type -- it beaded up on metal. I had to invent a new ink. You'll leave with a jar of ink good enough to print with. Wear old clothes.",
                "item_type": "service",
                "category": "tools",
                "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # 8. JAMES WATT (1736-1819)
    # ============================================================
    {
        "slug": "watts-engine-house",
        "display_name": "James Watt",
        "email": "watt@borrowhood.local",
        "date_of_birth": "1736-01-19",
        "mother_name": "Agnes Muirhead",
        "father_name": "James Watt Sr.",
        "workshop_name": "Watt's Engine House",
        "workshop_type": "workshop",
        "tagline": "I can think of nothing else but this machine",
        "bio": "Born in Greenock, Scotland. Sickly child. My mother taught me to read, my father taught me to use tools. I was instrument maker to the University of Glasgow when they gave me a broken Newcomen steam engine to repair. I fixed it. Then I realized how terrible the design was -- it wasted three-quarters of its steam. The separate condenser was my breakthrough. Keep the cylinder hot, keep the condenser cold. Simple idea, took me years to make it work. My partnership with Matthew Boulton saved me. I was the engineer, he was the businessman. 'I sell here, sir, what all the world desires to have: power.' Tip: An invention without a business partner is a hobby. Boulton had the factory, the capital, and the customers. I had the engine. Together we powered the Industrial Revolution. Horsepower? I defined it. Watt? They named the unit of power after me. Not bad for a sickly boy from Greenock.",
        "telegram_username": "steam_power",
        "city": "Greenock",
        "country_code": "GB",
        "latitude": 55.946,
        "longitude": -4.764,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Steam Engineering", "category": "engineering", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Instrument Making", "category": "tools", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Mechanical Design", "category": "engineering", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Thermodynamics", "category": "science", "self_rating": 5, "years_experience": 40}
        ],
        "social_links": [],
        "points": {"total_points": 2300, "rentals_completed": 58, "reviews_given": 44, "reviews_received": 72, "items_listed": 8, "helpful_flags": 40},
        "offers_training": True,
        "items": [
            {
                "name": "Steam Engine Model (Working, Watt Type with Separate Condenser)",
                "slug": "steam-engine-model-watt-condenser",
                "description": "Working model of my improved steam engine with separate condenser. Brass and steel, spirit-fired boiler, governor mechanism. Watch it run and understand why the Industrial Revolution happened. The separate condenser is the key -- you can see the cylinder stays hot while the condenser stays cold. That's a 75% efficiency improvement over Newcomen.",
                "item_type": "physical",
                "category": "engineering",
                "listings": [{"listing_type": "rent", "price": 20.0, "price_unit": "per_day", "currency": "EUR", "deposit": 100.0}]
            },
            {
                "name": "Thermodynamics Workshop -- Heat, Work & Efficiency",
                "slug": "thermodynamics-workshop-heat-work",
                "description": "Hands-on session with steam models, thermometers, and pressure gauges. You'll learn the relationship between heat, pressure, volume, and work. Why does steam push a piston? Why does a condenser improve efficiency? Why can't you build a perpetual motion machine? Tip: Energy is never created or destroyed, only converted. The trick is converting more of it into useful work and less into waste heat.",
                "item_type": "service",
                "category": "science",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Precision Instrument Making -- Measure Twice, Cut Once",
                "slug": "precision-instrument-making-workshop",
                "description": "Small group (max 3). Build a simple scientific instrument from scratch: a barometer, a micrometer, or a beam balance. Metalwork, filing, fitting, calibration. I was instrument maker at Glasgow University. The difference between a tool and a precision instrument is the care in the finishing. A thousandth of an inch matters.",
                "item_type": "service",
                "category": "tools",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Machinist's Tool Set (Watchmaker Grade)",
                "slug": "machinists-tool-set-watchmaker-grade",
                "description": "Complete set of precision hand tools: files (Swiss-cut, 6 grades), small lathework tools, calipers, micrometers, taps and dies. The same quality I used to build instruments for Joseph Black's chemistry experiments. Keep them oiled. Return them sharper than you found them.",
                "item_type": "physical",
                "category": "tools",
                "listings": [{"listing_type": "rent", "price": 10.0, "price_unit": "per_day", "currency": "EUR", "deposit": 60.0}]
            },
            {
                "name": "Engineering Mentoring -- From Idea to Industry",
                "slug": "engineering-mentoring-idea-to-industry",
                "description": "One-on-one sessions for aspiring engineers. I'll help you refine your mechanical design, calculate stresses and tolerances, and -- most importantly -- find your Matthew Boulton. The greatest engine in the world is worthless without someone to sell it. I was nearly bankrupt before Boulton. Technical genius plus business sense equals the Industrial Revolution.",
                "item_type": "service",
                "category": "engineering",
                "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # 9. BENJAMIN FRANKLIN (1706-1790)
    # ============================================================
    {
        "slug": "franklins-printing-house",
        "display_name": "Benjamin Franklin",
        "email": "franklin@borrowhood.local",
        "date_of_birth": "1706-01-17",
        "mother_name": "Abiah Folger",
        "father_name": "Josiah Franklin",
        "workshop_name": "Franklin's Printing House & Laboratory",
        "workshop_type": "laboratory",
        "tagline": "An investment in knowledge pays the best interest",
        "bio": "Born in Boston, tenth son of a soap maker with 17 children. Left school at 10. Apprenticed to my brother's print shop at 12. Ran away to Philadelphia at 17 with one Dutch dollar and a copper shilling. Built a printing empire, founded the first lending library, the first volunteer fire department, the University of Pennsylvania, and the American Philosophical Society. Then I got bored and started doing science. The kite experiment -- yes, I really did it, and yes, it was stupid and dangerous. I invented the lightning rod, bifocal glasses, the Franklin stove, the glass armonica, and the flexible urinary catheter (you're welcome). Tip: Never stop being curious. I was 70 when I helped draft the Declaration of Independence, 81 at the Constitutional Convention. My friend Voltaire and I embraced publicly in Paris. Two old troublemakers. I also helped fund Gutenberg-style printing in America. The press is the people's weapon.",
        "telegram_username": "poor_richard",
        "city": "Boston",
        "country_code": "US",
        "latitude": 42.360,
        "longitude": -71.059,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "fr", "proficiency": "fluent"}
        ],
        "skills": [
            {"skill_name": "Electrical Science", "category": "science", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Printing", "category": "tools", "self_rating": 5, "years_experience": 60},
            {"skill_name": "Diplomacy", "category": "education", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Invention", "category": "tools", "self_rating": 5, "years_experience": 55}
        ],
        "social_links": [],
        "points": {"total_points": 2700, "rentals_completed": 72, "reviews_given": 52, "reviews_received": 82, "items_listed": 10, "helpful_flags": 48},
        "offers_training": True,
        "items": [
            {
                "name": "Electricity Demonstration -- Kite, Key & Leyden Jar",
                "slug": "electricity-demo-kite-key-leyden",
                "description": "Safe indoor demonstration of static electricity, Leyden jars, and electrical conduction. We will NOT be flying kites in thunderstorms. I did that once and it was phenomenally reckless. Instead, we'll use friction machines and Leyden jars to generate sparks, charge objects, and understand positive vs negative charge. I named those, by the way.",
                "item_type": "service",
                "category": "science",
                "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Glass Armonica (Working Replica, 37 Bowls)",
                "slug": "glass-armonica-replica-37-bowls",
                "description": "My most beautiful invention. 37 glass bowls mounted on a spindle, turned by a foot pedal, played with wet fingers. Mozart and Beethoven both composed for it. The sound is unearthly -- people fainted at performances. Some thought it caused madness. It doesn't. It causes wonder. Handle with extreme care.",
                "item_type": "physical",
                "category": "music",
                "listings": [{"listing_type": "rent", "price": 25.0, "price_unit": "per_day", "currency": "EUR", "deposit": 150.0}]
            },
            {
                "name": "Bifocal Lens Demonstration & Fitting",
                "slug": "bifocal-lens-demo-fitting",
                "description": "I got tired of switching between two pairs of glasses -- one for reading, one for distance. So I cut the lenses in half and combined them. Revolutionary? No. Practical? Enormously. This workshop covers basic optics, lens grinding principles, and why bifocals work. Tip: The best inventions solve annoyances, not emergencies.",
                "item_type": "service",
                "category": "science",
                "listings": [{"listing_type": "training", "price": 12.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Franklin Stove (Cast Iron, Working Replica)",
                "slug": "franklin-stove-cast-iron-replica",
                "description": "Cast iron replica of the Pennsylvania Fireplace. More efficient than an open fireplace -- the baffle system circulates warm air into the room instead of up the chimney. I refused to patent it. Some things should be free. The Governor of Pennsylvania offered me a patent; I said no. Heat is a public good.",
                "item_type": "physical",
                "category": "tools",
                "listings": [{"listing_type": "rent", "price": 15.0, "price_unit": "per_day", "currency": "EUR", "deposit": 75.0}]
            },
            {
                "name": "Writing & Persuasion Workshop -- Poor Richard's Method",
                "slug": "writing-persuasion-poor-richards-method",
                "description": "Small group (max 6). I'll teach you how to write clearly, persuade effectively, and publish for maximum impact. I wrote Poor Richard's Almanack for 25 years. Sold 10,000 copies a year. 'Early to bed and early to rise' -- that's mine. 'A penny saved is a penny earned' -- also mine. Short, memorable, useful. That's the formula.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # 10. ALBERT EINSTEIN (1879-1955)
    # ============================================================
    {
        "slug": "einsteins-thought-lab",
        "display_name": "Albert Einstein",
        "email": "einstein@borrowhood.local",
        "date_of_birth": "1879-03-14",
        "mother_name": "Pauline Koch",
        "father_name": "Hermann Einstein",
        "workshop_name": "Einstein's Thought Experiment Laboratory",
        "workshop_type": "study",
        "tagline": "Imagination is more important than knowledge",
        "bio": "Born in Ulm, Germany. Failed to get an academic position after university. Worked as a patent clerk in Bern, Switzerland. In 1905, while examining other people's inventions at the patent office, I published four papers that changed physics: the photoelectric effect, Brownian motion, special relativity, and mass-energy equivalence. E equals mc squared. All four papers, in one year, while working full time at a desk job. They called it the Annus Mirabilis. Tip: The patent office was the best thing that happened to me. No academic pressure, no department politics, plenty of time to think. My best ideas came from thought experiments -- riding a beam of light, dropping an elevator, watching clocks from a moving train. You don't need a laboratory. You need a quiet room and a willingness to follow an idea to its logical conclusion, no matter how strange. My friend Marcel Grossmann helped me with the tensor mathematics for general relativity. Find a friend who is better at math than you.",
        "telegram_username": "patent_clerk",
        "city": "Ulm",
        "country_code": "DE",
        "latitude": 48.401,
        "longitude": 9.988,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "de", "proficiency": "native"},
            {"language_code": "en", "proficiency": "fluent"},
            {"language_code": "fr", "proficiency": "conversational"},
            {"language_code": "it", "proficiency": "conversational"}
        ],
        "skills": [
            {"skill_name": "Theoretical Physics", "category": "science", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Mathematics", "category": "science", "self_rating": 4, "years_experience": 50},
            {"skill_name": "Thought Experiments", "category": "education", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Violin", "category": "music", "self_rating": 3, "years_experience": 45}
        ],
        "social_links": [],
        "points": {"total_points": 3000, "rentals_completed": 80, "reviews_given": 60, "reviews_received": 90, "items_listed": 8, "helpful_flags": 55},
        "offers_training": True,
        "items": [
            {
                "name": "Relativity Explained -- Thought Experiments for Everyone",
                "slug": "relativity-explained-thought-experiments",
                "description": "Two-hour session. No equations (well, one equation). I'll explain special and general relativity using the same thought experiments I used to discover them. Riding a beam of light. Trains and lightning strikes. Falling elevators. If you can imagine it, you can understand it. Tip: Relativity is not abstract. Your GPS uses it. Without relativistic corrections, your navigation would be off by 10 kilometers per day.",
                "item_type": "service",
                "category": "science",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Violin (German Make, 1920s, Concert Quality)",
                "slug": "violin-german-1920s-concert",
                "description": "My violin. Well, a replica of my favorite one. I named the original Lina. Mozart and Bach -- that's what I play when I'm stuck on a physics problem. The music reorganizes my thinking. If you can play, borrow it. If you can't, I'll give you a beginner lesson. Badly. I'm a better physicist than violinist.",
                "item_type": "physical",
                "category": "music",
                "listings": [{"listing_type": "rent", "price": 8.0, "price_unit": "per_day", "currency": "EUR", "deposit": 40.0}]
            },
            {
                "name": "Physics Problem-Solving Tutoring",
                "slug": "physics-problem-solving-tutoring",
                "description": "One-on-one tutoring in physics. Any level, any topic. I spent 10 years as a professor. The secret to teaching physics is this: never start with the formula. Start with the question. Why does this happen? What would you expect? Now let's check. The formula is just the shorthand for the understanding.",
                "item_type": "service",
                "category": "science",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Compass (Pocket, Brass -- Like the One That Started It All)",
                "slug": "compass-pocket-brass-einstein",
                "description": "Brass pocket compass. When I was five years old, my father showed me a compass. The needle moved without being touched. Something invisible was acting on it. That moment -- the mystery of the invisible force -- started everything. Give this to a curious child and watch what happens.",
                "item_type": "physical",
                "category": "science",
                "listings": [{"listing_type": "offer", "price": 6.0, "price_unit": "per_unit", "currency": "EUR"}]
            },
            {
                "name": "Creative Thinking Workshop -- The Patent Clerk Method",
                "slug": "creative-thinking-patent-clerk-method",
                "description": "Small group (max 5). I'll teach you how to do thought experiments: isolate a problem, strip it to essentials, follow the logic to impossible conclusions, then ask why they're impossible. This is how I found special relativity. This is how you solve any problem where the conventional answer feels wrong. Bring a notebook. Bring a problem. Leave with a new way to think.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },

    # ============================================================
    # 11. ISAAC NEWTON (1643-1727)
    # ============================================================
    {
        "slug": "newtons-principia-study",
        "display_name": "Isaac Newton",
        "email": "newton@borrowhood.local",
        "date_of_birth": "1643-01-04",
        "mother_name": "Hannah Ayscough",
        "father_name": "Isaac Newton Sr.",
        "workshop_name": "Newton's Principia Study",
        "workshop_type": "study",
        "tagline": "If I have seen further, it is by standing on the shoulders of giants",
        "bio": "Born in Woolsthorpe, Lincolnshire, England. Premature, so small they said I could fit in a quart mug. My father died three months before I was born. My mother remarried and left me with my grandmother. I hated my stepfather. Channeled that rage into study. Cambridge sent everyone home during the plague of 1665. In those two years of isolation, I invented calculus, discovered the laws of motion, proved white light is a spectrum of colors, and began formulating universal gravitation. The apple story is mostly true -- I watched one fall and asked why it fell straight down instead of sideways or up. Tip: Isolation is productive. The world distractions are the enemy of deep thought. Leibniz claims he invented calculus independently. Perhaps. I invented it first. My Principia Mathematica is the most important scientific book ever written.",
        "telegram_username": "principia_man",
        "city": "Woolsthorpe",
        "country_code": "GB",
        "latitude": 52.808,
        "longitude": -0.617,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "la", "proficiency": "fluent"}
        ],
        "skills": [
            {"skill_name": "Mathematics", "category": "science", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Optics", "category": "science", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Physics", "category": "science", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Alchemy", "category": "science", "self_rating": 4, "years_experience": 30}
        ],
        "social_links": [],
        "points": {"total_points": 2900, "rentals_completed": 75, "reviews_given": 58, "reviews_received": 88, "items_listed": 9, "helpful_flags": 52},
        "offers_training": True,
        "items": [
            {"name": "Optics Demonstration -- Prisms, Spectra & Light", "slug": "optics-demo-prisms-spectra-light", "description": "I will demonstrate how white light splits into a spectrum through a glass prism, and how a second prism recombines it. This experiment settled a 2,000-year debate. Light is not pure -- it is a mixture of colors. Includes hands-on experiments with reflection, refraction, and Newton rings.", "item_type": "service", "category": "science", "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Glass Prism Set (Optical Grade, 3-Piece)", "slug": "glass-prism-set-optical-3pc", "description": "Three optical-grade glass prisms: equilateral, right-angle, and porro. The equilateral prism splits white light into its spectrum. I purchased mine from a fair in Stourbridge in 1666. These are considerably better quality. Handle them by the edges -- fingerprints ruin the optical surfaces.", "item_type": "physical", "category": "science", "listings": [{"listing_type": "rent", "price": 8.0, "price_unit": "per_day", "currency": "EUR", "deposit": 40.0}]},
            {"name": "Calculus Tutoring -- From First Principles", "slug": "calculus-tutoring-first-principles", "description": "One-on-one tutoring in calculus. I call it the method of fluxions. We start with rates of change and accumulation -- the two fundamental ideas. I will teach it the way I discovered it: from observing how things move, how areas grow, how curves bend. Forget memorizing formulas. Understand why the formula works.", "item_type": "service", "category": "science", "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Reflecting Telescope (Newtonian Design, 6-Inch)", "slug": "reflecting-telescope-newtonian-6inch", "description": "Six-inch Newtonian reflector telescope. My design -- a curved mirror instead of a lens. No chromatic aberration. I built the first one in 1668, grinding the mirror myself from speculum metal. This modern version uses aluminum-coated glass. Point it at Saturn.", "item_type": "physical", "category": "science", "listings": [{"listing_type": "rent", "price": 15.0, "price_unit": "per_day", "currency": "EUR", "deposit": 80.0}]},
            {"name": "Laws of Motion Workshop -- Forces & Momentum", "slug": "laws-of-motion-workshop-forces", "description": "Small group (max 5). Hands-on experiments demonstrating all three laws of motion. Newton cradle, collision carts, spring scales, inclined planes. You will measure forces, predict outcomes, and verify them. Every bridge, every car, every rocket uses these three laws.", "item_type": "service", "category": "science", "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]}
        ]
    },

    # ============================================================
    # 12. MICHAEL FARADAY (1791-1867)
    # ============================================================
    {
        "slug": "faradays-magnetic-lab",
        "display_name": "Michael Faraday",
        "email": "faraday@borrowhood.local",
        "date_of_birth": "1791-09-22",
        "mother_name": "Margaret Hastwell",
        "father_name": "James Faraday",
        "workshop_name": "Faraday's Magnetic Laboratory",
        "workshop_type": "laboratory",
        "tagline": "Nothing is too wonderful to be true, if it be consistent with the laws of nature",
        "bio": "Born in Newington Butts, London. My father was a blacksmith who could not always afford food. I had almost no formal education. Apprenticed to a bookbinder at 14 -- and read every book I bound. At 20, I attended four lectures by Sir Humphry Davy at the Royal Institution. I took meticulous notes, bound them beautifully, and sent them to Davy asking for a job. He hired me as a laboratory assistant. Within 15 years, I surpassed him. I discovered electromagnetic induction -- the principle behind every electric generator and transformer on Earth. Every time you turn on a light, that is my work. Also discovered benzene, invented the Faraday cage, and gave the first Christmas Lectures for children. Tip: You do not need a degree to do world-changing science. You need curiosity, rigor, and someone willing to give you a chance.",
        "telegram_username": "magnetic_mike",
        "city": "London",
        "country_code": "GB",
        "latitude": 51.509,
        "longitude": -0.097,
        "badge_tier": "legend",
        "languages": [{"language_code": "en", "proficiency": "native"}],
        "skills": [
            {"skill_name": "Electromagnetism", "category": "electronics", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Chemistry", "category": "science", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Science Communication", "category": "education", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Laboratory Technique", "category": "science", "self_rating": 5, "years_experience": 40}
        ],
        "social_links": [],
        "points": {"total_points": 2450, "rentals_completed": 64, "reviews_given": 48, "reviews_received": 76, "items_listed": 8, "helpful_flags": 43},
        "offers_training": True,
        "items": [
            {"name": "Electromagnetic Induction Demonstration Kit", "slug": "electromagnetic-induction-demo-kit", "description": "Magnets, copper wire coils, galvanometer, and iron rings. I will show you how moving a magnet through a coil generates electricity -- the experiment that powers civilization. On August 29, 1831, I wrapped two coils around an iron ring and discovered that changing the current in one coil induced current in the other.", "item_type": "physical", "category": "electronics", "listings": [{"listing_type": "rent", "price": 12.0, "price_unit": "per_day", "currency": "EUR", "deposit": 55.0}]},
            {"name": "Electricity & Magnetism Workshop -- Fields You Cannot See", "slug": "electricity-magnetism-workshop-fields", "description": "Hands-on session. Iron filings on paper over magnets -- watch the field lines appear. Compass needles deflected by current-carrying wires. Electromagnets lifting iron. I will explain how electricity and magnetism are two faces of the same force. James Clerk Maxwell later wrote the math. I gave him the experiments.", "item_type": "service", "category": "electronics", "listings": [{"listing_type": "training", "price": 16.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Science for Young People -- The Christmas Lecture", "slug": "science-young-people-christmas-lecture", "description": "A demonstration-rich science talk designed for children and teenagers. I started the Christmas Lectures at the Royal Institution in 1825. Fire, ice, magnets, sparks, bubbles -- real science made visceral. No equations. Just wonder. The Chemical History of a Candle -- six lectures explaining all of chemistry through a single burning candle.", "item_type": "service", "category": "education", "listings": [{"listing_type": "training", "price": 10.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Faraday Cage (Demonstration Model, Mesh)", "slug": "faraday-cage-demo-model-mesh", "description": "Tabletop Faraday cage -- a wire mesh enclosure that blocks electromagnetic fields. Put a radio inside, close the cage, the signal disappears. Open it, the signal returns. This is why your microwave oven has a mesh screen in the door.", "item_type": "physical", "category": "electronics", "listings": [{"listing_type": "rent", "price": 8.0, "price_unit": "per_day", "currency": "EUR", "deposit": 35.0}]},
            {"name": "Self-Education Mentoring -- The Bookbinder Path", "slug": "self-education-mentoring-bookbinder", "description": "One-on-one mentoring for anyone without a formal science education who wants to learn. I had no degree, no university, no connections. I had a library and a willingness to work harder than anyone in the room. I will help you build a self-study plan and find your Humphry Davy -- the person who opens the first door.", "item_type": "service", "category": "education", "listings": [{"listing_type": "training", "price": 0.0, "price_unit": "per_session", "currency": "EUR"}]}
        ]
    },

    # ============================================================
    # 13. HEDY LAMARR (1914-2000)
    # ============================================================
    {
        "slug": "lamarrs-frequency-lab",
        "display_name": "Hedy Lamarr",
        "email": "lamarr@borrowhood.local",
        "date_of_birth": "1914-11-09",
        "mother_name": "Gertrud Kiesler",
        "father_name": "Emil Kiesler",
        "workshop_name": "Lamarr's Frequency Hopping Lab",
        "workshop_type": "laboratory",
        "tagline": "Any girl can be glamorous. All you have to do is stand still and look stupid. I prefer to use my brain.",
        "bio": "Born Hedwig Eva Maria Kiesler in Vienna, Austria. My father was a bank director who explained how machines worked during our walks. I was taking apart music boxes at age five. At 18, I married Fritz Mandl, an Austrian arms dealer. He locked me in his mansion and took me to meetings with Mussolini and Hitler. I memorized everything about weapons systems and radio-controlled torpedoes. Escaped by disguising myself and fleeing to Paris, then London, then Hollywood. Became one of the biggest movie stars of the 1940s. But that was the side project. With composer George Antheil, I patented frequency-hopping spread spectrum technology. The Navy dismissed it. Decades later, it became the basis for WiFi, Bluetooth, and GPS. Tip: The people who dismiss your ideas because of what you look like are telling you about themselves, not about your ideas.",
        "telegram_username": "freq_hopper",
        "city": "Vienna",
        "country_code": "AT",
        "latitude": 48.210,
        "longitude": 16.364,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "de", "proficiency": "native"},
            {"language_code": "en", "proficiency": "fluent"},
            {"language_code": "fr", "proficiency": "conversational"}
        ],
        "skills": [
            {"skill_name": "Radio Engineering", "category": "electronics", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Frequency Spectrum", "category": "electronics", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Acting", "category": "art", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Patent Design", "category": "education", "self_rating": 4, "years_experience": 25}
        ],
        "social_links": [],
        "points": {"total_points": 2150, "rentals_completed": 56, "reviews_given": 42, "reviews_received": 68, "items_listed": 7, "helpful_flags": 38},
        "offers_training": True,
        "items": [
            {"name": "Radio & Wireless Communication Workshop", "slug": "radio-wireless-communication-workshop", "description": "Hands-on session covering radio fundamentals: frequency, amplitude, modulation, and why your WiFi works. I will explain frequency hopping with a player piano analogy -- the same concept George Antheil and I patented in 1942. You will build a simple AM radio receiver by the end.", "item_type": "service", "category": "electronics", "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "AM/FM Radio Kit (Build Your Own, Soldering Required)", "slug": "am-fm-radio-kit-build-soldering", "description": "Complete kit to build a working AM/FM radio from components. Circuit board, capacitors, resistors, coils, speaker. Soldering iron included. Takes about 3 hours. You will understand tuning, amplification, and demodulation by building them with your hands.", "item_type": "physical", "category": "electronics", "listings": [{"listing_type": "offer", "price": 12.0, "price_unit": "per_unit", "currency": "EUR"}]},
            {"name": "Invention & Reinvention Mentoring", "slug": "invention-reinvention-mentoring-lamarr", "description": "One-on-one session. I was a movie star and a weapons inventor. I escaped a fascist husband and reinvented myself three times. If you are stuck between identities, between careers, between who you were and who you want to be -- talk to me. The world will try to put you in one box. Refuse.", "item_type": "service", "category": "education", "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Spectrum Analyzer (Handheld, Educational)", "slug": "spectrum-analyzer-handheld-educational", "description": "Handheld RF spectrum analyzer. See the invisible: WiFi signals, Bluetooth, cellular, radio stations -- all visualized as peaks on a frequency display. I spent my life thinking about how radio signals move through the air. This tool lets you see what I could only imagine.", "item_type": "physical", "category": "electronics", "listings": [{"listing_type": "rent", "price": 15.0, "price_unit": "per_day", "currency": "EUR", "deposit": 70.0}]}
        ]
    },

    # ============================================================
    # 14. GEORGE WASHINGTON CARVER (1864-1943)
    # ============================================================
    {
        "slug": "carvers-plant-lab",
        "display_name": "George Washington Carver",
        "email": "carver@borrowhood.local",
        "date_of_birth": "1864-01-01",
        "mother_name": "Mary",
        "father_name": "Giles -- a slave on a neighboring farm, killed before my birth",
        "workshop_name": "Carver's Plant Laboratory",
        "workshop_type": "laboratory",
        "tagline": "When you do the common things in life in an uncommon way, you will command the attention of the world",
        "bio": "Born into slavery in Diamond, Missouri. Kidnapped as an infant with my mother by Confederate raiders. Moses Carver traded a racehorse for my return. My mother was never found. Too frail for field work, so they let me garden. Plants became my language. Denied admission to Highland College because I was Black. Eventually got to Iowa State -- first Black student, then first Black faculty member. Booker T. Washington recruited me to Tuskegee Institute. I developed 300 products from peanuts, 118 from sweet potatoes. But the real mission was teaching poor Southern farmers to rotate crops and save their soil. Cotton was destroying the land. Peanuts fixed nitrogen. Science in service of survival. Tip: The answer is always in the soil. I refused to patent most of my discoveries. Knowledge should be free for those who need it most.",
        "telegram_username": "peanut_wizard",
        "city": "Diamond",
        "country_code": "US",
        "latitude": 36.757,
        "longitude": -94.138,
        "badge_tier": "legend",
        "languages": [{"language_code": "en", "proficiency": "native"}],
        "skills": [
            {"skill_name": "Agricultural Science", "category": "science", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Botany", "category": "science", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Soil Chemistry", "category": "science", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Painting", "category": "art", "self_rating": 4, "years_experience": 40}
        ],
        "social_links": [],
        "points": {"total_points": 2350, "rentals_completed": 60, "reviews_given": 50, "reviews_received": 74, "items_listed": 8, "helpful_flags": 44},
        "offers_training": True,
        "items": [
            {"name": "Soil Science Workshop -- Read Your Dirt", "slug": "soil-science-workshop-read-dirt", "description": "Bring a soil sample from your garden. I will teach you to read it: pH, nitrogen, phosphorus, potassium, organic matter, texture. Your soil tells you what it needs. Most people guess. I measure. Tip: If your soil is dead, nothing you plant will thrive. Feed the soil, not the plant.", "item_type": "service", "category": "science", "listings": [{"listing_type": "training", "price": 12.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Crop Rotation & Companion Planting Guide", "slug": "crop-rotation-companion-planting", "description": "Hands-on session in the garden. I will show you which plants fix nitrogen, which ones deplete it, and how to rotate so your soil gets richer every year. The peanut-cotton rotation saved Southern agriculture. The same principles work in any garden, any climate.", "item_type": "service", "category": "science", "listings": [{"listing_type": "training", "price": 10.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Soil Testing Kit (Professional Grade)", "slug": "soil-testing-kit-professional-grade", "description": "Complete soil analysis kit: pH meter, NPK test reagents, color charts, sample bags, field notebook. Test up to 50 samples. I tested thousands across Alabama. Every farm was different. This kit lets you read the story your land is trying to tell you.", "item_type": "physical", "category": "science", "listings": [{"listing_type": "rent", "price": 8.0, "price_unit": "per_day", "currency": "EUR", "deposit": 35.0}]},
            {"name": "Natural Dye & Paint Making Workshop", "slug": "natural-dye-paint-making-workshop", "description": "Make paints and dyes from plants, clay, and minerals. I was an accomplished painter who made all my own pigments from Alabama clay. Red from pokeberry, yellow from goldenrod, blue from indigo. You will leave with a palette of natural colors and the knowledge to make more.", "item_type": "service", "category": "art", "listings": [{"listing_type": "training", "price": 14.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Botanical Press & Specimen Kit", "slug": "botanical-press-specimen-kit", "description": "Wooden plant press with blotting paper, corrugated cardboard, and straps. Plus mounting paper, labels, and a hand lens. I collected thousands of specimens for Tuskegee herbarium. Pressing plants is meditation. Label everything: date, location, species, habitat.", "item_type": "physical", "category": "science", "listings": [{"listing_type": "rent", "price": 6.0, "price_unit": "per_day", "currency": "EUR", "deposit": 25.0}]}
        ]
    },

    # ============================================================
    # 15. SAMUEL MORSE (1791-1872)
    # ============================================================
    {
        "slug": "morses-telegraph-office",
        "display_name": "Samuel Finley Breese Morse",
        "email": "morse@borrowhood.local",
        "date_of_birth": "1791-04-27",
        "mother_name": "Elizabeth Ann Finley Breese",
        "father_name": "Jedidiah Morse",
        "workshop_name": "Morse's Telegraph Office",
        "workshop_type": "workshop",
        "tagline": "What hath God wrought",
        "bio": "Born in Charlestown, Massachusetts. My father was a prominent pastor and geographer. I studied art at Yale and the Royal Academy in London. For 20 years I was a professional painter. Then my wife Lucretia died while I was away painting a portrait. By the time the letter reached me, she was already buried. I never got to say goodbye. That grief drove the telegraph. On May 24, 1844: What hath God wrought -- sent from Washington to Baltimore. Tip: My code was not arbitrary. I visited a printer shop and counted which letters had the most type pieces. E was most common, so E gets a single dot. Always optimize for the common case. Alfred Vail helped me refine the system. Give collaborators credit.",
        "telegram_username": "dot_dash",
        "city": "Charlestown",
        "country_code": "US",
        "latitude": 42.380,
        "longitude": -71.061,
        "badge_tier": "legend",
        "languages": [{"language_code": "en", "proficiency": "native"}, {"language_code": "fr", "proficiency": "conversational"}],
        "skills": [
            {"skill_name": "Telegraphy", "category": "electronics", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Portrait Painting", "category": "art", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Electrical Engineering", "category": "electronics", "self_rating": 4, "years_experience": 30},
            {"skill_name": "Code Design", "category": "education", "self_rating": 5, "years_experience": 35}
        ],
        "social_links": [],
        "points": {"total_points": 2000, "rentals_completed": 50, "reviews_given": 38, "reviews_received": 62, "items_listed": 7, "helpful_flags": 35},
        "offers_training": True,
        "items": [
            {"name": "Morse Code Workshop -- The Original Digital Language", "slug": "morse-code-workshop-original-digital", "description": "Learn Morse code -- the first digital communication system. On/off, long/short, 1/0. In two hours you will send and receive at 5 words per minute. We use a real telegraph key and sounder. Tip: Learn the rhythm, not the dots and dashes. Your ear learns faster than your eyes.", "item_type": "service", "category": "electronics", "listings": [{"listing_type": "training", "price": 14.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Telegraph Key & Sounder Set (Working, Brass)", "slug": "telegraph-key-sounder-brass-set", "description": "Brass telegraph key and electromagnetic sounder connected by wire. Press the key, the sounder clicks. The same setup that connected America coast to coast. Includes battery and wire. Set up two stations across a room and send messages.", "item_type": "physical", "category": "electronics", "listings": [{"listing_type": "rent", "price": 10.0, "price_unit": "per_day", "currency": "EUR", "deposit": 45.0}]},
            {"name": "Portrait Painting Lesson -- Classical Technique", "slug": "portrait-painting-classical-technique-morse", "description": "Before the telegraph, I was a painter. Studied under Washington Allston and Benjamin West. I will teach you classical portrait technique: underpainting in burnt umber, building up layers, glazing for luminosity. My portrait of Lafayette hangs in the Capitol.", "item_type": "service", "category": "art", "listings": [{"listing_type": "training", "price": 16.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Signal Encoding Workshop -- Data Compression Before Computers", "slug": "signal-encoding-data-compression", "description": "Small group (max 4). The principles behind Morse code, Braille, semaphore, and other encoding systems. How do you represent complex information with simple signals? How do you optimize for speed and reliability? Shannon formalized it 100 years later. I figured it out by counting type.", "item_type": "service", "category": "education", "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]}
        ]
    },

    # ============================================================
    # 16. ALEXANDER FLEMING (1881-1955)
    # ============================================================
    {
        "slug": "flemings-petri-dish",
        "display_name": "Alexander Fleming",
        "email": "fleming@borrowhood.local",
        "date_of_birth": "1881-08-06",
        "mother_name": "Grace Stirling Morton",
        "father_name": "Hugh Fleming",
        "workshop_name": "Fleming's Petri Dish Laboratory",
        "workshop_type": "laboratory",
        "tagline": "One sometimes finds what one is not looking for",
        "bio": "Born in Darvel, Ayrshire, Scotland. Grew up on a sheep farm. My father died when I was seven. Served in World War I -- watched soldiers die from infected wounds, not the wounds themselves. September 1928, I went on holiday and left petri dishes of Staphylococcus on my bench. Came back and found a mould -- Penicillium notatum -- had killed the bacteria around it. That contamination saved more lives than any other discovery in history. Tip: My lab was famously messy. A cleaner lab would not have been contaminated. But a less observant scientist would not have noticed. Howard Florey and Ernst Chain turned my observation into a usable drug. The discovery was mine, but the medicine was theirs.",
        "telegram_username": "mould_man",
        "city": "Darvel",
        "country_code": "GB",
        "latitude": 55.613,
        "longitude": -4.277,
        "badge_tier": "legend",
        "languages": [{"language_code": "en", "proficiency": "native"}],
        "skills": [
            {"skill_name": "Microbiology", "category": "science", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Bacteriology", "category": "science", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Laboratory Safety", "category": "science", "self_rating": 4, "years_experience": 35},
            {"skill_name": "Medical Research", "category": "science", "self_rating": 5, "years_experience": 40}
        ],
        "social_links": [],
        "points": {"total_points": 2250, "rentals_completed": 58, "reviews_given": 44, "reviews_received": 70, "items_listed": 7, "helpful_flags": 40},
        "offers_training": True,
        "items": [
            {"name": "Microbiology Workshop -- The Invisible World", "slug": "microbiology-workshop-invisible-world", "description": "Hands-on session. Swab surfaces, streak petri dishes, incubate, and examine colonies. You will see what lives on your phone, your doorknob, your skin. The ability to see the invisible world is the foundation of modern medicine. Tip: Always label your plates.", "item_type": "service", "category": "science", "listings": [{"listing_type": "training", "price": 16.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Microscope (Compound, Research Grade, 1000x)", "slug": "microscope-compound-research-1000x", "description": "Research-grade compound microscope with 40x, 100x, 400x, and 1000x magnification. Oil immersion lens. See bacteria, blood cells, plant cells, crystals. Comes with prepared slides and blank slides for your own specimens.", "item_type": "physical", "category": "science", "listings": [{"listing_type": "rent", "price": 15.0, "price_unit": "per_day", "currency": "EUR", "deposit": 80.0}]},
            {"name": "Antibiotic Resistance Lecture -- The Crisis We Created", "slug": "antibiotic-resistance-lecture-crisis", "description": "I warned about this in my 1945 Nobel lecture. Bacteria evolve resistance when we use antibiotics carelessly. The ignorant man who takes insufficient doses creates resistant strains. Seventy years later, it is a global crisis. This lecture covers the mechanism and what we can still do.", "item_type": "service", "category": "science", "listings": [{"listing_type": "training", "price": 12.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Petri Dish & Agar Kit (Sterile, 50-Pack)", "slug": "petri-dish-agar-kit-sterile-50", "description": "Fifty sterile petri dishes with pre-poured nutrient agar. Ready for streaking, swabbing, or zone-of-inhibition experiments. Includes inoculation loops and a Bunsen burner. Proper aseptic technique required.", "item_type": "physical", "category": "science", "listings": [{"listing_type": "rent", "price": 10.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0}]},
            {"name": "Scientific Observation Skills -- Seeing What Others Miss", "slug": "scientific-observation-skills-seeing", "description": "Small group (max 4). I will train your eye to notice anomalies. We will examine slides, cultures, and experiments looking for the unexpected. The mould on my petri dish was an anomaly. A hundred scientists would have thrown it away. I looked closer. The most important words in science are not Eureka -- they are That is funny.", "item_type": "service", "category": "education", "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]}
        ]
    },

    # ============================================================
    # 17. LOUIS PASTEUR (1822-1895)
    # ============================================================
    {
        "slug": "pasteurs-fermentation-lab",
        "display_name": "Louis Pasteur",
        "email": "pasteur@borrowhood.local",
        "date_of_birth": "1822-12-27",
        "mother_name": "Jeanne-Etiennette Roqui",
        "father_name": "Jean-Joseph Pasteur",
        "workshop_name": "Pasteur's Fermentation Laboratory",
        "workshop_type": "laboratory",
        "tagline": "In the fields of observation, chance favors only the prepared mind",
        "bio": "Born in Dole, Jura, France. My father was a tanner and decorated sergeant in Napoleon's army. Mediocre student as a boy. But at the Ecole Normale Superieure, I fell in love with crystallography. Discovered molecular chirality at 25. That led to fermentation, germ theory, pasteurization, and vaccines. I proved life does not arise spontaneously with swan-neck flask experiments. Developed vaccines for anthrax, cholera, and rabies. The rabies vaccine on young Joseph Meister in 1885 -- if it failed, the boy would die. It worked. Tip: The prepared mind comes from working 16-hour days, six days a week, for 40 years. There are no shortcuts.",
        "telegram_username": "germ_hunter",
        "city": "Dole",
        "country_code": "FR",
        "latitude": 47.095,
        "longitude": 5.492,
        "badge_tier": "legend",
        "languages": [{"language_code": "fr", "proficiency": "native"}, {"language_code": "la", "proficiency": "fluent"}],
        "skills": [
            {"skill_name": "Microbiology", "category": "science", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Immunology", "category": "science", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Chemistry", "category": "science", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Food Science", "category": "science", "self_rating": 5, "years_experience": 35}
        ],
        "social_links": [],
        "points": {"total_points": 2550, "rentals_completed": 66, "reviews_given": 50, "reviews_received": 78, "items_listed": 8, "helpful_flags": 46},
        "offers_training": True,
        "items": [
            {"name": "Fermentation Science Workshop -- Grapes to Wine to Vinegar", "slug": "fermentation-science-workshop-grapes", "description": "Hands-on. We will ferment grape juice, observe yeast under the microscope, test for alcohol and acetic acid. This is how I started -- wine merchants of Lille asked why their fermentations kept failing. The answer was contaminating microorganisms. Clean your equipment. Always.", "item_type": "service", "category": "science", "listings": [{"listing_type": "training", "price": 16.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Germ Theory Demo -- Swan-Neck Flask Experiment", "slug": "germ-theory-demo-swan-neck-flask", "description": "Replicate my famous experiment. Two flasks of broth: one open, one with a swan-curved neck. The straight one spoils. The swan-neck stays clear for years. I still have flasks from the 1860s that are sterile. This experiment ended the debate on spontaneous generation forever.", "item_type": "service", "category": "science", "listings": [{"listing_type": "training", "price": 14.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Pasteurization Kit (Home Dairy/Brewing)", "slug": "pasteurization-kit-home-dairy", "description": "Everything to pasteurize milk, juice, or homebrew: precision thermometer, stainless steel pot, timer, instructions. Heat to 72 degrees Celsius for 15 seconds, then cool rapidly. Named after me, and I am proud of that. This process saves millions of lives every year.", "item_type": "physical", "category": "science", "listings": [{"listing_type": "rent", "price": 8.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0}]},
            {"name": "Microscope Slide Preparation Workshop", "slug": "microscope-slide-preparation-workshop", "description": "Learn professional slide prep: fixation, staining (Gram, methylene blue, crystal violet), mounting, labeling. Proper staining is the difference between seeing nothing and everything. Techniques from the Pasteur Institute.", "item_type": "service", "category": "science", "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Swan-Neck Flask Set (Borosilicate, 3-Piece)", "slug": "swan-neck-flask-set-borosilicate-3pc", "description": "Three hand-blown borosilicate glass flasks with swan-curved necks. The design that proved microbes come from the environment, not thin air. Perfect for classroom demonstrations. Fragile -- handle with the respect you would give a 160-year-old argument settler.", "item_type": "physical", "category": "science", "listings": [{"listing_type": "rent", "price": 10.0, "price_unit": "per_day", "currency": "EUR", "deposit": 45.0}]}
        ]
    },

    # ============================================================
    # 18. ROBERT GODDARD (1882-1945)
    # ============================================================
    {
        "slug": "goddards-rocket-shed",
        "display_name": "Robert Hutchings Goddard",
        "email": "goddard@borrowhood.local",
        "date_of_birth": "1882-10-05",
        "mother_name": "Fannie Louise Hoyt",
        "father_name": "Nahum Danford Goddard",
        "workshop_name": "Goddard's Rocket Shed",
        "workshop_type": "workshop",
        "tagline": "It is difficult to say what is impossible, for the dream of yesterday is the hope of today and the reality of tomorrow",
        "bio": "Born in Worcester, Massachusetts. On October 19, 1899, I climbed a cherry tree and looked up at the sky. I imagined a device that could reach Mars. I climbed down a different person. Published A Method of Reaching Extreme Altitudes in 1919. The New York Times mocked me -- said rockets cannot work in a vacuum. Newton Third Law. On March 16, 1926, I launched the first liquid-fueled rocket. It flew for 2.5 seconds, reached 41 feet. Pathetic by any standard except it was the first time in history. Tip: The press will mock you. The military will ignore you. Do the work anyway. Document everything. Von Braun admitted his V-2s used my patents. NASA Goddard Space Flight Center is named for me. I never saw it.",
        "telegram_username": "cherry_tree_man",
        "city": "Worcester",
        "country_code": "US",
        "latitude": 42.263,
        "longitude": -71.802,
        "badge_tier": "legend",
        "languages": [{"language_code": "en", "proficiency": "native"}],
        "skills": [
            {"skill_name": "Rocketry", "category": "engineering", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Physics", "category": "science", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Machining", "category": "tools", "self_rating": 4, "years_experience": 30},
            {"skill_name": "Propulsion Engineering", "category": "engineering", "self_rating": 5, "years_experience": 35}
        ],
        "social_links": [],
        "points": {"total_points": 2100, "rentals_completed": 54, "reviews_given": 40, "reviews_received": 66, "items_listed": 7, "helpful_flags": 37},
        "offers_training": True,
        "items": [
            {"name": "Model Rocketry Workshop -- Build & Launch", "slug": "model-rocketry-workshop-build-launch", "description": "Build a solid-fuel model rocket, learn thrust, drag, stability, recovery, then launch. We calculate expected altitude before launch and measure after. Tip: Center of pressure behind center of gravity. If not, it tumbles.", "item_type": "service", "category": "engineering", "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Rocket Engine Test Stand (Educational)", "slug": "rocket-engine-test-stand-educational", "description": "Tabletop test stand for small solid rocket motors. Measures thrust with a load cell and data logger. See the thrust curve, calculate impulse and burn time. I tested engines hundreds of times at my aunt Effie farm in Auburn. The neighbors complained. Worth it.", "item_type": "physical", "category": "engineering", "listings": [{"listing_type": "rent", "price": 18.0, "price_unit": "per_day", "currency": "EUR", "deposit": 80.0}]},
            {"name": "Orbital Mechanics Tutoring -- Getting to Space", "slug": "orbital-mechanics-tutoring-space", "description": "One-on-one tutoring in spaceflight physics. Escape velocity, orbital insertion, Hohmann transfers, gravity assists. I worked this out by hand in the 1910s. Tip: Getting to orbit is not about going up. It is about going sideways fast enough.", "item_type": "service", "category": "science", "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Nozzle Design Workshop -- Convergent-Divergent", "slug": "nozzle-design-workshop-de-laval", "description": "Small group (max 3). The nozzle is the heart of any rocket engine. Why a convergent-divergent nozzle accelerates gas to supersonic speeds, how to calculate throat area and expansion ratio. We will machine a simple nozzle from aluminum stock.", "item_type": "service", "category": "engineering", "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]}
        ]
    },

    # ============================================================
    # 19. GUGLIELMO MARCONI (1874-1937)
    # ============================================================
    {
        "slug": "marconis-wireless-station",
        "display_name": "Guglielmo Marconi",
        "email": "marconi@borrowhood.local",
        "date_of_birth": "1874-04-25",
        "mother_name": "Annie Jameson",
        "father_name": "Giuseppe Marconi",
        "workshop_name": "Marconi's Wireless Station",
        "workshop_type": "laboratory",
        "tagline": "Every day sees humanity more victorious in the struggle with space and time",
        "bio": "Born in Bologna, Italy. My mother was Annie Jameson, of the Jameson Irish whiskey family. I studied under Augusto Righi at Bologna, who worked on Hertz electromagnetic waves. At 20, I began experiments in my father attic. In 1901, I received the first transatlantic radio signal -- the letter S, three dots -- from Cornwall to Newfoundland, 3,500 km. The ionosphere bounced the waves. I got lucky. I also got the Nobel Prize. Tip: Hertz discovered radio waves. I made them useful. Tesla built better transmitters. I built the business. The inventor and the entrepreneur are different skills. You need both. My wireless saved 700 lives on the Titanic.",
        "telegram_username": "wireless_man",
        "city": "Bologna",
        "country_code": "IT",
        "latitude": 44.494,
        "longitude": 11.347,
        "badge_tier": "legend",
        "languages": [{"language_code": "it", "proficiency": "native"}, {"language_code": "en", "proficiency": "fluent"}],
        "skills": [
            {"skill_name": "Radio Engineering", "category": "electronics", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Wireless Communication", "category": "electronics", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Antenna Design", "category": "electronics", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Business Development", "category": "education", "self_rating": 4, "years_experience": 30}
        ],
        "social_links": [],
        "points": {"total_points": 2200, "rentals_completed": 57, "reviews_given": 43, "reviews_received": 68, "items_listed": 7, "helpful_flags": 39},
        "offers_training": True,
        "items": [
            {"name": "Crystal Radio Build -- No Batteries Required", "slug": "crystal-radio-build-no-batteries", "description": "Build a crystal radio from scratch: coil, capacitor, crystal detector, earphone. No batteries -- it runs on the energy of radio waves. You will tune into AM stations and hear voices pulled from thin air.", "item_type": "service", "category": "electronics", "listings": [{"listing_type": "training", "price": 14.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Antenna Design & Construction Workshop", "slug": "antenna-design-construction-workshop", "description": "Build working antennas: dipole, ground plane, Yagi-Uda. Wavelength, impedance matching, gain, directivity. The antenna is the most important part of any radio system. A perfect transmitter with a bad antenna is useless.", "item_type": "service", "category": "electronics", "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Spark Gap Transmitter (Demo Model, Low Power)", "slug": "spark-gap-transmitter-demo-low-power", "description": "Low-power replica of an early spark-gap transmitter. Generates broadband radio pulses you can receive on an AM radio across the room. The crackle of the spark, the hiss in the receiver -- this is how the Titanic called for help.", "item_type": "physical", "category": "electronics", "listings": [{"listing_type": "rent", "price": 12.0, "price_unit": "per_day", "currency": "EUR", "deposit": 55.0}]},
            {"name": "Radio History & Maritime Safety Lecture", "slug": "radio-history-maritime-safety-lecture", "description": "Wireless at sea: from first ship-to-shore messages to the Titanic to modern GMDSS. 700 survived because Jack Phillips stayed at his post sending SOS until power failed. After Titanic, every ship was required to carry wireless.", "item_type": "service", "category": "education", "listings": [{"listing_type": "training", "price": 10.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Coherer & Detector Collection (Replicas)", "slug": "coherer-detector-collection-replicas", "description": "Early radio detectors: Branly coherer, magnetic detector, crystal detector. Each a step in the evolution of radio reception. The coherer -- a tube of metal filings that clumps when radio waves hit it -- is crude and brilliant.", "item_type": "physical", "category": "electronics", "listings": [{"listing_type": "rent", "price": 10.0, "price_unit": "per_day", "currency": "EUR", "deposit": 40.0}]}
        ]
    },

    # ============================================================
    # 20. HENRY FORD (1863-1947)
    # ============================================================
    {
        "slug": "fords-assembly-line",
        "display_name": "Henry Ford",
        "email": "ford@borrowhood.local",
        "date_of_birth": "1863-07-30",
        "mother_name": "Mary Litogot Ford",
        "father_name": "William Ford",
        "workshop_name": "Ford's Assembly Line Workshop",
        "workshop_type": "garage",
        "tagline": "Whether you think you can, or you think you cannot -- you are right",
        "bio": "Born in Dearborn, Michigan, on a farm. Hated farming. Loved machines. At 12, I saw a steam engine on the road and never looked back. Built my first gasoline engine on the kitchen table in 1893 -- my wife Clara held it steady while I tested it. My first two car companies failed. The third succeeded because of one idea: the moving assembly line. Model T build time dropped from 12 hours to 93 minutes. Price dropped from $850 to $260. I paid workers $5 a day -- double the rate. Workers who can afford the product they build become customers. Tip: Simplify. Model T came in one color -- black -- because black paint dried fastest. Edison was my mentor and friend. He told me to keep going.",
        "telegram_username": "model_t",
        "city": "Dearborn",
        "country_code": "US",
        "latitude": 42.322,
        "longitude": -83.176,
        "badge_tier": "legend",
        "languages": [{"language_code": "en", "proficiency": "native"}],
        "skills": [
            {"skill_name": "Manufacturing", "category": "engineering", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Mechanical Engineering", "category": "engineering", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Business Management", "category": "education", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Process Optimization", "category": "engineering", "self_rating": 5, "years_experience": 40}
        ],
        "social_links": [],
        "points": {"total_points": 2400, "rentals_completed": 62, "reviews_given": 46, "reviews_received": 74, "items_listed": 8, "helpful_flags": 42},
        "offers_training": True,
        "items": [
            {"name": "Assembly Line Simulation Workshop", "slug": "assembly-line-simulation-workshop", "description": "Small group (max 8). Simulate a moving assembly line. First round: each person builds complete item. Second round: each person does one step. Measure the difference. Tip: The bottleneck is the slowest station. Fix that first.", "item_type": "service", "category": "engineering", "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Engine Rebuilding Workshop -- Gasoline Fundamentals", "slug": "engine-rebuilding-workshop-gasoline", "description": "Disassemble and reassemble a small gasoline engine. Pistons, valves, crankshaft, carburetor, ignition. You will understand the four-stroke cycle by touching every part. I built my first engine on the kitchen table. Clara held the fuel line.", "item_type": "service", "category": "engineering", "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Complete Mechanic Tool Set (Metric & Imperial)", "slug": "complete-mechanics-tool-set-ford", "description": "Full mechanic tool set: wrenches, sockets, screwdrivers, pliers, torque wrench, feeler gauges, timing light. Quality tools are an investment. Cheap tools break at the worst moment.", "item_type": "physical", "category": "tools", "listings": [{"listing_type": "rent", "price": 10.0, "price_unit": "per_day", "currency": "EUR", "deposit": 50.0}]},
            {"name": "Process Optimization Consulting -- Eliminate Waste", "slug": "process-optimization-eliminate-waste", "description": "One-on-one. Bring me your workflow -- manufacturing, service, office, anything. I will find the waste. Every process has value-adding steps and non-value-adding steps. Eliminate the latter. At Highland Park, chassis assembly went from 12 hours 28 minutes to 1 hour 33 minutes.", "item_type": "service", "category": "engineering", "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Model T Wheel & Brake Drum (Display)", "slug": "model-t-wheel-brake-drum-display", "description": "Original-spec Model T wooden-spoke wheel with brake drum. Hickory and elm, 30 inches diameter. 15 million Model Ts built. This wheel design barely changed in 19 years. When something works, do not fix it.", "item_type": "physical", "category": "engineering", "listings": [{"listing_type": "rent", "price": 8.0, "price_unit": "per_day", "currency": "EUR", "deposit": 40.0}]}
        ]
    },

    # ============================================================
    # 21. MADAM C.J. WALKER (1867-1919)
    # ============================================================
    {
        "slug": "walkers-beauty-lab",
        "display_name": "Madam C.J. Walker",
        "email": "walker@borrowhood.local",
        "date_of_birth": "1867-12-23",
        "mother_name": "Minerva Anderson Breedlove",
        "father_name": "Owen Breedlove",
        "workshop_name": "Walker's Beauty Laboratory & Business School",
        "workshop_type": "laboratory",
        "tagline": "I got my start by giving myself a start",
        "bio": "Born Sarah Breedlove in Delta, Louisiana. First person in my family born free. Orphaned at 7, married at 14, widowed at 20 with a daughter. Worked as a washerwoman for $1.50 a day. Began losing my hair from stress, poor diet, and harsh products. Developed my own formula -- the Walker System -- for scalp treatment and hair growth. Built a company, a factory, trained thousands of Walker Agents -- Black women earning their own money when few doors were open. First self-made female millionaire in America. Tip: I did not start with money. I started with a problem I understood personally. Every great business starts with personal pain that becomes universal solution. Also: pay your people well and they become your best advertisement. Booker T. Washington thought I was too flashy. I told him I came from the cotton fields of the South and built this with my own hands.",
        "telegram_username": "walker_system",
        "city": "Delta",
        "country_code": "US",
        "latitude": 32.352,
        "longitude": -91.692,
        "badge_tier": "legend",
        "languages": [{"language_code": "en", "proficiency": "native"}],
        "skills": [
            {"skill_name": "Cosmetic Chemistry", "category": "science", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Business Development", "category": "education", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Sales Training", "category": "education", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Manufacturing", "category": "engineering", "self_rating": 4, "years_experience": 15}
        ],
        "social_links": [],
        "points": {"total_points": 2300, "rentals_completed": 60, "reviews_given": 48, "reviews_received": 72, "items_listed": 7, "helpful_flags": 42},
        "offers_training": True,
        "items": [
            {"name": "Entrepreneurship Workshop -- From Nothing to Empire", "slug": "entrepreneurship-from-nothing-to-empire", "description": "I started with $1.50 and a problem. I will teach you how to identify a market need from personal experience, develop a product, build a sales force, and scale without outside investment. No venture capital. No bank loans. Sweat equity and reinvestment. The Walker method for business.", "item_type": "service", "category": "education", "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Natural Hair Care Formulation Workshop", "slug": "natural-hair-care-formulation-workshop", "description": "Learn to make scalp treatments, hair oils, and conditioning products from natural ingredients. I developed my formulas through years of experimentation. Sulfur, petrolatum, plant extracts. You will leave with three products and the knowledge to create more.", "item_type": "service", "category": "science", "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Sales Training Masterclass -- Door-to-Door to Empire", "slug": "sales-training-door-to-door-empire", "description": "Small group (max 6). I trained 20,000 Walker Agents. The secret is demonstration. Do not tell people your product works -- show them. Do not sell features -- sell transformation. I will teach you the Walker pitch: personal story, live demonstration, satisfied customer testimonial, close.", "item_type": "service", "category": "education", "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Walker System Product Kit (Replica)", "slug": "walker-system-product-kit-replica", "description": "Replica of the original Walker System product line: Wonderful Hair Grower, Temple Salve, Tetter Salve, and Glossine. Historical packaging and formulations adapted for modern use. A piece of entrepreneurial history you can actually use.", "item_type": "physical", "category": "science", "listings": [{"listing_type": "offer", "price": 12.0, "price_unit": "per_unit", "currency": "EUR"}]}
        ]
    },

    # ============================================================
    # 22. STEPHANIE KWOLEK (1923-2014)
    # ============================================================
    {
        "slug": "kwoleks-polymer-lab",
        "display_name": "Stephanie Kwolek",
        "email": "kwolek@borrowhood.local",
        "date_of_birth": "1923-07-31",
        "mother_name": "Nellie Zajdel Kwolek",
        "father_name": "John Kwolek",
        "workshop_name": "Kwolek's Polymer Laboratory",
        "workshop_type": "laboratory",
        "tagline": "I never in a thousand years expected that small laboratory project would unfold as it did",
        "bio": "Born in New Kensington, Pennsylvania. My father died when I was 10. He was a naturalist who took me on walks through the woods to study plants. My mother was a seamstress who taught me to sew. I wanted to be a doctor but could not afford medical school, so I took a temporary job at DuPont to save money. I stayed 40 years. In 1965, I was working on lightweight fibers for tires when I produced a strange, cloudy solution. Most chemists would have thrown it away. I insisted on spinning it. The fiber was five times stronger than steel by weight. Kevlar. It now protects police officers, soldiers, firefighters, and astronauts. Tip: When the experiment gives you something unexpected, do not discard it. Investigate it. The biggest discoveries come from anomalies, not from predictions. Also: temporary jobs sometimes become life work.",
        "telegram_username": "kevlar_queen",
        "city": "New Kensington",
        "country_code": "US",
        "latitude": 40.570,
        "longitude": -79.765,
        "badge_tier": "legend",
        "languages": [{"language_code": "en", "proficiency": "native"}],
        "skills": [
            {"skill_name": "Polymer Chemistry", "category": "science", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Material Science", "category": "science", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Fiber Technology", "category": "engineering", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Laboratory Research", "category": "science", "self_rating": 5, "years_experience": 40}
        ],
        "social_links": [],
        "points": {"total_points": 2050, "rentals_completed": 52, "reviews_given": 40, "reviews_received": 64, "items_listed": 7, "helpful_flags": 36},
        "offers_training": True,
        "items": [
            {"name": "Materials Science Workshop -- Polymers & Fibers", "slug": "materials-science-polymers-fibers", "description": "Hands-on session. Test the strength of different fibers: nylon, polyester, aramid (Kevlar), carbon fiber, silk. Measure tensile strength, stretch, and failure modes. Understand why Kevlar stops a bullet but scissors cut it. Material properties are not obvious -- you must test them.", "item_type": "service", "category": "science", "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Kevlar Sample Kit (Educational, 5 Weave Types)", "slug": "kevlar-sample-kit-5-weaves", "description": "Five Kevlar fabric samples in different weave patterns: plain, twill, satin, unidirectional, and hybrid. Cut them, stretch them, test them. Feel the difference between weaves and understand why ballistic vests use specific patterns. Includes magnifier and test instructions.", "item_type": "physical", "category": "science", "listings": [{"listing_type": "rent", "price": 10.0, "price_unit": "per_day", "currency": "EUR", "deposit": 40.0}]},
            {"name": "Chemistry Career Mentoring -- The Accidental Discovery Path", "slug": "chemistry-career-mentoring-accidental", "description": "One-on-one. I took a temporary job and stayed 40 years. My biggest discovery came from a failed experiment. I will help you navigate a science career: when to persist, when to pivot, how to recognize the unexpected as opportunity, and how to get your work recognized in a field that often overlooks women.", "item_type": "service", "category": "education", "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Tensile Testing Workshop -- How Strong Is It Really", "slug": "tensile-testing-how-strong", "description": "Small group (max 4). We will test materials to destruction: pulling, bending, cutting. Measure force, elongation, and breaking point. Compare metals, plastics, composites, and natural fibers. The numbers always surprise people. Intuition about material strength is usually wrong. Measure.", "item_type": "service", "category": "engineering", "listings": [{"listing_type": "training", "price": 16.0, "price_unit": "per_session", "currency": "EUR"}]}
        ]
    },

    # ============================================================
    # 23. ROSALIND FRANKLIN (1920-1958)
    # ============================================================
    {
        "slug": "franklins-xray-lab",
        "display_name": "Rosalind Franklin",
        "email": "rosalind@borrowhood.local",
        "date_of_birth": "1920-07-25",
        "mother_name": "Muriel Frances Waley",
        "father_name": "Ellis Arthur Franklin",
        "workshop_name": "Franklin's X-Ray Crystallography Lab",
        "workshop_type": "laboratory",
        "tagline": "Science and everyday life cannot and should not be separated",
        "bio": "Born in Notting Hill, London, into a prominent Anglo-Jewish family. Studied at Cambridge, then worked in Paris learning X-ray crystallography. Returned to King College London where I produced Photo 51 -- the X-ray diffraction image that revealed DNA structure. Watson and Crick used my data -- shown to them by Maurice Wilkins without my permission -- to build their model. They got the Nobel Prize. I was never told they had seen my work. I died of ovarian cancer at 37, likely from years of X-ray exposure. Tip: Document your work meticulously and guard your data. The history of science is full of stolen credit. Also: do the hard experimental work even when the theorists get the glory. Without Photo 51, Watson and Crick had nothing but speculation. The evidence is everything.",
        "telegram_username": "photo_51",
        "city": "London",
        "country_code": "GB",
        "latitude": 51.509,
        "longitude": -0.197,
        "badge_tier": "legend",
        "languages": [{"language_code": "en", "proficiency": "native"}, {"language_code": "fr", "proficiency": "fluent"}],
        "skills": [
            {"skill_name": "X-Ray Crystallography", "category": "science", "self_rating": 5, "years_experience": 15},
            {"skill_name": "Physical Chemistry", "category": "science", "self_rating": 5, "years_experience": 18},
            {"skill_name": "Molecular Biology", "category": "science", "self_rating": 5, "years_experience": 12},
            {"skill_name": "Laboratory Photography", "category": "science", "self_rating": 5, "years_experience": 15}
        ],
        "social_links": [],
        "points": {"total_points": 2150, "rentals_completed": 55, "reviews_given": 44, "reviews_received": 66, "items_listed": 7, "helpful_flags": 38},
        "offers_training": True,
        "items": [
            {"name": "X-Ray Crystallography Demonstration", "slug": "xray-crystallography-demo", "description": "How we see molecules. I will explain diffraction patterns, Bragg law, and how a flat photograph reveals three-dimensional structure. We will analyze diffraction patterns from simple crystals. Photo 51 was not lucky -- it was 100 hours of exposure with perfect fiber alignment. Technique matters more than equipment.", "item_type": "service", "category": "science", "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "DNA Model Kit (Double Helix, Molecular Scale)", "slug": "dna-model-kit-double-helix", "description": "Build a physical model of DNA double helix from molecular components. Bases, sugars, phosphates -- snap them together and see why the structure works. Watson and Crick built a model like this. But their model was correct only because my data showed them the dimensions, the symmetry, and the backbone orientation.", "item_type": "physical", "category": "science", "listings": [{"listing_type": "rent", "price": 8.0, "price_unit": "per_day", "currency": "EUR", "deposit": 35.0}]},
            {"name": "Scientific Photography Workshop -- Capturing the Invisible", "slug": "scientific-photography-capturing-invisible", "description": "Laboratory photography techniques: proper exposure, contrast, alignment, documentation. A scientific photograph is evidence. It must be sharp, properly labeled, and reproducible. Photo 51 required weeks of preparation for a 100-hour exposure. Every detail matters.", "item_type": "service", "category": "science", "listings": [{"listing_type": "training", "price": 16.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Women in STEM Mentoring -- Credit and Recognition", "slug": "women-stem-mentoring-credit", "description": "One-on-one mentoring. My work was used without my knowledge. My contribution was minimized for decades. I will teach you how to protect your intellectual contribution: documentation, publication timing, co-authorship agreements, and when to speak up. The work is everything, but credit matters too.", "item_type": "service", "category": "education", "listings": [{"listing_type": "training", "price": 0.0, "price_unit": "per_session", "currency": "EUR"}]}
        ]
    },

    # ============================================================
    # 24. RACHEL CARSON (1907-1964)
    # ============================================================
    {
        "slug": "carsons-field-station",
        "display_name": "Rachel Louise Carson",
        "email": "carson@borrowhood.local",
        "date_of_birth": "1907-05-27",
        "mother_name": "Maria Frazier McLean",
        "father_name": "Robert Warden Carson",
        "workshop_name": "Carson's Field Station & Writing Desk",
        "workshop_type": "study",
        "tagline": "In every outward and visible grace of life, in every truth of nature, there is a mystery",
        "bio": "Born in Springdale, Pennsylvania. My mother taught me to love nature on walks through the woods. Started as a marine biologist for the US Fish and Wildlife Service. Published The Sea Around Us in 1951 -- a bestseller that made ocean science accessible. Then in 1962, Silent Spring. I documented how DDT and other pesticides were poisoning birds, fish, and the entire food chain. The chemical industry attacked me viciously -- called me hysterical, a communist, an unmarried woman who had no business in science. I had breast cancer and knew I was dying. I testified before Congress anyway. DDT was banned. The EPA was created. The modern environmental movement began. Tip: Write clearly enough that non-scientists understand, and precisely enough that scientists cannot dismiss you. The pen is more powerful than the spray plane. My friend Dorothy Freeman and I exchanged hundreds of letters. Find someone who believes in your work when the world attacks.",
        "telegram_username": "silent_spring",
        "city": "Springdale",
        "country_code": "US",
        "latitude": 40.538,
        "longitude": -79.783,
        "badge_tier": "legend",
        "languages": [{"language_code": "en", "proficiency": "native"}],
        "skills": [
            {"skill_name": "Marine Biology", "category": "science", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Environmental Science", "category": "science", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Science Writing", "category": "education", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Ecology", "category": "science", "self_rating": 5, "years_experience": 25}
        ],
        "social_links": [],
        "points": {"total_points": 2200, "rentals_completed": 56, "reviews_given": 46, "reviews_received": 68, "items_listed": 7, "helpful_flags": 40},
        "offers_training": True,
        "items": [
            {"name": "Nature Writing Workshop -- Science as Literature", "slug": "nature-writing-science-literature", "description": "Small group (max 5). I will teach you to write about science with beauty and precision. Observe a tide pool, a meadow, a single tree -- then write what you see so that readers feel it. The Sea Around Us sold two million copies because people could taste the salt. Accuracy and poetry are not enemies.", "item_type": "service", "category": "education", "listings": [{"listing_type": "training", "price": 16.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Field Ecology Walk -- Reading the Landscape", "slug": "field-ecology-walk-reading-landscape", "description": "A guided walk through any natural area. I will teach you to read the ecosystem: what eats what, who pollinates whom, where the water flows, why certain plants grow in certain spots. Every landscape tells a story of interconnection. Once you see it, you cannot unsee it.", "item_type": "service", "category": "science", "listings": [{"listing_type": "training", "price": 12.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Field Naturalist Kit (Notebook, Loupe, Guides)", "slug": "field-naturalist-kit-notebook-loupe", "description": "Waterproof field notebook, 10x hand loupe, regional plant and bird identification guides, collecting vials, and a lightweight shoulder bag. Everything you need for a day of serious nature observation. My mother gave me a similar kit when I was eight.", "item_type": "physical", "category": "science", "listings": [{"listing_type": "rent", "price": 6.0, "price_unit": "per_day", "currency": "EUR", "deposit": 25.0}]},
            {"name": "Environmental Advocacy Workshop -- Science Meets Policy", "slug": "environmental-advocacy-science-policy", "description": "How to translate scientific evidence into public policy change. I will teach you how to build an airtight case, anticipate industry counterattacks, write for legislators who do not read journals, and testify under pressure. The chemical industry threw everything at me. I had the data. Data wins.", "item_type": "service", "category": "education", "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Tide Pool Ecology Kit (Marine Biology Starter)", "slug": "tide-pool-ecology-kit-marine-starter", "description": "Clear observation containers, pH strips, salinity meter, waterproof ID cards for intertidal species, and a guide to tide pool ecology. The tide pool is a complete world in miniature. Everything connects. Disturb one species and watch the cascade. This is what Silent Spring was about -- scaled up to continents.", "item_type": "physical", "category": "science", "listings": [{"listing_type": "rent", "price": 7.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0}]}
        ]
    },

    # ============================================================
    # 25. ALFRED NOBEL (1833-1896)
    # ============================================================
    {
        "slug": "nobels-chemistry-vault",
        "display_name": "Alfred Bernhard Nobel",
        "email": "nobel@borrowhood.local",
        "date_of_birth": "1833-10-21",
        "mother_name": "Karolina Andriette Ahlsell",
        "father_name": "Immanuel Nobel",
        "workshop_name": "Nobel's Chemistry Vault",
        "workshop_type": "laboratory",
        "tagline": "My dynamite will sooner lead to peace than a thousand world conventions",
        "bio": "Born in Stockholm, Sweden. My father was an engineer and inventor who went bankrupt, moved us to St. Petersburg, and rebuilt. I was privately tutored, spoke five languages by 17. Studied chemistry in Paris under Theophile-Jules Pelouze. My brother Emil was killed in a nitroglycerin explosion at our factory in 1864. That drove me to tame the substance. Mixed nitroglycerin with diatomaceous earth: dynamite. Stable, safe to handle, devastating when detonated. Then detonating caps. Then blasting gelatin. Then ballistite. 355 patents. Factories in 20 countries. Then I read my own obituary -- a French newspaper confused me with my brother Ludvig and published it. The headline: The Merchant of Death Is Dead. I decided my fortune should fund prizes for peace, literature, and science. Tip: What the world says about you after you die matters. You still have time to change the story. My friend Bertha von Suttner convinced me the peace prize was essential.",
        "telegram_username": "dynamite_man",
        "city": "Stockholm",
        "country_code": "SE",
        "latitude": 59.329,
        "longitude": 18.069,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "sv", "proficiency": "native"},
            {"language_code": "fr", "proficiency": "fluent"},
            {"language_code": "en", "proficiency": "fluent"},
            {"language_code": "de", "proficiency": "fluent"},
            {"language_code": "ru", "proficiency": "fluent"}
        ],
        "skills": [
            {"skill_name": "Chemistry", "category": "science", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Explosives Engineering", "category": "engineering", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Patent Law", "category": "education", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Business Strategy", "category": "education", "self_rating": 5, "years_experience": 40}
        ],
        "social_links": [],
        "points": {"total_points": 2500, "rentals_completed": 64, "reviews_given": 50, "reviews_received": 76, "items_listed": 8, "helpful_flags": 44},
        "offers_training": True,
        "items": [
            {"name": "Chemistry of Energetic Materials -- Safe Demonstration", "slug": "chemistry-energetic-materials-safe-demo", "description": "Safe demonstrations of exothermic reactions, combustion chemistry, and energy release. No explosives -- but you will understand why nitroglycerin is unstable and how adding diatomaceous earth makes it safe to handle. The chemistry of energy storage and release underpins everything from batteries to rockets.", "item_type": "service", "category": "science", "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Legacy Planning Workshop -- Write Your Own Obituary First", "slug": "legacy-planning-write-obituary-first", "description": "I read my own obituary and it horrified me. Merchant of Death. So I rewrote my legacy. This workshop: write the obituary you want published, then work backwards. What do you need to do between now and then? I will help you design a legacy that outlasts you. The Nobel Prizes are mine.", "item_type": "service", "category": "education", "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Patent Strategy Consulting -- 355 Patents Method", "slug": "patent-strategy-355-patents", "description": "One-on-one session. I held 355 patents in multiple countries. I will teach you patent strategy: what to patent, where to file, how to create a patent portfolio that protects your business, and how to license effectively. A single patent is a shield. A portfolio is a fortress.", "item_type": "service", "category": "education", "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Laboratory Safety Equipment Set (PPE, Full Kit)", "slug": "lab-safety-equipment-ppe-full", "description": "Complete lab safety kit: goggles, face shield, nitrile gloves, lab coat, fire extinguisher, first aid kit, chemical spill kit. My brother died in an explosion. Safety is not optional. Every experiment begins with the question: what is the worst that can happen, and am I prepared for it?", "item_type": "physical", "category": "science", "listings": [{"listing_type": "rent", "price": 8.0, "price_unit": "per_day", "currency": "EUR", "deposit": 35.0}]}
        ]
    },

    # ============================================================
    # 26. JAMES CLERK MAXWELL (1831-1879)
    # ============================================================
    {
        "slug": "maxwells-field-equations",
        "display_name": "James Clerk Maxwell",
        "email": "maxwell@borrowhood.local",
        "date_of_birth": "1831-06-13",
        "mother_name": "Frances Cay",
        "father_name": "John Clerk Maxwell",
        "workshop_name": "Maxwell's Field Equations Study",
        "workshop_type": "study",
        "tagline": "The special theory of relativity owes its origins to Maxwell's equations of the electromagnetic field -- Albert Einstein",
        "bio": "Born in Edinburgh, Scotland. Published my first scientific paper at 14 -- on oval curves. At Cambridge, I unified electricity, magnetism, and light into four equations. Maxwell equations. Everything from radio waves to X-rays to visible light to microwaves -- all the same phenomenon, differing only in wavelength. I predicted electromagnetic waves travel at the speed of light. Therefore light IS an electromagnetic wave. Hertz proved it experimentally eight years after my death. Einstein kept a photograph of me on his wall alongside Newton and Faraday. Tip: If you can express a physical law as a mathematical equation, you can predict phenomena no one has ever observed. I predicted radio waves with mathematics alone. The equations do not care about human doubt. Also pioneered statistical mechanics and produced the first color photograph in 1861. Faraday gave me the experimental foundation. I gave the world the mathematical framework.",
        "telegram_username": "field_equations",
        "city": "Edinburgh",
        "country_code": "GB",
        "latitude": 55.953,
        "longitude": -3.189,
        "badge_tier": "legend",
        "languages": [{"language_code": "en", "proficiency": "native"}, {"language_code": "la", "proficiency": "fluent"}],
        "skills": [
            {"skill_name": "Mathematical Physics", "category": "science", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Electromagnetism", "category": "science", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Statistical Mechanics", "category": "science", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Color Theory", "category": "science", "self_rating": 4, "years_experience": 15}
        ],
        "social_links": [],
        "points": {"total_points": 2650, "rentals_completed": 68, "reviews_given": 52, "reviews_received": 80, "items_listed": 7, "helpful_flags": 46},
        "offers_training": True,
        "items": [
            {"name": "Electromagnetic Waves Workshop -- Light Is Electricity", "slug": "em-waves-workshop-light-electricity", "description": "I will demonstrate that light, radio, microwaves, and X-rays are all the same thing. We will measure wavelength and frequency, build simple wave detectors, and see the electromagnetic spectrum laid out physically. Four equations explain all of it. Tip: The universe is more unified than it appears.", "item_type": "service", "category": "science", "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Color Theory & Photography Demo -- First Color Photo", "slug": "color-theory-first-color-photo", "description": "In 1861, I produced the first color photograph by combining three black-and-white photos taken through red, green, and blue filters. I will demonstrate the principle. Every screen you look at uses this method. RGB. Three colors make a world. Includes hands-on experiments with color mixing and filters.", "item_type": "service", "category": "science", "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Advanced Mathematics Tutoring -- Vectors and Fields", "slug": "advanced-math-tutoring-vectors-fields", "description": "One-on-one tutoring in vector calculus, field theory, and differential equations. The mathematics behind electromagnetism, fluid dynamics, and gravity. I will teach you to see equations as pictures and pictures as equations. If you can visualize a field, you can understand any force in nature.", "item_type": "service", "category": "science", "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Color Filter Set (Optical, RGB + Complementary)", "slug": "color-filter-set-optical-rgb", "description": "Precision optical filters: red, green, blue, cyan, magenta, yellow. Mount them on a light source and explore additive and subtractive color mixing. Combine red and green light -- you get yellow. This surprises everyone. Color is not in the objects. Color is in the light and in your eyes.", "item_type": "physical", "category": "science", "listings": [{"listing_type": "rent", "price": 6.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0}]}
        ]
    },

    # ============================================================
    # 27. DMITRI MENDELEEV (1834-1907)
    # ============================================================
    {
        "slug": "mendeleevs-element-table",
        "display_name": "Dmitri Ivanovich Mendeleev",
        "email": "mendeleev@borrowhood.local",
        "date_of_birth": "1834-02-08",
        "mother_name": "Maria Dmitrievna Kornilieva",
        "father_name": "Ivan Pavlovich Mendeleev",
        "workshop_name": "Mendeleev's Element Table Laboratory",
        "workshop_type": "laboratory",
        "tagline": "I saw in a dream a table where all the elements fell into place as required",
        "bio": "Born in Tobolsk, Siberia, the youngest of 14 children. My mother walked me 1,500 miles to Moscow so I could attend university -- then to St. Petersburg when Moscow rejected me. She died weeks after I was admitted. In 1869, I arranged the 63 known elements by atomic weight and valence. I noticed a pattern -- elements with similar properties appeared at regular intervals. The periodic table. I left gaps for elements not yet discovered and predicted their properties. Gallium, germanium, scandium -- all found within 15 years, matching my predictions exactly. Tip: The table came to me in a dream, but only because I had been studying element properties obsessively for months. You dream about what you work on. Feed your mind and your subconscious will solve the puzzle. Also: I was denied the Nobel Prize by one vote. Sometimes the world is slow to recognize what matters.",
        "telegram_username": "element_table",
        "city": "Tobolsk",
        "country_code": "RU",
        "latitude": 58.198,
        "longitude": 68.254,
        "badge_tier": "legend",
        "languages": [{"language_code": "ru", "proficiency": "native"}, {"language_code": "de", "proficiency": "fluent"}, {"language_code": "fr", "proficiency": "conversational"}],
        "skills": [
            {"skill_name": "Chemistry", "category": "science", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Pattern Recognition", "category": "science", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Teaching", "category": "education", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Scientific Classification", "category": "science", "self_rating": 5, "years_experience": 40}
        ],
        "social_links": [],
        "points": {"total_points": 2400, "rentals_completed": 62, "reviews_given": 48, "reviews_received": 74, "items_listed": 7, "helpful_flags": 42},
        "offers_training": True,
        "items": [
            {"name": "Periodic Table Workshop -- Patterns in Nature", "slug": "periodic-table-workshop-patterns", "description": "Interactive session. We will build the periodic table from scratch using element property cards. Arrange them by weight, notice the patterns, predict the gaps. You will discover what I discovered -- that nature organizes itself. Tip: The table is not arbitrary. It reflects the structure of atoms themselves.", "item_type": "service", "category": "science", "listings": [{"listing_type": "training", "price": 16.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Element Sample Collection (Safe, 30 Elements)", "slug": "element-sample-collection-safe-30", "description": "Thirty element samples in labeled vials: iron, copper, tin, sulfur, silicon, carbon (graphite and diamond chip), aluminum, zinc, and more. Each labeled with atomic number, weight, and properties. Hold the building blocks of the universe in your hand. Some are shiny, some are dull, some are gas in sealed ampules.", "item_type": "physical", "category": "science", "listings": [{"listing_type": "rent", "price": 12.0, "price_unit": "per_day", "currency": "EUR", "deposit": 60.0}]},
            {"name": "Chemistry Tutoring -- Elements, Compounds & Reactions", "slug": "chemistry-tutoring-elements-compounds", "description": "One-on-one tutoring from the man who organized all of chemistry. I will teach you how elements combine, why some react violently and others are inert, and how the periodic table predicts it all. Bring your textbook questions. I wrote the textbook that started it all.", "item_type": "service", "category": "science", "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Pattern Recognition Seminar -- Finding Order in Chaos", "slug": "pattern-recognition-finding-order", "description": "Small group (max 4). Not just chemistry -- the skill of finding patterns in any dataset. I will give you messy data and teach you to sort, classify, and predict. The periodic table was a pattern recognition exercise. The same skill applies to business data, medical records, financial trends, or any complex system.", "item_type": "service", "category": "education", "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]}
        ]
    },

    # ============================================================
    # 28. LOUIS BRAILLE (1809-1852)
    # ============================================================
    {
        "slug": "brailles-tactile-studio",
        "display_name": "Louis Braille",
        "email": "braille@borrowhood.local",
        "date_of_birth": "1809-01-04",
        "mother_name": "Monique Baron",
        "father_name": "Simon-Rene Braille",
        "workshop_name": "Braille's Tactile Studio",
        "workshop_type": "studio",
        "tagline": "Access to communication in the widest sense is access to knowledge",
        "bio": "Born in Coupvray, France. My father was a leatherworker. At age three, I was playing with his tools and an awl slipped into my eye. The infection spread to both eyes. Blind by five. Attended the Royal Institute for Blind Youth in Paris at 10. At 15, I adapted Charles Barbier night writing system into a six-dot cell that could represent any letter, number, or musical note. The Institute resisted my system for decades. The sighted administrators could not read it and felt threatened. It was adopted widely only after my death. Tip: The people who benefit most from your invention are not always the people who decide whether to adopt it. Persistence outlasts resistance. Six dots. Sixty-three combinations. Enough for any language on Earth.",
        "telegram_username": "six_dots",
        "city": "Coupvray",
        "country_code": "FR",
        "latitude": 48.884,
        "longitude": 2.815,
        "badge_tier": "legend",
        "languages": [{"language_code": "fr", "proficiency": "native"}, {"language_code": "la", "proficiency": "conversational"}],
        "skills": [
            {"skill_name": "Tactile Communication", "category": "education", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Music", "category": "music", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Code Design", "category": "education", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Teaching", "category": "education", "self_rating": 5, "years_experience": 25}
        ],
        "social_links": [],
        "points": {"total_points": 2100, "rentals_completed": 54, "reviews_given": 42, "reviews_received": 66, "items_listed": 7, "helpful_flags": 38},
        "offers_training": True,
        "items": [
            {"name": "Braille Reading & Writing Workshop", "slug": "braille-reading-writing-workshop", "description": "Learn to read and write Braille. Six dots, 63 combinations, any language. In two hours you will write your name and read simple words by touch. Sighted people benefit too -- it sharpens tactile awareness and spatial thinking.", "item_type": "service", "category": "education", "listings": [{"listing_type": "training", "price": 12.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Braille Slate & Stylus Set (Professional)", "slug": "braille-slate-stylus-professional", "description": "Professional-grade Braille writing slate with interline spacing and a steel-tipped stylus. Write by punching dots right-to-left (they read left-to-right when flipped). Includes 50 sheets of Braille paper.", "item_type": "physical", "category": "education", "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR", "deposit": 20.0}]},
            {"name": "Accessibility Design Workshop -- Building for Everyone", "slug": "accessibility-design-building-everyone", "description": "Small group (max 5). Think about accessibility from the start, not as an afterthought. Blindfold exercises, navigation challenges, communication without sight. When you design for the most constrained user, you improve the experience for everyone. Curb cuts were designed for wheelchairs. Everyone uses them.", "item_type": "service", "category": "education", "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Organ Concert & Music Lesson (Beginner)", "slug": "organ-concert-music-lesson-beginner", "description": "I was the organist at the Church of Saint-Nicolas-des-Champs in Paris. I also developed Braille music notation so blind musicians could read scores. This lesson covers basic organ technique and an introduction to reading music by touch.", "item_type": "service", "category": "music", "listings": [{"listing_type": "training", "price": 14.0, "price_unit": "per_session", "currency": "EUR"}]}
        ]
    },

    # ============================================================
    # 29. PHILO FARNSWORTH (1906-1971)
    # ============================================================
    {
        "slug": "farnsworths-image-lab",
        "display_name": "Philo Taylor Farnsworth",
        "email": "farnsworth@borrowhood.local",
        "date_of_birth": "1906-08-19",
        "mother_name": "Serena Amanda Bastian",
        "father_name": "Lewis Edwin Farnsworth",
        "workshop_name": "Farnsworth's Image Dissector Lab",
        "workshop_type": "laboratory",
        "tagline": "I visualized the entire television system while plowing a potato field at age 14",
        "bio": "Born in Beaver, Utah, in a log cabin with no electricity. When we moved to Rigby, Idaho, I found science magazines in the attic. At 14, plowing a potato field, I watched the rows of turned earth and imagined scanning an image line by line with an electron beam. That vision became television. Built the first fully electronic TV at 21 in San Francisco. RCA and David Sarnoff fought me for years. I won in court but lost in life -- they had the money and manufacturing. My high school teacher Justin Tolman testified that I had drawn the design on his blackboard in 1922. That drawing won my patent case. Tip: Document your ideas obsessively. A sketch on a blackboard, witnessed by your teacher, won a Supreme Court patent case.",
        "telegram_username": "image_dissector",
        "city": "Beaver",
        "country_code": "US",
        "latitude": 38.277,
        "longitude": -112.641,
        "badge_tier": "legend",
        "languages": [{"language_code": "en", "proficiency": "native"}],
        "skills": [
            {"skill_name": "Electronics Engineering", "category": "electronics", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Vacuum Tube Technology", "category": "electronics", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Optics", "category": "science", "self_rating": 4, "years_experience": 30},
            {"skill_name": "Patent Litigation", "category": "education", "self_rating": 5, "years_experience": 25}
        ],
        "social_links": [],
        "points": {"total_points": 1950, "rentals_completed": 50, "reviews_given": 38, "reviews_received": 60, "items_listed": 7, "helpful_flags": 34},
        "offers_training": True,
        "items": [
            {"name": "Television History & Electronics Workshop", "slug": "television-history-electronics-workshop", "description": "How I built the first electronic TV. Electron beams, phosphor screens, scanning patterns. We will build a simple cathode ray demonstration and understand how 525 lines of light become a moving picture.", "item_type": "service", "category": "electronics", "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Oscilloscope (Analog, Teaching Model)", "slug": "oscilloscope-analog-teaching-model", "description": "Analog oscilloscope -- a cathode ray tube that draws electrical signals as visible waveforms. See your voice as a wave, see music as patterns. The oscilloscope is the engineer's eye.", "item_type": "physical", "category": "electronics", "listings": [{"listing_type": "rent", "price": 12.0, "price_unit": "per_day", "currency": "EUR", "deposit": 55.0}]},
            {"name": "Young Inventor Mentoring -- Potato Field to Patent", "slug": "young-inventor-mentoring-potato-field", "description": "One-on-one mentoring for young inventors. I was 14 in a potato field. The vision comes first; the engineering follows. I will help you develop your idea, document it properly, and avoid the mistakes I made with investors and corporations.", "item_type": "service", "category": "education", "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Soldering & Circuit Building Workshop", "slug": "soldering-circuit-building-workshop", "description": "Learn to solder, read circuit diagrams, and build a working electronic project. Through-hole components on perfboard. I built my first TV transmitter in a rented apartment. You will build something simpler but learn the same fundamental skill.", "item_type": "service", "category": "electronics", "listings": [{"listing_type": "training", "price": 14.0, "price_unit": "per_session", "currency": "EUR"}]}
        ]
    },

    # ============================================================
    # 30. ELI WHITNEY (1765-1825)
    # ============================================================
    {
        "slug": "whitneys-machine-shop",
        "display_name": "Eli Whitney",
        "email": "whitney@borrowhood.local",
        "date_of_birth": "1765-12-08",
        "mother_name": "Elizabeth Fay",
        "father_name": "Eli Whitney Sr.",
        "workshop_name": "Whitney's Machine Shop",
        "workshop_type": "workshop",
        "tagline": "One of my primary objects is to form the tools so the tools themselves shall fashion the work",
        "bio": "Born in Westborough, Massachusetts. At 14, I was manufacturing nails in my father's workshop. Graduated Yale at 27. On a Georgia plantation, I saw the labor of separating cotton seeds from fiber. Built the cotton gin in 10 days. Everyone copied it. Patents were unenforceable. The gin also tragically increased demand for slave labor. Later, I pioneered interchangeable parts for muskets -- any trigger fits any musket. Mass production before Ford. Tip: A simple invention is easy to copy. Protect with manufacturing advantage, not just patents. Also: consider second-order effects. The cotton gin made slavery more profitable. Intentions do not control consequences.",
        "telegram_username": "interchangeable",
        "city": "Westborough",
        "country_code": "US",
        "latitude": 42.269,
        "longitude": -71.616,
        "badge_tier": "legend",
        "languages": [{"language_code": "en", "proficiency": "native"}],
        "skills": [
            {"skill_name": "Manufacturing", "category": "engineering", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Tool Making", "category": "tools", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Mechanical Design", "category": "engineering", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Quality Control", "category": "engineering", "self_rating": 5, "years_experience": 25}
        ],
        "social_links": [],
        "points": {"total_points": 2050, "rentals_completed": 52, "reviews_given": 40, "reviews_received": 64, "items_listed": 7, "helpful_flags": 36},
        "offers_training": True,
        "items": [
            {"name": "Interchangeable Parts Workshop -- Birth of Mass Production", "slug": "interchangeable-parts-workshop", "description": "Small group (max 4). Make identical parts using jigs and fixtures, then assemble them randomly. Any part fits any assembly. This is the foundation of all modern manufacturing.", "item_type": "service", "category": "engineering", "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Woodworking Jig & Fixture Building", "slug": "woodworking-jig-fixture-building", "description": "Build a jig that produces identical parts every time. The jig transfers skill from craftsman to tool. A skilled worker makes one perfect piece. A jig lets anyone make a thousand.", "item_type": "service", "category": "tools", "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Metal Filing & Fitting -- Hand Precision", "slug": "metal-filing-fitting-hand-precision", "description": "Before machine tools, precision came from hand filing. File metal flat, square, and to dimension using a file, a square, and a surface plate. Patient, precise, and deeply satisfying.", "item_type": "service", "category": "tools", "listings": [{"listing_type": "training", "price": 14.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Complete Filing Set (Swiss, 12-Piece)", "slug": "complete-filing-set-swiss-12pc", "description": "Twelve Swiss-pattern files: flat, half-round, round, square, triangular, and knife -- in bastard and smooth cuts. Plus a file card for cleaning. Fundamental metalworking tools. With files and patience, you can make anything.", "item_type": "physical", "category": "tools", "listings": [{"listing_type": "rent", "price": 6.0, "price_unit": "per_day", "currency": "EUR", "deposit": 25.0}]},
            {"name": "Ethics of Invention -- Second-Order Effects", "slug": "ethics-invention-second-order-effects", "description": "The cotton gin was supposed to reduce labor. Instead it made slavery more profitable. Every invention has consequences the inventor did not intend. This seminar explores who benefits, who suffers, and how to think about responsibility.", "item_type": "service", "category": "education", "listings": [{"listing_type": "training", "price": 12.0, "price_unit": "per_session", "currency": "EUR"}]}
        ]
    },

    # ============================================================
    # 31. CHARLES DARWIN (1809-1882)
    # ============================================================
    {
        "slug": "darwins-study",
        "display_name": "Charles Robert Darwin",
        "email": "darwin@borrowhood.local",
        "date_of_birth": "1809-02-12",
        "mother_name": "Susannah Wedgwood",
        "father_name": "Robert Waring Darwin",
        "workshop_name": "Darwin's Study & Greenhouse",
        "workshop_type": "study",
        "tagline": "There is grandeur in this view of life",
        "bio": "Born in Shrewsbury, England. My father was a wealthy physician who thought I was destined for nothing. Dropped out of medical school because I could not stand surgery without anesthesia. Then sailed on the Beagle for five years. The Galapagos finches, the fossil record -- it all pointed to natural selection. I sat on the theory for 20 years, terrified. When Alfred Russel Wallace sent me a paper with the same idea, I finally published. On the Origin of Species, 1859. Tip: I spent eight years studying barnacles. Those barnacles taught me more about variation than any textbook. My friends Joseph Hooker and Thomas Huxley defended my work when I could not face the debates.",
        "telegram_username": "beagle_naturalist",
        "city": "Shrewsbury",
        "country_code": "GB",
        "latitude": 52.708,
        "longitude": -2.754,
        "badge_tier": "legend",
        "languages": [{"language_code": "en", "proficiency": "native"}],
        "skills": [
            {"skill_name": "Natural History", "category": "science", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Evolutionary Biology", "category": "science", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Taxonomy", "category": "science", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Geology", "category": "science", "self_rating": 4, "years_experience": 30}
        ],
        "social_links": [],
        "points": {"total_points": 2600, "rentals_completed": 66, "reviews_given": 52, "reviews_received": 78, "items_listed": 8, "helpful_flags": 46},
        "offers_training": True,
        "items": [
            {"name": "Natural Selection Workshop -- Evolution in Action", "slug": "natural-selection-evolution-action", "description": "Hands-on with specimens. Variation within species, selection pressure, adaptation. The fittest does not mean strongest -- it means best adapted. We examine bird beaks, shell shapes, and seed dispersal.", "item_type": "service", "category": "science", "listings": [{"listing_type": "training", "price": 16.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Specimen Collection Walk -- Observe Like Darwin", "slug": "specimen-collection-walk-observe", "description": "Guided nature walk focused on observation. Collect, label, and preserve specimens. My method: observe first, classify second, theorize third. Most people skip to theory. That is why most theories are wrong.", "item_type": "service", "category": "science", "listings": [{"listing_type": "training", "price": 12.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Dissecting Kit (Naturalist Grade)", "slug": "dissecting-kit-naturalist-grade", "description": "Complete dissecting kit: scalpels, forceps, scissors, pins, dissecting tray, magnifier. The tools I used to study barnacles for eight years. Comparative anatomy reveals evolutionary relationships.", "item_type": "physical", "category": "science", "listings": [{"listing_type": "rent", "price": 7.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0}]},
            {"name": "Scientific Journal Writing Workshop", "slug": "scientific-journal-writing-workshop", "description": "Small group (max 4). Write clear, persuasive scientific papers. On the Origin of Species is 490 pages of meticulous evidence before a single bold claim. Build your case like a lawyer. Present it like a storyteller.", "item_type": "service", "category": "education", "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Greenhouse Access (Orchid & Carnivorous Plants)", "slug": "greenhouse-orchid-carnivorous-plants", "description": "My greenhouse collection: orchids, carnivorous plants (sundews, Venus flytraps), and climbing plants. Observe adaptation in real time. The sundew catches insects with sticky tendrils. The orchid mimics a female wasp. Nature is more creative than any engineer.", "item_type": "physical", "category": "science", "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR"}]}
        ]
    },

    # ============================================================
    # 32. FLORENCE NIGHTINGALE (1820-1910)
    # ============================================================
    {
        "slug": "nightingales-ward",
        "display_name": "Florence Nightingale",
        "email": "nightingale@borrowhood.local",
        "date_of_birth": "1820-05-12",
        "mother_name": "Frances Smith",
        "father_name": "William Edward Nightingale",
        "workshop_name": "Nightingale's Ward & Statistical Office",
        "workshop_type": "study",
        "tagline": "I attribute my success to this: I never gave or took any excuse",
        "bio": "Born in Florence, Italy, to wealthy English parents -- hence the name. Felt a calling to nursing at 16. My family was horrified. In 1854, I took 38 nurses to the Crimean War. Scutari hospital was a death trap. I reduced the death rate from 42 percent to 2 percent through sanitation. Then changed the world with data. My polar area diagrams showed Parliament visually that sanitation saves lives. Tip: You cannot argue with a picture. Data presented visually is more persuasive than any speech. The real enemy is not disease -- it is bureaucratic indifference. My friend Sidney Herbert helped me get access to the army.",
        "telegram_username": "lady_with_lamp",
        "city": "Florence",
        "country_code": "IT",
        "latitude": 43.769,
        "longitude": 11.256,
        "badge_tier": "legend",
        "languages": [{"language_code": "en", "proficiency": "native"}, {"language_code": "fr", "proficiency": "fluent"}, {"language_code": "de", "proficiency": "conversational"}, {"language_code": "it", "proficiency": "conversational"}],
        "skills": [
            {"skill_name": "Nursing", "category": "science", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Statistics", "category": "science", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Hospital Management", "category": "education", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Data Visualization", "category": "education", "self_rating": 5, "years_experience": 35}
        ],
        "social_links": [],
        "points": {"total_points": 2500, "rentals_completed": 64, "reviews_given": 50, "reviews_received": 76, "items_listed": 8, "helpful_flags": 44},
        "offers_training": True,
        "items": [
            {"name": "Data Visualization Workshop -- Make Numbers Speak", "slug": "data-visualization-make-numbers-speak", "description": "I invented the polar area diagram to show Parliament that soldiers died from bad sanitation. Numbers in a table are ignorable. Numbers in a picture are undeniable. Bring your data. Leave with a visual argument.", "item_type": "service", "category": "education", "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "First Aid & Wound Care Training", "slug": "first-aid-wound-care-training", "description": "Wound cleaning, bandaging, splinting, infection prevention. Tip: Wash your hands. In 1854, army surgeons did not wash between patients. I made them. The death rate dropped 40 percent. Hygiene is not optional.", "item_type": "service", "category": "science", "listings": [{"listing_type": "training", "price": 14.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Hospital Sanitation Audit Toolkit", "slug": "hospital-sanitation-audit-toolkit", "description": "Checklist-based audit kit for any care facility: hand hygiene stations, ventilation, waste disposal, linen management, water quality. The same methodology I used at Scutari.", "item_type": "physical", "category": "science", "listings": [{"listing_type": "rent", "price": 8.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0}]},
            {"name": "Statistical Analysis for Beginners", "slug": "statistical-analysis-beginners-nightingale", "description": "One-on-one tutoring. First woman elected to the Royal Statistical Society. Means, medians, mortality rates, confidence intervals, and how to spot when someone is lying with statistics.", "item_type": "service", "category": "science", "listings": [{"listing_type": "training", "price": 16.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Healthcare Leadership -- Fighting Bureaucracy", "slug": "healthcare-leadership-fighting-bureaucracy", "description": "Small group (max 5). How to reform a system from within. Build alliances, collect irrefutable data, present visually, lobby relentlessly, and never take no from someone who lacks the authority to say yes.", "item_type": "service", "category": "education", "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]}
        ]
    },

    # ============================================================
    # 33. WERNER HEISENBERG (1901-1976)
    # ============================================================
    {
        "slug": "heisenbergs-uncertainty-lab",
        "display_name": "Werner Karl Heisenberg",
        "email": "heisenberg@borrowhood.local",
        "date_of_birth": "1901-12-05",
        "mother_name": "Annie Wecklein",
        "father_name": "August Heisenberg",
        "workshop_name": "Heisenberg's Uncertainty Laboratory",
        "workshop_type": "study",
        "tagline": "What we observe is not nature itself, but nature exposed to our method of questioning",
        "bio": "Born in Wuerzburg, Germany. My father was a professor of medieval Greek. At 23, I formulated matrix mechanics -- the first complete framework for quantum theory. At 25, the uncertainty principle: you cannot simultaneously know both exact position and exact momentum of a particle. This is not instrument limitation -- it is a fundamental property of nature. Won the Nobel at 31. Tip: The uncertainty principle applies beyond physics. In business, relationships, self-knowledge -- observing changes what is observed. Precision in one measurement costs precision in another. My teacher Niels Bohr became my greatest intellectual opponent. Argue with your mentors.",
        "telegram_username": "uncertain_werner",
        "city": "Wuerzburg",
        "country_code": "DE",
        "latitude": 49.794,
        "longitude": 9.929,
        "badge_tier": "legend",
        "languages": [{"language_code": "de", "proficiency": "native"}, {"language_code": "en", "proficiency": "fluent"}],
        "skills": [
            {"skill_name": "Quantum Mechanics", "category": "science", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Theoretical Physics", "category": "science", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Mathematics", "category": "science", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Philosophy of Science", "category": "education", "self_rating": 5, "years_experience": 40}
        ],
        "social_links": [],
        "points": {"total_points": 2350, "rentals_completed": 60, "reviews_given": 46, "reviews_received": 72, "items_listed": 7, "helpful_flags": 42},
        "offers_training": True,
        "items": [
            {"name": "Quantum Mechanics for Non-Physicists", "slug": "quantum-mechanics-non-physicists", "description": "Two-hour session. Superposition, uncertainty, wave-particle duality, entanglement using analogies and demonstrations. Quantum mechanics is strange but the most precisely tested theory in science. Your phone uses it.", "item_type": "service", "category": "science", "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Double-Slit Experiment Kit (Laser & Detector)", "slug": "double-slit-experiment-kit-laser", "description": "Laser pointer, precision double slit, screen, and single-photon detector. Fire photons one at a time through two slits. They create an interference pattern as if each photon went through both slits. This will break your intuition. Good.", "item_type": "physical", "category": "science", "listings": [{"listing_type": "rent", "price": 15.0, "price_unit": "per_day", "currency": "EUR", "deposit": 70.0}]},
            {"name": "Philosophy of Science Seminar -- What Can We Know", "slug": "philosophy-science-what-can-we-know", "description": "Small group (max 5). The uncertainty principle is epistemology. What does it mean to measure? What does it mean to know? Bohr, Einstein, Bell -- the arguments are unresolved. The questions are eternal.", "item_type": "service", "category": "education", "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Advanced Physics Tutoring -- Quantum Theory", "slug": "advanced-physics-tutoring-quantum", "description": "One-on-one. Schrodinger equation, matrix mechanics, perturbation theory, angular momentum. Prerequisite: calculus and linear algebra. Not easy. But beautiful.", "item_type": "service", "category": "science", "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]}
        ]
    },

    # ============================================================
    # 34. JOSEPH LISTER (1827-1912)
    # ============================================================
    {
        "slug": "listers-antiseptic-ward",
        "display_name": "Joseph Lister",
        "email": "lister@borrowhood.local",
        "date_of_birth": "1827-04-05",
        "mother_name": "Isabella Harris",
        "father_name": "Joseph Jackson Lister",
        "workshop_name": "Lister's Antiseptic Surgery Ward",
        "workshop_type": "laboratory",
        "tagline": "Since the antiseptic treatment has been brought into full operation, my wards have completely changed their character",
        "bio": "Born in Upton, Essex, England. My father was a wine merchant and amateur microscopist who improved the achromatic lens. Became professor of surgery at Glasgow. Surgical mortality from infection ran 45 to 50 percent. Surgeons operated in street clothes with unwashed hands. I read Pasteur on germ theory and started using carbolic acid to sterilize wounds, instruments, and dressings. Mortality dropped to 15 percent. Surgeons fought me for years -- the suggestion their hands were dirty was an insult. Tip: When people resist your evidence, it is because accepting it means admitting they have been doing harm. Be persistent. Let the mortality statistics speak. Pasteur gave me the theory. Nightingale and I approached the same problem from different angles.",
        "telegram_username": "antiseptic_joe",
        "city": "Upton",
        "country_code": "GB",
        "latitude": 51.553,
        "longitude": 0.002,
        "badge_tier": "legend",
        "languages": [{"language_code": "en", "proficiency": "native"}, {"language_code": "fr", "proficiency": "conversational"}],
        "skills": [
            {"skill_name": "Surgery", "category": "science", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Antiseptic Technique", "category": "science", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Microbiology", "category": "science", "self_rating": 4, "years_experience": 30},
            {"skill_name": "Medical Education", "category": "education", "self_rating": 5, "years_experience": 40}
        ],
        "social_links": [],
        "points": {"total_points": 2250, "rentals_completed": 58, "reviews_given": 44, "reviews_received": 70, "items_listed": 7, "helpful_flags": 40},
        "offers_training": True,
        "items": [
            {"name": "Sterile Technique Workshop -- Infection Prevention", "slug": "sterile-technique-infection-prevention", "description": "Hands-on aseptic technique: surgical scrub, gloving, draping, instrument sterilization, wound cleaning. Before carbolic acid, half of surgical patients died from infection. Surgeons operated in frock coats stiff with dried blood.", "item_type": "service", "category": "science", "listings": [{"listing_type": "training", "price": 16.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Surgical Instrument Set (Educational, Stainless)", "slug": "surgical-instrument-set-educational-ss", "description": "Educational surgical instruments: scalpel handles, forceps, scissors, needle holders, retractors, hemostats. Stainless steel, autoclavable. For anatomy study and dissection practice.", "item_type": "physical", "category": "science", "listings": [{"listing_type": "rent", "price": 12.0, "price_unit": "per_day", "currency": "EUR", "deposit": 55.0}]},
            {"name": "History of Medicine -- From Barbarism to Antisepsis", "slug": "history-medicine-barbarism-antisepsis", "description": "Surgery before and after germ theory. Sawing limbs without anesthesia, 50 percent mortality. Then Pasteur, carbolic acid, sterile technique. A single idea -- germs cause infection -- saved more lives than any drug. Semmelweis figured it out before me and they drove him to madness.", "item_type": "service", "category": "education", "listings": [{"listing_type": "training", "price": 12.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Microscopy Workshop -- Seeing Germs", "slug": "microscopy-workshop-seeing-germs-lister", "description": "Hands-on microscopy. Prepare slides, stain bacteria, observe microorganisms that cause infection. My father improved the microscope lens. I used the improved microscope to see what was killing surgical patients. One generation builds the tool, the next uses it.", "item_type": "service", "category": "science", "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]},
            {"name": "Evidence-Based Practice -- Convince the Skeptics", "slug": "evidence-based-practice-convince-skeptics", "description": "Small group (max 5). Introduce new practices into resistant institutions. Collect before-and-after data, present clearly, find early adopters, publish results, and never argue with ego -- argue with mortality rates.", "item_type": "service", "category": "education", "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]}
        ]
    },
]


def merge_into_seed():
    """Merge inventor legends into seed.json."""
    import json
    from pathlib import Path

    seed_path = Path(__file__).parent / "seed.json"
    with open(seed_path) as f:
        data = json.load(f)

    existing_slugs = {u["slug"] for u in data["users"]}
    existing_item_slugs = {i["slug"] for i in data["items"]}

    added_users = 0
    added_items = 0
    for legend in LEGENDS_INVENTORS:
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
                    added_items += 1

    with open(seed_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Inventors: Added {added_users} new legend users")
    print(f"Inventors: Added {added_items} items for inventor legends")
    print(f"Total users: {len(data['users'])}")
    print(f"Total items: {len(data['items'])}")


if __name__ == "__main__":
    merge_into_seed()
