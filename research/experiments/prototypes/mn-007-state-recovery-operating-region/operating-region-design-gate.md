# MN-007 — Contiguous State-Recovery Operating-Region Design Gate

## Status and authorization boundary

**`mn007_static_operating_region_design_frozen`**

This is a prospective static research-design gate. It freezes the construct, bounded
contiguous difficulty landscape, calibration interpretation, and later-evidence
separation for MN-007. It records no model output, no measured evidence, no
authority plan, no generated calibration corpus, no executor, and no inference
authorization.

MN-006 remains closed and immutable at `measurement_interface_blocked`. Its Q0
`9/9` and Q1 `1/9` results are motivation and interface evidence only; this gate
does not retry, rescore, relax, or otherwise amend them. In particular, it does
not establish a locality result or authorize a locality comparison.

The sole next step licensed by this gate is the separate static workload-definition
and materialization-contract work stated in [Next authorized action](#next-authorized-action).
Model execution requires a later authority step.

## 1. Primary construct and boundary

MN-007 calibrates **contiguous two-entity latest-state recovery** for the qualified
small-model/runtime. A case succeeds exactly when the model returns the final state
of each of the two queried entities, in the query's declared order, after replaying
the contiguous ordered assignment schedule.

The construct includes:

- retaining direct assignments for two named entities;
- respecting within-entity update order and taking each entity's last assignment;
- binding the two recovered values to the declared query order; and
- emitting the exact ordered state vector.

It excludes locality, interleaving effects, generic reasoning, equality tests,
arbitrary-label selection, instruction-following beyond the fixed response grammar,
intervention efficacy, state summarization, external memory, and general small-model
capability. A contiguous calibration score is not a locality effect, because it has
no matched interleaved condition.

The queried endpoint remains exactly two entities. Increasing answer arity would
add output-binding pressure and change the construct before the two-entity control
condition is calibrated.

## 2. Prospective response-observable decision

MN-007 adopts the direct semantic observable as its own prospective decision:

```text
ordered queried entities
    -> ordered final-state vector
    -> exact deterministic scoring
```

The model-visible answer form is the bare two-token vector, for example `S1,S2`.
The first token is the final state of the first entity named in the query; the
second token is the final state of the second. The grammar is:

```text
root ::= state "," state
state ::= "S0" | "S1" | "S2"
```

The parser trims leading/trailing ASCII whitespace only and otherwise accepts one
comma and exactly two vocabulary tokens. Exact vector equality is the only score;
there is no partial credit, synonym, keyed form, reversed vector, or LLM judge.

This is not an automatic inheritance of an MN-006 contract. MN-006 Q0 did,
however, supply finite direct evidence relevant to this prospective choice: the
qualified Llama 3.2 3B / llama.cpp subject produced all nine ordered state vectors
exactly (`9/9`) when both semantic values were supplied positionally. That covers
the three-token vocabulary, two output slots, slot order, comma serialization, and
strict parser. It is therefore sufficient evidence that response serialization is
not the primary variable MN-007 needs to recalibrate. It does **not** qualify
task-bearing recovery, which MN-007 measures anew under its own workload.

MN-007 must not restore MN-006's retired equality-to-`VALID`/`INVALID` or
equality-to-arbitrary-label adapter. Making the answer less state-like would add a
conditioned-output variable without improving the measurement of latest-state
recovery.

## 3. Frozen contiguous difficulty landscape

The landscape is exactly the following six cells, fixed before any inference:

| Entity-load profile | Active entities `E` | Updates/entity `U` | Query-block placement `P` | Total events `E × U` | Non-query entities | Latest-update distances `(first, second)` |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| `e3_terminal` | 3 | 3 | terminal pair | 9 | 1 | `(3, 0)` |
| `e3_leading` | 3 | 3 | leading pair | 9 | 1 | `(6, 3)` |
| `e5_terminal` | 5 | 3 | terminal pair | 15 | 3 | `(3, 0)` |
| `e5_leading` | 5 | 3 | leading pair | 15 | 3 | `(12, 9)` |
| `e7_terminal` | 7 | 3 | terminal pair | 21 | 5 | `(3, 0)` |
| `e7_leading` | 7 | 3 | leading pair | 21 | 5 | `(18, 15)` |

`E` and `P` are the only selected workload dimensions. `U=3` is fixed. There are
exactly 18 prospective calibration cases per cell, for 108 cases in the whole
landscape. No cell, level, case count, response interface, or threshold may be
added, removed, resampled, or retuned after observing any calibration output.

### Selected dimension: entity-load profile `E ∈ {3, 5, 7}`

`E` is the number of active canonical entity IDs, `E01` through the required final
identifier. Every active entity receives exactly three updates. Consequently total
event count is `3E`, and the number of non-query distractor entities is `E - 2`.

Increasing `E` increases the number of independently maintained trajectories,
non-query assignments, and rendered context. It is deliberately an **entity-load
profile**, not a claim that MN-007 separately estimates an entity-count effect, a
token-count effect, or a distractor effect: those quantities co-vary by design and
are recorded as derived metrics. Separating them would require additional workload
families and would expand this calibration beyond the smallest useful frontier.

The lower bound `E=3` retains one genuine non-query trajectory; `E=2` is excluded
because it has no distractor entity and cannot later support an interruption-based
locality design. `E=7` is a prospectively selected upper calibration profile, not a
new MN-006 Level 2 case and not a replay of its eight-entity Q1 authority.

### Selected dimension: query-block placement `P ∈ {terminal, leading}`

The global schedule is contiguous entity blocks. Let the two named query entities
occupy block positions `b1 < b2`, and let an update distance be the number of event
lines after that entity's last update and before the query.

- `terminal`: query blocks occupy `b1=E-1`, `b2=E`; their distances are always
  `(3, 0)`.
- `leading`: query blocks occupy `b1=1`, `b2=2`; their distances are
  `(3(E-1), 3(E-2))`.

This dimension changes retention interval to the final query while preserving the
same entity count, update depth, vocabulary, direct-assignment semantics, and
contiguous schedule. It may still be confounded with a query entity's source
position and the direction in which a model reads the prompt. The case construction
below balances query output order relative to source-block order, but MN-007 does
not claim a causal recency or positional effect from this calibration; placement
only maps the control-condition frontier needed for later locality design.

### Deliberately fixed or derived quantities

| Quantity | Status | Reason and consequence |
| --- | --- | --- |
| Queried endpoint | Fixed at 2 | Preserves the direct ordered-vector construct and avoids changing output arity. |
| Updates/entity | Fixed at 3 | Preserves a nontrivial ordered history while avoiding a second update-depth frontier. |
| State vocabulary and initial state | Fixed: `S0`, `S1`, `S2`; all start `S0` | Keeps semantic transition complexity and the response vocabulary constant. |
| Event semantics | Fixed direct assignments; no consecutive no-op | Keeps replay deterministic and avoids operator/reasoning depth. |
| Schedule kind | Fixed contiguous blocks only | Calibration is a control-capability measurement, not locality evidence. |
| Total event count | Derived: `3E` | Co-varies with entity-load profile; it is recorded, not separately manipulated. |
| Non-query entities/events | Derived: `E-2` entities and `3(E-2)` events | Represents the distractor burden implicit in `E`, not an independent axis. |
| Latest-update distances | Derived from `E` and `P` | Prevents an additional, partially redundant distance-tuning axis. |
| Source wording, output grammar, decoding/runtime settings | Fixed in the later static contract | Prevents prompt, serialization, or runtime drift from masquerading as difficulty. |
| Natural-language noise, derived rules, external knowledge, tools, retrieval, and interventions | Excluded | They would make a recovery score harder to interpret. |

The known MN-006 eight-entity/24-event contiguous Q1 workload is neither a level
nor a calibration case in this landscape. Its immutable `1/9` result remains a
workload-bound reason to conduct prospective calibration; it is not an adaptive
instruction to search immediately adjacent difficulty values until a preferred
score appears.

## 4. Canonical semantic-case construction

The later static materialization contract must implement the following construction
exactly and reject rather than repair a nonconforming case.

1. For each cell and ordinal `0..17`, derive deterministic independent sub-seeds
   for entity permutation, query-output orientation, expected vector, queried
   histories, and non-query histories from that cell's future frozen root seed.
2. Construct the active ID inventory `E01..E0E` and a deterministic permutation.
   Choose the entities occupying the cell's required block positions as the queried
   pair; their identity selection is independent of their final-state vector.
3. Assign expected ordered final-state vectors in the fixed lexicographic sequence
   `S0,S0`, `S0,S1`, `S0,S2`, `S1,S0`, `S1,S1`, `S1,S2`, `S2,S0`, `S2,S1`,
   `S2,S2` for ordinals `0..8`, and repeat that same sequence for ordinals `9..17`.
   Thus each cell covers every ordered vector exactly twice.
4. For ordinals `0..8`, name queried entities in source-block order. For ordinals
   `9..17`, name the same two entities in reverse source-block order. Bind the
   expected vector to that declared query order, not to source order. This gives
   exactly nine forward and nine reverse query-order cases in every cell.
5. Construct each entity's exactly three direct assignments backwards from its
   assigned final state. Every assignment is in `S0,S1,S2`; the first differs from
   the common initial `S0`; each later value differs from the immediately prior
   value. Nonconsecutive reuse is permitted.
6. Choose non-query histories deterministically so that every complete case has
   exactly `E` rendered assignments to each of `S0`, `S1`, and `S2`. The assignment
   frequency vector is therefore identical within a cell and cannot identify a
   queried final-state vector. If no valid construction exists under this rule, the
   static materializer must fail rather than resample or loosen the balance rule.
7. Serialize the entity permutation as contiguous three-event blocks, preserving
   each entity's internal update order. Render only the common initial-state line,
   event lines of the form `ENTITY_ID STATE = STATE_TOKEN`, then:

   ```text
   For <QUERY_ENTITY_1> and <QUERY_ENTITY_2>, output their final states in this order.
   Output exactly two state tokens from S0, S1, S2 separated by one comma.
   ```

8. A deterministic authority-only oracle replays all event lines, derives the two
   final states in declared query order, and stores the canonical vector. The public
   prompt contains no final-state, answer, derived, seed, block-placement, or
   authority field. Exact scoring compares the strict parsed vector with this
   authority-owned vector.

The later contract must retain distinct public, evaluator, and authority views;
use UTF-8, LF-normalized canonical serializations; validate event conservation,
history validity, schedule placement, vector coverage, orientation balance,
state-frequency balance, query/final-value independence, prompt non-leakage, and
deterministic replay. These are static construction requirements, not permission to
materialize an authority corpus or run a model during this task.

## 5. Predeclared calibration and operating-region rule

The future calibration has one request per frozen case, 18 per cell, under one
separately authorized clean-environment attempt. Fresh independent requests are
required; there are no conversation carryovers, retries, prompt changes, or
response-dependent substitutions.

### Protocol validity

The entire calibration is `protocol_valid` only if the later frozen authority and
static validators pass, all 108 intended requests are made exactly once under the
frozen qualified subject/runtime configuration, raw records and integrity artifacts
are complete, and no infrastructure event occurs. Timeout, HTTP/server error,
unexpected process exit, OOM, environmental contamination, missing record, prompt
or authority-integrity mismatch, or interruption makes the calibration
`measurement/design blocked`; partial cell results are retained but cannot be used
to select an operating region.

For a protocol-valid cell `i`, let:

- `P_i` be strict-parser-valid responses out of 18; and
- `C_i` be exact ordered-vector-correct responses out of 18.

Every exact response is parser-valid. A malformed or wrong response is a measured
zero, not an infrastructure failure and not a retry trigger.

### Cell classification

The following exhaustive rule applies independently to every protocol-valid cell:

| Classification | Exact deterministic condition | Interpretation |
| --- | --- | --- |
| `ceiling` | `P_i = 18` and `C_i >= 17` | At least 94.4% exact recovery leaves too little predeclared failure headroom for this calibration to seed a sensitive later locality comparison. |
| `usable` | `P_i = 18` and `15 <= C_i <= 16` | 83.3%–88.9% exact recovery is fully serialization-valid, above the contiguous qualification floor, and not at the defined ceiling. |
| `floor` | every other protocol-valid result | This includes `C_i <= 14` or any `P_i < 18`; it is not reliable enough as a future locality control. |

These boundaries are intentional MN-007 operating-region criteria, not a relaxation
of MN-006's interface qualification. MN-006 required exact `18/18` because it was
a binary construct-validity gate for a frozen locality workload. MN-007 instead
needs a reliable but non-ceiling control condition with known room for a later
matched schedule effect. Eighteen cases provide two exposures of every ordered
vector and exact integer boundaries: `14/18` is floor, `15–16/18` is usable, and
`17–18/18` is ceiling. Equality at every boundary follows the table; no confidence
interval, discretionary judgment, or post-hoc aggregation is permitted.

### Deterministic selection when multiple cells are usable

Let `U` be all cells classified `usable`. If `U` is nonempty, select exactly one
seed cell by sorting `U` in descending lexicographic order of:

```text
(C_i, E, placement_rank)
```

where `placement_rank(leading)=1` and `placement_rank(terminal)=0`.

Thus the selected cell first has the higher exact reliability within the usable
band, then the larger predeclared entity/distractor load, then the longer-retention
placement. This never selects a defined ceiling or floor cell. It makes selection
mechanical without asserting that these structural burdens are empirically linear
or that MN-007 has measured their separate causal effects.

## 6. Calibration versus later hold-out locality evidence

All 108 MN-007 calibration prompts, case IDs, root/sub-seeds, entity permutations,
histories, canonical vectors, public serializations, and raw responses are
**calibration-only**. They may determine whether a parameter cell is eligible, but
they are not locality evidence and must not become the sole cases in a later
contiguous-versus-interleaved claim.

If a seed cell is selected, a later separately authorized locality design may reuse
only:

- the semantic workload rules and selected parameter values `E`, `U=3`, and `P`;
- the direct ordered state-vector observable and exact parser/scorer;
- the qualified Llama 3.2 3B / llama.cpp subject and frozen runtime identity,
  unless a separate prospective decision changes the subject; and
- the general deterministic validation and evidence-retention discipline.

It must use a new frozen hold-out namespace and independently materialized semantic
cases with new case IDs, root/sub-seeds, histories, permutations, and prompt bytes.
It must create fresh matched contiguous/interleaved pairs only after its own static
causal authority establishes what schedule factor changes and what all other
semantics hold constant. No calibration case may be relabeled, rescheduled, or
reused as a hold-out pair.

## 7. Research-level success and stop outcomes

After a separately authorized future calibration, exactly one outcome is assigned:

| Outcome | Deterministic condition | Consequence |
| --- | --- | --- |
| `usable operating region identified` | Calibration is `protocol_valid` and `U` is nonempty; select the unique seed cell by the rule above. | It authorizes only consideration of a separate static hold-out locality design. It does not authorize locality measurement, an intervention, or architecture selection. |
| `no usable operating region in bounded landscape` | Calibration is `protocol_valid` and `U` is empty, whether all cells are floor, ceiling, or a mix. | Retain the bounded negative calibration result. It does not authorize adding levels, adapting prompts, changing thresholds, or searching another MN-007 landscape. |
| `measurement/design blocked` | Static materialization/validation cannot satisfy this frozen design, or a later authorized calibration is not `protocol_valid`. | Retain diagnostics and resolve only the stated design/infrastructure defect through a separately authorized static decision; do not interpret partial scores or adapt difficulty. |

None of these outcomes selects an architecture, establishes locality, or tests a
state-management intervention. The subject remains the qualified Llama 3.2 3B /
llama.cpp runtime unless a later prospective decision explicitly changes it; no
claim generalizes this result to all small models.

## 8. Next authorized action

The exact next authorized action is a **static MN-007 deterministic
workload-definition and materialization-contract gate**. It may freeze the root
seed/namespace, case schema, canonical serializations, public/evaluator/authority
separation, static validators, no-leakage audit, and the boundary a future executor
must obey. It must not create an executor, a run plan, a model authority, a
calibration corpus, a model request, or measured evidence.

Only after that separate static gate may another authority decide whether to
implement a bounded executor and, later still, whether to authorize clean-environment
calibration. MN-006 remains closed throughout.
