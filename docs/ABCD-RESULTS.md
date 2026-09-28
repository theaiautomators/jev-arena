# ABCD: next-step and action selection

Run `abcd-test-v1`, 28 September 2026. All **12,720 candidate records** are complete and independently verified. The blinded CLI audit, all flagged-case inspections and [Astra adversarial closing review](evidence/ASTRA-ABCD-REVIEW.md) are complete; no material scientific or numerical blocker remains. Original [Arena v2 results](archive/full-v2-final/RESULTS.md) and their denominators are preserved.

**Winnow leads combined next-step agreement in this adaptation. Jev leads conditional action selection with the full handbook. More context does not consistently improve the complete pipeline.** These are results for five pinned serving profiles, not a universal ranking of model families.

## What was measured

Three hundred held-out ABCD conversations, each with one recorded action checkpoint, one noninitial agent-message checkpoint, and one synthesized terminal checkpoint. Each appears with the complete public handbook and with five BM25-retrieved policy sections. Each condition has 900 three-way routing questions and 300 conditional action questions. Every action question exposes all 30 ontology labels and explicitly says an action is due. The combined score requires the route and, when appropriate, the action to match the recorded reference. It does not score action parameters, generated messages or completed support cases.

There are 12,000 natural prediction records and 720 separately reported synthetic records. Five profiles each produced 2,544 records; unsupported capacity and failed requests remain in the record count. There was no fine-tuning. Selection, splits, prompts, profiles, scoring and audit IDs were frozen before test predictions. Seventeen upstream source files and all 2,400 natural inputs were independently reconstructed and checked. Target turns are scored before their text is added; scenario/intent/target/future fields cannot reach candidate inputs. See [the frozen protocol](ABCD-PROTOCOL.md).

## Combined routing and action

Strict agreement requires a correct label and valid Arena output. Label agreement ignores probability formatting. All scores below use the same 900 checkpoints per condition for profiles that support them. Nimble has no full-handbook support, so there is no five-profile shared full-handbook cohort.

| Profile | Full handbook: strict | Full handbook: label | Retrieved policy: strict | Retrieved policy: label |
|---|---:|---:|---:|---:|
| Winnow 12B Q8 | 616/900 · 68.44% | 68.44% | 626/900 · 69.56% | 69.56% |
| Jev 1.13 | 566/900 · 62.89% | 63.78% | 584/900 · 64.89% | 65.78% |
| Nimble 9B | Unavailable | Unavailable | 541/900 · 60.11% | 60.11% |
| Qwen 3.5 4B JSON | 504/900 · 56.00% | 56.00% | 518/900 · 57.56% | 57.56% |
| Decider 4B v2 | 414/900 · 46.00% | 54.33% | 479/900 · 53.22% | 59.00% |

Winnow minus Jev in strict combined agreement is +5.56 percentage points with the full handbook (paired 95% interval +2.67 to +8.44), and +4.67 with retrieval (+1.67 to +7.67). Selected-label differences are +4.67 (+1.89 to +7.44) and +3.78 (+0.78 to +6.78). These descriptive intervals resample whole conversations 10,000 times; they are not adjusted for multiple comparisons.

The ranking depends on the task mix. On true action checkpoints, full-handbook route-plus-action label agreement is Jev 221/300 versus Winnow 141/300. On agent-message checkpoints, it is Jev 69/300 versus Winnow 185/300. Winnow's combined lead reflects much better agreement about when to speak; it does not mean it leads every action-related task. This balanced mix is not the natural production prevalence of these decisions.

The synthesized end checkpoint is comparatively easy. Excluding those checkpoints, full-handbook combined label agreement is Winnow 326/600 (54.33%), Jev 290/600 (48.33%), Qwen 220/600 (36.67%), and Decider 201/600 (33.50%). With retrieval: Winnow 336/600 (56.00%), Jev 308/600 (51.33%), Nimble 256/600 (42.67%), Decider 242/600 (40.33%), Qwen 229/600 (38.17%). These are secondary, explicitly different denominators. Always choosing end would score 33.33% on the balanced combined task.

