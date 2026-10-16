"""Optional LLM judge: is the claim backed by what the interviewee said?

A quote can be verbatim and still not support the claim it is attached to. The
deterministic check cannot see that, so a cheaper model judges it. The judge sees the
whole transcript, because a quote often depends on the interviewer's question.
"""
from __future__ import annotations

from typing import Any

from .extract import MAX_TOKENS, RefusalError
from .models import Insight, Verdict

DEFAULT_JUDGE_MODEL = "claude-haiku-4-5"

JUDGE_SYSTEM = """You check whether an analyst's claim is backed by an interviewee's words. You get the full transcript, the quote the analyst cited and the claim.

The quote may be missing the interviewer's question. Use the transcript to work out what the interviewee is referring to.

Choose one label:
- supported: the quote, read in the context of the transcript, backs every part of the claim.
- inference: every fact in the claim is backed by what the interviewee said, but the claim adds a conclusion or interpretation the interviewee did not state, one a reasonable consultant could draw.
- unsupported: the claim adds a fact, number, cause or scope that the interviewee did not state, or contradicts what they said."""
JUDGE_USER = "<transcript>\n{transcript}\n</transcript>\n\n<quote>\n{quote}\n</quote>\n\n<claim>\n{claim}\n</claim>"


def judge_insight(client: Any, model: str, insight: Insight, transcript: str) -> tuple[Verdict, dict[str, int]]:
    response = client.messages.parse(
        model=model,
        max_tokens=MAX_TOKENS,
        system=JUDGE_SYSTEM,
        messages=[{"role": "user", "content": JUDGE_USER.format(transcript=transcript, quote=insight.quote, claim=insight.claim)}],
        output_format=Verdict,
    )
    if response.stop_reason == "refusal":
        raise RefusalError("judge refused the request")
    usage = {"input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens}
    return response.parsed_output, usage
