# Direct-State Vector Construct-Validity Gate

## Status

`direct_state_vector_qualification_ready`

This is a static authority gate. It freezes the response interface and the two-layer qualification contract; it does not authorize an executor, a qualification run, a locality run, D2, `attempt-0003`, a perfect-state control, or an intervention.

## Scientific construct and causal cut

MN-006 retains its original untreated construct: with the same semantic entity histories, queried entities, transition model, model/runtime, and exact scoring, compare a contiguous update schedule with a matched distributed/interleaved schedule. The target is distributed-state locality / latest-state integration.

The retired v1 equality-to-label adapter required equality reasoning and a non-neutral conditioned label selection. Its protocol-valid fixed-label evidence is therefore not construct-valid access to locality. This gate removes that adapter entirely. The observable is the direct ordered two-entity final-state vector. It neither asks for equality, `VALID`/`INVALID`, `A`/`B`, nor a conditional mapping.

## Frozen interface

The semantic state vocabulary is the unchanged workload vocabulary:

```text
S0, S1, S2
```

There are exactly `3 × 3 = 9` ordered two-state vectors. The query identities remain the two workload query entities for each authority-owned Q1 source; output position one always represents the first named query entity and position two the second.

The selected serialization is the **bare ordered vector**:

```text
S1,S2
```

The prompt explicitly declares the query order. This is lower burden than a keyed representation such as `E01=S1\nE02=S2`: keyed output adds entity literals, equals signs, line breaks, and another ordering/serialization failure surface without adding state-recovery evidence. A reversed bare vector remains an exact error; its ambiguity is diagnostic of wrong ordered binding or state recovery, not a tolerated alternate form.

The sole grammar is:

```text
root ::= state "," state
state ::= "S0" | "S1" | "S2"
```

The authority string has one final LF and no optional whitespace. It has exactly one response form for each ordered vector. The parser trims outer ASCII whitespace only, then accepts exactly two vocabulary members separated by one comma. It rejects internal spaces, keyed forms, reordered/extra entities, aliases, partial vectors, extra tokens, malformed separators, and values outside `S0`/`S1`/`S2`.

Scoring is exact vector equality. Per-position diagnostics may be retained later, but neither layer gives partial credit.

## Frozen authority

- Interface contract: `mn006-direct-state-vector-interface-v1`
- Qualification contract: `mn006-direct-state-vector-qualification-v1`
- Prospective run identity: `direct-state-vector-qualification-run-0001`
- Parser: `mn006-direct-state-vector-parser-v1`
- Evaluator: `mn006-direct-state-vector-evaluator-v1`
- Runtime reference: `mn006-baseline-runtime-v1`
- Semantic inventory fingerprint: `8cdcf1e792f495c9a4ca57ddcda865769db01bad8cfab65c9afb4cd225ad2ec9`
- Authority plan: [`plan.json`](definition/direct-state-vector-qualification-v1/plan.json), SHA-256 `5a487200b0dd72275d37482bc0c3c5cd09feed483419223005519b5034064bbc`
- Prerequisite redesign: [`measurement-interface-redesign.md`](measurement-interface-redesign.md), SHA-256 `ca328e63d2fbeaa84de4996b74138b649a025ba9b57bf7d4d8d9743600818698`

No run directory or executor exists at this gate boundary.

## Exact 18-cell qualification inventory

The full deterministic order is Q0 first, then Q1. Within each layer it is canonical lexicographic state order: `S0,S0`, `S0,S1`, `S0,S2`, `S1,S0`, `S1,S1`, `S1,S2`, `S2,S0`, `S2,S1`, `S2,S2`. This order is mechanical and is not chosen from prospective model behavior.

### Q0 — exact vector-output qualification

Q0 contains records 1–9, one for every ordered vector. Each prompt supplies two semantic values in positional form:

```text
First query state: S1
Second query state: S2
Output exactly two state tokens in this order, separated by one comma.
```

It deliberately never supplies `S1,S2` as a serialized target string. Q0 qualifies the exact state-token vocabulary, two positions, output order, comma serialization, grammar, and parser. It does not establish task-bearing recovery, history replay, locality, or state integration.

| Record | Expected ordered vector |
| --- | --- |
| q0-01-S0-S0 | S0,S0 |
| q0-02-S0-S1 | S0,S1 |
| q0-03-S0-S2 | S0,S2 |
| q0-04-S1-S0 | S1,S0 |
| q0-05-S1-S1 | S1,S1 |
| q0-06-S1-S2 | S1,S2 |
| q0-07-S2-S0 | S2,S0 |
| q0-08-S2-S1 | S2,S1 |
| q0-09-S2-S2 | S2,S2 |

