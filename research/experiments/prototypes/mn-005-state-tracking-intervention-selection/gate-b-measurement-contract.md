# MN-005 Gate B — Multi-pass Reconstruction measurement contract

## Status and authority

**Gate B is frozen.** This contract operationalizes the frozen [Gate A hypothesis](gate-a-hypothesis.md) for a single bounded Llama 3.2 3B / ECC-006 8k experiment. It authorizes neither measured inference nor a claim of efficacy. Gate C may implement only this contract and may not alter its causal question, control, sample policy, thresholds, or runtime policy.

Authority is the immutable ECC-006 definition/cases fingerprint `37f2dc1cc4cdfbf4a667c54f159bbd5203918f85f4d39001fa62ffcba379ac2e`, its six frozen 8,192-level source cases, and the retained Llama 3.2 3B runtime identity. MN-004 is historical evidence and a source of operational lessons only; none of its inventory, outputs, scores, thresholds, or evidence enter an MN-005 denominator.

## Objective, estimands, and claim boundary

The primary estimand is paired exact final-state correctness for Arm C versus Arm B on the six frozen ECC-006 cases at requested level 8,192. The primary unit is one paired B/C final-answer outcome for one frozen case. A fresh Arm A result is a system-level compatibility check, not causal evidence for the reconstruction artifact.

If the primary rule is met, the sole supported claim is:

> In the frozen Llama 3.2 3B / ECC-006 8k region, a literal target-aware model-generated reconstruction artifact contributed to exact final-state selection beyond the matched two-call/source-rereading active control.

No result establishes decomposition independently of all computation, broad long-context reasoning, cross-model effectiveness, external memory, external state management, architecture efficiency, or general mutable-state reliability.

## Frozen workload and arms

The primary workload is exactly the six ECC-006 case IDs `ecc006-001` through `ecc006-006`, rendered at requested level 8,192 by the immutable ECC-006 composition rule. The source event sequence, midpoint placement, entity names, state tokens, target, original question, and exact evaluator are unchanged. No MN-004-added cases, regenerated cases, alternate context level, replacement case, or historical output is allowed in a primary denominator.

### Arm A — direct single-pass compatibility baseline

Arm A makes one fresh call per case with the exact inherited ECC-006 user content:

```text
Context event log:
{unchanged ECC-006 rendered source events}

Question:
What is the current state of {exact target entity}? Return only the state.
```

It has no intermediate artifact and uses the frozen exact final-answer evaluator. All six Arm A calls are newly executed; historical ECC-006 scores are context only. Arm A must reproduce `0/6` for the experiment to earn a supported or unsupported primary conclusion. A different valid Arm A score is `baseline_drift` and yields `inconclusive`, not a reason to alter the contract.

### Arm B — two-call active control

Arm B uses two independent requests for each case. Stage A receives the unchanged source and the exact original question above, followed by this fixed instruction:

```text
Stage A instruction:
Do not answer the question. Do not use, restate, summarize, retrieve, rank,
classify, or reason about the event log or question. Output exactly these four
lines, in this order, with no surrounding text:
pad=KAPPA LAMBDA MU NU XI OMICRON PI RHO
pad=KAPPA LAMBDA MU NU XI OMICRON PI RHO
pad=KAPPA LAMBDA MU NU XI OMICRON PI RHO
pad=KAPPA LAMBDA MU NU XI OMICRON PI RHO
```

The vocabulary is fixed before measurement and contains no source event text, entity identifier, state token, target identifier, expected answer, ordinal, or ordering reference. Four fixed rows match the known target-update row count structurally, but do not encode source order. This deliberately uses a fixed four-row grammar rather than dynamically matching treatment text, characters, tokens, or observed outputs. Its target tokenizer size is established only from this fixed text during preflight; it must never be altered to match Arm C behavior.

Stage B receives the unchanged source, then exactly this UTF-8 envelope, then the unchanged original question:

```text
Context event log:
{unchanged ECC-006 rendered source events}

Intermediate artifact (literal, unmodified):
<artifact>
{literal raw Stage A UTF-8 bytes}
</artifact>

Question:
What is the current state of {exact target entity}? Return only the state.
```

The host inserts the raw Stage A byte sequence without normalization, parsing, escaping, trimming, row selection, repair, or semantic inspection. The Stage B artifact-slot byte hash must equal the retained Stage A output byte hash. Stage B returns the final answer only under the inherited evaluator.

### Arm C — Multi-pass Reconstruction treatment

