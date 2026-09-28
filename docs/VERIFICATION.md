# Verification and limits

This page summarizes checks on the two published assessments. Results are measurements of fixed profiles on one Windows RTX 5090 system. Automated review is not human semantic validation; the original `publication_ready=false` human-audit gate is retained in the saved evidence.

## Arena Full v2

Run `20260927-205440-6350b9`, 27–28 September 2026:

- Independently recomputed 99,723 unique static records, candidate-input hashes, all 13 model counts, strict/selected-label totals, 39 timing blocks, 1,040 workflow episodes and 33 local load/cleanup cycles.
- Verified 5,671 primary references per entrant before exclusions and the 4,635-reference shared cohort. Failed and unsupported attempts remain in their recorded categories.
- Checked 1,600 follow-up predictions, repeat/reversal inputs, hashes and usable-label denominators. These reuse main-run cases and are not independent new test cases.
- Completed 879 automated answer reviews across 300 selected questions, inspected flagged references and preserved all original answer keys. See [the Full v2 review](evidence/ASTRA-V2-REVIEW.md).
- Disclosed the Winnow harness error: the native limit is 64 choices, while the frozen manifest advertised 255, causing 500 BANKING77 errors. The future capability declaration is corrected; recorded results are unchanged.
- Native CLM parity passed 36 short development labels with maximum probability delta 4.0396e-7 under the declared batch-invariant profile. This does not establish parity on every input or optimized serving speed.

The task breakdown recombines to the frozen shared selected-label count for every profile. The overview uses that existing comparison; strict/full-cohort scores remain available. Prior browser checks covered results navigation, scoring controls, model profiles, task filters and recorded workflow replay.

## ABCD support decisions

Assessment `abcd-test-v1`, 28 September 2026:

- Independently checked 12,720 unique candidate records, five profiles, input hashes, token capacity and cleanup. Reconstructed all 17 pinned upstream source files and all 2,400 natural inputs per profile.
- Independently rebuilt combined scores and verified frozen source and journal hashes. Full v2 measurements and denominators are separate.
- Completed 118 automated answer reviews across 76 questions in 27 successful batches. Inspected all 33 flags across 21 questions; no reference labels changed. The requested model was GPT-6 Astra; its observed identifier was unavailable.
- Corrected the initial retrieval diagnostic using upstream step annotations only after execution. Corrected coverage is 236/300 action and 731/900 routing checkpoints. This changes the diagnostic, not model scores. See [the inspection](evidence/ABCD-AUDIT-REVIEW.md) and [closing review](evidence/ASTRA-ABCD-REVIEW.md).

Earlier browser checks covered task/context/scoring controls, action support, synthetic context controls and local case browsing. Raw dialogue and policy text are excluded from the portable reports.

## Public packages

The [downloadable reports](../results/README.md) preserve frozen metrics and include relevant methodology, sanitized predictions and license notices. Full v2 also includes its original source snapshot. Editorial drafts, planning notes, credentials, raw dataset text and private paths are excluded. Exporters use explicit document lists and scan the resulting archives, including nested source archives.

The source repository contains aggregate evidence and the runnable app; private run databases and full case inputs are not bundled. A fresh checkout can build and run CPU tests without model weights. Checks requiring original private assessment data skip when it is absent.

Reproduce source checks with:

```sh
uv sync --frozen --extra dev
uv run pytest -q
npm ci
node --experimental-strip-types --test apps/web/tests/*.test.mjs
npm run build
python -m scripts.check_publication
```

The publication check rejects tracked working material and broken relative documentation links. GPU inference and hosted judging are not required for these checks. Original frozen protocols and saved run measurements are retained; public documentation changes do not retroactively change them.

## Interpretation

Public training exposure is unknown; generated fixtures share templates; some references are ambiguous; task balance, hardware, runtime, quantization and network conditions affect comparisons. Paired intervals are descriptive. Short-request timing is not maximum throughput. ABCD measures agreement with recorded support steps rather than customer-resolution success. See [Full v2 results](RESULTS.md), [ABCD results](ABCD-RESULTS.md), [implemented methods](IMPLEMENTATION.md) and [reference cautions](REFERENCE-CAUTIONS.md).
