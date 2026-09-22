# MN-009: Scoped Context Delivery Engine

MN-009 investigates host-side deterministic context scaffolding to enable small language models (<4B) to operate reliably over extensive information spaces without experiencing the severe long-context degradation identified in MN-003, MN-004, MN-007, and MN-008.

## Direction

- **Target Component:** `research/experiments/prototypes/mn-009-context-scaffolding/src/packer.py` (candidate for `src/mong_nhiem/context/packer.py`).
- **Core Mechanism:** Greedy Budget Knapsack with lexical salience scoring and natural boundary slicing (paragraphs/sentences).
- **Target Constraint:** Strict hard ceiling $\le 512$ tokens under local `llama-tokenize.exe` (Llama-3.2-3B-Instruct).
- **Governance Invariant:** Zero code promoted into `src/mong_nhiem/` until Gate D disposition review formally approves promotion.

## Navigation

- [Gate A: Charter & Hypothesis](charter.md)
- [Gate B: Measurement Contract](gate-b-contract.md)
- [Reports](reports/)
