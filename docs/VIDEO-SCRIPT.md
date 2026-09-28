# Jev Arena: what we learned from testing local decision models

Recording draft, about 2,080 spoken words (14–16 minutes before extended demonstrations). Spoken paragraphs below; blockquotes are filming directions, not narration. Exact evidence and scope are in [VIDEO-ANALYSIS.md](VIDEO-ANALYSIS.md). The earlier working text in `VIDEO-SCRIPT.txt` is preserved.

## Intro

TypeSafe's Jev has some serious competition.

Models like Winnow, Laya and Decider let you run AI decisions on your own hardware. You can host them yourself, keep inference completely inside your own infrastructure, and build them directly into your software.

But how close are they really to Jev? And which ones should you actually use?

To find out, I built this Jev Arena and compared 13 model setups against a suite of over 7,000 decisions.

I wanted to know how often they got the answer right, how quickly they responded, and what it would take to run them locally.

And there were some interesting findings and tradeoffs. A tiny model topped one of our tests. Some models couldn't even accept the number of answers we needed. And the speed advantage of running locally changed when we gave the models a much longer input.

So let's get straight into it.

> Show Arena, then a quick sequence: Laya at the top of News topics; BANKING77's 77 choices; short-input versus full-handbook timing. Keep the 7,671 suite size separate from the 4,635-question shared score. Avoid “each answered 7,000”: some requests were unsupported or failed. The original “popularity skyrocketing / every day” opening needs independent growth evidence; this draft keeps the premise without inventing that evidence.

## The models, and what a decision model actually does

Here are the setups I ran.

There is hosted Jev. Then Winnow, Decider, Plumb, Nimble and CLM. I also included SemIf, three versions of Laya, a ModernBERT classifier, and a regular Qwen model asked to answer in JSON.

The thirteenth entry is a simple control. It always picks the first option. It isn't an AI model, but we'll see why it is useful.

> Show the full roster grouped by approach, not thirteen profile pages. Hold on Winnow 12B, Decider 4B and English Laya 421M as the size contrast. Evaluated revisions are pinned; Decider here is v2, not the newer v2.1. The three Laya entries are related checkpoints.

The common interface is simple. Give the model some information, ask a question, and supply the allowed answers. Which team should get this ticket? Is this action allowed? Which document is relevant?

A normal language model can write the answer as JSON. Another approach is to score the possible answers directly. For example, the model might score Billing, Technical Support and Sales, and your software takes the highest-scoring option.

Some decision models start with an existing language model and fine-tune it on those choices. Winnow builds on Gemma; Decider builds on Qwen. Their decision interfaces can read scores for the allowed answers instead of generating a paragraph.

But that isn't how every entry works. SemIf uses scores from an existing model without a new decision fine-tune. CLM learns small scoring heads on a frozen language-model backbone. Laya uses a much smaller text encoder with a decision head.

So these models can have a similar interface while doing quite different things underneath. We did no fine-tuning in this experiment. We tested the saved releases and serving settings shown here.

