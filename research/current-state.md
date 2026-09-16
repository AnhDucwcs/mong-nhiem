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

## MN-006 — Distributed State Integration workload design — first baseline complete, no usable locality signal

MN-006 completed [Design Gate B](experiments/prototypes/mn-006-distributed-state-integration/design-gate-b.md), which freezes the [v1 semantic workload contract](experiments/prototypes/mn-006-distributed-state-integration/workload-contract.md) and [v1 case schema](experiments/prototypes/mn-006-distributed-state-integration/case-schema.md). Its deterministic infrastructure and the [Baseline Inventory and Measurement Gate](experiments/prototypes/mn-006-distributed-state-integration/baseline-inventory-measurement-gate.md) materialized 32 matched pairs per profile (64 pairs / 128 public prompts total), identified by the canonical [inventory manifest](experiments/prototypes/mn-006-distributed-state-integration/definition/baseline-inventory-v1/manifest.json). The canonical Llama [attempt-0001 report](experiments/prototypes/mn-006-distributed-state-integration/reports/mn-006-attempt-0001.md) is `protocol_valid`: all 128 requests completed, inventory/prompt integrity and paired recomputation passed, and the server terminated normally. However, all outputs were malformed under the frozen exact-label parser, yielding `0/32` contiguous and `0/32` interleaved exact correctness in both profiles. Both profile classifications are therefore `no_usable_locality_failure_signal_under_v1_baseline`, not an interleaving effect. The regular round-robin schedule's periodicity remains an audited v1 limitation, not a claim about arbitrary interleaving.

The planned primary question is no longer which intervention to try next on ECC-006. It is whether a candidate-neutral experimental substrate can expose distributed state-integration failures while remaining deterministic enough to compare multiple state-management hypotheses causally.

The working workload direction is distributed/interleaved multi-entity state tracking followed by minimal bounded deterministic downstream reasoning. State tracking remains the central subject; downstream reasoning is introduced only so that maintained external state is useful input rather than the final answer itself. The task must not become a general reasoning benchmark.

MN-006 should initially change as few dimensions as possible: make related entity updates genuinely distributed/interleaved and add only the minimum deterministic downstream rule needed to avoid an answer-oracle interface. Other dimensions such as true hierarchy, nested scope, causal dependency, noisy language, cross-episode persistence, and long-term memory should stay simple until evidence justifies changing them.

The workload design must define canonical source events, canonical final entity state, canonical derived facts, and a finite canonical final answer so future evaluation can distinguish state-tracking failure, downstream-reasoning failure, and end-to-end failure without an LLM judge.

Previous candidates may be reconsidered on MN-006 only with workload-specific justification. Their MN-005 history remains intact: `unselected on ECC-006` is not reset to `untested`, and the Multi-pass `inconclusive` result remains canonical evidence.

MN-006 now has one immutable untreated Llama baseline, but no intervention comparison, Hierarchical treatment, External State treatment, or Multi-pass rerun. The perfect-state diagnostic is ineligible because neither profile met the signal rule and malformed outputs were `64/64` per profile. The [Response-Channel Gate](experiments/prototypes/mn-006-distributed-state-integration/response-channel-gate.md) is `response_channel_revision_ready`: it authorizes only a separate future `attempt-0002` with the same workload/public bytes/parser/evaluator and one globally constant `VALID`/`INVALID` grammar field. It is not a retry, locality conclusion, or intervention.

The separate uninvoked executor [`run_mn006_constrained_baseline.py`](experiments/prototypes/mn-006-distributed-state-integration/scripts/run_mn006_constrained_baseline.py) is prepared before any `attempt-0002` model behavior is observed. It retains the inventory, public prompts, parser, evaluator, runtime, and request order, adding only the globally constant request-level grammar; the next permitted step is clean-environment execution, not intervention work.
