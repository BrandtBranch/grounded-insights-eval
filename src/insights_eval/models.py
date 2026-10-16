from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class Insight(BaseModel):
    claim: str = Field(description="One-sentence insight, stated in the analyst's words.")
    quote: str = Field(description="Verbatim, contiguous excerpt from the interviewee that supports the claim.")


class Extraction(BaseModel):
    insights: list[Insight]


class KeepList(BaseModel):
    keep: list[int] = Field(description="Zero-based indexes of the insights that are fully supported.")


class Verdict(BaseModel):
    label: Literal["supported", "inference", "unsupported"] = Field(
        description="supported: the quote, read in context, backs the whole claim. "
        "inference: the facts are backed but the claim adds a conclusion the interviewee did not state. "
        "unsupported: the claim adds a fact, number, cause or scope the interviewee did not state."
    )
    reason: str


class PlantedInsight(BaseModel):
    id: str
    description: str
    evidence: list[str] = Field(description="Verbatim spans of the transcript that carry this insight.")


class Case(BaseModel):
    id: str
    title: str
    transcript: str
    expect_none: bool = False
    planted: list[PlantedInsight]
    kind: str = "base"  # base | padded | leading_question | hedged | reported_views | negation | buried | empty_long
    group: str | None = None  # id of the base case a padded variant was built from
    position: str | None = None  # where the planted core sits in a padded transcript: start | middle | end | interleaved
    distractors: list[str] = Field(default_factory=list, description="Verbatim filler answers; an insight quoted from these is a distraction.")

    @property
    def words(self) -> int:
        return len(self.transcript.split())


def load_cases(*paths: str | Path) -> list[Case]:
    cases: list[Case] = []
    for path in paths:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        cases += [Case.model_validate(item) for item in raw]
    ids = [c.id for c in cases]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate case ids across case files")
    return cases
