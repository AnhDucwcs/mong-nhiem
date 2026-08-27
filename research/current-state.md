# Current state

## MN-001 — completed

MN-001 established the source layout, canonical research knowledge base, minimal packaging, pytest/Ruff checks, CI, and a package-import smoke test.

## MN-002 — Model Qualification — completed and frozen

MCB v0.1.0 and v0.2.0 remain historical/superseded evidence. Re-evaluation of v0.2 failures under the frozen v0.3 accepted-answer contract converts 143 previously failing semantic-suite outputs into accepted output-equivalence cases; 56 semantic-suite failures remain failing under the corrected deterministic evaluator.

MCB v0.3.0 is the canonical frozen qualification benchmark. Its fingerprint is `2ac24df4e6cca12e13da577fb48db5da8e39d89cf3646ef705ea7679b4548f7a`. It contains 100 cases across Instruction Following, Structured Output, Context Retrieval, State Tracking, and Causal Reasoning. Six local GGUF candidates were measured. Llama-3.2-3B-Instruct-Q4_K_M and Qwen3-4B-Q4_K_M meet every capability gate and are the qualified capability baselines. Capability qualification and runtime performance are separate evidence.

This qualification is not a production-model choice and does not validate an ECC, retrieval, memory, RAG, summarization, compression, routing, or context-management mechanism.

## MN-003 — Effective Context Capacity — active baseline implementation

MN-003 is a bounded prototype under `research/experiments/prototypes/`. ECC-001 now defines deterministic single-fact Context Retrieval across a 512–16,384 requested-token ladder using direct, unmodified context, fixed midpoint evidence, exact evaluation, model-token-aware construction, explicit schemas, a canonical runner, and an offline validator. Canonical full-run evidence is pending. This measurement is distinct from an advertised context-window size.

The experiment supports both MN-002-qualified capability baselines, Llama 3.2 3B and Qwen3-4B; neither is a production-model selection. State Tracking and Causal Reasoning remain later candidate task families. Retrieval, memory, RAG, summarization, compression, and context-routing work remain explicitly out of scope until the direct-context baseline and its limitations are measured.
