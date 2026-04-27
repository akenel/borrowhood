#!/bin/bash
# deploy-prod.sh -- Promote a commit to La Piazza production.
# Gate B: clean tree + tests green + explicit 'deploy' consent.
#
# USAGE:
#   bash scripts/deploy-prod.sh                         # deploy HEAD
#   bash scripts/deploy-prod.sh <commit-or-tag>         # deploy a specific ref
#   bash scripts/deploy-prod.sh --templates-only        # no rebuild (Jinja only)
#
# Safety checks (ALL must pass before any server action):
#   1. You are on branch 'main'
#   2. Working tree clean (no uncommitted changes)
#   3. Target commit exists on origin/main
#   4. pytest passes
#   5. You type 'deploy' to confirm
#
# Post-deploy:
#   - Previous image tagged borrowhood:prod-previous (for rollback-prod.sh)
#   - New image tagged borrowhood:prod-YYYY-MM-DD-HHMM
#   - Matching git tag pushed to origin (audit)
set -e

SERVER="root@46.62.138.218"
APP_REPO="/opt/helixnet/BorrowHood"
COMPOSE_DIR="/opt/helixnet/hetzner"
COMPOSE="docker compose -f docker-compose.uat.yml"
CONTAINER="borrowhood"
DOMAIN="lapiazza.app"

# Colors
R='\033[0;31m'; G='\033[0;32m'; Y='\033[0;33m'; B='\033[0;34m'; N='\033[0m'

TEMPLATES_ONLY=false
TARGET_REF="HEAD"

# Parse args
for arg in "$@"; do
    case "$arg" in
        --templates-only) TEMPLATES_ONLY=true ;;
        --skip-tests)     SKIP_TESTS=true ;;
        -h|--help)
            sed -n '2,22p' "$0"
            exit 0
            ;;
        *) TARGET_REF="$arg" ;;
    esac
done

echo -e "${B}=== La Piazza production deploy ===${N}"
echo "$(date '+%Y-%m-%d %H:%M:%S')"
echo

# ── GATE 1: on main branch
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "$BRANCH" != "main" ]]; then
    echo -e "${R}!! branch is '$BRANCH', not 'main'. Switch first.${N}"
    exit 1
fi

# ── GATE 2: clean working tree
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo -e "${R}!! working tree is dirty. Commit or stash first.${N}"
    git status --short
    exit 1
fi

# ── GATE 3: target is on origin/main
git fetch origin main --quiet
TARGET_SHA=$(git rev-parse "$TARGET_REF")
TARGET_SHORT=$(git rev-parse --short "$TARGET_REF")
if ! git merge-base --is-ancestor "$TARGET_SHA" origin/main; then
    echo -e "${R}!! $TARGET_SHORT is not on origin/main. Push first.${N}"
    exit 1
fi

# ── GATE 4: tests green (skippable with --skip-tests for emergency hotfix)
if [[ "${SKIP_TESTS:-false}" != "true" ]]; then
    echo -e "${Y}--- running pytest${N}"
    # Find a python with pytest installed (prefer the project venv)
    PYTHON_BIN=""
    for candidate in .venv/bin/python python3 python; do
        if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import pytest' >/dev/null 2>&1; then
            PYTHON_BIN="$candidate"
            break
        fi
    done
    if [[ -z "$PYTHON_BIN" ]]; then
        echo -e "${R}!! no python with pytest found. Activate the venv or use --skip-tests.${N}"
        exit 1
    fi
    # Run pytest with PIPESTATUS so tail doesn't swallow the real exit code
    set -o pipefail
    if ! "$PYTHON_BIN" -m pytest tests/ -q --no-header --tb=line 2>&1 | tail -5; then
        set +o pipefail
        echo -e "${R}!! tests failed. Fix before deploying.${N}"
        exit 1
    fi
    set +o pipefail
    echo -e "${G}✓ tests green (via $PYTHON_BIN)${N}"
fi

# ── Summary
echo
echo -e "${B}--- Deploy plan${N}"
echo "  Target ref : $TARGET_REF ($TARGET_SHORT)"
echo "  Host       : $SERVER"
echo "  Mode       : $($TEMPLATES_ONLY && echo 'templates only' || echo 'full rebuild')"
echo "  Commit msg :"
git log -1 --format='    %s%n    (%an, %ar)' "$TARGET_SHA"
echo

