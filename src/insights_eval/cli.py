from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .analyze import render_analysis
from .extract import DEFAULT_MODEL, STRATEGIES
from .judge import DEFAULT_JUDGE_MODEL
from .models import load_cases
from .runner import regrade, render_report, run_eval, save
from .text import is_verbatim

DEFAULT_DATA = [Path("data/cases.json"), Path("data/cases_hard.json"), Path("data/cases_long.json")]


def _validate(cases_paths: list[Path]) -> int:
    cases = load_cases(*cases_paths)
    bad = 0
    for case in cases:
        for planted in case.planted:
            for span in planted.evidence:
                if not is_verbatim(span, case.transcript):
                    print(f"{case.id}/{planted.id}: evidence not verbatim: {span!r}")
                    bad += 1
    print(f"{len(cases)} cases checked, {bad} problems")
    return 1 if bad else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="insights-eval", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run strategies against the cases and write a report")
    run.add_argument("--cases", type=Path, nargs="+", default=DEFAULT_DATA)
    run.add_argument("--strategies", nargs="+", default=list(STRATEGIES), choices=list(STRATEGIES))
    run.add_argument("--model", default=DEFAULT_MODEL)
    run.add_argument("--judge", action="store_true", help="Also run the LLM judge on genuine interviewee quotes")
    run.add_argument("--judge-model", default=DEFAULT_JUDGE_MODEL)
    run.add_argument("--out", type=Path, default=Path("results"))
    run.add_argument("--workers", type=int, default=4)
    run.add_argument(
        "--backend", choices=["api", "claude-code"], default="claude-code",
        help="claude-code (default) uses your Claude Code login and needs no key. api uses ANTHROPIC_API_KEY and is billed to that key.",
    )
    run.add_argument("--effort", choices=["low", "medium", "high", "xhigh", "max"], help="claude-code backend only; not applied to Haiku")

    check = sub.add_parser("validate-data", help="Check that every planted evidence span is verbatim")
    check.add_argument("--cases", type=Path, nargs="+", default=DEFAULT_DATA)

    analyze = sub.add_parser("analyze", help="Break saved results down by length, kind and position")
    analyze.add_argument("results", type=Path, help="Path to a results.json written by `run`")
    analyze.add_argument("--cases", type=Path, nargs="+", default=DEFAULT_DATA)

    regr = sub.add_parser("regrade", help="Re-score saved results with the current graders, without calling any model")
    regr.add_argument("results", type=Path, help="Path to a results.json written by `run`")
    regr.add_argument("--cases", type=Path, nargs="+", default=DEFAULT_DATA)

    args = parser.parse_args(argv)
    if args.command == "regrade":
        backup = args.results.with_name("results.before-regrade.json")
        if not backup.exists():
            backup.write_text(args.results.read_text(encoding="utf-8"), encoding="utf-8")
        results = regrade(json.loads(args.results.read_text(encoding="utf-8")), load_cases(*args.cases))
        save(results, args.results.parent)
        print(render_report(results))
        print(f"Rescored {args.results} (original kept as {backup.name})")
        return 0
    if args.command == "validate-data":
        return _validate(args.cases)
    if args.command == "analyze":
        results = json.loads(args.results.read_text(encoding="utf-8"))
        text = render_analysis(results, load_cases(*args.cases))
        out_path = args.results.parent / "analysis.md"
        out_path.write_text(text, encoding="utf-8")
        print(text)
        print(f"Wrote {out_path}")
        return 0

    backend = args.backend
    if backend == "claude-code":
        from .claude_code import ClaudeCodeClient

        client = ClaudeCodeClient(effort=args.effort)
    else:
        import anthropic  # imported lazily so validate-data and analyze work without credentials

        client = anthropic.Anthropic()
    print(f"Backend: {backend}" + (" (billed to your API key)" if backend == "api" else " (uses your Claude Code login, no API key)"), file=sys.stderr, flush=True)
    cases = load_cases(*args.cases)
    results = run_eval(
        client, cases, args.strategies, args.model,
        judge_model=args.judge_model if args.judge else None, workers=args.workers,
    )
    results["backend"] = backend
    json_path, md_path = save(results, args.out)
    print(render_report(results))
    print(f"Wrote {json_path} and {md_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
