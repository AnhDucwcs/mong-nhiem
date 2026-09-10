# MN-005 — State Tracking Intervention Selection

## Status

**Gate A is frozen for Multi-pass Reconstruction. Gate B has not started. No runner, schema, run directory, implementation, or MN-005 measured evidence exists.**

MN-005 is an ongoing successor research track to completed MN-004. It inherits MN-003 and MN-004 as immutable evidence rather than reopening either milestone. Its frozen [Gate A hypothesis](gate-a-hypothesis.md) selects a target-aware, model-generated reconstruction artifact externalized between two fresh model calls; Gate B and later permitted work remain separate future stages.

MN-004 tested one frozen representation package: a globally indexed, fixed-field state-transition ledger. Its final valid 8k Llama comparison moved from untreated `0/24` to ledger `7/24`, but failed both predeclared support thresholds (`>=12/24` and delta `>=+8/24`). The 2k reference remained within the frozen no-harm margin (`4/24` to `2/24`), while Qwen untreated was only `14/24` and therefore did not qualify for ledger control. MN-004 closed as `unsupported_no_effect_or_insufficient_effect` and did not earn Gate D promotion.

The observed seven 8k wrong-to-correct flips are retained as a bounded signal worth explaining, not as support for the ledger hypothesis and not as permission to tune MN-004 thresholds or syntax after the fact.

## Research objective

MN-005 selected one new falsifiable hypothesis that is better justified by the retained evidence than simply retrying or modifying the MN-004 ledger.

The selection question is:

> Does a target-aware, model-generated reconstruction artifact contribute to exact final-state reliability beyond a matched two-call/source-rereading procedure on the frozen ECC-006 Llama failure region?

MN-005 does not treat this selected procedure as retrieval, RAG, summarization by host code, compression, external memory, routing, external state management, or another ledger variant.

## Inherited evidence boundary

MN-005 must preserve and cite, rather than rewrite:

- MN-003 ECC-006 as the frozen Llama 3.2 3B State Tracking failure baseline.
- MN-004 Gate A through v5 definitions, runs, reports, fingerprints, thresholds, and verdicts.
- The MN-004 finding that the full ledger package is operationally executable at 8k in at least one clean run but has substantial token and latency overhead.
- The MN-004 final result that the ledger package did not meet the frozen efficacy threshold.
- The absence of a qualified Qwen State Tracking control in MN-004 v5.

No MN-004 run may be rescored as MN-005 evidence.

## Other candidate directions — not selected

These are candidate research directions only. Listing them does not authorize implementation or inference.

### 1. Mechanism decomposition of the MN-004 representation package

Test whether the bounded `0/24 -> 7/24` signal is associated with a narrower component of the package rather than the full ledger: for example explicit global order cues, fixed-field regularity, or another inspectable representation property.

A valid design would need predeclared ablations and must avoid post-hoc cherry-picking from the seven successful MN-004 cases. Token footprint and structural changes must be measured separately.

### 2. Token-efficient explicit ordering representation

Preserve an inspectable ordering/state-transition cue while substantially reducing the approximately `+2,981` median 8k prompt-token overhead observed for the MN-004 ledger.

The design must not gain efficiency by deleting distractors, omitting events, moving the target, computing final state, or otherwise reducing the semantic workload.

### 3. Hierarchical or checkpointed state representation

Investigate deterministic intermediate checkpoints or hierarchical state structure that may reduce repeated overwrite-tracking burden across long event histories.

This direction has a high leakage risk: a checkpoint must not become an oracle final-state register or silently precompute the answer. Its derivation and information budget would need to be frozen before inference.

### 4. External state/register architecture as a distinct hypothesis class

Investigate whether maintaining explicit state outside the raw model context is a better long-term architecture than asking the model to recover state from the entire event history.

This would be a larger change than MN-004. If selected, it may require a new task/interface contract rather than being described as a direct representation-only comparison against ECC-006. Retrieval, memory, and state storage must remain conceptually separated.

### 5. Resource-aware deployment robustness as a later validation dimension

Mộng Nhiễm is intended to coexist with games and other local workloads. Clean-GPU execution is therefore a research-control condition, not a permanent product assumption.

Resource coexistence should eventually be measured under predeclared VRAM/utilization budgets. It is not, by itself, an MN-005 efficacy hypothesis and should not replace mechanism selection.

## Gate A selection criteria and outcome

The selected candidate satisfies these Gate A prerequisites:

1. the precise causal mechanism being tested;
2. the single primary independent variable or a justified factorial decomposition;
3. how every representation/state artifact is deterministically derived;
4. why it does not reveal or compute the expected answer;
5. how semantic workload is preserved or, if the interface changes, how the new comparison is defined honestly;
6. how token footprint, latency, and runtime-resource changes are reported rather than hidden;
7. which frozen baseline establishes an observable failure region for the treatment subject;
8. the exact metric, sample policy, success threshold, no-harm rule, and invalidation taxonomy to be frozen before measured inference;
9. what evidence would falsify the hypothesis;
10. how any eventual deployment/robustness test will remain separate from controlled mechanism evidence.

## Proposed gates

### Gate A — successor hypothesis selection — complete and frozen

Multi-pass Reconstruction is the sole selected hypothesis. Gate A does not authorize implementation or model execution.

### Gate B — measurement contract — not started

Freeze workload, controls, sample size, thresholds, token/resource interpretation, environment qualification, evidence retention, and claim boundary.

### Gate C — implementation and measured evidence — not authorized

Only after Gate A and Gate B are frozen.

### Gate D — promotion decision — not authorized

Only evidence that satisfies the new hypothesis and its frozen promotion criteria may justify reusable architecture work.

## Immediate next step

Next action: define and freeze Gate B measurement details for the selected hypothesis before implementation or model inference. Do not reopen MN-004 or treat the Gate A selection as architecture promotion.