# Academic Evaluation Report: Milestone MN-018
## Stateful Simulated Microworld Evolution (Stress Suite (T=150-200 ticks, K=8 subgoals))

**Date:** 2026-10-10 10:13:13 UTC  
**Track:** Track 2 (Real LLM Inference)  
**Corpus:** `corpus-v2-stress` (30 High-Difficulty Stress Scenarios)  
**Model Evaluated:** `Qwen3.5-2B`  
**Overall Verdict:** `PASS`  

---

### 1. Executive Summary

Milestone MN-018 evaluates the long-horizon governance capabilities (T = 150 - 200 steps, K = 8 subgoals) of lightweight language models coupled with the full Mộng Nhiễm Dual-Engine Cognitive Host across 30 microworld scenarios spanning Orbital Life Support, Smart Industrial Microgrid, and Multi-Hub Supply Chain.

- **Arm 3 (Dual-Engine Host):** **30/30 (100.0%)** success rate.
- **Arm 2 (Static Plan Control):** 0/30 (0.0%) success rate.
- **Arm 1 (Flat Baseline):** 0/30 (0.0%) success rate.
- **Comparative Margin (Delta Accuracy):** **+100.0%** (threshold $\ge +50.0\%$).
- **Physical Conservation Breaches:** **0** committed to world state (threshold $= 0$; **0** invariant breaches safely intercepted and rolled back by Memento).
- **Stale Version Overwrites:** **0** committed (threshold $= 0$).
- **Peak GPU VRAM Usage:** **1507.0 MiB** (1.47 GB / 4.00 GB, 36.8% capacity).
- **Maximum Prompt Tokens:** **503** (ceiling $\le 512$).
- **Mean Prompt Tokens:** **241.9** (budget $\le 384$).
- **Mean Turn Latency:** **708.8 ms** (SLA $< 1000\text{ ms}$).

---

### 2. Gate B Acceptance Contract Audit

| Clause | Description | Formal Bound | Empirical Result | Audit Verdict |
|---|---|:---:|:---:|:---:|
| **M1** | Task Completion Rate | $\ge 90.0\%$ | 100.0% (30/30) | `PASS` |
| **M2** | Comparative Margin | $\ge +50.0\%$ | +100.0% | `PASS` |
| **M3** | Conservation Law Violations | $= 0.0\%$ | 0 committed (0 rolled back) | `PASS` |
| **M4** | Stale Version Commit Rate | $= 0.0\%$ | 0 | `PASS` |
| **M5** | AutoDream Compression Ratio | $\ge 70.0\%$ | 71.0% | `PASS` |
| **M7** | Prompt Token Ceiling | $\le 512\text{ tok}$ | 503 tok | `PASS` |
| **M8** | Mean Prompt Budget | $\le 384\text{ tok}$ | 241.9 tok | `PASS` |
| **M9** | Turn Latency SLA | $< 1000\text{ ms}$ | 708.8 ms | `PASS` |
| **M10** | Host Processing Overhead | $< 10.0\text{ ms}$ | $< 0.5\text{ ms}$ | `PASS` |
| **M11** | Peak VRAM Footprint | $\le 3072\text{ MiB}$ (3.0 GB) | 1507.0 MiB (1.47 GB) | `PASS` |

---

### 3. Case-by-Case Performance Breakdown

