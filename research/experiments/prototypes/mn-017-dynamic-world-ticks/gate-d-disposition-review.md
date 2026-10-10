# MN-017 Gate D — Disposition & Directional Review

## Final Status

**Completed and Verified — Gate D Acceptance Criteria Met.**

```text
Final Milestone Disposition: host_authoritative_dynamic_ticks_hierarchical_planning_proven
Promotion to src/mong_nhiem/: QUARANTINED in research/experiments/prototypes/mn-017-dynamic-world-ticks/
Canonical Pre-Run Manifest: definition/pre-run-freeze-manifest.json
Canonical Post-Run Manifest: definition/post-run-freeze-manifest.json
Canonical Evidence:
  - Track 1 (Deterministic State Simulator):
      * Arm 1 (Flat Baseline): 0/40 PASS (0.0%), 118 horizon jumping failures
      * Arm 2 (Static Plan Control): 40/40 PASS (100.0%), 0 horizon jumping, 0 stale overwrites
      * Arm 3 (Dual-Engine MN-017): 40/40 PASS (100.0%), 0 horizon jumping, 0 stale overwrites, 0.1 ms latency
  - Track 2 (Primary Model Subject — Qwen3.5-2B-Q4_K_M on llama-server):
      * Overall Task Completion: 40/40 PASS (100.0%)
      * Domain A (Infrastructure Migration & Leases): 15/15 PASS (100.0%)
      * Domain B (Asset Logistics & Depletion): 15/15 PASS (100.0%)
      * Domain C (Concurrent System Registry): 10/10 PASS (100.0%)
      * Horizon Jumping Events: Exactly 0 (0.0%) [Down from 118 in Arm 1]
      * Premature Resolutions: Exactly 0 (0.0%) [Down from 40 in Arm 2 and 1 in Arm 1]
      * Unmanaged Stale Overwrites Committed: Exactly 0 (0.0%)
      * Stale Version Drifts Intercepted & Recovered: 31 events across multi-rate stress cases
      * Token Budget Ceiling: 100.0% turns <= 512 tokens (Max: 253.0, Mean: 137.8)
      * Mean Turn Latency: 534.4 ms (< 1000 ms SLA)
  - Prototype Test Suite: 13/13 PASSED (100.0%)
Canonical Report: reports/mn017_benchmark_report_mn017-run-20261010-095256-track2.md
```

This disposition is strictly bounded to the Primary Research Subject (`Qwen3.5-2B-Q4_K_M.gguf` on local `llama-server.exe` runtime) and the frozen 40-case dynamic world benchmark corpus (`definition/corpus-v1/cases.json`).

---

## 1. Empirical Evidence Summary

The canonical Gate C execution completed evaluations across 3 operational domains (40 dynamic cases, $K = 3-5$ sub-goals, $T = 15-35$ steps) comparing all three experimental arms on Track 2:

| Evaluation Dimension | Arm 1 (Flat Baseline) | Arm 2 (Static Plan Control) | Arm 3 (Dual-Engine MN-017) | Gate Contract Target | Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Overall Task Resolution Rate** | 0/40 (0.0%) | 0/40 (0.0%) | **40/40 (100.0%)** | $\ge 90.0\%$ | **PASS** |
| — *Domain A: Infrastructure Migration ($N=15$)* | 0/15 (0.0%) | 0/15 (0.0%) | **15/15 (100.0%)** | $\ge 90.0\%$ | **PASS** |
| — *Domain B: Asset Logistics ($N=15$)* | 0/15 (0.0%) | 0/15 (0.0%) | **15/15 (100.0%)** | $\ge 90.0\%$ | **PASS** |
| — *Domain C: System Registry & Failover ($N=10$)* | 0/10 (0.0%) | 0/10 (0.0%) | **10/10 (100.0%)** | $\ge 90.0\%$ | **PASS** |
| **Horizon Jumping Events** | 118 | 0 | **0** | Exactly 0 | **PASS** |
| **Premature Resolutions** | 1 | 40 | **0** | Exactly 0 | **PASS** |
| **Unmanaged Stale Overwrites Committed** | 0 | 0 | **0** | Exactly 0 | **PASS** |
| **Stale Interceptions (Delta Recovery)** | 0 | 0 | **31** | Host Handled | **PASS** |
| **Token Ceiling Violations ($>512$)** | 0/40 (0.0%) | 0/40 (0.0%) | **0/40 (0.0%)** | Exactly 0 | **PASS** |
| **Mean Prompt Tokens** | 161.8 | 116.1 | **137.8** | $\le 384.0$ | **PASS** |
| **Max Prompt Tokens** | 225 | 178 | **253** | $\le 512$ | **PASS** |
| **Mean Turn Latency** | 919.2 ms | 318.4 ms | **534.4 ms** | $< 1000.0\text{ ms}$ | **PASS** |

### Cross-Model Comparative Generalization

