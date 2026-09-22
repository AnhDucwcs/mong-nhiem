# MN-008 — External State Management

## Status

**Completed and closed — Gate D disposition review complete (`unpromoted_hypothesis_unsupported`).**

MN-008 succeeds MN-007 following its formal closure at `no usable operating region in bounded landscape` ([mn007-calibration-report.md](../mn-007-state-recovery-operating-region/mn007-calibration-report.md)). Across MN-003 (ECC-006), MN-004, MN-005, MN-006, and MN-007, small models (<4B parameter class, specifically `Llama-3.2-3B-Instruct`) consistently fail to maintain and recover multi-entity state purely within implicit attention context (floor performance $\le 22.2\%$).

MN-008 abandons the attempt to force small models to act as in-context latent state engines. Instead, it offloads deterministic state tracking to an external host engine, supplying compact, structured state snapshots for downstream non-trivial conditional/causal evaluation.

## Research Question

> For the qualified small-model/runtime (`Llama-3.2-3B-Instruct`), does decoupling deterministic state tracking to a host-managed state engine (supplying structured state snapshots) reliably enable downstream non-trivial conditional reasoning compared to an in-context baseline receiving the same raw event stream?

## Architectural Foundation: Deterministic Core × LLM Reasoning

MN-008 adopts the architectural separation proven in large-scale production systems (such as Alibaba's *Open Code Review*):

1. **Deterministic Host State Engine ($O(1)$ amortized):** Ingests raw state-transition event streams, executes exact state updates in host memory via verified logic (reusing hardened `replay()` from MN-007), and emits minimal scoped snapshots for queried entities.
2. **Downstream LLM Conditional Reasoning:** Consumes the compact snapshot and evaluates a 4-branch mutually exclusive decision rule matrix ($2 \times 2$). The LLM is evaluated strictly on conditional branch selection, escaping both the latent state-tracking bottleneck and the trivial copy-paste lookup trap identified in MN-005.

## Required Milestone Sequence

```text
Gate A: Causal hypothesis, 3 conceptual arms, boundary framework, Latin Square counterbalancing
    ->
Gate B: Measurement contract, 24-case balanced corpus specification, exact evaluator schema
    ->
Gate C: Deterministic materialization, llama.cpp runner execution, artifact hashing, comparative report
    ->
Gate D: Promotion and disposition review (evaluate promotion into src/mong_nhiem/)
```

## Preserved Measurement Principles

1. **Anti-Tautology Rule:** The host state snapshot contains only raw entity states (`E1=S0; E2=S1`). It must never contain pre-evaluated rule outcomes, action recommendations, or branch labels.
2. **Neutral Vocabulary:** Reuses the frozen, single-token neutral state vocabulary `STATE_VOCABULARY = ("S0", "S1")` from MN-007 to avoid pre-training semantic prior leakage.
3. **Deterministic Latin Square Counterbalancing:** To ensure fair comparison across arms and prevent memorization or positional bias, mapping between state pairs and action tokens is counterbalanced across cases via a deterministic Latin Square of order 4, frozen during materialization.
4. **Exact Deterministic Evaluation:** LLM responses are constrained to a strict single action token (`ACTION_0` .. `ACTION_3`) and evaluated via exact boundary regex against materialized oracle records.

## Inherited Immutable Evidence

- **MN-002:** MCB v0.3.0 qualification baseline (`Llama-3.2-3B-Instruct-Q4_K_M`).
- **MN-003 (ECC-006):** Monotonic state-tracking collapse under context load (`0/6` at 8k/16k).
- **MN-004:** Ineffective ledger representation intervention (`unsupported_no_effect_or_insufficient_effect`).
- **MN-005:** Inconclusive Multi-pass Reconstruction (`1/6` Arm C vs `0/6` active control; identified the lookup tautology trap).
- **MN-006:** Response-channel qualification passed (Q0 `9/9`), but contiguous task-bearing floor blocked locality comparison (Q1 `1/9`).
- **MN-007:** Calibration rerun classified all 6 landscape cells as `floor` ($\le 22.2\%$). In-context contiguous state recovery rejected on Llama 3.2 3B.
