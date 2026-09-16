# MN-006 label-selection D1 diagnostic run-0001

## Status

**`protocol_valid` / `fixed_label_preference_supported`.** This is a separate direct-state, neutral-label causal diagnostic under `mn006-label-selection-diagnostic-v1`; it is neither `attempt-0003` nor an MN-006 baseline measurement. It does not test state reconstruction, distributed locality, a perfect-state control, or a candidate intervention.

The result is retained because it localizes the immediate obstruction: under the frozen constrained channel, the model selected surface label `A` for all 16 counterbalanced direct-mapping requests. The D1 result supports a fixed-label/response-selection mechanism under this diagnostic; it does not establish the magnitude or internal source of any token/logit preference, and it does not establish a state-computation failure.

## Identity and valid execution

- Run ID: `label-selection-d1-run-0001`.
- Executor commit: `ebd8420fa3fb9ba5bc68bd3e0fafaa0dfd4b7515` (`MN-006: add label-selection D1 executor`).
- Plan SHA-256: `cfa3aac029aa803cfbd546bf9bba3808739f343758acadca12214d53af4aa465`.
- Plan: source ordinals `0`, `1`, `2`, and `3`; two equal-state and two unequal-state sources; mappings `M1_equal_A` and `M2_equal_B`; both `G_AB` and `G_BA` for each source/mapping cell; 16 independent requests total.
- Model: `llama-3.2-3b`, `Llama-3.2-3B-Instruct-Q4_K_M.gguf`, SHA-256 `6c1a2b41161032677be168d354123594c0e6e67d2b9227c84f296ad037c728ff`.
- Runtime: llama.cpp `0.2.0-dev`, build `10566`, commit `bb4caa754`; context `16896`, temperature `0.0`, seed `42`, maximum output `16`, threads `12`, batch `2048`, one slot, flash attention enabled, prompt cache disabled, and `--jinja`.
- Environment: NVIDIA GeForce RTX 3050 Laptop GPU, driver `595.95`; the pre-run snapshot recorded `0 MiB` GPU usage, `0%` GPU utilization, no GPU compute process, and no existing local model server. The measurement server passed health before request 1 and was terminated by the runner after request 16.

All 16 requests completed in the frozen plan order: source ordinal ascending; mapping order alternating by source ordinal; grammar order prescribed by the plan. There were no retries, no infrastructure failures, and no malformed outputs. Every completion had `finish_reason = stop`.

## Frozen D1 matrix

`M1`: equal -> `A`, unequal -> `B`. `M2`: equal -> `B`, unequal -> `A`. `G_AB`: `root ::= "A" | "B"`; `G_BA`: `root ::= "B" | "A"`. Both grammars include one final LF and accept the same language.

| Request | Source ordinal | Relation | Mapping | Grammar order | Canonical label | Model label | Correct |
| ---: | ---: | --- | --- | --- | --- | --- | --- |
| 1 | 0 | equal | M1 | G_AB | A | A | yes |
| 2 | 0 | equal | M1 | G_BA | A | A | yes |
| 3 | 0 | equal | M2 | G_BA | B | A | no |
| 4 | 0 | equal | M2 | G_AB | B | A | no |
| 5 | 1 | unequal | M2 | G_BA | A | A | yes |
| 6 | 1 | unequal | M2 | G_AB | A | A | yes |
| 7 | 1 | unequal | M1 | G_AB | B | A | no |
| 8 | 1 | unequal | M1 | G_BA | B | A | no |
| 9 | 2 | equal | M1 | G_AB | A | A | yes |
| 10 | 2 | equal | M1 | G_BA | A | A | yes |
| 11 | 2 | equal | M2 | G_BA | B | A | no |
| 12 | 2 | equal | M2 | G_AB | B | A | no |
| 13 | 3 | unequal | M2 | G_BA | A | A | yes |
| 14 | 3 | unequal | M2 | G_AB | A | A | yes |
| 15 | 3 | unequal | M1 | G_AB | B | A | no |
| 16 | 3 | unequal | M1 | G_BA | B | A | no |

## Grammar-order control and summaries

| Source | Mapping | G_AB | G_BA | Agree? |
| ---: | --- | --- | --- | --- |
| 0 | M1 | A | A | yes |
| 0 | M2 | A | A | yes |
| 1 | M1 | A | A | yes |
| 1 | M2 | A | A | yes |
| 2 | M1 | A | A | yes |
| 2 | M2 | A | A | yes |
| 3 | M1 | A | A | yes |
| 3 | M2 | A | A | yes |

- Strict-parser-valid: `16/16`; malformed: `0/16`.
- Correct: `8/16`.
- Surface outputs: `A = 16`, `B = 0`.
- Mapping accuracy: `M1 = 4/8`; `M2 = 4/8`.
- Relation accuracy: equal = `4/8`; unequal = `4/8`.
- Grammar-order disagreements: `0/8` matched pairs.

The frozen classifier therefore selects `fixed_label_preference_supported`: all outputs parse, every grammar-order pair agrees, and all 16 retained outputs are the same surface label. The all-`A` observation must not be read as a quantified logit preference; logprob data were not retained.

## Causal boundary and next action

- **H1 — grammar/runtime asymmetry:** no grammar-order asymmetry was observed in D1. This does not prove probabilistic symmetry beyond the earlier static audit, but the observed D1 classification is not the H1 precedence condition.
- **H2 — response selection / label preference:** supported under this bounded neutral-label direct-mapping diagnostic. The model did not follow the counterbalanced mapping when the correct surface label was `B`.
- **H3 — underlying state/equality computation failure:** not isolated by D1. D1 supplied final states directly and the fixed-label collapse prevents a clean inference about equality or mapping computation.

D2 is **not eligible**: its frozen authorization required D1 `mapping_following_supported`, which was not observed. Consequently D2 was not run, no locality claim is made, no perfect-state diagnostic is authorized, and no candidate intervention was selected or tested. `attempt-0001` remains the unconstrained malformed-output floor; `attempt-0002` remains the constrained all-`INVALID` baseline collapse. D1 does not pool with or rewrite either baseline.

## Evidence and integrity

The canonical retained evidence is:

- [Run metadata](../runs/label-selection-d1-run-0001/metadata.json)
- [Raw request/response records](../runs/label-selection-d1-run-0001/results.jsonl)
- [Machine-readable summary](../runs/label-selection-d1-run-0001/summary.json)
- [Server lifecycle and pre/post environment snapshots](../runs/label-selection-d1-run-0001/server-lifecycle.json)
- [Physical artifact integrity record](../runs/label-selection-d1-run-0001/integrity.json)
- [Server stderr log](../runs/label-selection-d1-run-0001/raw/llama-server.stderr.txt)

The integrity record verifies binary readback and SHA-256 for metadata, raw records, lifecycle, summary, and both server logs. The stored summary was recomputed from the raw records with the frozen D1 evaluator and matched exactly.
