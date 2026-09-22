# Current state

## MN-001 — completed

MN-001 established the source layout, canonical research knowledge base, minimal packaging, pytest/Ruff checks, CI, and a package-import smoke test.

## MN-002 — Model Qualification — completed and frozen

MCB v0.1.0 and v0.2.0 remain historical/superseded evidence. Re-evaluation of v0.2 failures under the frozen v0.3 accepted-answer contract converts 143 previously failing semantic-suite outputs into accepted output-equivalence cases; 56 semantic-suite failures remain failing under the corrected deterministic evaluator.

MCB v0.3.0 is the canonical frozen qualification benchmark. Its fingerprint is `2ac24df4e6cca12e13da577fb48db5da8e39d89cf3646ef705ea7679b4548f7a`. It contains 100 cases across Instruction Following, Structured Output, Context Retrieval, State Tracking, and Causal Reasoning. Six local GGUF candidates were measured. Llama-3.2-3B-Instruct-Q4_K_M and Qwen3-4B-Q4_K_M meet every capability gate and are the qualified capability baselines. Capability qualification and runtime performance are separate evidence.

This qualification is not a production-model choice and does not validate an ECC, retrieval, memory, RAG, summarization, compression, routing, or context-management mechanism.

## MN-003 — Effective Context Capacity — completed measurement synthesis

MN-003 is complete and closed for further ECC measurement work as a bounded direct-context measurement and synthesis milestone under `research/experiments/prototypes/`. It freezes no new universal benchmark: each ECC definition and its retained canonical evidence remain immutable in its own experiment directory. The canonical synthesis is [MN-003 capability map](experiments/prototypes/mn-003-effective-context-capacity/reports/mn-003-synthesis.md).

The completed map separates Retrieval, Integration/State Tracking, and Inference/Causal Reasoning by subject rather than treating all ECC results as one cross-model ladder. The shared conclusions are bounded to deterministic direct context, actual model-token accounting, exact evaluation, the recorded llama.cpp/local hardware configuration, and tested ranges up to 16,384 requested tokens.

- **Retrieval:** ECC-001 is an easy-task lower bound: both qualified models are stable through 16,384. ECC-002 shows Llama 3.2 3B declining monotonically from 1.00 to 0.85 under confusable same-template records while Qwen3-4B remains stable. ECC-003/ECC-004 replicate a Llama long-context early-over-late position effect on fresh cases; ECC-003/ECC-005 retain a bounded Qwen null result. The Llama retrieval failures are not tracked distractor selections, so no retrieval/routing remedy is established.
- **State Tracking:** ECC-006 measures Llama 3.2 3B only. Its fixed four-update contract is at 0.333 accuracy at 512, 0.167 at 2,048, and zero at 8,192/16,384. The 21 failures are `incorrect_state`, with zero invalid, malformed, truncated, or runtime-error rows. This is a strong Llama bottleneck with a short-context floor and monotonic degradation, but it does not prove that context length alone is the cause.
- **Causal Reasoning:** ECC-007 measures Qwen3-4B only. Two-hop reachability is 1.000, 1.000, 0.875, and 1.000 across 512/2,048/8,192/16,384, with one 8k false positive and otherwise zero invalid/malformed/truncated/runtime-error rows. The non-monotonic miss does not establish a stable causal context-length boundary. Its metric ECC95/ECC90 = 2,048 is a contiguous-prefix convention, not a causal boundary conclusion.

ECC-006 and ECC-007 use different model subjects, so MN-003 does not rank State Tracking against Causal Reasoning or infer that one model is generally stronger. Runtime slowdown, prompt-cache eviction, and lifecycle pressure at 16k are retained practical local-runtime evidence, not capability scores.

No ECC-008 is justified solely to investigate the isolated Qwen 8k causal miss: its reproducibility would not change an architecture decision. No architecture is selected.

## MN-004 — State Representation Intervention Design — completed and frozen

MN-004 tested one explicit, inspectable state-representation hypothesis against the immutable ECC-006 Llama State Tracking failure region: a globally indexed, fixed-field state-transition ledger that preserves all source events and chronological order without computing final state. [Gate A](experiments/prototypes/mn-004-state-representation-intervention/gate-a-hypothesis.md), the measurement contracts, definitions, retained runs, and reports are frozen historical evidence.

The milestone required several versioned execution contracts to resolve measurement feasibility and infrastructure issues without rewriting prior evidence. Gate C v1 closed at `contract_not_executable` for the frozen 16k paired rendering; v2 closed at `invalid_comparison`; v3 closed at `infrastructure_failure`; v4 established that the 8k ledger persistent phase can complete operationally in one uncontaminated attempt without reproducing the v3 CUDA-OOM crash. None of those intermediate outcomes supplied a valid efficacy result.

