#!/bin/bash
# Fix broken/missing item images across prod.
#
# Phase 1: items with no media -> insert Pollinations image derived from
#          item name + category, deterministic seed per item so re-runs
#          produce the same image.
# Phase 2: items whose Unsplash URL returns 4xx/5xx -> replace with
#          Pollinations using same rule.
#
# Usage (on the UAT/prod server):
#   bash scripts/fix_broken_images.sh
#
# Idempotent: can be re-run safely. Phase 1 only inserts where no media
# exists. Phase 2 only UPDATEs URLs that are actually dead on this run.
#
# Requires: docker exec postgres psql ... works, curl available.

set -eu

PSQL="docker exec -i postgres psql -U helix_user -d borrowhood"
# For calls inside a read-loop: same command, no -i so it doesn't slurp the loop's stdin
PSQL_NOIN="docker exec postgres psql -U helix_user -d borrowhood"

say() { printf '[%s] %s\n' "$(date +%H:%M:%S)" "$*" >&2; }

# ---------- Phase 1: items with no media ----------
say "Phase 1: inserting Pollinations media for items with no media..."

INSERTED=$($PSQL -At <<'SQL'
WITH inserted AS (
  INSERT INTO bh_item_media (id, item_id, url, alt_text, media_type, sort_order, created_at, updated_at)
  SELECT gen_random_uuid(), i.id,
         'https://image.pollinations.ai/prompt/'
           || REPLACE(REPLACE(REPLACE(i.name || ' ' || i.category, ' ', '%20'), ',', '%2C'), '&', '%26')
           || '?width=800&height=600&nologo=true&seed='
           || ABS(HASHTEXT(i.id::text))::text,
         i.name,
         'PHOTO'::mediatype,
         0,
         NOW(), NOW()
  FROM bh_item i
  WHERE i.deleted_at IS NULL
    AND NOT EXISTS (SELECT 1 FROM bh_item_media m WHERE m.item_id = i.id)
  RETURNING 1
)
SELECT COUNT(*) FROM inserted;
SQL
)

say "Phase 1 done: inserted $INSERTED media records for imageless items."

# ---------- Phase 2: dead Unsplash URLs ----------
say "Phase 2: scanning all Unsplash URLs for dead links (this takes a few minutes)..."

# Export: one media row per line as pipe-separated media_id|url|item_id|name|category
TMPFILE=$(mktemp)
trap 'rm -f "$TMPFILE"' EXIT

$PSQL -At <<'SQL' > "$TMPFILE"
SELECT m.id::text
    || chr(9) || m.url
    || chr(9) || i.id::text
    || chr(9) || REPLACE(i.name, chr(9), ' ')
    || chr(9) || COALESCE(i.category, '')
FROM bh_item_media m
JOIN bh_item i ON i.id = m.item_id
WHERE m.url LIKE '%images.unsplash.com%'
  AND i.deleted_at IS NULL;
SQL

TOTAL=$(wc -l < "$TMPFILE")
say "Checking $TOTAL Unsplash URLs..."

DEAD=0
FIXED=0
COUNTER=0

while IFS=$(printf '\t') read -r media_id url item_id name category; do
  COUNTER=$((COUNTER + 1))
  status=$(curl -sI --max-time 5 "$url" 2>/dev/null | head -1 | grep -oE '[0-9]{3}' || echo "000")
  if [ -n "$status" ] && [ "$status" -ge 400 ] 2>/dev/null; then
    DEAD=$((DEAD + 1))
    # URL-encode name + category for Pollinations prompt
    prompt_raw="${name} ${category}"
    # very basic URL encoding for spaces, commas, ampersands (covers 99% of our seed names)
    prompt=$(printf '%s' "$prompt_raw" | sed -e 's/ /%20/g' -e 's/,/%2C/g' -e "s/'/%27/g" -e 's/&/%26/g')
    seed=$(printf '%s' "$item_id" | cksum | cut -d' ' -f1)
    new_url="https://image.pollinations.ai/prompt/${prompt}?width=800&height=600&nologo=true&seed=${seed}"
    $PSQL_NOIN -c "UPDATE bh_item_media SET url = '${new_url}', updated_at = NOW() WHERE id = '${media_id}';" > /dev/null
    FIXED=$((FIXED + 1))
    say "  [$COUNTER/$TOTAL] DEAD($status) -> fixed: $name"
  fi
  # progress ping every 100 rows
  if [ $((COUNTER % 100)) -eq 0 ]; then
    say "  ...$COUNTER/$TOTAL checked, $DEAD dead so far"
  fi
done < "$TMPFILE"

say "Phase 2 done: scanned $TOTAL URLs, found $DEAD dead, fixed $FIXED."
say "All done."
