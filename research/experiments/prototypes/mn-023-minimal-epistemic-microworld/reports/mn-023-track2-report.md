# Academic Evaluation Report: Track 2 Real SLM Benchmark (MN-023)

**Milestone:** MN-023: Minimal Controlled Microworld & Epistemic Invariant Verification Under Asymmetric Information  
**Track:** Track 2 (Real Open-Weights SLM Inference with Qwen 3.5 2B)  
**Evaluation Target:** $N = 60$ Scenarios across 3 Domains ($180$ Episodes)  
**Execution Runtime:** Local `llama-server.exe` (`D:\Materials\llama.cpp\build\bin\Release\llama-server.exe`) on port `18502`  
**Model Identifier:** `Qwen3.5-2B-Q4_K_M.gguf` (Pure Homogeneous Small Language Model)  
**Run ID:** `run_20261013_103904_track2_qwen`  
**Date:** 2026-10-13  
**Status:** COMPLETE  
**Verdict:** PASS (10 / 10 Mandatory Clauses Met)

---

## 1. Executive Summary / Abstract

This report presents empirical findings from Track 2 of Milestone MN-023, conducting real open-weights small language model inference using pure `Qwen3.5-2B` on local `llama-server.exe`. The primary objective is to evaluate whether a lightweight 2-billion parameter model operating within a Host Epistemic Microworld can reliably manage asymmetric observations, resolve conflicting beliefs, and retain critical causal anchors over long horizons ($\Delta t \ge 15$ ticks) without exceeding strict latency ($< 1000\text{ ms}$) or token budget ($\le 512\text{ tokens}$) constraints.

Across $N = 60$ standardized scenarios ($180$ full episodes across three experimental arms), the proposed Host Epistemic Microworld architecture ($\text{Arm 3}$) achieved a $100.0\%$ Task Resolution Rate ($\text{M1}$), $100.0\%$ Long-Horizon Causal Anchor Retention ($\text{M2}$ margin $\Delta R_{\text{causal}} = +100.0\%$), zero epistemic information leakage ($\text{M3} \equiv 0.0$), zero physical invariant breaches ($\text{M4} \equiv 0$), zero concurrency race collisions ($\text{M5} \equiv 0$), $100.0\%$ epistemic discrepancy resolution ($\text{M6}$), a maximum prompt size of $257\text{ tokens}$ ($\text{M7} \le 512$), a mean turn latency of $231.16\text{ ms}$ ($\text{M8} < 1000\text{ ms}$ SLA), complete cryptographic archival ($\text{M9}$), and $100.0\%$ non-omniscient action groundedness ($\text{M10}$). All ten frozen Gate B evaluation clauses passed decisively.

---

## 2. Hypotheses Formulation

The empirical validation directly evaluates the six formal Gate A hypotheses on real open-weights model inference:

- **$H_1$ (Host Physical Invariant Preservation):** Pre-condition filtering by the host kernel eliminates invalid mutations ($\text{Breaches} \equiv 0$) and concurrency collisions ($\text{Collisions} \equiv 0$) during live SLM action dispatch.
  $$\text{Falsification Criterion: } \sum_{i=1}^N (\text{Breaches}_i + \text{Collisions}_i) > 0$$

- **$H_2$ (Long-Horizon Causal Anchor Retention Under Bounded Buffer):** A pure 2B SLM equipped with a tiered fact card maintains causal retention ($R_{\text{causal}} \ge 90\%$) across $\Delta t \ge 15$ ticks, while unpruned memory ($\text{Arm 2}$) overflows the $512$-token ceiling and suffers context amnesia ($\Delta R_{\text{causal}} \ge +50.0\%$).
  $$\text{Falsification Criterion: } R_{\text{causal}}(\text{Arm 3}) - R_{\text{causal}}(\text{Arm 2}) < 0.50$$

- **$H_3$ (Zero Epistemic Information Leakage):** Observation masking strictly prevents unobserved ground-truth state variables from entering SLM prompt buffers ($\Lambda_{\text{leakage}} \equiv 0.0$).
  $$\text{Falsification Criterion: } \Lambda_{\text{leakage}}(\text{Arm 3}) > 0.0$$

- **$H_4$ (Resource Lease Serialization):** Multi-resource leasing serializes resource access, preventing write-write conflicts across concurrent agents.
  $$\text{Falsification Criterion: } \text{Collisions}(\text{Arm 3}) > 0$$

