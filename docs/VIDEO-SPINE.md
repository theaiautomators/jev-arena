# Video spine — choosing a decision model for the job

Use [VIDEO-SCRIPT.txt](VIDEO-SCRIPT.txt) as the spoken script and [BUILDER-TAKEAWAYS.md](BUILDER-TAKEAWAYS.md) for the supporting explanation. Evidence remains in [RESULTS.md](RESULTS.md) and [ABCD-RESULTS.md](ABCD-RESULTS.md). Previous scripts/spines are preserved in archive/before-builder-edit; original v2-only materials are in archive/full-v2-final.

The story: local decision models can be fast and competitive, but task fit, input limits, output reliability and complete-workflow performance matter more than one overall rank. This presentation revision does not change predictions, reference answers, the frozen primary metric or original reports. The underlying assessments received Astra adversarial reviews; this new editorial revision has separate display/data verification.

| Beat | Show in the dashboard | Explain |
|---|---|---|
| Practical question | What we learned | Which model fits the decisions inside your software? Start with the deployment choice, not benchmark vocabulary. |
| Why build Arena? | Overview, then model details and Case explorer | Existing leaderboards help shortlist models. Arena adds inspection of these pinned profiles, hardware, memory, input limits and workflow tradeoffs. Different cases and scoring; no direct cross-leaderboard percentage comparison. See WHY-ARENA.md. |
| First result | Overview, then Enlarge chart | On the same 4,635 answer-key questions: Jev 95.23%, Winnow 94.61%, Decider 94.46%. These are selected answers; Jev is only 29 answers ahead of Winnow here. |
| What these models are | Model guide: Jev, Winnow, Decider, Laya | Hosted closed service versus local open weights; 12B, 4B and roughly 0.4B examples. Three Laya profiles are related. Parameters, dates and recorded load memory are different facts; load memory is not peak VRAM or system RAM. |
| Check feasibility first | Model guide: Plumb, Winnow, Nimble | 16 choices cannot directly cover 77 intents; Winnow supports 64. The 500 rejected Winnow requests remain in evidence. The same-question headline excludes unsupported groups for everyone. |
| Task specialization | What we learned: task table | Laya 92.2% news; Decider 84% multilingual entailment; Jev/Winnow 100% on our controlled policy groups. Narrow wins can be hidden by the overall average. |
| Read the benchmark carefully | Task table plus Tests & scoring | Policy templates and variations are 2,440/4,635 of the shared headline. SciFact always-irrelevant baseline gets 90.6%. These are selected, sometimes correlated cases, not a random sample of enterprise work. |
| Short-input response times | Enlarge chart; Presenter mode | Selected local contenders roughly 47–56ms versus hosted Jev 245ms. One request at a time on RTX 5090; hosted time includes network. Not concurrent throughput or an SLA. |
| Context correction | Model guide; Support conversations | Jev is not uniquely long-context. ABCD used Jev32K, Winnow64K, Decider32K, Qwen32K configured; Nimble8K. Most extra input was a handbook, not a very long dialogue. |
| The speed reversal | Support conversations | Full-handbook route medians: Jev0.36s, Qwen1.57s, Decider1.90s, Winnow2.85s. Different serving/caching/precision; Jev size is undisclosed. Do not infer model size from latency. |
| Choosing an action versus choosing when to act | Support conversations: full handbook → conditional action → combined task | Label comparison: Jev78.67% vs Winnow66.67% when an action is due; Winnow68.44% vs Jev63.78% when also deciding act/speak/finish. Keep denominator and score selector visible. |
| Retrieval changes the system | Switch to Retrieved policy | Winnow action labels76.33%; Nimble becomes feasible. Retrieval can shorten inputs and help, but can omit the needed policy. It is a different system design. |
| An answer your software can use | Score selector; Results output checks | Selected answer vs correct-and-usable output. Arena's probability tolerance is specific to this harness; label-only Qwen does not face that check. |
| Confidence and repeated decisions | Results confidence chart; Workflow replays | Confidence must be checked against observed correctness. Two tabs are two workflow types with many saved episodes, separate from static questions. Replays animate saved measurements. |
| Explain trust in the results | Tests & scoring | Code compares with answer keys. AI teacher agreement is separate. Astra audits a sample, contributes zero weight to the headline and is not human validation. |
| Deployment conclusion | What we learned | Shortlist by input length, choice count, task, memory and privacy needs. Measure production-like inputs and failure handling. No universal winner, no live customer-success claim. |

## Filming controls

- Run controls live on Run a new test. Configure new test opens settings; the final start action would create a separate run, potentially spend money and take hours. Do not start a test during filming.
- Enlarge chart and Presenter enlarge the evidence. Escape exits Presenter. Chart points can be focused to identify a model.
- Support conversations is a separate five-profile experiment in the same dashboard. Do not add its questions to the 13-profile denominator or imply all 13 ran ABCD.
- Keep the score selector visible when switching from selected answer to correct + usable output. Use the same metric within a comparison.
- The context-control extension is deliberately simple, with only 12 base questions. All four supported long-context models selected every label; it does not establish unique Jev superiority or general long-context reasoning quality.
- Recorded combined Jev usage was $1.458954042, not total electricity/hardware/subscription cost. A failed request retains a small unknown-usage reservation. V2 measurement/follow-up window was about4h33m; ABCD candidate window about3h16m. Waiting, preflight, audit and report work are not included in those windows.
- The source is being published under MIT at https://github.com/theaiautomators/jev-arena. Third-party licenses still apply. No fine-tuning was done in these assessments.
- ABCD cases: Case explorer → ABCD support conversations. Raw text is local only; exact inputs, answer keys and model responses are clearly separated.
- Winnow memory check after the evaluations: Q8_0, about 12.90 GiB idle GPU-memory increase at 8K and 13.61 GiB at 64K. No predictions were repeated; this is not peak inference memory.
