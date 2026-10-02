# Mộng Nhiễm

Mộng Nhiễm researches reliable small-model use over information and context spaces beyond a model's current effective capability.

## Direction

Comparative definitions and architectural principles are formalized in [ECC vs NCC](concepts/ecc-vs-ncc.md). Both directions strictly adhere to Mộng Nhiễm's invariant principle: **no fine-tuning, no weight modification, and no architectural alteration to the model**; the model is maintained strictly as an unchanged black-box reasoning engine.

- **Effective Context Capacity (ECC) — Utilization:** optimize useful operation over a fixed native context window through an external context management layer (structured decomposition, external state tracking, noise filtering, and task-aligned restructuring).
- **Native Context Capacity (NCC) — Expansion:** enable reliable operation over information spaces far exceeding the model's native effective context via an external context substrate (*large external memory + bounded native context + iterative access*).

State consistency, positional degradation, context overload, and reasoning over distributed information are research concerns, not selected solutions. MN-001 is complete. MN-002 is complete and freezes MCB v0.3.0 as the capability-qualification baseline. MN-003 completed its bounded direct-context measurement and synthesis phase. MN-004 then tested one explicit state-representation intervention and closed without meeting its frozen efficacy thresholds; no architecture was promoted. MN-005 is completed and closed for further ECC-006 candidate efficacy work: its canonical Multi-pass result is `inconclusive` (`1/6` Arm C versus `0/6` active control; `D=+1`), no `attempt-0003` is authorized, and its Hierarchical audit is `hierarchical_gate_a_unselected`. MN-006's first frozen Llama baseline is protocol-valid but yields a shared malformed-output floor (`0/32` in both schedules and profiles). Its separately frozen grammar-constrained `attempt-0002` is also protocol-valid: all responses parse but every response is `INVALID`, yielding `16/32` in both schedules and profiles. Neither establishes a locality-sensitive state-integration failure region; no candidate treatment has been created.

MN-006 is now formally [completed and closed](experiments/prototypes/mn-006-distributed-state-integration/milestone-closure.md) at `measurement_interface_blocked` for the qualified model/runtime. Its direct ordered two-entity final-state-vector qualification was `protocol_valid` / `direct_state_vector_interface_blocked`: Q0 exact response competence passed `9/9`, while Q1 contiguous task-bearing recovery passed only `1/9` under the frozen exact `18/18` requirement. The response channel is therefore qualified, but the frozen Level 2 contiguous workload does not provide the control capability floor needed for a locality comparison. Locality remains unmeasured and no intervention is authorized.

MN-007 is completed and closed: [State Recovery Operating Region](experiments/prototypes/mn-007-state-recovery-operating-region/README.md). Its clean 108-case calibration rerun (`calibration-run-0002`) classified all six cells as `floor` ($C_i \le 4/18$). Its outcome is `no usable operating region in bounded landscape`. In-context contiguous state recovery without explicit support is rejected for Llama 3.2 3B; no adaptive tuning within MN-007 is authorized.

MN-008 is completed and closed: [External State Management](experiments/prototypes/mn-008-external-state-management/README.md). Its canonical execution scored 2/24 on Arm C, failing primary efficacy; its Gate D disposition is `unpromoted_hypothesis_unsupported`. Zero code promoted into `src/mong_nhiem/`.

MN-009 is completed and promoted: [Scoped Context Delivery Engine](experiments/prototypes/mn-009-context-scaffolding/README.md). It established deterministic context scaffolding (<=512 tokens) over large knowledge spaces ($2\text{k}-32\text{k}$ tokens) without silent truncation, earning Gate D promotion into `src/mong_nhiem/context/`.

MN-010 is completed and promoted: [Iterative Context Working Set Loop](experiments/prototypes/mn-010-iterative-context-loop/README.md). It established host-coordinated multi-turn working set dispatch over large external corpora ($32\text{k}+$ tokens) under strict $\le 512$ token forward passes and $\le 3$ turn circuit breaker safety, resolving multi-hop transitive dependencies with 100% accuracy (30/30 vs 0/30 baseline), earning Gate D promotion into `src/mong_nhiem/context/`.

The primary active successor is **MN-011: Scaffolding-Assisted Effective Context Frontier** (ECC Reactivation), re-evaluating the model's true empirical context capacity boundary across budget tiers ($256, 512, 1024, 2048$ tokens) under hybrid host-scaffolded substrates.

The context subsystem (`src/mong_nhiem/context/`) is selected and promoted for production context scaffolding and iterative coordination. Retrieval, memory, and routing architectures remain open for future milestones. Later deployment validation must eventually include coexistence with games and other local workloads, but controlled mechanism experiments may still require a clean GPU environment to make causal attribution interpretable.

## Navigate

- [Architecture](concepts/architecture.md)
- [ECC vs NCC](concepts/ecc-vs-ncc.md)
- [Current state](current-state.md)
- [Research methodology](research.md)
- [Experiments](experiments/README.md)
- [MN-002](experiments/baselines/mn-002-model-qualification/README.md)
- [MN-003](experiments/prototypes/mn-003-effective-context-capacity/README.md)
- [MN-004](experiments/prototypes/mn-004-state-representation-intervention/README.md)
- [MN-005](experiments/prototypes/mn-005-state-tracking-intervention-selection/README.md)
- [MN-006](experiments/prototypes/mn-006-distributed-state-integration/README.md)
- [MN-007](experiments/prototypes/mn-007-state-recovery-operating-region/README.md)
- [MN-008](experiments/prototypes/mn-008-external-state-management/README.md)
- [MN-009](experiments/prototypes/mn-009-context-scaffolding/README.md)
- [MN-010](experiments/prototypes/mn-010-iterative-context-loop/README.md)
- [MN-011](experiments/prototypes/mn-011-scaffolding-context-frontier/README.md)
- [Decisions](decisions/decisions.md)
- [Roadmap](roadmap.md)

