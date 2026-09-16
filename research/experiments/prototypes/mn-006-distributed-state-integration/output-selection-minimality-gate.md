# MN-006 Output-Selection Minimality Gate

## Status

**`output_selection_minimality_diagnostic_ready`.** This static gate freezes the smallest prospective ladder needed to locate the lowest layer at which the qualified Llama subject stops conditioning its grammar-constrained output on its input. It authorizes only a future separate S0 direct-copy diagnostic executor and execution boundary. S1 is frozen as contingent behind an exact S0 result; this gate does not authorize S1 execution, D2, `attempt-0003`, a baseline rerun, a perfect-state control, locality measurement, or a candidate intervention.

The immutable history is retained without reinterpretation:

| Evidence | Protocol status | Bounded finding | Does not establish |
| --- | --- | --- | --- |
| [`attempt-0001`](reports/mn-006-attempt-0001.md) | `protocol_valid` | Unconstrained channel: 128/128 malformed Python-solution responses. | Locality or state-integration mechanism. |
| [`attempt-0002`](reports/mn-006-attempt-0002.md) | `protocol_valid` | Grammar-constrained channel usable; 128/128 `INVALID`. | Whether output selection, relation computation, or mapping abstraction caused the collapse. |
| [D1](reports/mn-006-label-selection-d1-run-0001.md) | `protocol_valid` | Direct final states plus counterbalanced A/B mapping: 16/16 `A`, zero grammar-order disagreements, `fixed_label_preference_supported`. | Direct copying, direct relation capability, state reconstruction, or locality sensitivity. |

## Causal question and layer order

D1 combined direct equality recognition, mapping-table parsing/application, and output selection. Its fixed-`A` outcome therefore cannot localize the final output-selection layer. The next causal question is:

> Can the model emit both permitted surface labels when the required label is progressively easier to determine?

The ladder remains strictly ordered:

```text
L0  explicit surface-label copying
L1  direct equality / inequality relation recognition
L2  counterbalanced mapping following (D1)
L3  source-event state reconstruction (D2 remains blocked)
L4  locality sensitivity (still unobserved)
```

S0 isolates L0. S1 isolates L1 only after S0 establishes exact L0 copying. Neither changes or replaces D1; both are diagnostic-only and do not pool scores with the baseline attempts.

## Frozen authority plan

The canonical static plan is [plan.json](definition/output-selection-minimality-v1/plan.json), contract `mn006-output-selection-minimality-v1`, SHA-256:

```text
8180ea423a05eeb2930b84cee6102fd94595e13856f1a91e1afe4d599bb8e827
```

It contains eight prospective records: four independently executable S0 records and four conditional S1 records. All prompts and grammars use UTF-8/LF canonical bytes. The shared parser remains the strict existing A/B parser: trim outer ASCII whitespace only; accept exactly `A` or `B`; reject punctuation, explanation text, case changes, substrings, and other labels.

The qualified subject/runtime remains inherited if a future stage is separately executed: `llama-3.2-3b`, the frozen GGUF identity, llama.cpp build `10566` / commit `bb4caa754`, context `16896`, temperature `0.0`, seed `42`, maximum output `16`, one slot, disabled prompt cache, and one independent request at a time. No stochastic sampling, seed sweep, or alternative label vocabulary is authorized.

## S0 — direct-copy control

### Purpose

S0 removes equality, state, mapping-table, reconstruction, and locality operations. It tests only:

```text
read explicit target label
        ↓
emit that same label through the frozen A/B grammar
```

A failure here would make every higher-layer failure uninterpretable. It permits only the behavioral conclusion that, under this constrained interface, output was not conditioned on the explicitly supplied target label. It does not prove faulty logits, a defective runtime, prompt invisibility, or grammar-forced selection.

### Exact prompt and grammar

For target `A`, the exact prompt is:

```text
Target label: A
Output exactly the target label.
Allowed labels: A or B.
```

For target `B`, only the target value changes to `B`. No state, equality, mapping, example, code, explanation, baseline terminology, `VALID`, or `INVALID` is present.

The existing same-language grammar control is retained:

```text
G_AB: root ::= "A" | "B"
G_BA: root ::= "B" | "A"
```

Each request-level grammar has exactly one final LF. It is independent of target, canonical answer, and request identity.

### Four-request matrix and frozen order

Four requests are sufficient because each explicit target receives both grammar orders, creating two matched grammar-order pairs without unnecessary repetition. The order alternates target labels rather than grouping them:

| S0 request | Explicit target / canonical label | Grammar |
| ---: | --- | --- |
| 1 | A | G_AB |
| 2 | B | G_BA |
| 3 | B | G_AB |
| 4 | A | G_BA |

### Exact S0 classifications

A future complete, infrastructure-valid S0 run is classified in this order:

