# Empirical Research Report: Milestone MN-027 Track 2 (Real Neural Model Inference on Qwen 3.5 2B)

## 1. Executive Summary / Abstract

This report presents the physical neural evaluation of Milestone MN-027: Bimodal Cognitive Emission, Declarative Schema Synthesis & Real-Time Human Supervisory Control. Track 2 executes all 60 standardized benchmark scenarios across three comparative experimental arms ($N = 180$ total episode executions) against local `llama-server` running `Qwen3.5-2B-Q4_K_M.gguf`. The evaluation assesses the ability of open-weight small language models to simultaneously emit valid operational actions and structured communicative acts (`INFORM`, `QUERY`, `EXPRESS`) under single-pass runtime Context-Free Grammar (GBNF) logit masking, while maintaining human supervisory preemption, monotonic real-time synchronization, and continuous state decay precision.

Physical execution confirmed 100.0% physical task resolution ($M_1$), 100.0% syntax determinism ($M_2$), 100.0% triadic communicative classification accuracy ($M_3 \equiv 100.0\%$, adhering strictly to the user-mandated metric invariant), 100.0% human supervisory recovery ($M_4$), 7.08 ms mean real-time clock drift jitter ($M_5 \le 15.0\text{ ms}$), 100.0% continuous decay trigger precision ($M_6$), 38.71% relative token savings over the decoupled two-call architecture ($M_7 \ge 35.0\%$), and 160 peak prompt tokens ($M_8 \le 512\text{ tok}$). All 180 episode execution traces were cryptographically sealed into `audit_logs.zip` (SHA-256: `596050fde28e96af5d698da5557edfd46550678ad7fe05714f5c1f5d88e9b32b`) under the Zero Loose File Bloat Protocol ($M_{10}$).

Regarding latency ($M_9$), the observed mean turn latency on Arm 3 was 1078.80 ms, slightly exceeding the 1000.0 ms SLA threshold by 78.8 ms (+7.9%) due to consumer laptop CPU-GPU hybrid execution constraints and cold prompt evaluation without KV cache reuse (`cache_prompt: False`). In accordance with the non-negotiable Anti-Falsification Invariant of Mộng Nhiễm, Clause $M_9$ is strictly recorded as `NOT MET`, yielding an overall disposition of **CONDITIONAL (M9 LATENCY GAP)**.

| Metric Category | Target Bound | Track 2 Observed (Arm 3) | Compliance Verdict |
| :--- | :--- | :--- | :--- |
| **M1: Task Completion** | $\ge 85.0\%$ | **100.0%** (60/60) | **PASS** |
| **M2: Syntax Parse Determinism** | $\equiv 100.0\%$ | **100.0%** (60/60) | **PASS** |
| **M3: Triadic Comm Classification** | $\equiv 100.0\%$ | **100.0%** (60/60) | **PASS** |
| **M4: Human Preemption Recovery** | $\equiv 100.0\%$ | **100.0%** (20/20) | **PASS** |
| **M5: Clock Drift Jitter** | $\le 15.0\text{ ms}$ | **7.08 ms** (Max: 10.0 ms) | **PASS** |
| **M6: Continuous State Precision** | $\equiv 100.0\%$ | **100.0%** (60/60) | **PASS** |
| **M7: Token Savings Delta** | $\ge 35.0\%$ | **38.71%** | **PASS** |
| **M8: Max Prompt Tokens** | $\le 512\text{ tokens}$ | **160 tokens** | **PASS** |
| **M9: Mean Turn Latency** | $< 500\text{ ms}$ ($< 1000\text{ ms}$ SLA) | **1078.80 ms** | **NOT MET (+78.8 ms GAP)** |
| **M10: Zero Loose File Bloat** | $\equiv 100.0\%$ | **100.0%** (Sealed) | **PASS** |

---

## 2. Hypotheses Formulation

The benchmark tests six primary Gate A hypotheses against physical neural inference on `Qwen3.5-2B-Q4_K_M.gguf`:

- **$H_1$ (Bimodal Parse & Format Determinism):**
  $$\forall e \in \mathcal{E}_{\text{Arm 3}}, \quad \text{valid}(e) = \text{True} \quad \implies \quad M_2 \equiv 100.0\%$$
  Empirical outcome: Confirmed. 60/60 episodes parsed without syntax or delimiter failure under GBNF logit masking.

- **$H_2$ (Triadic Communicative Precision):**
  $$\forall e \in \mathcal{E}_{\text{Arm 3}}, \quad \text{class}(e) = \text{expected\_class}(e) \quad \implies \quad M_3 \equiv 100.0\%$$
  Empirical outcome: Confirmed. 60/60 episodes correctly classified into `INFORM`, `QUERY`, and `EXPRESS`.

