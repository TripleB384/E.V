# Setup

## Prerequisites

- [Claude Code](https://code.claude.com/docs/en/quickstart) installed (`claude` on your PATH).
- A Claude.ai account. The web chat works with any account, but headless/scheduled use in later phases needs a Pro, Max, Team, or Enterprise plan (see `docs/RISKS.md`).
- Python 3.11+. [`uv`](https://docs.astral.sh/uv/) is recommended but not required — the setup script falls back to plain `venv`/`pip`.

## Get running

```bash
git clone <this repo>
cd E.V
./scripts/setup.sh   # logs Claude Code into your account, installs Python deps
./scripts/run_dev.sh # starts the local web server
```

Open `http://localhost:8765` and start chatting.

If `./scripts/setup.sh` reports `claude` isn't found, install Claude Code first, then re-run it.

## Manually verifying the Claude Code connection

If something's not working, check the underlying CLI call directly before debugging the web app:

```bash
cd E.V
claude -p "say hi as yourself" --output-format json
```

You should get back a JSON object with a `result` field containing E.V's reply (persona comes from this repo's `CLAUDE.md`, loaded automatically because the command ran from the repo root) and a `session_id`. If this fails, the problem is in your Claude Code login/install, not in `harness/`.

## Troubleshooting

- **"claude CLI was not found on PATH"** — install Claude Code, or check your shell's PATH if you installed it somewhere non-standard.
- **502 from `/api/chat`** — the error detail includes the CLI's stderr; often an auth issue (`claude /login` again) or a request that timed out.
- **Replies don't sound like E.V** — confirm you're running the server from the repo root (`scripts/run_dev.sh` does this) so `CLAUDE.md` is actually being picked up.
