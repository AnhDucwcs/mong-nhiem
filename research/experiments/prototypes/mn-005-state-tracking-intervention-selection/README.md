# MN-005 — State Tracking Intervention Selection

## Status

**Completed and closed for further ECC-006 candidate efficacy work. Gate A and Gate B v1 remain frozen historical records. `attempt-0001` remains `experiment_invalid` because the v1 Arm B four-row placeholder could not fit its frozen `max_tokens=64` cap. Gate B v2 is frozen solely to repair that static executability contradiction: it preserves the grammar and replaces the common Stage A cap with `80` after tokenizer sizing. `attempt-0002` is the canonical first-valid Gate C v2 attempt; its frozen result is `inconclusive` (`1/6` Arm C versus `0/6` active control, `D=+1`). No architecture is promoted, no replacement efficacy attempt is authorized, and the Hierarchical Gate A audit is `hierarchical_gate_a_unselected` on frozen ECC-006.**

MN-005 is the completed successor research track to MN-004. It inherits MN-003 and MN-004 as immutable evidence rather than reopening either milestone. Its frozen [Gate A hypothesis](gate-a-hypothesis.md) selected a target-aware, model-generated reconstruction artifact externalized between two fresh model calls. [Gate B v1](gate-b-measurement-contract.md) remains historical; [Gate B v2](gate-b-v2-measurement-contract.md) is the frozen executable measurement contract. The final research transition is recorded in the [MN-005 → MN-006 handoff](mn-006-handoff.md).

MN-004 tested one frozen representation package: a globally indexed, fixed-field state-transition ledger. Its final valid 8k Llama comparison moved from untreated `0/24` to ledger `7/24`, but failed both predeclared support thresholds (`>=12/24` and delta `>=+8/24`). The 2k reference remained within the frozen no-harm margin (`4/24` to `2/24`), while Qwen untreated was only `14/24` and therefore did not qualify for ledger control. MN-004 closed as `unsupported_no_effect_or_insufficient_effect` and did not earn Gate D promotion.

The observed seven 8k wrong-to-correct flips are retained as a bounded signal worth explaining, not as support for the ledger hypothesis and not as permission to tune MN-004 thresholds or syntax after the fact.

## Research objective

MN-005 selected and tested one new falsifiable hypothesis that was better justified by the retained evidence than simply retrying or modifying the MN-004 ledger.

The selection question was:

> Does a target-aware, model-generated reconstruction artifact contribute to exact final-state reliability beyond a matched two-call/source-rereading procedure on the frozen ECC-006 Llama failure region?

MN-005 does not treat this selected procedure as retrieval, RAG, summarization by host code, compression, external memory, routing, external state management, or another ledger variant.

The milestone also audited whether a Hierarchical State Representation supplied a clean next candidate on ECC-006. That design-only audit found that the workload already provides target-local ordered trajectories, so hierarchy cannot be isolated there without introducing grouping, formatting, compression, reordering, target salience, or answer simplification.

## Inherited evidence boundary

MN-005 must preserve and cite, rather than rewrite:

- MN-003 ECC-006 as the frozen Llama 3.2 3B State Tracking failure baseline.
- MN-004 Gate A through v5 definitions, runs, reports, fingerprints, thresholds, and verdicts.
- The MN-004 finding that the full ledger package is operationally executable at 8k in at least one clean run but has substantial token and latency overhead.
- The MN-004 final result that the ledger package did not meet the frozen efficacy threshold.
- The absence of a qualified Qwen State Tracking control in MN-004 v5.

No MN-004 run may be rescored as MN-005 evidence.

## Other candidate directions — workload-bounded outcomes

These are candidate research directions, not architecture rankings. MN-005 closes without authorizing further ECC-006 inference for them.

### 1. Mechanism decomposition of the MN-004 representation package

Test whether the bounded `0/24 -> 7/24` signal is associated with a narrower component of the package rather than the full ledger: for example explicit global order cues, fixed-field regularity, or another inspectable representation property.

A valid design would need predeclared ablations and must avoid post-hoc cherry-picking from the seven successful MN-004 cases. Token footprint and structural changes must be measured separately.

### 2. Token-efficient explicit ordering representation

Preserve an inspectable ordering/state-transition cue while substantially reducing the approximately `+2,981` median 8k prompt-token overhead observed for the MN-004 ledger.

The design must not gain efficiency by deleting distractors, omitting events, moving the target, computing final state, or otherwise reducing the semantic workload.

### 3. Hierarchical or checkpointed state representation

