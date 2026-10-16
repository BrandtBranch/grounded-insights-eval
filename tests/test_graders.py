from insights_eval.graders import aggregate, grade_case
from insights_eval.models import Case, Extraction, Insight, PlantedInsight, Verdict

TRANSCRIPT = "Interviewer: Why?\nCOO: Planning only sees the promo calendar two weeks before launch. Nobody owns the gap."

CASE = Case(
    id="c1",
    title="t",
    transcript=TRANSCRIPT,
    planted=[
        PlantedInsight(id="late", description="d", evidence=["Planning only sees the promo calendar two weeks before launch"]),
        PlantedInsight(id="owner", description="d", evidence=["Nobody owns the gap"]),
    ],
)
EMPTY_CASE = Case(id="c2", title="t", transcript="Interviewer: Hi.\nDirector: Hello there.", planted=[], expect_none=True)


def test_faithful_extraction_that_finds_one_of_two_planted_insights():
    extraction = Extraction(insights=[Insight(claim="Calendar arrives late", quote="Planning only sees the promo calendar two weeks before launch")])
    result = grade_case(CASE, extraction)
    assert result.n_faithful == 1
    assert result.planted_found == ["late"]
    assert result.planted_missed == ["owner"]


def test_fabricated_quote_is_flagged_and_does_not_count_as_coverage():
    extraction = Extraction(insights=[Insight(claim="Owner is unclear", quote="Nobody in the organisation owns the gap between teams")])
    result = grade_case(CASE, extraction)
    assert result.unfaithful_quotes == ["Nobody in the organisation owns the gap between teams"]
    assert result.n_faithful == 0
    assert result.planted_found == []


def test_any_insight_on_a_no_insight_transcript_is_a_false_positive():
    extraction = Extraction(insights=[Insight(claim="They are friendly", quote="Hello there.")])
    assert grade_case(EMPTY_CASE, extraction).false_positive
    assert not grade_case(EMPTY_CASE, Extraction(insights=[])).false_positive


def test_judge_verdicts_are_aligned_to_insights_and_none_is_skipped():
    extraction = Extraction(insights=[
        Insight(claim="a", quote="Nobody owns the gap"),
        Insight(claim="b", quote="Nobody owns the gap"),
        Insight(claim="c", quote="made up quote text"),
    ])
    verdicts = [Verdict(label="supported", reason=""), Verdict(label="unsupported", reason="adds a cause"), None]
    result = grade_case(CASE, extraction, verdicts)
    assert (result.judged, result.judged_supported) == (2, 1)
    assert result.unsupported_claims == ["b"]


def test_aggregate_pools_across_cases_and_handles_empty_denominators():
    good = grade_case(CASE, Extraction(insights=[Insight(claim="x", quote="Nobody owns the gap")]))
    quiet = grade_case(EMPTY_CASE, Extraction(insights=[]))
    agg = aggregate([good, quiet])
    assert agg["faithfulness"] == 1.0
    assert agg["recall"] == 0.5
    assert agg["false_positive_rate"] == 0.0
    assert agg["judge_support"] is None


def test_inference_counts_for_analyst_standard_but_not_strict():
    extraction = Extraction(insights=[
        Insight(claim="a", quote="Nobody owns the gap"),
        Insight(claim="b", quote="Nobody owns the gap"),
        Insight(claim="c", quote="Nobody owns the gap"),
    ])
    verdicts = [
        Verdict(label="supported", reason=""),
        Verdict(label="inference", reason="adds a conclusion"),
        Verdict(label="unsupported", reason=""),
    ]
    result = grade_case(CASE, extraction, verdicts)
    assert (result.judged, result.judged_supported, result.judged_strict) == (3, 2, 1)
    assert result.inference_claims == ["b"] and result.unsupported_claims == ["c"]
    agg = aggregate([result])
    assert agg["judge_support"] == 2 / 3 and agg["judge_strict"] == 1 / 3


def test_quoting_the_interviewer_counts_as_unfaithful():
    extraction = Extraction(insights=[Insight(claim="x", quote="Interviewer: Why?")])
    assert grade_case(CASE, extraction).unfaithful_quotes == ["Interviewer: Why?"]
    extraction = Extraction(insights=[Insight(claim="x", quote="Why?")])  # too short anyway
    assert grade_case(CASE, extraction).n_faithful == 0


def test_distraction_counts_insights_quoted_from_filler_not_from_planted_evidence():
    case = Case(
        id="noisy", title="t",
        transcript="Interviewer: Why?\nCOO: Planning only sees the promo calendar two weeks before launch.\nInterviewer: Office?\nCOO: Honestly the new office is a bit grim and the lighting is poor.",
        planted=[PlantedInsight(id="late", description="d", evidence=["Planning only sees the promo calendar two weeks before launch"])],
        distractors=["Honestly the new office is a bit grim and the lighting is poor."],
    )
    extraction = Extraction(insights=[
        Insight(claim="calendar late", quote="Planning only sees the promo calendar two weeks before launch"),
        Insight(claim="office is grim", quote="the new office is a bit grim"),
    ])
    result = grade_case(case, extraction)
    assert result.has_distractors and result.distracted == 1
    assert aggregate([result])["distraction_rate"] == 0.5


def test_distraction_is_not_measured_without_filler_or_on_empty_transcripts():
    extraction = Extraction(insights=[Insight(claim="x", quote="Nobody owns the gap")])
    assert not grade_case(CASE, extraction).has_distractors
    assert aggregate([grade_case(CASE, extraction)])["distraction_rate"] is None


def test_an_insight_split_across_two_quotes_still_counts_as_found():
    case = Case(
        id="split", title="t",
        transcript="Interviewer: Why?\nCOO: In practice it's closer to fourteen because product teams submit incomplete files and we chase them.",
        planted=[PlantedInsight(id="p", description="d", evidence=["In practice it's closer to fourteen because product teams submit incomplete files"])],
    )
    extraction = Extraction(insights=[
        Insight(claim="takes fourteen weeks", quote="In practice it's closer to fourteen"),
        Insight(claim="files are incomplete", quote="because product teams submit incomplete files and we chase them"),
    ])
    assert grade_case(case, extraction).planted_found == ["p"]
