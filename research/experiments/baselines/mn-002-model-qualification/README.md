# MN-002 — Model Qualification

## Status

Completed. MN-002 establishes a local capability baseline before bounded ECC experiments; it is not a production-model selection or a general leaderboard.

## Research question

Which locally runnable small models meet a minimum, reproducible capability gate and are therefore meaningful ECC experiment subjects?

## Candidate set

Six local GGUF candidates were measured: Qwen3-1.7B, Llama-3.2-3B-Instruct, SmolLM3, Phi-4-mini-instruct, Gemma-3-4B-it, and Qwen3-4B. Model binaries are local inputs and are not committed.

## Benchmark history

### v0.1.0

Initial deterministic benchmark. Later audit identified output-contract defects.

### v0.2.0

Clarified output instructions and corrected native-thinking template integration for Qwen3 and SmolLM3. Remaining lexical-equivalence false negatives were identified.

### v0.3.0

Frozen JSONL definitions use explicit accepted values for semantic suites and strict JSON validation for structured output. Fingerprint: `2ac24df4e6cca12e13da577fb48db5da8e39d89cf3646ef705ea7679b4548f7a`.

## Qualification

Thresholds are unchanged: overall `>= 0.80`; instruction `>= 0.80`; structured `>= 0.90`; retrieval `>= 0.80`; state `>= 0.70`; causal `>= 0.70`. Every suite is critical.

| Model | Overall | Result |
| --- | ---: | --- |
| Llama-3.2-3B-Instruct-Q4_K_M | 0.89 | PASS |
| Qwen3-4B-Q4_K_M | 0.93 | PASS |

Qwen3-1.7B exceeds the overall threshold but fails the State gate. Gemma exceeds the overall threshold but fails the Structured gate. A candidate must meet every critical suite.

## Runtime and evidence

Capability qualification and runtime performance are separate. See the [v0.1 audit](reports/mcb-v0.1.0-audit.md), [v0.2 audit](reports/mcb-v0.2.0-audit.json), [v0.2 report](reports/model-qualification-v0.2.0.md), [v0.3 report](reports/model-qualification-v0.3.0.md), [v0.3 validation](reports/mcb-v0.3.0-validation.json), selected `runs/` artefacts, and [retention policy](reports/artifact-retention-policy.md).

## Reproduction

From a clean checkout with the required local model files and `llama-server`:

```powershell
python research/experiments/baselines/mn-002-model-qualification/scripts/validate_mcb_v030.py
python research/experiments/baselines/mn-002-model-qualification/scripts/run_mcb_v030.py --run-all
```

The validation command verifies the committed historical evidence. The runner creates a future v0.3 run; it does not regenerate frozen benchmark definitions.

## Limitations

MCB is a small synthetic qualification benchmark, not a long-context benchmark or general leaderboard. Its accepted-answer contract is finite. Historical v0.3 runs executed with Git `HEAD` at `a6e6c49` while the v0.3 changes were present in the working tree; the frozen fingerprint and persisted requests/raw outputs allow deterministic verification. The committed runner supports future end-to-end reproduction.
