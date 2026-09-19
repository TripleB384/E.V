#!/usr/bin/env bash
# One-time setup for E.V's Phase 1 text chat: logs Claude Code into your
# personal subscription and installs the harness's Python dependencies.
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v claude >/dev/null 2>&1; then
  # Common right after a fresh install: this shell's PATH was captured
  # before the installer updated your shell config, so `claude` is on disk
  # but this process doesn't know it yet. Ask your actual login shell to
  # resolve PATH the way a brand new terminal window would, and adopt that.
  resolved_path="$("${SHELL:-/bin/zsh}" -lc 'echo $PATH' 2>/dev/null || true)"
  if [[ -n "$resolved_path" ]]; then
    PATH="$resolved_path"
    export PATH
  fi
fi

if ! command -v claude >/dev/null 2>&1; then
  echo "Claude Code CLI not found on PATH." >&2
  echo "Install it first: https://code.claude.com/docs/en/quickstart" >&2
  echo "If you just installed it and this still fails, fully quit Terminal" >&2
  echo "(Cmd+Q, not just close the window) and try again." >&2
  exit 1
fi

echo "E.V uses your own Claude Code login (Pro/Max subscription) as its brain —"
echo "no separate API key needed for the Phase 1 web chat."
read -rp "Run 'claude /login' now? [y/N] " do_login
if [[ "${do_login:-}" =~ ^[Yy]$ ]]; then
  claude /login
fi

if command -v uv >/dev/null 2>&1; then
  uv venv .venv
  # shellcheck disable=SC1091
  source .venv/bin/activate
  uv pip install -r harness/requirements.txt -r mcp_servers/requirements.txt
else
  echo "uv not found, falling back to python3 -m venv + pip"
  python3 -m venv .venv
  # shellcheck disable=SC1091
  source .venv/bin/activate
  pip install -r harness/requirements.txt -r mcp_servers/requirements.txt
fi

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example (only needed later, for headless/scheduled use)."
fi

echo
echo "Setup complete. Start E.V with: ./scripts/run_dev.sh"
