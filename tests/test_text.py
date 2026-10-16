from insights_eval.text import is_verbatim, normalize, overlaps

TRANSCRIPT = "COO: Honestly, the promo calendar is built by marketing in January.\nIt’s late."


def test_normalize_collapses_whitespace_case_and_quotes():
    assert normalize("  It’s   LATE.\n") == "it's late."


def test_verbatim_ignores_case_whitespace_and_curly_quotes():
    assert is_verbatim("the promo  calendar is built by MARKETING", TRANSCRIPT)
    assert is_verbatim("It's late.", TRANSCRIPT)


def test_paraphrase_is_not_verbatim():
    assert not is_verbatim("marketing builds the promo calendar in January", TRANSCRIPT)


def test_ellipsis_joins_segments_that_each_appear():
    assert is_verbatim("the promo calendar ... in January", TRANSCRIPT)
    assert not is_verbatim("the promo calendar ... in February", TRANSCRIPT)


def test_empty_or_tiny_quotes_are_rejected():
    assert not is_verbatim("", TRANSCRIPT)
    assert not is_verbatim("the", TRANSCRIPT)


def test_overlap_when_quote_contains_or_sits_inside_span():
    span = "replenishment only sees it two weeks before launch"
    assert overlaps(span, "the calendar means replenishment only sees it two weeks before launch, by then...")
    assert overlaps(span, "only sees it two weeks before launch")
    assert not overlaps(span, "two weeks")  # too short to count
    assert not overlaps(span, "an unrelated quote about something else")


from insights_eval.text import interviewee_turns, is_interviewee_quote

DIALOGUE = (
    "Interviewer: Can you be more specific about the delay?\n"
    "COO: The calendar reaches replenishment two weeks before launch.\n"
    "Interviewer: And who owns the gap?\n"
    "COO: Nobody owns it. Planning blames marketing."
)


def test_interviewer_words_are_not_an_interviewee_quote():
    assert is_verbatim("Can you be more specific about the delay?", DIALOGUE)  # appears in the transcript...
    assert not is_interviewee_quote("Can you be more specific about the delay?", DIALOGUE)  # ...but was not said by the interviewee


def test_interviewee_words_are_accepted_including_across_turns_with_an_ellipsis():
    assert is_interviewee_quote("two weeks before launch", DIALOGUE)
    assert is_interviewee_quote("The calendar reaches replenishment ... Nobody owns it", DIALOGUE)


def test_a_segment_may_not_run_across_a_turn_boundary():
    stitched = "two weeks before launch. And who owns the gap? Nobody owns it"
    assert not is_interviewee_quote(stitched, DIALOGUE)


def test_continuation_lines_belong_to_the_same_turn():
    transcript = "Interviewer: Why?\nCOO: First part of the answer\nand the second part of it."
    assert interviewee_turns(transcript) == ["first part of the answer and the second part of it."]


def test_transcript_without_speaker_labels_falls_back_to_plain_verbatim_check():
    assert interviewee_turns("Just some text with no labels") is None
    assert is_interviewee_quote("some text with no labels", "Just some text with no labels")


def test_overlap_looks_at_each_ellipsis_part_of_the_quote():
    span = "Nobody owns the gap between planning and marketing"
    assert overlaps(span, "an unrelated opening part ... Nobody owns the gap between planning and marketing, I'd say")
    assert overlaps(span, "something else entirely ... owns the gap between planning")  # part sits inside the span
    assert not overlaps(span, "something else entirely ... and another unrelated part")


from insights_eval.text import covers


def test_covers_credits_a_quote_that_carries_at_least_half_the_span():
    span = "In practice it's closer to fourteen because product teams submit incomplete files"
    # A model split this insight across two quotes. The second carries 55% of the span, the first 43%.
    assert covers(span, "because product teams submit incomplete files and we spend weeks chasing missing documents")
    assert not covers(span, "Formally in six weeks. In practice it's closer to fourteen")
    assert not covers(span, "an unrelated quote about something else entirely")
    assert not covers(span, "")
