# MN-006 v1 semantic workload contract

## Status and authority

**`mn006_v1_semantic_contract_frozen`** for later deterministic generator, oracle, and static validator implementation. This contract is not a generated corpus, measured evidence, candidate treatment, or inference authorization. It supersedes only the unresolved semantic placeholders in the MN-006 Design Gate A draft; MN-003 through MN-005 remain immutable historical evidence.

## Causal question and scope boundary

MN-006 v1 tests one primary workload dimension:

```text
contiguous/local entity histories
            ↓
distributed/interleaved entity histories
```

The only interface adaptation is a fixed one-step truth-table decision over two final states. It prevents a maintained state register from being the answer itself. It is **not** an increasing reasoning-difficulty dimension: context/state-distribution pressure may increase by profile; rule depth, arity, state vocabulary, rule family, answer grammar, and parsing do not.

V1 excludes hierarchy/nested scopes, parent-child semantics, causal graphs or propagation, multi-hop/recursive reasoning, noisy or ambiguous language, commonsense/external knowledge, planning, tools, retrieval/RAG, cross-session or cross-episode memory, and open-ended explanation. Any such axis requires a later design decision, not a Level 3 extension hidden inside v1.

## State model and transitions

Every entity has one shared scalar field:

```text
STATE ∈ {S0, S1, S2}
```

All entities start at `S0`. Entity identifiers are canonical zero-padded tokens `E01`, `E02`, …, `E08`; an active profile uses the first required number of identifiers. The tokens have no domain semantics.

An event is a direct assignment, not an operator:

```text
ENTITY_ID STATE = STATE_TOKEN
```

A valid v1 entity history has exactly three assignments. Each assignment must use a member of the state vocabulary and differ from the immediately preceding state, including the common initial state for the first assignment. Nonconsecutive reuse is allowed. Thus `S0 → S1 → S2 → S0` is valid; `S0 → S0` and `S1 → S1` are invalid. Every profile gives every active entity three assignments, so no final state depends on an implicit/missing update.

Direct assignment plus the no-op prohibition keeps replay trivial while forcing the model to retain update order. Invalid entity IDs, values, history lengths, no-ops, and out-of-order per-entity events are construction errors, not model-scored cases.

## Source syntax and ordering

The frozen model-visible serialization is UTF-8 text with LF line endings:

```text
All entities begin in S0.
E01 STATE = S1
E02 STATE = S2
...
For <QUERY_ENTITY_1> and <QUERY_ENTITY_2>, output VALID if their states are equal; otherwise output INVALID.
Output exactly one label: VALID or INVALID.
```

`ENTITY_ID STATE = STATE_TOKEN` is the complete event grammar. There are no pronouns, aliases, paraphrases, implicit references, narrative content, derived fields, or answer-like metadata. Source order is global event order. Within a single entity, its first, second, and third assignment retain that order under every schedule.

## Fixed rule and answer grammar

Each case queries exactly two entities selected independently of their final values and of the schedule. Let their replayed final states be `a` and `b`.

```text
derived.equal_state = (a == b)
answer = VALID   if derived.equal_state
answer = INVALID otherwise
```

The rule has arity 2 and depth 1. It has no intermediate derived-fact chaining, no recursion, and no dependency on non-query entities. It is not an identity mapping from either stored state to the answer.

| `state(A)` | `state(B)` | `derived.equal_state` | Answer |
| --- | --- | --- | --- |
| S0 | S0 | true | VALID |
| S0 | S1 | false | INVALID |
| S0 | S2 | false | INVALID |
| S1 | S0 | false | INVALID |
| S1 | S1 | true | VALID |
| S1 | S2 | false | INVALID |
| S2 | S0 | false | INVALID |
| S2 | S1 | false | INVALID |
| S2 | S2 | true | VALID |

The canonical response grammar is exactly one case-sensitive label, `VALID` or `INVALID`, after trimming leading/trailing ASCII whitespace. Any other character, token, label, or explanatory text is malformed and scores zero. The evaluator never uses an LLM judge.

## Profiles and matched contiguous control

A contiguous serialization is a **generator capability and matched diagnostic control**, not a primary MN-006 difficulty level. Every Level 1 or Level 2 canonical case must be serializable in both schedules with identical entities, initial states, per-entity histories, events, final states, query, rule, allowed answers, and canonical answer. Only global cross-entity placement changes.

| Schedule/profile | Entities | Updates/entity | Queried entities | Total events | Query same-entity gaps | Purpose |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| `contiguous_control` | inherited from paired level | 3 | 2 | inherited | all `0` | Matched locality diagnostic; not a primary level. |
| `level_1_light_interleaved` | 3 | 3 | 2 | 9 | all `2` | Light genuine interruption and generator/oracle sanity regime. |
| `level_2_primary_interleaved` | 8 | 3 | 2 | 24 | all `7` | Primary distributed/interleaved regime. |

