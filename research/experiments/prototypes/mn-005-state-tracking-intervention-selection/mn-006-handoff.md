# MN-005 → MN-006 research handoff

## Status

This document closes the MN-005 candidate-selection phase and defines the bounded research handoff into MN-006. It does not create an MN-006 experiment, implementation, runner, schema, measured attempt, model run, or GPU workload.

MN-005 closes without selecting a winning intervention for frozen ECC-006. This is not equivalent to concluding that all candidate classes failed. The accumulated result is that ECC-006 no longer provides a sufficiently discriminative substrate for several deeper state-management hypotheses.

## What MN-005 established

### Multi-pass Reconstruction

Multi-pass Reconstruction was experimentally observable on ECC-006 and was measured under the frozen Gate B v2 contract. The canonical first-valid Gate C v2 attempt is `attempt-0002`.

Its result remains `inconclusive`: Arm B=`0/6`, Arm C=`1/6`, and `D=+1`. None of the six Arm C Stage A artifacts satisfied the intended exact-reconstruction criterion, including the sole beneficial B-to-C flip. The result therefore supplies no evidence that the hypothesized reconstruction mechanism caused the improvement.

This is neither support nor universal rejection of Multi-pass Reconstruction. The same frozen contract is not eligible for an `attempt-0003`; a future use of multi-pass would require a new workload-specific mechanism justification rather than a replacement efficacy run.

### Hierarchical State Representation

The Hierarchical candidate was not experimentally falsified. Its Gate A static audit is `hierarchical_gate_a_unselected` because frozen ECC-006 already presents each target trajectory as an ordered contiguous four-event block with no distractor inside it.

A hierarchy treatment strong enough to differ meaningfully on that workload would also introduce at least one non-hierarchy variable such as grouping, formatting, compression, reordering, target salience, or answer simplification. ECC-006 therefore cannot isolate a hierarchy-specific causal effect.

Hierarchy remains a coherent hypothesis class for a workload with genuinely distributed entity membership or meaningful parent/child scope.

### External State Management

External State Management remains a strong architectural hypothesis class, but ECC-006 asks directly for a final state endpoint. A host-maintained state store would therefore be too close to computing the evaluated answer itself.

A fair future test needs a downstream task in which maintained state is useful input to the model but is not identical to the final answer.

### Other candidate classes

Event-to-State Normalization and Symmetric State Partitioning also remain workload-bounded candidate judgments. ECC-006's regular event syntax and contiguous target histories make their intended mechanisms weakly observable there.

The candidate history is cumulative:

> unobservable or unselected on ECC-006 does not mean universally invalid.

A future workload may reopen a candidate only when that workload contains the structural condition its mechanism is intended to address.

## Why candidate selection stops on ECC-006

The six frozen 8k ECC-006 cases share properties that make several state-management interventions hard to distinguish causally:

- target updates are already contiguous and ordered;
- no distractor event appears inside the target block;
- target locality is therefore already supplied by the untreated workload;
- source event syntax is highly regular;
- the evaluated endpoint is the final state itself.

These properties made ECC-006 valuable for discovering a Llama state-tracking failure region, but they also limit its usefulness as a general intervention-comparison substrate.

MN-005 therefore closes candidate search on this frozen workload rather than manufacturing additional efficacy attempts whose independent variables cannot be isolated cleanly.

## MN-006 research question

MN-006 should shift the primary question from:

> Which intervention should be tried next on ECC-006?

into:

> What candidate-neutral workload can expose distributed state-integration failures while preserving deterministic evaluation and allowing multiple competing state-management hypotheses to be compared fairly?

A working direction is **Distributed State Integration**.

The central workload hypothesis is:

> Small language models may fail when the state of multiple entities must be integrated from updates that are distributed and interleaved across context, and that state must then be used for a bounded deterministic downstream decision.

The exact name and measurement contract remain to be frozen inside MN-006.

## Why bounded downstream reasoning is added

MN-006 should preserve state tracking as the central subject. It is not intended to become a general reasoning benchmark.

A small downstream reasoning step is introduced for one design reason: an external state store must not become an answer oracle.

The intended structure is:

```text
raw distributed events
    ↓
canonical entity state
    ↓
bounded deterministic rule application
    ↓
finite final answer
```

The downstream task should use state rather than merely ask the model to repeat a maintained state value.

Reasoning must remain objectively gradeable: deterministic rules, no external-world knowledge, one canonical answer, a finite answer space, and no LLM judge.

## MN-006 workload-design constraints

MN-006 should design and freeze the workload before selecting an intervention. The workload must be derived from a failure mode, not from a preferred candidate.

The first design should change as few dimensions as necessary. The preferred initial changes are:

- state distribution: contiguous → distributed/interleaved;
- reasoning: none or endpoint-only → minimal bounded deterministic downstream reasoning.

Other dimensions such as true hierarchy, nested scope, causal dependency, cross-episode persistence, noisy natural language, or long-term memory should remain simple unless evidence later justifies changing them.

This prevents a future accuracy drop from becoming uninterpretable.

## Required diagnostic observability

The workload should define canonical intermediate truth so later experiments can distinguish state-tracking failure from downstream-reasoning failure.

At minimum, future case generation should be able to determine exactly:

- canonical source events;
- canonical final entity state;
- canonical derived facts required by the bounded rule;
- canonical final answer.

The design should support future metrics equivalent to:

- state accuracy;
- reasoning accuracy given correct state;
- end-to-end accuracy.

A later diagnostic control may provide perfect canonical state and test only the downstream rule. That control is a future design option, not an MN-005 experiment.

## Candidate-neutral reopening policy

Once the MN-006 workload is defined and frozen, prior candidates may be reconsidered only with workload-specific justification:

- **Hierarchical representation:** reconsider if entity updates are genuinely distributed or meaningful scope relations exist.
- **External State Management:** reconsider if stored state is input to a downstream decision rather than the evaluated answer itself.
- **Event-to-State Normalization:** reconsider if source event semantics require real canonicalization rather than cosmetic reformatting.
- **Multi-pass Reconstruction:** reconsider only if the new workload creates a reconstruction bottleneck with a new falsifiable mechanism; do not repeat the old Gate B v2 contract.
- **Symmetric State Partitioning:** reconsider only if the workload contains the structural asymmetry or interleaving its mechanism is meant to address.

These are hypotheses, not rankings and not implementation authorization.

## MN-006 entry gate

Before MN-006 authorizes a measured intervention experiment, its workload design should answer clearly:

1. What exact failure mode is being exposed?
2. Why could frozen ECC-006 not expose it cleanly?
3. Which workload dimensions change, and which remain controlled?
4. What is the canonical state oracle?
5. What is the canonical answer oracle?
6. Can every answer be scored deterministically without an LLM judge?
7. Can state-tracking failure be distinguished from reasoning failure?
8. Does the task avoid making External State Management an answer oracle?
9. Is the workload neutral with respect to Hierarchical or any other candidate?
10. Can multiple competing intervention classes be evaluated on the same frozen workload?

If these questions cannot be answered cleanly, MN-006 should remain in workload-design phase rather than proceeding to model inference.

## Boundary at MN-005 closure

MN-005 creates no MN-006 implementation or evidence. Frozen MN-003, MN-004, and MN-005 measurement artifacts remain immutable. No new ECC-006 efficacy attempt is authorized by this handoff.

The next milestone begins only after MN-005 is merged and a separate MN-006 branch is created from the updated main branch.