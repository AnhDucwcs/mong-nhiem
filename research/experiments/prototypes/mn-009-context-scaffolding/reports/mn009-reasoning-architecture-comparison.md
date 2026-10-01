# MN-009 Downstream Reasoning Architecture Comparison Report

## Context & Navigation

- Canonical Research Base: [00-mong-nhiem](../../../../00-mong-nhiem.md)
- System Architecture: [architecture](../../../../concepts/architecture.md)
- Current Milestone State: [current-state](../../../../current-state.md)
- Parent Milestone Charter: [MN-009 Gate A Charter](../charter.md)
- Measurement Contract: [MN-009 Gate B Contract](../gate-b-contract.md)
- Gate C Packaging Report: [MN-009 Qwen 3.5 Execution Report](mn009-execution-report-qwen35.md)
- Canonical Evidence Run: `runs/mn009-comparison-run-20261001T144940Z/`

---

## 1. Executive Summary & Empirical Results

**Run ID:** `mn009-comparison-run-20261001T144940Z`  
**Model:** `Qwen3.5-2B-Q4_K_M.gguf` on `llama-server.exe` (Flash Attention ON, Port 18502)  
**Corpus:** 30 packed cases from MN-009 Gate C across 3 problem domains ($2\text{k}-32\text{k}$ raw scale).

| Architecture Arm | Configuration & Pipeline | Overall Accuracy | Mean Latency | Mean Tokens | Text Stream (10) | Graph/Table (10) | Code AST (10) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Arm 1: Direct Single-Call (Ponytail)** | Single-pass, CoT OFF (`max_tokens: 64`) | **100.0% (30/30)** | **471.7 ms** | **21.7 toks** | **10/10 (100%)** | **10/10 (100%)** | **10/10 (100%)** |
| **Arm 2: Monolithic CoT** | Single-pass, CoT ON (`max_tokens: 512`) | **0.0% (0/30)** | 5,953.7 ms | 512.0 toks | 0/10 (0%) | 0/10 (0%) | 0/10 (0%) |
| **Arm 3: 2-Milestone Pipeline** | M1 Decompose (CoT) $\rightarrow$ Host $\rightarrow$ M2 Synthesize | **33.3% (10/30)** | 3,417.1 ms | 265.2 toks | 0/10 (0%) | 0/10 (0%) | **10/10 (100%)** |

---

## 2. Core Scientific Findings

### 1. The Ponytail Theorem: Host Scaffolding Eliminates Model Complexity
- When **MN-009** compresses raw context down to $\le 512$ tokens using host-level deterministic logic (AST slicing, latest-state tabular projection, Anchor-and-Spoke causal ordering), the downstream extraction task becomes **trivial for a 2B parameter model**.
- **Arm 1 achieves a flawless 100% (30/30) accuracy** in **471 ms** (sub-second response) consuming only 21 tokens.
- No CoT, no reasoning loops, and no agentic decomposition are required when context is cleanly scaffolded.

### 2. The Small Model CoT Trap (Runaway Monologue Collapse)
- In **Arm 2**, enabling autonomous `<think>` on `Qwen3.5-2B` caused a catastrophic failure: in **100% of cases**, the model exhausted the entire 512-token completion budget inside an internal monologue loop without ever generating the closing `</think>` tag.
- As a consequence, generation latency ballooned by **$12.6\times$** (from 471 ms to 5,953 ms), while producing **0.0% usable answers**.
- Small models (<4B) cannot reliably terminate open-ended internal reasoning chains on short factual extraction tasks.

### 3. Pipeline Decomposition Hazard (Compound Formatting Drift)
- In **Arm 3**, introducing an intermediate milestone (M1 $\rightarrow$ Host $\rightarrow$ M2) increased latency by **$7.2\times$** (3,417 ms) and dropped accuracy from 100% down to 33.3%.
- While Arm 3 performed well on Code AST (10/10), it failed on Text Stream and Table domains because Milestone 2 suffered from prompt leakage (e.g. regurgitating header phrases like *"Operative Alex is located in the Verified State Card..."*) rather than emitting clean direct values.
- Multi-step prompting on small models compounds instructional drift.

---

## 3. Architectural Decision Implication

1. **Keep Downstream Inference Minimal (Single-Call CoT OFF):** For all scoped contexts delivered by MN-009, default to direct single-call greedy decoding (`enable_thinking: false`).
2. **Never Enable Autonomous CoT on Extraction Hot Paths:** Autonomous thinking is completely unnecessary and counterproductive when context is properly structured.
3. **Preserve Host Dominance:** Heavy lifting (state tracking, deduplication, BFS graph filtering, AST pruning) belongs 100% on the Host CPU ($< 4\text{ms}$), not inside multi-turn model agent loops.
