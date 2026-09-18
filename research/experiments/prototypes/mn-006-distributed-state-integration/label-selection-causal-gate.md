# MN-006 Label-Selection Causal Gate

## Status

**`label_selection_diagnostic_ready`**. This is a static causal-design gate. It authorizes only a future, separately classified label-selection diagnostic beginning with its direct-state stage. It does not authorize `attempt-0003`, a baseline rerun, a perfect-state control, candidate treatment, prompt tuning, label trial, or model inference.

The canonical untreated baseline history remains immutable:

| Measurement | Status | What it establishes | What it does not establish |
| --- | --- | --- | --- |
| [`attempt-0001`](reports/mn-006-attempt-0001.md) | `protocol_valid`; shared malformed-output floor | The unconstrained response channel did not yield parseable finite answers. | A locality mechanism or a state-integration failure. |
| [`attempt-0002`](reports/mn-006-attempt-0002.md) | `protocol_valid`; response channel usable; all-`INVALID` label-selection collapse | The frozen grammar made all 128 outputs parseable, while all 128 selected `INVALID`. | Whether grammar mechanics, response selection, or underlying state/equality computation caused that collapse. |

Neither result is a state-integration failure, and neither result may be rescored, replaced, pooled, or reclassified by this diagnostic.

## Gate question

Why did `attempt-0002` select `INVALID` for every one of its 128 grammar-constrained requests, including all 64 whose frozen canonical answer was `VALID`?

The diagnostic isolates three classes of explanation:

| Hypothesis | Meaning | Diagnostic treatment |
| --- | --- | --- |
| H1 — grammar/runtime asymmetry | Grammar implementation, tokenization, alternative order, or termination mechanics make one branch structurally privileged. | Static source/tokenizer audit plus a direct-state grammar-order control. |
| H2 — label prior / response-selection collapse | The model can legally select both labels but persistently emits one surface label independently of the counterbalanced mapping. | Direct-state, neutral-label mapping counterfactuals. |
| H3 — task-computation failure | The model can apply a supplied equality-to-label mapping but does not reliably derive the relation from contiguous source events. | A contingent contiguous state-tracking stage using the same cases and mappings. |

The gate does not presume any one of H1–H3 is true.

## Frozen baseline invariants

The following remain unchanged historical authority: the MN-006 v1 state machine, source-event grammar, canonical 64-pair inventory and aggregate SHA-256 `8cdcf1e792f495c9a4ca57ddcda865769db01bad8cfab65c9afb4cd225ad2ec9`, paired schedules, state/equality oracle, `VALID`/`INVALID` baseline truth table, strict baseline parser, locality thresholds, model identity, runtime identity, and the raw evidence for attempts 0001 and 0002.

The diagnostic is a separate experiment with a separate output vocabulary and evaluator. It must never be reported as an MN-006 baseline attempt or combined with the baseline locality statistics.

## Static grammar audit — H1

The audit used the exact source checkout corresponding to the retained runtime: llama.cpp `0.2.0-dev`, build `10566`, commit `bb4caa754`. The source and tokenizer observations are retained in the machine-readable [static audit](definition/label-selection-diagnostic-v1/static-audit.json).

For the frozen grammar:

```text
root ::= "VALID" | "INVALID"
```

- The literals begin with distinct characters, `V` and `I`; neither literal is a prefix of the other.
- The GBNF parser expands alternatives into separate grammar stacks. Candidate rejection is applied across all active stacks, so a candidate accepted by either branch remains legal.
- `llama-server` calls the ordinary sampler with `grammar_first = false`: it samples first, tests the selected token against grammar, and only then resamples with grammar masking if that token is illegal. A legal branch is still selected by the model/sampling chain, not by the textual order of the alternatives.
- EOS is permitted only after an accepting grammar stack exists. Both literal alternatives become accepting only after their complete string, so neither has an earlier termination path.
- The static source audit found no obvious acceptance, prefix, or termination asymmetry that would force `INVALID`.

This does **not** prove equal candidate-token mass or equal model logits after grammar filtering. Static source cannot measure probability. The D1 grammar-order control therefore retains an empirical check for an order-sensitive runtime effect without treating alternative order as a semantic manipulation.

## Static tokenizer and label audit

The qualified GGUF was inspected with local `llama-tokenize.exe` only, using `--no-bos --no-parse-special --ids --show-count`. No server, generation, GPU inference, or measured prompt was run.