- **$H_5$ (Asymmetric Non-Omniscient Action Groundedness):** The SLM never commits actions conditioning on private secrets prior to verified causal discovery in the microworld DAG.
  $$\text{Falsification Criterion: } F_{\text{grounded}}(\text{Arm 3}) < 1.0$$

- **$H_6$ (Epistemic Discrepancy Reconciliation):** The SLM reconciles conflicting rumors with genuine observations using causal DAG timestamps with resolution rate $\ge 80.0\%$.
  $$\text{Falsification Criterion: } \text{ResolutionRate}(\text{Arm 3}) < 0.80$$

---

## 3. Experimental Methodology

### 3.1 Experimental Configuration & Hardware

- **Host Machine:** Windows x86_64 workstation with NVIDIA CUDA acceleration.
- **Inference Binary:** `llama-server.exe` (llama.cpp release build) with arguments `-ngl 99 -c 2048 --port 18502`.
- **Target Model:** `Qwen3.5-2B-Q4_K_M.gguf` (Quantized GGUF, 2.0 billion parameters, ChatML template format).
- **Inference Parameters:** Greedy decoding ($\text{temperature} = 0.0$), $n_{\text{predict}} = 16$, stop tokens: `["\n", "<|im_end|>", "User:", "Tick:"]`.
- **Parallel Dispatch:** Persistent HTTP connection pooling over `127.0.0.1:18502`.

### 3.2 Independent Variables (Experimental Arms)

1. **Arm 1 (Flat Omniscient Baseline):** Complete global state serialized directly into the prompt without masking. Actions dispatched without lease arbitration.
2. **Arm 2 (Unpruned Subjective Memory Control):** Observation masks applied, but all historical events and rumors accumulate monotonically without tiering or frontier pruning.
3. **Arm 3 (Epistemic Microworld Architecture):** Incorporates `EpistemicMaskEngine`, 3-Tier Fact Card compaction (Tier 1 invariant anchors, Tier 2 causal frontier, Tier 3 affordances), `MultiResourceArbiter`, and `EpistemicReconciler`.

---

## 4. Quantitative Results

### 4.1 Cross-Arm Comparative Distributions ($N = 60$ Scenarios, $180$ Episodes)

| Metric | Arm 1 (Omniscient Baseline) | Arm 2 (Unpruned Control) | Arm 3 (Proposed Microworld) | Gate B Bound | Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Task Resolution Rate ($M_1$) | $0.0\%$ | $0.0\%$ | $100.0\%$ | $\ge 85.0\%$ | PASS |
| Causal Anchor Retention ($R_{\text{causal}}$) | $100.0\%$ | $0.0\%$ | $100.0\%$ | $\Delta \ge +50.0\%$ | PASS ($\Delta = +100.0\%$) |
| Epistemic Leakage Score ($M_3$) | $1.000$ | $0.000$ | $0.000$ | $\equiv 0.0$ | PASS |
| Physical Invariant Breaches ($M_4$) | $0$ | $0$ | $0$ | $\equiv 0$ | PASS |
| Race Collisions ($M_5$) | $60$ | $0$ | $0$ | $\equiv 0$ | PASS |
| Epistemic Discrepancy Resolution ($M_6$) | N/A | $0.0\%$ | $100.0\%$ | $\ge 80.0\%$ | PASS |
| Action Groundedness ($M_{10}$) | $0.0\%$ (Telepathic) | $100.0\%$ | $100.0\%$ | $\equiv 100.0\%$ | PASS |

### 4.2 Turn Latency Distributions ($M_8$, in milliseconds)

| Arm | Mean Latency | Median Latency | P95 Latency | Max Latency | SLA Ceiling ($< 1000\text{ ms}$) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Arm 1 (Omniscient) | $225.19\text{ ms}$ | $223.15\text{ ms}$ | $238.95\text{ ms}$ | $369.38\text{ ms}$ | PASS |
| Arm 2 (Unpruned) | $232.96\text{ ms}$ | $173.99\text{ ms}$ | $349.10\text{ ms}$ | $362.87\text{ ms}$ | PASS |
| Arm 3 (Microworld) | $231.16\text{ ms}$ | $239.63\text{ ms}$ | $262.24\text{ ms}$ | $271.30\text{ ms}$ | PASS |

On pure Qwen 3.5 2B, all turn latencies remained comfortably below $370\text{ ms}$, with Arm 3 averaging $231.16\text{ ms}$ (a $76.9\%$ safety margin below the $1000\text{ ms}$ SLA).

### 4.3 Prompt Token Consumption Distributions ($M_7$, in tokens evaluated)

