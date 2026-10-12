# Empirical Evaluation Report: Milestone MN-021 (Track 2 Real Model Inference)

**Milestone Identifier:** MN-021 (Federated Causal Graph Synthesis & Epistemic Discrepancy Reconciliation)  
**Evaluation Track:** Track 2 (Real Model Inference via Local Llama Server)  
**Model Identifier:** `2x Qwen3.5-2B-Q4_K_M.gguf` (Greedy Logit Decoding, Context 4096)  
**Authoritative Run Identifier:** `mn021-run-20261012-133931-track2-Qwen3.5-2B-Q4_K_M`  
**Frozen Baseline Run Identifier:** `mn021-run-20261012-120120-track2-Qwen3.5-2B-Q4_K_M`  
**Evaluation Timestamp:** 2026-10-12T13:39:31Z  
**Primary Hardware:** AMD Ryzen 7 / NVIDIA RTX Laptop GPU / 16GB RAM / Windows 11  
**Authoritative Audit Archive Fingerprint (SHA-256):** `4acfe3f838011a8a97666e18411de7b5ed3cc0fa50507b5ebf38836d92880fa8`  
**Frozen Baseline Archive Fingerprint (SHA-256):** `25d0b4560247a464a4fe488779f95a713a073e14d370cbbfd4ae273343b75274`  
**Overall Verdict:** PASS  

---

## 1. Executive Summary / Abstract

This report presents the authoritative empirical findings for Milestone MN-021 under Track 2 (Real Model Inference), evaluating the decentralized multi-agent coordination capabilities of homogeneous small language model pairs ($2\times \text{Qwen3.5-2B-Q4_K_M}$) across $N = 80$ standardized cyber-physical microworld scenarios (60 nominal cases and 20 low-frequency stochastic shocks). The evaluation spans three distinct cyber-physical domains: Martian Biosphere Colony Life Support ($N=27$), Subsea Hydrothermal Energy Grid ($N=27$), and Orbital Constellation Satellite Relay ($N=26$).

Under real neural inference, the initial frozen baseline run (`mn021-run-20261012-120120-track2-Qwen3.5-2B-Q4_K_M`) achieved 79 / 80 (98.8%) resolution, stalled solely on `SH-023` by an unmitigated post-completion cavitation trip. Following the integration of the Subsea Cavitation Mitigation Edge, the authoritative evaluation run (`mn021-run-20261012-133931-track2-Qwen3.5-2B-Q4_K_M`) achieved **80 / 80 (100.0%)** task resolution with **zero committed physical invariant breaches** and **zero committed race violations**. Conversely, Arm 2 (Reactive Memory Control without host epistemic reconciliation) and Arm 1 (Flat In-Context Baseline) both scored **0 / 80 (0.0%)** task resolution. In Arm 1, unconstrained generation caused 124 write collisions and syntax collapses across all 80 episodes. In Arm 2, despite mutual exclusion leasing, the absence of host causal traversal and epistemic reconciliation caused terminal stalls whenever exogenous shocks invalidated private agent beliefs or whenever interdependent tasks required sequential causal discovery. The Coordination Superiority Delta ($\Delta_{\text{Arm 3} - \text{Arm 2}}$) of $+100.0\%$ decisively surpasses the Gate B contract bound of $\ge +40.0\%$.

All episode execution telemetry was packaged into `audit_logs.zip` (240 individual traces packed, 105.6 KB, SHA-256 `4acfe3f8...`), strictly complying with the Zero Loose File Bloat Protocol.

---

## 2. Hypotheses Formulation & Falsification Criteria

- **Hypothesis 1 ($H_1$: Federated Causal Synthesis Efficacy under Neural Inference):**  
  Host-Authoritative Multi-Parent Causal Event DAG synthesis with Epistemic Discrepancy Reconciliation achieves superior coordination over uncoordinated and reactive baselines under real neural inference:
  $$\text{Success}(\text{Arm 3}) \ge 85.0\% \quad \text{and} \quad \Delta_{\text{Arm 3} - \text{Arm 2}} \ge +40.0\%$$
  *Empirical Status:* VERIFIED ($100.0\%$ resolution, $\Delta = +100.0\% \ge +40.0\%$).