Arm C also uses two independent requests per case. Stage A receives the unchanged source and the exact original question, followed by this fixed instruction:

```text
Stage A instruction:
Do not answer the question. Transcribe every source state-update event for the
queried entity in original source order. Output exactly four lines and nothing
else. Each line must be:
entity={exact queried entity identifier} | state={exact assigned source state}
Do not include an ordinal, current, latest, final, answer, summary, conclusion,
or any derived state.
```

The intended artifact carries only unchanged entity identifiers and assigned state tokens; row position represents source order. An explicit ordinal may be copied only if the frozen source itself supplies one, which ECC-006 does not. Stage A mistakes, extra text, omissions, non-target rows, prohibited fields, or truncation remain literal model outcomes.

Stage B uses the exact same envelope, raw source, question, final-answer instruction, evaluator, and byte-preservation rule as Arm B. It receives no session, conversation, KV, or hidden state from Stage A.

## Shared prompt, completion, and host protocol

All calls use the inherited Llama chat template with exactly one `user` message and no system, assistant, tool, developer, or hidden message. The model-specific chat-template kwargs remain `{}`. The raw source is always first; the Stage A instruction is appended after the unchanged question, and the Stage B literal artifact is placed after the source and before the unchanged question as specified above. No cosmetic renderer freedom may change labels, delimiters, source placement, question text, instructions, or artifact location.

Arm A and every Stage B request use `max_tokens=16`. Every Arm B/C Stage A request uses `max_tokens=64`; its scheduled maximum is equal across B and C. No stop sequence is used. No retry, continuation, self-correction prompt, output repair, or alternate prompt is allowed. `finish_reason == length` is a valid model outcome, not input truncation.

The host is transport-only. It may assemble fixed text, preserve raw bytes, send the next request, count tokens, and record evidence. It must not access an expected answer while assembling prompts; parse Stage A before Stage B; determine reconstruction correctness; filter, reorder, correct, summarize, or replace output; select evidence or state values; or calculate a final state. Stage A diagnostics may be computed only after the literal Stage B request and its provenance record have been finalized.

## Case, sampling, and execution policy

Each of the six frozen 8k cases is measured exactly once in each arm. Temperature `0` and seed `42` retain ECC-006's deterministic setting; no alternative seed, stochastic sampling, or replicate block is authorized. Repeating deterministic calls would not create new semantic cases or statistical sample size, so it is not used to enlarge the denominator.

Arm A runs first in canonical case-ID order and must complete validly at `0/6`. Then, for each case in canonical order, Arms B and C run as an adjacent paired unit. The B/C order alternates by case to balance immediate order: `B,C` for `ecc006-001`, `C,B` for `ecc006-002`, continuing alternation through `ecc006-006`. Each arm/case pair uses its own fresh server process; the server must be stopped and verified gone before the other arm for that case begins. Its Stage A and Stage B are separate fresh API requests with prompt cache, session identifiers, and conversation continuity prohibited.

This schedule produces 6 Arm A calls, 12 Arm B calls, and 12 Arm C calls. The six paired Stage B outcomes—not the 30 requests—form the primary denominator.

## Runtime and environment comparability

The subject remains `Llama-3.2-3B-Instruct-Q4_K_M.gguf` with SHA-256 `6c1a2b41161032677be168d354123594c0e6e67d2b9227c84f296ad037c728ff`. The runtime is pinned to retained ECC-006/MN-004 authority: llama.cpp `0.2.0-dev`, build `10566`, commit `bb4caa754`; configured context `16,896`; threads `12`; batch size `2,048`; parallel slots `1`; Flash Attention on; prompt cache off; temperature `0`; seed `42`; Jinja chat template; empty chat-template kwargs; and the retained RTX 3050 Laptop GPU / driver `595.95` target.

No top-p, top-k, min-p, repeat-penalty, grammar, logit bias, or stop parameter may be added to the inherited request configuration. Their absence is part of the frozen request; the pinned runtime's effective defaults must be captured in runtime metadata. GPU offload, server command, port, CPU/GPU settings, model file, tokenizer, cache policy, and server configuration must match the retained runtime authority or the affected experiment is invalid. Any permitted infrastructure cache must be disabled or demonstrably identical; it must never preserve request/KV/session state between Stage A and B.

Before Arm A and before every B/C arm/case server process, capture GPU identity, free/used VRAM, utilization, active compute processes, server command/PID, server readiness, and runtime identity. An unexpected non-experiment GPU compute process blocks that unit as `environment_contaminated`; it causes no server start and no canonical request. Do not kill unrelated processes. A clean later invocation is a new prospective attempt, not a retry.