# ── GATE 5: explicit consent
read -r -p "$(echo -e "${Y}Type 'deploy' to promote to production: ${N}")" CONFIRM
if [[ "$CONFIRM" != "deploy" ]]; then
    echo -e "${Y}=== cancelled${N}"
    exit 0
fi

TAG="prod-$(date -u +%Y-%m-%d-%H%M)"

# ── Pre-deploy health check
echo -e "${Y}--- pre-deploy check${N}"
ssh $SERVER "docker exec $CONTAINER curl -sf http://localhost:8000/api/v1/health 2>/dev/null" \
    && echo -e "${G}prod: healthy${N}" \
    || echo -e "${Y}prod: not running (first deploy or down)${N}"

# ── Git tag for audit trail
echo -e "${Y}--- tagging as $TAG${N}"
git tag -a "$TAG" "$TARGET_SHA" -m "Production deploy $TAG"
git push origin "$TAG" 2>&1 | tail -1

# ── Push commits
echo -e "${Y}--- pushing to GitHub${N}"
git push origin main 2>&1 | tail -3

# ── Pull + rebuild on server
echo -e "${Y}--- pulling on server${N}"
ssh $SERVER "cd $APP_REPO && git fetch origin --tags && git checkout $TARGET_SHA" 2>&1 | tail -3

# Save previous image as rollback target
ssh $SERVER "docker image inspect borrowhood:latest >/dev/null 2>&1 && docker tag borrowhood:latest borrowhood:prod-previous || true"

if $TEMPLATES_ONLY; then
    echo -e "${Y}--- templates only: restart only${N}"
    ssh $SERVER "cd $COMPOSE_DIR && $COMPOSE restart $CONTAINER"
else
    echo -e "${Y}--- rebuilding $CONTAINER${N}"
    ssh $SERVER "cd $COMPOSE_DIR && $COMPOSE up -d --build --no-deps $CONTAINER" 2>&1 | tail -5
fi

# Tag the fresh image with the deploy stamp
ssh $SERVER "docker tag borrowhood:latest borrowhood:$TAG"

# ── Wait for healthy
echo -e "${Y}--- health check${N}"
for i in $(seq 1 30); do
    if ssh $SERVER "docker exec $CONTAINER curl -sf http://localhost:8000/api/v1/health" >/dev/null 2>&1; then
        echo -e "${G}✓ healthy after $((i*2))s${N}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${R}!! not healthy after 60s -- rolling back${N}"
        ssh $SERVER "docker tag borrowhood:prod-previous borrowhood:latest && cd $COMPOSE_DIR && $COMPOSE up -d --no-deps $CONTAINER"
        exit 1
    fi
    sleep 2
done

# ── Smoke test
echo -e "${Y}--- smoke test${N}"
curl -sf -o /dev/null -w "Home  : HTTP %{http_code}\n" "https://$DOMAIN/"
curl -sf -o /dev/null -w "Browse: HTTP %{http_code}\n" "https://$DOMAIN/browse"
curl -sf -o /dev/null -w "Calen.: HTTP %{http_code}\n" "https://$DOMAIN/calendar"
curl -sf -o /dev/null -w "Health: HTTP %{http_code}\n" "https://$DOMAIN/api/v1/health"

# ── Disk hygiene (April 27 incident: containerd filled to 64GB and Postgres
#     ran out of write space). Keep latest + prod-previous + 5 newest prod-*
#     tags, prune everything else and the build cache. Quiet on success.
echo -e "${Y}--- cleanup: prune old images + build cache${N}"
ssh $SERVER "docker images borrowhood --format '{{.Tag}} {{.CreatedAt}}' | grep '^prod-2' | sort -k2 -r | tail -n +6 | awk '{print \"borrowhood:\" \$1}' | xargs -r docker rmi >/dev/null 2>&1; docker builder prune -af >/dev/null 2>&1; df -h / | awk 'NR==2 {print \"  disk: \" \$3 \" used / \" \$2 \" total (\" \$5 \" full)\"}'"

echo
echo -e "${G}=== deployed $TAG to production ===${N}"
echo "Rollback if needed: bash scripts/rollback-prod.sh"
