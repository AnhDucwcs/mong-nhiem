# MN-006 constrained baseline attempt-0002

## Status

**`protocol_valid` / `no_usable_locality_failure_signal_under_v1_baseline`** for both frozen profiles. This is the separately frozen response-channel-contract measurement. It uses the same MN-006 workload, inventory, paired schedules, parser, evaluator, and locality criterion as `attempt-0001`, but adds the one global constrained-output grammar authorized by the [Response-Channel Gate](../response-channel-gate.md). It is not a replication, retry, or pooled continuation of `attempt-0001`.

## Workload and execution identity

- Executor commit: `f5d2dcfb1729f7c9f017c88b3ec737715770c65b` (`MN-006: add constrained baseline attempt runner`).
- Response-channel contract: `mn006-response-channel-grammar-v1`.
- Request-level grammar, identical in every request: `root ::= "VALID" | "INVALID"` plus one LF. No server-global grammar, prompt revision, system prompt, template override, case-specific grammar, or answer-specific grammar was used.
- Inventory: `mn006-v1-baseline-inventory-1`, aggregate SHA-256 `8cdcf1e792f495c9a4ca57ddcda865769db01bad8cfab65c9afb4cd225ad2ec9`.
- Coverage: 32 matched pairs / 64 prompts in Level 1 and 32 matched pairs / 64 prompts in Level 2; 128 independent requests total.
- Ordering: Level 1 then Level 2; ordinal ascending; even ordinals contiguous then interleaved and odd ordinals interleaved then contiguous.
- Model: `llama-3.2-3b`, `Llama-3.2-3B-Instruct-Q4_K_M.gguf`, SHA-256 `6c1a2b41161032677be168d354123594c0e6e67d2b9227c84f296ad037c728ff`.
- Runtime: llama.cpp `0.2.0-dev`, build `10566`, commit `bb4caa754`; context `16896`, temperature `0.0`, seed `42`, maximum output `16`, threads `12`, batch `2048`, one slot, flash attention enabled, prompt cache disabled, and `--jinja`.
- Environment: NVIDIA GeForce RTX 3050 Laptop GPU, driver `595.95`; pre-run GPU use was `0 MiB` and GPU utilization `0%`, with no GPU compute app or pre-existing local model server. The measurement server was terminated by the runner after request 128.

The inherited Jinja template can insert a runtime-dependent `Today Date` value. The valid matched invariant is therefore unchanged public prompt bytes, unchanged request messages and workload facts, and the intentional constant grammar field; it is not byte identity of the fully rendered historical template.

## Execution and response-channel validity

All 128 planned requests completed, with no retries and no infrastructure failures. The server health check passed before request 1; every observed prompt-token count matched the pre-request template/tokenization check; each retained request used the expected inventory prompt fingerprint and differed from its retained `attempt-0001` counterpart only by the exact grammar member.

All 128 retained payloads contain the frozen grammar and every output parses under the unchanged strict parser. All completions have `finish_reason = stop`.

This establishes **response-channel usability**, not state-tracking competence. The grammar made the finite response channel usable, but it did not supply a correct label, state, entity, query, schedule, or canonical answer.

## Frozen paired evaluation

| Profile | Contiguous | Interleaved | Delta | C✓→I✓ | C✓→I✗ (`b`) | C✗→I✓ (`c`) | C✗→I✗ | Exact one-sided p | Classification |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| Level 1 | `16/32` (50.0%), 0 malformed | `16/32` (50.0%), 0 malformed | `0.0` | 16 | 0 | 0 | 16 | not applicable (`b <= c`) | `no_usable_locality_failure_signal_under_v1_baseline` |
| Level 2 | `16/32` (50.0%), 0 malformed | `16/32` (50.0%), 0 malformed | `0.0` | 16 | 0 | 0 | 16 | not applicable (`b <= c`) | `no_usable_locality_failure_signal_under_v1_baseline` |

For both profiles, the paired locality effect `(b - c) / 32` is `0.0`. The frozen criterion is not met: contiguous correctness is below `24/32`, there is no directional discordance (`b = c = 0`), and the one-sided exact paired test is not applicable.

## Descriptive response behavior and scope

Unlike `attempt-0001`, which had 128 malformed free-form responses, `attempt-0002` had 128 parseable constrained responses. The retained response label was `INVALID` in every request: all 64 canonical `INVALID` cases were correct and all 64 canonical `VALID` cases were wrong. This is a descriptive label-selection collapse under the constrained channel, not a causal comparison of response interfaces and not evidence that the grammar itself caused a semantic effect.

Within each profile, matched contiguous and interleaved members received the same result for every pair. Consequently this valid attempt does not expose a regular round-robin locality-sensitive state-integration failure region. MN-006 v1 still makes no claim about arbitrary interleaving.

## Consequences under frozen rules

- Perfect-state diagnostic: **`perfect_state_diagnostic_not_eligible`**. Neither profile has a candidate locality-failure signal, even though malformed-output counts are `0/64` per profile.
- No intervention is selected or tested. No Hierarchical, External State Management, Event-to-State Normalization, Multi-pass Reconstruction, Symmetric State Partitioning, or other treatment result exists.
- The next research decision is not prompt or grammar tuning inside this attempt. A separate causal-design decision is required before any further MN-006 measurement can address the observed all-`INVALID` label-selection behavior while preserving a prospectively frozen, comparable workload contract.

## Evidence and integrity

The canonical retained evidence is:

- [Attempt metadata](../runs/attempt-0002/metadata.json)
- [Raw request/response records](../runs/attempt-0002/results.jsonl)
- [Machine-readable summary](../runs/attempt-0002/summary.json)
- [Server lifecycle and pre/post environment snapshots](../runs/attempt-0002/server-lifecycle.json)
- [Physical artifact integrity record](../runs/attempt-0002/integrity.json)
- [Server stderr log](../runs/attempt-0002/raw/llama-server.stderr.txt)

The integrity record verifies binary readback and SHA-256 for metadata, raw records, lifecycle, summary, and both server logs. The stored summary was recomputed from raw records using the frozen evaluator and matched exactly.
