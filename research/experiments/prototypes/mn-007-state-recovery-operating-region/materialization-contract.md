# MN-007 — Deterministic Materialization Contract

## Status and authority boundary

**mn007_deterministic_materialization_contract_frozen**

This document freezes the deterministic source construction for the prospective
MN-007 contiguous calibration landscape. It is a pre-measurement design boundary,
not a corpus, inference authority, run plan, executor, or result. It creates no
calibration case artifact, public prompt corpus, model request, response, or
measured evidence.

It implements the construction required by the immutable
[operating-region design gate](operating-region-design-gate.md) without changing
the six cells, the 18 cases per cell, the 15–16/18 usable band, the 17–18/18
ceiling band, or deterministic usable-cell selection.

The next permitted action is a separately authorized deterministic
implementation/infrastructure stage. It may materialize and validate the frozen
corpus, but cannot authorize model execution. A later explicit authority remains
necessary before clean-environment calibration.

## 1. Namespaces and stable identities

All identifiers are ASCII and derived from frozen inputs; none is allocated after
materialization.

| Role | Frozen identifier or grammar |
| --- | --- |
| Contract namespace | mn007-materialization-contract-v1 |
| Calibration namespace | mn007-calibration-v1 |
| Semantic-case schema | mn007-semantic-case-v1 |
| Public-prompt schema | mn007-public-prompt-v1 |
| Evaluator schema | mn007-evaluator-oracle-v1 |
| Reserved future hold-out namespace | mn007-locality-holdout-v1 |
| Cell ID | mn007-calibration-v1-e{E}-{placement} |
| Case ID | {cell_id}-c{ordinal} |
| Semantic-history identity | mn007-sem-v1-{sha256} |

E is exactly 3, 5, or 7; placement is exactly terminal or leading; ordinal is
two decimal digits from 01 through 18. Therefore:

    cell_id ::= mn007-calibration-v1-e(3|5|7)-(terminal|leading)
    case_id ::= cell_id-c(01|02|...|18)

The canonical cell order is e3 terminal, e3 leading, e5 terminal, e5 leading,
e7 terminal, e7 leading, each under the calibration namespace.

For case ordinal n, vector slot is (n - 1) modulo 9. Orientation is source_order
for 01–09 and reverse_source_order for 10–18. Cases c01/c10 through c09/c18
share a vector slot and source entity permutation, while retaining individual
semantic histories. Each slot thus has one source-order and one reverse-order
presentation.

Semantic-history identity is the literal prefix mn007-sem-v1- followed by the
lowercase hexadecimal SHA-256 of canonical semantic-source bytes. The source
contains all semantic construction fields except that derived identity. A mismatch
is a materialization failure, never a corrected identifier.

## 2. Root seed and deterministic sub-seeds

The canonical root-seed text is:

    mn007-state-recovery-operating-region|calibration|materialization-contract-v1|root-seed

No implementation-language pseudo-random generator is part of this contract.
Every seed uses SHA-256. Let US be the single ASCII Unit Separator byte 0x1f.
Hash the UTF-8 bytes of this exact concatenation, with no trailing separator or
newline:

    MN007-SEED-V1 <US> root-seed-text <US> scope <US> cell-id <US>
    pair-slot <US> case-ordinal <US> purpose

Pair slot is two decimal digits 00–08; case ordinal is 01–18. The stored result
is the 32-byte SHA-256 digest in lowercase hexadecimal.

For the case-pair scope, case ordinal is the literal sentinel 00. For the case
scope, pair slot and case ordinal are the values derived from that actual case.
This makes the shared source entity order unambiguous.

| Domain | Scope | Purpose | Rule |
| --- | --- | --- | --- |
| Source entity order | case-pair | entity-rank | Shared by the paired orientation cases. |
| Query orientation | case | query-orientation | Provenance check; must equal the ordinal rule. |
| Expected vector | case | expected-vector | Provenance check; must equal frozen vector slot. |
| Queried histories | case | queried-history-rank | Ranks queried histories. |
| Non-query histories | case | non-query-history-rank | Ranks non-query histories. |

For candidate ranking, append one US and the canonical ASCII candidate signature
to the applicable domain preimage and SHA-256 it. Sort ascending digest bytes,
then canonical signature. If an integer is needed, use only the first 16 digest
bytes as one unsigned big-endian integer. No other truncation or reinterpretation
is permitted.

## 3. Canonical semantic case schema

Semantic truth is authoritative; rendered prompt text is derived and cannot define
the expected answer. Each case contains:

