#!/usr/bin/env python3
"""Expand BorrowHood seed data.

Adds:
- Images to 3 giveaway items that are missing them
- 15 new professional users
- 30 new items (2 per new user) with 2-4 photos each

Run: python3 expand_seed.py
"""
import json
from pathlib import Path

SEED_FILE = Path(__file__).parent / "seed.json"

# ── New Users ────────────────────────────────────────────────────────
NEW_USERS = [
    {
        "slug": "sofias-studio",
        "display_name": "Sofia Ferraro",
        "email": "sofia@borrowhood.local",
        "workshop_name": "Luce di Sicilia",
        "workshop_type": "studio",
        "tagline": "La luce racconta la storia",
        "bio": "Professional photographer for 12 years. Weddings, portraits, food photography. I have more cameras than friends. Equipment rental when I'm not on a shoot.",
        "telegram_username": "sofia_foto",
        "city": "Trapani",
        "country_code": "IT",
        "latitude": 38.019,
        "longitude": 12.535,
        "badge_tier": "trusted",
        "languages": [
            {"language_code": "it", "proficiency": "native"},
            {"language_code": "en", "proficiency": "B2"},
            {"language_code": "fr", "proficiency": "A2"}
        ],
        "skills": [
            {"skill_name": "Portrait Photography", "category": "photography", "self_rating": 5, "years_experience": 12},
            {"skill_name": "Food Photography", "category": "photography", "self_rating": 5, "years_experience": 8},
            {"skill_name": "Photo Editing", "category": "photography", "self_rating": 4, "years_experience": 10}
        ],
        "social_links": [
            {"platform": "instagram", "url": "https://instagram.com/lucedisicilia", "label": "Portfolio"}
        ],
        "points": {"total_points": 185, "rentals_completed": 6, "reviews_given": 4, "reviews_received": 8, "items_listed": 12, "helpful_flags": 3},
        "offers_training": True,
    },
    {
        "slug": "giuseppes-electric",
        "display_name": "Giuseppe Russo",
        "email": "giuseppe@borrowhood.local",
        "workshop_name": "Elettrica Russo",
        "workshop_type": "garage",
        "tagline": "Corrente giusta, prezzo giusto",
        "bio": "Licensed electrician, 20 years in the trade. Residential and commercial. I rent out my specialty tools when they're not on a job site. Why buy a cable puller you'll use once?",
        "telegram_username": "giuseppe_elettrica",
        "city": "Trapani",
        "country_code": "IT",
        "latitude": 38.024,
        "longitude": 12.541,
        "badge_tier": "trusted",
        "languages": [
            {"language_code": "it", "proficiency": "native"},
            {"language_code": "en", "proficiency": "A2"}
        ],
        "skills": [
            {"skill_name": "Electrical Installation", "category": "electrical", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Solar Panel Installation", "category": "electrical", "self_rating": 4, "years_experience": 8},
            {"skill_name": "Home Automation", "category": "electrical", "self_rating": 3, "years_experience": 5}
        ],
        "social_links": [],
        "points": {"total_points": 220, "rentals_completed": 10, "reviews_given": 5, "reviews_received": 12, "items_listed": 8, "helpful_flags": 4},
        "offers_repair": True,
        "offers_pickup": True,
    },
    {
        "slug": "chiaras-kitchen",
        "display_name": "Chiara Lombardi",
        "email": "chiara@borrowhood.local",
        "workshop_name": "Sapori di Chiara",
        "workshop_type": "kitchen",
        "tagline": "Cucina come nonna insegnava",
        "bio": "Chef for 18 years, trained in Palermo and Rome. Now I run cooking classes from my home kitchen. Professional equipment rental for events and catering. If you can taste the love, I made it.",
        "telegram_username": "chiara_sapori",
        "city": "Trapani",
        "country_code": "IT",
        "latitude": 38.016,
        "longitude": 12.533,
        "badge_tier": "pillar",
        "languages": [
            {"language_code": "it", "proficiency": "native"},
            {"language_code": "en", "proficiency": "B1"},
            {"language_code": "es", "proficiency": "A2"}
        ],
        "skills": [
            {"skill_name": "Sicilian Cuisine", "category": "cooking", "self_rating": 5, "years_experience": 18},
            {"skill_name": "Pastry & Desserts", "category": "cooking", "self_rating": 5, "years_experience": 15},
            {"skill_name": "Catering", "category": "cooking", "self_rating": 4, "years_experience": 10}
        ],
        "social_links": [
            {"platform": "instagram", "url": "https://instagram.com/saporidichiara", "label": "Daily Dishes"}
        ],
        "points": {"total_points": 310, "rentals_completed": 14, "reviews_given": 8, "reviews_received": 16, "items_listed": 10, "helpful_flags": 6},
        "offers_training": True,
        "offers_delivery": True,
        "offers_custom_orders": True,
    },
    {
        "slug": "lucas-plumbing",
        "display_name": "Luca Di Maggio",
        "email": "luca@borrowhood.local",
        "workshop_name": "Idraulica Di Maggio",
        "workshop_type": "garage",
        "tagline": "Nessuna perdita è troppo piccola",
        "bio": "Third-generation plumber. My grandfather laid pipes in Trapani before I was born. I have specialty tools most plumbers rent from supply houses -- now you can rent them from me instead.",
        "telegram_username": "luca_idraulica",
        "city": "Trapani",
        "country_code": "IT",
        "latitude": 38.021,
        "longitude": 12.544,
        "badge_tier": "trusted",
        "languages": [
            {"language_code": "it", "proficiency": "native"},
            {"language_code": "en", "proficiency": "B1"}
        ],
        "skills": [
            {"skill_name": "Plumbing", "category": "plumbing", "self_rating": 5, "years_experience": 22},
            {"skill_name": "Pipe Fitting", "category": "plumbing", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Drain Inspection", "category": "plumbing", "self_rating": 4, "years_experience": 12}
        ],
        "social_links": [],
        "points": {"total_points": 175, "rentals_completed": 8, "reviews_given": 3, "reviews_received": 10, "items_listed": 6, "helpful_flags": 2},
        "offers_repair": True,
        "offers_pickup": True,
    },
    {
        "slug": "francescas-flowers",
        "display_name": "Francesca Vitale",
        "email": "francesca@borrowhood.local",
        "workshop_name": "Fiori di Francesca",
        "workshop_type": "studio",
        "tagline": "Ogni fiore ha un messaggio",
        "bio": "Florist and event decorator. 15 years creating arrangements for weddings, funerals, and everything in between. My tools and vases are available when I'm between events.",
        "telegram_username": "francesca_fiori",
        "city": "Trapani",
        "country_code": "IT",
        "latitude": 38.017,
        "longitude": 12.536,
        "badge_tier": "newcomer",
        "languages": [
            {"language_code": "it", "proficiency": "native"},
            {"language_code": "en", "proficiency": "A2"}
        ],
        "skills": [
            {"skill_name": "Floral Arrangement", "category": "creative", "self_rating": 5, "years_experience": 15},
            {"skill_name": "Event Decoration", "category": "creative", "self_rating": 4, "years_experience": 12},
            {"skill_name": "Garden Design", "category": "gardening", "self_rating": 3, "years_experience": 8}
        ],
        "social_links": [
            {"platform": "instagram", "url": "https://instagram.com/fioridifrancesca", "label": "Arrangements"}
        ],
        "points": {"total_points": 90, "rentals_completed": 4, "reviews_given": 2, "reviews_received": 5, "items_listed": 7, "helpful_flags": 1},
        "offers_delivery": True,
        "offers_custom_orders": True,
    },
    {
        "slug": "paolos-painting",
        "display_name": "Paolo Costa",
        "email": "paolo@borrowhood.local",
        "workshop_name": "Colori di Paolo",
        "workshop_type": "garage",
        "tagline": "Colore su ogni parete",
        "bio": "House painter and decorator for 25 years. Interior, exterior, wallpaper, stucco -- you name it. My spray equipment alone costs EUR 3,000. Rent it for EUR 30/day.",
        "telegram_username": "paolo_colori",
        "city": "Trapani",
        "country_code": "IT",
        "latitude": 38.023,
        "longitude": 12.539,
        "badge_tier": "trusted",
        "languages": [
            {"language_code": "it", "proficiency": "native"},
            {"language_code": "en", "proficiency": "A1"}
        ],
        "skills": [
            {"skill_name": "Interior Painting", "category": "painting", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Wallpaper Installation", "category": "painting", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Decorative Stucco", "category": "painting", "self_rating": 4, "years_experience": 15}
        ],
        "social_links": [],
        "points": {"total_points": 145, "rentals_completed": 7, "reviews_given": 3, "reviews_received": 8, "items_listed": 5, "helpful_flags": 2},
        "offers_repair": True,
    },
    {
        "slug": "carmens-sewing",
        "display_name": "Carmen Romano",
        "email": "carmen@borrowhood.local",
        "workshop_name": "Sartoria Carmen",
        "workshop_type": "studio",
        "tagline": "Fatto su misura, fatto con amore",
        "bio": "Seamstress since I was 16. Alterations, custom dresses, curtains, upholstery. My industrial sewing machines handle everything from silk to canvas. Rent a machine or bring your project to me.",
        "telegram_username": "carmen_sartoria",
        "city": "Trapani",
        "country_code": "IT",
        "latitude": 38.020,
        "longitude": 12.531,
        "badge_tier": "pillar",
        "languages": [
            {"language_code": "it", "proficiency": "native"},
            {"language_code": "en", "proficiency": "B1"},
            {"language_code": "es", "proficiency": "B2"}
        ],
        "skills": [
            {"skill_name": "Tailoring", "category": "sewing", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Pattern Making", "category": "sewing", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Upholstery", "category": "sewing", "self_rating": 4, "years_experience": 15}
        ],
        "social_links": [],
        "points": {"total_points": 260, "rentals_completed": 12, "reviews_given": 6, "reviews_received": 14, "items_listed": 8, "helpful_flags": 5},
        "offers_training": True,
        "offers_custom_orders": True,
        "offers_repair": True,
    },
    {
        "slug": "robertos-fishing",
        "display_name": "Roberto Di Stefano",
        "email": "roberto@borrowhood.local",
        "workshop_name": "Il Pescatore Roberto",
        "workshop_type": "other",
        "tagline": "Il mare dà, il mare prende",
        "bio": "Fisherman for 35 years. The sea is my office. When I'm not fishing, my boat and gear sit idle. Why let a good fishing rod collect salt? Rent my equipment and I'll tell you where the fish are.",
        "telegram_username": "roberto_pesca",
        "city": "Trapani",
        "country_code": "IT",
        "latitude": 38.014,
        "longitude": 12.529,
        "badge_tier": "trusted",
        "languages": [
            {"language_code": "it", "proficiency": "native"},
            {"language_code": "en", "proficiency": "A1"}
        ],
        "skills": [
            {"skill_name": "Deep Sea Fishing", "category": "fishing", "self_rating": 5, "years_experience": 35},
            {"skill_name": "Net Repair", "category": "fishing", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Boat Maintenance", "category": "marine", "self_rating": 4, "years_experience": 25}
        ],
        "social_links": [],
        "points": {"total_points": 130, "rentals_completed": 6, "reviews_given": 2, "reviews_received": 7, "items_listed": 5, "helpful_flags": 1},
        "offers_training": True,
    },
    {
        "slug": "elenas-yoga",
        "display_name": "Elena Rossi",
        "email": "elena@borrowhood.local",
        "workshop_name": "Yoga con Elena",
        "workshop_type": "studio",
        "tagline": "Respira, muoviti, vivi",
        "bio": "Certified yoga instructor, 10 years teaching. Hatha, Vinyasa, and Yin. I run classes on the beach in summer and in my home studio in winter. Equipment available for groups and retreats.",
        "telegram_username": "elena_yoga",
        "city": "Trapani",
        "country_code": "IT",
        "latitude": 38.015,
        "longitude": 12.534,
        "badge_tier": "newcomer",
        "languages": [
            {"language_code": "it", "proficiency": "native"},
            {"language_code": "en", "proficiency": "C1"},
            {"language_code": "de", "proficiency": "A2"}
        ],
        "skills": [
            {"skill_name": "Hatha Yoga", "category": "wellness", "self_rating": 5, "years_experience": 10},
            {"skill_name": "Meditation", "category": "wellness", "self_rating": 4, "years_experience": 8},
            {"skill_name": "Breathwork", "category": "wellness", "self_rating": 4, "years_experience": 6}
        ],
        "social_links": [
            {"platform": "instagram", "url": "https://instagram.com/yogaconelena", "label": "Classes & Events"}
        ],
        "points": {"total_points": 75, "rentals_completed": 3, "reviews_given": 2, "reviews_received": 4, "items_listed": 6, "helpful_flags": 1},
        "offers_training": True,
    },
    {
        "slug": "matteos-carpentry",
        "display_name": "Matteo Bruno",
        "email": "matteo@borrowhood.local",
        "workshop_name": "Falegnameria Matteo",
        "workshop_type": "workshop",
        "tagline": "Il legno non mente mai",
        "bio": "Carpenter and furniture maker, 18 years. I build kitchens, wardrobes, and one-off pieces. My workshop has a full set of power tools -- table saw, planer, jointer, band saw. Rent time on the machines or hire me for the job.",
        "telegram_username": "matteo_legno",
        "city": "Erice",
        "country_code": "IT",
        "latitude": 38.037,
        "longitude": 12.587,
        "badge_tier": "trusted",
        "languages": [
            {"language_code": "it", "proficiency": "native"},
            {"language_code": "en", "proficiency": "B1"}
        ],
        "skills": [
            {"skill_name": "Furniture Making", "category": "woodworking", "self_rating": 5, "years_experience": 18},
            {"skill_name": "Kitchen Installation", "category": "woodworking", "self_rating": 5, "years_experience": 15},
            {"skill_name": "Wood Turning", "category": "woodworking", "self_rating": 4, "years_experience": 10}
        ],
        "social_links": [],
        "points": {"total_points": 200, "rentals_completed": 9, "reviews_given": 4, "reviews_received": 11, "items_listed": 7, "helpful_flags": 3},
        "offers_repair": True,
        "offers_custom_orders": True,
    },
    {
        "slug": "valentinas-bakery",
        "display_name": "Valentina Serra",
        "email": "valentina@borrowhood.local",
        "workshop_name": "Dolci di Valentina",
        "workshop_type": "kitchen",
        "tagline": "La vita è dolce",
        "bio": "Pastry chef, specialty in Sicilian sweets -- cannoli, cassata, frutta di Martorana. I trained at a pasticceria in Palermo for 6 years before opening my home workshop. Professional baking equipment for rent.",
        "telegram_username": "valentina_dolci",
        "city": "Trapani",
        "country_code": "IT",
        "latitude": 38.018,
        "longitude": 12.540,
        "badge_tier": "newcomer",
        "languages": [
            {"language_code": "it", "proficiency": "native"},
            {"language_code": "en", "proficiency": "A2"}
        ],
        "skills": [
            {"skill_name": "Sicilian Pastry", "category": "baking", "self_rating": 5, "years_experience": 14},
            {"skill_name": "Cake Decorating", "category": "baking", "self_rating": 5, "years_experience": 12},
            {"skill_name": "Chocolate Tempering", "category": "baking", "self_rating": 4, "years_experience": 8}
        ],
        "social_links": [
            {"platform": "instagram", "url": "https://instagram.com/dolcidivalentina", "label": "Sweet Creations"}
        ],
        "points": {"total_points": 65, "rentals_completed": 3, "reviews_given": 1, "reviews_received": 3, "items_listed": 5, "helpful_flags": 0},
        "offers_training": True,
        "offers_custom_orders": True,
    },
    {
        "slug": "antonios-garage",
        "display_name": "Antonio Ferretti",
        "email": "antonio@borrowhood.local",
        "workshop_name": "Officina Antonio",
        "workshop_type": "garage",
        "tagline": "Ogni motore ha una voce",
        "bio": "Auto mechanic for 28 years. Specializing in European cars -- Fiat, Alfa Romeo, Lancia, VW. My garage has a lift, diagnostic equipment, and every specialty tool you can't find at the hardware store.",
        "telegram_username": "antonio_officina",
        "city": "Trapani",
        "country_code": "IT",
        "latitude": 38.026,
        "longitude": 12.543,
        "badge_tier": "pillar",
        "languages": [
            {"language_code": "it", "proficiency": "native"},
            {"language_code": "en", "proficiency": "A1"}
        ],
        "skills": [
            {"skill_name": "Auto Repair", "category": "mechanics", "self_rating": 5, "years_experience": 28},
            {"skill_name": "Engine Diagnostics", "category": "mechanics", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Bodywork", "category": "mechanics", "self_rating": 3, "years_experience": 10}
        ],
        "social_links": [],
        "points": {"total_points": 280, "rentals_completed": 13, "reviews_given": 5, "reviews_received": 15, "items_listed": 9, "helpful_flags": 4},
        "offers_repair": True,
        "offers_pickup": True,
    },
    {
        "slug": "giulias-design",
        "display_name": "Giulia La Rosa",
        "email": "giulia@borrowhood.local",
        "workshop_name": "Studio Giulia Design",
        "workshop_type": "studio",
        "tagline": "Lo spazio racconta chi sei",
        "bio": "Interior designer, 10 years. Residential and small commercial. I have professional tools -- laser levels, wallpaper steamers, floor sanders -- that homeowners need once but can't justify buying.",
        "telegram_username": "giulia_design",
        "city": "Trapani",
        "country_code": "IT",
        "latitude": 38.022,
        "longitude": 12.537,
        "badge_tier": "newcomer",
        "languages": [
            {"language_code": "it", "proficiency": "native"},
            {"language_code": "en", "proficiency": "B2"},
            {"language_code": "fr", "proficiency": "B1"}
        ],
        "skills": [
            {"skill_name": "Interior Design", "category": "design", "self_rating": 5, "years_experience": 10},
            {"skill_name": "Color Consulting", "category": "design", "self_rating": 5, "years_experience": 10},
            {"skill_name": "Space Planning", "category": "design", "self_rating": 4, "years_experience": 8}
        ],
        "social_links": [
            {"platform": "instagram", "url": "https://instagram.com/studiogiuliadesign", "label": "Projects"}
        ],
        "points": {"total_points": 55, "rentals_completed": 2, "reviews_given": 1, "reviews_received": 3, "items_listed": 6, "helpful_flags": 0},
        "offers_custom_orders": True,
    },
    {
        "slug": "tommasos-farm",
        "display_name": "Tommaso Amato",
        "email": "tommaso@borrowhood.local",
        "workshop_name": "Oliveto Amato",
        "workshop_type": "garden",
        "tagline": "Olio buono, vita buona",
        "bio": "Olive farmer, fourth generation. 200 trees on the hills above Erice. I make extra virgin olive oil the old way. My farming equipment -- nets, presses, pruning tools -- is available outside harvest season.",
        "telegram_username": "tommaso_olive",
        "city": "Erice",
        "country_code": "IT",
        "latitude": 38.035,
        "longitude": 12.580,
        "badge_tier": "trusted",
        "languages": [
            {"language_code": "it", "proficiency": "native"},
            {"language_code": "en", "proficiency": "A1"}
        ],
        "skills": [
            {"skill_name": "Olive Cultivation", "category": "farming", "self_rating": 5, "years_experience": 30},
            {"skill_name": "Oil Pressing", "category": "farming", "self_rating": 5, "years_experience": 25},
            {"skill_name": "Pruning", "category": "gardening", "self_rating": 5, "years_experience": 30}
        ],
        "social_links": [],
        "points": {"total_points": 160, "rentals_completed": 7, "reviews_given": 3, "reviews_received": 9, "items_listed": 5, "helpful_flags": 2},
        "offers_training": True,
    },
    {
        "slug": "alessias-music",
        "display_name": "Alessia Colombo",
        "email": "alessia@borrowhood.local",
        "workshop_name": "Musica con Alessia",
        "workshop_type": "studio",
        "tagline": "La musica è il linguaggio dell'anima",
        "bio": "Music teacher, piano and guitar, 12 years. Conservatory trained in Palermo. I give private lessons and rent instruments to students who aren't ready to buy. Everyone deserves to play.",
        "telegram_username": "alessia_musica",
        "city": "Trapani",
        "country_code": "IT",
        "latitude": 38.019,
        "longitude": 12.538,
        "badge_tier": "newcomer",
        "languages": [
            {"language_code": "it", "proficiency": "native"},
            {"language_code": "en", "proficiency": "B2"},
            {"language_code": "de", "proficiency": "A1"}
        ],
        "skills": [
            {"skill_name": "Piano", "category": "music", "self_rating": 5, "years_experience": 20},
            {"skill_name": "Classical Guitar", "category": "music", "self_rating": 4, "years_experience": 15},
            {"skill_name": "Music Theory", "category": "music", "self_rating": 5, "years_experience": 12}
        ],
        "social_links": [
            {"platform": "youtube", "url": "https://youtube.com/@musicaconalessia", "label": "Lessons & Performances"}
        ],
        "points": {"total_points": 70, "rentals_completed": 3, "reviews_given": 2, "reviews_received": 4, "items_listed": 8, "helpful_flags": 1},
        "offers_training": True,
    },
]

# ── New Items (2 per new user, 2-4 photos each) ─────────────────────
NEW_ITEMS = [
    # Sofia - Photographer
    {
        "owner_slug": "sofias-studio",
        "name": "Canon EOS R5 Camera Kit",
        "slug": "canon-eos-r5-camera-kit",
        "description": "Canon EOS R5 mirrorless camera body with 24-70mm f/2.8L lens, 70-200mm f/2.8L lens, 2 batteries, charger, and camera bag. Professional grade, perfect for events and commercial shoots.",
        "content_language": "en",
        "item_type": "physical",
        "category": "photography",
        "subcategory": "cameras",
        "condition": "excellent",
        "brand": "Canon",
        "model": "EOS R5",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800&h=600&fit=crop&q=80", "alt_text": "Canon EOS R5 camera body - front view"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=800&h=600&fit=crop&q=80", "alt_text": "Canon camera with lens kit - complete set"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1452587925148-ce544e77e70d?w=800&h=600&fit=crop&q=80", "alt_text": "Professional camera in use - photography session"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 45.0, "price_unit": "per_day", "currency": "EUR", "deposit": 200.0, "pickup_only": True, "notes": "Includes 30-min orientation. Insurance required for events. SD cards not included."},
        ],
        "latitude": 38.019,
        "longitude": 12.535,
        "story": "Saved for 2 years to buy this kit. It's my workhorse but sits idle 3 days a week. Rather than let it sleep in the bag, I rent it to photographers who need pro gear without the pro price tag."
    },
    {
        "owner_slug": "sofias-studio",
        "name": "Photography Studio Backdrop Kit",
        "slug": "photography-studio-backdrop-kit",
        "description": "Complete backdrop system: 3m x 6m support stand, 3 muslin backdrops (white, black, grey), 2 softbox lights, reflector kit. Sets up in 15 minutes.",
        "content_language": "en",
        "item_type": "physical",
        "category": "photography",
        "subcategory": "studio",
        "condition": "good",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1604754742629-3e5728249d73?w=800&h=600&fit=crop&q=80", "alt_text": "Photography backdrop kit - studio setup"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1471341971476-ae15ff5dd4ea?w=800&h=600&fit=crop&q=80", "alt_text": "Studio lighting softbox equipment"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 20.0, "price_unit": "per_day", "currency": "EUR", "deposit": 50.0, "delivery_available": True, "pickup_only": False, "notes": "Free delivery within Trapani. Setup assistance available for EUR 10."},
        ],
        "latitude": 38.019,
        "longitude": 12.535,
    },
    # Giuseppe - Electrician
    {
        "owner_slug": "giuseppes-electric",
        "name": "Electrical Testing Kit (Fluke)",
        "slug": "electrical-testing-kit-fluke",
        "description": "Fluke 117 multimeter, Fluke T6 voltage tester, wire stripper set, crimping tool, cable puller, voltage detector pen. Everything you need for residential electrical work.",
        "content_language": "en",
        "item_type": "physical",
        "category": "tools",
        "subcategory": "electrical",
        "condition": "good",
        "brand": "Fluke",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1621905251189-08b45d6a269e?w=800&h=600&fit=crop&q=80", "alt_text": "Electrical testing kit with Fluke multimeter"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1558618666-fcd25c85f1d7?w=800&h=600&fit=crop&q=80", "alt_text": "Wire strippers and electrical tools laid out"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1555664424-778a1e5e1b48?w=800&h=600&fit=crop&q=80", "alt_text": "Fluke multimeter close-up display"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 15.0, "price_unit": "per_day", "currency": "EUR", "deposit": 40.0, "pickup_only": True, "notes": "I'll show you how to use the Fluke if you've never used one. 5-minute crash course included."},
        ],
        "latitude": 38.024,
        "longitude": 12.541,
        "story": "A good multimeter costs EUR 300+. Most people need one for a single job. Rent mine, save EUR 280, do the job right."
    },
    {
        "owner_slug": "giuseppes-electric",
        "name": "Honda EU2200i Portable Generator",
        "slug": "honda-eu2200i-portable-generator",
        "description": "Honda EU2200i inverter generator. 2200W, super quiet (48-57 dB), fuel efficient (8hrs on 1 tank). Perfect for camping, outdoor events, or backup power. Includes fuel can and oil.",
        "content_language": "en",
        "item_type": "physical",
        "category": "tools",
        "subcategory": "power",
        "condition": "good",
        "brand": "Honda",
        "model": "EU2200i",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1611117775350-ac3950990985?w=800&h=600&fit=crop&q=80", "alt_text": "Honda portable generator - compact unit"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?w=800&h=600&fit=crop&q=80", "alt_text": "Generator in use at outdoor event"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 25.0, "price_unit": "per_day", "currency": "EUR", "deposit": 100.0, "delivery_available": True, "pickup_only": False, "notes": "Delivered with full tank. Return with full tank or pay EUR 10 refueling fee. Free delivery within 10km."},
        ],
        "latitude": 38.024,
        "longitude": 12.541,
    },
    # Chiara - Chef
    {
        "owner_slug": "chiaras-kitchen",
        "name": "Wüsthof Professional Knife Set (8 pieces)",
        "slug": "wusthof-professional-knife-set-8pc",
        "description": "Wüsthof Classic 8-piece knife set in walnut block. Chef's knife, bread knife, utility, paring, carving, santoku, kitchen shears, honing steel. German forged, razor sharp.",
        "content_language": "en",
        "item_type": "physical",
        "category": "kitchen",
        "subcategory": "knives",
        "condition": "excellent",
        "brand": "Wüsthof",
        "model": "Classic",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1593618998160-e34014e67546?w=800&h=600&fit=crop&q=80", "alt_text": "Wüsthof knife set in walnut block"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1556910103-1c02745aae4d?w=800&h=600&fit=crop&q=80", "alt_text": "Professional chef's knife on cutting board"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1466637574441-749b8f19452f?w=800&h=600&fit=crop&q=80", "alt_text": "Chef preparing food with professional knife"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 12.0, "price_unit": "per_day", "currency": "EUR", "deposit": 60.0, "pickup_only": True, "notes": "Freshly sharpened before each rental. Please hand-wash only, no dishwasher."},
        ],
        "latitude": 38.016,
        "longitude": 12.533,
        "story": "A EUR 800 knife set. Most home cooks will never justify it. But for that one dinner party where you want to prep like a pro? Rent mine for EUR 12."
    },
    {
        "owner_slug": "chiaras-kitchen",
        "name": "Commercial Pasta Machine (Imperia)",
        "slug": "commercial-pasta-machine-imperia",
        "description": "Imperia RMN220 electric pasta machine with 6 attachments -- spaghetti, fettuccine, ravioli, lasagna, tagliatelle, and pappardelle. Motor-driven, table clamp mount. Makes 15kg/hour.",
        "content_language": "en",
        "item_type": "physical",
        "category": "kitchen",
        "subcategory": "appliances",
        "condition": "good",
        "brand": "Imperia",
        "model": "RMN220",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1556761223-4c4282c73f77?w=800&h=600&fit=crop&q=80", "alt_text": "Commercial pasta machine with attachments"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1547592180-85f173990554?w=800&h=600&fit=crop&q=80", "alt_text": "Fresh pasta being made with machine"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1551183053-bf91a1d81141?w=800&h=600&fit=crop&q=80", "alt_text": "Handmade pasta shapes from Imperia machine"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 15.0, "price_unit": "per_day", "currency": "EUR", "deposit": 40.0, "delivery_available": True, "pickup_only": False, "notes": "Includes recipe card for basic egg pasta dough. Clean all attachments before return."},
            {"listing_type": "training", "price": 25.0, "price_unit": "per_session", "currency": "EUR", "notes": "2-hour pasta making class. You go home with 1kg of fresh pasta and the skills to make more. All ingredients included."},
        ],
        "latitude": 38.016,
        "longitude": 12.533,
    },
    # Luca - Plumber
    {
        "owner_slug": "lucas-plumbing",
        "name": "Pipe Threading Set (RIDGID)",
        "slug": "pipe-threading-set-ridgid",
        "description": "RIDGID 12-R manual pipe threader with 6 die heads (1/2\" to 2\"), pipe cutter, reamer, pipe vise, thread sealant, and carrying case. Everything for threading steel and iron pipe.",
        "content_language": "en",
        "item_type": "physical",
        "category": "tools",
        "subcategory": "plumbing",
        "condition": "good",
        "brand": "RIDGID",
        "model": "12-R",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1585704032915-c3400ca199e7?w=800&h=600&fit=crop&q=80", "alt_text": "RIDGID pipe threading set in case"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1504148455328-c376907d081c?w=800&h=600&fit=crop&q=80", "alt_text": "Pipe threading tool in use"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 20.0, "price_unit": "per_day", "currency": "EUR", "deposit": 80.0, "pickup_only": True, "notes": "Apply cutting oil before each thread. I'll show you how if you haven't threaded pipe before."},
        ],
        "latitude": 38.021,
        "longitude": 12.544,
        "story": "My grandfather's set. He threaded every pipe in the Trapani fish market with these dies. RIDGID tools last forever."
    },
    {
        "owner_slug": "lucas-plumbing",
        "name": "Drain Camera Inspection Kit",
        "slug": "drain-camera-inspection-kit",
        "description": "30m drain inspection camera with 7-inch LCD screen, LED lights, video recording. See inside pipes before you start digging. Saves you from guessing where the blockage is.",
        "content_language": "en",
        "item_type": "physical",
        "category": "tools",
        "subcategory": "plumbing",
        "condition": "excellent",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=800&h=600&fit=crop&q=80", "alt_text": "Drain inspection camera with LCD display"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=800&h=600&fit=crop&q=80", "alt_text": "Camera probe for pipe inspection"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?w=800&h=600&fit=crop&q=80", "alt_text": "Drain camera kit in carrying case"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 30.0, "price_unit": "per_day", "currency": "EUR", "deposit": 100.0, "pickup_only": True, "notes": "Battery lasts 6 hours. Comes with USB cable to download recordings. Clean the probe with disinfectant after use."},
            {"listing_type": "service", "price": 50.0, "price_unit": "per_visit", "currency": "EUR", "notes": "I come to you, inspect the drain, record video, and tell you what's wrong. Report included."},
        ],
        "latitude": 38.021,
        "longitude": 12.544,
    },
    # Francesca - Florist
    {
        "owner_slug": "francescas-flowers",
        "name": "Professional Floral Arrangement Kit",
        "slug": "professional-floral-arrangement-kit",
        "description": "Complete floral kit: 20 crystal vases (various sizes), oasis foam blocks, floral tape, wire, cutters, ribbon collection. Perfect for weddings and events. Enough for 8-10 table centerpieces.",
        "content_language": "en",
        "item_type": "physical",
        "category": "creative",
        "subcategory": "floral",
        "condition": "good",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1490750967868-88aa4f44baae?w=800&h=600&fit=crop&q=80", "alt_text": "Professional floral arrangement in crystal vase"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1487530811176-3780de880c2d?w=800&h=600&fit=crop&q=80", "alt_text": "Collection of floral arrangement tools"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1455659817273-f96807779a8a?w=800&h=600&fit=crop&q=80", "alt_text": "Crystal vases set up for event decorating"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 35.0, "price_unit": "per_day", "currency": "EUR", "deposit": 80.0, "delivery_available": True, "pickup_only": False, "notes": "Available for weekend events. Vases must be returned clean and dry. Missing/broken vases charged at EUR 15 each."},
        ],
        "latitude": 38.017,
        "longitude": 12.536,
    },
    {
        "owner_slug": "francescas-flowers",
        "name": "Wedding Arch & Decoration Kit",
        "slug": "wedding-arch-decoration-kit",
        "description": "Metal wedding arch (2.2m x 1.5m), 4 column stands, white fabric draping, LED fairy lights (10m), and silk flower garlands. Sets up in 30 minutes. Used for 50+ weddings.",
        "content_language": "en",
        "item_type": "physical",
        "category": "events",
        "subcategory": "decoration",
        "condition": "good",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1519741497674-611481863552?w=800&h=600&fit=crop&q=80", "alt_text": "Wedding arch decorated with flowers and fabric"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1465495976277-4387d4b0b4c6?w=800&h=600&fit=crop&q=80", "alt_text": "Wedding ceremony setup with arch and lights"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 50.0, "price_unit": "per_day", "currency": "EUR", "deposit": 100.0, "delivery_available": True, "pickup_only": False, "notes": "Free setup within Trapani if booked for full weekend. Weekday discount: EUR 35/day."},
        ],
        "latitude": 38.017,
        "longitude": 12.536,
        "story": "Built this arch for my sister's wedding. Now it's been to 50 more. Every bride asks 'Is this the same arch from the photos?' Yes. Yes it is."
    },
    # Paolo - Painter
    {
        "owner_slug": "paolos-painting",
        "name": "Wagner Airless Paint Sprayer",
        "slug": "wagner-airless-paint-sprayer",
        "description": "Wagner Control Pro 250M airless paint sprayer. Covers a room in 20 minutes instead of 2 hours with a roller. Low overspray technology. Includes hose, gun, and 3 tip sizes.",
        "content_language": "en",
        "item_type": "physical",
        "category": "tools",
        "subcategory": "painting",
        "condition": "good",
        "brand": "Wagner",
        "model": "Control Pro 250M",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1562259929-b4e1fd3aef09?w=800&h=600&fit=crop&q=80", "alt_text": "Airless paint sprayer in action on wall"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1589939705384-5185137a7f0f?w=800&h=600&fit=crop&q=80", "alt_text": "Wagner paint sprayer setup with hoses"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1558618666-fcd25c85f1d7?w=800&h=600&fit=crop&q=80", "alt_text": "Professional painting equipment ready for work"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 30.0, "price_unit": "per_day", "currency": "EUR", "deposit": 80.0, "pickup_only": True, "notes": "MUST clean immediately after use or the pump seizes. I'll demonstrate cleaning procedure at pickup. 5-minute orientation included."},
        ],
        "latitude": 38.023,
        "longitude": 12.539,
        "story": "Bought this for EUR 600. It's paid for itself 20 times over. But it sits in the van 4 days a week. Your walls deserve better than a roller."
    },
    {
        "owner_slug": "paolos-painting",
        "name": "Professional Scaffold Tower (2m Platform)",
        "slug": "professional-scaffold-tower-2m",
        "description": "Aluminium scaffold tower, 2m working platform height (3.7m reach). Lockable wheels, adjustable legs, safety rail. Holds 150kg. Fits through standard doors. Way safer than a ladder.",
        "content_language": "en",
        "item_type": "physical",
        "category": "tools",
        "subcategory": "access",
        "condition": "good",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=800&h=600&fit=crop&q=80", "alt_text": "Aluminium scaffold tower assembled"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=800&h=600&fit=crop&q=80", "alt_text": "Scaffold platform with safety rails"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 15.0, "price_unit": "per_day", "currency": "EUR", "deposit": 50.0, "delivery_available": True, "pickup_only": False, "notes": "Assembles in 20 minutes. I'll deliver and set up for EUR 20 extra. Weekly rate: EUR 60."},
        ],
        "latitude": 38.023,
        "longitude": 12.539,
    },
    # Carmen - Seamstress
    {
        "owner_slug": "carmens-sewing",
        "name": "Industrial Sewing Machine (Juki DDL-8700)",
        "slug": "industrial-sewing-machine-juki-ddl8700",
        "description": "Juki DDL-8700 single needle lockstitch. Sews everything from silk to denim to canvas. 5500 stitches per minute. Table-mounted with servo motor (quiet). Professional grade.",
        "content_language": "en",
        "item_type": "physical",
        "category": "tools",
        "subcategory": "sewing",
        "condition": "good",
        "brand": "Juki",
        "model": "DDL-8700",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1558171813-01ed3d751f32?w=800&h=600&fit=crop&q=80", "alt_text": "Industrial Juki sewing machine at workstation"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1605289355680-75fb41239154?w=800&h=600&fit=crop&q=80", "alt_text": "Sewing machine close-up with thread"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1612198188060-c7c2a3b66eae?w=800&h=600&fit=crop&q=80", "alt_text": "Professional sewing setup with fabric"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 20.0, "price_unit": "per_day", "currency": "EUR", "deposit": 60.0, "pickup_only": True, "notes": "Available at my workshop. Bring your own fabric and thread. I'll set the tension for your material."},
            {"listing_type": "training", "price": 15.0, "price_unit": "per_hour", "currency": "EUR", "notes": "Learn to sew on a real machine, not a toy. 2-hour minimum. You'll make a tote bag in your first session."},
        ],
        "latitude": 38.020,
        "longitude": 12.531,
        "story": "This machine has been running 8 hours a day for 15 years. Juki builds them to last a lifetime. It handles silk at 8am and canvas at 2pm without missing a stitch."
    },
    {
        "owner_slug": "carmens-sewing",
        "name": "Adjustable Dress Form (Size 36-46)",
        "slug": "adjustable-dress-form-size-36-46",
        "description": "Professional adjustable dress form, European sizes 36-46. 12-point adjustment (bust, waist, hips, back, shoulders). Wheeled stand. Essential for fitting custom garments.",
        "content_language": "en",
        "item_type": "physical",
        "category": "tools",
        "subcategory": "sewing",
        "condition": "good",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1558171813-01ed3d751f32?w=800&h=600&fit=crop&q=80", "alt_text": "Adjustable dress form with measurement tape"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1612198188060-c7c2a3b66eae?w=800&h=600&fit=crop&q=80", "alt_text": "Dress form with pinned fabric pattern"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 8.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0, "delivery_available": True, "pickup_only": False, "notes": "Set to your measurements before pickup. Weekly rate: EUR 35. Monthly: EUR 100."},
        ],
        "latitude": 38.020,
        "longitude": 12.531,
    },
    # Roberto - Fisherman
    {
        "owner_slug": "robertos-fishing",
        "name": "Deep Sea Fishing Rod Set (3 rods)",
        "slug": "deep-sea-fishing-rod-set-3-rods",
        "description": "3 heavy-duty fishing rods: trolling rod (30-50lb), jigging rod (20-40lb), bottom fishing rod (50-80lb). Penn reels, braided line, tackle box with 200+ lures and hooks. Ready for tuna, swordfish, grouper.",
        "content_language": "en",
        "item_type": "physical",
        "category": "sports",
        "subcategory": "fishing",
        "condition": "good",
        "brand": "Penn",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800&h=600&fit=crop&q=80", "alt_text": "Deep sea fishing rods on boat"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1514469480255-2e0f5afacf7d?w=800&h=600&fit=crop&q=80", "alt_text": "Fishing tackle box with lures and hooks"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1498654896293-37aacf113fd9?w=800&h=600&fit=crop&q=80", "alt_text": "Fishing reels close-up - Penn equipment"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 25.0, "price_unit": "per_day", "currency": "EUR", "deposit": 60.0, "pickup_only": True, "notes": "Rods are rigged and ready. I'll tell you where the fish are biting. Rinse with fresh water after saltwater use."},
        ],
        "latitude": 38.014,
        "longitude": 12.529,
        "story": "These rods have caught more tuna than I can count. The trolling rod landed a 180kg bluefin in 2019. They know the sea."
    },
    {
        "owner_slug": "robertos-fishing",
        "name": "Fishing Kayak (Sit-on-Top, 3.5m)",
        "slug": "fishing-kayak-sit-on-top-3-5m",
        "description": "Ocean fishing kayak, sit-on-top design. 3.5m long, rated for 150kg. 2 rod holders, anchor trolley, waterproof storage hatch, comfortable seat with back support. Paddle included.",
        "content_language": "en",
        "item_type": "physical",
        "category": "sports",
        "subcategory": "water",
        "condition": "good",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1526188717906-ab4a2f949f71?w=800&h=600&fit=crop&q=80", "alt_text": "Fishing kayak on calm water at sunset"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=800&h=600&fit=crop&q=80", "alt_text": "Sit-on-top kayak with fishing rod holders"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 20.0, "price_unit": "per_day", "currency": "EUR", "deposit": 50.0, "delivery_available": True, "pickup_only": False, "notes": "Life jacket included. I can deliver to any launch point within 15km. Roof rack straps provided if you transport yourself."},
        ],
        "latitude": 38.014,
        "longitude": 12.529,
    },
    # Elena - Yoga
    {
        "owner_slug": "elenas-yoga",
        "name": "Yoga Equipment Set (10 person group)",
        "slug": "yoga-equipment-set-10-person",
        "description": "10 premium yoga mats (6mm, non-slip), 20 cork blocks, 10 cotton straps, 10 bolsters, 5 meditation cushions. Everything for a group class or retreat. Comes in storage bags.",
        "content_language": "en",
        "item_type": "physical",
        "category": "wellness",
        "subcategory": "yoga",
        "condition": "good",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=800&h=600&fit=crop&q=80", "alt_text": "Yoga mats and blocks arranged for group class"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=800&h=600&fit=crop&q=80", "alt_text": "Yoga equipment - mats, blocks, and straps"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1545389336-cf090694435e?w=800&h=600&fit=crop&q=80", "alt_text": "Group yoga session with mats set up outdoors"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 25.0, "price_unit": "per_day", "currency": "EUR", "deposit": 50.0, "delivery_available": True, "pickup_only": False, "notes": "Mats are sanitized between rentals. Perfect for retreats, corporate events, or beach yoga sessions. Weekly rate: EUR 100."},
        ],
        "latitude": 38.015,
        "longitude": 12.534,
    },
    {
        "owner_slug": "elenas-yoga",
        "name": "Tibetan Singing Bowl Collection (7 bowls)",
        "slug": "tibetan-singing-bowl-collection-7",
        "description": "Set of 7 handmade Tibetan singing bowls, one for each chakra. Sizes from 10cm to 30cm. Includes mallets and cushions. Used for sound healing, meditation, and yoga classes.",
        "content_language": "en",
        "item_type": "physical",
        "category": "wellness",
        "subcategory": "meditation",
        "condition": "excellent",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1591228127791-8e2eaef098d3?w=800&h=600&fit=crop&q=80", "alt_text": "Tibetan singing bowls arranged on wooden surface"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1545389336-cf090694435e?w=800&h=600&fit=crop&q=80", "alt_text": "Sound healing session with singing bowls"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 15.0, "price_unit": "per_day", "currency": "EUR", "deposit": 40.0, "pickup_only": True, "notes": "Handle with care -- these are hand-forged in Nepal. I'll demonstrate playing technique at pickup. Sound healing session available for EUR 30/hour."},
        ],
        "latitude": 38.015,
        "longitude": 12.534,
        "story": "Brought these back from Nepal in 2019. Each bowl was chosen by a master craftsman for its specific tone. When you play all seven together, the room vibrates."
    },
    # Matteo - Carpenter
    {
        "owner_slug": "matteos-carpentry",
        "name": "DeWalt Table Saw (DWE7491RS)",
        "slug": "dewalt-table-saw-dwe7491rs",
        "description": "DeWalt DWE7491RS portable table saw with rolling stand. 10\" blade, 32.5\" rip capacity, rack and pinion fence. Cuts through hardwood like butter. Dust collection port included.",
        "content_language": "en",
        "item_type": "physical",
        "category": "tools",
        "subcategory": "woodworking",
        "condition": "good",
        "brand": "DeWalt",
        "model": "DWE7491RS",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1504148455328-c376907d081c?w=800&h=600&fit=crop&q=80", "alt_text": "DeWalt table saw set up in workshop"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1530124566582-a45a7e9ff500?w=800&h=600&fit=crop&q=80", "alt_text": "Table saw cutting hardwood plank"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1572981779307-38b8cabb2407?w=800&h=600&fit=crop&q=80", "alt_text": "Portable table saw on rolling stand"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 25.0, "price_unit": "per_day", "currency": "EUR", "deposit": 80.0, "delivery_available": True, "pickup_only": False, "notes": "Blade freshly sharpened. I deliver and pick up within Trapani/Erice. Safety goggles and push stick included."},
        ],
        "latitude": 38.037,
        "longitude": 12.587,
        "story": "This saw has built 200+ kitchens. The fence is dead accurate -- I check it with a dial indicator every month. Your cuts will be perfect."
    },
    {
        "owner_slug": "matteos-carpentry",
        "name": "Router Table Set (Bosch + Kreg)",
        "slug": "router-table-set-bosch-kreg",
        "description": "Bosch 1617EVSPK router with Kreg precision router table. Fixed base and plunge base. 12 router bits (straight, round-over, chamfer, dovetail, etc.). Perfect for edge profiling, joinery, and dadoes.",
        "content_language": "en",
        "item_type": "physical",
        "category": "tools",
        "subcategory": "woodworking",
        "condition": "good",
        "brand": "Bosch",
        "model": "1617EVSPK",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1530124566582-a45a7e9ff500?w=800&h=600&fit=crop&q=80", "alt_text": "Router table setup with bits collection"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1504148455328-c376907d081c?w=800&h=600&fit=crop&q=80", "alt_text": "Router profiling an edge on hardwood"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 20.0, "price_unit": "per_day", "currency": "EUR", "deposit": 60.0, "pickup_only": True, "notes": "Available at my workshop. You can use it here or take it with you. Router bits charged at EUR 5 each if damaged."},
        ],
        "latitude": 38.037,
        "longitude": 12.587,
    },
    # Valentina - Baker
    {
        "owner_slug": "valentinas-bakery",
        "name": "Commercial Stand Mixer (Hobart N50)",
        "slug": "commercial-stand-mixer-hobart-n50",
        "description": "Hobart N50 commercial mixer, 5-quart capacity. The bakery standard. Comes with dough hook, flat beater, wire whip. 3-speed. Makes 3kg of bread dough or 5kg of cake batter per batch.",
        "content_language": "en",
        "item_type": "physical",
        "category": "kitchen",
        "subcategory": "appliances",
        "condition": "good",
        "brand": "Hobart",
        "model": "N50",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1594385208974-2f8bb07b7c24?w=800&h=600&fit=crop&q=80", "alt_text": "Hobart commercial stand mixer"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800&h=600&fit=crop&q=80", "alt_text": "Bread dough in commercial mixer bowl"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1486427944544-d2c246c4df14?w=800&h=600&fit=crop&q=80", "alt_text": "Pastries made with commercial mixer"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 15.0, "price_unit": "per_day", "currency": "EUR", "deposit": 50.0, "pickup_only": True, "notes": "Heavy (25kg) -- bring help or a trolley. All attachments included. Clean before return."},
        ],
        "latitude": 38.018,
        "longitude": 12.540,
        "story": "Rescued this from a bakery that was closing. Hobart built these to run 24/7 for 30 years. Mine's only 12 years old -- it's barely warmed up."
    },
    {
        "owner_slug": "valentinas-bakery",
        "name": "Bread Proofing Cabinet (12 trays)",
        "slug": "bread-proofing-cabinet-12-trays",
        "description": "Professional bread proofing cabinet with temperature and humidity control. 12 full-size trays. Digital controller (25-45°C, 50-90% humidity). Perfect for bread, brioche, pizza dough, and croissants.",
        "content_language": "en",
        "item_type": "physical",
        "category": "kitchen",
        "subcategory": "baking",
        "condition": "good",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800&h=600&fit=crop&q=80", "alt_text": "Proofing cabinet with bread dough rising"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1517433670267-08bbd4be890f?w=800&h=600&fit=crop&q=80", "alt_text": "Freshly proofed bread loaves on trays"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 20.0, "price_unit": "per_day", "currency": "EUR", "deposit": 60.0, "delivery_available": True, "pickup_only": False, "notes": "Plug-in, 220V standard outlet. I'll set the temperature and humidity for your recipe. Weekly rate: EUR 80."},
        ],
        "latitude": 38.018,
        "longitude": 12.540,
    },
    # Antonio - Mechanic
    {
        "owner_slug": "antonios-garage",
        "name": "Engine Hoist (2-Ton Hydraulic)",
        "slug": "engine-hoist-2-ton-hydraulic",
        "description": "2-ton hydraulic engine hoist with load leveler. Foldable legs for storage. Boom extends to 4 positions. The only way to safely pull an engine. Includes chains and hooks.",
        "content_language": "en",
        "item_type": "physical",
        "category": "tools",
        "subcategory": "automotive",
        "condition": "good",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1530046339160-ce3e530c7d2f?w=800&h=600&fit=crop&q=80", "alt_text": "Engine hoist lifting engine from car"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1619642751034-765dfdf7c58e?w=800&h=600&fit=crop&q=80", "alt_text": "2-ton hydraulic hoist with chains"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 20.0, "price_unit": "per_day", "currency": "EUR", "deposit": 50.0, "delivery_available": True, "pickup_only": False, "notes": "Folds flat for transport. I'll deliver with my van if you can't fit it. Check the hydraulic ram -- if it drifts, stop and call me."},
        ],
        "latitude": 38.026,
        "longitude": 12.543,
        "story": "Every shade-tree mechanic needs one of these eventually. Buying one for a single engine swap makes no sense. Rent mine."
    },
    {
        "owner_slug": "antonios-garage",
        "name": "OBD2 Diagnostic Scanner (Autel MaxiCOM)",
        "slug": "obd2-diagnostic-scanner-autel-maxicom",
        "description": "Autel MaxiCOM MK808 professional diagnostic scanner. Full system scan, ABS, SRS, transmission, live data, oil reset, EPB, BMS. Supports all European, Japanese, and American makes 1996+.",
        "content_language": "en",
        "item_type": "physical",
        "category": "tools",
        "subcategory": "automotive",
        "condition": "excellent",
        "brand": "Autel",
        "model": "MaxiCOM MK808",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1619642751034-765dfdf7c58e?w=800&h=600&fit=crop&q=80", "alt_text": "OBD2 diagnostic scanner connected to car"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1530046339160-ce3e530c7d2f?w=800&h=600&fit=crop&q=80", "alt_text": "Autel scanner showing diagnostic screen"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?w=800&h=600&fit=crop&q=80", "alt_text": "Scanner reading engine codes under hood"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 15.0, "price_unit": "per_day", "currency": "EUR", "deposit": 40.0, "pickup_only": True, "notes": "Fully updated software. I'll show you how to connect and read codes. Takes 2 minutes to learn."},
            {"listing_type": "service", "price": 25.0, "price_unit": "per_visit", "currency": "EUR", "notes": "I come to you, scan your car, read all codes, and explain what's wrong. Printout included."},
        ],
        "latitude": 38.026,
        "longitude": 12.543,
    },
    # Giulia - Interior Designer
    {
        "owner_slug": "giulias-design",
        "name": "Bosch Laser Level Kit (GLL 3-80 CG)",
        "slug": "bosch-laser-level-kit-gll-3-80-cg",
        "description": "Bosch GLL 3-80 CG green laser level with tripod and target plate. 360-degree coverage on 3 planes. Self-leveling. Visible in daylight. The gold standard for hanging cabinets, tiling, and framing.",
        "content_language": "en",
        "item_type": "physical",
        "category": "tools",
        "subcategory": "measurement",
        "condition": "excellent",
        "brand": "Bosch",
        "model": "GLL 3-80 CG",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=800&h=600&fit=crop&q=80", "alt_text": "Bosch laser level projecting green lines"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1504148455328-c376907d081c?w=800&h=600&fit=crop&q=80", "alt_text": "Laser level setup for cabinet installation"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 10.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0, "pickup_only": True, "notes": "Comes with 2 batteries (4-hour life each). Green laser visible outdoors. Self-leveling -- just set it down and it finds level."},
        ],
        "latitude": 38.022,
        "longitude": 12.537,
    },
    {
        "owner_slug": "giulias-design",
        "name": "Wallpaper Steamer & Tool Kit",
        "slug": "wallpaper-steamer-tool-kit",
        "description": "2400W wallpaper steamer with 3.5m hose and large plate. Plus scoring tool, scraper set, smoothing brush, and seam roller. Everything to strip old wallpaper and hang new. Strips a room in 2 hours.",
        "content_language": "en",
        "item_type": "physical",
        "category": "tools",
        "subcategory": "decorating",
        "condition": "good",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1589939705384-5185137a7f0f?w=800&h=600&fit=crop&q=80", "alt_text": "Wallpaper steamer in use on wall"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1562259929-b4e1fd3aef09?w=800&h=600&fit=crop&q=80", "alt_text": "Wallpaper removal tools laid out"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?w=800&h=600&fit=crop&q=80", "alt_text": "Room with freshly hung wallpaper"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 12.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0, "delivery_available": True, "pickup_only": False, "notes": "Score the wallpaper first, then steam. Old paste slides right off. I'll explain the technique at pickup."},
        ],
        "latitude": 38.022,
        "longitude": 12.537,
    },
    # Tommaso - Olive Farmer
    {
        "owner_slug": "tommasos-farm",
        "name": "Traditional Olive Press (Manual)",
        "slug": "traditional-olive-press-manual",
        "description": "Hand-operated olive press, traditional Sicilian design. Granite millstone, wooden frame, steel screw. Produces 2-3 liters of oil per batch. For small batches and educational demonstrations.",
        "content_language": "en",
        "item_type": "physical",
        "category": "farming",
        "subcategory": "processing",
        "condition": "fair",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=800&h=600&fit=crop&q=80", "alt_text": "Traditional olive press with granite millstone"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1504185945330-7a3ca1380535?w=800&h=600&fit=crop&q=80", "alt_text": "Olive oil dripping from press into bowl"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800&h=600&fit=crop&q=80", "alt_text": "Fresh pressed olive oil in glass bottle"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 30.0, "price_unit": "per_day", "currency": "EUR", "deposit": 50.0, "pickup_only": True, "notes": "Heavy (80kg). Bring a van and two strong people. Perfect for agritourism demos and school groups."},
            {"listing_type": "training", "price": 20.0, "price_unit": "per_session", "currency": "EUR", "notes": "I show you the whole process: harvest, sort, crush, press, filter. 3-hour session at my farm. You take home a bottle of fresh oil."},
        ],
        "latitude": 38.035,
        "longitude": 12.580,
        "story": "This press belonged to my great-grandfather. It made oil for the family for 80 years. Now it's mostly ceremonial -- we use a modern centrifuge for production. But nothing tastes like stone-pressed oil."
    },
    {
        "owner_slug": "tommasos-farm",
        "name": "Olive Harvesting Net Set (100sqm)",
        "slug": "olive-harvesting-net-set-100sqm",
        "description": "5 heavy-duty olive harvesting nets, 20sqm each (100sqm total). UV-resistant, reinforced edges, tie-down loops. Plus 3 hand rakes and 2 crate stackers. Covers 15-20 mature olive trees.",
        "content_language": "en",
        "item_type": "physical",
        "category": "farming",
        "subcategory": "harvest",
        "condition": "good",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=800&h=600&fit=crop&q=80", "alt_text": "Olive harvesting nets spread under trees"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1504185945330-7a3ca1380535?w=800&h=600&fit=crop&q=80", "alt_text": "Olive harvest in progress with nets and crates"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 15.0, "price_unit": "per_day", "currency": "EUR", "deposit": 30.0, "delivery_available": True, "pickup_only": False, "notes": "Available October through January (harvest season). Shake the branches, olives fall on nets. Simple. Weekly rate: EUR 50."},
        ],
        "latitude": 38.035,
        "longitude": 12.580,
    },
    # Alessia - Music Teacher
    {
        "owner_slug": "alessias-music",
        "name": "Yamaha P-125 Digital Piano (88 keys)",
        "slug": "yamaha-p125-digital-piano-88-keys",
        "description": "Yamaha P-125 weighted-key digital piano. 88 keys with graded hammer action. Built-in speakers, headphone jack for silent practice. Includes stand, bench, pedal, and music rest.",
        "content_language": "en",
        "item_type": "physical",
        "category": "music",
        "subcategory": "keyboards",
        "condition": "excellent",
        "brand": "Yamaha",
        "model": "P-125",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1520523839897-bd0b52f945a0?w=800&h=600&fit=crop&q=80", "alt_text": "Yamaha digital piano with bench and stand"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1507838153414-b4b713384a76?w=800&h=600&fit=crop&q=80", "alt_text": "Piano keys close-up - weighted action"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1511379938547-c1f69419868d?w=800&h=600&fit=crop&q=80", "alt_text": "Digital piano in home setting with sheet music"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 15.0, "price_unit": "per_day", "currency": "EUR", "deposit": 80.0, "delivery_available": True, "pickup_only": False, "notes": "Perfect for students not ready to buy. Monthly rental: EUR 60. I deliver and tune the stand. Lesson discount: EUR 10/day if taking lessons with me."},
            {"listing_type": "training", "price": 20.0, "price_unit": "per_hour", "currency": "EUR", "notes": "Piano lessons for beginners to intermediate. Classical, pop, jazz basics. 45-minute sessions at my studio or your home."},
        ],
        "latitude": 38.019,
        "longitude": 12.538,
        "story": "I have 3 of these because students kept asking 'Where can I practice?' Now they rent one, take it home, and practice between lessons. Everyone deserves a piano that feels real."
    },
    {
        "owner_slug": "alessias-music",
        "name": "Guitar Collection (Acoustic, Classical, Electric)",
        "slug": "guitar-collection-acoustic-classical-electric",
        "description": "3 guitars: Yamaha FG800 acoustic (steel string), Cordoba C5 classical (nylon string), Squier Stratocaster electric with Fender Champion 20 amp. Each comes with case, picks, strap, and tuner.",
        "content_language": "en",
        "item_type": "physical",
        "category": "music",
        "subcategory": "guitars",
        "condition": "good",
        "brand": "Various",
        "media": [
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1510915361894-db8b60106cb1?w=800&h=600&fit=crop&q=80", "alt_text": "Three guitars - acoustic, classical, and electric"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1525201548942-d8732f6617a0?w=800&h=600&fit=crop&q=80", "alt_text": "Acoustic guitar close-up with warm wood grain"},
            {"media_type": "photo", "url": "https://images.unsplash.com/photo-1550291652-6ea9114a47b1?w=800&h=600&fit=crop&q=80", "alt_text": "Electric guitar with amplifier setup"},
        ],
        "listings": [
            {"listing_type": "rent", "price": 8.0, "price_unit": "per_day", "currency": "EUR", "deposit": 40.0, "pickup_only": True, "notes": "Rent one or all three. Monthly rate: EUR 30/guitar. Fresh strings on every rental. Beginners welcome -- I'll show you 3 chords in 5 minutes."},
        ],
        "latitude": 38.019,
        "longitude": 12.538,
    },
]

