# ABCD blinded audit: inspection record

All 33 flagged answer reviews across 21 questions were inspected. Issues include optional farewells, flexible action order, missing action identity, omitted retrieved policy, and policy-compliance judgments that differ from recorded continuation. Primary gold is unchanged; no human semantic audit was performed.

The frozen audit covered 118 unique case/answer pairs over all 76 selected questions: 61 correct, 36 incorrect and 21 ambiguous judgments. Twelve answer-level reference disagreements and 21 ambiguity flags produced 33 flags. They are sampled, correlated reviews, not an estimate of the entire suite error rate. No primary labels or scores were changed. Inspection is automated analysis, not a human audit.

## Method and attribution

Codex CLI 0.157.1 requested GPT-6 Astra. There were 27 successful batches plus one preserved usage-limit failure that graded no answers. Model identity and reference gold were absent from judge inputs; identical case/answer pairs were deduplicated. Observed model identifiers were not exposed. Saved usage totals are 1,539,565 input tokens (59,136 cached) and 15,468 output tokens (including 5,344 reasoning tokens). These are CLI usage records, not measured billed credits or cash. No purchase/reset was performed by this workflow.

## Diagnostic correction

Initial scenario-string retrieval coverage was 189/300 action and 582/900 route checkpoints. Fine-grained FAQ names and occasional scenario/dialogue differences made that diagnostic misleading. The separate correction uses the upstream actual step subflow annotation; terminal checkpoints inherit the last observed annotated procedure. Corrected coverage is **236/300 actions (78.67%) and 731/900 routes (81.22%)**. Forty-seven action and 149 route records change from diagnostic miss to hit; no hits become misses. This is post-execution analysis only and never affects retrieval, prompts, targets or model scores. The original summary is retained; its retrieval_diagnostic field is superseded by [the correction](abcd-retrieval-correction.json). Even the corrected annotation is not a human-verified measure of sufficient evidence.

## Every flagged question

### abcd-10124-15-full_handbook-action

**Policy versus recorded sequence**. The history contains the membership level and address but no membership-button outcome. The policy calls for membership before entering the address; the recorded next action is enter-details. A policy-repair answer and prediction of the recorded sequence differ. Keep the reference; the judge does not replace the source annotation.

Reference: `enter-details`. Audited answer/verdict: `membership` / correct.
Review IDs: `d61237998be136127c6d0dfb`.

### abcd-1021-11-retrieved_policy-action

**Action-history ambiguity**. A generic earlier action message does not expose which troubleshooting button was clicked. The supplied troubleshooting sections allow flexible ordering. Logging the earlier logout advice and choosing another option are not uniquely ordered; ambiguity does not make every offered button correct.

Reference: `log-out-in`. Audited answer/verdict: `log-out-in` / ambiguous, `notify-team` / ambiguous, `try-again` / ambiguous.
Review IDs: `19ebdd2227a549a436dbbda3`, `2bc524cdcd997fb4516cac3e`, `fe3959f4edadef118bb778b9`.

### abcd-10228-10-full_handbook-route

**Policy versus recorded sequence**. The refund method has been supplied, but the last agent turn asks for account ID. The handbook supports recording the method before entering that ID, while the recorded continuation is another agent message. The judge applies policy order more strictly than the actual dialogue; the exact next recorded turn is not uniquely entailed.

Reference: `retrieve_utterance`. Audited answer/verdict: `take_action` / correct, `retrieve_utterance` / incorrect.
Review IDs: `730a64921f1122974aa74b3f`, `a2c36088ca62115f7e15d531`.

### abcd-1655-42-retrieved_policy-action

**Repeated recorded action**. A promo-code-created outcome is already in history, yet the next recorded reference is another promo-code action. The judge reasonably objects to repeating it, but the conditional question explicitly says an action is due. This is reference/policy/conditional-premise tension, not evidence that the importer shifted the target. Preserve the repeated source event and gold.

Reference: `promo-code`. Audited answer/verdict: `promo-code` / incorrect.
Review IDs: `e8489bcfc02d70a7c334488a`.

### abcd-1822-11-retrieved_policy-route

**Scope ambiguity**. Password generation and sharing are complete, but the initial customer also wanted to check an order. A follow-up message or closure can be interpreted differently depending on whether the scope is password recovery or the entire request. Keep the recorded agent-message reference.

