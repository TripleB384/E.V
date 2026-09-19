# E.V

A personal AI assistant in the spirit of J.A.R.V.I.S. (Iron Man) and E.D.I.T.H. (Spider-Man) — built to cost **$0**, with the only optional expense being a Claude subscription you may already have.

Built first for college students: deadline tracking, lecture/note summarization, research help, study Q&A, task capture — plus general personal-assistant usefulness.

## How it works, in one paragraph

E.V's brain is the real [Claude Code](https://code.claude.com) CLI, run headlessly under your own Claude.ai login — not a paid API key, not the Claude Agent SDK. Its persona, memory, and tools are configured through Claude Code's own native project files (`CLAUDE.md`, `.claude/skills/`, `.claude/agents/`, MCP servers), versioned right here in the repo. A small local web app (`harness/` + `web/`) is the only custom code — it just shells out to `claude -p` and renders the reply. See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full design and build-phase roadmap, and [`docs/RISKS.md`](docs/RISKS.md) for exactly why it's built this way instead of the more obvious "call an API" approach.

The big idea

E.V is a chat assistant you run on your own computer.
It uses your Claude subscription as its "brain." No extra API costs.

When you type a message

You open a webpage in your browser.
You type a question and hit send.
Your browser sends that message to a small program running on your computer (the "harness").

The harness talks to Claude

The harness runs the same claude command-line tool that Claude Code uses.
It's like typing claude -p "your question" in a terminal, but done automatically.
Claude reads a file called CLAUDE.md first. That file tells it "you are E.V, act like this."

Claude answers

Claude sends back an answer as text.
The harness passes that answer back to your browser.
Your browser shows it in the chat window.

Remembering the conversation

Each chat gets an ID number.
When you send a follow-up message, the harness tells Claude "continue this same conversation."
That's how it remembers what you just said, within one chat session.
It does NOT remember across different chat sessions yet — that's a future feature.

Why it's free

You're not paying per message.
You're just using the Claude subscription you already pay for (or a free trial), the same way Claude Code uses it.
No cloud servers, no hosting fees — everything runs on your own machine.

What's built so far

Just the basic chat. That's "Phase 1."
Memory, calendar, task lists, voice, and research help are planned but not built yet.

The files, in plain terms

CLAUDE.md = E.V's personality and instructions.
harness/ = the Python program that connects your browser to Claude.
web/ = the actual chat webpage you see.
docs/ = explanations of how it all fits together and what's next.

## Quickstart

```bash
./scripts/setup.sh
./scripts/run_dev.sh
```

Then open `http://localhost:8765`. Full steps and troubleshooting: [`docs/SETUP.md`](docs/SETUP.md).

## Status

Live: text chat, creating files (documents/code/generated images via `workspace/`), and Todoist/Google Calendar/Canvas integrations (each optional — set up whichever you want in [`docs/SETUP.md`](docs/SETUP.md)). Not yet built: memory across separate conversations, voice, and proactive nudges — see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for what's next.

## License

GPLv2 — see [`LICENSE`](LICENSE).
