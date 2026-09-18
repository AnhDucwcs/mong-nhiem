# MN-006 recurring fixed-label causal review

## Status

**`next_minimal_diagnostic_identified`.** This is a static causal-design review of immutable S0, S1, D1, and baseline evidence. It identifies one possible future diagnostic boundary only; it creates no prospective request plan, executor, run directory, model result, locality result, or treatment.

The immediate question is not whether interleaving harms the model. It is the lower-level question exposed by the retained records: after the model has been shown to copy either explicit A/B target, which operation first prevents its constrained output from conditioning on task-bearing input?

## Immutable evidence basis

| Evidence | Exact retained result | Bounded observation |
| --- | --- | --- |
| `attempt-0001` | `protocol_valid`; 128 malformed free-form outputs | The unconstrained channel did not produce usable finite answers; it is not a locality result. |
| `attempt-0002` | `protocol_valid`; 128 `INVALID` outputs | The constrained `VALID`/`INVALID` channel was usable but selected one label for every baseline case; locality remained unobserved. |
| S0 `output-selection-s0-run-0001` | `protocol_valid` / `direct_copy_supported`; A, B, B, A | Under the neutral A/B grammar, the model copied both explicitly supplied target labels under both grammar orders. |
| S1 `output-selection-s1-run-0001` | `protocol_valid` / `fixed_label_preference_recurred`; A, A, A, A | With directly supplied state pairs and a fixed direct equality rule, equal cases matched A and unequal cases requiring B still produced A. |
| D1 `label-selection-d1-run-0001` | `protocol_valid` / `fixed_label_preference_supported`; A x 16, zero grammar-order disagreements | With direct states, counterbalanced M1/M2 mapping tables, and G_AB/G_BA controls, every output was A. |

All retained records, plan fingerprints, parsers, grammars, runtime parameters, and prior classifications are authority. This review does not modify or rescore them.

### Exact interface observations

The minimality authority plan is SHA-256 `8180ea423a05eeb2930b84cee6102fd94595e13856f1a91e1afe4d599bb8e827`. S0 used `root ::= "A" | "B"` and `root ::= "B" | "A"`; both explicit B-target requests returned B, including one under each grammar order. Its strict parser accepts only A or B after outer ASCII-whitespace trimming.

S1 used only `G_AB`, `root ::= "A" | "B"`, with the direct public rule:

```text
E01 STATE = S1
E02 STATE = S2
Output A if the states are equal.
Output B if the states are different.
Output exactly one label: A or B.
```

Its four frozen records covered two equal and two unequal pairs, both `S1` and `S2`, and both unequal orientations. The canonical labels were B, A, A, B; all retained raw outputs were A.

D1 used the same strict A/B parser and grammar language, while counterbalancing both mappings for every source relation:

```text
M1: equal -> A; unequal -> B
M2: equal -> B; unequal -> A
```

Every source-plus-mapping cell occurred once under G_AB and once under G_BA. Canonical D1 labels were balanced eight A and eight B. All 16 retained outputs were A, including G_BA cells for which A is not the first written grammar alternative.

## Updated causal decomposition

S0 supports only the first layer. S1 jointly required the remaining layers, so its all-A result cannot be assigned to one of them without another causal cut.

| Layer | Operation | What the evidence establishes |
| --- | --- | --- |
| L0 | Emit/copy an explicitly supplied surface label. | Supported only for the frozen S0 copy prompts: explicit A produced A and explicit B produced B. |
| L1a | Perceive/extract the two supplied state symbols and their structured presentation. | Not isolated. S1 and D1 contain state-bearing text; S0 does not. |
| L1b | Determine whether those symbols are equal or different. | Not established. S1's A on equal rows is compatible with correct equality, but A was also the repeated default. |
| L1c | Interpret a conditional rule that connects equality/difference to A/B. | Not isolated from L1d in S1. D1 adds a mapping-table abstraction rather than removing this ambiguity. |
| L1d | Select the constrained surface label after task-bearing input has been interpreted. | Not established. S0 shows label availability/copying, not post-inference label selection. |

The useful distinction is therefore **surface-label availability** versus **surface-label selection after inference**. S0 supports the former under its explicit-copy interface. S1 and D1 do not support the latter when a relation or mapping-bearing condition must determine the label.

