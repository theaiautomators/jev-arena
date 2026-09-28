# ABCD v1 assessment protocol

Prepared before any ABCD test predictions, 28 September 2026. Final machine freeze occurs only after development capacity preflight passes. This is a separate assessment; [Arena Full v2](RESULTS.md) is complete and remains unchanged. No fine-tuning is included.

## Questions and selected profiles

Can these pinned profiles select the next recorded support step and the correct tool action with the complete public handbook, compared with policy retrieved from observed history? A separate synthetic extension tests retrieval of an explicit active procedure as unrelated context grows; it is not natural support dialogue.

Selection rule, declared before ABCD predictions: hosted Jev; the top three eligible local decision profiles from v2 by all-entrant shared selected-label agreement (excluding statistical/NLI/generative controls; ties by model ID); and the same Qwen JSON generative baseline. This selects **Jev, Winnow, Decider, Nimble and Qwen**. It selects deployment profiles using a prior different benchmark, not ABCD outcomes.

| Profile | ABCD serving ceiling | Evidence and interpretation |
|---|---:|---|
| Jev1.13 |32,000 state plus longest question;64K total API request | TypeSafe documented service limit. API usage tokens are recorded. |
| Winnow12B Q8 |65,536 positions,1 decision branch | Pinned author's native64K demonstration; own5090 preflight must pass. Native64-choice limit accommodates30 actions. |
| Decider4B v2 |32,768 full-prompt ceiling in this profile | Pinned decision release documents32K; its base positional configuration is larger. Exact native IDs checked before inference, no truncation. |
| Nimble9B |8,192 full-prompt tokens | Pinned September24 release explicitly documents8,192, despite Qwen backbone262,144 positional configuration. Capacity gaps are unsupported, not wrong answers. |
| Qwen3.5 4B JSON |32,768 prompt plus128 output budget | Base configuration supports262,144;32K is a chosen feasible comparison profile, not its architectural limit. Greedy, thinking disabled, no grammar constraints. |

