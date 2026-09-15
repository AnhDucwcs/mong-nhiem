# MN-006 v1 case schema

## Status and authority

**`mn006_v1_case_schema_frozen`** for a future deterministic generator and validators. This is a semantic/schema contract, not a generated inventory or measured evidence. The prior proposed schema is superseded by this file; its design intent remains traceable in Design Gate A.

## Artifact boundary

A case has three views. They may be stored together in an authority artifact, but only the public view may be rendered to the untreated model condition.

| View | Fields | Visibility |
| --- | --- | --- |
| Public model case | `case_id`, `profile`, public `initial_state`, ordered `source_events`, `query`, `allowed_answers`, public serialization version | Model-visible. Contains no final/derived/answer field. |
| Evaluator record | `case_id`, `allowed_answers`, `canonical_answer`, response-parser/version metadata | Evaluator-only. |
| Authority provenance | seed/sub-seeds, entity inventory, histories, event provenance, schedule metrics, canonical states, derived facts, answer, validation results, canonical hashes | Generator/validator/audit-only. |

## Frozen logical fields

| Field | Meaning |
| --- | --- |
| `case_id` | Stable ID derived from schema version, profile, schedule kind, and ordinal; it does not encode an answer. |
| `schema_version` / `semantic_contract_version` | Frozen authority version identifiers. |
| `seed` / `subseeds` | Case seed and named independent derivations for query, answer class, state tuple, histories, and permutation. |
| `profile` / `schedule_kind` | `level_1_light_interleaved` or `level_2_primary_interleaved`, paired with `contiguous_control` or matching interleaved serialization. |
| `entities` | Active canonical entity IDs and common initial state `S0`. |
| `entity_histories` | Authority-only ordered three-assignment history for every entity. |
| `source_events` | Public ordered events, each with `event_id`, global ordinal, `entity_id`, and `assigned_state`. |
| `event_provenance` | Authority-only mapping from event to entity-history ordinal and expected predecessor state. |
| `interleaving_metrics` | Entity/event counts, query/non-query counts, gap vectors/minimum/mean, spans, and seeded permutation. |
| `query` | Two entity IDs, fixed `rule_id`, exact question rendering, and response grammar version. |
| `allowed_answers` | Exactly `["VALID", "INVALID"]`. |
| `canonical_entity_states` | Authority-only replay state map for every entity. |
| `canonical_derived_facts` | Authority-only `{ "equal_state": boolean }`. |
| `canonical_answer` | Authority-only/evaluator `VALID` or `INVALID`. |
| `generation_metadata` | Generator version, canonical serialization/hash, validator versions/results, and pair identifier. |

`source_events` never contains previous state, final state, `current`, derived facts, answer, target-answer metadata, or a compressed per-entity summary. The public query names the two selected entities and states the shared rule, but does not state their values or truth-table result.

## Pair identity and equivalence

A `pair_id` links contiguous and interleaved renderings of one underlying canonical case. Their authority records must have identical entity histories, source-event multiset, initial state, query, rule ID, allowed answers, canonical entity states, derived facts, canonical answer, and answer class. Only global event ordinals/order, schedule kind, and schedule-derived metrics may differ.

## Canonical serialization

Public and authority JSON are serialized as UTF-8, LF-normalized, sorted-key JSON with a final newline. SHA-256 is calculated over that canonical byte sequence. The generator must not use platform-default text encoding, newline translation, or mutable worktree bytes as authority input.
