# ECC-004 — Confirmatory Llama Evidence Position Sensitivity

## Status

Definition frozen; canonical execution is pending. ECC-004 is a bounded Llama-only direct-context confirmation under MN-003. It does not implement or evaluate a context-management architecture.

## Question and rationale

ECC-003 found measurable Llama 3.2 3B position sensitivity in a confusable single-fact retrieval task: at 16,384 requested tokens, early/middle/late accuracy was 1.00/0.85/0.70 across 20 cases. ECC-004 asks whether this directional effect persists with 40 fresh independent cases, giving 0.025 accuracy resolution.

Only Llama 3.2 3B is run. This is a follow-up for a Llama-specific observed effect, not a new cross-model comparison. Qwen3-4B's ECC-003 360/360 result remains historical bounded reference; its absence from ECC-004 is not a production-model selection.

## Frozen design

- **Matrix:** 40 fresh cases × 8,192 and 16,384 requested model-input tokens × early/middle/late evidence positions = exactly 240 canonical requests.
- **Task:** target and distractors are ordinary same-template `Registry entry` records. There is one target, no marker, no target-specific delimiter, no target leakage, and exact deterministic evaluation.
- **Fresh inventory:** entities and access codes are deterministic and unique; validator rejects overlap with ECC-002/ECC-003 target inventories.
- **Placement:** early 0.10, middle 0.50, late 0.90, each measured with model tokens and allowed ±0.05 error. ECC-003 allocation logic is retained.
- **Inference:** Llama 3.2 3B; llama.cpp; temperature 0; seed 42; output budget 16; context size 16,896; threads 12; batch 2,048; one parallel slot; Flash Attention on; prompt cache off; unchanged Llama chat-template kwargs.
- **Token accounting:** bounded calibration is reused from ECC-003, but each selected prompt is measured with the actual runtime. Overflow and truncation are invalid evidence.

ECC-004 intentionally has no new ECC95/ECC90/ECC80 calculations because its two long-context levels are not a full ladder. ECC-003 remains the full-ladder threshold evidence.

## Predeclared endpoint and interpretation

The primary endpoint is the 16,384-token `early − late` accuracy difference. Secondary endpoints are 16k early−middle and middle−late, plus all 8k pairwise differences. For each level, the summary retains position gap and paired-case transitions for early/middle, early/late, and middle/late.

The result is classified as **replicated** only if all conditions hold at 16k:

1. early accuracy exceeds late accuracy;
2. early−late gap is at least 0.10;
3. at least four fresh cases are early-pass/late-fail; and
4. early-pass/late-fail outnumbers early-fail/late-pass.

If early exceeds late but not every condition holds, the result is reported as partially replicated or weakened with unmet conditions. Otherwise it is reported as not replicated. These criteria do not establish a causal mechanism or a lost-in-the-middle label.

## Diagnostics and evidence

Canonical scoring remains normalized exact match. Deterministic diagnostics do not change score and classify every failure as one of:

- `tracked_distractor_code`
- `expected_code_with_extra_text`
- `invented_code`
- `partial_or_malformed_code`
- `other_text`

Each retained result includes model-token accounting, placement, deterministic distractor metadata, prompt hash, raw request/response, normalized output, exact score, diagnostic, truncation/error state, and request time. The validator recomputes all of these plus complete 240-row coverage, paired transitions, summary metrics, diagnostics, and confirmation classification.

## Reproduction

Run cheap checks before expensive inference:

```powershell
.venv\Scripts\python.exe -m pytest tests\unit\test_ecc004_contracts.py
.venv\Scripts\python.exe scripts\validate_ecc004.py
```

Minimal smoke examples are intentionally partial and must not be retained as canonical evidence:

```powershell
.venv\Scripts\python.exe scripts\run_ecc004.py --context-level 8192 --case-limit 2 --output-dir <smoke-output>
.venv\Scripts\python.exe scripts\run_ecc004.py --context-level 16384 --case-limit 1 --output-dir <smoke-output>
```

Only the full predefined matrix produced from a clean worktree belongs under `runs/`:

```powershell
.venv\Scripts\python.exe scripts\run_ecc004.py --output-dir <canonical-staging-output>
.venv\Scripts\python.exe scripts\validate_ecc004.py <canonical-run>
```

## Non-goals

ECC-004 does not implement or select retrieval, RAG, memory, summarization, compression, routing, embeddings, semantic search, external state, or any architecture intervention. Its purpose is confirmation or falsification of a bounded direct-context observation before any such work is considered.
