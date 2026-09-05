# MN-004 Gate B v4 — runtime-feasibility contract

## Status and historical boundary

**v4 contract frozen / v4 implementation pending.** This is an operational-feasibility study prompted by the retained v3 `infrastructure_failure`. It does not reopen or modify Gate A; Gate B v1, v2, or v3; any prior definition or inventory; retained preflight; historical runs; reports; fingerprints; or historical verdicts.

V1 remains `contract_not_executable`; v2 remains `invalid_comparison`; and v3 remains `infrastructure_failure`. V3's incomplete ledger outputs are not efficacy evidence and must not be reused as v4 outputs. V4 creates fresh evidence only after this contract and its implementation are committed.

## Question, estimand, and claim boundary

> Under the pinned Llama 3.2 3B artifact, llama.cpp runtime, 16,896-token context, decoding configuration, and immutable MN-004 8k source cases, does the frozen globally indexed ledger reproduce the runtime/resource failure observed in v3 relative to contemporaneous natural-language execution with the same telemetry and server lifecycle?

The estimand is **operational execution stability**: request completion, server/process survival, CUDA/ggml runtime behavior, and observed resource pressure. It is not exact final-state reliability. Raw model responses are retained only for audit integrity; exact-answer scoring, model-output content, malformed outputs, and output-token-limit termination do not decide a v4 operational verdict.

V4 may support only bounded statements about this representation package's execution feasibility in the pinned environment, including per-request versus persistent-server behavior where the predeclared diagnostics distinguish them. It may not support an efficacy claim, a Qwen claim, 16k efficacy, token-independent fixed-field causality, general effective-context improvement, or architecture promotion.

## Frozen invariants

V4 uses exactly the Gate A globally indexed state-transition ledger and the retained natural-language renderer. It reuses the immutable 24 source cases at requested level 8,192 only, in retained inventory order, with identical event order, target identity/indexes, distractors, questions, expected answers, tokenizer, and retained token accounting.

It pins the Llama 3.2 3B artifact/hash; llama.cpp version, build, and commit; context `16,896`; output allowance `16`; temperature, seed, prompt-cache policy, batch, parallel-slot, thread, flash-attention, and chat-template settings; GPU target; and driver environment. V4 must not resize the workload, alter events or rendering, move targets, add filler, enlarge context, lower runtime resource settings, change CUDA settings, change decoding/output allowance, or run Qwen.

## Outcome taxonomy

- `untreated_environment_failure`: the natural-language Stage A control has an infrastructure, process, CUDA/ggml, or resource failure. Stop; do not run ledger.
- `ledger_runtime_failure_reproduced`: Stage A completes, then persistent-server ledger Stage B has a CUDA OOM, fatal CUDA/ggml diagnostic, server-process death, listener loss/connection reset caused by that death, or equivalent runtime failure.
- `ledger_persistent_phase_completed`: Stage A and Stage B each complete all 24 requests without infrastructure failure. This means v3's crash was not reproduced in this one attempt; it must not be called `ledger_stable`.
- `protocol_invalid`: a required frozen condition was not executed exactly, including source/prompt/token/runtime mismatch, missing audit evidence, or input/context truncation.
- `environment_contaminated`: an unexpected non-experiment compute process is using the target GPU before a canonical phase begins.
- `diagnostic_inconclusive`: required diagnostic evidence cannot distinguish the relevant resource mechanism.

Model-output content is never an infrastructure failure: a received response completes the operational request regardless of correctness, format, or `finish_reason == "length"`.

## Contamination and lifecycle policy

Before each canonical phase, record GPU identity, VRAM, and active compute processes using `nvidia-smi`. If any non-experiment compute process is present at phase start, record `environment_contaminated` and do not start that phase. Desktop/display activity not exposed as compute use is retained as an environmental limitation, not automatic contamination. V4 never kills unrelated processes.

Every Stage A, B, C1, and C2 phase uses its own fresh llama-server process. Before starting the next phase, the previous process must be terminated and absence verified; server lifecycle and GPU baseline are captured anew. Persistent-server behavior is intentionally retained **within** each phase.

## Required telemetry and fail-fast behavior

Every phase records server PID, exact command, process-start timestamp, health state, stdout/stderr, observed exit timestamp/code, and termination state. Every request records its ordinal, case ID, prompt tokens, event count, target token positions, start/end timestamps, latency, completion/infrastructure status, and raw response.

Record target-GPU name, driver, total/used/free VRAM and active compute processes before phase start, immediately before every request, immediately after every successful request, and at/after first infrastructure failure when obtainable. The same request-boundary telemetry applies to untreated and ledger; no periodic profiler is used.

At the first infrastructure error, immediately capture stderr tail, process poll/exit status, health status, GPU snapshot, error type/message, and timestamp on that first failed record; then stop the phase. No later request may be issued. A protocol-invalid row also stops its phase and makes the relevant operational comparison invalid.

## Canonical execution order

### Stage A — natural-language control

Start a fresh server and run the 24 immutable 8k cases sequentially in retained order using natural-language rendering. The sole decision metric is operational completion. An infrastructure/resource/process failure is `untreated_environment_failure`; stop v4 without ledger. Valid model-output failures remain completed requests.

### Stage B — persistent-server ledger

Only after Stage A completes, start a fresh server and run the same 24 cases, in the same order, with the frozen ledger. If all complete, record `ledger_persistent_phase_completed` and do not run diagnostics. If the first failure has the defined CUDA/ggml/process signature, record `ledger_runtime_failure_reproduced`; otherwise record `diagnostic_inconclusive` for operational mechanism analysis. Both paths fail fast.

### Stage C — predeclared conditional diagnostics

Only after `ledger_runtime_failure_reproduced`, mechanically select the first failed Stage B case `F` and its immediately preceding successful case `P`, if any.

1. **C1:** on a fresh server, run only ledger case `F` with unchanged prompt/runtime/telemetry. Equivalent CUDA/resource/process failure supports `per_request_resource_pressure`. If `F` completes, proceed to C2 only when `P` exists. A non-equivalent failure leaves the mechanism `ledger_runtime_failure_reproduced_mechanism_unresolved`.
2. **C2:** on another fresh server, run exactly `P` then `F`. If `P` completes and `F` has equivalent resource/process failure, support `short_sequence_or_persistent_state_pressure`. If both complete, record `diagnostic_inconclusive`.

No further cases, phases, alternate levels, workload changes, boundary search, or retries are authorized. C1/C2 are server-lifecycle diagnostics, not efficacy samples.

## Definition, evidence, and reporting

The separate machine-readable v4 definition must pin Gate A and v3-postmortem hashes, the immutable inventory fingerprint, authorized 8k rows, Llama/runtime identities, telemetry schema, lifecycle/contamination policy, Stage A/B/C rules, taxonomy, and fail-fast policy. Its deterministic fingerprint changes when a contract-critical field changes.

The v4 report must show operational completion, process lifecycle, first failure and preceding request when relevant, CUDA diagnostics, request/GPU telemetry, and the root-mechanism assessment. It must separately state that efficacy evidence remains unavailable.
