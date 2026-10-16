import importlib.util
from pathlib import Path

import pytest

from insights_eval.analyze import BUCKETS, bucket, render_analysis, spearman
from insights_eval.models import Extraction, Insight, KeepList, Verdict, load_cases
from insights_eval.runner import run_eval
from insights_eval.text import is_verbatim

ROOT = Path(__file__).resolve().parent.parent
ALL_FILES = [ROOT / "data" / n for n in ("cases.json", "cases_hard.json", "cases_long.json")]


def test_spearman_perfect_reversed_and_degenerate():
    xs = [1, 2, 3, 4, 5, 6, 7, 8]
    assert spearman(xs, [10, 20, 30, 40, 50, 60, 70, 80]) == pytest.approx(1.0)
    assert spearman(xs, [8, 7, 6, 5, 4, 3, 2, 1]) == pytest.approx(-1.0)
    assert spearman(xs, [5] * 8) is None  # no variation
    assert spearman([1, 2, 3], [1, 2, 3]) is None  # too few points


def test_spearman_handles_ties_and_skips_missing_values():
    xs = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    ys = [1, 1, 2, 2, 3, 3, 4, 4, None]
    assert 0.9 < spearman(xs, ys) <= 1.0


def test_bucket_boundaries():
    assert bucket(299) == BUCKETS[0] and bucket(300) == BUCKETS[1]
    assert bucket(1200) == BUCKETS[1] and bucket(1201) == BUCKETS[2]


def test_all_case_files_load_with_unique_ids_and_verbatim_evidence():
    cases = load_cases(*ALL_FILES)
    assert len(cases) == 45
    for case in cases:
        assert bool(case.planted) != case.expect_none, case.id
        for planted in case.planted:
            for span in planted.evidence:
                assert is_verbatim(span, case.transcript), f"{case.id}/{planted.id}: {span!r}"


def test_padded_cases_keep_the_core_and_are_much_longer():
    cases = {c.id: c for c in load_cases(*ALL_FILES)}
    base = cases["retail_stockouts"]
    for suffix, position in [("long_start", "start"), ("long_middle", "middle"), ("long_end", "end")]:
        padded = cases[f"retail_stockouts__{suffix}"]
        assert padded.kind == "padded" and padded.group == base.id and padded.position == position
        assert base.transcript in padded.transcript
        assert padded.words > 10 * base.words
    assert cases["retail_stockouts__long_start"].transcript.startswith(base.transcript)
    assert cases["retail_stockouts__long_end"].transcript.endswith(base.transcript)


def test_generator_is_deterministic():
    spec = importlib.util.spec_from_file_location("make_long_cases", ROOT / "scripts" / "make_long_cases.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    base = {c.id: c for c in load_cases(ROOT / "data" / "cases.json")}["saas_churn"]
    assert module.padded_case(base, "long", "middle", 2000) == module.padded_case(base, "long", "middle", 2000)


def test_analysis_renders_on_a_full_fake_run(make_client):
    cases = load_cases(*ALL_FILES)

    def extraction(user):
        # Quote the first planted span found in the transcript, if any, otherwise nothing
        for case in cases:
            for planted in case.planted:
                if planted.evidence[0] in user and case.transcript.split("\n")[0] in user:
                    return Extraction(insights=[Insight(claim="c", quote=planted.evidence[0])])
        return Extraction(insights=[])

    client = make_client({
        Extraction: extraction,
        KeepList: lambda _u: KeepList(keep=[0]),
        Verdict: lambda _u: Verdict(label="supported", reason="ok"),
    })
    results = run_eval(client, cases, ["grounded"], "m", judge_model="j", workers=2)
    text = render_analysis(results, cases)
    assert "By transcript length" in text and "By case kind" in text
    assert "Padded transcripts, by length and layout" in text and "| long / interleaved |" in text and "Distraction rate" in text
    assert "Does length correlate with errors?" in text
    for kind in ("padded", "negation", "buried", "empty_long"):
        assert f"| {kind} |" in text


def test_interleaved_cases_spread_filler_through_the_core_and_record_distractors():
    cases = {c.id: c for c in load_cases(*ALL_FILES)}
    base = cases["saas_churn"]
    inter = cases["saas_churn__long_interleaved"]
    assert inter.position == "interleaved" and inter.words > 10 * base.words
    assert inter.distractors and all(d in inter.transcript for d in inter.distractors)
    # Core questions survive in their original order, but with filler between them
    questions = [line for line in base.transcript.splitlines() if line.startswith("Interviewer:")]
    positions = [inter.transcript.index(q) for q in questions]
    assert positions == sorted(positions)
    assert not inter.transcript.startswith(base.transcript)
    # Every core answer is still present (an aside may follow it)
    answers = [line for line in base.transcript.splitlines() if not line.startswith("Interviewer:")]
    assert all(a in inter.transcript for a in answers)