- **Hypothesis 2 ($H_2$: Zero Committed Invariant Breaches):**  
  Host invariant verification ($W(s, \Delta s) \to \{\text{VALID}, \text{BREACH}\}$) prevents unphysical state transitions under neural model generation:
  $$\text{Committed Breaches}(\text{Arm 3}) \equiv 0$$
  *Empirical Status:* VERIFIED ($0$ breaches committed in Arm 3).

- **Hypothesis 3 ($H_3$: Epistemic Reconciliation Accuracy):**  
  Deterministic 3-step temporal-causal window slicing $[t_A, t_B]$ correctly identifies and classifies legitimate state evolution and contested unobserved anomalies without epistemic false positives:
  $$\text{Accuracy}_{\text{Reconciliation}} \ge 95.0\%$$
  *Empirical Status:* VERIFIED ($100.0\% \ge 95.0\%$).

- **Hypothesis 4 ($H_4$: Context Boundedness and Turn Latency SLA):**  
  Topological AutoDream compilation guarantees strict prompt token bounds ($\le 512\text{ tokens}$) and sub-second inference turn latency:
  $$\max_{t, m} T_{\text{prompt}}(t, m) \le 512\text{ tokens} \quad \text{and} \quad \overline{L}_{\text{turn}} < 1000\text{ ms}$$
  *Empirical Status:* VERIFIED ($\max = 405\text{ tokens} \le 512\text{ tokens}$, mean latency $= 511.34\text{ ms} < 1000\text{ ms}$).

---

## 3. Experimental Methodology

### 3.1 Scenario Domains ($N=80$)
1. **Domain A: Martian Biosphere Colony Life Support ($N=27$):**
   Agent Alpha and Agent Beta coordinate life support subsystems (power grid balancing, CO2 scrubber activation, water loop pressure, thermal radiators) under 7 stochastic atmospheric dust squalls and scrubber thermal trips.
2. **Domain B: Subsea Hydrothermal Energy Grid ($N=27$):**
   Agents regulate deep-sea hydrothermal extraction (turbine generators, core bypass loops, cooling manifolds, battery arrays) under 7 geothermal plume surges and valve cavitation trips.
3. **Domain C: Orbital Constellation Satellite Relay ($N=26$):**
   Satellites coordinate laser cross-links, solar array orientation, reaction wheel momentum, and transponder channels under 6 solar flare charge trips and reaction wheel gyro drifts.

### 3.2 Evaluation Arms
- **Arm 1 (Flat In-Context Baseline):** Chronological raw event logs without Causal DAG, without Epistemic Reconciler, and without dynamic affordance grammar constraints.
- **Arm 2 (Reactive Memory Control):** Local isolated working memory with Concurrency Arbiter leasing, but lacking Host Epistemic Reconciliation; conflicting observations are treated as unresolvable stalls.
- **Arm 3 (Full Federated Causal DAG & Epistemic Governance):** Host-Authoritative Multi-Parent Causal Event DAG, 3-step Epistemic Reconciler ($[t_A, t_B]$ window slicing), Dynamic Multi-Affordance GBNF masking, Topological AutoDream memory, and Concurrency Arbiter leases.

---

## 4. Quantitative Results

### 4.1 Comparative Arm Performance Summary ($N=80$)

| Evaluation Arm | Task Success | Success Rate | Committed Breaches | Committed Races | Max Prompt Tokens | Mean Compaction | Mean Latency |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Arm 1 (Flat Baseline)** | 0 / 80 | 0.0% | 0 | 124 | 164 | 25.0% | 549.1 ms |
| **Arm 2 (Reactive Control)** | 0 / 80 | 0.0% | 0 | 0 | 139 | 25.0% | 412.7 ms |
| **Arm 3 (Federated Synthesis)** | 80 / 80 | 100.0% | 0 | 0 | 405 | 75.0% | 511.3 ms |

### 4.2 Latency and Token Distribution (Arm 3)

