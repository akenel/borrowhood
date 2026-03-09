# EP02 "The Cookie Run" -- Post-Take Review

**Take:** 15 (final)
**Date:** March 8, 2026
**Duration:** 11 minutes 8 seconds
**File:** `the-cookie-run-FINAL.mp4`

---

## What shipped (visible on screen)

| BL# | Feature | Where it shows |
|-----|---------|----------------|
| BL-077 | In-app messaging | Message icon + unread badge in nav bar |
| BL-078 | Review photos | Photo upload endpoint ready (no photos in EP2 flow) |
| BL-079 | Recently viewed items | Horizontal strip on item detail pages |
| BL-080 | Listing Q&A | Q&A section on item detail pages |
| BL-082 | Order history page | "Orders" link in nav, full history with filters |
| BL-098 | Last seen / online indicator | "online now", "seen Xm ago" on member cards + workshops |
| BL-099 | Telegram/email comm icons | TG (sky blue) and email icons on member cards + workshops |
| BL-100 | Geolocation fallback | Trapani centro default when browser denies location |

**Total: 8 features built and deployed in one session.**

---

## What broke / got fixed before recording

| Issue | Root cause | Fix |
|-------|-----------|-----|
| Sally Thompson vs Sally Baker | Demo login page had "Baker", seed.json had "Thompson" | Fixed demo_login to "Thompson" |
| Hardcoded dates Mar 4/8 in scenes 6d/6e | Would show past dates on any take after Mar 8 | Replaced with dynamic relative dates |
| Missing `x-init` on messages page | Alpine.js wouldn't call `init()` on page load | Added `x-init="init()"` |
| Missing cascade deletes in cleanup SQL | bh_payment, bh_insurance, bh_message, bh_listing_qa not cleaned | Added DELETE statements for all 4 tables |
| `bh_insurance` table doesn't exist on Hetzner | Model exists but table never created | Wrapped in `DO $$ IF EXISTS` conditional |
| `src/models/mentorship.py` missing on Hetzner | File existed locally but wasn't in deploy tarball | Deployed separately |
| Geolocation "access denied" on Hetzner | mkcert on bare IP isn't a "secure context" for browsers | Added Trapani fallback coordinates |

---

## Lessons learned

1. **Five features in one session is possible** when you parallelize -- agents build models while you wire templates
2. **The seal inspection lesson applies to code** -- one name mismatch means check ALL names across all layers (seed.json, demo_login, script overlays)
3. **Every new table needs a DELETE in the cleanup SQL** -- add the cleanup line in the same session you add the feature
4. **mkcert on a bare IP is NOT HTTPS** in the browser's eyes -- geolocation, service workers, clipboard API all require a real secure context
5. **Dynamic dates beat hardcoded dates** -- scripts should work on any recording date, not just today
6. **Voice recordings ARE the product roadmap** -- 4 recordings became 12 backlog items, a security plan, and a revenue model
7. **Verify before claiming done** -- audit agents caught 5 critical issues that would have forced another take

---

## Backlog for next episode (EP03: The Scooter)

### High priority (build before EP03)
| BL# | Item | Priority |
|-----|------|----------|
| BL-089 | Rate limiting -- Traefik middleware | HIGH |
| BL-090 | Cloudflare DNS + DDoS protection | HIGH |
| BL-091 | Email verification on signup | HIGH |
| BL-095 | Real domain + Let's Encrypt SSL | HIGH |

### Medium priority (nice to have for EP03)
| BL# | Item | Priority |
|-----|------|----------|
| BL-085 | Advanced search -- filters, autocomplete | MEDIUM |
| BL-092 | hCaptcha on registration | MEDIUM |
| BL-093 | Account age gate for reviews | MEDIUM |

### Low priority (Season 2)
| BL# | Item | Priority |
|-----|------|----------|
| BL-096 | Affiliate program -- footer partner links | LOW |
| BL-097 | Seller promoted listings | LOW |
| BL-084 | Social sharing previews (OG meta tags) | LOW |
| BL-088 | Rental calendar / availability picker | LOW |

### Known visual issues
- Sally's "electric scooter" item shows a bicycle image (Pollinations prompt needs refinement)
- Johnny's broken bike is listed as OFFER (free) -- intentional for story arc, not a bug

---

## Next episode prep notes (EP03: The Scooter)

**Arc:** Sally sees Johnny's broken bike, recognizes the opportunity. Mentorship begins.
**Characters:** Sally Thompson, Johnny Abela, Pietro Ferretti (cameo)
**Data setup needed:**
- Johnny's broken bike must be visible and listed as OFFER
- Sally needs to have rental history showing she's established
- Mentorship relationship Sally -> Johnny may need to be seeded
- Scooter image should be fixed (real scooter, not bicycle)

---

*"No flashbacks. Do it right the first time."*
*Reviewed by: Angel + Tigs, March 8, 2026*
