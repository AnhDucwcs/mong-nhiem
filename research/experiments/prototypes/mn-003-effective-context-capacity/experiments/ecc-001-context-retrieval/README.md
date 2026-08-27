# ECC-001 — Context Retrieval under increasing context pressure

## Status

Experiment infrastructure implemented and the canonical direct-context baseline completed for both qualified models. See the [ECC-001 results](reports/ecc-001-results.md). MN-003 remains active because ECC-001 did not locate a degradation boundary within the tested ladder.

ECC-001 is the first bounded MN-003 measurement. It does not implement or evaluate a context-management architecture.

Canonical definition fingerprint: `d9c86595d84266dcc87becc4469bf5a1ed691a4cadbf30ef620d4ac8983efa29`.

## Hypothesis

As irrelevant direct-context length increases, normalized exact-match accuracy on a fixed single-fact retrieval task may decline for an MCB-qualified small local model. Stable accuracy across the tested ladder is an equally valid result.

## Design

- **Task:** retrieve one unambiguous project access code from direct, unmodified context.
- **Subjects:** the MN-002-qualified Llama 3.2 3B and Qwen3-4B GGUF capability baselines. Qualification is not production-model selection.
- **Semantic cases:** 20 deterministic synthetic cases with unique entities and unique short answers.
- **Independent variable:** requested model input length at 512, 1,024, 2,048, 4,096, 8,192, and 16,384 tokens.
- **Short-context baseline:** 512 requested input tokens.
- **Evidence position:** deterministic midpoint policy. The target fact begins at relative token position 0.50 within the context, with absolute tolerance 0.05.
- **Distractors:** deterministic, plausible registry records generated in symmetric before/after pairs from seed `20260827`.
- **Evaluation:** conservative normalized exact match. Unicode compatibility normalization, case folding, surrounding whitespace collapse, and terminal punctuation removal are allowed; explanations, changed separators, extra tokens, and semantic errors fail.
- **Generation:** temperature 0, seed 42, 16 output tokens, prompt cache disabled, one server slot.

Only context length changes within a model run. Relevant-information count, answer complexity, question form, evidence policy, distractor rules, evaluator, model configuration, and inference configuration remain fixed.

## Token-budget contract

The runner renders the model's actual chat template and tokenizes that rendered prompt through the active llama.cpp server before inference. Special tokens are included in prompt counts. It records requested and actual input tokens, content tokens, prompt overhead, context tokens, evidence position, configured context size, and output budget for every result.

Natural-language distractors are added as symmetric sentence pairs. Because token increments are discrete and model tokenizers differ, the largest permitted target shortfall is 96 tokens. Inputs may never exceed a target, and `actual_input_tokens + output_token_budget` may never exceed the configured 16,896-token runtime context. The runner rejects overflow and rejects any API prompt count that differs from preflight; it never silently truncates.

The semantic case and deterministic generator are shared across models, but the number of generated distractor pairs can differ because each model is built toward the ladder with its own tokenizer. Actual token counts and pair counts therefore govern interpretation; model prompts are semantically equivalent but not guaranteed byte-identical.

## Metrics

For each requested level, the summary records accuracy and:

```text
relative_accuracy(L) = accuracy(L) / baseline_accuracy
```

ECC95, ECC90, and ECC80 are the largest contiguous tested levels meeting 95%, 90%, and 80% of baseline accuracy. Evaluation stops at the first failed threshold level, so an isolated later pass cannot imply recovery. No interpolation is fabricated, and the complete curve plus a non-monotonicity flag is retained.

A metric equal to 16,384 means the threshold held through the largest tested level; it is a tested lower bound, not a claim about capacity beyond the ladder or the model's advertised context window.

## Success criteria

The predeclared implementation criteria are:

1. deterministic case generation;
2. reproducible model-token budget construction;
3. no silent truncation;
4. deterministic exact evaluation;
5. retained raw per-case request/response evidence;
6. aggregate accuracy by context level;
7. a derivable degradation curve;
8. derivable ECC thresholds when data support them;
9. one definition reusable across qualified models;
10. offline recomputation reproduces committed summaries.