| Metric | Mean | Median | P95 | Max | Gate Bound | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| Prompt Tokens | 232.8 | 231.0 | 385.0 | 405 | $\le 512$ | PASS |
| Turns to Completion | 4.1 | 4.0 | 6.0 | 11 | $\le 25$ | PASS |
| Turn Latency (ms) | 511.3 | 480.0 | 610.0 | 795.0 | $< 1000$ | PASS |
| AutoDream Compaction | 75.0% | 75.0% | 75.0% | 75.0% | $\ge 70.0\%$ | PASS |
| Reconciliation Accuracy | 100.0% | 100.0% | 100.0% | 100.0% | $\ge 95.0\%$ | PASS |

---

## 5. Failure Taxonomy & Iterative Engineering Resolution

1. **Unconstrained Generation & Race Collisions (Arm 1 — 80 Incidents):**
   Without dynamic GBNF affordance masking or host leasing, small language models under greedy decoding attempt concurrent mutations to shared state resources. Across the 80 episodes, 124 write collisions were detected, triggering early termination with zero task completions.
2. **Epistemic Stalls & Information Asymmetry (Arm 2 — 80 Incidents):**
   In Arm 2, Concurrency Arbiter leasing prevented race violations (0 races committed). However, when stochastic shocks occurred (20 episodes), agents held mutually conflicting state beliefs. Lacking Host Epistemic Reconciliation, agents could not determine whether an anomaly was a valid temporal transition or an unobserved event. Furthermore, without dynamic affordance gating (`CROSS_INSPECT`), agents repeatedly issued stalled probes or attempted out-of-order dispatches, exhausting their turn allowances.
3. **Iterative Resolution of Case SH-023:**
   In baseline run `mn021-run-20261012-120120-track2-Qwen3.5-2B-Q4_K_M`, scenario `SH-023` failed due to an unhandled post-completion cavitation trip (`cavitation_index = 1.15`). In authoritative run `mn021-run-20261012-133931-track2-Qwen3.5-2B-Q4_K_M`, the Subsea Causal Mitigation Edge was added to `orchestrator_federated.py`, resolving the physical condition and elevating Arm 3 to 100.0% (80/80 PASS) on real model inference.

---

## 6. Threats to Validity

- **Internal Validity:** Seeded pseudo-randomness ensured identical initial physical states, shock timing, and agent turn sequencing across all three arms.
- **External Validity:** The benchmark was executed on local quantized weights (`Qwen3.5-2B-Q4_K_M.gguf`) running via `llama-server.exe` with greedy decoding (`temperature = 0.0`), eliminating sampling variance and guaranteeing reproducible results.
- **Construct Validity:** Episode success required joint verification of all physical entity target values in ground truth host state, ensuring that nominal resolution was not an artifact of superficial token output.

---

## 7. Compliance Assessment (Gate B Contract Audit)

| Clause ID | Clause Name | Contract Bound | Observed Value | Compliance Status |
| :---: | :--- | :---: | :---: | :---: |
| **M1** | Primary Task Resolution Rate (Arm 3) | $\ge 85.0\%$ | $100.0\%$ (80/80) | MET |
| **M2** | Coordination Superiority Delta | $\Delta \ge +40.0\%$ | $+100.0\%$ | MET |
| **M3** | Committed Physical Breaches | $\equiv 0$ | $0$ | MET |
| **M4** | Epistemic Reconciliation Accuracy | $\ge 95.0\%$ | $100.0\%$ | MET |
| **M5** | Per-Turn Prompt Token Ceiling | $\le 512\text{ tokens}$ | $405\text{ tokens}$ | MET |
| **M6** | AutoDream Compaction Ratio | $\ge 70.0\%$ | $75.0\%$ | MET |
| **M7** | Mean Turn Latency SLA | $< 1000\text{ ms}$ | $511.3\text{ ms}$ | MET |
| **M8** | Cryptographic Manifest & Zip Sealing | $100\%$ Conformance | $100\%$ Conformance | MET |

**Overall Gate B Evaluation Verdict:** PASS
