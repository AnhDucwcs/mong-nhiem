# Architecture

Only high-level boundaries are established.

| Area | Responsibility |
| --- | --- |
| `src/mong_nhiem/` | Future reusable Python library. |
| `api/` | Reserved future external API. |
| `core/` | Reserved shared domain contracts and foundations. |
| `knowledge/` | External knowledge available to the system. |
| `retrieval/` | Finding potentially relevant information from a large knowledge space. |
| `context/` | Deciding what enters a model's usable context. |
| `models/` | Model adapters and model-facing integration, without coupling to one LLM. |
| `runtime/` | Future orchestration. |
| `extensions/` | Optional memory, tools, and autodream capabilities. |
| `evaluation/` | Reusable evaluation work. |
| `experiments/` | Baselines and prototypes separate from package code. |

Retrieval and context construction are conceptually separate. Extensions must not become core architectural dependencies. No algorithms, APIs, or dependency direction beyond these boundaries have been decided.
