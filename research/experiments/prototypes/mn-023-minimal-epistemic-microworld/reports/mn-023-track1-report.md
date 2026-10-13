# Academic Evaluation Report: Track 1 Simulator Benchmark (MN-023)

**Milestone:** MN-023: Minimal Controlled Microworld & Epistemic Invariant Verification Under Asymmetric Information  
**Track:** Track 1 (Deterministic Host Simulation)  
**Evaluation Target:** $N = 60$ Scenarios across 3 Domains ($180$ Episodes)  
**Date:** 2026-10-13  
**Status:** COMPLETE  
**Verdict:** PASS (10 / 10 Mandatory Clauses Met)

---

## 1. Executive Summary / Abstract

This report presents empirical findings from Track 1 of Milestone MN-023, evaluating the architectural integrity and formal invariants of the Mộng Nhiễm Epistemic Microworld. Mộng Nhiễm operates under the fundamental architectural invariant that the host environment exercises absolute authority over world-state mutations, access control, and causal provenance, while autonomous agents operate with partial, asymmetric observations and subjective beliefs.

The benchmark evaluated $N = 60$ standardized scenarios ($M = 3$ agents per scenario, totaling $180$ episodes) across three distinct physical domains: Secure Cyber-Physical Vaults ($N = 20$), Smart Microgrid Fault Isolation ($N = 20$), and Deep-Space Habitat Systems ($N = 20$). Across all test cases, the proposed Host Epistemic Microworld architecture ($\text{Arm 3}$) achieved a $100.0\%$ Task Resolution Rate ($\text{M1}$), $100.0\%$ Long-Horizon Causal Anchor Retention ($\text{M2}$ margin $\Delta R_{\text{causal}} = +100.0\%$), zero information leakage ($\text{M3} \equiv 0.0$), zero physical invariant breaches ($\text{M4} \equiv 0$), zero concurrency race collisions ($\text{M5} \equiv 0$), and $100.0\%$ non-omniscient action groundedness ($\text{M10} \equiv 100.0\%$). All ten frozen Gate B acceptance clauses passed decisively.

---

## 2. Hypotheses Formulation

The empirical validation was guided by six formal research hypotheses ratified during Gate A:

- **$H_1$ (Host Physical Invariant Preservation):** A host-authoritative kernel enforcing discrete pre-condition validation guarantees zero invalid physical mutations ($\text{Breaches} \equiv 0$) and zero concurrency collisions ($\text{Collisions} \equiv 0$).
  $$\text{Falsification Criterion: } \sum_{i=1}^N (\text{Breaches}_i + \text{Collisions}_i) > 0$$

- **$H_2$ (Long-Horizon Causal Anchor Retention Under Bounded Buffer):** Agents equipped with a 3-tier fact card maintain long-horizon causal retention ($R_{\text{causal}} \ge 90\%$) across $\Delta t \ge 15$ ticks, while unpruned gossip context ($\text{Arm 2}$) suffers amnesia or token overflow, exhibiting a delta $\Delta R_{\text{causal}} \ge +50.0\%$.
  $$\text{Falsification Criterion: } R_{\text{causal}}(\text{Arm 3}) - R_{\text{causal}}(\text{Arm 2}) < 0.50$$

- **$H_3$ (Zero Epistemic Information Leakage):** Cryptographic observation masking guarantees zero private state variables enter unauthorized agent prompt buffers ($\Lambda_{\text{leakage}} \equiv 0.0$).
  $$\text{Falsification Criterion: } \Lambda_{\text{leakage}}(\text{Arm 3}) > 0.0$$

- **$H_4$ (Resource Lease Serialization):** Host multi-resource arbiter eliminates state collisions during concurrent action dispatch.
  $$\text{Falsification Criterion: } \text{Collisions}(\text{Arm 3}) > 0$$

- **$H_5$ (Asymmetric Non-Omniscient Action Groundedness):** No agent commits an action conditioning on private state variables prior to causal discovery.
  $$\text{Falsification Criterion: } F_{\text{grounded}}(\text{Arm 3}) < 1.0$$

