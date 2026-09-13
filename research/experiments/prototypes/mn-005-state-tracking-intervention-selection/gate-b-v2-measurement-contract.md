# MN-005 Gate B v2 — Multi-pass Reconstruction measurement-contract repair

## Status and historical boundary

**Gate B v2 is frozen.** It is a narrowly versioned executability repair to the frozen [Gate B v1 measurement contract](gate-b-measurement-contract.md), not a replacement for it. [Gate A](gate-a-hypothesis.md), Gate B v1, and the retained [attempt-0001 invalid-experiment record](reports/mn-005-attempt-0001-invalid.md) remain immutable historical research evidence.

`attempt-0001` remains `experiment_invalid` with efficacy classification `not_applicable_due_to_invalid_experiment`. It does not support, weaken, or otherwise contribute to the Multi-pass Reconstruction efficacy result. Arm A freshly reproduced `0/6`; Arm B Stage A then reached the v1 64-token completion cap before completing the required four-row neutral artifact; Arm C did not run. The failure establishes only that Gate B v1's fixed Arm B grammar and Stage A budget were not jointly executable on the frozen subject/runtime.

Gate B v2 preserves the Gate A causal question. Its primary comparison is still Arm C versus Arm B; Arm C versus Arm A remains system-level context only. It changes only the common B/C Stage A completion cap and the preflight/request-progression requirements needed to make the existing contract executable and auditable.

## Unchanged scientific contract

The following remain exactly as frozen by Gate A and Gate B v1:

- the six frozen ECC-006 8k cases, source facts, source order, target question, final exact evaluator, one execution per case/arm, temperature `0`, and seed `42`;
- Arm A as one fresh direct ECC-006 call, and a fresh Arm A rerun in every complete prospective attempt;
- Arm B and Arm C as two fresh calls with identical source/question availability in Stage A, raw-source rereading in Stage B, and no conversation, session, prompt-cache, or KV continuity;
- literal, byte-preserved Stage A transport inside the frozen Stage B artifact envelope and the transport-only host boundary;
- Arm B's fixed four-row semantic-neutral grammar and Arm C's target-aware, source-derived four-row reconstruction semantics;
- the frozen model, llama.cpp/runtime fingerprint, context `16896`, threads `12`, batch `2048`, parallel slots `1`, Flash Attention, disabled prompt cache, no added decoding parameters, execution order, clean-environment rules, support rule, and first-valid-attempt policy.

Gate B v2 does not permit chain-of-thought, free-form analysis, answer statements, summaries, conclusions, external state computation, host repair, target-evidence retrieval, or any altered prompt semantics. Extra or prohibited Stage A content remains a model outcome; increasing the cap is solely an artifact-executability repair.

## Unchanged Arm B artifact and static sizing basis

Arm B retains exactly this UTF-8 artifact, with no trailing newline:

```text
pad=KAPPA LAMBDA MU NU XI OMICRON PI RHO
pad=KAPPA LAMBDA MU NU XI OMICRON PI RHO
pad=KAPPA LAMBDA MU NU XI OMICRON PI RHO
pad=KAPPA LAMBDA MU NU XI OMICRON PI RHO
```

The tokenizer-only static record is [gate-b-v2-artifact-sizing.json](preflight/gate-b-v2-artifact-sizing.json). Using the retained model tokenizer and chat template, it measured the exact fixed artifact at **71 completion tokens**, 163 UTF-8 bytes, and three mandatory newline bytes. The mechanically constructed ideal Arm C artifact is only a sizing oracle: it is derived from frozen source truth to count permitted output, is never supplied as treatment input, and is not efficacy evidence.

| Case | Ideal Arm C artifact tokens | UTF-8 bytes | Mandatory newline bytes | Stage B prompt tokens with ideal C artifact |
| --- | ---: | ---: | ---: | ---: |
| `ecc006-001` | 52 | 144 | 3 | 8,254 |
| `ecc006-002` | 51 | 150 | 3 | 8,250 |
| `ecc006-003` | 50 | 150 | 3 | 8,244 |
| `ecc006-004` | 53 | 141 | 3 | 8,214 |
| `ecc006-005` | 50 | 146 | 3 | 8,233 |
| `ecc006-006` | 48 | 147 | 3 | 8,208 |

The maximum ideal Arm C artifact is 53 tokens. The larger fixed Arm B artifact therefore governs the common cap.

## Repaired common Stage A budget

The v1 common Stage A cap of `64` is replaced by a common Arm B/Arm C Stage A cap of **`80`**. Arm A and every Stage B retain `max_tokens=16`.

The frozen deterministic sizing rule is:

> Let `M` be the maximum tokenizer count of the exact fixed Arm B artifact and each mechanically derived exact ideal Arm C artifact. Reserve a fixed 8-token completion margin. Select the smallest multiple of 16 that is greater than or equal to `M + 8`.

