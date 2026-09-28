# Arena Full v2: measured results

**For builders and the video:** [Practical takeaways and plain-English scoring guide](BUILDER-TAKEAWAYS.md). The dashboard now leads with the existing shared selected-answer comparison; the original strict metrics and all measurements below remain unchanged.

**Separate follow-on:** [ABCD next-step/action assessment](ABCD-RESULTS.md) has 12,720 independently verified records, a completed blinded audit and a completed Astra adversarial closing review. Its contexts and denominators are separate from all v2 numbers below. Original v2-only materials remain [archived](archive/full-v2-final/RESULTS.md).

Run `20260927-205440-6350b9`, 27–28 September 2026, Windows RTX 5090 (32 GB). This supersedes the [earlier Demo and three-entry Full report](archive/pre-full-v2/RESULTS.md). Original runs remain intact.

**Jev led this suite; several local profiles were close on shared label selection and much faster per serial request. There is no universal winner.** On the identical 4,635-reference cohort, Jev matched 95.23% of labels, Winnow 94.61%, Decider 94.46%, and Nimble 92.34%. These are pinned deployment profiles, not interchangeable model families or latest-version claims.

## Scope and scoring

All 13 entrants finished 7,671 static records each: **99,723 unique records**, including unsupported/failed attempts. Each has 5,671 primary reference cases and 2,000 teacher-agreement cases before capability exclusions. There are also **39 serial timing blocks, 1,040 workflow episodes, 33 local load/cleanup cycles**, and **1,600 targeted follow-up predictions**. Failed/unsupported records are not successful model answers. The 13 entrants include three related Laya configurations and diagnostic controls, not 13 independent architectures.

Primary strict correctness requires both the reference label and Arena's frozen output contract. Selected-label agreement ignores probability formatting and is a secondary diagnostic. A probability-sum tolerance of 1e-4 is an Arena choice, not a universal vendor guarantee. Qwen returns labels without probability vectors and does not face that sum requirement. Vectors inside the tolerance may be renormalized, with `normalized_rounding` recorded; vectors outside it are not repaired. Gold labels remain unchanged.

The shared reference cohort excludes 1,000 high-cardinality cases unsupported by Plumb/SemIf and 36 context-unsupported CLM cases. Thus it is a **restricted intersection**, not the entire workload. The recorded all-entrant shared count including teacher cases is 6,635; use **4,635** for reference accuracy.

## Same 4,635 references for every entrant

| Profile | Strict correct | Label matches | Label agreement |
|---|---:|---:|---:|
| Jev 1.13 | 4,412 | 4,414 | 95.23% |
| Winnow 12B | 4,385 | 4,385 | 94.61% |
| Decider 4B · v2 | 4,373 | 4,378 | 94.46% |
| Nimble 9B | 4,280 | 4,280 | 92.34% |
| Plumb 4B | 4,150 | 4,150 | 89.54% |
| Qwen 3.5 · JSON | 3,976 | 3,976 | 85.78% |
| SemIf 4B | 3,787 | 3,787 | 81.70% |
| Laya | 3,000 | 3,005 | 64.83% |
| Laya · typed | 2,960 | 2,962 | 63.91% |
| ModernBERT · NLI | 2,722 | 2,722 | 58.73% |
| Laya · multilingual | 2,604 | 2,610 | 56.31% |
| Uniform baseline | 2,075 | 2,075 | 44.77% |
| CLM 8B | 1,673 | 1,673 | 36.09% |

Jev's selected-label advantage is 29 answers over Winnow and 36 over Decider. Descriptive paired cluster-bootstrap intervals for **competitor minus Jev on this same cohort and label metric** are Winnow −0.63 percentage points [−1.25, −0.07], Decider −0.78 [−2.17, +0.38], and Nimble −2.89 [−5.59, −1.03]. The Decider interval crossing zero proves neither equivalence nor superiority. These are unadjusted exploratory comparisons on a fixed suite, not population guarantees. Related variants share clusters; eight formal templates remain a substantial dependence/generalization limit.

The dashboard's existing pairwise intervals instead describe **strict correctness on pair-specific supported cohorts**. They must not be attached to this shared selected-label table. Correctly scoped intervals are in [the supplement](evidence/full-v2-supplement.json).

## Full coverage, output validity and the Winnow harness error

