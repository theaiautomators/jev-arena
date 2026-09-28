# Adversarial review — current verdict

Reviewed 27 September 2026. This is an independent source, saved-evidence and script audit. No new candidate inference, hosted model call, CLI judging, credential access or publication was performed by the reviewer.

**CURRENT VERDICT: the corrected Demo and terminal-complete Full measurements are accepted for the bounded claims below. The Full judge audit completed with disagreements and ambiguity flags; completion is accepted, not blanket semantic agreement.** The reported numbers are internally consistent with the stored predictions and traces. No unresolved demonstrated adapter defect invalidates these measured profiles. This does not establish numerical parity with every unmodified native runtime, human-audited semantic truth, peak serving speed or a universal winner.

The final spoken script's numerical and practical conclusions are supported. The two requested wording corrections are now applied: it describes the actual service-unavailability flag and says Jev **succeeded in** 40/40 untimed episodes and 39/40 deadline episodes, distinguishing task success from completion of execution. Its recommendation to investigate Decider/Winnow/Nimble further, rather than declare them equal or superior to Jev, is proportional to the Demo evidence.

**Final release checks accepted within scope:** the parent supplied a clean **37/37 test pass** using a scoped writable temporary directory and a successful production build. This supersedes the earlier sandbox-only setup failures. Final CPU Smoke `20260927-154819-1905f2` independently has 36 valid outputs and complete cached/terminal status; its implemented-profile hash matches the snapshotted `docs/IMPLEMENTATION.md`, and its snapshot includes methodology, reference cautions and licenses. The reporting-only corrections are exercised without rerunning or changing the accepted model predictions.

The reviewer independently inspected `.arena/reports/demo-report.zip` and `full-report.zip`: both carry terminal-complete run/result states, the correct 13/3 entrants, recorded RTX 5090 and Codex CLI 0.157.1 provenance. Their nested source-snapshot bytes exactly match the original accepted runs. `METHOD-NOTES.md` explicitly identifies report-time explanations rather than pretending they were frozen before inference. The parent verified regenerated primary counts, accuracy and intervals unchanged, with other numerical differences bounded by 1e-12 from summation order.

The supplied final browser evidence records standalone Full-report loading from an independent static server with no Arena API calls or app errors; mobile 390×844 has 375px body width and the visible 3,147/5,671 Laya score, with the 7,671 coverage denominator distinguished. The release-privacy report independently read by the reviewer records **169 checked items and zero findings**, covering staged source, HTML/ZIP exports and nested snapshots. These checks support the portable reporting release; they do not turn the benchmark into a human semantic audit. The clean-clone recheck is separate and was not required to close this bounded review. No publication is implied or authorized by this acceptance.

## Accepted evidence and scope

- **Corrected thirteen-entry Demo:** `20260927-142204-8262c6`. Independently checked saved cases, predictions, judge jobs, load/runtime logs, cleanup records, episodes and exported report. All 1,560 unique prediction keys, 52 untimed episodes and 161 answer reviews are present. The export `.arena/verification/demo-report.zip` independently reports both run and result status as `complete`.
- **Terminal-complete Full:** `20260927-144758-15b0d8`. Independently read the frozen cases and SQLite in read-only mode, plus saved timing blocks, episode traces and Laya's three cleanup records. All **23,013 static records**, nine 200-request timing blocks and **240 episodes** are present. The final saved `run.json` independently reports `complete`, with 117 completed judge jobs over 60 case IDs. Candidate scores remain independent of those judgments.
- Original development runs, including `20260927-133444-c484c3` and preliminary cancelled Full runs, are superseded and must not supply final headline numbers.

Both accepted runs identify their input hashes, source snapshots, model revisions and worker image identities. All-roster Full evaluation has **not** occurred. Only Jev, English Laya and the first-label control ran Full. Demo and Full cannot be combined into one universal leaderboard.

## Full results independently recomputed

