from __future__ import annotations

import json
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .extract import STRATEGIES
from .graders import CaseResult, aggregate, grade_case
from .judge import judge_insight
from .models import Case, Extraction, Verdict
from .text import is_interviewee_quote


def _run_one(client: Any, case: Case, strategy: str, model: str, judge_model: str | None):
    extraction, usage = STRATEGIES[strategy](client, model, case.transcript)
    verdicts: list[Verdict | None] = []
    for insight in extraction.insights:
        # A fabricated quote cannot support anything, so only genuine interviewee quotes are judged.
        if judge_model and is_interviewee_quote(insight.quote, case.transcript):
            verdict, judge_usage = judge_insight(client, judge_model, insight, case.transcript)
            usage["judge_input_tokens"] = usage.get("judge_input_tokens", 0) + judge_usage["input_tokens"]
            usage["judge_output_tokens"] = usage.get("judge_output_tokens", 0) + judge_usage["output_tokens"]
            verdicts.append(verdict)
        else:
            verdicts.append(None)
    return grade_case(case, extraction, verdicts), extraction, usage


def run_eval(
    client: Any,
    cases: list[Case],
    strategies: list[str],
    model: str,
    judge_model: str | None = None,
    workers: int = 4,
) -> dict[str, Any]:
    """Run every strategy on every case and return per-case results plus aggregates."""
    out: dict[str, Any] = {"model": model, "judge_model": judge_model, "strategies": {}, "errors": []}

    done = {"n": 0}
    lock = threading.Lock()

    def attempt(case: Case, strategy: str):
        try:
            outcome = _run_one(client, case, strategy, model, judge_model)
            status = "ok"
        except Exception as exc:  # one failed call should not lose the rest of a long run
            outcome = f"{type(exc).__name__}: {exc}"
            status = "FAILED"
        with lock:
            done["n"] += 1
            print(f"[{strategy}] {done['n']}/{len(cases)} {case.id} {status}", file=sys.stderr, flush=True)
        return outcome

    for strategy in strategies:
        done["n"] = 0
        with ThreadPoolExecutor(max_workers=workers) as pool:
            attempts = list(pool.map(lambda c: attempt(c, strategy), cases))
        failed = [(c.id, a) for c, a in zip(cases, attempts) if isinstance(a, str)]
        if len(failed) == len(cases):
            raise RuntimeError(f"every case failed for strategy {strategy!r}; first error: {failed[0][1]}")
        out["errors"] += [{"strategy": strategy, "case_id": cid, "error": err} for cid, err in failed]
        runs = [a for a in attempts if not isinstance(a, str)]
        results: list[CaseResult] = [r for r, _, _ in runs]
        tokens: dict[str, int] = {}
        for _, _, usage in runs:
            for key, value in usage.items():
                tokens[key] = tokens.get(key, 0) + value
        out["strategies"][strategy] = {
            "aggregate": aggregate(results),
            "tokens": tokens,
            "cases": [asdict(r) | {"extraction": ext.model_dump()} for r, ext, _ in runs],
        }
    return out


def _pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.0%}"


