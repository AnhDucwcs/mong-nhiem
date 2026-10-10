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

### Table 1: End-to-End Comparative Performance Across Models (Arm 3)

| Model Subject | Model Size | Overall Success Rate | Domain A (Infrastructure) | Domain B (Logistics) | Domain C (Registry) | Stale Overwrites Committed | Mean Latency | Mean Prompt Tokens | Gate B Disposition |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **`Qwen3.5-2B-Q4_K_M`** | **1.40 GB** | **100.0% (40/40)** | **15/15 (100.0%)** | **15/15 (100.0%)** | **10/10 (100.0%)** | **0** | 534.4 ms | 137.8 tok | **VERIFIED_PASS** |
| **`Llama-3.2-3B-Instruct`** | 2.02 GB | **62.5% (25/40)** | 0/15 (0.0%) | **15/15 (100.0%)** | **10/10 (100.0%)** | **0** | 339.4 ms | 122.7 tok | FAIL |
| **`Qwen3-4B-Q4_K_M`** | 2.50 GB | **32.5% (13/40)** | 13/15 (86.7%) | 0/15 (0.0%) | 0/10 (0.0%) | **0** | 445.3 ms | 136.3 tok | FAIL |

---

## 2. Comparative Analysis Across Evaluation Arms

### Table 2: Arm-by-Arm Task Resolution Across Models

| Evaluation Arm | Metric | `Qwen3.5-2B` | `Llama-3.2-3B` | `Qwen3-4B` | Target Requirement |
|---|---|:---:|:---:|:---:|:---:|
| **Arm 1 (Flat Baseline)** | Task Resolution Rate | 0.0% (0/40) | 0.0% (0/40) | 0.0% (0/40) | Compatibility Floor |
| | Horizon Jumping Events | 118 | 0 | 22 | — |
| | Premature Resolutions | 1 | 40 | 36 | — |
| **Arm 2 (Static Plan Control)** | Task Resolution Rate | 0.0% (0/40) | 0.0% (0/40) | 0.0% (0/40) | Control Floor |
| | Premature Resolutions | 40 | 40 | 40 | Zero unmasked resolves |
| **Arm 3 (Dual-Engine MN-017)** | Task Resolution Rate | **100.0% (40/40)** | **62.5% (25/40)** | **32.5% (13/40)** | $\ge 90.0\%$ |
| | Premature Resolutions | **0** | **0** | **0** | Exactly 0 |
| | Horizon Jumping Events | **0** | **0** | **0** | Exactly 0 |
| | Stale Overwrites Committed | **0** | **0** | **0** | Exactly 0 |
| | Stale Interceptions Handled | **31** | **0** | **45** | Host Managed |

---

## 3. Deep Failure Taxonomy & Diagnostic Analysis

### 1. Universal Protection of Phase-Gate Logit Masking (Arms 1 & 2 vs Arm 3)
Across all three models, **Arm 1 and Arm 2 scored 0.0% (0/40)**.
- In Arm 1 (Flat global prompt), models collapsed due to premature resolution claims and horizon jumping to terminal actions.
- In Arm 2 (Sub-goal text prompt without GBNF masking), **100% of cases across all three models (40/40 in Qwen 3.5, 40/40 in Llama 3.2, 40/40 in Qwen 4B)** failed on Turn 1 due to the model emitting `ACTION: RESOLVE COMPLETE`.
- This confirms universally across model architectures that natural language instructions alone cannot prevent small models from emitting termination actions when unconstrained logit spaces permit them. In Arm 3, GBNF phase-gate logit masking completely eliminated 100% of premature resolutions (0 events across all models).

### 2. The Idempotent Recall Absorption Loop (Llama 3.2 & Qwen 4B Failure Mode)
The performance divergence in Arm 3 between `Qwen3.5-2B` (100.0%), `Llama-3.2-3B` (62.5%), and `Qwen3-4B` (32.5%) originates from grammar branch preference during greedy decoding:
- When a target entity is unobserved, the grammar affords both `ACTION: RECALL <entity>` and `ACTION: DISPATCH <action>`.
- `Qwen3.5-2B` correctly exhibits semantic progression: once the entity fact card is in working memory, it transitions to `ACTION: DISPATCH`.
- `Llama-3.2-3B` in Domain A and `Qwen3-4B` in Domains B and C entered an **idempotent recall absorption loop**, repeating `ACTION: RECALL <entity>` continuously until reaching the hard 35-turn cap.
- Because `action_type == "RECALL"` was exempt from the 3-turn identical unprogressed action circuit breaker, the Host permitted these repeated recalls rather than tripping a break.
- Notably, where this loop did not trigger, both secondary models demonstrated strong competence:
  - `Llama-3.2-3B` achieved **100.0% (25/25)** on Domain B and Domain C.
  - `Qwen3-4B` achieved **86.7% (13/15)** on Domain A.

---

## 4. Latency and Token Ceiling Invariant Audit

All three models strictly satisfied the hardware and operational constraints of the Gate B contract:

1. **Token Budget Ceiling ($\le 512$ tokens)**:
   - `Qwen3.5-2B`: Max prompt 253 tokens, Mean prompt 137.8 tokens.
   - `Llama-3.2-3B`: Max prompt 179 tokens, Mean prompt 122.7 tokens.
   - `Qwen3-4B`: Max prompt 244 tokens, Mean prompt 136.3 tokens.
   - Zero forward passes exceeded 512 tokens on any model (100.0% compliance).

2. **Turn Latency SLA ($< 1000\text{ ms}$)**:
   - `Llama-3.2-3B`: 339.4 ms mean turn latency.
   - `Qwen3-4B`: 445.3 ms mean turn latency.
   - `Qwen3.5-2B`: 534.4 ms mean turn latency.
   - All models executed well within the 1000 ms SLA on local single-GPU inference.

---

## 5. Architectural Conclusions & Subject Designation

1. **Reaffirmation of `Qwen3.5-2B-Q4_K_M` as Primary Research Subject**:
   `Qwen3.5-2B` is the sole evaluated model achieving **100.0% end-to-end task completion** across all operational domains without succumbing to grammar branch trapping, while requiring the smallest parameter footprint (1.40 GB vs 2.02 GB and 2.50 GB).
2. **Host Dynamic Affordance Hardening for MN-Final**:
   In MN-Final, the Host affordance compiler will dynamically prune `ACTION: RECALL <entity>` once `<entity>` is already active in working memory, mathematically precluding secondary models from entering idempotent recall absorption loops.
