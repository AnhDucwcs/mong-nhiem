# MN-006 v1 deterministic infrastructure

## Direct-state-vector qualification executor boundary

The frozen [construct-validity gate](direct-state-vector-construct-validity-gate.md) has a separate executor, [`run_mn006_direct_state_vector_qualification.py`](scripts/run_mn006_direct_state_vector_qualification.py), for only `direct-state-vector-qualification-run-0001`. Its canonical [qualification evidence](reports/mn-006-direct-state-vector-qualification-run-0001.md) is now retained. The authority remains SHA-256 `5a487200b0dd72275d37482bc0c3c5cd09feed483419223005519b5034064bbc`; gate, redesign, old plans, histories, and prior retained model evidence are unchanged.

The runner's `--dry-run` path reads repository branch identity, rejects existing canonical/pending/invalid output, verifies the physical authority and prerequisite hashes, freshly validates the baseline inventory, and constructs exactly nine Q0 then nine Q1 payloads in memory. It starts no subprocess, opens no model, makes no network call, and writes no evidence. Implementation edits are allowed during static construction; the future real preflight additionally requires a clean repository synchronized with the requested upstream. All prompts, vectors, grammar bytes, ordering, queries, and histories are loaded from physical authority records. Deterministic regeneration is used only to validate those records. Exact authority Q1 events are replayed through the unchanged oracle and checked for contiguous order, expected ordered states, and the frozen no-leakage constraints.

The frozen JSON plan does not contain a top-level evaluator-version field. The executor records the evaluator version from the existing frozen helper and verifies the unchanged gate that names it; it does not add a field or reserialize the authority. Runtime values come from the inherited baseline runtime source, guarded by its frozen parameter fingerprint. Before any future server startup the real preflight verifies model bytes, executable identity, endpoint, repository cleanliness, remote synchronization, inventory, authority, output absence, and the existing GPU/process rules.

Prospective evidence is `metadata.json`, `results.jsonl`, `server-lifecycle.json`, `summary.json`, `integrity.json`, and the two `raw/llama-server` logs. Each retained request includes authority source facts, global/layer ordinals, exact payload/response text, strict vector evaluation, timing, tokens, finish reason, and runtime identity. The lifecycle is private pending state, exactly 18 requests without retries, controlled cleanup, completeness validation, frozen classification, physical hashes, completed-artifact validation, then same-volume atomic promotion. The canonical validator rejects pending/invalid directory identities; incomplete or infrastructure-invalid data receives `classification: null`. A finalization failure preserves raw records and its provisional summary in the invalid directory and writes an infrastructure-invalid final summary.

Canonical [qualification evidence](reports/mn-006-direct-state-vector-qualification-run-0001.md) now records `protocol_valid` / `direct_state_vector_interface_blocked`: Q0 exact vector output was `9/9`, but Q1 task-bearing contiguous recovery was `1/9`. The frozen all-cells-exact condition was therefore not met. This blocks this measurement instrument for the qualified model/runtime without establishing a general state-tracking, locality, or reasoning deficit. Under the frozen redesign, MN-006 is `measurement_interface_blocked`; no retry, alternate serialization/interface search, locality gate, D2, perfect-state work, or intervention is authorized.

## Status

**`generator_oracle_validator_implementation_complete`** for the frozen MN-006 v1 semantic contract. The subsequent [Baseline Inventory and Measurement Gate](baseline-inventory-measurement-gate.md) materialized the inventory. The dedicated frozen runners produced protocol-valid [attempt-0001](reports/mn-006-attempt-0001.md) and separately frozen grammar-constrained [attempt-0002](reports/mn-006-attempt-0002.md). The runner remains untreated baseline infrastructure; it is not a candidate-treatment implementation.

## Implemented boundary

The MN-006-local `scripts/mn006/` package now provides:

