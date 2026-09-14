# MN-005 Gate C v2 attempt-0002 invalid-attempt report

**Status:** `experiment_invalid`
**Efficacy:** `not_applicable_due_to_invalid_experiment`

All six Arm A outcomes and all twelve B/C paired outcomes were retained. After the final response, the runner crashed during post-run classification: the frozen implementation passed paired dictionaries to a classifier that requires flattened records. Consequently it did not produce a contract-valid canonical classification. This is an implementation/infrastructure invalidation, not an efficacy finding. Raw evidence is retained unchanged; no replacement attempt was started.
