# Analysis by length, kind and position

## naive

**By transcript length**

| Group | Cases | Recall | Faithfulness | Judge (strict) | Judge (analyst) | False-positive rate | Distraction rate | Insights |
|---|---|---|---|---|---|---|---|---|
| short (<300 words) | 13 | 100% | 100% | - | - | 50% | - | 54 |
| medium (300-1200) | 12 | 100% | 100% | - | - | 100% | 6% | 64 |
| long (>1200) | 20 | 100% | 100% | - | - | - | 1% | 94 |

**By case kind**

| Group | Cases | Recall | Faithfulness | Judge (strict) | Judge (analyst) | False-positive rate | Distraction rate | Insights |
|---|---|---|---|---|---|---|---|---|
| base | 8 | 100% | 100% | - | - | 50% | - | 33 |
| buried | 1 | 100% | 100% | - | - | - | - | 4 |
| empty_long | 2 | - | 100% | - | - | 100% | - | 12 |
| hedged | 1 | 100% | 100% | - | - | - | - | 4 |
| leading_question | 1 | 100% | 100% | - | - | - | - | 5 |
| negation | 1 | 100% | 100% | - | - | - | - | 4 |
| padded | 30 | 100% | 100% | - | - | - | 3% | 146 |
| reported_views | 1 | 100% | 100% | - | - | - | - | 4 |

**Padded transcripts, by length and layout (block = filler before and after the planted interview; interleaved = filler between its turns)**

| Group | Cases | Recall | Faithfulness | Judge (strict) | Judge (analyst) | False-positive rate | Distraction rate | Insights |
|---|---|---|---|---|---|---|---|---|
| medium / middle | 5 | 100% | 100% | - | - | - | 12% | 25 |
| medium / interleaved | 5 | 100% | 100% | - | - | - | 0% | 27 |
| long / start | 5 | 100% | 100% | - | - | - | 5% | 22 |
| long / middle | 5 | 100% | 100% | - | - | - | 0% | 21 |
| long / end | 5 | 100% | 100% | - | - | - | 0% | 25 |
| long / interleaved | 5 | 100% | 100% | - | - | - | 0% | 26 |

## grounded

**By transcript length**

| Group | Cases | Recall | Faithfulness | Judge (strict) | Judge (analyst) | False-positive rate | Distraction rate | Insights |
|---|---|---|---|---|---|---|---|---|
| short (<300 words) | 13 | 100% | 100% | - | - | 0% | - | 48 |
| medium (300-1200) | 12 | 100% | 100% | - | - | 0% | 2% | 50 |
| long (>1200) | 20 | 100% | 100% | - | - | - | 1% | 100 |

**By case kind**

| Group | Cases | Recall | Faithfulness | Judge (strict) | Judge (analyst) | False-positive rate | Distraction rate | Insights |
|---|---|---|---|---|---|---|---|---|
| base | 8 | 100% | 100% | - | - | 0% | - | 30 |
| buried | 1 | 100% | 100% | - | - | - | - | 4 |
| empty_long | 2 | - | - | - | - | 0% | - | 0 |
| hedged | 1 | 100% | 100% | - | - | - | - | 3 |
| leading_question | 1 | 100% | 100% | - | - | - | - | 4 |
| negation | 1 | 100% | 100% | - | - | - | - | 4 |
| padded | 30 | 100% | 100% | - | - | - | 1% | 150 |
| reported_views | 1 | 100% | 100% | - | - | - | - | 3 |

**Padded transcripts, by length and layout (block = filler before and after the planted interview; interleaved = filler between its turns)**

| Group | Cases | Recall | Faithfulness | Judge (strict) | Judge (analyst) | False-positive rate | Distraction rate | Insights |
|---|---|---|---|---|---|---|---|---|
| medium / middle | 5 | 100% | 100% | - | - | - | 0% | 23 |
| medium / interleaved | 5 | 100% | 100% | - | - | - | 4% | 27 |
| long / start | 5 | 100% | 100% | - | - | - | 0% | 24 |
| long / middle | 5 | 100% | 100% | - | - | - | 4% | 23 |
| long / end | 5 | 100% | 100% | - | - | - | 0% | 26 |
| long / interleaved | 5 | 100% | 100% | - | - | - | 0% | 27 |

## verify

**By transcript length**

| Group | Cases | Recall | Faithfulness | Judge (strict) | Judge (analyst) | False-positive rate | Distraction rate | Insights |
|---|---|---|---|---|---|---|---|---|
| short (<300 words) | 13 | 87% | 100% | - | - | 0% | - | 36 |
| medium (300-1200) | 12 | 89% | 100% | - | - | 0% | 0% | 38 |
| long (>1200) | 20 | 92% | 100% | - | - | - | 0% | 77 |

**By case kind**

| Group | Cases | Recall | Faithfulness | Judge (strict) | Judge (analyst) | False-positive rate | Distraction rate | Insights |
|---|---|---|---|---|---|---|---|---|
| base | 8 | 82% | 100% | - | - | 0% | - | 20 |
| buried | 1 | 100% | 100% | - | - | - | - | 5 |
| empty_long | 2 | - | - | - | - | 0% | - | 0 |
| hedged | 1 | 100% | 100% | - | - | - | - | 3 |
| leading_question | 1 | 100% | 100% | - | - | - | - | 3 |
| negation | 1 | 100% | 100% | - | - | - | - | 3 |
| padded | 30 | 91% | 100% | - | - | - | 0% | 115 |
| reported_views | 1 | 67% | 100% | - | - | - | - | 2 |

**Padded transcripts, by length and layout (block = filler before and after the planted interview; interleaved = filler between its turns)**

| Group | Cases | Recall | Faithfulness | Judge (strict) | Judge (analyst) | False-positive rate | Distraction rate | Insights |
|---|---|---|---|---|---|---|---|---|
| medium / middle | 5 | 89% | 100% | - | - | - | 0% | 19 |
| medium / interleaved | 5 | 89% | 100% | - | - | - | 0% | 19 |
| long / start | 5 | 89% | 100% | - | - | - | 0% | 18 |
| long / middle | 5 | 100% | 100% | - | - | - | 0% | 21 |
| long / end | 5 | 84% | 100% | - | - | - | 0% | 18 |
| long / interleaved | 5 | 95% | 100% | - | - | - | 0% | 20 |

## Does length correlate with errors?

Spearman rank correlation between a transcript's word count and its per-case score. Positive means the score rises with length; negative means it falls. A dash means fewer than 8 usable cases or no variation in the score.

| Strategy | Cases | Recall | Faithfulness | Judge (strict) | Insights from empty transcripts | Distraction |
|---|---|---|---|---|---|---|
| naive | 45 | - | - | - | - | -0.41 |
| grounded | 45 | - | - | - | - | -0.12 |
| verify | 45 | +0.04 | - | - | - | - |

Treat these as hints, not findings. Each strategy has a few dozen cases, many scores sit at 100%, and the padded cases share the same five core interviews, so they are not independent.