## Conditional selection among all 30 actions

These questions supply the fact that an action is due. They do not include the preceding routing challenge.

| Profile | Full strict / label | Retrieved strict / label | Full / retrieved label macro F1 |
|---|---:|---:|---:|
| Jev | 76.00% / 78.67% | 73.33% / 75.33% | .769 / .732 |
| Winnow | 66.67% / 66.67% | 76.33% / 76.33% | .523 / .663 |
| Nimble | Unavailable | 64.00% / 64.00% | — / .598 |
| Decider | 32.33% / 58.67% | 41.00% / 61.33% | .574 / .573 |
| Qwen JSON | 51.00% / 51.00% | 55.67% / 55.67% | .437 / .458 |

Each available cell has 300 actions. All 30 labels occur, but support ranges from one to 55 examples; per-action counts and confusion matrices are in the report data. The largest single label represents 18.33%. Macro F1 treats all 30 labels equally, making Jev's stronger coverage of rarer actions visible. A one-example action cannot establish reliable generalization.

Retrieval raises Winnow's action-label score by 9.67 points (paired interval +4.67 to +14.67). Jev's retrieved-minus-full action difference is −3.33 points (−7.67 to +1.00); this does not establish that the full handbook is generally better. In combined strict agreement, retrieval changes Winnow by +1.11 points (−1.44 to +3.67), Jev +2.00 (−0.33 to +4.44), and Decider +7.22 (+4.56 to +9.89).

The fixed top-five retrieval includes the actual annotated procedure at 236/300 action checkpoints (78.67%) and 731/900 routing checkpoints (81.22%). The initial scenario-string diagnostic understated coverage because of FAQ aliases and scenario/dialogue differences; it is superseded by the separate [reporting correction](evidence/abcd-retrieval-correction.json). The original summary is retained. A hit is not proof of sufficient evidence, and a miss does not make every answer impossible. Retrieval used only observed history; upstream step annotations were used only in this subsequent diagnostic (the last observed annotation for terminal checkpoints).

## Context, validity and latency

Actual median full-handbook inputs are roughly 19.5–21.0K native tokens, depending on profile and task. The long state comes mainly from the handbook, not exceptionally long customer conversations. Retrieved inputs are roughly 2.3–2.9K. Each profile's tokenizer/wrapper counts were saved, and every capacity decision was independently checked against its frozen ceiling. No clipping was used.

Nimble's pinned release supports 8,192 input tokens. All 1,200 full-handbook records and 108 longer synthetic variants were explicitly unavailable. Its 1,200 retrieved natural questions and 36 shorter stress variants were valid. Unavailable capacity is not a wrong reasoning answer. Qwen's 32K serving ceiling is a chosen profile below the backbone's larger native configuration; Winnow's profile is 64K and the longest tested input is only 29,128 tokens. No model was validated over its entire advertised context range.

Across all 2,544 records/profile, Jev has 2,507 valid, 36 probability-invalid and one HTTP503; Decider has 2,255 valid and 289 probability-invalid; Winnow and Qwen each have 2,544 valid. Decider's action probability sums frequently violate Arena's 1e-4 tolerance, despite selecting the reference label on many such rows. That tolerance is our frozen contract, not a universal vendor requirement. Within-tolerance vectors may be normalized and flagged. Qwen returns labels without probabilities, so it has no probability-sum requirement. The failed Jev request has unknown input usage and retains a conservative reservation; it was not retried or erased.

| Profile | Full handbook route / action median | Retrieved route / action median |
|---|---:|---:|
| Jev | 358 / 356 ms | 265 / 266 ms |
| Decider | 1,895 / 1,927 ms | 144 / 156 ms |
| Winnow | 2,847 / 2,876 ms | 320 / 336 ms |
| Nimble | Unavailable | 240 / 251 ms |
| Qwen JSON | 1,570 / 1,564 ms | 468 / 456 ms |

These are serial model-request medians for supported attempts, including invalid outputs. Retrieval overhead and complete request pipeline distributions are separately saved. They exclude loading; hosted latency includes network travel. Prefix caching, model precision and runtimes differ. These measurements support neither maximum-throughput comparisons nor controlled architectural speed claims. All four local profiles loaded on the RTX 5090 and passed unload/memory cleanup checks.

