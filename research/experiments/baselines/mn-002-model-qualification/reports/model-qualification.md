# MN-002 Model Qualification — MCB v0.1.0

Generated from measured run artifacts. Capability and performance remain separate.

| Model | Instruction Following | Structured Output | Context Retrieval | State Tracking | Causal Reasoning | Overall | Qualification | Generation tok/s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| Qwen3-1.7B-Q4_K_M.gguf | 0.85 | 1.00 | 0.70 | 0.00 | 0.40 | 0.59 | FAIL | 116.04 |
| Qwen3-4B-Q4_K_M.gguf | 0.90 | 1.00 | 0.75 | 0.00 | 0.30 | 0.59 | FAIL | 54.94 |
| gemma-3-4b-it-Q4_K_M.gguf | 0.90 | 0.55 | 0.95 | 0.00 | 0.20 | 0.52 | FAIL | 54.08 |
| Llama-3.2-3B-Instruct-Q4_K_M.gguf | 0.90 | 0.95 | 0.25 | 0.00 | 0.00 | 0.42 | FAIL | 70.58 |
| microsoft_Phi-4-mini-instruct-Q4_K_M.gguf | 0.90 | 0.00 | 0.45 | 0.00 | 0.00 | 0.27 | FAIL | 59.33 |
| SmolLM3-Q4_K_M.gguf | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | FAIL | 72.42 |

## Limitations

Each run retains raw server output, commands, model SHA-256, runtime output, hardware snapshot, records, and summary. MCB v0.1.0 is a small synthetic qualification gate, not a broad knowledge, safety, multilingual, or long-context benchmark. llama-bench throughput is auxiliary only.