The design-only [Hierarchical State Representation audit](hierarchical-gate-a.md) is `hierarchical_gate_a_unselected` on frozen ECC-006. The target's four updates are already contiguous and ordered, so the intended target-locality mechanism is substantially present before treatment. A meaningful future hierarchy hypothesis requires a workload with genuinely distributed entity membership or independently meaningful scope structure.

This is not an experimental falsification of hierarchy.

### 4. External state/register architecture as a distinct hypothesis class

Maintaining explicit state outside raw model context remains a strong long-term architecture hypothesis, but the frozen ECC-006 final-state endpoint makes a host-maintained state register too close to directly computing the evaluated answer.

A future evaluation therefore needs a new workload/interface in which maintained state is useful input to a bounded downstream decision but is not itself the final answer.

### 5. Resource-aware deployment robustness as a later validation dimension

Mộng Nhiễm is intended to coexist with games and other local workloads. Clean-GPU execution is therefore a research-control condition, not a permanent product assumption.

Resource coexistence should eventually be measured under predeclared VRAM/utilization budgets. It is not, by itself, an MN-005 efficacy hypothesis and should not replace mechanism selection.

## Gate A selection criteria and outcome

The selected candidate satisfied these Gate A prerequisites:

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

Multi-pass Reconstruction was the sole selected experimental hypothesis. Gate A did not authorize implementation or model execution by itself.

### Gate B v1 — historical measurement contract — complete and frozen

The [frozen v1 measurement contract](gate-b-measurement-contract.md) fixes the original three arms, exact prompt/protocol, content-neutral active control, six-case paired sample, support rule, runtime, preflight, evidence retention, and failure policy. It remains immutable.

### Gate B v2 — executability repair — complete and frozen

The [frozen v2 measurement contract](gate-b-v2-measurement-contract.md) preserves v1's causal question, grammar, cases, runtime, support rule, and safety boundaries. It changes only the common Stage A cap from `64` to `80`, using a predeclared tokenizer-derived strict-fit rule, and requires persist-before-validate plus Arm B grammar validation before Stage B submission. It did not authorize measured inference by itself.

### Gate C v1 — implementation/preflight complete; canonical attempt invalid

The implementation and tokenizer preflight conformed to the frozen contract. `attempt-0001` then became `experiment_invalid` when Arm B could not emit the frozen four-row placeholder within its frozen `max_tokens=64`; no valid efficacy comparison was produced.

### Gate C v2 — canonical result inconclusive

The v2 runner and static preflight conformed to the frozen contract. `attempt-0002` is the first fully protocol-valid and infrastructure-complete attempt, so it is canonical under the first-valid-attempt rule. Its result is `inconclusive`: Arm A=`0/6`, Arm B=`0/6`, Arm C=`1/6`, `n10=1`, `n01=0`, and `D=+1`; no Arm C artifact met the exact reconstruction condition. The initial post-run classifier crash was repaired offline without modifying raw evidence; see the [canonical report](reports/mn-005-gate-c-v2-attempt-0002.md).

### Hierarchical Gate A static audit — complete; unselected on ECC-006

The [Hierarchical audit](hierarchical-gate-a.md) found no independently observable hierarchy variable in frozen ECC-006. This is a workload-bounded design result, not an efficacy failure and not a universal rejection of hierarchy. No Hierarchical Gate B is authorized from ECC-006.

### Gate D — promotion decision — not authorized

No retained MN-005 evidence satisfies a promotion criterion for reusable architecture work.

## Closure and MN-006 handoff

MN-005 closes candidate selection on frozen ECC-006. Multi-pass Reconstruction is canonically measured and `inconclusive`, not supported or unsupported, and is deprioritized for further ECC-006 reruns under the same formulation. Hierarchical State Representation is `hierarchical_gate_a_unselected` because the current workload cannot expose a hierarchy-specific mechanism independently of non-hierarchy changes. External State Management remains architecturally relevant but needs a different task/interface to avoid becoming an answer oracle.

The next milestone is therefore a workload-design milestone rather than another ECC-006 candidate attempt. The [MN-005 → MN-006 handoff](mn-006-handoff.md) defines the planned direction: a candidate-neutral distributed/interleaved state-integration workload with minimal bounded deterministic downstream reasoning, canonical intermediate state truth, finite exact answers, and explicit diagnostic separation between state-tracking failure and downstream-reasoning failure.

MN-006 must design and freeze that experimental substrate before selecting or implementing an intervention. Prior candidates may be reconsidered only with workload-specific justification; their MN-005 history is not reset.

Do not replace `attempt-0002`, alter frozen authority, create `attempt-0003`, promote architecture, implement MN-006 on this branch, or run additional model/GPU efficacy work as part of MN-005 closure.