- bounded generation by construction from profile, ordinal, and root seed;
- independently derived named sub-seeds for query selection, entity permutation, target-state tuple rotation, and history construction;
- one shared canonical core with paired `contiguous_control` and regular round-robin `interleaved` schedules;
- pure `replay → derive(equal_state) → decide(VALID/INVALID)` oracle functions;
- separate public, evaluator, and authority records;
- UTF-8/LF canonical JSON/text serialization and SHA-256 fingerprints; and
- semantic, oracle, schedule, matched-pair, public-boundary, answer-proxy, and positional static validators; and
- a non-measured `label_selection` diagnostic planner with canonical prompt/fingerprint construction, strict `A`/`B` parsing, mapping/grammar counterbalance validation, and predeclared outcome classifiers.

The generator/oracle package never calls a model or answer-selection host logic. The separate `run_mn006_baseline.py` executes only the predeclared untreated Llama request plan, with no prompt adaptation, case replacement, retry, or treatment. Test-only batches remain separate from inventory and measured evidence.

## v1 periodicity boundary

The interleaved serializer intentionally repeats one seeded entity permutation for all three assignment rounds. It therefore tests **regular round-robin distributed interleaving**, not arbitrary or irregular interleaving. Authority metadata retains query permutation slots, source positions, query-gap vectors, and relevant spans; the positional audit makes position coverage visible without changing the frozen scheduler.

## Next boundary

The frozen first baseline's shared malformed-output floor did not authorize a candidate intervention or the perfect-state diagnostic. The [Response-Channel Gate](response-channel-gate.md) then prospectively froze the grammar-only `attempt-0002` executor before its model behavior was observed. [`run_mn006_constrained_baseline.py`](scripts/run_mn006_constrained_baseline.py) reused the baseline lifecycle and added only the constant request-level grammar; its resulting measurement is protocol-valid but has no usable locality signal because every parsed response was `INVALID`. No tuning, prompt revision, parser relaxation, or case change occurred.

The later [Label-Selection Causal Gate](label-selection-causal-gate.md) freezes a separate D1 direct-state mapping diagnostic. Its executor was committed before behavior and the retained [D1 run](reports/mn-006-label-selection-d1-run-0001.md) is `protocol_valid` / `fixed_label_preference_supported`: all 16 neutral constrained outputs were `A` and no grammar-order pair disagreed. D2 contiguous source-event reconstruction remains unauthorized because D1 did not satisfy its exact mapping-following prerequisite.

[`run_mn006_label_selection_d1.py`](scripts/run_mn006_label_selection_d1.py) is the distinct D1 executor for the frozen 16-request direct-state diagnostic. It reused the qualified runtime lifecycle and append-only evidence policy, consumed only D1 entries, and cannot submit D2.

The later [Output-Selection Minimality Gate](output-selection-minimality-gate.md) adds only `output_selection.py`, a non-executing deterministic authority-plan and classifier module for S0/S1 diagnostics. It freezes four S0 direct-copy requests and four conditional S1 direct-relation requests under the existing neutral A/B grammar/parser. The separate [`run_mn006_output_selection_s0.py`](scripts/run_mn006_output_selection_s0.py) executor consumed only the canonical S0 plan, staged evidence privately, and promoted the canonical run only after all four requests and the frozen validator passed. The resulting [S0 evidence](reports/mn-006-output-selection-s0-run-0001.md) is protocol-valid / `direct_copy_supported`. The separate [`run_mn006_output_selection_s1.py`](scripts/run_mn006_output_selection_s1.py) executor mechanically revalidated S0 integrity and its exact classification before constructing the four frozen direct-relation requests, then staged and atomically promoted only complete validated evidence. The resulting [S1 evidence](reports/mn-006-output-selection-s1-run-0001.md) is protocol-valid / `fixed_label_preference_recurred`: all four outputs were `A`, so direct equality/instruction following is not established and the D1 failure cannot be localized specifically to its added mapping-table abstraction. D2 remains independently blocked by its D1 prerequisite; neither reconstruction, locality, nor intervention efficacy follows.
