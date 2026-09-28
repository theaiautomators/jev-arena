# Video evaluation v2 — frozen scope

Authorized 27 September 2026: one Full run across all 13 registered entrants, a larger blind audit, targeted repeat checks, and independent Astra review. This document specifies the new experiment before its candidate outputs exist. It is not a claim that those measurements have completed.

## Suite and scoring

- 7,671 cases per entrant before hard capability exclusions, retaining the pinned public datasets and teacher/reference separation.
- Formal fixtures use `formal-v2`: new random seeds, entities and IDs; topic explicitly determines routing while availability determines urgency; Reader never requires approval and the binary approval question asks about required approval. The original v1 runs and labels are retained unchanged. These are refreshed formal examples sharing eight policy templates, not an independent human-authored semantic benchmark.
- All 13 pinned profiles, including English/typed/multilingual Laya, generative Qwen, NLI and deterministic first-label controls. No contender is selected based on this run's scores.
- Report strict contract accuracy and selected-label agreement together, each with supported denominators. Show shared-support comparisons, unsupported coverage, English and non-English breakdowns, teacher agreement separately, and descriptive paired cluster intervals. Probability calibration uses only valid probability outputs.
- Keep the existing 1e-4 probability tolerance. Native rounding failures must not be described as reasoning mistakes. No label correction after scoring; disputes remain visible and any exclusion analysis is separately labelled.

## Judge audit

- Freeze 250 case IDs before inference with reproducible stratification by pack, task family, primitive and language. Save the exact IDs in the run manifest.
- Add at most 50 previously unselected cases where non-control entrants choose different labels. Select by a fixed hash order independent of gold, model identity or the eventual ranking. Publish the two audit subsets separately.
- Deduplicate equal case/answer pairs; blind all model names, probabilities and timing. Semantically review labels even if their probability vectors failed the contract; do not change their primary strict score.
- Use GPT-6 Astra through ChatGPT-authenticated Codex CLI, eight answers per call maximum. Requested/observed identity stays distinct. No direct judge API, automatic credit purchase or quota-reset redemption.
- Rubric v2 explicitly flags alternative defensible interpretations as ambiguity. Before the run, check 60 formal controls, 12 blind repeats and eight ambiguity controls. Gates: at least 90% formal agreement, 95% repeat agreement, and 7/8 ambiguity flags with review requested. Record failures rather than choosing a rubric to obtain a desired leaderboard.
- All returned ambiguity/reference disagreements receive an explicit evidence review. Automated review is not described as a human annotation exercise.

## Runtime and follow-up

- One GPU worker at a time, using the shared Arena/Support Lab GPU lock. Do not stop unrelated jobs. Cached weights; existing pinned serving profiles and precisions. Stop on failed cleanup or a dead worker; preserve partial results and explain unsupported inputs.
- Per entrant: 10 warmups, 7,671 static records, three serial 200-request timing blocks, 80 workflow episodes across two tasks and two deadline modes, and three local load/unload cycles. These measure these deployments, not peak optimized serving or production reliability.
- After Full: select Jev and up to three local candidates by shared-reference selected-label agreement with their coverage shown. Break exact ties by entrant ID. Use a fresh hashed 200-case supported reference Choice cohort for exact-repeat and reversed-choice-order checks. Reverse both label lists and native criteria ordering while preserving meanings. Repeats are not new independent test cases. Any timing extension is a separately labelled run.
- Inspect surprising failures with native input/output evidence, especially CLM and systematic workflow deferral. Do not claim universal model failure from a profile without native parity evidence.
- Preflight recovery before any Full predictions: CLM's native-path checks selected identical labels on 36/36 development probes, but BF16 confidence values varied both across paths and across repeated Arena launches (up to 0.01980 between Arena launches). Matching prefix-cache and token-batch settings did not establish numerical parity. The v2 CLM serving profile now enables vLLM's batch-invariant mode on both paths, with prefix caching disabled. The same 1e-4 parity gate still applies; failures remain archived. This is an explicit configuration change from v1, and its speed represents this deterministic deployment rather than peak CLM serving performance.
- Independently rebuild score totals, check trace completeness and exports, update the video evidence and script, then obtain the requested adversarial Astra review.

Jev spending cap remains $5 for the main run. Judge quota/time is separate; no automatic paid purchase is authorized. The anticipated 4–6 hours excludes waiting for the GPU or recovery from a newly discovered runtime fault.
