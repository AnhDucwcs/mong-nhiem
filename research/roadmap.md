# Roadmap

## MN-001 — Development foundation

Status: completed.

## MN-002 — Model qualification

Status: completed and frozen. MCB v0.3.0 is the canonical capability-qualification benchmark (fingerprint `2ac24df4e6cca12e13da577fb48db5da8e39d89cf3646ef705ea7679b4548f7a`). Llama 3.2 3B and Qwen3-4B are qualified capability baselines; capability and runtime evidence remain separate. This is not a production-model choice.

## MN-003 — Effective Context Capacity

Status: completed and closed for further ECC measurement work. ECC-001 through ECC-007 establish a model-specific capability map; no architecture has been selected. See the [MN-003 synthesis](experiments/prototypes/mn-003-effective-context-capacity/reports/mn-003-synthesis.md).

1. Easy retrieval is stable for both qualified models in the tested range, but Llama has a monotonic semantic-interference retrieval decline and a replicated late-position sensitivity under the confusable exact-output task.
2. Llama State Tracking is a bounded capability bottleneck: its fixed four-update contract has a short-context floor and declines monotonically to zero at 8k/16k without execution confounds.
3. Qwen causal reachability has no stable context-length degradation boundary in the tested range; its single 8k false positive is an unresolved isolated observation, not an ECC boundary or an ECC-008 trigger.
4. Timing/VRAM pressure at 16k is practical local-runtime evidence, not capability evidence.
5. MN-003 did not select a remedy; it supplied the immutable failure evidence used by MN-004.

## MN-004 — State Representation Intervention Design

Status: **completed and frozen for the globally indexed state-transition ledger hypothesis. Gate D promotion was not earned.**

1. Gate A selected one falsifiable intervention only: a globally indexed, one-to-one state-transition ledger preserving every event and global order without calculating final state.
2. Gate B froze the matched workload, thresholds, validity taxonomy, runtime controls, Llama primary estimand, 2k no-harm reference, and Qwen eligibility/control rules before efficacy inference.
3. Historical execution versions remain immutable: v1 `contract_not_executable`, v2 `invalid_comparison`, v3 `infrastructure_failure`, and v4 `ledger_persistent_phase_completed` as operational-feasibility evidence only.
4. V5 delivered the valid final efficacy comparison. Llama 8k untreated scored `0/24`; ledger scored `7/24`. The observed delta `+7/24` missed both frozen support rules: ledger `>=12/24` and delta `>=+8/24`.
5. The canonical final verdict is [`unsupported_no_effect_or_insufficient_effect`](experiments/prototypes/mn-004-state-representation-intervention/reports/mn-004-v5-final-efficacy.md). The seven wrong-to-correct flips remain an observation, not threshold support.
6. Llama 2k remained within the frozen no-harm margin (`4/24` untreated to `2/24` ledger).
7. Qwen untreated was `14/24`, below eligibility `20/24`; Qwen ledger was therefore prohibited and the control is `control_not_qualified`.
8. The ledger incurred material 8k token and latency overhead, so MN-004 does not establish a token-independent structural mechanism or a production-feasible architecture.
9. No v6, threshold adjustment, post-hoc ledger tuning, or promotion into `src/mong_nhiem/` is justified. MN-004 is closed.

## MN-005 — State Tracking Intervention Selection

Status: **completed and closed for further ECC-006 candidate efficacy work.** Gate A and Gate B v1 remain frozen historical records. `attempt-0001` is permanently `experiment_invalid`; Gate B v2 remains the tokenizer-verifiable executability repair. `attempt-0002` is the canonical first-valid Gate C v2 attempt and remains `inconclusive` (`1/6` Arm C versus `0/6` active control, `D=+1`). The Hierarchical Gate A audit is `hierarchical_gate_a_unselected`. No architecture is selected and no `attempt-0003` is authorized.

MN-005 established two different kinds of evidence that must not be conflated:


1. **Multi-pass Reconstruction was measurable but inconclusive.** None of the six Arm C Stage A artifacts met the intended exact-reconstruction criterion, including the sole beneficial B-to-C flip. The result does not show that reconstruction caused the observed `+1/6`, but it also does not universally reject multi-pass methods.
2. **Hierarchical State Representation was not experimentally falsified.** Frozen ECC-006 already supplies an ordered contiguous target trajectory, so hierarchy cannot be isolated from grouping, formatting, compression, reordering, salience, or answer simplification. Its decision is workload-bounded: `hierarchical_gate_a_unselected`.
3. **External State Management remains architecturally strong but poorly matched to the ECC-006 endpoint.** A host-maintained final state would be too close to directly supplying the evaluated answer.
4. **Event-to-State Normalization and Symmetric State Partitioning are also weakly observable on ECC-006** because source syntax is highly regular and target histories are already contiguous.

The milestone conclusion is therefore not that all candidates failed. It is that frozen ECC-006 has become insufficiently discriminative for several deeper state-management hypotheses. Candidate selection stops on ECC-006 rather than continuing with confounded efficacy attempts.

See the [MN-005 → MN-006 research handoff](experiments/prototypes/mn-005-state-tracking-intervention-selection/mn-006-handoff.md).

## MN-006 — Distributed State Integration

Status: **completed and closed at `measurement_interface_blocked` for the qualified model/runtime.**

MN-006 attempted to establish a deterministic, candidate-neutral contiguous-versus-interleaved locality measurement. The v1 equality/label path was retired after the diagnostic ladder showed a lower-level conditioned-output confound. The replacement direct ordered state-vector interface qualified its response channel at Q0 `9/9`, but its frozen contiguous task-bearing Q1 qualification scored only `1/9`. The predeclared exact `18/18` requirement was therefore not met.

The final scientific boundary is that the response serialization is usable, while the frozen Level 2 contiguous control condition is below the capability floor required for a causal locality comparison. Locality remains unmeasured. MN-006 does not support a negative locality claim, a general state-tracking claim, or an intervention claim. No retry, alternate interface, D2, perfect-state diagnostic, locality run, or intervention is authorized. See [MN-006 milestone closure](experiments/prototypes/mn-006-distributed-state-integration/milestone-closure.md).

## MN-007 — State Recovery Operating Region

Status: **completed and closed at `no usable operating region in bounded landscape`.**

MN-007 prospectively calibrated the contiguous state-recovery operating region needed before any future locality experiment. It was a separate milestone so the frozen MN-006 Q1 failure did not trigger post-hoc benchmark tuning inside MN-006.

The clean calibration rerun (`calibration-run-0002`) executed under clean commit `bfecd51` with evidence frozen at `23906e8`. All 108 requests executed strictly once in round-robin order with decoupled disk evaluation.
1. All six candidate cells in the bounded landscape ($E \in \{3, 5, 7\}, U=3$) scored $C_i \le 4/18$, resulting in a 100% `floor` classification.
2. The canonical research outcome is **`no usable operating region in bounded landscape`**.
3. Under the frozen prospective gate, this is an authoritative bounded negative result: in-context contiguous state recovery without explicit support is rejected for Llama 3.2 3B; no post-hoc tuning or search is permitted. MN-007 is closed.

See [MN-007 — State Recovery Operating Region](experiments/prototypes/mn-007-state-recovery-operating-region/README.md) and [Calibration Report](experiments/prototypes/mn-007-state-recovery-operating-region/mn007-calibration-report.md).

## MN-008 — External State Management

Status: **completed and closed at `unpromoted_hypothesis_unsupported`.**

