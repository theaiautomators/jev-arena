# System 1 vs System 2 lesson: sanity check

Reviewed 27 September 2026 against the accepted Jev Arena measurements and selected primary sources. Course folder: `AI-Architects-Course/lessons/intro-to-agentic-systems/system-1-vs-system-2/`.

Status: major corrections applied at the user's request to the lesson HTML, presentation, talk track, lesson page, research notes, Python demo and notebook. The original findings below are retained as the rationale; smaller teaching suggestions were left alone. The architectural structure remains intact.

Verification: Python and notebook syntax passes and all nine shared functions match structurally. Offline simulated responses exercised both routing branches, demonstrating that selected-answer probability rather than concentration controls escalation. Empty retained cohorts display N/A, shared routing policies match, and cascade timing includes both stages. The edited presentation and lesson were opened in a browser; the calibration slide and corrected evidence text render. No paid model calls were made, so live gateway connectivity is unverified. Historical and research citations were spot-checked, not exhaustively audited. Originals are backed up locally under `.arena/course-review/original/`.

## Corrections before recording

### 1. Separate selected-answer probability, concentration and calibration

Locations: `lesson.html:1103`, `lesson.html:1137`, `lesson.html:1183`; `talk-track.md:130`; `demo_system_1_vs_system_2.py:391` and `:433`; corresponding notebook cells and presentation slide 8.

