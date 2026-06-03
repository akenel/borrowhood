# La Piazza Stock-Take — 2026-06-03

*Snapshot taken Wednesday evening from PROD. Beckenried sunset. First-week-back at HQ.*

---

## 1. The headlines

| Metric | Value |
|---|---|
| Active items | **910** |
| Items with at least one photo | 906 (99.6%) |
| Listings total | 964 |
| Listings ACTIVE | **883** |
| Registered users | **352** |
| Item views, last 30 days | **33,139** |
| Distinct items viewed, last 30 days | **863** |

**Headline take:** The marketplace is real. 33k views across 863 items is not your testing. Real anonymous traffic, distributed across nearly every active listing.

---

## 2. Listings by type — active only

```
TRAINING    413  ████████████████████████████████████████████ 47%
RENT        328  ███████████████████████████████████ 37%
SERVICE      53  █████ 6%
SELL         32  ███ 4%
OFFER        28  ██ 3%
GIVEAWAY     12  █ 1%
COMMISSION    8  · 1%
EVENT         4  · <1%
AUCTION       3  · <1%
RAFFLE        2  · <1%
```

**Take:** TRAINING + RENT = 84% of the marketplace. La Piazza is functioning primarily as a **learning + lending platform**, not a sales platform. Lean into that with the Locandina aesthetics — most cards will be Training/Rental, not Event/Raffle.

---

## 3. Items by category — top 15

| # | Category | Count |
|---|---|---|
| 1 | art | 187 |
| 2 | sports | 125 |
| 3 | education | 105 |
| 4 | science | 65 |
| 5 | music | 51 |
| 6 | electronics | 34 |
| 7 | tools | 31 |
| 8 | kitchen | 20 |
| 9 | power_tools | 19 |
| 10 | training_service | 19 |
| 11 | engineering | 17 |
| 12 | outdoor | 16 |
| 13 | garden | 15 |
| 14 | vehicles | 14 |
| 15 | tools_services | 13 |

**Take:** art + sports + education + science + music = makers, teachers, scientists, players. Exactly the people you've been talking about all along. No "shopping" categories dominating; this is a craft-economy.

---

## 4. Users by city — top 10

| # | City | Users |
|---|---|---|
| 1 | Trapani | 22 |
| 2 | (none set) | 19 |
| 3 | London | 17 |
| 4 | New York | 9 |
| 5 | Los Angeles | 6 |
| 6 | Alexandria | 5 |
| 7 | Paris | 5 |
| 8 | New Orleans | 3 |
| 9 | Stockholm | 3 |
| 10 | Beckenried | **3** ← HQ Base Camp + Sylvie + ? |

**Take:** Trapani leads (the Tribe is real). London + NY + LA show the seeded historical legends. Beckenried at 3 is you + Sylvie + one more — who's the third?

---

## 5. Users by badge tier

| Tier | Users |
|---|---|
| LEGEND | **273** |
| NEWCOMER | 31 |
| TRUSTED | 23 |
| ACTIVE | 15 |
| PILLAR | **10** ← apex |

**Take on tier system reality:** the live badge taxonomy is `NEWCOMER / ACTIVE / TRUSTED / LEGEND / PILLAR`, not the `Newcomer/Apprentice/Master/Legend` I sketched in the spec. **The spec needs updating to match prod reality.** PILLAR is the apex (10 users), LEGEND is the populous mid-high tier (273). Tomorrow's bombshell should redraw the tier-light palette around the real names.

---

## 6. Locandina coverage — the money number

```
Active listings:    883
  has photo:        883  (100.0%)
  has description:  882   (99.9%)
  CARD-READY:       882   (99.9%)
```

**Take:** **99.9% of active listings can render a non-empty Locandina TODAY.** When we merge `feat/locandina` to main and deploy, almost every existing listing is immediately printable. Zero data work needed. The feature lights up the entire catalog at once.

---

## 7. Top 10 most-viewed items (prod, 30 days)

