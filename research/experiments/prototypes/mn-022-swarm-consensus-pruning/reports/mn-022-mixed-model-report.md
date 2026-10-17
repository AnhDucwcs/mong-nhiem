# Academic Benchmark Report: MN-022 (Heterogeneous Swarm Benchmark)

**Milestone Identifier:** MN-022 (`mn-022-swarm-consensus-pruning`)  
**Track:** Heterogeneous Stress Track (Mixed Small Language Model Swarm)  
**Evaluated Topology:** Heterogeneous Swarm of $M = 5$ agents:  
  - Agent 1: `Qwen3.5-2B-Q4_K_M` (Port 18502)  
  - Agent 2: `Llama-3.2-3B-Instruct-Q4_K_M` (Port 18503)  
  - Agent 3: `Qwen3.5-2B-Q4_K_M` (Port 18502)  
  - Agent 4: `Llama-3.2-3B-Instruct-Q4_K_M` (Port 18503)  
  - Agent 5: `Qwen3.5-2B-Q4_K_M` (Port 18502)  
**Corpus Scale:** $N = 80$ standardized multi-agent swarm scenarios across 3 physical domains  
**Run Identifier:** `mn022-mixed-run-20261012-181151-heterogeneous-swarm`  
**Overall Verdict:** `PASS` (All Heterogeneous Stress Bounds Satisfied)

---

## 1. Executive Summary / Abstract

This report evaluates the cross-architecture robustness of the MN-022 Host Consensus Hub and AutoDream DAG pruning engine under an asynchronous heterogeneous multi-agent swarm ($M = 5$). In contrast to the homogeneous benchmark (Track 2), the swarm was partitioned across distinct model families: three agents deployed on `Qwen3.5-2B-Q4_K_M` (Alibaba Cloud) and two agents deployed on `Llama-3.2-3B-Instruct-Q4_K_M` (Meta AI), executed concurrently across two dedicated local inference engines within a single unified 4.0 GB GPU VRAM envelope.

Across $N = 80$ test scenarios subjected to stochastic latency $\tau_i \in [0, 5]$ discrete ticks and 10% out-of-order jitter, the heterogeneous swarm achieved a task resolution rate of **97.5% (78/80 PASS)**. The Host Consensus Hub maintained absolute physical invariant integrity (**0 physical breaches**) and concurrency safety (**0 race collisions**). AutoDream Swarm pruning sustained an average compaction ratio of **97.92%**, constraining peak prompt lengths to **297 tokens** (well below the frozen 512-token ceiling). Due to concurrent execution of two distinct model architectures on a single 4 GB GPU, mean turn latency averaged **2445.43 ms**.

---

## 2. Experimental Methodology & Architecture

### 2.1 Dual-Model VRAM Packing & Execution Topology
- **Physical Hardware:** NVIDIA GeForce RTX 3050 Laptop GPU (4,096 MiB VRAM).
- **Daemon 1:** `llama-server.exe` on Port 18502 serving `Qwen3.5-2B-Q4_K_M.gguf` (1,390 MiB VRAM allocated).
- **Daemon 2:** `llama-server.exe` on Port 18503 serving `Llama-3.2-3B-Instruct-Q4_K_M.gguf` (2,020 MiB VRAM allocated).
- **Total VRAM Utilization:** 3,806 MiB / 4,096 MiB (92.9% VRAM density with zero out-of-memory faults).
- **Role Allocation:** Agents 1, 3, and 5 query Qwen 2B; Agents 2 and 4 query Llama 3.2 3B. Both model families emit standardized action proposals parsed and validated by the host arbiter.

---

## 3. Quantitative Results

### 3.1 Heterogeneous Swarm Distribution Metrics ($N = 80$)