V5 produced the first complete valid paired efficacy comparison. Llama 3.2 3B reproduced the frozen 8k failure baseline at `0/6`. On 24 matched 8k cases, untreated scored `0/24` and ledger scored `7/24`, yielding seven wrong-to-correct flips, but the result missed both predeclared support thresholds: ledger `>=12/24` and delta `>=+8/24`. The canonical verdict is therefore [`unsupported_no_effect_or_insufficient_effect`](experiments/prototypes/mn-004-state-representation-intervention/reports/mn-004-v5-final-efficacy.md). The Llama 2k reference remained within its maximum-drop margin (`4/24` untreated to `2/24` ledger). Qwen untreated scored `14/24`, below its `20/24` eligibility requirement, so Qwen ledger was prohibited and the control is `control_not_qualified`.

The observed `0/24 -> 7/24` change is retained as a bounded signal, not as support for the frozen ledger hypothesis and not as permission to lower thresholds or tune the ledger post hoc. Ledger prompts also carried substantial token and latency overhead at 8k, so no token-independent structural mechanism is established.

MN-004 is complete for this intervention. Gate D promotion was not earned, no MN-004 code is promoted into `src/mong_nhiem/`, and no v6 continuation is justified.

## MN-005 — State Tracking Intervention Selection — completed and closed on ECC-006

MN-005 is complete as a bounded intervention-selection and candidate-audit milestone over the frozen ECC-006 Llama State Tracking failure region. It does not establish a winning architecture, and it does not establish that all candidate classes failed.

Its frozen [Gate A hypothesis](experiments/prototypes/mn-005-state-tracking-intervention-selection/gate-a-hypothesis.md) selected Multi-pass Reconstruction: a target-aware model-generated transcription of source target-update events in source order, passed literally between two fresh model calls. The host remained literal transport only and was prohibited from parsing, correcting, selecting, summarizing, or computing state from Stage A output.

The frozen [Gate B v1 measurement contract](experiments/prototypes/mn-005-state-tracking-intervention-selection/gate-b-measurement-contract.md) remains historical evidence. Its first prospective canonical attempt is retained as `experiment_invalid`: Arm B Stage A hit the v1 64-token cap before completing the fixed four-row neutral grammar; Arm A freshly reproduced `0/6` and Arm C never ran. Therefore no valid paired efficacy result exists from v1.

[Gate B v2](experiments/prototypes/mn-005-state-tracking-intervention-selection/gate-b-v2-measurement-contract.md) is frozen solely to repair that tokenizer-verifiable executability contradiction. It preserves the grammar and causal/support contract, increases the common B/C Stage A cap to `80` by a predeclared strict-fit rule, and requires persistence-before-validation plus Arm B exact-grammar validation before Stage B. Its first fully valid Gate C v2 attempt, [`attempt-0002`](experiments/prototypes/mn-005-state-tracking-intervention-selection/reports/mn-005-gate-c-v2-attempt-0002.md), is canonical and `inconclusive`: Arm A was `0/6`, Arm B was `0/6`, Arm C was `1/6`, and `D=+1`; the sole beneficial flip lacked a clean exact reconstruction. None of the six Arm C Stage A artifacts satisfied the intended exact-reconstruction criterion. The result therefore does not show that the hypothesized reconstruction mechanism caused the improvement. No replacement `attempt-0003` is authorized under the same contract.

The subsequent [Hierarchical State Representation audit](experiments/prototypes/mn-005-state-tracking-intervention-selection/hierarchical-gate-a.md) is `hierarchical_gate_a_unselected`, not an experimental failure. Frozen ECC-006 already presents each target trajectory as an ordered contiguous four-event block with no distractor inside it, so a hierarchy treatment cannot be isolated there from grouping, formatting, compression, reordering, target salience, or answer simplification.

External State Management remains a strong architectural hypothesis class, but ECC-006's final-state endpoint would make host-maintained state too close to the evaluated answer. Event-to-State Normalization and Symmetric State Partitioning are likewise weakly observable under the regular syntax and contiguous target layout. These are workload-bounded judgments, not universal rankings.

The accumulated MN-005 conclusion is that frozen ECC-006 has become insufficiently discriminative for several deeper state-management hypotheses. Candidate selection therefore stops on ECC-006 rather than manufacturing additional efficacy attempts whose mechanisms cannot be isolated cleanly.

The canonical research transition is documented in the [MN-005 → MN-006 handoff](experiments/prototypes/mn-005-state-tracking-intervention-selection/mn-006-handoff.md).

## MN-006 — Distributed State Integration — completed and closed

MN-006 is complete and closed for further model execution under its frozen contracts. Its original goal was to obtain a construct-valid matched contiguous-versus-interleaved measurement of distributed-state locality/integration.

The v1 equality/label response path was protocol-valid but non-diagnostic: baseline attempts and the D1/S0/S1/explicit-relation ladder established a lower-level conditioned-output confound, so locality was never attributable from that interface. The fixed-label branch is closed and D2 remains permanently unauthorized under v1.

