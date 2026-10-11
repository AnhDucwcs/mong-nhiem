# Stage 3 Gate B Evaluation Contract (`drift-003-causal-event-synthesis`)

## Status & Governance Invariant

This contract establishes the immutable, frozen acceptance bounds for Stage 3 of Milestone MN-019. In accordance with `AGENTS.md` Section 5, retroactive alteration or relaxation of these thresholds is strictly prohibited. Every clause must evaluate to `PASS` from raw traces before a milestone disposition of `PASS` can be declared.

---

## 1. Quantitative Evaluation Bounds (Clauses M1–M9)

| Clause ID | Metric Description | Frozen Acceptance Threshold | Mathematical Bound | Verification Source |
| :---: | :--- | :---: | :---: | :--- |
| **M1** | Overall Task Resolution (Arm 3) | $\ge 85.0\%$ | $\text{SR}_{\text{Arm3}} \ge 51/60$ | `audit_logs/*.json` |
| **M2** | Comparative Margin vs Arm 2 (Reactive Control) | $\ge +40.0\%$ | $\text{SR}_{\text{Arm3}} - \text{SR}_{\text{Arm2}} \ge +40.0\%$ | `audit_logs/*.json` |
| **M3** | Comparative Margin vs Arm 1 (Flat Baseline) | $\ge +80.0\%$ | $\text{SR}_{\text{Arm3}} - \text{SR}_{\text{Arm1}} \ge +80.0\%$ | `audit_logs/*.json` |
| **M4** | Out-of-Distribution (OOD) Resolution | $\ge 80.0\%$ | $\text{SR}_{\text{OOD}} \ge 24/30$ | `audit_logs/*.json` |
| **M5** | Physical & Schema Invariant Integrity | Exactly 0 violations | $\sum N_{\text{committed\_violations}} = 0$ | `audit_logs/*.json` |
| **M6** | Proactive Latent Trap Bypass Rate | $\ge 80.0\%$ | $N_{\text{proactive\_bypass}} / N_{\text{traps}} \ge 0.80$ | `audit_logs/*.json` |
| **M7** | AutoDream Causal Compaction Ratio | $\ge 70.0\%$ | $\text{Compaction} \ge 0.70$ | `audit_logs/*.json` |
| **M8** | Forward Prompt Token Budget Ceiling | $\le 512\text{ tok}$ (Max), $\le 384\text{ tok}$ (Mean) | $\max \le 512, \text{mean} \le 384$ | `audit_logs/*.json` |
| **M9** | Mean Turn Latency SLA | $< 1000\text{ ms}$ | $\text{mean}(\text{latency}) < 1000.0$ | `audit_logs/*.json` |

---

## 2. Mandatory Failure Categorization

Any failure in control arms or ablation sweeps must be categorized according to the following failure taxonomy:
1. **Mode 1: Latent Causal Trap Trigger:** Execution of an action that triggers an unobserved cascading failure due to lack of counterfactual projection.
2. **Mode 2: Reactive Memento Rollback Exhaustion:** Excessive trial-and-error rollbacks exhausting the turn budget without finding the safe causal path.
3. **Mode 3: Physical Conservation Law Breach:** Committing an invariant breach directly into the microworld state.
4. **Mode 4: Context Overflow / Token Thrashing:** Exceeding the 512-token forward prompt budget.
