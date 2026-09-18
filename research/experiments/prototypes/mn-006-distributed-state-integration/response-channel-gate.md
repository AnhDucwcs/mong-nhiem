# MN-006 Response-Channel Gate — prospective grammar constraint

## Status

**`response_channel_revision_ready`**

This gate records a narrow, prospective response-interface revision only. It does not modify the MN-006 semantic workload, canonical inventory, evaluator, thresholds, prior attempt, model identity, or candidate-treatment boundary. It authorizes a later, separately frozen `attempt-0002`; it does not execute one.

## Immutable attempt-0001 evidence

`attempt-0001` remains immutable canonical evidence with this interpretation:

```text
protocol_valid
shared_malformed_output_floor
locality_mechanism_unobserved
```

All 128 independent requests completed without infrastructure failure, but every response was malformed under the predeclared exact-label parser. That is neither a workload failure nor a state-integration failure. It means the paired locality mechanism was unobserved through the unconstrained response channel.

## Static input-path audit

### Public case and request

The public case bytes remain exactly the frozen inventory serialization:

```text
All entities begin in S0.
E## STATE = S#
...
For E## and E##, output VALID if their states are equal; otherwise output INVALID.
Output exactly one label: VALID or INVALID.
```

`attempt-0001` sent one `user` message containing those exact UTF-8 public bytes, decoded without alteration, to `POST /v1/chat/completions` with:

```json
{"messages":[{"role":"user","content":"<exact public prompt>"}],"temperature":0.0,"seed":42,"max_tokens":16,"chat_template_kwargs":{}}
```

The runner first used `/apply-template` with the same one-message structure and `add_generation_prompt: true`, then `/tokenize` as a non-generative prompt-token consistency check. The actual generation endpoint was `/v1/chat/completions`. Prompt caching was disabled server-wide with `--no-cache-prompt`.

The resulting template skeleton is:

```text
<|begin_of_text|><|start_header_id|>system<|end_header_id|>

Cutting Knowledge Date: December 2023
Today Date: <strftime_now("%d %b %Y")><|eot_id|><|start_header_id|>user<|end_header_id|>

<exact public prompt bytes, with trailing whitespace trimmed by the template><|eot_id|><|start_header_id|>assistant<|end_header_id|>

```

### Embedded template and roles

The qualified GGUF contains `tokenizer.chat_template` with SHA-256 `5816fce10444e03c2e9ee1ef8a4a1ea61ae7e69e438613f3b17b69d0426223a4`. It is byte-identical to the local build source template `models/templates/meta-llama-Llama-3.2-3B-Instruct.jinja`.

Under the frozen `--jinja` and empty `chat_template_kwargs`, the request had no caller-supplied system or assistant message and no tools. The embedded Llama template inserts its generic system wrapper (`Cutting Knowledge Date`, a host-current `Today Date`) and renders the public text as the sole user turn, followed by an assistant generation header. The GGUF BOS token is `<|begin_of_text|>` and the end-of-turn token is `<|eot_id|>`.

The retained attempt records public prompt bytes and post-template token counts (`133` for Level 1; `238` for Level 2), but not the `/apply-template` rendered text. The exact historical date string therefore cannot be byte-reconstructed from retained evidence alone. The template source proves the role structure and all workload-bearing content: no system instruction, tool declaration, code request, answer field, or case-specific data was added by the runner. The template adds an `Environment: ipython` line only when tools exist; tools were absent. Therefore the static audit does not support claiming that the template itself instructed a coding task.

## Retained-output audit

The 128 raw outputs have five complete-text variants and two first-line families:

| First line | Count |
| --- | ---: |
| `Here is a Python solution for the problem:` | 96 |
| `Here is a Python solution for the given problem:` | 32 |

All 128 have `finish_reason = length`, hit the frozen 16-token cap, and contain neither `VALID` nor `INVALID` anywhere before truncation. None begins with an answer label. The five exact output variants are short Python-fence/function prefixes; the most frequent variant occurs 83 times.

The malformed condition is shared by every profile, schedule, answer class, and ordinal: Level 1 has 64 malformed outputs, Level 2 has 64; contiguous has 64 and interleaved has 64; `VALID` and `INVALID` canonical-answer cases each have 64. First-line variants are not uniformly distributed across those strata, but no stratum contains a parseable label. This supports a shared response-mode interpretation and does not support a locality-sensitive semantic interpretation.

## Exact-runtime constrained-output audit

The installed runtime used by `attempt-0001` is llama.cpp `0.2.0-dev`, build `10566`, commit `bb4caa754`. Its local executable help advertises `--grammar` as BNF-like constrained generation. More importantly for a narrow revision, the checked local source for this exact revision shows that `POST /v1/chat/completions` parses a request `grammar` field, rejects it only when tools are present, propagates it through the Jinja chat-template path, and installs it as generation grammar. The MN-006 request has no tools.

The selected constant GBNF is:

```text
root ::= "VALID" | "INVALID"
```

This is syntax already exercised by the installed source tree's PEG grammar tests (`root ::= "cat" | "dog"`). Static source inspection establishes compatibility of the request field and grammar form. It does not substitute for future run-time behavior: the first model generation under this grammar remains the separately authorized future measurement.

