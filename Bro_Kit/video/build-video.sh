#!/bin/bash
#
# BorrowHood Demo Video Builder
# Screenshots -> scene clips -> concat -> add music -> final MP4
#
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
FRAMES="$DIR/frames"
TMP="$DIR/tmp"
MUSIC="$DIR/../Brotherhood Run.mp3"
OUTPUT="$DIR/borrowhood-demo.mp4"

mkdir -p "$TMP"

echo ""
echo "  BorrowHood Demo Video Builder"
echo "  ============================="
echo ""

# --- Scene definitions ---
# Format: filename | duration | overlay text
# NOTE: ffmpeg drawtext chokes on colons -- use dashes or avoid them
SCENES=(
  "01-hero.png|4|Every Garage Becomes a Rental Shop"
  "02-recently-listed.png|4|20+ Items with AI-Generated Images"
  "03-origin-story.png|4|Built from a Camper Van in Sicily"
  "04-browse-grid.png|4|Browse, Search, and Filter by Category"
  "05-browse-search.png|3|Smart Search with Language Badges"
  "06-item-detail-top.png|4|Rich Listings - Maps, Deposits, Lockbox"
  "07-item-detail-reviews.png|4|Weighted Reviews - Trust Scores"
  "08-workshop.png|4|Every User Gets a Workshop Storefront"
  "09-list-item.png|4|AI-Powered Listing + Image Generation"
  "10-onboarding.png|3|3-Step Onboarding with AI Bio Expand"
  "11-italian-home.png|3|Full Bilingual - English + Italian"
  "12-italian-browse.png|3|i18n Everywhere - Even Category Pills"
)

# --- Step 1: Create title card (4s) ---
echo "  [1/4] Creating title card..."
ffmpeg -y -loglevel error \
  -f lavfi -i "color=c=#6C3CE0:s=1920x1080:d=4,format=yuv420p" \
  -vf "drawtext=text='BorrowHood':fontsize=96:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2-60:font=Arial:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf,\
       drawtext=text='Every Garage Becomes a Rental Shop':fontsize=36:fontcolor=white@0.9:x=(w-text_w)/2:y=(h-text_h)/2+40:font=Arial,\
       drawtext=text='DEV Weekend Challenge 2026':fontsize=24:fontcolor=white@0.7:x=(w-text_w)/2:y=(h-text_h)/2+100:font=Arial" \
  -c:v libx264 -r 30 -t 4 "$TMP/00-title.mp4"
echo "  00-title.mp4               Title card... OK"

# --- Step 2: Create scene clips with text overlays ---
echo "  [2/4] Creating scene clips..."
i=1
for scene in "${SCENES[@]}"; do
  IFS='|' read -r file duration text <<< "$scene"
  padded=$(printf "%02d" $i)
  outfile="$TMP/${padded}-scene.mp4"

  printf "  %-30s %s... " "$file" "$text"

  ffmpeg -y -loglevel error \
    -loop 1 -i "$FRAMES/$file" \
    -t "$duration" \
    -vf "scale=1920:1080,format=yuv420p,\
         drawbox=y=ih-70:w=iw:h=70:color=black@0.55:t=fill,\
         drawtext=text='${text}':fontsize=28:fontcolor=white:x=(w-text_w)/2:y=h-48:font=Arial" \
    -c:v libx264 -preset fast -crf 18 -r 30 \
    "$outfile"

  echo "OK (${duration}s)"
  i=$((i+1))
done

# --- Step 3: Create end card (5s) ---
echo ""
echo "  [3/4] Creating end card..."
ffmpeg -y -loglevel error \
  -f lavfi -i "color=c=#6C3CE0:s=1920x1080:d=5,format=yuv420p" \
  -vf "drawtext=text='BorrowHood':fontsize=72:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2-80:font=Arial:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf,\
       drawtext=text='250 Tests -- 14 Badges -- Lockbox Exchange':fontsize=28:fontcolor=white@0.9:x=(w-text_w)/2:y=(h-text_h)/2:font=Arial,\
       drawtext=text='FastAPI + Alpine.js + Keycloak + Tailwind':fontsize=24:fontcolor=white@0.7:x=(w-text_w)/2:y=(h-text_h)/2+50:font=Arial,\
       drawtext=text='github.com/akenel/borrowhood':fontsize=28:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2+110:font=Arial" \
  -c:v libx264 -r 30 -t 5 "$TMP/99-end.mp4"
echo "  99-end.mp4                 End card... OK"

# --- Step 4: Concat all clips + add music ---
echo ""
echo "  [4/4] Stitching video + adding music..."

# Build concat list
CONCAT_LIST="$TMP/concat.txt"
echo "file '$(realpath "$TMP/00-title.mp4")'" > "$CONCAT_LIST"
for j in $(seq -w 1 ${#SCENES[@]}); do
  echo "file '$(realpath "$TMP/${j}-scene.mp4")'" >> "$CONCAT_LIST"
done
echo "file '$(realpath "$TMP/99-end.mp4")'" >> "$CONCAT_LIST"

echo "  Concat list:"
cat "$CONCAT_LIST" | while read line; do
  echo "    $line"
done

# Concat video (no audio yet)
ffmpeg -y -loglevel error \
  -f concat -safe 0 -i "$CONCAT_LIST" \
  -c:v libx264 -preset fast -crf 18 -r 30 \
  "$TMP/video-silent.mp4"

# Get video duration
VDUR=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$TMP/video-silent.mp4")
echo "  Video duration: ${VDUR}s"

# Add music: fade in 1s, fade out 3s before end
FADE_OUT_START=$(echo "$VDUR - 3" | bc)
ffmpeg -y -loglevel error \
  -i "$TMP/video-silent.mp4" \
  -i "$MUSIC" \
  -filter_complex "[1:a]atrim=0:${VDUR},afade=t=in:st=0:d=1.5,afade=t=out:st=${FADE_OUT_START}:d=3,volume=0.4[music]; \
                   [music]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[aout]" \
  -map 0:v -map "[aout]" \
  -c:v copy -c:a aac -b:a 192k -ar 48000 \
  -shortest \
  "$OUTPUT"

# Final stats
FSIZE=$(du -h "$OUTPUT" | cut -f1)
echo ""
echo "  OUTPUT: $OUTPUT"
echo "  Size:   $FSIZE"
echo "  Duration: ${VDUR}s"
echo ""
echo "  Done. Play it: mpv '$OUTPUT'"
echo ""

# Cleanup tmp
# rm -rf "$TMP"
