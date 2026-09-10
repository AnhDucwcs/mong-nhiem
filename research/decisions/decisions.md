# Decisions

| Date | Decision | Status |
| --- | --- | --- |
| 2026-08-19 | Mộng Nhiễm is structured as a reusable Python library under `src/mong_nhiem/`. | accepted |
| 2026-08-19 | Retrieval and context construction remain separate conceptual areas. | accepted |
| 2026-08-19 | Experimental code remains separate from the reusable package. | accepted |
| 2026-08-19 | Memory, tools, and autodream are optional extensions, not core dependencies. | accepted |
| 2026-08-22 | Research experiments live under `research/experiments/` as part of the canonical knowledge base while remaining separate from reusable package code. | accepted |
| 2026-08-22 | MN-002 uses a deterministic minimum-capability qualification gate rather than a general model leaderboard. | accepted |
| 2026-08-22 | Capability qualification remains separate from runtime-performance measurement. | accepted |
| 2026-08-23 | MCB v0.3.0 freezes definitions and uses explicit accepted-answer contracts for semantic suites while keeping strict format tests strict. | accepted |
| 2026-08-28 | MN-003 completed its bounded direct-context measurement phase; its canonical synthesis closes further ECC measurement work without selecting an architecture, and MN-004 begins as a separate hypothesis/intervention-design milestone inheriting immutable ECC-006 baseline evidence. | accepted |
| 2026-09-05 | MN-004 closes the globally indexed state-transition ledger hypothesis as `unsupported_no_effect_or_insufficient_effect`: Llama 8k improved from `0/24` untreated to `7/24` ledger but missed both frozen support thresholds; Gate D promotion is not earned, thresholds and treatment are not retuned, and the experimental implementation remains outside `src/mong_nhiem/`. | accepted |
| 2026-09-07 | MN-005 is prepared as a separate design-only successor milestone. It must compare candidate state-management/state-representation mechanisms and freeze one falsifiable Gate A hypothesis before measurement design or model inference; no candidate architecture is preselected. | accepted |

Record meaningful architecture or evaluation decisions here. Research hypotheses, parameters, and measurements belong in the relevant experiment evidence.