Each entrant attempted all 7,671 records, with **zero unsupported cases**. The main denominator is **5,671 reference cases** after excluding 2,000 teacher cases. A strict success requires both a matching reference label and Arena's fixed output contract. “Valid-answer accuracy” would be an ambiguous label because it might suggest a denominator containing only valid outputs; “Strict accuracy: correct label + Arena output contract” is clearer.

| Entrant | Strict correct / 5,671 | Strict accuracy | Selected-label correct / 5,671 | Selected-label accuracy | All-quality median |
|---|---:|---:|---:|---:|---:|
| Jev | 5,156 | 90.92% | 5,192 | 91.55% | 264.0 ms |
| English Laya | 3,147 | 55.49% | 3,240 | 57.13% | 18.4 ms |
| Uniform probabilities / first label | 2,088 | 36.82% | 2,088 | 36.82% | 0.0037 ms |

Selected-label accuracy is an explicitly **post-hoc diagnostic**, not a replacement main score. The control's latency measures arithmetic and dispatch, not neural inference; it should not set a neural-speed comparison scale.

All 83 Jev invalid outputs and all 675 Laya invalid outputs fail the chosen probability-sum rule. There are **no static transport-error or timeout records**. Jev's invalid count includes nine teacher cases, so its main-reference probability metrics have 5,597 valid inputs. Laya's 675 invalids are all main-reference cases, leaving 4,996 valid inputs. These denominators matter when comparing Brier/NLL/ECE.

A native vector totaling approximately 0.99 fails Arena's 1e-4 tolerance; it does not by itself establish a reasoning failure or breach of a documented vendor guarantee. Rounding drift accumulates with label count. Label-only Qwen in Demo does not face this additional probability requirement. Strict accuracy is therefore a deployment-contract comparison, not semantic accuracy alone. The large Full Jev/Laya difference remains under selected-label scoring, so rounding failures do not account for the overall conclusion. The paired cluster bootstrap was independently recomputed on the frozen cases: Laya-minus-Jev is −35.43 percentage points, with descriptive 95% interval −39.35 to −31.23, matching `docs/RESULTS.md`.

### Per-pack check and language objection

Counts below are strict correct, with selected-label correct in parentheses where different.

| Pack | Cases | Jev | English Laya | First-label control |
|---|---:|---:|---:|---:|
| Public JevBench | 231 | 202 | 125 (128) | 70 |
| Classification | 1,500 | 1,318 (1,331) | 1,022 (1,089) | 382 |
| Multilingual | 1,000 | 794 (817) | 332 (353) | 180 |
| SciFact fixed-pool relevance | 500 | 469 | 260 | 453 |
| Formal policy fixtures | 1,440 | 1,403 | 823 (825) | 577 |
| Perturbations | 1,000 | 970 | 585 | 426 |
| Teacher decisions, excluded from main accuracy | 2,000 | 1,458 (1,465) | 722 | 553 |

The multilingual objection is legitimate: this Full entrant is **English Laya**, not the multilingual checkpoint. Within the 200 aligned records per language, strict Jev/Laya counts are English 174/102, Spanish 166/80, German 157/68, Hindi 155/37 and Arabic 142/45. Do not generalize this to the multilingual Laya model, which ran only Demo.

The comparison is not explained solely by non-English cases. An explicitly exploratory English-only screen retains 4,871 main references: Jev 4,536 strict / 4,552 selected-label, versus Laya 2,917 / 2,997. More simply, the script's English formal-fixture comparison is correct: 1,403/1,440 (97.43%) versus 823/1,440 (57.15%). Those are shared-template conformance fixtures, not broad reasoning intelligence.

SciFact deserves special caution: the first-label “no” control already gets **453/500 (90.6%)**, versus Jev's 469/500 (93.8%). High raw accuracy on that imbalanced pack is not strong evidence of useful relevance ranking by itself. Use the fixed-pool ranking diagnostics and pool recall if discussing retrieval quality. Unjudged documents follow the declared BEIR nonrelevant convention; they were not independently human-audited.

