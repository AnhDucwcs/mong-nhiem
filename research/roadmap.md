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

Status: **scheduled active milestone.**  
Track: **NCC Phase 4 (Robust Action Synthesis).**

1. **Core Objective:** Eliminate formatting token collapses and punctuation/whitespace sensitivity on sub-4B models (`Qwen3.5-2B`) via native GBNF (Grammar-Based Context-Free Grammar) decoding at the `llama-server` engine layer.
2. **Core Mechanisms:**
   - **Native GBNF Action Grammar:** Engine-level logit masking enforcing strictly valid action syntax (`ACTION: READ <target>`, `ACTION: DISPATCH <tool> <payload>`, `ACTION: RESOLVE <ans>`), completely eliminating regex parsing failures and malformed parameter concatenation.
   - **Dynamic Affordance Filtering:** Injecting dynamic grammar rules or host-filtered candidate action lists to prevent the model from selecting unavailable tools.
   - **Full Stack Integration (MN-010 + MN-012 + MN-013 + MN-014):** Coupling bounded context working set ($\le 512$ tokens), Host Memento state stack, Phase Gate validation, and GBNF grammar decoding to target $\ge 85\%$ end-to-end task completion across all 60 benchmark cases.
3. **Pivoting Gate:** Evaluates whether GBNF grammar constraints eliminate all non-trap false rejections and elevate overall task completion to qualify for production promotion into `src/mong_nhiem/`.

## North Star Horizon: MN-Final — Stateful Simulated Microworld Evolution

Status: **ultimate benchmark / long-horizon destination.**  
Track: **NCC Phase 5 (Full Stateful World Continuity).**

1. **Ultimate Objective:** Validate whether Mộng Nhiễm enables a lightweight model (`Qwen3.5-2B`) to sustain, evolve, and reliably govern a multi-entity simulated world across extended discrete time horizons ($T \ge 20-50$ steps).
2. **Evaluation Protocol:**
   - An authoritative, discrete simulated microworld (locations, entities, inventories, physics/causal invariants).
   - Zero hallucinated state transitions, zero conservation-law breaches, and zero memory leaks.
3. **Incremental Gating & Failure Isolation Philosophy:**
   - Intermediate stepping stones (MN-012 Tool Memory, MN-013 Backtracking, MN-014 Grammar Decoding) methodically isolate and solve each cognitive and architectural failure mode before scaling to the full world simulation.





