# ECC-006 results — State Tracking baseline

Canonical evidence: `20260828T053342Z-ecc-006-llama-3.2-3b-ab958c23`; definition fingerprint: `37f2dc1cc4cdfbf4a667c54f159bbd5203918f85f4d39001fa62ffcba379ac2e`.

Llama 3.2 3B was measured on six deterministic direct-context State Tracking cases. Each target had exactly four chronological updates, fixed midpoint placement, and a final-state question; only context length changed. The model used the inherited llama.cpp contract: temperature 0, seed 42, 16 output tokens, context size 16,896, no prompt cache, and exact explicit accepted-answer evaluation.

| Requested tokens | Accuracy | Relative accuracy | Actual input-token range |
| --- | ---: | ---: | --- |
| 512 | 2/6 = 0.333 | 1.000 | 485–494 |
| 2,048 | 1/6 = 0.167 | 0.500 | 2,007–2,016 |
| 8,192 | 0/6 = 0.000 | 0.000 | 8,145–8,187 |
| 16,384 | 0/6 = 0.000 | 0.000 | 16,347–16,367 |

The curve is monotonic. ECC95, ECC90, and ECC80 are each 512 under the contiguous tested-prefix rule. There are zero invalid or truncated rows, zero infrastructure failures, zero invalid cases, zero malformed responses, and 21 `incorrect_state` failures. Raw outputs are retained, including prior target states returned at the longer levels.

ECC-006 therefore answers its baseline question clearly for this subject and bounded task: State Tracking reliability declines sharply as direct context length increases while the update count, event structure, placement policy, scoring and runtime remain fixed. This is not an advertised context-window claim, causal explanation, production-model choice, or architecture decision. No ECC-007 is justified merely to verify this result: the retained evidence already resolves the principal ambiguity categories predeclared in ECC-006.
