# MN-006 proposed case schema

## Status and boundary

**Proposed, not frozen and not implemented.** This document defines the minimum audit data a future deterministic generator should emit. It is not JSON Schema, a generated inventory, a measured artifact, or authorization to implement a runner.

## Design goals

A case must be reproducible from its definition and seed, and its retained data must permit an auditor to determine the exact source events and global positions; relevant entity histories; degree of interleaving; final state for each entity; bounded-rule facts; and why the finite canonical answer is correct.

The primary model input contains source events and the non-answer-bearing question only. Canonical final states, derived facts, and the answer are oracle-only fields and must never be rendered into the untreated primary condition.

## Proposed logical record

| Field | Proposed meaning | Visibility / validation requirement |
| --- | --- | --- |
| `case_id` | Stable unique identifier. | Public case identity; deterministic. |
| `schema_version` / `generator_version` | Versioned semantic and generator authority. | Retained for reproducibility. |
| `seed` | Deterministic per-case generation seed. | Retained; not an answer hint. |
| `difficulty_level` | `level_1` or `level_2` profile identifier. | Must map to frozen profile limits. |
| `entities` | Entity IDs, permitted initial states, and role-neutral inventory metadata. | IDs must not encode answer/target state. |
| `source_events` | Ordered facts: `event_id`, global ordinal, entity ID, assigned state. | One-to-one source truth; no `current`, `final`, derived, or answer field. |
| `event_positions` | Per-entity ordered event IDs/ordinals and provenance. | Recomputable from `source_events`. |
| `query` | Queried entity set, rule identifier/version, question rendering. | May name entities but not states, facts, or answer. |
| `allowed_answers` | Complete finite answer vocabulary. | Same grammar policy across matched arms. |
| `canonical_entity_states` | Oracle map after replay. | Never primary-source visible. |
| `canonical_derived_facts` | Predicate values consumed by the rule. | Oracle-only; no treatment may expose them. |
| `canonical_answer` | Unique rule label. | Oracle-only; exact scorer authority. |
| `generation_metadata` | Counts, balance, interleaving metrics, validity checks, hashes. | Supports profile and leakage audits. |

## Event and provenance requirements

The frozen implementation should retain a source event equivalent to:

```text
event_id
global_ordinal
entity_id
assigned_state
```

Previous state, final state, and derived predicates are oracle computations, not source-event fields. The scheduler must retain enough provenance to recompute for every queried entity:

- its event sequence in within-entity order;
- global ordinal of each event;
- count/distance of intervening non-self events between successive updates;
- number of entities represented in those events; and
- a declared interleaving-density statistic.

The exact metric and thresholds remain to be frozen. A level cannot claim distributed interleaving merely because another entity appears somewhere in the context.

## Oracle evaluation model

The canonical oracle must be separable into pure deterministic functions:

```text
replay(source_events, initial_states) -> canonical_entity_states
derive(canonical_entity_states, query, rule_version) -> canonical_derived_facts
decide(canonical_derived_facts, rule_version) -> canonical_answer
```

The final validator must reject a case when replay is ambiguous, an event is invalid, a query lacks required inputs, a derived fact is undefined, the answer is outside `allowed_answers`, more than one answer is valid, or the answer is a direct identity copy of one entity-state value under the selected rule family.

## Treatment and control provenance

Later interventions must add condition-specific rendered artifacts outside this canonical source record. Every artifact must cite `case_id` and preserve a verifiable mapping to `source_events`. A matched-control validator must test source fact multiset, event membership, entity handling, intended ordering/locality, question, answer vocabulary, and non-answer-bearing fields according to the frozen independent variable.

An External State Management condition may derive a state table by replaying the same source events, but its treatment artifact must omit `canonical_derived_facts` and `canonical_answer`; the model, rather than the host, must apply the shared downstream rule.

## Open schema decisions

Before implementation, Design Gate A must choose the exact serialization format, state vocabulary, rule identifier semantics, hash canonicalization, public/private artifact boundary, and whether `initial_states` is rendered or fixed by a common rule. These are intentionally not encoded in an implementation schema yet.
