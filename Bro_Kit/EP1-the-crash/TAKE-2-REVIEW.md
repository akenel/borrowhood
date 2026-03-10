# EP15 "The Crash" -- Take 2 Review Report

**Video:** `the crash take 2 -- RAW -- OBS_2026-03-04 18-20-11.mp4`
**Duration:** 6:06 (366s) | **Resolution:** 1920x1080
**Reviewed:** 73 frames at 5s intervals + voice recording transcript

---

## VERDICT: Good bones, needs major pacing expansion for Take 3

The story works. The features work. The problem is speed -- a viewer watching
at 1x will miss most of what's happening. For a 10-12 minute training video,
we need to roughly double the runtime by adding missing scenes, longer pauses,
and WHO IS LOGGED IN indicators throughout.

---

## FRAME-BY-FRAME FINDINGS

### Pre-Roll (0:00-0:15) -- TRIM NEEDED
| Time | Frame | Issue |
|------|-------|-------|
| 0:00-0:10 | sec_001-002 | VS Code terminal visible -- OBS started before browser was ready |
| 0:15 | sec_004 | OBS CHECK card showing but VS Code terminal ALSO visible behind it |

**Fix:** Trim raw footage to start at THE CRASH intro card (~0:25). The OBS CHECK
card at sec_004 has split-screen contamination (VS Code terminal visible alongside).

### Act 1: The Drone Rental (~0:25-3:20)

| Time | Frame | What Shows | Issue |
|------|-------|-----------|-------|
| 0:25-0:30 | sec_005-006 | THE CRASH intro card | Good -- clean, readable |
| 0:35-0:40 | sec_007-008 | PIETRO FERRETTI character card | Good content but **no login screen shown** |
| 0:45-0:50 | sec_009-010 | Pietro's workshop page (SkyView Sicilia) | Good -- Trusted badge, reputation visible |
| 0:55 | sec_011 | Skills + 170 reputation points | Good |
| 1:00 | sec_012 | Items section shows **3 items, not 4** | Script says "4 drones to rent" but only 3 visible |
| 1:05-1:10 | sec_013-014 | SALLY THOMPSON character card | Good but **no login transition shown** |
| 1:15-1:20 | sec_015-016 | DJI Mini 4 Pro listing (Sally logged in - nav shows "sally") | **Goes too fast** -- viewer barely registers who is logged in |
| 1:25 | sec_017 | Listing scrolled to description | Barely visible before next action |
| 1:30 | sec_018 | Rental Request modal -- message being typed | **DATES ARE EMPTY** (dd/mm/yyyy placeholders) |
| 1:35-1:40 | sec_019-020 | Modal still open, message filled | Dates STILL empty -- no dates picked |
| 1:45 | sec_021 | DEPOSIT HELD overlay | **Way too fast after request** -- no Send button click visible, no notification toast |
| 1:50 | sec_022 | DEPOSIT HELD still showing | Card text is good |
| 1:55 | sec_023 | Sally's Dashboard -- My Items tab | **Why My Items?** Should show My Rentals to see the new rental |
| 2:00 | sec_024 | PICKUP DAY overlay | Good card content |
| 2:10 | sec_026 | THE RETURN overlay | Good -- damage details clear |
| 2:20 | sec_028 | Overlay fading, dashboard visible | Transition OK |

**Critical Issues in Act 1:**
1. **No login screens shown** -- viewers don't know who is operating
2. **Dates empty in rental form** -- the most important part of a rental request
3. **No Send Request click or notification** -- jump straight to DEPOSIT HELD
4. **3 items vs 4 drones** -- script text doesn't match seed data
5. **No favorites shown** -- Sally should favorite the member and/or item
6. **Too fast** -- entire rental sequence (browse, request, deposit) in ~20 seconds

### Act 1: Dispute + Resolution (~2:25-3:25)

