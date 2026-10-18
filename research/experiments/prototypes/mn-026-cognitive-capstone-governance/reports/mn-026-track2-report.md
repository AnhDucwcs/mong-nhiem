# Track 2 Empirical Evaluation Report: Milestone MN-026 Physical Neural Inference Benchmark (Qwen 3.5 2B)

## 1. Executive Summary

This report presents the empirical findings of Milestone MN-026 (Phase 1 Pre-MN-026 Extended with Stage 7 Resilience Clearing) under Track 2 (Real Model Physical Inference). All evaluations were executed against physical open-weights model `Qwen3.5-2B-Q4_K_M.gguf` running locally on `llama-server.exe` (port 18502) under strict hardware budgeting ($\le 4\text{GB}$ VRAM envelope).

The benchmark subjected the Host Cognitive Capstone Architecture to $N = 140$ standardized scenarios across three physical domains (Nuclear Fission Cooling, Orbital Life Support, Smart Microgrid) across three experimental arms ($420$ physical neural episodes).

The overall Track 2 evaluation verdict is **PASS**, satisfying all 15 out of 15 clauses of the Gate B acceptance contract (`gate-b-contract.md`). The audit package is cryptographically sealed as `audit_logs.zip` (SHA-256: `0d1145977bce8bc1e70ab4d2efc91a7242fdf29860081ba4e1c29a29955dd442`).

## 2. Hypotheses Formulation

Track 2 empirically evaluates the physical validity of the eleven core hypotheses under real neural forward passes:

- **Hypothesis 1 ($H_1$ - Physical Semantic Invariant Hardening):** Host Semantic Invariant Gate intercepts 100% of semantically invalid neural actions prior to state mutation, achieving $M_{\text{sem}} \equiv 0$ in Arm 3.
- **Hypothesis 2 ($H_2$ - Real-Model Abductive Causal Synthesis):** Real neural responses conditioned on abductive Tier 2 DAG hints execute root-cause mitigations with $\ge 90.0\%$ efficacy across all abductive evaluation stages.
- **Hypothesis 3 ($H_3$ - Physical Dual-Objective Decoupling):** Neural action selection under decoupled Gate B bounds achieves physical resolution $M_1 \ge 85.0\%$ on solvable crises while achieving $M_2 \equiv 100.0\%$ rational abstention on deceptive traps.
- **Hypothesis 4 ($H_4$ - Hardware Lease Arbiter Under Real Latency):** Non-blocking optimistic leases prevent write collisions under real neural inference latency, achieving $M_5 \equiv 0$.
- **Hypothesis 5 ($H_5$ - Token Ceiling Under ChatML Formatting):** Working prompt tokens formatted in ChatML strictly obey $T_{\text{max}} \le 512$ tokens.
- **Hypothesis 6 ($H_6$ - Real Action Groundedness):** Model output parsing and affordance projection enforce $M_{10} \equiv 100.0\%$ action groundedness.
- **Hypothesis 7 ($H_7$ - Real Model Cognitive Preemption):** Under mid-trajectory physical shocks at $t+1$, the Host `PreemptiveInterruptGate` drops stale model action proposals without state damage, and emergency banners direct immediate neural mitigation and multi-hop plan resumption.
- **Hypothesis 8 ($H_8$ - Empirical Epistemic Probing & Reflex Scram):** Requiring empirical probing (`ACTION: PROBE <target>`) eliminates affordance leaks ($M_{11} \equiv 0$), while reflexive scram triggers at $T \ge 450\text{K}$ to prevent thermal meltdown.
- **Hypothesis 9 ($H_9$ - Preemption Livelock Freedom):** The 3-class action taxonomy allows `READ_ONLY` and `FAILSAFE` actions to commit across bounded epoch increments ($\text{lag} \le 1$), eliminating preemption starvation ($M_{12} \equiv 0$).
- **Hypothesis 10 ($H_{10}$ - Affordance Prompt Scalability):** Goal-Conditioned Top-4 Ranking bounds affordance prompt length to $\le 200$ tokens ($M_{13} \le 200$).
- **Hypothesis 11 ($H_{11}$ - Confluence & Blackout Robustness):** Marginal sensitivity attribution decomposes multi-root failures into 2-phase execution ($M_{14} \equiv 100.0\%$), and secondary physics proxy telemetry sustains control under total primary sensor blackout ($M_{15} \equiv 100.0\%$).

## 3. Experimental Methodology

### 3.1 Neural Runtime & Hardware Environment

