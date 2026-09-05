# MN-004 — State Representation Intervention Design

## Status

**Gate A and Gate B v1 are frozen. Gate C v1 closed at `contract_not_executable`; v2 remains `invalid_comparison`; v3 closed at `infrastructure_failure`; v4 completed its uncontaminated ledger persistent phase without reproducing a runtime failure.**

MN-004 is the successor intervention milestone to completed MN-003. Gate C v1 materialized a deterministic definition and source inventory, schemas, renderers, exact evaluator, validators, runner, and tokenizer preflight tooling under this prototype namespace. The preflight retained a feasibility failure before any completion request; it is neither positive nor negative efficacy evidence.
The frozen Gate A selection, candidate rejections, deterministic rendering semantics, contamination boundaries, and falsification prediction are in [the Gate A hypothesis note](gate-a-hypothesis.md).
The frozen estimand, workload, contemporaneous baseline policy, thresholds, runtime controls, token handling, Qwen strategy, invalidation rules, evidence retention, and execution/reporting sequence are in [the Gate B measurement contract](gate-b-measurement-contract.md).

The distinct [Gate B v2 measurement contract](gate-b-v2-measurement-contract.md) reuses only executable 2k/8k v1 inventory rows and preserves v1 as historical feasibility evidence. Its [retained outcome](reports/mn-004-v2-results.md) is `invalid_comparison`, not positive or negative ledger efficacy evidence.
The separate [Gate B v3 measurement contract](gate-b-v3-measurement-contract.md) corrected only the distinction between protocol invalidation and valid model-output failure. V3 reproduced Llama 8k at `0/6` and completed Llama untreated conditions, but stopped during the ledger phase at `infrastructure_failure`; Qwen did not run. The retained-evidence [postmortem](reports/mn-004-v3-infrastructure-postmortem.md) diagnoses a high-confidence treatment-coupled CUDA-OOM/process failure. V3 provides no ledger efficacy, Llama no-harm, or Qwen control result.
The separate [v4 operational-feasibility contract](gate-b-v4-runtime-feasibility-contract.md) froze enhanced lifecycle and GPU telemetry to test v3 runtime failure reproducibility without using efficacy metrics. It retained an initial blocked `environment_contaminated` preflight, then completed uncontaminated fresh-server untreated and ledger phases at `24/24` requests each. The [`ledger_persistent_phase_completed` outcome](reports/mn-004-v4-runtime-feasibility.md) means v3's failure was not reproduced in this attempt; it supplies no stability, resource-mechanism, efficacy, or Qwen result. No v5 is authorized.
Gate A records the selected falsifiable representation hypothesis. Gate B v1 freezes the original measurement contract. Gate C v1 is historical retained evidence, not evidence that the intervention works or fails. Any continuation requires a new versioned measurement contract; it must not modify v1 authority or evidence.

## Frozen MN-003 evidence boundary

MN-003 is completed and closed for further ECC measurement. Its canonical definitions, fingerprints, selected runs, raw evidence, summaries, reports, metrics, and synthesis are immutable. MN-004 consumes that evidence; it must not add a measurement and call it an MN-003 continuation, nor alter ECC-001 through ECC-007 to make a treatment comparison favorable.

ECC-006 is the frozen Llama 3.2 3B direct-context State Tracking baseline: six deterministic four-update cases at each of 512, 2,048, 8,192, and 16,384 requested tokens. Exact final-state accuracy is 0.333, 0.167, 0, and 0, and all 21 failures are incorrect_state without execution confounds. It provides the before/after failure region for MN-004; it does not make Llama the eventual architecture target.

Qwen3-4B has no frozen ECC-006-equivalent State Tracking baseline. Qwen therefore cannot be called improved by an ECC-006 intervention. In its own canonical MN-003 workloads, it remains reliable in the tested range: the retrieval controls are stable and ECC-007 causal reachability is 1.000, 1.000, 0.875, and 1.000. The isolated non-monotonic ECC-007 8k miss is not a Qwen failure boundary.

## Research questions and bounded claim

> Primary question: Does one explicit, inspectable state-representation mechanism increase Llama 3.2 3B exact final-state reliability in the frozen ECC-006 failure region, relative to the frozen untreated direct-context baseline?

> Secondary question: Does that same mechanism preserve Qwen3-4B correctness on a predeclared canonical workload and range where Qwen's frozen baseline remains reliable?

