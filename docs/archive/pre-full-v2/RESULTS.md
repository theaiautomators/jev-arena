# Accepted measurements

These are measurements of pinned deployment profiles on one Windows RTX 5090 machine on 27 September 2026. Hosted Jev latency includes the network. Strict accuracy requires a matching reference label and Arena's fixed output rules. These results do not establish a universal winner.

## Thirteen-entry Demo

Run `20260927-142204-8262c6` completed all 1,560 predictions, 52 workflow episodes and 161 blinded answer reviews across 60 questions. The 120 questions comprise 72 original and 12 easy public JevBench cases plus 36 formal policy fixtures. There are no hard JevBench cases in this Demo. All entrants support all 120 cases.

| Deployment | Strict correct / 120 | Selected labels / 120 | Median quality request |
|---|---:|---:|---:|
| Jev 1.13 hosted | 115 | 115 | 267.6 ms |
| Plumb 4B | 113 | 113 | 34.3 ms |
| Decider 4B v2 | 115 | 115 | 43.7 ms |
| Winnow 12B Q8 | 117 | 117 | 52.6 ms |
| SemIf 4B | 109 | 109 | 36.7 ms |
| CLM 8B | 43 | 43 | 50.7 ms |
| Nimble 9B | 112 | 112 | 45.4 ms |
| Laya English | 86 | 87 | 16.8 ms |
| Laya typed | 82 | 82 | 17.5 ms |
| Laya multilingual | 61 | 61 | 13.7 ms |
| Qwen 3.5 JSON | 111 | 111 | 285.2 ms |
| ModernBERT NLI | 74 | 74 | 17.6 ms |
| Uniform probabilities, first label | 41 | 41 | 0.0036 ms |

Twelve entrants produced 120 valid outputs. Laya English produced 119; one correct label had probabilities summing to 0.9998, outside the chosen 1e-4 tolerance. Selected-label accuracy is an explicitly post-hoc diagnostic, not a replacement primary metric. Label-only Qwen does not face a probability-sum requirement. The uniform row is deterministic arithmetic, not random guessing or neural inference.

Winnow minus Jev is +1.67 percentage points with a descriptive paired 95% interval of **-3.33 to +5.88 points**. That does not establish superiority or equivalence. SemIf's median is about 7.8 times lower than this Qwen JSON profile's median; this is not a server-throughput comparison or a universal speedup.

### Workflow interpretation

Jev, Decider, Winnow and Nimble completed both ticket and both warehouse episodes. Other profiles completed neither task in this two-seed test. Episode success alone hides the mechanism:

- Laya, both Laya variants, Plumb and Qwen sent all 24 tickets to Review: 8/24 correct, no restricted-account violations, and 16/16 unrestricted tickets unnecessarily deferred.
- CLM sent all 24 to Billing: 6/24 correct and eight restricted-account violations.
- SemIf got 10/24 ticket decisions correct; NLI got 12/24.
- Many warehouse failures repeat one blocked action against an unchanged state. Violation steps are not independent mistakes. All seeds permit a ten-step edge route; a deterministic shortest-path oracle solves this toy environment.

### Reference-wording sensitivity

Two Demo routing questions combine a payment topic with the service marked unavailable, without stating rule precedence. Both are among Jev's five primary misses. Engineering is a plausible alternate reading. See [the caution and exact affected IDs](REFERENCE-CAUTIONS.md).

The primary labels remain frozen. A separate **post-hoc exclusion** leaves 118 shared reference cases: Jev and Winnow both score 115/118 (97.46%); Decider scores 113/118 (95.76%); Laya scores 84/118 strict (71.19%) or 85/118 selected labels (72.03%). This sensitivity removes the observed Jev/Winnow count difference, further ruling out a winner claim from this Demo.

The judge agreed with the references on its sampled answers; that does not settle this linguistic ambiguity. Its 161 reviews represent distinct answers across 60 questions, including all 36 formal fixtures and 24 public questions, not 161 independently sampled questions.

