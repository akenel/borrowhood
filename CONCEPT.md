# BorrowHood -- Concept Document

**"Rent it. Lend it. Share it. Teach it."**

*Free as in freedom. Open source. No platform fees. Forever.*

---

## One Line

Every garage becomes a rental shop. Every neighbor becomes a supplier. Every kitchen becomes a bakery.

## The Problem

People have garages, kitchens, workshops, and gardens full of stuff they use twice a year. Their neighbors need that stuff but don't want to buy it. There's no good way to connect them -- especially across language barriers.

Craigslist is a wasteland. Facebook Marketplace is a data farm. Etsy takes 6.5%. eBay takes 13%. None of them care about your community. None of them know that you speak B1 Italian and the guy with the shovel speaks C1 English. None of them turn a tool rental into a garden job into a friendship.

## The Solution

BorrowHood is a community rental, sales, and services platform where:

1. **You list your stuff** -- tools, kitchen gear, equipment, anything
2. **You set your terms** -- rent, sell, make an offer, or "not for sale"
3. **You offer services** -- "I'll deliver it", "I'll show you how", "I'll do it for you"
4. **The platform matches people** -- by distance, language, trust, and what they need
5. **Relationships grow organically** -- rent a shovel, need a wheelbarrow, hire the gardener

## The Origin Story

My father was a hand-shovel landscaper for 60 years in Switzerland. His garage was legendary -- 500 tools, every one with a story. When he passed in 2020, those tools sat there. Every neighborhood has a garage like his. Every neighborhood has people who need what's in it. BorrowHood connects them.

Built from a camper van in Trapani, Sicily, 2026.

---

## Core Concepts

### The Workshop

Every user IS a shop. Their profile is their storefront.

| Field | Example |
|-------|---------|
| Workshop Name | "Sally's Kitchen" |
| Workshop Type | kitchen, garage, garden, workshop, studio, other |
| Tagline | "Grandma's recipes, your table" |
| Bio/Story | Free text -- the human story |
| Avatar | Profile photo |
| Banner | Workshop banner image |
| Location | Lat/lng, city, country |
| Delivery Radius | 0 = pickup only, or km radius |
| Will Ship | true/false (Zalando-style send & return) |
| Availability | weekends, anytime, by appointment |
| Contact Method | in-app, phone, email |

#### Social Links (The Pro's Portfolio)

The furniture builder who already has YouTube, Instagram, a website -- he doesn't recreate that inside BorrowHood. He links to it. We leverage existing credibility instead of building a walled garden.

| Field | Example |
|-------|---------|
| Website | `https://marcos-furniture.it` |
| YouTube | `https://youtube.com/@marcobuilds` |
| Instagram | `https://instagram.com/marcobuilds` |
| LinkedIn | `https://linkedin.com/in/marco-rossi` |
| Etsy | `https://etsy.com/shop/marcobuilds` |
| Other Links | Any URL + label (TikTok, portfolio, blog, etc.) |

These show as icons on the workshop page. Instant credibility. The platform plays nice with the existing ecosystem.

#### Workshop Services

Each workshop owner declares what they offer:

| Service | Description |
|---------|-------------|
| **Rents Items** | "Borrow my stuff" |
| **Sells Items** | "Buy my stuff" |
| **Offers Training** | "I'll show you how to use it" |
| **Offers Service** | "I'll do it for you" |
| **Ships Items** | "I'll mail it, you return it" |

### Language Proficiency (CEFR Standard)

**This is the differentiator. Nobody else does this.**

Each user declares the languages they speak and their level:

| Level | Meaning | Icon |
|-------|---------|------|
| A1 | "I know 5 words + hand gestures" | 1 dot |
| A2 | "I can order coffee and ask for directions" | 2 dots |
| B1 | "I can have a real conversation, slowly" | 3 dots |
| B2 | "I'm comfortable, might miss jokes" | 4 dots |
| C1 | "Fluent, can discuss cookie recipes in detail" | 5 dots |
| C2 | "Native or mastery" | Full bar |

**Why it matters:**

- The expat in Trapani who speaks A1 Italian finds the garage owner who speaks C1 English
- 10 people list the same cookie cutter, but only one speaks your language fluently
- Browse and search filter by "speaks at least B1 English"
- Language badges show on every listing and workshop

### Listing Types (Expanded)

Not everything is a shovel. The platform handles five distinct listing types:

| Type | Example | Delivery |
|------|---------|----------|
| **Physical item** (rent or sell) | Shovel, cookie cutter, drill | Pickup / deliver / ship & return |
| **Physical item made to order** | Custom furniture, tailored clothing | Commission -- "I build these, order one" |
| **Digital goods** | PDF recipe, blueprint, pattern, 3D model file, template | Instant download (Minio) |
| **Experience or service** | Garden work, baking lesson, city tour, 3D printing | In person or video call |
| **Space** | Room, workshop bench, parking spot, garden plot | Time-based access |

Sally's cookie cutter is physical. Her recipe PDF is digital. Her "I'll bake you a dozen cookies" is a service. Her kitchen counter for a baking workshop is a space. All four live in her workshop, all four are listable.

For v1, digital items are simple: owner uploads a file, buyer/renter gets a download link. No DRM, no complexity. Trust-based, like the rest of the platform.

### The Collaboration Layer -- Makers + Creators

**The 3D printer scenario:**

Jake has a 3D printer in his garage. He lists it as equipment for rent AND as a printing service. Luna is a 19-year-old art student with zero equipment but she designs steampunk flying submarines in 2D -- incredible detailed work. She lists her designs as digital goods (STL files, concept art).

```
Jake's Garage                    Luna's Studio
├── 3D Printer (rent)            ├── Steampunk Submarine STL (digital)
├── 3D Printing Service          ├── Flying Machine Blueprint (digital)
├── Filament (sell)              ├── Custom Design Service
└── "I'll print your design"    └── "I'll design anything steampunk"
```

They find each other on BorrowHood. Jake prints Luna's submarines. Luna designs custom pieces for Jake's clients. Neither could do it alone. Together they're a business.

**This is the unlock:** BorrowHood doesn't just match people with things. It matches **skills with equipment**. The kid with the vision finds the neighbor with the machine. The designer finds the maker. The recipe finds the kitchen.

**How it surfaces:**

- Luna's STL file listing says "Needs: 3D printer (FDM, PLA filament)"
- Jake's printer listing says "Compatible with: STL, OBJ files"
- The platform shows: "3 makers near you can print this design"
- Or: "12 designers have files ready for your printer"

**v1:** Simple tags on listings ("needs_equipment", "compatible_with"). Manual discovery via search.
**v2:** Smart matching -- "People who have X often need Y. You have Y."

### The 6 Transaction Types

| Type | Example | How Money Works (v2) |
|------|---------|---------------------|
| **Rent** | "Borrow my shovel, EUR 5/week" | Rental fee + deposit |
| **Sell** | "Buy my shovel, EUR 25" | One-time sale |
| **Commission** | "I'll build you a table like this one" | Custom order fee |
| **Offer** | "Make me an offer on this" | Negotiation |
| **Ship & Return** | Sally mails cookie cutter to California | Rental + shipping |
| **Service** | "I'll come dig your garden" / "I'll print your design" | Service fee |

### The Service Layer

This is what turns a rental platform into a community:

```
Level 1: Rent the tool
Level 2: Deliver the tool + show them how to use it
Level 3: Just do the job for them
Level 4: Train them so they can do it themselves
Level 5: Collaborate -- your skill + my equipment = our product
```

**Shovel guy:** rents tools -> delivers -> teaches -> gets hired for garden work
**Cookie lady:** rents cutter -> ships it -> sells cookies -> teaches baking
**Tour guide:** rents his B&B -> offers city tours -> becomes local guide
**3D printer guy:** rents printer -> prints your files -> collaborates with designers
**Steampunk kid:** sells designs -> commissions prints -> builds a brand from nothing

The platform surfaces hidden talent through ownership AND hidden potential through creativity. The kid with nothing except a laptop and imagination becomes a creator. The guy with the garage full of machines becomes her manufacturing partner. Freedom for the motivated.

### Data Sovereignty -- Your Store, Your Data

**THE TRUST LAYER. The thing that makes BorrowHood different from every platform that holds your data hostage.**

#### The Problem

Every platform that ever existed -- eBay, Etsy, Airbnb, Facebook Marketplace -- holds your data hostage. You spend years building your store, your reviews, your listings, your story. Then they change the rules, raise the fees, or get acquired. You lose everything.

BorrowHood does not do that.

#### The Principle

**You own your data. Always. We are just the hosting layer.**

#### One-Click Export

Every user can export their entire store at any time. No questions asked. No waiting. No fees.

**What gets exported:**
- All listings with photos
- All descriptions and stories
- All reviews and ratings received
- All transaction history
- All comments and Q&A threads
- Profile and social links
- Digital goods (PDFs, STL files, etc.)

**Export format:**
```
SallysKitchen-export-2026-03-01/
├── index.html               <- Full store as a browsable webpage
├── profile.json             <- Machine-readable profile data
├── listings/
│   ├── cookie-cutter-set/
│   │   ├── listing.html     <- Standalone webpage for this item
│   │   ├── listing.json     <- Machine-readable data
│   │   ├── reviews.html     <- All reviews for this item
│   │   └── images/
│   │       ├── front.jpg
│   │       ├── side.jpg
│   │       └── detail.jpg
│   ├── recipe-pdf/
│   │   ├── listing.html
│   │   └── files/
│   │       └── grandmas-cookies.pdf
│   └── ...
└── reviews/
    └── all-reviews.html     <- Every review, importable
```

**Result:** The user has a complete static website of their entire BorrowHood store. Zip it, upload it to Netlify/Wix/WordPress/any host, point a domain at it. Live independently. The data is theirs and it's already formatted.

#### The Graduation Path

BorrowHood is not trying to trap anyone. We are the launchpad.

```
Stage 1: Start on BorrowHood. Zero cost. Build your store. Get your first transactions.
Stage 2: Export your store anytime. Back it up. Sleep well.
Stage 3: When you are ready, graduate to your own website. We help you do it.
```

We keep the transaction layer. They keep their content. Everyone wins.

#### Why This Is Smart

- Users trust us MORE because we don't hide the exit door
- Word of mouth explodes because people feel safe
- The graduation path means successful users become our best advertising
- "I started on BorrowHood, now I have my own site" -- that's a success story, not a loss

