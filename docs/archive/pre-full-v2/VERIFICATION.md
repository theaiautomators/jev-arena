# Build verification

Environment: Windows, Docker Desktop, NVIDIA RTX 5090 (32 GB), 27 September 2026. This distinguishes application verification from general model-quality claims.

## Completed checks

- **37 automated tests pass**, including exact preservation of all 2,231 imported native questions, probability boundaries, invalid-output accounting, teacher/reference separation, connected duplicate clusters, independent workflow oracles, deadline behavior, cancel/resume, runtime drift rejection, cleanup failures, local HTTP protections, Codex CLI isolation, and export privacy/license retention. The initial sandboxed attempt encountered seven temporary-directory permission errors; the scoped rerun passed all 37 with no test failures.
- TypeScript and the production frontend build pass. The npm dependency audit reported zero vulnerabilities at verification time.
- All eleven local GPU configurations loaded on the 5090, produced real answers, ran recorded workflow episodes, unloaded, and passed the recorded cleanup gate. The uniform control and authenticated hosted Jev also ran. No unrelated container was stopped.
- Corrected **13-entry Demo `20260927-142204-8262c6`** completed **1,560 predictions**, **52 workflow episodes**, and **161 distinct blinded Astra answer reviews over 60 case IDs**. There were no judge/reference disagreements in that sample. This does not audit the entire suite or establish human agreement.
- The Demo has 72 original + 12 easy public JevBench cases, plus 36 formal policy fixtures. It contains no hard JevBench cases. Twelve entrants returned 120 valid outputs; Laya returned 119 valid outputs and one correct-label vector whose probabilities summed to 0.9998, outside the fixed 1e-4 tolerance. Main scores remain unchanged; label-only sensitivity is disclosed separately.
- GPT-6 Astra was requested through ChatGPT-authenticated Codex CLI 0.157.1. The CLI accepted the request but did not expose an observed model identifier. Sixty formal judge controls plus twelve blind repeats passed; these are not a human semantic audit.
- Jev's key is held in ignored local configuration. It is excluded from source and report exports.
- Browser checks covered desktop and 390×844 layouts, keyboard focus/Escape, measured results, case inspection and replay controls. The final Full HTML report also ran on an independent static server with no Arena API, retaining its three recorded entrants, metrics, workflow outcomes and caveats. Mobile body width was 375 px within a 390 px viewport, with the selected model and reference denominator visible. No browser application errors were recorded.
- A fresh checkout of the release source, with no private caches or credentials, installed both pinned dependency sets and passed **35 tests with two expected prepared-dataset skips**. Its production frontend build passed, and npm reported zero vulnerabilities. The two dataset checks also pass in the prepared development workspace (37/37 total). Only this verification note and the measured preview image changed after that source check.

## Completed Full acceptance

**Full `20260927-144758-15b0d8`** was launched through the actual **Impress** button with Jev, English Laya and the uniform control. It completed **23,013 static records**, nine 200-request serial timing blocks, **240 workflow episodes**, three Laya load/cleanup cycles and **117 blinded answer reviews over 60 case IDs**. All entrants supported every case. The common primary denominator is 5,671 reference cases; 2,000 teacher cases remain separate.

The Full audit returned 52 correct, 55 incorrect and ten ambiguous verdicts. Three reference disagreements concern two case IDs; ten ambiguity flags concern seven teacher cases. The reviewer inspected competing XNLI interpretations and a tool-policy question where the judge accepted both yes and no under different readings. Neither the judge nor the reviewer changed frozen labels or primary scores. See the [accepted measurements](RESULTS.md), [reference cautions](REFERENCE-CAUTIONS.md) and [Astra review](ADVERSARIAL-REVIEW.md).

The independent Astra agent recomputed the Full counts, paired interval, sensitivity results and workflows, and reviewed the final teleprompter script for unsupported claims and likely viewer objections. It found no remaining script blocker within the stated scope.

## Final reporting checks

Reporting fixes preserve recorded hardware, model revisions and actual CLI metadata when exported; they do not probe the current GPU/login to invent historical provenance. New runs save the implemented-profile hash and supporting methodology/license files in their source snapshot. Terminal status is written consistently to the stored run and cached result.

Real CPU-only Smoke `20260927-154819-1905f2` completed 36/36 valid predictions and verified the terminal artifact, implemented-profile hash and snapshot contents after these fixes. Accepted Demo/Full reports were regenerated with original reports retained. Primary counts, accuracy and intervals were asserted exactly unchanged; other derived metrics agreed within 1e-12 floating-point tolerance. The original cases, predictions and runtime snapshots were not rewritten.

Final ZIPs contain the portable HTML, aggregate metrics, sanitized predictions, original source snapshot, license notices and explicitly labeled report-time methodology notes. Local copies are under `.arena/reports/`; they are intentionally outside the source repository.

The staged source and final HTML/ZIP reports, including nested original source snapshots, passed a 169-item scan for the exact local credential, credential patterns and private user paths. The public `main` starts from a clean release tree; earlier development history is preserved under a private local ref and excluded from the public branch. No GitHub remote is configured.

## Brand verification

The Arena uses the original The AI Automators wordmark from the supplied transcriber project, bundled Poppins fonts, charcoal surfaces and the reference blue (`#25a4ef`). The copied logo is byte-identical to the supplied asset. The production build passed; the dashboard, results and recorded replay were inspected at desktop and mobile widths, including a 390px layout without page overflow.

Both accepted portable reports were regenerated. The logo and all eight WOFF/WOFF2 font sources are embedded, and the Poppins license is included. The saved Demo report was opened and its logo, typography and recorded run verified. All four report tests passed. This styling change did not rerun evaluations or alter recorded predictions. The repository replay preview was refreshed.

## Superseded development evidence

The 12-entry Demo `20260927-133444-c484c3` predates the numeric and native-input fixes. Full runs `20260927-135813-5807f8` and `20260927-140330-ed8141` were cancelled to apply those corrections. Keep their evidence for debugging; do not use their numbers for the video. Corrected Laya smoke `20260927-142007-15840f` passed 36 valid predictions and cleanup before the roster rerun.

## Limits and publication

Linux GPU inference and other cards have not been verified. Every entrant has not completed the 7,671-case workload. The broader planned protocol contains human/semantic audits, concurrency scaling and thermal controls beyond this implementation. Read `IMPLEMENTATION.md` before making claims.

GitHub destination: **theaiautomators/jev-arena**. Publication is deferred to tomorrow at the owner's request. No remote has been created or pushed, and GitHub CI has not run.
