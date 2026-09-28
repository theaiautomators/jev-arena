# Recorded assessments

These are the two assessments demonstrated in the video, measured on Windows with an RTX 5090 (32 GB) on 27–28 September 2026. Scores, failures and frozen references are unchanged.

| Assessment | Interactive HTML | Evidence ZIP | Findings |
|---|---|---|---|
| Arena Full v2 — 13 profiles | [Download report](https://github.com/theaiautomators/jev-arena/releases/download/video-results-2026-09/arena-full-v2.html) | [Download evidence](https://github.com/theaiautomators/jev-arena/releases/download/video-results-2026-09/arena-full-v2.zip) | [Results](../docs/RESULTS.md) · [Task analysis](../docs/ANALYSIS.md) |
| ABCD support decisions — five profiles | [Download report](https://github.com/theaiautomators/jev-arena/releases/download/video-results-2026-09/abcd-v1.html) | [Download evidence](https://github.com/theaiautomators/jev-arena/releases/download/video-results-2026-09/abcd-v1.zip) | [Results](../docs/ABCD-RESULTS.md) |

Save an HTML file and open it in a browser. Alternatively, extract an evidence ZIP and open `report.html`. Viewing requires no installation, GPU, credentials or model calls. [Release details and checksums](https://github.com/theaiautomators/jev-arena/releases/tag/video-results-2026-09) · [Committed asset manifest](manifest.json).

Full v2 is run `20260927-205440-6350b9`: 99,723 static records, 39 serial timing blocks, 1,040 workflow episodes and 1,600 targeted follow-up predictions. Its portable viewer includes saved workflow replays. ABCD is `abcd-test-v1`: 12,720 records across five profiles, with full-handbook and retrieved-policy conditions. ABCD scores are separate from the Full v2 total.

The ZIPs contain the viewer, machine-readable results, sanitized prediction records, relevant methods, limitations and license notices. Full v2 includes the original source snapshot. Raw third-party case text, local paths, credentials, editorial drafts and agent planning files are excluded. Case browsing in the installed app requires the locally prepared inputs and saved run data.

These are fixed deployment comparisons. Unsupported requests, output-contract failures and reference ambiguities remain visible. Automated audits do not establish human semantic validity or a universal model ranking.

## Rebuild the public packages

With the original runs available locally under `.arena/`, build the frontend and run:

```sh
npm run build
uv run python -m scripts.export_builder_report
uv run python -m scripts.export_abcd
```

Outputs go to `.arena/public-reports/`. The scripts read existing predictions; they make no inference or judge calls and leave the original `.arena/reports/` exports unchanged. A source-only clone has the aggregate evidence but cannot regenerate per-prediction packages without the original local runs. Run your own assessment and use the app's Export action to share its results.
