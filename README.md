# Mộng Nhiễm

Mộng Nhiễm researches reliable reasoning and state tracking for lightweight open-weights language models (<4B parameters) over extensive knowledge and context spaces ($32\text{k}+$ tokens).

The project adheres strictly to an invariant core principle: **no fine-tuning, no weight modification, and no architectural alteration to the model**. The model is maintained strictly as an unchanged black-box reasoning engine, while host-managed substrates guarantee deterministic context bounds, prompt sanitization, and safety invariants.

---

## Production Library (`src/mong_nhiem/`)

The core library is implemented using **100% Python Standard Library** with zero external runtime dependencies.

### Scoped Context & Scaffolding Subsystem (`mong_nhiem.context`)

Promoted into production under milestones **MN-009** and **MN-010**:

- **`ContextPacker`:** Deterministic Knapsack context packing algorithm that compresses extensive document streams ($2\text{k}-32\text{k}$ tokens) down to a strict $\le 512$-token native forward-pass ceiling. Features lexical salience ranking, natural boundary preservation (zero sentence-splitting mid-token), and complete prompt injection sanitization against ChatML, Llama 3 headers, and reasoning delimiters (`<think>...</think>`).
- **`CodebaseSlicer`:** AST-based code compression engine that generates function skeletons, stubs uncalled auxiliary helpers, and adaptively inlines short utility functions while maintaining $100\%$ valid Python syntax (`ast.parse`).
- **`IterativeCoordinator`:** Host-managed multi-turn context loop coordinator. Interleaves bounded model forward passes ($\le 512$ tokens per turn) with deterministic host-side context extraction to resolve sequential multi-hop dependencies ($A \rightarrow B \rightarrow C$).
- **`CircuitBreaker`:** Defensive safety subsystem enforcing a hard turn ceiling ($\le 3$ turns) and duplicate/cycle detection (`visited_targets` set hashing), guaranteeing zero infinite retrieval loops or runaway latency.
- **Graph & Tabular Slicers:** Breadth-first $k$-hop subgraph extraction ($O(V+E)$) and attribute projection for structured state tables.

### Cognitive Orchestration Subsystem (`mong_nhiem.orchestration`)

Promoted into production under milestones **MN-015** and **Post-MN-022**:

- **`CognitiveOrchestrator`:** Dual-layer cognitive steering engine. Integrates prompt attention priors with runtime dynamic GBNF logit masking, host memento rollbacks, context rewind, and phase gate interceptors.
- **`MultiResourceArbiter`:** Host-authoritative resource lease manager with TTL decay, lock stealing, and Goal-Conditioned Affordance Sorting.
- **`StarConsensusHub` & `ByzantineAdmissionGate`:** Star-topology swarm consensus hub and admission filter sanitizing action proposals against syntax and authorization constraints.
- **`AsynchronousTransport`:** Network packet queue emulating stochastic propagation latency $\tau \in [0, \tau_{\max}]$ and out-of-order jitter.
- **`HierarchicalPlanner` & `MissionGraph`:** Multi-phase mission planner with DAG dependency gating and compact scoped prompt rendering.
- **`DynamicGBNFCompiler`:** Sub-millisecond CFG grammar compiler ($< 0.1\text{ ms}$) compiling state-dependent token masks for `llama.cpp` to eliminate parse collapses and constrain model logits to valid runtime affordances.
- **`MementoStack`:** Bounded deepcopy state snapshot and rollback engine isolating host state mutations from trial-and-error model explorations.
- **`ContextRewindManager`:** Prompt working memory manager guaranteeing strict $\le 512$-token context ceilings and managing negative action masks after rollbacks.
- **`PhaseGate`:** Task completion interceptor evaluating custom predicates before accepting model termination, preventing premature hallucinated resolutions.
- **`DeclarativeAffordanceEngine`:** Schema-driven, domain-agnostic affordance registry mapping host state models to action specifications without hardcoded domain couplings.

### Core Primitives & Invariants (`mong_nhiem.core`)

Promoted into production under milestone **Post-MN-022**:

