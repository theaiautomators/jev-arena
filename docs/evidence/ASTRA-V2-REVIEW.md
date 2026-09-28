# Astra adversarial review — Full v2

Run: `20260927-205440-6350b9`. Review date: 28 September 2026. This is an automated adversarial review of saved evidence, not a human annotation exercise. No candidate/judge calls were made, no reference labels changed, and no measured outputs edited. Final script review is pending at this stage.

## Material findings and claim boundaries

1. **High: Winnow's all-reference deficit includes a harness capability error.** The saved run has 500 BANKING77 HTTP 400 failures. The coordinator identified a native 64-option cap while the registry advertised 255; BANKING77 has 77. Those records are real failed attempts, but they are not 500 reasoning errors. Preserve the frozen ledger and disclose the mistaken capability declaration. The shared 4,635-reference cohort already excludes BANKING77, so its comparison is unaffected. Follow-up failures on 13 BANKING77 cases per condition likewise are not evidence of nondeterministic answers.
2. **High: strict and selected-label rankings answer different questions.** Jev is 5,217/5,671 strict versus 5,263 selected-label; Decider is 4,752 versus 5,235. Describing Decider's whole strict deficit as reasoning failure would be misleading. On the same 4,635 references, Jev has 4,414 selected-label matches, Winnow 4,385, Decider 4,378, and Nimble 4,280. Say these are measured profile results on this cohort; the top gap is only 29 answers (0.63 percentage points).
3. **High: interval scope must match the claim.** `results.json` comparisons use pairwise supported reference cohorts and STRICT correctness. They are not intervals for all-entrant shared selected-label accuracy. For example Jev/Nimble uses 5,671 references, whereas Jev/Plumb uses 4,671. The bootstrap joins related scenario clusters and identical inputs; it does not establish uncertainty over unseen policy templates. The fresh formal suite shares eight templates. Multiple comparisons are descriptive, without corrected significance claims.
4. **High: the judge is a diagnostic, not a replacement truth source.** There are 879 deduplicated answer reviews on 300 questions, not 879 independent questions. The 250 frozen pack-balanced questions produced 725 reviews; the 50 outcome-selected disagreement questions produced 154. Their populations and sampling probabilities differ. Raw audit fractions cannot estimate suite-wide error/ambiguity prevalence. The CLI requested Astra but did not expose an observed model ID.
5. **High: an ambiguous verdict does not endorse the proposed answer.** The judge marks `classification-banking77-173` / `activate_my_card` ambiguous while explicitly saying activation lacks support. The same issue occurs for `massive-11915-hi` / `transport_taxi` and `massive-3050-ar` / `iot_hue_lightdim`. Count these as flags about question interpretation, never rescued model answers. Some case-level ambiguity judgments are themselves debatable, as detailed below.
6. **Medium: limited parity and deployment fairness.** CLM parity covers 36 short development probes, not the Full corpus or near-limit contexts. Batch-invariant kernels explicitly change its speed profile. Sequential serial request timings, overlapping CLI host work, an unexplained runner exit/resume, and hosted-versus-local deployment differences prevent peak-throughput or controlled idle-host claims. Describe CLM's poor measured profile result without declaring its architecture universally incapable.
7. **Medium: no long-context quality claim.** Jev input-token median 423, p95 1,756, max 4,297 in this run does not test near-limit context quality. Configured deployment caps are not native architecture limits.
8. **Medium: follow-up stability needs usable-answer denominators.** The 200 Choice cases are reused under exact-repeat and reversed-order conditions; these are 1,600 additional predictions, not independent new test cases. Selected labels may be usable even when probability contracts fail. Report availability separately from answer agreement. The saved Jev follow-up transport failure was a local cost-ledger replacement error, not evidence of a remote API outage.

## Audit arithmetic independently checked

| Subset | Questions | Answer reviews | Correct | Incorrect | Ambiguous |
|---|---:|---:|---:|---:|---:|
| Frozen representative | 250 | 725 | 218 | 413 | 94 |
| Outcome-selected disagreements | 50 | 154 | 36 | 77 | 41 |

Reference questions: 215 representative and 34 disagreement. Teacher questions: 35 representative and 16 disagreement. Among reference reviews, 43 ambiguity verdicts concern 21 questions; 12 unambiguous disagreement verdicts concern seven questions. These sets overlap on two questions, yielding **55 flagged reviews on 26 unique reference questions**, not 28. Teacher ambiguity comprises 92 reviews on 38 questions. Teacher disagreement remains separate from primary reference accuracy.

## Seven reference cases with an unambiguous disagreement verdict

