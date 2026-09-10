# MN-004 Gate B v3 — output-failure taxonomy correction

## Status and historical boundary

**v3 measurement contract frozen / v3 implementation pending.** V3 is a minimal correction to the validity and failure taxonomy after v2 closed at `invalid_comparison`. It does not modify [Gate A](gate-a-hypothesis.md), [Gate B v1](gate-b-measurement-contract.md), [Gate B v2](gate-b-v2-measurement-contract.md), their definitions, immutable inventory, preflight evidence, runs, reports, fingerprints, or verdicts.

V1 remains `contract_not_executable` at its frozen 16k scope. V2 remains permanently `invalid_comparison`; its retained untreated results are not reclassified, scored under v3, or reused for any v3 efficacy/no-harm computation. V2 evidence may be cited only as the observation motivating this taxonomy correction. V3 requires fresh canonical evidence after this contract and its implementation are committed.

## Sole change: distinct execution categories

V2 conflated input/context/protocol truncation with an observed model response reaching `max_tokens=16`. V3 corrects only that distinction.

### Protocol invalidation

A row is protocol-invalid if the frozen requested condition was not actually executed: input/context overflow; source-event truncation; missing, added, reordered, duplicated, or modified event; target marking; answer leakage; semantic-pair, prompt-hash, or source-hash mismatch; evaluator, model artifact, runtime identity, decoding, inference-parameter, or prompt-token-accounting mismatch; incomplete required audit metadata; or another condition-changing violation.

Protocol-invalid rows are not scientific evidence. Any protocol invalidation in a required condition produces `invalid_comparison`; no row may be discarded selectively.

### Infrastructure failure

Server startup/crash, HTTP/request failure, timeout, or operating/runtime failure preventing a response is `infrastructure_failure`, not a model scientific failure. Failed attempts must be retained. The frozen canonical policy is to stop v3 at any infrastructure failure during a required phase; no individual-row retry policy exists.

### Model-output failure

The following are valid observed model outcomes and score zero without invalidating a condition: `incorrect_state`, `malformed_response`, and reaching the frozen generation allowance (`finish_reason == "length"`). The last is recorded as `output_token_limit_reached`, with `output_limit_reached: true`, `input_truncated: false`, `evaluation.passed: false`, `evaluation.score: 0.0`, and `validator_status: valid`. Raw output and the full response are retained. Malformed output follows the same valid-zero rule when the request itself was valid.

`input_truncated` and `output_limit_reached` are separate fields; the ambiguous term `truncation` is not used as a model-output failure class.

## Unchanged scientific contract

Everything else is inherited unchanged from v2: the globally indexed state-transition ledger; the immutable v1 inventory; renderers; source events/order/target placement; questions and expected answers; evaluator; Llama/Qwen artifact SHA-256 values; llama.cpp version/build/commit; 16,896 context; `max_tokens=16`; decoding, seed and repetition policy; preflight/token accounting; no filler, resizing, context enlargement, relocation, source removal, duplicate log, or answer precomputation.

The primary workload is the same 24 paired 8,192 cases, with the same historical ECC-006 8k `0/6` reference. A fresh Llama six-case untreated reproduction is compatible only when every request is protocol-valid and infrastructure-complete and exact score is `0/6`; valid model-output failures remain in the denominator. Otherwise record `baseline_drift` and stop treatment.

After compatible reproduction, run 24 Llama untreated and 24 ledger cases at 2k and 8k. The unchanged 8k efficacy rule is valid comparison plus ledger `>= 12/24` and ledger-minus-untreated `>= +8/24`; otherwise the result is `unsupported_no_effect_or_insufficient_effect`. The unchanged 2k reference rule is ledger `>= untreated - 2`; violation is `llama_reference_regression`.

Qwen remains 8k regression/control only and starts only after a complete valid Llama comparison. Eligibility remains untreated `>= 20/24`; otherwise `control_not_qualified` and no Qwen ledger. If eligible, no-harm remains ledger `>= untreated - 2`; a larger drop is `qwen_regression`. Valid model-output failures count as zero for Qwen too.

## Execution, evidence, and claim boundary

The frozen order is: offline authority/semantic/preflight validation; Llama frozen 8k reproduction; Llama untreated 2k+8k; Llama ledger 2k+8k; mechanical Llama verdict; Qwen untreated 8k; Qwen ledger only if eligible; Qwen verdict; report.

Every record retains protocol-validity flags, infrastructure status, failure class, `input_truncated`, `output_limit_reached`, raw/full response, exact score, model/runtime/token evidence, and diagnostics. A report must separately show validity, infrastructure completeness, output-limit count, malformed count, incorrect-state/prior-target diagnostics, denominators, token distributions, thresholds, and bounded verdict.

A positive v3 result may support only the unchanged bounded 8k Llama ledger claim, with Qwen no-harm only if earned. It cannot support 16k improvement, token-independent fixed-field causality, a general effective-context mechanism, model-general improvement, Qwen improvement, or architectural promotion. V3 stops after reporting; no v4 or intervention redesign is implied.
