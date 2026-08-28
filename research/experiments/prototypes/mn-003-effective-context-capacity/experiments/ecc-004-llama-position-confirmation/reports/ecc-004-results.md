# ECC-004 results — Confirmatory Llama Evidence Position Sensitivity

## Result status

ECC-004 produced complete, clean-worktree, offline-validated canonical evidence for Llama 3.2 3B only. The frozen definition fingerprint is `055773d5239c478c66b6ef98a70d64435eb254649bbb45023f69bbd8a87b738c`.

The canonical run was made from clean commit `92977de0ee79592232d9b7a717d6b1545986f6f2` and contains exactly 240 results: 40 fresh independent semantic cases × 2 requested context levels × 3 target positions. It contains zero invalid, overflowing, or truncated cases.

Qwen3-4B was deliberately not run. ECC-004 confirms the Llama-specific pattern observed in ECC-003; Qwen's ECC-003 360/360 result remains historical bounded reference and its absence here is not a production-model choice.

## Frozen design and confirmation rule

ECC-004 retains the direct confusable registry-record task: one unmarked target and natural same-template distractors, one short access-code answer, deterministic construction, temperature 0, seed 42, 16 output tokens, exact normalized evaluation, and actual model-token accounting. The only conditions are 8,192 and 16,384 requested input tokens crossed with early 0.10, middle 0.50, and late 0.90 target positions (±0.05 token-relative tolerance).

All 40 target entities/codes are fresh and deterministic. The offline validator rejects target overlap with the ECC-002/ECC-003 inventories; it also replays the generator, position allocation, token budget, request hash, score, diagnostics, summary, and paired analysis.

The predeclared primary endpoint is 16k `early − late`. A result is **replicated** only when all four conditions hold: early exceeds late; the gap is at least 0.10; at least four cases are early-pass/late-fail; and that transition count exceeds early-fail/late-pass. No criterion was changed after execution.

## Smoke evidence and diagnostic correction

Before canonical execution, a two-case 8k smoke passed all six rows. A one-case 16k smoke passed early and returned the numeric suffix only at middle/late. This exposed a deterministic diagnostic defect: the exact evaluator correctly failed `9001`, but the initial diagnostic called it `other_text` instead of malformed/incomplete code. The classifier was corrected and regression-tested before the clean canonical commit; rerunning the same minimal 16k smoke classified both failures as `partial_or_malformed_code`. Smoke artifacts are intentionally partial and remain outside canonical `runs/`.

## Canonical capability results

Accuracy resolution is 1/40 = 0.025. ECC-004 does not calculate ECC95/ECC90/ECC80 because its two long-context conditions are not a full threshold ladder; ECC-003 remains that evidence.

| Requested tokens | Early actual / accuracy | Middle actual / accuracy | Late actual / accuracy | Position gap |
| --- | ---: | ---: | ---: | ---: |
| 8,192 | 8,094–8,186 / 0.975 (39/40) | 8,063–8,192 / 0.975 (39/40) | 8,081–8,190 / 0.850 (34/40) | 0.125 |
| 16,384 | 16,225–16,382 / 1.000 (40/40) | 16,250–16,384 / 0.925 (37/40) | 16,245–16,380 / 0.825 (33/40) | 0.175 |

Pairwise differences and directional paired transitions are retained for every level:

| Requested tokens | Early−middle | Early−late | Middle−late | E pass / M fail vs reverse | E pass / L fail vs reverse | M pass / L fail vs reverse |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 8,192 | 0.000 | 0.125 | 0.125 | 0 / 0 | 5 / 0 | 5 / 0 |
| 16,384 | 0.075 | **0.175** | 0.100 | 3 / 0 | **7 / 0** | 4 / 0 |

At the primary 16k endpoint, all predeclared replication checks hold: early accuracy 1.000 exceeds late 0.825; gap is 0.175; seven fresh cases pass early and fail late; and zero move in the opposite direction. ECC-004 therefore classifies the bounded Llama position effect as **replicated**.

## Failure diagnostics

There are 18 exact-match failures: eight at 8k and ten at 16k; one early, four middle, and thirteen late. All 18 are `partial_or_malformed_code`; none are tracked distractor codes, expected code with extra text, invented codes, or other text.

Every failed raw response is the four-digit numeric suffix of the expected access code (for example, expected `AM-9001`, raw `9001`). Under the frozen exact evaluator this remains a failure. The new diagnostic establishes that the observed effect is not evidence of selecting a competing distractor code; it includes output-format/instruction-following behavior coupled to the retrieval task. It does not establish whether the model retained the missing prefix internally.

Repeated failing IDs across 8k/16k are `ecc004-024`, `ecc004-027`, `ecc004-034`, and `ecc004-035`; repeated failures across positions are `ecc004-001`, `ecc004-027`, `ecc004-034`, and `ecc004-035`. No tracked distractor selection occurred before or after the target, so no distractor-side or nearby-distractor count is nonzero.

## Descriptive runtime evidence

Request timing excludes server startup and is descriptive evidence for this exact local runtime, not a capability metric or production-throughput claim.

| Requested tokens | Early median (min–max) ms | Middle median (min–max) ms | Late median (min–max) ms |
| --- | ---: | ---: | ---: |
| 8,192 | 7,476 (6,490–9,299) | 7,631 (7,328–10,141) | 7,411 (7,046–9,307) |
| 16,384 | 19,176 (17,455–26,438) | 18,594 (17,768–21,299) | 18,673 (17,562–19,965) |

## Comparison with ECC-003 and bounded interpretation

ECC-003 Llama results at 8k were early/middle/late = 1.00/0.90/1.00; ECC-004 gives 0.975/0.975/0.850. The ECC-003 late-position recovery does **not** replicate on fresh ECC-004 cases: late is the weakest 8k condition with a 0.125 gap and five early-pass/late-fail transitions.

At 16k, ECC-003 was 1.00/0.85/0.70 and ECC-004 is 1.00/0.925/0.825. The fresh-case effect is numerically weaker than ECC-003's 0.30 early−late gap but has the same direction, a 0.175 gap, and seven one-way paired transitions; it meets the frozen confirmation rule.

This confirms a bounded Llama direct-context position-sensitive limitation under this synthetic confusable retrieval/exact-output contract. It does not prove an attention mechanism, a generic lost-in-the-middle phenomenon, an advertised context-window limitation, a general model ranking, or a remediation. No architecture intervention is selected.

## Evidence and next step

- [Canonical Llama run](../runs/20260827T234326Z-ecc-004-llama-3.2-3b-0731b10a/): metadata, 240 raw request/response rows, recomputable summary, and llama.cpp diagnostics.
- The canonical offline validator verifies complete coverage, fresh target isolation, deterministic generation, placement/tokens, exact score, diagnostics, paired transitions, runtime aggregates, and confirmation classification.

MN-003 now has replicated bounded direct-context position evidence for Llama on this task. Before any architecture comparison, the next step should be a predeclared harder inherited MCB task family or a narrowly scoped intervention hypothesis with this direct-context result as the comparison baseline. Retrieval, RAG, memory, summarization, compression, routing, embeddings, semantic search, and external state remain out of scope until that next design is explicitly authorized.
