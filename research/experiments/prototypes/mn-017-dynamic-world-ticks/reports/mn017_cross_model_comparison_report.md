# Cross-Model Comparative Benchmark Report — Milestone MN-017: Dynamic World Ticks & Hierarchical Planning

**Evaluation Date**: 2026-10-10  
**Evaluation Track**: Track 2 (Real Model Inference on Local `llama-server.exe`, $T = 0.0$, Context Size = 2048)  
**Evaluated Subjects**:
1. `Qwen3.5-2B-Q4_K_M.gguf` (1.40 GB, Primary Research Subject)
2. `Llama-3.2-3B-Instruct-Q4_K_M.gguf` (2.02 GB, Secondary Reference Subject)
3. `Qwen3-4B-Q4_K_M.gguf` (2.50 GB, Secondary Reference Subject)

---

## 1. Executive Summary & Comparative Headline Metrics

This report evaluates cross-model generalization for Milestone **MN-017** across all three locally qualified open-weights models in Mộng Nhiễm. The benchmark executes 40 dynamic cases ($K = 3-5$ DAG sub-goals, $T = 15-35$ turns, multi-rate ticks $\Delta t_{world} = 1-3$) across 3 operational domains under matched 3-arm protocol.

Following initial baseline runs, an architectural root-cause patch was applied:
1. **Host-Side Dynamic Grammar Pruning**: The dynamic GBNF compiler prunes `ACTION: RECALL <entity>` affordances for entities already active in working memory context, eliminating degenerate state transitions ($S \rightarrow S$).
2. **Delta Notice Observation Synchronization**: Working memory entity cards and Host observation versions are synchronously updated upon presenting concurrency delta notices, precluding continuous background telemetry decay lockouts.
3. **Uniform Circuit Breaker**: Standardized 3-turn identical unprogressed action circuit breaker protection restored uniformly across all action types.

### Table 1: Pre-Patch vs Post-Patch Cross-Model Performance (Arm 3)

| Model Subject | Model Size | Pre-Patch Success | Post-Patch Success | Delta Accuracy | Domain A (Infr) | Domain B (Logist) | Domain C (Reg) | Stale Overwrites | Gate B Verdict |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **`Qwen3.5-2B-Q4_K_M`** | **1.40 GB** | 100.0% (40/40) | **100.0% (40/40)** | +0.0% | **15/15 (100.0%)** | **15/15 (100.0%)** | **10/10 (100.0%)** | **0** | **PASS** |
| **`Llama-3.2-3B-Instruct`** | 2.02 GB | 62.5% (25/40) | **87.5% (35/40)** | **+25.0%** | 10/15 (66.7%) | **15/15 (100.0%)** | **10/10 (100.0%)** | **0** | **NEAR_PASS** |
| **`Qwen3-4B-Q4_K_M`** | 2.50 GB | 32.5% (13/40) | **95.0% (38/40)** | **+62.5%** | 13/15 (86.7%) | **15/15 (100.0%)** | **10/10 (100.0%)** | **0** | **PASS** |
| **Cross-Model Mean** | — | 65.0% (26/40) | **94.2% (37.7/40)**| **+29.2%** | 12.7/15 (84.4%) | 15/15 (100.0%) | 10/10 (100.0%) | **0** | — |

---

## 2. Comparative Analysis Across Evaluation Arms

### Table 2: Post-Patch Arm-by-Arm Task Resolution Across Models

| Evaluation Arm | Metric | `Qwen3.5-2B` | `Llama-3.2-3B` | `Qwen3-4B` | Contract Floor |
|---|---|:---:|:---:|:---:|:---:|
| **Arm 1 (Flat Baseline)** | Task Resolution Rate | 0.0% (0/40) | 0.0% (0/40) | 0.0% (0/40) | Control Floor |
| | Horizon Jumping Events | 118 | 0 | 22 | — |
| | Premature Resolutions | 1 | 40 | 36 | — |
| **Arm 2 (Static Plan Control)** | Task Resolution Rate | 0.0% (0/40) | 0.0% (0/40) | 0.0% (0/40) | Control Floor |
| | Premature Resolutions | 40 | 40 | 40 | 0 allowed |
| **Arm 3 (Dual-Engine MN-017)** | Task Resolution Rate | **100.0% (40/40)** | **87.5% (35/40)** | **95.0% (38/40)** | $\ge 90.0\%$ |
| | Premature Resolutions | **0** | **0** | **0** | Exactly 0 |
| | Horizon Jumping Events | **0** | **0** | **0** | Exactly 0 |
| | Stale Overwrites Committed | **0** | **0** | **0** | Exactly 0 |
| | Stale Interceptions Handled | **35** | **21** | **48** | Host Handled |

