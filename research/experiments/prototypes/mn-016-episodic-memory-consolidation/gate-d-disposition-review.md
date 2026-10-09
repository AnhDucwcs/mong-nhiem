# MN-016 Gate D — Disposition & Directional Review

## Final Status

**Completed and Verified — Gate D Acceptance Criteria Met.**

```text
Final Milestone Disposition: host_authoritative_autodream_empirically_proven
Promotion to src/mong_nhiem/: QUARANTINED in research/experiments/prototypes/mn-016-episodic-memory-consolidation/
Canonical Pre-Run Manifest: definition/pre-run-freeze-manifest.json
Canonical Post-Run Manifest: definition/post-run-freeze-manifest.json
Canonical Evidence:
  - Track 1 (Deterministic State Simulator): 
      * Arm 1 (FIFO Baseline): 0/40 PASS (0.0%), 40 amnesia failures
      * Arm 2 (Cadence-Only Control): 25/40 PASS (62.5%), 15 token ceiling violations
      * Arm 3 (Dual-Trigger MN-016): 40/40 PASS (100.0%), 0 amnesia, 0 violations, 0.1 ms latency
  - Track 2 (Primary Model Subject — Qwen3.5-2B-Q4_K_M on llama-server):
      * Overall Task Completion: 40/40 PASS (100.0%)
      * Domain A (Code Refactoring): 15/15 PASS (100.0%)
      * Domain B (Asset Ledger & Audit): 15/15 PASS (100.0%)
      * Domain C (System Registry & Leases): 10/10 PASS (100.0%)
      * Amnesia Failures: Exactly 0 (0.0%) [Down from 40 in Arm 1]
      * Token Budget Ceiling: 100.0% turns <= 512 tokens (Max: 334, Mean: 111.0)
      * Mean Turn Latency: 64.9 ms (< 1000 ms SLA)
      * Memory Contradictions: Exactly 0 (0.0%)
  - Production Test Suite: 14/14 PASSED (100.0%)
Canonical Report: reports/mn016_benchmark_report_mn016-run-20261009-210120-track2.md
```

This disposition is strictly bounded to the Primary Research Subject (`Qwen3.5-2B-Q4_K_M.gguf` on local `llama-server.exe` runtime) and the frozen 40-case long-horizon benchmark corpus (`definition/corpus-v1/cases.json`).

---

## 1. Empirical Evidence Summary

The canonical Gate C execution completed evaluations across 3 operational domains (40 long-horizon cases, $T = 20-50$ steps) comparing all three experimental arms on Track 2:

| Evaluation Dimension | Arm 1 (FIFO Baseline) | Arm 2 (Cadence-Only Control) | Arm 3 (Dual-Trigger MN-016) | Gate Contract Target | Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Overall Task Resolution Rate** | 0/40 (0.0%) | 25/40 (62.5%) | **40/40 (100.0%)** | $\ge 90.0\%$ | **PASS** |
| — *Domain A: Code Refactoring ($N=15$)* | 0/15 (0.0%) | 0/15 (0.0%) | **15/15 (100.0%)** | $\ge 90.0\%$ | **PASS** |
| — *Domain B: Asset Ledger & Audit ($N=15$)* | 0/15 (0.0%) | 15/15 (100.0%) | **15/15 (100.0%)** | $\ge 90.0\%$ | **PASS** |
| — *Domain C: System Registry ($N=10$)* | 0/10 (0.0%) | 10/10 (100.0%) | **10/10 (100.0%)** | $\ge 90.0\%$ | **PASS** |
| **Historical Amnesia Failures** | 40/40 (100.0%) | 0/40 (0.0%) | **0/40 (0.0%)** | 0 | **PASS** |
| **Token Ceiling Violations ($>512$)** | 0/40 (0.0%) | 15/40 (37.5%) | **0/40 (0.0%)** | 0 | **PASS** |
| **Mean Prompt Tokens** | 51.0 | 137.5 | **111.0** | $\le 384.0$ | **PASS** |
| **Max Prompt Tokens** | 69 | 514 | **334** | $\le 512$ | **PASS** |
| **Mean Turn Latency** | 0.0 ms | 0.0 ms | **64.9 ms** | $< 1000.0\text{ ms}$ | **PASS** |
| **Memory Contradiction Rate** | N/A | 0.0% | **0.0% (0 contradictions)** | 0.0% | **PASS** |

---

## 2. Gate B Acceptance Rules Audit

In strict compliance with `gate-b-contract.md`:

1. **Rule 1 (Primary Efficacy Gate $\ge 90.0\%$):** **PASS**  
   Achieved **100.0% ($40/40$)** on real model inference (`Qwen3.5-2B-Q4_K_M`).
2. **Rule 2 (Amnesia Remediation Delta $\ge +50.0\%$):** **PASS**  
   Measured delta $\Delta(\text{Arm 3} - \text{Arm 1}) = \mathbf{+100.0\%}$ ($+40/40$ cases).
3. **Rule 3 (Strict Token Ceiling Invariant $\le 512$, Mean $\le 384$):** **PASS**  
   **100.0% compliance** across all turns. Peak prompt: **334 tokens**; Mean: **111.0 tokens**.
4. **Rule 4 (Latency SLA Invariant $< 1000\text{ ms}$):** **PASS**  
   Mean turn latency was **64.9 ms** on local GPU runtime.
5. **Rule 5 (Memory Contradiction Suppression $= 0.0\%$):** **PASS**  
   Exactly **0 contradictions** detected across all persisted entity cards.

---

## 3. Core Architectural Takeaways

1. **Host Authority Eliminates Sub-4B Hallucination Risk:**
   Claude Code delegates dream summarization to an LLM subagent writing free-form Markdown. For SLMs ($<4\text{B}$), ungrounded generation hallucinates facts. In Mộng Nhiễm, the Host derives all facts directly from authoritative tool execution outputs, hashes them with SHA-256, and replays state deterministically.
2. **Autonomous Gating Replaces Human Time:**
   Wall-clock time ($24\text{h}$) is meaningless in autonomous simulation. Replacing it with discrete machine ticks ($\Delta T \ge 25$) and state mutation flux ($M \ge 10$) creates clean, deterministic cadences.
3. **Emergency Context Pressure Interceptor is Mandatory:**
   Arm 2 proved that cadence gates alone leave the model vulnerable to context overflow during burst mutations ($15/40$ violations). Arm 3's Emergency Pressure Interceptor ($\ge 400$ tokens) flushes buffers dynamically, keeping peak tokens at 334.

---

## 4. Promotion Decision & Next Milestone Handoff

In accordance with Mộng Nhiễm core rules:
- *"Do not silently promote experimental code into `src/mong_nhiem/`."*
- Code remains quarantined in `research/experiments/prototypes/mn-016-episodic-memory-consolidation/`.
- All milestone artifacts, manifests, benchmark runs, and tests are verified and frozen.

### Successor Milestone Handoff (MN-017):
- **MN-017 (Dynamic World Ticks & Hierarchical Planning)**:
  - Builds directly on MN-016's episodic memory store and consolidation engine.
  - Integrates multi-rate simulation clocks and hierarchical task decomposition over long horizons.