**Winnow's 500 BANKING77 HTTP 400s came from a missed native 64-option limit; BANKING77 supplies 77 choices. Arena incorrectly advertised 255. These are failed requests caused by a capability mismatch, not 500 wrong decisions.** The recorded manifest/errors remain frozen; the future registry is corrected and a 64/65 boundary regression test passes. See [the incident and correction](evidence/winnow-option-limit.md). The shared table above already excludes BANKING77 and is unaffected.

The next table preserves each profile's *recorded* reference denominator. Different denominators and the Winnow capability mistake make it inappropriate to rank these rows as equal-coverage reasoning accuracy.

| Profile | Recorded reference n | Strict correct | Label matches | Valid outputs / 7,671 | Recorded unsupported |
|---|---:|---:|---:|---:|---:|
| Jev 1.13 | 5,671 | 5,217 (91.99%) | 5,263 (92.81%) | 7,587 | 0 |
| Winnow 12B | 5,671 | 4,813 (84.87%) | 4,813 (84.87%) | 7,171 | 0 |
| Decider 4B · v2 | 5,671 | 4,752 (83.79%) | 5,235 (92.31%) | 7,090 | 0 |
| Nimble 9B | 5,671 | 5,121 (90.30%) | 5,121 (90.30%) | 7,671 | 0 |
| Plumb 4B | 4,671 | 4,177 (89.42%) | 4,177 (89.42%) | 6,671 | 1,000 |
| Qwen 3.5 · JSON | 5,671 | 4,675 (82.44%) | 4,675 (82.44%) | 7,669 | 0 |
| SemIf 4B | 4,671 | 3,807 (81.50%) | 3,807 (81.50%) | 6,671 | 1,000 |
| Laya | 5,671 | 3,151 (55.56%) | 3,244 (57.20%) | 6,997 | 0 |
| Laya · typed | 5,671 | 3,056 (53.89%) | 3,234 (57.03%) | 7,111 | 0 |
| ModernBERT · NLI | 5,671 | 3,207 (56.55%) | 3,207 (56.55%) | 7,671 | 0 |
| Laya · multilingual | 5,671 | 2,806 (49.48%) | 2,927 (51.61%) | 7,023 | 0 |
| Uniform baseline | 5,671 | 2,096 (36.96%) | 2,096 (36.96%) | 7,671 | 0 |
| CLM 8B | 5,635 | 1,731 (30.72%) | 1,731 (30.72%) | 7,635 | 36 |

Jev reaches 91.99% strict and 92.81% selected-label agreement on all 5,671 references. Nimble has the highest local strict result on that full denominator, 90.30%. Decider reaches 92.31% selected-label agreement, only 28 labels behind Jev, but 83.79% strict. Across all 7,671 records, Decider has 581 probability-sum failures, Jev 84, Laya 674, typed Laya 560, and multilingual Laya 648. Two Qwen outputs select undeclared labels. Output quality and decision quality therefore need separate explanations.

As a **post-hoc capacity sensitivity**, excluding the 500 BANKING77 cases leaves 5,171 references: Jev is 4,818 strict / 4,852 labels; Winnow is 4,813 strict / 4,813 labels. That is only five strict answers apart. This does not replace the frozen primary result or establish equivalence.

Teacher agreement is excluded from all primary tables. All profiles have 2,000 teacher cases; agreement is not correctness:

Jev 1.13: 73.35%, Winnow 12B: 71.25%, Decider 4B · v2: 68.45%, Nimble 9B: 67.25%, Plumb 4B: 60.95%, Qwen 3.5 · JSON: 56.65%, SemIf 4B: 61.90%, Laya: 36.10%, Laya · typed: 76.90%, ModernBERT · NLI: 33.80%, Laya · multilingual: 34.65%, Uniform baseline: 27.65%, CLM 8B: 41.30%.

## Speed: repeated serial deployment measurements

Each timing block uses the same first 200 frozen public JevBench inputs, one request in flight, three blocks per profile. Loading and warmup are excluded. CLM supports only 172 of these 200 inputs per block. A fast invalid response is still included in attempted-request timing; inspect validity alongside latency.

