# Results

Extractor: `claude-opus-5-5` | Backend: `claude-code`

| Strategy | Faithfulness | Recall | False-positive rate | Distraction rate | Insights | Output tokens |
|---|---|---|---|---|---|---|
| verify_analyst | 100% | 99% | 0% | 1% | 190 | 49130 |

- **Faithfulness**: extracted quotes that appear verbatim in the transcript (deterministic).
- **Recall**: planted insights that an extracted quote covers.
- **False-positive rate**: transcripts with no real insight where the model extracted something anyway.
- **Distraction rate**: insights, in transcripts that contain filler, that were quoted from the filler instead of the planted interview.

## Failures: verify_analyst

- `leading_morale` missed insight: `weak_assent`
- `reported_views` missed insight: `training_symptom`
- `bank_compliance__medium_middle` 1 insight(s) quoted from filler instead of the planted interview
