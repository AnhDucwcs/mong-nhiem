# MN-004 Gate B — frozen measurement contract

## Status and authority

**Gate B complete / Gate C pending. No MN-004 implementation, model invocation, treatment evidence, or result exists.** This document freezes the measurement decisions for the Gate A hypothesis in [the hypothesis note](gate-a-hypothesis.md). Any contradiction that requires changing the globally indexed ledger itself reopens Gate A; Gate B must not silently revise it.

The historical untreated reference is the immutable ECC-006 canonical run `20260828T053342Z-ecc-006-llama-3.2-3b-ab958c23`, definition fingerprint `37f2dc1cc4cdfbf4a667c54f159bbd5203918f85f4d39001fa62ffcba379ac2e`. MN-004 evidence, if later authorized, is separate and never modifies or supersedes that run.

## Primary estimand and claim boundary

The primary estimand is the difference in exact final-state reliability for Llama 3.2 3B when the same ordered State Tracking source-event sequence is rendered as either the frozen ECC-006 natural-language events or the frozen globally indexed state-transition ledger. Source facts, target identity, distractors, event count, global event order, final-state question, accepted-answer semantics, and exact evaluator are invariant.

The ledger may have a different actual prompt-token count from natural language. This difference is retained and reported as a representation-induced mediator/confound; it is not equalized with filler or changed source events. A positive result supports only the bounded observation of higher ledger reliability under the matched semantic workload. It does not identify a fixed-field effect independent of token length, nor select an architecture or generalize across models.

## Workload and sample policy

### Context levels and roles

| Requested level | Role | Historical ECC-006 result |
| ---: | --- | --- |
| 512 | short-context no-harm reference | 2/6 |
| 2,048 | transition no-harm reference | 1/6 |
| 8,192 | primary failure region | 0/6 |
| 16,384 | primary failure region | 0/6 |

The primary failure region is exactly 8,192 and 16,384. Both are included because the frozen baseline is zero at each, and requiring a per-level effect prevents an aggregate gain from being concentrated in only one long-context level. The 2,048 floor is reported but is not part of the primary aggregate; its distinct non-zero baseline makes it a transition reference rather than the clearest long-context failure region.

At every level and in every condition, the workload contains 24 semantic cases: the six immutable ECC-006 cases plus 18 fresh deterministic MN-004 cases. All 24 cases are used in both conditions; no case is dropped, substituted, or added after a result is seen. Thus the primary aggregate contains 48 requests per condition and has a resolution of 1/48 = 2.083 percentage points; each level has a resolution of 1/24 = 4.167 percentage points. Repeated identical deterministic inferences do not increase sample size and are not part of this contract.

### Fresh deterministic cases

Fresh cases are MN-004 evidence, never MN-003 continuation evidence. Their source inventory is frozen before execution as follows:

- case IDs are `mn004-state-001` through `mn004-state-018`;
- target entities are `Unit Ledger 9201` through `Unit Ledger 9218`, respectively;
- `STATE_VOCAB` is the ordered list `RED, BLUE, AMBER, GREEN, SILVER, VIOLET, ORANGE, BLACK, WHITE, TEAL, GOLD, MAROON, NAVY, LIME, GRAY, COPPER, PINK, OLIVE, CYAN, INDIGO, TAN, PURPLE, YELLOW, BROWN`;
- for fresh case number `j` in 1 through 18, its four target updates are `STATE_VOCAB[(4(j-1)+k) mod 24]` for `k = 0, 1, 2, 3`, using zero-based indexing; its answer is the fourth update;
- each case has one target entity, exactly four chronological target updates, four distinct target state values, and no conflicting target event;
- distractors use the frozen ECC-006 deterministic state-history construction with fresh-case ID, side, index, and seed `20260905`; the target placement policy remains nearest feasible midpoint with ratio 0.50 plus or minus 0.05; and
- requested levels, output allowance, overflow rejection, source-event ordering, and question are the ECC-006 contract. Fresh source events are first sized using the natural-language rendering; the ledger condition reuses exactly that source-event sequence.

