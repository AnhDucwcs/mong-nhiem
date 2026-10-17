# MN-023 — Minimal Controlled Microworld & Epistemic Invariant Verification Under Asymmetric Information

## 1. Overview

Milestone MN-023 investigates the mathematical and behavioral correctness of host-managed multi-agent state tracking and cognitive memory under conditions of:
- **Asymmetric observation masks:** Each agent observes only a subset of the global microworld state.
- **Hidden state & secrets:** Information partitions ensuring private entity states cannot be accessed without explicit in-world discovery actions.
- **Divergent subjective beliefs:** Agents maintaining distinct epistemic models without forced premature consensus.
- **Causal pivot events:** Pivotal actions that alter the world state and propagate causal dependencies through the topological DAG.

MN-023 adheres strictly to the invariant that **Mộng Nhiễm is an empirical SLM operational capability platform, not a game product.** The microworld implemented here is a minimal controlled experimental testbed designed to isolate and falsify specific cognitive architecture hypotheses ($H_1$ through $H_5$).

---

## 2. Directory Structure

```text
mn-023-minimal-epistemic-microworld/
├── README.md                 # Milestone overview and operational guide
├── charter.md                # Formal Gate A research questions and falsification criteria
├── gate-b-contract.md        # Frozen Gate B quantitative acceptance bounds
├── src/                      # Minimal experimental benchmark harness and scenarios
├── tests/                    # Unit tests for epistemic masks and microworld invariants
└── reports/                  # Generated academic evaluation reports (post-run)
```

---

## 3. Production Dependencies

In strict compliance with Mộng Nhiễm governance rules, MN-023 does not duplicate previous prototypes. It consumes verified production modules directly from `src/mong_nhiem/`:
- `mong_nhiem.core.vector_clock.VectorClock`
- `mong_nhiem.core.invariants.ConservationInvariantGuard`
- `mong_nhiem.knowledge.causal_dag.CausalEventDAG`
- `mong_nhiem.knowledge.epistemic.EpistemicReconciler`
- `mong_nhiem.orchestration.arbiter.MultiResourceArbiter`
- `mong_nhiem.orchestration.consensus.StarConsensusHub`
- `mong_nhiem.extensions.autodream.consolidator.FrontierBranchPruner`
- `mong_nhiem.extensions.autodream.fact_cards.FactCardProjector`
- `mong_nhiem.runtime.microworld.AuthoritativeMicroworld`
