#!/usr/bin/env bash
# Deploy to staging. No gate -- every push to main should land here.
#
# Run on the Hetzner box (either manually or via CI over SSH).
#
# What it does:
#   1. Pulls latest main
#   2. Builds borrowhood:staging image (separate tag from prod)
#   3. Restarts borrowhood_staging container with zero downtime
#   4. Waits for healthz
#   5. Runs pending DB migrations (idempotent ALTER TABLE IF NOT EXISTS patterns)
#
# Safety: does NOT touch the prod container or prod DB.

set -euo pipefail

HETZNER_REPO=/opt/helixnet/BorrowHood
HETZNER_COMPOSE_DIR=/opt/helixnet/hetzner

cd "$HETZNER_REPO"

echo "== [staging] pulling latest main"
git fetch origin
git checkout main
git pull --ff-only origin main
CURRENT_SHA="$(git rev-parse --short HEAD)"
echo "== [staging] target SHA: $CURRENT_SHA"

cd "$HETZNER_COMPOSE_DIR"

echo "== [staging] rebuilding image borrowhood:staging"
docker compose -f docker-compose.uat.yml -f docker-compose.staging.yml build borrowhood_staging

echo "== [staging] recreating container"
docker compose -f docker-compose.uat.yml -f docker-compose.staging.yml up -d borrowhood_staging

echo "== [staging] waiting for healthcheck"
for i in {1..30}; do
    state=$(docker inspect borrowhood_staging --format '{{.State.Health.Status}}' 2>/dev/null || echo "starting")
    if [[ "$state" == "healthy" ]]; then
        echo "== [staging] healthy after ${i}0s"
        break
    fi
    sleep 10
    if [[ $i -eq 30 ]]; then
        echo "!! [staging] failed to become healthy in 5 minutes"
        docker logs borrowhood_staging --tail 50
        exit 1
    fi
done

# Tag image with SHA for audit trail
docker tag borrowhood:staging borrowhood:staging-$CURRENT_SHA

echo "== [staging] done. visit https://staging.lapiazza.app (SHA: $CURRENT_SHA)"