| Profile | Three block p50 values (ms) | Valid responses / 600 |
|---|---|---:|
| Jev 1.13 | 244.70, 243.63, 245.13 | 600 |
| Winnow 12B | 55.00, 55.97, 59.14 | 600 |
| Decider 4B · v2 | 46.95, 47.45, 48.49 | 600 |
| Nimble 9B | 47.90, 49.68, 52.58 | 600 |
| Plumb 4B | 48.07, 49.59, 48.84 | 600 |
| Qwen 3.5 · JSON | 316.90, 318.95, 305.06 | 600 |
| SemIf 4B | 54.29, 50.96, 48.16 | 600 |
| Laya | 17.22, 16.60, 18.01 | 588 |
| Laya · typed | 18.10, 15.86, 17.06 | 597 |
| ModernBERT · NLI | 23.29, 20.45, 18.91 | 600 |
| Laya · multilingual | 15.19, 13.87, 13.45 | 594 |
| Uniform baseline | 0.00, 0.00, 0.00 | 600 |
| CLM 8B | 116.58, 117.22, 117.84 | 516 |

Jev's hosted network trip is included. The local profiles differ in size, precision and runtime; these are not each author's maximum-throughput servers. No concurrency/batching speedup or controlled idle-host claim is supported. Some Codex audit work overlapped on the host, though no local GPU benchmarks overlapped. CLM uses a declared batch-invariant profile after 36 short native development probes passed label parity and a maximum probability delta of 4.04e-7; this improves numerical reproducibility but changes latency and does not validate all contexts. See [the recovery note](evidence/clm-preflight-recovery.md).

## Small workflow tests

Twenty seeds per task and mode. Each ticket episode requires all 12 routes correct; warehouse success means reaching the goal. The deadline mode waits for a response then discards an action over 500 ms; it is an offline deadline simulation.

| Profile | Untimed tickets | Untimed warehouse | 500 ms tickets | 500 ms warehouse |
|---|---:|---:|---:|---:|
| Jev 1.13 | 20/20 | 20/20 | 20/20 | 20/20 |
| Winnow 12B | 20/20 | 19/20 | 20/20 | 19/20 |
| Decider 4B · v2 | 20/20 | 9/20 | 20/20 | 9/20 |
| Nimble 9B | 20/20 | 17/20 | 20/20 | 17/20 |
| Plumb 4B | 0/20 | 7/20 | 0/20 | 7/20 |
| Qwen 3.5 · JSON | 0/20 | 1/20 | 0/20 | 1/20 |
| SemIf 4B | 0/20 | 0/20 | 0/20 | 0/20 |
| Laya | 0/20 | 0/20 | 0/20 | 0/20 |
| Laya · typed | 0/20 | 0/20 | 0/20 | 0/20 |
| ModernBERT · NLI | 0/20 | 0/20 | 0/20 | 0/20 |
| Laya · multilingual | 0/20 | 0/20 | 0/20 | 0/20 |
| Uniform baseline | 0/20 | 0/20 | 0/20 | 0/20 |
| CLM 8B | 0/20 | 0/20 | 0/20 | 0/20 |

Mechanisms matter more than zeroes. Plumb, Qwen and all Laya variants route every untimed ticket to Review: 62/240 correct and 178 unnecessary deferrals. CLM sends all to Billing: 58/240 correct and 62 restricted-account violations. Jev has 240/240 correct ticket routes in each mode, while one invalid warehouse step in deadline mode still permits eventual success. Qwen has 20 ticket and 24 warehouse deadline misses; untimed and deadline quality must be kept distinct.

Warehouse failures often repeat a blocked choice against an unchanged state. Those repeated violations are not independent errors. Every grid permits a ten-step edge path. A deterministic planner solves this environment; the experiment tests these supplied interfaces and constraints, not difficult navigation or general agent competence. Production action masking, retries, tools or a different prompt can change results and were not tested here.

## Repetition and option-order checks

The declared rule selected Jev plus the top three eligible local contenders by shared label agreement: Winnow, Decider and Nimble. The same 200 reference Choice cases were repeated, then repeated with options and their associated criteria reversed. These are reused cases selected after the main comparison, not 1,600 independent new test cases.

| Model | Same label on exact repeat | Same label after reversal | Valid repeat / 200 | Valid reversal / 200 |
|---|---:|---:|---:|---:|
| Jev | 199/200 | 196/199 | 199 | 195 |
| Winnow | 187/187 | 183/187 | 187 | 187 |
| Decider | 200/200 | 196/200 | 180 | 186 |
| Nimble | 200/200 | 189/200 | 200 | 200 |

Agreement denominators require a usable selected label in both runs; labels can be usable even with invalid probability sums. Winnow's 13 unavailable answers per condition are the same option-limit issue. Jev's one unavailable reversed-order result was a **local Windows cost-ledger replacement error**, not an established remote API outage. Probability vectors were not asserted identical. Reversed-order runs differ from the original run on some answers, sometimes toward the reference and sometimes away. These comparisons can reflect order sensitivity or run-to-run variation; one repeat does not isolate the cause. Full strict/label follow-up counts remain in the machine-readable evidence.

