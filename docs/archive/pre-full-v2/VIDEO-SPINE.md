# Video spine and recording notes

Target: approximately 13–15 minutes at 140–155 words per minute. The clean [teleprompter script](VIDEO-SCRIPT.txt) is approximately 2,020 words, without stage directions. Open on the app; explain the category after the audience sees the experiment. Numeric claims use the run IDs and limits in [RESULTS.md](RESULTS.md).

| Beat | Screen | Spoken purpose |
|---|---|---|
| 0:00–0:45: arena cold open | Measured replay, then the quality/latency chart | "I've put Jev head to head with a lineup of local decision models to see which ones are worth using." Establish a concrete decision, a visible failure and the question the experiment answers. |
| 0:45–1:20: the experiment | Impress, selected entrants and saved run | Show one-button loading, evaluation, unloading and judging. Explain that live playback uses recorded sequential runs. |
| 1:20–2:30: initial result and decision-model explanation | One routing example and its allowed labels | Contrast choosing a permitted action, assigning a probability and scoring an ordered scale. A valid label can still be wrong. |
| 2:30–4:45: meet the challengers | Setup roster; group models by approach | Jev hosted; small Laya variants; specialized Plumb, Decider, Nimble and Winnow; SemIf's base-model logit readout; CLM's contrastive approach; ordinary Qwen JSON and NLI controls. |
| 4:45–6:00: what was actually tested | Suite counts and coverage | Distinguish the 120-case demo from the 7,671-case Full suite. Name the entrants that actually finished each. Explain public references, teacher agreement and formal fixtures. |
| 6:00–7:30: headline trade-offs | Matched metrics, latency and coverage | Discuss measured numbers with denominators. Hosted latency includes the network. Local runtime configuration and model precision are part of the result. |
| 7:30–9:00: inspect failures | Cases and probability calibration | Show a wrong answer, a correct low-confidence answer if available, and the strict output contract. Explain why confidence is not proof. |
| 9:00–10:45: do decisions help a workflow? | Warehouse and ticket traces; untimed/deadline toggle | Success, violations and late answers matter beyond static accuracy. These are transparent simulations, not proof of general agent reliability. |
| 10:45–12:15: objections that survived review | Short on-screen methodology notes | Public exposure, small-sample rankings, templates, capability exclusions, precision/runtime differences, judge limitations and any unresolved adapter concern. |
| 12:15–end: practical takeaways | Results dashboard and repository | Recommend a shortlist to test on the viewer's own workload, proportional to evidence. Explain how to reproduce the exact configuration. |

## Competitor facts to source

