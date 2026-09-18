# MN-006 Explicit-Relation Direct-Rule Gate

Status: `explicit_relation_direct_rule_diagnostic_ready`

This is a static causal-design gate. It freezes one prospective diagnostic and contains no model output, executor, run directory, locality measurement, or intervention evidence.

## Immutable evidence basis

The gate depends on the following canonical sequence:

- S0 `output-selection-s0-run-0001` is `protocol_valid` / `direct_copy_supported`: both A and B were copied under the constrained channel.
- S1 `output-selection-s1-run-0001` is `protocol_valid` / `fixed_label_preference_recurred`: all four outputs were A.
- D1 `label-selection-d1-run-0001` remains `protocol_valid` / `fixed_label_preference_supported` and is retained context, not an execution prerequisite.
- The [recurring fixed-label causal review](recurring-fixed-label-causal-review.md) has disposition `next_minimal_diagnostic_identified`.

These artifacts and all earlier attempts remain immutable.

## Causal purpose

S1 jointly required:

```text
L1a  extract the supplied structured state symbols
L1b  determine equality or difference
L1c  interpret equal -> A and different -> B
L1d  select the constrained label after task-bearing input
```

The new control removes exactly L1a and L1b by supplying the semantic relation directly. It retains L1c and L1d. It asks:

> When the relation is supplied explicitly, can the qualified model/runtime apply the fixed direct rule and select A or B?

This differs from S0. S0 supplied the target surface label and required copying. This control supplies only a semantic relation; the model must still apply the rule to select the label.

## Frozen authority

- Contract: `mn006-explicit-relation-direct-rule-v1`
- Prospective run: `explicit-relation-direct-rule-run-0001`
- Stage: `explicit_relation_direct_rule`
- Authority: [plan.json](definition/explicit-relation-direct-rule-v1/plan.json)
- Authority SHA-256: `dc40c15a896f5f0413783818c39593b8a9c34eeea3ef4ce284e1b311112bc80a`
- Parser: existing strict `mn006-label-selection-parser-v1`
- Runtime: existing `mn006-baseline-runtime-v1`

The two requests are sufficient for this deterministic sanity control: one cell requires each relation and each output label. Replication would not remove another operation or resolve a new causal ambiguity.

## Exact request matrix

The order is the mechanical first-occurrence projection of the frozen S1 plan: the first S1 occurrence of `different`, then the first occurrence of `equal`. It was not selected from model behavior.

| Ordinal | Relation | Canonical label | Grammar |
| ---: | --- | --- | --- |
| 1 | `different` | `B` | `G_AB` |
| 2 | `equal` | `A` | `G_AB` |

Exact public prompt 1, including one final LF:

```text
Relation: different
Output A if the relation is equal.
Output B if the relation is different.
Output exactly one label: A or B.
```

Exact public prompt 2, including one final LF:

```text
Relation: equal
Output A if the relation is equal.
Output B if the relation is different.
Output exactly one label: A or B.
```

The prompts contain no state pair, source events, mapping-table block, example, demonstration, target-label field, or case-specific answer hint.

## Grammar and parser

Both requests use only:

```text
root ::= "A" | "B"
```

with one final LF. Grammar-order pairing is not repeated: S0 established that both labels can be copied under both orders, and D1 observed A under both orders. Holding `G_AB` fixed matches S1 and keeps this control to the adjacent causal cut.

The strict parser trims outer ASCII whitespace and accepts exactly uppercase `A` or `B`. It performs no substring extraction, punctuation repair, fuzzy matching, or case folding.

## Rule-counterbalancing decision

The fixed S1 rule is retained:

```text
equal     -> A
different -> B
```

Counterbalancing would add the mapping variation already present in D1 and would no longer isolate the removal of S1's upstream comparison operations. The single rule cannot distinguish a general A prior from every possible rule failure, but the two outcome patterns below answer the narrower adjacent-cut question without reintroducing mapping abstraction.

## Frozen semantic classifier

Infrastructure validity is evaluated first. An incomplete or infrastructure-invalid run has `outcome: infrastructure_invalid` and a null semantic classification.

For a complete infrastructure-valid two-record run, precedence is:

1. `explicit_relation_malformed_or_invalid`: either output fails the strict parser.
2. `explicit_relation_direct_rule_supported`: outputs are `B, A` in frozen request order.
3. `fixed_label_preference_persisted`: outputs are `A, A`.
4. `explicit_relation_inconclusive`: any other complete parseable pattern.

The implementation in [explicit_relation.py](scripts/mn006/explicit_relation.py) is static planning and classification support only; it performs no network or model activity.

## Interpretation boundaries

### `explicit_relation_direct_rule_supported`

The qualified model/runtime can apply this fixed semantic relation-to-label rule and select both constrained labels when the relation is explicit. Combined with S1, the unresolved bottleneck moves upstream to the removed operations: structured state extraction and/or equality comparison. This result does not separate L1a from L1b or establish general reasoning.

### `fixed_label_preference_persisted`

State extraction and equality comparison are not necessary for the recurring fixed-A behavior. The remaining failure region lies within or below direct conditional-rule interpretation and/or post-task label selection. No internal mechanism is inferred.

### Other semantic outcomes

A malformed result establishes only strict-channel invalidity for this diagnostic. Any other complete parseable pattern is inconclusive; it is not post-hoc reclassified.

## Future execution prerequisites

A future executor must fail closed unless it mechanically validates:

1. the authority bytes and SHA-256 above;
2. canonical S0 as `protocol_valid` / `direct_copy_supported`, including physical-artifact integrity;
3. canonical S1 as `protocol_valid` / `fixed_label_preference_recurred`, including physical-artifact integrity;
4. the causal-review path, SHA-256, and `next_minimal_diagnostic_identified` disposition.

D1 is relevant retained context but is not causally necessary as an execution prerequisite for this adjacent S1 decomposition.

## Decision register

### Frozen

- the two-request design, order, prompts, labels, `G_AB` grammar, strict parser, fixed direct rule, classifier, prerequisites, and interpretation boundaries;
- the diagnostic-only relationship to S0, S1, and D1;
- no grammar-order or rule counterbalancing in this control.

### Deferred

- an executor boundary and any model run;
- any later split between state-symbol extraction and equality comparison;
- any higher-level state reconstruction or locality diagnostic.

### Rejected

- increasing replication without a new causal factor;
- prompt demonstrations, reasoning instructions, synonyms, adaptive tuning, logprobs, seed sweeps, or alternate labels;
- treating this diagnostic as D2, `attempt-0003`, a perfect-state control, locality evidence, or an intervention.

## Authorization boundary

The next permitted task is only a separately authorized static executor boundary for `explicit-relation-direct-rule-run-0001`. This gate does not authorize inference. D2, state reconstruction, locality measurement, perfect-state work, and interventions remain blocked.
