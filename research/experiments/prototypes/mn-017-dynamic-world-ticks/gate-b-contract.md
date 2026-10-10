# Gate B Evaluation Contract — Milestone MN-017: Dynamic World Ticks & Hierarchical Planning

## 1. Executive Evaluation Contract

This document formalizes the quantitative acceptance criteria, evaluation methodology, failure taxonomy, and threat models for Milestone **MN-017** (*Dynamic World Ticks & Hierarchical Planning*).

Execution occurs across two validation tracks:
- **Track 1: Deterministic Simulator**: Programmatic state machine executing 40 benchmark cases across 3 arms to verify state invariants, multi-rate clock mechanics, and DAG phase-gate progression.
- **Track 2: Real Model Inference**: Real LLM inference executing 40 cases across 3 arms on `Qwen3.5-2B-Q4_K_M.gguf` via `llama-server.exe` ($T = 0.0$, greedy decoding, native GBNF grammar).

---

## 2. Frozen Support Rules & Quantitative Thresholds

To pass Gate B and qualify for Gate D architectural disposition review, the prototype must satisfy all five frozen rules simultaneously under Track 2:

### Rule 1: Task Completion Efficacy Gate
$$\text{Accuracy}(\text{Arm 3}) \ge 90.0\% \quad (36/40 \text{ cases})$$
$$\Delta \text{Accuracy} = \text{Accuracy}(\text{Arm 3}) - \text{Accuracy}(\text{Arm 1}) \ge +40.0\%$$
- Arm 3 must resolve complex multi-phase missions ($K = 3-5$ sub-goals, $T = 15-35$ steps) under concurrent environmental drift.
- Unassisted flat baseline (Arm 1) must be shown to fail significantly due to Goal Divergence and Stale-State Overwrites.

### Rule 2: Zero Stale-State Mutation Invariant
$$\text{StaleMutationRate}(\text{Arm 3}) = 0.0\% \quad (0 \text{ violations across all turns})$$
- When a world entity mutates asynchronously during agent planning, any attempt to mutate based on a stale version ($v_{agent} < v_{world}$) must be intercepted and rejected by the Host with an atomic refresh notice.

### Rule 3: Zero Horizon Jumping Invariant
$$\text{HorizonJumpingRate}(\text{Arm 3}) = 0.0\% \quad (0 \text{ out-of-order action emissions})$$
- Actions pertaining to unactivated future sub-goals ($G_{>k}$) must never be emitted or accepted during the execution of active sub-goal $G_k$. Dynamic GBNF affords only valid $G_k$ actions.

### Rule 4: Absolute Forward-Pass Token Ceiling Invariant
$$\max_{t}(\text{PromptTokens}_t) \le 512 \quad \text{for } 100.0\% \text{ of turns}$$
$$\mathbb{E}[\text{PromptTokens}] \le 384 \quad \text{across all turns}$$
- Working memory context delivered to the model must remain strictly bounded by delivering only the active sub-goal $G_k$, immediate relevant entity cards, and delta notices.

### Rule 5: Turn Latency SLA
$$\mathbb{E}[\text{TurnLatency}] < 1000\text{ ms} \quad \text{on local } \text{llama-server.exe}$$
$$\max(\text{HostOverhead}) < 10.0\text{ ms}$$
- Mean turn latency must adhere to interactive small-model deployment limits. Host-side clock progression, DAG evaluation, and grammar compilation must execute in single-digit milliseconds.

---

## 3. Comparative Evaluation Arms

| Parameter | Arm 1: Flat Baseline | Arm 2: Static Plan Control | Arm 3: Dual-Engine MN-017 |
|---|---|---|---|
| **Goal Framing** | Global mission text dumped into prompt | Sequential sub-goals $G_k$ presented | Active sub-goal $G_k$ scoped prompt |
| **Affordance Constraint** | Unconstrained global GBNF | Unconstrained global GBNF | Dynamic GBNF masked strictly to $G_k$ |
| **World Ticks** | Active ($\Delta t_{world} = 1-3$) | Active ($\Delta t_{world} = 1-3$) | Active ($\Delta t_{world} = 1-3$) |
| **Concurrency Guard** | Disabled (Silent stale overwrite) | Disabled (Silent stale overwrite) | Enabled (Host version check & delta) |
| **Phase Advancement** | Self-declared by model | Evaluated by Host predicate | Evaluated by Host predicate |

---

## 4. Failure Mode Taxonomy

Every failed run must be classified into one of the following mutually exclusive categories:
1. `FAIL_HORIZON_JUMPING`: Model attempts an action associated with a future unactivated sub-goal before prerequisites are met.
2. `FAIL_PREMATURE_RESOLUTION`: Model claims mission completion before all DAG sub-goals are satisfied.
3. `FAIL_STALE_STATE_OVERWRITE`: Agent executes mutation based on superseded entity version, causing environment corruption or constraint violation.
4. `FAIL_TOKEN_OVERFLOW`: Forward-pass prompt size exceeds the hard ceiling of $512$ tokens.
5. `FAIL_DEADLOCK_CYCLE`: Agent gets trapped in repeated identical action attempts without progressing the active sub-goal.
6. `FAIL_TIMEOUT_EXCEEDED`: Mission turn limit ($T_{max} = 40$) exceeded without achieving terminal goal.

---

## 5. Threats to Validity

### Internal Validity
- **Causal Attribution**: The 3 matched arms isolate the exact impact of (a) GBNF-governed sub-goal scoping vs flat prompting, and (b) Concurrency Guard versioning vs unassisted world drift.
- **Determinism**: Greedy decoding ($T=0.0$), fixed pseudo-random seeds, and frozen test cases ensure zero non-deterministic variance between runs.

### External Validity
- Synthetic domains (Infrastructure, Asset Logistics, Registry) model realistic production microworld patterns (leases, resource drains, heartbeats).
- Evaluated on qualified 2B small model (`Qwen3.5-2B-Q4_K_M.gguf`), establishing bounds directly applicable to resource-constrained local deployment.

### Construct Validity
- Task success requires actual verification by Host symbolic predicates in the state store, preventing superficial text compliance from masking semantic state failure.