Scientific success does not require degradation.

## Evidence contracts

- `definition/experiment.json` freezes the hypothesis, variables, controls, ladder, metrics, success criteria, and non-goals.
- `definition/cases.json` contains the deterministic semantic inventory.
- `configs/models.json` selects either qualified model and fixes chat-template behavior.
- `schemas/` defines experiment, metadata, per-case result, and summary artifacts.
- `runs/<run-id>/metadata.json` records model/runtime hashes and versions, hardware, inference settings, tokenizer/context settings, Git commit and dirty state, selection, and commands.
- `runs/<run-id>/results.jsonl` retains full request, raw response, normalized answer, evaluation, token counts, hashes, errors, and timing.
- `runs/<run-id>/summary.json` retains the recomputable curve and ECC metrics.
- `runs/<run-id>/raw/` retains llama.cpp stdout/stderr diagnostics.

The definition fingerprint is SHA-256 over labeled canonical UTF-8 JSON values for `experiment.json` and `cases.json`, with sorted object keys and a fixed newline. It excludes volatile run metadata and is independent of source line endings.

A complete run from a dirty worktree is invalid. This ensures its recorded Git commit actually contains the scientific definition and executable tooling.

## Reproduction

From the repository root, validate the definition and run cheap checks first:

```powershell
.venv\Scripts\python.exe research\experiments\prototypes\mn-003-effective-context-capacity\experiments\ecc-001-context-retrieval\scripts\validate_ecc001.py
.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests\unit\test_ecc001_contracts.py
```

Run a two-case, two-level smoke check:

```powershell
.venv\Scripts\python.exe research\experiments\prototypes\mn-003-effective-context-capacity\experiments\ecc-001-context-retrieval\scripts\run_ecc001.py --model llama-3.2-3b --context-level 512 --context-level 2048 --case-limit 2
```

Run a complete qualified-model matrix:

```powershell
.venv\Scripts\python.exe research\experiments\prototypes\mn-003-effective-context-capacity\experiments\ecc-001-context-retrieval\scripts\run_ecc001.py --model llama-3.2-3b
.venv\Scripts\python.exe research\experiments\prototypes\mn-003-effective-context-capacity\experiments\ecc-001-context-retrieval\scripts\run_ecc001.py --model qwen3-4b
```

The defaults match the retained MN-002 local artifact and llama.cpp locations. Use `--models-dir`, `--llama-server`, `--output-dir`, or `--port` when the local environment differs. The runner refuses missing dependencies, unknown cases/levels, token overflow, truncation, and preflight/API token-count disagreement.

Validate all canonical runs without inference:

```powershell
.venv\Scripts\python.exe research\experiments\prototypes\mn-003-effective-context-capacity\experiments\ecc-001-context-retrieval\scripts\validate_ecc001.py
```

## Retention policy

Commit the frozen definition/configuration, schemas, canonical scripts, complete per-case evidence, summaries, and raw runtime diagnostics used for the reported result. Smoke and pre-freeze development runs are not scientific results; keep them outside canonical `runs/` if retained for local diagnostics. Never overwrite a retained run.

Capability accuracy and runtime observations are reported separately. Model files remain local artifacts and must not be committed.

## Limitations

- ECC-001 studies only easy, single-fact Context Retrieval with evidence near the middle.
- Twenty cases give a coarse accuracy resolution of 0.05 per level.
- Evidence position, relevant-information density, distributed evidence, State Tracking, and Causal Reasoning are not varied here.
- Model-specific tokenization produces different actual prompt lengths and potentially different distractor-pair counts.
- The 16,384 ceiling preserves the configured output reserve and is not an advertised-window test.
- Runtime timing is descriptive environment evidence, not a production-performance benchmark.
- No retrieval, RAG, memory, summarization, compression, routing, or other intervention is selected or tested.