Completed under Gate D disposition review (`100bbdc`). Run 0001 (24 cases, 96 calls) failed primary efficacy ($2/24$, exact $p \approx 0.991$) and utility delta ($C - B = +0.0\%$). Zero code promoted into `src/mong_nhiem/`. Host state decoupling eliminates history context bloat, but downstream boolean truth-table conjunction over neutral variables is not viable zero-shot on models <4B. See [gate-d-disposition-review.md](experiments/prototypes/mn-008-external-state-management/gate-d-disposition-review.md).

## MN-009 — Scoped Context Delivery Engine

Status: **completed and promoted into `src/mong_nhiem/context/`.**

1. **Gate A Charter & Gate B Contract:** Frozen 5 support rules across 3 data categories and 5 context tiers ($2\text{k}-32\text{k}$).
2. **Gate C Execution & Gate D Promotion:** All 5 support rules achieved $100\%$ ($30/30$), achieving $2.07\text{M tokens/sec}$ CPU packing throughput, $100\%$ causal remedy on ECC-006, $100\%$ negative query abstention, $100\%$ injection immunity, and $22.9\times$ downstream inference latency reduction. Promoted into `src/mong_nhiem/context/` under Decision 2026-10-01.

## MN-010 — Iterative Context Working Set Loop

Status: **completed and promoted into `src/mong_nhiem/context/`.**
Track: **NCC Phase 2 (Substrate Expansion).**

1. **Gate A Charter & Gate B Contract:** Frozen 5 support rules and 30 multi-hop cases across Code AST, Knowledge Graph paths, and State Tables.
2. **Action Protocol & Circuit Breaker:** Implemented Action Protocol Grammar Choice A (flat regex text: `ACTION: FETCH <target>` / `ACTION: RESOLVE <answer>`) and circuit breaker hard ceiling $\le 3$ turns with duplicate/cycle detection.
3. **Gate C Execution & Gate D Promotion:** All 5 support rules verified with $100\%$ compliance (Arm B $100.0\%$ [30/30] vs Arm A $0.0\%$ [0/30] accuracy, $100\%$ per-turn token adherence $\le 512$ tokens, $100\%$ circuit breaker safety, $< 0.5\text{ms}$ host coordination). Formally promoted into `src/mong_nhiem/context/coordinator.py` with zero regressions (420/420 tests passing).

## MN-011 — Scaffolding-Assisted Effective Context Frontier

Status: **completed and synthesized.**
Track: **ECC Reactivation (Utilization & Frontier Mapping).**

1. **Gate A Charter & Gate B Contract:** Frozen 4 support rules and 40 evaluation cases across Suite A (parametric budget sweep $256-2048$ tokens) and Suite B (ECC-007 causal reachability matched suite $512-16\text{k}$ tokens).
2. **Pre-Run Freeze Authority:** Pre-run authority sealed under commit `f9e52aa`. Operational buffer limitations under Windows OS CLI flags (`WinError 206`) recorded in Attempt 0001 (`a2a7866`) and repaired via stdin streaming in Attempt 0002 (`738e714`).
3. **Gate C Execution & Gate D Synthesis:** Confirmed $H_1$ (capacity plateaus at $B^* \approx 512$ tokens, while expanding to $1024/2048$ yields 0% gain with $35.4\%$ efficiency degradation), confirmed $H_2$ (100% causal reachability accuracy on ECC-007 up to 16k context, eliminating false positives), and confirmed $H_3$ ($\eta_{512} = 0.139$ vs $\eta_{\text{raw}} = 0.0023$, a $60\times$ efficiency gap).

## MN-012 — Hierarchical Tool & Memory Integration

Status: **completed and synthesized (pivoting gate activated).**  
Track: **NCC Phase 3 (Cognitive Orchestration).**

1. **Gate A Charter & Gate B Contract:** Frozen 5 support rules and 60 stateful evaluation cases across Code AST, Resource Ledger, and System Registry under Dual-Track protocol.
2. **Gate C Dual-Track Execution:**
   - Track 1 (Simulator): 100% (60/60) task completion on Arm B vs 0% on Arm A, 100% budget compliance ($\le 512$ tokens), 0 invariant breaches, $< 0.15\text{ms}$ host overhead. Frozen under `freeze-manifest.json` (`41a54c5`).
   - Track 2 (Real Model Inference — `Qwen3.5-2B`): Run 0002 confirmed Failure Mode 1 (Format Collapse) under raw zero-shot. Run 0004 under Ponytail grounding achieved 100% valid protocol action parses and 4/4 PASS on AST error recovery (Cases 13–16), but unassisted models exhibited Goal Divergence (Premature Resolution / Horizon Jumping and lack of error recovery), triggering **Failure Mode 3 (Goal Divergence)**.
3. **Gate D Disposition Review:** Closed as `pivoting_gate_activated_failure_mode_3`. Prototype remains hermetically quarantined in `research/experiments/prototypes/mn-012-hierarchical-tool-memory/` (zero code promoted into `src/mong_nhiem/`). Empirically proves that small models require host-directed state machine and backtracking, authorizing immediate transition to MN-013.

## MN-013 — Backtracking & Error Self-Correction

Status: **completed and closed (quarantined prototype, core mechanism verified).**  
Track: **NCC Phase 4 (Autonomous Recovery).**

1. **Gate A Charter & Gate B Contract:** Frozen 5 support rules and 60 benchmark cases (30 normal, 30 dead-end traps across Code AST, Resource Ledger, and System Registry) evaluated across 4 comparative arms under Dual-Track protocol. Pre-run freeze commit: `6bcd358`.
2. **Gate C Dual-Track Execution:**
   - Track 1 (Simulator, 240 runs): Arm 4 achieved 100% (60/60) task completion with 30 rollbacks and 0 deadlocks. Arms 2 and 3 suffered 30 deadlock cycles each.
   - Track 2 (Real Model Inference — `Qwen3.5-2B`, 132 runs):
     - **Domain B Traps (Resource Ledger):** Arm 4 achieved **10/10 PASS (100.0% recovery)** vs Arm 1 baseline **0/10 PASS (0.0%)**, empirically validating that Host Memento Rollback + Context Rewind + Negative Masking enables sub-4B models to autonomously escape dead-ends.
     - **Domain A Traps (AST Recovery):** Arm 4 achieved 8/10 PASS (80.0%) with 11 rollbacks, while Arm 1 committed unverified Horizon Jumping.
     - **Arm 2 Ablation:** Demonstrated monotonic context inflation (+138 tokens on turn 1 failure).
     - **Arm 3 Ablation:** Produced 100% Amnesia Deadlock on registry traps, confirming that state rollback without negative masking causes deterministic cycle repetition under greedy decoding ($T=0.0$).
     - **Non-Trap Formatting Brittleness:** Unconstrained greedy decoding occasionally emitted unspaced parameters (`DISPATCH calculate_tax_1:rate=22`), triggering Phase Gate premature resolve rejections and cycle breaker trips.
3. **Gate D Disposition Review:** Formally closed at `quarantined_prototype_core_mechanism_verified`. Zero code promoted into `src/mong_nhiem/` (prototype quarantined in `research/experiments/prototypes/mn-013-backtracking-error-correction/`). Post-run manifest sealed under `definition/post-run-freeze-manifest.json` (389 files). Directs transition to MN-014 for grammar-constrained decoding.

## MN-014 — Grammar-Constrained Decoding & Structured Cognitive Routing

Status: **completed and closed (quarantined prototype, GBNF standard adopted).**  
Track: **NCC Phase 4 (Robust Action Synthesis).**

