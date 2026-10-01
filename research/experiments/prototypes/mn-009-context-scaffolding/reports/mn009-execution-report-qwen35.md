# MN-009 Gate C: Scoped Context Delivery Engine Execution Report

## Context & Navigation

- Canonical Research Base: [00-mong-nhiem](../../../../00-mong-nhiem.md)
- System Architecture: [architecture](../../../../concepts/architecture.md)
- Current Milestone State: [current-state](../../../../current-state.md)
- Parent Milestone Charter: [MN-009 Gate A Charter](../charter.md)
- Measurement Contract: [MN-009 Gate B Contract](../gate-b-contract.md)
- Gate D Disposition Review: [MN-009 Gate D Disposition Review](../gate-d-disposition-review.md)
- Canonical Evidence Run: `runs/mn009-execution-run-0002-qwen35/`

**Run ID:** `mn009-execution-run-0002-qwen35`  
**Timestamp:** `2026-10-01T13:41:14.871162+00:00`  
**Evaluated Tokenizer:** `D:\Materials\llama.cpp\build\bin\Release\llama-tokenize.exe`  
**Model Weights:** `Qwen3.5-2B-Q4_K_M.gguf`  

---

## 1. Acceptance Verification across 5 Frozen Rules

| Support Rule | Target Threshold | Measured Empirical Result | Status |
| :--- | :--- | :--- | :---: |
| **Rule 1: Hard Token Ceiling** | $\le 512$ tokens ($100\%$ of cases) | Max: **490**, Mean: **236.5** | **PASS** |
| **Rule 2: Boundary & AST Integrity** | $100\%$ valid syntax & natural boundaries | Pass rate: **30/30** ($100\%$) | **PASS** |
| **Rule 3: Salience Recall** | $\ge 28/30$ cases ($93.3\%$) | Recall rate: **30/30 (100.0%)** | **PASS** |
| **Rule 4: CPU Latency Gate** | Mean $< 15.0\text{ ms}$, Max $< 35.0\text{ ms}$ | Mean: **3.77 ms**, Max: **17.73 ms** | **PASS** |
| **Rule 5: Prefix Cache Invariant** | $100\%$ identical prefix header | Cache Hit Rate: **100%** | **PASS** |

---

## 2. Empirical Performance by Problem Domain

| Domain | Case Count | Raw Scale Range | Packed Tokens | Mean CPU Latency | AST / Syntax Integrity |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Domain A: Text Stream** | 10 | 2k - 32k | $\le 512$ | 3.88 ms | $10/10$ Natural Boundaries |
| **Domain B: Graph & State Tables** | 10 | 2k - 32k | $\le 512$ | 0.58 ms | $10/10$ Projected Invariants |
| **Domain C: Codebase AST Slicing** | 10 | 2k - 32k | $\le 512$ | 6.84 ms | $10/10$ Valid Python AST |

---

## 3. Gate D Disposition Recommendation

- **Overall Milestone Evaluation:** **RECOMMEND_PROCEED**
- All 5/5 frozen support rules have been satisfied with zero margin breaches.
- Zero token overflow detected across the 30-case matrix under official `llama-tokenize.exe`.
- Zero AST syntax errors produced across arbitrary Python code structures.
- Host packaging executed on CPU in an average of 3.77 ms with zero GPU/VRAM footprint.
- Scaffolding engine qualifies for promotion consideration under [MN-009 Gate D Disposition Review](../gate-d-disposition-review.md).