## Routing-wording sensitivity

The policy generator intends routing to depend solely on `topic`. However, a payment/onboarding topic can coexist with `service unavailable=yes`, and the policy sends “outage” to Engineering without explicitly resolving precedence. A reader can reasonably interpret an unavailable service as an outage. The executable oracle's intention is not sufficient to dismiss that interpretation.

The frozen subset `.arena/verification/ambiguous-routing-cases.json` identifies **50 potentially affected Full Choice records**: 19 formal and 31 perturbations, representing 31 distinct state strings. Selection used case text/metadata, not Full predictions. It was nevertheless discovered after inspecting Demo and is therefore **post-hoc**. No labels or primary scores changed.

| Entrant | Strict after exclusion / 5,621 | Selected-label after exclusion / 5,621 |
|---|---:|---:|
| Jev | 5,152 (91.66%) | 5,188 (92.30%) |
| English Laya | 3,108 (55.29%) | 3,201 (56.95%) |
| First-label control | 2,054 (36.54%) | 2,054 (36.54%) |

This sensitivity does not remove the Full gap. In Demo it is consequential for the tiny lead: removing the two related questions leaves Jev and Winnow tied at **115/118**. Therefore neither the original two-answer lead nor the ambiguity-adjusted tie supports superiority/equivalence.

My early suggestion to present Jev's 0.97-confidence Engineering answer as a clean reasoning error is **withdrawn**. It can illustrate benchmark ambiguity instead. The subsequent Full judge review also exposed a second wording issue in the tool-selection Noul template, described below. The earlier bounded source reread was not a comprehensive human semantic audit. Future versions should explicitly say routing depends only on the topic field and service availability affects urgency only, using newly held-out cases rather than rewriting this run.

## Timing and workflows

Full's separate timing pack is the **first 200 public JevBench cases**, repeated three times serially; it is not a balanced sample of all 7,671 records. Jev block medians are 250.5, 257.4 and 263.1 ms; Laya's are 17.2, 16.1 and 17.1 ms. Valid counts are Jev 200/199/199 and Laya 196/196/196. Report validity alongside throughput. Same-state fanout is serial repeated dispatch, not native batching. No peak concurrency, thermal-bracketing rerun or multiple hosted time windows were measured.

Full has twenty seeds per task in each mode. Jev succeeds in all **40 untimed episodes**, and **39/40 deadline episodes**. The sole deadline failure is ticket seed 5104, step 10: a correct `Success` answer arrives at **525.55 ms** and is discarded under the preregistered 500 ms cutoff. Ticket success then fails because it requires all twelve routes correct. The script's statement that one late answer cost an episode is accurate; it must not be sold as substantial general unreliability.

English Laya succeeds in 0/40 episodes in either mode. It gets **62/240 ticket routes correct**, deferring every ticket to Review, with no restricted-account violations; its failure is blanket over-deferral. It has no deadline misses. In each warehouse mode, its 700 violation steps are repeated moves at unchanged boundaries, not 700 independent decisions on novel states. The first-label control also succeeds in no episodes.

All obstacles are internal, leaving a ten-step edge route for every warehouse seed. All four directions remain available, including illegal moves. There is no legal-action mask or corrective conversation after a blocked move. These are legitimate measurements of this unguarded loop, not a difficult planning benchmark or proof that a guarded application using the model must fail. A simple shortest-path oracle solves the environment. Ticket generation is independent of previous routing, so it is sequential policy routing rather than a rich agent environment.

The environment waits for inference and then discards late actions; this is a defined service-deadline simulation, not continuously advancing physics. Jev latency includes the network, appropriately for that end-to-end requirement, while untimed task quality is shown separately.

## Corrected all-roster Demo

