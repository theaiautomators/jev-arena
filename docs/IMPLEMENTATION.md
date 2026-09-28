# Implemented evaluation profile

This describes the running v0.1 application. `EVALUATION.md` preserves the broader proposed protocol; this file governs claims about the implementation.

New runs now use Arena v2 fixtures and the [video evaluation scope](VIDEO-EVALUATION-V2.md). Prior v1 measurements remain frozen in their own run directories and snapshots. V2 changes the owned-fixture seeds/IDs and explicitly resolves topic-versus-urgency and required-approval wording; public data and scoring rules are unchanged. Shared templates still limit generalization.

## Cases and references

Full contains 7,671 records: 231 public JevBench cases; 2,000 typed teacher decisions; 1,500 classification examples; 1,000 aligned multilingual examples; 500 fixed-pool SciFact decisions; 1,440 formal policy fixtures; and 1,000 perturbations. Imported datasets use fixed revisions. Public labels are not changed after candidate scoring.

Fresh uses executable policies with proof traces. Entities and IDs differ by split, but policy templates are shared. This is conformance/integration evidence, **not the proposed template-disjoint, human-audited semantic evaluation**. Paraphrases are mechanical. Counterfactuals change the reference but need not change exactly one fact. No human semantic audit is claimed; `publication_ready` stays false.

Public exposure is possible. The selected Nimble release declares BANKING77, AG News and MultiNLI training components and registered JevBench evaluation. Public results must not be described as unseen generalization. Original model cards are linked in the research notes; no exposure declaration does not prove independence.

Smoke uses 36 owned formal fixtures. Demo combines those fixtures with the all 72 original plus the first 12 easy pinned public JevBench cases (no hard cases); it requires those sources. Full refuses to start without every required source pack and expected count. No dummy data is substituted.

## Scores and cohorts

Implemented: accuracy, macro F1 (mean of class F1 terms across namespaced tasks), task confusion data, Brier, NLL, ten-bin ECE, normalized absolute error of the expected score, per-task binary AUROC, paired perturbation diagnostics, descriptive confidence/coverage thresholds, fixed-pool SciFact nDCG/MRR and pack macro accuracy. Teacher agreement/probability distance are separate.

Strict accuracy requires reference-label agreement and Arena output-contract validity, with all supported attempts in the denominator. It is not accuracy conditional on valid answers. Native rounded vectors face a probability requirement that label-only Qwen does not, so read strict and selected-label metrics together. Failing Arena’s tolerance is not evidence of a vendor API-contract breach. Failures count against supported-case accuracy. Hard-limit unsupported cases reduce coverage. No invented probabilities, repaired answers, silent label dropping or truncation. Sum normalization is permitted only within 1e-4 rounding drift, with a 1e-12 floating-point boundary guard and a recorded flag; larger drift is invalid. Native Choice selections are preserved even when rounded probabilities tie. Noul argmax ties use the shared no-before-yes convention. A separately labeled, post-hoc selected-label sensitivity diagnostic ignores output-contract validity on the same supported reference cohort; it never changes the frozen primary score. The uniform control assigns equal probabilities and chooses the first label deterministically; it is not sampled random guessing.

The report exposes an observed hard-limit common cohort and an option-limit cohort frozen before inference. Tokenizer context exclusions are observed during inference, so the common cohort is not claimed as a fully preregistered intersection. Plumb/SemIf support 16 options in this profile; CLM's encoder is limited to 2,048 tokens.

95% cluster bootstrap intervals use 10,000 draws. Related scenario groups and exact duplicated canonical inputs are joined into connected components before resampling; the Full suite has 2,625 resulting clusters. This does not remove shared-template dependence or establish generalization to new templates. Jev/Qwen comparisons are descriptive paired differences. No significance claims or Holm-adjusted hypothesis tests are made. Threshold curves use test data descriptively; calibration-fitted operating points and error-cost recommendations remain future work.

## Runtime profiles

Reference workers are networkless with read-only weight mounts. Evidence records precision, image IDs and adapter/base/head revisions. Laya uses FP32 weights and reference CUDA autocast; its loader can clamp native temperatures. Nimble merges the pinned adapter into its pinned base at load and resolves native temperature by adapter hash. CLM uses native heads with Qwen3 LAST pooling and action/prefix caches disabled. Winnow uses its native CUDA llama.cpp runtime with Q8 weights. Qwen is deterministic JSON-prompted generation with exact validation, not grammar-constrained decoding.

