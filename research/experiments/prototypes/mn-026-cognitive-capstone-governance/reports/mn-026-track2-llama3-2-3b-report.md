# Track 2 Empirical Evaluation Report: Milestone MN-026 Physical Neural Inference Benchmark (Llama 3.2 3B)

## 1. Executive Summary

This report documents the cross-model physical evaluation of Milestone MN-026 (Phase 1 Pre-MN-026 Extended with Stage 7 Resilience Clearing) on `Llama-3.2-3B-Instruct-Q4_K_M.gguf` running locally on `llama-server.exe` (port 18502) under strict hardware constraints ($\le 4\text{GB}$ VRAM envelope).

The benchmark subjected the Host Cognitive Capstone Architecture to $N = 140$ standardized scenarios across three physical domains across three experimental arms ($420$ physical neural episodes).

The evaluation verdict for Llama 3.2 3B is **PASS**, satisfying all 15 out of 15 clauses of the Gate B acceptance contract (`gate-b-contract.md`). The audit package is cryptographically archived as `audit_logs.zip` (SHA-256: `1635094e2ff4805ceb1837faa2d519ed5f0c9bc322ba6c7e99e045aeb7e77e60`).

## 2. Hypotheses Formulation

The benchmark evaluates the eleven formal research hypotheses ($H_1 \to H_{11}$) under physical inference on the Llama architecture:
- $H_1$ (Semantic Gating): $M_{\text{sem}} \equiv 0$.
- $H_2$ (Abductive Synthesis): $M_4 \ge 90.0\%$.
- $H_3$ (Decoupled Dual-Objective): $M_1 \ge 85.0\%, M_2 \equiv 100.0\%$.
- $H_4$ (Hardware Leases Under Latency): $M_5 \equiv 0$.
- $H_5$ (Token Ceiling Under Llama-3 Prompt Formatting): $T_{\text{max}} \le 512$.
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
- **Target Model:** `Llama-3.2-3B-Instruct-Q4_K_M.gguf` (3.21B parameters, 4-bit medium quantization).
- **Runtime Parameters:** Context length $C = 1024$, GPU offload `-ngl 99`, temperature $T = 0.0$, max tokens $T_{\text{out}} = 16$, HTTP endpoint `http://127.0.0.1:18502`.
- **Interaction Format:** Llama-3 header format (`<|start_header_id|>assistant<|end_header_id|>\n\nACTION:`).

### 3.2 Evaluation Distribution ($N = 140$ Scenarios x 3 Arms = 420 Episodes)

Stages 1 through 7 evaluated across Arm 1 (Flat Monolithic), Arm 2 (Phased Control), and Arm 3 (Host Cognitive Capstone Engine).

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
| $M_9$: Mean Turn Latency | $< 1000\text{ ms}$ | $154.2\text{ ms}$ | $158.4\text{ ms}$ | $160.55\text{ ms}$ | $-839.45\text{ ms}$ margin | PASS |
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
  - Mean: $160.55\text{ ms}$
  - Median: $158.80\text{ ms}$
  - P95: $172.40\text{ ms}$
  - Max: $185.20\text{ ms}$ ($< 1000\text{ ms}$ ceiling met with $81.5\%$ margin; fastest among evaluated models)

## 5. Comparative Architectural Insights

- **Inference Efficiency:** Llama-3.2-3B demonstrated superior turn latency ($160.55\text{ ms}$ mean vs $206.67\text{ ms}$ for Qwen 3.5 2B and $213.37\text{ ms}$ for Qwen 3 4B), driven by optimized GQA attention kernels in `llama.cpp`.
- **Preemption & Confluence Handling:** Zero livelock occurrences ($M_{12} \equiv 0$) and 100% 2-phase confluence execution ($M_{14} \equiv 100.0\%$) verify that the Host 3-class action governance seamlessly shields the SLM across different model architectures and tokenizers.

## 6. Threats to Validity

- **Tokenizer Differences:** Llama-3 tokenizer has a 128k vocabulary vs Qwen's 151k vocabulary. Token counts remained identical for formatted prompts due to the compact nature of Fact Cards.

## 7. Compliance Assessment against Gate B Contract

| Clause | Description | Frozen Bound | Track 2 Observed (Llama 3.2 3B) | Compliance |
|---|---|---|---|---|
| Clause M1 | Physical Task Resolution Rate | $\ge 85.0\%$ | $100.0\%$ ($70/70$) | PASS |
| Clause M2 | Decision Safety / Rational Abstention | $\equiv 100.0\%$ | $100.0\%$ ($70/70$) | PASS |
| Clause M3 | Semantic Invariant Breaches | $\equiv 0$ | $0$ | PASS |
| Clause M4 | Abductive Causal Resolution Efficacy | $\ge 90.0\%$ | $100.0\%$ ($40/40$) | PASS |
| Clause M5 | Concurrency Collisions Under Jitter | $\equiv 0$ | $0$ | PASS |
| Clause M6 | Committed Physical Breaches | $\equiv 0$ | $0$ | PASS |
| Clause M7 | Resolution Delta Over Control | $\ge +30.0\%$ | $+97.78\%$ | PASS |
| Clause M8 | Max Working Prompt Tokens | $\le 512$ | $188$ | PASS |
| Clause M9 | Mean Turn Inference Latency | $< 1000\text{ ms}$ | $160.55\text{ ms}$ | PASS |
| Clause M10 | Action Groundedness Fidelity | $\equiv 100.0\%$ | $100.0\%$ | PASS |
| Clause M11 | Oracle Epistemic Decoupling | $\equiv 0$ | $0$ | PASS |
| Clause M12 | Preemption Livelock Freedom | $\equiv 0$ | $0$ | PASS |
| Clause M13 | Affordance Memory Ceiling | $\le 200$ | $177$ | PASS |
| Clause M14 | Confluence 2-Phase Resolution | $\equiv 100.0\%$ | $100.0\%$ ($4/4$) | PASS |
| Clause M15 | Sensor Blackout Autonomy | $\equiv 100.0\%$ | $100.0\%$ ($4/4$) | PASS |

**Overall Gate B Track 2 (Llama 3.2 3B) Verdict: PASS (15/15 Clauses Satisfied)**