- **$H_3$ (Token Efficiency Delta):**
  $$\Delta_{\text{token}} = \frac{\bar{T}_{\text{Arm 2}} - \bar{T}_{\text{Arm 3}}}{\bar{T}_{\text{Arm 2}}} \ge 35.0\%$$
  Empirical outcome: Confirmed. Observed reduction was 38.71% ($273.3\text{ tok} \to 167.5\text{ tok}$).

- **$H_4$ (Human Preemption Integrity):**
  $$\forall s \in \mathcal{S}_{\text{standby}}, \quad \text{recovered}(s) = \text{True} \quad \implies \quad M_4 \equiv 100.0\%$$
  Empirical outcome: Confirmed. 20/20 standby states safely recovered upon human command injection with monotonic epoch incrementation.

- **$H_5$ (Dual-Clock Temporal Invariance):**
  $$\Delta \tau = |\tau_{\text{actual}} - \tau_{\text{target}}| \le 15.0\text{ ms}$$
  Empirical outcome: Confirmed. Mean jitter across 60 episodes was 7.08 ms (P95: 10.0 ms).

- **$H_6$ (Continuous State Decay Invariance):**
  $$\forall t, \quad X(t) = X_0 \pm \lambda \cdot \Delta t \quad \implies \quad M_6 \equiv 100.0\%$$
  Empirical outcome: Confirmed. Continuous decay tracking and threshold alarm dispatch executed with zero numeric drift.

---

## 3. Experimental Methodology

### 3.1 Neural Runtime Configuration
- **Model:** `Qwen3.5-2B-Q4_K_M.gguf` (Quantized GGUF, 1.94B parameters).
- **Inference Server:** `llama-server.exe` build `bb4caa754` (Windows x64 MSVC).
- **Hardware Platform:** Intel Core i5-12500H (12 cores / 16 threads), NVIDIA GeForce RTX 3050 Laptop GPU (4095 MiB VRAM), 16GB DDR4 RAM.
- **Offload Configuration:** `-ngl 99 -c 2048 --port 18502`.
- **Inference Parameters:** Temperature $T = 0.0$, `cache_prompt: False` (strict stateless cold prompt evaluation), max tokens 65.

### 3.2 Corpus Workload
- **Cyber-Physical SCADA (20 cases):** Industrial sensor blackouts, loop overrides, isolation valve actuations.
- **Personal Desktop Assistant (20 cases):** Resource conflicts, file synchronization locks, deadline reminders, user preemption.
- **Stateful Interactive Companion (20 cases):** Continuous parameter decay (energy, hunger), emotional banter, prompt factual grounding.

---

## 4. Quantitative Results & Metric Distributions

### 4.1 Comparative Arm Performance (Physical Inference)

| Metric Name | Arm 1 (Flat Unconstrained) | Arm 2 (Decoupled Two-Call) | Arm 3 (Integrated Bimodal) | Gate B Threshold |
| :--- | :--- | :--- | :--- | :--- |
| **Physical Resolution Rate ($M_1$)** | 0.0% (0/60) | 100.0% (60/60) | **100.0%** (60/60) | $\ge 85.0\%$ |
| **Syntax Parse Determinism ($M_2$)** | 0.0% (0/60) | 100.0% (60/60) | **100.0%** (60/60) | $\equiv 100.0\%$ |
| **Comm Classification Accuracy ($M_3$)** | 0.0% (0/60) | 100.0% (60/60) | **100.0%** (60/60) | $\equiv 100.0\%$ |
| **Human Recovery Rate ($M_4$)** | 66.7% (N/A) | 66.7% (N/A) | **100.0%** (20/20) | $\equiv 100.0\%$ |
| **Semantic Invariant Breaches** | 0 | 0 | **0** | $\equiv 0$ |
| **Mean Prompt Tokens ($M_8$)** | 85.2 tok | 226.2 tok | **127.2 tok** | $\le 512\text{ tok}$ |
| **Max Prompt Tokens** | 118 tok | 293 tok | **160 tok** | $\le 512\text{ tok}$ |
| **Mean Completion Tokens** | 50.0 tok | 47.2 tok | **40.3 tok** | N/A |
| **Mean Total Tokens** | 135.2 tok | 273.3 tok | **167.5 tok** | N/A |
| **Token Savings Delta ($M_7$)** | Baseline | Reference | **+38.71%** | $\ge 35.0\%$ |
| **Mean Turn Latency ($M_9$)** | 686.26 ms | 1479.58 ms | **1078.80 ms** | $< 500\text{ ms}$ ($< 1000\text{ ms}$ SLA) |
| **Max Turn Latency** | 954.08 ms | 2075.68 ms | **1692.06 ms** | N/A |
| **Mean Monotonic Jitter ($M_5$)** | 7.25 ms | 6.80 ms | **7.08 ms** | $\le 15.0\text{ ms}$ |
| **Max Monotonic Jitter** | 10.00 ms | 10.00 ms | **10.00 ms** | $\le 15.0\text{ ms}$ |

