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

Retrieval and context construction remain separate concepts. Experimental evaluation or prototype code is not reusable package code by default; only proven components may be promoted through an explicit decision. MN-003 first establishes an Effective Context Capacity degradation baseline under controlled context pressure; architecture interventions are deferred until its hypothesis, baseline, variables, and success criteria are defined and measured. No ECC algorithm, dependency structure, retrieval approach, memory, RAG, summarization, compression, or context-routing architecture has been selected.
