#!/usr/bin/env bash
# Local dev launcher that pins the live postgres container IP at startup.
#
# The postgres container on helixnet_core has no host port mapping, and its
# internal Docker IP can shift on reboot -- .env can't keep up. This script
# reads the current IP and exports BH_DATABASE_URL before launching uvicorn,
# so you never have to edit .env again.
#
# Usage:
#   ./scripts/dev-server.sh          # runs uvicorn --reload
#   ./scripts/dev-server.sh --test   # exports vars and runs pytest
#   source ./scripts/dev-server.sh   # exports vars into current shell

set -euo pipefail

# Resolve live postgres IP from docker (first network only)
POSTGRES_IP="$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' postgres 2>/dev/null || true)"

if [[ -z "$POSTGRES_IP" ]]; then
    echo "!! postgres container not running. Start it first, then re-run." >&2
    exit 1
fi

# Only override BH_DATABASE_URL -- everything else stays from .env
export BH_DATABASE_URL="postgresql+asyncpg://helix_user:helix_pass@${POSTGRES_IP}:5432/borrowhood"
echo "== BH_DATABASE_URL pinned to postgres@${POSTGRES_IP}:5432"

# If sourced, stop here (don't launch)
[[ "${BASH_SOURCE[0]}" != "$0" ]] && return 0

# If arg is --test, run pytest; otherwise uvicorn
if [[ "${1:-}" == "--test" ]]; then
    shift
    exec python -m pytest "$@"
else
    exec uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 "$@"
fi
