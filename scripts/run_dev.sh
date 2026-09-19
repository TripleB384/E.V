#!/usr/bin/env bash
# Starts E.V's local web server. Open http://localhost:8765 (or $EV_PORT)
# once it's running.
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ -f .venv/bin/activate ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

exec uvicorn harness.server:app --reload --port "${EV_PORT:-8765}"
