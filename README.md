# Jev Arena

A local app for comparing decision models: inspect their answers, measure response times and input limits, and replay decisions inside small software workflows.

![Jev Arena dashboard with shared-question accuracy and response times](docs/arena-dashboard.png)

## Explore the recorded results

The video demonstrates two completed assessments on Windows with an RTX 5090 (32 GB):

| Assessment | Scope | Read the findings |
|---|---|---|
| Arena Full v2 | 13 profiles, 7,671 cases per profile, serial timing and recorded workflows | [Results](docs/RESULTS.md) · [Task analysis](docs/ANALYSIS.md) |
| ABCD support decisions | Five profiles, 300 conversations, full handbook versus retrieved policy | [Results](docs/ABCD-RESULTS.md) |

**[Download the interactive reports and evidence](results/README.md)** to explore the saved assessments without installing models, Docker or a GPU. Download an HTML report and open it in your browser, or unzip an evidence package and open `report.html`.

The source checkout includes aggregate evidence, methods and the app. Saved run databases and raw third-party case text stay local. A fresh installation therefore has no recorded run history or full case inputs; use the portable reports to inspect the published results, or run an assessment to populate the app. The reports include saved metrics and workflow replays; raw case browsing requires local run data.

These are measurements of specific deployment profiles. The two assessments have different tasks and denominators. See the [practical takeaways](docs/BUILDER-TAKEAWAYS.md), [scoring and implementation](docs/IMPLEMENTATION.md), and [reference limitations](docs/REFERENCE-CAUTIONS.md).

## Run the app on Windows

Install [Node.js 22+](https://nodejs.org/), [uv](https://docs.astral.sh/uv/), [Docker Desktop](https://docs.docker.com/desktop/) and an NVIDIA driver with working Docker GPU support. The full roster needs at least 150 GB free, preferably 200 GB; smaller selections use less storage.

```powershell
git clone https://github.com/theaiautomators/jev-arena.git
cd jev-arena
.\Start-Arena.ps1
```

Open **http://127.0.0.1:8787**. In Setup, select models and choose **Prepare selected** to download pinned sources, datasets and checkpoints and build their workers. Detailed preparation logs stay in `.arena/setup.log`.

For a smaller initial roster:

```powershell
.\Start-Arena.ps1 -Prepare -Models laya,plumb,decider
```

Choose **Run a new test → Configure new test**. Start with **Smoke**, then use **Demo** or **Full** as needed. Starting a test creates a new run and Full can take hours. Browsing results and replaying recordings make no model requests.

## Run the app on Linux

Install Node.js, uv, Docker and the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).

```sh
bash start-arena.sh
# Optionally prepare selected models on first launch:
bash start-arena.sh --prepare laya plumb decider
```

Winnow defaults to CUDA architecture 120 (RTX 5090). Set `ARENA_CUDA_ARCH` before preparation for another GPU. GPU inference was verified on Windows/5090; Linux CI checks the contracts and frontend without model weights.

## Optional hosted model and audit

For hosted Jev, obtain a key from [TypeSafe](https://typesafe.ai), copy `.env.example` to `.env`, set `TYPESAFE_API_KEY`, and restart Arena. The key stays server-side. A persisted $5 per-run cap uses conservative reservations before requests and across resume. Never commit `.env`.

Numeric accuracy is calculated against saved answer keys. The optional blinded sample audit uses the project-local Codex CLI, requesting GPT-6 Astra through your ChatGPT login:

```sh
npx codex login
uv run python -m arena.judge_controls
```

Choose **Verify judge** in Setup. Your account must have access to the requested model. The audit consumes Codex quota and has no direct API-key fallback or silent model substitution. Automated review is separate from accuracy and is not human semantic validation. See the [judge boundaries](docs/IMPLEMENTATION.md#judge).

## Reproduce and develop

```sh
uv sync --frozen --extra dev
uv run pytest -q
npm ci
node --experimental-strip-types --test apps/web/tests/*.test.mjs
npm run build
uv run python -m scripts.verify_models laya plumb --preset smoke --judge
```

The last command runs models and an audit; omit `--judge` to skip the audit. Checkpoints and sources are pinned in `arena/registry.py` and `sources.lock.json`. Manifests record hardware, inputs, code, images and dependency hashes; resume refuses to mix changed runtimes into an existing run.

- [Full v2 protocol](docs/VIDEO-EVALUATION-V2.md), [ABCD protocol](docs/ABCD-PROTOCOL.md) and [implemented methods](docs/IMPLEMENTATION.md)
- [Verification and limitations](docs/VERIFICATION.md)
- [Results and report export commands](results/README.md)
- [Why Arena complements existing leaderboards](docs/WHY-ARENA.md)
- [Shared app layout](apps/shared/README.md)

Frozen protocols, including [the original evaluation specification](EVALUATION.md), retain their original wording for provenance. Their historical scheduling/publication notes describe the time of the experiment; the current results and implemented methods describe what was completed.

Run data, source datasets, weights and logs live under ignored `.arena/`. Use sanitized exports for sharing. The service binds to loopback and rejects foreign hosts/origins; do not expose the development service directly to the internet.

## License

Arena's original code is [MIT licensed](LICENSE). Weights, datasets and reference runtimes retain their publishers' terms; see [attribution](THIRD_PARTY.md) and [bundled notices](THIRD-PARTY-LICENSES.txt). Jev Arena is independent and unaffiliated with TypeSafe or the model authors.
