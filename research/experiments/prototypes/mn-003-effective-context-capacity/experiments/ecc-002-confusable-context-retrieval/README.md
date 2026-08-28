# ECC-002 — Confusable Context Retrieval under increasing context pressure

## Status

Definition, deterministic tooling, smoke evidence, and canonical full-run evidence are complete for both qualified models. See the [ECC-002 results](reports/ecc-002-results.md). MN-003 remains active: ECC-002 provides a measurable Llama direct-context degradation curve, while Qwen remains right-censored at the tested ceiling.

## Hypothesis and falsification value

ECC-001 embedded an explicitly marked target fact among semantically unrelated records and found no boundary through the tested ladder. ECC-002 preserves the same task family, models, direct context, ladder, midpoint placement, generation contract, and exact evaluator, while changing the distractor procedure to create direct semantic competition.

Every context record, including the target, has the same template:

```text
Registry entry: Project <entity> has access code <code>.
```

The target is not marked. Distractors have confusable project names, the same question-relevant vocabulary, and the same two-letter/four-digit answer shape. The sole target entity and answer remain unique. Thus, a stable curve is valid evidence, while an observed decline would be attributable to increased context length under a more competitive retrieval task—not to an architecture intervention.

## Frozen design

- **Subjects:** MN-002-qualified Llama 3.2 3B and Qwen3-4B capability baselines; qualification is not production-model selection.
- **Semantic cases:** 20 deterministic cases. This preserves the ECC-001 per-level accuracy resolution (0.05) and was fixed before results.
- **Independent variable:** requested model-input tokens: 512, 1,024, 2,048, 4,096, 8,192, and 16,384.
- **Fixed evidence policy:** target record begins at relative model-token position 0.50 inside the registry context, tolerance 0.05. Symmetric before/after distractor pairs retain the policy across levels.
- **Inference:** llama.cpp, temperature 0, seed 42, 16 output tokens, prompt cache disabled, one server slot.
- **Evaluation:** normalized exact match only. It allows Unicode compatibility normalization, case folding, whitespace collapse, and terminal punctuation removal; explanations, changed separators, extra tokens, and semantic alternatives fail.
- **Token construction:** active model chat template plus active llama.cpp tokenizer determine the actual prompt count. The builder rejects overflow, target overshoot, unacceptable shortfall, unstable evidence placement, and preflight/API count disagreement. It never truncates silently.

The generator validates target answer/entity uniqueness, distractor answer/entity uniqueness, record uniqueness, target-answer non-leakage, and template equivalence before inference. Tokenizer-specific final pair counts may differ and are retained per result; the semantic inventory and deterministic sequence are shared.

## Metrics and runtime evidence

The 512-token level is the short-context baseline. `relative_accuracy(L) = accuracy(L) / baseline_accuracy`. ECC95, ECC90, and ECC80 use the contiguous tested prefix; no interpolation or later isolated recovery increases a threshold.

When a threshold remains true at the largest tested level, the summary marks that threshold right-censored and reports a tested lower bound, for example `ECC90 >= 16,384 tested tokens`. It is not a measured failure boundary or an advertised-context claim.

Runtime remains descriptive, not a performance benchmark. Each context level retains count, median, minimum, and maximum total request time to make a practical 16k hardware cost visible without conflating runtime with capability.

## Reproduction and retention

Validate offline evidence with:

```powershell
.venv\Scripts\python.exe research\experiments\prototypes\mn-003-effective-context-capacity\experiments\ecc-002-confusable-context-retrieval\scripts\validate_ecc002.py
```

Canonical evidence will retain frozen definition/configuration, scripts, model/runtime metadata, request/response JSONL, summaries, and llama.cpp diagnostics. Smoke and pre-freeze runs stay outside canonical `runs/`. Model binaries are local artifacts and are never committed.

## Limitations

ECC-002 measures direct single-fact retrieval only. It does not vary evidence position, relevant-fact count, distributed evidence, State Tracking, Causal Reasoning, or an architecture. It does not implement or select retrieval, RAG, memory, summarization, compression, routing, embeddings, semantic search, or external state.
