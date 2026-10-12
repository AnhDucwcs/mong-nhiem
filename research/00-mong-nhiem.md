# Mộng Nhiễm

Mộng Nhiễm researches reliable small-model use over information and context spaces beyond a model's current effective capability.

## Direction

Comparative definitions and architectural principles are formalized in [ECC vs NCC](concepts/ecc-vs-ncc.md). Both directions strictly adhere to Mộng Nhiễm's invariant principle: **no fine-tuning, no weight modification, and no architectural alteration to the model**; the model is maintained strictly as an unchanged black-box reasoning engine.

- **Effective Context Capacity (ECC) — Utilization:** optimize useful operation over a fixed native context window through an external context management layer (structured decomposition, external state tracking, noise filtering, and task-aligned restructuring).
- **Native Context Capacity (NCC) — Expansion:** enable reliable operation over information spaces far exceeding the model's native effective context via an external context substrate (*large external memory + bounded native context + iterative access*).

State consistency, positional degradation, context overload, and reasoning over distributed information are research concerns, not selected solutions. MN-001 is complete. MN-002 is complete and freezes MCB v0.3.0 as the capability-qualification baseline. MN-003 completed its bounded direct-context measurement and synthesis phase. MN-004 then tested one explicit state-representation intervention and closed without meeting its frozen efficacy thresholds; no architecture was promoted. MN-005 is completed and closed for further ECC-006 candidate efficacy work: its canonical Multi-pass result is `inconclusive` (`1/6` Arm C versus `0/6` active control; `D=+1`), no `attempt-0003` is authorized, and its Hierarchical audit is `hierarchical_gate_a_unselected`. MN-006's first frozen Llama baseline is protocol-valid but yields a shared malformed-output floor (`0/32` in both schedules and profiles). Its separately frozen grammar-constrained `attempt-0002` is also protocol-valid: all responses parse but every response is `INVALID`, yielding `16/32` in both schedules and profiles. Neither establishes a locality-sensitive state-integration failure region; no candidate treatment has been created.

MN-006 is now formally [completed and closed](experiments/prototypes/mn-006-distributed-state-integration/milestone-closure.md) at `measurement_interface_blocked` for the qualified model/runtime. Its direct ordered two-entity final-state-vector qualification was `protocol_valid` / `direct_state_vector_interface_blocked`: Q0 exact response competence passed `9/9`, while Q1 contiguous task-bearing recovery passed only `1/9` under the frozen exact `18/18` requirement. The response channel is therefore qualified, but the frozen Level 2 contiguous workload does not provide the control capability floor needed for a locality comparison. Locality remains unmeasured and no intervention is authorized.

MN-007 is completed and closed: [State Recovery Operating Region](experiments/prototypes/mn-007-state-recovery-operating-region/README.md). Its clean 108-case calibration rerun (`calibration-run-0002`) classified all six cells as `floor` ($C_i \le 4/18$). Its outcome is `no usable operating region in bounded landscape`. In-context contiguous state recovery without explicit support is rejected for Llama 3.2 3B; no adaptive tuning within MN-007 is authorized.

MN-008 is completed and closed: [External State Management](experiments/prototypes/mn-008-external-state-management/README.md). Its canonical execution scored 2/24 on Arm C, failing primary efficacy; its Gate D disposition is `unpromoted_hypothesis_unsupported`. Zero code promoted into `src/mong_nhiem/`.

MN-009 is completed and promoted: [Scoped Context Delivery Engine](experiments/prototypes/mn-009-context-scaffolding/README.md). It established deterministic context scaffolding (<=512 tokens) over large knowledge spaces ($2\text{k}-32\text{k}$ tokens) without silent truncation, earning Gate D promotion into `src/mong_nhiem/context/`.

MN-010 is completed and promoted: [Iterative Context Working Set Loop](experiments/prototypes/mn-010-iterative-context-loop/README.md). It established host-coordinated multi-turn working set dispatch over large external corpora ($32\text{k}+$ tokens) under strict $\le 512$ token forward passes and $\le 3$ turn circuit breaker safety, resolving multi-hop transitive dependencies with 100% accuracy (30/30 vs 0/30 baseline), earning Gate D promotion into `src/mong_nhiem/context/`.