A positive MN-004 result can establish only a measurable effect of one specified mechanism on one established model failure mode, without a regression on the named Qwen control. It cannot establish a result for all models, most models, or a selected production architecture. Generalization requires additional qualified models with independently established failure boundaries.

## Falsifiable treatment contract

The selected intervention is a globally indexed state-transition ledger: a deterministic, one-to-one rendering of every ordered event, including distractors, into fixed fields. It is not retrieval, RAG, generic memory, summarization, compression, routing, embeddings, a hidden scratchpad, an external store, or tool use. The Gate A note defines its exact syntax and prohibited transformations.

Gate A has frozen the representation deterministic derivation, refresh semantics, model exposure, causal hypothesis, and answer-leakage prohibitions. It does not reveal the final answer, omit updates, turn State Tracking into direct lookup, precompute the answer, or hide model/evaluator failures.

The untreated condition is the frozen ECC-006 run. MN-004 may only add a contemporaneous untreated repetition under the same frozen cases and contract when its purpose and rule are predeclared; it remains MN-004 evidence and never replaces MN-003.

The treatment may change only the representation. Model and artifact hash, runtime/toolchain, inference and decoding settings, output allowance, seed/repetition policy, cases, workload ordering, token accounting and budget, final-state semantics, exact evaluator, failure taxonomy, and retained raw evidence must otherwise remain fixed or be explicitly controlled. Any tokenization or prompt-length change requires a predeclared equivalent-budget rule that rules out added inference budget, reduced distractor pressure, or hidden answer information.

Exact final-state reliability compatible with ECC-006 is the primary metric, reported by level and over a predeclared failure-region aggregate. Cost and latency are secondary diagnostics only. Before treatment results are inspected, Gate B must freeze the aggregate threshold, per-level rule, sample-size/replication rationale, variance rule, Qwen no-harm margin, contamination checks, and evidence-retention policy.

Qwen is regression/control only. Gate B must name a frozen reliable Qwen workload where the selected treatment is semantically equivalent, its canonical run and tested range, and its no-harm margin. If no such control is possible for the candidate, MN-004 must report that limitation and must not claim Qwen non-regression.

Positive evidence requires a measurable predeclared Llama improvement in the named failure region, matched semantics and conditions, no Qwen regression beyond the frozen margin, and retained auditable evidence. The intervention is unsupported, a valid negative result, if Llama does not improve, a gain is outside the failure region, Qwen regresses, conditions are uncontrolled, or the representation cannot be separated from changed inputs, scoring, or inference. Failed, invalid, and falsified attempts must be retained rather than tuned away.
## Motivation and inherited baseline

MN-003 identified the clearest candidate limitation as Llama 3.2 3B State Tracking on the frozen ECC-006 contract. ECC-006 measures one target entity with exactly four ordered updates at fixed midpoint placement across 512, 2,048, 8,192, and 16,384 requested input tokens. Exact final-state accuracy is 0.333, 0.167, 0, and 0. Its 21 failures are `incorrect_state`; there are no runtime, malformed-response, invalid-case, or truncation confounds.

This is a bounded State Tracking bottleneck with a short-context floor and a monotonic context-pressure curve. It does **not** prove that context length is its sole cause, and it does not choose a remedy.

ECC-006 is MN-004's immutable inherited direct-context baseline evidence:

- [ECC-006 charter](../mn-003-effective-context-capacity/experiments/ecc-006-state-tracking/README.md)
- [Frozen ECC-006 definition](../mn-003-effective-context-capacity/experiments/ecc-006-state-tracking/definition/experiment.json)
- [ECC-006 result report](../mn-003-effective-context-capacity/experiments/ecc-006-state-tracking/reports/ecc-006-results.md)
- [Canonical ECC-006 summary](../mn-003-effective-context-capacity/experiments/ecc-006-state-tracking/runs/20260828T053342Z-ecc-006-llama-3.2-3b-ab958c23/summary.json)
- [MN-003 capability synthesis](../mn-003-effective-context-capacity/reports/mn-003-synthesis.md)

MN-004 must not alter ECC-006 definitions, cases, fingerprints, metrics, scores, runs, or reports to make a later intervention appear favorable.

## Research boundary

MN-004 does not ask “which architecture is best?” Its first question is:

