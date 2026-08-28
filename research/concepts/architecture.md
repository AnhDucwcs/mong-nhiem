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

Retrieval and context construction remain separate concepts. Experimental evaluation or prototype code is not reusable package code by default; only proven components may be promoted through an explicit decision. MN-003 established an Effective Context Capacity degradation baseline under controlled context pressure and completed its synthesis; a future intervention must still be separately hypothesized and authorized. No ECC algorithm, dependency structure, retrieval approach, memory, RAG, summarization, compression, or context-routing architecture has been selected.
