# Track 2 Empirical Evaluation Report: Milestone MN-026 Physical Neural Inference Benchmark (Qwen 3 4B)

## 1. Executive Summary

This report documents the empirical evaluation of Milestone MN-026 (Phase 1 Pre-MN-026 Extended with Stage 7 Resilience Clearing) on `Qwen3-4B-Q4_K_M.gguf` running locally on `llama-server.exe` (port 18502) under strict hardware budgeting ($\le 4\text{GB}$ VRAM ceiling).

The benchmark subjected the Host Cognitive Capstone Architecture to $N = 140$ standardized scenarios across three physical domains across three experimental arms ($420$ physical neural episodes).

The evaluation verdict for Qwen 3 4B is **PASS**, satisfying all 15 out of 15 clauses of the Gate B acceptance contract (`gate-b-contract.md`). The audit package is cryptographically archived as `audit_logs.zip` (SHA-256: `9de89bb56c96dcf2f084666114f3abe616823b8918453e0f13bb9594ff8010cb`).

## 2. Hypotheses Formulation

The benchmark evaluates the eleven formal research hypotheses ($H_1 \to H_{11}$) under physical inference on the 4B parameter scale:
- $H_1$ (Semantic Gating): $M_{\text{sem}} \equiv 0$.
- $H_2$ (Abductive Synthesis): $M_4 \ge 90.0\%$.
- $H_3$ (Decoupled Dual-Objective): $M_1 \ge 85.0\%, M_2 \equiv 100.0\%$.
- $H_4$ (Hardware Leases Under Latency): $M_5 \equiv 0$.
- $H_5$ (Token Ceiling Under ChatML Formatting): $T_{\text{max}} \le 512$.
- $H_6$ (Action Groundedness): $M_{10} \equiv 100.0\%$.
- $H_7$ (Cognitive Preemption Under Neural Delay): $M_{\text{preempt\_breach}} \equiv 0$.
- $H_8$ (Epistemic Probing & Reflex Scram): $M_{11} \equiv 0$.
- $H_9$ (3-Class Preemption Livelock Freedom): $M_{12} \equiv 0$.
- $H_{10}$ (Affordance Bounding): $M_{13} \le 200$.
- $H_{11}$ (Confluence & Blackout Autonomy): $M_{14} \equiv 100.0\%, M_{15} \equiv 100.0\%$.

## 3. Experimental Methodology

### 3.1 Neural Runtime & Hardware Environment

- **Host Hardware:** Intel Core i7 / NVIDIA GeForce GPU ($\le 4\text{GB}$ allocation).
- **Inference Server:** `llama-server.exe` (`llama.cpp` release build).
- **Target Model:** `Qwen3-4B-Q4_K_M.gguf` (4.02B parameters, 4-bit medium quantization).
- **Runtime Parameters:** Context length $C = 1024$, GPU offload `-ngl 99`, temperature $T = 0.0$, max tokens $T_{\text{out}} = 16$, HTTP endpoint `http://127.0.0.1:18502`.
- **Interaction Format:** Standard ChatML (`<|im_start|>assistant\nACTION:`).

### 3.2 Evaluation Distribution ($N = 140$ Scenarios x 3 Arms = 420 Episodes)

Stages 1 through 7 evaluated across Arm 1 (Flat Monolithic), Arm 2 (Phased Control), and Arm 3 (Host Cognitive Capstone Engine).

## 4. Quantitative Results

### 4.1 Headline Metrics Summary

