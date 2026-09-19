# Setup

## Prerequisites

- [Claude Code](https://code.claude.com/docs/en/quickstart) installed (`claude` on your PATH).
- A Claude.ai account. The web chat works with any account, but headless/scheduled use in later phases needs a Pro, Max, Team, or Enterprise plan (see `docs/RISKS.md`).
- Python 3.11+. [`uv`](https://docs.astral.sh/uv/) is recommended but not required — the setup script falls back to plain `venv`/`pip`.

## Get running

### Mac: double-click, no typing

1. Get the code onto your computer (e.g. `git clone` it, or download and unzip it from GitHub).
2. Open the `E.V` folder in Finder and double-click **`Start E.V.command`**.
3. First time only: this runs setup automatically (installs a few things, and opens a browser for you to log into Claude Code). After that, double-clicking just starts E.V straight away.
4. It opens `http://localhost:8765` in your browser automatically once it's ready.
5. To stop E.V, close that Terminal window (or press Ctrl+C in it).

If macOS refuses to open it the very first time ("unidentified developer" — only happens if you downloaded a ZIP instead of using `git clone`): right-click **`Start E.V.command`** → **Open** → **Open**, once. After that, plain double-clicking works normally.

### Everyone else (or if you prefer the terminal)

```bash
git clone <this repo>
cd E.V
./scripts/setup.sh   # logs Claude Code into your account, installs Python deps
./scripts/run_dev.sh # starts the local web server
```

Open `http://localhost:8765` and start chatting.

If setup reports `claude` isn't found, install Claude Code first, then re-run it.

## Manually verifying the Claude Code connection

If something's not working, check the underlying CLI call directly before debugging the web app:

```bash
cd E.V
claude -p "say hi as yourself" --output-format json
```

You should get back a JSON object with a `result` field containing E.V's reply (persona comes from this repo's `CLAUDE.md`, loaded automatically because the command ran from the repo root) and a `session_id`. If this fails, the problem is in your Claude Code login/install, not in `harness/`.

## Optional: tasks, calendar, and Canvas

None of these are required — `check-deadlines` just skips whatever isn't configured. Set up whichever you want, in any order.

### Tasks (Todoist)

1. Create a free account at [todoist.com](https://todoist.com) if you don't have one.
2. Settings → Integrations → Developer → copy your API token.
3. Put it in `.env`: `TODOIST_API_TOKEN=...`
4. Restart `run_dev.sh`, then try: "add a task to email my professor by Friday."

### Canvas

Some schools block students from creating their own access tokens — check first (ask IT or just try step 2; if there's no option, skip this one).

1. In Canvas: Account → Settings → **+ New Access Token**.
2. Put your school's Canvas URL and the token in `.env`:
   ```
   CANVAS_BASE_URL=https://yourschool.instructure.com
   CANVAS_ACCESS_TOKEN=...
   ```
3. Restart `run_dev.sh`, then try: "what's due this week."

### Calendar (Google)

This one has more setup than the others — a Google Cloud OAuth app, not just a token.

1. Go to the [Google Cloud Console](https://console.cloud.google.com/), create a project (or use an existing one).
2. Enable the **Google Calendar API** for it (APIs & Services → Library).
3. APIs & Services → Credentials → Create Credentials → OAuth client ID → Application type **Desktop app**.
4. Download the JSON and save it as `harness/.secrets/google_credentials.json` (the folder is gitignored — this file should never be committed).
5. Restart `run_dev.sh`, then ask E.V something calendar-related (e.g. "what's on my calendar this week"). The **first** call opens a browser window for you to sign in and consent — this needs a real browser available, so do it once while sitting at the machine, not from something headless.
6. Note: if you leave the Google app in "Testing" publishing status (the default, and fine for personal use), your login expires every 7 days — just repeat step 5's consent flow when it does. See `docs/RISKS.md`.

## Troubleshooting

- **"claude CLI was not found on PATH"** — install Claude Code, or check your shell's PATH if you installed it somewhere non-standard.
- **502 from `/api/chat`** — the error detail includes the CLI's stderr; often an auth issue (`claude /login` again) or a request that timed out.
- **Replies don't sound like E.V** — confirm you're running the server from the repo root (`scripts/run_dev.sh` does this) so `CLAUDE.md` is actually being picked up.
