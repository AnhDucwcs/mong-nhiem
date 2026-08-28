# ECC-003 results — Evidence Position Sensitivity under Confusable Context

## Result status

Canonical direct-context evidence is complete and offline-validated for both MN-002-qualified capability baselines. The frozen ECC-003 definition fingerprint is `9c7e541c2810fa0e7d063b45f94312d434d58c87e965131c90dff3e0613345f2`.

Each run contains 360 raw case-level results: 20 deterministic semantic cases × 6 requested token levels × 3 evidence positions. Both runs have zero invalid, overflowing, or truncated cases. The Llama run was produced from clean commit `2c12e59`; the Qwen run was produced from clean commit `89b380b`, which adds only recorded server restart lifecycle handling between position batches for the 4 GB GPU host.

ECC-003 holds ECC-002's confusable unmarked registry-record task constant and varies only target evidence position: early (0.10), middle (0.50), and late (0.90), each within the frozen ±0.05 relative-position tolerance. This retains direct, unmodified context and does not test a context-management intervention.

## Smoke evidence

Before canonical execution, both models passed two-case 512/2,048-token smoke coverage across all positions. After the Qwen CUDA out-of-memory diagnostic attempt at late 16k, a one-case 16k lifecycle smoke passed early, middle, and late with the server restarted between position batches. These intentionally partial artifacts remain outside canonical `runs/`; only the two complete validated runs below are retained as canonical evidence.

## Canonical capability results

The 512-token condition is the per-position short-context baseline. Every baseline accuracy was 1.00, so relative accuracy equals accuracy in this experiment. Accuracy resolution is 0.05 (one of 20 cases).

### Llama 3.2 3B

| Requested tokens | Early: actual / accuracy-relative | Middle: actual / accuracy-relative | Late: actual / accuracy-relative |
| --- | ---: | ---: | ---: |
| 512 | 479–509 / 1.00–1.00 | 480–509 / 1.00–1.00 | 481–509 / 1.00–1.00 |
| 1,024 | 992–1,024 / 1.00–1.00 | 988–1,024 / 1.00–1.00 | 986–1,022 / 1.00–1.00 |
| 2,048 | 2,014–2,048 / 1.00–1.00 | 2,014–2,048 / 0.95–0.95 | 2,009–2,048 / 0.90–0.90 |
| 4,096 | 4,053–4,092 / 1.00–1.00 | 4,059–4,091 / 0.95–0.95 | 4,061–4,096 / 0.90–0.90 |
| 8,192 | 8,140–8,191 / 1.00–1.00 | 8,107–8,187 / 0.90–0.90 | 8,110–8,191 / 1.00–1.00 |
| 16,384 | 16,327–16,377 / 1.00–1.00 | 16,274–16,378 / 0.85–0.85 | 16,268–16,376 / 0.70–0.70 |

Early position held 20/20 at every level: `ECC95 >= 16,384`, `ECC90 >= 16,384`, and `ECC80 >= 16,384 tested tokens`, all right-censored lower bounds. Middle gave `ECC95 = 4,096`, `ECC90 = 8,192`, and `ECC80 >= 16,384` (right-censored). Late gave `ECC95 = 1,024`, `ECC90 = 8,192`, and `ECC80 = 8,192` under the contiguous-tested-prefix rule.

The position gap (best minus worst accuracy) is 0.00, 0.00, 0.10, 0.10, 0.10, then 0.30 over the ladder. Late recovers from 0.90 at 4,096 to 1.00 at 8,192 before declining to 0.70 at 16,384, so that curve is non-monotonic. The middle condition exactly reproduces ECC-002's Llama accuracy curve at the tested resolution, supporting the intended historical compatibility of the fixed symmetric middle policy.

There are 17 Llama failures. None output a tracked distractor code; all were classified as other output. No result selected a before/after distractor or a nearby distractor. This evidence supports position-sensitive retrieval behavior in this bounded task, but it does not establish a causal mechanism or a simple lost-in-the-middle pattern: the late condition is weakest at the tested ceiling, not middle.

### Qwen3-4B

