# Evidence behind the revised video

Analysis date: 28 September 2026. Main run: `20260927-205440-6350b9`. The analysis reads frozen cases and predictions; it makes no inference calls and changes no original scores. All thirteen profiles' reference/shared selected-label and strict counts reconcile with the saved `results.json`.

Reproduce with `python -m scripts.analyze_video_findings`. Outputs: [task slices](evidence/video-task-analysis.json) and [additional findings](evidence/video-findings.json). Original evidence: [Arena results](RESULTS.md), [ABCD results](ABCD-RESULTS.md), [model guide](evidence/model-guide.json).

## Editorial spine

Keep the user's sequence: intro → models and how they work → a few visible questions → brief headline → what we learned → practical shortlist. The headline creates the question; the five lessons answer it. Each lesson should show an observation, a case or comparison that explains it, and a consequence for a builder.

The script says **13 setups**, because this roster contains related checkpoints, a general JSON model, a classifier and a deterministic control. There are 7,671 planned cases per profile, not 7,671 successfully answered questions. The opening claim that Jev's popularity is “skyrocketing” is not established by this experiment.

## 1. Task fit: the aggregate conceals different strengths

| Slice | Observation on the same supported questions | Consequence |
|---|---|---|
| News, 500 cases | English Laya 461/500 (92.2%); Jev 441/500 (88.2%); Decider 450/500 (90.0%) | Test a small classifier for a narrow job before choosing by overall rank. |
| News paired outcomes | Both correct 427; Laya only 34; Jev only 14; both wrong 25 | Neither model's correct-answer set contains the other's. Their errors differ. |
| XNLI, 500 cases | Decider 420/500 (84%); Jev 407/500 (81.4%); both correct 370, Decider only 50, Jev only 37, both wrong 43 | A multilingual product needs task/language testing; these translated rows are correlated. |
| Shared public JevBench, 195 cases | Plumb 180/195 (92.31%); Jev 176/195 (90.26%) | A lower overall entrant can still perform well on a particular slice. This is a small public subset. |

These are selected-label matches to saved references. Slice selection is post-hoc; these differences do not establish deployment superiority or independent statistical significance. Public training exposure is unknown. In particular, the news references need scrutiny (lesson 4).

### New: sensitivity to the task mix

The shared score contains 2,440 generated policy/variation questions out of 4,635: **52.64%**, from eight recurring templates. Removing those two packs yields this descriptive comparison:

| Profile | Remaining selected-label matches | Accuracy |
|---|---:|---:|
| Decider | 1,976 / 2,195 | 90.02% |
| Jev | 1,974 / 2,195 | 89.93% |
| Winnow | 1,945 / 2,195 | 88.61% |
| Nimble | 1,923 / 2,195 | 87.61% |

Decider and Jev differ by two labels here. The useful conclusion is that weighting changes the ranking; this is not a replacement primary benchmark or a claim that the remaining mix is the correct mix. Invalid probability outputs still count as selected-label matches when the selected label matches.

### New: relevance accuracy conceals what gets retrieved

SciFact has 453 “no” and 47 “yes” references. The control always selects the first option, “no.” Its apparent 90.6% accuracy finds **zero** relevant documents.

| Profile | Overall label accuracy | Relevant found / 47 (recall) | False positives | Precision among “yes” answers |
|---|---:|---:|---:|---:|
| Jev | 93.6% | 40 (85.1%) | 25 | 61.5% |
| Winnow | 92.6% | 38 (80.9%) | 28 | 57.6% |
| Decider | 92.4% | 35 (74.5%) | 26 | 57.4% |
| Laya | 52.0% | 40 (85.1%) | 233 | 14.7% |
| First-option control | 90.6% | 0 (0%) | 0 | Undefined: no positive predictions |

Laya and Jev find the same number of relevant documents, but Laya admits far more irrelevant ones. This also shows why recall alone is insufficient. These are binary relevance decisions on a selected sample, not end-to-end search quality; query ranking metrics in the original report answer a different question.

