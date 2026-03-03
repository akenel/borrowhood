"""Cinema legends seed data for BorrowHood.

34 movie stars, directors, and screenwriters -- each with a workshop full of
items to rent, lend, or teach. From Bruce Lee's dojo to Fellini's dream studio.

Chaplin is already in legends.py -- NOT duplicated here.

Run: python seed_data/legends_cinema.py
Output: merges into seed_data/seed.json
"""

LEGENDS_CINEMA = [
    # ------------------------------------------------------------------
    # 1. BRUCE LEE (1940-1973)
    # ------------------------------------------------------------------
    {
        "slug": "bruces-dojo",
        "display_name": "Bruce Lee",
        "email": "bruce.lee@borrowhood.local",
        "date_of_birth": "1940-11-27",
        "mother_name": "Grace Ho",
        "father_name": "Lee Hoi-chuen",
        "workshop_name": "Bruce's Dojo",
        "workshop_type": "studio",
        "tagline": "Be water, my friend",
        "bio": "Born in San Francisco, raised in Hong Kong. I studied Wing Chun under Ip Man, then created Jeet Kune Do -- the style of no style. Tip: The best technique is no technique. Absorb what is useful, reject what is useless, add what is specifically your own. I was a philosophy student at the University of Washington before Hollywood noticed. Every fight scene I choreographed was a lesson in efficiency -- no wasted movement. I taught Steve McQueen, James Coburn, and Kareem Abdul-Jabbar. My one-inch punch generated more force than most people's full swing. The key? Structure, speed, and total commitment.",
        "telegram_username": "the_dragon",
        "city": "San Francisco",
        "country_code": "US",
        "latitude": 37.774,
        "longitude": -122.419,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "zh", "proficiency": "native"},
            {"language_code": "en", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Jeet Kune Do", "category": "sports", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Film Choreography", "category": "art", "self_rating": 5, "years_experience": 15},
            {"skill_name": "Philosophy", "category": "education", "self_rating": 5, "years_experience": 15},
            {"skill_name": "Wing Chun", "category": "sports", "self_rating": 5, "years_experience": 20}
        ],
        "social_links": [],
        "points": {"total_points": 2200, "rentals_completed": 60, "reviews_given": 45, "reviews_received": 70, "items_listed": 8, "helpful_flags": 40},
        "offers_training": True,
        "items": [
            {
                "name": "Jeet Kune Do Private Lesson -- The Art of Fighting Without Fighting",
                "slug": "jkd-private-lesson",
                "description": "One-on-one martial arts training. We focus on YOUR body, YOUR speed, YOUR reach. I don't teach you to fight like me. I teach you to fight like the best version of you. Footwork, trapping, striking -- and the philosophy behind every movement.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Wing Chun Wooden Dummy (Mook Jong)",
                "slug": "wing-chun-wooden-dummy-mook-jong",
                "description": "Traditional wooden dummy for Wing Chun training. 108 movements. It teaches you angles, deflection, and structure. The dummy doesn't lie -- if your form is wrong, your wrists will tell you.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 8.0, "price_unit": "per_day", "currency": "EUR", "deposit": 40.0}]
            },
            {
                "name": "Nunchaku Set (Training Foam + Competition Wood)",
                "slug": "nunchaku-training-competition-set",
                "description": "Foam pair for learning, hardwood pair for performance. I made these famous but they're actually an Okinawan farming tool. Start with the foam. Trust me.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 4.0, "price_unit": "per_day", "currency": "EUR"}]
            },
            {
                "name": "Philosophy of Martial Arts Workshop -- Small Group",
                "slug": "philosophy-martial-arts-workshop",
                "description": "Small group session (max 6). We discuss Tao Te Ching, Krishnamurti, and the connection between combat and self-knowledge. Tip: Knowing is not enough, you must apply. Willing is not enough, you must do. Bring a notebook.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 12.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Film Fight Choreography Session",
                "slug": "film-fight-choreography-session",
                "description": "Learn to design fight scenes for camera. Real combat is ugly. Screen combat is poetry. I'll show you camera angles, timing, and how to sell a punch that misses by six inches. Every fight tells a story -- what's yours?",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    # ------------------------------------------------------------------
    # 2. SYD FIELD (1935-2013)
    # ------------------------------------------------------------------
    {
        "slug": "syds-screenplay-lab",
        "display_name": "Syd Field",
        "email": "syd.field@borrowhood.local",
        "date_of_birth": "1935-12-19",
        "mother_name": "Bea Field",
        "father_name": "Paul Field",
        "workshop_name": "Syd's Screenplay Lab",
        "workshop_type": "studio",
        "tagline": "Structure is the foundation of all good screenwriting",
        "bio": "Born in Hollywood, California -- literally grew up in the shadow of the studios. I worked with Jean Renoir at the Neighborhood Playhouse and studied with Sam Peckinpah. Tip: Every screenplay has a beginning, middle, and end -- but not necessarily in that order. What matters is the paradigm: Act I sets it up, Act II confronts it, Act III resolves it. Plot Point 1 hits around page 25. Plot Point 2 around page 85. I didn't invent structure -- I revealed the structure that was already there in every great film from Casablanca to Chinatown. James Cameron, Thelma Schoonmaker, and Frank Pierson all used my method. I taught at USC, UCLA, Harvard, and in 30 countries. My book Screenplay has been translated into 27 languages. Every screenwriter alive has either read it or read someone who read it.",
        "telegram_username": "paradigm_syd",
        "city": "Los Angeles",
        "country_code": "US",
        "latitude": 34.052,
        "longitude": -118.244,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Screenwriting", "category": "art", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Story Structure", "category": "education", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Script Analysis", "category": "art", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Teaching", "category": "education", "self_rating": 5, "years_experience": 35}
        ],
        "social_links": [],
        "points": {"total_points": 2100, "rentals_completed": 55, "reviews_given": 50, "reviews_received": 65, "items_listed": 7, "helpful_flags": 38},
        "offers_training": True,
        "items": [
            {
                "name": "The Paradigm Workshop -- 3-Act Structure Masterclass",
                "slug": "paradigm-workshop-3act-structure",
                "description": "The workshop that changed screenwriting worldwide. In four hours, I break down the three-act structure using your favorite films. You'll never watch a movie the same way again. Bring a film you love and I'll show you its skeleton. Tip: The first ten pages are everything -- that's where the reader decides to keep going or toss your script.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 30.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Script Coverage & Notes -- Professional Feedback",
                "slug": "script-coverage-professional-notes",
                "description": "Send me your screenplay (120 pages max). I'll read it, write detailed notes on structure, character, and dialogue, and return a 3-page coverage report. I've read over 2,000 screenplays for Cinemobile Systems and another 2,000 for the Royal Swedish Film Institute. I know what works.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "service", "price": 40.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Screenplay by Syd Field (Annotated Copy)",
                "slug": "screenplay-syd-field-annotated",
                "description": "My personal annotated copy of Screenplay -- the book that's been called the bible of screenwriting. Margin notes from 30 years of teaching. Dog-eared pages. Coffee stains from late nights at Musso & Frank. Read it, return it, write your script.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 3.0, "price_unit": "per_day", "currency": "EUR"}]
            },
            {
                "name": "Character Development Workshop -- Who Is Your Hero?",
                "slug": "character-development-workshop-hero",
                "description": "A screenplay is only as good as its main character. In this workshop we build characters from the inside out: dramatic need, point of view, attitude, change. I'll make you answer four questions about your protagonist that will unlock your entire story.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Classic Screenplay Collection (Bound Scripts)",
                "slug": "classic-screenplay-collection-bound",
                "description": "Bound shooting scripts of Chinatown, Annie Hall, Thelma & Louise, American Beauty, and The Shawshank Redemption. These are the scripts I used in my workshops for decades. Read them with a highlighter. Study how they handle plot points. Tip: Read scripts, not books about scripts.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR"}]
            }
        ]
    },
    # ------------------------------------------------------------------
    # 3. CHUCK NORRIS (1940-)
    # ------------------------------------------------------------------
    {
        "slug": "chucks-training-compound",
        "display_name": "Chuck Norris",
        "email": "chuck.norris@borrowhood.local",
        "date_of_birth": "1940-03-10",
        "mother_name": "Wilma Scarberry",
        "father_name": "Ray Norris",
        "workshop_name": "Chuck's Training Compound",
        "workshop_type": "garage",
        "tagline": "I don't initiate violence. I retaliate.",
        "bio": "Born Carlos Ray Norris in Ryan, Oklahoma. Grew up dirt poor -- my father was an alcoholic who left the family. I was shy and average at everything until the Air Force sent me to Osan Air Base in South Korea, where I discovered Tang Soo Do. That changed my life. I became a six-time undefeated World Professional Middleweight Karate Champion. Tip: A black belt is a white belt who never quit. Bruce Lee was my friend and sparring partner -- we trained together and fought on screen in Way of the Dragon. I founded Chun Kuk Do and UFAF. Total Gym isn't just a product, it's the machine I actually use every morning at 5am. I'm in my 80s and I still train.",
        "telegram_username": "walker_texas",
        "city": "Ryan",
        "country_code": "US",
        "latitude": 34.011,
        "longitude": -97.956,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "ko", "proficiency": "intermediate"}
        ],
        "skills": [
            {"skill_name": "Tang Soo Do", "category": "sports", "self_rating": 5, "years_experience": 60},
            {"skill_name": "Chun Kuk Do", "category": "sports", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Action Film Acting", "category": "art", "self_rating": 4, "years_experience": 40},
            {"skill_name": "Brazilian Jiu-Jitsu", "category": "sports", "self_rating": 4, "years_experience": 30}
        ],
        "social_links": [],
        "points": {"total_points": 2050, "rentals_completed": 58, "reviews_given": 42, "reviews_received": 68, "items_listed": 7, "helpful_flags": 36},
        "offers_training": True,
        "items": [
            {
                "name": "Tang Soo Do Fundamentals -- From White to Green Belt",
                "slug": "tang-soo-do-fundamentals",
                "description": "Traditional Korean martial arts training. We start with basic stances, blocks, and kicks. No flashy nonsense -- just solid technique that works. I'll teach the same forms I learned at Osan Air Base in 1958. Tip: Your roundhouse kick should come from the hip, not the knee. Most beginners kick with their leg. Champions kick with their whole body.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Heavy Bag (100lb Leather) + Speed Bag Station",
                "slug": "heavy-bag-speed-bag-station",
                "description": "Professional-grade heavy bag and speed bag mounted on a steel frame. The heavy bag teaches power. The speed bag teaches timing. Use both. I hit these every morning before sunrise and have since 1962.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 6.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0}]
            },
            {
                "name": "Total Gym XLS (The Machine That Actually Works)",
                "slug": "total-gym-xls",
                "description": "The same Total Gym model I use personally. Over 80 exercises on one machine using your own body weight. Incline bench, cable pulls, squats, core work. I'm not just the spokesman -- I've used this thing every day for 30 years.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 10.0, "price_unit": "per_day", "currency": "EUR", "deposit": 60.0}]
            },
            {
                "name": "Action Scene Workshop -- How to Throw a Punch on Camera",
                "slug": "action-scene-workshop-punch-camera",
                "description": "Film fighting is NOT real fighting. I'll teach you camera angles, pull distances, reaction timing, and how to sell a hit. We'll choreograph a 30-second fight scene by the end of the session. Bruce Lee taught me the value of screen combat efficiency -- I'm passing it on.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Board Breaking Kit (Pine + Rebreakable Plastic)",
                "slug": "board-breaking-kit-pine-plastic",
                "description": "Stack of 1-inch pine boards plus rebreakable plastic boards in 5 difficulty levels. Tip: Breaking boards is not about strength. It's about focus, follow-through, and believing your hand goes THROUGH the board, not TO it.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 4.0, "price_unit": "per_day", "currency": "EUR"}]
            }
        ]
    },
    # ------------------------------------------------------------------
    # 4. MARLON BRANDO (1924-2004)
    # ------------------------------------------------------------------
    {
        "slug": "brandos-method-room",
        "display_name": "Marlon Brando",
        "email": "marlon.brando@borrowhood.local",
        "date_of_birth": "1924-04-03",
        "mother_name": "Dorothy Pennebaker Brando",
        "father_name": "Marlon Brando Sr.",
        "workshop_name": "Brando's Method Room",
        "workshop_type": "studio",
        "tagline": "An actor is at most a poet and at least an entertainer",
        "bio": "Born in Omaha, Nebraska. My mother was an actress in the Omaha Community Playhouse -- she taught young Henry Fonda. My father was a salesman who drank. I was expelled from military school for insubordination. Best decision I never made. Stella Adler changed everything. She didn't teach you to play a character -- she taught you to BECOME one. I studied with her, not Strasberg. That's an important distinction. Tip: Don't act. React. Listen to the other actor. The most powerful moments on screen happen between the lines, not during them. Elia Kazan directed me in Streetcar and On the Waterfront. Coppola gave me the Godfather when nobody in Hollywood would touch me. I put cotton in my cheeks for that audition. Nobody asked me to -- I just knew that's what Vito Corleone's jaw looked like.",
        "telegram_username": "the_contender",
        "city": "Omaha",
        "country_code": "US",
        "latitude": 41.256,
        "longitude": -95.934,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "fr", "proficiency": "intermediate"}
        ],
        "skills": [
            {"skill_name": "Method Acting", "category": "art", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Character Transformation", "category": "art", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Improvisation", "category": "art", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Script Analysis", "category": "art", "self_rating": 5, "years_experience": 40}
        ],
        "social_links": [],
        "points": {"total_points": 2150, "rentals_completed": 52, "reviews_given": 38, "reviews_received": 72, "items_listed": 7, "helpful_flags": 42},
        "offers_training": True,
        "items": [
            {
                "name": "Method Acting Intensive -- Becoming the Character",
                "slug": "method-acting-intensive-brando",
                "description": "Two-hour session. We don't rehearse lines -- we build a life. Where did your character grow up? What does their kitchen smell like? What song makes them cry? Once you know that, the lines say themselves. Stella Adler's approach: imagination over memory. Tip: If you're thinking about acting, you're not acting.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 35.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Scene Study Workshop -- Reacting, Not Acting",
                "slug": "scene-study-reacting-not-acting",
                "description": "Bring a scene partner. We work two scenes in two hours. I watch, I redirect, I provoke. Most actors prepare what they're going to say. Wrong. Prepare to LISTEN. The other actor's lines should change something in you every single time.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 28.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Stella Adler's Acting Technique (First Edition)",
                "slug": "stella-adler-acting-technique-first-ed",
                "description": "Stella Adler's own handbook, first edition. She studied with Stanislavski in Paris -- the only American actor who did. This book is the foundation. Strasberg got the attention, but Adler got the method right.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 4.0, "price_unit": "per_day", "currency": "EUR"}]
            },
            {
                "name": "Makeup & Prosthetics Kit -- Physical Transformation",
                "slug": "makeup-prosthetics-kit-brando",
                "description": "The kit I used to age myself for the Godfather screen test. Spirit gum, cotton balls, dental plumpers, hairpieces, and scar wax. Your face is clay. Tip: Physical transformation starts a chain reaction -- change your jaw and your voice changes, your posture shifts, the character emerges from the body outward.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 6.0, "price_unit": "per_day", "currency": "EUR"}]
            },
            {
                "name": "Improvisation for Film Actors -- Finding the Moment",
                "slug": "improv-film-actors-finding-moment",
                "description": "Film improv is not comedy improv. It's about being so deeply in character that when the script breaks, you don't. The 'I coulda been a contender' speech in On the Waterfront -- half of that was written, half was felt. Learn to blur the line.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    # ------------------------------------------------------------------
    # 5. AUDREY HEPBURN (1929-1993)
    # ------------------------------------------------------------------
    {
        "slug": "audreys-atelier",
        "display_name": "Audrey Hepburn",
        "email": "audrey.hepburn@borrowhood.local",
        "date_of_birth": "1929-05-04",
        "mother_name": "Ella van Heemstra",
        "father_name": "Joseph Victor Anthony Ruston",
        "workshop_name": "Audrey's Atelier",
        "workshop_type": "studio",
        "tagline": "Elegance is the only beauty that never fades",
        "bio": "Born Audrey Kathleen Ruston in Ixelles, Brussels. I survived the Nazi occupation of the Netherlands -- we ate tulip bulbs and grass to stay alive. I trained as a ballet dancer with Sonia Gaskell in Amsterdam and Marie Rambert in London before Colette herself spotted me and cast me in Gigi on Broadway. Tip: Elegance is not about what you put on, it's about what you leave out. Givenchy became my partner in style -- we created Holly Golightly's little black dress together. I won the Oscar, Emmy, Grammy, and Tony. But my real work was UNICEF. I spent my last years in the field -- Ethiopia, Sudan, Somalia, Vietnam. The children taught me more than any director ever did. Billy Wilder said I could make any scene better just by walking into the room. I think the room was already fine -- I just noticed it.",
        "telegram_username": "holly_golightly",
        "city": "Brussels",
        "country_code": "BE",
        "latitude": 50.827,
        "longitude": 4.365,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "nl", "proficiency": "native"},
            {"language_code": "fr", "proficiency": "fluent"},
            {"language_code": "it", "proficiency": "fluent"},
            {"language_code": "es", "proficiency": "intermediate"}
        ],
        "skills": [
            {"skill_name": "Screen Acting", "category": "art", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Ballet", "category": "sports", "self_rating": 4, "years_experience": 20},
            {"skill_name": "Humanitarian Advocacy", "category": "education", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Fashion & Style", "category": "art", "self_rating": 5, "years_experience": 40}
        ],
        "social_links": [],
        "points": {"total_points": 2300, "rentals_completed": 65, "reviews_given": 55, "reviews_received": 80, "items_listed": 8, "helpful_flags": 50},
        "offers_training": True,
        "items": [
            {
                "name": "Screen Presence Workshop -- Less Is Everything",
                "slug": "screen-presence-workshop-less-is-everything",
                "description": "I teach you what Billy Wilder taught me: the camera sees everything you're thinking. You don't need to show it -- you need to FEEL it. We work on stillness, listening, and the art of the reaction shot. Tip: Most young actors try to DO too much. Stop doing. Start being.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 30.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Ballet Fundamentals for Actors -- Grace in Motion",
                "slug": "ballet-fundamentals-actors-grace",
                "description": "Four positions, posture, and how to walk like you own the room. I studied ballet to be a dancer, but it made me an actress. Every movement on screen is a dance -- even sitting down. Sonia Gaskell would say: the spine tells the story.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Givenchy Little Black Dress (Replica, Size 6)",
                "slug": "givenchy-lbd-replica",
                "description": "Museum-quality replica of the Breakfast at Tiffany's dress. Hubert made the original for me in 1961. This one is for costume research, photo shoots, or just feeling invincible for an evening. Handle with care -- it's lined in silk.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 15.0, "price_unit": "per_day", "currency": "EUR", "deposit": 100.0}]
            },
            {
                "name": "Opera-Length Gloves & Tiara Set (Tiffany's Costume Kit)",
                "slug": "opera-gloves-tiara-tiffanys-kit",
                "description": "Black satin opera-length gloves, rhinestone tiara, and oversized sunglasses. The complete Holly Golightly look. Tip: Accessories don't complete an outfit. They complete a character.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 8.0, "price_unit": "per_day", "currency": "EUR", "deposit": 40.0}]
            },
            {
                "name": "Humanitarian Storytelling Workshop -- Making the World Listen",
                "slug": "humanitarian-storytelling-workshop",
                "description": "How to tell stories that move people to action. I learned this at UNICEF -- you can show a million statistics and nothing changes. Show one child's face and the whole world responds. We work on narrative, photography, and the courage to witness.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    # ------------------------------------------------------------------
    # 6. HUMPHREY BOGART (1899-1957)
    # ------------------------------------------------------------------
    {
        "slug": "bogarts-gin-joint",
        "display_name": "Humphrey Bogart",
        "email": "humphrey.bogart@borrowhood.local",
        "date_of_birth": "1899-12-25",
        "mother_name": "Maud Humphrey",
        "father_name": "Belmont DeForest Bogart",
        "workshop_name": "Bogart's Gin Joint",
        "workshop_type": "studio",
        "tagline": "Here's looking at you, kid",
        "bio": "Born on Christmas Day in New York City. My mother was a successful illustrator -- she drew me as the Gerber baby model, though I never lived that down. Phillips Academy expelled me. The Navy gave me the scar on my lip -- a prisoner hit me with handcuffs during a transfer. That scar gave me my lisp, and that lisp gave me my voice. Tip: The less you try to charm an audience, the more they follow you. Just tell the truth quietly. I worked 20 years in Hollywood before Casablanca. Twenty years of B-pictures and thankless roles. John Huston finally saw what I could do and gave me The Maltese Falcon. Lauren Bacall taught me to whistle. I taught her everything else. The Rat Pack was my living room -- Sinatra, Garland, Niven, all of them. We drank too much and laughed too loud. I regret nothing.",
        "telegram_username": "rick_blaine",
        "city": "New York",
        "country_code": "US",
        "latitude": 40.713,
        "longitude": -74.006,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Film Noir Acting", "category": "art", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Sailing", "category": "sports", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Screen Presence", "category": "art", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Chess", "category": "education", "self_rating": 4, "years_experience": 40}
        ],
        "social_links": [],
        "points": {"total_points": 1950, "rentals_completed": 48, "reviews_given": 40, "reviews_received": 62, "items_listed": 6, "helpful_flags": 35},
        "offers_training": True,
        "items": [
            {
                "name": "Film Noir Acting Workshop -- The Art of the Anti-Hero",
                "slug": "film-noir-acting-workshop-antihero",
                "description": "I teach you to play the guy who's seen too much but still does the right thing. Noir isn't about shadows -- it's about moral ambiguity. We work on understatement, world-weariness, and how to deliver a line like you've been thinking it for years. Tip: Never raise your voice when lowering it works better.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Trench Coat & Fedora (Screen-Accurate Casablanca Set)",
                "slug": "trench-coat-fedora-casablanca-set",
                "description": "Aquascutum trench coat and Borsalino fedora. The exact combination I wore as Rick Blaine. Tip: A costume isn't what the character wears -- it's what the character would choose to wear. Rick chose armor that looks like elegance.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 10.0, "price_unit": "per_day", "currency": "EUR", "deposit": 60.0}]
            },
            {
                "name": "Chess Set (Tournament Grade Staunton)",
                "slug": "chess-set-tournament-staunton-bogart",
                "description": "I played chess on every set I ever worked on. Between takes, between scenes, during lunch. It teaches you to think three moves ahead -- exactly what an actor needs. This is a regulation Staunton set with a roll-up vinyl board. I'll play you a game if you rent it.",
                "item_type": "physical",
                "category": "education",
                "listings": [{"listing_type": "rent", "price": 3.0, "price_unit": "per_day", "currency": "EUR"}]
            },
            {
                "name": "On-Camera Dialogue Coaching -- Making Every Word Count",
                "slug": "on-camera-dialogue-coaching-bogart",
                "description": "Most actors read lines. I teach you to THROW lines -- like darts. Short, sharp, landed. We study Casablanca, The Big Sleep, and The Maltese Falcon. Tip: The audience should feel like they're overhearing you, not listening to you.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    # ------------------------------------------------------------------
    # 7. MARILYN MONROE (1926-1962)
    # ------------------------------------------------------------------
    {
        "slug": "marilyns-mirror-room",
        "display_name": "Marilyn Monroe",
        "email": "marilyn.monroe@borrowhood.local",
        "date_of_birth": "1926-06-01",
        "mother_name": "Gladys Pearl Baker",
        "father_name": "Charles Stanley Gifford",
        "workshop_name": "Marilyn's Mirror Room",
        "workshop_type": "studio",
        "tagline": "Imperfection is beauty, madness is genius",
        "bio": "Born Norma Jeane Mortenson in Los Angeles. Twelve foster homes before I turned sixteen. I stuttered as a child -- acting was how I learned to speak without fear. Everyone thinks I was discovered. I wasn't. I studied. Lee Strasberg at the Actors Studio. Michael Chekhov for technique. Natasha Lytess for voice. Tip: Comedy is harder than drama. In drama you cry and they believe you. In comedy your timing has to be perfect or they stare at you. Some Like It Hot took 47 takes for one scene -- not because I couldn't do it, but because Billy Wilder and I disagreed on which take was funniest. I was right. I also co-founded my own production company, Marilyn Monroe Productions, in 1955 -- one of the first actresses to do so. They called me a dumb blonde. I was reading Dostoevsky on set.",
        "telegram_username": "sugar_kane",
        "city": "Los Angeles",
        "country_code": "US",
        "latitude": 34.052,
        "longitude": -118.244,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Comedy Acting", "category": "art", "self_rating": 5, "years_experience": 15},
            {"skill_name": "Method Acting", "category": "art", "self_rating": 5, "years_experience": 10},
            {"skill_name": "Singing", "category": "music", "self_rating": 4, "years_experience": 12},
            {"skill_name": "Modeling & Camera Work", "category": "art", "self_rating": 5, "years_experience": 18}
        ],
        "social_links": [],
        "points": {"total_points": 2000, "rentals_completed": 50, "reviews_given": 42, "reviews_received": 75, "items_listed": 7, "helpful_flags": 38},
        "offers_training": True,
        "items": [
            {
                "name": "Comedy Timing Workshop -- The Art of the Pause",
                "slug": "comedy-timing-workshop-pause",
                "description": "Comedy lives in the silence between lines. I teach you where to breathe, where to look, and where to let the audience catch up. We study Some Like It Hot and Gentlemen Prefer Blondes frame by frame. Tip: If you're rushing the punchline, you don't trust the joke.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Camera Confidence Workshop -- Owning the Lens",
                "slug": "camera-confidence-owning-the-lens",
                "description": "The camera is not your enemy. It's your best friend -- the one who sees everything and forgives everything. I teach you how to find your light, your angle, and your truth. We work with a live camera feed so you can see yourself the way the audience sees you.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Vintage Pin-Up Photography Lighting Kit",
                "slug": "vintage-pin-up-photography-lighting-kit",
                "description": "Three-point lighting setup from the golden age of Hollywood glamour. Key light, fill light, backlight, plus a butterfly diffuser for that soft, luminous look. This is how they shot me, Garbo, and Dietrich. Tip: The backlight is the secret -- it separates you from the background and makes your hair glow.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 12.0, "price_unit": "per_day", "currency": "EUR", "deposit": 50.0}]
            },
            {
                "name": "Singing Coaching -- Finding Your Breathy Best",
                "slug": "singing-coaching-breathy-best",
                "description": "I sang Happy Birthday to a president and Diamonds Are a Girl's Best Friend to the world. My voice wasn't perfect -- it was MINE. I teach you to stop imitating and start expressing. We work on breath control, phrasing, and emotional delivery. You don't need range. You need truth.",
                "item_type": "service",
                "category": "music",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Method Acting Books (Strasberg + Chekhov Collection)",
                "slug": "method-acting-books-strasberg-chekhov",
                "description": "My personal copies of Strasberg's Dream of Passion and Chekhov's To the Actor. Annotated in my handwriting. These are the two books that made me a real actress instead of just a movie star. Read both -- they contradict each other and that's the point.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 4.0, "price_unit": "per_day", "currency": "EUR"}]
            }
        ]
    },
    # ------------------------------------------------------------------
    # 8. SIDNEY POITIER (1927-2022)
    # ------------------------------------------------------------------
    {
        "slug": "sidneys-stage",
        "display_name": "Sidney Poitier",
        "email": "sidney.poitier@borrowhood.local",
        "date_of_birth": "1927-02-20",
        "mother_name": "Evelyn Outten",
        "father_name": "Reginald James Poitier",
        "workshop_name": "Sidney's Stage",
        "workshop_type": "studio",
        "tagline": "I made a decision not to accept the limitation society placed on me",
        "bio": "Born premature in Miami while my parents were visiting from Cat Island, Bahamas. I grew up in the Bahamas until fifteen, then moved to Miami alone with one dollar and a half. I washed dishes in New York and read the newspaper classified ads to teach myself to read English properly. An elderly Jewish waiter spent months helping me lose my Bahamian accent. I auditioned for the American Negro Theatre and they laughed me out. I came back six months later and they took me. Tip: Dignity is not a performance. It is a decision you make before you walk on set. I was the first Black man to win the Academy Award for Best Actor -- Lilies of the Field, 1964. I didn't win it for Black people. I won it for ALL the people who were told they couldn't. Harry Belafonte was my brother in arms. We marched with Dr. King. We put our careers on the line. I would do it again.",
        "telegram_username": "mr_tibbs",
        "city": "Miami",
        "country_code": "US",
        "latitude": 25.761,
        "longitude": -80.192,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Dramatic Acting", "category": "art", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Film Directing", "category": "art", "self_rating": 4, "years_experience": 25},
            {"skill_name": "Public Speaking", "category": "education", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Stage Acting", "category": "art", "self_rating": 5, "years_experience": 55}
        ],
        "social_links": [],
        "points": {"total_points": 2250, "rentals_completed": 62, "reviews_given": 50, "reviews_received": 78, "items_listed": 7, "helpful_flags": 45},
        "offers_training": True,
        "items": [
            {
                "name": "Commanding the Room -- Presence and Dignity on Screen",
                "slug": "commanding-the-room-presence-dignity",
                "description": "I teach you to walk into a scene and own it without raising your voice or clenching your fist. Power isn't volume. It's stillness when everyone else is shouting. We work on posture, eye contact, and the silence between words. Tip: Before you say your first line, stand still for three seconds. Let the audience come to you.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 28.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Dialect & Accent Coaching -- From Caribbean to Classical",
                "slug": "dialect-accent-coaching-caribbean-classical",
                "description": "I rebuilt my voice from a thick Bahamian accent to classical American diction. I can teach you to do the same with any accent. We work on vowel placement, consonant precision, and rhythm. The goal isn't to erase where you're from -- it's to choose how you sound for each role.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Film Directing Fundamentals -- Telling the Story Through the Lens",
                "slug": "film-directing-fundamentals-poitier",
                "description": "I directed nine films. The trick is knowing what the camera should see versus what the audience should feel. Those are often different things. We work on shot selection, actor direction, and visual storytelling. Bring a short script and we'll storyboard it together.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 30.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Autobiography Collection (The Measure of a Man + This Life)",
                "slug": "autobiography-collection-poitier",
                "description": "Both my memoirs. The Measure of a Man won the Grammy for spoken word. This Life tells the full story -- Cat Island, the tomato fields, dishwashing in Harlem, and every role that mattered. Read them in order.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 3.0, "price_unit": "per_day", "currency": "EUR"}]
            },
            {
                "name": "Public Speaking Masterclass -- The Voice That Cannot Be Ignored",
                "slug": "public-speaking-voice-cannot-be-ignored",
                "description": "Whether you're addressing a boardroom or a protest march, your voice must carry conviction. I'll teach you pacing, breath control, and how to land a sentence so it stays in the room after you've left. Harry and I spoke at the March on Washington. The microphone helps, but the message does the work.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    # ------------------------------------------------------------------
    # 9. TOSHIRO MIFUNE (1920-1997)
    # ------------------------------------------------------------------
    {
        "slug": "mifunes-sword-hall",
        "display_name": "Toshiro Mifune",
        "email": "toshiro.mifune@borrowhood.local",
        "date_of_birth": "1920-04-01",
        "mother_name": "Sen Mifune",
        "father_name": "Tokuzo Mifune",
        "workshop_name": "Mifune's Sword Hall",
        "workshop_type": "studio",
        "tagline": "The sword is an extension of the soul",
        "bio": "Born in Qingdao, China to Japanese parents. My father was a photographer and Methodist missionary. I grew up speaking Mandarin and Japanese. The Imperial Army drafted me as an aerial photographer in World War II. After the war I stumbled into a Toho Studios audition by accident -- a friend dragged me along. Akira Kurosawa saw something wild in me. We made sixteen films together. Rashomon introduced Japanese cinema to the world. Seven Samurai changed how every action film is made. Tip: A sword fight is a conversation. Every cut, every parry, every breath tells the audience who these people are and what they fear. George Lucas based Han Solo on my bandit in The Hidden Fortress. Sergio Leone modeled the Man With No Name after my ronin in Yojimbo. I never went to acting school. The camera just believed me.",
        "telegram_username": "ronin_mifune",
        "city": "Qingdao",
        "country_code": "CN",
        "latitude": 36.067,
        "longitude": 120.383,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "ja", "proficiency": "native"},
            {"language_code": "zh", "proficiency": "fluent"}
        ],
        "skills": [
            {"skill_name": "Samurai Swordsmanship", "category": "sports", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Physical Acting", "category": "art", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Horseback Riding", "category": "sports", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Photography", "category": "art", "self_rating": 4, "years_experience": 30}
        ],
        "social_links": [],
        "points": {"total_points": 2100, "rentals_completed": 55, "reviews_given": 40, "reviews_received": 68, "items_listed": 7, "helpful_flags": 38},
        "offers_training": True,
        "items": [
            {
                "name": "Samurai Screen Combat Workshop -- The Way of the Blade",
                "slug": "samurai-screen-combat-workshop",
                "description": "Katana work for film. Proper draw, strike, and resheath. We use bokken (wooden swords) first, then move to iaito (blunt steel). I'll teach you the difference between real kenjutsu and what looks good on camera. Kurosawa insisted on realism -- the audience can feel a fake swing. Tip: Speed comes from relaxation, not tension.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Bokken Set (Oak Practice Swords, Pair)",
                "slug": "bokken-set-oak-practice-swords",
                "description": "Two red oak bokken -- standard katana length. These are the training weapons I used before every Kurosawa film. They teach you distance, timing, and respect for the blade. Tip: If you're gripping too tight, you're already losing.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR"}]
            },
            {
                "name": "Physical Acting Masterclass -- The Body Tells the Story",
                "slug": "physical-acting-masterclass-mifune",
                "description": "I never went to acting school. I learned by doing. My body was my instrument -- the way I scratched, squatted, spat, laughed. Kurosawa once told me to watch how animals move. A tiger doesn't announce itself. It moves, and you KNOW it's a tiger. We work on physicality, gesture, and primal energy.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Samurai Armor Set (Reproduction Do, Kabuto, Menpo)",
                "slug": "samurai-armor-reproduction-set",
                "description": "Full reproduction samurai armor: chest plate (do), helmet (kabuto), and face guard (menpo). I wore gear like this in Throne of Blood and Samurai Trilogy. It changes how you stand, walk, and breathe. Tip: Wear it for an hour before filming -- let your body adapt so the armor disappears.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 15.0, "price_unit": "per_day", "currency": "EUR", "deposit": 80.0}]
            },
            {
                "name": "Japanese Film History Screening & Discussion",
                "slug": "japanese-film-history-screening",
                "description": "We watch one of my films with Kurosawa -- Rashomon, Seven Samurai, Yojimbo, or Ikiru -- and I break down every choice. Camera placement, performance decisions, what was improvised, what was argued about. Small group, max 8. Bring sake or tea.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    # ------------------------------------------------------------------
    # 10. AKIRA KUROSAWA (1910-1998)
    # ------------------------------------------------------------------
    {
        "slug": "kurosawas-editing-room",
        "display_name": "Akira Kurosawa",
        "email": "akira.kurosawa@borrowhood.local",
        "date_of_birth": "1910-03-23",
        "mother_name": "Shima Kurosawa",
        "father_name": "Isamu Kurosawa",
        "workshop_name": "Kurosawa's Editing Room",
        "workshop_type": "studio",
        "tagline": "To be an artist means never to avert one's eyes",
        "bio": "Born in Shinagawa, Tokyo. My father was an army officer and athleticism director who believed in both martial discipline and Western cinema -- he took us to films every week. My older brother Heigo was a benshi, a silent film narrator, and his suicide in 1933 shaped my understanding of tragedy forever. I trained as a painter before entering cinema as an assistant director at PCL Studios. Tip: Edit with a razor blade and trust your instincts. If a scene feels slow, it IS slow -- cut it. I edited all my own films. Spielberg called me the Shakespeare of cinema. George Lucas and Francis Ford Coppola helped fund my later films when Japanese studios wouldn't. Toshiro Mifune was my instrument for sixteen films -- I composed, he performed. Seven Samurai took a year to shoot and nearly bankrupted Toho. It became the most influential action film ever made. Every heist movie, every team-assembles story, every last-stand battle owes me a drink.",
        "telegram_username": "emperor_kurosawa",
        "city": "Tokyo",
        "country_code": "JP",
        "latitude": 35.676,
        "longitude": 139.650,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "ja", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Film Directing", "category": "art", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Film Editing", "category": "art", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Painting & Storyboarding", "category": "art", "self_rating": 5, "years_experience": 60},
            {"skill_name": "Screenwriting", "category": "art", "self_rating": 5, "years_experience": 50}
        ],
        "social_links": [],
        "points": {"total_points": 2350, "rentals_completed": 64, "reviews_given": 48, "reviews_received": 82, "items_listed": 8, "helpful_flags": 48},
        "offers_training": True,
        "items": [
            {
                "name": "Film Directing Masterclass -- Composing with the Camera",
                "slug": "film-directing-masterclass-kurosawa",
                "description": "I teach directing the way I learned painting -- through composition. Where is the eye drawn? What is the relationship between foreground and background? We use storyboards, not shot lists. Every frame should be a painting that moves. Tip: Use multiple cameras. Actors perform differently when they don't know which camera is live.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 35.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Storyboard Workshop -- Drawing Your Film Before You Shoot",
                "slug": "storyboard-workshop-kurosawa",
                "description": "I painted full-color storyboards for every scene in my later films -- Kagemusha, Ran, Dreams. They're works of art on their own. You don't need to be a great painter. You need to THINK visually. We work with watercolors and ink. Bring your script and we'll draw your film.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 28.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Film Editing Workshop -- The Invisible Art",
                "slug": "film-editing-workshop-invisible-art",
                "description": "Editing is where the film is truly made. I'll show you how a two-second cut changes everything -- mood, pace, meaning. We work with actual footage. I cut on a Moviola for forty years. Digital is faster but the principles are eternal: rhythm, contrast, surprise. Tip: The best cut is the one the audience doesn't notice.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Watercolor & Ink Set (Kurosawa's Storyboard Kit)",
                "slug": "watercolor-ink-storyboard-kit-kurosawa",
                "description": "Professional watercolor set, sumi ink, and 50 sheets of storyboard paper with the frame templates I used. This is the exact setup for the Ran storyboards now in museums. Tip: Use big brushes. Small brushes make you fussy. Cinema is bold.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 6.0, "price_unit": "per_day", "currency": "EUR"}]
            },
            {
                "name": "Kurosawa Film Library (Criterion Collection Box Set)",
                "slug": "kurosawa-criterion-collection-box",
                "description": "Twenty-five films on Blu-ray. Rashomon through Madadayo. Every film has commentary tracks and my own notes. Watch them in order and you'll see an artist evolve over fifty years. Start with Stray Dog if you want noir. Start with Ikiru if you want to cry.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR"}]
            }
        ]
    },
    # ------------------------------------------------------------------
    # 11. ALFRED HITCHCOCK (1899-1980)
    # ------------------------------------------------------------------
    {
        "slug": "hitchcocks-suspense-lab",
        "display_name": "Alfred Hitchcock",
        "email": "alfred.hitchcock@borrowhood.local",
        "date_of_birth": "1899-08-13",
        "mother_name": "Emma Jane Whelan",
        "father_name": "William Hitchcock",
        "workshop_name": "Hitchcock's Suspense Lab",
        "workshop_type": "studio",
        "tagline": "There is no terror in the bang, only in the anticipation of it",
        "bio": "Born in Leytonstone, East London. My father was a greengrocer. When I was five, he sent me to the local police station with a note. The officer locked me in a cell for ten minutes and said, 'This is what we do to naughty boys.' I have been afraid of the police -- and fascinated by fear -- ever since. I studied engineering at the London County Council School of Engineering and Navigation, then worked at Henley's drawing title cards for silent films. Tip: The difference between suspense and surprise is information. Surprise is a bomb going off. Suspense is showing the audience the bomb under the table while the characters eat lunch. I made 53 films. Psycho, Vertigo, Rear Window, North by Northwest, The Birds. Francois Truffaut spent a week interviewing me -- that book taught more about filmmaking than most film schools. I never won a Best Director Oscar. That tells you everything about the Oscars.",
        "telegram_username": "master_of_suspense",
        "city": "London",
        "country_code": "GB",
        "latitude": 51.569,
        "longitude": 0.015,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Film Directing", "category": "art", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Suspense & Thriller Craft", "category": "art", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Storyboarding", "category": "art", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Screenwriting", "category": "art", "self_rating": 5, "years_experience": 50}
        ],
        "social_links": [],
        "points": {"total_points": 2400, "rentals_completed": 68, "reviews_given": 52, "reviews_received": 85, "items_listed": 8, "helpful_flags": 50},
        "offers_training": True,
        "items": [
            {
                "name": "Suspense Filmmaking Masterclass -- The Bomb Under the Table",
                "slug": "suspense-filmmaking-masterclass-hitchcock",
                "description": "I'll teach you to terrify an audience without showing them anything. We study the shower scene in Psycho (70 cuts, no knife-on-skin contact), the crop duster in North by Northwest (silence is scarier than music), and the dinner party in Rope (one continuous take). Tip: Always give the audience more information than the characters have. That's where suspense lives.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 35.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Storyboard & Shot Planning Workshop",
                "slug": "storyboard-shot-planning-hitchcock",
                "description": "I planned every frame before we rolled camera. By the time we shot, the film was already made -- the set was just a formality. We'll storyboard a five-minute suspense sequence from your script. Every shot has a PURPOSE. If it doesn't build tension, cut it.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 28.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Hitchcock/Truffaut (First Edition, Hardcover)",
                "slug": "hitchcock-truffaut-first-edition",
                "description": "The definitive book on filmmaking. Truffaut asked me 500 questions over five days. Every answer is a masterclass. This is the first American edition, 1967. Dog-eared at the Vertigo chapter because everyone always goes there first.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR"}]
            },
            {
                "name": "Film Score Analysis Workshop -- Music as Fear",
                "slug": "film-score-analysis-music-as-fear",
                "description": "Bernard Herrmann wrote the Psycho strings, the Vertigo spirals, and the North by Northwest overture. Without his music, my films are half as terrifying. We study how music creates dread, release, and the false sense of safety. Tip: The scariest sound in cinema is silence followed by a single note.",
                "item_type": "service",
                "category": "music",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "MacGuffin Writing Kit (Plot Device Workshop Materials)",
                "slug": "macguffin-writing-kit",
                "description": "Cards, prompts, and exercises for creating compelling plot devices. The MacGuffin is the thing the characters care about but the audience doesn't -- it's the excuse for the story, not the story itself. The Maltese Falcon is a MacGuffin. The uranium in Notorious is a MacGuffin. The real story is always about people.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 3.0, "price_unit": "per_day", "currency": "EUR"}]
            }
        ]
    },
    # ------------------------------------------------------------------
    # 12. STANLEY KUBRICK (1928-1999)
    # ------------------------------------------------------------------
    {
        "slug": "kubricks-control-room",
        "display_name": "Stanley Kubrick",
        "email": "stanley.kubrick@borrowhood.local",
        "date_of_birth": "1928-07-26",
        "mother_name": "Sadie Gertrude Perveler",
        "father_name": "Jacques Leonard Kubrick",
        "workshop_name": "Kubrick's Control Room",
        "workshop_type": "studio",
        "tagline": "A film is -- or should be -- more like music than like fiction",
        "bio": "Born in the Bronx, New York. My father was a doctor who gave me a camera at thirteen and a chess set at twelve. Both shaped everything. I was a terrible student but I could see. Look Magazine hired me as a staff photographer at seventeen. I learned composition, lighting, and timing with a still camera before I ever touched film. Tip: Master one thing at a time. I learned photography first, then editing, then directing. Each skill builds on the last. Never skip steps. I made thirteen films in forty years. Dr. Strangelove, 2001: A Space Odyssey, A Clockwork Orange, The Shining, Full Metal Jacket. Each one was a different genre because repetition is creative death. I did more takes than anyone -- sometimes 70, sometimes 100. Not because the actors were wrong but because I was looking for something I couldn't describe until I saw it. Shelley Duvall did 127 takes of the baseball bat scene in The Shining. The exhaustion you see is real. That's the shot.",
        "telegram_username": "room_237",
        "city": "New York",
        "country_code": "US",
        "latitude": 40.851,
        "longitude": -73.866,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Film Directing", "category": "art", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Cinematography", "category": "art", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Photography", "category": "art", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Chess", "category": "education", "self_rating": 5, "years_experience": 50}
        ],
        "social_links": [],
        "points": {"total_points": 2350, "rentals_completed": 60, "reviews_given": 35, "reviews_received": 80, "items_listed": 8, "helpful_flags": 45},
        "offers_training": True,
        "items": [
            {
                "name": "Cinematography Masterclass -- Light Is Everything",
                "slug": "cinematography-masterclass-kubrick",
                "description": "Barry Lyndon was lit entirely by candlelight using a NASA lens. The Shining used Steadicam before anyone knew what Steadicam was. 2001 invented front-projection on a scale nobody had attempted. We study how to light a scene so it tells the story before anyone speaks. Tip: Natural light is almost always better than artificial. Learn to see it first.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 35.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Photography Fundamentals -- Seeing Before Shooting",
                "slug": "photography-fundamentals-kubrick",
                "description": "I was a Look Magazine photographer before I was a filmmaker. Still photography teaches you composition in ways no film school can. One frame. One moment. No second chances. We shoot on the street with 35mm cameras. Tip: The subject is never the subject. The LIGHT on the subject is the subject.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "35mm Film Camera (Arriflex IIC)",
                "slug": "arriflex-iic-35mm-camera",
                "description": "The same model I used for Paths of Glory and Spartacus. Pin-registered gate, crystal sync motor. This camera taught me everything about exposure, framing, and the cost of mistakes (film stock isn't cheap). Comes with three prime lenses: 25mm, 50mm, and 85mm.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 20.0, "price_unit": "per_day", "currency": "EUR", "deposit": 150.0}]
            },
            {
                "name": "Chess Strategy Session (Tournament Level)",
                "slug": "chess-strategy-session-kubrick",
                "description": "I played chess in Washington Square Park for money as a teenager. It taught me to think five moves ahead -- which is exactly what directing is. We play and I teach you to see patterns. Tip: In chess and filmmaking, the opening determines everything. Control the center early.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Kubrick Film Library (Every Film on 4K UHD)",
                "slug": "kubrick-film-library-4k-uhd",
                "description": "All thirteen features restored in 4K. From Fear and Desire (1953) to Eyes Wide Shut (1999). Watch them in order and you'll see a photographer become the most visually precise director who ever lived. Start with Paths of Glory -- it's the most underrated antiwar film ever made.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR"}]
            }
        ]
    },
    # ------------------------------------------------------------------
    # 13. KATHARINE HEPBURN (1907-2003)
    # ------------------------------------------------------------------
    {
        "slug": "kates-rehearsal-barn",
        "display_name": "Katharine Hepburn",
        "email": "katharine.hepburn@borrowhood.local",
        "date_of_birth": "1907-05-12",
        "mother_name": "Katharine Martha Houghton",
        "father_name": "Thomas Norval Hepburn",
        "workshop_name": "Kate's Rehearsal Barn",
        "workshop_type": "studio",
        "tagline": "If you obey all the rules, you miss all the fun",
        "bio": "Born in Hartford, Connecticut. My father was a urologist and my mother was a suffragette who marched with Emmeline Pankhurst. They raised me to think, to swim in cold water, and to never apologize for having an opinion. Bryn Mawr College gave me the education and the accent. I won four Academy Awards for Best Actress -- no one else has more than three. Spencer Tracy was my partner for twenty-seven years and nine films. He never left his wife and I never asked him to. Tip: The trick to acting is not acting at all. Just be truthful in imaginary circumstances. Hollywood called me box office poison in 1938. I bought out my own contract, went to Broadway, did The Philadelphia Story, and came back on my own terms. They wanted me to be decorative. I wore trousers. They wanted me to be quiet. I swam in the Long Island Sound every morning until I was ninety. Life is for living, not for auditioning.",
        "telegram_username": "kate_the_great",
        "city": "Hartford",
        "country_code": "US",
        "latitude": 41.763,
        "longitude": -72.685,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "fr", "proficiency": "intermediate"}
        ],
        "skills": [
            {"skill_name": "Dramatic Acting", "category": "art", "self_rating": 5, "years_experience": 65},
            {"skill_name": "Stage Acting", "category": "art", "self_rating": 5, "years_experience": 65},
            {"skill_name": "Comedy Acting", "category": "art", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Swimming", "category": "sports", "self_rating": 4, "years_experience": 80}
        ],
        "social_links": [],
        "points": {"total_points": 2250, "rentals_completed": 62, "reviews_given": 48, "reviews_received": 76, "items_listed": 7, "helpful_flags": 44},
        "offers_training": True,
        "items": [
            {
                "name": "Stage-to-Screen Acting Workshop -- Projecting Without Shouting",
                "slug": "stage-to-screen-acting-workshop-kate",
                "description": "I started on Broadway and moved to Hollywood. The transition destroys most actors -- they're either too big for camera or too small for stage. I teach you to calibrate. Same truth, different volume. Tip: On stage, your eyes reach the back row. On camera, your thoughts do.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 28.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Comedy of Equals Workshop -- Screwball Technique",
                "slug": "comedy-of-equals-screwball-technique",
                "description": "Bringing Up Baby and The Philadelphia Story are screwball comedies -- the man and woman are EQUALS in wit, speed, and stubbornness. I teach rapid-fire dialogue, physical comedy with dignity, and how to win an argument on screen while making the audience love both sides.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Cold-Water Swimming Coaching -- Morning Discipline",
                "slug": "cold-water-swimming-coaching-kate",
                "description": "I swam in the Long Island Sound every morning, year-round, into my nineties. Cold water wakes up everything -- your body, your mind, your courage. I'll teach you to breathe, to enter the water without flinching, and to find the joy in discomfort. Tip: The first thirty seconds are terrible. After that, you're alive.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 10.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Golden Age Script Collection (12 Bound Screenplays)",
                "slug": "golden-age-script-collection-kate",
                "description": "Bound scripts from my best films: The Philadelphia Story, African Queen, Guess Who's Coming to Dinner, The Lion in Winter, Bringing Up Baby, and more. Tracy used to say reading the script was my religion. He was right. Study these. Then throw them away and find your own truth.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR"}]
            }
        ]
    },
    # ------------------------------------------------------------------
    # 14. BETTE DAVIS (1908-1989)
    # ------------------------------------------------------------------
    {
        "slug": "bettes-dressing-room",
        "display_name": "Bette Davis",
        "email": "bette.davis@borrowhood.local",
        "date_of_birth": "1908-04-05",
        "mother_name": "Ruth Augusta Favor",
        "father_name": "Harlow Morrell Davis",
        "workshop_name": "Bette's Dressing Room",
        "workshop_type": "studio",
        "tagline": "Fasten your seatbelts, it's going to be a bumpy night",
        "bio": "Born Ruth Elizabeth Davis in Lowell, Massachusetts. My father walked out when I was seven. My mother became a portrait photographer to support us -- she taught me that a woman works and doesn't wait. I studied at John Murray Anderson's Dramatic School alongside Lucille Ball. Universal Studios told me I had 'as much sex appeal as Slim Summerville.' I framed that letter. Tip: Use your eyes. The camera lives in the eyes. Your body, your voice -- those are supporting players. Your eyes are the lead. I was the first woman to receive ten Academy Award nominations. I fought Warner Brothers for better roles and they suspended me. I fought them in court and lost. Then they gave me the roles because they knew I was right. Joan Crawford and I despised each other. That was real. But What Ever Happened to Baby Jane? wouldn't have worked without real venom.",
        "telegram_username": "bette_eyes",
        "city": "Lowell",
        "country_code": "US",
        "latitude": 42.633,
        "longitude": -71.316,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Dramatic Acting", "category": "art", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Villainous Roles", "category": "art", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Eye Acting", "category": "art", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Voice & Delivery", "category": "art", "self_rating": 5, "years_experience": 50}
        ],
        "social_links": [],
        "points": {"total_points": 2050, "rentals_completed": 54, "reviews_given": 44, "reviews_received": 66, "items_listed": 6, "helpful_flags": 36},
        "offers_training": True,
        "items": [
            {
                "name": "Dramatic Intensity Workshop -- Eyes That Burn Through the Screen",
                "slug": "dramatic-intensity-workshop-davis",
                "description": "I teach you to hold a close-up. Most actors blink, shift, fidget. Stop. Be STILL. Let the camera come to your eyes and STAY there. We do exercises in sustained intensity -- thirty seconds of pure emotion without a word. Tip: If you can't hold a close-up for ten seconds, you're not ready for film.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 28.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Playing the Villain -- Making Evil Magnetic",
                "slug": "playing-the-villain-evil-magnetic",
                "description": "My best roles were women the audience shouldn't root for -- and did anyway. Margo Channing, Baby Jane Hudson, Regina Giddens. The secret? Villains believe they're the hero. Play their conviction, not their cruelty. We build three-dimensional antagonists in this workshop.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Vintage Cigarette Holder & Prop Kit",
                "slug": "vintage-cigarette-holder-prop-kit-davis",
                "description": "Art deco cigarette holders (long and short), prop cigarettes, and a lighter. I used cigarettes as punctuation marks -- a drag for emphasis, a flick for dismissal, a crush for rage. Props are an actor's secret weapon. This kit teaches you to use objects as extensions of emotion.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 4.0, "price_unit": "per_day", "currency": "EUR"}]
            },
            {
                "name": "Voice & Delivery Workshop -- Every Syllable Is a Weapon",
                "slug": "voice-delivery-workshop-davis",
                "description": "My voice was my signature. Clipped, precise, weaponized. I teach you to use rhythm, pause, and emphasis to make every line land. We work on monologues from All About Eve and The Little Foxes. Tip: Slow down. The audience hangs on the pause, not the word.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Golden Age Hollywood Costume Jewelry Collection",
                "slug": "golden-age-costume-jewelry-davis",
                "description": "Rhinestone brooches, chandelier earrings, cocktail rings -- all screen-used replicas from the 1940s-1960s era. Each piece tells a story about the character who wore it. Borrow for period shoots, photo sessions, or just feeling dangerous.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 6.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0}]
            }
        ]
    },
    # ------------------------------------------------------------------
    # 15. ORSON WELLES (1915-1985)
    # ------------------------------------------------------------------
    {
        "slug": "welles-radio-tower",
        "display_name": "Orson Welles",
        "email": "orson.welles@borrowhood.local",
        "date_of_birth": "1915-05-06",
        "mother_name": "Beatrice Ives",
        "father_name": "Richard Head Welles",
        "workshop_name": "Welles' Radio Tower",
        "workshop_type": "studio",
        "tagline": "If you want a happy ending, that depends on where you stop your story",
        "bio": "Born in Kenosha, Wisconsin. My mother was a concert pianist. My father was an inventor and adventurer. I was declared a genius at age two -- the press loved it, and I've been trying to live it down ever since. I directed my first play at sixteen and convinced the Gate Theatre in Dublin I was a Broadway star at fifteen. Nobody checked. Tip: The most powerful tool in filmmaking is the low angle. Point the camera up at someone and they become a god. Point it down and they become a victim. Citizen Kane was my first film. I was twenty-five. RKO gave me final cut and I didn't know enough to be afraid. The deep focus, the ceilings on sets, the overlapping dialogue -- I did those because I didn't know the rules yet. Gregg Toland, the cinematographer, taught me everything in three days. John Houseman produced my Mercury Theatre radio broadcast of War of the Worlds. We accidentally made a million people believe Martians had invaded New Jersey. Hemingway said I was the greatest American living. He was drunk, but he wasn't wrong.",
        "telegram_username": "citizen_orson",
        "city": "Kenosha",
        "country_code": "US",
        "latitude": 42.584,
        "longitude": -87.821,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "es", "proficiency": "intermediate"}
        ],
        "skills": [
            {"skill_name": "Film Directing", "category": "art", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Radio Drama", "category": "art", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Stage Directing", "category": "art", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Voice Acting", "category": "art", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Magic & Illusion", "category": "art", "self_rating": 4, "years_experience": 35}
        ],
        "social_links": [],
        "points": {"total_points": 2200, "rentals_completed": 56, "reviews_given": 42, "reviews_received": 74, "items_listed": 7, "helpful_flags": 40},
        "offers_training": True,
        "items": [
            {
                "name": "Deep Focus Cinematography Workshop -- Everything in Focus at Once",
                "slug": "deep-focus-cinematography-workshop-welles",
                "description": "Gregg Toland taught me this for Citizen Kane: keep the foreground AND background sharp. It forces the audience to choose where to look -- and that choice IS the story. We study lens selection, lighting for depth, and staging in three dimensions. Tip: When everything is in focus, composition becomes your only guide.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 30.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Radio Drama Production Workshop -- Theatre of the Mind",
                "slug": "radio-drama-production-workshop-welles",
                "description": "No picture. No set. Just voices, sound effects, and the listener's imagination. I panicked a nation with War of the Worlds using nothing but a microphone and clever editing. Radio drama is the purest form of storytelling. We write, record, and produce a 10-minute piece in one session.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Professional Condenser Microphone (RCA 44-BX Ribbon)",
                "slug": "rca-44bx-ribbon-microphone-welles",
                "description": "The same model microphone I used for Mercury Theatre broadcasts. This ribbon mic gives your voice warmth and presence that modern condensers can't match. Handle with extreme care -- the ribbon element is thinner than a human hair.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 12.0, "price_unit": "per_day", "currency": "EUR", "deposit": 80.0}]
            },
            {
                "name": "Magic & Misdirection Workshop -- The Art of Deception",
                "slug": "magic-misdirection-workshop-welles",
                "description": "I performed magic my entire life -- for troops in WWII, on talk shows, and between takes on set. Magic teaches you about attention, misdirection, and the willingness of people to believe. Every filmmaker is a magician. We learn card magic, cups and balls, and the psychology behind why people see what you want them to see.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Citizen Kane Annotated Shooting Script",
                "slug": "citizen-kane-annotated-shooting-script",
                "description": "The shooting script with my margin notes. Every camera angle, every lighting note, every argument with Herman Mankiewicz documented in red ink. This is the most studied film in cinema. This is its blueprint. Read it with the film paused beside you.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR"}]
            }
        ]
    },
    # ------------------------------------------------------------------
    # 16. JACKIE CHAN (1954-)
    # ------------------------------------------------------------------
    {
        "slug": "jackies-stunt-gym",
        "display_name": "Jackie Chan",
        "email": "jackie.chan@borrowhood.local",
        "date_of_birth": "1954-04-07",
        "mother_name": "Lee-Lee Chan",
        "father_name": "Charles Chan",
        "workshop_name": "Jackie's Stunt Gym",
        "workshop_type": "garage",
        "tagline": "Do not let circumstances control you. You change your circumstances.",
        "bio": "Born Chan Kong-sang in Victoria Peak, Hong Kong. My parents were so poor they almost sold me to the British doctor who delivered me. Instead, my father enrolled me in the China Drama Academy at age six. Master Yu Jim-yuen trained us in Peking Opera -- acrobatics, martial arts, singing, and acting. It was brutal. We trained eighteen hours a day. Sammo Hung and Yuen Biao were my classmates -- we became the Three Brothers. Tip: Comedy and pain are the same thing. When I fall off a building, you laugh because I get up. If I didn't get up, you'd cry. Timing is everything. I've broken my nose three times, my ankle once, most of my fingers, my cheekbone, and my skull. I do my own stunts because the audience knows the difference. Bruce Lee showed that a Chinese man could be a hero. I showed he could also be funny. Every Hollywood stunt coordinator has studied my work. I always show the outtakes during credits -- the audience deserves to see the cost.",
        "telegram_username": "jackie_stunts",
        "city": "Hong Kong",
        "country_code": "HK",
        "latitude": 22.278,
        "longitude": 114.175,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "zh", "proficiency": "native"},
            {"language_code": "en", "proficiency": "fluent"},
            {"language_code": "ko", "proficiency": "intermediate"},
            {"language_code": "ja", "proficiency": "intermediate"}
        ],
        "skills": [
            {"skill_name": "Kung Fu Comedy", "category": "sports", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Stunt Coordination", "category": "sports", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Peking Opera", "category": "art", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Acrobatics", "category": "sports", "self_rating": 5, "years_experience": 55}
        ],
        "social_links": [],
        "points": {"total_points": 2300, "rentals_completed": 65, "reviews_given": 50, "reviews_received": 78, "items_listed": 8, "helpful_flags": 44},
        "offers_training": True,
        "items": [
            {
                "name": "Kung Fu Comedy Workshop -- Fighting and Falling with Style",
                "slug": "kung-fu-comedy-workshop-jackie",
                "description": "I'll teach you to take a hit, sell a fall, and make the audience laugh while you're in pain. We use chairs, ladders, and tables as props -- everything in the room is a weapon and a punchline. Tip: Always show the whole body. Wide shots let the audience see the skill. Close-ups are for actors who can't fight.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Stunt Safety & Fall Training Workshop",
                "slug": "stunt-safety-fall-training-jackie",
                "description": "Before you can do a stunt, you need to know how to fall. We cover breakfalls, rolls, wall hits, and stair tumbles on mats. I've broken nearly every bone in my body -- YOU don't have to. Safety isn't about being careful. It's about being PREPARED. We drill until the landing is automatic.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Crash Mats & Safety Pads (Full Stunt Kit)",
                "slug": "crash-mats-safety-pads-stunt-kit",
                "description": "Eight crash mats in various sizes, knee pads, elbow pads, and a body harness. This is the safety equipment my stunt team uses for medium-height falls and wall work. Tip: Never do a stunt for the first time on camera. Rehearse until the fear becomes respect.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 10.0, "price_unit": "per_day", "currency": "EUR", "deposit": 50.0}]
            },
            {
                "name": "Prop Weapons Collection (Breakaway Chairs, Rubber Bottles, Foam Pipes)",
                "slug": "prop-weapons-breakaway-collection",
                "description": "Sugar glass bottles, balsa wood chairs, foam pipes, rubber bricks -- everything you need for a prop fight scene. I've used more chairs as weapons than any actor in history. They break beautifully on camera and barely sting in person. Barely.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 8.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0}]
            },
            {
                "name": "Acrobatics Fundamentals -- Flips, Rolls, and Wall Runs",
                "slug": "acrobatics-fundamentals-flips-rolls",
                "description": "Peking Opera trained me in acrobatics from age six. I teach forward rolls, backward rolls, cartwheels, wall runs, and basic flips -- all on safety mats. You don't need to be young. You need to be willing. Sammo Hung and I still warm up with these moves. Tip: Your hands and feet should never land at the same time.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    # ------------------------------------------------------------------
    # 17. CLINT EASTWOOD (1930-)
    # ------------------------------------------------------------------
    {
        "slug": "eastwoods-ranch",
        "display_name": "Clint Eastwood",
        "email": "clint.eastwood@borrowhood.local",
        "date_of_birth": "1930-05-31",
        "mother_name": "Ruth Runner",
        "father_name": "Clinton Eastwood Sr.",
        "workshop_name": "Eastwood's Ranch",
        "workshop_type": "garage",
        "tagline": "A man's got to know his limitations",
        "bio": "Born in San Francisco during the Depression. My family moved constantly -- my father chased work as a steelworker and salesman. I was drafted into the Army, survived a plane crash into the Pacific off Point Reyes, swam three miles to shore. That changes your perspective on everything. Sergio Leone cast me in A Fistful of Dollars because I was cheap and available. Three Dollars More and The Good, The Bad and The Ugly made me an icon. Tip: Less is more. The Man With No Name barely speaks and the audience can't look away. In directing, I rarely do more than two takes. Actors give their best work when they're not exhausted. I learned that by watching Don Siegel work -- fast, clean, no wasted motion. I've directed over forty films. Unforgiven, Million Dollar Baby, Letters from Iwo Jima. I compose the music for my own films now. Piano, mostly. Jazz is structured improvisation -- just like good filmmaking.",
        "telegram_username": "no_name_man",
        "city": "San Francisco",
        "country_code": "US",
        "latitude": 37.774,
        "longitude": -122.419,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "it", "proficiency": "intermediate"}
        ],
        "skills": [
            {"skill_name": "Film Directing", "category": "art", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Screen Acting", "category": "art", "self_rating": 5, "years_experience": 65},
            {"skill_name": "Film Composing", "category": "music", "self_rating": 4, "years_experience": 30},
            {"skill_name": "Jazz Piano", "category": "music", "self_rating": 4, "years_experience": 40}
        ],
        "social_links": [],
        "points": {"total_points": 2280, "rentals_completed": 63, "reviews_given": 45, "reviews_received": 76, "items_listed": 7, "helpful_flags": 42},
        "offers_training": True,
        "items": [
            {
                "name": "Minimalist Film Directing Workshop -- Two Takes and Print",
                "slug": "minimalist-directing-workshop-eastwood",
                "description": "I direct fast and quiet. No yelling, no ego, no fiftieth take. We shoot a short scene with available light, two cameras, and maximum two takes per setup. Tip: Trust your actors. Hire good people and get out of their way. The director's job is to create an environment where the truth can happen.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 30.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "The Anti-Hero Workshop -- Power Through Silence",
                "slug": "anti-hero-workshop-silence-eastwood",
                "description": "The Man With No Name, Dirty Harry, William Munny. Three different decades, one technique: say less, mean more. I teach you to hold a scene with a look, a squint, and a well-timed pause. We work on screen economy -- every gesture must earn its place.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Spaghetti Western Costume Kit (Poncho, Hat, Cigarillo Props)",
                "slug": "spaghetti-western-costume-kit",
                "description": "The green poncho, the flat-brim hat, and prop cigarillos from the Dollars trilogy. Leone made me an icon with these three items and Morricone's music. Tip: A costume works when the audience can sketch it from memory. Keep it simple.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 8.0, "price_unit": "per_day", "currency": "EUR", "deposit": 40.0}]
            },
            {
                "name": "Jazz Piano Session -- Improvisation and Film Scoring",
                "slug": "jazz-piano-session-eastwood",
                "description": "I've composed scores for many of my own films. Jazz is conversation -- you listen, you respond, you leave space. We work on basic piano improvisation over blues and jazz standards. No sheet music. Tip: The notes you DON'T play are just as important as the ones you do. Same in acting. Same in life.",
                "item_type": "service",
                "category": "music",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    # ------------------------------------------------------------------
    # 18. ROBERT DE NIRO (1943-)
    # ------------------------------------------------------------------
    {
        "slug": "deniros-workshop",
        "display_name": "Robert De Niro",
        "email": "robert.deniro@borrowhood.local",
        "date_of_birth": "1943-08-17",
        "mother_name": "Virginia Admiral",
        "father_name": "Robert De Niro Sr.",
        "workshop_name": "De Niro's Workshop",
        "workshop_type": "studio",
        "tagline": "You talkin' to me?",
        "bio": "Born in Manhattan. Both my parents were painters -- my father studied with Hans Hofmann, my mother with Josef Albers. I grew up in Little Italy and Greenwich Village surrounded by artists. Stella Adler and Lee Strasberg both taught me, but the street taught me more. Tip: Research is not optional. For Taxi Driver, I got a real hack license and drove a cab through New York at night. For Raging Bull, I gained sixty pounds and trained with Jake LaMotta for a year. You don't play a character -- you BECOME the character, then you let the character go when the film wraps. Scorsese is my brother. We've made ten films together starting with Mean Streets in 1973. The mirror scene in Taxi Driver was improvised -- Scorsese left the camera rolling and I just... talked. That's what preparation gives you: the freedom to improvise from a place of total knowledge. Al Pacino and I didn't share a scene until Heat in 1995. Twenty years of people asking, and Michael Mann finally put us at the same table.",
        "telegram_username": "travis_bickle",
        "city": "New York",
        "country_code": "US",
        "latitude": 40.726,
        "longitude": -73.993,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "it", "proficiency": "intermediate"}
        ],
        "skills": [
            {"skill_name": "Method Acting", "category": "art", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Physical Transformation", "category": "art", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Improvisation", "category": "art", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Boxing", "category": "sports", "self_rating": 4, "years_experience": 15}
        ],
        "social_links": [],
        "points": {"total_points": 2200, "rentals_completed": 58, "reviews_given": 40, "reviews_received": 72, "items_listed": 7, "helpful_flags": 40},
        "offers_training": True,
        "items": [
            {
                "name": "Method Research Intensive -- Becoming Someone Else",
                "slug": "method-research-intensive-deniro",
                "description": "I don't start with the script. I start with the world. Where does the character live? What's in his pockets? What radio station does he listen to? We build a character from the ground up -- wardrobe, daily routine, voice, walk. Tip: Spend a day living as the character before you memorize a single line.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 35.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Scene Improvisation Workshop -- Finding Truth Without a Script",
                "slug": "scene-improvisation-workshop-deniro",
                "description": "The 'You talkin' to me?' scene wasn't written. It was felt. I teach you to prepare so thoroughly that when the script disappears, you're still the character. We set up scenarios and go. No safety net. The best moments in film happen when the actor surprises themselves.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 28.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Boxing Training Session -- Raging Bull Fundamentals",
                "slug": "boxing-training-raging-bull-fundamentals",
                "description": "Jake LaMotta trained me for a year. I learned jab, cross, hook, uppercut, and the footwork of a middleweight. Boxing teaches you rhythm, distance, and controlled aggression -- all of which translate directly to screen performance. We wrap hands, hit bags, and spar light.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Character Wardrobe Kit (Taxi Driver Era)",
                "slug": "character-wardrobe-kit-taxi-driver",
                "description": "Army surplus jacket, aviator sunglasses, boots, and the mohawk wig. Travis Bickle's wardrobe tells his whole story before he opens his mouth -- military discipline decaying into isolation. Tip: A character's clothes are their armor. Choose every piece deliberately.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 8.0, "price_unit": "per_day", "currency": "EUR", "deposit": 40.0}]
            },
            {
                "name": "Boxing Gear Set (Gloves, Wraps, Heavy Bag)",
                "slug": "boxing-gear-set-deniro",
                "description": "16oz training gloves, 180-inch hand wraps, and a 70lb heavy bag with ceiling mount. The same weight class gear I trained with for Raging Bull. Hit the bag for twenty minutes and tell me acting isn't physical work.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 7.0, "price_unit": "per_day", "currency": "EUR", "deposit": 35.0}]
            }
        ]
    },
    # ------------------------------------------------------------------
    # 19. AL PACINO (1940-)
    # ------------------------------------------------------------------
    {
        "slug": "pacinos-stage-door",
        "display_name": "Al Pacino",
        "email": "al.pacino@borrowhood.local",
        "date_of_birth": "1940-04-25",
        "mother_name": "Rose Gerardi",
        "father_name": "Salvatore Pacino",
        "workshop_name": "Pacino's Stage Door",
        "workshop_type": "studio",
        "tagline": "I always tell the truth. Even when I lie.",
        "bio": "Born Alfredo James Pacino in East Harlem, New York. My parents split when I was two. My mother and I moved in with her parents in the South Bronx. I dropped out of school at seventeen to pursue acting. We were poor -- I worked as a janitor, a busboy, a mail carrier. Lee Strasberg at the Actors Studio saw something in me and became like a father. Tip: The stage is where you learn your craft. Film is where you apply it. I've done both my entire career and they feed each other. Never abandon the stage for the screen. The Godfather was my break, but I'd already won an Obie for The Indian Wants the Bronx. Coppola fought the studio to cast me -- they wanted Robert Redford. Can you imagine? Scent of a Woman finally got me the Oscar after seven nominations. The tango scene was real -- I learned to tango blind. Bobby De Niro is my other half. Heat was the first time we sat across from each other on camera. The diner scene was two actors who'd waited twenty years.",
        "telegram_username": "michael_corleone",
        "city": "New York",
        "country_code": "US",
        "latitude": 40.795,
        "longitude": -73.933,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "it", "proficiency": "intermediate"}
        ],
        "skills": [
            {"skill_name": "Method Acting", "category": "art", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Stage Acting", "category": "art", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Shakespeare Performance", "category": "art", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Film Directing", "category": "art", "self_rating": 4, "years_experience": 20}
        ],
        "social_links": [],
        "points": {"total_points": 2180, "rentals_completed": 57, "reviews_given": 44, "reviews_received": 70, "items_listed": 7, "helpful_flags": 39},
        "offers_training": True,
        "items": [
            {
                "name": "Intensity Workshop -- The Quiet Before the Explosion",
                "slug": "intensity-workshop-quiet-explosion-pacino",
                "description": "Michael Corleone is quiet for two hours before he pulls the trigger. Tony Montana never stops burning. I teach both -- controlled intensity and unleashed fire. We work on building emotional pressure in a scene until the release is inevitable. Tip: The explosion means nothing without the silence that precedes it.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 30.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Shakespeare for Screen Actors -- Making the Bard Breathe",
                "slug": "shakespeare-screen-actors-pacino",
                "description": "I directed and starred in Looking for Richard because Shakespeare terrified me -- and the only way past fear is through it. We work on verse-speaking, iambic pentameter as BREATH not math, and finding the modern man inside the Elizabethan language. Richard III is our text. Bring your courage.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Monologue Coaching -- One Voice, Full Room",
                "slug": "monologue-coaching-one-voice-pacino",
                "description": "Audition monologue, film monologue, stage monologue -- each needs different calibration. I'll coach your piece line by line. We work on breath, beats, subtext, and the moment you stop performing and start LIVING the text. Tip: The best monologue sounds like a conversation with someone who isn't there.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 28.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Tango Dance Lesson -- The Scent of a Woman Masterclass",
                "slug": "tango-dance-lesson-pacino",
                "description": "I learned the Argentine tango for Scent of a Woman and performed it blind. Tango is a conversation between two bodies -- lead, follow, improvise. I teach basic tango: the walk, the ocho, the cross. You'll dance in twenty minutes. Tip: Tango is not about steps. It's about the embrace.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Complete Shakespeare (Riverside Edition, Annotated)",
                "slug": "complete-shakespeare-riverside-pacino",
                "description": "My personal Riverside Shakespeare -- every play, every sonnet. Heavily annotated in pencil. Richard III has three colors of markup from three different productions. Hamlet has coffee stains from 1979. These margins contain forty years of wrestling with the greatest writer in the English language.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 4.0, "price_unit": "per_day", "currency": "EUR"}]
            }
        ]
    },
    # ------------------------------------------------------------------
    # 20. MERYL STREEP (1949-)
    # ------------------------------------------------------------------
    {
        "slug": "streeps-transformation-studio",
        "display_name": "Meryl Streep",
        "email": "meryl.streep@borrowhood.local",
        "date_of_birth": "1949-06-22",
        "mother_name": "Mary Wolf Wilkinson",
        "father_name": "Harry William Streep Jr.",
        "workshop_name": "Streep's Transformation Studio",
        "workshop_type": "studio",
        "tagline": "The great gift of human beings is that we have the power of empathy",
        "bio": "Born Mary Louise Streep in Summit, New Jersey. My father was a pharmaceutical executive, my mother a commercial artist and art editor. I studied opera seriously as a teenager -- my teacher said I could have gone professional. Vassar gave me the liberal arts foundation. Yale Drama School gave me the technique. Tip: Accent work is not imitation -- it's architecture. You rebuild your mouth, your breathing, your thinking in the rhythm of another language. That's how I became Polish in Sophie's Choice, Danish in Out of Africa, Australian in A Cry in the Dark, and Italian in The Bridges of Madison County. I hold the record for Academy Award nominations -- twenty-one. Three wins. But who's counting? Robert De Niro was my first great scene partner in The Deer Hunter. Dustin Hoffman pushed me in Kramer vs. Kramer -- sometimes too hard. I pushed back. The improvised slap in the courtroom scene was real frustration channeled into art.",
        "telegram_username": "meryl_voices",
        "city": "Summit",
        "country_code": "US",
        "latitude": 40.715,
        "longitude": -74.365,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "de", "proficiency": "intermediate"},
            {"language_code": "it", "proficiency": "intermediate"},
            {"language_code": "pl", "proficiency": "intermediate"}
        ],
        "skills": [
            {"skill_name": "Character Transformation", "category": "art", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Dialect & Accent", "category": "art", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Opera Singing", "category": "music", "self_rating": 4, "years_experience": 30},
            {"skill_name": "Stage Acting", "category": "art", "self_rating": 5, "years_experience": 50}
        ],
        "social_links": [],
        "points": {"total_points": 2400, "rentals_completed": 70, "reviews_given": 55, "reviews_received": 85, "items_listed": 8, "helpful_flags": 50},
        "offers_training": True,
        "items": [
            {
                "name": "Accent & Dialect Masterclass -- Rebuilding Your Voice",
                "slug": "accent-dialect-masterclass-streep",
                "description": "I don't do accents -- I rebuild the architecture of speech. Jaw placement, tongue position, breath pattern, rhythm. We start with the International Phonetic Alphabet, then move to a specific accent of your choice. By the end, you won't be imitating -- you'll be THINKING in that accent. Tip: Record native speakers and transcribe what you HEAR, not what the words say.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 30.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Character Empathy Workshop -- Becoming Someone You're Not",
                "slug": "character-empathy-workshop-streep",
                "description": "The hardest characters are the ones you disagree with. I teach you to find the humanity in ANYONE -- a cruel mother, a fascist collaborator, a bitter editor. We don't judge characters. We understand them. That understanding IS the performance. Tip: Ask 'Why does this person think they're right?' and you've found the character.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 28.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Opera Singing for Actors -- Voice as Instrument",
                "slug": "opera-singing-for-actors-streep",
                "description": "I studied opera before acting. Vocal training teaches breath control, projection, and emotional range that transforms film performances. We warm up with scales, work on one aria, and apply the techniques to spoken text. You don't need to be a singer. You need to be a breather.",
                "item_type": "service",
                "category": "music",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "IPA (International Phonetic Alphabet) Training Kit",
                "slug": "ipa-training-kit-streep",
                "description": "Flash cards, audio recordings, and workbook for mastering the International Phonetic Alphabet. This is the foundation of all dialect work. Once you can READ sound, you can reproduce any accent on earth. I use this system for every role. No exceptions.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 4.0, "price_unit": "per_day", "currency": "EUR"}]
            },
            {
                "name": "Audition Preparation Coaching -- The 3-Minute Performance",
                "slug": "audition-preparation-coaching-streep",
                "description": "You get three minutes to show them everything. I teach you to walk in prepared, grounded, and PRESENT. We work on your specific audition piece -- cold read or prepared. Tip: They've decided about you before you open your mouth. Own the room from the door.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    # ------------------------------------------------------------------
    # 21. DENZEL WASHINGTON (1954-)
    # ------------------------------------------------------------------
    {
        "slug": "denzels-stage",
        "display_name": "Denzel Washington",
        "email": "denzel.washington@borrowhood.local",
        "date_of_birth": "1954-12-28",
        "mother_name": "Lennis Lowe",
        "father_name": "Denzel Hayes Washington Sr.",
        "workshop_name": "Denzel's Stage",
        "workshop_type": "studio",
        "tagline": "Do what you have to do, to do what you want to do",
        "bio": "Born in Mount Vernon, New York. My father was a Pentecostal minister and worked for the local water department and at S. Klein department store. My mother owned a beauty parlor. When my parents divorced, my mother sent me to Oakland Academy, a private boarding school that probably saved my life. Fordham University gave me the education and a drama professor named Robinson Stone who said, 'You should try acting.' Best advice I ever received. Tip: Fall forward. Every failed audition, every bad review, every closed door is pushing you FORWARD if you let it. I trained at the American Conservatory Theater in San Francisco. Sidney Poitier walked so I could run -- and I've told him that to his face. Glory, Malcolm X, Training Day, Fences. Each one demanded everything I had. August Wilson's plays are scripture to me -- I've directed and produced them for the screen because that man's words deserve to be heard by everyone.",
        "telegram_username": "king_kong_denzel",
        "city": "Mount Vernon",
        "country_code": "US",
        "latitude": 40.912,
        "longitude": -73.837,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Dramatic Acting", "category": "art", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Film Directing", "category": "art", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Stage Acting", "category": "art", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Public Speaking", "category": "education", "self_rating": 5, "years_experience": 35}
        ],
        "social_links": [],
        "points": {"total_points": 2320, "rentals_completed": 64, "reviews_given": 52, "reviews_received": 80, "items_listed": 7, "helpful_flags": 46},
        "offers_training": True,
        "items": [
            {
                "name": "Commanding Presence Masterclass -- Owning Every Room",
                "slug": "commanding-presence-masterclass-denzel",
                "description": "Whether it's a boardroom, a courtroom, or a battlefield, I teach you to walk in like you belong. We work on voice projection, stillness under pressure, and the art of the deliberate pause. Tip: Don't rush. The audience waits for you. You don't wait for the audience.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 30.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Character Preparation Workshop -- Building From the Ground Up",
                "slug": "character-preparation-ground-up-denzel",
                "description": "For Malcolm X, I read every speech, visited every location, and fasted for three days. For Training Day, I rode with real narcotics officers. Preparation is the foundation. We build your character's backstory, physicality, and voice from scratch. Tip: Know ten times more about your character than the script reveals. The audience sees the iceberg tip, but they FEEL the mass beneath.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 28.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "August Wilson Scene Study -- American Master",
                "slug": "august-wilson-scene-study-denzel",
                "description": "We work scenes from Fences, Ma Rainey's Black Bottom, and The Piano Lesson. Wilson wrote the poetry of ordinary Black American life with the weight of Shakespeare. I direct these workshops personally. Bring the text memorized -- we're not here to read. We're here to LIVE.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Motivational Speaking Workshop -- Words That Move People",
                "slug": "motivational-speaking-workshop-denzel",
                "description": "My commencement speeches have millions of views because I don't lecture -- I TELL STORIES. Every speech is a performance. Every performance is a truth. We work on structure, delivery, vulnerability, and the courage to say something real. Tip: If you're not a little afraid of what you're about to say, it's not worth saying.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "August Wilson Complete Plays (Two-Volume Set)",
                "slug": "august-wilson-complete-plays-denzel",
                "description": "The complete American Century Cycle -- ten plays spanning ten decades of Black American experience. My copies are marked up with director's notes, blocking ideas, and questions I still haven't answered. Wilson wrote this nation's story better than anyone. Start with Fences, end with Radio Golf.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 4.0, "price_unit": "per_day", "currency": "EUR"}]
            }
        ]
    },
    # ------------------------------------------------------------------
    # 22. MORGAN FREEMAN (1937-)
    # ------------------------------------------------------------------
    {
        "slug": "freemans-porch",
        "display_name": "Morgan Freeman",
        "email": "morgan.freeman@borrowhood.local",
        "date_of_birth": "1937-06-01",
        "mother_name": "Mayme Edna Revere",
        "father_name": "Morgan Porterfield Freeman",
        "workshop_name": "Freeman's Porch",
        "workshop_type": "studio",
        "tagline": "Get busy living, or get busy dying",
        "bio": "Born in Memphis, Tennessee. Raised by my grandmother in Charleston, Mississippi until I was six. My first role was at age nine -- the lead in a school play. I fell in love with performance and never fell out. The Air Force recruited me at eighteen -- I wanted to be a fighter pilot. Instead, they made me a radar technician. I hated it. Quit after four years and went to Los Angeles with nothing. Tip: Your voice is your primary instrument. Protect it, train it, and let it carry the weight of what you mean, not just what you say. I didn't become a star until I was fifty. Fifty. Street Smart, Driving Miss Daisy, The Shawshank Redemption, Million Dollar Baby -- all after fifty. I narrate because people trust this voice. But trust isn't given -- it's earned through decades of doing the work honestly. Clint Eastwood directed me in three films. He works the way I like -- quiet, fast, respectful of the actor's process.",
        "telegram_username": "red_freeman",
        "city": "Memphis",
        "country_code": "US",
        "latitude": 35.149,
        "longitude": -90.049,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Voice Acting & Narration", "category": "art", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Dramatic Acting", "category": "art", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Beekeeping", "category": "garden", "self_rating": 4, "years_experience": 15},
            {"skill_name": "Sailing", "category": "sports", "self_rating": 4, "years_experience": 25}
        ],
        "social_links": [],
        "points": {"total_points": 2250, "rentals_completed": 60, "reviews_given": 50, "reviews_received": 77, "items_listed": 7, "helpful_flags": 43},
        "offers_training": True,
        "items": [
            {
                "name": "Voice & Narration Workshop -- Making People Listen",
                "slug": "voice-narration-workshop-freeman",
                "description": "I've narrated documentaries, audiobooks, and the voice of God himself. The secret? Slow down, breathe deeply, and mean every word. We work on resonance, pacing, and the art of reading text as if you're discovering it for the first time. Tip: Read the sentence silently first. Feel it. THEN say it aloud.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 28.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Late-Career Acting Workshop -- Your Best Work Isn't Behind You",
                "slug": "late-career-acting-workshop-freeman",
                "description": "I became a star at fifty. Most people think their window closes at thirty. It doesn't. Maturity gives you gravity, and gravity is what holds a scene together. We work on presence, patience, and using your real age and experience as assets, not obstacles.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Professional Voiceover Microphone Kit (Neumann U87)",
                "slug": "professional-voiceover-mic-kit-freeman",
                "description": "Neumann U87 large-diaphragm condenser microphone with pop filter, shock mount, and boom arm. This is the industry standard for voiceover work. Warm, detailed, forgiving. Treat it with respect -- this microphone costs more than most used cars.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 15.0, "price_unit": "per_day", "currency": "EUR", "deposit": 100.0}]
            },
            {
                "name": "Beekeeping Introduction -- The Hive Teaches Patience",
                "slug": "beekeeping-introduction-freeman",
                "description": "I converted my 124-acre ranch in Mississippi into a bee sanctuary. Bees teach you more about community, discipline, and patience than any acting school. We suit up, inspect a hive, and I show you how to read a colony. Tip: Move slowly, breathe calmly. Bees sense anxiety.",
                "item_type": "service",
                "category": "garden",
                "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    # ------------------------------------------------------------------
    # 23. SOPHIA LOREN (1934-)
    # ------------------------------------------------------------------
    {
        "slug": "sophias-cucina",
        "display_name": "Sophia Loren",
        "email": "sophia.loren@borrowhood.local",
        "date_of_birth": "1934-09-20",
        "mother_name": "Romilda Villani",
        "father_name": "Riccardo Scicolone",
        "workshop_name": "Sophia's Cucina",
        "workshop_type": "studio",
        "tagline": "Everything you see I owe to spaghetti",
        "bio": "Born Sofia Villani Scicolone in the Clinica Regina Margherita in Rome. I grew up in Pozzuoli during the war -- we lived through bombing, hunger, and the German occupation. My father never acknowledged me. My mother played piano and had the beauty of Greta Garbo but never the opportunity. Carlo Ponti discovered me at a beauty contest when I was fifteen. He became my producer, my mentor, and eventually my husband. Tip: Authenticity is the only beauty that ages well. I never had plastic surgery. I never changed my nose. They told me to fix it for decades. I told them my nose works perfectly -- it breathes, it smells, and it belongs to me. I won the Oscar for Two Women -- the first actress to win for a foreign language performance. Vittorio De Sica directed me five times. He taught me that neorealism isn't a style -- it's a commitment to truth. I cook the way I act: with passion, generosity, and too much garlic.",
        "telegram_username": "sophia_roma",
        "city": "Rome",
        "country_code": "IT",
        "latitude": 41.902,
        "longitude": 12.496,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "it", "proficiency": "native"},
            {"language_code": "en", "proficiency": "fluent"},
            {"language_code": "fr", "proficiency": "fluent"}
        ],
        "skills": [
            {"skill_name": "Screen Acting", "category": "art", "self_rating": 5, "years_experience": 65},
            {"skill_name": "Italian Cooking", "category": "garden", "self_rating": 5, "years_experience": 60},
            {"skill_name": "Comedy Acting", "category": "art", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Singing", "category": "music", "self_rating": 4, "years_experience": 30}
        ],
        "social_links": [],
        "points": {"total_points": 2200, "rentals_completed": 58, "reviews_given": 48, "reviews_received": 74, "items_listed": 7, "helpful_flags": 41},
        "offers_training": True,
        "items": [
            {
                "name": "Italian Neorealism Acting Workshop -- Truth Without Tricks",
                "slug": "italian-neorealism-acting-workshop-loren",
                "description": "Vittorio De Sica taught me that the best acting is no acting at all. We work on stripping away technique until only the truth remains. Real locations, real emotions, real light. No Hollywood gloss. Tip: If you need to cry, don't think about something sad. Think about something TRUE. The tears take care of themselves.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Neapolitan Cooking Class -- Cucina Povera e Ricca",
                "slug": "neapolitan-cooking-class-loren",
                "description": "I cook the food I grew up with in Pozzuoli -- pasta e fagioli, melanzane alla parmigiana, spaghetti con le vongole. Poor food made with dignity. I published two cookbooks because the kitchen is where I feel most myself. We cook for three hours and eat together. Tip: Never measure garlic. Measure with your heart.",
                "item_type": "service",
                "category": "garden",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Screen Presence for Women -- Commanding Without Diminishing",
                "slug": "screen-presence-for-women-loren",
                "description": "I was told to shrink -- change your nose, lose weight, lower your voice. I did none of it. I teach women to take up space on screen without apology. Posture, gaze, and the power of a well-timed silence. Men take up space instinctively. Women must choose to. That choice is power.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Sophia's Italian Pantry Kit (Olive Oil, Pasta, San Marzano Tomatoes)",
                "slug": "sophias-italian-pantry-kit",
                "description": "Premium Italian ingredients: cold-pressed extra virgin olive oil from Puglia, bronze-die pasta from Gragnano, and genuine DOP San Marzano tomatoes. These are the three ingredients that built Italian cinema -- because every set had a kitchen, and every kitchen had these.",
                "item_type": "physical",
                "category": "garden",
                "listings": [{"listing_type": "rent", "price": 10.0, "price_unit": "per_day", "currency": "EUR"}]
            },
            {
                "name": "Italian Comedy Masterclass -- Commedia dell'Arte to Screen",
                "slug": "italian-comedy-masterclass-loren",
                "description": "From Harlequin to Totò to Marcello Mastroianni -- Italian comedy is a tradition spanning centuries. I teach the physical comedy, the timing, and the heartbreak underneath the laughter. We work scenes from Marriage Italian Style and Yesterday, Today and Tomorrow. Marcello was my greatest screen partner. The chemistry was real -- the love was professional.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    # ------------------------------------------------------------------
    # 24. INGRID BERGMAN (1915-1982)
    # ------------------------------------------------------------------
    {
        "slug": "ingrids-dressing-room",
        "display_name": "Ingrid Bergman",
        "email": "ingrid.bergman@borrowhood.local",
        "date_of_birth": "1915-08-29",
        "mother_name": "Friedel Adler Bergman",
        "father_name": "Justus Samuel Bergman",
        "workshop_name": "Ingrid's Dressing Room",
        "workshop_type": "studio",
        "tagline": "Be yourself. The world worships the original.",
        "bio": "Born in Stockholm, Sweden. My mother died when I was three. My father, a photographer and artist, died when I was thirteen. I was raised by an aunt who died shortly after. By fifteen I was essentially alone in the world. The Royal Dramatic Theatre School in Stockholm took me in -- same school that trained Greta Garbo. Tip: The camera loves honesty more than beauty. Hollywood wanted me to pluck my eyebrows, cap my teeth, and change my name. I refused all three. David O. Selznick brought me to America for Intermezzo. Casablanca with Bogart made me immortal -- and I almost turned it down because nobody could tell me how the story ended during filming. They were writing it as we shot. Roberto Rossellini wrote me a letter and I went to Italy. Hollywood condemned me for leaving my husband. The Senate called me 'a powerful influence for evil.' I survived it. I always survived. Three Oscars, two Emmys, one Tony. My last film was Autumn Sonata with Ingmar Bergman -- no relation, but what a coincidence.",
        "telegram_username": "ilsa_lund",
        "city": "Stockholm",
        "country_code": "SE",
        "latitude": 59.329,
        "longitude": 18.069,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "sv", "proficiency": "native"},
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "it", "proficiency": "fluent"},
            {"language_code": "de", "proficiency": "fluent"},
            {"language_code": "fr", "proficiency": "fluent"}
        ],
        "skills": [
            {"skill_name": "Screen Acting", "category": "art", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Stage Acting", "category": "art", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Multilingual Performance", "category": "art", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Emotional Authenticity", "category": "art", "self_rating": 5, "years_experience": 45}
        ],
        "social_links": [],
        "points": {"total_points": 2150, "rentals_completed": 56, "reviews_given": 46, "reviews_received": 72, "items_listed": 6, "helpful_flags": 39},
        "offers_training": True,
        "items": [
            {
                "name": "Natural Screen Acting Workshop -- No Makeup, No Tricks",
                "slug": "natural-screen-acting-workshop-bergman",
                "description": "I refused the Hollywood makeover. My eyebrows stayed thick, my name stayed Swedish, and the camera loved me anyway. I teach you to show up as yourself and let that be enough. We work on emotional transparency, natural movement, and the courage to be imperfect on camera. Tip: Beauty fades. Honesty doesn't.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Multilingual Acting Workshop -- Performing in Other Languages",
                "slug": "multilingual-acting-workshop-bergman",
                "description": "I performed in Swedish, English, Italian, German, and French -- each language changes how you think, gesture, and breathe. We pick two languages and do the same scene in both. You'll discover that your character shifts when the language shifts. That's not a problem -- that's a gift.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Classic Hollywood Makeup Kit (1940s Natural Look)",
                "slug": "classic-hollywood-makeup-kit-bergman",
                "description": "The 1940s 'no makeup' look actually required extraordinary skill. Soft foundation, natural brow, minimal eye, rosy lip. This kit replicates the golden-age Hollywood look that Selznick's makeup artists created for me. Includes application guide.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 6.0, "price_unit": "per_day", "currency": "EUR"}]
            },
            {
                "name": "Emotional Scene Work -- Crying, Laughing, Raging on Cue",
                "slug": "emotional-scene-work-bergman",
                "description": "In Casablanca, the tears were real -- I didn't know how the story ended. That uncertainty became the performance. I teach you to access genuine emotion without tricks, onions, or menthol. We work on sense memory, breath, and emotional preparation. Tip: Don't try to cry. Try to NOT cry. The struggle is what the camera captures.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 28.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    # ------------------------------------------------------------------
    # 25. STEVE MCQUEEN (1930-1980)
    # ------------------------------------------------------------------
    {
        "slug": "mcqueens-garage",
        "display_name": "Steve McQueen",
        "email": "steve.mcqueen@borrowhood.local",
        "date_of_birth": "1930-03-24",
        "mother_name": "Julia Ann Crawford",
        "father_name": "Terrence Steven McQueen",
        "workshop_name": "McQueen's Garage",
        "workshop_type": "garage",
        "tagline": "Racing is life. Everything before and after is just waiting.",
        "bio": "Born in Beech Grove, Indiana. My father left before I could remember. My mother couldn't handle me -- I bounced between foster homes and my great-uncle's farm in Slater, Missouri. Ran away to join the circus at age nine. Joined the Marines at seventeen -- they threw me in the brig for going AWOL, then made me a tank driver. The Neighborhood Playhouse and Uta Hagen's classes turned me into an actor. Sandy Meisner taught me the rest. Tip: Coolness is not about what you do. It's about what you DON'T do. Every extra gesture, every unnecessary word, every fidget -- cut it. The audience fills in the blanks. That's where charisma lives. Bullitt's car chase -- twelve minutes, no dialogue, and I did 90% of the driving myself. Bruce Lee trained me in Jeet Kune Do. We were friends. I rode motorcycles in The Great Escape because sitting still made me crazy. I raced at Le Mans because acting wasn't enough adrenaline. Nobody called me the King of Cool. I just showed up and didn't try too hard.",
        "telegram_username": "king_of_cool",
        "city": "Beech Grove",
        "country_code": "US",
        "latitude": 39.722,
        "longitude": -86.090,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Screen Acting", "category": "art", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Motorcycle Racing", "category": "sports", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Car Racing", "category": "sports", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Stunt Driving", "category": "sports", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Martial Arts", "category": "sports", "self_rating": 4, "years_experience": 10}
        ],
        "social_links": [],
        "points": {"total_points": 2050, "rentals_completed": 52, "reviews_given": 38, "reviews_received": 68, "items_listed": 7, "helpful_flags": 37},
        "offers_training": True,
        "items": [
            {
                "name": "Screen Coolness Workshop -- Less Is More, Period",
                "slug": "screen-coolness-workshop-mcqueen",
                "description": "I cut half my lines from every script. The directors hated it. The audience loved it. I teach you the Meisner principle applied to film: react truthfully, say only what's essential, and let your face do the work. Tip: If you can say it with a look, don't say it with words.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Stunt Driving Workshop -- Speed, Control, Camera Angles",
                "slug": "stunt-driving-workshop-mcqueen",
                "description": "Bullitt's twelve-minute car chase changed action cinema. I'll teach you pursuit driving: heel-toe downshifting, controlled drifts, and how to hit your mark at speed while a camera car is six feet off your bumper. We use a closed course and start slow. Tip: Smooth is fast. Jerky is dangerous.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 30.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Triumph Bonneville T120 (1968 Restoration)",
                "slug": "triumph-bonneville-t120-1968",
                "description": "The same model I jumped the wire fence on in The Great Escape (though I jumped it on a modified TR6 Trophy). This '68 Bonnie is fully restored -- 650cc parallel twin, beautiful chrome. Rental includes helmet, jacket, and a prayer that you bring it back in one piece.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 25.0, "price_unit": "per_day", "currency": "EUR", "deposit": 200.0}]
            },
            {
                "name": "Motorcycle Maintenance Workshop -- Wrench Your Own Bike",
                "slug": "motorcycle-maintenance-workshop-mcqueen",
                "description": "I rebuilt engines in my garage between films. A rider who can't fix their own bike is a passenger, not a rider. We cover oil changes, chain adjustment, brake bleeding, and carburetor tuning on a vintage British twin. Bring old clothes.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Leather Racing Jacket (Heuer-Patched, Le Mans Replica)",
                "slug": "leather-racing-jacket-le-mans-replica",
                "description": "Gulf-blue leather racing jacket with Heuer patch, exactly as I wore in Le Mans. This is the jacket that launched a thousand fashion imitations. It's insured, so please don't crash in it. Borrow for photo shoots, car shows, or just feeling invincible.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 12.0, "price_unit": "per_day", "currency": "EUR", "deposit": 80.0}]
            }
        ]
    },
    # ------------------------------------------------------------------
    # 26. GENE KELLY (1912-1996)
    # ------------------------------------------------------------------
    {
        "slug": "kellys-dance-floor",
        "display_name": "Gene Kelly",
        "email": "gene.kelly@borrowhood.local",
        "date_of_birth": "1912-08-23",
        "mother_name": "Harriet Catherine Curran",
        "father_name": "James Patrick Joseph Kelly",
        "workshop_name": "Kelly's Dance Floor",
        "workshop_type": "studio",
        "tagline": "You dance love, and you dance joy, and you dance dreams",
        "bio": "Born in the Highland Park neighborhood of Pittsburgh, Pennsylvania. My mother enrolled all five Kelly kids in dance class. The boys got beaten up for it. I got tough. I learned to combine athletic power with grace -- that became my signature. I studied economics at the University of Pittsburgh, taught dance to pay tuition, and ran my own dance studio by twenty-one. Tip: Dance for the camera is NOT dance for the stage. The camera can go anywhere the audience can't -- ground level, overhead, behind you. Use that. I choreographed my own numbers in Singin' in the Rain, An American in Paris, and On the Town. The rain scene took one take on a flooded set. I had a 103-degree fever. Fred Astaire was elegant. I was athletic. Together we redefined what musical cinema could be. I brought ballet, jazz, tap, and modern dance to the screen and proved they could all coexist. Stanley Donen co-directed with me -- we pushed each other. He handled the camera. I handled the movement. Perfection takes a partner.",
        "telegram_username": "singin_gene",
        "city": "Pittsburgh",
        "country_code": "US",
        "latitude": 40.474,
        "longitude": -79.953,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "fr", "proficiency": "intermediate"}
        ],
        "skills": [
            {"skill_name": "Tap Dance", "category": "sports", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Dance Choreography", "category": "art", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Ballet", "category": "sports", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Film Directing", "category": "art", "self_rating": 4, "years_experience": 25}
        ],
        "social_links": [],
        "points": {"total_points": 2200, "rentals_completed": 59, "reviews_given": 47, "reviews_received": 73, "items_listed": 7, "helpful_flags": 41},
        "offers_training": True,
        "items": [
            {
                "name": "Tap Dance Fundamentals -- Athletic Style",
                "slug": "tap-dance-fundamentals-kelly",
                "description": "I don't teach pretty tap. I teach POWERFUL tap. We start with shuffles, flaps, and time steps, then build to combinations that use your whole body. I combined tap with ballet and jazz because dance shouldn't live in boxes. Tip: Your tap shoes are percussion instruments. You're not dancing -- you're drumming with your feet.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Dance for Camera Workshop -- Choreographing for the Lens",
                "slug": "dance-for-camera-workshop-kelly",
                "description": "Stage dance faces one direction. Camera dance exists in 360 degrees. I teach you to choreograph for angles, cuts, and tracking shots. We study the puddle-splashing in Singin' in the Rain and the ballet in An American in Paris. Tip: The camera is your dance partner. Don't ignore it.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Professional Tap Shoes (Capezio K360, Men's & Women's Sizes)",
                "slug": "professional-tap-shoes-capezio-kelly",
                "description": "Capezio K360 oxfords -- the tap shoe I helped design. Split-sole for flexibility, Teletone taps for a warm sound, leather upper for durability. Available in men's 8-12 and women's 6-10. Break them in on a wooden floor, not concrete.",
                "item_type": "physical",
                "category": "sports",
                "listings": [{"listing_type": "rent", "price": 6.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0}]
            },
            {
                "name": "Musical Film History Screening & Discussion",
                "slug": "musical-film-history-screening-kelly",
                "description": "We screen one of the great musicals -- Singin' in the Rain, An American in Paris, On the Town, or West Side Story -- and I break down the choreography, camera work, and directorial decisions. Small group, max 10. Come ready to discuss how dance tells story.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Umbrella (Singin' in the Rain Replica, Full Size)",
                "slug": "umbrella-singin-rain-replica",
                "description": "Full-size black umbrella, exact replica of the one from the most famous dance sequence in cinema history. Borrow it for your own rain dance, photo shoots, or just because it makes you happy. Tip: The rain was a mix of water and milk -- milk showed up better on camera.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 3.0, "price_unit": "per_day", "currency": "EUR"}]
            }
        ]
    },
    # ------------------------------------------------------------------
    # 27. FRED ASTAIRE (1899-1987)
    # ------------------------------------------------------------------
    {
        "slug": "astaires-dance-pavilion",
        "display_name": "Fred Astaire",
        "email": "fred.astaire@borrowhood.local",
        "date_of_birth": "1899-05-10",
        "mother_name": "Johanna Ann Geilus",
        "father_name": "Friedrich Emanuel Austerlitz",
        "workshop_name": "Astaire's Dance Pavilion",
        "workshop_type": "studio",
        "tagline": "The hardest job kids face today is learning good manners without seeing any",
        "bio": "Born Frederick Austerlitz in Omaha, Nebraska. My father was an Austrian immigrant who worked at the Storz Brewing Company. My mother recognized talent in my sister Adele and me early -- she moved us to New York at age four to study dance. Adele and I performed as a vaudeville act from childhood through Broadway. When Adele married and retired, I went to Hollywood alone. An RKO talent scout wrote: 'Can't act. Slightly bald. Can dance a little.' I framed that. Tip: Do it until it looks effortless. I rehearsed every number until my feet bled, then rehearsed more. The audience should see joy, not work. Ginger Rogers was my greatest partner -- she did everything I did, backwards and in heels. Gene Kelly was athletic where I was elegant. We admired each other completely. I insisted on full-body shots in my dance numbers -- no cutting, no close-ups, no cheating. The camera had to show it was real. Hermes Pan choreographed with me for decades. Every step was a conversation between us.",
        "telegram_username": "top_hat_fred",
        "city": "Omaha",
        "country_code": "US",
        "latitude": 41.256,
        "longitude": -95.934,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Ballroom Dance", "category": "sports", "self_rating": 5, "years_experience": 75},
            {"skill_name": "Tap Dance", "category": "sports", "self_rating": 5, "years_experience": 75},
            {"skill_name": "Dance Choreography", "category": "art", "self_rating": 5, "years_experience": 65},
            {"skill_name": "Singing", "category": "music", "self_rating": 4, "years_experience": 60}
        ],
        "social_links": [],
        "points": {"total_points": 2300, "rentals_completed": 63, "reviews_given": 50, "reviews_received": 79, "items_listed": 7, "helpful_flags": 45},
        "offers_training": True,
        "items": [
            {
                "name": "Ballroom Dance Masterclass -- Elegance in Motion",
                "slug": "ballroom-dance-masterclass-astaire",
                "description": "Waltz, foxtrot, quickstep, and the Viennese waltz. I teach you to move across a dance floor as if the floor were made of clouds. Posture, frame, lead-and-follow, and musicality. Tip: Your partner should feel weightless in your arms. If they feel heavy, you're leading too hard.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Tap Dance -- The Art of Effortless Complexity",
                "slug": "tap-dance-effortless-complexity-astaire",
                "description": "My tap style is different from Gene's. He's power. I'm precision. We work on clean sounds, syncopation, and the illusion of spontaneity that only comes from ruthless preparation. Tip: If the audience can see you counting, you haven't practiced enough.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Top Hat & Tails Costume Set (Screen-Quality Formal Wear)",
                "slug": "top-hat-tails-costume-set-astaire",
                "description": "White tie and tails, silk top hat, white gloves, patent leather shoes, and walking cane. The complete Fred Astaire look from Top Hat. Every piece is dance-functional -- the jacket moves with you, the shoes are flexible, the hat stays on during spins. Tip: Formal wear should make you stand straighter. If it doesn't, it doesn't fit.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 12.0, "price_unit": "per_day", "currency": "EUR", "deposit": 60.0}]
            },
            {
                "name": "Singing for Non-Singers -- Charm Over Range",
                "slug": "singing-for-non-singers-astaire",
                "description": "Irving Berlin, Cole Porter, and the Gershwins all wrote songs specifically for my voice -- and I had barely one octave. The trick isn't range. It's phrasing, charm, and meaning every word. We work on selling a song with personality instead of power. Tip: If you can speak it convincingly, you can sing it.",
                "item_type": "service",
                "category": "music",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Dance Cane (Bamboo, Performance Grade)",
                "slug": "dance-cane-bamboo-performance-astaire",
                "description": "A performance-weight bamboo cane -- the same kind I used in Puttin' on the Ritz and Top Hat. A cane transforms a walk into a performance. We practice twirls, tosses, and the gentleman's lean. Lighter than it looks, stronger than you'd think.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 3.0, "price_unit": "per_day", "currency": "EUR"}]
            }
        ]
    },
    # ------------------------------------------------------------------
    # 28. GINGER ROGERS (1911-1995)
    # ------------------------------------------------------------------
    {
        "slug": "gingers-rehearsal-studio",
        "display_name": "Ginger Rogers",
        "email": "ginger.rogers@borrowhood.local",
        "date_of_birth": "1911-07-16",
        "mother_name": "Lela Emogene Owens",
        "father_name": "William Eddins Rogers",
        "workshop_name": "Ginger's Rehearsal Studio",
        "workshop_type": "studio",
        "tagline": "I did everything Fred did, backwards and in heels",
        "bio": "Born Virginia Katherine McMath in Independence, Missouri. My mother, Lela, was a force of nature -- journalist, scriptwriter, and stage mother who guided my career with iron determination. I won a Charleston contest at fourteen and was in vaudeville by fifteen. Hollywood came quickly -- I was in 42nd Street by twenty-two. Then Fred Astaire walked into my life. We made ten films together at RKO and redefined what dance could do on screen. Tip: Following is harder than leading. The follower interprets, adapts, and makes the leader look good -- all in real time, all in reverse. That's a skill most people never appreciate. I won my Oscar for Kitty Foyle, a dramatic role -- not a musical. I wanted people to know I could act, not just dance. People always quote that line about doing everything backwards in high heels. I never actually said it. But I lived it. I also produced, directed, and ran my own cattle ranch in Oregon. Don't let anyone put you in a box. Especially if you can dance your way out of it.",
        "telegram_username": "ginger_backwards",
        "city": "Independence",
        "country_code": "US",
        "latitude": 39.091,
        "longitude": -94.415,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Ballroom Dance", "category": "sports", "self_rating": 5, "years_experience": 60},
            {"skill_name": "Tap Dance", "category": "sports", "self_rating": 5, "years_experience": 60},
            {"skill_name": "Dramatic Acting", "category": "art", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Comedy Acting", "category": "art", "self_rating": 5, "years_experience": 50}
        ],
        "social_links": [],
        "points": {"total_points": 2100, "rentals_completed": 57, "reviews_given": 46, "reviews_received": 71, "items_listed": 6, "helpful_flags": 39},
        "offers_training": True,
        "items": [
            {
                "name": "Partner Dance Workshop -- The Art of Following",
                "slug": "partner-dance-workshop-following-rogers",
                "description": "Everyone wants to learn to lead. Nobody teaches you to follow brilliantly. Following is interpretation in real time -- you feel the lead's intention through your frame and translate it into movement, often in reverse, often in heels. We work on frame, connection, and musical sensitivity. Tip: The best follower makes every leader feel like a genius.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Dancing in Heels Workshop -- Grace Under Pressure",
                "slug": "dancing-in-heels-workshop-rogers",
                "description": "I danced in three-inch heels on polished floors going backwards. It requires ankle strength, balance, and nerve. We start with low heels on a forgiving surface and work up. Tip: The heel hits the ground differently than a flat shoe -- you must relearn your weight placement from the ground up.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "1930s Dance Costume Collection (Gowns, Heels, Feathers)",
                "slug": "1930s-dance-costume-collection-rogers",
                "description": "Three replica gowns from the Astaire-Rogers films: the feathered dress from Top Hat (it shed everywhere -- Fred hated it and I loved it), the satin from Swing Time, and the beaded from Shall We Dance. Includes matching dance heels. Handle with care -- the beading is hand-sewn.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 15.0, "price_unit": "per_day", "currency": "EUR", "deposit": 80.0}]
            },
            {
                "name": "Screen Acting for Dancers -- When the Music Stops",
                "slug": "screen-acting-for-dancers-rogers",
                "description": "I won my Oscar in a drama, not a musical. Dancers make extraordinary actors because we understand timing, physicality, and emotional expression through the body. I teach dancers how to carry those skills into dialogue scenes. Tip: Every pause in dialogue is a rest in music. Feel it that way.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    # ------------------------------------------------------------------
    # 29. KEANU REEVES (1964-)
    # ------------------------------------------------------------------
    {
        "slug": "keanus-dojo",
        "display_name": "Keanu Reeves",
        "email": "keanu.reeves@borrowhood.local",
        "date_of_birth": "1964-09-02",
        "mother_name": "Patricia Taylor",
        "father_name": "Samuel Nowlin Reeves Jr.",
        "workshop_name": "Keanu's Dojo",
        "workshop_type": "garage",
        "tagline": "Be excellent to each other",
        "bio": "Born in Beirut, Lebanon. My father left when I was three -- I haven't seen him since I was thirteen. My mother was a costume designer in the rock and roll industry in Toronto. I grew up moving between Beirut, Sydney, New York, and Toronto. I was a decent hockey goalie -- good enough that people said I should go pro. I chose acting instead. Tip: Show up. Show up prepared, show up kind, show up ready to work harder than everyone else. That's the whole secret. There is no shortcut to being good. The Matrix changed everything -- four months of martial arts training with Yuen Woo-ping before we shot a single frame. I learned that the body has its own intelligence. John Wick required three-gun tactical training -- I can reload a rifle on the move now. Keanu Reeves is not cool. I'm just a guy who does the work and tries to be decent. I ride the subway. I give up my seat. I eat lunch alone on a bench. The internet turned me into a meme. That's fine. As long as the work is honest, the rest doesn't matter.",
        "telegram_username": "the_one_neo",
        "city": "Beirut",
        "country_code": "LB",
        "latitude": 33.894,
        "longitude": 35.502,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "fr", "proficiency": "intermediate"}
        ],
        "skills": [
            {"skill_name": "Action Film Acting", "category": "art", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Tactical Firearms Training", "category": "sports", "self_rating": 4, "years_experience": 10},
            {"skill_name": "Motorcycle Riding", "category": "sports", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Jiu-Jitsu", "category": "sports", "self_rating": 4, "years_experience": 10},
            {"skill_name": "Bass Guitar", "category": "music", "self_rating": 3, "years_experience": 20}
        ],
        "social_links": [],
        "points": {"total_points": 2150, "rentals_completed": 58, "reviews_given": 55, "reviews_received": 74, "items_listed": 7, "helpful_flags": 48},
        "offers_training": True,
        "items": [
            {
                "name": "Action Film Preparation Workshop -- Body as Weapon",
                "slug": "action-film-preparation-workshop-keanu",
                "description": "For The Matrix, I trained four months. For John Wick, six months. I teach you the actor's approach to combat training: not to fight, but to look like you've been fighting your whole life. Jiu-jitsu, judo throws, gun handling, and the physical stamina to do take after take. Tip: Train until the movement disappears and only the character remains.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Three-Gun Tactical Training Workshop",
                "slug": "three-gun-tactical-training-keanu",
                "description": "Pistol, rifle, and shotgun -- safe handling, reload drills, transition drills, and shoot-on-the-move technique. I trained at Taran Tactical for John Wick and now I compete in 3-gun matches for fun. Safety is absolute. We start with fundamentals and build up. Tip: Slow is smooth, smooth is fast.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 30.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "ARCH Motorcycle Experience (Custom KRGT-1)",
                "slug": "arch-motorcycle-experience-krgt1",
                "description": "A ride on the KRGT-1 -- the motorcycle I co-designed with Gard Hollinger at ARCH Motorcycle Company. S&S 2032cc V-twin, billet aluminum frame, handcrafted everything. This isn't a rental. It's a supervised ride experience on a closed course. Because some things you have to feel to understand.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "service", "price": 40.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Bass Guitar (Fender Jazz Bass, Sunburst)",
                "slug": "bass-guitar-fender-jazz-keanu",
                "description": "My Fender Jazz Bass from the Dogstar days. I'm not a great bassist -- I'm an enthusiastic one. Sometimes enthusiasm is enough. Borrow it, start a band, play badly with joy. Tip: The bass holds everything together. Like kindness.",
                "item_type": "physical",
                "category": "music",
                "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0}]
            },
            {
                "name": "Kindness in the Industry Workshop -- Staying Human in Hollywood",
                "slug": "kindness-workshop-staying-human-keanu",
                "description": "This isn't an acting class. It's a conversation about how to work in a brutal industry without becoming brutal yourself. We talk about loss, patience, showing up, and the radical act of being decent. Small group, max 6. Tip: The person who has the least to prove usually has the most to offer.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    # ------------------------------------------------------------------
    # 30. ANTHONY HOPKINS (1937-)
    # ------------------------------------------------------------------
    {
        "slug": "hopkins-painting-studio",
        "display_name": "Anthony Hopkins",
        "email": "anthony.hopkins@borrowhood.local",
        "date_of_birth": "1937-12-31",
        "mother_name": "Muriel Anne Yeats",
        "father_name": "Richard Arthur Hopkins",
        "workshop_name": "Hopkins' Painting Studio",
        "workshop_type": "studio",
        "tagline": "We are all dying. Every day we are dying. But we are also living.",
        "bio": "Born in Margam, Port Talbot, Wales. My father was a baker. I was a terrible student -- dyslexic, distracted, and furious about everything. Then I saw Richard Burton perform and thought: 'That man is from the same town as me. If he can do it, I can.' Laurence Olivier invited me to the National Theatre. He called me his successor. I ran from that burden for years. Tip: Learn your lines until you can say them in your sleep. Then forget them and play the moment. I read my scripts two hundred times or more. By the time we film, the words are in my bones and my mind is free to listen, react, and surprise myself. Hannibal Lecter was sixteen minutes of screen time. Sixteen minutes and it became the most iconic villain in cinema. I based him on HAL 9000 -- no blink, no wasted movement, total stillness. I'm also a composer and painter now. I paint every day. Music and painting are acting without an audience. They're how I stay sane at eighty-eight.",
        "telegram_username": "sir_tony_hopkins",
        "city": "Port Talbot",
        "country_code": "GB",
        "latitude": 51.591,
        "longitude": -3.798,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "cy", "proficiency": "intermediate"}
        ],
        "skills": [
            {"skill_name": "Dramatic Acting", "category": "art", "self_rating": 5, "years_experience": 60},
            {"skill_name": "Painting", "category": "art", "self_rating": 4, "years_experience": 25},
            {"skill_name": "Music Composition", "category": "music", "self_rating": 4, "years_experience": 30},
            {"skill_name": "Shakespeare Performance", "category": "art", "self_rating": 5, "years_experience": 55}
        ],
        "social_links": [],
        "points": {"total_points": 2280, "rentals_completed": 61, "reviews_given": 48, "reviews_received": 79, "items_listed": 7, "helpful_flags": 44},
        "offers_training": True,
        "items": [
            {
                "name": "Line Mastery Workshop -- 200 Reads and Freedom",
                "slug": "line-mastery-workshop-200-reads-hopkins",
                "description": "My technique is brutally simple: read your script 200 times. Not 50. Not 100. Two hundred. By read 150, the words dissolve into your nervous system. By read 200, you're free to play. We work on a five-page scene in this session. You'll read it aloud until it transforms. Tip: Boredom is the gateway to mastery. Push through it.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 30.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Villain Masterclass -- Stillness as Terror",
                "slug": "villain-masterclass-stillness-terror-hopkins",
                "description": "Hannibal Lecter doesn't move. Doesn't blink. Doesn't raise his voice. And he terrifies every person in the room. I teach you that villainy isn't volume -- it's precision. We work on stillness, vocal control, and the chilling power of a well-timed smile. Tip: The scariest person in the room is the one who's completely comfortable.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 28.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Abstract Painting Workshop -- Art Without Rules",
                "slug": "abstract-painting-workshop-hopkins",
                "description": "I paint large abstract canvases every day. Bold colors, no plan, no rules. Painting silences the noise in my head. I teach you to pick up a brush with no destination and see where it goes. We use acrylics on large canvas -- go big or go home. Tip: The painting knows what it wants. Your job is to get out of the way.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Oil Paint & Acrylic Set (Professional Grade, 48 Colors)",
                "slug": "oil-paint-acrylic-set-hopkins",
                "description": "Professional-grade paints: 24 oil colors and 24 acrylic colors, plus brushes in every size from detail to barn-wall. Includes two stretched canvases (24x36 inches). I use acrylics for speed and oils for depth. Start with acrylics -- they forgive mistakes.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 8.0, "price_unit": "per_day", "currency": "EUR", "deposit": 40.0}]
            },
            {
                "name": "Shakespeare Intensive -- King Lear and the Weight of Language",
                "slug": "shakespeare-intensive-king-lear-hopkins",
                "description": "I've played Lear, Othello, Prospero, and Antony. Shakespeare terrifies actors because the language is dense. I teach you to find the human being inside the verse. We work on one soliloquy -- breath, thought, emotion, and the moment where the character breaks through the poetry. Tip: Shakespeare wrote for actors, not scholars. Speak it like a human being.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    # ------------------------------------------------------------------
    # 31. ANNA MAY WONG (1905-1961)
    # ------------------------------------------------------------------
    {
        "slug": "annas-lantern-house",
        "display_name": "Anna May Wong",
        "email": "anna.may.wong@borrowhood.local",
        "date_of_birth": "1905-01-03",
        "mother_name": "Lee Gon Toy",
        "father_name": "Wong Sam Sing",
        "workshop_name": "Anna's Lantern House",
        "workshop_type": "studio",
        "tagline": "I was born in Los Angeles, but I was never truly allowed to be American on screen",
        "bio": "Born Wong Liu Tsong in the Chinatown neighborhood of Los Angeles. My father ran a laundry on Figueroa Street. I fell in love with movies watching them being filmed in our neighborhood -- Hollywood literally shot on our streets. My first role was at fourteen as an extra in The Red Lantern. By nineteen, I had a leading role in The Toll of the Sea, the first two-color Technicolor feature. Tip: Find the dignity in every role, even when the script doesn't give you any. Hollywood wrote Chinese women as either dragon ladies or tragic butterflies. I played both and made them human anyway. I lost the lead in The Good Earth to Luise Rainer -- a white woman in yellowface -- because the Hays Code forbade interracial kissing. That defeat defined my fight. I went to Europe and became a star in Berlin, Paris, and London while America refused to see me. Marlene Dietrich became my dear friend in Berlin. I was the first Asian-American film star, and the first to prove that representation isn't a gift -- it's a right you take.",
        "telegram_username": "anna_may",
        "city": "Los Angeles",
        "country_code": "US",
        "latitude": 34.062,
        "longitude": -118.238,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "zh", "proficiency": "fluent"},
            {"language_code": "de", "proficiency": "fluent"},
            {"language_code": "fr", "proficiency": "fluent"}
        ],
        "skills": [
            {"skill_name": "Screen Acting", "category": "art", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Fashion & Costume Design", "category": "art", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Multilingual Performance", "category": "art", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Stage Acting", "category": "art", "self_rating": 4, "years_experience": 25}
        ],
        "social_links": [],
        "points": {"total_points": 1950, "rentals_completed": 50, "reviews_given": 42, "reviews_received": 65, "items_listed": 6, "helpful_flags": 36},
        "offers_training": True,
        "items": [
            {
                "name": "Representation in Film Workshop -- Fighting for the Role",
                "slug": "representation-in-film-workshop-wong",
                "description": "I fought Hollywood's stereotypes for forty years. Sometimes I won. Sometimes I took the role anyway and subverted it from inside. This workshop is about navigating an industry that doesn't see you -- how to advocate for yourself, how to find humanity in limited scripts, and how to build a career when the system is designed to exclude you. Tip: Your anger is valid. Channel it into the work.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Silent Film Acting Workshop -- Expression Without Words",
                "slug": "silent-film-acting-workshop-wong",
                "description": "I learned to act in silent film, where your face and body ARE the language. No dialogue to hide behind. We work on facial expression, gesture, and the art of conveying a complete story through movement alone. Tip: Silent film acting isn't bigger than sound film acting -- it's more PRECISE.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Vintage Qipao Collection (1920s-1940s Silk Dresses)",
                "slug": "vintage-qipao-collection-wong",
                "description": "Five hand-tailored silk qipao dresses in the styles I wore on screen and in life. Each one is a work of art -- embroidered, fitted, and designed to make a statement. I was the most photographed Asian woman in the world. These dresses are why. Borrow for shoots, exhibitions, or costume reference.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 12.0, "price_unit": "per_day", "currency": "EUR", "deposit": 60.0}]
            },
            {
                "name": "International Film Career Workshop -- Beyond Hollywood",
                "slug": "international-film-career-workshop-wong",
                "description": "When America wouldn't cast me fairly, our went to Europe and became a star in Berlin, London, and Paris. I teach you to think globally -- how to navigate international film industries, work in multiple languages, and build a career that doesn't depend on one country's approval. Marlene and I became friends because we both refused to be limited.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    # ------------------------------------------------------------------
    # 32. SATYAJIT RAY (1921-1992)
    # ------------------------------------------------------------------
    {
        "slug": "rays-editing-suite",
        "display_name": "Satyajit Ray",
        "email": "satyajit.ray@borrowhood.local",
        "date_of_birth": "1921-05-02",
        "mother_name": "Suprabha Ray",
        "father_name": "Sukumar Ray",
        "workshop_name": "Ray's Editing Suite",
        "workshop_type": "studio",
        "tagline": "The only solutions that are ever worth anything are the solutions that people find themselves",
        "bio": "Born in Calcutta into a family of writers, artists, and intellectuals. My father Sukumar was a beloved children's author and poet -- he died when I was three. My grandfather Upendrakishore founded a printing press and children's magazine. I studied economics at Presidency College, then art at Rabindranath Tagore's Shantiniketan. Tip: You don't need money to make a great film. You need eyes that see and a story that matters. Pather Panchali was made with no money -- I pawned my wife Bijoya's jewelry, shot on weekends with a skeleton crew, and it took three years. Jean Renoir visited Calcutta in 1949 and told me to shoot on location with real people. That conversation changed Indian cinema. Akira Kurosawa said: 'Not to have seen the cinema of Satyajit Ray means existing in the world without seeing the sun or the moon.' I also composed music for my later films, designed all my own title cards and posters, and wrote science fiction under the name of my character Professor Shonku. I did everything because in Bengal, you had to.",
        "telegram_username": "apu_ray",
        "city": "Calcutta",
        "country_code": "IN",
        "latitude": 22.572,
        "longitude": 88.364,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "bn", "proficiency": "native"},
            {"language_code": "en", "proficiency": "native"},
            {"language_code": "hi", "proficiency": "fluent"}
        ],
        "skills": [
            {"skill_name": "Film Directing", "category": "art", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Music Composition", "category": "music", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Graphic Design", "category": "art", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Screenwriting", "category": "art", "self_rating": 5, "years_experience": 40},
            {"skill_name": "Illustration", "category": "art", "self_rating": 5, "years_experience": 50}
        ],
        "social_links": [],
        "points": {"total_points": 2250, "rentals_completed": 60, "reviews_given": 50, "reviews_received": 76, "items_listed": 7, "helpful_flags": 43},
        "offers_training": True,
        "items": [
            {
                "name": "Zero-Budget Filmmaking Workshop -- Pather Panchali Method",
                "slug": "zero-budget-filmmaking-workshop-ray",
                "description": "I made the most acclaimed debut film in Indian history with no money, no studio, and no experience. I teach you to work with what you have: natural light, real locations, non-professional actors, and a story worth telling. We plan a short film using only resources within walking distance. Tip: Limitations are not obstacles. They are your style.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Film Music Composition Workshop -- Scoring Your Own Film",
                "slug": "film-music-composition-workshop-ray",
                "description": "I composed the music for my later films because nobody else could hear what I heard. Indian classical ragas, Western orchestration, and folk melodies -- all serving the image. We study the sitar-and-flute scoring of the Apu Trilogy and learn to write music that enhances without overpowering. Tip: The best film music makes you forget it's there.",
                "item_type": "service",
                "category": "music",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Graphic Design & Film Poster Workshop",
                "slug": "graphic-design-film-poster-workshop-ray",
                "description": "I designed every poster, title card, and publication for my films. Typography is architecture. Layout is storytelling. We design a film poster from scratch -- concept, typography, illustration, and final composition. Bring a film idea or I'll give you one. Tip: A poster is a one-second film. It must convey mood, genre, and intrigue in a single glance.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Calligraphy & Lettering Set (Bengali + Roman Scripts)",
                "slug": "calligraphy-lettering-set-ray",
                "description": "Professional calligraphy kit with nibs, inks, and practice sheets for both Bengali and Roman scripts. I designed the Ray Roman typeface -- typography was as important to me as cinematography. This kit includes my template sheets for poster lettering.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR"}]
            },
            {
                "name": "Satyajit Ray Film Collection (Criterion, Complete)",
                "slug": "satyajit-ray-criterion-collection",
                "description": "The complete Criterion Collection of my films -- the Apu Trilogy, Charulata, The Music Room, Days and Nights in the Forest, and more. Subtitled in English. Kurosawa said seeing these films was like seeing the sun and moon. Start with Pather Panchali. Bring tissues.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR"}]
            }
        ]
    },
    # ------------------------------------------------------------------
    # 33. FEDERICO FELLINI (1920-1993)
    # ------------------------------------------------------------------
    {
        "slug": "fellinis-dream-studio",
        "display_name": "Federico Fellini",
        "email": "federico.fellini@borrowhood.local",
        "date_of_birth": "1920-01-20",
        "mother_name": "Ida Barbiani",
        "father_name": "Urbano Fellini",
        "workshop_name": "Fellini's Dream Studio",
        "workshop_type": "studio",
        "tagline": "All art is autobiographical. The pearl is the oyster's autobiography.",
        "bio": "Born in Rimini on the Adriatic coast. My father was a traveling salesman for a food company. I ran away to join the circus as a boy -- just for a day, but the circus never left me. Every film I made has a circus in it, or wants to. I came to Rome at nineteen to be a cartoonist, wrote gags for radio and jokes for variety shows, then stumbled into screenwriting for Roberto Rossellini's Rome, Open City. Tip: Dreams are the raw material of cinema. Keep a dream journal. I sketched mine every morning -- thousands of drawings that became scenes, characters, entire films. 8 1/2 is literally about a director who doesn't know what his next film is. That was me. I made a masterpiece out of creative block. La Dolce Vita invented the word 'paparazzi' -- Paparazzo was a character I named after a buzzing mosquito. Giulietta Masina was my wife, my muse, and my conscience. She played Gelsomina in La Strada -- the saddest clown in cinema. We died months apart. Nino Rota scored all my films. Without his music, my dreams would have been silent.",
        "telegram_username": "maestro_fellini",
        "city": "Rimini",
        "country_code": "IT",
        "latitude": 44.061,
        "longitude": 12.566,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "it", "proficiency": "native"},
            {"language_code": "fr", "proficiency": "intermediate"}
        ],
        "skills": [
            {"skill_name": "Film Directing", "category": "art", "self_rating": 5, "years_experience": 45},
            {"skill_name": "Screenwriting", "category": "art", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Drawing & Caricature", "category": "art", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Dream Interpretation", "category": "education", "self_rating": 4, "years_experience": 40}
        ],
        "social_links": [],
        "points": {"total_points": 2300, "rentals_completed": 62, "reviews_given": 48, "reviews_received": 78, "items_listed": 7, "helpful_flags": 44},
        "offers_training": True,
        "items": [
            {
                "name": "Surrealist Filmmaking Workshop -- Dreams as Cinema",
                "slug": "surrealist-filmmaking-workshop-fellini",
                "description": "Logic is for accountants. Cinema is for dreamers. I teach you to build a film from images, feelings, and memories instead of plot outlines. We start with your strangest dream and work backward to a script. Tip: The image comes first. Then the meaning. Never the other way around. If you start with a message, you'll make a lecture, not a film.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 28.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Dream Journal Workshop -- Sketching the Unconscious",
                "slug": "dream-journal-workshop-fellini",
                "description": "I drew my dreams every morning for forty years. Thousands of sketches that became La Dolce Vita, 8 1/2, Amarcord, Juliet of the Spirits. I teach you to keep a visual dream journal -- not writing, DRAWING. Your pen remembers what your brain forgets. Bring colored pencils and a blank notebook.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Caricature Drawing Workshop -- Faces Tell Everything",
                "slug": "caricature-drawing-workshop-fellini",
                "description": "Before I was a director, I was a caricaturist in the streets of Rome. I'd draw tourists for money. A caricature captures what a photograph misses -- the ESSENCE of a face. We draw each other, strangers from photos, and characters from imagination. Tip: Exaggerate one feature. That's the person's truth.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Sketchbook & Colored Pencil Set (Fellini's Dream Kit)",
                "slug": "sketchbook-colored-pencil-dream-kit-fellini",
                "description": "Large-format sketchbook (A3) and 72 professional colored pencils -- the same tools I used for my dream journals. The sketchbook has thick paper that handles ink and pencil. Keep it by your bed. Draw before coffee. The dreams are freshest in the first five minutes.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 5.0, "price_unit": "per_day", "currency": "EUR"}]
            },
            {
                "name": "Italian Cinema History -- Neorealism to Surrealism",
                "slug": "italian-cinema-history-neorealism-surrealism",
                "description": "We screen one of my films alongside a Rossellini or De Sica film and trace the evolution from neorealism to surrealism. How did Italian cinema go from Bicycle Thieves to 8 1/2 in fifteen years? The answer is autobiographical. We'll trace it together. Nino Rota's music is mandatory.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 15.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
    # ------------------------------------------------------------------
    # 34. CARY GRANT (1904-1986)
    # ------------------------------------------------------------------
    {
        "slug": "grants-drawing-room",
        "display_name": "Cary Grant",
        "email": "cary.grant@borrowhood.local",
        "date_of_birth": "1904-01-18",
        "mother_name": "Elsie Maria Kingdon",
        "father_name": "Elias James Leach",
        "workshop_name": "Grant's Drawing Room",
        "workshop_type": "studio",
        "tagline": "Everyone wants to be Cary Grant. Even I want to be Cary Grant.",
        "bio": "Born Archibald Alexander Leach in Horfield, Bristol, England. My father worked in a clothing factory. My mother was committed to a mental institution when I was nine -- my father told me she had gone on a long holiday. I didn't learn the truth until I was thirty-one. I ran away to join Bob Pender's troupe of acrobats at thirteen. We toured America and I never went back. I reinvented myself completely -- voice, name, posture, nationality. Tip: Comedy requires absolute technical precision disguised as spontaneous charm. Every pratfall, every double-take, every raised eyebrow is choreographed. The audience must never see the machinery. Howard Hawks directed me in Bringing Up Baby, His Girl Friday, and Monkey Business. Hitchcock used me in four films -- North by Northwest, Notorious, To Catch a Thief, and Suspicion. Between Hawks and Hitchcock, I learned to be funny and dangerous in the same breath. I retired at sixty-two because I wanted to leave while they still wanted me. Mae West gave me my first break. Katharine Hepburn challenged me. Grace Kelly intimidated me -- and that's not easy. I was an acrobat first. Everything else was built on top of that.",
        "telegram_username": "archie_leach",
        "city": "Bristol",
        "country_code": "GB",
        "latitude": 51.454,
        "longitude": -2.588,
        "badge_tier": "legend",
        "languages": [
            {"language_code": "en", "proficiency": "native"}
        ],
        "skills": [
            {"skill_name": "Comedy Acting", "category": "art", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Acrobatics", "category": "sports", "self_rating": 5, "years_experience": 55},
            {"skill_name": "Physical Comedy", "category": "art", "self_rating": 5, "years_experience": 50},
            {"skill_name": "Charm & Screen Presence", "category": "art", "self_rating": 5, "years_experience": 50}
        ],
        "social_links": [],
        "points": {"total_points": 2200, "rentals_completed": 60, "reviews_given": 48, "reviews_received": 76, "items_listed": 7, "helpful_flags": 42},
        "offers_training": True,
        "items": [
            {
                "name": "Sophisticated Comedy Workshop -- Charm as a Weapon",
                "slug": "sophisticated-comedy-workshop-grant",
                "description": "Screwball comedy, romantic comedy, light thriller -- I did them all with one tool: precision disguised as ease. We work on timing, physical comedy, the double-take, and the art of making the audience fall in love with you. Tip: Be faster than the audience expects and slower than they need. That gap is where the laugh lives.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Self-Reinvention Workshop -- Becoming Who You Choose to Be",
                "slug": "self-reinvention-workshop-grant",
                "description": "Archie Leach became Cary Grant. A poor boy from Bristol became the most suave man in Hollywood. I teach you that persona is a craft -- voice, posture, wardrobe, and the stories you tell about yourself. We're not faking it. We're CHOOSING who to become. Tip: Dress for the role you want, walk like you already have it, speak like it's already yours.",
                "item_type": "service",
                "category": "education",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Acrobatics for Actors -- The Pratfall as Art",
                "slug": "acrobatics-for-actors-pratfall-grant",
                "description": "I was an acrobat before I was an actor, and every physical comedy beat I ever did came from tumbling with Bob Pender's troupe. Forward rolls, backward falls, the controlled stumble, and the pratfall that looks accidental but is engineered to the inch. We work on mats. Tip: The funnier the fall, the more controlled it actually is.",
                "item_type": "service",
                "category": "sports",
                "listings": [{"listing_type": "training", "price": 18.0, "price_unit": "per_session", "currency": "EUR"}]
            },
            {
                "name": "Vintage Suit Collection (1940s-1960s Savile Row Replicas)",
                "slug": "vintage-suit-collection-savile-row-grant",
                "description": "Four suits: charcoal flannel (North by Northwest), light gray (To Catch a Thief), midnight navy (Charade), and cream linen (An Affair to Remember). All tailored in the Savile Row style I favored -- natural shoulders, single-vent, drape cut. Tip: A suit should look like you were born in it. If it looks new, it doesn't fit yet.",
                "item_type": "physical",
                "category": "art",
                "listings": [{"listing_type": "rent", "price": 15.0, "price_unit": "per_day", "currency": "EUR", "deposit": 80.0}]
            },
            {
                "name": "Voice & Accent Transformation Coaching",
                "slug": "voice-accent-transformation-grant",
                "description": "My accent is mid-Atlantic -- a blend of Bristol working class and American sophistication that exists nowhere in nature. I invented it. I teach you to craft your own vocal persona: pitch, pace, resonance, and diction. Your voice is your calling card. Make it memorable. Tip: Record yourself and listen. Then record yourself pretending to be the person you want to be. The gap between them is your work.",
                "item_type": "service",
                "category": "art",
                "listings": [{"listing_type": "training", "price": 22.0, "price_unit": "per_session", "currency": "EUR"}]
            }
        ]
    },
]


def merge_into_seed():
    """Merge cinema legends into seed.json."""
    import json
    from pathlib import Path

    seed_path = Path(__file__).parent / "seed.json"
    with open(seed_path) as f:
        data = json.load(f)

    existing_slugs = {u["slug"] for u in data["users"]}
    existing_item_slugs = {i["slug"] for i in data["items"]}

    added_users = 0
    added_items = 0
    for legend in LEGENDS_CINEMA:
        if legend["slug"] not in existing_slugs:
            items = legend.pop("items", [])
            data["users"].append(legend)
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

    print(f"Cinema: Added {added_users} new users, {added_items} new items")
    print(f"Total users: {len(data['users'])}, Total items: {len(data['items'])}")


if __name__ == "__main__":
    merge_into_seed()
