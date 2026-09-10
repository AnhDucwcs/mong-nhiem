# MN-004 Gate B v5 — final bounded efficacy contract

## Status and historical boundary

**v5 measurement contract frozen / v5 implementation pending.** V5 is the final, bounded efficacy attempt for the unchanged Gate A globally indexed state-transition ledger. It does not reopen or modify [Gate A](gate-a-hypothesis.md); Gate B v1, v2, v3, or v4; any previous definition; the immutable inventory; retained preflight; historical runs; reports; fingerprints; or verdicts.

V1 remains `contract_not_executable`; v2 remains `invalid_comparison`; and v3 remains `infrastructure_failure`, with a high-confidence treatment-coupled runtime failure postmortem. V4 retained a blocked `environment_contaminated` preflight and then a clean operational run in which both persistent-server 8k phases completed 24/24 requests. V4 is operational evidence only; it does not provide efficacy evidence. No v3 or v4 response, score, provisional ledger output, or diagnostic may enter a v5 denominator. V5 produces fresh evidence only after this contract and its implementation are locally committed.

## Question, estimand, and bounded claim

> On the matched 8,192-level State Tracking workload, does the frozen globally indexed state-transition ledger improve exact final-state reliability for Llama 3.2 3B relative to the frozen natural-language representation under the same pinned runtime, while remaining within the frozen no-harm margins at the 2,048 Llama reference and Qwen 8k control?

The primary estimand is exact final-state reliability at requested level 8,192. Qwen is regression/no-harm control only, never an improvement subject. V5 may support only the specified 8k Llama representation/workload claim and, if earned, Qwen performance within the predeclared no-harm margin. It cannot support 16k improvement, a general long-context solution, model-general effectiveness, token-independent fixed-field causality, memory-architecture validation, Qwen improvement, or production promotion.

## Frozen intervention, inventory, and runtime

Treatment remains exactly Gate A: for each source event in global chronological order, emit exactly one ASCII row `event=<positive decimal index> | entity=<original entity identifier> | new_state=<original state token>`. Indexing begins at 1 without zero padding. Entity and state fields are copied exactly. There is no grouping, target marker, summary, current/final field, answer calculation, natural-language-log duplication, event removal, event reordering, target relocation, or token equalization. Untreated rendering remains the frozen `State update: ENTITY changed to STATE.` form.

V5 reuses the immutable inventory only: Llama uses the retained 24 cases at 2,048 followed by the same retained 24 cases at 8,192; Qwen uses those 24 retained 8k cases. The inventory fingerprint and all selected row hashes must match retained authority. No case regeneration, replacement, resizing, alternate seed, or custom level is permitted.

The Llama 3.2 3B and Qwen3-4B artifact SHA-256 values, llama.cpp backend/version/build/commit, configured context `16,896`, output allowance `16`, temperature `0`, frozen seed, threads, batch size, parallel slots, Flash Attention, prompt-cache policy, tokenizer, chat-template kwargs, and GPU/driver target are pinned exactly to v3/v4 authority. V5 must not alter a resource parameter, reduce prompt size, enlarge context, change decoding, add filler, or change CUDA settings.

## Validity and outcome taxonomy

### Protocol invalidation

Input/context overflow; actual source-event truncation; missing, added, reordered, duplicated, or modified events; target marking; answer leakage; semantic/source/prompt-hash mismatch; model/runtime/decoding/evaluator mismatch; prompt-token-accounting mismatch; or missing required audit metadata means the frozen condition was not executed. Such a row is excluded from scientific denominators; any required-condition protocol invalidation yields `invalid_comparison`, with no selective removal.

### Infrastructure failure

Startup failure, process crash, CUDA OOM, timeout, connection reset/refusal caused by runtime failure, or other execution failure preventing a response is `infrastructure_failure`, not an answer. A canonical phase fails fast at its first infrastructure failure: retain that request's attachment and issue no residue requests or retries. A required phase infrastructure failure yields `infrastructure_failure`.

### Valid model-output failure

