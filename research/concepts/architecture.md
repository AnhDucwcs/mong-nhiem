# Architecture

Only high-level boundaries are established.

| Area | Responsibility |
| --- | --- |
| `src/mong_nhiem/` | Reusable Python library. |
| `retrieval/` | Find potentially relevant information from a large knowledge space. |
| `context/` | Decide what enters a model's usable context. |
| `models/` | Future model-facing integration. |
| `evaluation/` | Future reusable evaluation components once proven. |
| `research/experiments/` | Experimental baselines and prototypes; evidence, not package code. |

Retrieval and context construction remain separate concepts. Experimental evaluation or prototype code is not reusable package code by default; only proven components may be promoted through an explicit decision. Under Decision 2026-10-01 (Gate D Promotion), the scoped context delivery subsystem was promoted into `src/mong_nhiem/context/` (`ContextPacker`, `CodebaseSlicer`, projections, and sanitization). Retrieval, memory, and context-routing architectures remain open for subsequent research milestones. See foundational research track definitions and principles in [ECC vs NCC](ecc-vs-ncc.md).
