# E.V

A personal AI assistant in the spirit of J.A.R.V.I.S. (Iron Man) and E.D.I.T.H. (Spider-Man) — built to cost **$0**, with the only optional expense being a Claude subscription you may already have.

Built first for college students: deadline tracking, lecture/note summarization, research help, study Q&A, task capture — plus general personal-assistant usefulness.

## How it works, in one paragraph

E.V's brain is the real [Claude Code](https://code.claude.com) CLI, run headlessly under your own Claude.ai login — not a paid API key, not the Claude Agent SDK. Its persona, memory, and tools are configured through Claude Code's own native project files (`CLAUDE.md`, `.claude/skills/`, `.claude/agents/`, MCP servers), versioned right here in the repo. A small local web app (`harness/` + `web/`) is the only custom code — it just shells out to `claude -p` and renders the reply. See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full design and build-phase roadmap, and [`docs/RISKS.md`](docs/RISKS.md) for exactly why it's built this way instead of the more obvious "call an API" approach.

## Quickstart

```bash
./scripts/setup.sh
./scripts/run_dev.sh
```

Then open `http://localhost:8765`. Full steps and troubleshooting: [`docs/SETUP.md`](docs/SETUP.md).

## Status

Phase 1 (text chat) is live. Memory, student integrations (calendar/Canvas/tasks/research), voice, and proactive nudges are designed but not yet built — see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for what's next.

## License

GPLv2 — see [`LICENSE`](LICENSE).