Target answers may repeat across independent fresh cases because only one case is presented per request. Entity identities are unique across the inventory. The generator must validate every listed invariant before model invocation and retain the resulting source inventory and its hash; it may not generate replacement cases to repair an unfavorable score.

## Conditions and contemporaneous Llama baseline

### Natural-language untreated condition

The historical ECC-006 run remains the immutable untreated baseline. MN-004 additionally requires one contemporaneous Llama natural-language reproduction before any Llama ledger treatment. It uses the exact six frozen cases at all four levels, unchanged ECC-006 source-event construction, question, evaluator, model artifact, and inference configuration.

The reproduction is baseline-compatible only when all rows are valid and its frozen-case pass counts are 1 through 3 at 512, 0 through 2 at 2,048, and exactly 0 at both 8,192 and 16,384. Otherwise it is `baseline_drift`; do not run or interpret the Llama treatment under this contract. Retain the drift evidence under MN-004 without changing any threshold.

If compatible, run the 24-case contemporaneous natural-language condition at every level. Its source event sequences are the matched reference for ledger treatment. It is MN-004 evidence, not a replacement for ECC-006.

### Ledger treatment condition

The treatment is exactly the Gate A globally indexed state-transition ledger. For each matched source-event sequence, it replaces the natural-language event log and changes nothing else. It never adds filler, extra distractors, a target marker, local per-entity grouping, a summary, a current/final state field, the original log, or an answer calculation.

Natural-language and ledger rows must use the same source case ID, source-event hash, event count, target identity, target-event source indexes, target update count, distractor count, distractor order, question, accepted-answer evaluator, and requested level. A source level is named after the natural-language construction; the ledger's actual prompt tokens may differ and are not refilled to match.

## Llama decision rules

### Primary support rule

After a compatible reproduction and valid matched 24-case conditions, the Llama hypothesis is `supported_under_bounded_claim` only if all four rules hold:

1. ledger exact accuracy is at least 12/24 at 8,192 and at least 12/24 at 16,384;
2. ledger minus contemporaneous natural-language pass count is at least +8/24 at each primary level;
3. ledger aggregate accuracy is at least 24/48 and its aggregate pass-count difference is at least +16/48 across the two primary levels; and
4. the 512 and 2,048 no-harm rules below both pass.

These thresholds demand a broad, practically visible effect at each zero-baseline level, rather than a single additional pass. Any valid comparison not meeting every rule is `unsupported_no_effect_or_insufficient_effect`; it is not a reason to revise the thresholds.

### No-harm references

At each of 512 and 2,048, ledger pass count must be no more than two cases below the matched contemporaneous natural-language count: `ledger_passes >= natural_language_passes - 2` out of 24. A larger drop is `llama_reference_regression`, even if the primary long-context rule passes.

### Paired comparison validity

Every primary or reference paired request must be complete, non-truncated, scored by the same exact evaluator, and have matching required source metadata. Any missing request, source mismatch, extra/missing/reordered event, target marking, answer leakage, duplicated original log, condition-specific truncation, evaluator/model/decoding mismatch, or insufficient audit metadata invalidates the corresponding comparison. A violation at either primary level invalidates the whole primary aggregate; a violation at 512 or 2,048 prevents a supported verdict because its no-harm rule cannot be evaluated. No invalid row may be discarded selectively.

## Runtime, token, placement, and evaluator controls

Llama uses the ECC-006 artifact `Llama-3.2-3B-Instruct-Q4_K_M.gguf`, SHA-256 `6c1a2b41161032677be168d354123594c0e6e67d2b9227c84f296ad037c728ff`; llama.cpp version `0.2.0-dev`, build `10566`, commit `bb4caa754`; configured context `16896`; temperature `0`; seed `42`; 16 output tokens; 12 threads; batch size `2048`; one parallel slot; Flash Attention on; prompt cache off; and empty chat-template kwargs. The same model artifact and configuration must be used in both Llama conditions. Hardware/driver, server command, raw version output, and lifecycle diagnostics are retained; a mismatch is an invalid comparison unless both paired conditions are rerun under one predeclared matching configuration.

