# What builders should learn from Arena

The revised [Markdown script](VIDEO-SCRIPT.md) and [video analysis](VIDEO-ANALYSIS.md) expand these findings with paired news disagreements, task-mix sensitivity, relevant-document recall/precision and a source-checked news reference concern. In the app, Results now filters by question type and model and links directly to cases.

The useful conclusion is not that one model wins everything. Local decision models can be competitive and fast, but task fit, input limits, output validity and complete-workflow behavior determine whether they are useful in an application.

All numbers below describe saved profiles, not every release or all deployments. No new predictions were made for this analysis. Task breakdowns were calculated after the run and are descriptive, not corrected significance tests.

## 1. Start with the actual decision, not the leaderboard

On the same 4,635 supported answer-key questions, selected-label agreement was Jev 95.23%, Winnow 94.61%, Decider 94.46%, Nimble 92.34%. That is a useful broad shortlist. It is not proof that the first model is best for your company's task.

The task breakdown changes the story:

| Job | Observation on the shared questions | Builder implication |
|---|---|---|
| News classification | Laya 92.2%, Decider 90.0%, Jev 88.2% on the same 500 articles | A small encoder can be a good starting point for a narrow classifier. Test your own labels and language. |
| Sentiment | Jev 96.4%, Winnow 96.2%, ModernBERT NLI 95.8% on 500 reviews | A compact classification model can be competitive without a large decision model. These small differences are not a general superiority claim. |
| Multilingual entailment | Decider 84.0%; Jev and Nimble 81.4% on 500 translated examples | Test the actual languages and task. A model named “multilingual” is not automatically the best multilingual choice. |
| Public decision questions | Plumb 92.3%, Jev 90.3% on the shared 195-question JevBench subset | Broad aggregate rank can hide a useful specialty. Public benchmark exposure is unknown; this subset is not the entire JevBench suite. |
| Explicit policy rules | Jev and Winnow 100% on 1,440 generated rules, and 100% on 1,000 changed-input cases | Strong controlled rule following; eight repeated templates do not prove arbitrary real-world policy competence. |
| Support action selection | Jev full-handbook selected-label agreement 78.67% vs Winnow 66.67%; retrieval changes these to 75.33% and 76.33% | Choose between full policy and retrieval experimentally. Different models respond differently to context. |
| Act/speak/finish plus action | Winnow leads the balanced ABCD combined task; Jev does better on true action checkpoints | Deciding whether to act is a distinct problem from choosing an action when told one is due. |

The shared score is case-weighted. Generated policy tests and their variants contribute 2,440 of 4,635 questions. SciFact also contains 90.6% “not relevant” answers: a first-option baseline already achieves 90.6% accuracy. Use retrieval ranking and positive-class performance instead of treating a high aggregate percentage as sufficient evidence.

## 2. Capacity is an eligibility check

Count the full input: instructions, policy, conversation history, options and runtime wrappers. Also count all the choices the application needs.

- Plumb and the tested SemIf interface accept 16 choices.
- Winnow's pinned native server accepts 64. BANKING77 has 77; those requests cannot be used to judge its reasoning.
- ABCD supplies all 30 actions, without giving a model an easier shortlist.
- Nimble's pinned release supports 8K inputs and could not take the complete ABCD handbook.
- Jev supports a 32K state/question input. ABCD also used Decider at 32K, Qwen at a configured 32K including its output budget, and Winnow at 64K. Winnow was not tested to its full ceiling.
- Many 8K figures in the original Arena setup were chosen serving limits, not architectural limits. Qwen's native configuration is larger than its tested setting.

Jev is therefore not uniquely long-context. Four supported profiles selected all answers in our easy synthetic control. That control was too simple to rank their long-context reasoning.

An unavailable case is not a wrong answer. Preserve it as a capacity limitation, and compare quality on identical supported questions.

## 3. Benchmark speed at the input length you will deploy

Repeated short-input timing blocks put Decider, Nimble, Plumb and Winnow at roughly 47–59 ms median, versus hosted Jev at roughly 245 ms. These were serial calls, not maximum-throughput measurements.

With the full ABCD handbook, median routing requests were roughly Jev 358 ms, Qwen 1,570 ms, Decider 1,895 ms and Winnow 2,847 ms. Retrieved policy reduced those to Jev 265 ms, Qwen 468 ms, Decider 144 ms and Winnow 320 ms; Nimble was 240 ms.

The important lesson is the reversal, not an architectural speed claim. Local versus hosted hardware, quantization, runtimes, prefix caching and network travel differ. Jev's parameter count and backend hardware are undisclosed; slower short requests do not prove it is a larger model.