## 2. Capacity: name the model and the failure

| Profile / interface tested | Choice capacity | What happens on BANKING77 |
|---|---:|---|
| Plumb 4B | 16 | 500 unsupported cases; no easier shortlist supplied. |
| SemIf on Qwen3.5-4B | 16 in this interface | 500 unsupported cases; not a universal SemIf limit. |
| Winnow 12B native server | 64 | 500 HTTP 400 failures because Arena initially declared 255. Preserved as historical failures, explained as a capacity-discovery bug. |

BANKING77 has 77 options per question. MASSIVE's 60-option task also exceeds Plumb/SemIf's 16-option interfaces, but fits Winnow's native 64. Those two 500-case groups plus 36 further unsupported public cases account for the 1,036 reference questions outside the 4,635 shared cohort. See the [Winnow incident](evidence/winnow-option-limit.md).

Nimble's pinned 8K release could not accept the full ABCD handbook. Jev used a 32K state/question limit; the later ABCD settings used Decider 32K, Qwen 32K including output budget, and Winnow 64K. No claim that Jev alone handles long input, or that each model was tested at its full ceiling.

Builder consequence: reducing labels or retrieving policy can make a request feasible, but creates a pipeline with its own errors. We did not test a hierarchical BANKING77 classifier.

## 3. Input strategy changes speed and quality

| Profile | Short-input block median* | Full-handbook routing median | Retrieved-policy routing median |
|---|---:|---:|---:|
| Jev | 244.70 ms | 358 ms | 265 ms |
| Winnow | 55.97 ms | 2,847 ms | 320 ms |
| Decider | 47.45 ms | 1,895 ms | 144 ms |
| Nimble | 49.68 ms | Unsupported | 240 ms |
| Qwen JSON | 316.90 ms | 1,570 ms | 468 ms |

*Median of the three saved block medians. Short timing uses repeated JevBench inputs; the other columns are a separate ABCD task. These illustrate workload dependence rather than a controlled causal comparison. Hosted network time is included; local hardware was an RTX 5090. All measurements are serial. Retrieval overhead is not included in the model-request medians above. Do not equate these with maximum throughput or complete application latency.

Winnow conditional action labels improve from 200/300 to 229/300 with retrieval: +9.67 points, saved paired interval +4.67 to +14.67. Jev changes from 236/300 to 226/300: -3.33 points, interval -7.67 to +1.00. This does not establish that full policy is generally better for Jev. Retrieval included the annotated procedure at 236/300 action checkpoints; that diagnostic does not prove each hit sufficient or each miss fatal.

## 4. A reference match, usable output and a sensible decision differ

Decider's original 5,671-reference cohort has 5,235 selected-label matches (92.31%) and 4,752 correct-plus-usable outputs (83.79%). The 483-answer gap is not 483 extra reasoning mistakes. Arena's fixed probability-sum tolerance is 1e-4; the scope is this contract, not a universal vendor requirement. Keep failures visible instead of silently normalizing arbitrary distributions.

### New inspection: public references can reward a questionable category

Case `classification-ag news-450` describes a US Olympic basketball match. The frozen AG News reference is **World**; Laya selects World; Jev selects **Sports**. I would question the reference for a news-topic product. Two additional examples are `classification-ag news-614` (Olympic hockey) and `classification-ag news-1617` (NFL), also World references and Sports predictions from Jev.

