---
title: "I Plugged Gemini Into My 10,000-Line Rental Platform. Here's What Happened."
published: false
tags: devchallenge, geminireflections, gemini, ai
---

*This is a submission for the [Built with Google Gemini: Writing Challenge](https://dev.to/challenges/mlh-built-with-google-gemini-02-25-26)*

## What I Built with Google Gemini

BorrowHood is a neighborhood sharing platform I built from a camper van in Trapani, Sicily. 10,000+ lines of Python. 100+ REST endpoints. 30+ database models. Keycloak authentication. Weighted reputation system where a Legend's review counts 10x more than a Newcomer's. Auctions with anti-snipe protection. CEFR language proficiency matching so expats can find neighbors who speak their language.

I built the platform with Claude Code. Four demo videos on YouTube. A live instance on Hetzner.

Then I saw the Gemini writing challenge and thought: what if I added a brain?

Not replacing anything. Adding an intelligence layer on top of what already exists. **Three AI agents powered by Google Gemini**, using Google's Agent Development Kit (ADK), talking to my production API.

### Agent 1: Smart Listing Assistant

User says "I want to list a Bosch power drill." Gemini searches existing items on the platform for price comparison, checks the 31 valid categories, and generates a complete listing:

```json
{
  "title": "Bosch GSB 18V Cordless Impact Drill",
  "description": "My trusty Bosch GSB 18V cordless impact drill is looking
    for a new adventure! It's been with me for about two years and is still
    in good working condition, perfect for all your home improvement projects.",
  "category": "power_tools",
  "subcategory": "drills",
  "condition": "good",
  "suggested_price": 8.0,
  "price_unit": "per_day",
  "deposit_suggestion": 24.0,
  "tags": ["power drill", "Bosch", "cordless drill"],
  "story_suggestion": "This drill has helped me hang countless shelves and
    assemble quite a few IKEA nightmares -- it's a real workhorse!"
}
```

That story suggestion? The agent came up with "IKEA nightmares" on its own. I call this the Grandma Test: if an 83-year-old in a wheelchair can understand your listing description, it passes.

### Agent 2: Review Sentiment Analyzer

Ask "Analyze Sally Thompson's reviews" and Gemini pulls all her reviews from the API, checks the reviewer's badge tier (because a review from a PILLAR member carries 8x the weight of a NEWCOMER), and returns:

```json
{
  "user_name": "Sally Thompson",
  "badge_tier": "trusted",
  "sentiment": { "positive": 1, "neutral": 0, "negative": 0 },
  "average_rating": 5.0,
  "weighted_average": 5.0,
  "fake_review_flags": ["No fake review indicators detected"],
  "top_keywords": {
    "positive": ["immaculate", "changed my life", "focaccia", "pro"],
    "negative": []
  },
  "summary": "Sally Thompson, a TRUSTED tier member, has an excellent
    reputation on BorrowHood. Her single review, from a highly influential
    PILLAR member, praises her KitchenAid stand mixer as 'immaculate'."
}
```

The agent understood the weighted reputation system without me hardcoding any analysis logic. It figured out that one review from a PILLAR member means more than five reviews from newcomers.

### Agent 3: AI Concierge

Natural language search. "I need something to cut tree branches" becomes an API search for garden tools, power tools, and saws. When nothing matches, the concierge responds like a neighbor, not a search engine:

> "I'm sorry, I couldn't find any listings for tree-cutting tools right now. Would you like to try searching for 'garden tools' or 'power tools'? Or perhaps you have a different type of cutting tool in mind?"

### The Root Orchestrator

One agent routes everything. Listing questions go to the Listing Assistant. Reputation questions go to the Review Analyzer. Search queries go to the Concierge. General BorrowHood questions, it answers directly.

```python
root_agent = Agent(
    model="gemini-2.5-flash",
    name="borrowhood_agent",
    sub_agents=[listing_assistant, review_analyzer, concierge],
)
```

Four lines of code to wire three specialists into one brain.

## Demo

**GitHub:** [github.com/akenel/borrowhood](https://github.com/akenel/borrowhood)
**Live demo:** [BorrowHood Demo Login](https://46.62.138.218/demo-login)
**YouTube playlist:** [BorrowHood: The Garage Sessions](https://youtube.com/playlist?list=PLxrmR3LJOIZ7cgPBMZjIRrKJPXHrCbR0b)

The agents sit in the `agents/` directory of the repo and call the same REST API that the web frontend uses. No special database access. No coupling. The intelligence layer sits on top of the platform, not inside it.

```
BorrowHood (FastAPI, 100+ endpoints)
    |
    +-- agents/
    |   +-- agent.py             (root orchestrator)
    |   +-- listing_assistant.py
    |   +-- review_analyzer.py
    |   +-- concierge.py
    |   +-- tools/
    |       +-- items.py         (search_items, get_categories)
    |       +-- reviews.py       (get_user_reviews, get_review_summary)
    |       +-- users.py         (search_members, get_user_profile)
    |       +-- common.py        (auth, HTTP helpers)
```

The tools are plain Python functions that wrap `httpx` calls:

```python
def search_items(query: str, category: str = "", limit: int = 10) -> dict:
    """Search BorrowHood items by keyword and optional category."""
    params = {"q": query, "limit": limit}
    if category:
        params["category"] = category
    return bh_get("/api/v1/items", params=params)
```

The ADK automatically introspects the function signature and docstring, presenting them as tool descriptions to Gemini. The model decides when to call which tool based on the user's query. Zero prompt engineering for tool selection.

## What I Learned

**1. The ADK is genuinely good.** I expected boilerplate. I got four lines to wire three agents. The `Agent` class, `sub_agents` for delegation, automatic tool introspection from function docstrings. This is how agent frameworks should work: code-first, no YAML, no visual builders.

```python
listing_assistant = Agent(
    model="gemini-2.5-flash",
    name="listing_assistant",
    instruction="You are a listing assistant for BorrowHood...",
    tools=[search_items, get_categories],
)
```

That is the entire agent definition. The instruction tells it what to do. The tools tell it what it can access. Done.

**2. Gemini understands context it was not trained on.** I told the Review Analyzer about BorrowHood's weighted reputation system: "NEWCOMER = 1x, ACTIVE = 2x, TRUSTED = 5x, PILLAR = 8x, LEGEND = 10x." In its analysis of Sally, it correctly noted that her single review from a PILLAR member "carries significant weight." It applied the weighting concept to the actual data and drew a conclusion. That is comprehension, not pattern matching.

**3. Existing APIs are the perfect tool layer.** I did not need to write any new backend code. BorrowHood already had 100+ endpoints covering items, reviews, users, listings, and badges. The agents just needed thin wrapper functions that translate ADK tool calls into REST API requests. The entire tools layer is 150 lines of Python. If your app already has an API, you are 80% of the way to having an AI agent.

**4. Agent delegation beats one mega-agent.** My first instinct was one agent with all tools. Wrong. The root orchestrator with three specialists is cleaner, faster, and produces better results. Each specialist has a focused instruction and a small tool set. The root agent's only job is routing.

## Google Gemini Feedback

### The Good

**gemini-2.5-flash is fast and smart.** The Listing Assistant generated a complete, valid JSON listing in under 3 seconds. It picked the right category from 31 options. It suggested a fair rental price (EUR 8/day for a power drill) by checking similar items on the platform. It even wrote a story about "IKEA nightmares."

**The ADK is excellent.** Minimal boilerplate. Python-native. Tool introspection from docstrings is a killer feature. Multi-agent delegation with `sub_agents` just works. I went from zero to three working agents in under an hour.

**Tool use is reliable.** Gemini consistently called the right tools with the right parameters. When the Review Analyzer needed Sally's reviews, it first searched for "Sally Thompson" via `search_members`, got her ID, then called `get_user_reviews` and `get_review_summary` with that ID. Multi-step tool chains work without babysitting.

### The Bad

**Free tier rate limits are punishing.** `gemini-2.5-flash` free tier: 5 requests per minute, 20 requests per day. A single multi-agent query can burn 4-6 requests (root agent + sub-agent + tool calls + follow-up). I ran exactly 3 test queries before hitting the daily limit. For a developer evaluating whether to build on Gemini, 20 requests per day is not enough to finish a single testing session.

**New API key propagation is confusing.** I created a fresh project and API key. The first 5 minutes: every model returned `limit: 0` errors. No requests allowed. No warning in the console. I had to wait blindly for quotas to propagate. A "your key is provisioning, try again in 5 minutes" message would save developers real confusion.

**Model naming is a moving target.** `gemini-1.5-flash` returned 404. `gemini-2.0-flash` hit rate limits. `gemini-2.5-flash` worked. The API lists 16+ model variants including `gemini-3-flash-preview` and `gemini-2.5-flash-lite`. Which one should I use? The docs say `gemini-2.0-flash` but the API disagreed. Clearer "use THIS model" guidance would help.

### The Ugly

I have history with Gemini. 11 months ago, before I met Claude, I was learning AI with Gemini. It made mistakes that felt almost deliberate. Hallucinations in code that compiled but did the wrong thing. I had to stop using it entirely. That experience taught me what to look for in an AI coding partner, and ultimately led me to Claude Code by Anthropic which I use to build BorrowHood.

Coming back to Gemini now through the ADK, I see real improvement. `gemini-2.5-flash` is a different animal. It follows structured output instructions, calls tools correctly, and understands domain context from instructions alone. The 11-month gap shows.

### What Is Next

BorrowHood has four more agents designed:

1. **Cross-Language Matchmaker** -- Luna's 3D design files say "Needs: 3D printer." Jake's listing says "Compatible with: STL." The agent finds these matches across language barriers using CEFR proficiency data.

2. **Onboarding Wizard Agent** -- Walk new users through setting up their workshop via conversation.

3. **Dispute Resolution Assistant** -- When a rental goes wrong, the agent reviews both sides and suggests fair resolution.

4. **Community Pulse Agent** -- Weekly digest of neighborhood activity.

The data model already supports all of this. The agents just need to be wired up.

**BorrowHood is open source. Free as in freedom. No platform fees. Your data is yours.**

Built from a camper van in Trapani, Sicily. Every neighborhood has a garage like his.

---

*Tech stack: FastAPI, SQLAlchemy, Keycloak OIDC, PostgreSQL, Redis, Docker, Tailwind CSS, Alpine.js*
*AI: Google Gemini 2.5 Flash via ADK (agents), Claude Code by Anthropic (platform development)*
*Hosting: Hetzner Cloud (EUR ~15/month)*