| Metric | Mean | Median | P95 | Max | Contract Bound | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Task Success Rate** | 97.5% | 100.0% | 100.0% | 100.0% | $\ge 85.0\%$ | `PASS` |
| **Prompt Token Usage** | 254.4 tok | 257.4 tok | 268.2 tok | 297 tok | $\le 512\text{ tok}$ | `PASS` |
| **Turn Latency** | 2445.43 ms | 2334.92 ms | 3372.03 ms | 4588.05 ms | Context Envelope | `PASS` |
| **Compaction Ratio** | 97.92% | 98.0% | 98.77% | 98.9% | $\ge 70.0\%$ | `PASS` |
| **Physical Invariant Breaches** | 0 | 0 | 0 | 0 | $\equiv 0$ | `PASS` |
| **Race Collisions** | 0 | 0 | 0 | 0 | $\equiv 0$ | `PASS` |

### 3.2 Domain-Specific Resolution Breakdown

| Physical Domain | Total Scenarios | Resolved Scenarios | Success Rate | Breaches | Collisions | Max Tokens | Compaction |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Cluster Scheduling | 26 | 25 | 96.2% | 0 | 0 | 283 tok | 98.3% |
| Fleet Logistics | 27 | 27 | 100.0% | 0 | 0 | 269 tok | 97.4% |
| Smart Microgrid | 27 | 26 | 96.3% | 0 | 0 | 297 tok | 98.1% |
| **Heterogeneous Swarm Total** | **80** | **78** | **97.5%** | **0** | **0** | **297 tok** | **97.92%** |

---

## 4. Cross-Topology Comparative Analysis (Homogeneous vs. Heterogeneous)

| Comparative Dimension | Track 2 Homogeneous ($5 \times$ Qwen 2B) | Heterogeneous ($3 \times$ Qwen 2B + $2 \times$ Llama 3.2 3B) | Delta / Assessment |
| :--- | :---: | :---: | :--- |
| **Swarm Task Resolution** | 90.0% (72/80) | 97.5% (78/80) | Consistent coordination across diverse architectures |
| **Physical Invariant Breaches** | 0 | 0 | Exact mathematical invariant preservation ($\equiv 0$) |
| **Race Collisions** | 0 | 0 | Zero concurrency lease violations ($\equiv 0$) |
| **Max Context Size** | 298 tokens | 297 tokens | Hard ceiling strictly preserved ($\le 512$ tokens) |
| **Compaction Ratio** | 98.02% | 97.92% | Topological DAG pruning invariant holds across architectures |
| **Mean Turn Latency** | 955.58 ms | 2445.43 ms | Latency increased due to dual-model GPU timesharing on 4 GB VRAM |

---

## 5. Compliance Assessment against Gate B Acceptance Contract

| Clause ID | Acceptance Contract Requirement | Measured Empirical Value | Clause Disposition |
| :---: | :--- | :---: | :---: |
| **M1** | Task Resolution Rate $\ge 85.0\%$ | **97.5%** | `PASS` |
| **M3** | Committed Physical Law Breaches $\equiv 0$ | **0** | `PASS` |
| **M4** | Committed Race Collisions $\equiv 0$ | **0** | `PASS` |
| **M5** | Per-Agent Prompt Token Ceiling $\le 512\text{ tokens}$ | **297 tokens** | `PASS` |
| **M6** | AutoDream Swarm Compaction Ratio $\ge 70.0\%$ | **97.92%** | `PASS` |
| **M8** | Cryptographic Manifest & Evidence Archival | **100% Conformance** | `PASS` |

---

## 6. Scientific Findings & Conclusion

1. **Architecture-Agnostic Coordination:** The Host Consensus Hub and Multi-Resource TTL Lease protocol operate independently of internal SLM weight distributions. Both Qwen and Llama architectures successfully interacted through standardized action and lease primitives without synchronization deadlock.
2. **Resilience to Reasoning Disparity:** Even with varying reasoning profiles between Qwen-2B and Llama-3.2-3B, the Vector Clock causal DAG prevented state drift and out-of-order action desynchronization.
3. **Token Ceiling Invariance:** AutoDream Fact Cards maintained a sub-300 token envelope across all models, proving that topological pruning scales consistently across heterogeneous swarms.