| Candidate | Answer-start token IDs | Token count | Leading-space form | Assessment |
| --- | --- | ---: | --- | --- |
| `VALID` | `[10250]` | 1 | `[44391]` | Mechanically compact but semantically loaded. |
| `INVALID` | `[47959]` | 1 | `[33369]` | Mechanically compact but semantically loaded. |
| `A` | `[32]` | 1 | `[362]` | Selected. One character, one token, no shared prefix with `B`. |
| `B` | `[33]` | 1 | `[426]` | Selected. One character, one token, no shared prefix with `A`. |
| `0` | `[15]` | 1 | `[220, 15]` | Rejected: binary-classification convention is avoidable semantic baggage. |
| `1` | `[16]` | 1 | `[220, 16]` | Rejected: binary-classification convention is avoidable semantic baggage. |

For `VALID` and `INVALID`, a newline adds the same token `[198]` after each label. For `A` and `B`, a newline likewise adds `[198]`. The selected grammar begins directly with `A` or `B`, so leading-space tokens are not a legal initial grammar path.

`VALID` and `INVALID` are syntactically workable, but their validation, rejection, checker, and compiler associations make a neutral-label counterbalance justified. The gate does not claim these semantics caused the all-`INVALID` result.

## Diagnostic families considered

| Family | Causal value | Decision |
| --- | --- | --- |
| A. Reverse equality-to-`VALID`/`INVALID` mapping | Holds label priors constant while counterbalancing the truth-table mapping, but retains the semantically loaded surface labels. | Rejected as the first diagnostic. It remains a possible later comparison only if the neutral-label ladder leaves a decision-relevant ambiguity. |
| B. Neutral `A`/`B` labels with counterbalanced mappings | Separates relation from label mapping and makes a fixed surface-label preference observable. Static tokenization is symmetric enough for the bounded purpose. | **Selected.** |
| C. Numeric `0`/`1` labels | Compact grammar, but binary-classification conventions are an avoidable alternative label prior. | Rejected. |
| D. Prompt clarification with `VALID`/`INVALID` | Grammar already forces exact output. A wording change would not counterbalance the mapping or distinguish H2 from H3. | Rejected. |
| E. Increase output budget or relax the parser | Would not isolate a label-selection cause and would rewrite frozen response/evaluator boundaries. | Rejected. |

## Frozen diagnostic architecture

The diagnostic has a deliberately small, predeclared causal ladder. Its deterministic planner is [`scripts/mn006/label_selection.py`](scripts/mn006/label_selection.py); its complete non-measured plan has SHA-256 `cfa3aac029aa803cfbd546bf9bba3808739f343758acadca12214d53af4aa465`.

### Source selection

- Source condition: Level 1 `contiguous_control` only.
- Mechanical selection: underlying canonical ordinals `0, 1, 2, 3` from the frozen inventory.
- Structural balance: exactly two `equal_state = true` and two `equal_state = false` cases.
- The same source case, query entities, query final-state pair, and equality relation are reused in every counterfactual condition for that source ordinal.

Interleaving is deliberately absent. The immediate question is label selection on the easier, contiguous condition; reintroducing locality now would confound a mechanism that remains unobservable.

### Output vocabulary, mappings, grammar, and parser

The vocabulary is frozen as `A` / `B`.

```text
M1: equal -> A; unequal -> B
M2: equal -> B; unequal -> A
```

The strict diagnostic parser trims outer ASCII whitespace only and accepts exactly `A` or `B`. It does not repair punctuation, change case, extract substrings, or accept explanations.

The grammar-order control has two same-language grammars:

```text
G_AB: root ::= "A" | "B"
G_BA: root ::= "B" | "A"
```

Each has exactly one final LF. Grammar order is an explicitly matched D1 factor: it is constant within a request, independent of case, relation, mapping, and canonical answer, and contains no state/query/answer information.

### D1 — direct-state mapping sanity diagnostic

D1 exposes the two canonical query states directly. It contains no event history and therefore no state-tracking burden.

For each of the four selected source cases, D1 contains both mappings and both grammar orders:

```text
4 source cases × 2 mappings × 2 grammar orders = 16 independent requests
```

The public structure is fixed:

```text
The final query states are:
E## STATE = S#
E## STATE = S#
For E## and E##, use this mapping:
equal states -> A|B
unequal states -> B|A
Output exactly one label: A or B.
```

D1 is the first and only stage authorized for the next diagnostic execution. It checks whether the model can compute equality from explicit states and follow a counterbalanced mapping, while the `G_AB`/`G_BA` pair checks an otherwise identical grammar-order change.

### D2 — contiguous source-event mapping diagnostic

D2 is predeclared but contingent: it may run only in a separately authorized diagnostic execution **after** D1 classifies `mapping_following_supported`.

D2 uses the same four source ordinals, their canonical contiguous source-event sequence, the same query entity pairs, and both mappings under fixed `G_AB`:

```text
4 source cases × 2 mappings = 8 independent requests
```

