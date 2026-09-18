# MN-006 — Milestone Closure

## Final status

MN-006 is **completed and closed** for further model execution under its frozen contracts.

Final milestone disposition:

```text
measurement_interface_blocked
```

This status is bounded to the qualified Llama 3.2 3B / llama.cpp runtime and the frozen MN-006 workload and measurement contracts.

The canonical direct-state-vector qualification is `protocol_valid` / `direct_state_vector_interface_blocked`:

- Q0 exact ordered-vector response qualification: `9/9`.
- Q1 contiguous task-bearing two-entity final-state recovery: `1/9`.
- Frozen qualification requirement: exact `18/18`.

The Q0 result establishes that the direct `Sx,Sy` response channel, state vocabulary, ordering, grammar, parser, and serialization are usable for this model/runtime when the two state values are explicitly supplied.

The Q1 result establishes only that the frozen Level 2 contiguous qualification workload did not satisfy the predeclared capability floor needed before a locality comparison. It does not establish a general inability to track state.

## Scientific conclusion

MN-006 does **not** contain a construct-valid locality result.

The intended distributed-state/locality comparison was never reached because the contiguous control condition did not qualify. Therefore locality remains:

```text
unmeasured
```

MN-006 does not support claims that:

- interleaving harms state integration;
- locality has no effect;
- the model generally cannot track state;
- reasoning generally fails;
- any state-management intervention is required or effective.

The final causal boundary is:

```text
direct response serialization
    -> qualified by Q0

contiguous task-bearing final-state recovery at frozen Level 2
    -> below the required qualification floor in Q1

matched contiguous/interleaved locality comparison
    -> not reached
```

The response adapter is no longer the demonstrated blocker. The remaining blocker for the intended locality experiment is the absence of a sufficiently reliable contiguous control region at the frozen MN-006 workload.

## Frozen and retired boundaries

All MN-006 authority, evidence, plans, executors, reports, validators, and raw artifacts remain immutable historical evidence.

No further MN-006 model work is authorized under the closed milestone, including:

- retrying the direct-state qualification;
- changing its prompt, grammar, parser, serialization, seed, or threshold;
- searching for another measurement interface;
- executing D2;
- creating `attempt-0003`;
- running a perfect-state diagnostic;
- running a locality comparison;
- selecting or testing Hierarchical State Representation, External State Management, Multi-pass Reconstruction, Event-to-State Normalization, Symmetric State Partitioning, or another intervention.

The v1 A/B branch remains closed and non-diagnostic for locality. The direct-state-vector evidence remains canonical and is not rescored.

## Handoff to MN-007

The next research problem is not to repair MN-006 after observing Q1. It is to prospectively determine whether the qualified model/runtime has a **contiguous state-recovery operating region** suitable for a later causal locality experiment.

That question is moved to MN-007 so that capability calibration is not performed post hoc inside the failed MN-006 workload.

MN-007 begins from these frozen lessons:

1. A response interface can be protocol-valid while still failing construct validity.
2. Direct ordered state-vector serialization itself is qualified by Q0 and is preferable to the retired equality-to-label adapter for isolating state recovery.
3. A locality experiment requires a control condition above the floor; the frozen MN-006 Level 2 contiguous workload does not provide one.
4. Operating-region search must be prospective and finite, not iterative prompt or benchmark tuning after each result.
5. Calibration evidence must remain separate from any later hold-out locality comparison.
6. No intervention is justified before a construct-valid locality-sensitive failure signal exists.

See [MN-007 — State Recovery Operating Region](../mn-007-state-recovery-operating-region/README.md).

## Closure boundary

MN-006 is complete. Future work that maps contiguous capability difficulty belongs to MN-007. Any later distributed/interleaved locality experiment requires a new prospective authority after MN-007, rather than reopening or modifying MN-006.