Reference: `retrieve_utterance`. Audited answer/verdict: `end_conversation` / ambiguous, `retrieve_utterance` / ambiguous.
Review IDs: `4742ace44d1c634443fa3872`, `df44196e342bd3de479e7ae5`.

### abcd-295-10-retrieved_policy-route

**Retrieval gap**. The five retrieved sections omit the shirt FAQ despite the visible shirt-care request. The judge lacks the relevant supplied procedure. This is a real retrieval miss even after correcting FAQ aliases; do not generalize ambiguity into credit for every route.

Reference: `take_action`. Audited answer/verdict: `take_action` / ambiguous, `retrieve_utterance` / ambiguous.
Review IDs: `3f3e05b0797c117235cbdda4`, `923af48aa8e51a553c0e2bfa`.

### abcd-312-14-retrieved_policy-route

**Missing prerequisite and metadata mismatch**. The observed billing dispute has no order ID before the next recorded action. The judge asks for missing purchase-validation information, while the source records another action. The hidden scenario says jacket FAQ, but the actual step annotation concerns billing. This also demonstrates why scenario-string coverage was a poor retrieval diagnostic. No hidden scenario field reached candidates.

Reference: `take_action`. Audited answer/verdict: `take_action` / incorrect, `retrieve_utterance` / correct.
Review IDs: `344498c097c7ee5dcf6dfa16`, `8603a3737c8e6ab80e1c3063`.

### abcd-3538-17-retrieved_policy-action

**Retrieval gap**. The supplied five sections omit Update Refund. That source procedure would support offer-refund after the additional item and previous refund amount; the visible substitutes do not uniquely determine it. Membership and enter-details are not automatically correct merely because the case is ambiguous.

Reference: `offer-refund`. Audited answer/verdict: `membership` / ambiguous, `offer-refund` / ambiguous, `enter-details` / ambiguous.
Review IDs: `2877cbbed4f9e03fde51acee`, `7448143d57d143018d16d284`, `ab8b2c9cc3bc77338dd0bf19`.

### abcd-3619-5-full_handbook-action

**Delayed action logging**. The agent gave logout advice and the customer tried it, but the required corresponding button is not yet recorded. The reference logs logout next. General troubleshooting order is flexible, but that does not make the alternative instructions action uniquely correct or negate the delayed button requirement.

Reference: `log-out-in`. Audited answer/verdict: `instructions` / ambiguous.
Review IDs: `b97703d7154f75228e82ea81`.

### abcd-3689-13-retrieved_policy-route

**Policy versus recorded sequence**. The jacket FAQ is open and the user asks about warmth. The judge expects the missing Select Answer button; the reference continues natural-language explanation. A policy-compliance judgment is different from matching this recorded next turn.

Reference: `retrieve_utterance`. Audited answer/verdict: `retrieve_utterance` / incorrect.
Review IDs: `e48018b0ba00d6f6cadd4280`.

### abcd-433-17-full_handbook-action

**Flexible order; unsupported proposed repeat**. The procedure allows several troubleshooting orders. The proposed search-faq repeats the immediately preceding FAQ search and is outside the listed next troubleshooting actions. The judge itself flags that weakness. Ambiguity is not blanket approval of this answer.

Reference: `instructions`. Audited answer/verdict: `search-faq` / ambiguous.
Review IDs: `25d8ac7a97dde132dd5acf5e`.

### abcd-4331-11-retrieved_policy-action

**Delayed action logging and flexible order**. The history contains slow-site diagnostic and logout advice without their button records. The policy requires both language and clicks while allowing order flexibility. The recorded logout action is defensible; notify-team or instructions are not uniquely licensed as the next recorded action.

Reference: `log-out-in`. Audited answer/verdict: `instructions` / ambiguous, `log-out-in` / ambiguous, `notify-team` / ambiguous.
Review IDs: `0c630a5dc1044172e36e0af2`, `6b31edc6819a41d10403bae5`, `a14622f9d125a2102a9442bc`.

### abcd-456-13-full_handbook-route

**Terminal versus repair ambiguity**. The observed dialogue has explicit farewells but omitted earlier shipping checks. The terminal reference matches the frozen end-of-dialogue construction. The judge questions whether omissions should be repaired; the assessment measures recorded continuation, not retrospective compliance repair.