The text and numeric label were checked against rows 450, 614 and 1617 of the locally pinned AG News test parquet; label 0 maps to World. This is not an importer off-by-one finding. Source revision: `eb185aade064a813bc0b7f42de02595523103ca4`, [dataset](https://huggingface.co/datasets/fancyzhx/ag_news). Raw article text remains local.

These examples were selected after inspecting model disagreements. They do not estimate the prevalence of bad labels, establish a corrected ranking, or prove that Laya memorized the benchmark. Do not erase Laya's measured lead, and do not describe every Jev mismatch as a semantic mistake. A broader blinded review would be required to estimate semantic quality. Original references and scores remain frozen.

## 5. Tool selection and workflow control are different jobs

| Full-handbook ABCD decision | Jev | Winnow |
|---|---:|---:|
| Conditional action label, told an action is due | 236/300 (78.67%) | 200/300 (66.67%) |
| Combined route plus action on action checkpoints | 221/300 | 141/300 |
| Correct route on agent-message checkpoints | 69/300 | 185/300 |
| Combined task, including synthesized endings | 574/900 (63.78%) | 616/900 (68.44%) |

The ranking reversal has an identifiable mechanism: Winnow's 116 additional message-checkpoint matches outweigh Jev's 80 additional action-checkpoint matches, with a further six-ending difference. This is a balanced recorded-step evaluation, not natural production prevalence or customer-resolution success. The audit found flexible sequencing and optional farewells; the primary reference labels were not changed.

In the separate toy warehouse workflow, untimed completion was Jev 20/20, Winnow 19/20, Nimble 17/20 and Decider 9/20. All four completed all 20 ticket scenarios. Plumb, Qwen and the Laya profiles sent every untimed ticket to Review, avoiding some violations while deferring useful work. Tiny workflow counts are illustrations of failure mechanisms, not production estimates.

## Showing questions without making the video hard to follow

Use **Case explorer → Jump to question type**, then one exact ID. Keep all responses hidden while presenting the input and allowed answers. Reveal the reference, then the responses. Select one model to inspect an error; choose All model responses for a disagreement. Probabilities and audit details are collapsed until needed.

| Shot | Exact navigation / case | What the viewer should notice |
|---|---|---|
| Simple policy | Arena Fresh / Workflow permissions; `fresh-v2-test-01-000-choice` | Ineligible takes precedence over signed approval; three visible choices. |
| Familiar classification | Classification / SST-2 or AG News | Same input/choices for every model. |
| Capacity | Classification / BANKING77 | All 77 choices; unavailable versus failed request. |
| Reference concern | Classification / AG News; `classification-ag news-450` | Saved reference World, Jev Sports, Laya World. |
| Model-specific errors | Select a model, then Selected answer differs | A concrete failure under the saved key; inspect before judging meaning. |

Results now has task and model selectors, explicit common-support versus individual-support denominators, selected-label versus strict scores, failure counts, and links into the corresponding cases. AI-teacher slices are labelled agreement. The same controls work for the selected local run; fixed editorial findings refer specifically to v2/ABCD.

## Roster to show on screen

| Entry | Tested approach | Base / scale |
|---|---|---|
| Jev 1.13 | Hosted decision service | Undisclosed |
| Winnow | Decision fine-tune, Q8_0 | Gemma 4 12B |
| Decider v2 | Decision fine-tune, BF16 | Qwen3.5-4B-Base |
| Plumb | Decision fine-tune, BF16 | JevK5 on Qwen3.5-4B |
| Nimble | Decision adapter/backbone, BF16 | Qwen3.5-9B |
| CLM | Learned contrastive heads | Frozen Qwen3-8B backbone |
| SemIf | Direct option scoring, no new decision fine-tune | Qwen3.5-4B |
| Laya English | Decision encoder | ModernBERT-large + head, 421M |
| Laya typed | Related task-specific checkpoint | ModernBERT-large + head, 421M |
| Laya multilingual | Related multilingual checkpoint | mmBERT + head, 322M |
| Qwen JSON | Generative classification control | Qwen3.5-4B |
| ModernBERT NLI | Entailment classification control | 395M |
| Uniform baseline | Deterministic first-option selection | No model |

Architecture details come from the pinned model guide and the official model cards linked in the script. Current upstream releases may differ from the saved configurations; model-card performance claims are not Arena measurements.
