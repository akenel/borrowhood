#!/usr/bin/env python3
"""Round 2 seed expansion: fill thin categories.

Adds 8 new users in new cities + ~24 items covering:
welding, furniture, camping, water_sports, computers, drones, cycling

Run: python3 expand_round2.py
"""
import json
from pathlib import Path

SEED_FILE = Path(__file__).parent / "seed.json"

NEW_USERS = [
    {
        "slug": "marcos-welding",
        "display_name": "Marco Ferretti",
        "email": "marcoferretti@borrowhood.local",
        "workshop_name": "Saldatura Ferretti",
        "workshop_type": "garage",
        "tagline": "Ferro e fuoco, dal 1995",
        "bio": "Welder and metalworker, 30 years. Structural steel, aluminum, stainless. Gates, railings, furniture frames. My shop has MIG, TIG, and stick welders plus a plasma cutter. Rent the tools or hire me.",
        "telegram_username": "marco_saldatura",
        "city": "Alcamo",
        "country_code": "IT",
        "latitude": 37.978,
        "longitude": 12.960,
        "badge_tier": "pillar",
        "languages": [
            {"language_code": "it", "proficiency": "native"},
            {"language_code": "en", "proficiency": "A2"}
        ],
        "skills": [
            {"skill_name": "MIG/TIG Welding", "category": "welding", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Metal Fabrication", "category": "metalwork", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Plasma Cutting", "category": "metalwork", "self_rating": 4, "years_experience": 15}
        ],
        "social_links": [],
        "points": {"total_points": 310, "rentals_completed": 15, "reviews_given": 6, "reviews_received": 18, "items_listed": 8, "helpful_flags": 5},
        "offers_repair": True,
        "offers_custom_orders": True,
    },
    {
        "slug": "giovannis-furniture",
        "display_name": "Giovanni Ferretti",
        "email": "giovanni@borrowhood.local",
        "workshop_name": "Mobili di Giovanni",
        "workshop_type": "workshop",
        "tagline": "Mobili che raccontano storie",
        "bio": "Furniture restorer and maker. 20 years turning old pieces into treasures. I strip, sand, stain, upholster, and rebuild. My workshop has every clamp, chisel, and finishing tool you could want.",
        "telegram_username": "giovanni_mobili",
        "city": "Castellammare del Golfo",
        "country_code": "IT",
        "latitude": 38.027,
        "longitude": 12.882,
        "badge_tier": "trusted",
        "languages": [
            {"language_code": "it", "proficiency": "native"},
            {"language_code": "en", "proficiency": "B1"}
        ],
        "skills": [
            {"skill_name": "Furniture Restoration", "category": "woodworking", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Upholstery", "category": "furniture", "self_rating": 5, "years_experience": 18},
            {"skill_name": "French Polishing", "category": "finishing", "self_rating": 4, "years_experience": 12}
        ],
        "social_links": [
            {"platform": "instagram", "url": "https://instagram.com/mobiledigiovanni", "label": "Restorations"}
        ],
        "points": {"total_points": 240, "rentals_completed": 11, "reviews_given": 5, "reviews_received": 13, "items_listed": 9, "helpful_flags": 4},
        "offers_repair": True,
        "offers_custom_orders": True,
        "offers_training": True,
    },
    {
        "slug": "fabios-camping",
        "display_name": "Fabio Ferretti",
        "email": "fabio@borrowhood.local",
        "workshop_name": "Avventura Sicilia",
        "workshop_type": "garage",
        "tagline": "L'avventura comincia qui",
        "bio": "Outdoor guide and gear hoarder. 15 years leading hiking, camping, and climbing trips across Sicily. I have enough tents, sleeping bags, and cooking gear to outfit a small army. Rent what you need.",
        "telegram_username": "fabio_avventura",
        "city": "San Vito lo Capo",
        "country_code": "IT",
        "latitude": 38.177,
        "longitude": 12.737,
        "badge_tier": "trusted",
        "languages": [
            {"language_code": "it", "proficiency": "native"},
            {"language_code": "en", "proficiency": "C1"},
            {"language_code": "de", "proficiency": "B1"}
        ],
        "skills": [
            {"skill_name": "Mountain Guiding", "category": "outdoor", "self_rating": 5, "years_experience": 15},
            {"skill_name": "Rock Climbing", "category": "outdoor", "self_rating": 4, "years_experience": 12},
            {"skill_name": "Camping Setup", "category": "outdoor", "self_rating": 5, "years_experience": 15}
        ],
        "social_links": [
            {"platform": "instagram", "url": "https://instagram.com/avventurasicilia", "label": "Adventures"}
        ],
        "points": {"total_points": 195, "rentals_completed": 9, "reviews_given": 4, "reviews_received": 10, "items_listed": 12, "helpful_flags": 3},
        "offers_delivery": True,
        "offers_training": True,
    },
    {
        "slug": "andreas-water",
        "display_name": "Andrea Ferretti",
        "email": "andrea@borrowhood.local",
        "workshop_name": "Blu Trapani Watersports",
        "workshop_type": "other",
        "tagline": "Il mare è la palestra più grande",
        "bio": "Windsurf and kitesurf instructor, 12 years. SUP rentals, kayak tours, snorkeling gear. Based at the beach near San Vito. Everything you need to get on the water without buying a garage full of gear.",
        "telegram_username": "andrea_blu",
        "city": "Custonaci",
        "country_code": "IT",
        "latitude": 38.078,
        "longitude": 12.674,
        "badge_tier": "trusted",
        "languages": [
            {"language_code": "it", "proficiency": "native"},
            {"language_code": "en", "proficiency": "C1"},
            {"language_code": "de", "proficiency": "B2"},
            {"language_code": "fr", "proficiency": "A2"}
        ],
        "skills": [
            {"skill_name": "Kitesurfing", "category": "water_sports", "self_rating": 5, "years_experience": 12},
            {"skill_name": "Windsurfing", "category": "water_sports", "self_rating": 5, "years_experience": 15},
            {"skill_name": "SUP Coaching", "category": "water_sports", "self_rating": 4, "years_experience": 8}
        ],
        "social_links": [
            {"platform": "instagram", "url": "https://instagram.com/blutrapani", "label": "Sessions & Conditions"}
        ],
        "points": {"total_points": 280, "rentals_completed": 14, "reviews_given": 6, "reviews_received": 16, "items_listed": 10, "helpful_flags": 5},
        "offers_training": True,
        "offers_delivery": True,
    },
    {
        "slug": "lorenzos-tech",
        "display_name": "Lorenzo Ferretti",
        "email": "lorenzo@borrowhood.local",
        "workshop_name": "TechLab Lorenzo",
        "workshop_type": "office",
        "tagline": "Tecnologia per tutti",
        "bio": "IT consultant and tech enthusiast. 15 years in the industry. I have spare laptops, monitors, networking gear, and servers that I rent to startups, students, and anyone who needs computing power without the commitment.",
        "telegram_username": "lorenzo_tech",
        "city": "Favignana",
        "country_code": "IT",
        "latitude": 37.931,
        "longitude": 12.329,
        "badge_tier": "newcomer",
        "languages": [
            {"language_code": "it", "proficiency": "native"},
            {"language_code": "en", "proficiency": "C1"}
        ],
        "skills": [
            {"skill_name": "System Administration", "category": "technology", "self_rating": 5, "years_experience": 15},
            {"skill_name": "Networking", "category": "technology", "self_rating": 4, "years_experience": 12},
            {"skill_name": "Computer Repair", "category": "technology", "self_rating": 4, "years_experience": 10}
        ],
        "social_links": [],
        "points": {"total_points": 85, "rentals_completed": 4, "reviews_given": 2, "reviews_received": 5, "items_listed": 8, "helpful_flags": 1},
        "offers_repair": True,
    },
    {
        "slug": "pietros-drones",
        "display_name": "Pietro Ferretti",
        "email": "pietro@borrowhood.local",
        "workshop_name": "SkyView Sicilia",
        "workshop_type": "studio",
        "tagline": "Vedi la Sicilia dall'alto",
        "bio": "Licensed drone pilot and aerial photographer. Real estate, events, agriculture, inspections. I have 4 drones from mini to heavy-lift. Rent a drone for your project or hire me to fly it.",
        "telegram_username": "pietro_skyview",
        "city": "Scopello",
        "country_code": "IT",
        "latitude": 38.068,
        "longitude": 12.820,
        "badge_tier": "trusted",
        "languages": [
            {"language_code": "it", "proficiency": "native"},
            {"language_code": "en", "proficiency": "B2"}
        ],
        "skills": [
            {"skill_name": "Drone Piloting", "category": "drones", "self_rating": 5, "years_experience": 8},
            {"skill_name": "Aerial Photography", "category": "photography", "self_rating": 5, "years_experience": 8},
            {"skill_name": "Video Editing", "category": "creative", "self_rating": 4, "years_experience": 6}
        ],
        "social_links": [
            {"platform": "youtube", "url": "https://youtube.com/@skyviewsicilia", "label": "Aerial Videos"}
        ],
        "points": {"total_points": 170, "rentals_completed": 8, "reviews_given": 3, "reviews_received": 9, "items_listed": 6, "helpful_flags": 2},
        "offers_training": True,
    },
    {
        "slug": "saras-cycles",
        "display_name": "Sara Ferretti",
        "email": "sara@borrowhood.local",
        "workshop_name": "Pedala Sicilia",
        "workshop_type": "garage",
        "tagline": "Due ruote, mille strade",
        "bio": "Cycling enthusiast and bike mechanic. Road bikes, mountain bikes, e-bikes, gravel bikes. I rent bikes for tourists and locals who want to explore the coast and hills without buying. Full service workshop too.",
        "telegram_username": "sara_pedala",
        "city": "Castellammare del Golfo",
        "country_code": "IT",
        "latitude": 38.029,
        "longitude": 12.885,
        "badge_tier": "trusted",
        "languages": [
            {"language_code": "it", "proficiency": "native"},
            {"language_code": "en", "proficiency": "B2"},
            {"language_code": "de", "proficiency": "A2"}
        ],
        "skills": [
            {"skill_name": "Bike Mechanics", "category": "cycling", "self_rating": 5, "years_experience": 10},
            {"skill_name": "Route Planning", "category": "outdoor", "self_rating": 4, "years_experience": 8},
            {"skill_name": "E-Bike Servicing", "category": "cycling", "self_rating": 4, "years_experience": 5}
        ],
        "social_links": [
            {"platform": "instagram", "url": "https://instagram.com/pedalasicilia", "label": "Routes & Rides"}
        ],
        "points": {"total_points": 210, "rentals_completed": 10, "reviews_given": 5, "reviews_received": 12, "items_listed": 10, "helpful_flags": 3},
        "offers_repair": True,
        "offers_delivery": True,
    },
    {
        "slug": "vittorios-marine",
        "display_name": "Vittorio Ferretti",
        "email": "vittorio@borrowhood.local",
        "workshop_name": "Marina Vittorio",
        "workshop_type": "garage",
        "tagline": "Dalla barca alla riva, tutto sotto controllo",
        "bio": "Marine mechanic and boat rental. 20 years fixing outboards, inflatables, and sailboats. I rent dinghies, snorkeling gear, wetsuits, and water toys. If it floats, I probably have it.",
        "telegram_username": "vittorio_marina",
        "city": "Bonagia",
        "country_code": "IT",
        "latitude": 38.056,
        "longitude": 12.596,
        "badge_tier": "pillar",
        "languages": [
            {"language_code": "it", "proficiency": "native"},
            {"language_code": "en", "proficiency": "B1"}
        ],
        "skills": [
            {"skill_name": "Outboard Repair", "category": "marine", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Sail Rigging", "category": "marine", "self_rating": 4, "years_experience": 15},
            {"skill_name": "Fiberglass Repair", "category": "marine", "self_rating": 4, "years_experience": 12}
        ],
        "social_links": [],
        "points": {"total_points": 255, "rentals_completed": 12, "reviews_given": 4, "reviews_received": 14, "items_listed": 9, "helpful_flags": 4},
        "offers_repair": True,
        "offers_delivery": True,
    },
]

NEW_ITEMS = [
    # ── WELDING (Marco, Alcamo) ──────────────────────────────────────
    {
        "owner_slug": "marcos-welding",
        "name": "MIG Welder (Lincoln Electric 180A)",
        "slug": "mig-welder-lincoln-electric-180a",
        "description": "Lincoln Electric 180A MIG welder with gas kit. Welds mild steel, stainless, and aluminum (with spool gun). Duty cycle: 30% at 180A. Includes 2kg wire spool, gas regulator, and welding mask.",
        "content_language": "en",
        "item_type": "physical",
        "category": "welding",
        "subcategory": "mig",
        "condition": "good",
        "brand": "Lincoln Electric",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?w=800&h=600&fit=crop&q=80", "alt_text": "Lincoln Electric MIG welder setup"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1504148455328-c376907d081c?w=800&h=600&fit=crop&q=80", "alt_text": "MIG welding in progress - bright arc"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1558618666-fcd25c85f1d7?w=800&h=600&fit=crop&q=80", "alt_text": "Welder complete kit with mask and gloves"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 25.0, "price_unit": "per_day", "currency": "EUR", "deposit": 80.0, "pickup_only": True, "notes": "Includes welding mask, gloves, and wire brush. You supply your own gas (Argon/CO2 mix). I have gas bottles for EUR 10/day extra."},
        ],
        "latitude": 37.978,
        "longitude": 12.960,
        "story": "Lincoln built this machine to last 30 years. It's only 8 years old and has welded everything from trailer hitches to garden gates. Smooth arc, clean welds."
    },
    {
        "owner_slug": "marcos-welding",
        "name": "Plasma Cutter (Hypertherm Powermax 45)",
        "slug": "plasma-cutter-hypertherm-powermax-45",
        "description": "Hypertherm Powermax 45 plasma cutter. Cuts up to 16mm steel, 12mm stainless, 12mm aluminum. Clean cuts, minimal cleanup. Includes 2 consumable sets, air compressor connection, and hand torch.",
        "content_language": "en",
        "item_type": "physical",
        "category": "welding",
        "subcategory": "cutting",
        "condition": "good",
        "brand": "Hypertherm",
        "model": "Powermax 45",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?w=800&h=600&fit=crop&q=80", "alt_text": "Hypertherm plasma cutter unit"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1558618666-fcd25c85f1d7?w=800&h=600&fit=crop&q=80", "alt_text": "Plasma cutting steel plate - sparks flying"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 35.0, "price_unit": "per_day", "currency": "EUR", "deposit": 100.0, "pickup_only": True, "notes": "Needs compressed air supply (6 bar minimum). Consumables included for light use. Heavy use = EUR 15 consumable charge."},
        ],
        "latitude": 37.978,
        "longitude": 12.960,
    },
    {
        "owner_slug": "marcos-welding",
        "name": "TIG Welder (Miller Syncrowave 210)",
        "slug": "tig-welder-miller-syncrowave-210",
        "description": "Miller Syncrowave 210 AC/DC TIG welder. The precision tool -- perfect for stainless steel, aluminum, chromoly. Foot pedal control, water-cooled torch, 10 tungsten electrodes. For clean, beautiful welds.",
        "content_language": "en",
        "item_type": "physical",
        "category": "welding",
        "subcategory": "tig",
        "condition": "good",
        "brand": "Miller",
        "model": "Syncrowave 210",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1504148455328-c376907d081c?w=800&h=600&fit=crop&q=80", "alt_text": "Miller TIG welder with foot pedal and torch"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?w=800&h=600&fit=crop&q=80", "alt_text": "TIG welding stainless steel - precision bead"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1558618666-fcd25c85f1d7?w=800&h=600&fit=crop&q=80", "alt_text": "Complete TIG setup with gas bottle and accessories"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 40.0, "price_unit": "per_day", "currency": "EUR", "deposit": 120.0, "pickup_only": True, "notes": "TIG is an art -- if you haven't done it before, book a training session first (EUR 30/hr). Argon gas bottle included."},
            {"listing_type": "training", "price": 30.0, "price_unit": "per_hour", "currency": "EUR", "notes": "Learn TIG welding from a 30-year pro. 3-hour intro session. You'll weld a practice joint and take it home."},
        ],
        "latitude": 37.978,
        "longitude": 12.960,
    },
    # ── FURNITURE (Giovanni, Castellammare del Golfo) ────────────────
    {
        "owner_slug": "giovannis-furniture",
        "name": "Upholstery Tool Kit (Professional)",
        "slug": "upholstery-tool-kit-professional",
        "description": "Complete upholstery toolkit: pneumatic staple gun, tack puller, webbing stretcher, foam cutter, sewing awl, regulator needle, fabric scissors, and 3 rolls of jute webbing. Everything to reupholster a sofa or chair.",
        "content_language": "en",
        "item_type": "physical",
        "category": "furniture",
        "subcategory": "upholstery",
        "condition": "good",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800&h=600&fit=crop&q=80", "alt_text": "Upholstery tools laid out on workbench"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1558171813-01ed3d751f32?w=800&h=600&fit=crop&q=80", "alt_text": "Pneumatic staple gun for upholstery work"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1612198188060-c7c2a3b66eae?w=800&h=600&fit=crop&q=80", "alt_text": "Chair being reupholstered with new fabric"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 15.0, "price_unit": "per_day", "currency": "EUR", "deposit": 40.0, "pickup_only": True, "notes": "Staple gun needs air compressor (rent separately or use mine at the workshop). I can advise on fabric selection."},
            {"listing_type": "training", "price": 20.0, "price_unit": "per_hour", "currency": "EUR", "notes": "Bring a chair, I'll teach you to strip and reupholster it. Full project usually takes 4-6 hours."},
        ],
        "latitude": 38.027,
        "longitude": 12.882,
    },
    {
        "owner_slug": "giovannis-furniture",
        "name": "Furniture Clamp Set (24 pieces)",
        "slug": "furniture-clamp-set-24-pieces",
        "description": "24-piece clamp set: 4 x bar clamps (900mm), 4 x bar clamps (600mm), 8 x F-clamps (various), 4 x spring clamps, 4 x band clamps. Plus wood glue and cauls. Enough to glue up a dining table.",
        "content_language": "en",
        "item_type": "physical",
        "category": "furniture",
        "subcategory": "woodworking",
        "condition": "good",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1504148455328-c376907d081c?w=800&h=600&fit=crop&q=80", "alt_text": "Furniture clamps holding table top glue-up"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1530124566582-a45a7e9ff500?w=800&h=600&fit=crop&q=80", "alt_text": "Bar clamps and F-clamps assorted set"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 10.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0, "pickup_only": True, "notes": "Clean off glue squeeze-out before return. Weekly rate: EUR 40."},
        ],
        "latitude": 38.027,
        "longitude": 12.882,
    },
    {
        "owner_slug": "giovannis-furniture",
        "name": "Floor Sander & Edger (Bona)",
        "slug": "floor-sander-edger-bona",
        "description": "Bona FlexiSand belt sander + Bona edge sander. Professional floor refinishing kit. Includes dust bag, sanding belts (40/60/80/120 grit), and finishing pads. Sand a 30sqm room in one day.",
        "content_language": "en",
        "item_type": "physical",
        "category": "furniture",
        "subcategory": "restoration",
        "condition": "good",
        "brand": "Bona",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=800&h=600&fit=crop&q=80", "alt_text": "Bona floor sander on hardwood floor"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?w=800&h=600&fit=crop&q=80", "alt_text": "Freshly sanded and finished hardwood floor"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 35.0, "price_unit": "per_day", "currency": "EUR", "deposit": 100.0, "delivery_available": True, "pickup_only": False, "notes": "Sanding belts included for one room. Extra belts EUR 8/set. I'll deliver and show you the technique. Dust bag MUST be emptied frequently."},
        ],
        "latitude": 38.027,
        "longitude": 12.882,
    },
    # ── CAMPING & OUTDOORS (Fabio, San Vito lo Capo) ─────────────────
    {
        "owner_slug": "fabios-camping",
        "name": "4-Person Tent (MSR Habitude 4)",
        "slug": "4-person-tent-msr-habitude-4",
        "description": "MSR Habitude 4 camping tent. Sleeps 4 comfortably. Full mesh inner, waterproof fly, 2 doors, 2 vestibules. Sets up in 10 minutes. Includes footprint groundsheet and repair kit.",
        "content_language": "en",
        "item_type": "physical",
        "category": "camping",
        "subcategory": "tents",
        "condition": "good",
        "brand": "MSR",
        "model": "Habitude 4",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=800&h=600&fit=crop&q=80", "alt_text": "MSR tent pitched in scenic campsite"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1478131143081-80f7f84ca84d?w=800&h=600&fit=crop&q=80", "alt_text": "Tent interior with sleeping bags set up"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1517824806704-9040b037703b?w=800&h=600&fit=crop&q=80", "alt_text": "Camping under the stars - tent with fairy lights"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 15.0, "price_unit": "per_day", "currency": "EUR", "deposit": 40.0, "delivery_available": True, "pickup_only": False, "notes": "Shake out sand before packing. Dry the fly if it rained. I deliver to campgrounds within 20km of San Vito. Weekly rate: EUR 60."},
        ],
        "latitude": 38.177,
        "longitude": 12.737,
    },
    {
        "owner_slug": "fabios-camping",
        "name": "Camping Kitchen Kit (Full Setup)",
        "slug": "camping-kitchen-kit-full-setup",
        "description": "Complete camp kitchen: 2-burner stove, 4-person cookware set, utensils, cutting board, collapsible wash basin, water container (20L), and fold-out kitchen table with windscreen. Cook like home, outdoors.",
        "content_language": "en",
        "item_type": "physical",
        "category": "camping",
        "subcategory": "cooking",
        "condition": "good",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=800&h=600&fit=crop&q=80", "alt_text": "Camp kitchen setup with stove and cookware"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1517824806704-9040b037703b?w=800&h=600&fit=crop&q=80", "alt_text": "Outdoor cooking at campsite with mountain view"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 12.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0, "delivery_available": True, "pickup_only": False, "notes": "Gas canisters not included (buy at any petrol station). Clean all pots before return. Weekly rate: EUR 50."},
        ],
        "latitude": 38.177,
        "longitude": 12.737,
    },
    {
        "owner_slug": "fabios-camping",
        "name": "Rock Climbing Gear Set (2 person)",
        "slug": "rock-climbing-gear-set-2-person",
        "description": "2-person climbing kit: 2 harnesses (adjustable), 60m dynamic rope (9.5mm), 12 quickdraws, 4 locking carabiners, belay device (ATC), chalk bags, and helmet. All UIAA certified. Inspected before every rental.",
        "content_language": "en",
        "item_type": "physical",
        "category": "camping",
        "subcategory": "climbing",
        "condition": "good",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1522163182402-834f871fd851?w=800&h=600&fit=crop&q=80", "alt_text": "Rock climbing gear - harness, rope, and carabiners"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=800&h=600&fit=crop&q=80", "alt_text": "Climbing quickdraws and locking carabiners"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1517824806704-9040b037703b?w=800&h=600&fit=crop&q=80", "alt_text": "Climber on rock face with Mediterranean view"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 20.0, "price_unit": "per_day", "currency": "EUR", "deposit": 60.0, "pickup_only": True, "notes": "EXPERIENCED CLIMBERS ONLY. I inspect every piece before and after rental. Rope and harnesses have log books. San Vito has world-class limestone routes."},
            {"listing_type": "training", "price": 40.0, "price_unit": "per_session", "currency": "EUR", "notes": "Half-day intro to outdoor climbing. Gear included. Meet at the crag. You'll learn to belay, tie in, and climb your first 5a route."},
        ],
        "latitude": 38.177,
        "longitude": 12.737,
        "story": "San Vito lo Capo has some of the best climbing in Europe. Tourists fly in from Germany and France just for the rock. Why buy gear you'll use twice a year? Rent mine."
    },
    # ── WATER SPORTS (Andrea, Custonaci + Vittorio, Bonagia) ─────────
    {
        "owner_slug": "andreas-water",
        "name": "Kitesurf Complete Kit (Cabrinha)",
        "slug": "kitesurf-complete-kit-cabrinha",
        "description": "Cabrinha Switchblade 12m kite, bar and lines, harness (M/L), and 140cm twin-tip board. Intermediate setup, perfect for 12-25 knot wind. Pump and repair kit included.",
        "content_language": "en",
        "item_type": "physical",
        "category": "water_sports",
        "subcategory": "kitesurfing",
        "condition": "good",
        "brand": "Cabrinha",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1526188717906-ab4a2f949f71?w=800&h=600&fit=crop&q=80", "alt_text": "Kitesurf kite inflated on the beach"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1502680390548-bdbac40529a6?w=800&h=600&fit=crop&q=80", "alt_text": "Kitesurfer riding waves at sunset"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=800&h=600&fit=crop&q=80", "alt_text": "Kitesurf equipment laid out on sand"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 40.0, "price_unit": "per_day", "currency": "EUR", "deposit": 150.0, "pickup_only": True, "notes": "MUST show IKO certification or equivalent experience. Beginners: book a lesson instead. Rinse everything with fresh water after session."},
            {"listing_type": "training", "price": 60.0, "price_unit": "per_session", "currency": "EUR", "notes": "3-hour kitesurf lesson. All gear included. Beach safety, kite control, water start. Group of 2 max."},
        ],
        "latitude": 38.078,
        "longitude": 12.674,
        "story": "The Trapani coast has perfect thermal winds May through October. Flat water, consistent side-on. This is where I learned, and this kite has taught 200 students."
    },
    {
        "owner_slug": "andreas-water",
        "name": "Windsurf Board & Sail Set",
        "slug": "windsurf-board-sail-set",
        "description": "Freeride windsurf board (150L), boom, mast, and 5.5m sail. Stable enough for beginners, fast enough for intermediates. Includes wetsuit (M or L), harness, and roof rack pads.",
        "content_language": "en",
        "item_type": "physical",
        "category": "water_sports",
        "subcategory": "windsurfing",
        "condition": "good",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1502680390548-bdbac40529a6?w=800&h=600&fit=crop&q=80", "alt_text": "Windsurf board and sail on beach"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1526188717906-ab4a2f949f71?w=800&h=600&fit=crop&q=80", "alt_text": "Windsurfer on Mediterranean waves"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 30.0, "price_unit": "per_day", "currency": "EUR", "deposit": 80.0, "pickup_only": True, "notes": "Wetsuit sizes M and L available. Rinse sail and board with fresh water. I can deliver to Lo Stagnone (best flat water spot) for EUR 10."},
        ],
        "latitude": 38.078,
        "longitude": 12.674,
    },
    {
        "owner_slug": "vittorios-marine",
        "name": "Snorkeling Gear Set (4 person)",
        "slug": "snorkeling-gear-set-4-person",
        "description": "4 complete snorkeling sets: masks (tempered glass, silicone skirt), dry-top snorkels, and fins (sizes 38-46). Plus underwater camera (GoPro Hero 8) with waterproof housing. See the Egadi marine reserve in HD.",
        "content_language": "en",
        "item_type": "physical",
        "category": "water_sports",
        "subcategory": "snorkeling",
        "condition": "good",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800&h=600&fit=crop&q=80", "alt_text": "Snorkeling gear set - masks, fins, and snorkels"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1502680390548-bdbac40529a6?w=800&h=600&fit=crop&q=80", "alt_text": "Snorkeling in clear Mediterranean water"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1526188717906-ab4a2f949f71?w=800&h=600&fit=crop&q=80", "alt_text": "Underwater camera with waterproof housing"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 15.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0, "delivery_available": True, "pickup_only": False, "notes": "GoPro comes with 32GB card. Rinse everything in fresh water. Best spots: Cala Rossa (Favignana), Scopello, Zingaro reserve."},
        ],
        "latitude": 38.056,
        "longitude": 12.596,
    },
    {
        "owner_slug": "vittorios-marine",
        "name": "Inflatable Dinghy with Outboard (3.3m)",
        "slug": "inflatable-dinghy-outboard-3-3m",
        "description": "3.3m rigid inflatable dinghy with 15HP Mercury outboard. Seats 4. Plywood floor, aluminum keel. Perfect for exploring coves, fishing, or getting to Favignana without the ferry. Fuel tank and anchor included.",
        "content_language": "en",
        "item_type": "physical",
        "category": "water_sports",
        "subcategory": "boating",
        "condition": "good",
        "brand": "Mercury",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800&h=600&fit=crop&q=80", "alt_text": "Inflatable dinghy on calm turquoise water"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1502680390548-bdbac40529a6?w=800&h=600&fit=crop&q=80", "alt_text": "Mercury outboard motor on dinghy"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 60.0, "price_unit": "per_day", "currency": "EUR", "deposit": 200.0, "pickup_only": True, "notes": "Boat license required (patente nautica). Fuel not included. Life jackets for 4 included. Return by sunset. Half-day rate: EUR 40."},
        ],
        "latitude": 38.056,
        "longitude": 12.596,
        "story": "From Bonagia, Favignana is 30 minutes by dinghy. No ferry schedule, no crowds. Just you, the sea, and the best swimming in the Mediterranean."
    },
    {
        "owner_slug": "vittorios-marine",
        "name": "Wetsuit Collection (Full Range)",
        "slug": "wetsuit-collection-full-range",
        "description": "8 wetsuits in stock: 3mm shorties (S/M/L), 3mm full suits (S/M/L/XL), and 5mm winter suit (M/L). Billabong and O'Neill brands. For surfing, diving, kitesurfing, or just cold-water swimming.",
        "content_language": "en",
        "item_type": "physical",
        "category": "water_sports",
        "subcategory": "wetsuits",
        "condition": "good",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1502680390548-bdbac40529a6?w=800&h=600&fit=crop&q=80", "alt_text": "Wetsuits hanging to dry on rack"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1526188717906-ab4a2f949f71?w=800&h=600&fit=crop&q=80", "alt_text": "Wetsuit in action - water sports session"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 8.0, "price_unit": "per_day", "currency": "EUR", "deposit": 20.0, "delivery_available": True, "pickup_only": False, "notes": "Rinse inside and out with fresh water after use. Hang to dry in shade (not direct sun). Weekly rate: EUR 30."},
        ],
        "latitude": 38.056,
        "longitude": 12.596,
    },
    # ── COMPUTERS (Lorenzo, Favignana) ───────────────────────────────
    {
        "owner_slug": "lorenzos-tech",
        "name": "MacBook Pro M2 (14-inch)",
        "slug": "macbook-pro-m2-14-inch",
        "description": "MacBook Pro 14-inch, M2 Pro chip, 16GB RAM, 512GB SSD. Perfect for video editing, development, or design work. Includes charger, USB-C hub, and sleeve. Clean install, ready to go.",
        "content_language": "en",
        "item_type": "physical",
        "category": "computers",
        "subcategory": "laptops",
        "condition": "like_new",
        "brand": "Apple",
        "model": "MacBook Pro 14 M2",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&h=600&fit=crop&q=80", "alt_text": "MacBook Pro on desk with external display"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&h=600&fit=crop&q=80", "alt_text": "MacBook Pro keyboard and trackpad close-up"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=800&h=600&fit=crop&q=80", "alt_text": "Laptop with USB-C hub and accessories"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 25.0, "price_unit": "per_day", "currency": "EUR", "deposit": 200.0, "pickup_only": True, "notes": "Wiped clean between rentals. Install your own apps. ID required. Weekly rate: EUR 100. Monthly: EUR 250."},
        ],
        "latitude": 37.931,
        "longitude": 12.329,
        "story": "I keep 3 MacBooks because clients always need one. Better to rent a good machine than suffer on a bad one."
    },
    {
        "owner_slug": "lorenzos-tech",
        "name": "27-inch 4K Monitor (LG UltraFine)",
        "slug": "27-inch-4k-monitor-lg-ultrafine",
        "description": "LG 27UK850-W 27-inch 4K monitor. USB-C input (charges laptop while connected), HDR10, IPS panel, height adjustable stand. For designers, developers, or anyone who needs screen real estate.",
        "content_language": "en",
        "item_type": "physical",
        "category": "computers",
        "subcategory": "monitors",
        "condition": "good",
        "brand": "LG",
        "model": "27UK850-W",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&h=600&fit=crop&q=80", "alt_text": "LG 4K monitor on desk with clean setup"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=800&h=600&fit=crop&q=80", "alt_text": "Monitor connected to laptop via USB-C"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 10.0, "price_unit": "per_day", "currency": "EUR", "deposit": 50.0, "delivery_available": True, "pickup_only": False, "notes": "USB-C cable included. Plug one cable into your laptop: video + power. Monthly rate: EUR 60."},
        ],
        "latitude": 37.931,
        "longitude": 12.329,
    },
    {
        "owner_slug": "lorenzos-tech",
        "name": "Home Server (Synology NAS DS920+)",
        "slug": "home-server-synology-nas-ds920-plus",
        "description": "Synology DS920+ NAS with 4 x 4TB drives (16TB total, RAID 5 = 12TB usable). Pre-configured for file sharing, backup, media server (Plex), and Docker containers. Plug in, connect, go.",
        "content_language": "en",
        "item_type": "physical",
        "category": "computers",
        "subcategory": "networking",
        "condition": "good",
        "brand": "Synology",
        "model": "DS920+",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800&h=600&fit=crop&q=80", "alt_text": "Synology NAS server unit"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=800&h=600&fit=crop&q=80", "alt_text": "NAS connected to network with Ethernet cables"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 15.0, "price_unit": "per_day", "currency": "EUR", "deposit": 80.0, "pickup_only": True, "notes": "Perfect for events (media server), temporary office backup, or trying Plex before buying. Data wiped between rentals. Monthly rate: EUR 80."},
        ],
        "latitude": 37.931,
        "longitude": 12.329,
    },
    # ── DRONES (Pietro, Scopello) ────────────────────────────────────
    {
        "owner_slug": "pietros-drones",
        "name": "DJI Mavic 3 Pro (Fly More Combo)",
        "slug": "dji-mavic-3-pro-fly-more-combo",
        "description": "DJI Mavic 3 Pro with Hasselblad camera. 4/3 CMOS sensor, 5.1K video, 46-min flight time. Fly More combo: 3 batteries, charging hub, ND filters, carrying case. The gold standard for aerial video.",
        "content_language": "en",
        "item_type": "physical",
        "category": "drones",
        "subcategory": "camera_drones",
        "condition": "like_new",
        "brand": "DJI",
        "model": "Mavic 3 Pro",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1507582020474-9a35b7d455d9?w=800&h=600&fit=crop&q=80", "alt_text": "DJI Mavic 3 Pro hovering over coast"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1473968512647-3e447244af8f?w=800&h=600&fit=crop&q=80", "alt_text": "Drone controller and Fly More accessories"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1508614589041-895b88991e3e?w=800&h=600&fit=crop&q=80", "alt_text": "Aerial view of Sicilian coastline from drone"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 50.0, "price_unit": "per_day", "currency": "EUR", "deposit": 200.0, "pickup_only": True, "notes": "EU drone license (A1/A3) required. Insurance proof needed. I brief you on local no-fly zones. 3 batteries = ~2 hours total flight time."},
            {"listing_type": "service", "price": 80.0, "price_unit": "per_session", "currency": "EUR", "notes": "I fly for you -- real estate, events, inspections, tourism content. 1-hour session, edited 4K video delivered within 48 hours."},
        ],
        "latitude": 38.068,
        "longitude": 12.820,
        "story": "Scopello from the air is unreal. The tonnara, the faraglioni, the turquoise water. This drone has captured it all. Now it can capture your project too."
    },
    {
        "owner_slug": "pietros-drones",
        "name": "DJI Mini 4 Pro (Beginner Friendly)",
        "slug": "dji-mini-4-pro-beginner-friendly",
        "description": "DJI Mini 4 Pro, under 249g (no registration needed in most EU zones). 4K/60fps, 48MP photos, 34-min flight, obstacle avoidance. 2 batteries, charger, controller, and spare propellers. Perfect for travel.",
        "content_language": "en",
        "item_type": "physical",
        "category": "drones",
        "subcategory": "camera_drones",
        "condition": "like_new",
        "brand": "DJI",
        "model": "Mini 4 Pro",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1507582020474-9a35b7d455d9?w=800&h=600&fit=crop&q=80", "alt_text": "DJI Mini 4 Pro - compact drone in hand"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1473968512647-3e447244af8f?w=800&h=600&fit=crop&q=80", "alt_text": "Mini drone flying over olive grove"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 25.0, "price_unit": "per_day", "currency": "EUR", "deposit": 100.0, "pickup_only": True, "notes": "Under 249g = no registration in open category. I'll give you a 15-minute tutorial. Great for vacation photos and video."},
        ],
        "latitude": 38.068,
        "longitude": 12.820,
    },
    {
        "owner_slug": "pietros-drones",
        "name": "FPV Racing Drone Kit (2 drones)",
        "slug": "fpv-racing-drone-kit-2-drones",
        "description": "2 x 5-inch FPV racing quads (BetaFPV), DJI FPV goggles V2, radio controller, 8 batteries, parallel charger, spare props. Experience drone racing first-person view. Absolute adrenaline.",
        "content_language": "en",
        "item_type": "physical",
        "category": "drones",
        "subcategory": "fpv_racing",
        "condition": "good",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1507582020474-9a35b7d455d9?w=800&h=600&fit=crop&q=80", "alt_text": "FPV racing drones with goggles and controller"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1473968512647-3e447244af8f?w=800&h=600&fit=crop&q=80", "alt_text": "FPV drone mid-flight at speed"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1508614589041-895b88991e3e?w=800&h=600&fit=crop&q=80", "alt_text": "DJI FPV goggles - first person view"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 35.0, "price_unit": "per_day", "currency": "EUR", "deposit": 100.0, "pickup_only": True, "notes": "MUST fly in open areas only. No flying near people or buildings. I'll demo the goggles and controls. Broken props free, broken frame EUR 20."},
            {"listing_type": "training", "price": 25.0, "price_unit": "per_hour", "currency": "EUR", "notes": "Learn FPV flying in a safe field. I control the safety switch. 2-hour intro gets you airborne. It's like nothing else."},
        ],
        "latitude": 38.068,
        "longitude": 12.820,
    },
    # ── CYCLING (Sara, Castellammare del Golfo) ──────────────────────
    {
        "owner_slug": "saras-cycles",
        "name": "Road Bike (Bianchi Via Nirone 7)",
        "slug": "road-bike-bianchi-via-nirone-7",
        "description": "Bianchi Via Nirone 7, aluminum frame, Shimano 105 groupset. Sizes 52/54/56cm available. Carbon fork, compact gearing (perfect for Sicilian hills). Helmet, lock, and repair kit included.",
        "content_language": "en",
        "item_type": "physical",
        "category": "cycling",
        "subcategory": "road",
        "condition": "good",
        "brand": "Bianchi",
        "model": "Via Nirone 7",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1576435728678-68d0fbf94e91?w=800&h=600&fit=crop&q=80", "alt_text": "Bianchi road bike on coastal road"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=800&h=600&fit=crop&q=80", "alt_text": "Road bike close-up - Shimano 105 groupset"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&h=600&fit=crop&q=80", "alt_text": "Cycling along the Sicilian coast"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 20.0, "price_unit": "per_day", "currency": "EUR", "deposit": 80.0, "delivery_available": True, "pickup_only": False, "notes": "Tell me your height and I'll set up the right size. Helmet included. GPX routes for the best coastal loops available on request."},
        ],
        "latitude": 38.029,
        "longitude": 12.885,
        "story": "Bianchi celeste blue on a Sicilian coastal road -- it doesn't get better than that. The Via Nirone is the perfect all-rounder: light enough for hills, comfortable enough for long days."
    },
    {
        "owner_slug": "saras-cycles",
        "name": "E-Bike (Specialized Turbo Vado 4.0)",
        "slug": "e-bike-specialized-turbo-vado-4-0",
        "description": "Specialized Turbo Vado 4.0 e-bike. 320Wh battery, 120km range in eco mode. Step-through frame, hydraulic disc brakes, integrated lights. Makes hills disappear. Perfect for touring or commuting.",
        "content_language": "en",
        "item_type": "physical",
        "category": "cycling",
        "subcategory": "e-bikes",
        "condition": "like_new",
        "brand": "Specialized",
        "model": "Turbo Vado 4.0",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1576435728678-68d0fbf94e91?w=800&h=600&fit=crop&q=80", "alt_text": "Specialized e-bike on Sicilian hilltop road"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=800&h=600&fit=crop&q=80", "alt_text": "E-bike display showing battery and assist level"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 30.0, "price_unit": "per_day", "currency": "EUR", "deposit": 100.0, "delivery_available": True, "pickup_only": False, "notes": "Charged to 100% at pickup. Charger included for multi-day rentals. The climb to Erice is nothing on this bike. Weekly rate: EUR 120."},
        ],
        "latitude": 38.029,
        "longitude": 12.885,
    },
    {
        "owner_slug": "saras-cycles",
        "name": "Mountain Bike (Canyon Spectral 125)",
        "slug": "mountain-bike-canyon-spectral-125",
        "description": "Canyon Spectral 125 trail mountain bike. 29er wheels, 125mm travel, SRAM GX Eagle drivetrain, dropper post. Perfect for the trails around Monte Cofano and Zingaro reserve. Helmet, gloves, and pump included.",
        "content_language": "en",
        "item_type": "physical",
        "category": "cycling",
        "subcategory": "mountain",
        "condition": "good",
        "brand": "Canyon",
        "model": "Spectral 125",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1576435728678-68d0fbf94e91?w=800&h=600&fit=crop&q=80", "alt_text": "Canyon mountain bike on dirt trail"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=800&h=600&fit=crop&q=80", "alt_text": "Mountain bike suspension fork and disc brakes"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&h=600&fit=crop&q=80", "alt_text": "Trail riding through Sicilian hills"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 25.0, "price_unit": "per_day", "currency": "EUR", "deposit": 100.0, "delivery_available": True, "pickup_only": False, "notes": "Check tire pressure before ride (30psi front, 32psi rear). I can suggest trails for all levels. Wash the bike if you ride in mud please."},
        ],
        "latitude": 38.029,
        "longitude": 12.885,
    },
]

def main():
    with open(SEED_FILE) as f:
        data = json.load(f)

    existing_user_slugs = {u["slug"] for u in data["users"]}
    existing_item_slugs = {i["slug"] for i in data["items"]}

    added_users = 0
    for user in NEW_USERS:
        if user["slug"] not in existing_user_slugs:
            data["users"].append(user)
            added_users += 1
            print(f"  User: {user['display_name']} ({user['city']})")

    added_items = 0
    for item in NEW_ITEMS:
        if item["slug"] not in existing_item_slugs:
            data["items"].append(item)
            added_items += 1
            print(f"  Item: {item['name']} [{item['category']}]")

    with open(SEED_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nRound 2 done: {added_users} users, {added_items} items added.")
    print(f"Total: {len(data['users'])} users, {len(data['items'])} items")

if __name__ == "__main__":
    main()