### Q1 — task-bearing contiguous endpoint qualification

Q1 contains records 10–18 and uses only qualification-only contiguous source histories under the unchanged MN-006 transition semantics. Each source has the primary Level 2 entity set, exactly 24 direct non-no-op updates (three per entity), the inherited canonical query identities and contiguous entity permutation, and the direct vector prompt. It contains no equality rule, mapping table, interleaved schedule, or response labels.

The existing baseline inventory did cover all nine vectors, but its selected first-occurrence cases had vector-specific global state-frequency signatures. Q1 therefore freezes additional qualification-only histories rather than modifying any canonical baseline case. Every Q1 history has exactly eight rendered `S0`, eight `S1`, and eight `S2` assignment tokens. It preserves the state machine, scheduler form, query identities/permutations, and replay oracle while avoiding a global-frequency answer shortcut.

| Record | Expected ordered vector | Query order | Inherited v1 identity source |
| --- | --- | --- | --- |
| q1-01-S0-S0 | S0,S0 | E06, E02 | level 2 ordinal 2 |
| q1-02-S0-S1 | S0,S1 | E06, E08 | level 2 ordinal 9 |
| q1-03-S0-S2 | S0,S2 | E04, E05 | level 2 ordinal 11 |
| q1-04-S1-S0 | S1,S0 | E06, E03 | level 2 ordinal 1 |
| q1-05-S1-S1 | S1,S1 | E07, E01 | level 2 ordinal 4 |
| q1-06-S1-S2 | S1,S2 | E04, E02 | level 2 ordinal 3 |
| q1-07-S2-S0 | S2,S0 | E07, E04 | level 2 ordinal 5 |
| q1-08-S2-S1 | S2,S1 | E06, E02 | level 2 ordinal 7 |
| q1-09-S2-S2 | S2,S2 | E01, E08 | level 2 ordinal 0 |

Q1 passing would support only that the qualified model/runtime can recover and serialize both queried entities’ final states across this finite ordered vector space under the Level 2 contiguous control. It does not establish interleaved integration, locality robustness, general long-context tracking, reasoning, or intervention efficacy.

## Coverage and leakage audit

Each layer covers all nine ordered vectors exactly once. Thus every state occurs in each output position; all repeated-state vectors are included; and every asymmetric pair is accompanied by its reversal. Unordered-pair equivalence is not accepted.

The Q1 audit is authority-owned and machine-verifiable. The serialized answer vector never appears in a Q1 prompt, and authority/oracle metadata is not rendered. Query-entity source position is mixed: the first query precedes the second in three sources and follows it in six. No Q1 global state-frequency signature identifies a vector: all are `S0=8`, `S1=8`, `S2=8`. No update is marked as final. The query appears after the histories because it is the question, but it does not expose an answer field. Locating an entity’s latest unmarked assignment is legitimate latest-state recovery; a hidden canonical vector, a unique frequency signature, or an explicit final-state field would not be.

## Exact decision rule

Future qualification has two mandatory layers:

```text
Q0 = 9/9 infrastructure-valid, parser-valid, exact
AND
Q1 = 9/9 infrastructure-valid, parser-valid, exact
→ direct_state_vector_interface_qualified
```

Any infrastructure event, strict-parser/serialization failure, or one incorrect ordered vector produces `direct_state_vector_interface_blocked`. Infrastructure invalidity is separate: `outcome: infrastructure_invalid`, `classification: null`. There is no aggregate threshold, partial pass, retry, prompt tuning, alternate serialization, or second interface search under this contract.

A failed qualification blocks attribution to distributed-state integration; it is not scientific evidence that the model cannot track state. An 18/18 pass only qualifies this interface for a **later static locality gate**. It does not authorize a locality run automatically.

## Retained and retired v1 assets

Retained unchanged: the state vocabulary and transitions, entity IDs, primary profile semantics, replay oracle, deterministic generator, contiguous/interleaved scheduler provenance, canonical runtime helpers, and evidence lifecycle discipline. Historical v1 evidence remains immutable.

Retired from new execution: equality-derived answers, `VALID`/`INVALID` evaluation, A/B label diagnostics as a measurement path, D1/D2 execution chain, and v1 locality scores as evidence about the target locality construct.

## Authorization boundary

The next permitted step is a separate static executor-boundary task for exactly this 18-request qualification authority. No model execution is authorized by this gate. D2 remains permanently unauthorized under v1; locality is unmeasured; the perfect-state diagnostic and all interventions remain unauthorized. Direct state output is answer-adjacent for a prospective external maintained-state treatment, so any later intervention requires a separate anti-oracle/intervention-validity decision.