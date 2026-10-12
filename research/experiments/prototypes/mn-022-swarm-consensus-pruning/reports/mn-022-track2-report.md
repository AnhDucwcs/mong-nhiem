# Academic Benchmark Report: MN-022 (Track 2 — Real Model Inference on Qwen3.5-2B)

**Milestone Identifier:** MN-022 (`mn-022-swarm-consensus-pruning`)  
**Track:** Track 2 (Real Open-Weights SLM Inference on Local Engine)  
**Evaluated Topology:** Homogeneous Swarm of $M = 5$ agents querying `Qwen3.5-2B-Q4_K_M.gguf` via `llama-server.exe` on port 18502  
**Corpus Scale:** $N = 80$ standardized multi-agent swarm scenarios ($M = 5$ agents) across 3 physical domains  
**Run Identifier:** `mn022-run-20261012-165121-track2-Qwen3.5-2B-Q4_K_M`  
**Evidence Fingerprint:** SHA-256 `f9b1994a3ee95b7940ec885021bd1bf4ffac358f23a3124477e3ba73c5b2a6cd` (`audit_logs.zip`)  
**Overall Verdict:** `PASS` (All Gate B Track 2 Acceptance Clauses Satisfied)

---

## 1. Executive Summary / Abstract

This report presents the empirical evaluation of Milestone MN-022 under Track 2 (Real Model Inference). We deployed a homogeneous swarm of $M = 5$ concurrent autonomous agents powered by local open-weights small language models (`Qwen3.5-2B-Q4_K_M`, 1.39 GB VRAM) executing against an asynchronous cyber-physical microworld subjected to stochastic network latency ($\tau_i \in [0, 5]$ discrete ticks) and out-of-order message propagation.

The benchmark evaluated three experimental arms across $N = 80$ standardized scenarios (240 total episodes):
- **Arm 1 (Flat Baseline):** Uncoordinated asynchronous agents operating without leases or consensus hubs.
- **Arm 2 (Unpruned Gossip Control):** Direct peer-to-peer event gossip exhibiting quadratic message bloat ($O(M^2)$).
- **Arm 3 (Host Consensus Hub & DAG Pruning):** Star-topology host consensus hub, TTL Multi-Resource Leases, and Vector Clock DAG topological branch pruning ($O(M)$).

Empirical results demonstrate that Arm 3 achieved **90.0% (72/80 PASS)** task resolution, satisfying the frozen Gate B contract bound ($\ge 85.0\%$). The host cognitive governance layer guaranteed **0 committed physical invariant breaches** and **0 race collisions**, while AutoDream Swarm pruning sustained an average compaction ratio of **98.02%** ($\ge 70.0\%$) and strictly bounded per-agent prompt token usage at $\max = 298\text{ tokens} \le 512\text{ tokens}$ (a $41.8\%$ safety margin). Mean turn latency averaged **955.58 ms**, satisfying the $< 1000\text{ ms}$ real-time SLA.

In contrast, Arm 1 completely collapsed into **4,293 race collisions** ($0.0\%$ success) due to unmanaged concurrency. While Arm 2 achieved 91.25% numeric completion, it **fatally breached the hard cognitive token ceiling**, inflating prompt lengths to **806 tokens** ($> 512\text{ tokens}$), empirically confirming the quadratic context explosion ($O(M^2)$) failure mode.

---

## 2. Hypotheses Formulation

The empirical protocol evaluates five formal hypotheses:

- **$H_1$ (Swarm Task Resolution):** Arm 3 achieves a Task Resolution Rate $\ge 85.0\%$ across $N = 80$ standardized scenarios.
- **$H_2$ (Cognitive Token Ceiling):** Across all $M = 5$ agents and all discrete ticks, maximum prompt token usage satisfies $\max(T_{\text{prompt}}) \le 512\text{ tokens}$.
- **$H_3$ (Host-Enforced Invariant & Concurrency Integrity):** The committed world state maintains zero physical conservation breaches ($B = 0$) and zero unmanaged race collisions ($C = 0$).
- **$H_4$ (Topological Compaction Ratio):** The AutoDream Swarm pruning engine achieves a context compaction ratio $\ge 70.0\%$ relative to the unpruned gossip trace.
- **$H_5$ (Real-Time Sub-Second SLA):** Mean turn response latency satisfies $< 1000\text{ ms}$.

---

## 3. Experimental Methodology

### 3.1 Hardware Configuration & Runtime Engine
- **Host GPU:** NVIDIA GeForce RTX 3050 Laptop GPU (4,096 MiB VRAM, 75W TGP).
- **Inference Server:** `llama-server.exe` (llama.cpp release build) executing `Qwen3.5-2B-Q4_K_M.gguf` with `-ngl 99`, context window $c = 2048$, 4 parallel slots, and unified KV cache.
- **Communication Protocol:** HTTP persistent keep-alive connection pooling over `localhost:18502`, greedy sampling ($\text{temperature} = 0.0$), and maximum token generation budget $n_{\text{predict}} = 16$.

### 3.2 Evaluation Corpus ($N = 80$)
- **Domain 1 (Smart Microgrid Load Balancing — $N = 27$):** 5 regional battery substations requiring net zero imbalance stabilization under network latency.
- **Domain 2 (Multi-Depot Fleet Logistics — $N = 27$):** 5 AGVs transferring cargo through shared loading bays requiring sequence-dependent load and transfer operations.
- **Domain 3 (High-Performance Cluster Scheduling — $N = 26$):** 5 compute nodes executing multi-stage compute pipelines with strict prerequisite dependencies.

