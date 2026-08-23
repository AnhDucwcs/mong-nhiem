# MN-002 qualification state addendum — MCB v0.3.0

This addendum supersedes the MN-002 progress statements in the prior current-state snapshot.

MCB v0.1.0 and v0.2.0 are preserved as historical evidence only. The v0.2 audit reviewed 243 failed case results. Among semantic-suite failures, 143 are output-equivalence defects and 56 are valid model failures; no fuzzy or model-judged evaluator was introduced.

Frozen MCB v0.3.0 was run across all six candidate models. Its immutable JSONL definitions have fingerprint `2ac24df4e6cca12e13da577fb48db5da8e39d89cf3646ef705ea7679b4548f7a`; the selected six run artefacts passed schema, exact-case-coverage, score-reproducibility, and fingerprint validation.

Llama-3.2-3B-Instruct-Q4_K_M and Qwen3-4B-Q4_K_M pass the deterministic capability gate. This is a qualification result, not a production-model selection or a change to the reusable `src/mong_nhiem/` architecture. Runtime-performance evidence remains a separate measurement.

See `experiments/baselines/mn-002-model-qualification/reports/model-qualification-v0.3.0.md`, `reports/mcb-v0.2.0-audit.json`, and `reports/mcb-v0.3.0-validation.json` for the reproducible evidence.
