# MN-006 baseline attempt-0001

## Status

**`protocol_valid` / `no_usable_locality_failure_signal_under_v1_baseline`** for both frozen profiles. This is the canonical first untreated Llama baseline. It is valid execution evidence, but it does not expose a usable contiguous-versus-interleaved state-locality region because every response was malformed under the predeclared exact-label parser.

## Workload and execution identity

- Inventory: `mn006-v1-baseline-inventory-1`, aggregate SHA-256 `8cdcf1e792f495c9a4ca57ddcda865769db01bad8cfab65c9afb4cd225ad2ec9`.
- Coverage: 32 paired cases / 64 prompts in Level 1 and 32 paired cases / 64 prompts in Level 2; 128 independent requests total.
- Schedule order: Level 1 then Level 2; ordinal ascending; even ordinals contiguous then interleaved and odd ordinals interleaved then contiguous.
- Model: `llama-3.2-3b`, `Llama-3.2-3B-Instruct-Q4_K_M.gguf`, SHA-256 `6c1a2b41161032677be168d354123594c0e6e67d2b9227c84f296ad037c728ff`.
- Runtime: llama.cpp `0.2.0-dev`, build `10566`, commit `bb4caa754`; context `16896`, temperature `0.0`, seed `42`, maximum output `16`, threads `12`, batch `2048`, one slot, flash attention on, prompt cache disabled, and `--jinja`.
- Environment: NVIDIA GeForce RTX 3050 Laptop GPU, driver `595.95`; pre-run GPU use was `0 MiB` and GPU utilization `0%`, with no compute app or pre-existing local model server. The created server terminated normally after the request sequence.

MN-006 v1 still measures regular repeated-permutation round-robin interleaving only; it does not establish behavior on arbitrary interleaving.

## Execution validity

All 128 planned requests completed. The server health check passed before request 1, each server-reported prompt-token count exactly matched the pre-request template/tokenization check, no response was retried, and no infrastructure failure, prompt mutation, inventory change, or case substitution occurred.

All 128 completions ended at the frozen 16-token cap and were malformed by the frozen parser. The raw outputs begin with either `Here is a Python solution for the given problem:` (32 responses) or `Here is a Python solution for the problem:` (96 responses), rather than containing exactly `VALID` or `INVALID` after outer ASCII whitespace trimming. This is a recorded model-output behavior, not an infrastructure failure and not grounds to change the frozen cap, prompt, parser, or inventory.

## Frozen paired evaluation

| Profile | Contiguous | Interleaved | Delta | C✓→I✓ | C✓→I✗ (`b`) | C✗→I✓ (`c`) | C✗→I✗ | Exact one-sided p | Classification |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| Level 1 | `0/32` (0.0%), 32 malformed | `0/32` (0.0%), 32 malformed | `0.0` | 0 | 0 | 0 | 32 | not applicable (`b <= c`) | `no_usable_locality_failure_signal_under_v1_baseline` |
| Level 2 | `0/32` (0.0%), 32 malformed | `0/32` (0.0%), 32 malformed | `0.0` | 0 | 0 | 0 | 32 | not applicable (`b <= c`) | `no_usable_locality_failure_signal_under_v1_baseline` |

For both profiles, the paired locality effect `(b - c) / 32` is `0.0`. Neither profile reaches the frozen contiguous-capability floor of `24/32`; neither has directional discordance `b > c`; and the directional exact paired test is therefore not applicable. The valid outcome is a shared malformed-output floor, not evidence that regular interleaving caused a performance degradation.

## Consequences under the frozen gate

- The perfect-state diagnostic is **not eligible**: no profile has a candidate locality-failure signal, and malformed outputs are `64/64` per profile rather than at most `2/64`.
- No candidate intervention is selected or tested.
- No Hierarchical, External State, Event-to-State Normalization, Multi-pass, Symmetric Partitioning, or other treatment result exists.
- The next research decision is not to tune MN-006 after this result. Any follow-up requires a separate design decision that explains how an output-channel failure can be resolved while preserving a predeclared, comparable workload and measurement contract.

## Evidence and integrity

The canonical retained evidence is:

- [Attempt metadata](../runs/attempt-0001/metadata.json)
- [Raw request/response records](../runs/attempt-0001/results.jsonl)
- [Machine-readable summary](../runs/attempt-0001/summary.json)
- [Server lifecycle and pre/post environment snapshots](../runs/attempt-0001/server-lifecycle.json)
- [Physical artifact integrity record](../runs/attempt-0001/integrity.json)
- [Server stderr log](../runs/attempt-0001/raw/llama-server.stderr.txt)

The integrity record verifies physical binary readback and SHA-256 for metadata, raw records, lifecycle, summary, and server logs. The summary was recomputed from the raw response records using the frozen evaluator and matched the stored summary exactly.
