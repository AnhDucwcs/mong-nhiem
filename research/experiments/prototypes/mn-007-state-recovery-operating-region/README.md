# MN-007 — State Recovery Operating Region

## Status

**Static design, deterministic materialization contract, and measurement-authority gate frozen. No executor, model run, locality comparison, or intervention is authorized. Status remains pre-measurement.**

MN-007 begins after the formal closure of [MN-006](../mn-006-distributed-state-integration/milestone-closure.md). MN-006 qualified the direct ordered state-vector response channel at Q0 (`9/9`) but failed its frozen contiguous task-bearing Q1 capability floor (`1/9`). Because the locality comparison was never reached, MN-006 closed as `measurement_interface_blocked` for the qualified model/runtime with locality still unmeasured.

MN-007 does not retry MN-006. It isolates the prerequisite question exposed by that closure.

## Research question

> For the qualified small-model/runtime, where is the prospectively defined operating region in which contiguous two-entity latest-state recovery is reliable enough to support a later causal locality comparison without sitting at a floor?

The immediate target is **contiguous state-recovery capability calibration**, not distributed/interleaved locality and not intervention efficacy.

## Why this is a separate milestone

Changing MN-006 difficulty after observing Q1 `1/9` would risk moving the goalposts and tuning the benchmark until the model passes.

MN-007 therefore treats operating-region calibration as an explicit research subject with its own prospective contract. The goal is to map a bounded capability frontier before selecting any future locality workload.

This preserves the distinction:

```text
MN-006
frozen Level 2 locality substrate
    -> contiguous qualification floor failed
    -> closed

MN-007
prospective contiguous capability calibration
    -> identify whether a usable operating region exists

later locality milestone / gate
    -> new hold-out matched contiguous vs interleaved comparison
```

## Preserved measurement principles

MN-007 should preferentially reuse the direct semantic state observable learned from MN-006:

```text
ordered queried entities
    -> ordered final-state vector
    -> exact deterministic scoring
```

The direct-state observable is not automatically adopted as a frozen MN-007 contract; a future static design gate must explicitly validate its reuse. However, MN-007 must not reintroduce the retired equality-to-arbitrary-label adapter merely to make the answer non-identical to maintained state.

The primary subject is state recovery. Additional reasoning may be introduced only if it is itself part of the declared construct or is independently qualified as neutral.

## Prospective difficulty landscape

Before any model inference, MN-007 must freeze a **finite, bounded difficulty landscape** and a deterministic selection rule.

Candidate workload dimensions may include, if justified by static design:

- total entity count;
- updates per entity;
- total event count / context load;
- number of non-query distractor entities;
- distance from each queried entity's latest update to the query;
- queried-entity placement within the contiguous schedule;
- other mechanically measurable load variables inherited from the MN-006 semantic workload.

The initial calibration should keep the queried endpoint bounded to two entities unless a static design decision shows that changing query arity is necessary.

MN-007 must not use an adaptive loop such as:

```text
run one difficulty
-> inspect score
-> invent the next easier/harder difficulty
-> repeat until a desirable baseline appears
```

Instead, the candidate levels and the rule for interpreting/selecting an operating region must be declared before inference.

## Operating-region objective

MN-007 is not simply looking for the easiest workload the model can pass.

A useful operating region must avoid both extremes:

```text
ceiling:
task too easy to expose meaningful degradation

usable region:
contiguous recovery is sufficiently reliable for causal comparison

floor:
contiguous recovery already too weak to attribute additional failure to locality
```

A future static design must freeze what "sufficiently reliable" means before measurement. MN-006's `18/18` qualification rule does not automatically become the MN-007 threshold.

The selection rule must be justified for causal locality measurement rather than chosen after viewing scores.

## Calibration versus later locality evidence

MN-007 calibration data must not itself be interpreted as locality evidence because its primary schedule is contiguous.

If MN-007 identifies a usable operating region, later locality work must use a separately authorized prospective design. That design should, where practical, use hold-out semantic cases or independently materialized matched pairs so that the same cases used to select difficulty are not also the sole evidence for a locality effect.

A future locality comparison must again hold constant:

- semantic histories;
- final states;
- queried entities;
- state vocabulary;
- scoring;
- qualified model/runtime;
- response interface;

while changing only the predeclared locality/schedule factor.

## Success and stop conditions

MN-007 should be capable of ending in at least these research-level outcomes:

- **usable operating region identified:** a prospectively defined contiguous region satisfies its frozen reliability/validity rule and can seed a separate future locality design;
- **no usable operating region in the bounded landscape:** the tested small model/runtime does not provide an adequate contiguous control within the declared search space;
- **measurement/design blocked:** the proposed calibration cannot isolate workload difficulty cleanly enough without introducing new confounds.

None of these outcomes selects an intervention.

If no usable region exists, the correct result is a bounded negative calibration finding, not further adaptive search within the same contract.

## Explicit non-goals

MN-007 does not initially:

- measure contiguous versus interleaved locality effects;
- reopen MN-006 or modify its evidence;
- tune prompts or output vocabularies until a pass appears;
- test Hierarchical State Representation;
- test External State Management;
- rerun Multi-pass Reconstruction;
- test Event-to-State Normalization or Symmetric State Partitioning;
- choose a production architecture;
- generalize from one qualified model/runtime to all small models.

## Required research sequence

No model execution is authorized by this foundation document.

The next work must remain prospective:

```text
static MN-007 research design
    ->
static finite difficulty / construct-validity gate
    ->
static executor boundary
    ->
separately authorized clean-environment calibration measurement
    ->
research-level operating-region decision
```

Only after a usable operating region is established may a separate future locality design be considered.

## Inherited immutable evidence

MN-003, MN-004, MN-005, and MN-006 remain frozen historical evidence.

MN-007 may use their conclusions to motivate design, but it may not rewrite, rescore, or reinterpret their canonical runs beyond their licensed conclusions. In particular:

- MN-003 retains the bounded ECC/state-tracking evidence.
- MN-004 retains the unsupported ledger intervention result.
- MN-005 retains the inconclusive Multi-pass result and unselected Hierarchical audit.
- MN-006 retains the confounded v1 branch, the direct-state redesign, Q0 `9/9`, Q1 `1/9`, and the final `measurement_interface_blocked` closure.

## Exact next permitted action

A separate **static deterministic implementation and infrastructure stage** may
materialize and validate the frozen 108-case calibration corpus defined by the
[materialization contract](materialization-contract.md). It must verify
reproducibility and all construction invariants without creating an inference
authority, executor, or model request.

That stage is complete: the canonical static corpus has 108 cases across six cells,
its semantic/public/evaluator artifacts validate, and two clean independent
regenerations were byte-identical. These are workload-definition facts, not model
evidence; no cell has been scored or classified.

The static executor / measurement-authority gate is complete and frozen in
[measurement-authority-gate.md](measurement-authority-gate.md). It binds the exact
model, llama.cpp runtime, sampling, grammar, evaluator, request ordering, raw persistence,
failure semantics, and preflight without executing a model. Status remains pre-measurement.
