# BorrowHood Video Production SOP

Standard Operating Procedure for creating walkthrough/demo videos.

---

## 1. Folder Structure

Every video gets its own numbered folder inside `Bro_Kit/`. Everything for that video lives in that folder -- script, raw footage, final video, thumbnail, YouTube kit. One folder, one video, zero guessing.

```
BorrowHood/Bro_Kit/
├── NN-descriptive-name/
│   ├── record-XXXXX.js           ← Puppeteer recording script
│   ├── XXXXX-silent.mp4          ← Trimmed raw footage (audio stripped)
│   ├── XXXXX-FINAL.mp4           ← Final video with Brotherhood Run
│   └── youtube-kit/
│       ├── YOUTUBE-METADATA.md   ← Title, description, tags, chapters, category
│       ├── description.txt       ← Ready-to-paste YouTube description
│       ├── tags.txt              ← Ready-to-paste comma-separated tags
│       ├── thumbnail.html        ← Thumbnail source (1280x720 HTML)
│       ├── thumbnail.png         ← High quality render (Puppeteer screenshot)
│       └── thumbnail.jpg         ← YouTube upload size (ffmpeg converted)
```

**Naming convention:**
- Folder: `NN-lowercase-hyphenated-name/` (e.g., `07-walk-though-happy-flow/`)
- Script: `record-descriptive-name.js`
- Silent video: `descriptive-name-silent.mp4`
- Final video: `Descriptive-Name-FINAL.mp4`

**RULE: Everything in the folder from day one.** Never create artifacts in a temp location and move them later. Create the numbered folder first, then build everything directly inside it. If you open the folder and it looks empty or incomplete, something went wrong.

---

## 2. Pre-Package Before Recording

Before the operator hits record, the folder should already contain everything that does NOT depend on raw footage. This speeds up the end-to-end pipeline because post-production only needs to add the video files and update chapter timestamps.

**Create BEFORE recording:**
- [ ] Numbered folder (`NN-descriptive-name/`)
- [ ] `youtube-kit/` subfolder
- [ ] Recording script (`record-XXXXX.js`) in the folder
- [ ] `YOUTUBE-METADATA.md` (chapters use `0:XX` placeholders, updated after recording)
- [ ] `description.txt` (ready to paste)
- [ ] `tags.txt` (ready to paste)
- [ ] `thumbnail.html` (designed and coded)
- [ ] `thumbnail.png` + `thumbnail.jpg` (rendered via Puppeteer)
- [ ] Script deployed to Hetzner
- [ ] DB cleanup SQL run

**Create AFTER recording (post-production only):**
- [ ] `XXXXX-silent.mp4` (trimmed raw footage)
- [ ] `XXXXX-FINAL.mp4` (final with Brotherhood Run)
- [ ] Update chapter timestamps in YOUTUBE-METADATA.md (from frame analysis)

This means when Angel finishes recording, we only need to trim, add music, and update timestamps. Everything else is already done and waiting in the folder.

---

## 3. Mobile Optimization (All Videos)

Most viewers watch on phones. Every video must be readable on a 6-inch screen without squinting.

### 3.1 Story Cards / Title Cards -- Double Font Size

Standard card text is too small on mobile. Use these minimums:

| Element | Desktop (old) | Mobile-optimized (new) |
|---------|---------------|----------------------|
| Heading | 48-64px | **96-128px** |
| Subtitle | 24-32px | **48-64px** |
| Extra text | 18-24px | **36-48px** |
| Badge text | 14-18px | **28-36px** |

In the `card()` and `storyCard()` functions, double all font sizes. Text should fill the card -- no wasted whitespace.

### 3.2 Browser Zoom for UI Demos

Set Puppeteer browser zoom to **150%** for all UI interaction scenes. This makes buttons, text, form fields, and status badges large enough to read on a phone.

```javascript
// Add after page.goto() for any UI page (not cards)
await page.evaluate(() => { document.body.style.zoom = '1.5'; });
```

- Cards (data: URLs) stay at 100% -- they already have large text
- UI pages (browse, dashboard, item detail) use 150% zoom
- If critical elements are cut off at 150%, drop to 125% for that scene

### 3.3 Click Ring Size

Increase the red click ring for mobile visibility:

| Property | Old | New |
|----------|-----|-----|
| Ring border | 3px | **5px** |
| Ring diameter | 40px | **60px** |
| Glow spread | 10px | **20px** |

Update `injectClickStyle()` in every recording script.

### 3.4 Cursor Size