This stage reintroduces contiguous state reconstruction but not interleaving. It cannot be used to make a locality claim.

### Predeclared diagnostic ordering

Within each stage, source ordinals are ascending. Mapping order alternates by source-ordinal parity (`M1, M2` for even ordinals and `M2, M1` for odd ordinals). In D1, grammar order alternates within each mapping so every source/mapping pair receives both `G_AB` and `G_BA`. No selection depends on model output.

The complete prospective plan comprises 24 records, but the maximum execution is staged: D1 has 16 requests; D2’s eight requests remain prohibited unless D1 passes its exact mapping-following rule.

## Exact outcome criteria

All stages require completed independent requests, zero infrastructure failures, retained raw payloads/responses, exact plan identity, frozen grammar presence, and strict-parser evaluation. A malformed output is a diagnostic model outcome, not an automatic retry.

| Stage | Outcome | Exact criterion | Interpretation and next boundary |
| --- | --- | --- | --- |
| D1 | `grammar_order_asymmetry_observed` | At least one same-source/same-mapping `G_AB`/`G_BA` pair produces different parsed labels. | H1 remains a live runtime/grammar concern. Do not run D2 or locality work. |
| D1 | `mapping_following_supported` | All 16 outputs parse; every same-source/same-mapping grammar-order pair agrees; all 16 equal their counterbalanced canonical labels. | Direct equality and mapping following are established for this bounded diagnostic. D2 becomes eligible for separate authorization. |
| D1 | `fixed_label_preference_supported` | All 16 outputs parse; all grammar-order pairs agree; all 16 outputs are the same surface label. | Supports H2-style fixed label/response selection under neutral labels. Do not run D2 or locality work. |
| D1 | `direct_mapping_malformed_or_inconclusive` or `mapping_diagnostic_inconclusive` | Any other retained pattern. | The source of collapse remains unresolved; do not infer H2 or H3. |
| D2 | `contiguous_mapping_and_relation_supported` | D1 passed; all 8 outputs parse and equal their counterbalanced canonical labels. | Contiguous state reconstruction, equality, and mapping following are adequate for this small diagnostic. A new separate gate may consider a locality-sensitive measurement. |
| D2 | `fixed_label_preference_recurred` | D1 passed; all eight D2 outputs are the same parsed surface label. | Fixed-label response selection has recurred in source-event context; locality remains unobservable. |
| D2 | `contiguous_mapping_malformed_or_inconclusive` or `contiguous_state_or_relation_diagnostic_inconclusive` | Any other retained pattern. | Source-event state/relation computation is not cleanly established; this is not yet a locality result. |

The criteria are exact rather than statistical because this is a small causal decomposition, not a performance benchmark. D1 success does not itself prove absence of all token/logit asymmetry; it only demonstrates that no observed D1 grammar-order difference prevented exact mapping following under the frozen diagnostic.

## Boundaries

- The older perfect-state policy remains separate. It was designed to decompose a valid locality signal and remains ineligible; D1 is a label/equality diagnostic, not a perfect-state MN-006 baseline control.
- No candidate intervention is selected, implemented, or tested. This gate does not authorize Hierarchical State Representation, External State Management, Event-to-State Normalization, Multi-pass Reconstruction, Symmetric State Partitioning, or any treatment.
- No `attempt-0003` exists or is authorized. The future work is a separately named label-selection diagnostic, not a baseline continuation.
- `attempt-0001` and `attempt-0002` retain their original parser, grammar, inventory, raw evidence, scores, classifications, and limitations.

## Decision register

| Decision | Status |
| --- | --- |
| Treat `attempt-0002` as response-channel-usable but all-`INVALID` label-selection collapse, not a locality result. | frozen |
| Treat the static grammar audit as finding no obvious structural acceptance/prefix/termination asymmetry, while retaining unknown legal-token mass/logit preference. | frozen |
| Use `A`/`B` as the first diagnostic vocabulary. | frozen |
| Use counterbalanced M1/M2 mappings. | frozen |
| Use `G_AB`/`G_BA` only as the matched D1 grammar-order control. | frozen |
| Use Level 1 contiguous ordinals 0–3 only. | frozen |
| Run D1 before D2 and authorize D2 only after D1 exact mapping following. | frozen |
| Make a locality claim, run a perfect-state control, or select a treatment from this gate. | rejected |
| Revisit same-label reversal or numeric labels. | deferred |

## Next action

The next permissible action is a separate static executor task for `mn006-label-selection-diagnostic-v1` D1. That task must preserve this plan and its exact 16-request D1 boundary, create no model evidence, and be committed before any diagnostic model behavior is observed. D2 remains contingent on the future D1 result.
