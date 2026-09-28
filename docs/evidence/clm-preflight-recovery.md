# CLM preflight recovery — 27 September 2026

Before any predictions in the all-13-entrant Full v2 run, we compared Arena's CLM adapter with the upstream CLM Engine and HTTP Embedder on 36 short development probes. Both paths used the same pinned Qwen3-8B BF16 encoder, LAST pooling, trained CLM head and native question mapping. These probes are not the held-out Full cases.

| Check | Selected-label agreement | Largest absolute probability difference | Gate |
|---|---:|---:|---|
| Native server defaults vs Arena | 36/36 | 0.03332456 | Fail |
| Matched prefix caching and token-batch budget | 36/36 | 0.03437022 | Fail |
| Matched settings with batch-invariant kernels on both paths | 36/36 | 0.000000404 | Pass |

The gate remained exact selected-label agreement and probability differences no larger than 0.0001. We did not relax it. Independent recomputation from the final saved vectors confirmed the passing result.

The two default-mode Arena launches themselves differed by up to 0.01979668 in probability, with all labels unchanged. That was evidence against treating the whole native-path difference as a wire-adapter error. After enabling batch-invariant mode, the native and Arena results met the strict gate. This is consistent with scheduling-dependent numerical variation, although we did not isolate every low-level kernel contribution.

[vLLM's reproducibility documentation](https://docs.vllm.ai/en/latest/usage/reproducibility/) says default execution does not guarantee reproducibility and identifies batch invariance as the online serving option. Its [batch-invariance documentation](https://docs.vllm.ai/en/latest/features/batch_invariance/) describes deterministic kernels and lists Qwen3-8B among tested models; the feature is marked beta. Our result establishes agreement for these probes on this hardware and pinned runtime, not general reproducibility across devices or versions.

The Full v2 CLM profile explicitly sets `VLLM_BATCH_INVARIANT=1`; both comparison paths disable prefix caching and use an 8,192-token scheduling budget. The underlying weights and image remain pinned and unchanged. The runtime metadata records `clm-v2-batch-invariant`. This serving configuration differs from v1 and can affect latency. Full timing results describe this deployment and must not be presented as peak CLM serving speed. All 41 local verification tests passed after the configuration change.

The two failed attempts are retained under `.arena/video-v2/native-clm-attempt-1-server-defaults/` and `native-clm-attempt-2-matched-cache/`. Passing evidence is under `.arena/video-v2/native-clm/`. The old run measurements remain unchanged. Full run `20260927-205440-6350b9` started only after the passing preflight, at 19:54:40 UTC. These checks do not establish task suitability, long-context parity, or the final leaderboard.