The Demo contains **72 original + 12 easy public JevBench cases and 36 formal fixtures**, zero hard cases, zero teacher cases and 60 statistical clusters. Every entrant supports all 120. Twelve return 120 valid outputs; English Laya returns 119. Independently recomputed main counts match all saved aggregates, with no duplicate prediction keys or native-choice normalization mismatch.

| Entrant | Strict correct / 120 | Median, ms | Ticket routes correct / 24 | Warehouse successes / 2 |
|---|---:|---:|---:|---:|
| Winnow Q8 | 117 | 52.6 | 24 | 2 |
| Jev | 115 | 267.6 | 24 | 2 |
| Decider v2 | 115 | 43.7 | 24 | 2 |
| Plumb | 113 | 34.3 | 8 | 0 |
| Nimble | 112 | 45.4 | 24 | 2 |
| Qwen JSON | 111 | 285.2 | 8 | 0 |
| SemIf | 109 | 36.7 | 10 | 0 |
| English Laya | 86 | 16.8 | 8 | 0 |
| Laya typed | 82 | 17.5 | 8 | 0 |
| ModernBERT NLI | 74 | 17.6 | 12 | 0 |
| Laya multilingual | 61 | 13.7 | 8 | 0 |
| CLM | 43 | 50.7 | 6 | 0 |
| First-label control | 41 | 0.0036 | 6 | 0 |

Winnow-minus-Jev is +1.67 percentage points, with a descriptive paired interval of **−3.33 to +5.88**. It does not establish superiority or equivalence. Demo medians are quality-request timings; no dedicated timing blocks run in Demo.

The SemIf/Qwen comparison shares the pinned Qwen3.5-4B backbone and BF16 profile. SemIf's median is about **7.8 times lower** in this setup, with 109 versus 111 correct. This is a ratio of observed medians, not a throughput ratio, quality equivalence or universal speedup. SemIf Score is an Arena categorical extension. Both runtime logs disclose reference causal-convolution fallback kernels; Qwen additionally uses a reference decode-update path. The script appropriately identifies JSON greedy decoding with thinking disabled.

Laya's sole Demo invalid is `jevbench-original-routing-06-1`: the correct label `general` accompanies probabilities totaling **0.9998**. Its label-only diagnostic is 87/120 versus strict 86/120. This is larger mathematical drift, not the superseded floating-point boundary bug. Laya's native loader also warns that choice confidence for 11+ options is uncalibrated after its temperature clamp.

CLM has **120 distinct probability vectors**, all valid. It selects the first label on only 9/60 static choice questions, so its 43/120 is not evidence of a hidden uniform mock. Source and runtime logs support trained heads, L2 normalization, CUDA and LAST pooling. Poor performance in this profile remains unexplained without a separate numerical native-parity/task-fit investigation. The script correctly avoids condemning contrastive models generally.

Demo ticket traces distinguish blanket Review deferral from unsafe routing: Laya variants, Plumb and Qwen send all tickets to Review, obtaining 8/24 with zero restricted-rule violations; CLM sends all to Billing, obtaining 6/24 with eight violations. Zero successful episodes alone conceals that difference.

## Judge, calibration and video acceptance

The **completed Demo judge** has 161 distinct-answer reviews over 60 question IDs: all 36 formal questions and 24/84 public questions. It gives 60 correct and 101 incorrect verdicts, no ambiguity flags, and no disagreement with the references in that sample. This is not an audit of every answer or proof of unambiguous labels; the routing issue is a concrete counterexample to treating judge agreement as conclusive. Equal case/answer pairs share one judgment. Numeric references and metrics remain code-scored.

The CLI explicitly requests `gpt-6-astra` but does not expose an observed model identity. Record this boundary in the report/description. Formal controls establish integration behavior, not broad semantic judging quality. The Full audit is terminal-complete and its mixed findings are detailed below; do not extend the Demo's no-disagreement statement to Full.

### Final Full judge findings

