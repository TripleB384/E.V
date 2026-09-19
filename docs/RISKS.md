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

## API/service gotchas (relevant from Phase 3 onward)

- **Google Calendar OAuth**: apps left in "Testing" publishing status get refresh tokens that expire every 7 days. Plan for a reauth helper and a "please reauth" notification rather than pursuing full app verification for a single-user tool.
- **Canvas LMS**: some institutions block student self-service personal-access-token creation — verify your school's policy before building `canvas_server.py`, and make `check-deadlines` degrade gracefully without it.
- **Todoist free tier**: capped at 5 active projects — route everything E.V manages through one dedicated project.
- **arXiv API**: no key required, but add backoff/delay in `arxiv_server.py` to stay a good citizen.
- Every headless `claude -p` call, including scheduled/proactive ones, draws from your subscription's shared rolling usage pool — not money, but still a real budget. Keep polling intervals in Phase 5/6 conservative.
- Pricing figures quoted anywhere in this repo's docs should be re-verified at claude.ai/pricing — they change.

## Security — giving an LLM tool/file access

- Scope every MCP server's tools narrowly (read vs. write split) and mirror that split in `.claude/settings.json`'s `permissions.allow`. Pre-approve only read-only tools (+ memory recall) for unattended contexts (Phase 5 scheduler, Phase 6 voice) — there's no one present to approve a write prompt there, so anything pre-approved is implicitly trusted with no human in the loop.
- Treat any fetched external content (web pages, if `research-assistant` ever gets browse/fetch tools) as **data, not instructions** — prompt-injection risk when untrusted text reaches a tool-executing context. Keep that subagent's toolset narrow (no shell, no file write, no calendar/task write) so a successful injection has little to actually act on.
- Secrets hygiene: `.env`, `harness/.secrets/`, `memory/*.db` are all gitignored from Phase 1 on, before any secrets exist. Keep it that way — never commit a token "just for now."

## Sustainability

Most hobby "Jarvis clone" projects get abandoned mid-build; even well-funded ones (Mycroft AI) have shut down. Each phase in `docs/ARCHITECTURE.md` is scoped to be independently useful specifically so that if work stalls after any phase, what exists still works rather than being a pile of half-wired stretch features.