- [TypeSafe Jev](https://docs.typesafe.ai/introduction): hosted structured decision service; not a locally downloaded checkpoint in this comparison.
- [Laya](https://github.com/NandhaKishorM/laya): small decision engines with separate English, typed and multilingual checkpoints. Do not count these as three unrelated model families.
- [Plumb](https://huggingface.co/crh225/plumb-4b): 4B checkpoint using the JevK5 runtime; this profile supports at most 16 choices.
- [Decider](https://huggingface.co/Mapika/decider-4b): specialized 4B decision model. Arena pins v2; the current model card may discuss a newer release.
- [Winnow](https://huggingface.co/EldanRing/Winnow-12B): larger Gemma-derived contender, measured with its native runtime and Q8 weights.
- [Nimble](https://huggingface.co/bespokelabs/Bespoke-Nimble-9B): Qwen3.5-9B plus a decision adapter. Its declared training mixture includes public classification material, so public benchmark results are not evidence of unseen generalization.
- [SemIf](https://github.com/TheoLeeCJ/SemIf-OpenJev): reads candidate-answer logits from a base model, instead of requiring a new decision fine-tune.
- [CLM](https://github.com/Contrastive-LM/CLM): a contrastive state/action approach with a Qwen3-8B encoder and released heads. This run disables action caches; don't generalize its timing to all deployment profiles.
- [Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B): ordinary JSON-prompted generation control, sharing the SemIf backbone revision; no invented confidence scores.
- [ModernBERT NLI](https://huggingface.co/MoritzLaurer/ModernBERT-large-zeroshot-v2.0): an entailment-based classification control, whose normalized scores are explicitly transformed.

## Recording rules

Show the run ID and preset when introducing a result. Do not splice Full and Demo numbers into a single leaderboard. Keep the measured replay label visible. Pin all model revisions in the description. The report export is suitable for a browser demonstration without loading a GPU model.

The opening should say "I've put", correcting the typo in the suggested line. Avoid "no hallucinations", "always correct", "free inference", "the fastest model", or "all models passed the full benchmark" unless the displayed evidence supports the exact claim.

## Claim ledger for the corrected Demo

These facts describe completed run `20260927-142204-8262c6`, including 161 blinded answer reviews across 60 case IDs. Its result counts were independently recomputed by the Astra reviewer. The interpretation remains limited to these configurations and this small suite.

- Winnow: 117/120; Jev and Decider: 115/120. A two-answer lead is visually interesting but too small for a winner claim. Winnow-minus-Jev paired interval: -3.33 to +5.88 percentage points.
- Laya English: 86/120 under the fixed output contract; one probability vector sums to 0.9998 and is invalid. Show selected-label sensitivity separately when discussing this failure.
- SemIf: 109/120 at 36.7 ms median; same-backbone JSON generation: 111/120 at 285.2 ms. These are observed short-suite deployment trade-offs; the two-case difference does not establish quality equivalence. SemIf Score is an Arena extension.
- CLM: 43/120; uniform first-label control: 41/120. Do not describe this as random-level general intelligence or a broken architecture. Native numerical parity and other CLM deployment profiles remain unestablished.
- Keep the multilingual Laya result scoped to this English-heavy Demo. Its name is not evidence that it should dominate English specialized decisions.

## Claim ledger for the longer comparison

Use Full run `20260927-144758-15b0d8`. Jev, English Laya and the uniform control each have 7,671 static records, of which 5,671 share public/formal reference labels and 2,000 are separate teacher-agreement cases. Do not show the other ten Demo entrants as if they ran Full.

- Strict reference agreement: Jev 5,156/5,671 (90.9%); Laya 3,147/5,671 (55.5%); uniform first label 2,088/5,671 (36.8%).
- Post-hoc selected-label diagnostic: Jev 5,192/5,671 (91.6%); Laya 3,240/5,671 (57.1%). This isolates the label from the chosen probability-output rule. The rule is an Arena contract, not a claim about each vendor's API guarantee.
- Quality-request medians: Jev 264 ms including hosted network time; Laya 18.4 ms locally. Dedicated serial block timing is separate and uses only the first 200 public JevBench inputs.
- The English Laya checkpoint ran Full; its multilingual sibling did not. English formal fixtures also show a large gap, but shared templates limit generalization. Do not attribute the entire aggregate gap to language coverage or probability rounding.
- Excluding 50 potentially ambiguous routing records leaves 5,621 references: Jev 91.66% strict / 92.30% labels; Laya 55.29% strict / 56.95% labels. This is post-hoc sensitivity, not a replacement leaderboard.
- Jev succeeded in 40/40 untimed episodes and 39/40 with a 500 ms deadline. English Laya succeeded in 0/40 in both modes, despite no deadline misses. It sent all tickets to Review, including all 178 unrestricted tickets per mode, and repeatedly hit the warehouse boundary. Show these mechanisms alongside episode counts.
- Raw RAG accuracy is vulnerable to class imbalance: first-label control 90.6%, Jev 93.8%. The script does not use this pack to claim strong retrieval ability.
- The practical shortlist is Decider and Winnow for a larger local follow-up, with Nimble and SemIf worth task-specific investigation. No all-roster Full ranking or native numerical parity claim is established.

## Workflow objections to address in the final review

The warehouse exposes all four direction labels, including moves that would hit a wall or leave the grid. That intentionally tests adherence to supplied constraints. Production systems should often mask impossible actions or validate them; this profile does not measure the performance of that guarded system. Deterministic models can repeat the same invalid answer because the unchanged state is sent again, without conversational retry history.

All blocked cells are internal; the outside edge always offers a ten-step route from start to goal. Different seeds do not create a broad planning benchmark. Call this a small workflow test, not difficult navigation or proof of general agent competence. Ticket episodes likewise contain independent policy decisions, with success defined strictly as all twelve correct. Show step accuracy alongside the all-or-nothing episode count when explaining a failed ticket episode.

## Configuration notes for on-screen captions

- Only local neural models run on the RTX 5090. Jev is hosted; the uniform control is CPU arithmetic.
- Qwen JSON: greedy decoding, thinking disabled, 128-token response budget, no grammar-constrained decoding. This is one baseline configuration, not all possible uses of Qwen.
- Decider uses the pinned v2 checkpoint; v2.1 is not included. Display the pinned checkpoint/version, not a moving latest-model claim.
- Jev latency includes network travel. Local profiles are reference/eager deployments, with different sizes/precision and some fallback kernels; these are not each author's best possible server throughput.
- Judge metadata: requested GPT-6 Astra; observed model identifier unavailable in tested CLI; Codex CLI 0.157.1. No API-key judge client.
- Full audit: 117 answer reviews over 60 case IDs; three reference disagreements across two cases and ten ambiguity verdicts across seven teacher cases. One tool-policy question received conflicting yes/no approvals. The judge never rewrites primary labels. Additional wording cautions are documented; the 50-case routing sensitivity is not an exhaustive semantic correction.
- Routing ambiguity: two Demo records and 50 Full records have a plausible alternate reading. Original scores remain frozen. See REFERENCE-CAUTIONS.md and the separate post-hoc sensitivity table.
- Strict accuracy requires a matching label and Arena's fixed output contract. Matched labels ignores contract validity on the shared cohort. Label-only Qwen has no probability-sum requirement. Do not call rounded-vector drift a reasoning failure.

## Cold-open shot setup

Use the completed corrected Demo `20260927-142204-8262c6`. Open Replay → Warehouse dispatch → Seed 5090 → Untimed quality. Select Jev, Decider v2, Winnow and Laya. Set playback to 0.25×, restart, then play. Keep the recorded/sequential/playback-speed labels visible. This gives an approximately eleven-second replay: three paths reach the destination while Laya repeatedly chooses east at the boundary. Show the actual path, then cut to the full roster. The still in `arena-replay.png` is from this measured replay.

For the routing shot, select Ticket routing with the same seed, then show the Results workflow panel. The aggregate across two seeds is 24 tickets. Laya/Plumb/Qwen/typed and multilingual Laya send all 24 to Review; 16 were unrestricted. CLM sends all 24 to Billing and violates the restricted-account rule 8 times. Explain these different failure modes rather than saying only that each failed its episodes.

For the confident-error shot, use Demo → Cases → Laya → `fresh-test-02-001-noul`. Show the complete source and question. The source and proposed answer both say the facility opened on Tuesday; Laya assigns 0.9096 to the claim being unsupported. Do not substitute the ambiguous Jev routing example as an unambiguous error. The Full checkpoint log also warns that Laya confidence for 11+ choices is uncalibrated after its native temperature clamp.

## Description and publication note

Link the research, implemented methodology, accepted results, reference cautions and adversarial review in the video description. The repository target is `theaiautomators/jev-arena`; create/publish it tomorrow as requested. The current script uses a future-tense repository line. After the repository and clean-clone CI are verified publicly, that line can become: “The repository is linked in the description, so you can run it and add your own cases.”