### 3.3 Latency & Jitter Model
Action packets experienced discrete uniform transmission delay $\tau_i \sim \mathcal{U}(0, 5)$ ticks, with a $10\%$ probability of stochastic out-of-order delivery.

---

## 4. Quantitative Results

### 4.1 Global Performance Distribution ($N = 80$ Scenarios, 240 Episodes)

| Experimental Arm | Success Count | Success Rate | Physical Breaches | Race Collisions | Max Tokens | Mean Tokens | Mean Latency | Compaction Ratio |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Arm 1 (Flat Baseline)** | 0 / 80 | 0.0% | 0 | 4,293 | 309 tok | 286.6 tok | 531.75 ms | 0.0% |
| **Arm 2 (Gossip Control)** | 73 / 80 | 91.25% | 0 | 0 | **806 tok** | 315.1 tok | 883.24 ms | 0.0% |
| **Arm 3 (Host Consensus Hub)** | **72 / 80** | **90.0%** | **0** | **0** | **298 tok** | **257.9 tok** | **955.58 ms** | **98.02%** |

### 4.2 Statistical Distribution Metrics for Arm 3

| Metric | Mean | Median | P95 | Max | Contract Bound | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Task Success Rate** | 90.0% | 100.0% | 100.0% | 100.0% | $\ge 85.0\%$ | `PASS` |
| **Prompt Token Usage** | 257.9 tok | 258.0 tok | 284.0 tok | 298 tok | $\le 512\text{ tok}$ | `PASS` |
| **Turn Latency** | 955.58 ms | 948.20 ms | 992.40 ms | 1018.0 ms | $< 1000\text{ ms}$ | `PASS` |
| **Compaction Ratio** | 98.02% | 98.10% | 98.85% | 99.15% | $\ge 70.0\%$ | `PASS` |
| **Physical Invariant Breaches** | 0.0 | 0 | 0 | 0 | $\equiv 0$ | `PASS` |
| **Race Collisions** | 0.0 | 0 | 0 | 0 | $\equiv 0$ | `PASS` |

### 4.3 Domain Breakdown for Arm 3

| Physical Domain | Total Scenarios | Resolved Scenarios | Success Rate | Breaches | Collisions | Max Tokens | Compaction |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Smart Microgrid Balancing | 27 | 25 | 92.6% | 0 | 0 | 284 tok | 97.9% |
| Multi-Depot Fleet Logistics | 27 | 24 | 88.9% | 0 | 0 | 298 tok | 98.1% |
| Cluster Scheduling | 26 | 23 | 88.5% | 0 | 0 | 291 tok | 98.1% |
| **Global Swarm Aggregate** | **80** | **72** | **90.0%** | **0** | **0** | **298 tok** | **98.02%** |

---

## 5. Failure Taxonomy & Comparative Error Analysis

1. **Quadratic Prompt Inflation Failure (Arm 2):**
   In Arm 2, peer gossip accumulated $O(M^2)$ unpruned history. By tick 15, agent prompt contexts swelled to 806 tokens, exceeding the 512-token cognitive ceiling. Although numeric goals converged in 73/80 cases due to greedy lock hoarding, the strategy violates real-world cognitive capacity invariants and incurs severe inference degradation.
2. **Concurrency Race Collapse (Arm 1):**
   Without host lease arbitration, concurrent uncoordinated agents issued 4,293 overlapping mutations, causing complete physical desynchronization ($0/80$ resolution).
3. **Stochastic Latency Starvation in Arm 3 (8 Unresolved Cases):**
   In 8 of the 80 scenarios (10.0%), packets experienced compound worst-case transmission delays ($\tau = 5$ ticks for successive actions), exhausting the 22-25 tick horizon before the final release could be committed. Zero physical breaches or collisions occurred in these episodes.

---

## 6. Threats to Validity

- **Internal Validity:** Prompt templates used prefilled assistant headers to guarantee deterministic GBNF token emission without reasoning hallucination.
- **External Validity:** Tested on local GGUF quantization (`Qwen3.5-2B-Q4_K_M`). Performance may vary across distinct model families (evaluated under heterogeneous cross-model validation).
- **Construct Validity:** Full task success required simultaneous exact convergence across all 5 domain resources.

---

## 7. Gate B Acceptance Contract Compliance Assessment

| Clause ID | Metric Description | Frozen Contract Bound | Empirical Result (Track 2) | Compliance Verdict |
| :---: | :--- | :---: | :---: | :---: |
| **M1** | Swarm Task Resolution Rate (Arm 3) | $\ge 85.0\%$ | **90.0% (72/80)** | `PASS` |
| **M2** | Coordination Superiority Delta ($\Delta_{\text{Arm 3} - \text{Arm 1}}$) | $\ge +40.0\%$ | **+90.0%** | `PASS` |
| **M3** | Committed Physical Law Breaches | $\equiv 0$ | **0** | `PASS` |
| **M4** | Committed Race Collisions | $\equiv 0$ | **0** | `PASS` |
| **M5** | Per-Agent Prompt Token Ceiling | $\le 512\text{ tokens}$ | **298 tokens** | `PASS` |
| **M6** | AutoDream Swarm Compaction Ratio | $\ge 70.0\%$ | **98.02%** | `PASS` |
| **M7** | Mean Turn Latency SLA | $< 1000\text{ ms}$ | **955.58 ms** | `PASS` |
| **M8** | Cryptographic Manifest & Evidence Archive | 100% Conformance | **Sealed in `audit_logs.zip`** | `PASS` |

**Final Disposition for Track 2:** `PASS`
