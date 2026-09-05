# MN-004 Gate B v2 — narrowed executable measurement contract

## Status and authority

**v2 measurement contract frozen / v2 implementation pending.** This is a new, narrower contract prompted by the retained Gate C v1 feasibility result. It does not alter [Gate A](gate-a-hypothesis.md), frozen [Gate B v1](gate-b-measurement-contract.md), the v1 definition, the v1 inventory, or v1 preflight evidence.

Gate C v1 established a measurement-feasibility fact only: under the 16,896-token runtime, the globally indexed ledger has a materially larger tokenizer footprint than the natural-language rendering on the ECC-006-sized 16k source inventory. It did not establish efficacy, inefficacy, baseline drift, Qwen reliability, Qwen regression, a token-independent fixed-field mechanism, or architectural value.

V2 reuses the immutable v1 materialized inventory fingerprint `7183de0be8813764087e77330c5758970d40dfc9fe8553637faccca027d17897`. Its authorized rows are exactly the 24 cases at requested 2,048 and 8,192; no case is regenerated, substituted, resized, reordered, or added.

## Candidate selection

Candidate A is selected: an 8k-only primary efficacy comparison under the same Llama/Qwen artifacts, llama.cpp build, 16,896 context window, decoding, evaluator, source events, natural-language rendering, and frozen globally indexed ledger.

Candidate B—resizing source inventory to fit both renderings at 16,896—would no longer make the natural-language condition an ECC-006 16,384-pressure comparison. It asks a new lower-source-pressure question and weakens direct comparability with the established 16k failure evidence.

Candidate C—enlarging model context—changes the runtime and context-pressure ratio. It would require a new contemporaneous untreated interpretation and cannot preserve the inherited 16k direct-context comparison as the same measured condition.

Candidate A is selected because retained preflight proves both conditions fit at 8,192 for Llama and Qwen, it preserves the existing source inventory and the established ECC-006 Llama `0/6` 8k failure baseline, and it adds no new independent variable. The claim is deliberately narrower and excludes 16,384.

## Primary question and conditions

> On the matched 8,192-level State Tracking workload, where frozen ECC-006 establishes zero exact final-state accuracy for Llama 3.2 3B, does replacing natural-language events with the frozen globally indexed ledger increase exact final-state reliability under the same 16,896-token runtime context?

The independent variable is only rendering: ECC-006 natural-language events versus the unchanged Gate A ledger `event=<i> | entity=<ENTITY> | new_state=<STATE>`. Source-event identity/order, target identity and indexes, distractors, question, answer semantics, evaluator, artifacts, runtime, decoding, output allowance, and repetition policy are invariant. There is no target marking, grouping, duplicate log, summary, current/final field, answer calculation, filler, event removal, or repositioning.

## Llama workload and decision rules

The primary level is exactly 8,192. The sample is 24 paired semantic cases: the six frozen ECC-006 cases plus the 18 already materialized deterministic MN-004 fresh cases. Repeated deterministic inferences do not add sample size.

The immutable historical reference remains ECC-006 8k `0/6`. Before treatment, v2 must run a contemporaneous Llama untreated reproduction on exactly the frozen six 8k cases. It is compatible only if every row is valid and exact passes equal `0/6`. Otherwise verdict is `baseline_drift` and no v2 Llama treatment may run.

After compatibility, run the 24-case contemporaneous untreated condition, then the matched 24-case ledger condition. The Llama hypothesis is `supported_under_bounded_claim` only when the paired comparison is valid and both conditions hold:

1. ledger exact passes are at least `12/24`; and
2. ledger minus untreated exact passes is at least `+8/24`.

Any valid comparison missing either rule is `unsupported_no_effect_or_insufficient_effect`. These unchanged per-level v1 thresholds remain meaningful at v2's sole primary level: they demand an absolute half-sample reliability and a practically visible eight-case paired improvement, not one additional pass.

The v2 Llama reference level is 2,048, selected to retain a short/transition no-harm check without adding the infeasible 16k level or diluting the 8k estimand. It uses the same 24 v1 inventory rows. Ledger must satisfy `ledger_passes >= untreated_passes - 2` at 2,048; otherwise verdict is `llama_reference_regression`. There is no aggregate across 2k and 8k.

## Token, validity, and evidence rules

V2 retains per pair untreated/ledger prompt tokens, delta, context-utilization ratio, event count, target source indexes, and physical target token-position diagnostics. Retained v1 preflight proves all Llama and Qwen 2k/8k paired prompts fit with the 16-token output allowance. V2 does not equalize token length with filler and makes no token-independent fixed-field claim.

Any later 8k/2k overflow, truncation, source mismatch, added/missing/reordered event, target marking, answer leakage, duplicate original log, evaluator mismatch, model/runtime/decoding mismatch, or insufficient audit metadata yields `invalid_comparison`; no row may be selectively discarded. Infrastructure faults are `infrastructure_failure`, not scientific verdicts. V2 must retain failed/invalid attempts.

## Qwen 8k regression control

Qwen3-4B is regression/control only and never an improvement subject. V2 uses the same 24 semantic 8k cases and both frozen renderings. Retained v1 preflight proves all 24 Qwen natural-language and all 24 ledger prompts fit at 8k.

Run Qwen untreated only after the Llama phase. Qwen is eligible only when every row is valid and untreated exact passes are at least `20/24`. If not, record `control_not_qualified`, do not run Qwen ledger treatment, do not search for another workload, and make no no-harm claim. If eligible, run matched ledger treatment; no-harm passes only when `ledger_passes >= untreated_passes - 2`. A larger drop is `qwen_regression`.

## Execution and reporting order

1. Offline validate v2 authority links, selected immutable inventory rows, pair semantics, evaluator, and retained token feasibility.
2. Run 8k Llama frozen-case untreated reproduction; stop at `baseline_drift` if incompatible.
3. Run Llama untreated at 2k and 8k on the 24 authorized rows.
4. Run matched Llama ledger at 2k and 8k; apply frozen primary and reference rules.
5. Run Qwen 8k untreated eligibility; only if eligible run matched Qwen ledger and no-harm rule.
6. Report passed/total, exact scores, deltas, token/position distributions, validity flags, failure classes, thresholds, and bounded interpretation.

No v2 implementation, model invocation, run, or evidence exists at this freeze point.

## Claim boundary

A positive valid v2 result may support only: **the ledger as specified improves exact final-state reliability for Llama 3.2 3B on this matched 8k State Tracking workload**, with the stated Qwen no-harm qualification if earned. It may not claim improvement at 16k, an effective-context solution generally, model-general improvement, fixed-field causality independent of token footprint, Qwen improvement, or architecture validation.