The lesson teaches “0.8 means 80% correct” and then gates on `team.confidence`. TypeSafe documents that field as a statistic describing the distribution's concentration, distinct from the per-option probabilities. It is not automatically the probability that the selected answer is correct. The demo also puts an LLM's self-reported correctness estimate next to this different statistic as if they shared an interpretation. [TypeSafe confidence documentation](https://docs.typesafe.ai/confidence).

Display the selected option's probability, `team.probabilities[team.choice]`, separately from `team.confidence`. If teaching probability calibration, evaluate the former against observed correctness. Either can be investigated as a routing score, but its threshold must be validated empirically; a concentration threshold of 0.8 does not establish 80% accuracy.

Suggested wording: “Jev returns probabilities for the available answers and a separate score describing how concentrated that distribution is. Neither is a guarantee. We measure how these signals relate to errors on our own task before using them to route work.”

### 2. Replace the money-transfer threshold example

Locations: `lesson.html:1152` and `:1162`; `talk-track.md:134`.

The prose teaches automatic action at high confidence, then suggests 0.85 for approving a transfer. This conflates intent recognition with authority to execute an action. Even a correctly calibrated 85% correctness probability would not be a sufficient authorization rule. A wrong balance screen also must not bypass account access checks.

Use reversible ticket routing to explain thresholds. If retaining a transfer example, the model only classifies the request; identity, permissions, transaction limits and required user confirmation are enforced by code. No confidence score overrides them. The vendor's own example calls a confirmation function for the transfer path. [TypeSafe example](https://docs.typesafe.ai/confidence).

### 3. Treat calibration as measured behavior, not a model-category guarantee

Locations: `presentation.html:763`; `lesson.html:808`, `:1060`, `:1133`, `:1459`; `talk-track.md:70` and `:114`; lesson-page takeaways.

“Calibrated” versus “self-reported at best” makes the table too absolute. “Trained for calibration; validate on your task” is the defensible Jev description. “A JSON field alone provides no calibration guarantee” is the defensible LLM description. Emitting a number as text does not prove that the number is uninformative or necessarily the weakest signal. A primary study found verbalized confidence better calibrated than conditional token probabilities for several RLHF models on its tested datasets. [Tian et al.](https://arxiv.org/abs/2305.14975).

The right rule applies to both families: do not assume a confidence signal transfers to your deployment without evaluation. A separate Jev calibration study also found task-dependent errors; this is not only an LLM problem. [Independent Jev calibration study](https://github.com/scienthoon/jev-ood-calibration).

Calibration is also not required for every useful router: an uncalibrated score can still rank easy and difficult cases well. Measure error rate versus retained coverage and escalation cost, alongside calibration.

### 4. Explain what actually produced the phishing result

Locations: `talk-track.md:84` and `:170`; `lesson.html:963`; `lesson-page.md:29`; presentation slide 5.

The 62.6% single-question result used 2,000 emails. The 95.0% result used five Jev signals plus a logistic regression fitted on 1,000 labelled emails and evaluated on the other 1,000. It was not simply a prompt rewrite with fixed handwritten combining rules. The held-out regex control scored 91.8%, showing that dataset construction matters too. [Original benchmark](https://github.com/anisselbd/jev-phishing-bench).

Suggested wording: “On one phishing dataset, a pipeline combining five Jev judgments with a small classifier trained on labelled examples reached 95% on its held-out half. That illustrates decomposition plus supervised combination, not a guaranteed gain from asking more questions.”

### 5. Correct the public-evaluation statement

Locations: `talk-track.md:86`; `lesson.html:972`; `research-report.md:13`.

“TypeSafe publishes no public benchmark results by design” is too broad. Its public workflow evaluation site reports comparisons, with references derived from frontier-model responses. Describe these as vendor workflow evaluations measuring agreement with model-derived references, rather than a human ground-truth benchmark. [TypeSafe workflow evaluations](https://evals.typesafe.ai/).

This also connects directly to Arena: teacher agreement was kept separate from reference accuracy, and Astra's audit did not replace frozen labels or human review.

### 6. Make the demo's experimental scope explicit

Locations: `demo_system_1_vs_system_2.py:46`, `:77`, `:248`, `:268`, `:400`, `:427`, `:437`; corresponding notebook cells.

The 16 tickets illustrate API contracts and routing mechanics. They do not validate calibration, a production threshold or a general cost/accuracy advantage. Specific changes to make before demonstrating it:

- Pin the direct Jev version instead of `jev-latest`. For the gateway, verify which identifiers it supports and record the resolved response model and provider. Log dependency versions, requests and responses. The official direct ID is currently `jev-1.13.0`; do not assume the gateway accepts the same version syntax. [Model/version documentation](https://docs.typesafe.ai/models).
- Give ambiguous tickets an explicit routing policy, including precedence, or mark multiple acceptable answers. Document whether the “support lead” labels were actually human-assigned or are illustrative author labels. Otherwise a plausible interpretation is counted as a model error—the exact problem found in Arena's routing fixtures.
- Keep the fixed 0.80 threshold visibly illustrative. A larger exercise should tune on one split and report retained accuracy, coverage and escalations on a separate test split. Do not select the best threshold from the displayed test sweep and call that validated performance.
- The all-LLM baseline disables reasoning and returns team, refund, urgency and confidence. The escalation call enables reasoning, sees Jev's suggestions and returns only team plus a note. These are different deployment configurations. Identify them explicitly; do not attribute their difference solely to cascading or compare costs as if the delivered outputs were identical. An all-reasoning routing-only baseline would help isolate the cascade's value.
- Only team labels are scored. Refund and urgency are API demonstrations, not evaluated outputs. Label that boundary.
- Report cascade latency too: Jev time plus escalation time for escalated tickets. A slow path can cost less on average while increasing tail latency.
- Include an out-of-scope case and an explicit review/unknown path. The script currently accepts every escalated label, whereas the lesson diagram includes a final human-review branch. Either implement it or call out the simplification.
- When zero cases pass a threshold, show retained accuracy as N/A, not 0%. Set the LLM's sampling configuration explicitly and retain truncation/refusal/provider errors rather than treating every response as valid JSON.

The OpenRouter TypeSafe base URL and alias used in the script match the vendor's documented gateway setup. [SDK gateway example](https://docs.typesafe.ai/sdk/python/usage). Runtime availability, actual provider billing and the full live sequence remain to be checked.

### 7. Add the assumption behind the workflow-reliability calculation

Locations: `talk-track.md:186`; `lesson.html:1422`; `research-report.md:180`.

`0.95 ** 10` is approximately 60%. That applies if all ten steps must succeed and each has an independent 95% success probability, or the appropriate conditional success probabilities are all 95%. Ten marginal confidence readings cannot simply be multiplied. Shared context and policies can correlate errors, and some workflows recover from mistakes. Introduce the example with its assumption, then say to measure end-to-end task success directly.

Likewise, Jev questions being evaluated independently does not mean their errors are statistically independent.

## What to bring in from our Arena work

Add one short section, “What changed when we tested this ourselves.” It will make the lesson less dependent on vendor positioning and review roundups. Keep the two experiments visibly separate:

| Experiment | Supported conclusion | Boundary |
| --- | --- | --- |
| Full: Jev, English Laya and deterministic control | Jev matched 90.92% of 5,671 references under the strict contract; English Laya matched 55.49%. Their full-quality medians were 264.0 ms and 18.4 ms. | Jev was hosted; Laya was local on the RTX 5090. Other candidates did not run Full, and this was the English Laya checkpoint. |
| Demo: 13 configurations, 120 cases | Winnow matched 117 references; Jev matched 115. Decider, Winnow and Nimble were worthwhile local follow-up candidates. | This did not establish a winner. Removing two potentially ambiguous references as a separate sensitivity analysis eliminated the observed Jev/Winnow count difference. |

Sources: [accepted results](RESULTS.md), [independent review](ADVERSARIAL-REVIEW.md), [reference cautions](REFERENCE-CAUTIONS.md).

Three practical takeaways from those experiments are more useful than a larger leaderboard:

1. **The reference can be ambiguous.** Define policy precedence before scoring; a plausible alternative interpretation is not automatically a reasoning failure.
2. **Output validity and decision quality are different metrics.** Arena rejected some native probability sums under its strict tolerance even when labels matched. Those failures did not establish a vendor schema breach. The Full selected-label comparison was 91.55% versus 57.13%; disclose which metric is being taught.
3. **Measure workflow behavior.** A model can avoid restricted actions by sending everything to Review while making the workflow unusable. Record useful completion, unnecessary deferrals, violations and deadline misses, not just per-question accuracy.

Mention the alternative families without promising interchangeability: Laya, larger local decision configurations, conventional classifiers, NLI-based classifiers and generative JSON baselines occupied different quality/latency positions. A typed interface does not make them equally capable or calibrated.

## Smaller teaching edits

- Replace “known answers” in the introduction with “known answer options.” The correct answer is what the model must infer.
- Retain “roles, not model types” throughout. A non-thinking Gemini call that emits a category can be the fast classifier; generating JSON does not itself make it System 2. Consider naming the three demo configurations “generative classifier,” “decision model” and “reasoning escalation.”
- Separate generation versus classification from the amount of reasoning needed. A binary answer can require extensive investigation. A short generated answer can require almost none. In the selection checklist, assess reasoning/tool requirements before stopping merely because output must be written.
- Change absolute “no multi-hop reasoning” to “unreliable on some multi-hop or indirect questions.” The vendor describes weaknesses, not a proof of categorical inability. [Jev limitations](https://docs.typesafe.ai/model-jaggedness/jev-1.13).
- A Score of 1.4 is an expectation across levels, not necessarily uncertainty confined to the two adjacent levels. Inspect the full distribution. [Score semantics](https://docs.typesafe.ai/primitives/score).
- “Exact, instant, free” overstates deterministic code. Use “deterministic; usually cheap for these tasks.” Correctness still depends on inputs and implementation.
- Keep latency claims attached to their measurement. The roughly 100 ms figure is vendor-reported; our hosted Jev requests had a roughly 264 ms full-quality median. Gateway, network, payload, warmup and concurrency affect what students observe.
- The approximately 3,800-word talk track is around 27 minutes at 140 words/minute, before a live demo. If this is meant to be a short introductory lesson, shorten the historical timeline and research-number tour; spend that time on one complete decision-and-escalation example.

## Suggested core explanation

“A decision model scores a bounded set of answers instead of writing an open-ended response. That can make it a useful fast component inside an AI system. But a typed answer is not necessarily correct, and a probability is not automatically calibrated on our task. We test the labels, the probability signal and the workflow separately. Then code applies permissions, business rules and a validated routing policy to decide what can proceed and what needs more work.”