All **117 distinct-answer reviews across 60 case IDs** completed: **52 correct, 55 incorrect and 10 ambiguous**. The ten ambiguous verdicts also carry human-review flags and concern **seven distinct teacher cases**, already excluded from main-reference accuracy. Their rationales identify missing decision policies, uncertain impact or insufficient evidence. They reinforce why teacher agreement cannot be called independent correctness.

The stratified sample contains 30 public JevBench IDs, 12 formal IDs, 12 teacher IDs, three classification IDs, two multilingual IDs and one RAG ID. There are **three binary judge/reference disagreements over two cases**, not three independently disputed questions. No numeric labels or primary scores changed.

| Case | Frozen reference and candidates | Independent assessment |
|---|---|---|
| `xnli-4703-ar` | Reference contradiction; Jev contradiction (0.83), Laya neutral (0.7789). Judge rejects contradiction and accepts neutral. | The premise says a nephew asked for an acoustic guitar; the hypothesis says he really wanted a banjo. Asking does not logically establish private desire, making neutral defensible. The contradiction label is consistent with a pragmatic reading of the request as the actual preference, but the original annotation rationale is unavailable. The aligned English source expresses the same distinction; no translation/import bug is demonstrated. Treat this as a reference-interpretation dispute, not proof of judge infallibility or a label to silently change. |
| `fresh-test-03-059-noul` | Read access needed; Reader can read; Editor requires approval; approval absent. Oracle no to “Is approval missing for the requested action?” Jev yes (0.55), Laya/control no. | Under the intended operational question—whether required approval is missing—no best follows the policy because Reader requires none. A literal approval-status reading supports yes. The judge calls **both yes and no correct in separate batches**, switching between these readings while marking neither ambiguous. This is concrete inconsistency in its grading criterion, compounded by question wording. It should have surfaced ambiguity rather than confidently certifying both opposing answers. |

Seventeen frozen Full formal Noul cases share the second pattern: read access with absent approval. Reproduce the screen using family `Tool selection`, question kind `noul`, and state containing both `needs read access` and `Approval present=no`. Independently confirmed: 17 Full Fresh records, one Demo record (`fresh-test-03-001-noul`), and no Robustness records. This is a potential template-level wording caution, not seventeen proven wrong labels. No additional exclusions or alternate main score are introduced. Future held-out versions can ask “Does the policy require an approval that is currently missing?” The frozen current suite stays unchanged.

**Final script check:** `docs/VIDEO-SCRIPT.txt` now explicitly distinguishes the completed Demo audit from Full and includes the conflicting yes/no grading and ambiguous teacher cases. The new paragraph is accepted. Its wording follows this accurate formulation: “In the Full audit, the judge disagreed with references on two cases and flagged ambiguous teacher examples. It even accepted both yes and no for one question under different readings. We keep those disagreements visible; the judge does not rewrite the scores.” Put the exact 117 reviews / 60 IDs / three binary disagreements / ten ambiguous reviews in the report or on-screen note. Do not describe Full as universally judge-validated or imply the binary disagreements are the only audit cautions.

These few audited disagreements do not by themselves overturn the large measured Jev/Laya reference-agreement gap. They also cannot establish a global label-error rate from this small stratified sample. The appropriate acceptance is reproducible fixed-reference measurements with disclosed semantic limitations, not a claim of human-validated ground truth.

Calibration charts use only valid probability outputs. ECE's probability is the selected label's probability, not an author's entropy-style confidence field. Ten-bin ECE over a small mixed suite is descriptive; no deployment threshold has been fitted. Uniform's Demo ECE is about 0.062 despite only 41/120 correct, illustrating that calibration alone does not imply useful decisions. Qwen probabilities are N/A; NLI probabilities are transformed entailment scores.

The script's concrete high-confidence example is sound: in `fresh-test-02-001-noul`, the source and proposed answer both say the facility opened on Tuesday, yet Laya assigns 0.9096 to “contains an unsupported status claim.” The entire state explicitly defines matching as supported. This example is clearer than the withdrawn Jev routing example, and the script correctly calls it one case.

