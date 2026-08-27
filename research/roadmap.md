# Roadmap

## MN-001 — Development foundation

Status: completed.

## MN-002 — Model qualification

Status: completed and frozen. MCB v0.3.0 is the canonical capability-qualification benchmark (fingerprint `2ac24df4e6cca12e13da577fb48db5da8e39d89cf3646ef705ea7679b4548f7a`). Llama 3.2 3B and Qwen3-4B are qualified capability baselines; capability and runtime evidence remain separate. This is not a production-model choice.

## MN-003 — Effective Context Capacity

Status: active research preparation. The bounded prototype belongs in `research/experiments/prototypes/mn-003-effective-context-capacity/`.

1. Establish a hypothesis for reliable task-performance degradation as controlled context pressure increases, distinct from advertised context-window size.
2. Select one or both MN-002-qualified capability baselines and an unmodified-context measurement baseline.
3. Define controlled variables, beginning with context length and potentially later relevant-information density, evidence position, and distributed evidence.
4. Define task families, metrics, degradation-curve analysis, and success criteria before any intervention.
5. Measure the baseline before considering retrieval, memory, RAG, summarization, compression, or context-routing architectures.
6. Keep any future architecture experiment separate, and promote only proven reusable components into `src/mong_nhiem/` through an explicit decision.
