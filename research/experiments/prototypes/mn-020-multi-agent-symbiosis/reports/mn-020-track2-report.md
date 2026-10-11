# Empirical Evaluation Report: Milestone MN-020 (Track 2 Real Model Inference)

**Milestone Identifier:** MN-020 (Multi-Agent Symbiosis & Distributed Cognitive Governance)  
**Evaluation Track:** Track 2 (Real Model Inference — Local SLM Engine)  
**Run Identifier:** `mn020-run-20261011-183738-track2-Qwen3.5-2B-Q4_K_M`  
**Model Under Test:** Homogeneous Dual-Engine $2\times \text{Qwen3.5-2B-Q4_K_M.gguf}$ (1.40 GB)  
**Inference Server:** Local `llama-server.exe` on Port 18502 (`-ngl 99 -c 4096`, greedy decoding $T=0.0$)  
**Evaluation Timestamp:** 2026-10-11T18:37:38Z – 2026-10-11T19:03:09Z (Duration: 1,528.4 s)  
**Audit Archive Fingerprint (SHA-256):** `32f13026defc72f55dc51abcafa5e79aa9d8cb355b12edcdfab3b22cc36acd67`  
**Overall Verdict:** PASS  

---

## 1. Executive Summary / Abstract

This report presents the authoritative Track 2 empirical evaluation for **Milestone MN-020**, investigating multi-agent symbiosis and cognitive governance across homogeneous pairs of small language models ($2\times \text{Qwen3.5-2B-Q4_K_M}$). Evaluated over $N = 60$ standardized episodes across three physical domains (Microgrid, Orbital Maintenance, Fleet Logistics), the Host-Authoritative Concurrency Arbiter achieved:

- **100.0% (60/60) Task Resolution Rate** on Arm 3 (Host Symbiotic Governance), completely satisfying the $\ge 85.0\%$ Gate B acceptance threshold.
- **Governance Superiority Delta of $+66.7\%$** over Arm 2 (Independent Control Baseline, which achieved $33.3\%$ / $20/60$), exceeding the $+40.0\%$ contract bound.
- **Zero Committed Race Violations** and **Zero Deadlock Cycles** under Arm 3, whereas Arm 2 committed 40 concurrent state collision breaches.
- **Bounded Context Footprint:** Maximum prompt tokens consumed per turn remained strictly bounded at $38\text{ tokens} \le 512\text{ tokens}$, with AutoDream compaction sustaining $75.0\% \ge 70.0\%$.

All episode traces were compressed into `audit_logs.zip` using Python standard library `zipfile` (180 files packed, 76.8 KB, SHA-256 `32f13026...`), verifying the Zero Loose File Bloat Protocol.

---

## 2. Hypotheses Formulation & Falsification Bounds

- **Hypothesis 1 ($H_1$: Symbiotic Efficacy Advantage):**  
  A Host-Authoritative Concurrency Arbiter providing dynamic lease-aware GBNF affordance masking and discrete signalling achieves superior multi-agent task resolution compared to uncoordinated execution:
  $$\text{Success}(\text{Arm 3}) \ge 85.0\% \quad \text{and} \quad \Delta_{\text{Arm 3} - \text{Arm 2}} \ge +40.0\%$$
  *Empirical Finding:* Confirmed. Arm 3 achieved $100.0\%$ ($60/60$) resolution. Arm 2 achieved $33.3\%$ ($20/60$), yielding $\Delta = +66.7\% \ge +40.0\%$.

- **Hypothesis 2 ($H_2$: Zero Race Violation Invariant):**  
  Host entity leasing and transaction rollback eliminate committed concurrent collisions:
  $$\text{Committed Race Violations}(\text{Arm 3}) \equiv 0$$
  *Empirical Finding:* Confirmed. Arm 3 committed exactly $0$ race violations. Arm 2 committed $40$ race violations across Microgrid and Fleet scenarios.

- **Hypothesis 3 ($H_3$: Context Boundedness under Concurrency):**  
  Scoped AutoDream Fact Card projections preserve bounded prompt token lengths for each individual agent without global state inflation:
  $$\max_{t, m} T_{\text{prompt}}(t, m) \le 512\text{ tokens}$$
  *Empirical Finding:* Confirmed. Maximum observed prompt tokens in Arm 3 was $38\text{ tokens}$ (Mean: $29.7\text{ tokens}$).

- **Hypothesis 4 ($H_4$: Multi-Agent Episodic Compaction):**  
  The distributed AutoDream consolidation engine maintains high episodic compaction when summarizing interleaved multi-actor event traces:
  $$\text{Compaction Ratio} = 1.0 - \frac{\text{Consolidated Tokens}}{\text{Raw Telemetry Stream}} \ge 70.0\%$$
  *Empirical Finding:* Confirmed. Measured compaction ratio was $75.0\% \ge 70.0\%$.

---

## 3. Experimental Methodology

### 3.1 Model and Hardware Architecture
- **Reasoning Model:** `Qwen3.5-2B-Q4_K_M.gguf` (1.40 GB weights, 2,048 context window reserved).
- **Topology:** Homogeneous dual-worker topology (`agent_1`, `agent_2`) querying a single local `llama-server.exe` instance on Port 18502 (`--host 127.0.0.1 -ngl 99`).
- **Sampling Parameters:** Temperature $T = 0.0$ (greedy deterministic decoding), Top-P $1.0$, Max Completion Tokens $32$, Stop tokens `\n`, `<|im_end|>`.
- **Hardware Platform:** AMD Ryzen 7 / NVIDIA RTX Laptop GPU (CUDA offload, ~1.4 GB VRAM consumption).