- **`ConservationInvariantGuard`:** Physical invariant validator enforcing non-negativity and domain conservation laws (mass, energy, pressure) before host state commit.
- **`VectorClock`:** Multi-agent discrete vector clock establishing partial causal ordering and detecting concurrent execution branches without wall-clock synchronization.
- **`CausalEvent`:** Cryptographically hash-chained causal event record with SHA-256 provenance chaining.

### Cognitive Compaction Subsystem (`mong_nhiem.extensions.autodream`)

Promoted into production under milestone **Post-MN-022**:

- **`FactCardProjector`:** Topological Fact Card generator formatting dense state cards strictly bounded by cognitive token capacity ($\le 512$ tokens).
- **`AutoDreamConsolidator` & `FrontierBranchPruner`:** Compaction engine collapsing $O(M^2)$ interaction history into active $O(M)$ working frontier heads ($\ge 70.0\%$ compaction ratio).

### Causal Knowledge & Epistemics (`mong_nhiem.knowledge`)

Promoted into production under milestone **Post-MN-022**:

- **`CausalEventDAG`:** Multi-parent directed acyclic graph maintaining topological sorting, reachability analysis, and causal anomaly tracing.
- **`EpistemicReconciler`:** Deterministic reconciler slicing temporal-causal windows $[t_A, t_B]$ between disparate agent perspectives to arbitrate observation discrepancies.
- **`DynamicSchemaRegistry`:** Dynamic schema engine tracking runtime entity emergence, structural property mutation, and entity retirement.

### Microworld Runtime Subsystem (`mong_nhiem.runtime`)

Promoted into production under milestone **Post-MN-022**:

- **`AuthoritativeMicroworld`:** Discrete simulated environment runtime executing physics transitions, state decay, and Memento rollback interception on invariant violations.

---

## Research Milestone Progression

Research is organized under strict Gate criteria (Gate A Charter $\rightarrow$ Gate B Contract $\rightarrow$ Gate C Execution $\rightarrow$ Gate D Disposition Review). Experimental artifacts remain isolated in `research/experiments/` until earned promotion into `src/mong_nhiem/`.