#### Hosting Reality for v1

8 seed users. 30 items. Runs on existing Hetzner alongside HelixNet. Negligible cost. Maybe EUR 5/month extra in Minio storage. Videos stay on YouTube. Photos in Minio. Everything else in Postgres. Export pulls it all together on demand.

### The Relationship Flywheel

```
Rent a shovel
  -> Need a wheelbarrow next week
    -> "Actually, can you just do my garden?"
      -> Casual rental becomes real work
        -> Real income from stuff collecting dust
```

### Teams -- Workshop Crews

**The grandmother scenario:** Nonna Rosa is 83, wheelchair-bound, makes the best cannoli in Trapani. She has zero computer skills. Her grandson Marco lives in California. Marco manages her BorrowHood workshop -- he creates her listings, uploads her photos, handles requests. Nonna does what she does best: make cannoli.

**The neighbor scenario:** John has a pickup truck. Dave has every tool known to man. Neither can do the full job alone. Together they're a mobile workshop. One workshop, two people, shared reputation.

**The family business:** Husband builds custom furniture. Wife handles all the customers, scheduling, photos. One workshop, two roles, one reputation.

#### How Teams Work

A Workshop can have multiple members, each with a role:

| Role | Can Do | Example |
|------|--------|---------|
| **Owner** | Everything. Final say. Their stuff. | Nonna Rosa |
| **Manager** | Edit listings, handle requests, respond to messages, manage calendar | Grandson Marco |
| **Helper** | Assigned to deliveries, pickups, specific tasks. Gets notification when needed. | John (has the truck) |
| **Contributor** | Add items to the shared workshop. Can't edit others' items. | Dave (adds his tools to the team workshop) |

#### Team Scenarios in Seed Data

| Team | Members | How It Works |
|------|---------|-------------|
| **Nonna Rosa's Kitchen** | Rosa (Owner, Trapani), Marco (Manager, California) | Marco manages everything remotely via Telegram. Rosa bakes. |
| **Dave & John Heavy Lifting** | Dave (Owner, tools), John (Helper, truck) | Items listed under Dave's workshop. John tagged as delivery partner. |
| **Cassisa Family Campers** | Sebastino (Owner), Nino (Manager) | Father owns the business, son runs the tech side. Sound familiar? |

#### Team Rules

