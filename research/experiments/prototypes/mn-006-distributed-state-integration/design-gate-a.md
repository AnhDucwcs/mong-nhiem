# MN-006 Design Gate A — workload contract audit

## Status

**`design_gate_a_drafted_not_frozen`**. This is a design audit, not a generator, experiment definition, measured result, or intervention selection. Its purpose is to make explicit what must be resolved before implementation, while avoiding arbitrary premature parameter choices.

## Gate question

Can MN-006 define a candidate-neutral, deterministic distributed-state workload that isolates interleaved multi-entity state integration from a small downstream rule and does not turn External State Management into an answer oracle?

## Audit answers

| Required question | MN-006 design answer | Status before implementation |
| --- | --- | --- |
| 1. Failure mode | Failure to integrate each queried entity's latest valid state when its updates are separated and interleaved with other entity updates. | Concept frozen; no model boundary claimed. |
| 2. Why ECC-006 is insufficient | ECC-006 gives one target a contiguous ordered block and asks directly for its final state, so hierarchy/locality is already present and external state can nearly answer the task. | Frozen inherited evidence. |
| 3. Changed dimensions | Contiguous → distributed/interleaved histories; endpoint-only answer → bounded rule over multiple states. | Concept frozen; profiles not yet frozen. |
| 4. Held-simple dimensions | Flat entities, direct assignments, regular language, no dependencies/scopes/retrieval/tools/persistence. | Intended v1 boundary. |
| 5. State | A finite per-entity value maintained by applying the ordered assignment events for that entity. | Exact vocabulary/model must freeze. |
| 6. Valid transition | One unambiguous event assigns a permitted next value to one known entity; the valid-transition table forbids malformed, unknown, contradictory, or no-op cases as the frozen definition requires. | Transition table must freeze. |
| 7. Interleaving | Deterministically schedule each entity's internally ordered events into a global sequence so queried-entity updates have recorded non-self gaps in distributed levels. | Algorithm and thresholds must freeze. |
| 8. Bounded reasoning | Apply a small published truth-table/rule over selected final entity-state predicates; it uses state but is not identical to one state field. | Exact rule table must freeze. |
| 9. Answer space | One finite enumerated vocabulary, exact parser, one correct label per valid case, no explanation requirement. | Exact labels and balancing policy must freeze. |
| 10. Canonical answer | Oracle applies events → final state map → derived facts → bounded rule label. | Independent oracle implementation/check required. |
| 11. State vs reasoning diagnosis | Retain canonical final state and derived facts in addition to answer; future probes can score state, rule-with-correct-state, and end-to-end paths separately. | Probe protocol must freeze before inference. |
| 12. External-state anti-oracle | A register may expose entity/state pairs only. It may not include final/derived/answer fields, and host logic may not execute the rule or select the label. | Representation and audit check required. |
| 13. Candidate neutrality | The workload is defined from interleaving failure, not a preferred representation. All later arms preserve source facts and are measured against matched controls. | Treatment-specific controls later. |
| 14. Shared workload | Hierarchy, external state, normalization, and a new multi-pass hypothesis could each be evaluated only with a workload-specific mechanism and matched controls on the same frozen cases. | No candidate selected. |
| 15. Conditions before generator | Freeze the semantic and deterministic-generation contract listed below; validate it with no model execution. | Gate not yet passed. |
| 16. Conditions before inference | Freeze generated inventory, validation results, scoring, measurement/control contract, and treatment hypothesis after static deterministic checks pass. | Not authorized. |

## Design requirements to freeze before generator implementation

The generator implementation gate is blocked until the following are explicit and internally consistent:

1. finite entity identifier policy and finite state vocabulary;
2. initial-state and event-transition semantics, including invalid-case prevention;
3. exact source-event grammar, rendering order, and question grammar;
4. deterministic interleaving scheduler, seed derivation, and recorded separation metrics;
5. selected entities/derived-predicate inputs and the complete bounded rule table;
6. finite answer vocabulary, exact parser, uniqueness rule, and label-balance policy;
7. canonical state, derived-fact, and answer oracle semantics;
8. difficulty profiles and which dimensions each profile may vary;
9. proposed-case-schema fields, provenance, and reproducibility hashes/versions; and
10. static anti-leakage, source-conservation, treatment-neutrality, and perfect-state-control specifications.

The gate must also decide whether a contiguous-history comparator is a generator profile, a diagnostic-only Level 1 condition, or both. It may not silently become a weaker control after model results are observed.

## Conditions before model inference

Model inference remains prohibited until a later gate verifies all of the following without using model accuracy as a design signal:

- seeded generation is reproducible and gives the same canonical serialization/hashes;
- every event is valid, each final state is recomputable, and each answer is unique;
- source-event conservation/provenance and interleaving measurements meet the frozen profile;
- the rule is not an identity mapping from a single state value to an answer;
- answer labels meet the frozen balance policy;
- the exact evaluator accepts only the finite grammar and needs no LLM judge;
- canonical state and derived-fact probes are representable without leaking them into the primary source condition;
- a perfect-state control is specified as a diagnostic, not used to tune the workload;
- any candidate treatment has a separately frozen mechanism, matched control, resource accounting, and no-oracle validation; and
- the generated case inventory, definition, validator results, and measurement contract are frozen before any request.

## Decision

MN-006 remains in design status. The causal design is sufficiently specified to reject three invalid directions now: direct final-state questions, a register that contains the final decision, and a hierarchy condition confounded with filtering/compression/reordering. It is not sufficiently specified to authorize code or inference because the finite semantics, rule table, interleaving thresholds, answer labels, and validator design remain intentionally unresolved.

## Gate B resolution

This Gate A draft remains historical. [Design Gate B](design-gate-b.md) subsequently froze the v1 state model, direct-assignment grammar, truth table, answer policy, scheduler, profiles, oracle, schema boundary, and validators. Its decision is generator_implementation_ready for non-model implementation only.