## Separate controlled context extension

There are 12 synthetic bases, four literal answer templates, four lengths and three evidence positions. Jev, Winnow, Qwen and Decider all match the constructed answer in all 144 supported variants. Decider passes the strict output contract on 91/144; the other three pass 144/144. Nimble passes 36/36 at the shortest length and is unavailable for the other 108. The nominal 8K state plus wrapper already exceeds Nimble's 8K input ceiling.

This is an easy extraction control with neutral distractors. It shows successful retrieval of an explicit procedure at these tested lengths; it neither separates long-context reasoning quality among the four supported profiles nor establishes Jev superiority. It has 12 bases, not 144 independent tasks, and is never pooled into natural ABCD accuracy.

## Runtime, cost and completed audit

The candidate window was **196.14 minutes (3h16m)**, ending 04:55:42 UTC /05:55:42 UK. This includes loading, warmups and the HTTP503 recovery, and excludes earlier GPU waiting, development preflight and subsequent audit/review/reporting.

ABCD's recorded Jev API cost is **$1.210811196**: $0.004244352 preflight plus $1.206566844 main/warmups. Four main warmup records include two additional development warmups after recovery. Combined with v2, recorded cost is **$1.458954042** and conservative reservation **$1.467018042**, under the unchanged $6 allowance. These are application token ledgers, not invoice reconciliation; hardware, electricity, earlier unrelated development and Codex subscription usage are separate. No credits were bought or resets redeemed by this evaluation.

The frozen blinded audit selects 76 questions (64 natural and 12 synthetic), with 118 unique usable case/answer pairs across profiles. It uses Codex CLI requesting GPT-6 Astra, at most eight answers per batch, no model identity or gold in the input, and no direct judge API. The first attempt stopped on a usage limit before grading any answer; saved measurements remained intact. The resumed audit completed 27 successful batches: 61 correct, 36 incorrect and 21 ambiguous answer judgments. All 33 flags (12 reference-disagreement reviews plus 21 ambiguity reviews) across 21 questions were inspected. No primary gold has changed. Saved usage: 1,539,565 input tokens including 59,136 cached; 15,468 output including 5,344 reasoning. These are not cash or billed-credit measurements. Requested model: GPT-6 Astra; CLI observed model identifier unavailable. See [the full inspection](evidence/ABCD-AUDIT-REVIEW.md). Automated audit and adversarial review do not constitute human semantic validation.

## Practical interpretation

- **Jev:** strong conditional 30-action selection, higher rare-action macro F1, and fast hosted full-handbook requests in this profile. Its tendency to choose action over an observed agent message limits combined agreement.
- **Winnow:** strongest combined result under this balanced next-step mix; retrieval substantially improves its conditional action selection. The 12B Q8 profile is heavier and full-handbook latency is much higher here.
- **Decider:** compact local option with fast retrieved-policy requests, but many probability-contract failures and lower ABCD quality than its v2 rank suggests. Selected-label scores must accompany strict scores.
- **Nimble:** valid and usable with retrieval, but the pinned 8K release cannot accept the full handbook. The experiment does not assess a hypothetical longer-context version.
- **Qwen JSON:** a general generative control rather than a decision-specialized interface; weaker combined/action agreement here, with valid JSON throughout. Passing the easy context control does not close the natural-task gap.

This experiment measures agreement with recorded support steps under supplied policy, not every acceptable next step. The completed audit identified optional farewells, flexible act-versus-speak order, missing action identity, policy gaps, and differences between policy repair and predicting recorded continuation. It does not establish a re-ranked semantic-acceptance winner. It is not published AST, full Cascading Dialogue Success, or live customer-resolution success. There is no human audit or GitHub publication.

Machine evidence: [main summary](evidence/abcd-v1-summary.json), [independent supplement](evidence/abcd-v1-supplement.json). Original frozen v2 results remain [archived](archive/full-v2-final/RESULTS.md).
