import json
import subprocess
from types import SimpleNamespace

import pytest

from insights_eval import claude_code
from insights_eval.claude_code import ClaudeCodeClient, ClaudeCodeError, find_claude_exe
from insights_eval.models import Extraction, Verdict


def _proc(payload=None, rc=0, stdout=None, stderr=""):
    out = stdout if stdout is not None else json.dumps(payload)
    return SimpleNamespace(returncode=rc, stdout=out, stderr=stderr)


GOOD = {
    "is_error": False,
    "stop_reason": "tool_use",
    "structured_output": {"insights": [{"claim": "c", "quote": "a quote that is long enough"}]},
    "usage": {"input_tokens": 2, "cache_creation_input_tokens": 100, "cache_read_input_tokens": 50, "output_tokens": 7},
}


@pytest.fixture
def calls(monkeypatch):
    seen = []

    def install(*responses):
        queue = list(responses)

        def fake_run(cmd, **kwargs):
            seen.append((cmd, kwargs))
            response = queue.pop(0)
            if isinstance(response, Exception):
                raise response
            return response

        monkeypatch.setattr(claude_code.subprocess, "run", fake_run)
        return seen

    return install


def _client(**kw):
    return ClaudeCodeClient(exe="fake-claude", **kw)


def _parse(client, schema=Extraction, model="claude-opus-5-5"):
    return client.messages.parse(model=model, max_tokens=1, system="sys", messages=[{"role": "user", "content": "the transcript"}], output_format=schema)


def test_parse_returns_validated_output_and_summed_usage(calls):
    seen = calls(_proc(GOOD))
    result = _parse(_client())
    assert result.parsed_output.insights[0].claim == "c"
    assert result.stop_reason == "end_turn"
    assert (result.usage.input_tokens, result.usage.output_tokens) == (152, 7)
    cmd, kwargs = seen[0]
    assert kwargs["input"] == "the transcript"  # the prompt goes through stdin, not the command line
    assert "--tools" in cmd and cmd[cmd.index("--tools") + 1] == ""
    assert cmd[cmd.index("--model") + 1] == "claude-opus-5-5"
    assert json.loads(cmd[cmd.index("--json-schema") + 1])["type"] == "object"


def test_effort_is_passed_except_for_haiku(calls):
    seen = calls(_proc(GOOD), _proc(GOOD))
    client = _client(effort="low")
    _parse(client, model="claude-opus-5-5")
    _parse(client, model="claude-haiku-4-5")
    assert "--effort" in seen[0][0] and "--effort" not in seen[1][0]


def test_falls_back_to_the_result_text_when_structured_output_is_missing(calls):
    payload = dict(GOOD, structured_output=None, result=json.dumps({"label": "supported", "reason": "r"}))
    calls(_proc(payload))
    assert _parse(_client(), schema=Verdict).parsed_output.label == "supported"


def test_retries_once_then_succeeds(calls):
    seen = calls(_proc(rc=1, stderr="boom"), _proc(GOOD))
    assert _parse(_client(retries=1)).parsed_output.insights
    assert len(seen) == 2


def test_gives_up_after_retries_with_a_clear_error(calls):
    calls(subprocess.TimeoutExpired("x", 1), _proc(dict(GOOD, is_error=True, api_error_status=429, result="rate limited")))
    with pytest.raises(ClaudeCodeError, match="429"):
        _parse(_client(retries=1))


def test_refusal_is_reported(calls):
    calls(_proc(dict(GOOD, stop_reason="refusal")))
    assert _parse(_client()).stop_reason == "refusal"


def test_find_exe_prefers_env_then_path_then_newest_bundled(monkeypatch, tmp_path):
    monkeypatch.setenv("CLAUDE_CODE_EXE", "from-env")
    assert find_claude_exe() == "from-env"
    monkeypatch.delenv("CLAUDE_CODE_EXE")
    monkeypatch.setattr(claude_code.shutil, "which", lambda name: "from-path")
    assert find_claude_exe() == "from-path"
    monkeypatch.setattr(claude_code.shutil, "which", lambda name: None)
    for version in ("2.1.9", "2.1.10", "2.1.284"):
        (tmp_path / "Claude" / "claude-code" / version).mkdir(parents=True)
        (tmp_path / "Claude" / "claude-code" / version / "claude.exe").write_text("")
    monkeypatch.setenv("APPDATA", str(tmp_path))
    assert "2.1.284" in find_claude_exe()
