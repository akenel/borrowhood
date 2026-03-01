#!/bin/bash
#
# BorrowHood Demo Video Builder v2
# Ken Burns zoom + crossfade transitions + music
#
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
FRAMES="$DIR/frames"
TMP="$DIR/tmp"
MUSIC="$DIR/../Brotherhood Run.mp3"
OUTPUT="$DIR/borrowhood-demo.mp4"

rm -rf "$TMP"
mkdir -p "$TMP"

echo ""
echo "  BorrowHood Demo Video v2"
echo "  ========================"
echo "  Ken Burns + Crossfades + Brotherhood Run"
echo ""

# --- Configuration ---
XFADE_DUR=0.7          # crossfade duration in seconds
KB_ZOOM_RATE=0.0008    # zoom speed per frame (subtle)
KB_MAX_ZOOM=1.12       # max zoom factor
KB_SCALE=2048:1152     # overscan resolution for zoom headroom
FPS=30

# --- Scene definitions ---
# Format: filename | duration | overlay text | zoom_direction
# zoom_direction: center, left, right (pan direction during zoom)
#
# 5 Phases: Public > Login > Authenticated > Logout > Italian
SCENES=(
  # Phase 1: Public Pages
  "01-hero.png|4|28 Listings - 11 Members - 7 Categories|center"
  "02-recently-listed.png|3.5|20+ Items with AI-Generated Images|right"
  "04-browse-grid.png|4|Browse, Search, and Filter by Category|left"
  "05-browse-search.png|3.5|Smart Search with Language Badges|center"
  "06-item-detail-top.png|4.5|Rich Listings - Maps, Deposits, Lockbox|right"
  "07-item-reviews.png|3.5|Weighted Reviews and Trust Scores|left"
  "08-workshop.png|3.5|Every User Gets a Workshop Storefront|center"
  # Phase 2: Keycloak Login
  "09-keycloak-login.png|3.5|Keycloak OIDC - Real Enterprise Auth|right"
  "10-keycloak-filled.png|3|Login as Mike Kenel|left"
  "11-logged-in-home.png|3|Authenticated - Dashboard and Notifications|center"
  # Phase 3: Authenticated Flows
  "12-dashboard.png|4|Personal Dashboard with Items and Rentals|right"
  "13-dashboard-rentals.png|3.5|Incoming Rental Requests from Neighbors|left"
  "14-my-workshop.png|4|Workshop Profile - Pillar Badge Earned|center"
  "15-my-items.png|3.5|Skills, Languages, and CEFR Levels|right"
  "16-list-item-auth.png|4.5|AI Description and Image Generation|left"
  "17-onboarding.png|3.5|3-Step Onboarding Wizard|center"
  # Phase 4: Logout
  "18-logged-out.png|3|Clean Session Logout via Keycloak|right"
  # Phase 5: Italian
  "19-italian-home.png|3.5|Full Bilingual - English and Italian|left"
  "20-italian-browse.png|3.5|i18n Everywhere - Even Category Pills|center"
)

# --- Ken Burns zoom expressions per direction ---
# center: zoom into center
# left: zoom + pan left-to-center
# right: zoom + pan right-to-center
kb_expr() {
  local dir="$1"
  local dur_frames="$2"
  case "$dir" in
    center)
      echo "z='min(zoom+${KB_ZOOM_RATE},${KB_MAX_ZOOM})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
      ;;
    left)
      echo "z='min(zoom+${KB_ZOOM_RATE},${KB_MAX_ZOOM})':x='(iw/4)*(1-on/${dur_frames})':y='ih/2-(ih/zoom/2)'"
      ;;
    right)
      echo "z='min(zoom+${KB_ZOOM_RATE},${KB_MAX_ZOOM})':x='iw/2-(iw/zoom/2)+(iw/8)*(on/${dur_frames})':y='ih/2-(ih/zoom/2)'"
      ;;
  esac
}

# --- Step 1: Create title card with Ken Burns on gradient ---
echo "  [1/4] Title card..."
ffmpeg -y -loglevel error \
  -f lavfi -i "color=c=#4F46E5:s=1920x1080:d=4.5,format=yuv420p" \
  -vf "drawtext=text='BorrowHood':fontsize=100:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2-80:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf,\
       drawtext=text='Every Garage Becomes a Rental Shop':fontsize=34:fontcolor=white@0.85:x=(w-text_w)/2:y=(h-text_h)/2+40:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf,\
       drawtext=text='DEV Weekend Challenge 2026':fontsize=22:fontcolor=white@0.6:x=(w-text_w)/2:y=(h-text_h)/2+100:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf,\
       fade=t=in:st=0:d=1:alpha=0" \
  -c:v libx264 -preset fast -crf 18 -r $FPS -t 4.5 \
  "$TMP/00-title.mp4"
echo "    Title card... OK (4.5s)"

# --- Step 2: Create scene clips with Ken Burns + text overlay ---
echo "  [2/4] Scene clips with Ken Burns..."
i=1
for scene in "${SCENES[@]}"; do
  IFS='|' read -r file duration text kb_dir <<< "$scene"
  padded=$(printf "%02d" $i)
  outfile="$TMP/${padded}-scene.mp4"
  dur_frames=$(echo "$duration * $FPS" | bc | cut -d. -f1)

  printf "    %-28s %-45s " "$file" "$text"

  KB_EXPR=$(kb_expr "$kb_dir" "$dur_frames")

  ffmpeg -y -loglevel error \
    -loop 1 -i "$FRAMES/$file" \
    -vf "scale=${KB_SCALE},zoompan=${KB_EXPR}:d=${dur_frames}:s=1920x1080:fps=${FPS},format=yuv420p,\
         drawbox=y=ih-65:w=iw:h=65:color=black@0.5:t=fill,\
         drawtext=text='${text}':fontsize=26:fontcolor=white@0.95:x=(w-text_w)/2:y=h-43:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" \
    -c:v libx264 -preset fast -crf 18 -r $FPS -t "$duration" \
    "$outfile"

  echo "OK (${duration}s)"
  i=$((i+1))
