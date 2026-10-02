# MN-009: Scoped Context Delivery Engine

## Context & Navigation

- Canonical Research Base: [00-mong-nhiem](../../../00-mong-nhiem.md)
- System Architecture: [architecture](../../../concepts/architecture.md)
- Current Milestone State: [current-state](../../../current-state.md)
- Architectural Decisions: [decisions](../../../decisions/decisions.md)

MN-009 investigates host-side deterministic context scaffolding to enable small language models (<4B) to operate reliably over extensive information spaces without experiencing the severe long-context degradation identified in [MN-003](../mn-003-effective-context-capacity/README.md), [MN-004](../mn-004-state-representation-intervention/README.md), [MN-007](../mn-007-state-recovery-operating-region/README.md), and [MN-008](../mn-008-external-state-management/README.md).

---

## Technical Direction

- **Target Component:** [`src/packer.py`](src/packer.py) and [`src/slicer.py`](src/slicer.py) (candidates for `src/mong_nhiem/context/`).
- **Core Mechanism:** Greedy Budget Knapsack with single-pass lexical salience scoring, Anchor-and-Spoke paragraph/sentence chunking, AST adaptive inlining, and $k$-hop BFS graph induction.
- **Target Constraint:** Strict hard ceiling $\le 512$ tokens under local `llama-tokenize.exe` (`Llama-3.2-3B-Instruct-Q4_K_M.gguf`).
- **Governance Invariant:** Zero code promoted into `src/mong_nhiem/` until Gate D disposition review formally approves promotion.

---

## Artifact Navigation

- [Gate A: Charter & Hypothesis](charter.md)
- [Gate B: Measurement Contract](gate-b-contract.md)
- [Gate C: Execution Report](reports/mn009-execution-report.md)
- [Gate D: Disposition Review](gate-d-disposition-review.md)
- Evaluation Corpus: [`definition/corpus-v1/`](definition/corpus-v1/)
- Benchmark Runner: [`scripts/mn009_executor.py`](scripts/mn009_executor.py)
- Unit Tests: [`tests/unit/test_mn009_packer.py`](../../../../tests/unit/test_mn009_packer.py)
