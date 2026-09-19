---
name: capture-task
description: Turn a natural-language request into a task in Todoist. Use when the user says things like "remind me to...", "add a task to...", "I need to...", or otherwise describes something to do without explicitly saying "add a task."
---

# Capture task

1. Extract the actual task from what the user said — rephrase into a short, clear action item rather than pasting their sentence verbatim if it's rambling.
2. If they mentioned a time or date ("by Friday", "tomorrow"), pass it straight through as `due_string` to the `tasks` tool's `add_task` — Todoist parses natural language due dates itself, so don't try to convert it to a strict date format first.
3. Confirm briefly what was added ("Added: <task>, due <when>") — don't over-explain.
4. If tasks aren't configured yet, say so briefly and offer to just note it in this reply instead of losing it.
