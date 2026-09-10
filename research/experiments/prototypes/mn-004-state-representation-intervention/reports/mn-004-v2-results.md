# MN-004 v2 — retained execution outcome

## Authority and scope

This report records the execution of the frozen [v2 measurement contract](../gate-b-v2-measurement-contract.md). It does not alter the [Gate A hypothesis](../gate-a-hypothesis.md), Gate B v1, the v1 definition/inventory, or v1's retained 16k feasibility result.

- v2 definition fingerprint: `e39b994576fcc468a1c7a7bd0b5c6db89c6c3c837b35b6994c99f9d830958bb1`
- immutable v1 inventory fingerprint: `7183de0be8813764087e77330c5758970d40dfc9fe8553637faccca027d17897`
- implementation provenance: `861739b7c826d26e9e8ed757ec79ab483952ae17`
- Llama reproduction run: `v2-20260905T134454Z-llama_8k_reproduction-0c1f481c`
- Llama untreated run: `v2-20260905T134708Z-llama_untreated-30e115b0`

The v2 contract permits ledger treatment only after a valid contemporaneous frozen-case Llama reproduction and valid 24-case Llama untreated conditions at both 2k and 8k. It requires an `invalid_comparison` outcome if a condition has truncation or another protocol-invalid row.

## Llama frozen 8k reproduction

The six frozen ECC-006 cases ran untreated at 8,192 requested tokens. All rows were valid and the exact result was `0/6`, matching the frozen compatibility rule exactly.

| level | passes | failure classes | token range (min–max; median) | compatibility |
| --- | ---: | --- | --- | --- |
| 8,192 | 0/6 | 6 `incorrect_state` (all `prior_target_state`) | 8,145–8,187; 8,173.5 | pass |

This is a valid contemporaneous baseline reproduction. The initial terminal watcher returned before the runner flushed its files, but the retained run itself completed normally: its summary records all six rows, `status: valid`, and no truncation or infrastructure error. The run artifacts, not watcher timing, are the authority for this result.

## Llama contemporaneous untreated condition

The 24 authorized natural-language cases were then run at both levels. The observed scores are retained below, but the condition is not valid for a treatment comparison.

| level | untreated passes | failure classes | token range (min–max; median) | condition status |
| --- | ---: | --- | --- | --- |
| 2,048 | 3/24 | 3 `correct`; 18 `incorrect_state`; 2 `malformed_response`; 1 `truncation` | 1,998–2,023; 2,015.5 | invalid |
| 8,192 | 0/24 | 24 `incorrect_state` (all `prior_target_state`) | 8,136–8,192; 8,169.5 | valid in isolation |

The predeclared invalidating row is `mn004-state-010` at 2,048. Its response reached the frozen 16-token output allowance (`finish_reason: length`) and is retained unmodified in the raw record. The contract classifies that as `truncation`; it cannot be selectively removed or rerun to obtain a valid condition.

## Token and position context

No v2 ledger completion was authorized. Retained v1 tokenizer preflight remains the only source for corresponding ledger token diagnostics: at 2k, Llama ledger prompts were 2,718–2,743 tokens (median 2,737; median delta `+722` versus natural language); at 8k they were 11,098–11,189 (median 11,151; median delta `+2,981`). The ledger's larger footprint remains a measured representation consequence, not a hidden variable that was equalized away.

## Mechanical outcome

The required order stopped at the Llama untreated validation gate:

1. frozen 8k reproduction: `compatible` (`0/6`);
2. Llama untreated at 2k/8k: `invalid_comparison` because the 2k condition contains a truncation;
3. Llama ledger: **not run**;
4. Llama primary efficacy and 2k reference no-harm verdicts: **not evaluable**;
5. Qwen untreated eligibility and ledger no-harm: **not run**.

The final frozen-rule outcome is **`invalid_comparison`**. It is neither evidence that the globally indexed ledger improves Llama nor evidence that it is ineffective. It is also not a Qwen result, a baseline-drift result, or a claim about the original v1 16k hard gate.

## Claim boundary and next state

MN-004 v2 did establish that the frozen 8k reproduction remains compatible under the pinned runtime. It did **not** produce a valid paired treatment comparison, an efficacy conclusion, Llama reference no-harm evidence, Qwen control evidence, model-general evidence, token-independent fixed-field causality, an effective-context solution, or an architecture validation.

Gate C v2 is closed at `invalid_comparison`. Any continuation requires a new, separately versioned design and must preserve v1/v2 history and the retained invalid row; it must not alter the frozen v2 contract after this result.
