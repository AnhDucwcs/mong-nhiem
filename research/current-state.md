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

## MN-005 — State Tracking Intervention Selection — prepared / design phase

MN-005 is prepared as a separate successor milestone. Its [design foundation](experiments/prototypes/mn-005-state-tracking-intervention-selection/README.md) inherits MN-003 and MN-004 as immutable evidence and has not selected an intervention, definition, runner, implementation, or measured experiment.

The immediate question is not how to rescue the MN-004 ledger, but which distinct, falsifiable mechanism is best justified next. Candidate directions currently include mechanism decomposition of the MN-004 representation package, token-efficient explicit ordering, hierarchical/checkpointed state representation, and a larger external-state/register hypothesis class. Resource coexistence with games and other local workloads is retained as a later deployment-robustness dimension rather than being confused with controlled mechanism evidence.

MN-005 Gate A must compare candidate mechanisms and select exactly one hypothesis before Gate B measurement design or any model execution. No architecture is selected.
