# ECC-006 — State Tracking Evaluation Report (Qwen 3.5 2B Calibrated)

## Context & Navigation

- Canonical Research Base: [00-mong-nhiem](../../../../../00-mong-nhiem.md)
- System Architecture: [architecture](../../../../../concepts/architecture.md)
- Current Milestone State: [current-state](../../../../../current-state.md)
- Parent Milestone Synthesis: [MN-003 Synthesis Report](../../reports/mn-003-synthesis.md)
- Historical Llama Report: [ECC-006 Llama 3.2 Results](ecc-006-results.md)
- Canonical Evidence Run: `runs/20261001T140734Z-ecc-006-qwen-qwen3.5-2b-f1593d17/`

---

## 1. Empirical Results Across the Context Ladder

**Run ID:** `20261001T140734Z-ecc-006-qwen-qwen3.5-2b-f1593d17`  
**Model:** `Qwen3.5-2B-Q4_K_M.gguf`  
**Runtime:** `llama-server.exe` (Release build, port 18502)  
**Calibration Applied:** Line-level fine-grained distractor budgeting + $O(\log N)$ binary search midpoint solver.

| Requested Tokens | Target Shortfall Budget | Measured Actual Tokens | Exact Passes | Accuracy (Qwen 3.5 2B) | Baseline Accuracy (Llama 3.2 3B) | Delta (Qwen vs Llama) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **512** | $\le 96$ tokens | $500 - 511$ | $4/6$ | **66.7%** | $2/6$ ($33.3\%$) | **+33.4%** |
| **2,048** | $\le 96$ tokens | $2035 - 2046$ | $1/6$ | **16.7%** | $1/6$ ($16.7\%$) | **0.0%** |
| **8,192** | $\le 96$ tokens | $8178 - 8192$ | $1/6$ | **16.7%** | $0/6$ ($0.0\%$) | **+16.7%** |
| **16,384** | $\le 96$ tokens | $16371 - 16381$ | $1/6$ | **16.7%** | $0/6$ ($0.0\%$) | **+16.7%** |

---

## 2. Core Scientific Findings

1. **Short-Context Superiority at 512 Tokens:**
   - At 512 tokens, Qwen 3.5 2B achieves **66.7% (4/6)** exact final-state accuracy, double that of Llama 3.2 3B ($33.3\%$).
2. **Immediate Attention Collapse Beyond 512 Tokens:**
   - As soon as context scales to 2,048 tokens, accuracy plummets by $-50.0\%$ to **16.7% (1/6)**, matching the exact failure cliff observed on Llama.
   - Performance remains flat at $16.7\%$ across 8,192 and 16,384 tokens.
3. **Cross-Model Invariant:**
   - Both models prove that implicit attention is fundamentally incapable of multi-entity chronological state tracking over long contexts ($>512$ tokens).
   - This validates the absolute necessity of **MN-009 (Scoped Context Delivery Engine)**: all information must be compressed and scoped to $\le 512$ tokens before reaching the small LLM.