Plumb/Decider use eager reference paths with CUDA graphs disabled. Optional optimized kernels may be absent; runtime warnings are retained. These are manageable local deployment profiles, not each author's peak throughput. Laya CPU fallback is forbidden and model placement is CUDA. ModernBERT runs FP32; its normalization is explicitly labeled transformed NLI. Native typed requests share one host/worker formatter and do not duplicate imported criteria in the instructions. SemIf preserves its author's Choice/Noul option descriptions and true/false ordering; Score uses an explicit Arena categorical extension beyond the author's frozen comparison. Laya rejects native option descriptions over 48 tokens, fully budgets instructions/options/state and checks the exact native sequence length, avoiding its internal truncation paths. Known SemIf/Nimble context-limit exceptions reduce coverage rather than count as reasoning failures.

Full collects three serial blocks over the first 200 frozen JevBench public cases, same-state repeated-question fanout at 1/5/20, and three startup/cleanup cycles. Warmup retains first inference/compilation. Concurrency 4/16 and native batch scaling are not claimed. Thermal-reference reruns, multiple hosted time windows, extended cache profiles and whole-machine energy measurement are not included. Whole-GPU sampled energy includes other GPU users, excludes CPU/display energy and may omit edge intervals.

## Recovery

SQLite plus an OS file lock permits one GPU owner across processes. Predictions persist before progress advances. Cancel reaches loading, inference and judging. Cleanup stops only the exact run-owned container, verifies absence and checks memory against baseline with 512 MiB tolerance. Failed cleanup stops the cascade. Resume keeps predictions and finishes missing stages, while refusing changed inputs/code/images/weights.

Hard process termination cannot execute cleanup. Restart marks unlocked nonterminal runs interrupted. Resume checks each exact worker name plus its Arena ownership label under the GPU lock, stops surviving owned workers and verifies absence. A name collision blocks execution; unrelated containers are never stopped. Downloads and builds are separate from measured inference.

## Judge

Only the ChatGPT-authenticated project-local Codex CLI is used, requesting `gpt-6-astra`. No direct OpenAI/Anthropic judge API or API-key fallback exists. User config/rules, plugins, shell, code execution, browser, apps and computer tools are disabled; tool events reject a batch. It runs read-only in a dedicated evidence directory. This is a CLI sandbox with disabled tools, not a separate OS account or networkless judge container. It keeps access to the user's Codex login for the authorized call.

The tested CLI accepts the requested model but exposes no observed model identifier; that field remains null. Auth/quota problems pause judging without losing candidate results. Calls are sequential: eight items maximum, 180 seconds per attempt, two attempts maximum. Quota-reset credits are never redeemed automatically.

The run request controls the representative audit size (default 60). The v2 video run freezes 250 case IDs, balancing packs then family/primitive/language, and separately adds up to 50 non-control answer disagreements under a gold-independent hash rule. Manifest IDs precede inference; the final selection file distinguishes representative and disagreement cohorts. Distinct answers are blinded; equal answers share a grade. Selected labels with invalid probability vectors can receive a semantic review without changing their strict score. All provisional/audited semantic cases are eligible. Fresh is formal and primarily code-scored. Judge grades never overwrite reference labels or numeric metrics.

Rubric v2 controls contain 60 unambiguous formal answers, injected instructions, 12 blind repeats and eight deliberately ambiguous answers. Passing these small controls does not establish broad semantic judgment quality or a human annotation audit. Actual control results are saved with the run.

## Workflows

Tickets use a supplied routing policy and restricted-account review rule. Warehouse navigation uses a seeded 6×6 world and shortest-path oracle. Demo runs two seeds/task. Full runs twenty seeds/task in two modes: untimed quality and a preregistered 500 ms deadline. A late answer consumes a step with no action. Every trace retains success, reward, violations, steps, request time and deadline misses. No external action occurs. Ticket episode success requires all twelve independent routes correct; the dashboard also reports decision accuracy and unnecessary Review deferrals. Warehouse exposes all four actions without masking invalid moves. Deterministic unchanged states can repeat a blocked move, so violation steps are not independent errors. Obstacles are internal and the outside-edge ten-step route remains available for every seed; this is a toy constraint test, not a broad navigation benchmark.

## External verification

Jev needs a user-provided TypeSafe key. Authenticated requests have succeeded on the development machine; final comparative claims must identify a completed accepted run from the verification record. Human audit, Linux GPU inference and non-5090 hardware remain separate checks. Linux CI validates platform-independent contracts and frontend compilation without weights.

See [reference cautions](REFERENCE-CAUTIONS.md) for the post-hoc routing-ambiguity audit. Frozen primary labels and scores are unchanged.