## Hypotheses compatible with the retained evidence

| Hypothesis | Compatibility and pressure from evidence | Remaining entanglement | Minimum discriminating observation |
| --- | --- | --- | --- |
| `relation_computation_failure` | Compatible with S1 because S0 never asks for equality and S1's unequal rows may reflect a failed comparison. The correct equal rows are not affirmative comparison evidence because fixed A also scores them correctly. | S1 jointly includes state extraction, equality computation, rule interpretation, and label selection. | Supply `equal` or `different` explicitly while retaining the exact direct A/B rule. Correct outputs for both relations would make the S1 failure upstream of direct rule/label selection. |
| `relation_to_label_rule_application_failure` | Compatible with S1: the direct conditional rule has to convert relation into the non-explicit response. D1's all-A result when mappings require B is also compatible. | S1 cannot distinguish rule application from a more general conditioned-output default. | The same explicit-relation control removes comparison while retaining the direct conditional rule. An all-A result there would show comparison is not required for the collapse. |
| `inference_conditioned_fixed_label_default` | Strongly compatible: D1 is A x 16 under both mappings and grammar orders, and S1 is A x 4. S0 contradicts only the stronger claim that B cannot be emitted at all. | A behavioral default cannot be separated from failed conditional-rule application by the current records. Token preference magnitude remains unknown because logprob collection is deferred. | In the explicit-relation control, a repeated A despite one explicit `different` relation requiring B would support recurrence of this behavior after comparison has been removed. It would not identify internal logits or implementation cause. |
| `state_symbol_or_prompt_representation_confound` | Compatible: S1 and D1 both use `E## STATE = S#` structure; S0 does not. The symbols and equality task have not been independently varied. | Representation extraction (L1a) and equality computation (L1b) are combined in S1. | Explicit relation text removes both state-symbol presentation and comparison. If direct rule/selection succeeds there, the remaining S1 explanation is within L1a/L1b; a later, separately justified split could distinguish them. |
| `first_option_or_surface_prior` | A remains a live surface/default explanation, but a pure grammar-alternative-first explanation is weakened. D1 returned A under G_BA, where B is written first; S0 copied B under both G_AB and G_BA. | S1 alone uses G_AB, so it does not independently re-audit alternative order. The retained D1/S0 controls are the relevant upstream evidence. | No additional grammar-order factor is needed for the immediate adjacent cut. A future grammar-order test would add a redundant factor unless a new interface produces an order-sensitive result. |
| `mapping_abstraction_failure` | D1 is compatible with mapping-table difficulty, but S1 removes that table and still produces A on all cells. Thus mapping abstraction is not necessary to explain the recurring behavior. | Mapping abstraction could still add difficulty; the evidence does not show it is irrelevant in every interface. | First establish whether a direct conditional rule works when the relation is explicit. Only a successful direct-rule control would make the added D1 mapping table a more specific remaining candidate. |

No hypothesis above is identified as an internal mechanism. The evidence is behavioral and deterministic under one qualified model/runtime/interface.

## Candidate diagnostic landscape

| Candidate | Removes from S1 | Retains | Causal value and new confounds | Decision |
| --- | --- | --- | --- | --- |
| Explicit relation -> direct A/B conditional | L1a state-symbol extraction and L1b equality comparison | L1c direct rule interpretation and L1d constrained label selection; same A/B parser, grammar language, runtime, and direct-rule wording | The closest adjacent causal cut. It can separate state comparison/representation from downstream conditioned selection without adding a mapping table. | **Selected as the single next diagnostic recommendation.** |
| Direct semantic relation output (`EQUAL` / `DIFFERENT`) | Arbitrary A/B mapping | State extraction/comparison and semantic-word output selection | Changes vocabulary, grammar, tokenization, and semantic priors simultaneously. It would not preserve the established A/B channel and risks replacing one surface-label question with another. | Rejected for now. |
| Explicit selector / arbitrary conditional control | Equality computation | Some symbolic condition and A/B selection | If the selected label is explicit it duplicates S0; if it is selected through a rule it is materially the same lower-level question as the selected explicit-relation control but less tied to S1. | Rejected as redundant. |
| State-presentation simplification | Potentially L1a | Potentially altered equality semantics and output selection | Changes state representation and comparison together while losing the direct adjacency to S1. It becomes useful only if the selected control supports direct rule/selection and leaves L1a/L1b as the next live cut. | Deferred. |
| Direct-rule counterbalance | None; adds a reversed mapping factor | Relation, conditional rule, A/B selection | D1 already shows A under both mapping directions, but only with a mapping table. Repeating counterbalance here would reintroduce an extra mapping factor before the simpler direct-rule cut is observed. | Not part of the next minimal diagnostic. |

