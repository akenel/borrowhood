# QA Bug Sniffing SOP -- Angel's Method

**Fast, efficient, no-nonsense bug hunting.**

---

## Setup (once)

1. Open the site in Firefox or Chrome
2. Press **F12** to open Developer Tools
3. Click the **Console** tab
4. Click **Errors** filter button (hides warnings, info, debug)
5. You should see ONLY red errors now -- everything else is filtered out

## The Process

1. Navigate to a page
2. Click around like a normal user would
3. If red errors appear, copy 3 things:

```
URL:    https://lapiazza.app/the-page-you-were-on
Action: what you clicked or did ("clicked My Orders tab")
Errors: paste the red text from console
```

4. Drop it to Tigs
5. Move to next page -- don't wait for the fix

## What to Copy

**Console errors (red text):** Just copy/paste the text. No screenshot needed for console errors -- text is faster and searchable.

**Screenshots:** Only for VISUAL bugs -- wrong layout, missing button, text overlapping, ugly stuff. Not needed for console errors.

## What to Ignore

- Yellow warnings (not bugs)
- `-webkit-text-size-adjust` (Firefox CSS thing)
- `cdn.tailwindcss.com production` warning
- `NS_BINDING_ABORTED` (browser cancelled a request)
- `OpaqueResponseBlocking` on images (cross-origin, cosmetic)

## Page Test Order

Hit these pages in order as each demo user:

| # | Page | URL | What to click |
|---|------|-----|---------------|
| 1 | Home | `/` | Hero buttons, category links |
| 2 | Browse | `/browse` | Category cards, search, filters, item cards |
| 3 | Item Detail | `/items/{any-slug}` | Gallery, tabs, Make an Offer, Rent/Buy |
| 4 | List Item | `/list` | Fill form, pick categories, upload photo |
| 5 | Dashboard | `/dashboard` | Every tab: My Items, Orders, Incoming, History, Favorites, Disputes, Settings |
| 6 | Orders | `/orders` | I Paid button, Confirm Payment, Mark Complete |
| 7 | Help Board | `/helpboard` | Post, reply, upvote, author links |
| 8 | Profile | `/profile` | Edit Profile link, avatar/banner upload |
| 9 | Members | `/members` | Search, filter, click profiles |
| 10 | Messages | `/messages` | Open threads, send message |

## Demo Users

All passwords: `helix_pass`

| Username | Role | Focus |
|----------|------|-------|
| `sally` | Seller | Kitchen items, incoming requests |
| `mike` | Service provider | Garage items, services |
| `leonardo` | Buyer | Orders, commitments |
| `sofiaferretti` | Baker | Items, reviews |
| `nino` | Camper services | Workshop |
| `george` | Landlord | Villa items |

## Bug Report Template

```
URL:
Action:
Errors:

```

Copy that template, fill it in, paste to Tigs. Done.

---

*"Click like a monkey. Report like a pro."*
*Created: March 26, 2026*
