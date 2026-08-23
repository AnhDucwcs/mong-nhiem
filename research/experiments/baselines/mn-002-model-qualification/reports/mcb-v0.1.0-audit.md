# MCB v0.1.0 failure audit

## Decision

**C. Revise benchmark version and rerun.** MCB v0.1.0 capability scores must not
be frozen because its State Tracking suite and many open-answer Causal Reasoning
cases had an output-contract defect: their prompts allowed explanatory answers,
but their evaluator required normalized exact equality. The correction changes
the requested response format, so it is a benchmark-version change rather than
an implementation-only fix.

MCB v0.2.0 preserves all case facts, logical answers, thresholds, suite weights,
and deterministic evaluators. It adds `Return only the answer, without
punctuation or explanation.` to every State Tracking and Causal Reasoning prompt.
It also applies the verified GGUF template option `enable_thinking=false` to
Qwen3 and SmolLM3, recording that setting in run metadata.

## Classifications

| Finding | Classification | Evidence |
| --- | --- | --- |
| Universal State Tracking 0.00 | `BENCHMARK_CASE_DEFECT` | All six models often produced the correct latest state plus explanation, e.g. `C has the key now.`; the v0.1 prompt did not demand exact-only output. Cases are supplied as one complete ordered event sequence in one user message, so this is not missing conversation history or state reset. |
| SmolLM3 universal 0.00 | `CHAT_TEMPLATE_OR_INTEGRATION_DEFECT` | API inspection showed `content: ""`, `reasoning_content` populated, and 16 completion tokens exhausted. The same prompt with native `chat_template_kwargs: {enable_thinking: false}` returned `amber` in final content. |
| Phi-4-mini structured output 0.00 | `VALID_MODEL_FAILURE` | Raw outputs are fenced JSON despite an explicit `Return only valid JSON, no Markdown` prompt. The strict JSON parser correctly rejects markdown fences. |
| Representative causal failures | `BENCHMARK_CASE_DEFECT` in v0.1 | Models frequently state the correct consequence with an explanation or terminal period; open-answer prompts did not require exact-only output, while the evaluator rejected both. |

The machine-readable case-level audit is in `mcb-v0.1.0-audit.json`; it records
rendered message, raw/parsed response, expected value, score, classification,
and a reference to the source run.

## v0.2.0 rerun

All six candidates were rerun under v0.2.0. No threshold was lowered and no
model qualified. The report in `model-qualification-v0.2.0.md` supersedes the
v0.1.0 capability comparison, while the v0.1.0 run data remains historical
evidence. Under MCB v0.2.0 and the corrected evaluation harness, no tested
candidate satisfied all qualification gates.

## Baseline recommendation

No candidate is qualified for an ECC prototype under the gate. If a bounded
integration prototype must proceed before a qualified replacement is found,
Qwen3-1.7B is the least-cost exploratory option: it has verified Qwen template
integration, leads generation throughput in existing runtime evidence, and has
strong instruction/structured-output results. This is not a qualification pass
and must not be treated as evidence of ECC suitability.
