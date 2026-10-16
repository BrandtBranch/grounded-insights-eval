from __future__ import annotations

from types import SimpleNamespace

import pytest

from insights_eval.models import Extraction, Insight, KeepList, Verdict


class FakeClient:
    """Stands in for anthropic.Anthropic. `script` maps a schema class to a callable(user_text) -> parsed."""

    def __init__(self, script):
        self.script = script
        self.calls = 0
        self.messages = SimpleNamespace(parse=self._parse)

    def _parse(self, *, model, max_tokens, system, messages, output_format):
        self.calls += 1
        parsed = self.script[output_format](messages[0]["content"])
        return SimpleNamespace(
            parsed_output=parsed,
            stop_reason="end_turn",
            usage=SimpleNamespace(input_tokens=10, output_tokens=5),
        )


@pytest.fixture
def make_client():
    return FakeClient


__all__ = ["FakeClient", "Extraction", "Insight", "KeepList", "Verdict"]
