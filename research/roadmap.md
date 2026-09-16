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

## MN-006 — Distributed State Integration workload design

Status: **v1 semantic workload design is frozen at Design Gate B; its deterministic infrastructure and canonical 64-pair / 128-prompt inventory are complete; first Llama [attempt-0001](experiments/prototypes/mn-006-distributed-state-integration/reports/mn-006-attempt-0001.md) is `protocol_valid` but `no_usable_locality_failure_signal_under_v1_baseline`; and the [Response-Channel Gate](experiments/prototypes/mn-006-distributed-state-integration/response-channel-gate.md) is `response_channel_revision_ready`.** Every attempt-0001 output was malformed under the frozen exact-label parser, so the result is a shared output-channel floor, not evidence about regular round-robin locality. A future separate `attempt-0002` may add only a constant two-label grammar field; the workload, public bytes, parser, evaluator, and thresholds remain unchanged. The periodic scheduler remains an intentional v1 limitation and does not claim arbitrary-interleaving coverage. No treatment or candidate intervention was run.

MN-006 changes the immediate research target from selecting another intervention on ECC-006 to designing a better experimental substrate.

The working central question is:

> Can a candidate-neutral workload expose failures in integrating state from distributed/interleaved multi-entity updates, while preserving deterministic evaluation and supporting fair comparison among multiple state-management hypotheses?

The intended workload structure is:

```text
raw distributed/interleaved events
    ↓
canonical entity state
    ↓
minimal bounded deterministic downstream rule
    ↓
finite canonical answer
```

The downstream reasoning step is not a new general-reasoning research goal. It is introduced only to prevent External State Management from becoming an answer oracle: maintained state should be useful input to a decision, not identical to the final evaluated answer.

Initial MN-006 design principles:

1. **Failure-mode first, candidate second.** Freeze the workload before selecting Hierarchical, External State Management, or another intervention.
2. **Change as few dimensions as possible.** The preferred first changes are contiguous → distributed/interleaved state and endpoint-only → minimal bounded deterministic downstream reasoning.
3. **Keep other complexity controlled.** Do not initially stack true hierarchy, nested scope, multi-hop causal dependencies, noisy natural language, cross-episode persistence, or long-term memory unless evidence requires them.
4. **Preserve deterministic grading.** Every case must have one canonical answer from a finite answer space, with no external-world knowledge, subjective judgment, or LLM judge.
5. **Expose intermediate truth.** The workload should define canonical events, final entity state, derived facts, and final answer so future analysis can separate state-tracking failure from downstream-reasoning failure.
6. **Remain candidate-neutral.** A valid workload should be capable of evaluating multiple competing state-management strategies rather than being designed to make one preferred treatment win.
7. **Preserve research history.** Prior candidate outcomes remain evidence. A candidate can reopen only because MN-006 changes the relevant workload properties, not because MN-005 decisions are reset.

Candidate-specific reopening requires new justification:

- Hierarchical representation: only if distributed membership or meaningful scope creates a real hierarchy/locality mechanism.
- External State Management: only when maintained state is not the final answer.
- Event-to-State Normalization: only when event semantics require real canonicalization.
- Multi-pass Reconstruction: only if MN-006 exposes a new reconstruction bottleneck; do not repeat the old Gate B v2 contract.
- Symmetric State Partitioning: only if the workload introduces the structural asymmetry/interleaving its mechanism is meant to address.

Before MN-006 implementation or measured inference, the workload contract must make the failure mode, controlled dimensions, state oracle, answer oracle, anti-leakage rules, deterministic evaluator, and diagnostic separation explicit. If that cannot be done cleanly, MN-006 should remain in design phase rather than proceed to GPU/model experiments.