| Case ID | Domain | Horizon $T$ | Arm 1 Status | Arm 2 Status | Arm 3 Status | Max Prompt | AutoDream Cycles |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `MN018-STRESS-CASE-001` | Orbital | 150 | `FAILED_INCOMPLETE` | `PREMATURE_RESOLUTION` | `SUCCESS` | 441 | 3 |
| `MN018-STRESS-CASE-002` | Orbital | 150 | `FAILED_INCOMPLETE` | `PREMATURE_RESOLUTION` | `SUCCESS` | 425 | 3 |
| `MN018-STRESS-CASE-003` | Orbital | 150 | `FAILED_INCOMPLETE` | `PREMATURE_RESOLUTION` | `SUCCESS` | 439 | 3 |
| `MN018-STRESS-CASE-004` | Orbital | 150 | `FAILED_INCOMPLETE` | `PREMATURE_RESOLUTION` | `SUCCESS` | 425 | 3 |
| `MN018-STRESS-CASE-005` | Orbital | 150 | `FAILED_INCOMPLETE` | `PREMATURE_RESOLUTION` | `SUCCESS` | 425 | 3 |
| `MN018-STRESS-CASE-006` | Orbital | 150 | `FAILED_INCOMPLETE` | `PREMATURE_RESOLUTION` | `SUCCESS` | 438 | 3 |
| `MN018-STRESS-CASE-007` | Orbital | 150 | `FAILED_INCOMPLETE` | `PREMATURE_RESOLUTION` | `SUCCESS` | 406 | 3 |
| `MN018-STRESS-CASE-008` | Orbital | 150 | `FAILED_INCOMPLETE` | `PREMATURE_RESOLUTION` | `SUCCESS` | 441 | 3 |
| `MN018-STRESS-CASE-009` | Orbital | 150 | `FAILED_INCOMPLETE` | `PREMATURE_RESOLUTION` | `SUCCESS` | 438 | 3 |
| `MN018-STRESS-CASE-010` | Orbital | 150 | `FAILED_INCOMPLETE` | `PREMATURE_RESOLUTION` | `SUCCESS` | 406 | 3 |
| `MN018-STRESS-CASE-011` | Microgrid | 150 | `FAILED_INCOMPLETE` | `FAILED_INCOMPLETE` | `SUCCESS` | 333 | 3 |
| `MN018-STRESS-CASE-012` | Microgrid | 150 | `FAILED_INCOMPLETE` | `FAILED_INCOMPLETE` | `SUCCESS` | 374 | 3 |
| `MN018-STRESS-CASE-013` | Microgrid | 150 | `FAILED_INCOMPLETE` | `FAILED_INCOMPLETE` | `SUCCESS` | 333 | 3 |
| `MN018-STRESS-CASE-014` | Microgrid | 150 | `FAILED_INCOMPLETE` | `FAILED_INCOMPLETE` | `SUCCESS` | 364 | 3 |
| `MN018-STRESS-CASE-015` | Microgrid | 150 | `FAILED_INCOMPLETE` | `FAILED_INCOMPLETE` | `SUCCESS` | 333 | 3 |
| `MN018-STRESS-CASE-016` | Microgrid | 150 | `FAILED_INCOMPLETE` | `FAILED_INCOMPLETE` | `SUCCESS` | 374 | 3 |
| `MN018-STRESS-CASE-017` | Microgrid | 150 | `FAILED_INCOMPLETE` | `FAILED_INCOMPLETE` | `SUCCESS` | 374 | 3 |
| `MN018-STRESS-CASE-018` | Microgrid | 150 | `FAILED_INCOMPLETE` | `FAILED_INCOMPLETE` | `SUCCESS` | 333 | 3 |
| `MN018-STRESS-CASE-019` | Microgrid | 150 | `FAILED_INCOMPLETE` | `FAILED_INCOMPLETE` | `SUCCESS` | 364 | 3 |
| `MN018-STRESS-CASE-020` | Microgrid | 150 | `FAILED_INCOMPLETE` | `FAILED_INCOMPLETE` | `SUCCESS` | 333 | 3 |
| `MN018-STRESS-CASE-021` | Supply Chain | 150 | `FAILED_INCOMPLETE` | `PREMATURE_RESOLUTION` | `SUCCESS` | 382 | 2 |
| `MN018-STRESS-CASE-022` | Supply Chain | 150 | `FAILED_INCOMPLETE` | `PREMATURE_RESOLUTION` | `SUCCESS` | 382 | 2 |
| `MN018-STRESS-CASE-023` | Supply Chain | 150 | `FAILED_INCOMPLETE` | `PREMATURE_RESOLUTION` | `SUCCESS` | 382 | 2 |
| `MN018-STRESS-CASE-024` | Supply Chain | 150 | `FAILED_INCOMPLETE` | `PREMATURE_RESOLUTION` | `SUCCESS` | 382 | 2 |
| `MN018-STRESS-CASE-025` | Supply Chain | 150 | `FAILED_INCOMPLETE` | `PREMATURE_RESOLUTION` | `SUCCESS` | 382 | 2 |
| `MN018-STRESS-CASE-026` | Supply Chain | 150 | `FAILED_INCOMPLETE` | `PREMATURE_RESOLUTION` | `SUCCESS` | 503 | 2 |
| `MN018-STRESS-CASE-027` | Supply Chain | 150 | `FAILED_INCOMPLETE` | `PREMATURE_RESOLUTION` | `SUCCESS` | 382 | 2 |
| `MN018-STRESS-CASE-028` | Supply Chain | 150 | `FAILED_INCOMPLETE` | `PREMATURE_RESOLUTION` | `SUCCESS` | 382 | 2 |
| `MN018-STRESS-CASE-029` | Supply Chain | 150 | `FAILED_INCOMPLETE` | `PREMATURE_RESOLUTION` | `SUCCESS` | 341 | 2 |
| `MN018-STRESS-CASE-030` | Supply Chain | 150 | `FAILED_INCOMPLETE` | `PREMATURE_RESOLUTION` | `SUCCESS` | 382 | 2 |

---

### 4. Threats to Validity

- **Internal Validity:** The host state machine and physics equations operate deterministically on discrete integer ticks. Floating point roundoffs in energy equations are bounded by a 1.0 kW epsilon guard.
- **External Validity:** The benchmark evaluates 3 diverse multi-entity domains. While synthetic, their coupled differential invariants closely mirror industrial SCADA and orbital life support architectures.
- **Construct Validity:** Task completion requires satisfying 100% of sub-goals without any physical invariant violations, verified by Host symbolic predicates.
