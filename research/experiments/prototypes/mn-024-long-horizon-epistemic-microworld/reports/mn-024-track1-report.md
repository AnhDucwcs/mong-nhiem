# Empirical Evaluation Report: MN-024 (Track 1 — Deterministic Host Simulation)

**Milestone:** MN-024 — Long-Horizon Physical Microworld Scaling & Multi-Hop Causal Maintenance Under Continuous Entropy Decay  
**Evaluation Track:** Track 1 (Deterministic Host Simulation across Dual Horizons: $T=60$ and $T=100$)  
**Target Environment:** 3 Cyber-Physical Microworlds ($N=60$ scenarios $\times 2$ horizons $\times 3$ experimental arms $= 360$ total episodes)  
**Evaluator:** `LongHorizonEvaluator` (`evaluator.py`)  
**Date:** 2026-10-17  
**Overall Verdict:** PASS  

---

## 1. Executive Summary

This academic evaluation report presents the empirical findings of Milestone MN-024 Track 1. The investigation evaluates multi-agent operational stability, 4-hop causal dependency chain resolution, and active maintenance under continuous passive environmental entropy decay across two extended temporal horizon tiers:
- **Horizon Tier A (Nominal):** $T = 60$ discrete ticks with causal distance $\Delta t \ge 40$ ticks.
- **Horizon Tier B (Stress):** $T = 100$ discrete ticks with causal distance $\Delta t \ge 80$ ticks.

The evaluation benchmarks three experimental arms:
1. **Arm 1 (Flat Omniscient Baseline):** Unpartitioned global state visibility without concurrency arbitration or access controls.
2. **Arm 2 (Unpruned Subjective Memory Control):** Epistemic observation partitioning without structured fact-card compaction, accumulating raw cumulative transcript history.
3. **Arm 3 (Host Epistemic Microworld Architecture):** Host-authoritative 3-tier fact-card compaction (Tier 1 invariant anchors, Tier 2 causal frontier, Tier 3 valid affordances), MultiResourceArbiter concurrency control, and continuous entropy mitigation.

Across all $360$ simulated episodes, Arm 3 satisfied all 10 quantitative acceptance clauses ($M_1$ through $M_{10}$) with zero physical invariant breaches, zero concurrency race collisions, zero epistemic leakages, and strict adherence to the prompt token ceiling ($55\text{ tokens} \le 512\text{ tokens}$).

---

## 2. Hypotheses Formulation & Falsification Thresholds

The experiment evaluated five formal hypotheses ($H_1$ to $H_5$):

- **$H_1$ (Multi-Hop Causal Cascade Resolution):** Under continuous passive decay, Arm 3 achieves 4-hop cascade completion $S_{\text{cascade}} \ge 80.0\%$, whereas Arm 1 and Arm 2 drop below $30.0\%$ due to uncoordinated race collisions or memory amnesia.
  $$\text{Falsified if: } S_{\text{cascade}}(\text{Arm 3}) < 80.0\%$$
- **$H_2$ (Causal Anchor Retention Across Temporal Distances):** Retaining ground-truth secret anchors in Tier 1 fact cards yields an anchor retention advantage $\Delta R_{\text{causal}} = R_{\text{Arm 3}} - R_{\text{Arm 2}} \ge +50.0\%$ at $\Delta t \ge 40$ and $\Delta t \ge 80$.
  $$\text{Falsified if: } \Delta R_{\text{causal}} < 50.0\%$$
- **$H_3$ (Zero Continuous Epistemic Information Leakage):** Host observation projection prevents private secrets or unauthorized state variables from appearing in agent observation contexts.
  $$\text{Falsified if: } L_{\text{epistemic}} > 0.0$$
- **$H_4$ (Continuous Environmental Stability):** Proactive lease-based maintenance prevents thermodynamic and electrical drift from exceeding safe operational bounds.
  $$\text{Falsified if: } B_{\text{physical}}(\text{Arm 3}) > 0$$
