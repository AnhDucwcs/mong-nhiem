# Roadmap

## MN-001 — Development foundation

Status: completed.

## MN-002 — Model qualification

Status: completed and frozen. MCB v0.3.0 is the canonical capability-qualification benchmark (fingerprint `2ac24df4e6cca12e13da577fb48db5da8e39d89cf3646ef705ea7679b4548f7a`). Llama 3.2 3B and Qwen3-4B are qualified capability baselines; capability and runtime evidence remain separate. This is not a production-model choice.

## MN-003 — Effective Context Capacity

Status: completed and closed for further ECC measurement work. ECC-001 through ECC-007 establish a model-specific capability map; no architecture has been selected. See the [MN-003 synthesis](experiments/prototypes/mn-003-effective-context-capacity/reports/mn-003-synthesis.md).

1. Easy retrieval is stable for both qualified models in the tested range, but Llama has a monotonic semantic-interference retrieval decline and a replicated late-position sensitivity under the confusable exact-output task.
2. Llama State Tracking is a bounded capability bottleneck: its fixed four-update contract has a short-context floor and declines monotonically to zero at 8k/16k without execution confounds.
3. Qwen causal reachability has no stable context-length degradation boundary in the tested range; its single 8k false positive is an unresolved isolated observation, not an ECC boundary or an ECC-008 trigger.
4. Timing/VRAM pressure at 16k is practical local-runtime evidence, not capability evidence.
5. MN-003 did not select a remedy; it supplied the immutable failure evidence used by MN-004.

## MN-004 — State Representation Intervention Design

Status: **completed and frozen for the globally indexed state-transition ledger hypothesis. Gate D promotion was not earned.**

1. Gate A selected one falsifiable intervention only: a globally indexed, one-to-one state-transition ledger preserving every event and global order without calculating final state.
2. Gate B froze the matched workload, thresholds, validity taxonomy, runtime controls, Llama primary estimand, 2k no-harm reference, and Qwen eligibility/control rules before efficacy inference.
3. Historical execution versions remain immutable: v1 `contract_not_executable`, v2 `invalid_comparison`, v3 `infrastructure_failure`, and v4 `ledger_persistent_phase_completed` as operational-feasibility evidence only.
4. V5 delivered the valid final efficacy comparison. Llama 8k untreated scored `0/24`; ledger scored `7/24`. The observed delta `+7/24` missed both frozen support rules: ledger `>=12/24` and delta `>=+8/24`.
5. The canonical final verdict is [`unsupported_no_effect_or_insufficient_effect`](experiments/prototypes/mn-004-state-representation-intervention/reports/mn-004-v5-final-efficacy.md). The seven wrong-to-correct flips remain an observation, not threshold support.
6. Llama 2k remained within the frozen no-harm margin (`4/24` untreated to `2/24` ledger).
7. Qwen untreated was `14/24`, below eligibility `20/24`; Qwen ledger was therefore prohibited and the control is `control_not_qualified`.
8. The ledger incurred material 8k token and latency overhead, so MN-004 does not establish a token-independent structural mechanism or a production-feasible architecture.
9. No v6, threshold adjustment, post-hoc ledger tuning, or promotion into `src/mong_nhiem/` is justified. MN-004 is closed.

## MN-005 — State Tracking Intervention Selection

Status: **completed and closed for further ECC-006 candidate efficacy work.** Gate A and Gate B v1 remain frozen historical records. `attempt-0001` is permanently `experiment_invalid`; Gate B v2 remains the tokenizer-verifiable executability repair. `attempt-0002` is the canonical first-valid Gate C v2 attempt and remains `inconclusive` (`1/6` Arm C versus `0/6` active control, `D=+1`). The Hierarchical Gate A audit is `hierarchical_gate_a_unselected`. No architecture is selected and no `attempt-0003` is authorized.

MN-005 established two different kinds of evidence that must not be conflated:

