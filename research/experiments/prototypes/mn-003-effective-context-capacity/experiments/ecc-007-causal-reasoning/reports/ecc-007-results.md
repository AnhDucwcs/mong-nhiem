# ECC-007 results — Causal Reasoning under increasing context length

ECC-007 is a direct-context causal-reachability measurement, not an architecture experiment. Its frozen definition fingerprint is `1af38f7db3d858eab5a3ba0bd94ac09cba46542bbeae62203fdb80474a358949`. The valid canonical Qwen3-4B run is `20260828T081030Z-ecc-007-qwen3-4b-3fe7479d`, created from clean commit `99e5795edf7a6d86562873b4b05e52eeb7269fc2` with llama.cpp build 10566 / commit `bb4caa754` on the RTX 3050 Laptop GPU (4 GiB).

## Frozen measurement contract

The workload contains eight deterministic two-hop graphs (four reachable YES, four unreachable NO). Each graph has one target chain and unique disconnected causal-edge distractors using the identical `Causal link: X causes Y.` record template. The target chain is placed at the nearest feasible midpoint (0.50 plus or minus 0.05). Only requested input-token length varies: 512, 2,048, 8,192, and 16,384. Qwen runs with temperature 0, seed 42, thinking disabled, 16 output tokens, and configured context size 16,896. Exact YES/NO evaluation normalizes only whitespace, case, and terminal punctuation.

Pre-freeze calibration used four balanced examples per candidate at 512 requested tokens. Qwen3-4B passed 4/4 at both two and three hops; the fixed selection rule chose two hops as the simplest candidate above the 0.75 non-floor criterion. Llama 3.2 3B passed 0/4 at both candidates because every response began an explanation and exhausted the 16-token contract without an exact YES/NO. That format floor is retained calibration evidence, not an inference about relative causal difficulty.

## Canonical result

| Requested input tokens | Actual input-token range | Pass | Accuracy | Relative accuracy | Median total request time |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 512 | 509–509 | 8/8 | 1.000 | 1.000 | 567 ms |
| 2,048 | 2,017–2,017 | 8/8 | 1.000 | 1.000 | 2,334 ms |
| 8,192 | 8,165–8,165 | 7/8 | 0.875 | 0.875 | 10,002 ms |
| 16,384 | 16,365–16,365 | 8/8 | 1.000 | 1.000 | 24,643 ms |

All 32 rows are valid. There are zero runtime/infrastructure errors, invalid cases, malformed responses, and truncations. The only failure is `ecc007-004` at 8,192: expected `NO`, raw normalized answer `YES`, classified `incorrect_causal_inference`. It is a false positive on an unreachable graph; raw evidence, graph, request, and response are retained in the canonical run.

Baseline accuracy is 1.000 at 512. Under the contiguous-tested-prefix rule, ECC95 and ECC90 resolve to 2,048 because the 8,192 point is 0.875. ECC80 is a right-censored lower bound `>= 16,384 tested tokens`: every tested point remains at or above 0.80. There is no interpolation.

The curve is non-monotonic: it dips once at 8,192 and recovers at 16,384. Therefore this small bounded run does **not** locate a stable context-length degradation boundary and does not establish a monotonic causal-capacity decline. It nevertheless retains a measurable false-positive error at 8,192 for follow-up replication, rather than treating the 16k recovery as proof of robustness.

Runtime is descriptive rather than a performance benchmark. Median total request time rises from 0.57 s at 512 to 24.64 s at 16,384; the retained llama.cpp logs show prompt-cache eviction at long context on the 4 GiB GPU. This indicates a practical local cost boundary in this configuration, but does not change the capability conclusion.

## Reproduction and validation

Run `python scripts/validate_ecc007.py runs/20260828T081030Z-ecc-007-qwen3-4b-3fe7479d` to replay the definition fingerprint, JSON schemas, graph reachability, target/distractor uniqueness and non-leakage, reconstructed prompt hash, deterministic evaluation, budget/placement checks, and aggregate summary. The canonical evidence lives under `runs/20260828T081030Z-ecc-007-qwen3-4b-3fe7479d/`.

This evidence neither selects an architecture nor warrants retrieval, RAG, memory, compression, summarization, routing, embeddings, or external-state intervention. A next direct-context experiment, if justified, should first replicate or isolate the 8,192 false-positive pattern with a pre-frozen design.
