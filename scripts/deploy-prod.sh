#!/bin/bash
# deploy-prod.sh -- Deploy La Piazza (BorrowHood) to production
# Run from laptop: bash scripts/deploy-prod.sh
#
# What it does:
#   1. Checks prod is alive before touching anything
#   2. Pushes your commits to GitHub (audit trail)
#   3. Pulls latest code on the server
#   4. Rebuilds the app container if Python/config changed
#   5. Waits until healthy
#   6. Smoke tests the public URL
#
# Templates only? Skip rebuild:
#   bash scripts/deploy-prod.sh --templates-only
set -e

SERVER="root@46.62.138.218"
APP_REPO="/opt/helixnet/BorrowHood"
COMPOSE_DIR="/opt/helixnet/hetzner"
COMPOSE="docker compose -f docker-compose.uat.yml"
CONTAINER="borrowhood"
DOMAIN="lapiazza.app"

TEMPLATES_ONLY=false
if [ "$1" = "--templates-only" ]; then
    TEMPLATES_ONLY=true
fi

echo "=== La Piazza Deploy ==="
echo "$(date '+%Y-%m-%d %H:%M:%S')"
echo "Branch: main"
echo "Mode: $(if $TEMPLATES_ONLY; then echo 'templates only (no rebuild)'; else echo 'full rebuild'; fi)"
echo ""

# 1. Pre-deploy health check
echo "--- Pre-deploy check ---"
ssh $SERVER "docker exec $CONTAINER curl -sf http://localhost:8000/api/v1/health 2>/dev/null" \
    && echo "PROD: healthy" \
    || echo "PROD: not running (first deploy or down)"

# 2. Push to GitHub (audit trail)
echo ""
echo "--- Pushing to GitHub ---"
git push origin main 2>&1 | tail -3

# 3. Pull on server
echo ""
echo "--- Pulling on server ---"
ssh $SERVER "cd $APP_REPO && git pull origin main" 2>&1 | tail -5

# 4. Rebuild + restart (skip if templates only)
if $TEMPLATES_ONLY; then
    echo ""
    echo "--- Templates only -- skipping rebuild ---"
    echo "Changes are live (Jinja2 renders on each request)"
else
    echo ""
    echo "--- Rebuilding $CONTAINER ---"
    ssh $SERVER "cd $COMPOSE_DIR && $COMPOSE up -d --build --no-deps $CONTAINER" 2>&1 | tail -5
fi

# 5. Wait for healthy
echo ""
echo "--- Health check ---"
for i in $(seq 1 15); do
    if ssh $SERVER "docker exec $CONTAINER curl -sf http://localhost:8000/api/v1/health" > /dev/null 2>&1; then
        echo "HEALTHY after $((i*2))s"
        break
    fi
    if [ $i -eq 15 ]; then
        echo "FAILED: not healthy after 30s"
        echo "Check logs: ssh $SERVER docker logs $CONTAINER --tail 50"
        exit 1
    fi
    sleep 2
done

# 6. Post-deploy smoke test
echo ""
echo "--- Smoke test ---"
curl -sf "https://$DOMAIN/api/v1/health" > /dev/null 2>&1 && echo "Health API: OK" || echo "Health API: FAIL"
curl -sf -o /dev/null -w "Home: HTTP %{http_code}\n" "https://$DOMAIN/"
curl -sf -o /dev/null -w "Profile: HTTP %{http_code}\n" "https://$DOMAIN/profile"
curl -sf -o /dev/null -w "Browse: HTTP %{http_code}\n" "https://$DOMAIN/browse"

echo ""
echo "=== Deploy complete ==="
echo "$(date '+%Y-%m-%d %H:%M:%S')"