## Astra audit and adversarial scrutiny

Codex CLI requested GPT-6 Astra; the tested CLI (0.157.1) did not expose an observed model identifier. No direct Claude/OpenAI judge API was used. There were **111 CLI calls, at most eight deduplicated case/answer reviews per call**, producing **879 answer reviews over 300 questions**. The 250 frozen pack-balanced questions produced 725 reviews; a separate 50 outcome-selected disagreement questions produced 154. This is neither one call per model prediction nor an audit of all 99,723 records.

All seven reference questions with an unambiguous judge disagreement and all 21 reference ambiguity questions were inspected. Two overlap, leaving **26 distinct reference questions with flags**. Taxonomy boundaries, translated entailment and retrieval relevance explain several disagreements. Some judge objections are themselves questionable: ambiguity does not endorse unsupported answers, and label-only projection of a probability task cannot assess the probability vector. No references were rewritten and no ambiguity flag automatically rescued an answer. The audit is pack-balanced/outcome-selected, so its raw flag fractions do not estimate prevalence across the suite. It is automated scrutiny, not human semantic validation. The saved `publication_ready=false` reflects that unmet human-audit gate; do not claim paper-level acceptance.

The [Astra adversarial review](evidence/ASTRA-V2-REVIEW.md) documents exact cases and likely viewer objections. Rubric controls passed 60 clear cases, 12 blind repeats and eight ambiguity probes; these establish limited control performance, not human agreement.

## Actual time and recorded costs

Main run including audit: **264.92 minutes (4 h 25 m)**. Through targeted follow-ups: **273.41 minutes (4 h 33 m)**. This includes an unexplained runner exit and resume, with completed predictions retained; it excludes earlier GPU waiting, native preflight and later report/review work. Local model loading is serialized under the shared GPU lease.

Jev application ledger: **$0.236304 main + $0.011839 follow-ups = $0.248143**. Conservative combined reservation is **$0.253519**. This includes warmup, timing and workflow requests as recorded; it is not a reconciled provider invoice. The local persistence error leaves a small billing uncertainty covered by the reservation. Local electricity, hardware, subscription cost and development runs are excluded.

Judge usage for those 111 calls: **1,461,596 input tokens**, including **433,664 cached**, and **77,308 output tokens**, of which 16,220 are reasoning tokens already included in output. Applying the standard Astra rates gives **364.46 standard-credit equivalent**. This is a comparison estimate, not observed billed credits or additional cash spend; included subscription usage follows different accounting, service mode can change pricing, and purchase prices depend on plan. No credits were purchased or reset redeemed. Controls, development and the final adversarial subagent review are outside that 111-call total. [Official credit pricing](https://learn.chatgpt.com/docs/pricing).

## What this supports, and what comes next

For this suite, Jev offers strong reference agreement and the most consistent success across these two small workflows. Winnow and Decider are credible local shortlist candidates on shared decisions; Nimble is particularly competitive under the full strict contract. Laya is very fast here but gives up substantial accuracy on this task mix. SemIf has lower shared label agreement than Qwen and the stronger decision profiles, despite much faster serial requests. CLM's weak measured profile does not establish that its architecture is universally ineffective. None of this proves a general replacement for a reasoning model.

Public dataset training exposure is unknown. Formal variants share eight templates. Locale labels are dataset metadata and some Arabic-labelled records contain English text. The relevance pool is imbalanced: Jev is 468/500 against a first-label control of 453/500. Calibration scores use valid probabilistic subsets and differing probability sources; they are not an apples-to-apples ranking of every entrant.

**This run does not test Jev's near-limit context advantage:** its measured main input tokens have median 423, p95 1,756 and maximum 4,297. The separately authorized ABCD next-action assessment will compare a full handbook with retrieved policy and an explicitly controlled context-stress extension. No ABCD results are claimed here and no fine-tuning is authorized.

Evidence: [independent summary](evidence/full-v2-summary.json), [follow-ups, intervals, runtime and ledger](evidence/full-v2-supplement.json), [frozen protocol](VIDEO-EVALUATION-V2.md), [verification](VERIFICATION.md), [teleprompter script](VIDEO-SCRIPT.txt), [video spine](VIDEO-SPINE.md). Portable dashboard/report files are saved separately under `.arena/reports/full-v2-report.*`. GitHub publication under `theaiautomators` remains deferred.