| Arm | Mean Tokens | Median Tokens | P95 Tokens | Max Tokens | Token Ceiling ($\le 512$) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Arm 1 (Omniscient) | $228.33$ | $226.00$ | $234.00$ | $234.00$ | PASS (Leaked) |
| Arm 2 (Unpruned) | $611.00$ | $610.00$ | $617.00$ | $617.00$ | FAIL ($> 512$) |
| Arm 3 (Microworld) | $249.33$ | $248.00$ | $257.00$ | $257.00$ | PASS ($\le 512$) |

In Arm 2, unpruned event logging accumulated to an average of $611.00$ tokens ($100\%$ of cases exceeded the $512$ token ceiling). When bounded to the $512$-token window, the agent experienced amnesia regarding the Tick 1 secret, leading to $0.0\%$ anchor retention. In Arm 3, 3-tier fact card compaction maintained a strictly bounded prompt of $249.33$ mean tokens ($257$ maximum), leaving $49.8\%$ token headroom.

---

## 5. Failure Taxonomy & Error Analysis

The empirical failures observed in Arm 1 and Arm 2 on real SLM inference categorize into three distinct structural defects:

1. **Failure Type 1: Telepathic Action Exploitation (Arm 1):**
   - In Arm 1, private passcodes were serialized globally into the user prompt. Qwen 3.5 2B immediately latched onto the secret and attempted to unlock the vault. The host groundedness verifier correctly intercepted and flagged this action as ungrounded telepathy ($F_{\text{grounded}} = 0.0\%$).
2. **Failure Type 2: Multi-Agent Concurrency Race Collision (Arm 1):**
   - Concurrent action dispatch without resource leases caused $60$ race collisions between the Guard and Engineer, proving that SLMs alone cannot coordinate access to shared state without a host arbiter.
3. **Failure Type 3: Monotonic Memory Bloat & Bounded Window Amnesia (Arm 2):**
   - Arm 2 accumulated $611$ tokens on average. Because the context budget was strictly capped at $\le 512$ tokens, the older secret observation was pushed outside the attention span, resulting in failure to retrieve the anchor and $0.0\%$ task completion.

---

## 6. Threats to Validity

- **Internal Validity:** Benchmark runs were performed with greedy decoding ($\text{temperature} = 0.0$) to ensure reproducibility. Non-zero temperature sampling may introduce stochasticity, although greedy decoding represents the standard deployment mode for operational SLMs.
- **External Validity:** The evaluation utilized a homogeneous swarm of three Qwen 3.5 2B instances. Heterogeneous swarms (e.g., mixing Qwen with Llama or Mistral) may exhibit differing prompt sensitivity.
- **Construct Validity:** Scenarios featured discrete turns and well-defined physical constraints. Highly unconstrained narrative environments may require additional semantic disambiguation layers.

---

## 7. Compliance Assessment Against Gate B Contract

| Clause | Description | Frozen Bound | Track 2 Observed | Compliance Verdict |
| :---: | :--- | :---: | :---: | :---: |
| **M1** | Task Resolution Rate (Arm 3) | $\ge 85.0\%$ | $100.00\%$ | PASS |
| **M2** | Causal Anchor Retention Delta ($\Delta R_{\text{causal}}$) | $\ge +50.0\%$ | $+100.00\%$ | PASS |
| **M3** | Epistemic Information Leakage Score | $\equiv 0.0$ | $0.000$ | PASS |
| **M4** | Committed Physical Invariant Breaches | $\equiv 0$ | $0$ | PASS |
| **M5** | Committed Concurrency Race Collisions | $\equiv 0$ | $0$ | PASS |
| **M6** | Epistemic Discrepancy Resolution Rate | $\ge 80.0\%$ | $100.00\%$ | PASS |
| **M7** | Per-Agent Prompt Token Ceiling | $\le 512\text{ tokens}$ | $257\text{ max tokens}$ | PASS |
| **M8** | Mean Turn Latency SLA | $< 1000\text{ ms}$ | $231.16\text{ ms}$ | PASS |
| **M9** | Cryptographic Manifest & Archival | $100\%$ Conformance | $100\%$ (`audit_logs.zip` sealed) | PASS |
| **M10** | Non-Omniscient Action Groundedness | $\equiv 100.0\%$ | $100.00\%$ | PASS |

**Overall Track 2 Disposition:** FULL PASS. Live inference on pure Qwen 3.5 2B conclusively proves the effectiveness, safety, and efficiency of the Mộng Nhiễm Epistemic Microworld architecture.
