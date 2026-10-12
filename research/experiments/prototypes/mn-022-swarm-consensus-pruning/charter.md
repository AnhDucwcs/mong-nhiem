# Milestone Charter: MN-022 — Asynchronous Multi-Agent Swarm Governance & Consensus Pruning

## 1. Executive Summary & Research Motivation

Milestone MN-021 verified that dyadic multi-agent teams ($M = 2$) operating under partial observation and stochastic environmental shocks achieve 100.0% task resolution when governed by a Host Multi-Parent Causal Event DAG and Epistemic Discrepancy Reconciler. However, MN-021 relied on two simplifying assumptions:
1. Turn-Synchronous Lockstep Execution: Agents took strictly alternating discrete turns ($A \to B \to A \to B$), eliminating concurrency drift.
2. Pairwise Communication ($M = 2$): Information exchange, lease management, and epistemic reconciliation scaled trivially in $O(1)$ space.

In real-world decentralized cyber-physical environments, scaling coordination to asynchronous agent swarms ($M \ge 5$) introduces three fundamental barriers for small open-weights language models ($< 4\text{B}$):
1. Quadratic Gossip Context Bloat ($O(M^2)$): Unstructured peer-to-peer event broadcasting across $M=5$ agents leads to prompt lengths exceeding the strict $\le 512$ token cognitive capacity ceiling within two interaction cycles.
2. Network Latency & Asynchronous Clock Drift ($\tau_i \in [0, 5]$ ticks): Transmission delays cause agents to formulate proposals against stale world states, triggering split-brain race conditions and conflicting mutations.
3. Byzantine & Noisy Node Vulnerability: A lagging, dropped, or corrupted node generating invalid physical mutations risks stalling or poisoning the entire swarm unless isolated by deterministic host admission gates.

MN-022 establishes a host-governed **Asynchronous Swarm Coordination & Consensus Pruning Substrate**, replacing quadratic peer gossip with a star-topology Host Consensus Hub, TTL-guarded multi-resource leases, and topological DAG consensus pruning ($O(M^2) \to O(M)$).

## 2. Research Questions & Hypotheses

### Primary Research Questions
- **RQ1 (Asynchronous Swarm Efficacy):** Can small language models ($M = 5$, $< 4\text{B}$) achieve task resolution $\ge 85.0\%$ in multi-agent environments subjected to stochastic transmission latency ($\tau_i \in [0, 5]$ ticks)?
- **RQ2 (Token Bound Invariant):** Does topological branch pruning and star-topology hub consolidation maintain prompt lengths strictly $\le 512\text{ tokens}$ across all 5 agents without cognitive degradation?
- **RQ3 (Zero Mutation Contagion):** Does host concurrency arbitration with TTL lock expiration and Byzantine proposal filtering guarantee zero committed physical invariant breaches and zero race collisions?
- **RQ4 (Cross-Model Heterogeneity):** Can a heterogeneous swarm composed of diverse architectures (Qwen3.5-2B, Qwen3-4B, and Llama-3.2-3B) coordinate effectively under host consensus without prompt format divergence or deadlock?

### Formal Hypotheses
- **$H_1$ (Coordination Superiority):** Arm 3 (Host Consensus Hub & DAG Pruning) achieves a Task Resolution Rate $\ge 85.0\%$ across $N = 80$ standardized scenarios, exceeding Arm 2 (Unpruned Gossip Control) by $\Delta \ge +40.0\%$.
- **$H_2$ (Cognitive Token Ceiling):** Across all $M = 5$ agents and all discrete ticks, the maximum prompt token count satisfies $\max(T_{\text{prompt}}) \le 512\text{ tokens}$.
- **$H_3$ (Physical & Concurrency Invariant):** The committed world state maintains zero physical conservation breaches ($B = 0$) and zero unmanaged race collisions ($C = 0$).
- **$H_4$ (Topological Compaction Ratio):** The AutoDream Swarm pruning engine achieves a context compaction ratio $\ge 70.0\%$ compared to the raw unpruned gossip trace.
- **$H_5$ (Turn Latency SLA):** Mean turn latency across all model evaluations remains $< 1000\text{ ms}$.

## 3. Scope & Non-Goals

### In Scope
- Swarm scale $M = 5$ concurrent autonomous agents.
- Stochastic network latency model: packet arrival delay $\tau_i \in [0, 5]$ ticks with $10\%$ out-of-order packet reordering.
- Star-topology Host Consensus Hub with Vector Clock causal tracking.
- Topological branch pruning: retaining only active frontier DAG nodes and compacting finalized sub-graphs.
- Multi-Resource Lease Arbiter with discrete TTL expiration and lock stealing.
- Byzantine Action Filter: admission control intercepting syntactically invalid or conservation-violating proposals.
- Standardized $N = 80$ evaluation corpus across 3 cyber-physical domains:
  1. Smart Microgrid Swarm Load Balancing ($N = 27$)
  2. Multi-Depot Autonomous Fleet Logistics ($N = 27$)
  3. Distributed High-Performance Cluster Scheduling ($N = 26$)
- Dual-Track Evaluation: Track 1 (Host Simulator) and Track 2 (Homogeneous $5 \times \text{Qwen3.5-2B}$ on `llama-server.exe`).
- Heterogeneous Swarm Cross-Model Evaluation: Mixture of Qwen3.5-2B, Qwen3-4B, and Llama-3.2-3B.
- Complete evidence archival in `audit_logs.zip` (0 loose JSON files).

### Non-Goals
- Large-scale swarms ($M \ge 20$): Defers to future distributed horizons.
- Direct peer-to-peer blockchain consensus (e.g., Raft/Paxos among LLMs): Host preserves single-source-of-truth state authority.
- Continuous multi-modal inputs or audio/video streaming.
- Promotion into production `src/mong_nhiem/`: Prototype remains 100% quarantined until cumulative promotion phase post-MN-022.