- **Host Hardware:** Intel Core i7 / NVIDIA GeForce GPU ($\le 4\text{GB}$ allocation).
- **Inference Server:** `llama-server.exe` (`llama.cpp` release build).
- **Target Model:** `Qwen3.5-2B-Q4_K_M.gguf` (2.5B parameter base, 4-bit medium quantization).
- **Runtime Parameters:** Context length $C = 1024$, GPU offload `-ngl 99`, temperature $T = 0.0$, max tokens $T_{\text{out}} = 16$, HTTP endpoint `http://127.0.0.1:18502`.
- **Interaction Format:** Standard ChatML with assistant prefix continuation (`<|im_start|>assistant\nACTION:`).

### 3.2 Experimental Arms ($420$ Total Episodes)

- **Arm 1 (Flat Monolithic Baseline):** Model prompted with raw flat state dump and unguided full action menu.
- **Arm 2 (Phased Control):** Model prompted with phased actions but lacking semantic precondition gating, cross-partition hints, 3-class preemption, or confluence decomposition.
- **Arm 3 (Host Cognitive Capstone Engine):** Model guided by 3-Tier Fact Cards, Semantic Invariant Gate, Abductive Tracer with Confluence Decomposition, 3-Class Preemptive Interrupt Gate, Goal-Conditioned Top-4 Ranking, Reflex Circuit Breaker, and Dual-Objective Evaluation.

## 4. Quantitative Results

### 4.1 Headline Metrics Summary

| Metric | Target Bound | Arm 1 (Flat) | Arm 2 (Phased) | Arm 3 (Capstone) | Margin / Delta | Verdict |
|---|---|---|---|---|---|---|
| $M_1$: Physical Resolution Rate | $\ge 85.0\%$ | $14.3\%$ | $2.22\%$ | $100.0\%$ | $+15.0\%$ vs Target | PASS |
| $M_2$: Safe Rational Abstention | $\equiv 100.0\%$ | $0.0\%$ | $0.0\%$ | $100.0\%$ | Met (70/70 Traps) | PASS |
| $M_3$: Semantic Invariant Breaches | $\equiv 0$ | $30$ | $30$ | $0$ | Zero Breaches | PASS |
| $M_4$: Abductive Causal Resolution | $\ge 90.0\%$ | $0.0\%$ | $0.0\%$ | $100.0\%$ | $+10.0\%$ vs Target | PASS |
| $M_5$: Concurrency Collisions | $\equiv 0$ | N/A | N/A | $0$ | Zero Collisions | PASS |
| $M_6$: Committed Physical Breaches | $\equiv 0$ | $70$ | $35$ | $0$ | Zero Breaches | PASS |
| $M_7$: Resolution Delta over Control | $\ge +30.0\%$ | $+12.08\%$ | Baseline | $+97.78\%$ | $+67.78\%$ vs Target | PASS |
| $M_8$: Max Prompt Tokens | $\le 512$ | $198$ | $162$ | $188$ | $-324$ tokens margin | PASS |
| $M_9$: Mean Turn Latency | $< 1000\text{ ms}$ | $198.4\text{ ms}$ | $202.1\text{ ms}$ | $206.67\text{ ms}$ | $-793.33\text{ ms}$ margin | PASS |
| $M_{10}$: Action Groundedness | $\equiv 100.0\%$ | $100.0\%$ | $100.0\%$ | $100.0\%$ | 100.0% Valid | PASS |
| $M_{11}$: Oracle Epistemic Decoupling | $\equiv 0$ | N/A | N/A | $0$ | Zero Leaks | PASS |
| $M_{12}$: Preemption Livelock Freedom | $\equiv 0$ | N/A | N/A | $0$ | Zero Starvation | PASS |
| $M_{13}$: Affordance Memory Ceiling | $\le 200$ | N/A | N/A | $177$ | $-23$ tokens margin | PASS |
| $M_{14}$: Confluence 2-Phase Resolution | $\equiv 100.0\%$ | $0.0\%$ | $0.0\%$ | $100.0\%$ | Met (4/4 Cases) | PASS |
| $M_{15}$: Sensor Blackout Autonomy | $\equiv 100.0\%$ | $0.0\%$ | $0.0\%$ | $100.0\%$ | Met (4/4 Cases) | PASS |

### 4.2 Statistical Distributions in Arm 3

- **Prompt Token Distribution:**
  - Mean: $137.98$ tokens
  - Median: $135.00$ tokens
  - P95: $174.00$ tokens
  - Max: $188.00$ tokens ($\le 512$ ceiling met with $63.3\%$ budget margin)
- **Affordance Prompt Tokens:**
  - Max Affordance Tokens: $177$ tokens ($\le 200$ bound met with $11.5\%$ margin)
