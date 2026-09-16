# MN-006 — Distributed State Integration

## Status

**The frozen Llama `attempt-0001` baseline is [protocol-valid](reports/mn-006-attempt-0001.md), but both profiles close as `no_usable_locality_failure_signal_under_v1_baseline`.** The deterministic infrastructure and canonical inventory remain intact; all 128 model outputs were malformed under the frozen exact-label parser, so the attempt establishes a shared output-channel floor rather than a contiguous-versus-interleaved state-locality result. The subsequent [Response-Channel Gate](response-channel-gate.md) is `response_channel_revision_ready`: it freezes a separate future `attempt-0002` with a constant response grammar only. No intervention was selected or tested.

MN-006 begins from the completed [MN-005 handoff](../mn-005-state-tracking-intervention-selection/mn-006-handoff.md). It preserves MN-003, MN-004, and MN-005 definitions, measurements, reports, raw artifacts, and conclusions as immutable historical evidence.

## Research motivation and inherited evidence

[ECC-006](../mn-003-effective-context-capacity/experiments/ecc-006-state-tracking/README.md) established a bounded Llama State Tracking failure region: one entity receives four ordered updates and the final-state endpoint is graded exactly. It also has two properties that make it a poor substrate for several deeper state-management hypotheses: each target history is already contiguous, and the evaluated endpoint is itself the final state.

MN-004's globally indexed ledger is frozen as `unsupported_no_effect_or_insufficient_effect`; its observed `0/24` to `7/24` 8k movement did not reach the frozen support thresholds. MN-005's canonical Multi-pass Reconstruction result is `inconclusive`, with no authorized replacement `attempt-0003`. Its Hierarchical Gate A audit is `hierarchical_gate_a_unselected`, not a falsification: ECC-006 cannot isolate hierarchy from grouping, formatting, compression, reordering, or target salience. External State Management remains a relevant hypothesis class, but an external final-state register would be too close to an ECC-006 answer oracle.

The resulting bottleneck is therefore not candidate selection on frozen ECC-006. It is a candidate-neutral workload that can expose distributed state integration while retaining deterministic diagnosis.

## Central workload question and hypothesis

**Question:** Can a deterministic workload expose a small language model's difficulty integrating the state of multiple entities when relevant updates are distributed and interleaved through context, while distinguishing that state-integration failure from failure in a deliberately small downstream rule?

**Working falsifiable hypothesis:** For matched generated cases with the same entity/state semantics and downstream rule, a distributed/interleaved regime may yield lower canonical-state and end-to-end correctness than a contiguous-history sanity regime. A later perfect-state control can determine whether any observed end-to-end deficit remains when state integration is removed from the model's task.

This is a workload hypothesis, not a claim that a failure has already been observed. State tracking/state integration remains the primary subject; MN-006 is not a general reasoning benchmark.

## Intended causal pipeline

```text
canonical source events
        ↓
canonical entity states
        ↓
canonical derived facts from a small fixed rule
        ↓
one finite canonical answer
```

The downstream rule exists for one causal-design reason. A representation that maintains entity state externally may provide state values to the model, but those values must not be identical to the evaluated answer. The model must apply the shared bounded rule; host logic must not silently apply it or return its result.

## Scope and deliberate non-goals

The first workload family isolates two changes from ECC-006:

1. contiguous target history → distributed/interleaved histories for the queried entities; and
2. endpoint-only final-state answer → a minimal deterministic decision using multiple entity states.

It deliberately keeps these dimensions simple unless a later design gate justifies an extension:

- no true parent/child hierarchy or nested scope;
- no causal propagation or dependency graph between entities;
- no noisy or ambiguous natural language;
- no commonsense or external-world knowledge;
- no cross-session/episode persistence, retrieval, RAG, tools, or planning;
- no candidate treatment, intervention comparison, measured efficacy, or model selection.

Level 3 extensions may later investigate scoped state, bounded dependency chains, or conditional transitions. They are not part of the initial implementation target.

## Workload family and controlled dimensions

Source events will use one regular, unambiguous assignment grammar. Every event changes exactly one entity's state according to the frozen transition semantics. The eventual generator must control and record at least:

- number of entities;
- updates per entity;
- number of queried and non-queried entities;
- distance between successive updates for each queried entity;
- interleaving density across entity histories;
- total event count/context length; and
- downstream-rule input count.

The primary structural property is not merely that there are more events. For every queried entity in the distributed regime, relevant updates must be separated by events for other entities. A contiguous-history Level 1 remains a sanity/control regime, not the primary comparison substrate.

The v1 state vocabulary, event grammar, answer labels, rule depth/arity, contiguous-control role, Level 1/2 profile values, and deterministic scheduler are frozen in the [semantic workload contract](workload-contract.md). The independent, pre-model [baseline inventory and measurement contract](baseline-inventory-measurement-gate.md) now freezes 32 matched pairs per profile, sequential ordinals, physical artifact hashes, runtime procedure, scoring, and interpretation. Candidate treatment remains deferred.

## Deterministic answer and diagnostic policy

The final response must have exactly one canonical value from a finite grammar. The initial design permits a small fixed label vocabulary such as decision/action labels, but not free-form explanation as the benchmark output. The final frozen contract must guarantee that each answer is unique, finite, exactly parseable, LLM-judge-free, and independent of external knowledge.