`incorrect_state`, `malformed_response`, and `finish_reason == "length"` are valid observed denominator rows scoring zero. The last is `output_token_limit_reached`, with `output_limit_reached: true`, `input_truncated: false`, `evaluation.passed: false`, score `0.0`, and valid validator status. Output-limit termination is never called input truncation.

## Environment qualification and operational safeguards

Before each canonical phase retain GPU identity, VRAM/utilization, and active compute processes. An unexpected non-experiment GPU compute process at phase start is `environment_contaminated`: retain a zero-server-start, zero-request blocked preflight and do not count it as a canonical attempt. Do not kill unrelated processes; a later, separately user-initiated clean invocation may perform the one canonical phase. Desktop activity not exposed as compute use is retained as a limitation, not automatic contamination.

Each canonical phase uses a fresh llama-server process. Before a next phase, verify the preceding server is gone and capture a new resource baseline. Retain PID, command, ready and exit timestamps, exit code when available, health, stdout/stderr; per request retain ordinal, case, prompt tokens, event/target diagnostics, start/end time, latency, raw/full response, and before/after GPU snapshots. On a first infrastructure error attach stderr tail, process poll/exit state, health, GPU snapshot, error, and timestamp. Exact-answer outcomes never alter lifecycle handling.

## Frozen execution order

1. Offline authority, inventory, semantic-pair, retained-feasibility, runtime, telemetry, and implementation validation.
2. Clean-environment preflight.
3. Fresh-server Llama 8k natural-language reproduction on exactly six frozen ECC-006 cases. All rows must be protocol-valid and infrastructure-complete and score exactly `0/6`. Otherwise record `baseline_drift` and stop v5; valid model-output failures remain denominator observations.
4. Fresh-server Llama untreated phase: 24 retained 2k cases, then 24 retained 8k cases, in that deterministic order.
5. Only after a complete valid untreated phase, fresh-server Llama ledger phase on the identical 48 rows in the identical order.
6. Apply Llama verdict mechanically.
7. Only after a complete valid Llama pair, fresh-server Qwen untreated 8k on the 24 retained cases. Eligibility is at least `20/24`; otherwise record `control_not_qualified` and do not run Qwen ledger.
8. Only if eligible, fresh-server Qwen ledger 8k on the identical 24 rows. Qwen no-harm requires ledger passes at least untreated passes minus `2`; a larger drop is `qwen_regression`.
9. Retain a canonical report and update state documentation. No v6 or intervention redesign is authorized automatically.

## Frozen Llama rules and precedence

Let `U8` and `L8` be fresh exact passes out of 24 at 8k, and `D8 = L8 - U8`. Bounded support requires a valid completed pair, `L8 >= 12/24`, and `D8 >= +8/24`. Otherwise a valid primary pair is `unsupported_no_effect_or_insufficient_effect`.

Let `U2` and `L2` be fresh exact passes out of 24 at 2k. The reference no-harm rule is `L2 >= U2 - 2`; a violation is `llama_reference_regression`. A 2k gain never broadens the efficacy claim.

Overall Llama precedence is: (1) protocol invalidation, `invalid_comparison`; (2) infrastructure failure, `infrastructure_failure`; (3) reproduction mismatch, `baseline_drift`; (4) 2k reference regression, `llama_reference_regression`; (5) complete primary pair satisfying both 8k thresholds, `supported_under_bounded_claim`; otherwise `unsupported_no_effect_or_insufficient_effect`. These thresholds are not statistical-significance claims.

## Evidence and reporting

Retain paired exact-score and diagnostic transitions, but only as secondary diagnostics. The report must show every denominator count, score, failure class, output-limit count, token distribution/delta, latency, resource snapshots, lifecycle status, and Qwen eligibility/no-harm outcome if reached. It must state separately that operational completion is not efficacy and that an operational failure is not negative efficacy.

After a valid v5 result, MN-004 is complete for this frozen Gate A hypothesis: do not tune the ledger, thresholds, cases, or create v6. If v5 stops for protocol or infrastructure reasons, retain that outcome without automatic redesign.
