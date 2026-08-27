# Roadmap

## MN-001 — Development foundation

Status: completed.

## MN-002 — Model qualification

Status: completed and frozen. MCB v0.3.0 is the canonical capability-qualification benchmark (fingerprint `2ac24df4e6cca12e13da577fb48db5da8e39d89cf3646ef705ea7679b4548f7a`). Llama 3.2 3B and Qwen3-4B are qualified capability baselines; capability and runtime evidence remain separate. This is not a production-model choice.

## MN-003 — Effective Context Capacity

Status: active baseline implementation. The bounded prototype belongs in `research/experiments/prototypes/mn-003-effective-context-capacity/`.

1. ECC-001 establishes a falsifiable direct-context degradation hypothesis, 20 deterministic Context Retrieval cases, and a controlled token-length ladder.
2. ECC-001 supports both MN-002-qualified capability baselines and fixes midpoint evidence, generation, evaluation, model, and runtime controls.
3. The canonical runner and offline validator retain actual per-model token counts, raw evidence, degradation curves, and threshold metrics.
4. Produce and validate canonical complete evidence from a clean committed definition.
5. Interpret the bounded result before extending task difficulty or other controlled dimensions.
6. Measure a baseline limitation before considering retrieval, memory, RAG, summarization, compression, or context-routing architectures.
7. Keep any future architecture experiment separate, and promote only proven reusable components into `src/mong_nhiem/` through an explicit decision.
