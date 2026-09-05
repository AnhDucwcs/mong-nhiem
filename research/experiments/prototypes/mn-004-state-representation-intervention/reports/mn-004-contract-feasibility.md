# MN-004 Gate C contract-feasibility report

## Verdict

`contract_not_executable` / `invalid_comparison` before measured inference.

The frozen source inventory and both frozen renderings were materialized and tokenized with the pinned llama.cpp runtime, configured context window (16,896), and output allowance (16). The Gate B hard rule prohibits truncation, source reduction, replacement cases, filler, or a changed context limit. No completion request was therefore permitted or sent.

## Retained preflight evidence

- Definition fingerprint: `bf5d51e3036128e94fa26a9e406c836fb06bd5f0c22cf46204c13dbccb842bfb`.
- Materialized inventory fingerprint: `7183de0be8813764087e77330c5758970d40dfc9fe8553637faccca027d17897`.
- Llama preflight: 24 ledger overflows at 16,384; examples range from 22,525 to 22,583 prompt tokens before the 16-token output allowance.
- Qwen preflight: 48 overflows at 16,384: all 24 natural-language prompts and all 24 ledger prompts. Qwen tokenization is not semantically comparable to the Llama-sized source construction at that requested level.

The full inventory and per-pair token/position records are retained in `../definition/source-inventory.json`, `../definition/preflight-llama-3.2-3b.json`, and `../definition/preflight-qwen3-4b.json`.

## Consequences under the frozen contract

This is not a Llama efficacy verdict, a negative treatment result, a baseline-drift result, or a Qwen regression result. The contemporaneous Llama reproduction, Llama untreated/treatment phases, and Qwen eligibility/treatment phases were not run because Gate B declares condition-specific truncation or context overflow invalid. The experiment cannot support any claim about ledger effectiveness or Qwen no-harm.

No contract field was changed after preflight. Any future redesign requires a new authorized design gate rather than modifying this frozen comparison.