Pinned cards/configurations are saved with source hashes. [Winnow card](https://huggingface.co/EldanRing/Winnow-12B/blob/b6ac22b0d51b69b18200acacb3fbdd98073fffe8/README.md), [Decider card](https://huggingface.co/Mapika/decider-4b/blob/49564ddcfccafb6db563eb757c1d41e6c78dcb56/README.md), [Nimble card](https://huggingface.co/bespokelabs/Bespoke-Nimble-9B/blob/bd792f44ec8e265be861bfcdf4e05967ffe0e858/README.md), [Jev documentation](https://docs.typesafe.ai/models). A supported context size does not guarantee quality at that size.

## Dataset, alignment and selection

Official ABCDv1.1 at commit `6b8700ce67c6b37b062dd7a60abc76d7ef832a97`:8,034 train /1,004 dev /1,004 test conversations. Source files and upstream preparation code are pinned and hashed. Dataset download remains private to the workspace. [Upstream repository](https://github.com/asappresearch/abcd).

Select300 test conversations by SHA256 order using seed15090 and conversation ID, after requiring action/nonempty-message checkpoints and excluding exact complete-history duplicates across splits. No predictions inform selection. Pick one action checkpoint, one noninitial agent-message checkpoint, and the synthetic terminal checkpoint per conversation, by a fixed hash rule. This balances next-step classes; it does not estimate their natural deployment prevalence. All30 action labels happen to occur in the selected action checkpoints, with unequal counts from1 to55. Report every label's support.

For each checkpoint, score the three-way route (`take_action`, `retrieve_utterance`, `end_conversation`). At true action checkpoints also score conditional action selection among **all30** public ontology labels. The conditional question openly states that an action is due. The combined route/action result only succeeds on action checkpoints if both route and action are correct. The route-only, conditional-action and combined measures have distinct denominators.

Each condition therefore contains900 route decisions and300 conditional action decisions. Full handbook plus retrieved policy gives2,400 natural cases/profile. Five profiles produce12,000 natural prediction records. Unsupported attempts still have explicit records. This is an action-label/next-step adaptation, not published AST with slots/values, utterance ranking, full Cascading Dialogue Success, or live customer-resolution success.

Alignment is tested against the pinned `CDSProcessor.build_features` boundary loop on all300 selected conversations: target agent/action turn is scored **before** appending its text; end is synthesized after the complete observed dialogue. Inputs contain only preceding delexicalized speaker/text, including prior action outcomes. Hidden scenario facts, latent intent, current action outcome/target, future turns, utterance candidate sets and target annotations are excluded. Scenario intent is retained only in private analysis metadata to evaluate retrieval coverage. Mutation tests prove it cannot change the candidate payload.

## Handbook and retrieval

The full condition includes all55 public guideline sections, their original policy wording, and each section's public KB action catalog. The catalog is not an instruction to ignore handbook conditions. A fixed button-alias legend resolves names such as Notify Internal Team/notify-team and Membership Privileges/membership. This avoids imposing an undocumented vocabulary mismatch on competitors; it is identical for all profiles and conditions. Original handbook/KB inconsistencies remain inspectable, not relabelled automatically.

The retrieved condition uses exactly the same conversation history and selects the top5 sections with fixed BM25 (`k1=1.2`, `b=.75`, declared stopword set and lexical tokenization). It uses no gold action, target intent, scenario or future text. Ties use section ID. The returned sections and rendered input are frozen; runner recomputes retrieval and asserts equality while recording retrieval and full pipeline latency. Initialization time is separate. All30 action options remain present regardless of retrieved sections. No target-informed shortlist or oracle policy is supplied to candidates.

Report whether the held-out conversation's source procedure is retrieved, plus accuracy conditional on retrieval hit/miss. These are post-execution diagnostics using hidden metadata, not candidate features. A missed source procedure need not make every simple next action impossible, and a hit is not proof of sufficient evidence.

## Controlled context stress

Twelve synthetic base probes, four fixed active-action labels, thirty allowed actions. An explicit active procedure and a corresponding customer request determine the answer by construction. Neutral inventory records supply unrelated text. Four lengths target approximately4,096 /8,192 /16,384 /28,672 **state tokens under the pinned Qwen tokenizer**, with relevant procedure at early/middle/late positions:144 variants/profile,720 prediction records total.

Measure each profile's actual native request tokens separately; the same text tokenizes differently and wrappers/options add tokens. These are context retrieval controls, not hard reasoning, natural long ABCD conversations, or144 independent policies. Report changes per base probe/length/position and native support; do not pool them into natural next-action accuracy.

## Development, freezing and execution

Six development conversations and two synthetic development bases are disjoint from test. Seven declared capacity probes/profile cover retrieved action, full-handbook action/route, and all four stress lengths. Check real token counts, no silent truncation, GPU residency, runtime errors and cleanup. Accuracy on these probes is diagnostic, not a model-selection/tuning gate. If a profile fails to load, run out of memory or reject an in-capacity input, diagnose before test predictions; do not silently substitute a different model. Save attempted configurations.

After preflight and importer checks, freeze: selected IDs; exact cases, candidates and prompts; labels; retrieval; model revisions/context/precision; image IDs; inference/source hashes; audit IDs; spending reservation; and this protocol hash. A resume must match the freeze, skip every already saved prediction and preserve failed attempts. Different inference configuration requires a separately identified experiment.

Global shared GPU lease remains in place. The whole preflight waits for Support Lab; do not stop it or overlap local GPU benchmarks. Local models run sequentially, with development warmups and verified unload/cleanup. Native prefix caches may operate, notably for a shared handbook; one request is in flight. Record actual configured serving latency and cache caveats, not a universal speed or peak-throughput claim. No host idle/thermal control is claimed.

## Scoring, audit and verification

Report planned counts, supported counts, unavailable capacity, transport/format failures, strict valid-label accuracy, and selected-label accuracy with explicit denominators. Within-tolerance probabilities may be normalized and flagged; keep the existing1e-4 contract. Also show correct-label yield over all planned cases without calling unsupported cases reasoning errors. For each condition/task, compare identical shared support where it exists; if no all-profile shared full-handbook cohort exists, say so. Paired comparisons may then use explicitly named supported-profile subsets.

Show per-action support, recall and macroF1 over the30-label task; route confusion; combined pipeline outcomes; retrieval misses; native token distributions; latency, VRAM, load/cleanup and cost. Confidence intervals cluster by conversation (or synthetic base for the controlled track), with related conditions paired. Bootstrap intervals are descriptive and unadjusted for multiple comparisons. No claim of equivalence from an interval crossing zero.

Freeze **64 natural audit case IDs** (16 per task×condition stratum) and **12 synthetic IDs** (one per length×position), hash-selected independently of predictions. Deduplicate identical case/selected-answer pairs, blind model names/probabilities/timing/reference gold, and use at most8 reviews per Codex CLI call. Request GPT-6 Astra through the existing ChatGPT login only. The existing rubric-v2 controls passed in v2; they are not human validation. Judge flags never change primary gold. Inspect every reference disagreement/ambiguity, especially act-versus-speak timing where recorded human choices may not be unique. Audit fractions do not estimate suite prevalence. Preserve observed/requested model identity separately. No direct judge API, purchases or reset redemption.

Independently rebuild record counts, hashes, scoring, retrieval and token/capacity outcomes. Export a separate branded dashboard and sanitized evidence. Obtain the explicitly requested Astra adversarial subagent review of the new conclusions, address substantive findings and update the video without changing v2 measurements. No GitHub publication yet.

## Spending

Preserve the original combined6USD authorization across v2 main/follow-ups and ABCD. V2 currently reserves0.253518846USD (actual0.248142846); ABCD development and test ledgers consume the remaining allowance, not a reset. Before each hosted request sum every ABCD ledger plus the two v2 ledgers; conservatively reserve up to64K input tokens before sending, then reconcile reported usage. Never buy credits or redeem a Codex reset. Codex subscription/credit usage is separate from the Jev API ledger and must be reported from actual saved audit metadata where available.