done

# --- Step 3: Create end card ---
echo "  [3/4] End card..."
ffmpeg -y -loglevel error \
  -f lavfi -i "color=c=#4F46E5:s=1920x1080:d=5,format=yuv420p" \
  -vf "drawtext=text='BorrowHood':fontsize=80:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2-100:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf,\
       drawtext=text='250 Tests | 14 Badges | Lockbox Exchange':fontsize=26:fontcolor=white@0.9:x=(w-text_w)/2:y=(h-text_h)/2-10:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf,\
       drawtext=text='FastAPI + Alpine.js + Keycloak + Tailwind':fontsize=22:fontcolor=white@0.7:x=(w-text_w)/2:y=(h-text_h)/2+40:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf,\
       drawtext=text='github.com/akenel/borrowhood':fontsize=28:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2+100:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf,\
       fade=t=out:st=3.5:d=1.5" \
  -c:v libx264 -preset fast -crf 18 -r $FPS -t 5 \
  "$TMP/99-end.mp4"
echo "    End card... OK (5s)"

# --- Step 4: Chain all clips with xfade crossfades ---
echo "  [4/4] Chaining with crossfades + music..."

# Build list of all clips in order
CLIPS=("$TMP/00-title.mp4")
for j in $(seq -w 1 ${#SCENES[@]}); do
  CLIPS+=("$TMP/${j}-scene.mp4")
done
CLIPS+=("$TMP/99-end.mp4")

NUM_CLIPS=${#CLIPS[@]}
echo "    Clips: $NUM_CLIPS"

# For xfade chaining we need to build a complex filter graph:
# [0][1]xfade=offset=O1[v01]; [v01][2]xfade=offset=O2[v012]; ...
# Offsets: each clip's start = prev_offset + prev_dur - xfade_dur

# Get durations
DURS=()
for clip in "${CLIPS[@]}"; do
  d=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$clip")
  DURS+=("$d")
done

echo "    Durations: ${DURS[*]}"

# Build input args
INPUT_ARGS=""
for clip in "${CLIPS[@]}"; do
  INPUT_ARGS="$INPUT_ARGS -i $clip"
done

# Build xfade filter chain
FILTER=""
OFFSET=0
PREV_LABEL="0:v"

for ((idx=1; idx<NUM_CLIPS; idx++)); do
  # Offset = cumulative duration so far minus cumulative xfade overlap
  prev_dur=${DURS[$((idx-1))]}
  OFFSET=$(echo "$OFFSET + $prev_dur - $XFADE_DUR" | bc)

  if [ $idx -eq 1 ]; then
    SRC_A="[0:v]"
  else
    SRC_A="[v$((idx-1))]"
  fi

  if [ $idx -eq $((NUM_CLIPS-1)) ]; then
    OUT_LABEL="[vout]"
  else
    OUT_LABEL="[v${idx}]"
  fi

  FILTER="${FILTER}${SRC_A}[${idx}:v]xfade=transition=fade:duration=${XFADE_DUR}:offset=${OFFSET}${OUT_LABEL};"
done

# Remove trailing semicolon
FILTER="${FILTER%;}"

echo "    Filter chain built (${NUM_CLIPS} clips, $((NUM_CLIPS-1)) crossfades)"

# Get total video duration (sum of all durations minus overlaps)
TOTAL_DUR=$(echo "${DURS[0]}" | bc)
for ((idx=1; idx<NUM_CLIPS; idx++)); do
  TOTAL_DUR=$(echo "$TOTAL_DUR + ${DURS[$idx]} - $XFADE_DUR" | bc)
done
echo "    Expected duration: ${TOTAL_DUR}s"

# Build video with crossfades
ffmpeg -y -loglevel warning \
  $INPUT_ARGS \
  -filter_complex "${FILTER}" \
  -map "[vout]" \
  -c:v libx264 -preset fast -crf 18 -r $FPS \
  "$TMP/video-silent.mp4"

# Verify duration
VDUR=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$TMP/video-silent.mp4")
echo "    Silent video: ${VDUR}s"

# Add music: fade in 1.5s, fade out 3s before end, volume 0.35
FADE_OUT_START=$(echo "$VDUR - 3" | bc)
ffmpeg -y -loglevel error \
  -i "$TMP/video-silent.mp4" \
  -i "$MUSIC" \
  -filter_complex "[1:a]atrim=0:${VDUR},afade=t=in:st=0:d=1.5,afade=t=out:st=${FADE_OUT_START}:d=3,volume=0.35[music]; \
                   [music]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[aout]" \
  -map 0:v -map "[aout]" \
  -c:v copy -c:a aac -b:a 192k -ar 48000 \
  -shortest \
  "$OUTPUT"

# Final stats
FSIZE=$(du -h "$OUTPUT" | cut -f1)
FDUR=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$OUTPUT")
echo ""
echo "  ==============================="
echo "  OUTPUT: $OUTPUT"
echo "  Size:   $FSIZE"
echo "  Duration: ${FDUR}s"
echo "  Resolution: 1920x1080"
echo "  Codec: H.264 + AAC 192kbps"
echo "  ==============================="
echo ""
echo "  Play it: vlc '$OUTPUT'"
echo ""
