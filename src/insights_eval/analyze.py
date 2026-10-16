"""Break results down by transcript length, case kind and position, and correlate length with errors."""
from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

from .models import Case

BUCKETS = ["short (<300 words)", "medium (300-1200)", "long (>1200)"]
POSITION_ORDER = ["medium / middle", "medium / interleaved", "long / start", "long / middle", "long / end", "long / interleaved"]
MIN_POINTS_FOR_CORRELATION = 8


def bucket(words: int) -> str:
    if words < 300:
        return BUCKETS[0]
    return BUCKETS[1] if words <= 1200 else BUCKETS[2]


def _ranks(values: list[float]) -> list[float]:
    """Ranks starting at 1, with tied values sharing their average rank."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        for k in range(i, j + 1):
            ranks[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return ranks


def spearman(xs: list[float | None], ys: list[float | None]) -> float | None:
    """Spearman rank correlation, or None when there are too few points or no variation."""
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    if len(pairs) < MIN_POINTS_FOR_CORRELATION:
        return None
    rx, ry = _ranks([p[0] for p in pairs]), _ranks([p[1] for p in pairs])
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    sx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    sy = math.sqrt(sum((b - my) ** 2 for b in ry))
    if sx == 0 or sy == 0:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(rx, ry)) / (sx * sy)


def _rate(num: int, den: int) -> float | None:
    return num / den if den else None


def _rows(strategy_data: dict[str, Any], cases: dict[str, Case]) -> list[dict[str, Any]]:
    rows = []
    for c in strategy_data["cases"]:
        case = cases[c["case_id"]]
        rows.append({
            "id": case.id, "words": case.words, "kind": case.kind, "position": case.position,
            "expect_none": case.expect_none, "n": c["n_insights"],
            "faithful": c["n_insights"] - len(c["unfaithful_quotes"]),
            "planted": c["planted_total"], "found": len(c["planted_found"]),
            "judged": c["judged"], "strict": c["judged_strict"], "analyst": c["judged_supported"],
            "has_distractors": c.get("has_distractors", False), "distracted": c.get("distracted", 0),
        })
    return rows


def _pool(rows: list[dict[str, Any]]) -> dict[str, float | int | None]:
    none_rows = [r for r in rows if r["expect_none"]]
    noisy = [r for r in rows if r["has_distractors"]]
    return {
        "distraction": _rate(sum(r["distracted"] for r in noisy), sum(r["n"] for r in noisy)),
        "cases": len(rows),
        "recall": _rate(sum(r["found"] for r in rows), sum(r["planted"] for r in rows)),
        "faithfulness": _rate(sum(r["faithful"] for r in rows), sum(r["n"] for r in rows)),
        "strict": _rate(sum(r["strict"] for r in rows), sum(r["judged"] for r in rows)),
        "analyst": _rate(sum(r["analyst"] for r in rows), sum(r["judged"] for r in rows)),
        "fp": _rate(sum(r["n"] > 0 for r in none_rows), len(none_rows)),
        "insights": sum(r["n"] for r in rows),
    }


def _pct(v: float | None) -> str:
    return "-" if v is None else f"{v:.0%}"


def _table(title: str, groups: dict[str, list[dict[str, Any]]], order: list[str]) -> list[str]:
    lines = [f"**{title}**", "", "| Group | Cases | Recall | Faithfulness | Judge (strict) | Judge (analyst) | False-positive rate | Distraction rate | Insights |", "|---|---|---|---|---|---|---|---|---|"]
    for name in order:
        rows = groups.get(name)
        if not rows:
            continue
        p = _pool(rows)
        lines.append(f"| {name} | {p['cases']} | {_pct(p['recall'])} | {_pct(p['faithfulness'])} | {_pct(p['strict'])} | {_pct(p['analyst'])} | {_pct(p['fp'])} | {_pct(p['distraction'])} | {p['insights']} |")
    return lines + [""]


def render_analysis(results: dict[str, Any], cases: list[Case]) -> str:
    by_id = {c.id: c for c in cases}
    lines = ["# Analysis by length, kind and position", ""]
    judged = bool(results["judge_model"])
    corr_rows = []

    for strategy, data in results["strategies"].items():
        rows = _rows(data, by_id)
        lines += [f"## {strategy}", ""]

        by_bucket: dict[str, list] = defaultdict(list)
        by_kind: dict[str, list] = defaultdict(list)
        by_position: dict[str, list] = defaultdict(list)
        for r in rows:
            by_bucket[bucket(r["words"])].append(r)
            by_kind[r["kind"]].append(r)
            if r["kind"] == "padded":
                by_position[f"{'long' if r['words'] > 1200 else 'medium'} / {r['position']}"].append(r)
        lines += _table("By transcript length", by_bucket, BUCKETS)
        lines += _table("By case kind", by_kind, sorted(by_kind))
        lines += _table(
            "Padded transcripts, by length and layout (block = filler before and after the planted interview; interleaved = filler between its turns)",
            by_position, POSITION_ORDER,
        )

        words = [float(r["words"]) for r in rows]
        corr_rows.append((
            strategy, len(rows),
            spearman(words, [_rate(r["found"], r["planted"]) for r in rows]),
            spearman(words, [_rate(r["faithful"], r["n"]) for r in rows]),
            spearman(words, [_rate(r["strict"], r["judged"]) for r in rows]) if judged else None,
            spearman(words, [float(r["n"]) if r["expect_none"] else None for r in rows]),
            spearman(words, [_rate(r["distracted"], r["n"]) if r["has_distractors"] else None for r in rows]),
        ))

    lines += [
        "## Does length correlate with errors?", "",
        "Spearman rank correlation between a transcript's word count and its per-case score. "
        "Positive means the score rises with length; negative means it falls. "
        f"A dash means fewer than {MIN_POINTS_FOR_CORRELATION} usable cases or no variation in the score.", "",
        "| Strategy | Cases | Recall | Faithfulness | Judge (strict) | Insights from empty transcripts | Distraction |", "|---|---|---|---|---|---|---|",
    ]
    for strategy, n, rec, faith, strict, empty, distraction in corr_rows:
        fmt = lambda v: "-" if v is None else f"{v:+.2f}"  # noqa: E731
        lines.append(f"| {strategy} | {n} | {fmt(rec)} | {fmt(faith)} | {fmt(strict)} | {fmt(empty)} | {fmt(distraction)} |")
    lines += [
        "",
        "Treat these as hints, not findings. Each strategy has a few dozen cases, many scores sit at 100%, "
        "and the padded cases share the same five core interviews, so they are not independent.",
    ]
    return "\n".join(lines) + "\n"