**Safe practical conclusion:** Jev achieves substantially stronger agreement with this suite's frozen references than English Laya, at substantially higher observed response latency; both strict and label-only scoring support that conclusion. Small local configurations remain worth task-specific investigation. Decider/Winnow/Nimble are candidates for a larger follow-up, not established Jev replacements. SemIf versus JSON is a useful deployment experiment for someone already using that backbone. CLM merits runtime-parity and task-fit investigation before a recommendation. None of these claims establishes private-test generalization, a best architecture, or production reliability.

Strong viewer objections are covered if the final edit retains the following adjacent to results: public training exposure; only three Full entrants; English versus multilingual Laya; fixed output-contract versus semantic correctness; the known routing ambiguity; repeated-template statistical dependence; unmasked/looping workflow design; probability-metric denominators; runtime optimization differences; and the judge's limited scope. The script is already unusually careful; do not add generic disclaimers that obscure these concrete findings.

## Historical source findings — superseded and resolved

These issues explain why preliminary runs were discarded. They are **not active defects in the corrected comparison**.

| Earlier finding | Evidence and verified resolution |
|---|---|
| Native request asymmetry | Imported criteria were repeated in local instructions while Jev received the original question (`arena/suites.py`, `arena/importers.py`, old `workers/runner.py`). Shared `arena/wire.py` now preserves native source payloads for hosted/local paths; the absent-criteria case is covered. Parent verified all 2,231 imports reconstruct exactly. |
| SemIf mapping divergence | Author mapping uses criterion descriptions prefixed with IDs and true/false ordering (`.arena/sources/semif/benchmarks/build_typesafe.py:76-87`). Shared wire conversion now follows that mapping; Score is explicitly an Arena extension. |
| Hidden Laya truncation risk | Native `.arena/sources/laya/laya/common.py:113-146` clips options to 48 tokens and budgets instruction/state tokens. The worker now checks actual rendered option lengths, rejects over-limit options, budgets the full head and asserts exact native sequence length. Corrected GPU smoke and Demo execute this path. |
| Context failures misclassified | SemIf and Nimble native context-limit ValueErrors formerly became transport errors. Narrow known-message handling now reports unsupported; arbitrary runtime errors remain errors. |
| Rounded native choices overwritten | Local adapters formerly re-argmaxed rounded vectors while hosted Jev preserved `choice`. Shared normalization preserves native choice and uses one Noul convention. No remaining static selection mismatch was found. |
| Duplicate counterfactuals under-clustered | Full had 118 identical-input groups spanning original clusters, up to nine clusters/group. `statistical_clusters` now joins scenario relationships and exact canonical input duplicates, excluding question IDs. Independent check finds zero remaining cross-cluster duplicates; 2,825 original clusters become 2,625 components. This still does not establish new-template generalization. |
| Floating-point tolerance boundary | Binary floating arithmetic could reject mathematically 1e-4 drift. The comparison now includes a tiny numerical epsilon at the fixed boundary; genuine 0.0002 or 0.01 drift remains invalid under the frozen contract. |
| Misleading labels/metadata | Family macro was actually pack macro; ordinal metric is absolute error of expected score; NLI runs FP32 without BF16 autocast. Names/metadata are corrected, and first-200-public timing scope is explicit. |
| Stale raw result status | Original Demo cached `results.json` said verifying after run completion. Its API/portable export already uses terminal status, independently verified. The final CPU smoke independently verifies the corrected raw finalization order. |

The CLM positive source checks remain useful: its engine defaults to the trained `clm-latest` head and projects both state/action embeddings (`.arena/sources/clm/src/clm/engine.py:104-136`); worker normalization mirrors reference L2; logs explicitly report LAST pooling. Laya's strict CUDA forward mirrors native autocast while removing silent CPU retry. These are meaningful source checks, but should never be relabeled as independently measured numerical parity.