- **$H_6$ (Epistemic Discrepancy Reconciliation):** Agents reconcile conflicting rumors and genuine observations via causal DAG provenance graphs with resolution rate $\ge 80.0\%$.
  $$\text{Falsification Criterion: } \text{ResolutionRate}(\text{Arm 3}) < 0.80$$

---

## 3. Experimental Methodology

### 3.1 Independent Variables (Experimental Arms)

1. **Arm 1 (Flat Omniscient Baseline):** Agents receive a full, unpartitioned global world-state dump. Agents dispatch actions directly without lease arbitration or provenance checks.
2. **Arm 2 (Unpruned Subjective Memory Control):** Agents observe subjective states through observation masks, but historical communications and observations accumulate linearly without frontier pruning or fact-card tiering.
3. **Arm 3 (Epistemic Microworld Architecture):** Incorporates `EpistemicMaskEngine`, 3-Tier Fact Card compaction (Tier 1 invariant anchors, Tier 2 causal frontier, Tier 3 affordances), `MultiResourceArbiter`, and `EpistemicReconciler`.

### 3.2 Evaluation Corpus

The test harness synthesizes $60$ distinct scenarios structured across three operational domains:
- **Cyber-Physical Vault:** Access control under encrypted passcodes, corridor patrols, and voltage isolation.
- **Smart Microgrid:** Substation transformer isolation, load balancing, and switch disconnections.
- **Deep-Space Habitat:** Air pressure stabilization, life support valve configuration, and oxygen scrubbing.

Each scenario enforces:
- $M = 3$ concurrent agents: Scout (Sensor/Discovery), Engineer (Resolution/Action), Guard (Environmental Maintenance).
- A mandatory causal separation of $\Delta t \ge 15$ discrete ticks between secret discovery (Tick 0/1) and resolution attempt (Tick 18).
- Initial epistemic discrepancy: Engineer holds a false rumor regarding the authorization credential.

---

## 4. Quantitative Results

### 4.1 Cross-Arm Comparative Distributions

| Metric | Arm 1 (Omniscient Baseline) | Arm 2 (Unpruned Control) | Arm 3 (Proposed Microworld) | Gate B Bound | Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Task Resolution Rate ($M_1$) | $0.0\%$ | $0.0\%$ | $100.0\%$ | $\ge 85.0\%$ | PASS |
| Causal Anchor Retention ($R_{\text{causal}}$) | $100.0\%$ | $0.0\%$ | $100.0\%$ | $\Delta \ge +50.0\%$ | PASS ($\Delta = +100.0\%$) |
| Epistemic Leakage Score ($M_3$) | $1.000$ | $0.000$ | $0.000$ | $\equiv 0.0$ | PASS |
| Physical Invariant Breaches ($M_4$) | $0$ | $0$ | $0$ | $\equiv 0$ | PASS |
| Race Collisions ($M_5$) | $60$ | $0$ | $0$ | $\equiv 0$ | PASS |
| Epistemic Discrepancy Resolution ($M_6$) | N/A | $50.0\%$ | $100.0\%$ | $\ge 80.0\%$ | PASS |
| Mean Turn Latency ($M_8$) | $1.5\text{ ms}$ | $1.5\text{ ms}$ | $1.5\text{ ms}$ | $< 1000\text{ ms}$ | PASS |
| Action Groundedness ($M_{10}$) | $0.0\%$ (Telepathic) | $100.0\%$ | $100.0\%$ | $\equiv 100.0\%$ | PASS |

### 4.2 Prompt Token Consumption Distributions ($M_7$)

| Arm | Mean Tokens | Median Tokens | P95 Tokens | Max Tokens | Bound ($\le 512$) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Arm 1 (Omniscient) | $162.0$ | $162.0$ | $162.0$ | $162.0$ | PASS (Leaked) |
| Arm 2 (Unpruned) | $530.0$ | $530.0$ | $530.0$ | $530.0$ | FAIL ($> 512$) |
| Arm 3 (Tiered Compact) | $156.4$ | $156.0$ | $162.0$ | $162.0$ | PASS ($\le 512$) |

