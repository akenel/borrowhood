# CLAUDE.md -- BorrowHood Bro_Kit (Video Production)

This file loads when working in the Bro_Kit directory. Follow these rules for every video session.

---

## The Rules (Non-Negotiable)

1. **Brotherhood Run at 30% volume** -- every video, no exceptions. Source: `Archive/archive/Brotherhood Run.mp3` (209.9s / 3:30). Loop if video is longer. Fade in 3s, fade out 5s.

2. **Every video gets a thumbnail** -- 1280x720 HTML, rendered to PNG + JPG via Puppeteer. High contrast, readable at small sizes.

3. **Every click shows a red ring** -- use `clickButton()` or `clickEl()` with `showRing()`. Never raw `page.click()`. Viewers need to see exactly what was clicked and in what order.

4. **One video at a time, end to end** -- don't start video N+1 until video N has its final MP4, thumbnail, and complete YouTube kit.

5. **Everything in its numbered folder from day one** -- script, youtube-kit, thumbnail all go DIRECTLY into the folder when created. Never make artifacts in a temp location and move them later. When Angel opens the folder before recording, it should already have the script + complete youtube-kit (everything except the video files).

6. **Pre-package before recording** -- create the folder, write the script, write the YouTube kit (metadata, description, tags), design and render the thumbnail -- all BEFORE the operator presses record. This means after recording, only 3 things remain: trim the video, add Brotherhood Run, update chapter timestamps. Angel also gets a ready folder to drop raw footage into.

7. **Re-encode when trimming** -- use `-c:v libx264 -crf 18`, NOT `-c:v copy`. Copy mode cuts at keyframes and loses intro cards.

8. **Strip the `-vn` flag on Brotherhood Run** -- the MP3 has embedded cover art that breaks ffmpeg's container detection.

9. **OBS uses Screen Capture** -- not Window Capture. Window Capture has captured the wrong window twice.

10. **Play 10 seconds immediately after recording** -- verify it shows browser content, not desktop. Non-negotiable post-flight check.

11. **No angled brackets in YouTube descriptions** -- YouTube strips `<` and `>`. No `->` arrows either.

12. **Chapters go IN the description.txt** -- YouTube reads chapters directly from the description text. Always include the full timestamp list in `description.txt` (not just in YOUTUBE-METADATA.md). First timestamp must be `0:00`, minimum 3 chapters, minimum 10s between each. One file to paste, done.

13. **Mobile-first text sizes** -- Most viewers watch on phones. Double all card font sizes (headings 96-128px, subtitles 48-64px, body 36-48px). Set browser zoom to 150% for UI demo pages (`document.body.style.zoom = '1.5'`). Bigger click rings (60px diameter, 5px border). Extra 2s pause after each UI click.

---

## Folder Convention

```
Bro_Kit/
├── NN-descriptive-name/          ← One folder per video
│   ├── record-XXXXX.js           ← Self-contained Puppeteer script
│   ├── XXXXX-silent.mp4          ← Trimmed, audio stripped
│   ├── XXXXX-FINAL.mp4           ← Final with Brotherhood Run
│   └── youtube-kit/
│       ├── YOUTUBE-METADATA.md
│       ├── description.txt
│       ├── tags.txt
│       ├── thumbnail.html
│       ├── thumbnail.png
│       └── thumbnail.jpg
├── Archive/                      ← Music, assets
├── scripts/                      ← Shared scripts (build-video.sh, etc.)
├── sop/                          ← VIDEO-PRODUCTION-SOP.md
└── CLAUDE.md                     ← This file
```

---

## Post-Production Pipeline (Quick Reference)

```bash
# 1. Trim raw footage (re-encode, strip audio)
ffmpeg -i raw.mp4 -ss START -to END -an -c:v libx264 -crf 18 XXXXX-silent.mp4

# 2. Loop Brotherhood Run at 40%, fade in/out
DURATION=$(ffprobe -v error -show_entries format=duration -of csv=p=0 XXXXX-silent.mp4)
FADE_OUT=$(echo "$DURATION - 5" | bc)
ffmpeg -stream_loop -1 -i "Archive/archive/Brotherhood Run.mp3" \
  -vn -af "volume=0.4,afade=t=in:d=3,afade=t=out:st=${FADE_OUT}:d=5" \
  -t $DURATION music-loop.m4a

# 3. Merge
ffmpeg -i XXXXX-silent.mp4 -i music-loop.m4a -c:v copy -c:a aac -b:a 128k -ar 48000 XXXXX-FINAL.mp4

# 4. Thumbnail
# Create thumbnail.html (1280x720), render with Puppeteer, convert:
ffmpeg -i thumbnail.png -q:v 2 thumbnail.jpg
```

---

## Hetzner Deployment

```bash
# Deploy script
scp record-XXXXX.js root@46.62.138.218:/opt/helixnet/BorrowHood/Bro_Kit/scripts/

# Clean stale data (ALWAYS run before recording)
ssh root@46.62.138.218 "docker exec postgres psql -U helix_user -d borrowhood -c \"
  DELETE FROM bh_dispute WHERE rental_id IN
    (SELECT id FROM bh_rental WHERE status NOT IN ('COMPLETED','DECLINED','CANCELLED'));
  DELETE FROM bh_lockbox_access WHERE rental_id IN
    (SELECT id FROM bh_rental WHERE status NOT IN ('COMPLETED','DECLINED','CANCELLED'));
  DELETE FROM bh_rental WHERE status NOT IN ('COMPLETED','DECLINED','CANCELLED');
\""

# Run on server
ssh root@46.62.138.218 "cd /opt/helixnet/BorrowHood/Bro_Kit/scripts && node record-XXXXX.js"
```

SSH rate limiting: sequential commands with pauses. Parallel scp + ssh gets refused.

---

## Test Credentials

All users: password `helix_pass`. Seed users: sally, mike, angel, maria, nino.

---

## Playlist

**"BorrowHood: The Garage Sessions"**

| # | Video | Folder | Status |
|---|-------|--------|--------|
| 1 | Happy Path Walkthrough | `07-walk-though-happy-flow/` | DONE |
| 2 | Edge Cases | `08-edge-cases-when-things-go-wrong/` | DONE |
| 3 | Community & Reputation | `09-community-and-reputation/` | DONE |
| 4 | The Auction | `10-the-auction/` | FINAL (2:49) |
| 5 | The Legends | `11-the-legends/` | FINAL (4:07) |
| 6 | The Italian Job | `12-the-italian-job/` | PRE-PACKAGED |
| 7 | The Giveaway | `13-the-giveaway/` | FINAL (2:36) |
| 8 | The Workshop | `14-the-workshop/` | FINAL (2:19) |
| 9 | The Crash | `15-the-crash/` | FINAL (EP1 PUBLISHED) |
| 10 | The Cookie Run | `16-the-cookie-run/` | FINAL (11:08, EP2 PUBLISHED) |

---

## Full SOP

See `sop/VIDEO-PRODUCTION-SOP.md` for the complete step-by-step procedure.
