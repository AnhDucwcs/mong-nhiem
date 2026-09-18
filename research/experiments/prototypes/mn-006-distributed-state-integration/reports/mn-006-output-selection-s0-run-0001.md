# MN-006 output-selection S0 run-0001

## Status

**`protocol_valid` / `direct_copy_supported`.** This is a distinct L0 direct-copy diagnostic under `mn006-output-selection-minimality-v1`, not an MN-006 baseline attempt, locality measurement, D2 run, perfect-state control, or candidate intervention.

The frozen S0 plan supplied an explicit target label and retained only the constrained A/B output channel. All four independent requests returned the target label exactly. Both grammar-order pairs agreed, so there is no observed grammar-order asymmetry in this control. The result establishes direct copying only; it does not test equality, mapping abstraction, state reconstruction, or distributed locality.

## Identity and valid execution

- Run ID: `output-selection-s0-run-0001`.
- Executor commit: `a186908bbceeba31e18617b3530e50af25f895ef` (`MN-006: add S0 static executor boundary`).
- Plan SHA-256: `8180ea423a05eeb2930b84cee6102fd94595e13856f1a91e1afe4d599bb8e827`.
- Plan: exactly four requests in canonical ordinal order: A / G_AB, B / G_BA, B / G_AB, A / G_BA.
- Model: `llama-3.2-3b`, `Llama-3.2-3B-Instruct-Q4_K_M.gguf`, SHA-256 `6c1a2b41161032677be168d354123594c0e6e67d2b9227c84f296ad037c728ff`.
- Runtime: llama.cpp `0.2.0-dev`, build `10566`, commit `bb4caa754`; `/v1/chat/completions`, context `16896`, temperature `0.0`, seed `42`, maximum output `16`, threads `12`, batch `2048`, one slot, flash attention enabled, prompt cache disabled, and `--jinja`.
- Environment: NVIDIA GeForce RTX 3050 Laptop GPU, driver `595.95`; the pre-run snapshot recorded `0 MiB` GPU usage, `0%` utilization, no GPU compute process, and no existing local model process. The measurement server passed health before request 1 and was terminated by the runner after request 4.

There were no retries, no infrastructure failures, and no malformed outputs. Each completion had `finish_reason = stop`.

## Frozen S0 matrix

`G_AB`: `root ::= "A" | "B"`. `G_BA`: `root ::= "B" | "A"`. Both grammars include one final LF and accept the same language.

| Request | Target | Grammar order | Model label | Correct |
| ---: | --- | --- | --- | --- |
| 1 | A | G_AB | A | yes |
| 2 | B | G_BA | B | yes |
| 3 | B | G_AB | B | yes |
| 4 | A | G_BA | A | yes |

| Target | G_AB | G_BA | Agree? |
| --- | --- | --- | --- |
| A | A | A | yes |
| B | B | B | yes |

- Strict-parser-valid: `4/4`; malformed: `0/4`.
- Correct: `4/4`.
- Surface outputs: `A = 2`, `B = 2`.
- Grammar-order disagreements: `0/2` matched pairs.

The frozen classifier therefore selects `direct_copy_supported`: every required target was copied exactly, and neither matched grammar-order pair differed.

## Causal boundary and next action

S0 shows that the qualified model/runtime can condition the constrained A/B output on an explicitly supplied target label. It narrows the retained D1 all-A result: that result cannot be attributed solely to failure of this direct-copy L0 control. S0 does not distinguish direct equality computation from higher mapping abstraction, because neither is present in this control.

The frozen condition for the separate S1 direct-relation diagnostic is now met. **S1 is eligible only for a later separately authorized task and was not run here.** D2 remains unauthorized because its independent D1 `mapping_following_supported` prerequisite did not occur. No locality claim, perfect-state control, or intervention follows from S0.

## Evidence and integrity

The canonical retained evidence is:

- [Run metadata](../runs/output-selection-s0-run-0001/metadata.json)
- [Raw request/response records](../runs/output-selection-s0-run-0001/results.jsonl)
- [Machine-readable summary](../runs/output-selection-s0-run-0001/summary.json)
- [Server lifecycle and pre/post environment snapshots](../runs/output-selection-s0-run-0001/server-lifecycle.json)
- [Physical artifact integrity record](../runs/output-selection-s0-run-0001/integrity.json)
- [Server stderr log](../runs/output-selection-s0-run-0001/raw/llama-server.stderr.txt)

The integrity record verifies binary readback and SHA-256 for metadata, raw records, lifecycle, summary, and both server logs. The stored summary was recomputed from raw records with the frozen S0 evaluator and matched exactly.