> Simple diagram: input + question + choices → model → selected choice and, where available, option probabilities. Below it, show three routes: generative JSON; LLM-based option scoring; encoder/head scoring. Do not imply that Laya is a compressed Jev, that every model uses reinforcement learning, or that probabilities guarantee correctness. Architecture sources: [Winnow](https://huggingface.co/EldanRing/Winnow-12B), [Decider](https://huggingface.co/Mapika/decider-4b), [SemIf](https://github.com/TheoLeeCJ/SemIf-OpenJev), [CLM](https://huggingface.co/Contrastive-LM/CLM-v0.1-8B), [Laya](https://huggingface.co/convaiinnovations/laya).

## What we asked them

Let me show you what a few of these decisions look like.

This first one is a policy question. The request is ineligible, but somebody has signed the approval. The rule says to stop if it is ineligible. Should the system proceed, review it, or stop?

The answer is Stop. The approval doesn't override that first condition.

> Case explorer → Explicit policy rules → Workflow permissions. Search `fresh-v2-test-01-000-choice`. Show the input and three options, pause, then reveal the saved reference and responses.

Then there are familiar classification jobs: is this review positive or negative, and which of these four categories describes a news article?

Other questions ask whether one statement follows from another, across five languages. We also ask whether a document contains relevant evidence for a claim, and which of 77 banking intents matches a customer's request.

> Use the question-type selector to jump between Sentiment, News topics, XNLI, SciFact and Banking intents. Show one input and its choices at a time. No scrolling through hundreds of JSON records; no wall of thirteen probability distributions.

There were 7,671 cases in the suite for each setup. Two thousand compare against answers supplied by other AI models, so I kept that agreement separate from accuracy.

For the headline comparison, I used the same 4,635 answer-key questions that every setup could support. I'll explain why some questions drop out in a moment.

The scores come from comparing the saved answers in code. A separate AI audit checks a sample for problems; it doesn't contribute a weighted share of the headline score.

## The headline, briefly

On that shared set, Jev matched 95.23% of the answers. Winnow was at 94.61%, and Decider was at 94.46%.

That puts Winnow just 29 answers behind Jev out of 4,635.

On our repeated short-input timing tests, Winnow was around 56 milliseconds and Decider around 47. Hosted Jev was around 245, including the network trip. The local models ran on an RTX 5090, with one request at a time.

So there are local options worth taking seriously. But those numbers leave out most of what I would want to know before choosing one.

> Overview: show only the top rows and timing context. Keep this beat brief. These are selected-answer scores, not the stricter correct-plus-usable scores. The timing figure is the median of three block medians, not the per-task Quality P50 shown in Results.

## Lesson 1: the overall winner may not fit your job

Watch what happens when I change the question type to news classification.

English Laya moves to the top. It matched 461 of the 500 news labels, compared with Jev's 441. That's 92.2% versus 88.2%, from a model with about 421 million parameters.

I checked where they disagreed, too. Laya got 34 answer-key labels that Jev missed. Jev got 14 that Laya missed. So the difference isn't simply that Laya answers every question Jev can answer, plus a few more.

Switch to multilingual entailment and the leading model changes again. Decider matched 84%, compared with Jev's 81.4%.

That is why I'd shortlist a model against the particular job I need. A small classifier can be useful even if it looks weak in the overall table.

> Results → News topics → Compare all profiles → Same supported questions → Selected answer. Then XNLI. Keep the 500-question denominator visible. These are descriptive sample results; XNLI includes related translations.

The overall table also depends on how we built the test. More than half of the shared questions are our generated policy tests and variations of them.

When I remove those as a separate analysis, Decider and Jev are just two answers apart on the remaining 2,195 questions. I haven't replaced the original score. I've changed the mix to see how much the conclusion depends on it.

And there is an even clearer example in document relevance. Our simple first-option control scores 90.6%. It does that by saying every document is irrelevant.

It misses all 47 relevant documents.

Jev finds 40 of those 47, but also incorrectly marks 25 irrelevant documents as relevant. Those two error counts tell me much more about whether I can use it than one big accuracy number.

If I'm building search, I need to decide how much I care about missing useful evidence versus passing through irrelevant material. If I'm routing tickets, I need to understand the expensive misroutes. The score should reflect the job.

> Show the post-hoc task-mix comparison from What we learned, then SciFact's 453 negative / 47 positive split. A small two-column graphic can show “relevant documents found” and “irrelevant documents passed through.” Do not present the task-mix sensitivity as a new primary leaderboard.

## Lesson 2: check whether the model can accept your decision

The number of choices sounds like a minor detail until it stops the whole request.

Plumb and the SemIf interface we tested accept 16 options. BANKING77 has 77 possible intents. Those setups can't directly answer that question with every option supplied.

Winnow's native server has a different limit: 64. Arena initially advertised the wrong limit for it, so all 500 of its banking requests failed.

That was a capability-discovery mistake in the harness. It wasn't evidence that Winnow misunderstood 500 banking messages.

You could build a first stage that narrows 77 intents to a shortlist. But that creates another decision that can go wrong. The correct intent might never reach the final model. We didn't test that alternative pipeline here.

Input length creates the same problem. Nimble's pinned release has an 8K input limit. It couldn't take the complete support handbook in our next experiment.

Other 8K settings in the first run were serving choices, rather than the models' maximum capacities. So check the exact release and server settings, and count the whole input: instructions, policy, conversation and choices.

> Results → Banking intents → Each model's supported questions. Show Plumb/SemIf unavailable and Winnow's historical 500 failures. All these cases are excluded from the shared headline for everyone. Then Model guide → Nimble. Context limits in the comparison are profile-specific, not blanket claims about all versions.

## Lesson 3: a short-input speed win can reverse

This was one of the most useful parts of the experiment for me.

The local contenders were much faster on short requests. But a support application may need a lot more information than a short routing question.

So I ran a separate test with five of the profiles, using 300 held-out customer-support conversations. In one condition I supplied the complete handbook. In the other I retrieved five policy sections from the conversation so far.

The full handbook made the input roughly twenty thousand tokens long. Most of that length was the policy, rather than an unusually long customer conversation.

With that input, Jev's typical routing request was around 358 milliseconds. Decider was around 1.9 seconds. Winnow was around 2.85 seconds.

The local speed advantage had reversed.

When I supplied the retrieved policy instead, Decider came down to about 144 milliseconds and Winnow to 320. Jev was around 265.

So “this model responds in fifty milliseconds” wasn't a useful description of every task I might give it.

Retrieval also changed answer quality. When we told Winnow an action was due and asked it to choose that action, it matched 200 of 300 recorded labels with the full handbook. With retrieved policy, that rose to 229.

Giving it less text helped on this task. But retrieval can also leave out the policy you need: our top-five retrieval included the annotated procedure at 236 of those 300 action checkpoints.

I'd test the complete input strategy alongside the model. Full policy and retrieved policy are two different systems, with different failure points.

> Support conversations: full handbook versus retrieved policy. Use route timing throughout the speed comparison, then explicitly switch to conditional action selection for quality. The 29-answer Winnow improvement is a different result from the 29-answer Arena headline gap. Keep the two experiments separate.

We don't know Jev's model size or backend hardware, and these deployments use different runtimes, precision and caching. These timings describe what I measured. They don't prove why one architecture is faster, or how much traffic it can handle concurrently.

## Lesson 4: inspect what “correct” means

There are two checks I want to keep separate: did the model choose the reference answer, and did it return something my software could use?

Across the original answer-key set, Decider selected a matching answer about 92.3% of the time. But the score fell to 83.8% when we also required its output to pass Arena's checks.

Some of those failures came from probability totals falling outside the tolerance we set. That is a different problem from choosing the wrong label, but it still matters if my application relies on those probabilities.

I'd log both, and decide explicitly what to do with invalid output. I wouldn't silently count it as a correct, usable response.

> Results → All question types → Decider → Each model's supported questions. Switch Selected answer to Correct + usable output, keeping 5,671 visible. Arena's probability-sum tolerance is 0.0001; it is a harness contract, not a universal vendor requirement. Qwen's label-only JSON doesn't face that probability-sum check.

We also need to inspect the reference answer itself.

Remember Laya's news result? One of the cases it wins against the answer key is an article about a basketball match. The dataset labels it World. Jev says Sports; Laya says World.

Reading that article, I would question the reference before calling Jev's answer a mistake.

That doesn't tell us the corrected winner. I haven't relabelled the whole dataset. It tells us that matching the benchmark's categories and making the decision we want are not always the same thing.

> Case explorer → News topics → All model responses → search `classification-ag news-450`. Show World as the saved reference and the model labels. The saved input and label were checked against source row 450 of the pinned AG News test file. This is an editorial concern about the reference, not a completed human audit or evidence of training contamination. Leave frozen labels and scores unchanged.

The same applies to confidence. A model giving an answer a high probability doesn't remove the need to check its errors on your own data.

## Lesson 5: choosing the right action isn't the whole workflow

For the support test, we asked two different questions.

One says: an action is due; which of these 30 actions should happen?

With the full handbook, Jev led that comparison at about 78.7%, versus Winnow's 66.7%.

The broader question is: should the system take an action, speak to the customer, or finish? And if it should act, did it choose the right action?

Winnow led that combined task. It was much better at matching when the recorded agent spoke to the customer. Jev was better at the action checkpoints.

So a useful tool selector isn't automatically a good controller for the whole conversation. You need to test the decision about when to act as well as which action to choose.

> Full handbook: conditional action → combined task. Combined label agreement: Winnow 616/900 (68.44%), Jev 574/900 (63.78%). For the explanation, show action checkpoints separately: Jev 221/300, Winnow 141/300; message checkpoints: Jev 69/300, Winnow 185/300. The combined set is deliberately balanced, including synthesized endings.

We saw another version of that in the small workflow demos. Decider looked strong on individual questions but completed only nine of twenty untimed warehouse scenarios. Jev completed twenty, and Winnow nineteen.

And some setups sent every support ticket to Review. That can avoid certain violations while leaving the automation with no useful work done.

These are small controlled workflows, and the support scores compare against recorded steps. There can be more than one acceptable next step in a real conversation. They aren't live customer-resolution rates.

But they give us failures to investigate that we'd never see in the headline table.

## What I would shortlist

For short decision requests that need to stay local, Winnow and Decider are the two I'd investigate first from this run. Decider uses less memory in our tested settings; Winnow performed better on the combined support task and on output validity here.

For a narrow classification job, I'd also try a much smaller model like Laya. Its news result earns it a place in that evaluation, even though I wouldn't choose it from this evidence to control an entire workflow.

For full-handbook support action selection, Jev was the strongest measured option here, and its hosted requests were fast. With retrieval, local options became more practical, including Nimble, which couldn't accept the full handbook.

> Show a shortlist by job, with the pinned version and input strategy. Laya's recorded load allocation was about 1.57 GiB; Decider's about 7.93 GiB. Winnow's separate whole-device idle-load probe was about 12.90 GiB at 8K, 13.61 GiB at 64K. These measurement methods differ and none is peak inference memory or minimum system RAM.

The point of building Arena was to get from a rank to a decision I could actually use.

Choose the task, check the input limits, measure the complete request, inspect the disagreements, and test whether the workflow finishes useful work.

That's what I learned from running this experiment. The app lets you open the individual questions and compare the models on the part of the workload you actually care about.