1. `direct_copy_malformed_or_invalid` — any strict-parser failure. A separately recorded infrastructure failure invalidates the run before semantic classification.
2. `grammar_order_asymmetry_observed` — for either fixed target, its G_AB/G_BA pair has different parsed labels. This takes precedence over semantic interpretation once all outputs parse.
3. `direct_copy_supported` — all four outputs parse, each grammar-order pair agrees, and every output equals its explicit target label.
4. `fixed_label_preference_persisted` — all four outputs parse, each grammar-order pair agrees, and every output is one identical surface label.
5. `direct_copy_inconclusive` — any other complete parseable pattern.

S1 is eligible **only** after the exact S0 result `direct_copy_supported`. No executor may override this condition.

## S1 — direct-relation control

### Purpose and exact prompt

S1 is conditional. It removes the counterbalanced mapping-table abstraction that D1 retained while keeping the smallest direct binary relation:

```text
E01 STATE = S1
E02 STATE = S2
Output A if the states are equal.
Output B if the states are different.
Output exactly one label: A or B.
```

Only the two directly supplied state values vary. There are no source histories, interleaving, mapping table, explicit target label, or locality metadata.

S1 uses the single direct rule `equal -> A`, `different -> B`. It intentionally does not counterbalance the rule: mapping counterbalance is the extra abstraction D1 already tested, and S1 is intended to remove rather than recreate it.

### Four-request matrix and order

The smallest balanced set has two equal and two unequal relations, both state values, both unequal orientations, and both output labels:

| S1 request | E01 | E02 | Relation | Canonical label |
| ---: | --- | --- | --- | --- |
| 1 | S1 | S2 | unequal | B |
| 2 | S1 | S1 | equal | A |
| 3 | S2 | S2 | equal | A |
| 4 | S2 | S1 | unequal | B |

S1 uses only `G_AB`. Grammar-order pairing is deliberately omitted because it has already been tested in D1 and is repeated upstream in S0. If S0 confirms direct copying under both grammar orders, adding grammar order to S1 would add a redundant factor rather than improve the relation test.

### Exact S1 classifications

S1 can be classified only after an eligible S0 result:

1. `direct_relation_malformed_or_invalid` — any strict-parser failure. Infrastructure invalidation is reported separately and blocks semantic classification.
2. `direct_relation_supported` — all four outputs parse and equal the direct-rule canonical labels.
3. `fixed_label_preference_recurred` — all four outputs parse and select one identical surface label.
4. `direct_relation_inconclusive` — any other complete parseable pattern.

If S0 passes and S1 passes, the bounded conclusion is that direct copying and direct equality relation handling work under this interface; D1 then becomes specifically informative about the added counterbalanced mapping-abstraction layer. It still does **not** authorize D2 automatically. If S0 passes and S1 does not, direct relation/instruction execution remains unsupported and no state reconstruction or locality work may proceed.

## Logprob capability audit

The exact local llama.cpp source checkout matches build `10566` / commit `bb4caa754`. Static source inspection confirms that `/v1/chat/completions` accepts `logprobs: true` with `top_logprobs`, maps them to `n_probs`, and can emit `choices[0].logprobs.content` for non-stream chat responses. The details are retained in [static-audit.json](definition/output-selection-minimality-v1/static-audit.json).

Logprobs are **deferred** for S0. The default source path records pre-sampling token probabilities, which are not established as grammar-filtered conditional A/B probabilities. The alternative `post_sampling_probs` path is available, but the sampler uses `grammar_first = false` and may apply grammar during fallback/resampling; static inspection does not establish a stable post-grammar distribution interpretation. Adding either request field would also change the frozen S0 request payload without being necessary for the exact behavioral classification.

Temperature stays `0.0`; a seed sweep or stochastic sampling would answer a different distributional question and is rejected. A/B stays fixed; trying C/D, X/Y, numeric, semantic, or Unicode labels to find a successful pair is label fishing and is rejected.

## Boundaries and decision table

| Decision | Status |
| --- | --- |
| Preserve attempts 0001/0002 and D1 as immutable, separate evidence. | frozen |
| Use A/B, the strict parser, the inherited runtime, and no logprobs for S0/S1. | frozen |
| Execute the four-request S0 direct-copy control only through a future separate executor/evidence boundary. | frozen |
| Permit S1 only after S0 exactly classifies `direct_copy_supported`. | frozen |
| Use one direct S1 rule and omit redundant grammar-order pairing from S1. | frozen |
| Treat D1 as an L2 mapping-abstraction diagnostic, not a state/locality result. | frozen |
| Interpret logprobs as a grammar-filtered A/B probability distribution. | deferred |
| Run S1 after partial or mixed S0 success. | rejected |
| Run D2, perfect-state work, locality measurement, or any intervention after this gate. | rejected |
| Increase temperature, sweep seeds, loosen the parser, alter prompts, or test alternate labels. | rejected |

## Next boundary

The next permissible action is a separate static executor task for `output-selection-s0-run-0001`. It must consume exactly the four frozen S0 records, preserve the inherited model/runtime and strict parser, create no S1/D2 request, and be committed before any S0 model behavior is observed. S1 requires a later separate executor/evidence boundary only if S0 meets its exact success classification.
