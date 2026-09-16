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

The later [Label-Selection Causal Gate](label-selection-causal-gate.md) freezes a separate D1 direct-state mapping diagnostic. Its executor was committed before behavior and the retained [D1 run](reports/mn-006-label-selection-d1-run-0001.md) is `protocol_valid` / `fixed_label_preference_supported`: all 16 neutral constrained outputs were `A` and no grammar-order pair disagreed. D2 contiguous source-event reconstruction remains unauthorized because D1 did not satisfy its exact mapping-following prerequisite.

[`run_mn006_label_selection_d1.py`](scripts/run_mn006_label_selection_d1.py) is the distinct D1 executor for the frozen 16-request direct-state diagnostic. It reused the qualified runtime lifecycle and append-only evidence policy, consumed only D1 entries, and cannot submit D2.

The later [Output-Selection Minimality Gate](output-selection-minimality-gate.md) adds only `output_selection.py`, a non-executing deterministic authority-plan and classifier module for S0/S1 diagnostics. It freezes four S0 direct-copy requests and four conditional S1 direct-relation requests under the existing neutral A/B grammar/parser. The separate [`run_mn006_output_selection_s0.py`](scripts/run_mn006_output_selection_s0.py) executor consumed only the canonical S0 plan, staged evidence privately, and promoted the canonical run only after all four requests and the frozen validator passed. The resulting [S0 evidence](reports/mn-006-output-selection-s0-run-0001.md) is protocol-valid / `direct_copy_supported`; no S1 executor or D2 path exists. S1 is eligible only for a future separately authorized run because S0 exactly met its frozen prerequisite.
