# MN-006 Design Gate B — v1 semantic contract decision

## Status

**`design_gate_b_complete`**

**Decision:** `generator_implementation_ready` for a deterministic non-model generator, oracle, paired serializer, and static validator suite. This does not authorize a case inventory, candidate treatment, model/GPU inference, or efficacy measurement.

## Contract classification

| Contract element | Classification | Decision |
| --- | --- | --- |
| Primary difficulty dimension | frozen | Distributed/interleaved state locality is the only primary manipulated research dimension. |
| Truth-table layer | frozen | Fixed depth-1, arity-2 equality rule; minimal answer-oracle adapter, not reasoning difficulty. |
| Scope exclusions | frozen | No hierarchy, causal/multi-hop reasoning, language variation, retrieval, tools, persistence, or explanation in v1. |
| State model | frozen | One shared scalar `STATE ∈ {S0,S1,S2}`, common initial `S0`. |
| Transitions | frozen | Exactly three direct assignments/entity; every consecutive assignment differs from predecessor; no-ops invalid. |
| Event grammar | frozen | `ENTITY_ID STATE = STATE_TOKEN`; exact UTF-8/LF serialization specified. |
| Query/rule | frozen | Exactly two independently chosen queried entities; equality table yields `VALID`/`INVALID`. |
| Answer parser/balance | frozen | Exact case-sensitive labels after outer ASCII trim; alternating answer-stratified ordinal sequence, imbalance at most one. |
| Contiguous role | frozen | Generator-supported matched diagnostic control, never a primary MN-006 level. |
| Level 1 | frozen | Three entities, three updates/entity, two queries, nine events, same-entity query gaps exactly two. |
| Level 2 | frozen | Eight entities, three updates/entity, two queries, twenty-four events, same-entity query gaps exactly seven. |
| Scheduler | frozen | Seeded entity permutation; repeated round-robin interleaving or grouped contiguous serialization; preserve internal order. |
| Generation method | frozen | Answer-stratified deterministic construction and replay; no Cartesian enumeration or answer-discovery rejection search. |
| Oracle decomposition | frozen | Pure replay → derive → decide operations with retained provenance. |
| Schema/public-authority boundary | frozen | [v1 case schema](case-schema.md) separates public, evaluator, and authority fields. |
| Validator requirements | frozen | Semantic, answer, schedule, matched-pair, leakage, serialization/hash, and coverage validators mandatory. |
| Inventory seed list/sample size | deferred | Freeze only in a later generator/inventory contract; no huge corpus or measurement size selected now. |
| Candidate treatment/control details | deferred | Require a later candidate-specific hypothesis and measurement contract. |
| Perfect-state diagnostic prompt | proposed | Its oracle data is frozen; model-facing control rendering is deferred until a measurement design. |
| Level 3/advanced axes | rejected for v1 | A new design decision is required; not an implicit future profile. |

## Gate answers

1. **Sole primary difficulty:** yes—distributed state locality/interleaving.
2. **Truth-table adapter:** yes—fixed, depth 1, arity 2.
3. **Finite state model:** `{S0,S1,S2}` one scalar field per entity.
4. **Legal transitions:** three direct non-no-op assignments per entity from common `S0`.
5. **Event grammar:** `E## STATE = S#`, global order with per-entity order preserved.
6. **Interleaving:** seeded repeated-round schedule; gaps/spans and event counts retained.
7. **Contiguous profile:** paired generator serialization and diagnostic control only.
8. **Level 1:** three entities, three updates each, gaps two; genuine interleaving.
9. **Level 2:** eight entities, three updates each, gaps seven; more distribution pressure only.
10. **Truth table:** equality of two replayed query states, fully enumerated in the semantic contract.
11. **Answer vocabulary:** `VALID` / `INVALID`, strict finite parser.
12. **Balance:** answer class selected before histories in alternating ordinal sequence.
13. **Bounded generation:** construct final state tuple/histories then schedule/replay; `O(E × U)`.
14. **Canonical computation:** pure replay → derive `equal_state` → decide table lookup.
15. **Mandatory validators:** semantic, answer, interleaving, pair-equivalence, leakage, canonical serialization/hash, and coverage checks.
16. **Unresolved before implementation:** none that require arbitrary scientific semantics. Deferred inventory size, model control renderings, and treatments are outside generator/oracle implementation.

## Scientific interpretation boundary

A later matched comparison may attribute a degradation to distributed state locality only if the pair-equivalence and schedule validators pass and both conditions share this frozen state model, histories, rule, question, answer grammar, and answer class. It may not attribute a difference to hierarchy, reasoning depth, language ambiguity, compression, target filtering, or answer format because those are excluded or held constant.

## Next boundary

The next authorized task may implement deterministic generation, oracle, validators, and paired public/authority serialization against this contract. It must not run models, generate measured evidence, choose a candidate intervention, or alter this frozen semantic contract without a recorded revision.
