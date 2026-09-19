# E.V — architecture

E.V's brain is the real **Claude Code CLI** (`claude`), run headlessly and authenticated with your own Claude.ai Pro/Max subscription — not the Claude Agent SDK, not the Anthropic Messages API. That distinction is what keeps this project free to run beyond an optional existing subscription; see `docs/RISKS.md` for exactly why it matters and don't route around it.

Everything Claude Code natively provides (persona, memory-of-facts-in-context, tool use, skills, subagents) is configured through its own project files, versioned in this repo:

- **`CLAUDE.md`** — persona, tone, standing instructions, and guidance on using the tools below.
- **`.claude/skills/`** — deterministic, well-known procedures (e.g. `summarize-notes`, `check-deadlines`, `capture-task`).
- **`.claude/agents/`** — subagents for open-ended sub-tasks with their own tone/tool scope (none yet).
- **`.mcp.json`** + **`mcp_servers/`** — real tool integrations that need actual auth/network/storage code: `tasks_server.py` (Todoist), `calendar_server.py` (Google Calendar), `canvas_server.py` (Canvas LMS).

Everything Claude Code does *not* provide — an HTTP/chat surface, scheduling, voice I/O, and *tool permission grants* (see below) — is a small external **harness**, in `harness/`, that shells out to `claude -p` as a subprocess. The harness is deliberately thin: it owns session bookkeeping, process invocation, and permission grants, not reasoning, memory, or persona.

### Permissions: `--allowedTools`, not `.claude/settings.json`

`.claude/settings.json`'s `permissions.allow` turns out to be inert for a project that's never been interactively "trusted" — and headless mode has no dialog to trust it with. So `harness/server.py` grants tools directly on each `claude -p` invocation via `--allowedTools` (`CHAT_ALLOWED_TOOLS` in that file) instead. This also means there's no per-call approval step the way there is in interactive Claude Code — see `docs/RISKS.md`'s security section before changing what's granted.

### Creating files

`Write`/`Edit`/`Bash(python3 *)` are granted to the chat, so E.V can write documents, code, and code-generated images/diagrams (charts via matplotlib, etc. — there's no text-to-image model available). `CLAUDE.md` instructs it to default to `workspace/` (gitignored — it's your generated output, not project source), but that's an instruction, not a technical sandbox; see `docs/RISKS.md`.

## Request flow (Phase 1)

```
 browser (web/)
     │  POST /api/chat {message, conversation_id}
     ▼
 harness/server.py (FastAPI)
     │  looks up / creates ConversationState (harness/sessions.py)
     ▼
 harness/claude_client.py
     │  claude -p "<message>" --output-format json [--resume <session_id>]
     │  run with cwd = repo root, so Claude Code auto-loads CLAUDE.md /
     │  .claude/settings.json / .mcp.json on its own
     ▼
 claude CLI  →  Anthropic, billed against your subscription's usage pool
     │  JSON: { result, session_id, is_error, subtype, ... }
     ▼
 harness/server.py  →  { reply, conversation_id }  →  browser renders it
```

## Build phases

| Phase | What it adds | Needs external credentials? |
|---|---|---|
| **1 — Text MVP** (done) | Local web chat ↔ headless Claude Code, in-persona replies | No |
| **File creation** (done) | `workspace/`, `Write`/`Edit`/`Bash(python3 *)` granted to chat — documents, code, code-generated images/diagrams | No |
| **Student integrations** (done, per-integration setup) | `tasks_server.py` (Todoist), `calendar_server.py` (Google Calendar), `canvas_server.py` (Canvas), `check-deadlines` / `capture-task` skills | Yes, per integration — Todoist API token, Google OAuth app, Canvas personal access token (each free, but an account you set up yourself; see `docs/SETUP.md`) |
| **2 — Memory** | SQLite + sqlite-vec store, `memory_server.py` MCP server, `remember`/`recall`, a `Stop` hook that auto-extracts durable facts | No (fully local) |
| **4 — Browser voice** | `web/voice.js` using the browser's built-in `SpeechRecognition`/`speechSynthesis` | No |
| **5 — Proactive scheduling** | `harness/scheduler.py` (APScheduler), desktop + Telegram notifications, launch-on-login | Telegram bot token if you want phone push (optional, free) |
| **6 — Ambient voice (stretch)** | openWakeWord + whisper.cpp + Piper always-on daemon, optionally on a Raspberry Pi satellite | No, but needs downloaded model files and real audio hardware to test |

(Numbering follows the original plan; file creation and the student integrations were pulled forward ahead of memory/voice/scheduling based on what was actually asked for next.)

See `/root/.claude/plans/i-want-you-to-compiled-creek.md` (or your own copy of the plan) for the full per-phase file lists and verification steps.

## Optional: running without a Claude subscription at all

Because a Claude subscription is meant to be *optional*, `harness/claude_client.py`'s `run_prompt()` is the one seam an alternate local-LLM backend (e.g. Ollama) would need to implement to swap in for free with no subscription. Be aware this is a real fork, not a drop-in: Ollama doesn't get `CLAUDE.md` / Skills / MCP auto-wiring the way Claude Code does, so tool-calling would need to be hand-rolled, at meaningfully lower capability. Not built here — documented as the path if you want it.
