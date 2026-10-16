from pathlib import Path

from insights_eval.models import Extraction, Insight, KeepList, Verdict, load_cases
from insights_eval.runner import render_report, run_eval
from insights_eval.text import is_verbatim

CASES_PATH = Path(__file__).resolve().parent.parent / "data" / "cases.json"


def test_case_ids_are_unique_and_every_planted_span_is_verbatim():
    cases = load_cases(CASES_PATH)
    assert len({c.id for c in cases}) == len(cases)
    for case in cases:
        assert bool(case.planted) != case.expect_none, f"{case.id}: expect_none must match planted"
        for planted in case.planted:
            for span in planted.evidence:
                assert is_verbatim(span, case.transcript), f"{case.id}/{planted.id}: {span!r}"


def test_pipeline_end_to_end_with_fake_client(make_client):
    cases = load_cases(CASES_PATH)
    first = cases[0]
    span = first.planted[0].evidence[0]

    def extraction(_user):
        # One real quote, one fabricated quote, on every transcript
        return Extraction(insights=[
            Insight(claim="real", quote=span if span in _user else "Honestly, the promo calendar"),
            Insight(claim="fake", quote="this sentence was never said by anybody"),
        ])

    client = make_client({
        Extraction: extraction,
        KeepList: lambda _u: KeepList(keep=[0]),
        Verdict: lambda _u: Verdict(label="supported", reason="ok"),
    })
    results = run_eval(client, cases, ["grounded", "verify"], "m", judge_model="j", workers=2)

    grounded = results["strategies"]["grounded"]["aggregate"]
    verify = results["strategies"]["verify"]["aggregate"]
    assert 0 < grounded["faithfulness"] < 1  # the fabricated quote is caught
    assert verify["faithfulness"] > grounded["faithfulness"]  # verify dropped it
    assert grounded["false_positive_rate"] == 1.0  # fake extracts on no-insight transcripts

    report = render_report(results)
    assert "| grounded |" in report and "fabricated quote" in report


def test_a_failing_case_is_recorded_and_the_run_continues(make_client):
    import pytest

    cases = load_cases(CASES_PATH)[:3]
    doomed = cases[1].transcript

    def extraction(user):
        if doomed in user:
            raise RuntimeError("rate limited")
        return Extraction(insights=[])

    client = make_client({Extraction: extraction})
    results = run_eval(client, cases, ["grounded"], "m", workers=1)
    assert [e["case_id"] for e in results["errors"]] == [cases[1].id]
    assert len(results["strategies"]["grounded"]["cases"]) == 2
    assert "failed to run" in render_report(results) and "rate limited" in render_report(results)

    everything_fails = make_client({Extraction: lambda user: (_ for _ in ()).throw(RuntimeError("down"))})
    with pytest.raises(RuntimeError, match="every case failed"):
        run_eval(everything_fails, cases, ["grounded"], "m", workers=1)


def test_regrade_reproduces_scores_and_picks_up_a_changed_grader(make_client):
    from insights_eval.runner import regrade

    cases = load_cases(CASES_PATH)[:3]
    span = cases[0].planted[0].evidence[0]
    client = make_client({Extraction: lambda user: Extraction(insights=[Insight(claim="c", quote=span)] if span in user else [])})
    results = run_eval(client, cases, ["grounded"], "m", workers=1)
    before = results["strategies"]["grounded"]["aggregate"]
    again = regrade(results, cases)["strategies"]["grounded"]["aggregate"]
    assert again == before and results["regraded"]

    # Corrupt the stored scores, then regrade: they come back from the saved extractions
    for case in results["strategies"]["grounded"]["cases"]:
        case["planted_found"], case["planted_missed"] = [], ["x"]
    assert regrade(results, cases)["strategies"]["grounded"]["aggregate"] == before


def test_verify_analyst_uses_its_own_prompt(make_client):
    from insights_eval.extract import STRATEGIES, VERIFY_ANALYST_SYSTEM, VERIFY_SYSTEM

    assert "verify_analyst" in STRATEGIES and VERIFY_ANALYST_SYSTEM != VERIFY_SYSTEM
    seen = []
    client = make_client({
        Extraction: lambda user: Extraction(insights=[Insight(claim="c", quote="a quote that is long enough")]),
        KeepList: lambda user: KeepList(keep=[0]),
    })
    original = client.messages.parse

    def spy(**kwargs):
        seen.append(kwargs["system"])
        return original(**kwargs)

    client.messages.parse = spy
    extraction, _ = STRATEGIES["verify_analyst"](client, "m", "Interviewer: hi\nCOO: a quote that is long enough")
    assert len(extraction.insights) == 1 and seen[-1] == VERIFY_ANALYST_SYSTEM
