# MN-006 v1 deterministic infrastructure

## Status

**`generator_oracle_validator_implementation_complete`** for the frozen MN-006 v1 semantic contract. The subsequent [Baseline Inventory and Measurement Gate](baseline-inventory-measurement-gate.md) materialized the inventory, and the dedicated frozen attempt runner produced the protocol-valid [attempt-0001](reports/mn-006-attempt-0001.md). The [Response-Channel Gate](response-channel-gate.md) now adds only static helpers that prove a future payload changes by one constant grammar field. The runner remains untreated baseline infrastructure; it is not a candidate-treatment implementation.

## Implemented boundary

The MN-006-local `scripts/mn006/` package now provides:

- bounded generation by construction from profile, ordinal, and root seed;
- independently derived named sub-seeds for query selection, entity permutation, target-state tuple rotation, and history construction;
- one shared canonical core with paired `contiguous_control` and regular round-robin `interleaved` schedules;
- pure `replay → derive(equal_state) → decide(VALID/INVALID)` oracle functions;
- separate public, evaluator, and authority records;
- UTF-8/LF canonical JSON/text serialization and SHA-256 fingerprints; and
- semantic, oracle, schedule, matched-pair, public-boundary, answer-proxy, and positional static validators; and

The generator/oracle package never calls a model or answer-selection host logic. The separate `run_mn006_baseline.py` executes only the predeclared untreated Llama request plan, with no prompt adaptation, case replacement, retry, or treatment. Test-only batches remain separate from inventory and measured evidence.

## v1 periodicity boundary

The interleaved serializer intentionally repeats one seeded entity permutation for all three assignment rounds. It therefore tests **regular round-robin distributed interleaving**, not arbitrary or irregular interleaving. Authority metadata retains query permutation slots, source positions, query-gap vectors, and relevant spans; the positional audit makes position coverage visible without changing the frozen scheduler.

## Next boundary

The frozen first baseline is complete. Its valid shared malformed-output floor does not authorize a candidate intervention or the perfect-state diagnostic. The [Response-Channel Gate](response-channel-gate.md) completes the separate causal-design review and freezes a grammar-only future `attempt-0002`; no model response was observed in that review. [`run_mn006_constrained_baseline.py`](scripts/run_mn006_constrained_baseline.py) is now the distinct pre-evidence executor: it reuses the baseline lifecycle and adds only the constant request-level grammar. Its next use requires a clean-environment execution task, with no tuning, prompt revision, parser relaxation, or case change.