These are judgments of the supplied task, not corrections to source datasets. The two marked overlap also received an ambiguous verdict for another proposed answer.

| Case ID | Assessment after inspecting case and rationale |
|---|---|
| `scifact-768-6421792` | Gold yes; judge favors no. The abstract concerns NT5C2 drug resistance, whereas the claim concerns TPMT metabolism. This is a credible mismatch between broad retrieval relevance and direct claim evidence, not conclusive proof that the source qrel is erroneous. |
| `scifact-859-22049489` | Gold no; judge favors yes. The abstract explicitly presents RUNX1 as a tumor suppressor, relevant to refuting a tumor-promoting claim. Strong evidence of the known unjudged-as-nonrelevant limitation in the adapted retrieval task. |
| `xnli-3834-hi` | Gold entailment; judge favors neutral. Being worthy of support versus needing support is a plausible semantic distinction. The translation and annotation convention deserve review; do not present the judge as definitive. |
| `xnli-1741-de` | Gold entailment; judge favors neutral. The premise's excited gunner and Pitt turning do not establish dizziness or walking beside him. Strong supplied-text support for the judge's objection. |
| `xnli-4623-es` | Gold contradiction; judge favors neutral. German-government cooperation and unconditional acceptance of a law have no supplied logical connection. Strong supplied-text support for the judge's objection. |
| `massive-50-en` | Gold datetime_convert; alternative datetime_query judged correct, gold judged ambiguous. Current time in a named offset fits both surface readings without dataset label definitions. This is a taxonomy boundary, not a proven bad gold. |
| `classification-ag news-3404` | Gold Sci/Tech; Business judged correct, gold judged ambiguous. Processor-company earnings cross technology/business boundaries. The judge's asymmetric certainty is not adequate grounds to relabel. |

## All 21 reference ambiguity cases inspected

| Case ID | Mechanism and review assessment |
|---|---|
| `classification-ag news-1898` | Corporate adoption of anti-spam technology: Business/Sci-Tech boundary plausible. |
| `classification-ag news-2671` | Bankers' international extradition over corporate fraud: Business/World boundary plausible. |
| `classification-ag news-3175` | Astronaut obituary: Sci-Tech/general-news boundary plausible; source taxonomy remains valid convention. |
| `classification-ag news-3404` | Technology earnings: Business/Sci-Tech boundary; also in disagreement table. |
| `classification-ag news-4` | Environmental regulation: science/public-policy boundary plausible. |
| `classification-ag news-4230` | Internet crime economy: technology/business boundary plausible. |
| `classification-banking77-173` | Unspecified fee leaves transaction type unknown. Card activation is still unsupported; ambiguity must not grant it credit. |
| `classification-banking77-219` | Failed ATM withdrawal and pending transaction both explicit; priority between two banking intents unspecified. |
| `classification-banking77-2692` | Transfer absent after hours: destination and pending/balance status unclear. |
| `jevbench-hard-opus-a-probability-04` | Distribution implies on-time is most likely. Judge objects that a future outcome is unknowable and probabilities were hidden. This is partly an audit projection limitation: a label-only judge cannot review the requested probability vector. It does not refute the most-likely-label reference. |
| `jevbench-hard-opus-a-probability-08` | Evidence implies 71% connection, 29% miss. Same probability-to-label projection issue; judging both categorical labels ambiguous should not erase the preferred outcome under the scoring convention. |
| `jevbench-hard-sol-a-adversarial-09` | Missing governing matrix thresholds support caution, but the explicit major multi-customer degradation category and observed partial failures favor score 2. Treat ambiguity as a debatable flag, not established reference invalidity. |
| `massive-11915-hi` | Desire for a drink does not specify coffee or ordering. Taxi remains unsupported despite an ambiguous verdict. |
| `massive-3050-ar` | Input contains both light-color change and switching off. Dimming is not thereby justified. The text is English despite Arabic locale metadata, so language slices measure dataset locale, not perfectly verified text language. |
| `massive-50-en` | Current-time versus timezone-conversion taxonomy boundary; also in disagreement table. |
| `massive-9193-es` | Repeating a date could describe calendar or alarm setup without further context. |
| `massive-9353-hi` | Music and radio both named; explicit radio gives the gold a reasonable more-specific reading. Ambiguity flag is not proof equal alternatives are required. |
| `massive-9678-es` | Named work lacks playback medium; audiobook/music/game ambiguity plausible, but unrelated general-conversation answers do not automatically become acceptable. |
| `scifact-1204-31141365` | Abstract addresses relevant cells/chromatin but omits the exact modifications; broad retrieval relevance versus direct evidence threshold unresolved. |
| `xnli-2461-ar` | Malformed hypothesis and unclear attachment undermine a confident logical relation. |
| `xnli-40-ar` | Garbled entity names make aircraft-versus-submarine interpretation depend on recognition beyond clearly stated text. |

