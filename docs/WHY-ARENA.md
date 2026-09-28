# Why build Arena when leaderboards already exist?

**Use a leaderboard to make a shortlist, then test the deployment you intend to build.** Arena records the exact profiles, inputs, outputs and serving setup behind our comparisons. It lets us inspect a failure instead of treating one aggregate score as the deployment decision.

Sources checked 28 September 2026:

| Resource | What it offers | How our work differs |
|---|---|---|
| [JevBench Live / Benchmark Heaven](https://benchmarkheaven.com/jev-models) | The page currently reports JevBench v1.4.2.2, 534 public and 308 sealed aggregate decisions, intelligence and calibration measures, plus cost and speed views. Requests are serial from Germany. | Arena's pinned public JevBench subset is only one component of an older frozen suite. We add selected classification/relevance tasks, explicit policy fixtures, variations and recorded workflows. This is **not** a reproduction of today's complete JevBench or its scoring. |
| [DecisionBench leaderboard](https://huggingface.co/spaces/Hanno-Labs/decision-bench-leaderboard) and [official runtime](https://github.com/Hanno-Labs/decision-bench) | An open, reproducible benchmark for document-grounded decisions, with breakdowns by task, family, domain and primitive. Its official overview describes 23,900 rows across nine families and three primitives, plus a reasoning track. | Arena answers a narrower deployment question using our pinned models, RTX 5090 setup and measured failure cases. Our ABCD adaptation adds support next-step decisions with full versus retrieved policy. We did not run the full DecisionBench suite. |

The motivation is practical: model loading and memory, allowed choice counts, usable input length, short versus long request times, output validation, and behavior across a sequence of decisions. Local runs make those details inspectable. Hosted Jev timings include the network and an undisclosed backend; they cannot reveal its size or hardware efficiency.

Arena is not automatically more comprehensive because it has more cases than a particular displayed subset. Some Arena cases are deliberately simple or correlated; teacher-labelled cases only measure teacher agreement. ABCD uses a balanced task mix and synthesized terminal checkpoints. Neither assessment establishes live customer-resolution success. Read the result limitations before choosing a model.

Read the [practical findings](BUILDER-TAKEAWAYS.md) and [task analysis](ANALYSIS.md), or [download the recorded reports](../results/README.md).
