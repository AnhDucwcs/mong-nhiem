# ECC-007 — Causal Reasoning under increasing context length

ECC-007 is the MN-003 direct-context causal-reasoning baseline. It tests whether Qwen3-4B can answer a deterministic two-hop causal-reachability question as irrelevant, same-template causal edges increase from 512 to 16,384 requested input tokens. It does not test or select retrieval, RAG, memory, summarization, compression, routing, embeddings, semantic search, or another architecture.

The frozen workload has eight independent graphs: four reachable (YES) and four unreachable (NO). Each target graph is exactly two hops; all distractors are unique disconnected causal edges in the same `Causal link: X causes Y.` template. The target graph is placed at the feasible token-relative midpoint (0.50 plus or minus 0.05). The only canonical independent variable is requested input-token length: 512, 2,048, 8,192, and 16,384. The runner measures actual model prompt tokens, reserves 16 output tokens within the 16,896-token runtime context, and rejects overflow rather than truncating.

Before freezing the definition, calibration evaluated four positive/negative-balanced examples at each of two and three hops, at the 512-token anchor. Qwen3-4B passed 4/4 for both. The frozen selection rule chooses the simplest non-floor candidate reaching 0.75, so ECC-007 uses two hops. Llama 3.2 3B produced zero exact YES/NO responses at both candidates under the identical 16-token response contract; this is retained as an output-format floor, not a comparison of causal difficulty.

The evaluator normalizes only case, whitespace, and terminal punctuation, then requires the exact expected `YES` or `NO`. Raw response, normalized response, graph, token counts, request/response, timing, and failure type are retained. The offline validator replays construction, independently verifies reachability and graph uniqueness/non-leakage, checks hashes and budget/placement contracts, and recomputes summaries.

Run a smoke subset with `python scripts/run_ecc007.py --model qwen3-4b --context-level 512 --case-limit 2`. Run canonical coverage with `python scripts/run_ecc007.py --model qwen3-4b`; validate retained evidence with `python scripts/validate_ecc007.py runs/<run-id>`.

See [calibration](calibration/README.md), the frozen [definition](definition/experiment.json), and the retained [results report](reports/ecc-007-results.md).
