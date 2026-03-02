---
title: BorrowHood -- Every Garage Becomes a Rental Shop
published: true
tags: devchallenge, weekendchallenge, showdev
---

## The Community

My father Albert was a hand-shovel landscaper in Switzerland from 1960 to 2020. His garage had 500 tools. When he passed, they sat there collecting dust. His neighbors still needed shovels, rakes, and chainsaws -- they just didn't know where to look.

Craigslist is a wasteland. Facebook Marketplace is a data farm. Neither cares about your neighborhood.

BorrowHood is for **real neighborhoods** -- the people on your street who own a drill you need once, a stand mixer sitting idle, a welder gathering dust. Every user is a workshop. Every garage becomes a rental shop. Every kitchen becomes a bakery.

The community I built for: **neighbors who share things instead of buying things they'll use once.**

## What I Built

A full-stack community rental and sharing platform where people list their underused tools, kitchen gear, equipment, and skills -- and neighbors borrow, rent, or trade. No middlemen. No fees. No algorithm deciding who sees what.

**Live demo:** [https://46.62.138.218](https://46.62.138.218)
Test user: `angel` / `helix_pass` (or sign in with GitHub)

> **Note:** Your browser will show a certificate warning on first visit -- the server uses a self-signed TLS certificate (no domain, just an IP). Click **Advanced** > **Proceed to site**. It only happens once.

![BorrowHood Home](https://raw.githubusercontent.com/akenel/borrowhood/main/docs/screenshots/home.png)

### What it does

**Eight ways to share:**
- **Rent** -- borrow a drill for the weekend
- **Sell** -- offload gear you don't need
- **Give Away** -- free items, simplified claim flow, earns Generous Neighbor badge
- **Auction** -- competitive bidding with reserve prices and anti-snipe protection
- **Commission** -- custom made-to-order items
- **Service** -- plumbing, tutoring, bike repair
- **Training** -- teach a neighbor your skill
- **Offer** -- name your price / make an offer

**Full rental lifecycle:**
Request > Approve > Pickup (lockbox code) > Return (lockbox code) > Review > Complete. With security deposits, dispute resolution, and PayPal payments at every step.

**Security deposits -- peer-to-peer insurance:**
You lend your neighbor a EUR 2,000 drone. How do you know you get it back in one piece? The deposit. The owner sets the amount. The renter pays it at pickup. Bring it back in one piece -- deposit returned. Break it -- owner keeps the deposit. No insurance company. No paperwork. Just neighbors handling it themselves. If they disagree, the 3-step dispute resolution kicks in and the deposit follows the outcome automatically.

**Reputation that means something:**
15 badges across 5 tiers (Newcomer to Legend). Reviews are weighted by the reviewer's badge tier -- a Legend's 5-star review counts 10x more than a Newcomer's. Your reputation is earned, not gamed.

**Bilingual from day one:**
One click switches the entire app between English and Italian. Navigation, forms, badges, categories, filters, error messages -- 500+ translated strings, nothing left behind.

![Browse Items](https://raw.githubusercontent.com/akenel/borrowhood/main/docs/screenshots/browse.png)

### Feature highlights

| Feature | What it does |
|---------|-------------|
| Workshop profiles | Every user is a shop with skills, CEFR language levels, social links |
| Auction system | Timed bidding, auto-outbid notifications, reserve prices, bid increments |
| Giveaway flow | Free items, simplified claim, no return dates, Generous Neighbor badge |
| Lockbox codes | One-time 8-character codes for contactless pickup and return |
| Security deposits | Owner sets amount, hold at pickup, auto-release on return, forfeit on damage |
| Dispute resolution | 3-step flow: file, respond, resolve (8 reasons, 7 resolutions, deposit auto-wired) |
| Community helpboard | Post requests ("Need a ladder this Saturday"), get replies, track status |
| AI-assisted listings | Generate descriptions and images via Pollinations API |
| Notification bell | 15 event types with optional Telegram bot forwarding |
| GitHub OAuth | Sign in with GitHub via Keycloak identity provider |
| Onboarding wizard | 3-step profile setup for new users |

![Workshop Profile](https://raw.githubusercontent.com/akenel/borrowhood/main/docs/screenshots/workshop.png)

## Demo

**6-part video series showing every feature live on a production server:**

1. [EP1 -- Giveaway Flow](https://youtu.be/ML1aPJqHDuc) -- free items, simplified claim
2. [EP2 -- Rental Flow](https://youtu.be/DRju5RuojeA) -- full lifecycle from request to review
3. [EP3 -- Auction System](https://youtu.be/T2WqnM457LI) -- competitive bidding with anti-snipe
4. [EP4 -- Badge System](https://youtu.be/MxlZX1yHoYc) -- 15 badges, 5 reputation tiers
5. [EP5 -- Multilingual Live Switch](https://youtu.be/SLB3-0vIlaI) -- one click, every label, instant
6. [EP6 -- Deposit System](https://youtu.be/MJWlWsiJHCY) -- hold, release, forfeit, dispute resolution

**Live demo:** [https://46.62.138.218](https://46.62.138.218)
Log in as `angel` / `helix_pass` or use **Sign in with GitHub**.

![Dashboard](https://raw.githubusercontent.com/akenel/borrowhood/main/docs/screenshots/dashboard.png)

## Code

**GitHub:** [github.com/akenel/borrowhood](https://github.com/akenel/borrowhood)

### By the numbers

| Metric | Count |
|--------|------:|
| Python source lines | 10,625 |
| HTML template lines | 6,244 |
| Test lines | 2,220 |
| SQLAlchemy models | 32 |
| Typed enums | 37 |
| REST API endpoints | 109 |
| Automated tests | 250 (201 without DB) |
| Puppeteer screen tests | 52 edge-case checks |
| i18n strings | 476 (EN + IT) |
| Seed data items | 119 across 21 categories |

250 automated tests across 23 test files (201 pass without any database). Rental state machine alone has 26 tests covering every valid and invalid transition. Plus 52 Puppeteer edge-case screen tests covering XSS probes, pagination boundaries, mobile viewport, gallery behaviour, and API boundary conditions. The i18n completeness test ensures every English key has an Italian translation -- add a key to `en.json` without adding it to `it.json` and the test suite fails.

## How I Built It

### Tech stack

| Layer | Technology |
|-------|-----------|
| Backend | **FastAPI** + SQLAlchemy 2.0 async + asyncpg |
| Auth | **Keycloak** OIDC (RS256 JWT, 6 roles, GitHub IDP) |
| Database | PostgreSQL 17 |
| Cache | Redis 7 |
| Queue | RabbitMQ 3.13 |
| Frontend | **Jinja2** SSR + **Tailwind CSS** (CDN) + **Alpine.js** (CDN) |
| Payments | PayPal REST API v2 |
| AI | Pollinations API (image + text generation) |
| Bot | Telegram Bot API |
| Tests | pytest + pytest-asyncio |
| Hosting | **Hetzner CX32** -- 4 vCPU, 8 GB RAM, EUR 7.59/month |

### Architecture

```
Browser --> Caddy (TLS) --> FastAPI (uvicorn)
                              |
                              +-- 18 Jinja2 templates (i18n: EN/IT)
                              +-- 109 API endpoints (JSON)
                              +-- Keycloak OIDC (6 roles, GitHub OAuth)
                              +-- PostgreSQL (32 models, UUID PKs)
                              +-- Redis + RabbitMQ + MinIO
```

### How Claude Code helped

Claude Code (Opus 4.6) was my co-pilot throughout. Not a code generator I copied from -- a pair programmer I worked with.

**What worked well:**
- **Scaffolding models and routers** -- describing a feature like "auction system with reserve prices and anti-snipe" and getting a working first draft with the right SQLAlchemy relationships
- **Test generation** -- 250 pytest tests + 52 Puppeteer edge-case screen tests, most written by describing the behavior I wanted tested
- **Edge-case testing** -- Puppeteer tests that probe XSS, pagination boundaries, invalid enums, mobile viewport, broken images -- found a real 500 error on invalid listing type filter
- **Deposit system wiring** -- the deposit auto-release on rental completion and dispute-to-deposit wiring were Claude Code fixes applied hours before deadline. Described the gap, got working code in minutes
- **i18n coverage** -- translating 476 strings to Italian with context-appropriate translations (not Google Translate quality)
- **Debugging production issues** -- tracing an OAuth redirect loop to a missing port number in an env var, across 4 different config files

**What I still did myself:**
- Architecture decisions (Keycloak over simple JWT, server-rendered over SPA)
- UI/UX design (every page layout, color choices, the workshop-as-identity concept)
- The deposit-as-insurance concept (no third-party insurer -- neighbors handle it themselves)
- Production deployment and ops (Docker Compose, Caddy config, Hetzner setup)
- Manual testing on a real server with real users
- All 6 demo videos (Puppeteer + OBS, recorded and edited same day)

The commit history tells the story. Every feature was built iteratively -- scaffold, test, deploy, fix, repeat.

### The origin story

Built from a camper van in Trapani, Sicily. The idea came from my father's garage -- 500 tools, no neighbors who knew they existed. BorrowHood is the platform I wish he'd had.

Open source. No platform fees. Forever.

*"Every neighborhood has a garage like his."*
