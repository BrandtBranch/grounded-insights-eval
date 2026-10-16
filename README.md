# grounded-insights-eval

An eval harness for one question: **when an LLM turns an interview transcript into insights, which part can you trust?**

Consultants use LLMs to summarise stakeholder interviews. This repo measures where that goes wrong, across three prompting strategies (plus a fourth I added after finding a flaw), 45 synthetic transcripts and about 750 extracted insights. The short answer: the quotes were fine, the checking passes were not, and my own evaluation was wrong in five ways before it became useful.

## What I found

**1. The quotes were never the problem. The claims and the checkers were.**
Across 751 insights from four strategies (rounds 2 and 3), no quote was fabricated or taken from the wrong speaker. One interviewer quote slipped through in round 1 (1 of about 90). The failure that did show up is a claim that goes a step beyond its quote. In round 1 an LLM judge flagged 37% of `naive` claims and 17% of `grounded` claims as adding a conclusion the interviewee never stated. *Strength: quote result is strong; the judge's percentages are suggestive, since the judge is a small model and I hand-checked only 7 of its verdicts.*

**2. A verification pass trades recall for precision, and my first version made a bad trade.**
Adding a second "audit each insight" pass raised strict claim support from 83% to 100% in round 1 (8 cases), but in round 2 (45 cases) it cut recall from 100% to 90% and doubled output tokens (60k vs 30k), with no faithfulness gain, because faithfulness was already 100%. It dropped the same seven true insights again and again: constraints ("I can't get the budget approved"), knowledge at risk ("never written down, retiring next spring"), and hedged stances. The cause was in my own prompt. It required the quote alone to prove the claim, the same too-strict standard I had already found and fixed in the judge. Changing it to "facts must be backed, fair conclusions are allowed" brought recall back to 99%, at 1.6x the tokens of the plain strategy. *Strength: the strict-prompt recall drop is strong. Whether the fixed verifier is worth its tokens is untested: the results did not record what it dropped, and no judge was run in rounds 2 and 3.*

**3. "Return nothing" has to be an allowed answer.**
On transcripts with no real insight (small talk, buzzwords), the casual prompt produced output on 3 of 4 in round 2 and on 2 of 2 in round 1. The `grounded` prompt, which says an empty list is a correct answer, produced none in both rounds, on two different backends. Most of what `naive` produced was not invented fact but accurate description of the absence ("the Director gave no concrete example"), so whether that counts as a failure depends on what you want the tool to do. *Strength: replicated, but a single run per case, and the `naive` strategy's output on one empty transcript differed between rounds.*

**4. Length and small talk did not hurt. The kind of statement did.**
Recall on long transcripts (about 2,200 words) was as good as on short ones, and no strategy showed a "lost in the middle" pattern. Mixing small talk between the turns of the real interview made no measurable difference. What did fail was a type of content: half-hearted agreement with the interviewer, and "X is a symptom, not the cause". *Strength: suggestive. Transcripts were at most about 2,300 words and built from five core interviews, so the cases are not independent.*

**5. Small talk caused one specific failure: invented links.**
Four times, `naive` took an off-topic complaint ("the intranet search is useless") and tied it to the real topic ("which may help explain why outdated guidance..."). It happened with the same line every time, which sits thematically close to the interview topics. The model connected things that were not connected. *Strength: weak: one filler line, four cases. It shows the mechanism, not a rate.*

**6. The biggest source of error was my own evaluation.**
I only found these by reading outputs instead of trusting the scores:

| Flaw | What it did | Fix |
|---|---|---|
| The judge saw only the quote | Rejected fair claims whose quote lacked the interviewer's question (`grounded` support read 78%) | Judge sees the transcript, with three labels: supported, inference, unsupported |
| Faithfulness ignored who spoke | Accepted a quote from the interviewer (`naive` faithfulness was really 97%, not 100%) | Quote must sit inside an interviewee turn |
| Recall rejected split quotes | Scored a found insight as missed when the model split it across two quotes (`grounded` read 99%, really 100%) | A quote carrying at least half the evidence counts |
| The verifier's standard was too strict | See finding 2 | Added `verify_analyst` |
| My filler text contradicted itself | Two "distraction" hits were the model correctly spotting a contradiction I wrote | Disclosed, not fixed |

A score of 100% usually means the test is too easy or the metric is blind. Neither is a result about the model.

## Strategies

- `naive`: "Extract the key insights."
- `grounded`: explicit rules: quote verbatim, never infer causes or numbers, record contradictions, and return an empty list when there is nothing to find.
- `verify`: `grounded`, then a second pass that keeps an insight only if the quote alone fully supports the claim.
- `verify_analyst`: the same, but facts must be backed by the interviewee's words in context, and fair conclusions are allowed.

## Metrics