| Time | Frame | What Shows | Issue |
|------|-------|-----------|-------|
| 2:25 | sec_029 | Sally's Dashboard (clean) | Brief pause |
| 2:30 | sec_030 | PIETRO FILES A DISPUTE overlay | Good -- reason + evidence clear |
| 2:40 | sec_032 | Dashboard zoomed out | Browser zoom changed (inconsistent) |
| 2:45 | sec_033 | My Rentals tab -- all Completed (old rentals) | **No drone rental visible!** Should show DISPUTED status |
| 2:50 | sec_034 | Incoming Requests tab -- old completed items | Not relevant to current story |
| 2:55 | sec_035 | Dashboard My Items (zoomed out) | Why showing this? |
| 3:00 | sec_036 | SALLY'S REBUTTAL overlay | Good text + fairness message |
| 3:10 | sec_038 | Dashboard back to My Items | Brief pause |
| 3:15-3:20 | sec_039-040 | THE RESOLUTION overlay | Good -- EUR 70/30 split explained clearly |
| 3:25 | sec_041 | Resolution still showing | Good hold time |

**Issues in Dispute Section:**
1. **No actual dispute UI shown** -- just overlay cards explaining what happened
2. **No rental with DISPUTED status visible** -- My Rentals shows only old completed items
3. **Dashboard tabs seem random** -- jumping between My Items, My Rentals, Incoming Requests without clear purpose
4. **Browser zoom inconsistent** -- changes between sections

### Act 1: Deposit Outcome (~3:30-3:45)

| Time | Frame | What Shows | Issue |
|------|-------|-----------|-------|
| 3:30 | sec_042 | Sally's Dashboard (clean) | |
| 3:35 | sec_043 | My Rentals -- click ring visible on Garden Hose | Red ring visible -- good |
| 3:40 | sec_044 | My Rentals (same view) | |
| 3:45 | sec_045 | DEPOSIT OUTCOME overlay | Good -- EUR 70 to Pietro, EUR 30 to Sally, PARTIAL RELEASE |

**This section is actually OK** -- the DEPOSIT OUTCOME card is clear and well-written.

### Act 2: The Clean Exit (~3:50-5:05)

| Time | Frame | What Shows | Issue |
|------|-------|-----------|-------|
| 3:50 | sec_046-047 | THE CLEAN EXIT intro card (red background) | Good -- sets up Act 2 clearly |
| 4:00 | sec_048 | Sally's Dashboard -- My Items | Brief view |
| 4:05 | sec_049 | Settings tab -- Telegram + Danger Zone | Good -- both cards visible |
| 4:10 | sec_050 | Settings scrolled -- Danger Zone prominent | Good |
| 4:15 | sec_051 | Confirm dialog: "Are you sure?" | Good -- browser native confirm |
| 4:20 | sec_052 | 409 error toast: "1 active service quote(s)" | Safety gate WORKS |
| 4:25 | sec_053 | **TWO error toasts stacked** | BUG: Delete button clicked twice? |
| 4:30 | sec_054 | **THREE notifications** -- banner + 2 toasts | Too many -- clicked too many times |
| 4:35-4:40 | sec_055-056 | RESOLVE FIRST overlay | Good card -- explains the blocker |
| 4:45 | sec_057 | Settings page -- toasts still visible | Toast stacking is messy |
| 4:50 | sec_058 | "Service quote cancelled." green toast | Good -- shows resolution |
| 4:55 | sec_059 | Settings -- clean view, ready to delete again | |
| 5:00 | sec_060 | Danger Zone scrolled into view | |
| 5:05 | sec_061 | Confirm dialog again | |

**Issues in Act 2 (Clean Exit):**
1. **Delete button clicked multiple times** -- sec_053-054 show 2-3 stacked error toasts
2. **No overlay card explaining "Now Sally goes to Settings"** -- jump is too abrupt
3. **No "Logged in as: Sally" indicator** before deletion attempt

### Act 2: The Deletion + Aftermath (~5:05-6:05)

| Time | Frame | What Shows | Issue |
|------|-------|-----------|-------|
| 5:10 | sec_062 | Home page -- BorrowHood hero | Redirected after deletion |
| 5:15 | sec_063 | Home page with "Account deleted. Goodbye, Sally." toast | Good toast message |
| 5:20 | sec_064 | Home page (toast faded) | **Nav still shows "sally" + "Log Out"** -- NOT LOGGED OUT |
| 5:25-5:30 | sec_065-066 | GONE overlay | Good card -- lists all cleanup actions |
| 5:35 | sec_067 | Members directory | |
| 5:40 | sec_068 | Members search -- "Sally" typed | Good -- proving she's gone |
| 5:45 | sec_069 | NOT FOUND overlay | Good -- "WHERE deleted_at IS NULL" shown |
| 5:50-6:05 | sec_070-073 | FEATURE COMPLETE card | Good ending card |