For a queried entity with event positions `p1 < p2 < p3`, its gaps are `p2 - p1 - 1` and `p3 - p2 - 1`; its relevant-update span is `p3 - p1 + 1`. Accordingly, interleaved Level 1 has per-query span `7`, and Level 2 has span `17`. The contiguous control has gap `0` and span `3`.

The interleaved scheduler derives one seeded permutation of active entity IDs and emits round 1 for every entity in that order, then round 2 in the same order, then round 3. Therefore every entity has exactly `entity_count - 1` foreign events between consecutive own updates. The contiguous scheduler emits all three events of each entity in the same seeded entity order. Both preserve internal history order.

Required retained metrics are: entity count, updates/entity, total event count, query/non-query event counts, per-query gap vector, minimum and mean query gap, per-query relevant span, query selection, entity permutation, and schedule kind. No larger metric suite is needed in v1. Level 1 has six query events and three non-query events; Level 2 has six query events and eighteen non-query events. This increase in non-query context is an intentional component of distribution pressure and is recorded rather than hidden.

## Deterministic generation by construction

Generation never enumerates the global state product or rejects arbitrary cases until an answer happens to balance. For a profile and case ordinal:

1. derive independent deterministic sub-seeds for query selection, entity permutation, query answer class, query final-state tuple, and non-query histories;
2. select the answer class from the predeclared balanced sequence;
3. select two queried entity IDs before selecting their final states;
4. construct a final-state pair consistent with the selected class: equal for `VALID`, unequal for `INVALID`;
5. construct each three-event history backwards from its chosen final state, with every consecutive assignment different and with the fixed initial `S0` respected;
6. choose non-query final states/histories from their independent sub-seeds;
7. schedule the already-valid histories using the selected contiguous or interleaved schedule;
8. replay, derive, decide, and validate the result before serialization.

If construction/validation disagree, that is a deterministic generator defect; the implementation must fail rather than search, mutate a case, or silently resample. With `E` entities and fixed `U=3` updates per entity, construction, scheduling, replay, metric calculation, and validation are all `O(E × U)` time and `O(E × U)` retained-event space. Truth-table lookup is `O(1)`.

## Answer balance and bounded coverage

For every frozen profile/seed batch, cases are answer-stratified by construction: the sorted case ordinal sequence alternates `VALID`, `INVALID`, `VALID`, `INVALID`, …, so the class-count difference is at most one. Within a class, deterministic sub-seeds rotate admissible final-state tuples; no post hoc rejection is used to balance labels.

Coverage is profile-based rather than Cartesian. A later inventory freezes a bounded seed list for each schedule/profile and includes both answer classes plus deterministic rotation through state tuples and query identities. It does not enumerate all states, entity subsets, event orders, or rule combinations. Any future interaction-coverage policy (for example pairwise coverage) requires an explicit revision; it is not inferred from model outcomes.

## Oracle boundary and visibility

The authority oracle consists only of pure deterministic operations:

```text
replay(source_events, initial_state) -> canonical_entity_states
derive(canonical_entity_states, query_entities, rule_id) -> canonical_derived_facts
decide(canonical_derived_facts, rule_id) -> canonical_answer
```

`replay` applies event assignments in global order while asserting each entity's expected predecessor state; it produces the state map and per-event provenance. `derive` reads only the two query states and computes `equal_state`. `decide` performs the fixed table lookup. None may summarize source facts for a model, choose an answer in a treatment, or expose oracle-only fields in the untreated prompt.

## Required validators

A later implementation must statically validate semantic validity, deterministic replay, history length, state values, no-op prevention, state/answer recomputation, answer grammar, balanced class sequence, query selection independence, schedule metrics, intra-entity order, contiguous/interleaved pair equivalence, source-event conservation, no source deletion/duplication/compression, and absence of oracle fields or forbidden answer-like names in model-visible data.

Canonical authority serialization is UTF-8, LF-normalized JSON with sorted object keys and a final newline before SHA-256 fingerprinting. Validators must hash canonical serialized content, not mutable platform worktree bytes. This requirement is informed by the retained CRLF/raw-byte authority issue; it does not alter any earlier frozen authority.

## Implementation boundary

This semantic contract is sufficient for a deterministic generator, oracle, case validator, and paired contiguous/interleaved serializer. It authorizes only that future non-model implementation work. A generated inventory, measurement contract, candidate treatment, model inference, or GPU run still requires a later gate.