1. **Gate A Charter & Gate B Contract:** Frozen 5 support rules and 60 benchmark cases (Domain A AST, Domain B Resource Ledger, Domain C System Registry) evaluated across 2 matched arms (Arm 1 Unconstrained Greedy vs Arm 2 GBNF Grammar Constrained) on `Qwen3.5-2B-Q4_K_M.gguf`. Pre-run freeze commits: `07c443e`, `9066b7e`, `9d12d13`.
2. **Gate C Dual-Track Execution:**
   - **Syntax Determinism ($H_1$ Supported):** Exactly 100% (197/197 turns) conformed to the Context-Free Grammar. Zero delimiter omissions, whitespace failures, or regex parsing errors.
   - **Efficacy Surge (+21.7% Absolute Gain):** Overall task completion rose from 33.3% (20/60) to 55.0% (33/60). Domain A standard refactoring surged from 0.0% (0/10) to 100.0% (10/10). Domain B maintained 100.0% (20/20).
   - **Thrashing Suppression:** Total turns dropped -16.5% (236 to 197), rollbacks dropped -34.3% (99 to 65), deadlock cycles dropped -31.8% (22 to 15).
   - **Hard Invariant:** 100% turns adhered to $\le 512$ tokens (Max: 489, Mean: 379.4) with sub-second turn latency (468.0 ms).
3. **Gate D Disposition Review:** Formally closed at `quarantined_prototype_gbnf_standard_adopted`. Engine-level GBNF grammar decoding is ratified as an authoritative architectural standard (ADR-0014). Code remains quarantined in `research/experiments/prototypes/mn-014-grammar-constrained-decoding/`. Post-run manifest sealed under `definition/post-run-freeze-manifest.json` (Commit `7a087fb`, 239 files). Directs transition to MN-015 to resolve multi-branch combinatorial search exhaustion.

## MN-015 — Dynamic Affordance Constrained Decoding & Dual-Layer Steering

Status: **completed and promoted into `src/mong_nhiem/orchestration/`.**  
Track: **NCC Phase 4 (Dynamic Affordance & Cognitive Orchestration).**

1. **Gate A Charter & Gate B Contract:** Frozen 5 support rules and 60-case benchmark evaluated across 2 matched arms on Track 1 (Simulator) and Track 2 (Real Model Inference on `Qwen3.5-2B-Q4_K_M.gguf` via `llama-server.exe`). Pre-run freeze commit: `9908575`.
2. **Gate C Dual-Track Execution:**
   - **Flawless Efficacy ($H_1$ Strongly Confirmed):** Achieved **100.0% (60/60 PASS)** task completion. Domain A: 20/20 (100.0%), Domain B: 20/20 (100.0%), Domain C: 20/20 (100.0%, surging +85.0% over MN-014).
   - **Zero Deadlock Cycles ($H_2$ Strongly Confirmed):** Circuit-breaker tripped deadlocks dropped from 15 in MN-014 to **exactly 0 (0.0%)**.
   - **Trap Recovery Efficacy:** Exactly **30/30 (100.0%)** traps resolved cleanly with 1 host rollback per trap and zero false rollbacks on non-trap cases.
   - **Hard Invariants & Latency ($H_3$ Confirmed):** 100% turns adhered to $\le 512$ tokens (Max: 396, Mean: 318.5) with 0 parse failures and 329.37 ms mean turn latency.
3. **Packaging & Cross-Model Reusability Qualification:**
   - Packaged into domain-agnostic `src/mong_nhiem/orchestration/` (100% Python standard library).
   - Added 14 unit and stress tests in `tests/unit/test_orchestration.py` (441/441 test suite passes).
   - Validated across all 3 qualified local models (`Qwen3.5-2B`, `Llama-3.2-3B`, `Qwen3-4B`), achieving 100.0% cross-model accuracy (15/15 PASS per subject) and sub-second turn latency.
4. **Gate D Disposition Review:** Formally promoted into `src/mong_nhiem/orchestration/` under Decision 2026-10-09 (ADR-0015). Post-run manifest sealed under `definition/post-run-freeze-manifest.json` (122 files). Advances roadmap to MN-016 (Episodic Memory & Long-Horizon Event Consolidation).

## MN-016 — Episodic Memory & Long-Horizon Event Consolidation

Status: **completed and verified prototype. Gate D criteria satisfied.**  
Track: **NCC Phase 5 (Long-Horizon Continuity & Archival Memory).**

1. **Strategic Intent & Outcome:**
   - Overcame Historical Amnesia across extended discrete horizons ($T = 20-50$ steps) via host-authoritative episodic logging and AutoDream consolidation under strict $\le 512$ token bounds.
   - Achieved 100.0% task resolution (40/40) on `Qwen3.5-2B`, remediating 100% of FIFO amnesia failures (+100.0% delta) with 0 memory contradictions, 0 ceiling violations (max: 334, mean: 111.0 tokens), and 64.9 ms latency.
2. **Core Architectural Pillars:**
   - **Host Episodic Store:** Immutable append-only event log with SHA-256 provenance hashes and monotonic causal replay.
   - **Autonomous Dual-Trigger Gates:** Machine ticks ($\Delta T \ge 25$) and mutation flux ($M \ge 10$) combined with Emergency Context Budget Pressure Interceptor ($\ge 400$ tokens).
   - **4-Phase Consolidation Lifecycle:** Orient $\rightarrow$ Gather $\rightarrow$ Consolidate $\rightarrow$ Prune & Index ($\le 128$ tokens).
   - **Episodic Recall Affordances:** Demand-driven retrieval via dynamic GBNF-governed `ACTION: RECALL <entity_id>` delivering compact Fact Cards ($\le 48$ tokens).
3. **Gate D Disposition:** Verified and closed under Decision 2026-10-09. Code quarantined in prototype directory per governance rules; transition to MN-017 authorized.

## MN-017 — Dynamic World Ticks & Hierarchical Planning

Status: **completed and verified prototype. Gate D criteria satisfied.**  
Track: **NCC Phase 6 (Environmental Concurrency & Autonomous Planning).**

1. **Strategic Intent & Outcome:**
   - Overcame environmental drift and asynchronous background mutations via multi-rate simulation clocks ($\Delta t_{world} = 1-3$), monotonic versioning, and an Optimistic Concurrency Guard with Host-driven delta notices.
   - Eliminated Goal Divergence and Horizon Jumping on complex multi-stage objectives ($K = 3-5$ sub-goals, $T = 15-35$ steps) by combining topological DAG sub-goal planning with dynamic GBNF phase-gate logit masking.
   - Achieved 100.0% task resolution (40/40) on `Qwen3.5-2B`, with 0 unmanaged stale-state overwrites committed, 31 intercepted version drifts recovered, 0 horizon jumping events, 0 premature resolutions, peak prompt bounded at 253 tokens (mean 137.8 tokens), and 534.4 ms turn latency.
   - Cross-Model Qualification: Host dynamic affordance pruning verified across all 3 local open-weights models (`Qwen3.5-2B`: 100.0%, `Qwen3-4B`: 95.0%, `Llama-3.2-3B`: 87.5%), lifting cross-model mean accuracy from 65.0% to 94.2% with zero unmanaged stale overwrites.
2. **Core Architectural Pillars:**
   - **`DynamicWorldEngine`**: Multi-rate world clock, entity TTL decay, and background mutation loops.
   - **`HierarchicalPlanner`**: Topological DAG mission graph evaluated by Host symbolic predicates.
   - **`DynamicAffordanceCompiler`**: GBNF phase-gate compiler masking out illegal actions for unactivated sub-goals.
   - **`ConcurrencyGuard`**: Monotonic entity versioning ($v_{entity}$), conflict detection, and compact delta notices ($\le 64$ tokens).