MN-011 is completed and synthesized: [Scaffolding-Assisted Effective Context Frontier](experiments/prototypes/mn-011-scaffolding-context-frontier/README.md). It empirically confirmed that small models achieve peak capacity-efficiency at $B^* \approx 512$ tokens ($H_1$), restored 100% causal reachability on ECC-007 across scales up to 16k tokens ($H_2$), and demonstrated a $60\times$ conversion efficiency advantage over raw attention ($H_3$).

MN-012 is completed and synthesized: [Hierarchical Tool & Memory Integration](experiments/prototypes/mn-012-hierarchical-tool-memory/README.md). It confirmed dual-tier memory partitioning, while unassisted SLMs exhibited Goal Divergence (Premature Resolution), activating the pivoting gate.

MN-013 is completed and closed: [Backtracking & Error Self-Correction](experiments/prototypes/mn-013-backtracking-error-correction/README.md). It proved that Host Memento state rollback, context rewind, and negative directives achieve 100% trap recovery on resource contention, while greedy unguided rewind causes 100% Amnesia Deadlock.

MN-014 is completed and closed: [Grammar-Constrained Decoding](experiments/prototypes/mn-014-grammar-constrained-decoding/README.md). It proved that Native GBNF engine-level logit masking eliminates 100% of formatting collapses (0 parse errors), boosting overall resolution to 55.0% and standard refactoring to 100%, ratifying ADR-0014.

MN-015 is completed and promoted: [Dynamic Affordance Constrained Decoding](experiments/prototypes/mn-015-dynamic-affordance-decoding/README.md). It established that Dual-Layer Affordance Steering (prompt attention priors + dynamic runtime GBNF logit masking) eliminates 100% of deadlock cycles (0 vs 15 in MN-014) and surges end-to-end task completion to 100.0% (60/60 cases). Following 100.0% cross-model qualification across Qwen3.5-2B, Llama-3.2-3B, and Qwen3-4B and 441/441 test suite verification, the domain-agnostic engine was promoted into `src/mong_nhiem/orchestration/` under Decision 2026-10-09 (ADR-0015).

MN-016 is completed and verified: [Episodic Memory & Long-Horizon Event Consolidation](experiments/prototypes/mn-016-episodic-memory-consolidation/README.md). It proved that Host-Authoritative Episodic Memory & AutoDream Consolidation overcomes Historical Amnesia across extended discrete horizons ($T = 20-50$ steps), achieving 100.0% task resolution (40/40) on `Qwen3.5-2B` (+100.0% delta over FIFO baseline), zero memory contradictions, zero token ceiling violations ($\le 512$ tokens, Max: 334, Mean: 111.0), and 64.9 ms mean turn latency. Prototype remains quarantined per Mộng Nhiễm governance rules, authorizing transition to **MN-017** (Dynamic World Ticks & Planning) and **MN-018** (Stateful Simulated Microworld Evolution).

MN-017 is completed and verified: [Dynamic World Ticks & Hierarchical Planning](experiments/prototypes/mn-017-dynamic-world-ticks/README.md). It proved that Dynamic World Ticks, Hierarchical Planning, and Optimistic Concurrency Guarding overcome Goal Divergence, Horizon Jumping, and asynchronous environmental drift across concurrent multi-phase missions ($K = 3-5$ sub-goals, $T = 15-35$ steps), achieving 100.0% task resolution (40/40) on `Qwen3.5-2B` (+100.0% delta over flat baseline), zero unmanaged stale overwrites committed (31 intercepted version drifts recovered via delta notices), zero horizon jumping events, bounded token ceilings ($\le 512$ tokens, Max: 253, Mean: 137.8), and 534.4 ms turn latency. Prototype remains quarantined per Mộng Nhiễm governance rules, authorizing transition to **MN-018** (Stateful Simulated Microworld Evolution).