Following primary verification, the identical 40-case Track 2 benchmark was evaluated across the two secondary reference subjects before and after the Host dynamic affordance pruning patch:
- **`Llama-3.2-3B-Instruct-Q4_K_M`**: Advanced from 25/40 (62.5%) pre-patch to **35/40 (87.5%)** post-patch (Domain A: 10/15 [66.7%]; Domain B: 15/15 [100.0%]; Domain C: 10/10 [100.0%]; 294.6 ms latency).
- **`Qwen3-4B-Q4_K_M`**: Advanced from 13/40 (32.5%) pre-patch to **38/40 (95.0%)** post-patch (Domain A: 13/15 [86.7%]; Domain B: 15/15 [100.0%]; Domain C: 10/10 [100.0%]; 413.3 ms latency).

Detailed comparative distributions are recorded in [`reports/mn017_cross_model_comparison_report.md`](reports/mn017_cross_model_comparison_report.md).

---

## 2. Gate B Acceptance Rules Audit

In strict compliance with `gate-b-contract.md`:

1. **Rule 1 (Primary Efficacy Gate $\ge 90.0\%$, Delta $\ge +40.0\%$):** **PASS**  
   Achieved **100.0% ($40/40$)** on real model inference (`Qwen3.5-2B-Q4_K_M`), with a delta of **+100.0%** over Arm 1.
2. **Rule 2 (Zero Stale-State Overwrite Invariant $= 0$):** **PASS**  
   Exactly **0 unmanaged stale-state overwrites committed**. In multi-rate stress cases, Host Concurrency Guard intercepted all 31 version mismatches ($v_{agent} < v_{world}$), rejected illegal mutations, and emitted atomic delta notices, leading to 100% recovery.
3. **Rule 3 (Zero Horizon Jumping Invariant $= 0$):** **PASS**  
   Exactly **0 out-of-order action emissions** accepted or executed in Arm 3 (down from 118 events in Arm 1).
4. **Rule 4 (Strict Token Ceiling Invariant $\le 512$, Mean $\le 384$):** **PASS**  
   **100.0% compliance** across all turns. Peak prompt: **253 tokens**; Mean prompt: **137.8 tokens**.
5. **Rule 5 (Turn Latency SLA Invariant $< 1000\text{ ms}$):** **PASS**  
   Mean turn latency was **534.4 ms** on local `llama-server.exe` runtime, with Host processing overhead under $0.3\text{ ms}$.

---

## 3. Core Architectural Takeaways

1. **GBNF Phase-Gate Logit Masking Eliminates Premature Resolution and Horizon Jumping:**
   In Arm 2, despite presenting only the active sub-goal in natural language prompt text, unconstrained action grammars permitting `ACTION: RESOLVE COMPLETE` caused `Qwen3.5-2B` to emit completion on Turn 1 in 100% of cases ($40/40$ failures). Natural language prompts are insufficient to constrain small models. Compiling active sub-goal affordances into dynamic GBNF grammar masks illegal tokens out of the logit distribution at the decoding layer.
2. **Optimistic Concurrency Guard with Host Delta Notices Shields Against Asynchronous Drift:**
   Multi-rate world ticks ($\Delta t_{world} = 2-3$ per agent turn) cause environmental drift during agent reasoning. By stamping entity observations with monotonic versions ($v_{entity}$) and validating mutations prior to execution, the Host intercepts drift and provides targeted delta notices ($\le 64$ tokens). The small model successfully integrates delta notices and proceeds without mission failure.
3. **Topological Plan Graph Decoupling Maintains Strict Token Bounds:**
   Decomposing long-horizon missions into DAG sub-goals with Host-evaluated completion predicates allows the agent prompt to contain only the active sub-goal and immediate entity cards, keeping context size bounded ($137.8$ tokens mean, $253$ tokens peak) across extended multi-turn interactions.

---

## 4. Promotion Decision & Next Milestone Handoff

In accordance with Mộng Nhiễm core governance constraints:
- *"Do not silently promote experimental code into `src/mong_nhiem/`."*
- Prototype remains quarantined in `research/experiments/prototypes/mn-017-dynamic-world-ticks/`.
- All milestone artifacts, manifests, benchmark runs, and tests are verified and frozen.

### Successor Milestone Handoff:
- **MN-018 (Stateful Simulated Microworld Evolution / Full Cognitive Host Synthesis)**:
  - Unifies all empirically validated milestones:
    - MN-001/MN-002: Formal GBNF Grammar Constraints & Small Model Inference.
    - MN-003/MN-004: Host-Authoritative Verification & Fact Card State Representation.
    - MN-015: Graph Memory & Bidirectional Entity Relational Retrieval.
    - MN-016: Episodic Memory Consolidation & Autonomous Dream Cadence.
    - MN-017: Multi-Rate Dynamic World Ticks & Hierarchical Planning.
  - Final architectural consolidation and earned promotion review into `src/mong_nhiem/`.