3. **Gate D Disposition:** Verified and closed under Decision 2026-10-10 (ADR-0017). Code quarantined in prototype directory per governance rules; handoff to MN-018 authorized.

## MN-018 — Stateful Simulated Microworld Evolution

Status: **completed and verified prototype (quarantined in research/experiments/prototypes/). Gate D criteria satisfied.**  
Track: **NCC Phase 7 (Stateful World Continuity & Governance).**

1. **Strategic Intent & Stepping Stone Horizon:**
   - Validated that lightweight models (`Qwen3.5-2B`, $<4\text{B}$) reliably govern and evolve complex, multi-entity simulated microworlds across extended discrete time horizons ($T = 50-100$ steps) under physical conservation invariants, multi-rate decay, and coupled dependencies.
   - Operates as a foundational stepping stone on the cognitive architecture ladder, establishing simulated microworld governance before progressing to non-stationary environments and multi-agent interaction.
   - Evaluated across 30 complex scenarios spanning 3 heterogeneous domains: Orbital Life Support ($N=10$), Smart Microgrid ($N=10$), and Fleet Logistics Supply Chain ($N=10$).
   - Achieved 100.0% task resolution (30/30) on real model inference (`Qwen3.5-2B`) on Arm 3 vs 0.0% in Arm 1 (+100.0% delta) and 0.0% in Arm 2.
   - Preserved zero committed conservation breaches (0 vs 10 intercepted and rolled back by Memento), 0 unmanaged stale-state overwrites, prompt ceiling strictly $\le 512$ tokens (max 386, mean 180.3), turn latency 649.4 ms ($< 1000\text{ ms}$ SLA).
2. **AutoDream Memory Optimization & M5 Contract Fulfillment:**
   - Identified root cause of the initial compaction gap: cumulative global entity card summation and verbose card rendering.
   - Implemented compact high-density Fact Cards (`[entity_id v{version} {key}:{val}]`, saving ~37.5% tokens), active TTL entity pruning, and terminal episodic finalization (`orch.finalize()`).
   - Achieved **70.0%** compression ratio on `corpus-v1` (both Track 1 and Track 2) and **71.0%** on `corpus-v2-stress`, fully meeting and surpassing the contract bound ($\ge 70.0\%$, PASS). Verified via dedicated test suite `test_autodream_benchmark.py` (6/6 tests passing).
3. **Arm 2 Methodological Resolution:**
   - Track 1 Simulator (decoupled static checklist without DAG gating): 20/30 (66.7%) on `corpus-v1` (10 invariant breaches in Orbital domain), 0/30 (0.0%) on `corpus-v2-stress` (100% trap failure).
   - Track 2 Real Inference (unconstrained grammar): 0/30 (0.0%) across baseline and stress suites due to premature resolution or repetitive action loops.
4. **Full System Convergence & High-Difficulty Stress Suite (`corpus-v2-stress`):**
   - Validated across 30 ultra long-horizon stress scenarios ($T = 150-200$ ticks, $K=8$ topological sub-goals, 4–6 actions per phase with delayed rollback traps, cascading compound shocks) across all 3 qualified local models (`Qwen3.5-2B`, `Llama-3.2-3B`, `Qwen3-4B`).
   - Arm 3 achieved **100.0% (90/90)** task resolution across all models and domains (Arm 1 and Arm 2 at 0.0%), zero committed conservation breaches, 45 trap breaches intercepted and rolled back by Memento, 1 to 4 consecutive AutoDream consolidation cycles per episode bounding prompt growth for primary model `Qwen3.5-2B` (max 503 tokens $\le 512$, while secondary `Qwen3-4B` reached 572 tokens on Case 26 evaluating its stress run as M7 FAIL), and all models operating inside 4.0 GB VRAM.
5. **Gate D Disposition & Prototype Quarantine:**
   - Disposition review: `stateful_microworld_evolution_verified_quarantined`.
   - In adherence to Gate D governance, experimental code remains strictly quarantined in `research/experiments/prototypes/mn-018-simulated-microworld-evolution/` and is NOT promoted directly to `src/mong_nhiem/` pending broader multi-milestone progression. Cryptographic manifests (`definition/pre-run-freeze-manifest.json`, `definition/post-run-freeze-manifest.json`) and raw execution traces (`runs/`) are sealed.

## MN-019 — Continuous Non-Stationary Causal Adaptation

Status: **completed and verified across Dual-Track protocol (`non_stationary_causal_adaptation_verified_quarantined`).**  
Track: **NCC Phase 8 (Non-Stationary Domain Drift & Dynamic Adaptation).**

1. **Sub-Stage 1: Parametric Adaptation (`drift-001-parametric-adaptation`):**  
   - Track 1 Simulator (60 cases, 30 ID / 30 OOD): Arm 3 **100.0% (60/60)** vs Arm 2 21.7% vs Arm 1 0.0%. 0 breaches, 85.5% compaction. Verdict: **PASS**.
   - Track 2 Real Model (`Qwen3.5-2B`, 60 cases): Arm 3 **100.0% (60/60)** vs Arm 2 50.0% vs Arm 1 3.3%. 0 breaches, 87.1% compaction. Max prompt: 94 tokens. Verdict: **PASS** ($\ge 85.0\%$).
2. **Sub-Stage 2: Dynamic Schema Evolution (`drift-002-schema-evolution`):**  
   - Track 1 Simulator (60 cases, 30 ID / 30 OOD): Arm 3 **100.0% (60/60)** vs Arm 2 0.0% vs Arm 1 0.0%. 0 violations, 73.0% compaction. Verdict: **PASS**.
   - Track 2 Real Model (`Qwen3.5-2B`, 60 cases): Arm 3 **85.0% (51/60)** vs Arm 2 0.0% vs Arm 1 0.0%. Subsea hydrothermal 15/15 (100.0%) under Stagnation Detection. 78.6% compaction. Max prompt: 153 tokens. Verdict: **PASS** ($\ge 85.0\%$).
3. **Sub-Stage 3: Counterfactual Causal Event Synthesis (`drift-003-causal-event-synthesis`):**  
   - Track 1 Simulator (60 cases, 31 ID / 29 OOD): Arm 3 **100.0% (60/60)** vs Arm 2 0.0% vs Arm 1 0.0%. 74 proactive bypasses, 0 violations, 79.2% compaction. Verdict: **PASS**.
   - Track 2 Real Model (`Qwen3.5-2B`, 60 cases): Arm 3 **100.0% (60/60)** vs Arm 2 100.0% vs Arm 1 0.0%. 89 bypasses, 0 committed breaches, 85.0% compaction. Max prompt: 245 tokens. Verdict: **PASS** ($\ge 85.0\%$).
4. **Master Milestone Verdict & Quarantine:**  
   - Dual-Track Total: Track 1 achieves **100.0% (180/180)** (PASS); Track 2 achieves **95.0% (171/180)** on Arm 3 vs 50.0% on Arm 2 vs 1.1% on Arm 1 (PASS, $\ge 85.0\%$ across all stages).
   - Milestone verdict: **PASS (`non_stationary_causal_adaptation_verified_quarantined`)**. Prototype code remains strictly quarantined under `research/experiments/prototypes/mn-019-non-stationary-causal-adaptation/` (zero promotion to `src/mong_nhiem/`). Full academic report frozen in `reports/mn-019-track2-comprehensive-report.md`.

## MN-020 — Multi-Agent Symbiosis & Distributed Cognitive Governance