> Can a specific explicit, inspectable state-representation hypothesis be formulated that could improve exact final-state reliability relative to the frozen ECC-006 direct-context baseline without changing task semantics or hiding failure?

MN-003 justifies explicit, inspectable state representation as a candidate class. Gate A selects one member of that class: the globally indexed state-transition ledger specified in [the Gate A hypothesis note](gate-a-hypothesis.md). It remains a hypothesis, not an adopted architecture or an assertion of efficacy.

## Requirements before implementation or measured inference

Before code is written or a measured experiment runs, MN-004 must freeze and predeclare:

1. The exact intervention hypothesis and the representation semantics.
2. How the representation is derived, refreshed, and exposed to the model.
3. The baseline and intervention conditions, including what information each receives.
4. The Llama 3.2 3B model subject, task semantics, controlled variables, and one explicit independent variable.
5. Case inventory, sample-size rationale, and any fresh-case or replication requirement.
6. Deterministic evaluation, failure taxonomy, contamination/leakage rules, and retained-evidence policy.
7. Aggregate success threshold, per-context-level behavior, baseline comparability, and no-harm criteria.
8. Runtime/cost measurements when relevant, kept separate from capability scoring.

The initial causal comparison must remain on Llama 3.2 3B. Replacing it with Qwen3-4B cannot be called an improvement over ECC-006. Qwen is a regression/control subject only, and a no-harm claim requires a predeclared semantically equivalent workload, range, and margin.

## Success and no-harm philosophy

Changing a few cases from fail to pass is not sufficient. ECC-006 has six cases per level and therefore coarse resolution; a future contract must assess sample-size adequacy and, where needed, use predeclared fresh-case or replication evidence. It must define aggregate success before execution, retain per-context-level results, preserve the exact answer contract, and show no harmful short-context regression.

An intervention must not be declared successful by leaking the final state, omitting intermediate updates, converting State Tracking into direct retrieval, precomputing the answer, weakening the evaluator or accepted-answer set, reducing non-equivalently the context difficulty, changing models, or excluding difficult failures. Semantic equivalence with the inherited ECC-006 task is mandatory.

## Decision gates

### Gate A — hypothesis selection — complete

The globally indexed state-transition ledger is the sole selected treatment hypothesis. Its one-to-one transformation and rejections of grouped, target-only, and computed-state alternatives are frozen in [the Gate A hypothesis note](gate-a-hypothesis.md). Gate A does not assert improvement.

### Gate B — measurement contract — complete

The frozen [Gate B measurement contract](gate-b-measurement-contract.md) defines baseline/intervention comparability, workload, controls, evaluator, failure taxonomy, retained evidence, aggregate success criteria, Qwen eligibility/no-harm criteria, the Llama failure-region rule, sample policy, token interpretation, runtime controls, execution order, and contamination/invalidation rules.

### Gate C v1 — closed feasibility execution

Gate C v1 was authorized and implemented. Its tokenizer-only hard gate found the frozen 16k paired comparison non-executable at the configured 16,896-token context window, so it correctly blocked completion inference. See [the feasibility report](reports/mn-004-contract-feasibility.md). A future v2 contract is a new design iteration, not a reopening or rewrite of v1.

### Gate D — promotion decision

Only retained evidence that supports the hypothesis may justify considering a reusable component or an architecture concept. Experimental code remains under `research/experiments/prototypes/` until then and must not enter `src/mong_nhiem/` by default.

Gate A and Gate B v1 remain frozen. Gate C v1 closed at `contract_not_executable`; see [the feasibility report](reports/mn-004-contract-feasibility.md). V2 closed at [`invalid_comparison`](reports/mn-004-v2-results.md) before ledger or Qwen inference. V3 closed at [`infrastructure_failure`](reports/mn-004-v3-results.md) during the ledger phase; its [postmortem](reports/mn-004-v3-infrastructure-postmortem.md) is operational-feasibility diagnosis, not efficacy evidence. No Gate D promotion or v5 is authorized.

## Retained layout

Gate C v1 created `definition/`, `configs/`, `scripts/`, `schemas/`, `runs/`, and `reports/`. Their v1 artifacts and tokenizer-only feasibility evidence are immutable historical records. V2 adds a separately fingerprinted definition, offline validator, phase runner, contract tests, retained Llama reproduction/untreated evidence, and the v2 outcome report; it does not alter any v1 authority or evidence.
