# Results

Extractor: `claude-opus-5-5` | Judge: `claude-haiku-4-5`

| Strategy | Faithfulness | Recall | False-positive rate | Judge support | Insights | Output tokens |
|---|---|---|---|---|---|---|
| naive | 100% | 100% | 100% | 56% | 32 | 3077 |
| grounded | 100% | 100% | 0% | 78% | 27 | 2484 |
| verify | 100% | 100% | 0% | 54% | 24 | 3850 |

- **Faithfulness**: extracted quotes that appear verbatim in the transcript (deterministic).
- **Recall**: planted insights that an extracted quote covers.
- **False-positive rate**: transcripts with no real insight where the model extracted something anyway.
- **Judge support**: verbatim insights whose claim the quote fully supports (LLM judge).

## Failures: naive

- `retail_stockouts` claim not supported by its quote:
  - claim: "The weekly cross-functional call has strong engagement but happens too late in the cycle to influence decisions, so it is an underused lever."
  - quote: "Our weekly cross-functional call is actually good, people turn up. It just happens after the decisions are made."
- `saas_churn` claim not supported by its quote:
  - claim: "Discounting does not reduce churn, suggesting price concessions are an ineffective retention lever."
  - quote: "Discounted customers churn at the same rate as full price ones."
- `saas_churn` claim not supported by its quote:
  - claim: "The VP's top proposed fix is extending onboarding ownership to month nine, but it is blocked by a budget request for two additional hires."
  - quote: "Keep the onboarding owner on the account until month nine. It would cost two more hires and I can't get the budget approved."
- `plant_changeovers` claim not supported by its quote:
  - claim: "Changeovers are the primary source of lost line time, occurring frequently and taking a long time each."
  - quote: "Changeovers. We switch product variants about eleven times a week and each one takes around ninety minutes."
- `plant_changeovers` claim not supported by its quote:
  - claim: "Long changeover times are not a technical constraint, since one shift already achieves less than half the typical duration."
  - quote: "No. Our best shift does it in forty minutes."
- `plant_changeovers` claim not supported by its quote:
  - claim: "The best shift's advantage comes from pre-staging tooling, a practice the other shifts have not adopted."
  - quote: "they pre-stage tooling during the previous run, and the other shifts never adopted it."
- `plant_changeovers` claim not supported by its quote:
  - claim: "The best practice is undocumented and at risk of being lost when the shift leader who holds it retires."
  - quote: "The practice was never written down. It lives in one shift leader's head, and he's retiring next spring."
- `plant_changeovers` claim not supported by its quote:
  - claim: "Maintenance is largely reactive, and even the few planned stops are poorly executed."
  - quote: "Mostly reactive. We only had three planned stops last quarter, and all three overran."
- `ceo_contradiction` claim not supported by its quote:
  - claim: "The CEO's initial portrayal of leadership decision-making as fast and final is contradicted by their own example, suggesting a self-perception gap."
  - quote: "Take the pricing decision in March. Actually, that one took us five months and got reversed twice, so maybe I'm being generous."
- `ceo_contradiction` claim not supported by its quote:
  - claim: "The CEO believes decisions are made in the room and not revisited, an assertion undercut by the pricing decision being reversed twice."
  - quote: "We are very fast. Decisions are made in the room and nobody relitigates them afterwards."
- `small_talk_only` claim not supported by its quote:
  - claim: "No substantive interview took place; the director is cooperative and willing to accommodate a rescheduled full conversation."
  - quote: "Of course. Send me some times and I'll make it work."
- `small_talk_only` extracted 2 insight(s) from a transcript with none
- `buzzword_wall` claim not supported by its quote:
  - claim: "The director frames the biggest challenge as organisational transformation but describes it only in abstract terms, with no specific problem named."
  - quote: "it's really about transformation, you know, and leveraging synergies across the organisation to drive value."
- `buzzword_wall` claim not supported by its quote:
  - claim: "When pressed for detail, the director listed broad aspirations (agility, customer-centricity, fewer silos) rather than a concrete issue, which suggests the challenge may not yet be clearly defined or the director is reluctant to share it."
  - quote: "we need to be more agile and customer-centric and break down silos, while staying focused on our strategic priorities."
- `buzzword_wall` claim not supported by its quote:
  - claim: "Asked directly for an example, the director gave none and pointed to momentum instead, so this interview offers no evidence-based insight and the topic needs a follow-up with targeted questions."
  - quote: "I'd say it's a journey. We are on it, and there is a lot of energy in the organisation."