1. **Multi-pass Reconstruction was measurable but inconclusive.** None of the six Arm C Stage A artifacts met the intended exact-reconstruction criterion, including the sole beneficial B-to-C flip. The result does not show that reconstruction caused the observed `+1/6`, but it also does not universally reject multi-pass methods.
2. **Hierarchical State Representation was not experimentally falsified.** Frozen ECC-006 already supplies an ordered contiguous target trajectory, so hierarchy cannot be isolated from grouping, formatting, compression, reordering, salience, or answer simplification. Its decision is workload-bounded: `hierarchical_gate_a_unselected`.
3. **External State Management remains architecturally strong but poorly matched to the ECC-006 endpoint.** A host-maintained final state would be too close to directly supplying the evaluated answer.
4. **Event-to-State Normalization and Symmetric State Partitioning are also weakly observable on ECC-006** because source syntax is highly regular and target histories are already contiguous.

The milestone conclusion is therefore not that all candidates failed. It is that frozen ECC-006 has become insufficiently discriminative for several deeper state-management hypotheses. Candidate selection stops on ECC-006 rather than continuing with confounded efficacy attempts.

See the [MN-005 → MN-006 research handoff](experiments/prototypes/mn-005-state-tracking-intervention-selection/mn-006-handoff.md).

## MN-006 — Distributed State Integration

Status: **completed and closed at `measurement_interface_blocked` for the qualified model/runtime.**

MN-006 attempted to establish a deterministic, candidate-neutral contiguous-versus-interleaved locality measurement. The v1 equality/label path was retired after the diagnostic ladder showed a lower-level conditioned-output confound. The replacement direct ordered state-vector interface qualified its response channel at Q0 `9/9`, but its frozen contiguous task-bearing Q1 qualification scored only `1/9`. The predeclared exact `18/18` requirement was therefore not met.

The final scientific boundary is that the response serialization is usable, while the frozen Level 2 contiguous control condition is below the capability floor required for a causal locality comparison. Locality remains unmeasured. MN-006 does not support a negative locality claim, a general state-tracking claim, or an intervention claim. No retry, alternate interface, D2, perfect-state diagnostic, locality run, or intervention is authorized. See [MN-006 milestone closure](experiments/prototypes/mn-006-distributed-state-integration/milestone-closure.md).

## MN-007 — State Recovery Operating Region

Status: **static operating-region design and deterministic materialization contract frozen. No model execution authorized.**

MN-007 prospectively calibrates the contiguous state-recovery operating region needed before any future locality experiment. It is a separate milestone so the frozen MN-006 Q1 failure does not trigger post-hoc benchmark tuning inside MN-006.

The completed static [operating-region design gate](experiments/prototypes/mn-007-state-recovery-operating-region/operating-region-design-gate.md) establishes:

1. the direct ordered state-vector observable, justified by MN-006 Q0 `9/9` as response-serialization evidence rather than recovery qualification;
2. six finite contiguous cells: entity counts `3`, `5`, `7` crossed with terminal or leading queried-block placement, while holding three updates/entity and two query entities fixed;
3. 18 balanced semantic cases per cell and exact parser/score rules;
4. an exhaustive floor (`<=14/18` exact or any malformed response), usable (`15–16/18` exact and `18/18` parser-valid), and ceiling (`17–18/18` exact and `18/18` parser-valid) classification;
5. deterministic selection among usable cells and a fresh-case hold-out policy for any later locality work;
6. bounded `usable operating region identified`, `no usable operating region in bounded landscape`, and `measurement/design blocked` outcomes; and
7. continued prohibition of interventions until a later construct-valid locality-sensitive signal exists.

The completed [materialization contract](experiments/prototypes/mn-007-state-recovery-operating-region/materialization-contract.md) freezes deterministic case identities, seed derivation, semantic histories, vector/orientation coverage, contiguous scheduling, canonical serialization, public/evaluator separation, and validation. No corpus, run authority, executor, or model evidence has been created.

The next action is a static deterministic implementation/infrastructure stage that materializes and validates the frozen corpus without model activity. The remaining required sequence is that stage -> static executor boundary -> separately authorized clean-environment calibration -> research-level operating-region decision. Only after a usable region exists may a separate future locality milestone/gate be designed.

See [MN-007 — State Recovery Operating Region](experiments/prototypes/mn-007-state-recovery-operating-region/README.md).
