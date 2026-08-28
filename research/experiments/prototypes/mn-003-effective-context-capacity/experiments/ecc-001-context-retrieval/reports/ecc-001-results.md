# ECC-001 canonical results

## Result status

ECC-001 version 0.1.0 was executed on both MN-002-qualified capability baselines from clean Git commit `701fb1fe417bde7db6f4749479955c37a734616d`. Both retained runs pass offline validation against definition fingerprint `d9c86595d84266dcc87becc4469bf5a1ed691a4cadbf30ef620d4ac8983efa29`.

The result shows no Context Retrieval degradation within the tested 512–16,384 requested-token ladder. This is valid negative evidence for the degradation hypothesis; it is not evidence that either model has unlimited effective context or that its advertised context window is fully usable for harder tasks.

## Subjects and environment

| Model | Model SHA-256 | Canonical run |
| --- | --- | --- |
| Llama-3.2-3B-Instruct-Q4_K_M | `6c1a2b41161032677be168d354123594c0e6e67d2b9227c84f296ad037c728ff` | `20260827T084957Z-ecc-001-llama-3.2-3b-21bf60a1` |
| Qwen3-4B-Q4_K_M | `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5` | `20260827T113851Z-ecc-001-qwen3-4b-4552a0b0` |

Both runs used llama.cpp `0.2.0-dev`, build `10566`, commit `bb4caa754`, with a configured 16,896-token context, 16 output tokens, temperature 0, seed 42, prompt caching disabled, and one parallel slot. The retained metadata contains the full commands, model/runtime identities, chat-template settings, and Windows/NVIDIA RTX 3050 Laptop GPU environment.

Model qualification remains capability evidence, not production-model selection. Timing observations below are environment-specific runtime evidence and are not part of the capability conclusion.

## Accuracy curve

| Requested input tokens | Llama actual-token range | Llama accuracy | Qwen actual-token range | Qwen accuracy |
| ---: | ---: | ---: | ---: | ---: |
| 512 | 476–480 | 1.00 | 452–457 | 1.00 |
| 1,024 | 998–1,002 | 1.00 | 987–997 | 1.00 |
| 2,048 | 2,042–2,046 | 1.00 | 1,995–2,010 | 1.00 |
| 4,096 | 4,072–4,076 | 1.00 | 4,031–4,095 | 1.00 |
| 8,192 | 8,136–8,192 | 1.00 | 8,126–8,189 | 1.00 |
| 16,384 | 16,368–16,372 | 1.00 | 16,324–16,358 | 1.00 |

Each level contains 20 independent semantic cases. Both runs have baseline accuracy 1.00, relative accuracy 1.00 at every level, 120 observed results, and zero invalid or overflowing results. No response was silently truncated. Neither curve is non-monotonic because neither curve changes.

## ECC metrics

| Model | ECC95 | ECC90 | ECC80 |
| --- | ---: | ---: | ---: |
| Llama 3.2 3B | 16,384 | 16,384 | 16,384 |
| Qwen3-4B | 16,384 | 16,384 | 16,384 |

These values use the predeclared contiguous-tested-prefix rule with no interpolation. They mean that each threshold holds through the largest tested requested level. They are lower bounds within ECC-001, not measured failure boundaries and not claims about capacity beyond 16,384 tokens.

## Runtime observations

Median total request time was 2,628.120 ms for Llama and 4,083.911 ms for Qwen in this environment. These values are retained for reproducibility only; ECC-001 does not rank production runtime performance.

## Validation and retained evidence

The offline validator recomputes schemas, fingerprint, case/context coverage, duplicate detection, evaluation, request hashes, prompt-token agreement, overflow/truncation rejection, summaries, relative accuracy, non-monotonicity, and ECC thresholds without rerunning inference.

Canonical evidence:

- `runs/20260827T084957Z-ecc-001-llama-3.2-3b-21bf60a1/`
- `runs/20260827T113851Z-ecc-001-qwen3-4b-4552a0b0/`

Development smoke and pre-freeze runs were excluded from canonical evidence. They were used to identify an initial missing-special-token preflight mismatch and a natural-language distractor step one token beyond the original construction tolerance. The final definition uses actual runtime prompt counts and a predeclared maximum 96-token shortfall; canonical runs were regenerated from a clean commit.

## Interpretation and next research step

ECC-001 infrastructure and the first direct-context measurement are complete, but MN-003 is not complete. The easy single-fact, midpoint-evidence task did not locate a degradation boundary for either qualified model. The next research definition should increase falsification power through one controlled dimension or a harder inherited capability while preserving direct context and deterministic evaluation.

No retrieval, RAG, memory, summarization, compression, routing, or other context-management architecture is selected by this result. Architecture intervention remains premature until a bounded baseline exposes a measurable limitation that an intervention can be compared against.
