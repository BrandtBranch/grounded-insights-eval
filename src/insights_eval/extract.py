"""Extraction strategies: three ways of prompting for grounded insights.

Each strategy takes a transcript and returns (Extraction, usage). The Anthropic client
is passed in, so tests can substitute a fake.
"""
from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from .models import Extraction, Insight, KeepList

DEFAULT_MODEL = "claude-opus-5-5"
MAX_TOKENS = 8000

Usage = dict[str, int]
Strategy = Callable[[Any, str, str], tuple[Extraction, Usage]]


class RefusalError(RuntimeError):
    pass


def _parse(client: Any, model: str, system: str, user: str, schema: type, usage: Usage):
    response = client.messages.parse(
        model=model,
        max_tokens=MAX_TOKENS,
        system=system,
        messages=[{"role": "user", "content": user}],
        output_format=schema,
    )
    if response.stop_reason == "refusal":
        raise RefusalError("model refused the request")
    usage["input_tokens"] += response.usage.input_tokens
    usage["output_tokens"] += response.usage.output_tokens
    return response.parsed_output


def _new_usage() -> Usage:
    return {"input_tokens": 0, "output_tokens": 0}


NAIVE_SYSTEM = "You help consultants analyse stakeholder interviews."
NAIVE_USER = "Extract the key insights from this interview transcript.\n\n<transcript>\n{transcript}\n</transcript>"

GROUNDED_SYSTEM = """You help consultants analyse stakeholder interviews. Your output is only useful if every insight can be traced back to the transcript.

Rules:
- An insight is a specific finding the interviewee stated: a cause, a number, a decision, a constraint, an owner or a contradiction. Generic themes, buzzwords and pleasantries are not insights.
- Base each claim only on what the interviewee said. Do not infer causes, add numbers or add recommendations they did not state.
- The quote must be copied character for character from the interviewee's words. It must be one contiguous passage, or several passages joined with an ellipsis (...). Never paraphrase it, and never quote the interviewer.
- When the interviewee contradicts themselves, record the contradiction as its own insight and quote both sides.
- If the transcript holds no real insight, return an empty list. An empty list is a correct answer. Do not pad."""
GROUNDED_USER = "Extract the grounded insights from this interview transcript.\n\n<transcript>\n{transcript}\n</transcript>"

VERIFY_SYSTEM = """You audit candidate insights extracted from an interview transcript. Keep an insight only if (1) its quote appears in the transcript exactly as written and is something the interviewee said, and (2) the quote on its own fully supports the claim, with nothing added in the claim that the interviewee did not say. Drop everything else."""
VERIFY_ANALYST_SYSTEM = """You audit candidate insights extracted from an interview transcript. Keep an insight if (1) its quote appears in the transcript exactly as written and is something the interviewee said, and (2) every fact in the claim is backed by what the interviewee said, reading the quote in the context of the whole transcript. The quote may leave out the interviewer's question or a neighbouring sentence, and that is fine. A claim may also state a conclusion the interviewee did not spell out, as long as it follows directly from what they said and a reasonable consultant would draw it. Drop an insight only if its claim adds a fact, number, cause or scope the interviewee did not state, contradicts them, or attributes to them something only the interviewer said."""
VERIFY_USER = """<transcript>
{transcript}
</transcript>

<candidates>
{candidates}
</candidates>

Return the zero-based indexes of the candidates to keep."""


def naive(client: Any, model: str, transcript: str) -> tuple[Extraction, Usage]:
    usage = _new_usage()
    return _parse(client, model, NAIVE_SYSTEM, NAIVE_USER.format(transcript=transcript), Extraction, usage), usage


def grounded(client: Any, model: str, transcript: str) -> tuple[Extraction, Usage]:
    usage = _new_usage()
    return _parse(client, model, GROUNDED_SYSTEM, GROUNDED_USER.format(transcript=transcript), Extraction, usage), usage


def _verify_with(system: str, client: Any, model: str, transcript: str) -> tuple[Extraction, Usage]:
    usage = _new_usage()
    draft = _parse(client, model, GROUNDED_SYSTEM, GROUNDED_USER.format(transcript=transcript), Extraction, usage)
    if not draft.insights:
        return draft, usage
    candidates = json.dumps([i.model_dump() for i in draft.insights], indent=2)
    keep = _parse(client, model, system, VERIFY_USER.format(transcript=transcript, candidates=candidates), KeepList, usage)
    kept: list[Insight] = [draft.insights[i] for i in sorted(set(keep.keep)) if 0 <= i < len(draft.insights)]
    return Extraction(insights=kept), usage


def extract_then_verify(client: Any, model: str, transcript: str) -> tuple[Extraction, Usage]:
    """Grounded extraction, then a pass that keeps only insights whose quote alone fully supports the claim."""
    return _verify_with(VERIFY_SYSTEM, client, model, transcript)


def extract_then_verify_analyst(client: Any, model: str, transcript: str) -> tuple[Extraction, Usage]:
    """Grounded extraction, then a pass that keeps fair inferences and drops only claims that add facts."""
    return _verify_with(VERIFY_ANALYST_SYSTEM, client, model, transcript)


STRATEGIES: dict[str, Strategy] = {
    "naive": naive,
    "grounded": grounded,
    "verify": extract_then_verify,
    "verify_analyst": extract_then_verify_analyst,
}