**Critical Issues in Aftermath:**
1. **Sally is NOT logged out** -- sec_063-064 clearly show "sally" in nav and "Log Out" link after deletion. She should be logged out with nav showing "Log In" instead.
2. **No search results shown** -- we see the search typed but not the actual filtered results (no Sally in list) before the overlay covers it
3. **Missing: Browse items to confirm her listings are paused/gone**

---

## BUG LIST (Code Fixes Needed)

| # | Severity | Description |
|---|----------|-------------|
| B1 | HIGH | **Sally not logged out after account deletion** -- DELETE /api/v1/users/me response should clear session cookie. Client JS should delete `bh_token` cookie and redirect. Nav still shows "sally" at sec_063-064. |
| B2 | MEDIUM | **Multiple error toasts stacking** -- Delete button clickable while request is in-flight. Add `deleting: true` loading state to disable button during API call. |
| B3 | LOW | **Item count mismatch** -- Script/overlay says "4 drones" but Pietro has 3 drone items in seed data. Either fix the text or add a 4th drone to seeds. |

---

## PACING ISSUES (Script Fixes for Take 3)

| # | Issue | Current | Target |
|---|-------|---------|--------|
| P1 | No login screens | 0s | Show Keycloak login for both Pietro and Sally (~15s each) |
| P2 | No favorites | 0s | Sally favorites Pietro as member + favorites the drone listing (~20s) |
| P3 | Rental dates empty | 0s | Pick start/end dates in the date picker (~15s) |
| P4 | No Send Request click | 0s | Click Send, show success toast, pause on it (~10s) |
| P5 | No rental status visible | 0s | Show My Rentals with PENDING then APPROVED status (~15s) |
| P6 | Deposit held -- too fast | ~3s | Add a card explaining deposit hold, show deposit in UI (~10s) |
| P7 | No dispute UI | 0s | Show the actual dispute form being filled out (~20s) |
| P8 | No rebuttal UI | 0s | Show Sally's actual response form (~15s) |
| P9 | Resolution too fast | ~5s | Show the resolve dispute form with EUR amounts (~15s) |
| P10 | No "who is logged in" banners | 0s | Add banner overlay before each user's actions (~5s x 4) |
| P11 | Sally not logging out | Missing | Clear cookie, show login button, search anonymously |
| P12 | No Browse Items check | 0s | After deletion, browse items to confirm listings paused (~10s) |

**Estimated new runtime with fixes: ~10-12 minutes** (current 6:06 + ~5-6 minutes of new scenes)

---

## RECOMMENDED SCENE LIST FOR TAKE 3

### Pre-Roll
1. OBS CHECK card (trim before this)

### Act 1: The Drone Rental (target: ~5 minutes)
2. THE CRASH intro card (10s)
3. **MEET PIETRO** character card -- "Logged in as: Pietro Ferretti" (8s)
4. **Pietro logs in** -- show Keycloak login screen (15s)
5. Pietro's workshop page -- scroll slowly through profile, skills, reputation (20s)
6. Pietro's items -- scroll through 3 drones, pause on each (20s)
7. **MEET SALLY** character card -- "Sally wants to rent a drone" (8s)
8. **Sally logs in** -- show Keycloak login (15s)
9. Sally browses Members directory -- finds Pietro (10s)
10. **Sally favorites Pietro** -- click heart, show confirmation (8s)
11. Sally clicks into Pietro's workshop from member card (5s)
12. Sally browses to DJI Mini 4 Pro listing (10s)
13. **Sally favorites the listing** -- click heart (8s)
14. Sally reads listing details -- scroll slowly (15s)
15. **RENTAL REQUEST card** -- "Sally wants this drone for a weekend shoot" (8s)
16. Sally clicks "Rent This" -- modal opens (5s)
17. **Pick dates** -- select start and end dates (15s)
18. Type message to Pietro (10s)
19. **Click Send Request** -- show button click + success toast (8s)
20. **DEPOSIT HELD card** -- EUR 100 held, explain what this means (10s)
21. Show Sally's Dashboard > My Rentals -- rental PENDING status (10s)
22. **PIETRO APPROVES card** -- switch to Pietro's view (8s)
23. Show Pietro's Incoming Requests -- approve the rental (10s)
24. **PICKUP DAY card** (8s)
25. API call: mark as PICKED_UP (5s)
26. Show rental status change to PICKED_UP (5s)
27. **THE RETURN card** -- drone comes back damaged (10s)
28. API call: mark as RETURNED (5s)

