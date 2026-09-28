# Reference cautions

The primary results use frozen labels and a fixed output contract. They measure agreement under those rules; they do not prove that every natural-language reference is unambiguous.

## Routing ambiguity found during adversarial review

A generated ticket can have `topic=payment` (or onboarding) and `service unavailable=yes`. The policy says payment routes to Billing, outages to Engineering, and onboarding to Success. The executable oracle routes by topic and treats unavailability as urgency. The prose does not explicitly state that separation or routing precedence. Engineering is therefore a plausible alternate reading for these cases.

The reviewer identified **50 Full records**: 19 Fresh and 31 Robustness, with 31 distinct state strings. They are 0.88% of the 5,671 reference records before capability exclusions. Two occur in the 120-case Demo, and they account for two of Jev's five strict-score misses. They must not be presented as unambiguous Jev reasoning failures.

This subset was identified after inspecting the completed Demo. Its Full IDs were selected using text and metadata before reviewing Full outcomes. The exact rule and all IDs are in [reference-cautions.json](reference-cautions.json). These are potential ambiguities, not a declaration that the labels are wrong.

Keep the labels and original primary scores unchanged. Any table excluding this subset is **post-hoc sensitivity analysis**, visibly separate from the primary result. It must include the remaining denominators. Do not select a preferred exclusion merely because it changes the ranking. A future fixture version can clarify routing precedence, receive human review, and run as a new experiment.

## Output-contract sensitivity

Primary accuracy requires a valid output and the selected reference label. The fixed probability-sum tolerance is 1e-4 with a floating-point boundary guard. Rounded native vectors can fail this rule even when the selected label is correct. That is a failure of Arena's chosen contract, not necessarily a reasoning error or a violation of a vendor's documented API guarantees.

The dashboard separately shows label-only sensitivity on the same supported reference cases, together with invalid-output counts and calibration denominators. Those diagnostics do not repair or replace the main metric. Probability calibration only includes valid probability vectors, so a smaller denominator matters.

Astra's agreement with a frozen reference does not settle a plausible human interpretation. The formal controls and sample audit are not a substitute for human semantic review.

## Additional ambiguities found in the completed Full judge audit

At `fresh-test-03-059-noul`, the state requests a read, says Reader can read, assigns an approval requirement to Editor, and records approval as absent. The question asks whether approval is missing for the requested action. The reference interprets this as required approval and answers no; Jev answers yes. Astra graded both answers correct using different readings, while marking neither as needing human review. This is a wording ambiguity and inconsistent grading criterion, not a definitive finding that the model or reference is wrong.

The same pattern occurs in 17 Full Fresh records, including one Demo record (`fresh-test-03-001-noul`); no Robustness records match. Reproduce the screen with family `Tool selection`, question kind `noul`, and state containing both `needs read access` and `Approval present=no`. This was identified after inspecting Full outcomes. No new exclusion or label change is applied, and the earlier 50-case routing sensitivity is not an exhaustive semantic correction.

The other reference disagreement, `xnli-4703-ar`, admits literal versus pragmatic readings of a guitar/banjo preference statement. The review found no demonstrated translation-adapter defect. Ten ambiguous judge verdicts cover seven teacher cases, already excluded from main accuracy. Full details and the judge's conflicting rationales are discussed in [ADVERSARIAL-REVIEW.md](ADVERSARIAL-REVIEW.md).
