"""E.V's local web server: serves the chat UI and proxies turns to Claude Code.

Run via scripts/run_dev.sh (which wraps `uvicorn harness.server:app`), from
the repo root so imports and Claude Code's own cwd-relative config loading
both resolve correctly.
"""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from harness.claude_client import ClaudeCLIError, ClaudeCLINotFound, run_prompt
from harness.sessions import store

WEB_DIR = Path(__file__).resolve().parent.parent / "web"

app = FastAPI(title="E.V")


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    conversation_id: str


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    if not req.message.strip():
        raise HTTPException(400, "message must not be empty")

    conversation_id = req.conversation_id or str(uuid.uuid4())
    state = store.get(conversation_id)

    async with state.lock:
        try:
            reply = await run_prompt(req.message, resume_session_id=state.claude_session_id)
        except ClaudeCLINotFound as exc:
            raise HTTPException(500, str(exc)) from exc
        except ClaudeCLIError as exc:
            detail = f"Claude Code call failed: {exc}"
            if exc.stderr:
                detail += f"\n{exc.stderr}"
            raise HTTPException(502, detail) from exc

        if reply.session_id:
            state.claude_session_id = reply.session_id

    return ChatResponse(reply=reply.text, conversation_id=conversation_id)


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}
