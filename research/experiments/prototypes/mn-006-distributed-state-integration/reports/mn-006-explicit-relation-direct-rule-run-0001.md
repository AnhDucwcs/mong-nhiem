# MN-006 explicit-relation direct-rule run-0001

## Status

**`protocol_valid` / `fixed_label_preference_persisted`.** This distinct direct-rule diagnostic under `mn006-explicit-relation-direct-rule-v1` is not an MN-006 baseline attempt, D2 run, state-reconstruction measurement, locality measurement, perfect-state control, or intervention.

It supplied the semantic relation directly, removed structured-state extraction and equality comparison, retained S1's fixed rule `equal -> A; different -> B`, and retained the strict constrained A/B output channel. Both independent requests returned strict `A`: the explicit `different` relation was wrong and the explicit `equal` relation was correct.

## Identity and valid execution

- Run ID: `explicit-relation-direct-rule-run-0001`.
- Executor commit: `24424707e0dde730ef860753be383d1223426d6a` (`MN-006: add explicit-relation static executor boundary`).
- Authority-plan SHA-256: `dc40c15a896f5f0413783818c39593b8a9c34eeea3ef4ce284e1b311112bc80a`.
- Causal-review prerequisite: integrity-valid [recurring fixed-label causal review](../recurring-fixed-label-causal-review.md), SHA-256 `a5e4bbca96d18043d5b0280c076425ba9beedf30feaf149a5645e6196cb8580a`, disposition `next_minimal_diagnostic_identified`.
- S0 prerequisite: integrity-valid `output-selection-s0-run-0001`, `protocol_valid` / `direct_copy_supported`.
- S1 prerequisite: integrity-valid `output-selection-s1-run-0001`, `protocol_valid` / `fixed_label_preference_recurred`.
- Model: `llama-3.2-3b`, `Llama-3.2-3B-Instruct-Q4_K_M.gguf`, SHA-256 `6c1a2b41161032677be168d354123594c0e6e67d2b9227c84f296ad037c728ff`.
- Runtime: llama.cpp `0.2.0-dev`, build `10566`, commit `bb4caa754`; `/v1/chat/completions`, context `16896`, temperature `0.0`, seed `42`, maximum output `16`, threads `12`, batch `2048`, one slot, flash attention enabled, prompt cache disabled, and `--jinja`.
- Environment: NVIDIA GeForce RTX 3050 Laptop GPU, driver `595.95`; the retained pre-run snapshot records `0 MiB` GPU usage, `0%` utilization, no GPU compute process, and no pre-existing local model process. The runner recorded server health before request 1 and terminated its own measurement server after request 2.

There were no retries, no infrastructure failures, and no malformed outputs. Both completions had `finish_reason = stop`.

## Frozen two-request matrix

`G_AB`: `root ::= "A" | "B"`, with one final LF. Both requests use the same frozen grammar; grammar order and rule counterbalancing were intentionally not factors in this adjacent diagnostic cut.

| Request | Explicit relation | Expected label | Raw output | Strict parsed label | Correct |
| ---: | --- | --- | --- | --- | --- |
| 1 | different | B | `A` | A | no |
| 2 | equal | A | `A` | A | yes |

- Strict-parser-valid: `2/2`; malformed: `0/2`.
- Correct: `1/2`.
- Surface outputs: `A = 2`, `B = 0`.
- Request order: canonical authority order, `different` then `equal`.

The frozen classifier therefore selects `fixed_label_preference_persisted`: all complete, parseable outputs were one surface label and the direct-rule answers were not all correct.

## Causal boundary and next action

S0 established that this qualified model/runtime can copy both explicitly supplied A/B labels under the frozen constrained channel. S1 showed fixed `A` while requiring structured state extraction, equality comparison, direct-rule interpretation, and post-task label selection. This run supplied the relation directly and still returned `A` for both relations. Therefore structured-state extraction and equality comparison are not necessary conditions for the recurring fixed-`A` behavior under this exact interface.

The evidence does not identify whether the remaining failure is direct conditional-rule interpretation, post-task constrained-label selection, a surface/default preference, or another internal mechanism. It does not establish general reasoning ability, state-reconstruction failure, distributed-state integration failure, a locality effect, or intervention efficacy.

D2 remains blocked independently because canonical D1 is `fixed_label_preference_supported`, not `mapping_following_supported`. State reconstruction, locality measurement, perfect-state work, `attempt-0003`, and interventions remain unauthorized. The next permitted action is a separately authorized causal-design review of this updated fixed-label boundary; no additional model execution is authorized by this result alone.

## Evidence and integrity

The canonical retained evidence is:

- [Run metadata](../runs/explicit-relation-direct-rule-run-0001/metadata.json)
- [Raw request/response records](../runs/explicit-relation-direct-rule-run-0001/results.jsonl)
- [Machine-readable summary](../runs/explicit-relation-direct-rule-run-0001/summary.json)
- [Server lifecycle and retained environment snapshots](../runs/explicit-relation-direct-rule-run-0001/server-lifecycle.json)
- [Physical artifact integrity record](../runs/explicit-relation-direct-rule-run-0001/integrity.json)
- [Server stderr log](../runs/explicit-relation-direct-rule-run-0001/raw/llama-server.stderr.txt)

The integrity record verifies binary readback and SHA-256 for metadata, raw records, lifecycle, summary, and both server logs. The canonical validator recomputed the stored summary from the two raw records with the frozen classifier and matched it exactly.