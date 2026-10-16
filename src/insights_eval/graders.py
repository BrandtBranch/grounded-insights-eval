from __future__ import annotations

from dataclasses import dataclass, field

from .models import Case, Extraction, Verdict
from .text import covers, is_interviewee_quote, overlaps


@dataclass
class CaseResult:
    case_id: str
    expect_none: bool
    n_insights: int
    unfaithful_quotes: list[str] = field(default_factory=list)
    planted_total: int = 0
    planted_found: list[str] = field(default_factory=list)
    planted_missed: list[str] = field(default_factory=list)
    judged: int = 0
    judged_supported: int = 0  # analyst standard: supported or a fair inference
    judged_strict: int = 0  # strict standard: fully supported only
    unsupported_claims: list[str] = field(default_factory=list)
    inference_claims: list[str] = field(default_factory=list)
    has_distractors: bool = False
    distracted: int = 0  # insights quoted from filler, not from any planted evidence

    @property
    def n_faithful(self) -> int:
        return self.n_insights - len(self.unfaithful_quotes)

    @property
    def false_positive(self) -> bool:
        """The extractor produced insights for a transcript that holds none."""
        return self.expect_none and self.n_insights > 0


def grade_case(case: Case, extraction: Extraction, verdicts: list[Verdict | None] | None = None) -> CaseResult:
    """Grade one extraction.

    `verdicts` is aligned with `extraction.insights`; None means the insight was not judged.
    """
    insights = extraction.insights
    result = CaseResult(case_id=case.id, expect_none=case.expect_none, n_insights=len(insights))

    for insight in insights:
        if not is_interviewee_quote(insight.quote, case.transcript):
            result.unfaithful_quotes.append(insight.quote)

    result.planted_total = len(case.planted)
    for planted in case.planted:
        hit = any(covers(span, i.quote) for span in planted.evidence for i in insights)
        (result.planted_found if hit else result.planted_missed).append(planted.id)

    if case.distractors and case.planted:
        result.has_distractors = True
        for insight in insights:
            on_target = any(covers(span, insight.quote) or overlaps(span, insight.quote) for p in case.planted for span in p.evidence)
            if not on_target and any(overlaps(d, insight.quote) for d in case.distractors):
                result.distracted += 1

    for insight, verdict in zip(insights, verdicts or [None] * len(insights)):
        if verdict is None:
            continue
        result.judged += 1
        if verdict.label == "supported":
            result.judged_strict += 1
        elif verdict.label == "inference":
            result.inference_claims.append(insight.claim)
        if verdict.label == "unsupported":
            result.unsupported_claims.append(insight.claim)
        else:
            result.judged_supported += 1

    return result


def _rate(num: int, den: int) -> float | None:
    return num / den if den else None


def aggregate(results: list[CaseResult]) -> dict[str, float | int | None]:
    """Pool case results into headline metrics.

    faithfulness: share of all extracted quotes that appear verbatim in the interviewee's turns.
    recall: share of planted insights that some extracted quote covers.
    false_positive_rate: share of no-insight transcripts where anything was extracted.
    distraction_rate: share of insights, in transcripts with filler, that were quoted from the filler.
    judge_support: share of judged insights that are supported or a fair inference (analyst standard).
    judge_strict: share of judged insights fully supported, with no added inference.
    """
    none_cases = [r for r in results if r.expect_none]
    noisy = [r for r in results if r.has_distractors]
    return {
        "distraction_rate": _rate(sum(r.distracted for r in noisy), sum(r.n_insights for r in noisy)),
        "cases": len(results),
        "insights": sum(r.n_insights for r in results),
        "faithfulness": _rate(sum(r.n_faithful for r in results), sum(r.n_insights for r in results)),
        "recall": _rate(sum(len(r.planted_found) for r in results), sum(r.planted_total for r in results)),
        "false_positive_rate": _rate(sum(r.false_positive for r in none_cases), len(none_cases)),
        "judge_support": _rate(sum(r.judged_supported for r in results), sum(r.judged for r in results)),
        "judge_strict": _rate(sum(r.judged_strict for r in results), sum(r.judged for r in results)),
    }
