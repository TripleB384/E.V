"""MCP server: Google Calendar read/create via OAuth (desktop app flow).

One-time setup: download an OAuth client ID (Desktop app type) from Google
Cloud Console, save it as harness/.secrets/google_credentials.json. The
first call opens a browser for consent and caches a refresh token at
harness/.secrets/google_token.json — that first call has to happen with a
browser available (run scripts/run_dev.sh and trigger a calendar call from
the chat once, interactively), not from a truly headless/no-display context.
See docs/SETUP.md.

Google apps left in "Testing" publishing status get refresh tokens that
expire every 7 days — see docs/RISKS.md. This module doesn't special-case
that; an expired/invalid token just means the next call re-opens the
consent browser flow.
"""

from __future__ import annotations

import datetime
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from mcp.server.mcpserver import MCPServer

app = MCPServer("calendar")

SCOPES = ["https://www.googleapis.com/auth/calendar"]

REPO_ROOT = Path(__file__).resolve().parent.parent
SECRETS_DIR = REPO_ROOT / "harness" / ".secrets"
TOKEN_PATH = SECRETS_DIR / "google_token.json"
CREDENTIALS_PATH = SECRETS_DIR / "google_credentials.json"

_NOT_CONFIGURED = (
    f"Calendar isn't set up yet: save an OAuth client ID (Desktop app) from Google "
    f"Cloud Console as {CREDENTIALS_PATH} — see docs/SETUP.md."
)


def _get_service():
    """Returns a Calendar API service, or None if not configured yet."""
    if not CREDENTIALS_PATH.exists():
        return None

    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)
        SECRETS_DIR.mkdir(parents=True, exist_ok=True)
        TOKEN_PATH.write_text(creds.to_json())

    return build("calendar", "v3", credentials=creds)


@app.tool()
def list_upcoming_events(days: int = 7) -> str:
    """List calendar events in the next N days (default 7)."""
    service = _get_service()
    if service is None:
        return _NOT_CONFIGURED

    now = datetime.datetime.utcnow().isoformat() + "Z"
    later = (datetime.datetime.utcnow() + datetime.timedelta(days=days)).isoformat() + "Z"

    try:
        result = (
            service.events()
            .list(calendarId="primary", timeMin=now, timeMax=later, singleEvents=True, orderBy="startTime")
            .execute()
        )
    except HttpError as exc:
        return f"Couldn't reach Google Calendar: {exc}"

    events = result.get("items", [])
    if not events:
        return f"No events in the next {days} days."

    lines = []
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        lines.append(f"- {start}: {event.get('summary', '(no title)')}")
    return "\n".join(lines)


@app.tool()
def create_event(title: str, start_iso: str, end_iso: str) -> str:
    """Create a calendar event. start_iso/end_iso are local ISO 8601 datetimes, e.g. 2026-09-20T15:00:00."""
    service = _get_service()
    if service is None:
        return _NOT_CONFIGURED

    event = {"summary": title, "start": {"dateTime": start_iso}, "end": {"dateTime": end_iso}}
    try:
        created = service.events().insert(calendarId="primary", body=event).execute()
    except HttpError as exc:
        return f"Couldn't create the event: {exc}"

    return f"Created '{title}' — {created.get('htmlLink', '')}"


if __name__ == "__main__":
    app.run()
