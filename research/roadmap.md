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

Status: **Gate A frozen / design phase. Gate B pending. No implementation or architecture selected.** See the [MN-005 Gate A hypothesis](experiments/prototypes/mn-005-state-tracking-intervention-selection/gate-a-hypothesis.md).

MN-005 is an ongoing research track that begins from the negative-but-informative MN-004 result rather than attempting to rescue the ledger. Gate A selected Multi-pass Reconstruction before implementation or inference; its causal comparison is defined in the Gate A hypothesis.

Other candidate directions remain unselected and are outside this Gate A:

1. **Mechanism decomposition:** test whether a narrower component such as explicit global ordering or fixed-field regularity explains part of the bounded MN-004 signal, using predeclared ablations rather than cherry-picking the seven successful cases.
2. **Token-efficient explicit ordering:** preserve inspectable ordering/state cues while reducing the ledger's approximately `+2,981` median 8k token overhead without deleting semantic workload or leaking final state.
3. **Hierarchical/checkpointed state representation:** reduce overwrite-tracking burden with deterministic intermediate structure, subject to strict anti-oracle/answer-leakage rules.
4. **External state/register hypothesis class:** investigate maintaining explicit state outside raw event history as a distinct architecture/interface hypothesis, not as a disguised representation-only continuation of MN-004.
5. **Deployment resource robustness:** later measure coexistence with games/background GPU workloads under predeclared VRAM/utilization budgets. This is a product/robustness validation dimension, not the MN-005 mechanism hypothesis itself.

Next action: define and freeze Gate B measurement details for the selected hypothesis before implementation or model inference. Do not reopen MN-004 or treat the Gate A selection as architecture promotion.
