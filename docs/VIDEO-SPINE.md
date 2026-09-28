# Video spine: what running the experiment taught us

The spoken draft is [VIDEO-SCRIPT.md](VIDEO-SCRIPT.md). The supporting claim ledger, new analyses, exact cases and source boundaries are in [VIDEO-ANALYSIS.md](VIDEO-ANALYSIS.md). Keep the existing `VIDEO-SCRIPT.txt` working draft intact.

The story is: local decision models are credible options, but choosing one requires understanding its task, interface, input strategy, output and workflow. Arena earns its place in the video by letting us inspect those differences.

## Sequence

| Beat | Question it answers | What to show | Point to land |
|---|---|---|---|
| Intro | How close are local models to Jev, and when should I use them? | Arena overview, quick flashes of news/capacity/long-input findings | Promise learnings from the experiment. Use 13 setups and a 7,671-case suite. |
| Models | What did we actually compare? | Grouped roster; highlight Winnow 12B, Decider 4B, Laya 421M | Thirteen entries include related checkpoints and controls. |
| How they work | How can an LLM become a decision model? | Input + question + choices → scores/answer; fine-tune, scoring head, encoder, JSON paths | Similar interfaces can hide different implementations. We did no fine-tuning. |
| Sample questions | What counts as a decision here? | Three short reveals: explicit policy, familiar classification, relevance/77 intents | Let viewers understand an input before revealing its answer. |
| Headline | Are any local profiles competitive? | Same 4,635-question table; Jev/Winnow/Decider; short serial timing | Winnow is 29 labels behind Jev. Establish the shortlist, then leave the aggregate. |
| Lesson 1: task fit | Does that rank tell me which model to deploy? | Results → News; XNLI; task-mix sensitivity; SciFact negatives/positives | Laya wins news labels; mix changes ranks; 90.6% can find zero relevant documents. |
| Lesson 2: capacity | Can the interface accept my actual problem? | 77 banking choices; Plumb/SemIf 16; Winnow 64; Nimble 8K | Unsupported inputs are different from bad decisions. Name exactly which model hit which limit. |
| Lesson 3: input strategy | Will the short-request speed carry over? | Full-handbook versus retrieval timing, then conditional action quality | The local speed advantage reverses with long input; retrieval changes both speed and quality. |
| Lesson 4: inspect correctness | Does a high score mean a useful answer? | Decider label/strict toggle; AG News basketball case; optional confidence chart | Output validity and reference quality both matter. A benchmark mismatch can be reasonable. |
| Lesson 5: workflow | Does choosing an action mean knowing when to act? | ABCD action versus combined task, message/action checkpoint split; warehouse replay | Test the controller and useful completion, not only the isolated choice. |
| Shortlist | What would I investigate next? | Job → candidate → thing to validate | Short local: Winnow/Decider. Narrow classification: Laya. Full-handbook action selection: Jev. Retrieval makes Nimble feasible. |

## Filming rhythm

The first four explanatory beats should take roughly a quarter of the video; spend most of the time on the five lessons. Each lesson follows one observed result into the reason it matters. Avoid reading all thirteen rows or explaining every metric. The Markdown script is a full spoken draft with optional shot directions; timing depends on how long examples and replays are held.

Start the samples with `fresh-v2-test-01-000-choice`: the applicant is ineligible, approval is signed, and the explicit policy says Stop. The explorer now shows the choices and has a reveal button. Use the type selector rather than sequential paging.

For the news result, keep “Same supported questions” and “Selected answer” visible. For capacity, switch to “Each model's supported questions” so unavailable cases are visible. For the Decider output gap, also use the supported set and explain the 5,671 denominator. These are intentional scope changes, not interchangeable percentages.

For the reference-quality example, use `classification-ag news-450`, then compare Laya and Jev. The source file itself labels this basketball article World. Do not claim this one example reverses the measured news ranking or proves benchmark memorization.

For the speed reversal, use routing medians consistently: Jev 358/265 ms, Decider 1,895/144 ms, Winnow 2,847/320 ms for full/retrieved policy. Then explicitly switch the subject to conditional action quality: Winnow 200/300 → 229/300. Retrieval overhead is outside those model-request medians.

## Boundaries that belong beside the relevant shot

- 7,671 planned cases/profile; 5,671 public or rule-derived references; 2,000 AI-teacher cases reported separately; 4,635 common supported references in the headline.
- Thirteen configurations include three related Laya checkpoints and a deterministic control. “Thirteen independent AI models” is inaccurate.
- The fixed policy templates and translated questions are correlated. Post-hoc task slices and task-mix changes are descriptive analyses.
- Original strict scores, predictions, failed requests and answer keys remain unchanged.
- The 500 Winnow banking failures came from Arena's incorrect capability declaration. The pinned server supports 64 choices; no reduced shortlist was tested.
- ABCD is a separate five-profile follow-on with 300 conversations. Keep its scores outside the thirteen-profile total.
- Hosted network time, local hardware, runtime, precision and caching differ. No maximum-throughput or architectural speed claim.
- Memory readings are after loading, not peak inference VRAM or minimum RAM. Winnow's whole-device measurement differs from the PyTorch allocator readings.
- Support-step agreement is not customer-resolution success. Automated audits are not human validation.
- The unverified “popularity skyrocketing / new competitors every day” lead is replaced by the observable existence of competitors. Preserve the user's practical question and hosting motivation.

## Files and app route

[Script](VIDEO-SCRIPT.md) · [Claim ledger and new analysis](VIDEO-ANALYSIS.md) · [Original Arena evidence](RESULTS.md) · [Separate support evidence](ABCD-RESULTS.md)

App: Results → question type/model → Open these questions or Inspect. Case explorer: type, model, outcome, answer format, global search and page jump. Answers and probabilities can be revealed separately for filming. Do not start a new evaluation while recording saved results.