MN-018 is completed and verified: [Stateful Simulated Microworld Evolution](experiments/prototypes/mn-018-simulated-microworld-evolution/README.md). It serves as a foundational stepping stone on the cognitive architecture ladder, validating that lightweight models (`Qwen3.5-2B`, $<4\text{B}$) reliably govern complex simulated microworlds across extended discrete horizons ($T = 50-100$ steps) under physical conservation invariants, multi-rate decay, and topological mission DAGs. Arm 3 achieved 100.0% task resolution (30/30) on real model inference (+100.0% delta over flat baseline), zero committed conservation breaches (0 vs 10 intercepted and rolled back by Memento), zero unmanaged stale overwrites, bounded prompt token ceilings ($\le 512$ tokens, Max: 386, Mean: 180.3), sub-second turn latency (649.4 ms), and sustained episodic execution. AutoDream memory compression achieved 70.0%–71.0% (satisfying the $\ge 70.0\%$ contract bound). High-difficulty stress testing ($K=8$ sub-goals, $T=150-200$ ticks, delayed traps, compound shocks) further demonstrated 100.0% (90/90) cross-model success within 4GB VRAM. Prototype code remains quarantined in `research/experiments/prototypes/mn-018-simulated-microworld-evolution/` pending subsequent multi-milestone integration, establishing the substrate for upcoming milestones: continuous non-stationary domain drift (**MN-019**) and multi-agent symbiosis (**MN-020**).

MN-019 is completed and verified across all three sub-stages under Dual-Track protocol: [Continuous Non-Stationary Causal Adaptation](experiments/prototypes/mn-019-non-stationary-causal-adaptation/README.md). Track 1 (Host Simulator) demonstrated 100.0% (180/180) mathematical validity and 0 committed breaches. Track 2 (Real Model Inference on `Qwen3.5-2B`, 180 runs) achieved 95.0% resolution on Arm 3 (171/180 PASS, exceeding the 85.0% contract bound across all three stages: Stage 1 100.0%, Stage 2 85.0%, Stage 3 100.0%) vs 50.0% (90/180) on Control and 1.1% (2/180) on Flat Baseline, with 0 committed invariant breaches, 89 proactive bypasses, and 83.6% AutoDream compaction. Prototype code remains quarantined (`non_stationary_causal_adaptation_verified_quarantined`), providing empirical grounding for **MN-020** (Multi-Agent Symbiosis & Distributed Cognitive Governance).

MN-020 is completed and verified under Dual-Track protocol: [Multi-Agent Symbiosis & Distributed Cognitive Governance](experiments/prototypes/mn-020-multi-agent-symbiosis/README.md). Track 1 (Deterministic Simulator) achieved 100.0% (60/60) mathematical validity and 0 committed races. Track 2 (Real Model Inference on homogeneous $2\times\text{Qwen3.5-2B}$ SLMs, 180 runs) achieved 100.0% resolution on Arm 3 (60/60 PASS, exceeding the 85.0% threshold) vs 33.3% (20/60) on Arm 2 (uncoordinated peer execution, committing 40 race breaches) and 0.0% (0/60) on Arm 1 (uncoordinated raw execution, committing 40 race breaches), yielding an empirical delta $\Delta_{\text{Arm 3} - \text{Arm 2}} = +66.7\% \ge +40.0\%$. Zero committed race violations occurred under Host Concurrency Arbiter leases and Dynamic Multi-Agent Affordance Masking. Standard library `.zip` evidence packaging (`audit_logs.zip`) eliminated repository bloat while preserving 100% cryptographic auditability. Prototype code remains quarantined in `research/experiments/prototypes/mn-020-multi-agent-symbiosis/` per Gate D disposition review (`PASS_VERIFIED_QUARANTINED`).