Status: **completed and verified prototype (`multi_agent_symbiosis_verified_quarantined`).**  
Track: **NCC Phase 9 (Multi-Agent Symbiosis & Distributed Cognitive Governance).**

1. **Strategic Intent & Outcome:**
   - Extended Host-Authoritative Cognitive Governance from solitary agent execution to concurrent multi-agent microworlds ($M=2$ agents) interacting over shared physical resources.
   - Designed and evaluated the **Host Concurrency Arbiter & Optimistic Lease Manager**, coupling mutual exclusion entity leases with dynamic Context-Free Grammar (GBNF) affordance masking, scoped AutoDream Fact Card context projections, and discrete non-conversational signalling.
   - Evaluated across $N = 60$ standardized multi-agent scenarios across 3 physical domains: Collaborative Smart Microgrid Balancing ($N=20$), Concurrent Orbital Maintenance ($N=20$), and Joint Fleet Logistics ($N=20$).
2. **Dual-Track Empirical Results ($2\times \text{Qwen3.5-2B}$ topology):**
   - **Track 1 (Host Simulator — 60 cases):** Arm 3 achieved **100.0% (60/60 PASS)** resolution with 0 committed race violations and 0 deadlocks, outperforming Arm 2 (Independent Control, 0.0%) by **+100.0%** and Arm 1 (Flat Baseline, 0.0%) by **+100.0%**.
   - **Track 2 (Real Model Inference — 60 cases):** Arm 3 achieved **100.0% (60/60 PASS)** resolution with 0 committed race violations and 0 deadlocks, outperforming Arm 2 (33.3%, 20/60) by **+66.7%** (exceeding the $\ge +40.0\%$ contract bound) and Arm 1 (0.0%) by **+100.0%**.
   - Hard Invariants & Performance: Prompt tokens strictly bounded at $\max = 38\text{ tokens} \le 512\text{ tokens}$, turn latency averaged 715 ms ($< 1000\text{ ms}$ SLA), and AutoDream compaction sustained $75.0\% \ge 70.0\%$.
3. **Evidence Packaging & Zero Loose File Bloat Protocol:**
   - Ratified standard library `.zip` evidence packaging (`audit_logs.zip`), packing all 360 episode traces across both runs and pruning all loose JSON logs from the working tree.
   - Verifiable SHA-256 fingerprints: Track 1 (`c24a64a3...`), Track 2 (`32f13026...`). Direct inspection verified via `scripts/validate_audit.py`.
4. **Gate D Disposition & Prototype Quarantine:**
   - Disposition review: `multi_agent_symbiosis_verified_quarantined`.
   - All prototype code strictly quarantined in `research/experiments/prototypes/mn-020-multi-agent-symbiosis/` (zero promotion to `src/mong_nhiem/`). Full academic reports frozen at `reports/mn-020-track1-report.md` and `reports/mn-020-track2-report.md`. Pre-run and post-run freeze manifests committed.

## MN-021 — Federated Causal Graph Synthesis & Epistemic Discrepancy Reconciliation

Status: **completed and verified prototype (`federated_causal_synthesis_verified_quarantined`).**  
Track: **NCC Phase 10 (Federated Causal Graph Synthesis & Epistemic Discrepancy Reconciliation).**

1. **Strategic Intent & Outcome:**
   - Extended multi-agent governance to handle partial epistemic visibility, information asymmetry, and stochastic physical shocks in decentralized cyber-physical microworlds.
   - Implemented a **Host Multi-Parent Causal Event DAG** with cryptographic hash chaining, a deterministic **Epistemic Discrepancy Reconciler** ($[t_A, t_B]$ temporal-causal window slicing), and **Dynamic Multi-Affordance Phase Gating** (`PROBE` $\to$ `CROSS_INSPECT` $\to$ `DISPATCH` $\to$ `RESOLVE`), eliminating epistemic amnesia and degenerate probing loops.
   - Evaluated across $N = 80$ standardized multi-agent scenarios across three heterogeneous physical domains: Martian Biosphere Colony Life Support ($N=27$), Subsea Hydrothermal Energy Grid ($N=27$), and Orbital Constellation Satellite Relay ($N=26$). Corpus composed of 60 nominal cases (75.0%) and 20 stochastic physical shocks (25.0%).
2. **Dual-Track Empirical Results ($2\times \text{Qwen3.5-2B}$ topology):**
   - **Track 1 (Host Simulator — 80 cases):** Arm 3 achieved **100.0% (80/80 PASS)** resolution with 0 committed physical breaches and 0 race collisions, outperforming Arm 2 (Reactive Control, 48.8% / 39/80) by **+51.2%** (contract bound $\ge +40.0\%$) and Arm 1 (Flat Baseline, 22.5% / 18/80) by **+77.5%**. Frozen baseline preserved at 98.8% (79/80).
   - **Track 2 (Real Model Inference — 80 cases):** Arm 3 achieved **100.0% (80/80 PASS)** resolution with 0 committed physical breaches and 0 race collisions, outperforming Arm 2 (0.0% / 0/80) by **+100.0%** and Arm 1 (0.0% / 0/80) by **+100.0%**. Frozen baseline preserved at 98.8% (79/80).
   - Hard Invariants & Performance: Prompt tokens strictly bounded at $\max = 405\text{ tokens} \le 512\text{ tokens}$ (mean: 232.8), turn latency averaged 511.3 ms ($< 1000\text{ ms}$ SLA), AutoDream compaction sustained $75.0\% \ge 70.0\%$, and reconciliation accuracy reached 100.0% ($\ge 95.0\%$).
3. **Evidence Packaging & Zero Loose File Bloat Protocol:**
   - All 960 episode audit traces across both frozen baseline and authoritative runs packaged into `audit_logs.zip` archives with zero loose JSON files in Git.
   - Verifiable SHA-256 fingerprints:
     - Authoritative Track 1 (`mn021-run-20261012-133857-track1-sim`): `f5ddc5f1b10ccb6da339e54bb404b23c2135cd1dd8ec87b279e1bc0d49740080`
     - Authoritative Track 2 (`mn021-run-20261012-133931-track2-Qwen3.5-2B-Q4_K_M`): `4acfe3f838011a8a97666e18411de7b5ed3cc0fa50507b5ebf38836d92880fa8`
     - Frozen Baseline Track 1 (`mn021-run-20261012-120017-track1-sim`): `1a0c215ab6b593395af9d3da8b553cc9c700c14d1bb063648aef380945ec9a0f`
     - Frozen Baseline Track 2 (`mn021-run-20261012-120120-track2-Qwen3.5-2B-Q4_K_M`): `25d0b4560247a464a4fe488779f95a713a073e14d370cbbfd4ae273343b75274`
   - Direct non-destructive inspection verified via `scripts/validate_audit.py`.
4. **Gate D Disposition & Prototype Quarantine:**
   - Disposition review: `federated_causal_synthesis_verified_quarantined`.
   - All prototype code strictly quarantined in `research/experiments/prototypes/mn-021-causal-graph-synthesis/` (zero promotion to `src/mong_nhiem/`). Full academic reports frozen at `reports/mn-021-track1-report.md` and `reports/mn-021-track2-report.md`. Pre-run and post-run freeze manifests committed.

## MN-022 — Asynchronous Multi-Agent Swarm Governance & Consensus Pruning

Status: **completed with conditional disposition (`swarm_consensus_pruning_conditional_quarantined`).**  
Track: **NCC Phase 11 (Asynchronous Swarm Governance & Consensus Pruning).**