| Milestone | Title | Track | Status | Primary Empirical Outcome |
| :--- | :--- | :---: | :---: | :--- |
| **MN-001** | Development Foundation | Foundation | **Completed** | Packaging, test harness, CI workflows, and canonical research structure. |
| **MN-002** | Model Qualification | Qualification | **Completed** | MCB v0.3.0 qualification benchmark. Qualified Llama 3.2 3B, Qwen3 4B, and Qwen 3.5 2B. |
| **MN-003** | Effective Context Capacity | ECC | **Completed** | Mapped empirical limits of direct native attention up to 16k tokens; identified state tracking collapse. |
| **MN-004** | State Representation Intervention | ECC | **Closed (Unsupported)** | Evaluated global state-transition ledgers; missed frozen support thresholds. |
| **MN-005** | State Tracking Intervention Selection | ECC | **Closed (Inconclusive)** | Multi-pass reconstruction audit; demonstrated ECC-006 workload limitations. |
| **MN-006** | Distributed State Integration | ECC | **Closed (Interface Blocked)** | Evaluated contiguous vs interleaved state locality under strict model qualification. |
| **MN-007** | State Recovery Operating Region | ECC | **Closed (Floor Regime)** | 108-case calibration proved in-context contiguous state recovery is unviable without support. |
| **MN-008** | External State Management | NCC | **Closed (Unsupported)** | Offloaded event replay to host engine; identified small-model conditional conjunction bounds. |
| **MN-009** | Scoped Context Delivery Engine | NCC Phase 1 | **Promoted** | 100% causal remedy on ECC-006, 100% injection immunity, and 22.9x downstream latency reduction. |
| **MN-010** | Iterative Context Working Set Loop | NCC Phase 2 | **Promoted** | 100% multi-hop resolution (30/30 vs 0/30 baseline), 100% budget adherence ($\le 512$ tokens), circuit breaker safety. |
| **MN-011** | Scaffolding-Assisted Context Frontier | ECC Reactivation | **Completed** | Proved $B^* \approx 512$ capacity-efficiency peak ($H_1$), 100% causal restoration on ECC-007 ($H_2$), and $60\times$ conversion advantage ($H_3$). |
| **MN-012** | Hierarchical Tool & Memory Integration | NCC Phase 3 | **Closed (Pivoted)** | Validated dual-tier memory; unassisted models suffer Horizon Jumping; activated pivoting gate. |
| **MN-013** | Backtracking & Error Self-Correction | NCC Phase 4 | **Closed (Quarantined)** | Achieved 100% trap recovery on resource contention via Memento rollback; proved amnesia deadlock on unguided rewind. |
| **MN-014** | Grammar-Constrained Decoding | NCC Phase 4 | **Closed (Standard Adopted)** | GBNF engine-level logit masking eliminated 100% format collapses (0 parse errors); surged refactoring to 100%. Ratified ADR-0014. |
| **MN-015** | Dynamic Affordance Constrained Decoding | NCC Phase 4 | **Promoted** | Dual-Layer Affordance Steering achieved 100.0% completion (60/60) and 0 deadlocks. Promoted to `src/mong_nhiem/orchestration/` after 100% qualification on Qwen3.5-2B, Llama-3.2-3B, Qwen3-4B. |
| **MN-016** | Episodic Memory & Long-Horizon Event Consolidation | NCC Phase 5 | **Completed (Quarantined)** | Host-Authoritative AutoDream achieved 100.0% completion (40/40) on Qwen3.5-2B, remediating 100% FIFO amnesia (+100% delta) with 0 contradictions, 0 ceiling violations ($\le 512$ tok), and 64.9 ms turn latency. |
| **MN-017** | Dynamic World Ticks & Hierarchical Planning | NCC Phase 6 | **Completed (Quarantined)** | Proved Dynamic World Ticks, Hierarchical Planning, and Optimistic Concurrency Guarding eliminate Goal Divergence, Horizon Jumping, and drift across 40 concurrent multi-phase missions (100.0% resolution, 0 stale overwrites, 0 horizon jumping, 534 ms latency). |
| **MN-018** | Stateful Simulated Microworld Evolution | NCC Phase 7 | **Conditionally Verified (Quarantined)** | Full cognitive host governance achieved 100.0% resolution (30/30 baseline, 90/90 stress) across Qwen3.5-2B, Llama-3.2-3B, Qwen3-4B within 4GB VRAM with 0 committed conservation breaches (45 traps rolled back) and $\le 512$ tok prompt ceiling. M5 AutoDream compression reached 57%–58% (gap against $\ge 70\%$ contract bound). Stepping stone on cognitive architecture ladder authorizing future milestones (MN-019, MN-020). |
| **MN-019** | Continuous Non-Stationary Causal Adaptation | NCC Phase 8 | **Completed and Verified (Quarantined)** | Evaluated SLM resilience under non-stationary drift across 3 stages under Dual-Track protocol. Track 1 achieved 100.0% (180/180 PASS, 0 breaches). Track 2 (real inference on Qwen3.5-2B, 180 runs) achieved 95.0% resolution on Arm 3 (171/180 PASS, exceeding the 85.0% threshold across all stages: 100%, 85.0%, 100%) vs 50.0% on Control vs 1.1% on Flat Baseline, with 0 committed invariant breaches and 83.6% AutoDream compaction. Prototype code quarantined. |
| **MN-020** | Multi-Agent Symbiosis & Distributed Cognitive Governance | NCC Phase 9 | **Completed and Verified (Quarantined)** | Evaluated homogeneous multi-agent governance ($2\times\text{Qwen3.5-2B}$) across $N=60$ scenarios under Dual-Track protocol. Track 1 achieved 100.0% (60/60). Track 2 achieved 100.0% resolution on Arm 3 (60/60 PASS) vs 33.3% on Arm 2 (40 committed race breaches) and 0.0% on Arm 1, establishing $\Delta_{\text{Arm 3} - \text{Arm 2}} = +66.7\% \ge +40.0\%$ and 0 committed race violations. Zip evidence protocol eliminated loose file bloat. Prototype code quarantined. |
| **MN-021** | Federated Causal Graph Synthesis & Epistemic Discrepancy Reconciliation | NCC Phase 10 | **Completed and Verified (Quarantined)** | Evaluated decentralized multi-agent coordination with partial observation and stochastic shocks ($N=80$ scenarios, 60 nominal + 20 shocks) under Dual-Track protocol. Track 1 (Simulator) achieved 100.0% (80/80) on Arm 3 vs 48.8% on Arm 2 (+51.2% delta) with 0 committed breaches. Track 2 (real inference on $2\times\text{Qwen3.5-2B}$) achieved 100.0% (80/80 PASS) on Arm 3 vs 0.0% on Arm 2 (+100.0% delta $\ge +40.0\%$) and 0.0% on Arm 1 with 0 committed breaches and 0 race collisions (baseline runs preserved frozen at 79/80, 98.8%). Host Multi-Parent Causal Event DAG and 3-step Epistemic Reconciler with dynamic affordance phase gating resolved epistemic discrepancy traps while bounding prompt tokens ($\le 512$) and AutoDream compaction (75.0%). 100% telemetry packaged into `audit_logs.zip` (960 traces, 0 loose JSON logs). Prototype code quarantined. |
| **MN-022** | Asynchronous Multi-Agent Swarm Governance & Consensus Pruning | NCC Phase 11 | **Conditionally Verified (Quarantined)** | Scaled coordination to asynchronous swarms ($M=5$ agents) across $N=80$ scenarios under stochastic latency $\tau_i \in [0, 5]$ ticks. Track 1 (Simulator) achieved 100.0% (80/80 PASS) on Arm 3 with 0 breaches and 0 collisions. Track 2 (real inference on $5\times\text{Qwen3.5-2B}$) achieved 90.0% (72/80) on Arm 3 vs 91.25% on Arm 2 (breaching token ceiling at 806 tokens) and 0.0% on Arm 1 (4,293 collisions). Because Gate B M2 required $\Delta_{\text{Arm 3} - \text{Arm 2}} \ge +40.0\%$ while empirical delta was $-1.25\%$, M2 is evaluated as FAIL, yielding a CONDITIONAL disposition. Host Consensus Hub and DAG pruner maintained prompt ceiling ($\le 512$ tok, max 298 tok) and 955.58 ms mean turn latency. Heterogeneous stress track verified concurrent Qwen-2B + Llama-3.2-3B swarm within 3.8 GB VRAM (2,445 ms latency). 100% telemetry packaged into `audit_logs.zip`. Prototype code quarantined. |

