# Current state

## MN-001 — completed

MN-001 established the source layout, canonical research knowledge base, minimal packaging, pytest/Ruff checks, CI, and a package-import smoke test.

## MN-002 — Model Qualification — completed and frozen

MCB v0.1.0 and v0.2.0 remain historical/superseded evidence. Re-evaluation of v0.2 failures under the frozen v0.3 accepted-answer contract converts 143 previously failing semantic-suite outputs into accepted output-equivalence cases; 56 semantic-suite failures remain failing under the corrected deterministic evaluator.

MCB v0.3.0 is the canonical frozen qualification benchmark. Its fingerprint is `2ac24df4e6cca12e13da577fb48db5da8e39d89cf3646ef705ea7679b4548f7a`. It contains 100 cases across Instruction Following, Structured Output, Context Retrieval, State Tracking, and Causal Reasoning. Six local GGUF candidates were measured. Llama-3.2-3B-Instruct-Q4_K_M and Qwen3-4B-Q4_K_M meet every capability gate and are the qualified capability baselines. Capability qualification and runtime performance are separate evidence.

This qualification is not a production-model choice and does not validate an ECC, retrieval, memory, RAG, summarization, compression, routing, or context-management mechanism.

## MN-003 — Effective Context Capacity — active baseline research

MN-003 is a bounded prototype under `research/experiments/prototypes/`. ECC-001 defines deterministic single-fact Context Retrieval across a 512–16,384 requested-token ladder using direct, unmodified context, fixed midpoint evidence, exact evaluation, model-token-aware construction, explicit schemas, a canonical runner, and an offline validator. Its canonical definition fingerprint is `d9c86595d84266dcc87becc4469bf5a1ed691a4cadbf30ef620d4ac8983efa29`.

Both MN-002-qualified capability baselines were measured from clean commit `701fb1fe417bde7db6f4749479955c37a734616d`. Llama 3.2 3B and Qwen3-4B each passed all 20 cases at every tested level: baseline accuracy 1.00, relative accuracy 1.00 throughout, zero invalid results, and ECC95/ECC90/ECC80 of 16,384 under the contiguous-tested-prefix rule. This is a tested lower bound, not a located failure boundary, advertised-window validation, or production-model selection.

ECC-002 adds a frozen confusable-record variant with the same direct-context ladder and controls: target and distractors share one natural registry-entry template, target evidence remains unmarked at the midpoint, and entity/code uniqueness plus non-leakage are validated deterministically. Its canonical definition fingerprint is `824ba4d6df62f8ddf4a49d90a2e2d4d44211399c730c831f2bf0338ba8e5c7cf`. Both qualified models produced valid clean-worktree evidence (120 results each). Llama 3.2 3B declined monotonically from 1.00 at 512 to 0.85 at 16,384 requested tokens: ECC95 = 4,096, ECC90 = 8,192, and ECC80 >= 16,384 tested tokens (right-censored). Qwen3-4B remained 1.00 through 16,384, so ECC95/ECC90/ECC80 are all right-censored lower bounds >= 16,384 tested tokens. See the retained [ECC-002 results](experiments/prototypes/mn-003-effective-context-capacity/experiments/ecc-002-confusable-context-retrieval/reports/ecc-002-results.md).

MN-003 remains active. ECC-002 finds a measurable direct-context limitation for one qualified baseline, but it does not identify a cause or select a remedy. The next research definition should remain direct-context and isolate one additional task-pressure dimension or harder inherited capability before any architecture intervention. Retrieval, memory, RAG, summarization, compression, and context-routing work remain out of scope.