MN-021 is completed and verified under Dual-Track protocol: [Federated Causal Graph Synthesis & Epistemic Discrepancy Reconciliation](experiments/prototypes/mn-021-causal-graph-synthesis/README.md). Track 1 (Simulator, $N=80$) achieved 100.0% (80/80) on Arm 3 vs 48.8% (39/80) on Arm 2 (+51.2% delta) with 0 committed breaches and 0 race violations. Track 2 (Real Model Inference on homogeneous $2\times\text{Qwen3.5-2B}$ SLMs, $N=80$) achieved 100.0% resolution on Arm 3 (80/80 PASS, exceeding the 85.0% contract bound) vs 0.0% (0/80) on Arm 2 and 0.0% (0/80) on Arm 1, yielding an empirical delta $\Delta_{\text{Arm 3} - \text{Arm 2}} = +100.0\% \ge +40.0\%$ (frozen baseline preserved at 79/80, 98.8%). The Host Multi-Parent Causal Event DAG and 3-step Epistemic Discrepancy Reconciler ($[t_A, t_B]$ window slicing) coupled with Dynamic Multi-Affordance Phase Gating (`PROBE` $\to$ `CROSS_INSPECT` $\to$ `DISPATCH` $\to$ `RESOLVE`) eliminated epistemic amnesia and degenerate loops under partial observation and stochastic physical shocks, maintaining bounded prompt tokens ($\le 512\text{ tokens}$), $75.0\%$ AutoDream compaction, and zero committed breaches. All 960 episode traces across frozen baseline and authoritative runs were packaged into `audit_logs.zip` under the Zero Loose File Bloat Protocol. Prototype code remains quarantined in `research/experiments/prototypes/mn-021-causal-graph-synthesis/` (`PASS_VERIFIED_QUARANTINED`).

The context subsystem (`src/mong_nhiem/context/`) and cognitive orchestration subsystem (`src/mong_nhiem/orchestration/`) are selected and promoted for production context scaffolding, iterative coordination, and dual-layer cognitive steering. Retrieval, episodic memory, autonomous planning, and microworld governance architectures remain open for subsequent research milestones. Later deployment validation must eventually include coexistence with games and other local workloads, but controlled mechanism experiments may still require a clean GPU environment to make causal attribution interpretable.

## Navigate

- [Architecture](concepts/architecture.md)
- [ECC vs NCC](concepts/ecc-vs-ncc.md)
- [Current state](current-state.md)
- [Research methodology](research.md)
- [Experiments](experiments/README.md)
- [MN-002](experiments/baselines/mn-002-model-qualification/README.md)
- [MN-003](experiments/prototypes/mn-003-effective-context-capacity/README.md)
- [MN-004](experiments/prototypes/mn-004-state-representation-intervention/README.md)
- [MN-005](experiments/prototypes/mn-005-state-tracking-intervention-selection/README.md)
- [MN-006](experiments/prototypes/mn-006-distributed-state-integration/README.md)
- [MN-007](experiments/prototypes/mn-007-state-recovery-operating-region/README.md)
- [MN-008](experiments/prototypes/mn-008-external-state-management/README.md)
- [MN-009](experiments/prototypes/mn-009-context-scaffolding/README.md)
- [MN-010](experiments/prototypes/mn-010-iterative-context-loop/README.md)
- [MN-011](experiments/prototypes/mn-011-scaffolding-context-frontier/README.md)
- [MN-012](experiments/prototypes/mn-012-hierarchical-tool-memory/README.md)
- [MN-013](experiments/prototypes/mn-013-backtracking-error-correction/README.md)
- [MN-014](experiments/prototypes/mn-014-grammar-constrained-decoding/README.md)
- [MN-015](experiments/prototypes/mn-015-dynamic-affordance-decoding/README.md)
- [MN-016](experiments/prototypes/mn-016-episodic-memory-consolidation/README.md)
- [MN-017](experiments/prototypes/mn-017-dynamic-world-ticks/README.md)
- [MN-018](experiments/prototypes/mn-018-simulated-microworld-evolution/README.md)
- [MN-019](experiments/prototypes/mn-019-non-stationary-causal-adaptation/README.md)
- [MN-020](experiments/prototypes/mn-020-multi-agent-symbiosis/README.md)
- [MN-021](experiments/prototypes/mn-021-causal-graph-synthesis/README.md)
- [MN-022](experiments/prototypes/mn-022-swarm-consensus-pruning/README.md)
- [Decisions](decisions/decisions.md)
- [Roadmap](roadmap.md)