- **$H_5$ (Bounded Working Memory Under Extended Horizons):** 3-Tier fact-card compaction maintains per-agent prompt size $P_{95} \le 512\text{ tokens}$ and achieves $\ge 70.0\%$ token compaction relative to raw cumulative history logs.
  $$\text{Falsified if: } \text{Tokens}_{P95}(\text{Arm 3}) > 512 \text{ or Compaction Ratio} < 70.0\%$$

---

## 3. Experimental Methodology

### 3.1 Scenario Corpus Configuration
The evaluation corpus comprises $N=60$ standardized scenarios across three critical physical domains:
1. **Fission Reactor Core Cooling & Containment ($N=20$):** Continuous core heat accumulation ($\Delta T = +1.2^\circ\text{C/tick}$), coolant loop telemetry, auxiliary bypass coupling, and radiation containment vault locking.
2. **Deep-Space Orbital Habitat Atmospheric Recycling ($N=20$):** Passive $O_2$ scrubber manifold pressure drop ($\Delta P = -0.8\text{ kPa/tick}$), nitrogen injector coupling, and airlock pressure vessel locking.
3. **Regional Smart Microgrid Cascading Fault Isolation ($N=20$):** Reactive line power oscillation ($\Delta f = +0.15\text{ Hz/tick}$), transformer coupling, and automated breaker switchboard authorization.

### 3.2 Discrete Horizon Tiers
- **Tier A ($T=60$ ticks):** Hop 1 at $t=0$, communication at $t=1$, Hop 2 isolation at $t=8$, Hop 3 coupling at $t=20$, Hop 4 resolution at $t=45$ ($\Delta t = 44 \ge 40$ ticks). Maintenance period = 8 ticks.
- **Tier B ($T=100$ ticks):** Hop 1 at $t=0$, communication at $t=1$, Hop 2 isolation at $t=15$, Hop 3 coupling at $t=40$, Hop 4 resolution at $t=85$ ($\Delta t = 84 \ge 80$ ticks). Maintenance period = 12 ticks.

---

## 4. Quantitative Results

### 4.1 Comparative Arm Performance Summary

| Horizon Tier | Metric | Arm 1 (Flat Omniscient) | Arm 2 (Unpruned Subjective) | Arm 3 (Host Architecture) | Target Bound |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **Tier A ($T=60$)** | Task Resolution Rate ($M_1$) | $0.00\%$ | $0.00\%$ | $100.00\%$ | $\ge 85.0\%$ |
| | Causal Anchor Retention ($M_2$) | $100.00\%$ (leaked) | $0.00\%$ | $100.00\%$ | $\Delta \ge +50.0\%$ |
| | Epistemic Leakage ($M_3$) | $180.0$ | $0.000$ | $0.000$ | $\equiv 0.0$ |
| | Physical Invariant Breaches ($M_4$) | $20$ | $8$ | $0$ | $\equiv 0$ |
| | Concurrency Race Collisions ($M_5$) | $240$ | $0$ | $0$ | $\equiv 0$ |
| | Cascade Completion Rate ($M_6$) | $0.00\%$ | $0.00\%$ | $100.00\%$ | $\ge 80.0\%$ |
| | Max Working Prompt Tokens ($M_7$) | $124$ | $880$ | $55$ | $\le 512$ |
| | Mean Turn Latency ($M_8$) | $0.48\text{ ms}$ | $0.50\text{ ms}$ | $0.51\text{ ms}$ | $< 1000\text{ ms}$ |
| | Token Compaction Ratio ($M_9$) | $0.0\%$ | $0.0\%$ | $91.73\%$ | $\ge 70.0\%$ |
| | Action Groundedness ($M_{10}$) | $100.0\%$ | $100.0\%$ | $100.0\%$ | $\equiv 100.0\%$ |
| **Tier B ($T=100$)** | Task Resolution Rate ($M_1$) | $0.00\%$ | $0.00\%$ | $100.00\%$ | $\ge 85.0\%$ |
| | Causal Anchor Retention ($M_2$) | $100.00\%$ (leaked) | $0.00\%$ | $100.00\%$ | $\Delta \ge +50.0\%$ |
| | Epistemic Leakage ($M_3$) | $180.0$ | $0.000$ | $0.000$ | $\equiv 0.0$ |
| | Physical Invariant Breaches ($M_4$) | $20$ | $8$ | $0$ | $\equiv 0$ |
| | Concurrency Race Collisions ($M_5$) | $240$ | $0$ | $0$ | $\equiv 0$ |
| | Cascade Completion Rate ($M_6$) | $0.00\%$ | $0.00\%$ | $100.00\%$ | $\ge 80.0\%$ |
| | Max Working Prompt Tokens ($M_7$) | $124$ | $1400$ | $55$ | $\le 512$ |
| | Mean Turn Latency ($M_8$) | $0.49\text{ ms}$ | $0.50\text{ ms}$ | $0.51\text{ ms}$ | $< 1000\text{ ms}$ |
| | Token Compaction Ratio ($M_9$) | $0.0\%$ | $0.0\%$ | $91.76\%$ | $\ge 70.0\%$ |
| | Action Groundedness ($M_{10}$) | $100.0\%$ | $100.0\%$ | $100.0\%$ | $\equiv 100.0\%$ |