| Metric | How it is computed | Needs an LLM? |
|---|---|---|
| **Faithfulness** | Share of quotes that appear verbatim inside an interviewee turn | No |
| **Recall** | Share of planted insights covered by a quote (at least half the evidence span) | No |
| **False-positive rate** | Share of no-insight transcripts where anything was extracted | No |
| **Distraction rate** | Share of insights quoted from filler instead of the planted interview | No |
| **Judge (analyst / strict)** | Share of verbatim insights whose claim is backed by the transcript. Analyst counts a fair added conclusion as backed; strict does not | Yes, optional |

## Results

**Round 1** (8 short transcripts, Anthropic API, judge `claude-haiku-4-5`; `results/judge-v2/`)

| Strategy | Faithfulness | Recall | False-positive rate | Judge (analyst) | Judge (strict) | Insights |
|---|---|---|---|---|---|---|
| naive | 97% | 100% | 100% | 100% | 63% | 35 |
| grounded | 100% | 100% | 0% | 100% | 83% | 29 |
| verify | 100% | 95% | 0% | 100% | 100% | 24 |

**Rounds 2 and 3** (45 transcripts from roughly 100 to 2,300 words, extractor `claude-opus-5-5` through a Claude Code login, no judge; `results/round2/`, `results/round3/`)

| Strategy | Faithfulness | Recall | False-positive rate | Distraction rate | Insights | Output tokens |
|---|---|---|---|---|---|---|
| naive | 100% | 100% | 75% | 3% | 212 | 27,710 |
| grounded | 100% | 100% | 0% | 1% | 198 | 29,995 |
| verify | 100% | 90% | 0% | 0% | 151 | 59,851 |
| verify_analyst | 100% | 99% | 0% | 1% | 190 | 49,130 |

Recall by transcript length:

| Strategy | Short (<300 words, 13 cases) | Medium (12 cases) | Long (>1200 words, 20 cases) |
|---|---|---|---|
| naive | 100% | 100% | 100% |
| grounded | 100% | 100% | 100% |
| verify | 87% | 89% | 92% |
| verify_analyst | 95% | 100% | 100% |

The short group contains the hand-written hard cases, so lower recall there reflects the kind of statement, not the length. Full tables, including layout and position, are in each run's `analysis.md`.

## Data

Everything is synthetic. There is no client data.

- `data/cases.json`: 8 short interviews, 6 with planted insights (one with a self-contradicting interviewee) and 2 with none.
- `data/cases_hard.json`: 5 hand-written traps: a leading question, a hedged figure, other people's opinions next to the interviewee's own, negated causes, and an insight buried in a rambling answer.
- `data/cases_long.json`: generated by `scripts/make_long_cases.py`. The 5 core interviews are padded with small talk, irrelevant facts and chatty complaints, at about 780 and 2,200 words, with the core at the start, middle or end, or with filler interleaved between its turns. Two long transcripts have no insight at all.

`insights-eval validate-data` and the tests check that every planted evidence span appears word for word in its transcript.

## Run it

```bash
pip install -e ".[dev]"
pytest                                           # offline, uses a fake client
python -m insights_eval run                      # no API key: uses your Claude Code login
python -m insights_eval run --backend api        # uses ANTHROPIC_API_KEY, billed to that key
python -m insights_eval run --strategies grounded verify_analyst --judge
python -m insights_eval analyze results/<run>/results.json
python -m insights_eval regrade results/<run>/results.json   # re-score saved output, no model calls
```

A full run of all strategies on all 45 cases is about 180 model calls, roughly 20 to 30 minutes with `--workers 4`.

## Limitations

- **The data is synthetic and written with Claude's help,** and Claude models extract from it and judge it. That is circular. Real interviews are messier and much longer than 2,300 words.
- **Each case is run once.** Extraction varies between runs, so differences of a point or two are noise.
- **The padded cases are not independent.** They are variants of five core interviews, so "missed in five of the seven plant cases" means one insight, missed consistently.
- **Rounds 1 and 2 to 3 used different backends** (the API, then Claude Code), which can change behaviour. Don't read the two tables as one experiment.
- **The judge is unvalidated.** I hand-checked 7 of its verdicts. In one probe it labelled an unsupported judgment ("Planning is slow and incompetent") as only an inference, so it may be lenient.
- **The 'analyst' standard is my choice.** Whether a fair inference counts as supported is a judgment call; the strict figures show the alternative.
- **No judge ran in rounds 2 and 3,** and `verify_analyst` does not record which candidates it dropped, so its benefit over `grounded` is unproven.
- **Speaker detection assumes `Speaker: text` lines** and treats `Interviewer`, `Int`, `Moderator` and `Facilitator` as interviewer labels.

## Layout

```
src/insights_eval/
  text.py         normalisation, verbatim, interviewee-turn and coverage checks
  graders.py      per-case grading and aggregation
  extract.py      the four strategies
  judge.py        optional claim-vs-transcript judge
  runner.py       runs everything, renders the report, re-scores saved results
  analyze.py      breakdown by length, kind and layout, with rank correlations
  claude_code.py  runs the same calls through a Claude Code login, no API key
  cli.py          insights-eval run | analyze | regrade | validate-data
data/             the 45 cases
scripts/          generator for the long cases
results/          saved output of each round
tests/            offline tests with a fake client
```