## Repair alternatives

| Candidate | Comparability | Semantic/leakage risk | Reproducibility | Decision |
| --- | --- | --- | --- | --- |
| A. Stop with no change | Exact attempt-0001 continuation | None | High | Rejected as the only next action: it cannot observe the existing finite answer task through a usable channel. |
| B. Constrained decoding only | Same workload and prompt bytes; only output language changes | Low: constant grammar exposes both predeclared labels but no case truth | High | **Selected.** |
| C. Minimal prompt clarification only | Changes public prompt bytes and therefore all prompt fingerprints | Moderate: wording may alter instruction-following and semantic salience | High after freeze | Rejected for now; unnecessary if B is available. |
| D. Grammar plus clarification | Changes output language and public prompt simultaneously | Higher causal ambiguity than B | High after freeze | Rejected. |
| E. Larger output budget | Retains facts but permits more irrelevant prose and does not force an answer choice | Moderate parser/format ambiguity | High | Rejected; retain 16. |
| F. Relaxed parser | Retroactively changes evaluator boundary and can rescue prose arbitrarily | High | Low | Rejected. |

## Causal interpretation

The selected grammar is a **`response_channel_constraint`**, not a state-tracking intervention. It is global and constant over all requests; it constrains only the output language already declared in every public prompt. The model still selects between `VALID` and `INVALID`; the grammar contains no canonical answer, entity ID, state, event, query, derived fact, or schedule property. The host neither computes state nor selects a label.

The constraint removes free-form formatting failure from the future measurement. Therefore `attempt-0002` would measure **semantic label selection under a constrained finite output channel**, not the combined ability to follow a free-form exact-output instruction and perform state tracking. Its scores must not be pooled with, replace, or be called a replication of `attempt-0001`.

## Prospective attempt-0002 contract

| Component | Classification | Contract |
| --- | --- | --- |
| Attempt relation | frozen | A separate canonical measurement, not a retry or replication of the protocol-valid `attempt-0001`. |
| Identifier | frozen | `attempt-0002`. |
| Response-channel contract version | frozen | `mn006-response-channel-grammar-v1`. |
| Output constraint | frozen | Add exactly one request field whose value is `root ::= "VALID" | "INVALID"` plus one LF. |
| Grammar scope | frozen | One identical constant for all 128 requests; no case-specific grammar or schema. |
| Public prompt bytes | frozen unchanged | Use the existing public files and fingerprints verbatim. No clarification, example, system-message, role, template, or source-event change. |
| Parser | frozen unchanged | Outer ASCII trim and exact case-sensitive `VALID` / `INVALID` only. |
| Output budget | frozen unchanged | `max_tokens = 16`. |
| Workload/inventory | frozen unchanged | Same aggregate fingerprint `8cdcf1e792f495c9a4ca57ddcda865769db01bad8cfab65c9afb4cd225ad2ec9`; same 64 pairs, schedules, profiles, facts, truth table, oracle, and canonical answers. |
| Model/runtime | frozen unchanged except constraint field | Same GGUF identity, llama.cpp build, context, temperature, seed, threads, batch, one slot, flash attention, `--jinja`, no-cache policy, and independent request procedure. Do not add server-wide `--grammar`; send the request-level field. |
| Execution/evaluation | frozen unchanged | Same request order, no-retry/invalidation policy, raw retention, exact paired metrics, thresholds, and environment preflight. |

The only allowed request-payload difference is the exact `grammar` member. The static helper `scripts/mn006/response_channel.py` and its tests enforce that boundary before any future runner is implemented.

## Predeclared response-channel usability

For a future `attempt-0002`, response-channel usability is distinct from model competence:

1. all 128 requests must complete without infrastructure failure;
2. each request record must show the exact frozen grammar value and retain the raw request/response payloads;
3. every response must parse under the unchanged strict parser; and
4. the same grammar must be present for every request, with public prompt fingerprint, inventory fingerprint, and paired request order unchanged.

Grammar-enforced parseability is not accuracy and is not evidence that the model tracked state. The original locality criterion remains unchanged for each profile: contiguous `>=24/32`, `b > c`, and one-sided exact paired `p <= 0.05`. Perfect-state remains ineligible unless that future valid measurement independently meets its already frozen eligibility rule.

## Boundaries and remaining risks

- **Frozen:** all workload semantics, inventory/public bytes, parser, scoring, thresholds, candidate-intervention prohibition, and attempt-0001 evidence.
- **Frozen:** grammar-only response-channel revision and the future attempt relationship above.
- **Deferred:** implementing a distinct `attempt-0002` runner and executing it after normal environment preflight; run-time grammar acceptance is not probed here because that would require model generation.
- **Deferred:** any perfect-state control, candidate-specific treatment, prompt revision, output-budget change, or model/runtime change.
- **Rejected:** parser relaxation, answer extraction, per-case grammar, host answer logic, prompt tuning, and interpreting attempt-0001 as a locality result.

No model/GPU inference, prompt trial, grammar-generation smoke test, or candidate intervention occurred during this gate.