# ── Giveaway Image Fixes ────────────────────────────────────────────
# Each item gets 3 photos so the image gallery (prev/next + thumbnails) shows up.
# Garden hose: REAL garden hose photos (old one was a plant, not a hose).
GIVEAWAY_IMAGES = {
    "garden-hose-30m-free": [
        {"media_type": "photo", "url": "https://images.unsplash.com/photo-1499892298463-01d7f9832da5?w=800&h=600&fit=crop&q=80", "alt_text": "Woman watering plants with garden hose in yard"},
        {"media_type": "photo", "url": "https://images.unsplash.com/photo-1684867430779-e66e779a19b7?w=800&h=600&fit=crop&q=80", "alt_text": "Person spraying water with garden hose"},
        {"media_type": "photo", "url": "https://images.unsplash.com/photo-1515150144380-bca9f1650ed9?w=800&h=600&fit=crop&q=80", "alt_text": "Watering garden with hose - close up"},
    ],
    "bread-maker-panasonic-free": [
        {"media_type": "photo", "url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800&h=600&fit=crop&q=80", "alt_text": "Fresh baked bread from bread maker"},
        {"media_type": "photo", "url": "https://images.unsplash.com/photo-1555932450-31a8aec2adf1?w=800&h=600&fit=crop&q=80", "alt_text": "Bread loaves fresh from oven"},
        {"media_type": "photo", "url": "https://images.unsplash.com/photo-1585190775860-a37ab092ac67?w=800&h=600&fit=crop&q=80", "alt_text": "Homemade bread on cutting board"},
    ],
    "kids-bicycle-16-inch-free": [
        {"media_type": "photo", "url": "https://images.unsplash.com/photo-1532298229144-0ec0c57515c7?w=800&h=600&fit=crop&q=80", "alt_text": "Kids bicycle with training wheels"},
        {"media_type": "photo", "url": "https://images.unsplash.com/photo-1583124688426-3128aec007f8?w=800&h=600&fit=crop&q=80", "alt_text": "Child's bicycle outdoors"},
        {"media_type": "photo", "url": "https://images.unsplash.com/photo-1595182747080-3b43712dd27d?w=800&h=600&fit=crop&q=80", "alt_text": "Kids bike parked on path"},
    ],
    "nanosecond-wire-teaching-aid": [
        {"media_type": "photo", "url": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&h=600&fit=crop&q=80", "alt_text": "Circuit board close-up - teaching electronics"},
        {"media_type": "photo", "url": "https://images.unsplash.com/photo-1613563696309-c2a4db7e1f36?w=800&h=600&fit=crop&q=80", "alt_text": "Science teaching materials and equipment"},
        {"media_type": "photo", "url": "https://images.unsplash.com/photo-1613563696452-c7239f5ae99c?w=800&h=600&fit=crop&q=80", "alt_text": "STEM education hands-on learning"},
    ],
}


def main():
    with open(SEED_FILE) as f:
        data = json.load(f)

    # 1. Fix giveaway items -- add missing images
    for item in data["items"]:
        if item["slug"] in GIVEAWAY_IMAGES:
            item["media"] = GIVEAWAY_IMAGES[item["slug"]]
            print(f"  Fixed: {item['slug']} -- added {len(item['media'])} image(s)")

    # 2. Add new users
    existing_slugs = {u["slug"] for u in data["users"]}
    added_users = 0
    for user in NEW_USERS:
        if user["slug"] not in existing_slugs:
            data["users"].append(user)
            added_users += 1
            print(f"  Added user: {user['display_name']} ({user['slug']})")

    # 3. Add new items
    existing_item_slugs = {i["slug"] for i in data["items"]}
    added_items = 0
    for item in NEW_ITEMS:
        if item["slug"] not in existing_item_slugs:
            data["items"].append(item)
            added_items += 1
            print(f"  Added item: {item['name']} ({item['slug']})")

    # 4. Write back
    with open(SEED_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nDone: {added_users} users, {added_items} items added. 3 giveaway images fixed.")
    print(f"Total: {len(data['users'])} users, {len(data['items'])} items")


if __name__ == "__main__":
    main()
