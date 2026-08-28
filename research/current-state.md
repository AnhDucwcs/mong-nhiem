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

## MN-004 — State Representation Intervention Design — prepared

MN-004 is prepared as a design-only successor under `research/experiments/prototypes/`; [its charter](experiments/prototypes/mn-004-state-representation-intervention/README.md) is the canonical scope. No intervention is selected, no MN-004 experiment definition or implementation exists, and no MN-004 evidence has been produced.

It inherits ECC-006 as immutable direct-context baseline evidence and must initially retain the Llama 3.2 3B subject for a causal comparison. The current work is Gate A/B only: select and justify one explicit, inspectable state-representation hypothesis, then freeze semantic equivalence, baseline/intervention conditions, controls, evaluator, failure taxonomy, sample-size rationale, aggregate success threshold, no-harm criteria, contamination rules, and retained-evidence policy. Only then can implementation be authorized. It must not assume retrieval, RAG, memory, summarization, compression, routing, embeddings, or external state as the solution.
