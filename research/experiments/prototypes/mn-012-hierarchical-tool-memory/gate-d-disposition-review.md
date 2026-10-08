# MN-012 Gate D — Disposition & Directional Pivoting Review

## Final Status

**Completed and closed — Quarantined Prototype / Directional Pivoting Gate Activated.**

```text
Final Milestone Disposition: pivoting_gate_activated_failure_mode_3
Promotion to src/mong_nhiem/: DENIED (Zero code promoted; strictly quarantined)
Canonical Manifest: definition/freeze-manifest.json (Commit 41a54c5)
Canonical Evidence:
  - Track 1 (Deterministic Simulator): runs/mn012-execution-run-0001/ (100.0% PASS)
  - Track 2 (Real Model Raw):         runs/mn012-execution-run-0002-qwen35/ (0.0%)
  - Track 2 (Real Model Ponytail):    runs/mn012-execution-run-0004-ponytail-resolve/ (6.7% PASS, 90.0% RESOLVED)
Canonical Report: reports/mn012-execution-report.md
```

This disposition is bounded to the Primary Research Subject (`Qwen3.5-2B-Q4_K_M.gguf` on local `llama.cpp` runtime) and the frozen MN-012 Gate B 60-case workload.

---

## 1. Empirical Evidence Summary

The canonical Gate C execution completed all 60 benchmark cases across 3 domains (Code AST Mutation, Stateful Resource Ledger, System Registry Configuration) under the frozen Dual-Track Protocol:

| Evaluation Track | Primary Subject | Task Accuracy (Arm B) | Hard Budget (<=512) | Action Grammar Validity | L2 Invariant Compliance | Host Latency Overhead | Gate B Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Track 1: Deterministic Simulator** | Rule-Guided Agent | **60/60 (100.0%)** | 100.0% (Max 316) | 100.0% (0 errors) | 100.0% (0 breaches) | < 0.15 ms/turn | **PASS** |
| **Track 2: Real Model (Zero-Shot)** | `Qwen3.5-2B` (Run 0002) | **0/60 (0.0%)** | 100.0% (Max 374) | 11.7% (53/60 collapsed) | 100.0% (0 breaches) | < 0.20 ms/turn | **FAIL** (Mode 1 & 2) |
| **Track 2: Real Model (Ponytail Scaffolding)** | `Qwen3.5-2B` (Run 0004) | **4/60 (6.7%)** | 88.3% (7 over budget) | **100.0%** (0 parse errors) | 100.0% (0 breaches) | < 0.20 ms/turn | **PIVOT** (Mode 3) |

---

## 2. Gate D Promotion Assessment

In strict accordance with Mộng Nhiễm core governance:
- *"Do not silently promote experimental code into `src/mong_nhiem/`."*
- *"Code may only be considered for promotion into `src/mong_nhiem/` after achieving 100% compliance across all 5 Gate B acceptance rules and passing formal Gate D disposition review."*

Because Track 2 real model execution achieved $6.7\%$ overall end-to-end task completion (failing Rule 1 threshold $\ge 85\%$), **promotion into `src/mong_nhiem/` is formally DENIED**.

All prototype implementations (`protocol.py`, `memory_store.py`, `circuit_breaker.py`, `coordinator.py`), test suites, corpus generators, and run artifacts remain strictly quarantined inside `research/experiments/prototypes/mn-012-hierarchical-tool-memory/`.

---

## 3. Scientific and Architectural Conclusions

1. **Host State Engine & Memory Partitioning Verified (Track 1):**
   Decoupling the ephemeral L1 prompt working set ($\le 512$ tokens) from the persistent L2 state store on disk/RAM completely resolves memory explosion. The Host State Store and Circuit Breaker successfully executed all 60 cases with 0 invariant breaches and sub-millisecond host overhead.
2. **Action Grammar Feasibility on Lightweight Models:**
   Under minimal Ponytail in-context grounding (3 concrete exemplars + prefilled `Directive: ACTION:`), `Qwen3.5-2B` achieved 100% valid protocol action emissions, eliminating format drift and successfully resolving 4 complex AST syntax error recovery cases (Cases 13–16).
3. **Identification of Cognitive Boundaries on Unassisted Models (<4B):**
   Across multi-step tasks, unassisted small models exhibit three fundamental limitations:
   - **Horizon Jumping (Premature Resolution):** Models leap directly to `ACTION: RESOLVE` on Turn 1 before executing necessary state mutations (`DISPATCH`).
   - **Value Truncation:** Emitting partial assignment tokens without full key-value bindings.
   - **Lack of Autonomous Error Recovery:** When actions are rejected by host invariants, the model lacks the ability to self-correct without host-managed backtracking.

---

## 4. Directional Pivoting Gate Activation

Under [`gate-b-contract.md`](gate-b-contract.md) Section 6:
> **Failure Mode 3: Goal Divergence (> 15% failure under Rule 1 despite valid tool syntax):**
> - *Diagnosis:* The model cannot synthesize multi-step causality without error recovery.
> - *Mandatory Pivot:* Advance immediately to MN-013 to introduce host-guided backtracking and action rejection feedback.

**Action:** MN-012 is formally closed as an immutable research milestone. The transition to **MN-013: Backtracking & Error Self-Correction** is officially authorized.