| # | Name | Views |
|---|---|---|
| 1 | Custom Photography Project — Let's Collaborate! | 109 |
| 2 | Pentax p30t Film Camera — Great for Beginners! | 102 |
| 3 | Masonry Work & Flagstone Walks — Local Landscaper | 101 |
| 4 | Reliable Handyman for All Your Home Projects | 73 |
| 5 | Dancing in Heels Workshop — Grace Under Pressure | 69 |
| 6 | Acrobatics Fundamentals — Flips, Rolls, and Wall Runs | 69 |
| 7 | Marsala Wine Tour | 67 |
| 8 | One-day Dolomites guiding — for the serious | 67 |
| 9 | Single Combat Workshop — The Duel | 67 |
| 10 | Koflach expedition boots — size 42 | 67 |

**Take:** Photography + masonry + film cameras + handyman + dance + wine tour + Dolomites + sword combat + boots. The marketplace is finding real interest across **skill, gear, hospitality, and adventure**. This is the demand signal the marketing copy already implied.

---

## 8. Recent listings — last 7 days

| Date | Type | Name |
|---|---|---|
| Jun 03 | TRAINING | Learn Event Planning — Online Training! |
| Jun 03 | EVENT | Learn Event Planning — Online Training! |
| Jun 03 | TRAINING | Learn La Piazza: Telegram Training Sessions ← Angel today |
| Jun 03 | EVENT | Learn La Piazza: Telegram Training Sessions ← Angel today |
| May 29 | SELL | SOPs & AI Configuration Guide for HelixNet |

**Take:** Quiet week. Angel's two listings (today) + two others (today + May 29). New listings are NOT the bottleneck; **engagement on existing listings** is where the volume lives.

---

## 9. Sample workshops — 5 random picks

| Name | Workshop | City | Tier |
|---|---|---|---|
| Blaise Pascal | Pascal's Calculator Shop | Clermont-Ferrand | PILLAR |
| Sylvken Thiel | SylvKen's World | Beckenried | ACTIVE |
| Rembrandt Harmenszoon van Rijn | Rembrandt's Light Studio | Leiden | LEGEND |
| Sitting Bull | Sitting Bull's Sacred Lodge | Mobridge | LEGEND |
| Steven Paul Jobs | The Garage | Cupertino | LEGEND |

**Take:** **Sylvken Thiel in Beckenried, ACTIVE tier, workshop "SylvKen's World".** That's almost certainly Sylvie's account on prod. She's already a member. The first non-Angel real user is in the household.

---

## 10. Items by view-band — where attention lives

```
0 views (dark)    47 items  ▏
1-10 views        14 items  ▏
11-50 views      758 items  █████████████████████████████ 86%
51-100 views      88 items  ███ 10%
100+ views (hot)   3 items  · <1%
```

**Take:** 86% of items get 11-50 views in a month. That's the long tail working. Only 3 items break 100 views (photography, Pentax, masonry — the hits). **47 dark items** is the cleanup opportunity: items with zero traffic could be re-promoted via Locandinas printed and handed out.

---

## Closing notes for the morning bombshell

1. **Update tier-light palette** in `docs/specs/locandina-bauhaus-banksy-spec.md` to use real names: `NEWCOMER / ACTIVE / TRUSTED / LEGEND / PILLAR`. PILLAR gets the heritage gold; LEGEND gets the indigo-master treatment.
2. **Sylvken Thiel exists on prod.** First non-Angel real user is in the room. Print her bio postcard early; ask her to use it.
3. **The 33k views are concentrated in the 11-50 band.** Items aren't going dark, they're going slow. Locandinas printed and pinned in physical spaces (Caffè Maltese, Camper & Tour, Color Clean) could be the catalyst to flip 758 medium items into 100+ items.
4. **TRAINING is the dominant listing type (47%)**, not EVENT (<1%). The Locandina being "born as an event flyer" was a starting point; its real job is training-session announcement.
5. **99.9% of active listings can render a card RIGHT NOW.** When `feat/locandina` merges, every owner has a printable artifact instantly. Zero migration. Just turn it on.

---

*End of stock-take. Cold drink earned.*
