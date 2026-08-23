# MN-002 Model Qualification — MCB v0.3.0

Frozen definition fingerprint: `2ac24df4e6cca12e13da577fb48db5da8e39d89cf3646ef705ea7679b4548f7a`.

The v0.3 evaluator performs exact comparison against each case's declared accepted values, after only Unicode/case/whitespace and terminal-punctuation normalization. Structured output remains strict JSON-object validation. No fuzzy, substring, or model-judged scoring is used.

| Model | Instruction | Structured | Retrieval | State | Causal | Overall | Qualification |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Qwen3-1.7B-Q4_K_M.gguf | 0.85 | 1.00 | 0.80 | 0.65 | 0.80 | 0.82 | FAIL |
| Llama-3.2-3B-Instruct-Q4_K_M.gguf | 0.90 | 1.00 | 0.80 | 0.95 | 0.80 | 0.89 | PASS |
| SmolLM3-Q4_K_M.gguf | 0.80 | 1.00 | 1.00 | 0.35 | 0.80 | 0.79 | FAIL |
| microsoft_Phi-4-mini-instruct-Q4_K_M.gguf | 0.90 | 0.00 | 1.00 | 0.90 | 0.80 | 0.72 | FAIL |
| gemma-3-4b-it-Q4_K_M.gguf | 0.90 | 0.55 | 0.95 | 0.95 | 0.90 | 0.85 | FAIL |
| Qwen3-4B-Q4_K_M.gguf | 0.90 | 1.00 | 1.00 | 0.75 | 1.00 | 0.93 | PASS |

Selection rule: newest run per required model whose metadata has benchmark `0.3.0`, the fingerprint above, a v0.3 inference label, and `run_status=valid`; directory names are not inputs to selection.

The raw run IDs retain a legacy `mcb-v020` orchestrator label. This is recorded as an integration naming defect; benchmark version and frozen fingerprint are the authoritative identifiers and were validated before reporting.
