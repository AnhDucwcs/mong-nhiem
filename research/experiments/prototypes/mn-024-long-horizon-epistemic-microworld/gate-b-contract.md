# Gate B Evaluation Contract: MN-024 — Long-Horizon Physical Microworld Scaling & Multi-Hop Causal Maintenance Under Continuous Entropy Decay

## 1. Frozen Evaluation Protocol

- **Evaluation Corpus:** $N = 60$ standardized multi-agent microworld scenarios ($M = 3$ agents) evaluated across two discrete horizon tiers:
  - **Tier A (Nominal):** $T = 60$ discrete ticks, causal distance $\Delta t \ge 40$ ticks.
  - **Tier B (Stress):** $T = 100$ discrete ticks, causal distance $\Delta t \ge 80$ ticks.
- **Physical Domains (Deep Cyber-Physical Environments):**
  1. Fission Reactor Core Cooling & Containment ($N=20$)
  2. Deep-Space Orbital Habitat Atmospheric Recycling ($N=20$)
  3. Regional Smart Microgrid Cascading Fault Isolation ($N=20$)
- **Experimental Arms:**
  - **Arm 1 (Flat Omniscient Baseline):** Direct unpartitioned global state view; vulnerable to epistemic leakage and race collisions.
  - **Arm 2 (Unpruned Subjective Memory Control):** Partitioned observation without topological branch pruning; vulnerable to massive context bloat and causal amnesia.
  - **Arm 3 (Host Epistemic Microworld Architecture):** Host access control, 3-Tier Causal Memory (Tier 1 invariant anchors, Tier 2 causal frontier, Tier 3 affordances), Vector Clock Causal DAG, and Concurrency Arbiter.
- **Evaluation Tracks:**
  - **Track 1:** Deterministic Host Simulator ($N = 60$ cases $\times 3$ arms $= 180$ episodes).
  - **Track 2:** Real Open-Weights SLM Inference with $3 \times \text{Qwen3.5-2B-Q4_K_M}$ on local `llama-server.exe` ($N = 60$ cases $\times 3$ arms $= 180$ episodes).

---

## 2. Quantitative Acceptance Clauses

| Clause ID | Metric Description | Frozen Acceptance Bound | Mandatory / Optional | Falsification Trigger |
| :---: | :--- | :---: | :---: | :--- |
| **M1** | Long-Horizon Task Resolution Rate (Arm 3) | $\ge 85.0\%$ | Mandatory | Score $< 85.0\%$ on either Horizon Tier |
| **M2** | Multi-Cycle Causal Anchor Retention Delta ($\Delta R_{\text{causal}}$ with $\Delta t \ge 40$ / $\ge 80$) | $\ge +50.0\%$ | Mandatory | Margin $< +50.0\%$ between Arm 3 and Arm 2 |
| **M3** | Continuous Epistemic Information Leakage Score | $\equiv 0.0$ | Mandatory | Any private secret/fact leaked into unauthorized prompt |
| **M4** | Committed Physical Invariant Breaches | $\equiv 0$ | Mandatory | Any invalid physical mutation committed to world state |
| **M5** | Committed Concurrency Race Collisions | $\equiv 0$ | Mandatory | Any unmanaged concurrent conflict committed |
| **M6** | Multi-Hop Causal Cascade Completion Rate | $\ge 80.0\%$ | Mandatory | 4-hop sequential dependency resolution $< 80.0\%$ |
| **M7** | Per-Agent Prompt Token Ceiling Under Long Horizon | $\le 512\text{ tokens}$ | Mandatory | Any prompt in Arm 3 exceeding $512$ tokens |
| **M8** | Mean Turn Latency SLA | $< 1000\text{ ms}$ | Mandatory | Average turn time $\ge 1000\text{ ms}$ on SLM |
| **M9** | AutoDream Long-Horizon Compaction Ratio | $\ge 70.0\%$ | Mandatory | Compaction ratio $< 70.0\%$ across multi-cycle pruning |
| **M10** | Non-Omniscient Action Groundedness ($F_{\text{grounded}}$) | $\equiv 100.0\%$ | Mandatory | Any action exploiting unobserved secrets or un-reconciled facts |

---

## 3. Operational Rules & Anti-Falsification Invariants

1. **Dual-Horizon Completeness:** Both Horizon Tier A ($T=60$) and Horizon Tier B ($T=100$) must be empirically audited.
2. **Independent Post-Generation Verification:** All metrics in generated reports must be verified directly against raw execution logs in `audit_logs.zip` and the frozen Gate B contract.
3. **Strict Clause-by-Clause Falsification:** If ANY empirical metric breaches a contract bound, the corresponding clause MUST be marked `FAIL`.
4. **Zero Retroactive Threshold Alteration:** Acceptance thresholds ($\ge 85.0\%$, $\ge +50.0\%$, $\equiv 0.0$, $\equiv 0$, $\le 512$, $< 1000\text{ ms}$) are permanently frozen upon ratification.
5. **Zero Loose File Bloat Protocol:** All episode execution traces must be archived into standard library `audit_logs.zip` archives before manifest freezing. No individual `.json` episode files in Git.
6. **Strict Prototype Quarantine:** All experimental scripts remain quarantined in `research/experiments/prototypes/mn-024-long-horizon-epistemic-microworld/` until earned Gate D disposition review.
