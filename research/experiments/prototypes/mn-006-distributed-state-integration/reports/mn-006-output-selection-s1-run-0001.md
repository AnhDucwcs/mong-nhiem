# MN-006 output-selection S1 run-0001

## Status

**`protocol_valid` / `fixed_label_preference_recurred`.** This distinct L1 direct-relation diagnostic under `mn006-output-selection-minimality-v1` is not an MN-006 baseline attempt, locality measurement, D2 run, perfect-state control, or candidate intervention.

S1 retained S0's neutral constrained A/B channel, supplied two final states directly, and removed D1's counterbalanced mapping table. Under the frozen direct rule `equal -> A; different -> B`, all four independent requests returned `A`. The two equal-state cases were correct and the two unequal-state cases were wrong. Direct equality/instruction following is therefore not established under this exact interface.

## Identity and valid execution

- Run ID: `output-selection-s1-run-0001`.
- Executor commit: `a7a2f4bd5fe7ecb55257565bdc0b7c56e90b3ab3` (`MN-006: add S1 static executor boundary`).
- Plan SHA-256: `8180ea423a05eeb2930b84cee6102fd94595e13856f1a91e1afe4d599bb8e827`.
- S0 prerequisite: integrity-valid `output-selection-s0-run-0001`, `protocol_valid` / `direct_copy_supported`; mechanically revalidated by the executor before request construction.
- Plan: exactly four requests in canonical ordinal order, all using `G_AB`: unequal S1/S2 -> B; equal S1/S1 -> A; equal S2/S2 -> A; unequal S2/S1 -> B.
- Model: `llama-3.2-3b`, `Llama-3.2-3B-Instruct-Q4_K_M.gguf`, SHA-256 `6c1a2b41161032677be168d354123594c0e6e67d2b9227c84f296ad037c728ff`.
- Runtime: llama.cpp `0.2.0-dev`, build `10566`, commit `bb4caa754`; `/v1/chat/completions`, context `16896`, temperature `0.0`, seed `42`, maximum output `16`, threads `12`, batch `2048`, one slot, flash attention enabled, prompt cache disabled, and `--jinja`.
- Environment: NVIDIA GeForce RTX 3050 Laptop GPU, driver `595.95`; the pre-run snapshot recorded `0 MiB` GPU usage, `0%` utilization, no GPU compute process, and no existing local model process. The measurement server passed health before request 1 and was terminated by the runner after request 4.

There were no retries, no infrastructure failures, and no malformed outputs. Each completion had `finish_reason = stop`.

## Frozen S1 matrix

`G_AB`: `root ::= "A" | "B"`, with one final LF. S1 deliberately has no `G_BA` condition: D1 and S0 already audited grammar order, while S1 isolates the direct relation instruction.

| Request | States | Relation | Expected label | Model label | Correct |
| ---: | --- | --- | --- | --- | --- |
| 1 | S1 / S2 | unequal | B | A | no |
| 2 | S1 / S1 | equal | A | A | yes |
| 3 | S2 / S2 | equal | A | A | yes |
| 4 | S2 / S1 | unequal | B | A | no |

- Strict-parser-valid: `4/4`; malformed: `0/4`.
- Correct: `2/4`.
- Surface outputs: `A = 4`, `B = 0`.
- Grammar-order comparison: not a factor in S1 by frozen design; every request used `G_AB`.

The frozen S1 classifier therefore selects `fixed_label_preference_recurred`: all complete, parseable outputs were the same surface label and not every direct-relation answer was correct.

## Causal boundary and next action

S0 established that this model/runtime can copy both explicitly supplied A/B labels in the frozen constrained channel. S1 does not establish direct equality/inequality instruction following because the output did not condition on the unequal relation under its fixed direct rule. Consequently, the existing D1 all-A result cannot be localized specifically to D1's additional counterbalanced mapping-table abstraction. This is a behavioral result under the exact protocol; it does not identify an internal mechanism, establish state-reconstruction failure, or establish a locality effect.

D2 remains blocked independently because canonical D1 is `fixed_label_preference_supported`, not `mapping_following_supported`. No locality measurement, perfect-state diagnostic, or candidate intervention is authorized by S1. The next permitted work is a separately authorized static causal-design review of the recurring A-label behavior; no further model run is authorized by this result alone.

## Evidence and integrity

The canonical retained evidence is:

- [Run metadata](../runs/output-selection-s1-run-0001/metadata.json)
- [Raw request/response records](../runs/output-selection-s1-run-0001/results.jsonl)
- [Machine-readable summary](../runs/output-selection-s1-run-0001/summary.json)
- [Server lifecycle and pre/post environment snapshots](../runs/output-selection-s1-run-0001/server-lifecycle.json)
- [Physical artifact integrity record](../runs/output-selection-s1-run-0001/integrity.json)
- [Server stderr log](../runs/output-selection-s1-run-0001/raw/llama-server.stderr.txt)

The integrity record verifies binary readback and SHA-256 for metadata, raw records, lifecycle, summary, and both server logs. The stored summary was recomputed from raw records with the frozen S1 evaluator and matched exactly.