- Every workshop has exactly ONE owner
- Owner can invite members via email or Telegram username
- Members can belong to MULTIPLE teams (John helps Dave AND helps Mike)
- Reputation is per-workshop AND per-person (John's delivery rating follows him across teams)
- Revenue/points split defined by the team (Owner sets percentages)
- Team activity log shows who did what (transparency)

#### Data Model Addition

```
WorkshopMember
├── id
├── workshop_id (FK to User -- the workshop owner)
├── member_user_id (FK to User -- the team member)
├── role ("owner" | "manager" | "helper" | "contributor")
├── invited_by, invited_at, accepted_at
├── points_split_percentage (default: 0 -- owner gets all)
├── status ("invited" | "active" | "inactive")
└── permissions (JSON -- granular overrides if needed)
```

### Transport & Location

Every user has lat/long. The platform knows:

- **Distance** between renter and owner ("this shovel is 2.3km away")
- **Delivery options** ("I'll deliver within 5km" or "pickup only")
- **Repeat patterns** ("Larry rented shovel last week, now wants wheelbarrow")
- **Route awareness** (v2: multi-stop delivery planning)

### Skills Profile

**The insight: Anyone can buy a shovel. What you can't buy is forty years of knowing how to use one. The tool is the entry point. The skill is the product.**

Every user lists their skills SEPARATELY from their items. Not just what they own. What they KNOW.

**Examples:**
- Baking (specialty: Sicilian pastry)
- Carpentry (specialty: furniture joinery)
- Language teaching (Italian native, teaches English)
- Programming (web development)
- Gardening (permaculture, soil prep)
- Cooking (Moroccan cuisine)
- Plumbing (basic household repairs)
- 3D Printing (FDM, resin, post-processing)

**Each skill has:**

| Field | Description |
|-------|-------------|
| Skill name | "Carpentry" |
| Specialty | "Furniture joinery, live-edge tables" |
| Self-declared level | Beginner / Intermediate / Expert |
| Community-verified level | Earned through reputation (see below) |
| Completed transactions | How many deals done using this skill |
| Skill-specific reviews | Reviews that rate THIS skill specifically |
| Years of experience | Self-declared |

**The skill teaching angle:**

This opens a whole new transaction type. Not just "rent my item." Not just "buy my item." **Learn from me.**

Telegram video call. Screen share. Walk them through it. One hour session. Set a price or do it for free and collect reputation points.

**Language teaching via Telegram** is the obvious killer use case for the expat community. The Italian who wants to learn English. The Canadian who needs survival Italian. They find each other on BorrowHood. Language match shows compatibility. They do the lesson on Telegram. Both rate each other. Both build reputation.

That's not an app. That's a neighborhood.

### Trust, Reputation & Gamification

**Reputation is EARNED, not claimed.**

#### The Badge System

You can say you're an expert programmer on day one. The badge says "self-declared." After real transactions with real reviews, the community verifies you.

| Badge | Points | Meaning |
|-------|--------|---------|
| **Newcomer** | 0-50 | Self-declared only. Just getting started. |
| **Contributor** | 50-200 | Community starting to verify. Some transactions completed. |
| **Trusted** | 200-500 | Solid reputation. Consistent quality. People rely on you. |
| **Expert** | 500+ | The real ones. Years of proof. Community-verified skills. |
| **Legend** | 1000+ | Sally with 100 cookie cutter rentals and 30 people taught. The OGs. |

#### Points System

| Action | Points | Why |
|--------|--------|-----|
| Complete a rental transaction | +10 | Basic community participation |
| Complete a skill/service transaction | +20 | Higher value, more effort |
| Receive a 5-star review | +15 | Quality signal |
| Receive a review from a Trusted+ member | +30 | Weighted -- experienced reviewers count more |
| First transaction bonus | +25 | Encourages new users to start |
| Cross-language deal completed | +20 | Language bridge bonus -- connects communities |
| Mentor a new user | +15 | Builds the community knowledge chain |
| Export your store (data sovereignty) | +10 | Rewarding people for using the freedom features |

#### Review Weighting -- The Fake Review Killer

**Not all reviews are equal.** This is the smart part.

| Reviewer Badge | Weight per star |
|---------------|----------------|
| Newcomer | 1x |
| Contributor | 2x |
| Trusted | 3x |
| Expert | 5x |
| Legend | 10x |

A 5-star review from a Newcomer = 5 points toward your trust score.
A 5-star review from a Legend = 50 points toward your trust score.

**This kills fake reviews naturally.** Your friends who just joined can't inflate your score meaningfully. Real reputation from real community members is what moves the needle. No algorithm needed. No AI fraud detection. Just math.

#### Skill Verification Path

```
Day 1:   "I'm an expert carpenter"        -> Badge: Self-Declared
5 txns:  4.2 avg rating in carpentry       -> Badge: Community Verified
20 txns: 4.5 avg from Trusted+ reviewers   -> Badge: Trusted Expert
50 txns: Consistent excellence             -> Badge: Legend
```

#### Bidirectional Reviews

Both renter AND owner get rated after every transaction:

- Star rating (1-5)
- Text review (language-tagged)
- Skill-specific rating (if applicable -- "How was their carpentry?")
- Response time rating
- Item condition accuracy ("Was the item as described?")

### i18n -- The Language Engine (Baked In Deep)

Language is not a feature. It's the foundation. BorrowHood is built for a world where people don't all speak the same language but still need each other's stuff.

**Three layers of language:**

#### Layer 1: UI Language (v1)

The platform interface itself -- buttons, labels, menus, navigation.

- English (en) and Italian (it) for v1
- Switches based on user preference
- Translation files: `/locales/en.json`, `/locales/it.json`
- Same MutationObserver pattern proven on ISOTTO and Camper

#### Layer 2: Content Language Tagging (v1)

Every piece of user-generated content is tagged with its language:

```
Item description  -> language_code: "it"
Review            -> language_code: "en"
Comment           -> language_code: "it"
Video link        -> language_code: "it" (demo is in Italian)
```

This is the foundation. We tag EVERYTHING from day one. Even if we don't translate yet, the data is structured for it.

**Translate button (v1):** On comments and reviews, a small translate button. One tap. Translates into the user's preferred language.

v1 options (pick one):
- **LibreTranslate** (self-hosted, free, open source) -- fits the Foo Fighter philosophy
- **DeepL API** (cheap, excellent quality) -- backup if LibreTranslate quality isn't good enough
- **Browser built-in translation** -- zero-cost fallback

Translation is done on DISPLAY, not on storage. The original text is sacred. We never overwrite it.

#### Layer 3: Full Translation Engine (v2/v3)

```
ContentTranslation (table exists from v1 -- empty, ready)
├── content_type     "item_description" | "review" | "comment"
├── content_id       FK to the source record
├── source_language  "it"
├── target_language  "en"
├── translated_text  "This cookie cutter was my grandmother's..."
├── translated_by    "browser" | "api" | "user" | "ai"
└── created_at
```

v2: Server-side translation with caching (translate once, serve forever)
v3: 65+ languages based on Keycloak's supported locales, AI-powered context-aware translation

**The principle:** Item descriptions stay in the owner's native language -- that's authentic. But anyone can hit translate. The system never auto-translates stories without asking. Your grandmother's recipe description in Italian is YOUR voice. We respect that.

### Media Strategy -- Photos Local, Videos Linked, Digital Downloads

**Rule: Do NOT store videos on Minio.** Too heavy, too expensive, too complex.

YouTube embed only for v1. User uploads to their own YouTube, pastes the link, we embed it. Clean, simple, free, already indexed by Google. Minio stays lean -- photos and small digital files only.

| Media | Storage | Why |
|-------|---------|-----|
| Photos | Minio (we own them) | Small, critical for listings, need control |
| Videos | YouTube embed link ONLY | They host, we embed, zero storage cost, Google indexes it |
| Digital goods | Minio (downloadable) | PDFs, STL files, recipes, blueprints -- small files |

**ItemMedia model:**
```
id, item_id
media_type    "photo" | "video_embed" | "digital_download"
url           Minio URL for photos/files, YouTube URL for video embeds
sort_order, caption
language_code  (for videos -- "this demo is in Italian")
file_size     (for digital downloads -- display to user)
```

Even video language is tagged. Browser shows: "3 photos, 1 video (Italian), 1 video (English)."

---

## Data Model

### User
```
id, email, name, avatar
workshop_name, workshop_type, tagline, bio, banner
lat, lng, city, country
delivery_radius_km, will_ship
availability
telegram_username (REQUIRED -- primary communication channel)
website_url, youtube_url, instagram_url, linkedin_url, etsy_url
rents_items, sells_items, offers_training, offers_service, ships_items, commissions
member_since, verified, trust_score
language_preference (UI language: "en" | "it")
```

### UserSkill
```
id, user_id
skill_name ("carpentry" | "baking" | "programming" | "language_teaching" | ...)
specialty ("furniture joinery" | "Sicilian pastry" | ...)
self_declared_level ("beginner" | "intermediate" | "expert")
community_verified_level (null | "verified" | "trusted_expert" | "legend")
years_experience
completed_transactions (count, auto-calculated)
avg_rating (auto-calculated from skill-specific reviews)
description (free text -- "I've been building furniture for 30 years...")
```

### UserPoints
```
id, user_id
action ("rental_complete" | "service_complete" | "review_received" | "first_txn" | "cross_language" | "mentor" | "export")
points (10 | 20 | 15 | 30 | 25 | 15 | 10)
reference_id (FK to rental, review, etc.)
created_at
```
Total points = SUM of all UserPoints for that user. Badge derived from total.

### UserSocialLink (for additional/custom links)
```
user_id, platform ("tiktok" | "portfolio" | "blog" | "other")
url, label
sort_order
```

### UserLanguage
```
user_id, language_code ("en", "it", "de", "fr", ...)
level ("A1" | "A2" | "B1" | "B2" | "C1" | "C2")
note ("Swiss German dialect", "Learning!", ...)
```

### Item
```
id, owner_id
title, description, story, condition
description_language ("en" | "it" | ...)
item_type ("physical" | "physical_made_to_order" | "digital" | "service" | "space")
category (tools, kitchen, garden, electronics, sports, home, craft, 3d_printing, art, music, other)
needs_equipment (null | "3D printer" | "oven" | "sewing machine" -- what's needed to use this)
compatible_with (null | "STL, OBJ" | "any filament" -- what this equipment works with)
status (active, rented, sold, inactive)
created_at, updated_at
```

### ItemMedia (replaces ItemPhoto -- handles photos, videos, digital files)
```
id, item_id
media_type ("photo" | "video_embed" | "digital_download")
url (Minio for photos/files, YouTube/IG for video embeds)
sort_order, caption
language_code (for videos -- "this demo is in Italian")
```

### Listing (terms per item)
```
item_id
rent_price, rent_period (day | week | month)
deposit_amount
sell_price (null = not for sale)
min_offer (null = no offers)
commission_available, commission_price, commission_description ("I'll build one for you")
training_available, training_price
service_available, service_price, service_description
shipping_available
currency_display ("EUR" | "USD" | "CHF" -- display only, no processing)
```

### Rental
```
id, item_id, renter_id, owner_id
start_date, due_date, returned_date
status (requested, approved, active, returned, overdue, disputed)
deposit_status (held, returned, claimed)
notes
```

### Offer
```
id, item_id, bidder_id
amount, message
status (pending, accepted, declined, withdrawn)
created_at
```

### Review
```
id, rental_id
reviewer_id, reviewee_id
rating (1-5), text
language_code ("en" | "it" | ...)
direction (renter_reviews_owner | owner_reviews_renter)
skill_id (null | FK to UserSkill -- rates a specific skill)
skill_rating (null | 1-5 -- "How was their carpentry?")
item_accuracy (null | 1-5 -- "Was the item as described?")
response_time_rating (null | 1-5)
reviewer_badge_at_time ("newcomer" | "contributor" | "trusted" | "expert" | "legend")
weighted_score (auto-calculated: rating * badge_weight)
created_at
```

### Message
```
id, sender_id, recipient_id
rental_id (optional -- links to context)
text, language_code
read_at, created_at
```

### Export (tracks user data exports)
```
id, user_id
format ("html_site" | "json" | "full_archive")
status ("queued" | "processing" | "ready" | "downloaded")
file_url (Minio -- the zip file)
file_size, item_count
created_at, expires_at
```

### ContentTranslation (table exists from v1 -- empty, ready for v2)
```
id
content_type ("item_description" | "item_story" | "review" | "comment" | "message")
content_id (FK to source record)
source_language ("it")
target_language ("en")
translated_text
translated_by ("browser" | "api" | "user" | "ai")
created_at
```

---

## Page Design

### 1. Landing Page
- Map (Leaflet + OpenStreetMap) showing nearby workshops
- Search bar: "What do you need?"
- Filters: distance, language, category
- Nearby workshops grid (name, rating, languages, item count)
- Recently listed items

### 2. Workshop Page
- Owner photo, name, tagline, bio
- Badge level (Newcomer/Contributor/Trusted/Expert/Legend) + points
- Location + distance from viewer
- Language badges (CEFR levels)
- Skills list with verification badges ("Carpentry: Expert, Community Verified, 47 txns")
- Social links (Telegram, YouTube, Instagram, website, etc.)
- Services offered (rent, sell, train, service, ship, commission)
- All items grid
- Reviews (with reviewer badge weights visible)

### 3. Item Detail Page
- Photo gallery (multiple angles)
- Title, story, condition
- Pricing card (rent/sell/offer/training/service/shipping options)
- Owner info + language badges + distance
- Request buttons
- Reviews for this item
- "Also from this workshop" cross-sell

### 4. Dashboard
- Stats bar (my items, rented out, renting, pending requests)
- Active rentals out (who has what, return dates, distance)
- Items I'm renting (what I have, return dates)
- Incoming requests (with requester language info)
- Trust score summary

### 5. Workshop Settings
- Edit profile, bio, tagline, avatar, banner
- Location (map picker or manual lat/lng)
- Languages (add/edit/remove with CEFR levels)
- Skills (add/edit/remove with self-declared level + specialty)
- Social links (Telegram username required, others optional)
- Services toggles
- Availability and contact preferences

### 6. Export My Store
- Big "Export My Store" button (not buried three menus deep)
- Preview of what's included (item count, photo count, reviews)
- Format choice: browsable website (HTML) or machine-readable (JSON) or both
- Download link when ready
- "Your data. Your rules. Always."

### 7. Browse / Search
- Map view + list view toggle
- Text search across items and workshops
- Filters: category, distance, language (min level), workshop type, availability
- Sort: distance, rating, newest, most rented

---

## Communication Philosophy

**We do not build a chat system. We are not a chat company.** We connect people and then get out of the way. Let the best tools do the communication job.

### What We DO NOT Build

| Feature | Who Handles It | Why |
|---------|---------------|-----|
| Chat / messaging | Telegram | Free, open, works everywhere, video calls built in |
| Video calling | Telegram | Screen sharing too -- show how the cookie cutter works |
| Video hosting | YouTube | They host, we embed, Google indexes it |
| Maps | Google Maps | Embed for pickup location (neighborhood level, not exact address) |
| Calendar | Google Calendar | Rental scheduling, pickup appointments |
| File sync | Google Drive | Data export destination (the sovereignty feature) |

### What We DO Build

The platform. The listings. The matching. The trust layer. The language engine. The export. Everything else, we delegate to tools that already exist and already work.

### Communication Stack -- No Compromises

**Telegram -- Primary communication layer:**
- Every user links their Telegram username on their profile
- One tap to open a Telegram chat with the seller
- Telegram bot for notifications (item rented, offer received, pickup reminder)
- Video calls built in -- no extra tools needed
- Screen sharing -- good enough for remote demos
- **No WhatsApp. Ever. Full stop.**
- **No Zoom. No Teams. No Slack.**

**Google -- Supporting infrastructure:**
- Google Maps embed for pickup location
- Google Calendar integration for rental scheduling
- YouTube for video embeds on listings
- Google OAuth as one login option (alongside email/password via Keycloak)
- Google Drive as export destination option
- **No Apple Drive. No iCloud. Google only for cloud storage layer.**

### Notifications via Telegram Bot

All push notifications go through Telegram. Zero cost.

| Event | Notification |
|-------|-------------|
| Rental request received | "Someone wants to rent your shovel!" |
| Offer made on your item | "New offer: EUR 20 for your cookie cutter" |
| Rental approved | "Your request was approved! Pickup details inside." |
| Pickup reminder | "Reminder: Pick up the shovel from Mike tomorrow at 2pm" |
| Return reminder | "The drill is due back to Mike tomorrow" |
| Item returned | "Sally confirmed the cookie cutter was returned in good condition" |
| New review | "You got a 5-star review from Larry!" |
| Export ready | "Your store export is ready to download" |

### Calendar & Scheduling

- Google Calendar integration for rental periods
- Seller sets availability on their listing
- Renter picks dates from available slots
- Confirmation goes to both via Telegram
- Calendar invite sent to both Google accounts

### Pickup Coordination

- Google Maps link in every listing showing neighborhood zone
- **Exact address only revealed AFTER rental is confirmed** (privacy)
- Seller sets delivery radius ("I'll bring it within 5km")
- Distance shown on every listing

## Tech Stack

### Already Running (zero setup)

| Component | Technology | Status |
|-----------|-----------|--------|
| Backend | FastAPI + SQLAlchemy | Running on Hetzner |
| Database | PostgreSQL | Running on Hetzner |
| Auth | Keycloak (OIDC, JWT RS256) | Running on Hetzner |
| File Storage | Minio | Running on Hetzner |
| Reverse Proxy | Traefik (local) / Caddy (Hetzner) | Running |
| Email (dev) | MailHog | Running on Hetzner |
| Containers | Docker + Docker Compose | Running on Hetzner |

### New (to add)

| Component | Technology | Effort |
|-----------|-----------|--------|
| Frontend | Jinja2 + Tailwind CSS (CDN) + Alpine.js (CDN) | Same stack as ISOTTO/Camper |
| Maps | Google Maps embed (or Leaflet + OSM as fallback) | 2 hours |
| i18n | JSON locale files + Alpine.js reactivity | Same pattern as ISOTTO |
| Translation | LibreTranslate (self-hosted container) | 1 command to add |
| Telegram Bot | Telegram Bot API (python-telegram-bot) | 1 afternoon |
| Google OAuth | Keycloak social login provider | 1 afternoon |
| Google Calendar | Google Calendar API | 1 day |

**Total new infrastructure for MVP: 2-3 days.**

---

## Versioning Roadmap -- v1 through v5

Each version has a clear theme, clear deliverables, and clear boundaries.
No scope creep between versions. Ship it, then grow it.

---

### v1 -- THE DEMO (DEV Weekend Challenge, Feb 27 - Mar 2, 2026)

**Theme: Prove the concept. One clean loop.**

**The loop that wins:** User registers -> sets up workshop -> lists an item with photo -> another user browses the map -> finds it -> taps Telegram link -> contacts the seller. That's the demo.

**Must have:**

| Feature | Detail | Effort |
|---------|--------|--------|
| Registration + Login | Keycloak, email confirm via MailHog, Google OAuth | Existing infra |
| Workshop Profile | Name, type, tagline, bio, avatar, location (lat/lng) | Build |
| Language Profile | CEFR levels per language, language badges | Build |
| Social Links | Telegram username (required), YouTube, Instagram, LinkedIn, website | Build |
| Skills Profile | Self-declared skills with level + specialty (baking, carpentry, etc.) | Build |
| Services Declared | Toggles: rents, sells, trains, services, ships, commissions | Build |
| Item Listing | Photos (Minio), title, description, story, condition, language tag | Build |
| Item Types | Physical, digital, service, space, made-to-order | Build |
| Listing Terms | Rent price/period, deposit, sell price, min offer, commission | Build |
| Browse + Map | Google Maps embed, search, filter by category/distance/language | Build |
| Item Detail Page | Photos, story, pricing card, owner info, language badges, distance | Build |
| Contact via Telegram | "Message on Telegram" button -> opens t.me/username | Build (trivial) |
| Dashboard | My workshop, rented out, renting, incoming requests | Build |
| Request Flow | Request -> Approve/Decline -> Active -> Return | Build |
| Teams | Owner + Manager/Helper/Contributor roles per workshop | Build |
| Onboarding Flow | 5-step guided setup for first-time users | Build |
| Community Rules | Terms of service, code of conduct, report button | Build |
| Location Privacy | 500m zone only, exact address encrypted, revealed after confirm | Build |
| Age Gate | 18+ to register, self-declared (v1), ID verification (v2) | Build |
| Report System | Report button on listings, reviews, profiles | Build |
| Help Board | Non-tech users post help requests, Verified Helpers respond | Build |
| i18n | EN/IT toggle in header, all UI text via locale files | Build (proven pattern) |
| Translate Button | On user content, browser API for v1 | Build |
| One-Click Export | Full store as HTML static site + JSON | Build |
| Data Sovereignty | Export page front and center, not buried | Build |
| Seed Data | 8 users, 30+ items, active rentals, reviews, collaborations | Build |
| README | The story, screenshots, live demo link | Write |
| ContentTranslation table | Empty, schema ready for v2 | Migration only |

**Nice to have (if Saturday goes well):**
- Bidirectional reviews (star + text + skill-specific rating)
- Points system + badge levels (Newcomer through Legend)
- Trust score calculation with review weighting
- Telegram bot notifications (at least "new rental request")
- "I Need This" board (post what you need, flip the model)

**By design -- NOT missing, INTENTIONAL:**
- No payment processing -- arrange offline via Telegram, like Craigslist
- No shipping integration -- "will ship" flag only, parties arrange via Telegram
- No auctions -- v2
- No video storage -- YouTube embed only
- No internal chat -- Telegram IS the chat
- No calendar integration -- parties coordinate via Telegram
- No LibreTranslate -- browser translate is fine for 2 languages

**Hosting:** Hetzner alongside HelixNet. EUR 0 extra. 8 users + 30 items = negligible load.

---

### v2 -- THE REAL DEAL (March - April 2026)

**Theme: Make it work for 100 real users. Add the systems they'll actually need.**

| Feature | Detail | Priority |
|---------|--------|----------|
| **Telegram Bot** | Notifications for all events (rental, offer, reminder, return, review) | High |
| **Google Calendar** | Rental scheduling, pickup appointments, availability slots | High |
| **LibreTranslate** | Self-hosted translation container. EN/IT to start, architecture supports all. | High |
| **Reviews + Skill Ratings** | Bidirectional, star + text, skill-specific, language tagged, reviewer badge weight | High |
| **Points + Badge System** | Full gamification: Newcomer -> Contributor -> Trusted -> Expert -> Legend. Points for every action. | High |
| **Review Weighting** | Legend review = 10x Newcomer review. Kills fake reviews with math, not AI. | High |
| **Skill Verification** | Self-declared -> Community Verified -> Trusted Expert -> Legend based on transaction history | High |
| **Trust Score** | Calculated from: weighted reviews, rentals completed, return rate, response time, badge level | High |
| **Payment Options** | Stripe + PayPal. User chooses per workshop. **BorrowHood takes ZERO cut.** Payment goes directly seller-to-buyer. We are infrastructure, not a middleman. | High |
| **QR Codes** | Every listed item gets a QR. Stick it on the item. Scan = listing page. The UFA model. | Medium |
| **Wishlist Board** | "I Need This" -- post what you need, nearby owners get notified | Medium |
| **Seasonal Tags** | Items tagged with seasons. December = snow blowers surface. Summer = BBQ + camping. | Medium |
| **Originator Badge** | First to list = "Original" badge. Copies flagged, not blocked. | Medium |
| **Workshop Templates** | Pre-built layouts per type (kitchen, garage, studio, garden) | Low |
| **Shipping Integration** | Rate calculator, tracking, Zalando-style ship & return | Low |
| **Service Booking** | Calendar for training sessions and service appointments | Low |

**Payment philosophy:** We NEVER take a cut. Not 1%. Not ever. Stripe/PayPal fees are between the user and the payment provider. BorrowHood is infrastructure. The moment we take a cut, we become the thing we're replacing.

**New languages:** Add based on user demand. LibreTranslate supports 30+ out of the box. Keycloak supports 60+. The i18n layer from v1 makes this a config change, not a code change.

---

### v3 -- THE COMMUNITY (Summer 2026)

**Theme: From marketplace to movement. From one neighborhood to many.**

| Feature | Detail |
|---------|--------|
| **Self-Hostable** | Any community downloads BorrowHood, runs `docker compose up`, done. Village in Nepal. Maker space in Berlin. Retirement community in Florida. |
| **Federation** | BorrowHood instances talk to each other. ActivityPub protocol. Trapani sees items in Palermo. Zurich sees Bern. Like Mastodon, but for community commerce. No central authority. |
| **Reputation Passport** | Trust score is PORTABLE. Move to a new city? Export your reputation. Import it to any BorrowHood instance. It's your maker credit score. Cryptographically signed. Can't be faked. |
| **Neighborhood Feed** | Not social media. A community bulletin board. "Mike listed a new drill." "Sally's cutter is back." "Luna and Jake completed their 10th collab." Digital grocery store pin board. |
| **Mentor System** | Experienced workshop owners mentor new ones. "Marco mentors 3 new woodworkers." Preserves institutional knowledge. The old guy who catches things passes it down. The mentorship chain, rebuilt. |
| **Smart Maker Matching** | "12 designers have files for your 3D printer." "3 workshops near you can print this STL." Skills meet equipment automatically via needs_equipment + compatible_with tags. |
| **Impact Dashboard** | "This community saved 2.3 tons of waste, EUR 15,000 in purchases, 450kg CO2." Environmental metrics. Pitch to city councils. EU green grants. Environmental funds. |
| **PWA Mobile App** | Works offline. Snap a photo, list an item without internet. Syncs when connected. |
| **Community Translations** | Volunteers translate listings. "I'll translate Sally's description into Japanese." The community helps itself. |
| **"Pay It Forward" Barter** | Instead of money, offer something in return. "I'll fix your website for a week with your drill." True barter alongside cash. Tracked as a transaction type. |
| **Route Optimization** | Multi-stop delivery. "Drop off shovel to Larry, pick up rake from Dave on the way back." |

**The key unlock:** Federation means BorrowHood can't be killed. No single server, no single company, no single point of failure. Like email -- you can't shut down email. You can't shut down BorrowHood.

---

### v4 -- THE FREEDOM LAYER (Late 2026 - 2027)

**Theme: Wipe out the middlemen. Give power back to the people.**

| Feature | Detail |
|---------|--------|
| **API-First Architecture** | Everything is an API. Telegram bots ("List via Telegram"). WordPress plugins ("Embed my shop"). Shopify bridge. The platform is the engine, anyone builds the car. |
| **Community Insurance Pool** | Micro-contribution per transaction into a community pot. Something breaks? The pot covers it. No insurance company. Transparent ledger. Everyone sees where the money goes. |
| **Skill Tree / Maker Journey** | Gamification that means something real. Milestones: "First rental", "First collaboration", "10 countries shipped to", "Workshop Veteran (100 txns)". Your skill tree IS your maker resume. Exportable. |
| **AI Concierge** | "I'm renovating my bathroom, what do I need?" AI suggests available tools in your BorrowHood, connects you with owners who've done it before. Not a chatbot. A community navigator. |
| **Cross-Federation Search** | Search every federated instance at once. "3D printer anywhere in Sicily." Results from Trapani, Palermo, Catania. Distance + language match shown. Network effect without central authority. |
| **City Partnerships** | Municipalities run BorrowHood for public tools. Library of Things, but open source and connected. City joins the federation. Public tools alongside neighborhood garages. |
| **Zero-Knowledge Payments** | Crypto where neither party's financial details touch BorrowHood servers. We facilitate, we don't hold. Tax is between you and your accountant, not between you and us. |
| **Graduation Accelerator** | Export + launch your own site = backlink "Originally on BorrowHood." Network grows even as users graduate. Every success story brings more people to the launchpad. |
| **DRM-Light for Digital Goods** | Download limits, watermarked PDFs, license keys for premium files. Protects Sally's recipe. Protects Luna's STL designs. Optional per item -- trust-based by default. |

---

### v5 -- THE ECOSYSTEM (2027+)

**Theme: BorrowHood becomes a protocol, not a platform. The infrastructure layer for community commerce worldwide.**

| Feature | Detail |
|---------|--------|
| **BorrowHood Protocol Spec** | Open specification that anyone can implement. Like HTTP for community commerce. Not our code -- our PROTOCOL. Any developer, any language, any stack can speak BorrowHood. |
| **SDK for Developers** | JavaScript, Python, Go SDKs. Build BorrowHood-compatible apps in hours. "npm install @borrowhood/sdk" |
| **Physical Pickup Points** | Partner with local businesses (cafes, libraries, convenience stores) as item exchange points. Safe, neutral, trackable. The cafe gets foot traffic. The renter gets a safe pickup spot. |
| **Community Lockers** | Smart lockers at high-traffic locations. Drop off the shovel, renter picks it up with a QR code. Like Amazon lockers but for your neighborhood. Open source hardware specs. |
| **Maker Space Integration** | BorrowHood instances inside physical maker spaces. Walk into the maker space, see what's available on the screen, rent it, use it on the spot. Bridge between digital listings and physical spaces. |
| **Education Platform** | Learn-by-doing through the mentor system. Structured courses: "Woodworking 101 with Marco" -- tools provided via BorrowHood rental, lessons tracked, certification issued. |
| **BorrowHood Foundation** | Non-profit governance. No VC money. No corporate board. Community-elected stewards. The protocol belongs to the people who use it. Like the Linux Foundation but for sharing. |
| **Franchise Toolkit** | Any entrepreneur in any country launches "BorrowHood [City]" with a complete package: branding, tech, training, seed data templates, local language pack. Not a franchise fee -- a support package. |
| **BorrowHood Key IoT** | NFC fobs for lockers, workshop access, helper entry. ESP32 + PN532 open source readers. MQTT to BorrowHood API. Full hardware specs published as open source STL + firmware. EUR 25/locker slot, EUR 4/member fob. |
| **Universal Trust Layer** | Your BorrowHood reputation works across all federated instances AND external platforms. A verified BorrowHood trust score becomes the open-source alternative to corporate credit scores. Carry it everywhere. Own it forever. |

---

### The Timeline

```
v1  Feb-Mar 2026    THE DEMO         DEV Challenge MVP -- prove the loop
v2  Mar-Apr 2026    THE REAL DEAL    Payments, Telegram bot, reviews, trust, QR
v3  Summer 2026     THE COMMUNITY    Federation, self-hosting, reputation passport
v4  Late 2026-2027  THE FREEDOM      API, AI, insurance pool, city partnerships
v5  2027+           THE ECOSYSTEM    Protocol spec, SDK, physical layer, foundation
```

### The Long Game

BorrowHood is not a company. It's infrastructure. Like email. Like the web. You don't pay to send email. You don't pay to have a website. You shouldn't pay to share your stuff with your neighbor.

Every platform that charges fees is extracting value from people who create value. BorrowHood does the opposite. Zero fees. Open source. Self-hostable. Federated. Your data is yours. Always.

The kid with nothing but a laptop and imagination becomes a creator. The retiree with a garage full of machines becomes her manufacturing partner. The immigrant who doesn't speak the language finds the neighbor who does. The motivated person with no startup capital builds a business from their garage.

Free as in freedom. That's not a slogan. That's the architecture.

---

## Testing -- Built Alongside The App

**THE PRINCIPLE: We build it right the first time. Then we verify it. Then we ship it.**

Every route gets a test. No exceptions. This is not optional. It is part of the build. Foo Fighters don't ship untested code.

### Phase 1 -- Core Auth
| Test | What It Verifies |
|------|-----------------|
| User registration | Email sent, account created, workshop profile initialized |
| Email confirmation | MailHog receives confirmation, link works |
| Login / Logout | JWT issued, session valid, logout clears tokens |
| Password reset | Reset email sent, new password works |
| Language preference | Saved to profile, UI switches correctly |
| Google OAuth | Social login creates account, links to Keycloak |

### Phase 2 -- Listings
| Test | What It Verifies |
|------|-----------------|
| Create listing with photos | Item created, photos uploaded to Minio, thumbnails generated |
| Edit listing | Changes persisted, photos updated |
| Set pricing | Rent price, sale price, deposit all saved correctly |
| Toggle rent/sell/both | Listing mode changes, correct buttons show on browse |
| YouTube video embed | Embed URL parsed, iframe renders, language tag stored |
| Language badge display | Listing shows owner's CEFR badges correctly in browse |
| Skills displayed | Owner's skills show on listing with correct verification level |
| Item types | Physical, digital, service, space, made-to-order all work |
| Digital download | File uploaded to Minio, download link generated for buyer |

### Phase 3 -- Transactions
| Test | What It Verifies |
|------|-----------------|
| Rent request sent | Request created, owner notified, status = "requested" |
| Rent request approved | Status -> "approved", renter notified, pickup details revealed |
| Rent request declined | Status -> "declined", renter notified with reason |
| Active rental | Status -> "active", due date set, both parties see it on dashboard |
| Rental return | Status -> "returned", deposit released, review prompt shown |
| Make an offer | Offer created, owner notified, can accept/decline/counter |
| Telegram link | Opens t.me/username correctly, works on mobile and desktop |
| Google Maps | Pickup location renders correctly, neighborhood level not exact |
| Google Calendar | Invite generated for both parties with correct dates |

### Phase 4 -- Reputation
| Test | What It Verifies |
|------|-----------------|
| Review submitted | Review created, language tagged, linked to rental |
| Skill-specific review | Skill rating stored, updates skill avg_rating |
| Points awarded | Correct points for action type (10 rental, 20 service, etc.) |
| Badge level updates | Points total triggers correct badge (Newcomer -> Contributor etc.) |
| Review weighting | Legend review = 10x Newcomer. Weighted score calculated correctly. |
| Cross-language bonus | +20 points when transaction crosses language barrier |
| Reviewer badge stored | Review records the reviewer's badge at time of writing |

### Phase 5 -- Data Sovereignty
| Test | What It Verifies |
|------|-----------------|
| Export triggered | Export job queued, status = "processing" |
| Folder structure | One folder per listing, images subfolder, index.html at root |
| Photos included | All listing photos present in export |
| HTML renders standalone | Open listing.html in browser -- looks correct without server |
| Reviews exported | All reviews with ratings, text, reviewer info |
| JSON export | Machine-readable, all fields present, valid JSON |
| Digital goods included | PDF/STL files present in export |
| Skills + reputation | Trust score, badges, skills all in export |

### Phase 6 -- Teams
| Test | What It Verifies |
|------|-----------------|
| Invite team member | Invitation sent via email/Telegram, status = "invited" |
| Accept invitation | Member joins team, role assigned, appears on workshop |
| Manager edits listing | Manager can edit owner's listings, changes saved |
| Helper assigned to delivery | Helper gets notification, can confirm/decline |
| Contributor adds item | Item appears in team workshop, contributor shown as source |
| Points split | Points distributed according to team percentages |
| Multi-team membership | User belongs to 2 teams, activity shows in both |

### Phase 7 -- Safety & Privacy
| Test | What It Verifies |
|------|-----------------|
| Location fuzzing | Public API never returns exact lat/lng, only neighborhood zone |
| Address encryption | Exact address encrypted at rest, only decrypted for confirmed transactions |
| Address reveal rules | Renter must be Contributor+ (50pts) AND transaction confirmed before address shown |
| Minor account blocked | Registration with age < 18 is rejected |
| Guardian mode | Parent account gets notified of all activity on child's items |
| Report button | Present on every listing, review, and profile |
| Help request | Only Verified Helpers can respond to help requests |
| Emergency contact | Alert fires if meetup not completed/cancelled within timeframe |

### Phase 8 -- i18n
| Test | What It Verifies |
|------|-----------------|
| UI language toggle | EN/IT switch works, all labels change, preference saved |
| Content language tag | New listing stores language_code correctly |
| Translate button | Browser translate fires on click, content translates |
| Mixed language browse | Italian listing + English listing both show correctly with flags |

---

## Bug Tracking

**BorrowHood gets its own bug dashboard. Separate from HelixNet and ISOTTO. Clean slate. Same tool, separate instance.**

### Standard Bug Fields

| Field | Description |
|-------|-------------|
| Bug ID | BH-001, BH-002, etc. |
| Title | Short description |
| Severity | Critical / High / Medium / Low |
| Route or Feature | Which page or API endpoint |
| Steps to Reproduce | Numbered steps, exact |
| Expected Behavior | What should happen |
| Actual Behavior | What actually happens |
| Assigned To | Who's fixing it |
| Status | Open / In Progress / Fixed / Verified / Closed |
| Git Commit | SHA when fixed |
| Test Added | Which test now prevents regression |

**Rule:** No bug is closed without a test that prevents it from coming back. Same standard as HelixNet.

---

## Hosting on Hetzner

BorrowHood runs as a **separate Docker stack** alongside HelixNet on the same Hetzner server.

```
Hetzner CX32 (46.62.138.218)
├── Caddy (reverse proxy, HTTPS)
│   ├── /helix/*        -> helix-platform container
│   ├── /borrowhood/*   -> borrowhood container (NEW)
│   └── /realms/*       -> keycloak container
├── PostgreSQL (shared, separate databases)
│   ├── helix_db
│   └── borrowhood_db   (NEW)
├── Keycloak (shared, separate realms)
│   ├── helix realm
│   ├── camper realm
│   ├── isotto realm
│   └── borrowhood realm (NEW)
├── Minio (shared, separate buckets)
│   ├── helix-uploads
│   └── borrowhood-photos (NEW)
├── Redis (shared)
├── RabbitMQ (shared)
└── MailHog (shared)
```

**Cost: EUR 0 extra.** Same server. Separate containers. Separate database. Separate Keycloak realm. Clean isolation with zero infrastructure cost for MVP.

**Domain options:** `borrowhood.helixnet.app` or `borrowhood.app` (grab the domain if available)

---

## The BorrowHood Key -- Physical Membership + IoT Access Layer

**A scammer can fake a profile. They can't fake a physical NFC fob mailed to a verified address.**

**The fob takes BorrowHood from app to real-world infrastructure. Not digital real. Physical real. Grandma real.**

### What It Is

An NFC key fob -- same tech as your gym tag, hotel room key, contactless payment card. **Every member gets one.** Not premium only. Not earned. Everyone. It arrives unactivated in the mail. EUR 10 to activate. That activation IS your membership.

### The Fob Tiers

| Tier | Cost | What It Does |
|------|------|-------------|
| **Unactivated** (arrives free) | EUR 0 | Proves you're a real person at a real address. Can browse listings. Cannot transact. |
| **Activated** (one-time fee) | EUR 10 | Registered to your account + identity. Unlocks smart lock access, GPS nav to items, auto-logged transactions. Full membership. |
| **Pro** (future versions) | TBD | Multiple fobs for family. Premium/high-value listings. Priority auctions. Extended rentals. v6/v7/v10 features. |

**The psychology:** The EUR 10 is not a subscription. It's not a paywall. You're holding a physical object. You're unlocking something you already have in your hand. One payment. Lifetime membership. Done.

### The Three Problems The Fob Solves At Once

**1. Identity.** A fob delivered by mail proves a real person at a real address. Fake accounts cannot get fobs. The postal system IS the identity verification layer.

**2. Trust.** When you hand your woodchipper access to someone with a registered, activated fob, you know who they are. One tap = verified identity, verified reputation, verified history.

**3. Monetization.** EUR 10 per activation. No subscription. No recurring fees. No paywall. Real revenue without taxing the community.

### Economics

| Metric | Number |
|--------|--------|
| Fob production cost | EUR 0.35 |
| Shipping cost (user pays) | EUR 1-3 |
| Activation fee (revenue) | EUR 10 |
| **Net per activation** | **~EUR 9.50** |
| At 1,000 members | EUR 9,500 |
| At 10,000 members | EUR 95,000 |
| At 100,000 members | EUR 950,000 |

### Hardware

| Component | Unit Cost | Notes |
|-----------|-----------|-------|
| NTAG215 / MIFARE NFC key fob (bulk) | EUR 0.25-0.35 | Industry standard, every NFC phone |
| Custom BorrowHood logo | +EUR 0.03 | Branded |
| Postage | EUR 1-3 | User pays |

For IoT locks (v3+):

| Component | Unit Cost | Notes |
|-----------|-----------|-------|
| ESP32 + PN532 NFC reader | EUR 8-12 | Open source hardware |
| 3D printed enclosure | EUR 2-5 | Published STL files |
| Electric lock / solenoid | EUR 10-15 | Per lock point |
| NFC-compatible padlock | EUR 15-30 | Outdoor equipment (Tapplock or similar) |
| **Total per lock point** | **EUR ~25-50** | DIY, open source, community-buildable |

### Open Source Stack

| Layer | Technology | License |
|-------|-----------|---------|
| NFC Fob | NTAG215 (NXP) | Industry standard |
| Locker Reader | ESP32 + PN532 | Open source hardware |
| Firmware | ESPHome / Arduino | Open source (MIT/Apache) |
| Communication | MQTT -> BorrowHood API | Open protocol |
| Smart Lock | Home Assistant compatible | Open source |
| 3D Printed Parts | Published STL files | CC-BY-SA |

Reference projects:
- HomeKey-ESP32 (github.com/rednblkx/HomeKey-ESP32)
- SmartLock (github.com/vogler/SmartLock) -- 3D printed, ESP32
- MQTTHomeKeyLock (github.com/Tomcuzz/MQTTHomeKeyLock)
- ECHO Lock (echolock.euro-locks.com) -- battery-free NFC locking

### What The Key Does -- By Tier

**Unactivated Fob (free, arrives with welcome pack):**
- Browse items, see listings, contact owners via Telegram
- Cannot rent, sell, or transact -- "you can look but not touch"
- Fob is a keychain reminder: "Activate me and join the hood"
- The psychology: you HAVE it, you HOLD it, the barrier is EUR 10 not a signup form

**Activated Fob (EUR 10 activation fee = membership):**
- Full platform access: rent, sell, list, review, earn points
- Meet for exchange -> both parties tap fobs -> transaction logged automatically
- GPS coordinates stored per item -> navigate to chained equipment in the dark
- "I am who I say I am" -- proved by a physical object at a verified address
- Lost/stolen? Deactivated instantly from the app. One fob per account.
- EUR 10 is NOT a subscription -- one-time activation, member for life

**Pro Fob (future -- v4/v5):**
- Locker access: BorrowHood lockers at partner locations (cafes, libraries, community centers)
  - Drop off shovel -> locker assigns slot -> renter taps fob -> locker opens
  - No meetup required. No address shared. Safe. Trackable. Asynchronous.
- Safe Helper access: Rosa's smart lock authorized for scheduled visits ONLY
  - Access logged: "Maria entered 14:02, left 15:15"
  - Rosa revokes access with one tap. Outside-hours tap = alert + emergency contact
- Workshop access: Marco's woodshop -- book "2 hours on the lathe" -> fob activates for that window only
  - Time-boxed. Logged. Revocable. No physical keys exchanged.

**GPS Navigation to Chained Items:**
- Jerry chains 3 woodchippers in his yard with NFC padlocks
- Each padlock stores GPS coordinates on the BorrowHood platform
- Renter books Woodchipper #2 -> app shows pin on map + "Navigate"
- It's 9pm, dark, unfamiliar yard -> GPS guides renter to exact equipment
- Tap fob -> chain releases -> Jerry gets Telegram notification
- No phone calls. No flashlights. No "it's the one by the fence."

**Anti-Fraud (all tiers):**
- One fob per account -- can't be shared
- Fob + phone = two-factor physical verification
- Every tap logged with timestamp + GPS
- Deactivate instantly if lost/stolen
- Can't clone NTAG215 cryptographic signature
- Unactivated fob = zero transaction capability (no value to steal)

### The Fob Economy -- How The Operator Makes Money

**The platform is free forever. The physical layer is the business.**

| Item | Who Pays | Amount | Goes To |
|------|----------|--------|---------|
| NFC fob | Free | EUR 0 | Operator absorbs (EUR 0.35 cost) |
| Fob activation | Member | EUR 10 | Operator (working capital, one-time) |
| Shipping | Member | EUR 1-3 | Postal service |
| Lost/stolen replacement | Member | EUR 10 new activation | Operator |
| Smart lock installation | Member | EUR 30-400 | Operator pays installer, keeps margin |
| Maintenance contract | Member | EUR 5-10/month | Operator |
| Hardware (lockboxes, locks) | Member | Varies | Operator marks up 30-40% |
| Emergency lockout | Member | Premium rate | Operator's callout service |

**1000 members x EUR 10 activation = EUR 10,000 working capital.** One-time fee, member for life. No subscriptions, no renewals, no gotchas.

### The Installation Service Network

The operator (Angel in Trapani, anyone in their city) manages a network of local installers:

```
1. User requests installation ("wire my garage door for BorrowHood Key")
2. Operator assigns installer from vetted network
3. Installer visits, assesses, quotes (parts + labor)
4. Operator reviews quote -- fair price? Correct scope?
5. Operator sends approved quote to user with guarantee
6. User approves
7. Installer does the work, documents it (photos + video report)
8. Operator reviews install report, confirms quality
9. User pays Operator
10. Operator pays installer (net 30-90 dunning cycle)
```

**Install types:**

| Type | What | Typical Quote |
|------|------|--------------|
| Smart front door | ESP32 + NFC reader + electric strike | EUR 80-150 |
| Lockbox (porch) | NFC-activated drop box for items | EUR 40-80 |
| Garage door NFC | Reader wired to existing opener | EUR 60-120 |
| Chain/padlock swap | NFC padlock on rototiller, woodchipper | EUR 30-60 |
| Workshop access | NFC reader at door, time-boxed | EUR 80-150 |
| Full property | Front + back + garage + lockbox | EUR 200-400 |

### Jerry's Woodchippers -- The Full Flow

```
1.  Jerry lists 3 woodchippers on BorrowHood
2.  Each has GPS coordinates stored (lat/lng of where it's chained)
3.  Each has an NFC padlock (EUR 30-60 installed by operator network)
4.  Renter searches "woodchipper" -> sees Jerry's 3 units on map
5.  Renter books Woodchipper #2, pickup window Friday 8pm-10pm
6.  Jerry gets Telegram: "Woodchipper #2 booked by Marco, pickup 20:00-22:00"
7.  Jerry approves (or auto-approve if he trusts the hood)
8.  Friday 9:04pm -- Marco opens app -> "Navigate to Woodchipper #2"
9.  GPS guides Marco through Jerry's dark yard to the exact machine
10. Marco taps fob on padlock -> chain releases -> pickup logged
11. Jerry gets Telegram: "Woodchipper #2 picked up at 21:04 by Marco"
12. Sunday 5:32pm -- Marco returns, taps fob -> chain locks -> return logged
13. Jerry gets: "Woodchipper #2 returned at 17:32 by Marco"
14. Jerry sleeps through the whole thing. The fob works.
```

**Why this matters:** Jerry has 3 woodchippers earning money while he watches TV.
No phone calls, no scheduling conflicts, no "can you come back at 6?"
The fob + GPS + NFC padlock = fully autonomous rental operation.

### The BorrowHood Operator Role

```
The First Operator: Angel Kenel, Trapani
├── Platform developer (the software -- open source, free)
├── Trapani Operator (the business -- this is where money comes from)
│   ├── Fob logistics (order bulk, program, ship to members)
│   ├── Installer network (vet, assign, quality-assure, pay net 30-90)
│   ├── Quality guarantor ("I reviewed the quote, it's fair")
│   ├── Payment handler (collect from users, pay installers)
│   └── Customer support (Telegram, the human touch)
└── Franchise template (document everything so other operators replicate)
```

**This IS the v5 Franchise Toolkit -- built by doing it first in Trapani.**

### Rollout Timeline

```
v1:     Pure digital. Build the platform, prove the community.
v2:     BorrowHood Key mailed to ALL members (unactivated, free).
        EUR 10 activation = full membership. Tap-to-verify at meetups.
        GPS coordinates on items. Operator handles fob logistics.
v3:     NFC padlocks on chained equipment. After-hours pickup.
        Installer network live. Smart lockers at partner locations.
v4:     Safe Helper access (smart locks for scheduled visits).
        Pro fob tier. Workshop time-boxed access.
v5:     Full IoT. Hardware specs published. Franchise toolkit.
        Franchise toolkit: any operator in any city replicates the model.
```

---

## Safety, Trust & Legal Architecture

**This section is not optional. This is not v2. This is the foundation. If we get this wrong, features don't matter.**

Every platform that connects strangers has blood on its hands somewhere. Airbnb has had murders. Craigslist has had kidnappings. Facebook Marketplace is a scam factory. The question isn't "can we prevent every bad thing." We can't. The question is: **what do we architect from day one to minimize harm, and what do we do when bad things happen anyway?**

### Location Privacy -- NON-NEGOTIABLE

```
WHAT THE PUBLIC SEES:           WHAT'S ACTUALLY STORED:
"Trapani, near city center"      38.0181, 12.5150 (exact)
[500m radius circle on map]      [Exact address in ENCRYPTED field]
                                 Decrypted ONLY after confirmed transaction
```

**Rules:**
1. **NEVER show exact address publicly.** Neighborhood zone only. 500m radius circle.
2. Exact address revealed ONLY after BOTH parties confirm the transaction AND the renter is at least Contributor level (50+ points).
3. Public meetup suggestion: platform recommends nearby public spaces (cafes, libraries) for first-time exchanges.
4. Users can opt for "public meetup only" -- never reveal home address at all.

### Minors Policy -- ABSOLUTE, NO EXCEPTIONS

1. **Minimum age to create an account: 18.** Period. Full stop.
2. Minors can ONLY participate through a parent/guardian team account. Luna (17) designs steampunk submarines -- her workshop is OWNED by her parent. Parent is the account holder. Parent approves every transaction.
3. **No in-person meetups involving minors unless parent/guardian is confirmed present.** Platform BLOCKS the transaction if guardian hasn't confirmed.
4. **Guardian mode:** Parent receives Telegram notification for EVERY transaction, message, and request involving their child's items. No exceptions. No override.
5. Age verification: self-declared at registration (v1), government ID verification (v2), age estimation from ID photo (v3).

### Vulnerable User Protection

Rosa is 83, wheelchair-bound. She's on the platform. Scammers see an easy target.

**The Verified Helper Program:**

| Requirement | Why |
|-------------|-----|
| Must be at least **Trusted** badge (200+ points) | Proven community member |
| Government ID uploaded, reviewed by admin | Real identity confirmed |
| Signed Helper Code of Conduct | Legal agreement |
| Background check (v2, where locally available) | Extra layer |
| Visible "Verified Helper" badge | Users can identify trusted helpers |

**What a Verified Helper does:**
- Visits non-tech users, helps take photos, write descriptions, set up workshop
- NEVER has access to the user's password or account
- Session is logged: who, when, approximate location
- Both parties rate each other afterward

**Protection layers for vulnerable users:**
- Emergency contact stored on every profile (optional but strongly encouraged)
- "Buddy system" option: flag yourself as wanting someone present during exchanges
- If a meetup doesn't result in "completed" or "cancelled" within expected timeframe, emergency contact gets a Telegram alert
- Vulnerable user flag (self-declared or helper-suggested) triggers extra verification on incoming requests

### The Community Help Board

Not a forum. Not Reddit. A simple "Help Wanted" section:

```
"I need help taking photos of my baking tools and setting up my workshop.
I'm in Trapani. I speak Italian (native). I can't travel.
Looking for a Verified Helper."
```

Only Verified Helpers can respond to help requests. Request + response = logged, trackable, reviewable.

### Scam Prevention

| Threat | Mitigation |
|--------|-----------|
| Fake listings (stock photos) | Reverse image search flag (v2). Community reporting. |
| Fake reviews (friends inflate score) | Weighted reviews -- Newcomer reviews barely count. |
| Stolen items listed | Require "I own this" checkbox. Community reporting. Serial number field (optional). |
| Advance fee scam ("pay deposit before seeing item") | Platform warns: "Never send money before seeing the item in person." |
| Identity theft | Exact address encrypted, never public. Neighborhood only. |
| Phishing via Telegram | Official BorrowHood bot has verified badge. "We will NEVER ask for your password via Telegram." |
| Account takeover | 2FA via Keycloak (v2). Session management. |

### Terms of Service & Community Rules

#### The BorrowHood Code

**1. Be Real**
- List only items you actually own or are authorized to rent
- Describe items honestly -- condition, defects, limitations
- Use real photos, not stock images
- Self-declare skill levels honestly (the community will verify)
- You must be 18 or older to create an account

**2. Be Fair**
- Honor your commitments -- if you agree to rent, follow through
- Return items on time and in the condition you received them
- If you break it, own it. Communicate immediately.
- Reviews must be honest. No revenge reviews. No fake praise.
- Pricing should be reasonable -- this is a neighborhood, not a hedge fund

**3. Be Safe**
- Never share exact addresses until a rental is confirmed
- Meet in public spaces for first-time exchanges when possible
- If a minor's items are involved, parent/guardian MUST be present
- If something feels wrong, report it. Trust your gut.
- No illegal items. No weapons. No controlled substances.

**4. Respect Privacy**
- Your location is shown at neighborhood level, not exact address
- Exact address only shared after confirmed transaction
- Your data is yours -- export anytime, delete anytime
- We don't sell your data. We don't mine your data. We don't have ads. Ever.
- GDPR compliant: right to be forgotten, data portability, consent management

**5. Disputes**
- Step 1: Resolve directly via Telegram (most disputes are miscommunication)
- Step 2: Request community mediation (a Trusted+ member reviews both sides)
- Step 3: Platform admin review (final decision, rare)
- Item damage: deposit covers it. If beyond deposit, parties negotiate.
- Platform is not a court and not a party to transactions.

### Reporting & Enforcement

| Action | Trigger |
|--------|---------|
| Report button | On every listing, review, profile, and message |
| Admin response | Within 24 hours |
| Warning | First valid report against a user |
| Restrictions | Three valid reports = account under review, listing ability suspended |
| Suspension | Serious violation (fraud, harassment, safety threat) = immediate suspension |
| Ban | Confirmed fraud, predatory behavior, or illegal activity = permanent ban |
| Law enforcement | If a report involves criminal activity, we cooperate fully with authorities |

### Platform Liability

**Legal position (v1 -- DEV challenge demo):**
- BorrowHood is a listing platform, not a transaction processor
- Like Craigslist -- we connect people, we don't guarantee transactions
- No money touches our servers in v1

**Before public launch with real users (post-challenge), we MUST have:**
- Legal review of ToS by an actual lawyer (EU/GDPR, local jurisdiction)
- Age verification mechanism beyond self-declaration
- GDPR data deletion compliance ("right to be forgotten")
- Law enforcement cooperation protocol documented
- Insurance for the platform itself (errors & omissions)
- Cookie consent and privacy policy (GDPR)

**What we are NOT responsible for (disclaimed in ToS):**
- The condition of items rented between users
- The outcome of in-person meetings
- Payment disputes (v1 has no payments; v2 payments go through Stripe/PayPal directly)
- The accuracy of self-declared skills or language levels

**What we ARE responsible for:**
- Keeping user data secure
- Responding to reports within 24 hours
- Removing illegal content immediately
- Cooperating with law enforcement
- Not selling or mining user data
- Providing data export at all times

---

## Onboarding Flow -- First-Time User Experience

**If the first experience is confusing, you lose them forever.**

### Grandma's Path (the non-tech onboarding)

Rosa has an email and a mobile phone. That's it. Here's how she gets on BorrowHood:

```
Option A: Self-service (mobile-friendly)
  1. Goes to borrowhood.app on her phone browser
  2. Taps "Create Account" -> email + password
  3. Guided setup walks her through (big buttons, simple language)
  4. Gets stuck on photos? -> Posts a Help Request
  5. A Verified Helper responds, comes to her place, helps set up

Option B: Family-assisted (the grandson path)
  1. Rosa sends email to grandson Marco: "I want to sell my recipes"
  2. Marco creates the account FOR her (with her email)
  3. Marco sets himself as Manager on her workshop team
  4. Marco manages everything remotely -- Rosa just bakes
  5. Rosa gets Telegram notifications: "Someone wants your cannoli recipe!"

Option C: Community-assisted (the Help Board)
  1. Rosa emails help@borrowhood.app (forwarded to the Help Board)
  2. "I make the best cannoli in Trapani. I need help getting online."
  3. A Verified Helper in Trapani picks up the request
  4. Helper visits Rosa, sets up her workshop, takes photos
  5. Rosa approves everything before it goes live
  6. Helper gets reputation points. Rosa gets her workshop.
```

**Key principle:** We meet people where they are. Not everyone is tech-savvy. Not everyone has a grandson. The platform must work for the 83-year-old in a wheelchair AND the 19-year-old with a laptop.

### The Guided Setup (runs once after first login)

```
Step 1: WELCOME
  "Welcome to BorrowHood! Let's set up your workshop in 4 steps."
  [Continue]

Step 2: YOUR WORKSHOP
  - Workshop name: [________________]
  - What kind? [Kitchen] [Garage] [Garden] [Workshop] [Studio] [Other]
  - Tagline: [________________] (one line about what you do)
  - Photo: [Upload avatar]
  [Next]

Step 3: YOUR LANGUAGES
  - "What languages do you speak?"
  - [Add Language] -> dropdown + CEFR level selector
  - Pre-filled with browser language at C2
  - Telegram username: [________________] (required)
  [Next]

Step 4: YOUR FIRST SKILL
  - "What do you know how to do?"
  - [Add Skill] -> name + level + specialty
  - "Don't worry, the community will verify this over time"
  [Next]

Step 5: YOUR FIRST LISTING
  - "Got something to share? List it now!"
  - Quick listing form: photo + title + description + rent/sell
  - [List It] or [Skip for now]

Step 6: DONE
  "Your workshop is live! Here's what you can do next:"
  - Browse your neighborhood
  - Complete your profile
  - Invite a team member
  [Go to Dashboard]
```

### The Team Onboarding

When the grandson in California is invited to manage Nonna's workshop:

```
Step 1: INVITATION
  "Rosa invited you to manage her workshop: Nonna Rosa's Kitchen"
  "Your role: Manager"
  [Accept] [Decline]

Step 2: WHAT YOU CAN DO
  "As a Manager, you can:"
  - Edit listings
  - Respond to rental requests
  - Handle messages
  - Upload photos
  "Rosa (Owner) handles the baking. You handle the tech."
  [Got it, let's go]
```

### Progressive Disclosure

Don't dump everything on day one. Features reveal as the user grows:

| User State | What They See |
|------------|--------------|
| Just registered | Basic workshop + first listing prompt |
| 1 listing added | Browse page, map, incoming requests |
| First transaction | Reviews, points, badge progress |
| 5 transactions | Full dashboard, export option, team invites |
| 20 transactions | Mentor option, advanced analytics |

**Rule:** Every new feature appears with a one-line explanation the first time. "You've unlocked Export! Your store, your data, always." Then it's just there, no more prompts.

---

## Competitive Position

| Platform | Fees | Language Match | Data Export | Collab | Digital Goods | Services | Open Source |
|----------|------|---------------|------------|--------|---------------|----------|-------------|
| Etsy | 6.5% | No | CSV only | No | Yes | No | No |
| eBay | 13% | No | Buried | No | Yes | No | No |
| FB Marketplace | Free (data farm) | No | LOL | No | No | No | No |
| Airbnb | 14-16% | Basic | Partial | No | No | Experiences | No |
| Craigslist | Free | No | None | No | No | No | No |
| Peerby | Free/Premium | No | None | No | No | No | No |
| Thingiverse | Free | No | Per-file | Sort of | STL only | No | No |
| **BorrowHood** | **Free forever** | **CEFR levels** | **Full static site** | **Maker+Creator** | **Any file** | **Rent+Sell+Train+Commission** | **Yes** |

---

## Seed Data Scenario

Trapani, Sicily neighborhood. Real-ish characters:

| User | Workshop | Type | Languages | Social | Items |
|------|----------|------|-----------|--------|-------|
| User | Workshop | Type | Languages | Skills | Social | Items |
|------|----------|------|-----------|--------|--------|-------|
| Sally Romano | Sally's Kitchen | kitchen | EN C2, IT A1 | Baking (Expert, Sicilian pastry), Teaching (Intermediate) | YouTube, IG | Cookie cutters, recipe PDF, baking lessons |
| Mike Torretti | Mike's Garage | garage | IT native, EN C1 | Carpentry (Expert), Plumbing (Intermediate), Gardening (Expert) | LinkedIn | Power drill, ladder, tile cutter, wheelbarrow, shovel |
| Angel Kenel | Angel's Studio | studio | EN C2, DE C2, IT A1, FR B1 | Design (Expert), Photography (Intermediate), Business consulting (Expert) | Web, YT, LI | Postcards, design tools, camera gear, templates |
| Nino Cassisa | Nino's Workshop | workshop | IT native, EN B2 | Mechanics (Expert, camper repair), Tour guiding (Intermediate) | Instagram | Camper parts, outdoor gear, generators, tours |
| Maria Ferrara | Maria's Garden | garden | IT native, EN A2 | Gardening (Expert, permaculture), Cooking (Expert, Sicilian) | -- | Garden tools, seedlings, composting, lessons |
| Marco Rossi | Marco's Woodshop | workshop | IT native, EN B1 | Carpentry (Expert, furniture joinery, 30 yrs), Teaching (Intermediate) | Web, Etsy, YT | Custom furniture, tools, blueprints |
| Jake Chen | Jake's MakerLab | workshop | EN C2, IT A2 | 3D Printing (Expert, FDM + resin), Programming (Expert) | YouTube, IG | 3D printer, filament, printing service |
| Luna Ferro | Luna's Designs | studio | IT native, EN B2 | Digital art (Expert, steampunk), 3D modeling (Intermediate) | IG, portfolio | STL files, concept art, design service |
| Rosa Ferretti | Nonna Rosa's Kitchen | kitchen | IT native, EN A1 | Baking (Legend, 60 yrs), Sicilian pastry (Expert) | -- | Cannoli, pastry tools, family recipes (digital) |
| Dave Murphy | Dave & John's | garage | EN C2, IT A2 | Carpentry (Expert), Plumbing (Intermediate) | -- | Full tool collection, workbench (space) |
| John Barrett | *(Helper on Dave's team)* | -- | EN C2, IT A1 | Driving (Expert, has pickup truck), Heavy lifting | -- | Delivery service for Dave's items |

**Seed scenarios to show off:**
- Sally has rented her cookie cutter 47 times + taught 12 baking lessons = **Legend** badge (1200+ pts)
- Mike has an active rental to Angel (power drill, due back Mar 5), badge: **Expert** (600 pts)
- Nino offers city tours as a service (B&B + tour combo), badge: **Trusted** (350 pts)
- Marco has digital blueprints AND physical tools AND mentors 2 new woodworkers, badge: **Expert**
- Maria's reviews are in Italian with translate buttons, badge: **Trusted** (280 pts)
- Angel has 4 languages + 3 cross-language deals = language bridge bonus shown, badge: **Contributor**
- Jake and Luna collaborating -- her STL says "Needs: 3D printer", his printer says "Compatible with: STL"
- Jake printed 3 of Luna's designs, both left skill-specific reviews ("3D printing: 5 stars", "Design quality: 5 stars")
- Sally got a 5-star review from Marco (Expert) = 25 weighted points vs a 5-star from Angel (Contributor) = 10 weighted points. Shows review weighting in action.
- Language teaching pair: Maria teaches Angel Italian (A1->A2), Angel teaches Maria English -- both rate the skill, cross-language bonus for both
- **Team: Nonna Rosa's Kitchen** -- Rosa (Owner, 83, wheelchair, Trapani) + grandson Marco (Manager, California) manages remotely
- **Team: Dave & John Heavy Lifting** -- Dave (Owner, tools) + John (Helper, truck) deliver together
- Team onboarding shown: Marco accepts invite, sees his Manager permissions
- **Help Board demo:** Rosa posted "Need help setting up" -> Maria (Verified Helper) responded -> session logged
- **Location privacy demo:** Browse shows "Trapani, near Via Fardella" with 500m circle, NOT exact address
- **Age gate demo:** Registration form shows "You must be 18+" with date picker

---

## The DEV Challenge Submission

### Post Title
"BorrowHood -- Every Garage Becomes a Rental Shop"

### Community
Neighborhoods. Every neighborhood on Earth. The expat who needs tools but doesn't speak the language. The retired gardener whose equipment collects dust. The baker whose grandmother's cookie cutter could bring joy to 100 families. The kid with a laptop and no equipment who finds the maker with the 3D printer.

### Story
"My father was a hand-shovel landscaper in Switzerland for 60 years. His garage was legendary -- 500 tools, every one with a story. When he passed in 2020, those tools sat there. Every neighborhood has a garage like his. Every neighborhood has people who need what's in it.

I'm building this from a camper van in Trapani, Sicily. I walked into a print shop that's been running since 1968. Three locations. All disconnected. I saw the same pattern everywhere -- people with stuff, people who need stuff, and no good way to connect them. Especially across language barriers.

BorrowHood connects them. Free as in freedom. Open source. No platform fees. Your data is yours -- export your entire store with one click. We're not a platform. We're a launchpad."

### Three Things That Make It Different

1. **Language proficiency matching (CEFR standard)** -- Nobody else does this. In a Mediterranean town where expats meet locals, knowing that the guy with the drill speaks B2 English changes everything. Filter by "speaks at least B1 English." Language badges on every listing.

2. **Data sovereignty** -- One-click export of your entire store as a browsable static website. Every other platform holds your data hostage. We show you the exit door on day one. Your data, your rules, always.

3. **Maker + Creator collaboration** -- The kid with the steampunk 3D designs finds the neighbor with the 3D printer. Her STL file says "Needs: 3D printer." His listing says "Compatible with: STL." The platform doesn't just match people with things. It matches skills with equipment.

4. **No bloat** -- We don't build chat (Telegram does it). We don't host video (YouTube does it). We don't do maps (Google does it). We build the platform, the trust layer, and the matching engine. Everything else, we delegate to tools that already work. Lean, focused, unkillable.

---

## File Structure

```
BorrowHood/
├── CONCEPT.md              <- This file
├── README.md               <- DEV challenge submission / project overview
├── VoiceRecordings/        <- Angel's concept recordings
├── Archive/                <- Old drafts
├── src/
│   ├── main.py             <- FastAPI app
│   ├── models/             <- SQLAlchemy models
│   ├── schemas/            <- Pydantic schemas
│   ├── routers/            <- API routes
│   ├── services/           <- Business logic
│   └── seed/               <- Seed data
├── templates/              <- Jinja2 + Tailwind + Alpine.js
├── static/                 <- CSS, images, icons
├── locales/
│   ├── en.json             <- English translations
│   └── it.json             <- Italian translations
├── scripts/                <- Utilities
├── Dockerfile
├── docker-compose.yml      <- Standalone deployment
└── requirements.txt
```

---

## Repo Strategy

**Development:** `/home/angel/repos/helixnet/BorrowHood/` (inside helixnet monorepo)
**Submission:** `github.com/akenel/borrowhood` (separate clean repo)

When ready to submit: copy clean build to new repo, fresh commit history, push.

---

*"Free as in freedom. Foo Fighters don't charge admission."*

*Concept v10: February 27, 2026 -- Trapani, Sicily*
*v1: Core concept, workshop profiles, CEFR language system*
*v2: Social links, digital items, deep language engine, translate buttons*
*v3: Collaboration layer (maker+creator), 5 listing types, 8 seed users, commission model*
*v4: Data sovereignty, one-click export, communication stack (Telegram + Google)*
*v5: Full v1-v5 roadmap, federation, protocol spec, physical layer, ecosystem vision*
*v6: Skills profile, reputation gamification, weighted reviews, badge system, skill verification*
*v7: Teams, test suite (7 phases), bug tracking, hosting plan, ToS, onboarding flow, 11 seed users*
*v8: SAFETY -- location privacy, minors policy, vulnerable user protection, Verified Helper program,*
*    scam prevention, community help board, grandma's onboarding path, platform liability, GDPR,*
*    law enforcement protocol, 8 test phases*
*v9: BorrowHood Key -- NFC physical trust token, locker system, helper access, workshop access,*
*    NTAG215 + ESP32 + MQTT open source hardware stack, EUR 4/member, EUR 25/locker*
*v10: OPERATOR MODEL -- fob economy, EUR 10 deposit, installer network, installation quotes,*
*     net 30-90 dunning, quality guarantee, Jerry's woodchippers, franchise template*
*Built from a camper van. For real communities. By real people.*
