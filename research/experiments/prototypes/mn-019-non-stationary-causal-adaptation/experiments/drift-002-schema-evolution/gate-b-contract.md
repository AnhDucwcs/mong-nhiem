# Stage 2 Gate B Evaluation Contract (`drift-002-schema-evolution`)

## Status & Governance Invariant

This contract establishes the immutable, frozen acceptance bounds for Stage 2 of Milestone MN-019. In accordance with `AGENTS.md` Section 5, retroactive alteration or relaxation of these thresholds is strictly prohibited. Every clause must evaluate to `PASS` from raw traces before a milestone disposition of `PASS` can be declared.

---

## 1. Quantitative Evaluation Bounds (Clauses M1–M9)

| Clause ID | Metric Description | Frozen Acceptance Threshold | Mathematical Bound | Verification Source |
| :---: | :--- | :---: | :---: | :--- |
| **M1** | Overall Task Resolution (Arm 3) | $\ge 85.0\%$ | $\text{SR}_{\text{Arm3}} \ge 51/60$ | `audit_logs/*.json` |
| **M2** | Comparative Margin vs Arm 2 (Static Control) | $\ge +50.0\%$ | $\text{SR}_{\text{Arm3}} - \text{SR}_{\text{Arm2}} \ge +50.0\%$ | `audit_logs/*.json` |
| **M3** | Comparative Margin vs Arm 1 (Flat Baseline) | $\ge +80.0\%$ | $\text{SR}_{\text{Arm3}} - \text{SR}_{\text{Arm1}} \ge +80.0\%$ | `audit_logs/*.json` |
| **M4** | Out-of-Distribution (OOD) Accuracy | $\ge 80.0\%$ | $\text{SR}_{\text{OOD}} \ge 24/30$ | `audit_logs/*.json` |
| **M5** | Schema & Physical Invariant Integrity | Exactly 0 violations | $\sum N_{\text{committed\_violations}} = 0$ | `audit_logs/*.json` |
| **M6** | Emergence Detection & Integration Latency | $\le 1\text{ tick}$ | $\Delta t_{\text{integration}} \le 1$ | `audit_logs/*.json` |
| **M7** | AutoDream Episodic Compaction Ratio | $\ge 70.0\%$ | $\text{Compaction} \ge 0.70$ | `audit_logs/*.json` |
| **M8** | Forward Prompt Token Budget Ceiling | $\le 512\text{ tok}$ (Max), $\le 384\text{ tok}$ (Mean) | $\max \le 512, \text{mean} \le 384$ | `audit_logs/*.json` |
| **M9** | Mean Turn Latency SLA | $< 1000\text{ ms}$ | $\text{mean}(\text{latency}) < 1000.0$ | `audit_logs/*.json` |

---

## 2. Mandatory Failure Categorization

Any failure in control arms or ablation sweeps must be categorized according to the following strict failure taxonomy:
1. **Mode 1: Illegal Entity Reference / Stale Invocation:** Attempting an action on an entity that has not yet emerged or has expired.
2. **Mode 2: Structural Desynchronization:** Failure of declarative memory to update when relational edges mutate, causing goal divergence.
3. **Mode 3: Physical Conservation Law Breach:** Exceeding energy, mass, or thermal capacity constraints under evolved conditions.
4. **Mode 4: Context Overflow / Token Thrashing:** Unbounded memory growth exceeding the 512-token ceiling.
