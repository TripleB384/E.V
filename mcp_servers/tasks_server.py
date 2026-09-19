"""MCP server: task capture and lookup via Todoist's REST API v2.

Needs a free Todoist account and a personal API token (Todoist Settings ->
Integrations -> Developer) in .env as TODOIST_API_TOKEN. See docs/SETUP.md.

Tools return plain strings, including for "not configured yet" and HTTP
errors — never raise — so a missing token degrades to a clear message
instead of an unhandled exception inside the MCP framework.
"""

from __future__ import annotations

import os

import requests

from mcp.server.mcpserver import MCPServer

app = MCPServer("tasks")

BASE_URL = "https://api.todoist.com/rest/v2"
TIMEOUT_SECONDS = 15


def _token() -> str:
    return os.environ.get("TODOIST_API_TOKEN", "")


def _not_configured() -> str:
    return (
        "Tasks aren't set up yet: add TODOIST_API_TOKEN to .env "
        "(free account, token from Todoist Settings -> Integrations -> Developer) "
        "— see docs/SETUP.md."
    )


def _headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {_token()}"}


@app.tool()
def list_tasks() -> str:
    """List your active Todoist tasks, with due dates where set."""
    if not _token():
        return _not_configured()
    try:
        resp = requests.get(f"{BASE_URL}/tasks", headers=_headers(), timeout=TIMEOUT_SECONDS)
        resp.raise_for_status()
    except requests.RequestException as exc:
        return f"Couldn't reach Todoist: {exc}"

    tasks = resp.json()
    if not tasks:
        return "No active tasks."

    lines = []
    for t in tasks:
        due = t.get("due") or {}
        due_str = due.get("string", "no due date")
        lines.append(f"- [{t['id']}] {t['content']} (due: {due_str})")
    return "\n".join(lines)


@app.tool()
def add_task(content: str, due_string: str = "") -> str:
    """Add a new task. due_string accepts natural language like 'tomorrow at 5pm' — Todoist parses it, don't reformat it yourself."""
    if not _token():
        return _not_configured()

    body: dict[str, str] = {"content": content}
    if due_string:
        body["due_string"] = due_string

    try:
        resp = requests.post(f"{BASE_URL}/tasks", headers=_headers(), json=body, timeout=TIMEOUT_SECONDS)
        resp.raise_for_status()
    except requests.RequestException as exc:
        return f"Couldn't add task: {exc}"

    task = resp.json()
    due = task.get("due") or {}
    due_str = f", due {due['string']}" if due.get("string") else ""
    return f"Added task [{task['id']}]: {task['content']}{due_str}"


@app.tool()
def complete_task(task_id: str) -> str:
    """Mark a task complete, by the id shown in list_tasks."""
    if not _token():
        return _not_configured()

    try:
        resp = requests.post(f"{BASE_URL}/tasks/{task_id}/close", headers=_headers(), timeout=TIMEOUT_SECONDS)
        resp.raise_for_status()
    except requests.RequestException as exc:
        return f"Couldn't complete task {task_id}: {exc}"

    return f"Marked task {task_id} complete."


if __name__ == "__main__":
    app.run()
