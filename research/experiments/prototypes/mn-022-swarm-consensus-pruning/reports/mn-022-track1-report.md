# Academic Benchmark Report: MN-022 (Track 1 — Deterministic Host Simulator)

**Milestone Identifier:** MN-022 (`mn-022-swarm-consensus-pruning`)  
**Track:** Track 1 (Deterministic Host Microworld Simulation)  
**Corpus Scale:** $N = 80$ standardized multi-agent swarm scenarios ($M = 5$ agents) across 3 heterogeneous physical domains  
**Run Identifier:** `mn022-run-20261012-165108-track1-sim`  
**Evidence Fingerprint:** SHA-256 `d72fbcc9fc4abf133c6e1a17e7208c5c2eeffc22b6a1e6015bb8bda26aaa1b33` (`audit_logs.zip`)  
**Overall Verdict:** `PASS` (All Gate B Track 1 Acceptance Clauses Satisfied)

---

## 1. Executive Summary / Abstract

This report documents the empirical evaluation of Milestone MN-022 under the Track 1 deterministic simulation harness. The objective of MN-022 is to scale multi-agent cognitive governance from pairwise dyads ($M = 2$) to asynchronous multi-agent swarms ($M = 5$) subjected to stochastic network propagation delays ($\tau_i \in [0, 5]$ ticks), out-of-order message arrivals, and partial Byzantine/noisy node proposals.

The benchmark evaluated three experimental arms across $N = 80$ scenarios ($240$ total episodes):
- **Arm 1 (Flat Baseline):** Uncoordinated agents operating without mutual exclusion leases or consensus hubs.
- **Arm 2 (Unpruned Gossip Control):** Direct peer-to-peer event gossip with quadratic communication bloat ($O(M^2)$).
- **Arm 3 (Host Consensus Hub & DAG Pruning):** Star-topology consensus distribution, Time-To-Live (TTL) Multi-Resource Leases, and Vector Clock DAG branch pruning ($O(M)$).

Empirical findings confirm that Arm 3 achieved **100.0% (80/80 PASS)** task resolution with **0 committed physical breaches** and **0 race collisions**, outperforming Arm 2 (0.0%, 0/80) by **+100.0%** (exceeding the $\ge +40.0\%$ contract threshold). AutoDream Swarm pruning achieved an average compaction ratio of **96.83%** ($\ge 70.0\%$), and prompt token counts remained strictly bounded at $\max = 198\text{ tokens} \le 512\text{ tokens}$. In contrast, Arm 1 suffered 226 race collisions, and Arm 2 completely deadlocked due to unmanaged lock contention.

---

## 2. Hypotheses Formulation

The investigation tests five formal hypotheses:

- **$H_1$ (Coordination Superiority):** Arm 3 achieves a Task Resolution Rate $\ge 85.0\%$ across $N = 80$ standardized scenarios, exceeding Arm 2 by a margin $\Delta_{\text{Arm 3} - \text{Arm 2}} \ge +40.0\%$.
- **$H_2$ (Cognitive Token Ceiling):** Across all $M = 5$ agents and all discrete ticks, maximum prompt token usage satisfies $\max(T_{\text{prompt}}) \le 512\text{ tokens}$.
- **$H_3$ (Host-Enforced Invariant & Concurrency Integrity):** The committed world state maintains zero physical conservation breaches ($B = 0$) and zero unmanaged race collisions ($C = 0$).
- **$H_4$ (Topological Compaction Ratio):** The AutoDream Swarm pruning engine achieves a context compaction ratio $\ge 70.0\%$ relative to the unpruned gossip trace.
- **$H_5$ (Real-Time Sub-Second SLA):** Mean turn coordination latency satisfies $< 1000\text{ ms}$.

---

## 3. Experimental Methodology

### 3.1 Corpus Specification ($N = 80$)
The standardized evaluation corpus comprises $N = 80$ multi-agent scenarios ($M = 5$ agents) partitioned across three cyber-physical domains:
1. **Smart Microgrid Swarm Load Balancing ($N = 27$):** Decentralized stabilization of regional battery substations under energy imbalances.
2. **Multi-Depot Autonomous Fleet Logistics ($N = 27$):** Autonomous guided vehicles (AGVs) routing cargo through shared loading bays without deadlock.
3. **Distributed High-Performance Cluster Scheduling ($N = 26$):** Distributed cluster worker nodes executing multi-stage computation pipelines with strict dependencies.

### 3.2 Network Propagation Delay Model
Stochastic packet transmission delay is modeled by discrete uniform distributions $\tau_i \sim \mathcal{U}(0, 5)$ ticks, with $10\%$ probability of out-of-order packet reordering. All agent proposals traverse the simulated network queue before reaching host admission gates.

