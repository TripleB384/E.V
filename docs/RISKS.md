# Risks, gotchas, and the rules that keep this project free

Keep this file current as later phases add real credentials and tool access.

## The ToS boundary — read this before touching `harness/claude_client.py`

E.V's brain must stay **the actual `claude` CLI binary, invoked headlessly (`claude -p ...`) as a subprocess, authenticated with a personal Pro/Max subscription** via `claude /login` or `claude setup-token` (`CLAUDE_CODE_OAUTH_TOKEN`). Per Anthropic's own docs, this fits their documented "ordinary use of Claude Code" allowance, including headless mode and cron/hook-driven automation, for personal use.

Do **not**:
- `pip install`/`npm install` the Claude Agent SDK (`claude-agent-sdk`) and script OAuth/subscription login programmatically for this project. Anthropic's Agent SDK docs explicitly say third-party developers may not offer claude.ai login or rate limits for products built on it — use API-key auth for that, which is metered.
- Route "brain" calls through the Anthropic Messages API or Managed Agents thinking either is subscription-covered. Both are separate, billed-per-token products.

Every "ask Claude something" call in this codebase should trace back to `harness/claude_client.run_prompt()`, which shells out to the CLI. If you ever find yourself importing an Anthropic SDK package to make a model call, stop — that's the line being crossed.

## Licenses

- This repo is GPLv2 (see `LICENSE`).
- Phase 6 will shell out to the actively-maintained Piper fork (`OHF-Voice/piper1-gpl`, GPL-3.0) as a separate external process — that's fine (a subprocess call, not linking/vendoring), but never copy Piper's source into this repo (GPLv2-only and GPLv3 code can't be combined into one work without an "or later" clause).
- Phase 6's openWakeWord code is Apache-2.0, but its bundled *pretrained* wake-word models are CC-BY-NC-SA (non-commercial only) — fine for this personal-use project; flag it if E.V is ever repurposed commercially.

## API/service gotchas

- **Google Calendar OAuth**: apps left in "Testing" publishing status get refresh tokens that expire every 7 days. If `calendar_server.py` starts failing after a week, this is probably why — re-trigger the consent flow rather than debugging the code.
- **Canvas LMS**: some institutions block student self-service personal-access-token creation — check your school's policy first. `canvas_server.py` degrades gracefully (a plain "not set up yet" message) if `CANVAS_BASE_URL`/`CANVAS_ACCESS_TOKEN` are unset, and `check-deadlines` just skips it.
- **Todoist free tier**: capped at 5 active projects — `tasks_server.py` operates on your default project/Inbox rather than assuming a dedicated project exists; if you hit the cap, route E.V's tasks through one project you pick.
- Every headless `claude -p` call, including future scheduled/proactive ones, draws from your subscription's shared rolling usage pool — not money, but still a real budget. Keep any future polling intervals conservative.
- Pricing figures quoted anywhere in this repo's docs should be re-verified at claude.ai/pricing — they change.

## Security — giving an LLM tool/file access

**How permissions actually work here (found by testing, not assumed):** Claude Code ignores a project's `.claude/settings.json` `permissions.allow` entirely until that directory has been interactively "trusted" (running `claude` once by hand and accepting the trust dialog) — and headless mode has no dialog to accept. So `harness/server.py` passes tool grants directly on the CLI invocation via `--allowedTools` instead (see `harness/claude_client.py`), which isn't gated by that trust check. Practical consequence: **there is no per-call approval step in this project at all** — the chat endpoint's tool list (`CHAT_ALLOWED_TOOLS` in `harness/server.py`) is pre-approved in bulk, and the only human check is reading the reply after the fact. This is a different safety model than running `claude` interactively yourself, where you approve each risky action as it happens — keep that in mind before widening `CHAT_ALLOWED_TOOLS`.

- **Write/Edit are not sandboxed to `workspace/`** — tested directly: with `Write` granted, Claude Code can write anywhere the OS user running the harness can write, not just inside the project. `workspace/` is enforced only by instruction (`CLAUDE.md`), not by a technical boundary. If you want a hard boundary, run the harness inside a container/VM with restricted filesystem access — not built here.
- Scope every MCP server's tools narrowly (read vs. write split) and mirror that in `CHAT_ALLOWED_TOOLS`. `canvas_server.py` has no write tools at all, on purpose — assignment data is the institution's, not E.V's to edit. `calendar_server.py`'s `create_event` and `tasks_server.py`'s `add_task`/`complete_task` are granted to the interactive chat (see the safety-model note above) but would need to be deliberately re-added if you ever build an unattended/scheduled caller — don't pre-approve writes there without a human reading the output.
- `Bash` is scoped to `Bash(python3 *)` only (confirmed this prefix-match syntax works, and confirmed `rm` outside that prefix is refused) — resist the urge to widen it to bare `Bash` for convenience.
- Treat any fetched external content (web pages, if a future tool gets browse/fetch) as **data, not instructions** — prompt-injection risk when untrusted text reaches a tool-executing context.
- Secrets hygiene: `.env`, `harness/.secrets/` (Google OAuth tokens live here), `memory/*.db` are all gitignored. Keep it that way — never commit a token "just for now."

## Sustainability

Most hobby "Jarvis clone" projects get abandoned mid-build; even well-funded ones (Mycroft AI) have shut down. Each phase in `docs/ARCHITECTURE.md` is scoped to be independently useful specifically so that if work stalls after any phase, what exists still works rather than being a pile of half-wired stretch features.
