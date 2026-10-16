from __future__ import annotations

import re
from difflib import SequenceMatcher

_QUOTE_TRANSLATION = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-"})
_ELLIPSIS = re.compile(r"…|\.{3}|\[\.\.\.\]")
_TURN = re.compile(r"^\s*([^:\n]{1,40}):\s*(.*)$")
INTERVIEWER_LABELS = {"interviewer", "int", "moderator", "facilitator"}
MIN_SEGMENT_CHARS = 8


def normalize(text: str) -> str:
    """Lowercase, unify quote characters and collapse whitespace."""
    text = text.translate(_QUOTE_TRANSLATION).lower()
    return re.sub(r"\s+", " ", text).strip(" \"'")


def _segments(quote: str) -> list[str] | None:
    """Split a quote on ellipses into normalized segments, or None if it is unusable."""
    segments = [normalize(s) for s in _ELLIPSIS.split(quote)]
    segments = [s for s in segments if s]
    if not segments or any(len(s) < MIN_SEGMENT_CHARS for s in segments):
        return None
    return segments


def is_verbatim(quote: str, transcript: str) -> bool:
    """True if every ellipsis-separated segment of the quote appears in the transcript.

    Case, whitespace and typographic quotes are ignored. Anything else, such as
    reworded or stitched-together text, counts as not verbatim. This does not check
    who said it: see is_interviewee_quote.
    """
    segments = _segments(quote)
    if segments is None:
        return False
    haystack = normalize(transcript)
    return all(s in haystack for s in segments)


def interviewee_turns(transcript: str) -> list[str] | None:
    """Normalized text of each non-interviewer turn, or None if the transcript has no speaker labels.

    Turns start at a line of the form "Speaker: text" with a label of at most 40 characters.
    A continuation line that happens to look like that will be misread as a new speaker.
    """
    turns: list[str] = []
    current: list[str] = []
    interviewer = False
    labelled = False
    for line in transcript.splitlines():
        match = _TURN.match(line)
        if match:
            labelled = True
            if current:
                turns.append(" ".join(current))
            current = []
            interviewer = match.group(1).strip().lower() in INTERVIEWER_LABELS
            line = match.group(2)
        if not interviewer and line.strip():
            current.append(line.strip())
    if current:
        turns.append(" ".join(current))
    return [normalize(t) for t in turns] if labelled else None


def is_interviewee_quote(quote: str, transcript: str) -> bool:
    """True if every segment of the quote sits inside a single turn spoken by the interviewee.

    Segments may come from different turns (joined with an ellipsis), but a segment may not
    run across a turn boundary. Transcripts without speaker labels fall back to is_verbatim.
    """
    turns = interviewee_turns(transcript)
    if turns is None:
        return is_verbatim(quote, transcript)
    segments = _segments(quote)
    if segments is None:
        return False
    return all(any(s in turn for turn in turns) for s in segments)


def overlaps(span: str, quote: str, min_chars: int = 15) -> bool:
    """True if any ellipsis-separated part of the quote covers the span, or sits inside it."""
    a = normalize(span)
    if not a:
        return False
    for part in _ELLIPSIS.split(quote):
        b = normalize(part)
        if b and (a in b or (len(b) >= min_chars and b in a)):
            return True
    return False


def covers(span: str, quote: str, min_chars: int = 15, min_fraction: float = 0.5) -> bool:
    """True if some ellipsis-separated part of the quote reproduces at least half of the evidence span.

    Unlike `overlaps`, this credits a quote that carries only part of the span, which happens when a
    model splits one insight across two quotes. The shared stretch must be contiguous.
    """
    a = normalize(span)
    if not a:
        return False
    needed = max(min_chars, min_fraction * len(a))
    for part in _ELLIPSIS.split(quote):
        b = normalize(part)
        if b and SequenceMatcher(None, a, b, autojunk=False).find_longest_match(0, len(a), 0, len(b)).size >= needed:
            return True
    return False
