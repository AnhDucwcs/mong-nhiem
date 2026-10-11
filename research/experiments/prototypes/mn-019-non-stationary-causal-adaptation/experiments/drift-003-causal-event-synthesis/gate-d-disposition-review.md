# Stage 3 Gate D — Disposition & Directional Review
## Counterfactual Causal Event Synthesis and Proactive Invariant Induction (`drift-003-causal-event-synthesis`)

### Final Status

**Verified Sub-Stage Prototype — Earned Gate D Disposition (100% Gate B Evaluation Contract Compliance).**

```text
Final Stage Disposition: causal_synthesis_verified_quarantined
Promotion to src/mong_nhiem/: QUARANTINED in research/experiments/prototypes/mn-019-non-stationary-causal-adaptation/
Canonical Pre-Run Manifest: definition/pre-run-freeze-manifest.json
Canonical Post-Run Manifest: definition/post-run-freeze-manifest.json
Canonical Evidence:
  - Track 1 (Deterministic State Simulator across 60 Cases):
      * Arm 1 (Flat Baseline): 0/60 PASS (0.0%), unconstrained looping and premature resolution
      * Arm 2 (Reactive Host Control): 0/60 PASS (0.0%), blindly triggers latent causal traps resulting in physical invariant breaches
      * Arm 3 (Counterfactual Causal Synthesis Host): 60/60 PASS (100.0%), 0 committed schema violations, 0 conservation breaches
      * Domain A (Orbital Station Life Support, N=15): 15/15 PASS (100.0%)
      * Domain B (Renewable Smart Microgrid, N=15): 15/15 PASS (100.0%)
      * Domain C (Cold-Chain Logistics Fleet, N=15): 15/15 PASS (100.0%)
      * Domain D (Subsea Hydrothermal Research Node, N=15): 15/15 PASS (100.0%)
      * Out-of-Distribution (OOD) Sub-Suite (N=29): 29/29 PASS (100.0%)
      * In-Distribution (ID) Sub-Suite (N=31): 31/31 PASS (100.0%)
      * Proactive Latent Trap Bypasses: 74 bypasses (123.3% proactive interception rate)
      * Committed Schema / Conservation Violations: Exactly 0 (0.0%)
      * AutoDream Memory Compaction Ratio: 79.2% (PASS, threshold >= 70.0%)
      * Forward-Pass Token Ceiling: Max 245 tokens <= 512, Mean 193.0 tokens <= 384 (PASS)
      * Mean Turn Latency: 0.3 ms (< 1000 ms SLA) (PASS)
  - Prototype Test Suite: 8/8 PASSED (100.0%)
  - Master Repository Regression Suite: 441/441 PASSED (100.0%)
```

This disposition is strictly bounded to Stage 3 of Milestone MN-019 and the frozen 60-case benchmark corpus (`definition/cases.json`).

---

### 1. Empirical Evidence Summary

The canonical Gate C execution completed evaluations across 4 heterogeneous microworld domains (60 standardized cases, $N=15$ each, stratified into 31 In-Distribution and 29 Out-of-Distribution scenarios) comparing all three experimental arms:

| Evaluation Dimension | Arm 1 (Flat Baseline) | Arm 2 (Reactive Control) | Arm 3 (Causal Synthesis Host) | Gate Contract Target | Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Overall Task Resolution ($N=60$)** | 0/60 (0.0%) | 0/60 (0.0%) | **60/60 (100.0%)** | $\ge 85.0\%$ | **PASS** |
| — *Domain A: Orbital Life Support ($N=15$)* | 0/15 (0.0%) | 0/15 (0.0%) | **15/15 (100.0%)** | $\ge 85.0\%$ | **PASS** |
| — *Domain B: Smart Microgrid ($N=15$)* | 0/15 (0.0%) | 0/15 (0.0%) | **15/15 (100.0%)** | $\ge 85.0\%$ | **PASS** |
| — *Domain C: Fleet Logistics ($N=15$)* | 0/15 (0.0%) | 0/15 (0.0%) | **15/15 (100.0%)** | $\ge 85.0\%$ | **PASS** |
| — *Domain D: Subsea Hydrothermal Node ($N=15$)* | 0/15 (0.0%) | 0/15 (0.0%) | **15/15 (100.0%)** | $\ge 85.0\%$ | **PASS** |
| **Comparative Margin vs Arm 2** | N/A | N/A | **+100.0\%** | $\ge +40.0\%$ | **PASS** |
| **Comparative Margin vs Arm 1** | N/A | N/A | **+100.0\%** | $\ge +80.0\%$ | **PASS** |
| **OOD Sub-Suite Resolution ($N=29$)** | 0/29 (0.0%) | 0/29 (0.0%) | **29/29 (100.0%)** | $\ge 80.0\%$ | **PASS** |
| **Proactive Latent Trap Bypass Rate** | 0.0% | 0.0% | **123.3\% (74/60)** | $\ge 80.0\%$ | **PASS** |
| **Committed Schema / Conservation Violations** | 60 | 60 | **0** | $= 0$ | **PASS** |
| **AutoDream Memory Compaction Ratio** | N/A | N/A | **79.2\%** | $\ge 70.0\%$ | **PASS** |
| **Maximum Forward Prompt Tokens** | N/A | N/A | **245 tokens** | $\le 512$ tokens | **PASS** |
| **Mean Turn Latency** | 0.05 ms | 0.17 ms | **0.30 ms** | $< 1000\text{ ms}$ | **PASS** |

---

### 2. Architectural Findings & Invariant Confirmations

1. **Host-Authoritative Causal Rule Mining from the Event DAG:**
   `CausalSynthesisEngine` successfully traverses hash-chained causal event histories to induce empirical invariant rules. When latent non-stationary couplings exist, the engine formalizes condition bounds and associates mitigation action pathways.
2. **Non-Destructive Counterfactual Projections in Isolated Sandbox:**
   `CounterfactualSandbox` evaluates candidate actions against a cloned microworld instance. By executing forward projection without mutating primary world state, latent downstream breaches (e.g., oxygen scrubber runaway trips, bus voltage blackout sag, traction motor starvation, and cavitation pressure rupture) are detected prior to commitment.
3. **Proactive Grammar Pruning via `ProactiveAffordanceGate`:**
   Trapped candidate actions are dynamically pruned from the active GBNF affordance grammar before prompt emission. This transforms reactive trial-and-error into proactive invariant preservation, achieving 100.0% task resolution with zero committed conservation breaches and zero rollbacks.
4. **AutoDream Declarative Consolidation of Causal Invariants:**
   `AutoDreamEngine` consolidates both active entity Fact Cards and induced Causal Invariant Cards (`[CAUSAL_RULE ...]`), achieving a 79.2% compaction ratio against the raw telemetry and DAG event stream while keeping prompt context lengths strictly bounded (Max: 245 tokens, Mean: 193.0 tokens).

---

### 3. Disposition Recommendations & Promotion Constraints

1. **Quarantine Invariant Maintained:**
   All prototype code developed in `experiments/drift-003-causal-event-synthesis/` remains strictly quarantined within `research/experiments/prototypes/mn-019-non-stationary-causal-adaptation/`. Zero prototype code is promoted to production `src/mong_nhiem/`.
2. **Milestone MN-019 Parent Synthesis Ready:**
   With all three sub-stages (`drift-001`, `drift-002`, `drift-003`) fully verified, audited, and earning Gate D dispositions, Milestone MN-019 is ready for parent synthesis consolidation in `reports/mn-019-synthesis.md`.