| Field | Meaning |
| --- | --- |
| schema_id | mn007-semantic-case-v1 |
| case_id, cell_id, semantic_history_id | Stable identities from section 1. |
| global_ordinal, cell_ordinal, vector_slot | Frozen ordering integers. |
| entity_count, updates_per_entity, initial_state, state_vocabulary | E, 3, S0, and ordered [S0,S1,S2]. |
| active_entities, source_block_order | Active inventory and contiguous schedule order. |
| source_query_entities, query_entities, query_orientation | Source pair, declared prompt pair, and orientation. |
| assignment_histories, event_stream | Three ordered assignments/entity and derived ordered events. |
| source_final_states, query_final_states, expected_vector | Evaluator authority in source and declared query order. |
| difficulty | E, placement, event count, non-query count, source-order distances. |
| query_order_latest_update_distances | Derived source distances after applying output orientation. |
| state_assignment_counts, seed_provenance | Per-case balance and deterministic reconstruction data. |
| public_prompt_fingerprint | SHA-256 of separately serialized public prompt bytes. |

The event stream is retained so an independent validator can replay final state,
verify distances, and verify the serializer without trusting implementation state.

## 4. Entities, queries, and orientation

For entity count E, the active inventory is E01 through E0E in that canonical
order. These are opaque IDs. Rank each entity using the shared pair's entity-rank
seed and candidate signature entity:ENTITY_ID. The ascending order is the source
entity permutation. Its first two entities are source query entities q1 and q2;
the rest are non-query entities. This occurs before state assignment and never
uses a vector value.

Terminal source blocks are non-query entities in permutation order, q1, q2.
Leading source blocks are q1, q2, then non-query entities in permutation order.

For first vector occurrence, query_entities are q1,q2. For second occurrence,
they are q2,q1. Expected vector follows declared query order. Hence the same
vector S0,S2 assigns q1=S0/q2=S2 in source order, and q1=S2/q2=S0 in reverse
order. This retains the observable vector while balancing output orientation.

## 5. State histories and balance

The exact vector order is:

    S0,S0  S0,S1  S0,S2  S1,S0  S1,S1  S1,S2  S2,S0  S2,S1  S2,S2

Slots 00–08 use it once in cases 01–09 and once in cases 10–18. Thus each ordered
vector occurs exactly twice per cell, and every orientation appears exactly nine
times.

Every entity receives a three-state direct-assignment history a1,a2,a3 such that:

    a1 != S0
    a2 != a1
    a3 != a2
    every ai is S0, S1, or S2

a3 is its final state. Candidate histories are filtered to the required a3 and
ranked in their deterministic domain using:

    entity:ENTITY_ID|history:a1,a2,a3

In canonical entity-ID order, choose the lexicographically first Cartesian product
of ranked candidate lists whose aggregate rendered assignments have exactly E
occurrences of each S0, S1, and S2. There is no resampling, manual curation, or
fallback: failure to find a combination blocks materialization.

The condition is always semantically feasible: histories S1,S2,S0; S2,S0,S1; and
S1,S0,S2 are valid examples ending in S0, S1, and S2 respectively and each
contains one of every state. Ranking selects a valid construction deterministically
without hand selection.

## 6. Contiguous schedule and distance metric

Every source block has three adjacent event lines. For one-based source block
position b, its event ordinals are 3b-2, 3b-1, 3b. With E blocks:

    latest_update_distance(b,E) = 3E - 3b

The metric counts only assignment-event lines after the entity's last update and
before the query/instruction section. It excludes query and output lines.

Frozen difficulty distances are stored in source-query block order q1,q2, never
in possibly reversed public output order:

| Cell | Source blocks | Distances |
| --- | --- | --- |
| e3_terminal | 2,3 | 3,0 |
| e3_leading | 1,2 | 6,3 |
| e5_terminal | 4,5 | 3,0 |
| e5_leading | 1,2 | 12,9 |
| e7_terminal | 6,7 | 3,0 |
| e7_leading | 1,2 | 18,15 |

Query-order distances are derived by orientation and may be recorded only as
diagnostic metadata. No event is marked final.

## 7. Public rendering and authority separation

A renderer may derive a public prompt only from the common initial state, ordered
event stream, and declared query entities. It must use LF and exactly one final LF:

    All entities begin in S0.
    ENTITY_ID STATE = STATE_TOKEN
    ...
    For QUERY_ENTITY_1 and QUERY_ENTITY_2, output their final states in this order.
    Output exactly two state tokens from S0, S1, S2 separated by one comma.

