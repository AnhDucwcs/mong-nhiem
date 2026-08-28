# ECC-005 results — Qwen position confirmation

Canonical evidence: `20260828T030811Z-ecc-005-qwen3-4b-7dfe418a`; definition fingerprint: `391556975df1477a5628faf9b4d8a2d71b44e50f430a0d5b7a652566afe1b0b8`.

Qwen3-4B-Q4_K_M ran the frozen 30 fresh-case direct-context matrix on a clean worktree: 8,192/16,384 requested input tokens crossed with early (0.10) and late (0.90) unmarked target position. The model, seed, temperature, exact evaluator, context construction, and record template were fixed. `enable_thinking=false`, 16 output tokens, context size 16,896, no prompt cache, and a server restart between position batches were retained from ECC-003.

| Requested tokens | Early accuracy | Late accuracy | Early − late | Early-pass / late-fail | Reverse | Actual input-token range |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 8,192 | 1.000 (30/30) | 1.000 (30/30) | 0.000 | 0 | 0 | early 8,094–8,190; late 8,092–8,192 |
| 16,384 | 1.000 (30/30) | 1.000 (30/30) | 0.000 | 0 | 0 | early 16,256–16,384; late 16,253–16,384 |

There were zero invalid or truncated rows and zero failures in every diagnostic class. The frozen endpoint rule therefore classifies this result as **stable**, not as observed position sensitivity. It independently reproduces ECC-003's Qwen null result on a larger fresh inventory, but remains a bounded direct-context result rather than proof of universal reliability, advertised-window validation, a production selection, or an architecture decision.

Runtime is descriptive only. Median total request time was 13.025 s early and 13.055 s late at 8k; 28.348 s early and 30.259 s late at 16k. The slower 16k requests are a practical local-runtime observation on the recorded RTX 3050 Laptop GPU (4 GB), not a capability score.
