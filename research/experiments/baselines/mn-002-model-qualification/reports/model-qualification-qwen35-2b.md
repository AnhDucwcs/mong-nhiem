# MN-002 Model Qualification — Qwen3.5-2B Evaluation

- **Model File:** `Qwen3.5-2B-Q4_K_M.gguf`
- **Architecture:** Hybrid Gated DeltaNet + Gated Attention (2B parameters)
- **Quantization:** Q4_K_M (1.29 GiB)
- **Run ID:** `20261001T121357Z-mcb-v030-qwen3-5-2b-q4-k-m-b288e5cb`
- **Benchmark Version:** MCB v0.3.0
- **Frozen Definition Fingerprint:** `2ac24df4e6cca12e13da577fb48db5da8e39d89cf3646ef705ea7679b4548f7a`
- **Qualification Verdict:** **PASS**

---

## 1. Capability Scorecard vs Baselines

The canonical qualification contract requires meeting every critical suite gate:
- Instruction Following $\ge 0.80$
- Structured Output $\ge 0.90$
- Context Retrieval $\ge 0.80$
- State Tracking $\ge 0.70$
- Causal Reasoning $\ge 0.70$
- Overall Score $\ge 0.80$

| Model | Instruction | Structured | Retrieval | State | Causal | Overall | Qualification |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `Qwen3-1.7B-Q4_K_M.gguf` | 0.85 | 1.00 | 0.80 | 0.65 | 0.80 | 0.82 | **FAIL** (State < 0.70) |
| `Llama-3.2-3B-Instruct-Q4_K_M.gguf` | 0.90 | 1.00 | 0.80 | 0.95 | 0.80 | 0.89 | **PASS** |
| `Qwen3-4B-Q4_K_M.gguf` | 0.90 | 1.00 | 1.00 | 0.75 | 1.00 | 0.93 | **PASS** |
| **`Qwen3.5-2B-Q4_K_M.gguf`** | **0.90** | **1.00** | **0.80** | **0.75** | **0.80** | **0.85** | **PASS** |

---

## 2. Key Findings

1. **State Tracking Gate Passed (0.75):**
   Where `Qwen3-1.7B` failed at 0.65, `Qwen3.5-2B` achieves 0.75 (15/20), satisfying the critical State gate and demonstrating generational progress in recurrent state retention.
2. **Flawless Structured Output (1.00):**
   Scored 20/20 on strict JSON-schema validation with `enable_thinking=false` passed via `chat_template_kwargs`, confirming zero JSON corruption or formatting drift.
3. **Hardware & Execution Efficiency:**
   The entire 100-case evaluation suite executed in under 19 seconds on local RTX 3050 Laptop GPU, consuming only 1.31 GiB of VRAM.

---

## 3. Navigation & Knowledge Graph Links

- [Mộng Nhiễm Root](../../../../00-mong-nhiem.md)
- [MN-002 Model Qualification](../README.md)
- [Historical MCB v0.3.0 Baseline Report](model-qualification-v0.3.0.md)
- [Current State Knowledge Base](../../../../current-state.md)
