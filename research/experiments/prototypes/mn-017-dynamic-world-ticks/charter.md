# Gate A Charter — Milestone MN-017: Dynamic World Ticks & Hierarchical Planning

## 1. Context & Motivation

Prior milestones (**MN-009** through **MN-016**) established foundational substrates for small language models ($<4\text{B}$ parameters):
- Context Scaffolding (MN-009) and Iterative Working Sets (MN-010) under bounded forward passes ($\le 512$ tokens).
- Backtracking & Memento Rollback (MN-013) to escape dead-end traps.
- Engine-level GBNF Grammar-Constrained Decoding (MN-014) eliminating syntax collapse.
- Dual-Layer Dynamic Affordance Steering (MN-015) suppressing deadlock cycles.
- Host-Authoritative Episodic Memory & AutoDream Consolidation (MN-016) eliminating historical amnesia across extended horizons ($T = 20-50$ steps).

However, in all prior milestones, the environment operated under **passive turn synchrony**: world state mutated *strictly and solely* upon agent action dispatch. In real-world multi-entity simulations (the explicit prerequisite for Milestone **MN-018: Stateful Simulated Microworld Evolution**), environments exhibit **independent, multi-rate temporal dynamics**:
1. **Asynchronous Environmental Concurrency**: Entities mutate, leases expire, queues process, and resources deplete along an independent simulation clock ($t_{world}$) between agent turns.
2. **Goal Divergence & Horizon Jumping (Failure Mode 3)**: When small models are presented with a global multi-stage objective ($K = 3-5$ phases) alongside dynamic environmental feedback, attention degrades. Models commit unearned *Horizon Jumping* (attempting final actions before prerequisite completion) or prematurely declare success.
3. **Context Inflation vs Environmental Concurrency**: Attempting to feed raw chronological event streams of asynchronous world mutations into the prompt causes catastrophic context explosion ($> 512$ tokens), triggering format collapse and severe hallucinations.

**MN-017 establishes the Dynamic World Ticks & Hierarchical Planning architecture**:
- **Host World Clock & Asynchronous Tick Engine**: Independent discrete clock ($t_{world}$) with monotonic entity versioning ($v_{entity}$) and deterministic state transition rules.
- **Hierarchical Goal Decomposition & Prerequisite Phase Gates**: High-level mission graph ($G_1 \rightarrow G_2 \dots \rightarrow G_K$) evaluated strictly by Host symbolic predicates. The model only receives the active sub-goal $G_k$ and localized affordances ($\le 512$ tokens), mathematically preventing horizon jumping via dynamic GBNF masking.
- **Stale-State Reconciliation & Concurrency Invariant Protection**: Host validates entity read versions ($v_{read} == v_{current}$). If an asynchronous world tick mutated the target entity during the turn, the Host blocks illegal mutation and emits an atomic delta refresh notice.

---

## 2. Falsifiable Hypotheses

### Hypothesis 1: Elimination of Goal Divergence & Horizon Jumping ($H_1$)
Under Host-Authoritative Hierarchical Goal Decomposition and dynamic GBNF phase-gate affordances, small models (`Qwen3.5-2B-Q4_K_M`) will achieve **$\ge 90.0\%$ task completion** across multi-phase missions ($K = 3-5$ sub-goals, $T = 15-35$ steps), delivering an absolute gain of **$\ge +40.0\%$** over flat-prompt baselines (Arm 1) where unconstrained models exhibit premature resolution or sequence violations.

### Hypothesis 2: Environmental Concurrency & Stale-State Immunity ($H_2$)
In environments with asynchronous World Ticks ($\Delta t_{world} = 1-3$ ticks per agent turn):
- Arm 3 (Dual-Engine MN-017) will achieve **$0.0\%$ stale-state mutation violations** and **$0.0\%$ state corruption events**.
- When environmental pre-conditions expire (e.g. lease expired during planning), Arm 3 will autonomously detect version drift and refresh state in $100.0\%$ of occurrences.

### Hypothesis 3: Bounded Forward-Pass Ceiling & Sub-Second Latency SLA ($H_3$)
Because the Host delivers only the active sub-goal $G_k$, immediate local entity cards, and delta notices:
- **100.0% of forward-pass turns** will strictly observe the prompt ceiling $\le 512$ tokens (mean prompt budget $\le 384$ tokens).
- Mean turn latency will remain **$< 1000\text{ ms}$** on local `llama-server.exe` hardware.

---

## 3. Scope & Non-Goals

### In Scope
1. Implementation of `DynamicWorldEngine` and `WorldClock` (monotonic entity versioning, TTL decay, resource consumption, asynchronous background tick execution).
2. Implementation of `HierarchicalPlanner` and `MissionGraph` (DAG of sub-goals, Host predicate validation, active sub-goal context scoping $\le 128$ tokens).
3. Implementation of `ConcurrencyGuard` and `StaleStateDetector` (read version validation, delta generation, illegal mutation blocking).
4. Implementation of `DynamicAffordanceCompiler` (GBNF grammar restricted strictly to active sub-goal affordances).
5. Implementation of `MN017Orchestrator` integrating components into an end-to-end execution loop.
6. 40-case long-horizon concurrent benchmark corpus ($K=3-5$ phases, $T=15-35$ turns) across 3 domains (Infrastructure Migration, Asset Logistics, System Registry).
7. Dual-track evaluation: Track 1 (Simulator) and Track 2 (Real Model Inference on `Qwen3.5-2B`).

### Explicit Non-Goals
1. No fine-tuning, LoRA, or weight alterations to language models.
2. No external runtime dependencies (zero third-party vector databases, embeddings, or heavyweight frameworks; 100% Python Standard Library).
3. No speculative continuous multi-agent physics simulations (deferred to MN-018 and subsequent milestones).
4. No code promotion to `src/mong_nhiem/` prior to Gate D disposition review.
