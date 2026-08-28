# MN-003 — Effective Context Capacity

## Status

Completed bounded direct-context measurement and synthesis phase. Canonical definitions, retained raw evidence, validators, and reports for ECC-001 through ECC-007 remain immutable. MN-003 does not select or implement a retrieval, RAG, memory, summarization, compression, routing, embedding, semantic-search, external-state, or other context-management architecture.

The canonical conclusion is recorded in the [MN-003 capability synthesis](reports/mn-003-synthesis.md). It closes the measurement phase with outcome **C**: no additional ECC experiment is justified before a separate intervention-design/hypothesis milestone, and no intervention is selected.

## Research question

For an MCB-qualified small local model, how does reliable task performance change as controlled direct context increases while task-relevant information remains controlled? Effective Context Capacity is a measured task-reliability range, distinct from advertised context-window size.

## Canonical evidence map

- **ECC-001:** easy marked single-fact Retrieval is stable for both Llama 3.2 3B and Qwen3-4B through 16,384 tested tokens.
- **ECC-002:** same-template semantic interference yields a monotonic Llama retrieval decline, while Qwen remains stable at the tested resolution.
- **ECC-003/ECC-004:** Llama late-position sensitivity in the confusable retrieval task is a replicated bounded long-context effect; its output diagnostics do not identify distractor selection as the cause.
- **ECC-003/ECC-005:** Qwen has no observed early/late position effect in the retained full and fresh-case control matrices.
- **ECC-006:** Llama has a four-update State Tracking floor at short context and monotonic decline to zero at 8k/16k under the fixed task contract.
- **ECC-007:** Qwen two-hop causal reachability has one isolated 8k false positive and a non-monotonic recovery at 16k; it does not establish a stable causal degradation boundary.

These results are model- and task-specific. ECC-006 is Llama-only and ECC-007 is Qwen-only, so they cannot be used to rank State Tracking against Causal Reasoning across models.

## Scope and next research boundary

The measured baseline uses direct, unmodified context, deterministic model-token-aware construction, exact evaluation, and retained evidence. `research/experiments/baselines/` contains comparison/reference evidence such as frozen MN-002; this `prototypes/` location contains scoped exploratory research and its evidence remains separate from `src/mong_nhiem/`.

The strongest candidate limitation for a future architecture hypothesis is the Llama State Tracking bottleneck. [MN-004 State Representation Intervention Design](../mn-004-state-representation-intervention/README.md) is prepared to formulate—rather than implement—a specified explicit-state hypothesis against the frozen ECC-006 direct-context baseline. That is a candidate hypothesis, not an adopted architecture. MN-003 is closed for further ECC measurement work; the isolated ECC-007 8k miss has no decision-critical impact and does not justify ECC-008.
