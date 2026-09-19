# E.V — architecture

E.V's brain is the real **Claude Code CLI** (`claude`), run headlessly and authenticated with your own Claude.ai Pro/Max subscription — not the Claude Agent SDK, not the Anthropic Messages API. That distinction is what keeps this project free to run beyond an optional existing subscription; see `docs/RISKS.md` for exactly why it matters and don't route around it.

Everything Claude Code natively provides (persona, memory-of-facts-in-context, tool use, skills, subagents) is configured through its own project files, versioned in this repo:

- **`CLAUDE.md`** — persona, tone, standing instructions.
- **`.claude/skills/`** — deterministic, well-known procedures (e.g. `summarize-notes`).
- **`.claude/agents/`** — subagents for open-ended sub-tasks with their own tone/tool scope.
- **`.mcp.json`** + **`mcp_servers/`** — real tool integrations (calendar, tasks, memory, research) that need actual auth/network/storage code.
- **`.claude/settings.json`** — permissions and hooks.

Everything Claude Code does *not* provide — an HTTP/chat surface, scheduling, voice I/O — is a small external **harness**, in `harness/`, that shells out to `claude -p` as a subprocess. The harness is deliberately thin: it owns session bookkeeping and process invocation, not reasoning, memory, or persona.

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
| **2 — Memory** | SQLite + sqlite-vec store, `memory_server.py` MCP server, `remember`/`recall`, a `Stop` hook that auto-extracts durable facts | No (fully local) |
| **3 — Student integrations** | Calendar / Todoist / Canvas / arXiv MCP servers, `check-deadlines` / `capture-task` skills, `study-buddy` / `research-assistant` subagents | Yes — Google OAuth app, Canvas personal access token, Todoist token (each is free, but is an account you set up yourself) |
| **4 — Browser voice** | `web/voice.js` using the browser's built-in `SpeechRecognition`/`speechSynthesis` | No |
| **5 — Proactive scheduling** | `harness/scheduler.py` (APScheduler), desktop + Telegram notifications, launch-on-login | Telegram bot token if you want phone push (optional, free) |
| **6 — Ambient voice (stretch)** | openWakeWord + whisper.cpp + Piper always-on daemon, optionally on a Raspberry Pi satellite | No, but needs downloaded model files and real audio hardware to test |

See `/root/.claude/plans/i-want-you-to-compiled-creek.md` (or your own copy of the plan) for the full per-phase file lists and verification steps.

## Optional: running without a Claude subscription at all

Because a Claude subscription is meant to be *optional*, `harness/claude_client.py`'s `run_prompt()` is the one seam an alternate local-LLM backend (e.g. Ollama) would need to implement to swap in for free with no subscription. Be aware this is a real fork, not a drop-in: Ollama doesn't get `CLAUDE.md` / Skills / MCP auto-wiring the way Claude Code does, so tool-calling would need to be hand-rolled, at meaningfully lower capability. Not built here — documented as the path if you want it.
