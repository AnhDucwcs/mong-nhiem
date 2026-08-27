# MN-003 — Effective Context Capacity

## Status

Active research preparation. This is a bounded, documentation-only prototype charter; it defines no experiment cases, runner, configuration, or architecture intervention.

## Research question

For an MCB-qualified small local model, how does reliable task performance degrade as context length and context pressure increase while the task-relevant information remains controlled?

Effective Context Capacity is the measured range over which a model performs a controlled task reliably. It is distinct from the model's advertised context-window size.

## Scope

- **Experiment subjects:** one or both MN-002-qualified capability baselines: Llama 3.2 3B and Qwen3-4B. Qualification comes from frozen MCB v0.3.0, fingerprint `2ac24df4e6cca12e13da577fb48db5da8e39d89cf3646ef705ea7679b4548f7a`; it is not a production-model selection.
- **Initial task families:** Context Retrieval, State Tracking, and Causal Reasoning inherited from MCB capabilities, subject to a later experiment definition.
- **Initial baseline:** direct, unmodified presentation of the controlled context and task to the model. It measures degradation; it does not select or evaluate a context-management architecture.
- **Candidate variables:** context length first; later controlled dimensions may include relevant-information density, evidence position, and distributed evidence.

## Required design gate

Before any architecture intervention, the experiment definition must state:

1. A falsifiable degradation hypothesis.
2. The unmodified-context baseline and controls that preserve task-relevant information.
3. The variables and their tested levels.
4. The reliability metric, analysis of the degradation curve, and success criteria.
5. Reproducible environment, inference, and evidence-retention requirements.

## Non-goals

MN-003 does not yet implement or select retrieval, RAG, memory, summarization, compression, context routing, or any other context-management architecture. Architecture experiments may follow only after measurable baseline degradation behavior has been established.

## Location and evidence boundary

This prototype belongs under `research/experiments/prototypes/`. In contrast, `research/experiments/baselines/` holds comparison/reference evidence such as completed MN-002. Experimental evidence remains separate from `src/mong_nhiem/`; promotion to reusable code requires an explicit decision.