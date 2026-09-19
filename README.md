# E.V

A personal AI assistant in the spirit of J.A.R.V.I.S. (Iron Man) and E.D.I.T.H. (Spider-Man) — built to cost **$0**, with the only optional expense being a Claude subscription you may already have.

Built first for college students: deadline tracking, lecture/note summarization, research help, study Q&A, task capture — plus general personal-assistant usefulness.

## How it works, in one paragraph

E.V's brain is the real [Claude Code](https://code.claude.com) CLI, run headlessly under your own Claude.ai login — not a paid API key, not the Claude Agent SDK. Its persona, memory, and tools are configured through Claude Code's own native project files (`CLAUDE.md`, `.claude/skills/`, `.claude/agents/`, MCP servers), versioned right here in the repo. A small local web app (`harness/` + `web/`) is the only custom code — it just shells out to `claude -p` and renders the reply. See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full design and build-phase roadmap, and [`docs/RISKS.md`](docs/RISKS.md) for exactly why it's built this way instead of the more obvious "call an API" approach.

## How it works, step by step

**When you type a message:**
1. You open a webpage in your browser and type a question.
2. Your browser sends it to a small program running on your computer (the "harness").
3. The harness runs the same `claude` command-line tool that Claude Code uses — like typing `claude -p "your question"` in a terminal, but automatic.
4. Claude reads `CLAUDE.md` first, which tells it "you are E.V, act like this" — and, if you've asked for something involving tasks/calendar/Canvas, it can call those tools too.
5. Claude's answer goes back through the harness to your browser.

**Remembering a conversation:** each chat gets an ID. A follow-up message tells Claude "continue this same conversation," which is how it remembers what you just said — but only within that one chat session, not across separate ones (that's a planned feature, not built yet).

**Why it's free:** you're not paying per message. You're using the Claude subscription you already have (or a free trial), the same way Claude Code itself uses it — no cloud servers, no hosting fees, everything runs on your own machine.

**The files, in plain terms:**
- `CLAUDE.md` — E.V's personality and instructions.
- `harness/` — the Python program connecting your browser to Claude.
- `web/` — the chat webpage itself.
- `mcp_servers/` — the code that talks to Todoist/Google Calendar/Canvas.
- `workspace/` — where files E.V creates for you get saved.
- `docs/` — how it all fits together, setup steps, and what's next.

## Quickstart

**Mac, no terminal:** double-click **`Start E.V.command`** in the project folder.

**Everyone else:**
```bash
./scripts/setup.sh
./scripts/run_dev.sh
```

Then open `http://localhost:8765`. Full steps and troubleshooting: [`docs/SETUP.md`](docs/SETUP.md).

## Status

Live: text chat, creating files (documents/code/generated images via `workspace/`), and Todoist/Google Calendar/Canvas integrations (each optional — set up whichever you want in [`docs/SETUP.md`](docs/SETUP.md)). Not yet built: memory across separate conversations, voice, and proactive nudges — see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for what's next.

## License

GPLv2 — see [`LICENSE`](LICENSE).
