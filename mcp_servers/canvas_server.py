"""MCP server: read-only upcoming-assignment lookup via the Canvas LMS API.

Needs CANVAS_BASE_URL (your school's Canvas URL, e.g.
https://university.instructure.com) and CANVAS_ACCESS_TOKEN (Canvas ->
Account -> Settings -> New Access Token) in .env. Some schools block
student self-service token creation — if yours does, this integration
just stays unconfigured; check_deadlines still works from other sources.
See docs/SETUP.md and docs/RISKS.md.

No write tools here on purpose: assignment data is the institution's, not
something E.V should ever be creating or editing.
"""

from __future__ import annotations

import datetime
import os

import requests

from mcp.server.mcpserver import MCPServer

app = MCPServer("canvas")

TIMEOUT_SECONDS = 15


def _base_url() -> str:
    return os.environ.get("CANVAS_BASE_URL", "").rstrip("/")


def _token() -> str:
    return os.environ.get("CANVAS_ACCESS_TOKEN", "")


def _not_configured() -> str:
    return (
        "Canvas isn't set up yet: add CANVAS_BASE_URL and CANVAS_ACCESS_TOKEN to .env "
        "— see docs/SETUP.md. If your school blocks student access-token creation, "
        "skip this one; check_deadlines still works from calendar/tasks."
    )


@app.tool()
def list_upcoming_assignments(days: int = 14) -> str:
    """List Canvas assignments/quizzes due in the next N days (default 14)."""
    base_url, token = _base_url(), _token()
    if not base_url or not token:
        return _not_configured()

    start = datetime.datetime.utcnow()
    end = start + datetime.timedelta(days=days)

    try:
        resp = requests.get(
            f"{base_url}/api/v1/planner/items",
            headers={"Authorization": f"Bearer {token}"},
            params={
                "start_date": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "end_date": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "per_page": 50,
            },
            timeout=TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        return f"Couldn't reach Canvas: {exc}"

    items = resp.json()
    assignments = [i for i in items if i.get("plannable_type") in ("assignment", "quiz")]
    if not assignments:
        return f"No assignments or quizzes due in the next {days} days."

    lines = []
    for item in assignments:
        plannable = item.get("plannable") or {}
        due = plannable.get("due_at", "unknown due date")
        title = plannable.get("title", "(untitled)")
        course = item.get("context_name", "")
        lines.append(f"- {due}: {title} ({course})")
    return "\n".join(lines)


if __name__ == "__main__":
    app.run()