The replacement direct ordered two-entity state-vector interface removed the equality-to-label adapter. Its canonical [qualification](experiments/prototypes/mn-006-distributed-state-integration/reports/mn-006-direct-state-vector-qualification-run-0001.md) is `protocol_valid` / `direct_state_vector_interface_blocked`: Q0 exact response competence is `9/9`, while Q1 contiguous task-bearing final-state recovery is `1/9`. Under the frozen exact `18/18` rule, the interface cannot support a construct-valid locality comparison at the frozen Level 2 workload.

The resulting milestone disposition is `measurement_interface_blocked` for the qualified Llama/runtime. This is not evidence that locality failed, that interleaving has no effect, or that the model generally cannot track state. Locality remains **unmeasured**. No retry, alternate interface search, perfect-state diagnostic, locality run, or intervention is authorized. See the formal [MN-006 closure](experiments/prototypes/mn-006-distributed-state-integration/milestone-closure.md).

## MN-007 — State Recovery Operating Region — completed and closed

MN-007 inherited the prerequisite exposed by MN-006: identify whether the qualified small-model/runtime (Llama-3.2-3B-Instruct Q4_K_M) has a prospectively defined contiguous two-entity latest-state recovery operating region suitable for a later causal locality experiment.

The canonical clean calibration rerun (`calibration-run-0002`, executed under clean commit `bfecd51`, evidence commit `23906e8`) completed all 108 requests under the frozen `mn007-interleaved-cell-round-robin-v1` order without retries or mutations. Every request was protocol-valid. The persist-before-evaluate contract was strictly enforced, with evaluation executed from disk artifacts via `scripts/mn007_evaluator.py`.

All six cells in the prospective landscape fell into the `floor` classification:
- `e3-terminal`: $P=18, C=3$ (16.7%) — `floor`
- `e3-leading`: $P=18, C=4$ (22.2%) — `floor`
- `e5-terminal`: $P=18, C=1$ (5.6%) — `floor`
- `e5-leading`: $P=18, C=2$ (11.1%) — `floor`
- `e7-terminal`: $P=18, C=1$ (5.6%) — `floor`
- `e7-leading`: $P=18, C=3$ (16.7%) — `floor`

The canonical outcome is **`no usable operating region in bounded landscape`**. Under the prospective design gate, this is a bounded negative result: no seed cell is selected, and no adaptive parameter tuning, prompt modification, threshold lowering, or landscape expansion is authorized within MN-007. MN-007 is formally closed. See [mn007-calibration-report.md](experiments/prototypes/mn-007-state-recovery-operating-region/mn007-calibration-report.md).

## MN-008 — External State Management — Gate C Phase 1 complete

MN-008 succeeds MN-007 to address the accumulated evidence across MN-003 (ECC-006), MN-004, MN-005, MN-006, and MN-007: small models (<4B) fail to reliably track and recover multi-entity state purely within implicit attention context.

MN-008 freezes its [Gate A hypothesis](experiments/prototypes/mn-008-external-state-management/gate-a-hypothesis.md) and its [Gate B measurement contract](experiments/prototypes/mn-008-external-state-management/gate-b-measurement-contract.md):
1. **Deterministic Host State Engine:** Ingests the raw event stream, maintains an exact state machine in host memory via verified logic ($O(1)$ amortized lookup), and formats a compact scoped state snapshot.
2. **Downstream LLM Conditional Reasoning:** The LLM consumes the snapshot to perform non-trivial conditional/causal evaluation over a Latin Square counterbalanced 4-branch decision matrix, escaping both the latent state-tracking bottleneck and the trivial copy-paste lookup trap identified in MN-005.
3. **Measurement Contract:** $N = 24$ cases ($E=5, U=3$), case-interleaved execution schedule, exact support rules ($A \le 6/24$ compatibility floor, $C \ge 18/24$ primary efficacy, $C - B \ge 10/24$ utility gate, $n_{B=1,C=0} = 0$ strict non-regression policy), hard preflight gate ($<100$ tokens for Arm C), and deterministic token sizing policy.
4. **Gate C Phase 1 (Materialization & Preflight):** Completed and verified.
   - Materialized canonical 24-case corpus in `definition/corpus-v1/` (`manifest.json` SHA-256: `61a2adbf1b8f29e90a302aa3065f7f5e08f812810b677a122297b8bfd1ba309c`).
   - Latin Square balance mathematically verified: each of 4 state pairs appears exactly 6 times; each of 4 actions is the target in exactly 6 cases.
   - Token budget hard preflight gate passed: all 24 Arm C Stage 2 prompts measure strictly $<100$ tokens under `Llama-3.2-3B-Instruct` tokenizer (max raw 87 tokens, max templated 96 tokens).
   - 7/7 unit tests pass in `tests/unit/test_mn008_materialization.py`.
Phase 2 (hermetic model runner execution) is the next required step.
