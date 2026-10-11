# MN-020: Multi-Agent Symbiosis & Distributed Cognitive Governance

## 1. Master Strategic Intent

Milestone MN-020 investigates the scaling of Host-Authoritative Cognitive Governance from a solitary reasoning agent (**MN-019**) to **concurrent multi-agent symbiosis** operating over shared microworld state graphs.

In distributed cyber-physical environments, autonomous microservices, and collaborative robotic clusters, solitary execution does not exist. Multiple agents, automated subroutines, and supervisory actors act asynchronously and concurrently upon shared resources. Without host-level cognitive arbitration, independent Small Language Models ($< 4\text{B}$) suffer catastrophic collapse due to:
1. **Resource Contention & Race Conditions**: Uncoordinated concurrent mutations that corrupt physical conservation invariants and violate state consistency.
2. **Mutual Plan Invalidation**: Interleaved actions where Agent A destroys the operational preconditions required for Agent B's sub-goal execution.
3. **Communication Context Explosion**: Free-form unconstrained inter-agent dialogue causing prompt lengths to rapidly exceed the strict $\le 512$ token ceiling.
4. **Git Repository Bloat**: Accumulating thousands of loose JSON audit logs. MN-020 introduces a standard library `.zip` packaging protocol (`audit_logs.zip`), reducing git tree footprint by $>99\%$ while preserving 100% cryptographic reproducibility.

MN-020 proves that a **Host Concurrency Arbiter & Lease Manager**, paired with **Dynamic Multi-Affordance GBNF Masking**, **Scoped AutoDream Projections**, and a **Compound Causal DAG**, enables homogeneous pairs of lightweight models ($2\times \text{Qwen3.5-2B}$) to achieve $\ge 85.0\%$ collaborative resolution without race collisions.

---

## 2. Experimental Architecture

The milestone is structured around three comparative arms evaluated across 60 multi-agent benchmark scenarios spanning 3 heterogeneous domains:
1. **Collaborative Smart Microgrid Balancing**: 2 agents jointly balancing variable renewable generation, industrial feeder loads, and battery storage under peak bus voltage limits.
2. **Concurrent Orbital Maintenance & Docking**: 2 agents concurrently coordinating reaction control thrusters, power redistribution, and solar array alignment during automated rendezvous.
3. **Joint Fleet Logistics & Cold-Chain Dispatch**: 2 agents concurrently managing transport routing, charging station queues, and auxiliary refrigeration units without exceeding depot power thresholds.

| Arm ID | Configuration | Concurrency Control | Affordance Steering | Context Delivery |
| :---: | :--- | :--- | :--- | :--- |
| **Arm 1** | Flat Baseline | Uncoordinated Free Execution | Raw unconstrained prompt | Full shared state dump |
| **Arm 2** | Independent Control | Independent Single-Agent Grammars | Single-agent GBNF | Global unpruned Fact Cards |
| **Arm 3** | Host Symbiotic Governance | Host Optimistic Lease Arbiter | Dynamic Multi-Agent GBNF | Scoped AutoDream Projections |

---

## 3. Governance and Promotion Boundaries

- **Quarantine Invariant**: 100% of MN-020 prototype code, schemas, benchmarks, and run traces remain strictly quarantined in `research/experiments/prototypes/mn-020-multi-agent-symbiosis/`.
- **Zero Silent Promotion**: No code will be promoted to `src/mong_nhiem/` during prototype evaluation.
- **Evidence Packaging Standard**: All episode audit logs are compressed using Python standard library `zipfile` into `audit_logs.zip` per run, with cryptographic SHA-256 fingerprints recorded in `post-run-freeze-manifest.json`.
