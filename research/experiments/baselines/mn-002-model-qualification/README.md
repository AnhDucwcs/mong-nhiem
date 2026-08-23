# MN-002 — Model Qualification

Status: active

## Question

Which locally runnable small language models have sufficient minimum capability and practical runtime characteristics to serve as meaningful subjects for subsequent Mộng Nhiễm experiments?

## Purpose

MN-002 establishes a reproducible model-selection baseline before experiments on Effective Context Capacity begin.

It measures two separate properties:

1. minimum model capability;
2. local runtime performance.

These measurements must remain separate.

A fast model that cannot reliably perform basic instruction following, context use, state tracking, or causal reasoning is not a useful research subject.

A capable model may still be impractical because of latency, throughput, RAM, or VRAM requirements.

## Candidate models

Current local GGUF candidates:

- `Qwen3-1.7B-Q4_K_M.gguf`
- `Llama-3.2-3B-Instruct-Q4_K_M.gguf`
- `SmolLM3-Q4_K_M.gguf`
- `microsoft_Phi-4-mini-instruct-Q4_K_M.gguf`
- `gemma-3-4b-it-Q4_K_M.gguf`
- `Qwen3-4B-Q4_K_M.gguf`

Local model directory:

`artifacts/models/mn-002/`

Model artifacts are local research inputs and must not be committed.

Every measurement must identify the exact GGUF using at least:

- filename;
- file size;
- SHA-256.

## Minimum Capability Benchmark

MN-002 defines Minimum Capability Benchmark `MCB v0.1.0`.

MCB is a qualification gate, not a general-purpose model leaderboard.

It contains five suites:

| Suite | Cases | Purpose |
| --- | ---: | --- |
| `instruction_following` | 20 | Follow explicit instructions and output constraints. |
| `structured_output` | 20 | Produce machine-readable structured output correctly. |
| `context_retrieval` | 20 | Retrieve supplied facts from synthetic context. |
| `state_tracking` | 20 | Maintain current state across ordered updates. |
| `causal_reasoning` | 20 | Follow supplied causal rules and short causal chains. |

Total: 100 cases.

Cases should be:

- deterministic;
- small;
- primarily synthetic;
- independent of internet access;
- designed to isolate the intended capability rather than world knowledge.

## Instruction following

Cases should test:

- exact requested output;
- selecting requested items;
- explicit output constraints;
- negative instructions;
- avoiding unsolicited explanation when exact output is required.

## Structured output

Cases should test:

- valid JSON;
- required fields;
- exact fields where specified;
- primitive types;
- arrays;
- objects;
- basic schema compliance.

JSON-like but invalid output does not pass a strict JSON case.

## Context retrieval

Cases should use synthetic facts where practical.

Vary:

- target position;
- distractor count;
- entity similarity;
- short and moderate context length.

This suite tests minimum supplied-context use.

It is not a long-context benchmark.

## State tracking

Cases should include:

- ownership transfer;
- location changes;
- overwrites;
- deletion/removal;
- temporal ordering;
- old versus latest state;
- multi-step state transitions.

## Causal reasoning

Cases should include:

- direct consequences;
- short causal chains;
- explicit rule application;
- blocked intermediate causes;
- simple counterfactuals;
- irrelevant distractors.

Causal rules should be supplied by the case rather than assumed from external knowledge whenever practical.

## Deterministic evaluation

MCB v0.1.0 must not use LLM-as-a-judge.

Evaluation must be deterministic.

Supported evaluator types should include at least:

- `exact_match`
- `normalized_exact_match`
- `choice_match`
- `json_schema`
- `contains_all`
- `unordered_set_match`
- `numeric_match`

Raw model output must be retained before normalization or parsing.

## Qualification

Initial MCB v0.1.0 thresholds:

| Suite | Minimum |
| --- | ---: |
| `instruction_following` | 0.80 |
| `structured_output` | 0.90 |
| `context_retrieval` | 0.80 |
| `state_tracking` | 0.70 |
| `causal_reasoning` | 0.70 |

Minimum overall score: `0.80`.

All five suites are critical.

A model qualifies only when:

- overall score is at least `0.80`; and
- every suite meets its own threshold.

These thresholds are experimental parameters of MCB v0.1.0.

They must not be changed after observing results merely to cause a particular candidate to pass.

## Runtime baseline

Runtime performance is measured separately from capability.

Record where reliably available:

- model load time;
- prompt-processing throughput;
- generation throughput;
- request latency;
- RAM;
- VRAM.

Performance does not contribute to MCB capability score.

Existing runtime measurements under `results/` are evidence and should be preserved.

## Baseline inference configuration

Qualification runs should minimize stochastic variation.

Default configuration:

- temperature: `0`;
- seed: `42`;
- context size: `4096`.

Other runtime parameters must be recorded using their actual values.

Use the model's supported GGUF/chat template rather than manually tailoring prompt formatting to improve individual model results.

## Reproducibility

A run should preserve enough information to identify:

- benchmark version;
- repository commit;
- model filename;
- model SHA-256;
- model size;
- llama.cpp version/revision;
- llama.cpp build information where available;
- inference configuration;
- operating system;
- CPU;
- system RAM;
- GPU;
- VRAM;
- driver;
- CUDA information where available;
- raw model outputs;
- deterministic evaluator results;
- timing and throughput measurements where available.

Unavailable metadata must remain unknown or null rather than inferred.

## Data contracts

MCB should define machine-readable schemas for:

- benchmark cases;
- run metadata;
- per-case results;
- run summaries.

Use JSON Schema Draft 2020-12 unless repository conventions require otherwise.

## Error handling

Distinguish:

- model failure;
- evaluator or benchmark failure;
- infrastructure failure.

An infrastructure-invalid run must not be converted into ordinary capability failures.

Failure of one candidate must not prevent attempts on the remaining candidates.

## Success criteria

MN-002 is complete when:

1. MCB v0.1.0 is machine-validatable.
2. Five suites exist.
3. Each suite contains exactly 20 cases.
4. All 100 cases validate against their schema.
5. All six candidate GGUF artifacts have been attempted.
6. Valid runs preserve reproducibility metadata.
7. Scores are calculated from per-case results.
8. Capability and runtime performance remain separate.
9. A comparison identifies the models qualified for downstream experiments.
10. Errors and limitations are explicitly recorded.

## Evidence

Existing runtime evidence is stored under `results/`.

Minimum Capability Benchmark results have not yet been completed for all candidate models.

## Conclusion

No final model qualification decision has been established yet.