---

## 5. Failure Taxonomy & Error Analysis

1. **Context Bloat & Attention Amnesia (Arm 2):**
   - By tick $45$, Arm 2 working context reached $880\text{ tokens}$, and by tick $85$ it reached $1400\text{ tokens}$, exceeding the $512$ token threshold. Unpruned gossip accumulation caused the true secret anchor to be drowned out by intermediate state noise and unanchored rumors, resulting in a $0.0\%$ resolution rate.
2. **Uncoordinated Race Conflicts & Decay Breaches (Arm 1):**
   - Without `MultiResourceArbiter`, concurrent attempts to interact with resources produced $240$ race collisions across the corpus. Uncoordinated maintenance led to $20$ physical boundary breaches where temperatures, pressures, and frequencies crossed safety thresholds.
3. **Information Leakage Invariance (Arm 1):**
   - Flat dumps unconditionally exposed private passwords and hidden internal properties, generating $180.0$ leakage penalty points ($3$ leakages per scenario $\times 60$ scenarios).

---

## 6. Threats to Validity

- **Internal Validity:** Track 1 uses deterministic agent workers to isolate system architecture effects from model sampling stochasticity. Realistic generation artifacts are evaluated in Track 2.
- **External Validity:** Scenarios are modeled as discrete state machines. Real-world systems may involve non-linear continuous physics and noisy communication channels.
- **Construct Validity:** Token counts in Track 1 use white-space approximation plus structural overhead; exact token counts with BPE tokenizers are audited in Track 2.

---

## 7. Clause-by-Clause Compliance Assessment

| Clause ID | Description | Frozen Acceptance Bound | Empirical Result (Tier A / Tier B) | Compliance Status |
| :---: | :--- | :---: | :---: | :---: |
| **M1** | Task Resolution Rate (Arm 3) | $\ge 85.0\%$ | $100.00\% / 100.00\%$ | PASS |
| **M2** | Causal Retention Delta ($\Delta R_{\text{causal}}$) | $\ge +50.0\%$ | $+100.00\% / +100.00\%$ | PASS |
| **M3** | Continuous Epistemic Leakage | $\equiv 0.0$ | $0.000 / 0.000$ | PASS |
| **M4** | Committed Physical Breaches | $\equiv 0$ | $0 / 0$ | PASS |
| **M5** | Committed Race Collisions | $\equiv 0$ | $0 / 0$ | PASS |
| **M6** | Cascade Completion Rate | $\ge 80.0\%$ | $100.00\% / 100.00\%$ | PASS |
| **M7** | Prompt Token Ceiling | $\le 512\text{ tokens}$ | $55\text{ tokens} / 55\text{ tokens}$ | PASS |
| **M8** | Mean Turn Latency SLA | $< 1000\text{ ms}$ | $0.51\text{ ms} / 0.51\text{ ms}$ | PASS |
| **M9** | Long-Horizon Compaction Ratio | $\ge 70.0\%$ | $91.73\% / 91.76\%$ | PASS |
| **M10** | Action Groundedness ($F_{\text{grounded}}$) | $\equiv 100.0\%$ | $100.00\% / 100.00\%$ | PASS |

**Final Track 1 Disposition Verdict: PASS**
