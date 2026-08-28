# MN-004 — State Representation Intervention Design

## Status

**Prepared / design phase. No intervention selected, no experiment started, and no evidence is being produced.**

MN-004 is the successor hypothesis-design milestone to completed MN-003. It exists to make the next causal comparison defensible before implementation is authorized. It does not define an intervention experiment, fingerprint, case inventory, runner, schema, or run directory.

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

The only justified **candidate class** from MN-003 is explicit / inspectable state representation. That is not an adopted representation and must not be equated with RAG, vector retrieval, summarization, generic memory, compression, routing, embeddings, hidden scratchpads, databases, event sourcing, external state stores, or tool use. A later design may consider a specific candidate only when its information semantics and measurement contract are justified.

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

The initial causal comparison must remain on Llama 3.2 3B. Replacing it with Qwen3-4B cannot be called an improvement over ECC-006. Qwen may become a separately justified follow-up subject later.

## Success and no-harm philosophy

Changing a few cases from fail to pass is not sufficient. ECC-006 has six cases per level and therefore coarse resolution; a future contract must assess sample-size adequacy and, where needed, use predeclared fresh-case or replication evidence. It must define aggregate success before execution, retain per-context-level results, preserve the exact answer contract, and show no harmful short-context regression.

An intervention must not be declared successful by leaking the final state, omitting intermediate updates, converting State Tracking into direct retrieval, precomputing the answer, weakening the evaluator or accepted-answer set, reducing non-equivalently the context difficulty, changing models, or excluding difficult failures. Semantic equivalence with the inherited ECC-006 task is mandatory.

## Decision gates

### Gate A — hypothesis selection

Choose one concrete representation hypothesis and explain why its information semantics address the inherited limitation without assuming a solution.

### Gate B — measurement contract

Freeze baseline/intervention comparability, workload, controls, evaluator, failure taxonomy, retained evidence, aggregate success criteria, and no-harm criteria.

### Gate C — implementation authorization

Only after Gates A and B may an intervention implementation and measured experiment be authorized.

### Gate D — promotion decision

Only retained evidence that supports the hypothesis may justify considering a reusable component or an architecture concept. Experimental code remains under `research/experiments/prototypes/` until then and must not enter `src/mong_nhiem/` by default.

This preparation task establishes the framework for Gates A and B only. It does not pass Gate C.

## Future layout

Once a frozen intervention experiment is justified, its evidence may use `definition/`, `configs/`, `scripts/`, `schemas/`, `runs/`, and `reports/` under this milestone directory. Those directories are intentionally not created now: empty machinery would imply an experiment design that has not yet been selected.
