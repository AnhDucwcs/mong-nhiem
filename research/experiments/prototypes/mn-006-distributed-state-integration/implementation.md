# MN-006 v1 deterministic infrastructure

## Status

**`generator_oracle_validator_implementation_complete`** for the frozen MN-006 v1 semantic contract. The subsequent [Baseline Inventory and Measurement Gate](baseline-inventory-measurement-gate.md) materializes and validates the pre-model inventory. This remains executable non-model infrastructure, not measured evidence, a candidate treatment, or a model-inference authorization.

## Implemented boundary

The MN-006-local `scripts/mn006/` package now provides:

- bounded generation by construction from profile, ordinal, and root seed;
- independently derived named sub-seeds for query selection, entity permutation, target-state tuple rotation, and history construction;
- one shared canonical core with paired `contiguous_control` and regular round-robin `interleaved` schedules;
- pure `replay → derive(equal_state) → decide(VALID/INVALID)` oracle functions;
- separate public, evaluator, and authority records;
- UTF-8/LF canonical JSON/text serialization and SHA-256 fingerprints; and
- semantic, oracle, schedule, matched-pair, public-boundary, answer-proxy, and positional static validators.

The package never calls a model, GPU runtime, treatment, external service, or answer-selection host logic. Test-only batches are generated in memory by unit tests and are not an inventory or research evidence.

## v1 periodicity boundary

The interleaved serializer intentionally repeats one seeded entity permutation for all three assignment rounds. It therefore tests **regular round-robin distributed interleaving**, not arbitrary or irregular interleaving. Authority metadata retains query permutation slots, source positions, query-gap vectors, and relevant spans; the positional audit makes position coverage visible without changing the frozen scheduler.

## Next boundary

The inventory and measurement contract is now frozen. `scripts/mn006/inventory.py` materializes its public, evaluator, and authority artifacts with exact binary write/readback SHA-256 verification. The next boundary is the first predeclared Llama baseline execution under that contract, after its environment preflight. It is not candidate-intervention selection.
