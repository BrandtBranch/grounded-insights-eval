# Results

Extractor: `claude-opus-5-5` | Backend: `claude-code`

| Strategy | Faithfulness | Recall | False-positive rate | Distraction rate | Insights | Output tokens |
|---|---|---|---|---|---|---|
| naive | 100% | 100% | 75% | 3% | 212 | 27710 |
| grounded | 100% | 100% | 0% | 1% | 198 | 29995 |
| verify | 100% | 90% | 0% | 0% | 151 | 59851 |

- **Faithfulness**: extracted quotes that appear verbatim in the transcript (deterministic).
- **Recall**: planted insights that an extracted quote covers.
- **False-positive rate**: transcripts with no real insight where the model extracted something anyway.
- **Distraction rate**: insights, in transcripts that contain filler, that were quoted from the filler instead of the planted interview.

## Failures: naive

- `buzzword_wall` extracted 5 insight(s) from a transcript with none
- `retail_stockouts__medium_middle` 1 insight(s) quoted from filler instead of the planted interview
- `retail_stockouts__long_start` 1 insight(s) quoted from filler instead of the planted interview
- `bank_compliance__medium_middle` 1 insight(s) quoted from filler instead of the planted interview
- `plant_changeovers__medium_middle` 1 insight(s) quoted from filler instead of the planted interview
- `empty_medium` extracted 6 insight(s) from a transcript with none
- `empty_long` extracted 6 insight(s) from a transcript with none

## Failures: grounded

- `retail_stockouts__long_middle` 1 insight(s) quoted from filler instead of the planted interview
- `saas_churn__medium_interleaved` 1 insight(s) quoted from filler instead of the planted interview

## Failures: verify

- `retail_stockouts` missed insight: `late_call`
- `bank_compliance` missed insight: `timing_point`
- `plant_changeovers` missed insight: `changeover_gap`
- `plant_changeovers` missed insight: `undocumented_practice`
- `reported_views` missed insight: `training_symptom`
- `retail_stockouts__medium_interleaved` missed insight: `private_spreadsheets`
- `saas_churn__medium_middle` missed insight: `fix_blocked`
- `saas_churn__long_start` missed insight: `fix_blocked`
- `saas_churn__long_end` missed insight: `fix_blocked`
- `saas_churn__long_interleaved` missed insight: `fix_blocked`
- `bank_compliance__long_end` missed insight: `timing_point`
- `plant_changeovers__medium_middle` missed insight: `undocumented_practice`
- `plant_changeovers__medium_interleaved` missed insight: `undocumented_practice`
- `plant_changeovers__long_start` missed insight: `undocumented_practice`
- `plant_changeovers__long_end` missed insight: `undocumented_practice`