## Endpoint and Stage A diagnostics

The sole primary endpoint is exact Stage B final-state correctness under ECC-006's frozen accepted-answer set: the exact state token or `The current state of <exact target entity> is <exact final state>`, after the inherited deterministic normalization. Every malformed Stage B answer, wrong state, or Stage B output-limit termination scores zero in the primary denominator.

For Arm C, retain post-run-only diagnostics for format validity; emitted row count; target-event recall; omitted target events; non-target insertions; duplicate rows; source-order correctness; entity-token accuracy; state-token accuracy; full exact transcription; prohibited-field emission; and output-limit termination. Arm B receives analogous artifact-format/length observations but no semantic source comparison is needed. Diagnostics may use frozen source truth only after Stage B has received the unchanged literal artifact; they may never repair or alter an input.

## Primary support and result classes

For each case `i`, let `B_i` and `C_i` be its valid binary Stage B exact scores. Let `n10` count pairs where `B_i=0, C_i=1`, `n01` pairs where `B_i=1, C_i=0`, and `D = sum(C_i - B_i)`.

`supported` requires all of the following:

1. all six Arm A, B, and C case outcomes are protocol-valid and infrastructure-complete;
2. Arm A freshly reproduces `0/6`;
3. `sum(C_i) >= 4/6`, `n10 >= 4`, `n01 = 0`, and therefore `D >= +4/6`; and
4. every `B_i=0, C_i=1` transition has a Stage C artifact that is a full exact four-row target transcription with no prohibited field or non-target row.

This requires a treatment benefit on at least two thirds of the frozen failure region and eliminates a treatment regression. It is a conservative bounded decision rule, not a statistical-significance claim.

`unsupported` requires a complete protocol-valid and infrastructure-complete experiment, fresh Arm A `0/6`, and `D <= 0`. It weakens the priority of explicit target-aware reconstruction in this region but does not reject multi-pass methods generally.

`inconclusive` applies to a complete valid experiment with Arm A baseline drift, a positive `D` of only `+1` through `+3`, any C improvement whose contributing Stage A artifact fails the clean-transcription condition, or another valid outcome that meets neither rule. No threshold may be relaxed after results exist.

`experiment_invalid` applies only to an attempt with a required protocol invalidation or infrastructure failure. It is not a zero score, cannot contribute to efficacy denominators, paired counts, or support thresholds, and must never be labelled `unsupported` or `inconclusive`. The retained report must identify whether the failure invalidates an individual request, paired case unit, Arm A phase, or the complete attempt; any missing required pair invalidates the complete primary comparison.

Only the first fully protocol-valid and infrastructure-complete attempt can receive efficacy interpretation. Within that canonical attempt, fresh Arm A baseline drift remains `inconclusive`, not `experiment_invalid`; ordinary model failures remain scored outcomes and never justify a rerun.

Arm C versus Arm A is reported separately as system-level context. It cannot convert an otherwise unsupported or inconclusive C-versus-B result into support.

## Reference/no-harm and resource policy

No 2k reference or Qwen condition is included. This experiment tests a bounded 8k procedural mechanism on the known ECC-006 failure region; a lower-context condition would add calls and a different question without increasing the primary causal identification. It is neither a support criterion nor an omitted safety claim. Any future efficiency, lower-context regression, cross-model, or promotion evaluation requires a separate contract.

For every call retain prompt, completion, and total tokens; configured context; Stage A or B role; call count; start/end timestamps; per-stage latency; end-to-end pair latency; model/runtime/environment data; and response finish reason. For B/C, report Stage A and Stage B separately plus pair totals. The fixed 64-token Stage A budget, fixed control grammar/tokenizer target size, actual B and C Stage A completion tokens, and resulting B/C Stage B prompt tokens are distinct mandatory fields.

Context fit, complete accounting, and absence of source truncation are hard validity gates. Token count, latency, and resource consumption are descriptive evidence only in this Gate B; no efficiency threshold can produce support, and an efficiency cost cannot erase a valid efficacy result. It must nevertheless be reported because MN-004 showed that representation-related token inflation can create operational failures.

## Failure, retry, and invalidation policy

Valid model outcomes remain scored observations: `incorrect_state`, `malformed_final_response`, `stage_a_malformed`, `stage_a_incomplete`, `stage_a_wrong_transcription`, `stage_a_non_target_insertion`, `stage_a_prohibited_field`, and either stage's `output_token_limit_reached`. A Stage A failure never authorizes host correction; its literal output remains Stage B input if the Stage B context fits.