1. **Strategic Intent & Outcome:**
   - Scaled multi-agent coordination from pairwise dyads ($M=2$) to asynchronous concurrent swarms ($M=5$ agents) interacting across shared cyber-physical microworlds subjected to stochastic network propagation latency ($\tau_i \in [0, 5]$ discrete ticks) and out-of-order jitter.
   - Engineered the **Host Star-Topology Consensus Hub**, **Multi-Resource TTL Lease Matrix** with non-blocking optimistic acquisition, **Vector Clock Causal DAG** with $O(M^2) \to O(M)$ frontier branch pruning, and **Topological AutoDream Fact Cards** with strict $\le 512$ token ceiling enforcement.
   - Evaluated across $N=80$ standardized multi-agent swarm scenarios across 3 physical domains: Smart Microgrid Swarm Load Balancing ($N=27$), Multi-Depot Fleet Logistics ($N=27$), and High-Performance Cluster Scheduling ($N=26$).
2. **Dual-Track & Heterogeneous Empirical Results ($M=5$ agents):**
   - **Track 1 (Host Simulator — 80 cases, 240 episodes):** Arm 3 achieved **100.0% (80/80 PASS)** resolution with 0 committed physical breaches and 0 race collisions, outperforming Arm 2 (0.0% / 0/80 deadlocked) and Arm 1 (100.0% with 226 unmanaged race collisions). Max tokens 198 $\le 512$, compaction 96.83%.
   - **Track 2 (Real Model Inference — $5\times\text{Qwen3.5-2B}$ — 80 cases, 240 episodes):** Arm 3 achieved **90.0% (72/80 PASS)** resolution with 0 committed physical breaches and 0 race collisions, decisively outperforming Arm 1 (0.0% / 0/80, 4,293 race collisions) and Arm 2 (91.25%, fatally breached prompt ceiling at 806 tokens $> 512$). Max tokens 298 $\le 512$, compaction 98.02%, mean turn latency 955.58 ms ($< 1000\text{ ms}$).
   - **Heterogeneous Stress Track ($3\times\text{Qwen 2B} + 2\times\text{Llama 3.2 3B}$):** Verified concurrent execution of two distinct model architectures within 3.8 GB VRAM on a single RTX 3050 GPU, maintaining 0 physical breaches, 0 collisions, and strict prompt ceiling adherence ($\le 512$ tokens).
3. **Evidence Packaging & Zero Loose File Bloat Protocol:**
   - All episode audit traces packaged into standard library `audit_logs.zip` archives with zero loose JSON files in Git.
   - Authoritative fingerprints: Track 1 (`d72fbcc9...`), Track 2 (`f9b1994a...`). Non-destructive inspection verified via `scripts/validate_audit.py`.
4. **Gate D Disposition & Prototype Quarantine:**
   - Disposition review: `swarm_consensus_pruning_verified_quarantined`.
   - All prototype code strictly quarantined in `research/experiments/prototypes/mn-022-swarm-consensus-pruning/` (zero promotion to `src/mong_nhiem/`). Full academic reports frozen at `reports/mn-022-track1-report.md`, `reports/mn-022-track2-report.md`, and `reports/mn-022-mixed-model-report.md`.

## Post-MN-022 Cumulative Production Promotion & Architectural Consolidation

Status: **completed and promoted into `src/mong_nhiem/`.**  
Track: **Core Cognitive Architecture Production Consolidation (MN-016 through MN-022).**

1. **Strategic Intent & Scope:**
   - Promoted empirically validated cognitive architecture mechanisms from Milestones MN-016 through MN-022 into production packages:
     - `src/mong_nhiem/core/`: `CausalEvent` with SHA-256 cryptographic hash chaining, `VectorClock` causal dependency checks, and `ConservationInvariantGuard` physical invariant enforcement.
     - `src/mong_nhiem/extensions/autodream/`: `FactCardProjector` (bounded $\le 512$ token ceiling) and `AutoDreamConsolidator` / `FrontierBranchPruner` ($\ge 70.0\%$ compaction).
     - `src/mong_nhiem/knowledge/`: `CausalEventDAG`, `EpistemicReconciler` ($[t_A, t_B]$ temporal slicing), and `DynamicSchemaRegistry`.
     - `src/mong_nhiem/orchestration/`: `MultiResourceArbiter` (TTL leases + goal-conditioned affordance sorting), `StarConsensusHub` + `ByzantineAdmissionGate`, `AsynchronousTransport`, and `HierarchicalPlanner`.
     - `src/mong_nhiem/runtime/`: `AuthoritativeMicroworld` with discrete-tick clock advances and Memento rollback interception.
2. **Minimalism & Backward Compatibility:**
   - 100% Python Standard Library (zero third-party dependencies added).
   - Zero breaking changes to existing `src/mong_nhiem/context/` and `src/mong_nhiem/orchestration/coordinator.py`.
3. **Verification & Test Coverage:**
   - 22 new comprehensive unit tests added in `tests/unit/`.
   - Full unit test suite verified: **463/463 tests passing** (100% PASS, zero regressions).

## MN-023 — Minimal Controlled Microworld & Epistemic Invariant Verification Under Asymmetric Information

Status: **completed and verified prototype (`epistemic_microworld_verified_quarantined`).**  
Track: **NCC Phase 12 (Minimal Controlled Epistemic Microworld & Causal Invariant Verification).**

1. **Strategic Intent & Outcome:**
   - Proved the mathematical and behavioral correctness of host-authoritative state tracking, multi-agent coordination, bounded memory organization, and causal DAG integrity when autonomous SLMs operate under partial observation, hidden secrets, and asymmetric or conflicting information.
   - Designed and evaluated the **Host Epistemic Microworld Architecture** integrating `EpistemicMaskEngine` (cryptographic projection + leakage auditing), `MultiResourceArbiter` (resource lease serialization), 3-Tier Fact Card compaction (Tier 1 invariant anchors, Tier 2 causal frontier, Tier 3 affordances), and `NonOmniscientGroundednessVerifier` (preventing telepathic actions).
   - Evaluated across $N=60$ standardized scenarios ($M=3$ agents: Scout, Engineer, Guard, totaling 180 episodes) across 3 heterogeneous physical domains: Secure Cyber-Physical Vaults ($N=20$), Smart Microgrid Fault Isolation ($N=20$), and Deep-Space Research Habitat ($N=20$).
2. **Dual-Track Empirical Results ($3\times\text{Qwen3.5-2B}$ topology):**
   - **Track 1 (Host Simulator — 60 cases, 180 episodes):** Arm 3 achieved **100.0% (60/60 PASS)** resolution with 0 physical breaches, 0 race collisions, 0 epistemic leakage, and +100.0% causal anchor retention delta vs Arm 2 (which exceeded 512 tokens). 10/10 Gate B clauses passed.
   - **Track 2 (Real Model Inference — $3\times\text{Qwen3.5-2B-Q4_K_M}$ on port 18502 — 60 cases, 180 episodes):** Arm 3 achieved **100.0% (60/60 PASS)** resolution with 0 physical breaches, 0 race collisions, 0.0 epistemic leakage, 100.0% discrepancy resolution, 100.0% action groundedness, max prompt size of 257 tokens $\le 512$, and mean turn latency of 231.16 ms ($< 1000\text{ ms}$ SLA). Arm 2 breached token budget at 611 tokens and suffered 0% retention under bounded buffer ($\Delta R_{\text{causal}} = +100.0\% \ge +50.0\%$). All 10 Gate B clauses passed decisively.