## Teacher ambiguity mechanisms

The teacher subset measures agreement with another model, not verified correctness. Representative examples: invoice discrepancy severity (`typed-invoice_processing_000017-discrepancy_severity`) lacks a materiality threshold; security urgency (`typed-security_incidents_000080-urgency`) lacks a response-time mapping; security compromise (`typed-security_incidents_000058-credential_compromise`) has suspicious activity without decisive authorization facts; customer-service action (`typed-customer_service_000042-action`) lacks escalation authority; trace intervention (`typed-agent_trace_observability_000050-action`) lacks thresholds mapping metrics to actions; risk (`typed-agent_trace_observability_000003-risk`) lacks actual action details. These are reasons to keep teacher agreement separate and qualify policy-compliance claims. No teacher labels were repaired.

## Likely viewer objections and defensible wording

- “You penalized a competitor for your broken adapter.” Acknowledge the Winnow capability declaration error before displaying its all-reference score; show the shared cohort alongside it.
- “Your winning margin is just rounding and hand-picked tasks.” Show strict plus selected-label counts, shared denominator, pack outcomes, and the shared-template limitation. The aggregate is a chosen task mix, not a universal winner.
- “The AI judge rubber-stamped your preferred model.” Describe blinded deduplicated answer review, disclose observed identity unavailable, retain disagreements and judge inconsistencies, and leave gold unchanged.
- “You slowed CLM down to make it lose.” Explain the explicit deterministic serving profile and small native parity scope; do not claim peak speed.
- “A hundred thousand samples proves real-world reliability.” Say 99,723 saved main records across 13 profiles on 7,671 shared cases, plus separately measured workflow and follow-up records. Correlation, repeated templates, limited workflows and reused follow-up questions constrain generalization.

Evidence: `.arena/runs/20260927-205440-6350b9/{results.json,cases.jsonl,predictions.jsonl,judge-jobs.jsonl,audit-selection.json,followups/}`; `docs/evidence/full-v2-summary.json`; `arena/scoring.py`; `arena/audit.py`; `docs/evidence/clm-preflight-recovery.md`; `docs/evidence/parallel-audit-amendment.md`. The evidence paths identify retained local records; no third-party full source passages are reproduced here.

## Closing review of final written materials

Reviewed `docs/RESULTS.md`, `docs/VIDEO-SCRIPT.txt`, `docs/VIDEO-SPINE.md`, `docs/evidence/full-v2-supplement.json`, and `docs/evidence/winnow-option-limit.md` after their Full v2 rewrite. Independently rebuilt the three headline shared selected-label paired intervals from raw predictions; all exactly match the supplement. Independently checked 99,723 unique main records, 5,671 primary references, the 4,635 shared intersection, all 1,600 follow-up records, and usable-label agreement denominators. The native Winnow source limits label tokens to 64 and rejects larger candidate counts; the incident disclosure is supported.

Two final wording issues were identified and verified corrected:

- Within-tolerance probability vectors can be renormalized with `normalized_rounding` recorded. The results now state this explicitly instead of implying that vectors are never normalized. Raw main records flag such normalization for 54 Jev and 2,048 Decider predictions; outside-tolerance vectors remain rejected.
- Reversed-order differences are comparisons with the original main run, not an isolated causal estimate of order effects. Jev's `jevbench-hard-opus-c-temporal_numeric-03` also changes on exact repeat. The script and results now acknowledge order sensitivity or run-to-run variation without claiming to isolate the cause.

**Closing verdict: no remaining material blocker to the scoped video narrative in these written materials.** The reported shared-cohort rankings, validity distinctions, follow-up counts, audit scope, workflow outcomes and ledger totals are consistent with the inspected evidence. The strongest objections are now addressed where they matter: the Winnow harness mistake is admitted, selected-label agreement is distinguished from strict correctness, the restricted shared cohort is identified, close margins are not called equivalence, automated review is not presented as human truth, and neither throughput nor long-context superiority is claimed.

This verdict is limited to the reviewed claims and retained evidence. It does not turn the fixed suite into a representative deployment population, certify native parity beyond the saved probes, establish scientific publication readiness, or authorize external publication. Dashboard visual/export checks and the final recording still need to preserve the written denominators and qualifications. The saved human-audit gate remains unmet and is disclosed. ABCD results remain a separate future assessment; this review does not cover them.