Protocol failures include source/question/template/evaluator mismatch; changed target availability; source deletion, duplication, reordering, or truncation; nonliteral Stage A transport; expected-answer access; host semantic work; active-control source/state/target/order content; changed control grammar; changed threshold; forbidden cache/session continuity; model/runtime/decoding mismatch; missing required fingerprint/accounting; or a Stage B prompt that cannot fit without truncation. Any such required-condition failure invalidates the complete causal comparison.

Infrastructure failures include startup/health failure, crash, CUDA OOM, timeout, connection failure, transport truncation, and unavailable runtime. They fail fast at the first occurrence: retain request/response state, server logs, telemetry, and error details; issue no residue requests or retries; and mark the attempt invalid.

### First-valid-attempt canonicalization

Every prospective execution attempt must receive an immutable, monotonically ordered `attempt_id` and a timestamped identity before its first request. Attempt order determines eligibility; no score, Stage A quality signal, or apparent result may influence selection. A protocol-invalid or infrastructure-incomplete attempt is permanently retained as `experiment_invalid`, but is excluded from all efficacy denominators, support thresholds, and paired outcome counts.

After an invalid attempt, the next prospective attempt may occur only after the recorded failure has been diagnosed and corrected without changing this frozen causal contract. Permitted repairs are limited to conformity fixes such as a server startup or unavailable-runtime problem, connection or transport failure, OOM caused by unintended environmental contamination, broken evidence logging, or an implementation bug that violated the frozen prompt contract. They must not change an arm definition, prompt semantics, placeholder grammar, sampling or case policy, runtime configuration, support threshold, active-control policy, evaluator, output budget, or execution-order policy. Any such design change requires Gate B to be explicitly reopened through a new documented research decision before further efficacy execution.

The first subsequent attempt that is fully protocol-valid and infrastructure-complete automatically becomes the canonical efficacy attempt and receives the `supported`, `unsupported`, or `inconclusive` interpretation. Once it exists, no later rerun may replace it because Arm A/B/C scores are undesirable, Stage A quality is weak, or a later outcome appears favorable. Later executions require separately authorized replication or a new contract and may not be substituted into the original Gate B result. The prohibited pattern is `attempt 1 invalid -> attempt 2 valid but weak -> attempt 3 stronger -> choose attempt 3`; the required behavior is `attempt 1 invalid -> attempt 2 valid -> attempt 2 is canonical`, regardless of outcome.

## Provenance and preflight

Gate C must retain an immutable definition fingerprint and case/source fingerprints; per-case arm and scheduled order; model and runtime fingerprints; complete request payloads; Stage A raw UTF-8 bytes and hash; Stage B prompt and artifact-slot byte hash; proof of equality between those hashes; raw Stage B response; evaluator input/output; token and latency fields; seed; timestamps; server/environment logs; retries (which must be empty for a canonical attempt); and failure/diagnostic classifications. Retain every attempted canonical record, including failures; no MN-005 run directory, schema, or output is created by this Gate B document.

Before measured inference, Gate C must complete a non-efficacy preflight that validates frozen source and template fingerprints, all delimiter/byte-transport invariants, active-control grammar, evaluator compatibility, runtime identity, clean environment, and evidence-log completeness. A tokenizer-only preflight must count every assembled static Arm A/B/C Stage A prompt, the fixed Arm B Stage B prompt, and conservative Stage C Stage B capacity using the 64-token Stage A allowance; every actual C Stage B prompt must also be counted before submission and fit with its 16-token completion allowance. It may not alter the frozen grammar, budgets, or thresholds.

No inference-based behavior preflight is required or authorized by this contract. If Gate C later needs an infrastructure smoke test, it must be separately labelled noncanonical, use no ECC-006 case or efficacy scoring, retain its output, and never change this contract or choose a control based on behavior. Measured execution may begin only after the static/tokenizer/environment preflight passes.

## Gate C entry criteria and decision

Gate C may begin implementation only when deterministic prompt construction, literal UTF-8 artifact transport, all frozen fingerprints, the fixed active-control grammar, case/schedule policy, runtime configuration, exact evaluator, support rules, failure/retry policy, and evidence retention are implemented without deviation. Measured execution requires the completed preflight above and no unresolved causal ambiguity.

Gate B is complete and frozen. Gate C implementation is authorized for this exact contract; no measured model work is authorized by this document alone.