| Requested tokens | Early: actual / accuracy-relative | Middle: actual / accuracy-relative | Late: actual / accuracy-relative |
| --- | ---: | ---: | ---: |
| 512 | 474–500 / 1.00–1.00 | 475–500 / 1.00–1.00 | 476–500 / 1.00–1.00 |
| 1,024 | 981–1,023 / 1.00–1.00 | 982–1,023 / 1.00–1.00 | 983–1,024 / 1.00–1.00 |
| 2,048 | 2,006–2,043 / 1.00–1.00 | 2,001–2,042 / 1.00–1.00 | 2,000–2,043 / 1.00–1.00 |
| 4,096 | 4,047–4,094 / 1.00–1.00 | 4,042–4,093 / 1.00–1.00 | 4,056–4,096 / 1.00–1.00 |
| 8,192 | 8,150–8,187 / 1.00–1.00 | 8,133–8,191 / 1.00–1.00 | 8,120–8,189 / 1.00–1.00 |
| 16,384 | 16,326–16,384 / 1.00–1.00 | 16,282–16,384 / 1.00–1.00 | 16,296–16,384 / 1.00–1.00 |

Qwen3-4B passed 20/20 at every level and position. For every position, `ECC95 >= 16,384`, `ECC90 >= 16,384`, and `ECC80 >= 16,384 tested tokens` are right-censored lower bounds, not measured failure boundaries or advertised-window claims. Every observed position gap and middle penalty is 0.00; there are no failures.

## Descriptive runtime evidence

Median total request time in milliseconds is reported below as `early / middle / late`, with min–max retained in the run summaries. It describes this exact local setup, not model quality or production throughput.

| Requested tokens | Llama median ms (early / middle / late) | Qwen median ms (early / middle / late) |
| --- | ---: | ---: |
| 512 | 488 / 497 / 510 | 984 / 1,058 / 855 |
| 1,024 | 872 / 848 / 867 | 1,389 / 1,774 / 1,705 |
| 2,048 | 1,606 / 1,763 / 1,842 | 2,794 / 2,761 / 2,558 |
| 4,096 | 3,477 / 3,446 / 3,413 | 5,629 / 5,475 / 5,354 |
| 8,192 | 7,307 / 7,157 / 7,652 | 11,080 / 11,278 / 11,199 |
| 16,384 | 18,541 / 18,641 / 18,156 | 28,396 / 29,198 / 28,657 |

At 16k, retained min–max request times are 16,693–21,164 ms (Llama early), 17,613–20,134 ms (middle), 17,439–18,540 ms (late); and 25,913–37,003 ms (Qwen early), 27,223–35,632 ms (middle), 26,600–35,757 ms (late). Both models completed every valid 16k request in the configured reserve on the RTX 3050 Laptop GPU with 4 GB VRAM. Qwen required a server restart between position batches to avoid the CUDA OOM observed during a discarded partial diagnostic run, which is a practical host-lifecycle constraint rather than an ECC capability result.

## Evidence and validation

- [Llama canonical run](../runs/20260827T171120Z-ecc-003-llama-3.2-3b-dc4f0fbc/): metadata, 360 raw request/response records, recomputable summary, and diagnostics.
- [Qwen canonical run](../runs/20260827T183725Z-ecc-003-qwen3-4b-0221f7d3/): metadata, 360 raw request/response records, recomputable summary, and diagnostics.
- The offline validator replays deterministic cases and verifies schemas, the definition fingerprint, complete selection, unique case/level/position rows, placement and confusability controls, no overflow or truncation, raw/evaluated response consistency, and recomputed accuracy, failure analysis, runtime aggregates, and ECC metrics.

## Interpretation and limitations

ECC-003 increases the falsification power of ECC-002 by isolating evidence position while preserving the same direct-context confusable task. It observes substantial Llama position sensitivity at 16k and no observed Qwen position sensitivity within this bounded matrix. It does not establish a general model ranking, an advertised context limit, why individual Llama outputs failed, or an intervention that improves performance.

The evidence remains limited to 20 synthetic single-fact cases, one entity/code record template, three predeclared positions, deterministic temperature-zero decoding, one local llama.cpp configuration, and a 16,384-token ceiling. The non-monotonic late Llama curve and 0.05 accuracy resolution mean a confirmatory direct-context experiment should precede any architecture comparison. A defensible next step is a predeclared repeat with more independent semantic cases or one harder inherited task family while holding position treatment fixed. Retrieval, RAG, memory, summarization, compression, routing, embeddings, semantic search, and external state remain out of scope.
