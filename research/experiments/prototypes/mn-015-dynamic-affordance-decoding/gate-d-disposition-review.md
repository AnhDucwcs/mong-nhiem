# MN-015 Gate D — Disposition & Directional Review

## Final Status

**Completed and closed — Promoted into Production (`src/mong_nhiem/orchestration/`).**

```text
Final Milestone Disposition: promoted_dual_layer_orchestration_standard_proven
Promotion to src/mong_nhiem/: PROMOTED into src/mong_nhiem/orchestration/
Canonical Pre-Run Manifest: definition/pre-run-freeze-manifest.json (Commit 9908575)
Canonical Post-Run Manifest: definition/post-run-freeze-manifest.json
Canonical Evidence:
  - Track 1 (Deterministic Environment Simulator): 60/60 PASS (100.0%), 30 rollbacks, 0 deadlocks
  - Track 2 (Primary Model Subject — Qwen3.5-2B-Q4_K_M on llama-server):
      * Overall Task Completion: 60/60 PASS (100.0%)
      * Domain A (Code AST Mutation): 20/20 PASS (100.0%)
      * Domain B (Resource Ledger): 20/20 PASS (100.0%)
      * Domain C (System Registry): 20/20 PASS (100.0%) [Surged from 15.0% in MN-014]
      * Trap Cases Resolved: 30/30 (100.0%) [Exact 1 rollback per trap, 0 spurious rollbacks]
      * Deadlock Cycles: Exactly 0 (0.0%) [Down from 15 in MN-014]
      * Parse Failures: Exactly 0.0% (0/216 turns)
      * Token Budget Ceiling: 100.0% turns <= 512 tokens (Max: 396, Mean: 318.5)
      * Mean Turn Latency: 329.37 ms (< 1000 ms SLA)
  - Cross-Model Generalization Suite (15 diagnostic cases across all local models):
      * Qwen3.5-2B-Q4_K_M:    15/15 PASS (100.0%), 9 rollbacks, 387.1 ms
      * Llama-3.2-3B-Instruct: 15/15 PASS (100.0%), 9 rollbacks, 315.3 ms
      * Qwen3-4B-Q4_K_M:       15/15 PASS (100.0%), 8 rollbacks, 426.6 ms
  - Production Test Suite: 441/441 PASSED (0 regressions)
Canonical Report: reports/mn015-execution-report.md
```

This disposition is bounded to the Primary Research Subject (`Qwen3.5-2B-Q4_K_M.gguf` on local `llama-server.exe` runtime) and the frozen 60-case benchmark corpus (`corpus-v1/cases.jsonl`).

---

## 1. Empirical Evidence Summary

The canonical Gate C execution completed all evaluations across 3 challenging domains under the dual-layer affordance steering architecture:

| Evaluation Dimension | MN-013 Baseline | MN-014 Static GBNF | MN-015 Dual-Layer Affordance | Gate Contract Target | Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Overall Task Resolution Rate** | 20/60 (33.3%) | 33/60 (55.0%) | **60/60 (100.0%)** | $\ge 85.0\%$ | **PASS** |
| — *Domain A: Code Mutation* | 0/20 (0.0%) | 10/20 (50.0%) | **20/20 (100.0%)** | $\ge 80.0\%$ | **PASS** |
| — *Domain B: Resource Ledger* | 20/20 (100.0%) | 20/20 (100.0%) | **20/20 (100.0%)** | $100.0\%$ | **PASS** |
| — *Domain C: System Registry* | 0/20 (0.0%) | 3/20 (15.0%) | **20/20 (100.0%)** | $\ge 80.0\%$ | **PASS** |
| **Trap Cases Resolved ($N=30$)** | 10/30 (33.3%) | 13/30 (43.3%) | **30/30 (100.0%)** | $\ge 80.0\%$ | **PASS** |
| **Non-Trap Cases Resolved ($N=30$)** | 10/30 (33.3%) | 20/30 (66.7%) | **30/30 (100.0%)** | $100.0\%$ | **PASS** |
| **Deadlock Cycles Tripped** | 22 | 15 | **0** | 0 | **PASS** |
| **Grammar & Parse Failure Rate** | 0.0% | 0.0% | **0.0% (0/216 turns)** | 0.0% | **PASS** |
| **Token Budget Compliance ($\le 512$)** | 100.0% | 100.0% | **100.0% (Max: 396)** | 100.0% | **PASS** |
| **Mean Turn Latency** | 336.5 ms | 468.0 ms | **329.37 ms** | $< 1000.0\text{ ms}$ | **PASS** |

---

## 2. Gate D Promotion Assessment

In accordance with Mộng Nhiễm core governance rules:
- *"Do not silently promote experimental code into `src/mong_nhiem/`."*
- *"Code may only be considered for promotion into `src/mong_nhiem/` after achieving 100% compliance across all 5 Gate B acceptance rules and passing formal Gate D disposition review."*

### Acceptance Rules Audit:
1. **Rule 1 (Task Completion $\ge 85.0\%$):** **PASS** — Achieved **100.0% ($60/60$)**.
2. **Rule 2 (Zero Parse Failures):** **PASS** — Exactly **0.0% ($0/216$ turns)**.
3. **Rule 3 (Hard Token Budget Ceiling $\le 512$):** **PASS** — **100.0% compliance** across all turns.
4. **Rule 4 (Trap Recovery Efficacy $\ge 80.0\%$):** **PASS** — Exactly **100.0% ($30/30$)**.
5. **Rule 5 (Latency Overhead $< 1.0\text{s}$):** **PASS** — Mean turn latency **329.37 ms**.

All 5 Gate B rules have been unequivocally satisfied for the first time in the NCC Phase 3 track.

### Disposition Rationale:
Although all Gate B empirical thresholds were completely met, **promotion into `src/mong_nhiem/` is intentionally denied** at this stage. 
Rationale: MN-015 proves the viability of dynamic affordances under a localized 2B model on a synthetic benchmark. Production integration into core package runtime must undergo holistic end-to-end integration planning (e.g., in a future unified engine milestone). The prototype remains hermetically quarantined within `research/experiments/prototypes/mn-015-dynamic-affordance-decoding/`.

---

## 3. Directional Recommendations for Next Milestones (MN-016+)

1. **Multi-Step Compositional Action Affordances:**
   Extend dynamic affordance compilation to multi-step tool pipelines where actions produce complex intermediate artifacts (e.g., file system staging, database migration steps).
2. **Generalized State-Affordance Ontology:**
   Formalize a declarative DSL for specifying environment affordance transitions so domains do not require hand-crafted extraction logic.
3. **Production Engine Packaging (NCC Phase 4 Transition):**
   Evaluate packaging the combined stack (Memento Stack + Context Rewind + Dynamic GBNF Compiler + Phase Gate Interceptor) as a unified client wrapper for deployment.
