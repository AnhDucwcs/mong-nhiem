# Gate B Evaluation Contract: MN-023 — Minimal Controlled Microworld & Epistemic Invariant Verification Under Asymmetric Information

## 1. Frozen Evaluation Protocol

- **Evaluation Corpus:** $N = 60$ standardized multi-agent microworld scenarios ($M = 3$ agents) featuring:
  - Asymmetric observation masks (Private versus Public entities).
  - Hidden state variables (Secrets, private keys, undisclosed event causes).
  - Causal pivot events requiring multi-hop discovery before resolution.
- **Experimental Arms:**
  - **Arm 1 (Flat Omniscient Baseline):** Direct unpartitioned state view; vulnerable to epistemic leakage and race collisions.
  - **Arm 2 (Unpruned Subjective Memory Control):** Partitioned observation without topological branch pruning; vulnerable to context overflow.
  - **Arm 3 (Host Epistemic Microworld Architecture):** Host access control, 3-Tier Causal Memory, Vector Clock Causal DAG, and Concurrency Arbiter.
- **Evaluation Tracks:**
  - **Track 1:** Deterministic Host Simulator ($N = 60$ cases $\times 3$ arms $= 180$ episodes).
  - **Track 2:** Real Open-Weights SLM Inference with $3 \times \text{Qwen3.5-2B}$ on local `llama-server.exe` ($N = 60$ cases $\times 3$ arms $= 180$ episodes).

---

## 2. Quantitative Acceptance Clauses

| Clause ID | Metric Description | Frozen Acceptance Bound | Mandatory / Optional | Falsification Trigger |
| :---: | :--- | :---: | :---: | :--- |
| **M1** | Task Resolution Rate (Arm 3) | $\ge 85.0\%$ | Mandatory | Score $< 85.0\%$ on Track 1 or Track 2 |
| **M2** | Coordination Superiority Margin ($\Delta_{\text{Arm 3} - \text{Arm 2}}$) | $\ge +40.0\%$ | Mandatory | Resolution margin $< +40.0\%$ |
| **M3** | Epistemic Information Leakage Score | $\equiv 0.0$ | Mandatory | Any private secret/fact leaked to unauthorized agent |
| **M4** | Committed Physical Invariant Breaches | $\equiv 0$ | Mandatory | Any invalid mutation committed to world state |
| **M5** | Committed Concurrency Race Collisions | $\equiv 0$ | Mandatory | Any unmanaged concurrent conflict committed |
| **M6** | Causal Anchor Epistemic Recall | $\ge 90.0\%$ | Mandatory | Recall of decision-critical anchor facts $< 90.0\%$ |
| **M7** | Per-Agent Prompt Token Ceiling | $\le 512\text{ tokens}$ | Mandatory | Any prompt exceeding $512$ tokens |
| **M8** | Mean Turn Latency SLA | $< 1000\text{ ms}$ | Mandatory | Average turn time $\ge 1000\text{ ms}$ on SLM |
| **M9** | Cryptographic Manifest & Evidence Archival | $100\%$ Conformance | Mandatory | Any unhashed file or loose JSON log |

---

## 3. Operational Rules & Anti-Falsification Invariants

1. **Independent Post-Generation Verification:** Every metric in generated academic reports must be directly audited against raw execution logs in `audit_logs.zip` and the frozen Gate B contract.
2. **Strict Clause-by-Clause Falsification:** If ANY empirical metric breaches a contract bound (e.g., Epistemic Leakage $> 0$ or Prompt $> 512$ tokens), the corresponding clause MUST be marked `FAIL`.
3. **Zero Retroactive Threshold Alteration:** Acceptance thresholds ($85.0\%$, $+40.0\%$, $0.0$, $\le 512$) are permanently frozen upon Gate B ratification.
4. **Zero Loose File Bloat Protocol:** All episode execution traces must be archived into standard library `audit_logs.zip` archives before manifest freezing. No individual `.json` episode files in Git.
5. **Strict Prototype Quarantine:** All experimental scripts remain quarantined in `research/experiments/prototypes/mn-023-minimal-epistemic-microworld/` until earned Gate D disposition review.
