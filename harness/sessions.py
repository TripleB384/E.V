"""Maps a browser-facing conversation id to a Claude Code session id.

Kept in-memory: this is a single-user local dev server, not a multi-tenant
service, so a process-wide dict is enough and simpler than a database for
this alone (durable cross-session memory is a separate concern — see Phase 2
in docs/ARCHITECTURE.md, backed by memory/ev.db).
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field


@dataclass
class ConversationState:
    claude_session_id: str | None = None
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)


class SessionStore:
    def __init__(self) -> None:
        self._conversations: dict[str, ConversationState] = {}

    def get(self, conversation_id: str) -> ConversationState:
        if conversation_id not in self._conversations:
            self._conversations[conversation_id] = ConversationState()
        return self._conversations[conversation_id]


# Process-wide singleton.
store = SessionStore()