Inject a larger custom cursor so viewers can track mouse movement on small screens:

```javascript
await page.evaluate(() => {
  const style = document.createElement('style');
  style.textContent = `* { cursor: url('data:image/svg+xml,...') 16 16, auto !important; }`;
  document.head.appendChild(style);
});
```

Use a 32x32 bright white arrow with dark outline (visible on both light and dark backgrounds).

### 3.5 Pacing

Add **2 extra seconds** of pause after each click on UI pages. Phone viewers need time to process what just happened before the next action. Story cards already have 5-8s which is fine.

---

## 4. Recording Script Rules

### 4.1 Self-Contained

Each script is self-contained. Copy all utility functions into the script -- no shared imports. This means any script can run standalone on Hetzner without dependencies beyond Puppeteer.

### 4.2 Required Utilities (copy from previous script)

```
waitForEnter()      -- OBS sync prompt (ENTER to continue)
sleep()             -- timing pauses
card()              -- colored title card (data: URL)
storyCard()         -- title card with detail text
injectClickStyle()  -- inject red ring CSS
showRing()          -- show red ring at click point
findButton()        -- find visible button by text
clickEl()           -- move cursor + ring + click
clickButton()       -- findButton + clickEl shorthand
apiCall()           -- browser fetch (non-throwing, returns error object)
apiCallStrict()     -- browser fetch (throws on error)
ensureOnSite()      -- navigate away from data: URLs
kcLogin()           -- Keycloak login
kcLogout()          -- Keycloak logout
showDashboard()     -- navigate to dashboard + click tab
highlightRental()   -- scroll to + highlight rental card
waitForImages()     -- wait for all images to load
getListingId()      -- extract listing ID from item detail page
createRentalViaAPI() -- create rental via API helper
```

### 4.3 Click Highlights -- MANDATORY

Every click must show the red ring animation. Use `clickButton()` or `clickEl()` for all interactive elements. Never use raw `page.click()` without `showRing()`. The viewer needs to see exactly what was clicked, in what order.

### 4.4 Scene Structure

```javascript
// Scene 1 is ALWAYS the OBS CHECK (red card, wait for ENTER)
// Scene 2 is ALWAYS the INTRO (dark card, 8-10s)
// Last scene is ALWAYS the OUTRO (dark card, 8-10s)
// Final card: CUT (stop OBS recording, wait for ENTER)
```

Story cards between scenarios use the scenario's color. Each scenario gets a distinct color.

### 4.5 API Fallbacks

