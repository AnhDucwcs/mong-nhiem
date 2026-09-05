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
5. The proposed next milestone is MN-004 — State Representation Intervention Design: formulate and predeclare one explicit-state hypothesis against ECC-006's direct-context baseline. This is not started and does not preselect retrieval, RAG, memory, summarization, compression, routing, embeddings, or external state.

## MN-004 — State Representation Intervention Design

Status: Gate B complete / Gate C pending. The explicit hypothesis and its measurement contract are frozen; no MN-004 implementation or evidence exists.

1. Inherit the immutable ECC-006 Llama 3.2 3B four-update State Tracking baseline rather than recreating or modifying it. Llama is the treatment subject because it has the observed bounded failure region, not because it is an architecture target.
2. Gate A: complete. The selected hypothesis is a globally indexed, one-to-one state-transition ledger that preserves every event and global order without calculating final state. See the [Gate A hypothesis note](experiments/prototypes/mn-004-state-representation-intervention/gate-a-hypothesis.md). This is a falsifiable hypothesis, not an assumed solution.
3. Gate B: complete. The [measurement contract](experiments/prototypes/mn-004-state-representation-intervention/gate-b-measurement-contract.md) freezes the Llama primary estimand, sample/replication policy, threshold and no-harm rules, token interpretation, runtime/evaluator controls, Qwen eligibility/no-harm strategy, invalidation, evidence retention, and reporting. Qwen remains regression/control only.
4. Gate C: requires separate authorization before any implementation or measured inference.
5. Gate D: consider promotion to reusable code or an architecture concept only if retained evidence supports it.