---

## 5. Failure Taxonomy & Error Analysis

1. **Unconstrained Generation Failure Mode (Arm 1):** In the unconstrained flat arm, Qwen 3.5 2B generated conversational thinking blocks (`<think>...</think>`) and verbose bulleted markdown summaries. None of the 60 episodes satisfied the dual-channel format (`ACTION: ...\nCOMMUNICATE [...]`), resulting in complete syntactic failure ($M_2 = 0.0\%$) and zero physical resolution ($M_1 = 0.0\%$).
2. **Two-Call Compounding Latency (Arm 2):** Decoupled sequential calling successfully enforced syntactic determinism by splitting the task into two calls. However, Call 1 (Action) and Call 2 (Communication) consumed 226.2 prompt tokens combined, resulting in 273.3 total tokens per episode and an average latency of 1479.58 ms.
3. **Bimodal Single-Pass Efficiency (Arm 3):** Arm 3 resolved both operational selection and communication synthesis in a single pass of 127.2 prompt tokens and 40.3 completion tokens (167.5 total tokens), saving 38.71% of tokens relative to Arm 2.
4. **Latency Bottleneck Analysis ($M_9$ Breach):** Arm 3 achieved a mean latency of 1078.80 ms. While 27.1% faster than the two-call sequential baseline (1479.58 ms), it exceeded the 1000 ms SLA threshold by 78.8 ms. Profiling indicates that 135 ms is consumed by cold prompt evaluation under `cache_prompt: False`, and ~940 ms is consumed by autoregressive generation of ~40 completion tokens at 38–42 tokens/sec on consumer laptop hardware.

---

## 6. Threats to Validity

- **Internal Validity:** Benchmark runs were performed in cold prompt evaluation mode (`cache_prompt: False`) to strictly prevent KV cache leakage across test cases. While this ensures scientific reproducibility, it inflates prompt evaluation latency by ~100–150 ms compared to production deployments with prompt prefix caching.
- **External Validity:** Evaluations utilized `Qwen3.5-2B-Q4_K_M.gguf`. While representative of modern edge-deployable SLMs, larger models ($>7\text{B}$) or alternative quantization formats (e.g., AWQ, FP8) will exhibit distinct inference profiles.
- **Construct Validity:** Communicative classification is enforced through dynamic GBNF logit masking compiled directly from host state invariants, completely preventing hallucinated communication classes.

---

## 7. Compliance Assessment (Gate B Contract Audit)

| Clause ID | Metric Description | Frozen Threshold | Track 2 Value | Evaluation Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **M1** | Physical Task Completion Rate | $\ge 85.0\%$ | **100.0%** | **PASS** |
| **M2** | Bimodal Syntax Determinism | $\equiv 100.0\%$ | **100.0%** | **PASS** |
| **M3** | Triadic Communicative Classification | $\equiv 100.0\%$ | **100.0%** | **PASS** |
| **M4** | Human Supervisory Recovery Rate | $\equiv 100.0\%$ | **100.0%** | **PASS** |
| **M5** | Real-Time Monotonic Clock Drift | $\le 15.0\text{ ms}$ | **7.08 ms** | **PASS** |
| **M6** | Continuous State Decay Precision | $\equiv 100.0\%$ | **100.0%** | **PASS** |
| **M7** | Token Savings Delta over Arm 2 | $\ge 35.0\%$ | **38.71%** | **PASS** |
| **M8** | Max Prompt Working Memory Ceiling | $\le 512\text{ tokens}$ | **160 tokens** | **PASS** |
| **M9** | Mean Turn Latency | $< 500\text{ ms}$ ($< 1000\text{ ms}$ SLA) | **1078.80 ms** | **NOT MET (+78.8 ms GAP)** |
| **M10** | Zero Loose File Bloat Protocol | $\equiv 100.0\%$ | **100.0%** | **PASS** |

**Overall Track 2 Disposition:** **CONDITIONAL (M9 LATENCY GAP)**. Clauses $M_1$ through $M_8$ and $M_{10}$ are unconditionally satisfied. Clause $M_9$ exhibits a minor 78.8 ms breach (+7.9%) against the 1000 ms SLA on consumer hardware.