UI button clicks can fail (modal doesn't close, button not found). Always have an API fallback:

```javascript
const clicked = await clickButton(page, 'Approve');
if (clicked) {
  await page.waitForNavigation(...).catch(() => {});
} else {
  console.log('    Button not found, using API...');
  await apiCallStrict(page, 'PATCH', `/api/v1/rentals/${id}/status`, { status: 'approved' });
}
```

### 4.6 Pre-Recording Cleanup SQL

Include in script header comment. Always clean stale data before recording:

```sql
DELETE FROM bh_dispute WHERE rental_id IN
  (SELECT id FROM bh_rental WHERE status NOT IN ('COMPLETED','DECLINED','CANCELLED'));
DELETE FROM bh_lockbox_access WHERE rental_id IN
  (SELECT id FROM bh_rental WHERE status NOT IN ('COMPLETED','DECLINED','CANCELLED'));
DELETE FROM bh_rental WHERE status NOT IN ('COMPLETED','DECLINED','CANCELLED');
```

---

## 5. Recording

### 5.1 Pre-Flight

1. Deploy script to Hetzner: `scp script.js root@46.62.138.218:/opt/helixnet/BorrowHood/Bro_Kit/scripts/`
2. Run cleanup SQL on Hetzner DB
3. Open OBS on local machine
4. Set OBS to Screen Capture (NOT Window Capture)
5. Run script: `node record-XXXXX.js`
6. RED OBS CHECK card appears -- confirm OBS preview shows the red screen
7. Press ENTER to start recording

### 5.2 During Recording

- Script runs automatically. Don't touch the mouse (Puppeteer controls the cursor)
- Watch for errors in terminal
- Each scene logs to console: `Scene N: Description`

### 5.3 Post-Flight -- MANDATORY

- Play 10 seconds of raw recording IMMEDIATELY
- Verify it shows browser content, NOT desktop
- If wrong, re-record (don't try to salvage bad footage)

---

## 6. Post-Production Pipeline

### 6.1 Trim Raw Footage

Angel provides raw footage path + start/end timestamps.

```bash
ffmpeg -i "raw-obs-recording.mp4" -ss START -to END \
  -an -c:v libx264 -crf 18 \
  XXXXX-silent.mp4
```

- `-an` strips ambient audio (laptop mic, room noise)
- `-c:v libx264 -crf 18` re-encodes for precision trim (NOT `-c:v copy` which cuts at keyframes only)
- Always re-encode when trimming. `-c:v copy` lost the intro card on Video 1.

### 6.2 Background Music

**Track: Brotherhood Run** -- always. No exceptions.
**Volume: 30%** -- always. No exceptions.
**Location:** `BorrowHood/Bro_Kit/Archive/archive/Brotherhood Run.mp3` (209.9s / 3:30)

Loop if video is longer than 3:30. Fade in 3s at start, fade out 5s before end.

**CRITICAL: Brotherhood Run has ~1.8s silence at start and ~1.8s at end.** Using `-stream_loop` creates 3-4 seconds of dead air at each seam. Instead, trim the silence and crossfade the loops:

```bash
DURATION=$(ffprobe -v error -show_entries format=duration -of csv=p=0 XXXXX-silent.mp4)
FADE_OUT_START=$(echo "$DURATION - 5" | bc)

# Step 1: Trim silence from start/end of Brotherhood Run
ffmpeg -y -i "Brotherhood Run.mp3" -vn -ss 1.8 -to 208.2 -c:a pcm_s16le /tmp/br-trimmed.wav

# Step 2: Crossfade 2 copies (2s overlap, no gap)
ffmpeg -y -i /tmp/br-trimmed.wav -i /tmp/br-trimmed.wav \
  -filter_complex "[0][1]acrossfade=d=2:c1=tri:c2=tri[ab]" -map "[ab]" /tmp/br-2x.wav

# Step 3: Crossfade again for ~4 loops seamless (819s)
ffmpeg -y -i /tmp/br-2x.wav -i /tmp/br-2x.wav \
  -filter_complex "[0][1]acrossfade=d=2:c1=tri:c2=tri[out]" -map "[out]" /tmp/br-4x.wav

# Step 4: Apply volume, fades, trim to video length
ffmpeg -y -i /tmp/br-4x.wav \
  -af "volume=0.3,afade=t=in:d=3,afade=t=out:st=${FADE_OUT_START}:d=5" \
  -t $DURATION -c:a aac -b:a 128k -ar 48000 music-loop.m4a
```

**Important:** Brotherhood Run mp3 has embedded cover art. Add `-vn` to strip the video stream, otherwise ffmpeg throws "Could not find tag for codec h264 in stream #0".

### 6.3 Merge Video + Audio

```bash
ffmpeg -i XXXXX-silent.mp4 -i music-loop.m4a \
  -c:v copy -c:a aac -b:a 128k -ar 48000 \
  XXXXX-FINAL.mp4
```

- `-c:v copy` preserves video quality (no re-encode)
- `-ar 48000` forces 48kHz (loudnorm can silently upsample to 192kHz)

### 6.4 Verify Final Video

- Play the final video start to finish
- Confirm music volume is right (audible but not overpowering)
- Confirm fade in at start, fade out before outro
- Check file size is reasonable

---

## 7. Thumbnail

**Every video gets a thumbnail. No exceptions.**

### 7.1 Create HTML

- 1280x720px (YouTube recommended)
- Self-contained HTML file (no external images)
- High contrast, readable at small sizes
- No text smaller than 24px
- Match the video's color scheme
- Use the `frontend-design` skill for distinctive design

### 7.2 Render to Image

```javascript
// Puppeteer screenshot
const browser = await puppeteer.launch();
const page = await browser.newPage();
await page.setViewport({ width: 1280, height: 720, deviceScaleFactor: 2 });
await page.goto('file:///path/to/thumbnail.html');
await page.screenshot({ path: 'thumbnail.png', fullPage: false });
await browser.close();
```

### 7.3 Convert to JPG

```bash
ffmpeg -i thumbnail.png -q:v 2 thumbnail.jpg
```

JPG for YouTube upload (smaller file), PNG for high quality archive.

---

## 8. YouTube Kit

Every video needs a complete YouTube kit in `youtube-kit/`.

### 8.1 YOUTUBE-METADATA.md

Must include:
- Title (under 100 chars)
- Description (ready to paste, explain every step so a 5-year-old understands)
- Tags (comma-separated)
- Category (Science and Technology)
- Visibility (Public)
- Language (English)
- Chapters (timestamps from frame analysis)
- Thumbnail filename
- Subtitles filename (if applicable)
- Files list

### 8.2 description.txt

Ready-to-paste. No angled brackets (`<`, `>`). No `->` arrows. Max 5000 chars. Chapters must start at `0:00`.

### 8.3 tags.txt

Comma-separated, ready to paste into YouTube.

### 8.4 Chapter Timestamps

Analyze the final video frame by frame (5-second intervals) to map accurate chapter timestamps. Don't guess -- verify against actual footage.

---

## 9. Checklist

**PHASE 1 -- Pre-package (before recording):**
- [ ] Numbered folder created (`NN-descriptive-name/`)
- [ ] `youtube-kit/` subfolder created
- [ ] Recording script written and placed in folder
- [ ] YOUTUBE-METADATA.md written (chapter timestamps as `0:XX` placeholders)
- [ ] description.txt written (ready to paste)
- [ ] tags.txt written (ready to paste)
- [ ] Thumbnail HTML designed and placed in youtube-kit/
- [ ] Thumbnail rendered to PNG + JPG
- [ ] Script deployed to Hetzner via scp
- [ ] Cleanup SQL run on Hetzner DB
- [ ] OBS set to Screen Capture (not Window Capture)
- [ ] Script uses mobile-optimized font sizes (2x) in card() and storyCard()
- [ ] Script uses 150% browser zoom for UI pages
- [ ] Click ring size is 60px with 5px border
- [ ] **Folder check: open the folder, verify it has script + full youtube-kit**

**PHASE 2 -- Record:**
- [ ] Run script on Hetzner, OBS captures screen
- [ ] Raw footage verified immediately (play 10 seconds)
- [ ] Start/end timestamps noted
- [ ] Raw footage saved into the numbered folder

**PHASE 3 -- Post-production (only video files + timestamp update):**
- [ ] Video trimmed with re-encode (`-c:v libx264`, NOT `-c:v copy`)
- [ ] Audio stripped from trimmed video
- [ ] Brotherhood Run at 40% volume, looped, faded
- [ ] Video + music merged
- [ ] Final video verified (play start to finish)
- [ ] Chapter timestamps updated in YOUTUBE-METADATA.md (from frame analysis)
- [ ] Silent + FINAL mp4 files in the numbered folder
- [ ] **Final folder check: everything present, nothing in random locations**

**PHASE 4 -- Post-Take Review (before YouTube publish):**

After the final video is rendered but BEFORE publishing to YouTube, the team does a structured review. This catches bugs, recognizes wins, and feeds the backlog for the next episode.

- [ ] **Lessons Learned (LL) breakdown** -- What went right, what went wrong, what surprised us
- [ ] **Bug review** -- Any visual glitches, wrong data, UI issues spotted during playback
- [ ] **Script fixes logged** -- Hardcoded dates, wrong names, missing fallbacks found during recording
- [ ] **Backlog items logged** -- New features, fixes, and improvements identified (with BL-numbers)
- [ ] **Feature recognition** -- List what shipped this episode (new features built and visible on screen)
- [ ] **Next episode prep notes** -- What the next episode needs (story arcs, data setup, new characters)
- [ ] **Backlog priorities updated** -- Re-rank items based on what matters for the next episode

**Format:**
```
## EP[XX] Post-Take Review

### What shipped
- BL-077: In-app messaging (model + router + UI)
- BL-080: Listing Q&A (public questions on listings)
- ...

### What broke / got fixed
- Sally Thompson vs Baker name mismatch (fixed)
- Hardcoded dates expired (fixed, now dynamic)
- ...

### Lessons learned
1. Five features in one session is possible with parallel agents
2. Every new table needs a DELETE in the pre-recording cleanup SQL
3. ...

### Backlog for next episode
- BL-089: Rate limiting (HIGH)
- BL-095: Real domain + SSL (HIGH)
- ...
```

Save the review to: `Bro_Kit/NN-episode-name/POST-TAKE-REVIEW.md`

This is the team's sprint retrospective. No publishing without it.

---

## 10. Test Credentials

All test users across all realms: password is `helix_pass`

Seed users: sally, mike, angel, maria, nino

---

## 11. Hetzner Server

- IP: 46.62.138.218
- SSH: `ssh root@46.62.138.218`
- App path: `/opt/helixnet/`
- DB: `docker exec postgres psql -U helix_user -d borrowhood`
- SSH rate limiting: Do sequential SSH commands with pauses. Parallel scp + ssh will get refused.