Machine-readable aggregates: [Demo evidence](evidence/demo-summary.json). Original predictions, model revisions, runtime hashes, inputs and traces remain in the local run; use the app's export for a portable report.

## Jev, English Laya and control: Full comparison

Run `20260927-144758-15b0d8` completed all **23,013 static records**, dedicated timing, **240 workflow episodes** and **117 blinded answer reviews across 60 case IDs**. All three entrants support all 7,671 records; the shared primary denominator is **5,671 reference cases**. The other 2,000 are teacher-agreement cases. The multilingual and typed Laya checkpoints were not tested in Full.

| Entrant | Strict correct / 5,671 | Strict accuracy | Selected labels / 5,671 | Label accuracy | Valid outputs / 7,671 | Quality p50 |
|---|---:|---:|---:|---:|---:|---:|
| Jev 1.13 | 5,156 | 90.92% | 5,192 | 91.55% | 7,588 | 264.0238 ms |
| Laya | 3,147 | 55.49% | 3,240 | 57.13% | 6,996 | 18.3569 ms |
| Uniform baseline | 2,088 | 36.82% | 2,088 | 36.82% | 7,671 | 0.0037 ms |

The selected-label diagnostic ignores Arena output validity and is post-hoc. Jev has 83 invalid outputs overall, 74 on the reference cohort; Laya has 675, all on references. These are probability-sum failures, not missing decisions. Correct labels recovered by the diagnostic number 36 for Jev and 93 for Laya. The observed label-agreement gap therefore persists when the probability requirement is removed. Calibration uses only the valid probabilistic reference subset: 5,597 Jev cases and 4,996 Laya cases.

Laya minus Jev strict accuracy is **-35.43 percentage points**, with a descriptive paired 95% cluster-bootstrap interval of **-39.35 to -31.23** on these 5,671 cases. This describes the fixed suite, not a random population of future workflows. Shared templates and possible public training exposure remain limits.

### Pack breakdown

| Reference pack | Cases | Jev strict | Jev labels | English Laya strict | English Laya labels |
|---|---:|---:|---:|---:|---:|
| JevBench public | 231 | 202/231 (87.4%) | 202/231 (87.4%) | 125/231 (54.1%) | 128/231 (55.4%) |
| Classification | 1,500 | 1318/1500 (87.9%) | 1331/1500 (88.7%) | 1022/1500 (68.1%) | 1089/1500 (72.6%) |
| Multilingual | 1,000 | 794/1000 (79.4%) | 817/1000 (81.7%) | 332/1000 (33.2%) | 353/1000 (35.3%) |
| RAG relevance | 500 | 469/500 (93.8%) | 469/500 (93.8%) | 260/500 (52.0%) | 260/500 (52.0%) |
| Arena Fresh | 1,440 | 1403/1440 (97.4%) | 1403/1440 (97.4%) | 823/1440 (57.2%) | 825/1440 (57.3%) |
| Robustness | 1,000 | 970/1000 (97.0%) | 970/1000 (97.0%) | 585/1000 (58.5%) | 585/1000 (58.5%) |

The multilingual pack tests the English Laya checkpoint, not its multilingual sibling. Differences also appear on the English formal fixtures, but those fixtures share eight policy templates and the reference-wording caution still applies. The Laya loader warned that its shipped choice temperature for 11+ options was clamped by the native loader and confidence for those entries should be treated as uncalibrated. This is not evidence that its selected labels were changed by an Arena temperature adjustment.

The relevance pool is imbalanced: the deterministic first-label control gets 453/500 (90.6%), versus Jev's 469/500 (93.8%). High raw relevance accuracy alone therefore says little about useful retrieval; inspect the fixed-pool ranking diagnostics and their complete-query denominators.

Teacher agreement, excluded from the main table: Jev **72.9%**, English Laya **36.1%**, uniform **27.65%**, each over 2,000 supported teacher cases. Agreement with this teacher is not correctness.

