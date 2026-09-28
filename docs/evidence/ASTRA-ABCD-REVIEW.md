# Astra adversarial review — separate ABCD assessment

Run `abcd-test-v1`, reviewed 28 September 2026. This automated review covers the final ABCD conclusions and revised video narrative. The completed Arena Full v2 measurements and earlier review were not changed. No inference, judge calls, purchases, quota resets or publication were performed during this review.

**Closing verdict: no material scientific or numerical blocker remains to the scoped video narrative and ABCD report.** The evidence supports Winnow leading this balanced combined recorded-step task, while Jev leads full-handbook conditional action selection. It does not support a universal winner, a semantic-acceptance ranking, a unique Jev long-context advantage, or live support success. The final materials make those distinctions explicit. Dashboard/export visual and privacy checks are a separate responsibility; this verdict does not certify those surfaces or authorize publication.

## Independent checks performed

- Confirmed 2,544 unique cases per profile and all 12,720 unique prediction records. Each prediction input hash matches its frozen case candidate. All five journal hashes match the saved verification summary.
- Verified the retained inference-source snapshots against their frozen hashes, all four frozen case/source manifests, and all 17 upstream source-file hashes.
- Reconstructed every natural case's visible conversation history directly from the original ABCD test conversation: all 2,400 histories contain only turns before the checkpoint. Every natural gold label matches the corresponding upstream target, or the explicitly synthesized terminal checkpoint. This check does not rely on the importer assigning its own gold correctly.
- Independently rebuilt combined route-plus-action counts from raw predictions, including both route and conditional action at true action checkpoints. Confirmed all strict/label totals, unsupported denominators and the by-route/nonterminal breakdowns in the report.
- Recomputed all 30-label macro-F1 values. Each condition contains all 30 reference actions, with supports from one to 55. The displayed F1 values agree with the raw reconstruction.
- Independently resampled 300 whole conversations 10,000 times for the four headline Winnow-minus-Jev combined intervals. Results exactly match the report: full strict +5.56 points [2.67, 8.44], full labels +4.67 [1.89, 7.44], retrieved strict +4.67 [1.67, 7.67], retrieved labels +3.78 [0.78, 6.78]. These remain exploratory unadjusted intervals conditional on this chosen policy/task mix.
- Recomputed every displayed natural request-latency median. They match the report's rounded values. The populations include supported invalid attempts; they are serial deployment measurements, not controlled prefill or throughput comparisons.
- Independently recomputed corrected retrieval coverage from original turn `targets[0]`: 236/300 action checkpoints and 731/900 route checkpoints. Terminal checkpoints use the last observed annotation. The correction affects analysis only; candidate hashes and journal hashes still match the freeze.
- Verified the 76 audit IDs equal the frozen IDs, the 118 planned jobs are unique case/answer pairs, and every one of the 33 flagged job IDs appears in the 21-question inspection. Inspected the original history for every flagged question and the accompanying rationale.
- Checked the two ABCD hosted ledgers: $0.004244352 development plus $1.206566844 main/warmups equals $1.210811196 recorded. The retained reservation exceeds this amount. Combined-with-v2 figures agree with the saved ledgers; neither represents invoice reconciliation or all project costs.

## Critical interpretation boundaries

### 1. Combined agreement and conditional action selection are genuinely different tasks

The combined denominator is 900 checkpoints per condition: 300 true actions, 300 agent messages and 300 synthesized endings. A true-action checkpoint requires both the route and action answer to match. Conditional action selection instead supplies the fact that an action is due and uses 300 examples. Those conditional questions provide useful information the combined routing task does not have.

On full-handbook true action checkpoints, Jev matches both route and action on 221/300, versus Winnow's 141/300. On agent-message checkpoints the direction reverses: Jev 69/300, Winnow 185/300. This is why Winnow can lead the balanced combined task while Jev leads conditional action selection. The report states this mechanism rather than treating the two rankings as contradictory or calling one a universal winner.

A further illustration: retrieval improves Winnow's conditional action labels from 200 to 229, but combined true-action successes go from 141 to 139. Its overall combined improvement comes from message checkpoints. The written claim is correctly limited to improved conditional action selection, not improved end-to-end execution of tool actions.

### 2. Recorded continuation is not the same as the uniquely correct support action

The route prompt asks for the next recorded step under the handbook, while conditional action prompts ask what the agent should do. Those aims can conflict when the human record delays a required click, omits a prerequisite, contains another farewell or repeats an action. This is an irreducible limitation of the frozen adaptation, not a reason to rewrite its gold afterward.

The current report and script disclose it prominently. “Recorded-next-step agreement” is the defensible wording. “Customer-support correctness,” “policy-compliance accuracy,” “customer resolution rate” or published ABCD/AST/CDS benchmark performance would overstate the evidence.

I inspected all 21 flagged histories. The inspection appropriately distinguishes:

