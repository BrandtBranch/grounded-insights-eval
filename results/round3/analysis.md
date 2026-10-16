# Analysis by length, kind and position

## verify_analyst

**By transcript length**

| Group | Cases | Recall | Faithfulness | Judge (strict) | Judge (analyst) | False-positive rate | Distraction rate | Insights |
|---|---|---|---|---|---|---|---|---|
| short (<300 words) | 13 | 95% | 100% | - | - | 0% | - | 47 |
| medium (300-1200) | 12 | 100% | 100% | - | - | 0% | 2% | 47 |
| long (>1200) | 20 | 100% | 100% | - | - | - | 0% | 96 |

**By case kind**

| Group | Cases | Recall | Faithfulness | Judge (strict) | Judge (analyst) | False-positive rate | Distraction rate | Insights |
|---|---|---|---|---|---|---|---|---|
| base | 8 | 100% | 100% | - | - | 0% | - | 31 |
| buried | 1 | 100% | 100% | - | - | - | - | 3 |
| empty_long | 2 | - | - | - | - | 0% | - | 0 |
| hedged | 1 | 100% | 100% | - | - | - | - | 3 |
| leading_question | 1 | 75% | 100% | - | - | - | - | 4 |
| negation | 1 | 100% | 100% | - | - | - | - | 4 |
| padded | 30 | 100% | 100% | - | - | - | 1% | 143 |
| reported_views | 1 | 67% | 100% | - | - | - | - | 2 |

**Padded transcripts, by length and layout (block = filler before and after the planted interview; interleaved = filler between its turns)**

| Group | Cases | Recall | Faithfulness | Judge (strict) | Judge (analyst) | False-positive rate | Distraction rate | Insights |
|---|---|---|---|---|---|---|---|---|
| medium / middle | 5 | 100% | 100% | - | - | - | 5% | 22 |
| medium / interleaved | 5 | 100% | 100% | - | - | - | 0% | 25 |
| long / start | 5 | 100% | 100% | - | - | - | 0% | 23 |
| long / middle | 5 | 100% | 100% | - | - | - | 0% | 23 |
| long / end | 5 | 100% | 100% | - | - | - | 0% | 23 |
| long / interleaved | 5 | 100% | 100% | - | - | - | 0% | 27 |

## Does length correlate with errors?

Spearman rank correlation between a transcript's word count and its per-case score. Positive means the score rises with length; negative means it falls. A dash means fewer than 8 usable cases or no variation in the score.

| Strategy | Cases | Recall | Faithfulness | Judge (strict) | Insights from empty transcripts | Distraction |
|---|---|---|---|---|---|---|
| verify_analyst | 45 | +0.32 | - | - | - | -0.20 |

Treat these as hints, not findings. Each strategy has a few dozen cases, many scores sit at 100%, and the padded cases share the same five core interviews, so they are not independent.
