# MN-006 direct-state-vector qualification run-0001

## Status

**`protocol_valid` / `direct_state_vector_interface_blocked`.** This is the canonical 18-cell construct-validity qualification under `mn006-direct-state-vector-qualification-v1`; it is not a baseline attempt, a locality measurement, D2, a perfect-state diagnostic, or an intervention.

The exact direct ordered two-entity state-vector response channel passed Q0 across all nine ordered vectors. It did not pass Q1 task-bearing contiguous endpoint recovery: only one of nine authority-owned final-state vectors was exact. The frozen 18/18 rule therefore blocks this interface for the qualified model/runtime.

## Identity and valid execution

- Run ID: `direct-state-vector-qualification-run-0001`.
- Executor commit: `2eb4dda7161982f8e04c591ae0c1bf2fd5cdd9e0` (`MN-006: add direct-state vector qualification executor`).
- Authority-plan SHA-256: `5a487200b0dd72275d37482bc0c3c5cd09feed483419223005519b5034064bbc`.
- Construct-validity gate: integrity-valid [direct-state-vector construct-validity gate](../direct-state-vector-construct-validity-gate.md), SHA-256 `72eeb1e50d9450deff54d5acc45d71d110d8426d3a0ab8da30deb788b6cbee6f`.
- Redesign prerequisite: integrity-valid [measurement-interface redesign](../measurement-interface-redesign.md), SHA-256 `ca328e63d2fbeaa84de4996b74138b649a025ba9b57bf7d4d8d9743600818698`, `single_measurement_interface_candidate_identified` for `direct ordered two-entity final-state vector`.
- Baseline inventory: integrity-valid aggregate SHA-256 `8cdcf1e792f495c9a4ca57ddcda865769db01bad8cfab65c9afb4cd225ad2ec9`.
- Model: `llama-3.2-3b`, `Llama-3.2-3B-Instruct-Q4_K_M.gguf`, SHA-256 `6c1a2b41161032677be168d354123594c0e6e67d2b9227c84f296ad037c728ff`.
- Runtime: llama.cpp `0.2.0-dev`, build `10566`, commit `bb4caa754`; `/v1/chat/completions`, context `16896`, temperature `0.0`, seed `42`, maximum output `16`, threads `12`, batch `2048`, one slot, flash attention enabled, prompt cache disabled, and `--jinja`.

The retained pre-run snapshot records NVIDIA GeForce RTX 3050 Laptop GPU driver `595.95`, `0 MiB` GPU usage, `0%` GPU utilization, no GPU compute process, and no local model process. The runner used only its own server process; its ready-state and before-cleanup snapshots retained only that process. The controlled post-run snapshot again records no compute or local model process, `0 MiB`, and `0%`. There were no retries, no extra requests, no infrastructure failures, and every completion had `finish_reason = stop`.

## Frozen Q0 and Q1 results

Grammar for every request:

```text
root ::= state "," state
state ::= "S0" | "S1" | "S2"
```

The authority-owned grammar has one final LF. The strict parser accepts only an exact ordered `STATE,STATE` vector after outer ASCII-whitespace trim.

| Ordinal | Layer | Expected vector | Raw output | Parsed vector | Correct |
| ---: | --- | --- | --- | --- | --- |
| 1 | Q0 | `S0,S0` | `S0,S0` | `S0,S0` | yes |
| 2 | Q0 | `S0,S1` | `S0,S1` | `S0,S1` | yes |
| 3 | Q0 | `S0,S2` | `S0,S2` | `S0,S2` | yes |
| 4 | Q0 | `S1,S0` | `S1,S0` | `S1,S0` | yes |
| 5 | Q0 | `S1,S1` | `S1,S1` | `S1,S1` | yes |
| 6 | Q0 | `S1,S2` | `S1,S2` | `S1,S2` | yes |
| 7 | Q0 | `S2,S0` | `S2,S0` | `S2,S0` | yes |
| 8 | Q0 | `S2,S1` | `S2,S1` | `S2,S1` | yes |
| 9 | Q0 | `S2,S2` | `S2,S2` | `S2,S2` | yes |
| 10 | Q1 | `S0,S0` | `S1,S2` | `S1,S2` | no |
| 11 | Q1 | `S0,S1` | `S1,S2` | `S1,S2` | no |
| 12 | Q1 | `S0,S2` | `S1,S2` | `S1,S2` | no |
| 13 | Q1 | `S1,S0` | `S2,S1` | `S2,S1` | no |
| 14 | Q1 | `S1,S1` | `S1,S2` | `S1,S2` | no |
| 15 | Q1 | `S1,S2` | `S1,S2` | `S1,S2` | yes |
| 16 | Q1 | `S2,S0` | `S1,S2` | `S1,S2` | no |
| 17 | Q1 | `S2,S1` | `S2,S2` | `S2,S2` | no |
| 18 | Q1 | `S2,S2` | `S2,S1` | `S2,S1` | no |

- Q0 strict-parser-valid: `9/9`; exact-correct: `9/9`.
- Q1 strict-parser-valid: `9/9`; exact-correct: `1/9`.
- Overall strict-parser-valid: `18/18`; malformed: `0/18`; exact-correct: `10/18`.

The Q1 authority was replayed before execution through the unchanged state-transition oracle. It retained the frozen contiguous schedule, query identities, expected vectors, 24-event histories, balanced state-assignment frequency, and no-leakage constraints. No interleaved request was submitted.

## Interpretation and boundary

Q0 supports only exact response-format competence for this direct state-vector observable. Q1 would have been needed, together with Q0, to qualify contiguous task-bearing two-entity final-state recovery across the finite ordered vector space. Its `1/9` result means the predeclared exact requirement was not met.

The licensed conclusion is therefore narrow: **this exact direct-state-vector interface did not satisfy the predeclared construct-validity qualification standard for the qualified model/runtime.** It does not establish a general inability to track state, a distributed-state failure, a locality failure, a reasoning failure, or an intervention effect.

Per the frozen redesign, MN-006 is now `measurement_interface_blocked` for this qualified model/runtime. This contract authorizes no retry, prompt change, parser relaxation, alternate serialization, alternate interface search, locality measurement, D2, perfect-state diagnostic, `attempt-0003`, or intervention. The fixed-label v1 branch remains retired and locality remains unmeasured.

## Evidence and integrity

The canonical retained evidence is:

- [Run metadata](../runs/direct-state-vector-qualification-run-0001/metadata.json)
- [Raw request/response records](../runs/direct-state-vector-qualification-run-0001/results.jsonl)
- [Machine-readable summary](../runs/direct-state-vector-qualification-run-0001/summary.json)
- [Server lifecycle and retained environment snapshots](../runs/direct-state-vector-qualification-run-0001/server-lifecycle.json)
- [Physical artifact integrity record](../runs/direct-state-vector-qualification-run-0001/integrity.json)
- [Server stderr log](../runs/direct-state-vector-qualification-run-0001/raw/llama-server.stderr.txt)

The integrity record verifies binary readback and SHA-256 for metadata, raw records, lifecycle, summary, and both server logs. The canonical validator recomputed the stored summary from all 18 raw records with the frozen parser, evaluator, and classifier, then matched it exactly.