### Act 1: The Dispute (target: ~3 minutes)
29. **PIETRO FILES A DISPUTE card** (10s)
30. Show Pietro logging in (or indicate he's logged in) (5s)
31. **Show dispute form** -- fill in reason, evidence, description (20s)
32. Submit dispute -- show success notification (5s)
33. Show rental status change to DISPUTED (5s)
34. **SALLY'S REBUTTAL card** (10s)
35. Show Sally logging in (or indicate) (5s)
36. **Show rebuttal form** -- Sally types her response (15s)
37. Submit -- status FILED to UNDER_REVIEW (5s)
38. **THE RESOLUTION card** (10s)
39. Show Pietro resolving -- partial deposit split form (15s)
40. **DEPOSIT OUTCOME card** -- EUR 70/30 breakdown (10s)
41. Show deposit status PARTIAL_RELEASE in UI (5s)

### Act 2: The Clean Exit (target: ~3 minutes)
42. **THE CLEAN EXIT intro card** (red, 10s)
43. **"Logged in as: Sally Thompson"** banner (5s)
44. Sally's Dashboard > Settings tab (8s)
45. Scroll to Danger Zone -- pause on it (5s)
46. **"SALLY TRIES TO LEAVE" card** (8s)
47. Click Delete Account -- confirm dialog (5s)
48. 409 blocked -- show toast (SINGLE toast, no double-click) (8s)
49. **RESOLVE FIRST card** (10s)
50. Sally cancels the service quote -- show the action (10s)
51. "Service quote cancelled" toast (5s)
52. **"NOW SHE CAN LEAVE" card** (8s)
53. Click Delete Account again -- confirm (5s)
54. **"Account deleted. Goodbye, Sally."** toast + redirect to home (8s)
55. **Verify: nav shows "Log In" not "sally"** (5s)
56. **GONE card** -- deleted_at, DEACTIVATED, PAUSED, audit log (10s)
57. Browse Members -- search "Sally" -- NOT FOUND (10s)
58. Browse Items -- Sally's listings gone from public view (10s)
59. **NOT FOUND card** -- "WHERE deleted_at IS NULL" (10s)
60. **FEATURE COMPLETE card** (15s)

**Estimated total: ~11 minutes**

---

## SUMMARY OF CHANGES NEEDED

### Code Fixes (before Take 3)
1. **Fix logout on deletion** -- `accountDelete()` in dashboard.html must clear `bh_token` cookie and reload page after successful DELETE
2. **Disable Delete button during API call** -- prevent double-click toast stacking
3. **Fix item count** -- either change overlay text from "4 drones" to "3 drones" or add 4th drone to seed data

### Script Rewrites (record-the-crash.js)
1. Add login scenes for both users
2. Add favorites workflow
3. Add date picker interaction
4. Add Send Request click + toast
5. Show rental status changes in UI (PENDING, APPROVED, PICKED_UP, RETURNED, DISPUTED)
6. Show actual dispute/rebuttal forms (not just overlay cards)
7. Add "Logged in as: USERNAME" banners before each user switch
8. Fix deletion to actually log out Sally
9. Add post-deletion browsing (Members + Items)
10. Slow everything down -- 10s minimum per card, 5s pauses between actions
11. Target 10-12 minutes total

---

*Report generated by Tigs after reviewing 73 frames + voice transcript.*
*"If one seal fails, check all the seals."*
