# MN-009 Gate A: Charter & Scientific Hypothesis

## Context & Navigation

- Canonical Knowledge Base: [00-mong-nhiem](../../../00-mong-nhiem.md)
- System Architecture: [architecture](../../../concepts/architecture.md)
- Current Milestone State: [current-state](../../../current-state.md)
- Architectural Decisions: [decisions](../../../decisions/decisions.md)
- Predecessors:
  - [MN-003: Effective Context Capacity](../mn-003-effective-context-capacity/README.md)
  - [MN-004: State Representation Intervention](../mn-004-state-representation-intervention/README.md)
  - [MN-007: State Recovery Operating Region](../mn-007-state-recovery-operating-region/README.md)
  - [MN-008: External State Management](../mn-008-external-state-management/README.md)
- Successors & Downstream Artifacts:
  - [MN-009 Gate B Measurement Contract](gate-b-contract.md)
  - [MN-009 Gate C Execution Report](reports/mn009-execution-report.md)
  - [MN-009 Gate D Disposition Review](gate-d-disposition-review.md)

---

## 1. Problem Statement

Empirical evidence across [MN-003](../mn-003-effective-context-capacity/README.md), [MN-004](../mn-004-state-representation-intervention/README.md), [MN-007](../mn-007-state-recovery-operating-region/README.md), and [MN-008](../mn-008-external-state-management/README.md) established that `Llama-3.2-3B-Instruct` suffers catastrophic capability loss on complex tasks (state tracking, multi-entity reasoning, conditional conjunction) as context expands beyond 512 tokens, collapsing to 0% accuracy at 8,192 tokens. Furthermore, feeding 8k-16k direct tokens incurs severe runtime latency (~18-25s per call on consumer 4GB VRAM hardware) and frequent KV-cache evictions.

Small models (<4B) cannot reliably manage their own global context in-context. A host-side deterministic scaffolding system is strictly required.

---

## 2. Falsifiable Hypothesis

A deterministic, CPU-bound Lexical Salience Knapsack Packer operating on natural semantic boundaries (paragraphs/sentences) can compress an unstructured document stream of $2\text{k} - 32\text{k}$ tokens into a strictly bounded $\le 512$-token context window such that:

1. **Hard Budget Invariant:** Exactly $100\%$ ($30/30$) of packed outputs measure $\le 512$ tokens under the model's exact tokenizer (`llama-tokenize.exe`).
2. **Boundary Preservation:** $0$ sentences or structural fields are truncated midway.
3. **Information Salience:** Target query-relevant facts are preserved with $\ge 93.3\%$ recall ($\ge 28/30$ cases).
4. **Runtime Overhead:** Mean host packaging time is $< 15\text{ ms}$ on CPU, while reducing inference Time-to-First-Token (TTFT) by $\ge 80\%$ compared to direct 8k ingestion.

---

## 3. Scope & Non-Goals

- **In Scope:**
  - Prototype implementation in [`src/packer.py`](src/packer.py) and [`src/slicer.py`](src/slicer.py).
  - Prefix-aligned system headers for KV prompt caching.
  - Deterministic evaluation corpus and offline unit tests ([`tests/unit/test_mn009_packer.py`](../../../../tests/unit/test_mn009_packer.py)).
  - Exact tokenization measurement against local `llama-tokenize.exe`.
- **Out of Scope (Non-Goals):**
  - External vector databases, embedding models, or neural rerankers (VRAM and dependency bloat prohibited).
  - Premature promotion into `src/mong_nhiem/context/` prior to Gate D disposition approval.

---

## 4. Promotion Criteria (Gate D Gatekeeper)

Source code may only be promoted into `src/mong_nhiem/context/packer.py` and `src/mong_nhiem/context/slicer.py` when:
1. All 5 frozen support rules of [Gate B](gate-b-contract.md) are satisfied without exception.
2. Zero regression or token overflow occurs across the entire benchmark matrix.
3. The formal [Gate D Disposition Review](gate-d-disposition-review.md) is approved.
