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

Record meaningful architecture or evaluation decisions here. Research hypotheses, parameters, and measurements belong in the relevant experiment evidence.