Reference: `end_conversation`. Audited answer/verdict: `end_conversation` / ambiguous.
Review IDs: `e6c3bbf76c94a8212339e4b5`.

### abcd-5691-16-retrieved_policy-route

**Retrieval gap**. The return-credit billing procedure is absent from retrieved policy. The history has a silver membership outcome, after which the correct source policy would call for explanation rather than a credit update. The generic supplied procedures leave the judge uncertain.

Reference: `retrieve_utterance`. Audited answer/verdict: `retrieve_utterance` / ambiguous.
Review IDs: `bc42304c13890da36f6f45a6`.

### abcd-6080-22-retrieved_policy-route

**Judge overreach on a synthesized terminal**. The full observed dialogue has finished with farewells. A required earlier shipping-status click is missing, but the judge treats retrospective repair as the next step. For the frozen terminal construction, end is the faithful source reference. This disagreement is not a reason to relabel it.

Reference: `end_conversation`. Audited answer/verdict: `end_conversation` / incorrect.
Review IDs: `709fe532784be08eb3496e46`.

### abcd-6395-22-retrieved_policy-route

**Optional farewell**. The promo code has been shared and the customer declines further help. The source contains an additional agent farewell, while the judge accepts ending immediately. Both describe a plausible conversational close; the primary score stays recorded-next-step agreement.

Reference: `retrieve_utterance`. Audited answer/verdict: `end_conversation` / correct.
Review IDs: `4f581488419f5db41d8c7b74`.

### abcd-6942-4-full_handbook-route

**Multiple permissible next steps**. The customer supplied a name and mixed refund-status/update requests. Account lookup is available, while another message can clarify the refund reason. The judge marks lookup correct but the reference message ambiguous; those asymmetric labels do not establish a unique valid next step.

Reference: `retrieve_utterance`. Audited answer/verdict: `retrieve_utterance` / ambiguous, `take_action` / correct.
Review IDs: `1221d5d63f582d10ca28abae`, `c76d2eb445c4d546ff3d7841`.

### abcd-7688-19-retrieved_policy-route

**Missing or ambiguous amount**. The customer answers an extra-charge question with a grand total. The judge reasonably seeks clarification, while the recorded reference proceeds to an action. Delexicalized amounts also remove numeric detail. Preserve the recorded target; do not equate it with guaranteed policy compliance.

Reference: `take_action`. Audited answer/verdict: `take_action` / incorrect.
Review IDs: `a12d9f08a7565ae33f6454d8`.

### abcd-7859-7-full_handbook-route

**Multiple permissible next steps**. The supplied name enables account lookup, but the refund reason is missing and could be requested. The handbook does not fully order those steps. Both audited route answers remain uncertain as predictions of the exact next turn.

Reference: `take_action`. Audited answer/verdict: `take_action` / ambiguous, `retrieve_utterance` / ambiguous.
Review IDs: `66b6dca0953e500eef572d43`, `e5ebbbd16f5759a3baa8b422`.

### abcd-9760-10-retrieved_policy-route

**Action-history ambiguity**. Generic troubleshooting action text hides which button was used, and the last agent message asks the user to try another site. Without action identity and fixed click/message order, another message versus a click is underdetermined.

Reference: `take_action`. Audited answer/verdict: `retrieve_utterance` / ambiguous.
Review IDs: `c25e2da14eceffdaf6941af7`.

### abcd-9811-12-full_handbook-route

**Optional farewell**. FAQ lookup, selection and explanation are complete; the customer declines further help. The recorded next turn is a final agent message, while ending immediately is pragmatically plausible. Preserve the source label and qualify what the accuracy measures.

Reference: `retrieve_utterance`. Audited answer/verdict: `end_conversation` / correct.
Review IDs: `da4db03ab77d098155b04016`.

## Interpretation

Describe these scores as agreement with recorded next steps. A handbook-compliant next step is not always the recorded one, and an observed next step is not always handbook-compliant. The audit does not prove a revised winner under semantic acceptance. No alternative acceptance score was created. Missing policy and ambiguous action text are real limitations of this frozen adaptation. The easy synthetic audit does not establish general long-context reasoning superiority.
