"""Thin subprocess wrapper around the `claude` CLI's headless mode.

This is deliberately the only place E.V talks to Claude. It never imports the
Claude Agent SDK and never touches the Anthropic Messages API — both are
metered products, separate from a claude.ai subscription. Instead it shells
out to the actual `claude` binary, authenticated via the user's own personal
`claude /login` (or `claude setup-token` for headless use), which is what
keeps this project on the free side of Anthropic's "ordinary use of Claude
Code" line. See docs/RISKS.md before changing this file.

Field names below (`result`, `session_id`, `is_error`, `subtype`) and flags
(`-p`, `--output-format json`, `--resume <id>`) were confirmed by hand
against a live `claude` CLI (version 2.1.278) rather than assumed — but CLI
output can change between versions, so if this starts breaking, the first
thing to do is re-run `claude -p "hi" --output-format json` by hand and diff
the shape against what's parsed here.
"""

from __future__ import annotations

import asyncio
import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_TIMEOUT_SECONDS = 120.0


class ClaudeCLINotFound(RuntimeError):
    """Raised when the `claude` binary isn't on PATH."""


class ClaudeCLIError(RuntimeError):
    """Raised when `claude -p` fails, times out, or returns unparsable output."""

    def __init__(self, message: str, stderr: str = ""):
        super().__init__(message)
        self.stderr = stderr


@dataclass
class ClaudeReply:
    text: str
    session_id: str
    is_error: bool
    subtype: str


def _claude_binary() -> str:
    binary = shutil.which("claude")
    if not binary:
        raise ClaudeCLINotFound(
            "The `claude` CLI was not found on PATH. Install Claude Code and run "
            "`claude /login` first (scripts/setup.sh does this for you) — see docs/SETUP.md."
        )
    return binary


async def run_prompt(
    prompt: str,
    *,
    resume_session_id: str | None = None,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> ClaudeReply:
    """Run one turn against Claude Code in headless mode and return the parsed reply.

    Runs with cwd=REPO_ROOT so Claude Code auto-loads this project's CLAUDE.md,
    .claude/settings.json, and (once it exists) .mcp.json on its own — callers
    never re-inject persona text or tool wiring by hand.
    """
    binary = _claude_binary()
    args = [binary, "-p", prompt, "--output-format", "json"]
    if resume_session_id:
        args += ["--resume", resume_session_id]

    # CLAUDE_CODE_OAUTH_TOKEN, if set in the environment (from `claude setup-token`),
    # is picked up by the CLI automatically; otherwise it falls back to the
    # credentials stored by an interactive `claude /login`.
    env = os.environ.copy()

    proc = await asyncio.create_subprocess_exec(
        *args,
        cwd=str(REPO_ROOT),
        env=env,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError as exc:
        proc.kill()
        await proc.wait()
        raise ClaudeCLIError(f"claude -p timed out after {timeout}s") from exc

    if proc.returncode != 0:
        raise ClaudeCLIError(
            f"claude -p exited with code {proc.returncode}",
            stderr=stderr.decode(errors="replace"),
        )

    try:
        payload = json.loads(stdout.decode())
    except json.JSONDecodeError as exc:
        raise ClaudeCLIError(f"Could not parse claude CLI output as JSON: {exc}") from exc

    return ClaudeReply(
        text=payload.get("result", ""),
        session_id=payload.get("session_id") or resume_session_id or "",
        is_error=bool(payload.get("is_error", False)),
        subtype=payload.get("subtype", "unknown"),
    )
