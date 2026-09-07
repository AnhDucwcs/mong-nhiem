# MN-004 — State Representation Intervention Design

## Status

**Completed and frozen for the globally indexed state-transition ledger hypothesis.**

- Gate A: complete and frozen.
- Gate B: complete and frozen.
- Gate C: complete after the versioned v1–v5 measurement/execution history.
- Final Llama verdict: `unsupported_no_effect_or_insufficient_effect`.
- Llama 2k reference: within frozen no-harm margin.
- Qwen control: `control_not_qualified`.
- Gate D promotion: **not earned / not opened**.
- No v6 is authorized.
- No MN-004 implementation is promoted into `src/mong_nhiem/`.

MN-004 is an immutable historical research milestone. A successor hypothesis belongs to MN-005 rather than reopening or retuning this intervention.

## Research question

MN-004 asked whether one explicit, inspectable representation mechanism could improve Llama 3.2 3B exact final-state reliability in the frozen ECC-006 failure region without changing the underlying State Tracking semantics or hiding failure.

The selected Gate A intervention was a **globally indexed state-transition ledger**: every source event, target and distractor alike, was rendered one-to-one in chronological order using fixed fields. It did not group entities, mark the target, remove events, compute final state, provide a summary/current-state register, or duplicate the original log.

The frozen hypothesis and syntax are defined in [Gate A](gate-a-hypothesis.md). The original measurement contract is [Gate B v1](gate-b-measurement-contract.md); later contracts are immutable versioned corrections or narrowed execution contracts, not rewrites of prior evidence.

## Inherited MN-003 evidence

MN-004 inherited ECC-006 as immutable direct-context baseline evidence for Llama 3.2 3B State Tracking. ECC-006 uses one target entity with four chronological updates and reports exact final-state accuracy of:

- 512: `2/6`
- 2,048: `1/6`
- 8,192: `0/6`
- 16,384: `0/6`

Its 21 failures are `incorrect_state` without execution, malformed-response, or truncation confounds. MN-004 does not alter or replace ECC-006.

Qwen3-4B has no frozen ECC-006-equivalent State Tracking failure baseline, so MN-004 never treats Qwen as an improvement subject. It is eligible only as a predeclared regression/no-harm control.

## Frozen intervention contract

The treatment representation is:

`event=<positive decimal index> | entity=<original entity identifier> | new_state=<original state token>`

with one row per event in original global order. The intervention preserves all source semantics while changing representation format and, as observed, token footprint. The experiment therefore evaluates the **ledger representation package**, not a token-independent fixed-field effect.

## Measurement history

### V1 — `contract_not_executable`

[Gate B v1](gate-b-measurement-contract.md) and Gate C v1 materialized the deterministic inventory, renderers, evaluator, schemas, validators, runner, and tokenizer preflight. The frozen 16k paired rendering exceeded the configured 16,896-token context for required conditions, so completion inference was correctly blocked. See the [feasibility report](reports/mn-004-contract-feasibility.md).

### V2 — `invalid_comparison`

The [v2 contract](gate-b-v2-measurement-contract.md) narrowed the primary comparison to executable 8k rows with a 2k Llama reference and 8k Qwen control. A stricter-than-intended output-limit validity rule caused the untreated condition to become invalid before ledger execution. V2 remains frozen and is not rescored. See the [v2 report](reports/mn-004-v2-results.md).

### V3 — `infrastructure_failure`

The [v3 contract](gate-b-v3-measurement-contract.md) corrected the distinction between protocol invalidation and valid model-output failures. Llama reproduced the frozen 8k failure at `0/6` and untreated conditions completed, but the ledger phase encountered CUDA OOM/process loss. The retained [postmortem](reports/mn-004-v3-infrastructure-postmortem.md) classifies the observed crash as a high-confidence treatment-coupled runtime/resource failure under that run; it is not efficacy evidence. See also the [v3 report](reports/mn-004-v3-results.md).

### V4 — operational feasibility

The [v4 contract](gate-b-v4-runtime-feasibility-contract.md) isolated operational execution from accuracy scoring and added lifecycle/GPU telemetry. After an initial blocked contamination preflight with zero server starts and zero requests, a clean canonical run completed both untreated and ledger 8k persistent-server phases at `24/24` requests each. The result `ledger_persistent_phase_completed` shows that the v3 crash was not reproduced in that attempt; it does not establish general stability or efficacy. See the [v4 report](reports/mn-004-v4-runtime-feasibility.md).

