# ECC-002 results — Confusable Context Retrieval

## Result status

Canonical direct-context evidence is complete and offline-validated for both MN-002-qualified capability baselines. The frozen ECC-002 definition fingerprint is `824ba4d6df62f8ddf4a49d90a2e2d4d44211399c730c831f2bf0338ba8e5c7cf`.

Both complete runs were produced from clean commit `bbd8cbdcc8818f1eee377a17bda5a59137dcfb3b`, contain 120 case-level results (20 semantic cases × 6 levels), and contain zero invalid, overflowing, or truncated cases.

ECC-002 increases falsification power relative to ECC-001 without adding an intervention: target and distractors are all ordinary `Registry entry` records with the same vocabulary, template, entity/code shapes, and direct context. The target is unique and unmarked.

## Smoke evidence

Before canonical execution, each qualified model passed a two-case smoke at requested 512 and 2,048 tokens. The smoke artifacts were offline-validated but intentionally partial and remain outside canonical `runs/`.

## Canonical capability results

The 512-token short-context baseline was 1.00 for both models. Accuracy resolution is 0.05 per level.

| Requested tokens | Llama actual range | Llama accuracy / relative | Qwen actual range | Qwen accuracy / relative |
| --- | ---: | ---: | ---: | ---: |
| 512 | 480–509 | 1.00 / 1.00 | 475–500 | 1.00 / 1.00 |
| 1,024 | 992–1,024 | 1.00 / 1.00 | 983–1,024 | 1.00 / 1.00 |
| 2,048 | 2,014–2,048 | 0.95 / 0.95 | 2,024–2,044 | 1.00 / 1.00 |
| 4,096 | 4,064–4,096 | 0.95 / 0.95 | 4,055–4,093 | 1.00 / 1.00 |
| 8,192 | 8,166–8,189 | 0.90 / 0.90 | 8,154–8,191 | 1.00 / 1.00 |
| 16,384 | 16,349–16,381 | 0.85 / 0.85 | 16,342–16,384 | 1.00 / 1.00 |

Llama 3.2 3B shows a monotonic observed degradation curve: 20/20, 20/20, 19/20, 19/20, 18/20, then 17/20. Under the contiguous-prefix rule, `ECC95 = 4,096`, `ECC90 = 8,192`, and `ECC80 >= 16,384 tested tokens`. ECC80 is right-censored: it held at the largest tested level, so the result is not a measured failure boundary.

Qwen3-4B passed 20/20 at every level. `ECC95 >= 16,384`, `ECC90 >= 16,384`, and `ECC80 >= 16,384 tested tokens` are all right-censored lower bounds. They do not describe performance beyond the ladder or an advertised context window.

Neither curve is non-monotonic. The model difference is retained evidence, not a production-model decision: MN-002 qualification remains a capability gate and runtime interpretation remains separate.

## Descriptive runtime evidence

The following are median total request times in milliseconds, with min–max retained in the run summaries. They describe this exact local setup, not production throughput or a model-quality metric.

| Requested tokens | Llama median (min–max) ms | Qwen median (min–max) ms |
| --- | ---: | ---: |
| 512 | 556 (534–622) | 1,006 (977–1,173) |
| 1,024 | 974 (933–1,028) | 1,581 (1,537–1,687) |
| 2,048 | 1,844 (1,729–2,033) | 2,799 (2,707–2,947) |
| 4,096 | 3,752 (3,467–4,796) | 6,146 (5,459–8,327) |
| 8,192 | 8,034 (7,614–10,419) | 12,525 (12,255–18,805) |
| 16,384 | 20,294 (19,718–29,788) | 31,179 (26,090–40,928) |

The retained metadata identifies an RTX 3050 Laptop GPU with 4 GB VRAM and llama.cpp runtime. Both models completed every 16k request within the configured context reserve, but median total request time rises materially at 16k. This is a practical local-hardware observation, not an overflow or capability conclusion.

## Evidence and validation

- [Llama canonical run](../runs/20260827T125047Z-ecc-002-llama-3.2-3b-6feee9c8/): metadata, 120 raw request/response records, recomputable summary, and llama.cpp diagnostics.
- [Qwen canonical run](../runs/20260827T130519Z-ecc-002-qwen3-4b-bacc3746/): metadata, 120 raw request/response records, recomputable summary, and llama.cpp diagnostics.
- The offline validator checks schemas, definition fingerprint, exact complete selection, clean-worktree requirement, deterministic generator replay, target/distractor contracts, context accounting, no truncation, raw response consistency, and summary/ECC recomputation.

## Interpretation and limitations

ECC-002 establishes a measurable direct-context degradation baseline for Llama 3.2 3B under controlled semantic interference. Qwen3-4B remains stable in this bounded task, which is also valid evidence. The experiment does not establish why the Llama failures occurred, a general model ranking, or a remedy.

The result remains limited to 20 single-fact synthetic cases with midpoint evidence, fixed entity/code record structure, exact-answer scoring, one runtime configuration, and a 16,384-token upper test level. It does not vary evidence position, relevant-fact count, distributed evidence, State Tracking, or Causal Reasoning.

The next experiment should remain direct-context and isolate one additional task-pressure dimension or inherited harder task family before any retrieval, RAG, memory, summarization, compression, routing, embeddings, semantic search, or external-state architecture is considered.
