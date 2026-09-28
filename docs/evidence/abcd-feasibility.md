# ABCD feasibility and the current context-length gap

Research date: 2026-09-27. The user subsequently authorized this assessment after completion of the current evaluation and review; see `docs/ABCD-ASSESSMENT-QUEUE.md`. No ABCD inference or training has been launched, and the frozen v2 evaluation is unchanged. Fine-tuning remains outside this assessment.

ABCD is a worthwhile separate customer-support next-action track and a useful basis for a later fine-tuning demonstration. Its conversations alone are short. Its complete company handbook makes a materially longer input and supports a useful full-handbook versus retrieved-policy comparison. Neither a large accepted context window nor this dataset alone establishes superior long-context decision quality.

## Measurements

Current run: `20260927-205440-6350b9`. All 7,671 saved Jev predictions were inspected read-only. API-reported input tokens have median **423**, p95 **1,756**, maximum **4,297**; only **37** exceed 2,048 and **none** exceed 8,192. These include the request content rather than measuring state alone. This suite cannot support claims about accuracy near Jev's context limit. The separate workflow episodes add sequential tests but do not close that length gap.

ABCD was downloaded from the [official repository](https://github.com/asappresearch/abcd), pinned at commit `6b8700ce67c6b37b062dd7a60abc76d7ef832a97`. The downloaded v1.1 release has 8,034 training, 1,004 development and 1,004 test conversations. Local profiles are in `.arena/research/abcd/profile.json` and `current-suite-context.json`.

| Measured test-set content | Median | 95th percentile | Maximum |
| --- | ---: | ---: | ---: |
| Full original conversation, turns | 21 | 35 | 56 |
| Full original conversation, whitespace words | 187 | 316 | 481 |
| Past delexicalized history before a labelled action, whitespace words | 92 | 216 | 420 |

There are 3,608 labelled action checkpoints in the test split and 30 distinct action labels. Word counts include speaker labels and are **not tokenizer counts**. Percentiles use the sorted value at floor((n-1)*0.95). History excludes the current target turn and all later turns. These are descriptive measurements; an evaluation importer still needs to verify alignment against upstream task preparation.

A readable rendering of all guideline flow/subflow names, descriptions, instructions, action buttons, text and subtext is **72,885 characters / 12,767 whitespace words**. It is saved privately as `guidelines-readable.txt`. This rendering omits JSON punctuation, includes repeated instructions present in the source, and has not yet been measured with each entrant's tokenizer. Do not present a word-to-token estimate as an observed count.

## Proposed additional experiment

1. Freeze approximately 300 held-out conversations, with action and non-action checkpoints selected before examining candidate answers. Preserve the original train/dev/test separation at conversation level. Report uncertainty clustered by conversation; checkpoints within a conversation are not independent samples.
2. Test whether to act, speak, or finish, then which action to take. Report the action selector conditional on a true action checkpoint separately from the combined routing result. A next-action-label adaptation does not reproduce the full published Action State Tracking task, which also includes action arguments, or establish live customer-resolution success. See the [original paper](https://arxiv.org/abs/2104.00783).
3. Compare the same checkpoints with the complete handbook versus policy retrieved from the observed history. Retrieval must not use the gold intent, action, or latent scenario; report retrieval misses and total pipeline latency/cost. Use gold policy selection only as an explicitly labelled oracle diagnostic.
4. Add a separately labelled synthetic context-stress extension, if needed: fixed decisions with relevant evidence at the beginning, middle and end and controlled distractor volume around 4k, 8k, 16k and the usable upper limit. Preserve the answer, validate policy consistency, and count each model's actual input tokens. Do not describe padded variants as natural ABCD conversations or as independent extra test examples.
5. Compare Jev, selected local contenders and a generative baseline under a declared selection rule. Verify native model limits and feasible RTX 5090 serving profiles first. Current Arena profile settings (CLM 2,048, most local entrants 8,192) are not evidence that their underlying architectures cannot support more. Report capacity/coverage separately from accuracy; no silent truncation. Entrants limited to 16 labels cannot directly handle the 30-action task. A shortlist/router must be label-blind, measured as a separate pipeline, and available on comparable terms.
6. Use supplied action labels as the primary reference and Codex CLI Astra to audit ambiguous cases. Show accuracy, macro action performance, coverage, latency and cost across input conditions. Do not automatically replace gold with a judge opinion. Keep new results separate from the frozen v2 leaderboard.

Exclude hidden `scenario.flow`/`subflow`, target annotations, current target action, future turns, and private scenario facts not available to the agent. Prior observed action outcomes belong in the history. Public benchmark contamination cannot be ruled out; company-policy variants would be a separate useful generalization test.

[TypeSafe's current model documentation](https://docs.typesafe.ai/models) specifies 64k tokens per request but only 32k for state plus the longest question. Its [limitations page](https://docs.typesafe.ai/model-jaggedness/jev-1.13) explicitly warns that irrelevant long-state content reduces accuracy and recommends filtering. Full-handbook versus retrieval therefore tests a practical trade-off rather than assuming Jev wins. Multiple questions sharing one state could be a separate efficiency experiment.

For the fine-tuning video, train an appropriate open-weight model on the training split, tune on development only, then evaluate the frozen test split. Compare the same model before and after training, with Jev as an external reference: TypeSafe currently says Jev is not customer fine-tuned or LoRA-adapted. Clearly separate fine-tuned and zero-shot results.
