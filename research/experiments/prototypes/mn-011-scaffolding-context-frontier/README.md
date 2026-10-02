# MN-011: Scaffolding-Assisted Effective Context Frontier

## Context & Navigation

- Canonical Research Base: [00-mong-nhiem](../../../00-mong-nhiem.md)
- System Architecture: [architecture](../../../concepts/architecture.md)
- Conceptual Taxonomy: [ECC vs NCC](../../../concepts/ecc-vs-ncc.md)
- Milestone Roadmap: [roadmap](../../../roadmap.md)
- Architectural Decisions: [decisions](../../../decisions/decisions.md)
- Predecessors:
  - [MN-003: Effective Context Capacity](../mn-003-effective-context-capacity/README.md) (Native direct-attention baseline)
  - [MN-009: Scoped Context Delivery Engine](../mn-009-context-scaffolding/README.md) (Single-shot scaffolding)
  - [MN-010: Iterative Context Working Set Loop](../mn-010-iterative-context-loop/README.md) (Multi-turn iterative coordinator)

---

## 1. Overview & Research Motivation

Milestones **MN-009** and **MN-010** developed and promoted the production context scaffolding engine (`src/mong_nhiem/context/`), demonstrating that small models (<4B) achieve 100% accuracy on retrieval and multi-hop reasoning when restricted to small, host-managed working sets ($\le 512$ tokens per forward pass).

However, those milestones evaluated fixed, conservative budget boundaries ($512$ tokens) on synthetic and curated unit tasks. Milestone **MN-011** marks the formal reactivation of the **Effective Context Capacity (ECC)** track.

Rather than evaluating raw native attention over unconstrained document streams (which MN-003 proved collapses beyond $512$ tokens), MN-011 employs the promoted scaffolding subsystem as a standardized measurement lens to map:
1. **The Scaffolding Frontier Curve:** How downstream reasoning accuracy varies as the per-turn knapsack budget $B$ scales across $B \in \{256, 512, 1024, 2048\}$ tokens.
2. **Causal Reasoning Resilience:** Whether scaffolding eliminates the long-context degradation and false positive anomalies observed in complex multi-entity causal reachability (ECC-007).
3. **Cross-Model Capacity Efficiency:** A comparative quantification of context conversion efficiency ($\eta = \text{Utilized} / \text{Fed}$) across qualified model architectures (`Qwen3.5-2B`, `Llama-3.2-3B`, `Qwen3-4B`).

---

## 2. Directory Structure

```
research/experiments/prototypes/mn-011-scaffolding-context-frontier/
├── README.md               # Milestone overview and navigation (this file)
├── charter.md              # Gate A Charter and scientific hypotheses
├── gate-b-contract.md      # Gate B Measurement contract and evaluation protocol (planned)
├── definition/             # Frozen benchmark corpus and manifests (planned)
├── src/                    # Experimental evaluation wrappers (planned)
├── scripts/                # Execution runners (planned)
├── runs/                   # Immutable execution artifacts and telemetry (planned)
└── reports/                # Gate C execution reports and analysis (planned)
```

---

## 3. Milestone Lifecycle & Gates

- **Gate A (Charter & Falsifiable Hypothesis):** [charter.md](charter.md) — Active.
- **Gate B (Measurement Contract & Corpus Design):** Scheduled.
- **Gate C (Execution & Empirical Verification):** Scheduled.
- **Gate D (Disposition Review & Synthesis):** Scheduled.
