# MN-004 Gate C implementation checklist

This checklist maps the frozen Gate B contract to implementation evidence. All items must validate before measured inference.

| Contract requirement | Implementation control | Offline evidence |
| --- | --- | --- |
| Gate A/B and ECC-006 authority remain immutable | definition pins SHA-256 references and ECC-006 fingerprint | `validate_mn004.py --definition` |
| Frozen and fresh source inventory | deterministic materializer with no replacement path | inventory hash and reconstruction validator |
| Exact untreated and ledger renderings | parser-backed renderers | semantic-equivalence validator |
| No answer leakage or target cues | prohibited-field and source-event checks | paired prompt validator |
| Exact evaluator and diagnostics | ECC-006-compatible evaluator | evaluator fixture tests and retained ECC-006 replay |
| Token/context hard gate | model-specific token preflight for every pair | preflight records and overflow rejection |
| Runtime/model invariants | model hash/runtime/config validation | run metadata validator |
| Retained raw evidence | versioned request/result schema | schema and run validator |
| Frozen execution order and verdicts | phase runner plus mechanical analysis | runner precondition checks and report validator |

No checklist item authorizes a change to Gate A or Gate B. A failed hard gate is retained as a feasibility or invalid-comparison outcome.