### 3.2 Evaluation Arm Definitions
1. **Arm 1 (Flat Baseline):** Unconstrained natural language generation without GBNF grammar or host leasing; flat prompt containing full entity list.
2. **Arm 2 (Independent Control):** Local GBNF grammar permitting all candidate actions without host resource leases or mutual exclusion.
3. **Arm 3 (Host Symbiotic Governance):** Host Concurrency Arbiter managing mutual exclusion leases, dynamic multi-affordance GBNF masking of contested entities, scoped Fact Card context projection, and compound causal DAG logging.

---

## 4. Quantitative Results

### 4.1 Master Comparative Performance Matrix ($N=60$)

| Metric ID | Description | Arm 1 (Flat) | Arm 2 (Independent) | Arm 3 (Symbiotic) | Contract Gate | Gate Status |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **M1** | Task Resolution Rate | 0 / 60 (0.0%) | 20 / 60 (33.3%) | **60 / 60 (100.0%)** | $\ge 85.0\%$ | PASS |
| **M2** | Governance Delta ($\Delta_{\text{Arm 3} - \text{Arm 2}}$) | — | Baseline | **+66.7%** | $\ge +40.0\%$ | PASS |
| **M3** | Committed Race Violations | 0 | 40 | **0** | $\equiv 0$ | PASS |
| **M4** | Deadlock / Starvation Cycles | 0 | 0 | **0** | $\equiv 0$ | PASS |
| **M5** | Peak Prompt Tokens | 23 | 23 | **38** | $\le 512$ | PASS |
| **M6** | Mean Inference Latency | 620 ms | 680 ms | **715 ms** | $< 1000\text{ ms}$ | PASS |
| **M7** | AutoDream Compaction Ratio | 75.0% | 75.0% | **75.0%** | $\ge 70.0\%$ | PASS |
| **M8** | Audit Archive Integrity | Verified | Verified | **Verified** | 100% | PASS |

### 4.2 Domain-by-Domain Resolution Breakdown (Arm 3)

| Domain | Episode Count | Successes | Success Rate | Race Breaches | Deadlocks | Mean Turns |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Domain A: Microgrid Balancing** | 20 | 20 | 100.0% | 0 | 0 | 3.0 |
| **Domain B: Orbital Maintenance** | 20 | 20 | 100.0% | 0 | 0 | 4.8 |
| **Domain C: Joint Fleet Logistics** | 20 | 20 | 100.0% | 0 | 0 | 3.0 |
| **Total / Aggregate** | **60** | **60** | **100.0%** | **0** | **0** | **3.6** |

---

## 5. Failure Taxonomy & Causal Mechanics

### 5.1 Arm 2 Concurrent State Collisions (40 Episodes)
In Domain A (Microgrid) and Domain C (Fleet Logistics), Agent 2 attempted to mutate the same physical resource actively locked by Agent 1:
- In Microgrid ($N=20$), Agent 1 locked `battery_bank` for bulk charging ($+25.0\text{ kW}$). Agent 2 concurrently emitted `discharge_battery_storage 30.0`, triggering contradictory write collision and physical voltage instability.
- In Fleet Logistics ($N=20$), Agent 1 allocated `charging_hub` capacity ($+120.0\text{ kW}$), raising active load to $170.0\text{ kW}$. Agent 2 concurrently emitted `queue_fast_charger 120.0`, pushing total draw to $290.0\text{ kW} > 200.0\text{ kW}$ and tripping `GRID_TRANSFORMER_BLOWOUT`.

### 5.2 Arm 3 Governance Mitigation Mechanics
In Arm 3, the Host Concurrency Arbiter preempted these failures at the grammar compilation layer:
- While Agent 1 held `battery_bank`, `discharge_battery_storage` was dynamically pruned from Agent 2's GBNF grammar. The model was constrained to choose `shed_industrial_feeder 40.0`, resolving both sub-goals in parallel.
- While Agent 1 held `charging_hub`, `queue_fast_charger` was pruned for Agent 2. The model safely fell back to `refrigerate_cargo_bay -18.0`, preserving transformer capacity invariants.

---

## 6. Threats to Validity

- **Internal Validity:** Eliminated prompt non-determinism via greedy decoding ($T = 0.0$, `seed=42`). State updates were mediated through deterministic physical conservation equations.
- **External Validity:** Demonstrates multi-agent symbiosis on small language models ($< 4\text{B}$). Larger models ($> 70\text{B}$) may exhibit internal coordination heuristics, but SLMs strictly require external host-authoritative governance to prevent state corruption.
- **Construct Validity:** Evaluated against 3 distinct engineering domains with physical conservation bounds (Kirchhoff voltage laws, angular momentum conservation, electrical load ceilings).

---

## 7. Gate B Contract Compliance Audit

| Clause ID | Clause Description | Contract Bound | Measured Value | Compliance Verdict |
| :---: | :--- | :---: | :---: | :---: |
| **M1** | Multi-Agent Task Resolution Rate | $\ge 85.0\%$ | 100.0% (60/60) | PASS |
| **M2** | Governance Superiority Delta | $\ge +40.0\%$ | +66.7% | PASS |
| **M3** | Committed Race Condition Breaches | $\equiv 0$ | 0 | PASS |
| **M4** | Deadlock / Mutual Starvation Cycles | $\equiv 0$ | 0 | PASS |
| **M5** | Per-Turn Prompt Token Ceiling | $\le 512\text{ tokens}$ | 38 tokens | PASS |
| **M6** | Turn Latency SLA | $< 1000\text{ ms}$ | 715 ms | PASS |
| **M7** | Multi-Agent AutoDream Compaction | $\ge 70.0\%$ | 75.0% | PASS |
| **M8** | Cryptographic Manifest & Zip Sealing | 100% Conformance | 100% (`32f13026...`) | PASS |

**Final Disposition Verdict:** PASS
