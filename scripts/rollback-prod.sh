#!/bin/bash
# rollback-prod.sh -- Restore the previous production image in ~30 seconds.
#
# Every deploy-prod.sh run tags the outgoing image as borrowhood:prod-previous.
# This script flips back to it. No tests, no ceremony -- it's the fire escape.
#
# USAGE: bash scripts/rollback-prod.sh
set -e

SERVER="root@46.62.138.218"
COMPOSE_DIR="/opt/helixnet/hetzner"
CONTAINER="borrowhood"
DOMAIN="lapiazza.app"

R='\033[0;31m'; G='\033[0;32m'; Y='\033[0;33m'; B='\033[0;34m'; N='\033[0m'

echo -e "${B}=== La Piazza PROD rollback ===${N}"

# Does the rollback image exist on the server?
if ! ssh $SERVER "docker image inspect borrowhood:prod-previous" >/dev/null 2>&1; then
    echo -e "${R}!! no borrowhood:prod-previous image on server. Nothing to roll back to.${N}"
    exit 1
fi

# Show what we're rolling back FROM and TO
CURRENT=$(ssh $SERVER "docker image inspect borrowhood:latest --format '{{.Created}}' 2>/dev/null || echo unknown")
PREVIOUS=$(ssh $SERVER "docker image inspect borrowhood:prod-previous --format '{{.Created}}' 2>/dev/null || echo unknown")
echo "  Currently running: $CURRENT"
echo "  Rolling back to  : $PREVIOUS"
echo

read -r -p "$(echo -e "${Y}Type 'rollback' to proceed: ${N}")" CONFIRM
if [[ "$CONFIRM" != "rollback" ]]; then
    echo -e "${Y}=== cancelled${N}"
    exit 0
fi

# Save the (broken) current image as prod-broken for forensics
ssh $SERVER "docker tag borrowhood:latest borrowhood:prod-broken || true"

# Flip the tag, restart the container
ssh $SERVER "docker tag borrowhood:prod-previous borrowhood:latest && cd $COMPOSE_DIR && docker compose -f docker-compose.uat.yml up -d --no-deps $CONTAINER" 2>&1 | tail -3

# Wait for healthy
for i in $(seq 1 30); do
    if ssh $SERVER "docker exec $CONTAINER curl -sf http://localhost:8000/api/v1/health" >/dev/null 2>&1; then
        echo -e "${G}✓ healthy after $((i*2))s${N}"
        break
    fi
    [ $i -eq 30 ] && { echo -e "${R}!! rollback image ALSO unhealthy. Check logs manually.${N}"; exit 1; }
    sleep 2
done

# Smoke test
curl -sf -o /dev/null -w "Home: HTTP %{http_code}\n" "https://$DOMAIN/"

echo -e "${G}=== rolled back ===${N}"
echo "Forensics image kept as borrowhood:prod-broken"