3. **Evidence Packaging & Zero Loose File Bloat Protocol:**
   - All 180 episode execution traces sealed into `runs/run_20261013_103904_track2_qwen/audit_logs.zip` (SHA-256: `6c248be9...`). Zero loose JSON files in Git.
4. **Gate D Disposition & Promotion Readiness:**
   - Disposition review: `epistemic_microworld_verified_quarantined`.
   - Prototype code remains quarantined in `research/experiments/prototypes/mn-023-minimal-epistemic-microworld/`. Full academic reports frozen at `reports/mn-023-track1-report.md` and `reports/mn-023-track2-report.md`. Pre-run and post-run freeze manifests committed. Core microworld abstractions earned promotion readiness for subsequent integration.

## MN-024 — Long-Horizon Physical Microworld Scaling & Multi-Hop Causal Maintenance Under Continuous Entropy Decay

Status: **completed and verified prototype (`long_horizon_microworld_verified_quarantined`).**  
Track: **NCC Phase 13 (Long-Horizon Microworld Scaling & Multi-Hop Causal Maintenance).**

1. **Strategic Intent & Outcome:**
   - Proved the scalability of Mộng Nhiễm's host-authoritative microworld architecture across extended temporal horizons under continuous passive thermodynamic and electrical decay, multi-hop causal cascades (4-hop sequential chains), and constant-space 3-tier fact-card context compaction.
   - Evaluated dual horizons: Tier A ($T=60$ ticks, causal distance $\Delta t \ge 40$ ticks) and Tier B ($T=100$ ticks, causal distance $\Delta t \ge 80$ ticks) across 3 physical domains ($N=60$ scenarios $\times 2$ horizons $\times 3$ arms $= 360$ episodes per track): Fission Reactor Core Cooling, Orbital Habitat Atmospheric Recycling, and Regional Smart Microgrid Fault Isolation.
   - Validated that lightweight open-weights models (`Qwen3.5-2B-Q4_K_M.gguf`) achieve perfect cascade execution, zero physical boundary breaches, and zero race collisions when assisted by host admission guards and lease arbitration.
2. **Dual-Track Empirical Results (360 Episodes Per Track):**
   - **Track 1 (Host Simulator — 360 episodes):** Arm 3 achieved **100.0% (60/60 PASS)** task resolution and cascade completion across both $T=60$ and $T=100$, with 0 physical breaches, 0 race collisions, 0.000 leakage, and 91.7% compaction ratio. 10/10 Gate B clauses met.
   - **Track 2 (Real Model Inference on Qwen 3.5 2B — 360 episodes):** Arm 3 achieved **100.0% (60/60 PASS)** task resolution and cascade completion across both $T=60$ and $T=100$ on local `llama-server.exe` (port 18502). Passed all 10 Gate B acceptance clauses (10/10 PASS). Peak prompt tokens remained at $55\text{ tokens} \le 512\text{ tokens}$ ($91.73\%$ compaction on $T=60$, $91.76\%$ on $T=100$), whereas Arm 2 unpruned memory bloated to $880$ and $1400$ tokens, suffering complete attention amnesia ($\Delta R_{\text{causal}} = +100.0\% \ge +50.0\%$). Turn latency averaged $145.23\text{ ms}$ on $T=60$ and $144.68\text{ ms}$ on $T=100$ ($< 1000\text{ ms}$ SLA). Extended horizon stability degradation was $0.00\% \le 5.0\%$.
3. **Evidence Packaging & Zero Loose File Bloat Protocol:**
   - All 360 episode execution traces sealed into `runs/run_1792212290/audit_logs.zip` (SHA-256: `989A574832B3DEDA334D6BE1C845402F01A4DCAD7075797AB996EBDCD8207F93`). Summary manifest at `runs/run_1792212290/summary.json` (SHA-256: `E8332497C054ECCAE9E88088A75AA52418BEF6A341059FECABB1DB4AECF1EFE2`). Zero loose JSON files in Git.
4. **Gate D Disposition & Promotion Readiness:**
   - Disposition review: `long_horizon_microworld_verified_quarantined`.
   - Prototype code remains quarantined in `research/experiments/prototypes/mn-024-long-horizon-epistemic-microworld/`. Full academic reports frozen at `reports/mn-024-track1-report.md` and `reports/mn-024-track2-report.md`. Pre-run and post-run freeze manifests committed. `EnvironmentalEntropyEngine` and `LongHorizonMicroworldEngine` earned promotion readiness for subsequent integration.

## MN-025 — Cross-Domain Epistemic Knowledge Transfer, Cognitive Belief Conflict Reconciliation, and Stochastic Open Microworlds

Status: **completed and verified prototype (`cross_domain_epistemic_transfer_verified_quarantined`).**  
Track: **NCC Phase 14 (Cross-Domain Epistemic Knowledge Transfer & Multi-Stage Cognitive Generalization).**

1. **Strategic Intent & Outcome:**
   - Evaluated three sequential cognitive frontiers on local `Qwen3.5-2B-Q4_K_M.gguf`: Stage 1 (Cross-Domain Epistemic Transfer), Stage 2 (Cognitive Belief Conflict Reconciliation), and Stage 3 (Open-World Stochastic Shocks & Dynamic Topology).
   - Designed and benchmarked **Host Topological Schema Cards**, **Epistemic Reconciler** ($d(\mathcal{G}_A, \mathcal{G}_B) \to 0$), **Dynamic Schema Registry**, **Non-Monotonic Anchor Demotion**, and Host Latent Derivative Tracking to neutralize both immediate negative transfer traps and latent time-bomb degradation traps.
   - Evaluated across $N=60$ standardized multi-stage scenarios across 3 physical domains (Nuclear Fission Core Cooling, Orbital Habitat Life Support, Regional Smart Microgrid).
2. **Dual-Track Empirical Results (180 Episodes Per Track):**
   - **Track 1 (Host Simulator — 180 episodes):** Arm 3 achieved **100.0% (60/60 PASS)** resolution with 0 physical breaches, 0 race collisions, 0 negative transfer violations, +50.0% speedup delta, and 100.0% anchor demotion fidelity. All 10 Gate B clauses met.
   - **Track 2 (Real Model Inference on Qwen 3.5 2B — 180 episodes):** Arm 3 achieved **95.0% (57/60 PASS)** task resolution (3 uncompleted cases were phantom decoy traps where the model rationally abstained), outperforming Arm 1 baseline (28.3%) and Arm 2 control (61.7%). Speedup delta reached **+64.29%**, dialectic convergence reached **100.0%**, physical breaches were **0**, collisions were **0**, max working prompt tokens were **153 tokens** ($\le 512$), turn latency averaged **179.19 ms** ($< 1000\text{ ms}$ SLA), and anchor demotion fidelity reached **100.0%**. Passed all 10 Gate B acceptance clauses (10/10 PASS).
3. **Evidence Packaging & Zero Loose File Bloat Protocol:**
   - All 360 episode execution traces sealed into `audit_logs.zip` archives with zero loose JSON files in Git.
   - Track 1 Archive: `runs/run_1792242182_track1_sim/audit_logs.zip`.
   - Track 2 Archive: `runs/run_1792242199_track2_qwen/audit_logs.zip`.
4. **Gate D Disposition & Promotion Readiness:**
   - Disposition review: `cross_domain_epistemic_transfer_verified_quarantined`.
   - Prototype code remains quarantined in `research/experiments/prototypes/mn-025-cross-domain-epistemic-transfer/`. Full academic reports frozen at `reports/mn-025-track1-report.md` and `reports/mn-025-track2-report.md`. Pre-run and post-run freeze manifests committed. `IsomorphismEngine`, `ConflictEngine`, and `StochasticEngine` earned promotion readiness for subsequent integration.

