"""Run the eval through a logged-in Claude Code install instead of the Anthropic API.

No API key is needed: `claude -p` uses the login you already have. The class exposes the same
`messages.parse(...)` call the strategies use, so nothing else in the package changes.

Differences from the API backend that can affect results: Claude Code wraps the model in its own
harness (structured output arrives through an internal tool call, so a call takes two or three turns),
and `max_tokens` cannot be set. Record which backend produced a set of results.
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import subprocess
import tempfile
from types import SimpleNamespace
from typing import Any

DEFAULT_TIMEOUT = 900


def find_claude_exe() -> str:
    """Locate the Claude Code binary: $CLAUDE_CODE_EXE, then PATH, then the Claude desktop app's bundled copy."""
    explicit = os.environ.get("CLAUDE_CODE_EXE")
    if explicit:
        return explicit
    on_path = shutil.which("claude")
    if on_path:
        return on_path
    pattern = os.path.join(os.environ.get("APPDATA", ""), "Claude", "claude-code", "*", "claude.exe")
    bundled = glob.glob(pattern)
    if bundled:
        return max(bundled, key=lambda p: [int(x) if x.isdigit() else 0 for x in os.path.basename(os.path.dirname(p)).split(".")])
    raise FileNotFoundError("Claude Code not found. Install it, put `claude` on PATH, or set CLAUDE_CODE_EXE.")


class ClaudeCodeError(RuntimeError):
    pass


class ClaudeCodeClient:
    """Drop-in for the part of `anthropic.Anthropic` that this project uses: `client.messages.parse`."""

    def __init__(self, exe: str | None = None, effort: str | None = None, timeout: int = DEFAULT_TIMEOUT, retries: int = 1):
        self.exe = exe or find_claude_exe()
        self.effort = effort
        self.timeout = timeout
        self.retries = retries
        self.workdir = tempfile.mkdtemp(prefix="insights-eval-")  # empty folder, so no project instructions are picked up
        self.messages = SimpleNamespace(parse=self._parse)

    def _command(self, model: str, system: str, schema: dict[str, Any]) -> list[str]:
        cmd = [
            self.exe, "-p", "--output-format", "json",
            "--json-schema", json.dumps(schema),
            "--system-prompt", system,
            "--tools", "",
            "--model", model,
            "--no-session-persistence",
            "--setting-sources", "",
            "--strict-mcp-config",
            "--disable-slash-commands",
        ]
        if self.effort and "haiku" not in model:  # Haiku 4.5 does not take an effort setting
            cmd += ["--effort", self.effort]
        return cmd

    def _run(self, cmd: list[str], prompt: str) -> dict[str, Any]:
        last_error = ""
        for _ in range(self.retries + 1):
            try:
                proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, encoding="utf-8",
                                      timeout=self.timeout, cwd=self.workdir)
            except subprocess.TimeoutExpired:
                last_error = f"timed out after {self.timeout}s"
                continue
            if proc.returncode == 0:
                try:
                    data = json.loads(proc.stdout)
                except json.JSONDecodeError:
                    last_error = f"unreadable output: {proc.stdout[:200]!r}"
                    continue
                if not data.get("is_error"):
                    return data
                last_error = f"{data.get('api_error_status')}: {str(data.get('result'))[:200]}"
            else:
                last_error = f"exit code {proc.returncode}: {proc.stderr[:200] or proc.stdout[:200]}"
        raise ClaudeCodeError(last_error)

    def _parse(self, *, model: str, max_tokens: int, system: str, messages: list[dict[str, Any]], output_format: type):
        del max_tokens  # Claude Code has no per-call output cap
        data = self._run(self._command(model, system, output_format.model_json_schema()), messages[0]["content"])
        payload = data.get("structured_output")
        if payload is None:
            try:
                payload = json.loads(data.get("result") or "")
            except json.JSONDecodeError as exc:
                raise ClaudeCodeError(f"no structured output in response: {str(data.get('result'))[:200]!r}") from exc
        usage = data.get("usage", {})
        return SimpleNamespace(
            parsed_output=output_format.model_validate(payload),
            stop_reason="refusal" if data.get("stop_reason") == "refusal" else "end_turn",
            usage=SimpleNamespace(
                input_tokens=usage.get("input_tokens", 0) + usage.get("cache_creation_input_tokens", 0) + usage.get("cache_read_input_tokens", 0),
                output_tokens=usage.get("output_tokens", 0),
            ),
        )