Here `M = 71`; `M + 8 = 79`; the resulting common cap is `80`. This gives the fixed control artifact nine tokens of observed headroom at the selected standard boundary. The rule is fixed before any Arm C output exists and is not derived from, matched to, or adjustable after treatment behavior.

This cap does not authorize additional content. Arm B must emit exactly the fixed grammar. Arm C must emit exactly four permitted source-derived rows in original source order and nothing else. A response that uses the additional scheduled budget for prose, derived fields, summary, conclusion, answer, or other prohibited content remains a scored/model diagnostic failure under the unchanged contract.

## Mandatory v2 static preflight

Before any prospective measured attempt, the runner must use the frozen tokenizer/template/runtime to assert all of the following mechanically:

1. the exact Arm B artifact and every exact ideal Arm C artifact satisfy `artifact_tokens + 8 <= 80`;
2. every Arm A, B Stage A, and C Stage A prompt fits context with its respective completion allowance;
3. every Arm B Stage B prompt with the exact fixed artifact and every Arm C Stage B prompt with its ideal sizing artifact fits `16896` with the 16-token final-answer allowance;
4. all source renderings are untruncated and retain the frozen six-case/source fingerprints;
5. the exact control grammar, artifact envelope, literal-byte transport check, evaluator, attempt sequence, provenance fields, and runtime identity are valid.

For the measured C Stage A output, the actual Stage B prompt must still be counted before submission and must fit `16896` with `max_tokens=16`; no truncation, replacement, or repair is allowed. Any failed assertion blocks the prospective attempt before model completion requests. The static sizing record confirms all required ideal artifacts and Stage B prompts fit under the v2 policy.

## Persist-before-validate and Arm B request progression

For every model response that reaches the host, Gate C v2 implementation must first serialize the raw response body/bytes, request payload, finish reason, token accounting, timestamps, and latency to the attempt evidence. Only after persistence may validation raise, fail fast, or stop the attempt. An exception may never discard a response that was actually received.

For Arm B Stage A only, the runner must proceed in this order:

1. submit Stage A and persist its raw response and metadata;
2. mechanically compare the emitted UTF-8 bytes with the exact frozen neutral grammar;
3. if the bytes do not match exactly, retain the condition, classify the attempt according to the frozen protocol/model taxonomy, and stop the complete attempt without constructing or submitting Arm B Stage B;
4. only if the grammar matches exactly, construct, fingerprint, persist, and submit Stage B with the literal artifact.

This mechanical equality check is not state reconstruction or semantic answer computation. It protects the active-control definition. Arm C does not gain an analogous semantic gate: its malformed, incomplete, non-target, prohibited, or incorrect reconstruction remains literal Stage B input and a scored/model diagnostic outcome. The host must not use frozen source truth to correct Arm C.

The missing invalidating Arm B Stage B raw response from `attempt-0001` remains a documented historical retention limitation. It must not be fabricated, recreated, or backfilled.

## Attempt identity, support, and future execution

Attempt identities remain monotonic. Since the retained history contains only `attempt-0001`, the next prospective measured execution is `attempt-0002`. `attempt-0001` remains permanently invalid and excluded from all denominators, paired counts, support thresholds, and efficacy interpretation.

The first later attempt that is fully protocol-valid and infrastructure-complete becomes canonical automatically, regardless of its Arm A/B/C scores or Stage A quality. If `attempt-0002` is fully valid, it is canonical and may not be replaced by a later favorable run. Invalid attempts remain retained; a later attempt may repair only implementation or infrastructure conformity without changing this v2 contract.

The primary support rule is unchanged: a complete valid A/B/C attempt; fresh Arm A `0/6`; Arm C at least `4/6`; `n10 >= 4`; `n01 = 0`; and a clean exact four-row Arm C reconstruction for every contributing B-to-C flip. `unsupported`, `inconclusive`, and `experiment_invalid` retain the Gate B v1 meanings. No v1 result is reclassified, and the cap repair does not lower a threshold.

## Gate C v2 entry criteria

`attempt-0002` is not authorized by this document alone. It may begin only after a separately reviewed Gate C v2 implementation checkpoint proves that:

- the common Stage A cap is `80` for both B and C, with all other budgets unchanged;
- the mandatory tokenizer assertions above pass and are retained;
- Arm B Stage A is persisted and exactly validated before any B Stage B request;
- every received response is persisted before validation or failure handling;
- literal transport, first-valid-attempt logic, evidence retention, focused static/unit checks, runtime fingerprints, and source/evaluator invariants pass;
- a fresh clean-GPU/environment preflight succeeds immediately before execution.

No model completion, measured efficacy run, or `attempt-0002` was performed while freezing Gate B v2.

## Gate B v2 status

`gate_b_v2_frozen`