### Sensitivity to the 50 flagged routing references

Excluding the preidentified potentially ambiguous cases leaves 5,621 shared reference cases. This is a post-hoc sensitivity calculation; the frozen primary scores above remain unchanged.

| Entrant | Strict agreement | Selected-label agreement |
|---|---:|---:|
| Jev | 5,152/5,621 (91.66%) | 5,188/5,621 (92.30%) |
| English Laya | 3,108/5,621 (55.29%) | 3,201/5,621 (56.95%) |
| Uniform first label | 2,054/5,621 (36.54%) | 2,054/5,621 (36.54%) |

### Dedicated serial timing

Each block contains the same first 200 frozen public JevBench cases. These are different measurements from the full-quality request medians in the headline table. Loading/warmup are excluded; a single adapter request is in flight.

| Entrant | Block p50 values, ms | Block requests/second | Valid responses across 600 requests |
|---|---:|---:|---:|
| jev | 250.5, 257.4, 263.1 | 3.86, 3.76, 3.69 | 598/600 |
| laya | 17.2, 16.1, 17.1 | 38.70, 39.34, 31.51 | 588/600 |

End-to-end deployment timing includes hosted network latency for Jev. It is not peak model throughput; no concurrency-4/16, native batching or multi-window hosted comparison is claimed. Uniform arithmetic timing is not a neural-model speed comparison. Laya completed the initial load plus two additional load/unload cycles, each passing container and memory cleanup.

### Full workflows

| Entrant | Untimed ticket episodes | Untimed warehouse episodes | 500 ms ticket episodes | 500 ms warehouse episodes |
|---|---:|---:|---:|---:|
| Jev | 20/20 | 20/20 | 19/20 | 20/20 |
| English Laya | 0/20 | 0/20 | 0/20 | 0/20 |
| Uniform first label | 0/20 | 0/20 | 0/20 | 0/20 |

Jev had one deadline miss: a late ticket decision, with 239/240 routes correct in deadline mode versus 240/240 untimed. English Laya had no deadline misses but sent every ticket to Review in both modes: 62/240 correct, all 178 unrestricted tickets unnecessarily deferred, and no restricted-account violations. Its 700 warehouse violation steps per mode repeat blocked actions against unchanged states. Uniform routed 58/240 tickets correctly, violated 62 restricted-account rules per mode, and recorded 800 blocked warehouse steps per mode. These are the same two simple task templates over twenty seeds, not 240 independent task types.

## Practical interpretation

The Full judge returned 52 correct, 55 incorrect and ten ambiguous verdicts. Three judge/reference disagreements concern two case IDs: `xnli-4703-ar` and `fresh-test-03-059-noul`. The XNLI example admits competing literal/pragmatic interpretations. The tool example asks whether approval is missing for a read; Astra accepted both yes and no under absence-of-approval versus no-approval-required readings, without flagging ambiguity. Ten ambiguous grades covered seven teacher cases already excluded from the main score. These findings remain visible and do not change the labels. See the [adversarial review](ADVERSARIAL-REVIEW.md) for evidence and additional wording cautions.

Machine-readable aggregates: [Full evidence](evidence/full-summary.json). Requested judge: GPT-6 Astra through Codex CLI 0.157.1; the tested CLI did not expose an observed model identifier.

Jev has substantially higher reference agreement than English Laya in this Full profile, with higher request latency. The short Demo makes Decider and Winnow reasonable local candidates for a larger follow-up, not established substitutes for Jev. Nimble also completed the Demo workflows. SemIf offers an interesting same-backbone scoring-versus-generation comparison, while CLM requires further native numerical parity and task-fit investigation before broad conclusions.

The public repository is prepared for `theaiautomators`; publication is deferred until tomorrow. Human semantic auditing, a Full all-roster experiment, native numerical parity experiments, optimized serving profiles and non-5090 GPU checks remain outside this acceptance scope.
