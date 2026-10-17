# Architecture

Only high-level boundaries are established.

| Area | Responsibility |
| --- | --- |
| `src/mong_nhiem/core/` | Foundational invariants, hash-chained causal events, and vector clocks. |
| `src/mong_nhiem/context/` | Scoped context delivery (`ContextPacker`, `CodebaseSlicer`) and working set coordinator. |
| `src/mong_nhiem/extensions/autodream/` | High-density Fact Card projection and $O(M)$ frontier branch compaction. |
| `src/mong_nhiem/knowledge/` | Multi-parent Causal Event DAGs, epistemic reconcilers, and dynamic schema registries. |
| `src/mong_nhiem/orchestration/` | Multi-resource leases, Byzantine admission gates, star consensus hubs, network transport, and hierarchical planners. |
| `src/mong_nhiem/runtime/` | Authoritative discrete simulated microworlds with Memento rollback. |
| `src/mong_nhiem/retrieval/` | Future retrieval abstractions over large external knowledge spaces. |
| `src/mong_nhiem/models/` | Future model-facing integration adapters. |
| `src/mong_nhiem/evaluation/` | Reusable evaluation frameworks and benchmark contracts. |
| `research/experiments/` | Hermetically quarantined experimental baselines and empirical evidence. |

Retrieval and context construction remain separate concepts. Experimental evaluation or prototype code is strictly quarantined by default; only proven cognitive components earn promotion into `src/mong_nhiem/` through formal Gate D disposition reviews (ADR-0009, ADR-0010, ADR-0015, and ADR-0023). Zero third-party dependencies are admitted into core library code (100% Python Standard Library). See foundational research track definitions and principles in [ECC vs NCC](ecc-vs-ncc.md).