---

## 3. Deep Failure Taxonomy & Diagnostic Analysis

### 1. Universal Necessity of Dynamic GBNF Masking (Arms 1 & 2 vs Arm 3)
Across all three models, **Arm 1 and Arm 2 scored 0.0% (0/40)**.
- In Arm 1 (Flat global prompt), models suffered severe Goal Divergence, Horizon Jumping to terminal sub-goals, and premature resolutions.
- In Arm 2 (Active sub-goal text prompt without GBNF logit masking), **100% of cases across all three models (40/40 in Qwen 3.5, 40/40 in Llama 3.2, 40/40 in Qwen 4B)** failed on Turn 1 due to the model emitting `ACTION: RESOLVE COMPLETE`.
- This confirms universally across model architectures that natural language instructions alone cannot constrain small models when unmasked logit spaces afford premature exits. In Arm 3, Host logit masking eliminated 100% of premature resolutions and horizon jumps.

### 2. Elimination of the Idempotent Recall Absorption Loop
Prior to the patch, secondary models entered infinite loops emitting `ACTION: RECALL <entity>` repeatedly:
- `Llama-3.2-3B` collapsed in Domain A (0/15 PASS), repeating `ACTION: RECALL res_1`.
- `Qwen3-4B` collapsed in Domain B and Domain C (0/25 PASS), repeating recalls despite cards already residing in context.
- Following dynamic grammar pruning (omitting recalled entities from subsequent grammar compiles), both models immediately progressed:
  - `Qwen3-4B` advanced from 0/25 to **25/25 (100.0%)** across Domains B and C, lifting overall accuracy from 32.5% to **95.0%**.
  - `Llama-3.2-3B` advanced from 0/15 to **10/15 (66.7%)** in Domain A, lifting overall accuracy from 62.5% to **87.5%**.

### 3. Residual Failure Analysis (Cases 11-15 in Llama 3.2 and Cases 11, 13 in Qwen 4B)
All residual failures occurred strictly within multi-rate stress cases in Domain A (Infrastructure Migration with $\Delta t_{world} = 2$ and tight lease TTLs):
- `Llama-3.2-3B` expended 4-6 preparatory turns on resource inspection and payload staging. Because ticks advanced at 2 ticks/turn, the lease TTL expired prior to lease renewal execution.
- Crucially, when the expired lease was targeted, the Host Concurrency Guard intercepted the action (`ENTITY_EXPIRED`), preventing state corruption (`stale_violations = 0`). The Host circuit breaker tripped cleanly on Turn 8, preserving state integrity.

---

## 4. Latency and Token Ceiling Invariant Audit

All three models adhered strictly to Gate B budget invariants under post-patch execution:

1. **Token Budget Ceiling ($\le 512$ tokens)**:
   - `Qwen3.5-2B`: Mean prompt 149.9 tokens, Max prompt 271.0 tokens (Ceiling Margin: 47.1%).
   - `Llama-3.2-3B`: Mean prompt 116.9 tokens, Max prompt 226.0 tokens (Ceiling Margin: 55.9%).
   - `Qwen3-4B`: Mean prompt 148.3 tokens, Max prompt 269.0 tokens (Ceiling Margin: 47.5%).
   - Zero token ceiling violations across all runs (100.0% compliance).

2. **Turn Latency SLA ($< 1000\text{ ms}$)**:
   - `Llama-3.2-3B`: 294.6 ms mean turn latency.
   - `Qwen3-4B`: 413.3 ms mean turn latency.
   - `Qwen3.5-2B`: 502.8 ms mean turn latency.
   - Mean latency comfortably satisfies the sub-second interactive deployment threshold across all model architectures.

---

## 5. Architectural Conclusions & Subject Designation

1. **Reaffirmation of `Qwen3.5-2B-Q4_K_M` as Primary Subject**:
   `Qwen3.5-2B` remains the premier subject for Mộng Nhiễm, achieving **100.0% (40/40)** task completion across all domains with the smallest memory footprint (1.40 GB).
2. **Empirical Validation of Dual-Engine Generalization**:
   The architectural patch was entirely Host-side (pruning degenerate affordances and synchronizing observation versions on delta notices). It required **zero prompt modifications, zero model fine-tuning, and zero model-specific hacks**.
   This proves the fundamental thesis of Mộng Nhiễm: **structural host constraints generalize across disparate small-model families**, elevating weak or idiosyncratic small models into highly reliable execution agents.