For each request retain requested level, actual input tokens, content/prompt-overhead tokens, source-event and prompt hashes, event count, target/distractor counts, target source-event indexes, target token-position diagnostics for each rendering, output-token allowance, truncation status, latency, raw output, normalized output, exact score, and failure class. Token and physical-position differences caused solely by the frozen rendering are reported, never hidden or corrected by moving source events. Any condition that exceeds context or truncates invalidates its pair; source events and distractors are not reduced to fit.

The primary evaluator is ECC-006 compatible: accept only the exact state token or `The current state of <exact target entity> is <exact state>` after the existing conservative normalization. There is no fuzzy matching, LLM judge, or accepted-answer expansion. Classes are `correct`, `incorrect_state`, `malformed_response`, `truncation`, `invalid_case`, `runtime_or_infrastructure_error`, and `protocol_violation`. Diagnostics may further classify an incorrect state as prior target state, distractor state, or other/unknown, but never alter exact scoring. The raw evidence machine-check confirms all 21 frozen ECC-006 incorrect-state rows are prior target-update values.

## Qwen regression/control contract

Qwen3-4B is a contemporaneous control on the same MN-004 State Tracking source cases and both renderings; it is never an improvement subject. It uses `Qwen3-4B-Q4_K_M.gguf`, SHA-256 `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5`, the same llama.cpp build/context/decoding controls as above, and chat-template kwargs `{"enable_thinking": false}` for both Qwen conditions.

Run Qwen natural-language untreated on all 96 requests before any Qwen ledger treatment. It is eligible as a no-harm control only if every level is at least 20/24 and the four-level aggregate is at least 88/96. These criteria assess contemporaneous reliability on the same workload; they do not claim an inherited Qwen failure boundary.

If Qwen is eligible, run ledger treatment on the same 96 paired requests. The no-harm rule passes only if ledger is no more than two passes below untreated at every level and no more than four passes below untreated in aggregate. A larger drop is `qwen_regression`. If untreated is not eligible, do not run Qwen ledger treatment, record `control_not_qualified`, and do not search for another workload or claim Qwen no harm. Qwen treatment accuracy is never an improvement metric.

## Execution, invalidation, evidence, and reporting

The execution order is fixed:

1. Offline validate frozen cases, fresh-case inventory, natural-language composer, ledger renderer, source hashes, semantic invariants, token accounting, and evaluator compatibility.
2. Run and validate the six-case Llama contemporaneous reproduction; stop at `baseline_drift` if incompatible.
3. Run and validate the 24-case Llama natural-language condition at all four levels.
4. Run and validate the matched 24-case Llama ledger condition at all four levels.
5. Apply the frozen Llama rules without modification.
6. Run and validate 24-case Qwen natural-language eligibility condition at all four levels.
7. Only if eligible, run and validate the matched Qwen ledger condition and apply the frozen no-harm rule.
8. Generate a report solely from retained MN-004 evidence.

An infrastructure error is `infrastructure_failure`, not a hypothesis verdict. A baseline-compatible but threshold-missing comparison is `unsupported_no_effect_or_insufficient_effect`; a no-harm breach is `regression`; a non-eligible Qwen baseline is `control_not_qualified`; and a semantic/protocol mismatch is `invalid_comparison`. Do not merge these verdicts or replace failed/invalid attempts with only successful configurations.

Every MN-004 request/run retains source case ID and structured source events; target and expected answer; both rendered prompts and hashes; actual token counts; source-event indexes; target/distractor counts and positions; model artifact/hash; runtime/hardware/version metadata; decoding/template settings; raw and normalized output; exact score; failure/protocol class; truncation; latency; and validator output. Reports must show passed/total, exact accuracy, untreated-versus-ledger differences, per-level and primary aggregates, token differences, failure distributions, every threshold verdict, Qwen eligibility/no-harm verdict or control-not-qualified result, and bounded interpretation/unsupported claims.

## Gate B decision

Gate B is complete. Any later execution must implement this contract exactly under separate Gate C authorization; it may not alter the frozen failure region, sample policy, thresholds, token interpretation, Qwen eligibility/no-harm rules, execution ordering, invalidation rules, evidence retention, or reporting requirements after treatment results are visible.
