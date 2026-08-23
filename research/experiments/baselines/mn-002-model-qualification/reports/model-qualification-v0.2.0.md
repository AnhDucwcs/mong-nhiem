# MN-002 Model Qualification — MCB v0.2.0

v0.2.0 clarifies the exact-only output contract for state and causal suites and disables verified native thinking for Qwen3 and SmolLM3. It supersedes v0.1.0 capability scores; v0.1.0 raw evidence is preserved.

| Model | Instruction | Structured | Retrieval | State | Causal | Overall | Qualification |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Qwen3-1.7B-Q4_K_M.gguf | 0.85 | 1.00 | 0.70 | 0.40 | 0.40 | 0.67 | FAIL |
| Llama-3.2-3B-Instruct-Q4_K_M.gguf | 0.90 | 1.00 | 0.25 | 0.65 | 0.15 | 0.59 | FAIL |
| SmolLM3-Q4_K_M.gguf | 0.80 | 1.00 | 0.00 | 0.35 | 0.35 | 0.50 | FAIL |
| microsoft_Phi-4-mini-instruct-Q4_K_M.gguf | 0.90 | 0.00 | 0.45 | 0.50 | 0.00 | 0.37 | FAIL |
| gemma-3-4b-it-Q4_K_M.gguf | 0.90 | 0.55 | 0.95 | 0.65 | 0.45 | 0.70 | FAIL |
| Qwen3-4B-Q4_K_M.gguf | 0.90 | 1.00 | 0.75 | 0.50 | 0.55 | 0.74 | FAIL |
