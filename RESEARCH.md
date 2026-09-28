# Research and model shortlist

Research date: **27 September 2026**. Recommendations below are candidates for testing, not claims that we have measured their performance on this machine.

## Findings that change the build

TypeSafe is the company behind Jev. Jev accepts state plus `choice`, `score`, and `noul` questions and returns structured decisions. Treat TypeSafe/Jev as one entrant. The official baseline is currently `jev-1.13.0`; pin it instead of a moving alias. Its documented tariff is **$0.042 per million input tokens**, with free output. Access and current account limits still need to be verified. [TypeSafe introduction](https://docs.typesafe.ai/introduction), [model specifications](https://docs.typesafe.ai/models).

The newest JevBench release found is **v1.4.2.1, released today**. Its composite top five are Plumb-4B, decider-4b v2, Jev, JevK5 v0.2, and Cygnet. These are combined quality/calibration/speed/cost results, not an accuracy ranking. Its sealed task contents are unavailable; our public-subset run cannot reproduce that leaderboard. [Release and provenance](https://github.com/fstandhartinger/jevbench/blob/main/docs/RELEASE-v1.4.2.1.md).

Search results initially surfaced the older v1.3 board. Direct repository retrieval found the newer release; the README commit was `fb829df88574e468f4b8e05484ad529d8c8d65f8`, timestamped 2026-09-26 23:46:52 UTC. This is why the build must freeze source revisions and record the research date.

Another useful independent finding: CLM's author's agent demonstrations are promising, while JevBench v1.4.2 reports weak results for CLM on its typed-decision tasks. That disagreement makes CLM worth testing across both static questions and closed-loop tasks. Neither result establishes universal superiority. [CLM project](https://github.com/Contrastive-LM/CLM), [independent release results](https://github.com/fstandhartinger/jevbench/blob/main/docs/RELEASE-v1.4.2.md).

## Recommended full roster

The first eight rows are the main on-screen comparison. The remaining four are diagnostic controls. All enabled entrants run all applicable suites; unsupported cases remain visible. GPU memory below is a planning estimate unless explicitly attributed to the author, not a measurement of our runtime.

| Entrant | Why include it | Proposed local execution and caveats |
|---|---|---|
| **Jev 1.13.0** | Hosted reference | TypeSafe API, server-held key, no local weights found in the official sources reviewed. |
| **Plumb-4B** | Current independent composite leader | `crh225/plumb-4b` through pinned JevK5 v0.2 runtime. Author says about 10 GB free GPU memory for BF16. **2–16 options**: no silent reduction of BANKING77 to 16 classes. [Model](https://huggingface.co/crh225/plumb-4b), [runtime](https://github.com/crh225/plumb). |
| **Mapika decider-4b v2** | Strong current general alternative | Pin the `v2` revision and its resolved commit. The default model card now describes **v2.1**, with changed calibration and task tradeoffs. Add v2.1 as a separate optional experiment, never substitute it for the benchmarked v2. BF16 weights are about 8.4 GB; allow runtime headroom. [Model and version notes](https://huggingface.co/Mapika/decider-4b). |
| **Winnow-12B Q8** | Larger local challenger | Author's typed-decision llama.cpp server; Q8 file is 12.67 GB. The author reports operation on a 16 GB GPU. Verify actual 5090 context/cache limits. [Model card](https://huggingface.co/EldanRing/Winnow-12B), [inference implementation](https://github.com/EldanRing/winnow-inference). |
| **SemIf / OpenJev, Qwen3.5-4B** | Tests direct answer-logit reading without another fine-tuned model | Use the author's native prompt/readout and frozen base model. Strong matched-backbone comparison with a generated-JSON baseline. MIT runtime; base weights retain their own license. [Project](https://github.com/TheoLeeCJ/SemIf-OpenJev). |
| **CLM-8B** | Different contrastive architecture and action-caching approach | Qwen3-8B pooling encoder plus the released head; approximately 16 GB of BF16 encoder weights before overhead. Coordinate both processes. Its default state limit is 2,048 tokens; raise both encoder and CLM limits together where supported. [Project](https://github.com/Contrastive-LM/CLM). |
| **Bespoke Nimble 9B** | Credible typed-decision model with reference inference and public evaluations | Qwen3.5-9B plus the Apache-2.0 adapter. Current card documents 8,192 tokens and up to 255 choices. Approximately 18 GB base BF16 weights before runtime overhead. [Model](https://huggingface.co/bespokelabs/Bespoke-Nimble-9B), [source](https://github.com/bespokelabsai/nimble). |
| **Laya English** | User-requested small local decision engine | Pin `convaiinnovations/laya` and the native runtime; 421M-class model. Start with its reference path before optimized runtimes. [Project](https://github.com/NandhaKishorM/laya). |
| **Laya typed-decisions** | Measures domain specialization | Separate entrant, never merged with Laya English. Its authors explicitly attribute its stronger typed-decisions performance to training on that benchmark's training split. [Benchmark disclosure](https://github.com/NandhaKishorM/laya/blob/main/BENCHMARKS.md). |
| **Laya multilingual** | Measures language support | Separate pinned checkpoint; compare on English and the same multilingual cases. A language router is a composite system and must get a separate row if evaluated. [Checkpoint routing documentation](https://github.com/NandhaKishorM/laya/blob/main/docs/index.md). |
| **Qwen3.5-4B, constrained JSON** | Answers whether a normal small LLM is sufficient | Same base revision/precision as SemIf wherever possible. Generate only required labels/levels, no explanatory essay. JSON validity is measured; probability metrics are N/A unless a valid probability method is separately specified. [Base model](https://huggingface.co/Qwen/Qwen3.5-4B). |
| **ModernBERT zero-shot NLI** | Classical classifier control | `MoritzLaurer/ModernBERT-large-zeroshot-v2.0`; its trained entailment head is an appropriate baseline. Score independent label hypotheses; distinguish transformed label scores from native joint probabilities. [Model card](https://huggingface.co/MoritzLaurer/ModernBERT-large-zeroshot-v2.0). |

Use constant uniform/majority baselines as additional reference rows. Fit priors on training/calibration data only. Public classification tasks can appear in model training mixtures: maintain a per-model dataset-exposure ledger rather than describing every public result as unseen generalization.

## Additional candidates and hosted options

| Candidate | Decision |
|---|---|
| **JevK5 v0.2** | Useful parent-model ablation for Plumb; add after the main roster. Shares lineage, so it is not independent corroborating evidence. [Parent identified in Plumb's card](https://huggingface.co/crh225/plumb-4b). |
| **Mica v0.1 4B** | Good small challenger with merged weights, GGUFs, a typed server, and published per-item output. Docker defaults target older CUDA architectures; verify a 5090 build explicitly. [Source](https://github.com/akivet/Mica-v0.1-4B). |
| **djev / DiffusionGemma** | Worth an optional hosted comparison and a later local feasibility spike. It is an inference method over DiffusionGemma, not new trained weights. Do not assume a 26B BF16 deployment fits 32 GB. Quantized and hosted configurations need separate identities and parity checks. [Source](https://github.com/Davipar/djev-dev). |
| **decision-machine-1** | Most concrete additional hosted option found. Official docs provide API signup, classification and yes/no endpoints, and a free test tier. Different API semantics need a dedicated adapter. Production tariff currently $0.04/M input; recheck before use. [Official quickstart](https://docs.milliseconds.ai/quickstart). |
| **AnyJev** | Valuable controlled experiment: compare raw readout, debiasing, calibration, and fitted heads on one backbone. Some levels require labeled fitting; put them in the adapted track. [Source](https://github.com/nokia-applied-research/AnyJev). |
| **Cygnet, Hopper, reflex, Kev, other decider sizes** | Expansion shortlist from the independent board. Resolve exact original weights, runtime and licenses before promotion; the board alone is insufficient for a ready-to-run adapter. [Current release](https://github.com/fstandhartinger/jevbench/blob/main/docs/RELEASE-v1.4.2.md). |
| **meraGPT Decider 1 / Featherless Simple Jev** | Leads found through the typed-decisions dataset card. Vendor/model access was not fully verified; keep them out of the committed roster pending a working endpoint and source review. [Dataset card](https://huggingface.co/datasets/LocalLLaMA/typed-decisions). |
| **Ollaya** | A promising runtime manager, not another model. It can serve several families behind a common interface. Use only after native-reference parity, exact revision and unload behavior pass; runtime choice can alter speed and probabilities. [Source](https://github.com/ollaya-dev/ollaya). |

## Benchmark evidence

| Source | Useful contribution | Limitation and implementation decision |
|---|---|---|
| [JevBench](https://github.com/fstandhartinger/jevbench) | Typed task families, public cases, probability metrics, raw results and versioned methodology | The downloadable public core has 72 original + 48 easy + 111 hard decisions. Newer full evaluations include private/imported/sealed material. Label our run **JevBench public 231**, never the full official leaderboard. |
| [JevBench method](https://github.com/fstandhartinger/jevbench/blob/main/docs/METHOD-v1.4.md) | Shows why sealed tests and transparent composite formulas matter | Keep its published rankings as external evidence. Use measured local timings and our own disclosed cost accounting rather than importing its hosted-cost estimates or latency adjustments. |
| [LocalLLaMA typed-decisions](https://huggingface.co/datasets/LocalLLaMA/typed-decisions) | Four workflows; 400 test states, five questions each; soft-label targets | Gold averages samples from a roughly 4B teacher. The card says agreement is not correctness. Preserve native teacher-agreement metrics and add a separate audit against evidence. Do not feed `gold`, latent factors or agreement metadata to candidates. |
| [Dhruv Mehra's jevbench](https://github.com/dhruvmehra/jevbench) | Reproducible SST-2, AG News and BANKING77 classification; matched label descriptions | Different project from JevBench above. Use 500 fixed examples per source for the default suite; publish IDs and source splits. |
| [Nimble public benchmark suite](https://github.com/bespokelabsai/nimble/blob/main/docs/PUBLIC_BENCHMARKS.md) | Additional human-labeled tasks and a reference comparison harness | Useful expansion and adapter cross-check; avoid double-counting overlap with the chosen core. |
| [MASSIVE](https://huggingface.co/datasets/AmazonScience/massive), [XNLI](https://github.com/facebookresearch/XNLI) | Multilingual intent and inference | Use aligned, fixed samples and source-provided labels. Read data files directly where legacy dataset loader scripts no longer work. |
| [BEIR](https://github.com/beir-cellar/beir) | Relevance and ranking methodology | Start with a pinned SciFact subset and identical candidate pools; publish retrieval-pool recall and retain relevance labels. |

The public datasets are sufficient to begin. Fresh cases are still needed for a convincing video because public benchmarks may influence model training, and some reference labels are noisy. The exact proposed suite is in [EVALUATION.md](EVALUATION.md).

## YouTube research

Used the user-linked [baoyu YouTube transcript skill](https://github.com/JimLiu/baoyu-skills/blob/main/skills/baoyu-youtube-transcript/SKILL.md). Captions were retrieved via its yt-dlp fallback for two videos. Full transcripts stay in the ignored local research cache and are not intended for redistribution.

| Video | What was actually reviewed | Implication for this video |
|---|---|---|
| [Adam Gardner — TypeSafe AI Jev vs. Laya](https://www.youtube.com/watch?v=OLgiHBlDhWU), 21 September | English transcript. 00:40–02:08 outlines several judgments over a blog draft; 02:40–05:23 discusses Laya's origins; 06:26 describes his local setup difficulty. | Good multi-question workflow inspiration. It is an explainer, not a controlled performance benchmark. Attribute origin allegations as opinions; they do not inform our score. |
| [Matthew Berman — We need to talk about Jev…](https://www.youtube.com/watch?v=2z-7pIj57f8), 18 September | English transcript. 02:07–03:08 discusses game/browser demos; 03:22–04:15 ticket routing; 06:19–08:41 visual simulations; 09:26–10:45 quality versus time limits. | Show both task success and elapsed time. Treat headline speedups and reliability statements as claims to test. Valid labels do not imply correct decisions. |
| [Sam Witteveen — Jev: The Ultimate Classification Model?](https://www.youtube.com/watch?v=X117w2Rark8), 18 September | Title/page identified; caption retrieval failed with HTTP 429. | Useful follow-up lead. No transcript-based conclusions are claimed here. |
| [TerraNet — Jev and Laya Explained](https://www.youtube.com/watch?v=fGl7T88bITo), 24 September | Read the creator's [published transcript](https://terranettechnologies.com/videos/jev-laya-decision-models-vs-llms-explained). | Reinforces testing calibration and fine-tuned versus base variants. Current specifications should come from model cards, since runtime limits change. |

The distinctive contribution of Jev Arena should be **reproducible local results, fresh cases, failure inspection and real-time replay**, rather than another release explainer.

## Local observations and reuse (before implementation)

Read-only inspection found:

- RTX 5090, **32,607 MiB** reported memory, NVIDIA driver **591.86**.
- About **399 GiB free on C:** at inspection. Model caches, images and build layers need an explicit disk estimate before download.
- Codex CLI **0.144.1**, with `exec`, JSON events, JSON-schema output, ephemeral runs and ignored user configuration supported by local help.
- `codex login status` reported **Logged in using ChatGPT**. An actual Astra judge invocation remains a build-stage smoke test.
- Docker, WSL, Git, Bun, Node, Python and yt-dlp executable paths found. Docker daemon/GPU access was not tested. GitHub CLI was not on PATH.
- The Jev-Arena directory had no application source or applicable AGENTS.md at inspection.

Reusable local references:

- An existing local video-editor project’s `codex_runner.py`: schema-bound CLI output, ChatGPT-auth check, subprocess execution, retry policy and saved evidence. Adapt the pattern; do not copy its task-specific schema or assume its model-resolution fallback proves the actual model.
- An existing local Qwen evaluation arena and its runner: one-GPU sequencing, measured side-by-side replay, warm-up and thermal-drift checks.
- An existing local server evaluation arena: existing Docker/Windows launch conventions.

Codex's documented non-interactive entry point supports scripted runs and JSON events. The installed CLI's help was also checked because flags can differ between versions. [Official developer commands](https://learn.chatgpt.com/docs/developer-commands#codex-exec).

## Feasibility checks identified before implementation

The build must verify live TypeSafe access; exact model/runtime revisions; Blackwell-compatible kernels; native-to-wrapper probability parity; actual VRAM and disk usage; Astra availability through this CLI; dataset redistribution terms; and the GitHub account/repository destination. None requires another product-design discussion. An unavailable account, purchase or inaccessible runtime should appear as a concrete setup issue with a fallback, not silently change the comparison.

These paragraphs preserve the research-stage observations. The completed build uses project-local Codex CLI 0.157.1 and has exercised hosted Jev and all eleven local neural configurations on the RTX 5090. Current acceptance evidence and remaining limits are recorded in [build verification](docs/VERIFICATION.md) and [the implemented profile](docs/IMPLEMENTATION.md); numerical native parity and a human semantic audit remain unestablished. The intended GitHub owner is `theaiautomators`, with publication deferred at the owner's request.