| **Post-MN-022** | Cumulative Production Promotion & Architectural Consolidation | Consolidation | **Promoted** | Systematic promotion of verified cognitive architecture modules from MN-016 through MN-022 into `src/mong_nhiem/` (Core, AutoDream, Knowledge, Swarm Orchestration, Microworld Runtime). 100% Python stdlib, 463 passing unit tests, 0 regressions. |
| **MN-023** | Minimal Controlled Microworld & Epistemic Invariant Verification | NCC Phase 12 | **Completed and Verified (Quarantined)** | Evaluated host-authoritative microworld state tracking, asymmetric observation masks, and causal DAG integrity across $N=60$ scenarios ($M=3$ agents, 180 episodes) on pure `Qwen3.5-2B` on `llama-server.exe`. Track 1 and Track 2 achieved 100.0% (60/60 PASS) on Arm 3 vs 0.0% on Arm 2 (which breached token ceiling at 611 tokens and suffered amnesia, $\Delta R_{\text{causal}} = +100.0\% \ge +50.0\%$) and 0.0% on Arm 1 (60 race collisions), meeting all 10 Gate B acceptance clauses (10/10 PASS). Zero epistemic leakage ($\Lambda \equiv 0.0$), 100% action groundedness, max prompt tokens 257 $\le 512$, and mean turn latency 231.16 ms ($< 1000\text{ ms}$ SLA). 100% telemetry sealed into `audit_logs.zip` (0 loose JSON logs). Prototype code quarantined. |
| **MN-024** | Long-Horizon Physical Microworld Scaling & Multi-Hop Causal Maintenance | NCC Phase 13 | **Completed and Verified (Quarantined)** | Scaled microworld governance across dual horizons (Tier A: $T=60$ ticks, $\Delta t \ge 40$; Tier B: $T=100$ ticks, $\Delta t \ge 80$) under continuous passive entropy decay and 4-hop causal cascades across 3 physical domains ($N=60$ scenarios $\times 2$ horizons $\times 3$ arms $= 360$ episodes per track) on pure `Qwen3.5-2B`. Track 1 and Track 2 achieved 100.0% (60/60 PASS) on Arm 3, meeting all 10 Gate B clauses on both tiers (10/10 PASS). Zero physical breaches occurred under continuous entropy decay, 0 race collisions, 0 epistemic leakage, 100% groundedness, constant-space prompt ceiling bounded to 55 tokens $\le 512$ ($91.7\%$ compaction vs $>1400$ in Arm 2), and 145 ms mean turn latency ($< 1000\text{ ms}$ SLA). Degradation across extended horizons was $0.00\% \le 5.0\%$. 100% telemetry sealed into `audit_logs.zip` (0 loose JSON logs). Prototype code quarantined. |
| **MN-025** | Cross-Domain Epistemic Knowledge Transfer, Cognitive Belief Conflict Reconciliation, and Stochastic Open Microworlds | NCC Phase 14 | **Completed and Verified (Quarantined)** | Evaluated cross-domain transfer, dialectic belief conflict reconciliation, and open-world stochastic shocks across 3 sequential stages ($N=60$ scenarios $\times 3$ arms $= 180$ episodes per track) on pure `Qwen3.5-2B` on `llama-server.exe`. Track 1 (Host Simulator) achieved 100.0% (60/60 PASS, 10/10 clauses met); Track 2 (Real Model Inference) achieved 95.0% resolution on Arm 3 (57/60 PASS, 3 uncompleted phantom decoy abstentions, bound $\ge 85.0\%$) with +64.29% transfer speedup ($\ge +40.0\%$), 0 negative transfer breaches, 100.0% dialectic convergence, 3.0 ticks stochastic recovery SLA, 0 physical breaches, 0 collisions, bounded token prompts (153 tok $\le 512$, mean 116.35 tok), 179.19 ms mean latency, and 100.0% anchor demotion fidelity, meeting all 10 Gate B acceptance clauses (10/10 PASS). Zero loose JSON files committed (sealed in `audit_logs.zip`). Prototype code quarantined. |

---

## Repository Layout

- `research/`: Canonical research knowledge base (directly viewable as an Obsidian vault).
  - `research/00-mong-nhiem.md`: Master entrypoint and navigational hub.
  - `research/concepts/`: Core theoretical frameworks ([`ecc-vs-ncc.md`](research/concepts/ecc-vs-ncc.md), [`architecture.md`](research/concepts/architecture.md)).
  - `research/decisions/`: Architectural Decision Records (ADRs).
  - `research/experiments/`: Sandbox prototypes and frozen empirical evidence.
- `src/mong_nhiem/`: Production package boundary (pure Python standard library).
- `tests/unit/`: Comprehensive test suite (475 unit and integration tests passing).


---

## Getting Started & Development

Python 3.11+ is required.

```powershell
# Install editable package with development dependencies
python -m pip install -e ".[dev]"

# Linting and syntax formatting checks
ruff check .

# Run test suite
python -m pytest tests/unit/ -v
```

Before contributing or modifying architectural decisions, read [`research/00-mong-nhiem.md`](research/00-mong-nhiem.md), [`research/concepts/architecture.md`](research/concepts/architecture.md), and [`research/decisions/decisions.md`](research/decisions/decisions.md).