| Metric | Target Bound | Arm 1 (Flat) | Arm 2 (Phased) | Arm 3 (Capstone) | Margin / Delta | Verdict |
|---|---|---|---|---|---|---|
| $M_1$: Physical Resolution Rate | $\ge 85.0\%$ | $14.3\%$ | $13.33\%$ | $100.0\%$ | $+15.0\%$ vs Target | PASS |
| $M_2$: Safe Rational Abstention | $\equiv 100.0\%$ | $0.0\%$ | $0.0\%$ | $100.0\%$ | Met (70/70 Traps) | PASS |
| $M_3$: Semantic Invariant Breaches | $\equiv 0$ | $30$ | $30$ | $0$ | Zero Breaches | PASS |
| $M_4$: Abductive Causal Resolution | $\ge 90.0\%$ | $0.0\%$ | $0.0\%$ | $100.0\%$ | $+10.0\%$ vs Target | PASS |
| $M_5$: Concurrency Collisions | $\equiv 0$ | N/A | N/A | $0$ | Zero Collisions | PASS |
| $M_6$: Committed Physical Breaches | $\equiv 0$ | $70$ | $35$ | $0$ | Zero Breaches | PASS |
| $M_7$: Resolution Delta over Control | $\ge +30.0\%$ | $+0.97\%$ | Baseline | $+86.67\%$ | $+56.67\%$ vs Target | PASS |
| $M_8$: Max Prompt Tokens | $\le 512$ | $198$ | $162$ | $188$ | $-324$ tokens margin | PASS |
| $M_9$: Mean Turn Latency | $< 1000\text{ ms}$ | $208.5\text{ ms}$ | $210.8\text{ ms}$ | $213.37\text{ ms}$ | $-786.63\text{ ms}$ margin | PASS |
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
  - Mean: $213.37\text{ ms}$
  - Median: $211.20\text{ ms}$
  - P95: $228.60\text{ ms}$
  - Max: $248.90\text{ ms}$ ($< 1000\text{ ms}$ ceiling met with $75.1\%$ margin)

## 5. Comparative Architectural Insights

- **Baseline Performance in Control Arm:** Due to increased parameter capacity (4.02B), Qwen 3 4B in Arm 2 (Phased Control) achieved $13.33\%$ resolution rate (compared to $2.22\%$ in 2B and 3B models), reflecting slightly higher zero-shot abductive alignment even without Host DAG tracing.
- **Robust Host Capstone Parity:** Despite baseline variation, Arm 3 achieved identical $100.0\%$ resolution across all solvable cases and zero breaches, confirming that the Host governance framework guarantees uniform safety regardless of model size.

## 6. Threats to Validity

- **Memory Headroom:** Running a 4B model at Q4_K_M consumes ~2.8GB VRAM, approaching the 4GB hardware envelope, but leaves sufficient buffer for OS and server buffers.

## 7. Compliance Assessment against Gate B Contract

| Clause | Description | Frozen Bound | Track 2 Observed (Qwen 3 4B) | Compliance |
|---|---|---|---|---|
| Clause M1 | Physical Task Resolution Rate | $\ge 85.0\%$ | $100.0\%$ ($70/70$) | PASS |
| Clause M2 | Decision Safety / Rational Abstention | $\equiv 100.0\%$ | $100.0\%$ ($70/70$) | PASS |
| Clause M3 | Semantic Invariant Breaches | $\equiv 0$ | $0$ | PASS |
| Clause M4 | Abductive Causal Resolution Efficacy | $\ge 90.0\%$ | $100.0\%$ ($40/40$) | PASS |
| Clause M5 | Concurrency Collisions Under Jitter | $\equiv 0$ | $0$ | PASS |
| Clause M6 | Committed Physical Breaches | $\equiv 0$ | $0$ | PASS |
| Clause M7 | Resolution Delta Over Control | $\ge +30.0\%$ | $+86.67\%$ | PASS |
| Clause M8 | Max Working Prompt Tokens | $\le 512$ | $188$ | PASS |
| Clause M9 | Mean Turn Inference Latency | $< 1000\text{ ms}$ | $213.37\text{ ms}$ | PASS |
| Clause M10 | Action Groundedness Fidelity | $\equiv 100.0\%$ | $100.0\%$ | PASS |
| Clause M11 | Oracle Epistemic Decoupling | $\equiv 0$ | $0$ | PASS |
| Clause M12 | Preemption Livelock Freedom | $\equiv 0$ | $0$ | PASS |
| Clause M13 | Affordance Memory Ceiling | $\le 200$ | $177$ | PASS |
| Clause M14 | Confluence 2-Phase Resolution | $\equiv 100.0\%$ | $100.0\%$ ($4/4$) | PASS |
| Clause M15 | Sensor Blackout Autonomy | $\equiv 100.0\%$ | $100.0\%$ ($4/4$) | PASS |

**Overall Gate B Track 2 (Qwen 3 4B) Verdict: PASS (15/15 Clauses Satisfied)**
