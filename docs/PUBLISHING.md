# Publication handoff

Destination: **theaiautomators/jev-arena**, public. The owner asked to create the GitHub repository tomorrow. No remote repository has been created or pushed by this build.

The repository contains the application, original fixtures, reproducible downloaders, pinned dependency/source files, tests and documentation. The local `.env`, `.arena` evidence/model cache, downloaded datasets and creator transcripts are ignored. Run exports deliberately omit keys, CLI logs, private paths and source dataset text.

Before the first public push:

1. Review `docs/VERIFICATION.md` and the adversarial review. Keep unresolved methodological limitations visible in the video and README.
2. Inspect the staged file list and check that `.env`, `.arena`, model weights and third-party datasets are absent.
3. Create an empty public repository under `theaiautomators`, then add its HTTPS URL as `origin` and push `main`.
4. Verify the public clean-clone instructions and GitHub Actions result. Add the published URL to the video description.
5. Share an exported report only after checking its run ID and methodology. A completed run is not a validated universal ranking.

Suggested description: "A local decision-model arena: Jev, Laya and open alternatives, reproducible evaluations, Codex CLI judging, and recorded workflow replays."

The benchmark service runs on loopback. A public source repository does not require exposing the running local application.

The public `main` history is prepared as a clean initial release. Earlier local development history is retained under the private local ref `refs/private/build-history`; it contains historical local-environment notes and must not be included in a mirror push. Push `main` only. The accepted original runtime snapshots remain in ignored local evidence and in sanitized run exports.
