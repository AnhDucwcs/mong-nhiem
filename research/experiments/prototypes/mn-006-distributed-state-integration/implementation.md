# MN-006 v1 deterministic infrastructure

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

The later [Label-Selection Causal Gate](label-selection-causal-gate.md) freezes a separate D1 direct-state mapping diagnostic; an executor and any model behavior remain future work, and D2 contiguous source-event reconstruction is contingent on D1 exact mapping following.

[`run_mn006_label_selection_d1.py`](scripts/run_mn006_label_selection_d1.py) is a distinct pre-evidence executor for the frozen 16-request D1 diagnostic. It reuses the qualified runtime lifecycle and append-only evidence policy, but consumes only direct-state D1 entries; it cannot submit D2.
