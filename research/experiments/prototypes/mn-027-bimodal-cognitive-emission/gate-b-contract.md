# Gate B Evaluation Contract: Milestone MN-027

## 1. Frozen Acceptance Clauses ($M_1 \to M_{10}$)

This contract establishes the quantitative acceptance criteria for Milestone MN-027: Bimodal Cognitive Emission, Declarative Schema Synthesis & Real-Time Human Supervisory Control. Both Track 1 (Host Simulator) and Track 2 (Real Model Inference on `Qwen3.5-2B-Q4_K_M.gguf`) must independently satisfy all 10 clauses to earn an unconditional passing disposition. Under Mộng Nhiễm governance rules, these thresholds are frozen prior to execution and cannot be altered retroactively.

| Clause ID | Metric Name | Mathematical Definition | Acceptance Threshold | Falsification Condition |
| :--- | :--- | :--- | :--- | :--- |
| **M1** | Physical Task Completion Rate | $\frac{N_{\text{resolved}}}{N_{\text{total}}}$ on Arm 3 | $\ge 85.0\%$ | $M_1 < 85.0\%$ |
| **M2** | Bimodal Syntax Parse Determinism | $\frac{N_{\text{valid\_syntax}}}{N_{\text{total\_turns}}}$ (both `ACTION` and `COMMUNICATE` parsed) | $\equiv 100.0\%$ | $M_2 < 100.0\%$ |
| **M3** | Triadic Communicative Classification | $\frac{N_{\text{correct\_class}}}{N_{\text{total\_turns}}}$ across `INFORM`, `QUERY`, `EXPRESS` | $\equiv 100.0\%$ | $M_3 < 100.0\%$ |
| **M4** | Human Supervisory Recovery Rate | $\frac{N_{\text{recovered}}}{N_{\text{standby}}}$ after `HUMAN_INTERRUPT` injection | $\equiv 100.0\%$ | $M_4 < 100.0\%$ |
| **M5** | Real-Time Clock Synchronization Drift | $|\tau_{\text{actual}} - \tau_{\text{target}}|$ jitter on monotonic tick | $\le 15.0\text{ ms}$ | $M_5 > 15.0\text{ ms}$ |
| **M6** | Continuous State Decay Trigger Precision | Rate of accurate threshold invariant triggering under decay | $\equiv 100.0\%$ | $M_6 < 100.0\%$ |
| **M7** | Token Savings Delta over Two-Call | $\frac{\text{Tokens}_{\text{Arm 2}} - \text{Tokens}_{\text{Arm 3}}}{\text{Tokens}_{\text{Arm 2}}}$ relative reduction | $\ge 35.0\%$ | $M_7 < 35.0\%$ |
| **M8** | Max Prompt Memory Ceiling | $\max_{t} \text{Tokens}_t(\text{Arm 3})$ working prompt tokens | $\le 512\text{ tokens}$ | $\text{Tokens}_{\max} > 512$ |
| **M9** | Mean Turn Inference Latency | $\frac{1}{K}\sum_{k=1}^K T_{\text{turn}, k}$ on local hardware | $< 500\text{ ms}$ ($< 1000\text{ ms}$ SLA) | $\bar{T}_{\text{turn}} \ge 1000\text{ ms}$ |
| **M10** | Zero Loose File Bloat Compliance | Verification of sealed `audit_logs.zip` and zero loose JSON logs | $\equiv 100.0\%$ | Loose JSON logs present |

---

## 2. Experimental Corpus & Workload Partitioning

- **Total Standardized Scenarios ($N = 60$):**
  - **Domain A ($N = 20$):** Cyber-Physical / SCADA Supervision (Sensor blackout, valve isolation, telemetry broadcast). Focus: `INFORM` & `QUERY`.
  - **Domain B ($N = 20$):** Personal Desktop Task Assistant (Deadlines, resource collisions, human supervisory preemption). Focus: `QUERY`, `INFORM`, `HUMAN_INTERRUPT`.
  - **Domain C ($N = 20$):** Stateful Interactive Companion (Energy/hunger continuous decay, social banter). Focus: `EXPRESS` ($T=0.5$), `INFORM`.
- **Comparative Evaluation Arms:**
  - Arm 1: Flat Unconstrained Baseline ($60$ episodes).
  - Arm 2: Decoupled Two-Call Control ($60$ episodes).
  - Arm 3: Integrated Bimodal Cognitive Host ($60$ episodes).
- **Total Episode Volume per Track:** $60 \times 3 = 180$ episodes ($360$ episodes across Track 1 and Track 2).

---

## 3. Mandatory Telemetry & Audit Packaging

In accordance with the **Zero Loose File Bloat Protocol**:
1. All individual episode traces must be serialized directly to standard zip archives:
   - Track 1 Archive: `runs/run_<timestamp>_track1_sim/audit_logs.zip`
   - Track 2 Archive: `runs/run_<timestamp>_track2_qwen/audit_logs.zip`
2. No loose JSON log files may be committed to Git.
3. Each run directory must contain exactly one `summary.json` manifest recording the aggregate metric distribution and SHA-256 archive checksum.