### Why D1 counterbalancing does not settle S1

D1 provides meaningful evidence: both A and B were canonical equally often; each state relation appeared under M1 and M2; and grammar order did not change the output. It weakens a pure alternative-order explanation and demonstrates that the model did not follow B-requiring mapping-table cells.

It does not, however, identify the lower S1 failure. D1 still requires direct-state comparison plus parsing and applying a counterbalanced table. Its all-A result could arise before, during, or after mapping interpretation. S1 removes the table but retains comparison and direct conditional selection; its all-A result makes a mapping-table-only explanation untenable, but leaves L1a–L1d entangled. Reintroducing direct-rule counterbalance now would add back a mapping dimension before observing the simpler cut.

## Selected disposition and next boundary

**Disposition: `next_minimal_diagnostic_identified`.**

The recommended future diagnostic is an **explicit-relation direct-rule control**. It must not be implemented, planned, or executed by this review. A later separate static gate would need to freeze its exact bytes and lifecycle.

Its sole causal purpose is:

```text
explicit relation token (equal / different)
    -> unchanged direct rule (equal -> A; different -> B)
    -> constrained A/B label
```

It removes S1's state-symbol extraction and equality-comparison operations while retaining the smallest relevant downstream operation: selecting A/B under the same direct conditional rule. The minimum balanced design is two independent requests—one explicit `equal` relation requiring A and one explicit `different` relation requiring B—using the existing G_AB grammar, strict A/B parser, qualified runtime, independent-request lifecycle, and a predeclared non-adaptive order. Two requests are sufficient for this deterministic causal sanity cut because they cover both labels and both relation values; duplicating state values, orientations, or grammar orders would restore factors that the control intentionally removes or that S0/D1 already audited.

Major future outcomes would license only these bounded inferences:

| Future explicit-relation result | Licensed inference | Not licensed |
| --- | --- | --- |
| Both labels correct | Direct rule interpretation and conditioned A/B selection work in this minimal relation-token interface. The S1 failure is then upstream, within state-symbol representation/extraction or equality comparison. | A distinction between L1a and L1b; state reconstruction ability; locality sensitivity; any intervention claim. |
| A for both relations | State comparison is not necessary for the recurring collapse. The remaining failure is in direct conditional rule interpretation and/or conditioned label selection under this interface, consistent with a fixed-A behavioral default. | An internal logit mechanism, grammar defect, or exact separation of L1c from L1d. |
| Any other complete parseable pattern | The lower cut is inconclusive; do not attribute S1 to comparison, rule application, or surface default. | Any locality or intervention conclusion. |
| Infrastructure-invalid or malformed outcome | No semantic inference. | Any causal conclusion. |

No mapping counterbalance is recommended for this immediate diagnostic because it would reintroduce a mapping dimension that the control is intended to remove. D1's counterbalanced result remains the upstream evidence that A persisted across mapping direction and grammar order. If the explicit-relation control later produces a pattern that leaves direct-rule direction specifically ambiguous, another separate causal-design decision—not an automatic follow-on—would be required.

## Authorization boundary

- D2 remains blocked by its independent D1 prerequisite: `mapping_following_supported` did not occur.
- Locality remains unmeasured.
- The perfect-state diagnostic remains unauthorized.
- `attempt-0003` remains prohibited.
- No candidate intervention, architecture treatment, alternative model, seed sweep, prompt tuning, logprob measurement, retry, or runtime change is authorized.
- S0, S1, D1, attempts 0001/0002, and frozen MN-003/MN-004/MN-005 evidence remain immutable.

The next permitted action is **only** a separately authorized static gate for the recommended explicit-relation direct-rule control. It must decide whether the two-request future diagnostic can be frozen without changing the established A/B response-channel contract. No model execution is authorized by this review.
