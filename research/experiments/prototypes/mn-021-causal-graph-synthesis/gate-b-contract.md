# Gate B Evaluation Contract: Milestone MN-021

**Milestone Identifier:** MN-021 (Federated Causal Graph Synthesis & Epistemic Discrepancy Reconciliation)  
**Evaluation Scope:** Dual-Track Benchmark Suite ($N=80$)  
**Target Subject Model:** Homogeneous pair of $2\times \text{Qwen3.5-2B-Q4_K_M.gguf}$  
**Contract Version:** 1.0.0 (Frozen)  

---

## 1. Experimental Methodology & Control Arms

The benchmark suite consists of $N=80$ standardized scenarios evaluated across three comparative experimental arms under Dual-Track execution:

1. **Arm 1 (Flat In-Context Baseline):**
   - Unassisted, uncoordinated peer execution.
   - Raw chronological narrative event text supplied in prompt context.
   - No Causal Event DAG, no Epistemic Reconciler, no GBNF affordance masking.
2. **Arm 2 (Reactive Memory Control):**
   - Independent peer execution with isolated local DAG representations.
   - Reactive action selection without Metacognitive Probing or Host Epistemic Reconciliation.
   - Physical leases enabled, but conflicting temporal observations treated as peer hallucination.
3. **Arm 3 (Full Federated Causal DAG & Epistemic Governance):**
   - Host-authoritative Multi-Parent Causal Event DAG ($P_1 \land \dots \land P_k \xrightarrow{R} E_{\text{new}}$).
   - Stochastic Shock Injection ($25\%$ anomaly base rate).
   - Epistemic Boundaries (Private Observations) enforcing active probing (`ACTION: PROBE`).
   - Deterministic 3-Step Host Epistemic Reconciliation ($[t_A, t_B]$ window slicing, intervening event lookup).
   - Topological AutoDream hierarchical graph clustering with bounded $k$-hop subgraphs.

---

## 2. Quantitative Acceptance Clauses

| Metric ID | Clause Name | Contract Bound | Verification Modality | Audit Status |
| :---: | :--- | :---: | :---: | :---: |
| **M1** | Primary Task Resolution Rate (Arm 3) | $\ge 85.0\%$ | Track 1 & Track 2 Suite ($N=80$) | MANDATORY |
| **M2** | Coordination Superiority Delta | $\Delta_{\text{Arm 3} - \text{Arm 2}} \ge +40.0\%$ | Absolute resolution percentage gain | MANDATORY |
| **M3** | Committed Physical Invariant Breaches | $\equiv 0$ | Hard constraint on committed state | MANDATORY |
| **M4** | Epistemic Reconciliation Accuracy | $\ge 95.0\%$ | Classification of temporal vs anomaly | MANDATORY |
| **M5** | Per-Turn Prompt Token Ceiling | $\le 512\text{ tokens}$ | Hard gate on all model forward passes | MANDATORY |
| **M6** | AutoDream Topological Compaction Ratio | $\ge 70.0\%$ | Relative to raw causal event stream | MANDATORY |
| **M7** | Mean Turn Latency SLA | $< 1000\text{ ms}$ | Track 2 real inference timing | MANDATORY |
| **M8** | Cryptographic Manifest & Zip Sealing | $100\%$ Conformance | Pre/post manifests & `audit_logs.zip` | MANDATORY |

---

## 3. Physical Domains & Scenario Allocation ($N=80$)

| Domain ID | Domain Description | Nominal Cases | Stochastic Shock Cases | Total Cases |
| :--- | :--- | :---: | :---: | :---: |
| **Domain A** | Martian Biosphere Colony Life Support | 20 | 7 | 27 |
| **Domain B** | Subsea Hydrothermal Energy Grid | 20 | 7 | 27 |
| **Domain C** | Orbital Constellation Satellite Relay | 20 | 6 | 26 |
| **TOTAL** | **Comprehensive Evaluation Corpus** | **60 (75%)** | **20 (25%)** | **80 (100%)** |

---

## 4. Dual-Track Execution Protocol

1. **Track 1 (Host Deterministic Simulator):**
   - Validates mathematical soundness, DAG traversal, and reconciliation algorithms across all 80 cases ($3 \text{ arms} \times 80 = 240\text{ runs}$).
2. **Track 2 (Real Model Inference via `llama-server.exe`):**
   - Executes $2\times \text{Qwen3.5-2B-Q4_K_M.gguf}$ on local Port 18502 ($3 \text{ arms} \times 80 = 240\text{ runs}$).
   - Strict temperature $T=0.0$, context length 4096.

---

## 5. Evidence Retention & Zero Bloat Protocol

- All 240 individual episode traces per track MUST be packaged into a single `audit_logs.zip` archive within the respective run directory.
- Exactly 0 loose JSON log files may be committed to Git.
- Archives MUST be verifiable via cryptographic SHA-256 fingerprints and readable via zero-extraction inspection.