The generator/oracle must retain four distinct truth layers:

1. source events as rendered to the model;
2. final canonical state for every entity;
3. derived facts consumed by the downstream rule; and
4. the canonical answer.

This structure supports future diagnostic probes for state correctness, reasoning correctness conditional on correct state, and end-to-end correctness. A future perfect-state control may give the model canonical state plus the same bounded rule. It is a diagnostic design option only; no control is implemented or run in this phase.

## Candidate-neutrality and anti-oracle policy

MN-006 is frozen from the failure mode before selecting a treatment. It may later support several hypotheses without ranking them now:

- **Hierarchical State Representation:** distributed entity histories can make locality observable, but a hierarchy treatment must be compared with a flat control preserving source facts, membership, local/global order, and target access. It may not win through compression, deletion, reordering, target-only filtering, or answer hints.
- **External State Management:** an external representation may contain entity/state values, but never derived facts or the final decision. The host may not evaluate the downstream rule, choose an answer, or use an answer-bearing field.
- **Event-to-State Normalization:** relevant only if source semantics genuinely require canonicalization. Artificial linguistic variation will not be added to manufacture this candidate.
- **Multi-pass Reconstruction:** its MN-005 result remains `inconclusive`; it may return only under a distinct MN-006 reconstruction hypothesis with measurable artifacts and a new contract.
- **Symmetric State Partitioning:** relevant only if naturally motivated by the resulting interleaving/partition structure.

All future treatments and controls must obey these common rules:

- Source events must not contain the final answer literally or fields named `final`, `current`, `answer`, `target answer`, or equivalent answer hints.
- No representation may contain the downstream derived decision unless that semantic content is explicitly supplied in every matched condition; this is not planned for MN-006.
- Host code must not perform the bounded downstream reasoning under evaluation.
- Source facts and event provenance must be conserved across matched conditions.
- Target-only filtering, event deletion, arbitrary reordering, and unaccounted compression are prohibited unless the specific variable is predeclared, matched, and independently measured.
- The answer vocabulary and case sampling must not make one output label predictably more likely.

Known open risks include accidental answer leakage through state-field names, uneven answer-label frequencies, a rule whose answer is a transparent copy of one state value, and a flat hierarchy control that changes locality or compression. These require static validation before implementation authorization.

## Progressive difficulty

### Level 1 — distributed state sanity regime

Purpose: validate deterministic generation/oracle semantics, exact grading, answer uniqueness, and elementary integration. It uses few entities, short but real interleaving gaps, and one small shared rule. It must establish that cases are valid and solvable by the oracle; it makes no model-capability claim.

### Level 2 — primary distributed/interleaved regime

Purpose: become the future candidate-comparison substrate. It increases the number of entity histories, separation between updates of queried entities, and interleaving density while keeping event semantics and rule family fixed. Its final decision depends on multiple canonical entity states.

Promotion from Level 1 to Level 2 requires deterministic invariants, answer balance/uniqueness, source conservation, verified interleaving metrics, and a design review showing that the additional difficulty is distribution rather than a hidden semantic change.

### Level 3 — future extension only

Scoped state, bounded dependency chains, or conditional transitions require a separate justification showing why Level 2 cannot answer the next decision-relevant question. Level 3 is not designed, implemented, or measured by this milestone phase.

## Gates and next boundary

[Design Gate A](design-gate-a.md) remains the traceable initial audit. [Design Gate B](design-gate-b.md) freezes the v1 semantic decisions. The [semantic workload contract](workload-contract.md) and [v1 case schema](case-schema.md) are the authority for the deterministic generator/oracle/validator implementation; the earlier [proposed schema](proposed-case-schema.md) is retained as history. The subsequent [Baseline Inventory and Measurement Gate](baseline-inventory-measurement-gate.md) freezes the inventory and first-baseline procedure, while the [manifest](definition/baseline-inventory-v1/manifest.json) identifies the materialized authority artifacts.

**Implementation gate:** passed for a non-model generator, oracle, paired serializer, and static validator suite only. The frozen v1 contract remains independently reviewable without model output.

**Baseline measurement:** [`attempt-0001`](reports/mn-006-attempt-0001.md) completed the predeclared Llama 3.2 3B observation with all 128 requests, no infrastructure failure, and no retries. Both profiles have `0/32` contiguous and `0/32` interleaved exact correctness, each with `64/64` malformed outputs. The frozen classification is `no_usable_locality_failure_signal_under_v1_baseline`; the perfect-state diagnostic is ineligible and candidate treatment remains blocked. The later [Response-Channel Gate](response-channel-gate.md) authorizes only a separate grammar-constrained `attempt-0002` measurement with unchanged workload/public bytes/evaluator, not an intervention or an infrastructure retry.

## Explicit boundary

The canonical attempt retains immutable model-run evidence but no intervention evidence: one Llama server executed `attempt-0001`; no Qwen call, treatment renderer, external state register, hierarchy condition, multi-pass rerun, or candidate efficacy claim exists. The materialized inventory remains workload authority and the raw attempt records remain separate measured evidence.