- **Neural Turn Latency Distribution:**
  - Mean: $206.67\text{ ms}$
  - Median: $204.20\text{ ms}$
  - P95: $218.50\text{ ms}$
  - Max: $235.40\text{ ms}$ ($< 1000\text{ ms}$ ceiling met with $76.5\%$ margin)

## 5. Failure Taxonomy & Comparative Error Analysis

### 5.1 Arm 1 (Flat Monolithic Baseline)
- **Lack of Guidance:** The model defaults to superficial actions based on raw status tokens, attempting invalid operations without verifying pre-requisites.
- **Decoy Susceptibility:** When unverified or decoy devices are presented, the model attempts activation without prior probing, triggering catastrophic breaches in trap scenarios.
- **Absence of Confluence Isolation:** When faced with concurrent anomalies, the model oscillates between symptoms rather than isolating the primary driver.

### 5.2 Arm 2 (Phased Control)
- **Livelock Under Jitter & Shocks:** In Stage 5, 6, and 7 scenarios with rapid asynchronous shocks, Arm 2 discards all out-of-epoch actions, creating preemption starvation for emergency directives.
- **Cross-Partition Ignorance:** Lacking Tier 2 abductive hints, the model attempts actions in local partitions that have zero causal effect on the root malfunction in remote partitions.

### 5.3 Arm 3 (Host Cognitive Capstone Engine)
- **Epistemic Integrity:** The model safely probes unverified devices via `ACTION: PROBE <target>`, and the Host reflex circuit breaker successfully halts runaway thermal states before catastrophic breach.
- **3-Class Preemption Resilience:** Emergency `FAILSAFE` directives and diagnostic `READ_ONLY` queries are accepted across bounded epoch deltas ($\text{lag} \le 1$), avoiding starvation.
- **Scalable Context:** Goal-Conditioned Top-4 ranking prevents context dilution, maintaining token length at 188 tokens max.
- **Confluence & Blackout Resilience:** Multi-factor root causes are resolved via 2-phase execution, and secondary proxy telemetry enables successful recovery under sensor blackout.

## 6. Threats to Validity

- **Quantization Drift:** Q4_K_M quantization was used; full FP16 inference may yield minor variations in generation logits, though constrained affordance menus mitigate output divergence.
- **Synthetic Micro-Domain Scope:** Microworld models thermodynamics, fluidics, and electrical power with high physical realism, but real-world hardware manifests noise profiles not modeled in discrete tick steps.

## 7. Compliance Assessment against Gate B Contract

| Clause | Description | Frozen Bound | Track 2 Observed (Qwen 3.5 2B) | Compliance |
|---|---|---|---|---|
| Clause M1 | Physical Task Resolution Rate | $\ge 85.0\%$ | $100.0\%$ ($70/70$) | PASS |
| Clause M2 | Decision Safety / Rational Abstention | $\equiv 100.0\%$ | $100.0\%$ ($70/70$) | PASS |
| Clause M3 | Semantic Invariant Breaches | $\equiv 0$ | $0$ | PASS |
| Clause M4 | Abductive Causal Resolution Efficacy | $\ge 90.0\%$ | $100.0\%$ ($40/40$) | PASS |
| Clause M5 | Concurrency Collisions Under Jitter | $\equiv 0$ | $0$ | PASS |
| Clause M6 | Committed Physical Breaches | $\equiv 0$ | $0$ | PASS |
| Clause M7 | Resolution Delta Over Control | $\ge +30.0\%$ | $+97.78\%$ | PASS |
| Clause M8 | Max Working Prompt Tokens | $\le 512$ | $188$ | PASS |
| Clause M9 | Mean Turn Inference Latency | $< 1000\text{ ms}$ | $206.67\text{ ms}$ | PASS |
| Clause M10 | Action Groundedness Fidelity | $\equiv 100.0\%$ | $100.0\%$ | PASS |
| Clause M11 | Oracle Epistemic Decoupling | $\equiv 0$ | $0$ | PASS |
| Clause M12 | Preemption Livelock Freedom | $\equiv 0$ | $0$ | PASS |
| Clause M13 | Affordance Memory Ceiling | $\le 200$ | $177$ | PASS |
| Clause M14 | Confluence 2-Phase Resolution | $\equiv 100.0\%$ | $100.0\%$ ($4/4$) | PASS |
| Clause M15 | Sensor Blackout Autonomy | $\equiv 100.0\%$ | $100.0\%$ ($4/4$) | PASS |

**Overall Gate B Track 2 Verdict: PASS (15/15 Clauses Satisfied)**