There is one initial line, exactly 3E event lines, then the two query/output lines.
No system prompt, examples, derived rule, mapping, answer label, or optional
wording is permitted. The output grammar is:

    root ::= state "," state
    state ::= "S0" | "S1" | "S2"

with one final LF. The strict parser accepts only the nine bare vectors after
outer ASCII whitespace trimming.

| Artifact role | May contain | Must not contain |
| --- | --- | --- |
| Semantic/evaluator authority | Histories, finals, expected vector, seeds, provenance, replay results | Model responses or result classifications. |
| Public prompt material | Prompt bytes/fingerprint, grammar bytes, opaque public fields | Case ID or placement in model-visible prompt text; expected vector, finals, seeds, oracle, evaluator metadata, or qualification status. |
| Later request metadata | Public prompt, grammar, runtime fields, opaque ID | Expected answer or evaluator-only truth. |
| Later measurement evidence | Raw request/response, parser, timing, infrastructure data | Authority mutation or response-dependent prompt changes. |

The evaluator may join a persisted raw record to semantic truth only by canonical
case ID after raw request and response retention. Persist-before-evaluate is
required.

## 8. Canonical serialization and determinism

All later semantic, public, evaluator, and manifest JSON uses UTF-8 without BOM,
NFC strings, LF only, recursively Unicode-code-point-sorted object keys, no
insignificant whitespace, declared array order, JSON integer numbers without
leading zeros, JSON strings for identity/token/digest fields, and exactly one
terminal LF. SHA-256 fingerprints are lowercase hex digests of physical bytes.

Future semantic JSONL order is canonical cell order then cell ordinals 01–18.
Public and evaluator artifacts use the same order. This task does not produce any
of those files or their hashes.

A later static implementation must regenerate twice in clean locations and require
byte-identical semantic JSONL, public prompt bytes, evaluator records, and
manifests. Only then may it record contract-document, root-seed-text, per-cell
semantic, full-corpus, public-manifest, and evaluator-manifest SHA-256 values plus
the materializer revision. Any mismatch blocks executor implementation and model
authority.

## 9. Required validators and failure boundary

A materialized corpus is invalid if any of these checks fail:

1. six cells, exactly 18 cases each, and 108 total, with global ordinals 1–108
   assigned only by canonical cell order then cell ordinal;
2. unique derivable IDs, semantic identities, and seed provenance;
3. unchanged E/P landscape, event/non-query counts, and distances;
4. canonical opaque inventory, permutation, query identities, and 9/9 orientation balance;
5. exactly three assignments/entity, initial S0, no consecutive no-op, contiguous blocks;
6. every ordered vector exactly twice per cell;
7. exactly E rendered occurrences of each state in every case;
8. replayed finals and expected vector equal authority in declared query order;
9. exact schedule placement, event counts, and distance metric;
10. exact state vocabulary, grammar, parser-compatible output form, and renderer;
11. no expected vector, final state, oracle, seed, provenance, placement, or evaluator leakage in public prompt material;
12. canonical-byte serialization and required fingerprints.

Semantic failure blocks materialization. A fingerprint mismatch blocks executor
implementation and model authority. Public leakage blocks all model authority.
Later execution validation is separate and cannot repair construction failure.

## 10. Calibration and hold-out separation

All mn007-calibration-v1 cases are calibration only. A later locality study must
use mn007-locality-holdout-v1, or a versioned successor, with distinct root seed,
cell/case IDs, semantic identities, permutations, histories, prompts, and bytes.
It may reuse only frozen semantic rules, selected parameters, parser, observable,
and runtime identity after its own locality gate. Calibration cases may never be
relabeled, rescheduled, or reused as contiguous/interleaved hold-out evidence.

## 11. Future executor boundary

A later executor may consume frozen public prompts, grammar bytes, opaque IDs,
runtime/request parameters, and public integrity metadata. It must not consume
expected vectors, semantic finals, evaluator records, operating-region
classifications, or response-dependent substitutions. It must persist raw
request/response before evaluation and make every future request independently
under separately frozen runtime authority.

It cannot create a locality comparison or intervention. A later calibration remains
subject to the design gate's unchanged 15–16/18 usable, 17–18/18 ceiling, and
deterministic selection rules.

## 12. Exact next authorization

The sole next permitted task is a separate static deterministic implementation and
infrastructure stage that materializes and validates this corpus. It must confirm
reproducibility and all validators without starting a model, creating a run
authority, or sending a request. Only after that stage may another authority
consider an executor boundary; model calibration remains separately authorized.
