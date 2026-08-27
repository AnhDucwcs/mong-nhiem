# ECC-003 — Evidence Position Sensitivity under Confusable Context

## Status

Definition frozen; runner, validator, tests, smoke evidence, and canonical results are pending. ECC-003 is a bounded direct-context experiment under MN-003, not a context-management intervention.

## Hypothesis

ECC-003 holds the ECC-002 confusable single-fact task constant while varying only the unmarked target record's token-relative position: early (0.10), middle (0.50), and late (0.90), each with tolerance 0.05. A consistently weaker middle condition across levels or failures would be behavioral evidence consistent with lost-in-the-middle; one isolated difference is not enough to claim that pattern or a causal mechanism.

## Frozen controls

- Same 20 ECC-002-equivalent semantic cases, target/distractor template, deterministic generator, uniqueness rules, question, answer format, direct context, inference settings, llama.cpp contract, and exact evaluator.
- The target has no marker, special heading, delimiter, or lexical cue.
- 512, 1,024, 2,048, 4,096, 8,192, and 16,384 requested model-input tokens are tested at every position.
- Middle preserves ECC-002's symmetric A-before/B-after sequence for a fixed pair count. Different tokenizers may choose different terminal pair counts; every actual count is retained.

## Metrics and retained evidence

Each position uses its 512-token condition as the relative-accuracy baseline. The summary derives ECC95/ECC90/ECC80 separately by position using contiguous tested prefixes and explicitly marks right-censored thresholds. It also predeclares `position_gap` and `middle_penalty` per level.

Each result records actual model tokens, requested/actual position, before/after distractor counts, full request/response, deterministic evaluation, failure classification, and timing. Failures that select a context distractor retain its entity, code, before/after side, record-relative position, and distance from target. Runtime is descriptive and aggregated by model × context level × position.

## Non-goals

ECC-003 does not implement or select retrieval, RAG, memory, summarization, compression, routing, embeddings, semantic search, external state, or an architecture. It measures behavioral direct-context sensitivity only.