- Optional closing messages: `abcd-6395-22-retrieved_policy-route`, `abcd-9811-12-full_handbook-route`.
- Policy repair versus the recorded next event: `abcd-10124-15-full_handbook-action`, `abcd-10228-10-full_handbook-route`, `abcd-3689-13-retrieved_policy-route`.
- Missing or ambiguous prior tool identity, delayed button logging and flexible troubleshooting order: `abcd-1021-11-retrieved_policy-action`, `abcd-3619-5-full_handbook-action`, `abcd-433-17-full_handbook-action`, `abcd-4331-11-retrieved_policy-action`, `abcd-9760-10-retrieved_policy-route`.
- Missing retrieved procedures: `abcd-295-10-retrieved_policy-route`, `abcd-3538-17-retrieved_policy-action`, `abcd-5691-16-retrieved_policy-route`.
- Ambiguous task scope or permissible action/message order: `abcd-1822-11-retrieved_policy-route`, `abcd-6942-4-full_handbook-route`, `abcd-7859-7-full_handbook-route`.
- Missing prerequisites or amount specificity: `abcd-312-14-retrieved_policy-route`, `abcd-7688-19-retrieved_policy-route`.
- A repeated source action: `abcd-1655-42-retrieved_policy-action`.
- Retrospective policy repair being mistaken for a continuation of an already completed dialogue: `abcd-456-13-full_handbook-route`, `abcd-6080-22-retrieved_policy-route`.

An ambiguous verdict is not acceptance of every proposed answer. The existing inspection explicitly rejects that inference, including irrelevant/repeated FAQ actions and tool alternatives unsupported by the supplied procedure. No semantic re-ranking was produced, and none is justified from this small audit.

### 3. Balanced checkpoints and synthesized endings change the meaning of the percentage

The class mix was declared in advance, which prevents selection based on outcomes, but it remains an artificial weighting rather than production prevalence. Endings comprise one third of the combined task and are relatively easy. The report's nonterminal n=600 table is therefore useful and correctly separate: full-handbook label agreement remains Winnow 326/600 versus Jev 290/600. Removing endings does not reverse that observed lead, but neither denominator is a deployment success rate.

The conversation bootstrap preserves the three checkpoint outcomes per conversation. It does not create uncertainty over unseen companies, handbook policies, annotation conventions or prompts. Many conversations share procedures. The video should retain its fixed-task and unadjusted-comparison qualifications.

### 4. The retrieval correction is justified but remains a diagnostic

Original scenario names are not always canonical handbook section IDs and can disagree with the actual dialogue. The corrected actual-step annotation matches the stated coverage question better. I reproduced the corrected counts from original source turns without modifying predictions.

This does not prove that the retrieved text contains every required fact, that only one procedure is relevant, or that a hit causes correctness. The source annotation is used only after inference. It must never be described as an oracle supplied to candidates. The retained initial summary contains the superseded scenario-string diagnostic; consumers should use `abcd-retrieval-correction.json` for this analysis.

### 5. Context capacity, probability validity and timing require separate claims

Nimble has 1,308 explicit unsupported records: all 1,200 natural full-handbook questions and 108 stress variants. Its available counts must remain 1,236, not an apparent 48.58% reasoning success rate. There is no five-profile common full-handbook cohort. Qwen's 32K is a chosen serving ceiling below its backbone configuration; Winnow's 64K profile was not tested to its full limit.

The full natural inputs are long principally because of the shared handbook. The synthetic control merely locates an explicit rule among neutral distractors. Four profiles match 144/144 labels, while Nimble matches its 36 supported cases. Decider has only 91/144 strict passes in that control, so “all profiles passed every test” would be false. The final script makes the label/contract distinction and calls the control too easy to separate the four supported profiles.

Jev's hosted full-handbook medians are lower than local medians here, but backend hardware and caching are not controlled. Preserve the serial request, precision, prefix-cache and network qualifications. No architectural latency or maximum-throughput conclusion follows.

### 6. Audit and cost claims are properly bounded

The audit has 27 successful batches and one retained failed attempt, not 28 successful grading calls. The 118 judgments are answer reviews over 76 selected questions, not independent test examples. The 33 flags cover 21 questions, with no human annotation or changed gold. Requested model identity is Astra; observed identity was not exposed. The initial quota interruption and later completion are disclosed without inventing purchases or resets.

The candidate window is 196.14 minutes and excludes the later audit/review. Quoted Jev cost is application ledger usage with a remaining HTTP503 billing uncertainty, separate from Codex, hardware, electricity and earlier unrelated work. This is the defensible interpretation, not a total project bill.

## Corrections and closing assessment

The new ABCD rows and filming notes in `VIDEO-SPINE.md` initially contained literal backslash-n sequences, which would collapse the production table. This was reported and the coordinator confirmed replacement with actual line breaks. No substantive numerical correction to the final ABCD report or narrative was required by this review.

The strongest likely viewer retorts are now answered: the winning model depends on whether timing or conditional action is scored; dialogue continuation can be ambiguous; one-third of combined checkpoints are easy endings; only five previously selected profiles were tested; the context control is simple; Nimble's capacity gap is not a reasoning failure; and a blinded AI audit is not human ground truth. Keep those qualifications with the headline visuals.

Reviewed material: `docs/ABCD-PROTOCOL.md`, `docs/ABCD-RESULTS.md`, `docs/evidence/ABCD-AUDIT-REVIEW.md`, `docs/evidence/abcd-v1-summary.json`, `docs/evidence/abcd-v1-supplement.json`, `docs/evidence/abcd-retrieval-correction.json`, `docs/VIDEO-SCRIPT.txt`, `docs/VIDEO-SPINE.md`; raw `.arena/abcd-v1/test-freeze.json`, `test-cases.jsonl`, run journals, source snapshots, ledgers and audit plan/report/inspection. No third-party source dialogue is reproduced in this note.
