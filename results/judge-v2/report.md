# Results

Extractor: `claude-opus-5-5` | Judge: `claude-haiku-4-5`

| Strategy | Faithfulness | Recall | False-positive rate | Judge (analyst) | Judge (strict) | Insights | Output tokens |
|---|---|---|---|---|---|---|---|
| naive | 100% | 100% | 100% | 100% | 63% | 35 | 3191 |
| grounded | 100% | 100% | 0% | 100% | 83% | 29 | 2530 |
| verify | 100% | 95% | 0% | 100% | 100% | 24 | 3903 |

- **Faithfulness**: extracted quotes that appear verbatim in the transcript (deterministic).
- **Recall**: planted insights that an extracted quote covers.
- **False-positive rate**: transcripts with no real insight where the model extracted something anyway.
- **Judge (analyst)**: verbatim insights judged supported or a fair inference (LLM judge, sees the transcript).
- **Judge (strict)**: verbatim insights judged fully supported, with no added inference.

## Failures: naive

- `retail_stockouts` claim adds an inference:
  - claim: "Store managers compensate with informal workarounds based on private data and instinct, which keeps knowledge siloed and inconsistent."
  - quote: "They keep a private spreadsheet of what usually sells out and they over-order by instinct."
- `retail_stockouts` claim adds an inference:
  - claim: "Reliance on tacit experience leaves new store managers exposed, so outcomes depend on individual tenure."
  - quote: "It works for the experienced ones. The new managers just get burned."
- `hospital_theatres` claim adds an inference:
  - claim: "Theatre utilisation is low at around 68 percent, partly because unused blocks are released too late to be reallocated."
  - quote: "We run at about 68 percent. Blocks get released only 24 hours ahead, which is too late for anyone else to use them."
- `saas_churn` claim adds an inference:
  - claim: "Product gaps are a minor churn driver; the main cause is failure to embed the product in customers' daily workflow."
  - quote: "only one in ten cited missing features. The rest said they never got the product embedded in their daily workflow."
- `saas_churn` claim adds an inference:
  - claim: "Discounting does not reduce churn, suggesting price concessions are an ineffective retention lever."
  - quote: "Discounted customers churn at the same rate as full price ones."
- `bank_compliance` claim adds an inference:
  - claim: "Actual compliance approval takes more than twice the formal timeline, largely due to time spent chasing missing documents from incomplete submissions."
  - quote: "Formally in six weeks. In practice it's closer to fourteen because product teams submit incomplete files and we spend weeks chasing missing documents."
- `plant_changeovers` claim adds an inference:
  - claim: "Changeovers are the primary source of lost line time, occurring frequently and taking a long time each."
  - quote: "Changeovers. We switch product variants about eleven times a week and each one takes around ninety minutes."
- `plant_changeovers` claim adds an inference:
  - claim: "Maintenance is largely reactive, and even the few planned stops are poorly executed."
  - quote: "Mostly reactive. We only had three planned stops last quarter, and all three overran."
- `small_talk_only` claim adds an inference:
  - claim: "No substantive topics were covered because the interview was cut short, but the Director is open to rescheduling the full conversation."
  - quote: "Of course. Send me some times and I'll make it work."
- `small_talk_only` extracted 2 insight(s) from a transcript with none
- `buzzword_wall` claim adds an inference:
  - claim: "Organisational silos are the closest thing to a concrete pain point mentioned and are worth probing in a follow-up."
  - quote: "break down silos"
- `buzzword_wall` claim adds an inference:
  - claim: "Asked directly for a concrete example, the Director gave none and described the change as ongoing, so there is no evidence yet of specific initiatives, milestones or results."
  - quote: "I'd say it's a journey. We are on it"
- `buzzword_wall` claim adds an inference:
  - claim: "The Director sees the organisation as positive about the change, though this is a subjective impression with no supporting detail."
  - quote: "there is a lot of energy in the organisation."
- `buzzword_wall` claim adds an inference:
  - claim: "This interview yields little actionable evidence, so a follow-up should ask for specific examples, such as a recent decision slowed by silos, a customer complaint, or a priority that has stalled."
  - quote: "Can you be more specific?"
- `buzzword_wall` extracted 6 insight(s) from a transcript with none

## Failures: grounded

- `retail_stockouts` claim adds an inference:
  - claim: "Supplier lead times exceed the notice replenishment gets, so promoted items stock out."
  - quote: "By then the supplier lead time is already longer than the notice we have."
- `retail_stockouts` claim adds an inference:
  - claim: "The weekly cross-functional call is well attended but happens after decisions are made, so it does not shape them."
  - quote: "Our weekly cross-functional call is actually good, people turn up. It just happens after the decisions are made."
- `saas_churn` claim adds an inference:
  - claim: "In exit interviews, only one in ten churned customers cited missing features; the rest said they never embedded the product in their daily workflow."
  - quote: "When we ran exit interviews, only one in ten cited missing features. The rest said they never got the product embedded in their daily workflow."
- `plant_changeovers` claim adds an inference:
  - claim: "Changeovers are the main source of lost line time, occurring about eleven times a week at roughly ninety minutes each."
  - quote: "Changeovers. We switch product variants about eleven times a week and each one takes around ninety minutes."
- `plant_changeovers` claim adds an inference:
  - claim: "The pre-staging practice is undocumented and held by a single shift leader who is retiring next spring, creating a knowledge-loss risk."
  - quote: "The practice was never written down. It lives in one shift leader's head, and he's retiring next spring."

## Failures: verify

- `bank_compliance` missed insight: `six_vs_fourteen`