For real-time applications, measure tail latency, cold start and concurrent load on your own system. We measured serial request medians and tails, load times and toy 500 ms deadlines; we did not validate production throughput.

## 4. A correct answer must also be usable by software

Decider selected the right label on 92.31% of all 5,671 original answer-key cases, but passed the correct-answer-plus-output-format check on 83.79%. The gap includes probability-sum failures under Arena's chosen tolerance.

That is a different problem from wrong choices. A builder needs both measurements. Validate output, log failures and choose a deliberate fallback policy. We did not silently repair failed outputs or prove that every failure has a safe repair.

Confidence also needs checking. “80% confident” should mean about 80% correct across comparable decisions. Do not adopt one model's confidence threshold for another without validation.

## 5. Test the workflow, not only isolated answers

In the small warehouse demo, Jev completed 20/20 untimed scenarios, Winnow 19/20, Nimble 17/20 and Decider 9/20. All four completed 20/20 ticket scenarios. These are separate from the static benchmark.

Some other models sent every ticket to Review. That avoided particular violations but unnecessarily deferred useful work. A safe-looking output is not necessarily a productive automation. Repeated invalid moves can also compound the same mistake.

Replay tabs are two task types, with seeds, model selection and deadline settings—not two benchmark questions. Playback uses saved responses and spends nothing.

## 6. Deployment choices depend on cost, privacy and engineering

Local weights allow deployment within your infrastructure, but bring GPU memory, serving and maintenance costs. Hosted Jev avoids that local serving work, but network access and the service's data-handling terms must fit the application. This evaluation does not certify a provider's privacy or compliance terms.

Our loaded GPU allocations were about 7.8 GiB for the tested 4B BF16 profiles, 17.5 GiB for Nimble, and 1.2–1.6 GiB for the small encoder profiles. These are allocated memory after load, not peak inference VRAM or system RAM. Winnow's runtime did not provide a directly comparable allocator figure. Long inputs and concurrent requests need additional headroom.

Use the model guide for each exact base, weights/license, repository age, measured load allocation and saved revision. A repository creation date is not necessarily its public release date.

## How to explain the dashboard

| Original term | Plain-language meaning |
|---|---|
| Strict accuracy | Correct answer AND usable output under Arena's checks. |
| Matched strict | The same check, on identical supported questions for every model. |
| Matched labels | Correct selected answer on those identical questions, ignoring probability-format failures. This existing comparison is now the overview's “Answer accuracy.” |
| P50 latency | Typical response time: half faster, half slower. |
| Valid coverage | Usable outputs divided by every planned case, regardless of correctness. |
| Teacher labels | Answers supplied by another AI model or average of AI judgments. Agreement is shown separately from accuracy. |
| Perturbation checks | Change the wording, distractions, choice order or decisive facts and see whether behavior changes appropriately. |
| Reliability plot | Stated confidence versus actual correctness. Below the ideal line means overconfidence. Empty groups contain no evidence. |

The 7,671 cases comprise 5,671 public/rule-derived answer-key questions and 2,000 teacher questions. Main accuracy is entirely calculated against saved answer keys; Astra contributes no weighted share to it. Astra's 879 answer reviews across 300 selected v2 questions check ambiguity and questionable references. They are a separate automated audit, not human validation.

JevBench provides 231 public cases. Other Arena components come from SST-2, AG News, BANKING77, XNLI, MASSIVE, SciFact, typed-decisions and our generated fixtures. The combined suite is broader than public JevBench but is not automatically more representative of any one business.

ABCD belongs alongside these results in the dashboard, but should not be folded into the original total. It was a later experiment with five profiles, different input conditions and different decisions. Pooling it would change weights after observing results and give only five models extra questions. Keep the evidence together and the scores distinct.

The former Impress button started a fresh run, not a replay; a Full run could take hours and incur API usage. New results receive a new run ID; old runs are not erased. Run controls are now on a separate page and the start action is explicitly named.

## Evidence

[Original v2 results](RESULTS.md) · [ABCD results](ABCD-RESULTS.md) · [Task breakdown](evidence/builder-task-breakdown.json) · [Model guide](evidence/model-guide.json) · [V2 review](evidence/ASTRA-V2-REVIEW.md) · [ABCD review](evidence/ASTRA-ABCD-REVIEW.md)

The revised viewer is a presentation layer. Original strict scores, raw attempts, frozen protocols and previously exported reports remain unchanged.
