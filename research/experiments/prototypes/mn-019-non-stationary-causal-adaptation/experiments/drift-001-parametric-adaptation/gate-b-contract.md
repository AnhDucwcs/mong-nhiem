# Gate B Evaluation Contract: Stage 1 — Parametric Drift Adaptation

## Formal Acceptance Criteria and Invariant Bounds

This contract defines the non-negotiable quantitative acceptance rules governing the empirical evaluation of `drift-001-parametric-adaptation`. In strict accordance with `AGENTS.md` Section 5, any clause failing to achieve its numerical threshold shall result in an immediate `FAIL` or `CONDITIONAL` milestone disposition. Zero retroactive threshold alteration is authorized.

| Clause ID | Metric Name | Mathematical Specification | Target Bound | Target Outcome |
| :---: | :--- | :--- | :---: | :---: |
| **M1** | Overall Task Success Rate | $\text{SR}_{\text{Arm3}} = \frac{N_{\text{success}}}{60}$ on `Qwen3.5-2B` | $\ge 85.0\%$ ($51/60$) | **PASS** |
| **M2** | Comparative Margin vs Static Control | $\Delta_{\text{Arm3} - \text{Arm2}} = \text{SR}_{\text{Arm3}} - \text{SR}_{\text{Arm2}}$ | $\ge +50.0\%$ | **PASS** |
| **M3** | Comparative Margin vs Flat Baseline | $\Delta_{\text{Arm3} - \text{Arm1}} = \text{SR}_{\text{Arm3}} - \text{SR}_{\text{Arm1}}$ | $\ge +80.0\%$ | **PASS** |
| **M4** | Out-of-Distribution (OOD) Accuracy | $\text{SR}_{\text{OOD}} = \frac{N_{\text{success, OOD}}}{30}$ | $\ge 80.0\%$ ($24/30$) | **PASS** |
| **M5** | Committed Conservation Invariant Breaches | $\sum N_{\text{committed\_breaches}}$ | $= 0$ | **PASS** |
| **M6** | Discrepancy Detection Latency SLA | $T_{\text{detect}} - T_{\text{breach}}$ | $\le 2\text{ ticks}$ | **PASS** |
| **M7** | Autonomous AutoDream Compaction | $1 - \frac{\text{Compacted Tokens}}{\text{Raw Event Tokens}}$ | $\ge 70.0\%$ | **PASS** |
| **M8** | Prompt Token Ceiling Invariant | $\max(\text{Prompt Tokens})$ and $\text{mean}(\text{Prompt Tokens})$ | $\max \le 512, \text{mean} \le 384$ | **PASS** |
| **M9** | Turn Latency SLA | $\text{mean}(\text{Latency})$ on `llama-server` | $< 1000\text{ ms}$ | **PASS** |

---

## Evaluation Arms Specification

1. **Arm 1 (Flat Baseline):**
   - Freeform unstructured model response.
   - Zero GBNF grammar constraints, zero Discrepancy Monitor.
   - Expected outcome: Near 0% success due to unconstrained action space and hallucinated parameters.
2. **Arm 2 (Static Memory Control):**
   - Fixed GBNF DAG derived from nominal parameters (MN-018 architecture).
   - Zero drift awareness. Actions remain afforded even when degraded parameters make them physically non-conservative.
   - Expected outcome: Catastrophic failure on delayed rollback traps.
3. **Arm 3 (Dynamic Dual-Engine Host):**
   - Host Discrepancy Monitor tracking error vectors $D_t$.
   - Dynamic GBNF Affordance DAG with inviable action pruning and safe probing enablement.
   - Memento atomic rollback protecting world state invariants.