### V5 — final valid efficacy comparison

The [v5 contract](gate-b-v5-final-efficacy-contract.md) preserved the intervention, inventory, model/runtime settings, corrected validity taxonomy, and operational safeguards while generating fresh efficacy evidence.

Llama 8k reproduction remained compatible at `0/6`. The matched results were:

| Level | Untreated | Ledger | Delta | Role |
| --- | ---: | ---: | ---: | --- |
| 2,048 | `4/24` | `2/24` | `-2/24` | no-harm reference |
| 8,192 | `0/24` | `7/24` | `+7/24` | primary efficacy |

The predeclared primary support criteria required **both**:

- ledger 8k `>=12/24`, and
- ledger-minus-untreated `>=+8/24`.

The ledger achieved `7/24` and `+7/24`, so it missed both thresholds. The canonical verdict is [`unsupported_no_effect_or_insufficient_effect`](reports/mn-004-v5-final-efficacy.md).

The seven untreated-wrong → ledger-correct flips are retained as a bounded observation. They are not threshold support and must not be used to lower thresholds or tune the intervention post hoc.

At 2k, ledger `2/24` equals the frozen lower no-harm boundary `untreated - 2`, so the reference does not trigger `llama_reference_regression`.

Qwen untreated 8k scored `14/24`, below its frozen eligibility requirement `20/24`. Qwen ledger was therefore prohibited and the control verdict is `control_not_qualified`. No Qwen improvement or no-regression claim is available.

## Cost and operational observations

At 8k, the ledger increased median prompt length by approximately `+2,981` tokens and materially increased latency. V3 also retained one CUDA-OOM/process-loss event, while v4 and v5 subsequently completed clean ledger phases without reproducing that failure.

These facts establish that resource cost and stability are relevant properties of the representation package, but they do not isolate a token-independent causal mechanism.

Clean-GPU execution is a controlled-research condition, not a permanent deployment assumption. A future Mộng Nhiễm system intended to coexist with games or other local workloads must eventually be tested under predeclared resource-pressure budgets rather than assuming exclusive GPU access.

## Scientific conclusion

MN-004 provides the first valid answer for this frozen hypothesis:

> The globally indexed state-transition ledger produced a bounded improvement signal on the matched Llama 8k State Tracking workload (`0/24 -> 7/24`), but the effect was insufficient under both predeclared support criteria and therefore does not support promotion of the intervention.

MN-004 does **not** establish:

- 16k improvement;
- a general effective-context solution;
- token-independent benefit of fixed fields or explicit ordering;
- model-general effectiveness;
- Qwen improvement or no-regression;
- a reusable architecture;
- production readiness.

The negative/insufficient-support result is final for this intervention. No threshold change, v6 retry, ledger syntax modification, case replacement, or post-hoc rescue is part of MN-004.

## Decision gates

### Gate A — hypothesis selection — complete

Globally indexed state-transition ledger selected and frozen.

### Gate B — measurement contract — complete

Workload, controls, thresholds, token/resource interpretation, validity taxonomy, and claim boundaries were frozen through retained versioned contracts before their corresponding inference.

### Gate C — measured evidence — complete

V5 delivered a valid matched efficacy result. The result is below support thresholds.

### Gate D — promotion decision — not earned

No reusable component or architecture concept is promoted from MN-004 because the hypothesis did not satisfy its frozen support criteria.

## Successor boundary

The successor milestone is [MN-005 — State Tracking Intervention Selection](../mn-005-state-tracking-intervention-selection/README.md).

MN-005 must begin with design-only comparison of distinct candidate mechanisms and select a new falsifiable hypothesis. It must inherit MN-003/MN-004 evidence without rescoring or rewriting it. Candidate directions include mechanism decomposition, token-efficient explicit ordering, hierarchical/checkpointed representation, and an external state/register hypothesis class; none is selected by MN-004.

Any future resource-coexistence work with games/background GPU workloads is a separate deployment-robustness dimension and must not be confused with controlled mechanism evidence.

## Retained evidence

All definitions, preflight artifacts, run directories, raw diagnostics, reports, fingerprints, and versioned contracts under this directory are retained as historical evidence. They must not be modified to make the intervention appear more favorable.