def render_report(results: dict[str, Any]) -> str:
    """Markdown report: headline table, then the concrete failures behind the numbers."""
    judged = bool(results["judge_model"])
    lines = [
        "# Results",
        "",
        f"Extractor: `{results['model']}`" + (f" | Judge: `{results['judge_model']}`" if judged else "") + (f" | Backend: `{results['backend']}`" if results.get("backend") else ""),
        "",
        "| Strategy | Faithfulness | Recall | False-positive rate | Distraction rate | " + ("Judge (analyst) | Judge (strict) | " if judged else "") + "Insights | Output tokens |",
        "|---|---|---|---|---|" + ("---|---|" if judged else "") + "---|---|",
    ]
    for name, data in results["strategies"].items():
        agg = data["aggregate"]
        row = [name, _pct(agg["faithfulness"]), _pct(agg["recall"]), _pct(agg["false_positive_rate"]), _pct(agg["distraction_rate"])]
        if judged:
            row += [_pct(agg["judge_support"]), _pct(agg["judge_strict"])]
        row += [str(agg["insights"]), str(data["tokens"].get("output_tokens", 0))]
        lines.append("| " + " | ".join(row) + " |")

    lines += [
        "",
        "- **Faithfulness**: extracted quotes that appear verbatim in the transcript (deterministic).",
        "- **Recall**: planted insights that an extracted quote covers.",
        "- **False-positive rate**: transcripts with no real insight where the model extracted something anyway.",
        "- **Distraction rate**: insights, in transcripts that contain filler, that were quoted from the filler instead of the planted interview.",
    ]
    if judged:
        lines.append("- **Judge (analyst)**: verbatim insights judged supported or a fair inference (LLM judge, sees the transcript).")
        lines.append("- **Judge (strict)**: verbatim insights judged fully supported, with no added inference.")

    if results.get("errors"):
        lines += ["", "## Cases that failed to run (excluded from the numbers above)", ""]
        lines += [f"- `{e['strategy']}` / `{e['case_id']}`: {e['error']}" for e in results["errors"]]

    for name, data in results["strategies"].items():
        lines += ["", f"## Failures: {name}", ""]
        found_any = False
        for case in data["cases"]:
            for quote in case["unfaithful_quotes"]:
                lines.append(f"- `{case['case_id']}` fabricated quote: \"{quote}\"")
                found_any = True
            for planted_id in case["planted_missed"]:
                lines.append(f"- `{case['case_id']}` missed insight: `{planted_id}`")
                found_any = True
            quotes = {i["claim"]: i["quote"] for i in case["extraction"]["insights"]}
            for claim in case["unsupported_claims"]:
                lines.append(f"- `{case['case_id']}` claim not supported by its quote:")
                lines.append(f"  - claim: \"{claim}\"")
                lines.append(f"  - quote: \"{quotes.get(claim, '?')}\"")
                found_any = True
            for claim in case["inference_claims"]:
                lines.append(f"- `{case['case_id']}` claim adds an inference:")
                lines.append(f"  - claim: \"{claim}\"")
                lines.append(f"  - quote: \"{quotes.get(claim, '?')}\"")
                found_any = True
            if case.get("distracted"):
                lines.append(f"- `{case['case_id']}` {case['distracted']} insight(s) quoted from filler instead of the planted interview")
                found_any = True
            if case["expect_none"] and case["n_insights"]:
                lines.append(f"- `{case['case_id']}` extracted {case['n_insights']} insight(s) from a transcript with none")
                found_any = True
        if not found_any:
            lines.append("None.")
    return "\n".join(lines) + "\n"


def save(results: dict[str, Any], out_dir: str | Path) -> tuple[Path, Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "results.json"
    md_path = out_dir / "report.md"
    json_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    md_path.write_text(render_report(results), encoding="utf-8")
    return json_path, md_path


_JUDGE_KEYS = ("judged", "judged_supported", "judged_strict", "unsupported_claims", "inference_claims")


def regrade(results: dict[str, Any], cases: list[Case]) -> dict[str, Any]:
    """Re-score saved extractions with the current graders, without calling any model.

    Judge verdicts cannot be recomputed this way, so the saved judge figures are carried over.
    """
    by_id = {c.id: c for c in cases}
    for data in results["strategies"].values():
        rows = []
        for old in data["cases"]:
            row = asdict(grade_case(by_id[old["case_id"]], Extraction.model_validate(old["extraction"])))
            row.update({k: old[k] for k in _JUDGE_KEYS if k in old})
            rows.append(row | {"extraction": old["extraction"]})
        data["cases"] = rows
        data["aggregate"] = aggregate([CaseResult(**{k: v for k, v in row.items() if k != "extraction"}) for row in rows])
    results["regraded"] = True
    return results
