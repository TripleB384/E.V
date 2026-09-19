#!/usr/bin/env bash
# Double-click this file in Finder to set up (first time only) and start
# E.V, then open it in your browser. No typing required.
#
# First double-click only: macOS may warn that this is from an
# "unidentified developer" (only if you downloaded a ZIP rather than
# `git clone`d the repo). If so: right-click this file -> Open -> Open,
# once. After that, plain double-clicking works.
set -euo pipefail
cd "$(dirname "$0")"

if [[ ! -d .venv ]]; then
  echo "First-time setup — this installs a few things and logs you into Claude Code."
  echo "(This only happens once. A browser window may open for the Claude Code login.)"
  echo
  ./scripts/setup.sh
fi

# shellcheck disable=SC1091
source .venv/bin/activate
if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

PORT="${EV_PORT:-8765}"

uvicorn harness.server:app --port "$PORT" &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null' EXIT

echo "Starting E.V..."
for _ in $(seq 1 30); do
  if curl -s "http://localhost:$PORT/api/health" >/dev/null 2>&1; then
    break
  fi
  sleep 0.5
done

open "http://localhost:$PORT"

echo
echo "E.V is running at http://localhost:$PORT"
echo "Leave this window open while you use E.V. Close this window (or press Ctrl+C) to stop it."
echo

wait "$SERVER_PID"