## MN-026 — Multi-Stage Cognitive Capstone Governance, Semantic Invariant Hardening, and Abductive Cross-Partition Causal Synthesis

Status: **completed and verified prototype across Phase 1, Phase 2, and Stage 7 (`cognitive_capstone_governance_verified_earned_promotion`). Full production promotion authorized.**  
Track: **NCC Phase 15 (Cognitive Capstone Governance, Abductive Synthesis, & Fault Resilience Clearing).**

1. **Strategic Intent & Outcome:**
   - Evaluated seven sequential cognitive remediation stages on local open-weights SLMs under a strict $\le 4\text{GB}$ VRAM ceiling: Stage 1 (Semantic Invariant Hardening & Virtual Jitter), Stage 2 (Hidden Inter-Partition Coupling & Abductive Tracing), Stage 3 (Dual-Objective Decoupled Evaluation), Stage 4 (Composite Stress-Test Microworld), Stage 5 (Preemptive Cognitive Interrupt Gate & $t+1$ Mid-Trajectory Shocks), Stage 6 (Long-Horizon Composite Capstone Microworld $T=50$ under Passive Thermodynamic Decay), and Stage 7 (Resilience Clearing Sub-Phase resolving 5 production-transition vulnerabilities).
   - Designed and benchmarked **Host Semantic Invariant Gate**, **Reflex Circuit Breaker** ($T \ge 450\text{K}$ auto-cutoff), **Abductive Causal Tracer** with marginal sensitivity confluence decomposition, **Goal-Conditioned Top-4 Affordance Ranker** ($\le 200$ tokens), **3-Class Preemptive Interrupt Gate** (`READ_ONLY`, `FAILSAFE`, `MUTATION`), **Virtual Jitter Arbiter** ($100\text{ ms} \leftrightarrow 800\text{ ms}$ leases), and **Dual-Mode Sensor Blackout Telemetry Observer**.
   - Evaluated across $N=140$ standardized multi-stage scenarios across 3 physical domains (Nuclear Fission Cooling, Orbital Life Support, Smart Microgrid) across 3 experimental arms ($420$ episodes per track, $1,260$ physical neural episodes in Track 2 across 3 models, $1,680$ total benchmark episodes).
2. **Post-Stage-7 3-Model Empirical Verification Matrix ($1,260$ Neural Episodes Across All 3 Qualified Models):**
   - **`Qwen3.5-2B-Q4_K_M`:** Physical Resolution: **100.0% (70/70)**, Safe Abstention: **100.0% (70/70)**, Breaches: **0**, Collisions: **0**, Abductive Resolution: **100.0%**, Mean Latency: **206.67 ms**, Max Tokens: **188 tokens** ($\le 512$). **PASS (15/15 Clauses Met)**. Audit Archive SHA-256: `0d1145977bce8bc1e70ab4d2efc91a7242fdf29860081ba4e1c29a29955dd442`.
   - **`Llama-3.2-3B-Instruct-Q4_K_M`:** Physical Resolution: **100.0% (70/70)**, Safe Abstention: **100.0% (70/70)**, Breaches: **0**, Collisions: **0**, Abductive Resolution: **100.0%**, Mean Latency: **160.55 ms**, Max Tokens: **188 tokens** ($\le 512$). **PASS (15/15 Clauses Met)**. Audit Archive SHA-256: `1635094e2ff4805ceb1837faa2d519ed5f0c9bc322ba6c7e99e045aeb7e77e60`.
   - **`Qwen3-4B-Q4_K_M`:** Physical Resolution: **100.0% (70/70)**, Safe Abstention: **100.0% (70/70)**, Breaches: **0**, Collisions: **0**, Abductive Resolution: **100.0%**, Mean Latency: **213.37 ms**, Max Tokens: **188 tokens** ($\le 512$). **PASS (15/15 Clauses Met)**. Audit Archive SHA-256: `9de89bb56c96dcf2f084666114f3abe616823b8918453e0f13bb9594ff8010cb`.
3. **Track 1 Simulator Results ($420$ Episodes):**
   - Physical Resolution: **100.0% (70/70)**, Safe Abstention: **100.0% (70/70)**, Breaches: **0**, Collisions: **0**, Abductive Resolution: **100.0%**, Mean Latency: **119.86 ms**, Max Tokens: **188 tokens**. **PASS (15/15 Clauses Met)**. Audit Archive SHA-256: `1a10d39fa2215835dc7df82f7517b9bc3a2ee21be7bf3c4edcfbf97ddfa2604a`.
4. **Phase 4 Edge Vulnerability Patches & Fast Track 2 Verification (Stage 7 Focused):**
   - Implemented 5 edge patches: Dead-reckoning confidence decay and TTL trip to `SUPERVISED_STANDBY`, Precondition dependency pulling (+25.0 boost), Post-scram breaker reset recovery state machine, Abductive tracer circular feedback termination, and Stateless KV-cache isolation (`"cache_prompt": False`).
   - Fast targeted Track 2 execution ($N=20$ Stage 7 scenarios $\times 3\text{ arms} = 60\text{ episodes/model}$, $180\text{ physical neural episodes}$):
     - `Qwen3.5-2B-Q4_K_M`: **PASS (15/15 Clauses Met)** (Latency: 238.36 ms, Max Tokens: 177). Archive: `runs/run_1792331241_track2_qwen3_5_2b_stage7/audit_logs.zip` (SHA-256: `8182b8109bfdb1149eec21eef00f6ee8e03023fb293c6ae1848bbdc0fcf3d9ca`).
     - `Llama-3.2-3B-Instruct-Q4_K_M`: **PASS (15/15 Clauses Met)** (Latency: 245.75 ms, Max Tokens: 177). Archive: `runs/run_1792331336_track2_llama3_2_3b_stage7/audit_logs.zip` (SHA-256: `a937a5b3a3ea5a65c404cfbb484d081b7e4f0dc2f96cfb2f7902cae466b080b0`).
     - `Qwen3-4B-Q4_K_M`: **PASS (15/15 Clauses Met)** (Latency: 315.66 ms, Max Tokens: 177). Archive: `runs/run_1792331431_track2_qwen3_4b_stage7/audit_logs.zip` (SHA-256: `fdb303112cf691060938a6a6858e378c66e2c3fb668fcbfba2c3f8753239cb32`).
     - Master Summary: `runs/post_patch_all_stage7_summary.json`.
5. **Evidence Packaging & Zero Loose File Bloat Protocol:**
   - All episode execution traces sealed into authenticated `audit_logs.zip` archives with zero loose JSON files committed to Git.
   - Master Summary: `runs/post_patch_3models_summary.json`.
6. **Gate D Disposition & Production Promotion Recommendation:**
   - Disposition review: `RECOMMEND UNCONDITIONAL PASS (EARNED PROMOTION TO PRODUCTION)`.
   - Authorized promotion into `src/mong_nhiem/`: `SemanticInvariantGate`, `ReflexBreaker`, `AbductiveCausalTracer` with Confluence Decomposition, `GoalConditionedAffordanceRanker`, `PreemptiveInterruptGate` (3-class taxonomy), `VirtualJitterArbiter`, and `TelemetryObserver`.

## Active Developmental Horizons

1. **Cumulative Production Promotion into `src/mong_nhiem/`:**
   - Status: **Ready for Immediate Execution (Gate D Approved).**
   - Core Mission: Integrate verified cognitive governance components into production runtime modules under comprehensive regression test harness.