- `buzzword_wall` extracted 3 insight(s) from a transcript with none

## Failures: grounded

- `hospital_theatres` claim not supported by its quote:
  - claim: "The interviewee says data was never the obstacle to reform, yet also says they do not fully trust the utilisation data."
  - quote: "The data was never the issue. ... Not fully. Anaesthetics logs start time differently from nursing"
- `saas_churn` claim not supported by its quote:
  - claim: "Exit interviews show only one in ten churned customers cited missing features; the rest said they never embedded the product in their daily workflow."
  - quote: "When we ran exit interviews, only one in ten cited missing features. The rest said they never got the product embedded in their daily workflow."
- `saas_churn` claim not supported by its quote:
  - claim: "The interviewee's first proposed change is to keep the onboarding owner on the account until month nine."
  - quote: "Keep the onboarding owner on the account until month nine."
- `bank_compliance` claim not supported by its quote:
  - claim: "The CCO agrees with the business that compliance is a blocker on timing, but not on substance."
  - quote: "Yes, and frankly they have a point on timing, though not on substance."
- `plant_changeovers` claim not supported by its quote:
  - claim: "Changeovers are the main source of lost line time, occurring about eleven times a week at roughly ninety minutes each."
  - quote: "Changeovers. We switch product variants about eleven times a week and each one takes around ninety minutes."
- `plant_changeovers` claim not supported by its quote:
  - claim: "The faster changeover practice is undocumented and held by a single shift leader who retires next spring, creating a knowledge-loss risk."
  - quote: "The practice was never written down. It lives in one shift leader's head, and he's retiring next spring."

## Failures: verify

- `hospital_theatres` claim not supported by its quote:
  - claim: "Theatre utilisation runs at about 68 percent."
  - quote: "We run at about 68 percent."
- `hospital_theatres` claim not supported by its quote:
  - claim: "Utilisation data is not fully reliable because anaesthetics and nursing log start times differently, so the two systems disagree by up to twenty minutes per case."
  - quote: "Anaesthetics logs start time differently from nursing, so the two systems disagree by up to twenty minutes per case."
- `saas_churn` claim not supported by its quote:
  - claim: "Exit interviews show only one in ten churned customers cited missing features; the rest said they never embedded the product in their daily workflow."
  - quote: "When we ran exit interviews, only one in ten cited missing features. The rest said they never got the product embedded in their daily workflow."
- `saas_churn` claim not supported by its quote:
  - claim: "The CEO and others assume churn is driven by price, but the VP says the data contradicts this because discounted customers churn at the same rate as full-price customers."
  - quote: "Everyone assumes it's price, including our CEO. The data does not support it. Discounted customers churn at the same rate as full price ones."
- `saas_churn` claim not supported by its quote:
  - claim: "The VP's first proposed change is to keep the onboarding owner on the account until month nine."
  - quote: "Keep the onboarding owner on the account until month nine."
- `saas_churn` claim not supported by its quote:
  - claim: "The proposed change would require two additional hires, and the VP cannot get the budget approved."
  - quote: "It would cost two more hires and I can't get the budget approved."
- `bank_compliance` claim not supported by its quote:
  - claim: "Files arrive incomplete because the requirements checklist is a PDF from 2019 that has never been updated, so product teams do not know the current requirements."
  - quote: "The checklist lives in a PDF from 2019 that nobody has updated, so teams don't know what we actually require now."
- `bank_compliance` claim not supported by its quote:
  - claim: "The CCO concedes the business is right that compliance is a blocker on timing, but not on the substance of its reviews."
  - quote: "Yes, and frankly they have a point on timing, though not on substance."
- `plant_changeovers` claim not supported by its quote:
  - claim: "The faster changeover practice is undocumented and held by a single shift leader who retires next spring, creating a knowledge-loss risk."
  - quote: "The practice was never written down. It lives in one shift leader's head, and he's retiring next spring."
- `ceo_contradiction` claim not supported by its quote:
  - claim: "The CEO separates decision speed by type: operational decisions are fast, while product portfolio decisions drag."
  - quote: "Operational decisions are fast. Anything touching the product portfolio drags"
- `ceo_contradiction` claim not supported by its quote:
  - claim: "The CEO attributes slow product portfolio decisions to disagreement between the founders and to no one being willing to break the tie."
  - quote: "Anything touching the product portfolio drags, because the founders disagree and no one will break the tie."