In Arm 2, monotonic unpruned history accumulation over $18$ ticks forced total token consumption to $530.0$ tokens, breaching the $512$ token ceiling. Under the 512-token rolling window, the critical causal discovery event at Tick 1 was truncated out, reducing causal anchor retention to $0.0\%$. In contrast, Arm 3 isolated the anchor into Tier 1, preserving complete causal memory with only $156.4$ mean tokens ($70.5\%$ buffer headroom remaining).

---

## 5. Failure Taxonomy & Error Analysis

The empirical failures observed in Arm 1 and Arm 2 follow three strict mathematical failure classes:

1. **Class A: Epistemic Telepathy & Information Leakage (Arm 1):**
   - Direct global state serialization exposed private entity passcodes to all agents prior to discovery. Although Arm 1 could theoretically unlock the vault, it violated Clause M3 ($\Lambda_{\text{leakage}} = 1.0$) and M10 ($F_{\text{grounded}} = 0.0\%$), rendering the baseline epistemically invalid.
2. **Class B: Concurrency Collision Under Uncoordinated Dispatch (Arm 1):**
   - Without the `MultiResourceArbiter`, concurrent actions by Engineer and Guard collided on target states, triggering $60$ committed race collisions across the $60$ scenarios.
3. **Class C: Context Overflow & Causal Amnesia (Arm 2):**
   - Without tiered pruning, gossip and routine event accumulation exceeded the $512$ token ceiling by Tick 18 ($530$ tokens). When bounded to $512$ tokens, the agent experienced amnesia regarding the initial secret transmission, resulting in $0.0\%$ anchor retention and $0.0\%$ task completion.

---

## 6. Threats to Validity

- **Internal Validity:** The Track 1 benchmark employed deterministic policy mock functions rather than real SLM autoregressive generation. While this isolates architectural logic from stochastic token generation, real SLM syntax formatting and latency dynamics require validation in Track 2.
- **External Validity:** Scenarios were generated deterministically across three cyber-physical templates. Complex open-world domains with non-linear branching may introduce higher epistemic ambiguity.
- **Construct Validity:** Epistemic discrepancy resolution assumed binary rumor-versus-observation conflicts. Multi-agent deception or Byzantine adversaries were evaluated in MN-022 rather than MN-023.

---

## 7. Compliance Assessment Against Gate B Contract

| Clause | Description | Frozen Bound | Track 1 Observed | Compliance Verdict |
| :---: | :--- | :---: | :---: | :---: |
| **M1** | Task Resolution Rate (Arm 3) | $\ge 85.0\%$ | $100.0\%$ | PASS |
| **M2** | Causal Anchor Retention Delta ($\Delta R_{\text{causal}}$) | $\ge +50.0\%$ | $+100.0\%$ | PASS |
| **M3** | Epistemic Information Leakage Score | $\equiv 0.0$ | $0.000$ | PASS |
| **M4** | Committed Physical Invariant Breaches | $\equiv 0$ | $0$ | PASS |
| **M5** | Committed Concurrency Race Collisions | $\equiv 0$ | $0$ | PASS |
| **M6** | Epistemic Discrepancy Resolution Rate | $\ge 80.0\%$ | $100.0\%$ | PASS |
| **M7** | Per-Agent Prompt Token Ceiling | $\le 512\text{ tokens}$ | $162.0\text{ max tokens}$ | PASS |
| **M8** | Mean Turn Latency SLA | $< 1000\text{ ms}$ | $1.5\text{ ms}$ | PASS |
| **M9** | Cryptographic Manifest & Archival | $100\%$ | Conforming | PASS |
| **M10** | Non-Omniscient Action Groundedness | $\equiv 100.0\%$ | $100.0\%$ | PASS |

**Overall Track 1 Disposition:** FULL PASS. The Host Epistemic Microworld architecture strictly satisfies all structural and causal invariants under deterministic simulation.