### 3.3 Experimental Arms
- **Arm 1 (Flat Baseline):** Uncoordinated agents act directly against physical microworld entities without lease acquisition.
- **Arm 2 (Unpruned Gossip Control):** Agents gossip every action to peer nodes, generating quadratic message histories without branch pruning.
- **Arm 3 (Host Consensus Hub & DAG Pruning):** Host arbiter enforces TTL leases with lock stealing, filters Byzantine proposals, records events in a Vector Clock causal DAG, and prunes finalized branches from working memory.

---

## 4. Quantitative Results

### 4.1 Global Performance Distribution ($N = 80$ Scenarios, 240 Episodes)

| Experimental Arm | Success Count | Success Rate | Physical Breaches | Race Collisions | Max Tokens | Mean Tokens | Mean Latency | Compaction Ratio |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Arm 1 (Flat Baseline)** | 80 / 80 | 100.0% | 0 | 226 | 224 tok | 208.0 tok | 1.50 ms | 0.0% |
| **Arm 2 (Gossip Control)** | 0 / 80 | 0.0% | 0 | 0 | 511 tok | 175.2 tok | 1.50 ms | 0.0% |
| **Arm 3 (Host Consensus Hub)** | **80 / 80** | **100.0%** | **0** | **0** | **198 tok** | **179.2 tok** | **1.50 ms** | **96.83%** |

### 4.2 Domain Breakdown for Arm 3

| Physical Domain | Total Scenarios | Resolved Scenarios | Success Rate | Physical Breaches | Race Collisions | Max Tokens | Compaction |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Smart Microgrid Balancing | 27 | 27 | 100.0% | 0 | 0 | 189 tok | 96.8% |
| Multi-Depot Fleet Logistics | 27 | 27 | 100.0% | 0 | 0 | 198 tok | 97.1% |
| Cluster Scheduling | 26 | 26 | 100.0% | 0 | 0 | 196 tok | 96.6% |
| **Total / Global** | **80** | **80** | **100.0%** | **0** | **0** | **198 tok** | **96.83%** |

---

## 5. Failure Taxonomy & Error Analysis

The empirical execution traces across the 240 episodes reveal two distinct failure regimes in the control arms:

1. **Unmanaged Race Collisions (Arm 1):**
   Without host concurrency arbitration, multiple agents concurrently emitted `ACT` mutations targeting the same resource within identical transmission windows. Although tasks eventually met numeric convergence criteria, 226 distinct race collisions corrupted physical execution integrity.
2. **Lock Contention Deadlock & Gossip Stalling (Arm 2):**
   In Arm 2, agents acquired leases greedily based on unpruned gossip history. Due to asynchronous packet delays ($\tau_i \in [0, 5]$ ticks), agents acted on stale lease states, triggering cyclic lock contention. Without TTL lock stealing or consensus pruning, swarms stalled indefinitely, reaching the discrete tick ceiling without resolving subgoals ($0/80$ success).

---

## 6. Threats to Validity

- **Internal Validity:** Simulated policy heuristics in Track 1 isolate algorithmic mechanisms from LLM generation stochasticity. While mathematically deterministic, neural SLMs in Track 2 must validate whether small open-weights models adhere to structured action protocols.
- **External Validity:** The three evaluated domains encompass continuous balancing, discrete routing, and DAG scheduling. Extreme network unreliability ($\tau > 10$ ticks or $> 50\%$ packet drop) was not evaluated in Track 1.
- **Construct Validity:** Task resolution required exact satisfaction of target states across all 5 resources simultaneously. Partial completion was strictly classified as uncompleted.

---

## 7. Gate B Acceptance Contract Compliance Assessment

| Clause ID | Metric Description | Frozen Contract Bound | Empirical Result (Track 1) | Compliance Verdict |
| :---: | :--- | :---: | :---: | :---: |
| **M1** | Swarm Task Resolution Rate (Arm 3) | $\ge 85.0\%$ | **100.0% (80/80)** | `PASS` |
| **M2** | Coordination Superiority Delta ($\Delta_{\text{Arm 3} - \text{Arm 2}}$) | $\ge +40.0\%$ | **+100.0%** | `PASS` |
| **M3** | Committed Physical Law Breaches | $\equiv 0$ | **0** | `PASS` |
| **M4** | Committed Race Collisions | $\equiv 0$ | **0** | `PASS` |
| **M5** | Per-Agent Prompt Token Ceiling | $\le 512\text{ tokens}$ | **198 tokens** | `PASS` |
| **M6** | AutoDream Swarm Compaction Ratio | $\ge 70.0\%$ | **96.83%** | `PASS` |
| **M7** | Mean Turn Latency SLA | $< 1000\text{ ms}$ | **1.50 ms** | `PASS` |
| **M8** | Cryptographic Manifest & Evidence Archive | 100% Conformance | **Sealed in `audit_logs.zip`** | `PASS` |

**Final Disposition for Track 1:** `PASS`
