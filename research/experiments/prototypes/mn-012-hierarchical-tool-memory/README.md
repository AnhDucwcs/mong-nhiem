# MN-012: Hierarchical Tool & Memory Integration

## Research Track
**Native Context Capacity (NCC) Phase 3 — Cognitive Orchestration**

## Overview
MN-012 advances Mộng Nhiễm from passive multi-hop context retrieval ([MN-010](../mn-010-iterative-context-loop/README.md)) to active, structured tool interaction and dual-tier hierarchical memory partitioning.

In MN-010, the host coordinator and language model resolved read-only dependency chains using an elementary action grammar (`ACTION: FETCH <target>`). However, evolving state in complex domains or simulated environments requires:
1. **Parameterized Tool Contracts:** Structured inspection and mutation operations (`READ`, `INSPECT`, `DISPATCH`) with deterministic observation feedback.
2. **Dual-Tier Memory Partitioning:** Decoupling ephemeral, token-bounded working sets (L1: $\le 512$ tokens in prompt context) from persistent, structured state ledgers (L2: host disk state storage).

MN-012 is the primary operational bridge toward the project's North Star Benchmark: **Stateful Simulated Microworld Evolution** ($T \ge 20-50$ steps). Crucially, MN-012 acts as an explicit **failure-isolation boundary and directional pivoting gate**: if lightweight models (<4B) cannot reliably maintain format adherence or state continuity under tool interactions ($T \le 5$), the milestone provides empirical grounds to revise the grammar or abstraction layer before introducing backtracking (MN-013) or long-horizon microworlds.

## Primary Research Subject
- **`Qwen3.5-2B-Q4_K_M.gguf`** (Canonical Primary Model, qualified under MCB v0.3.0 and validated across MN-008 through MN-011).
- Secondary Generalization Baselines: `Llama-3.2-3B-Instruct-Q4_K_M.gguf`, `Qwen3-4B-Q4_K_M.gguf`.

## Navigation
- [Gate A Charter](charter.md)
- [Gate B Measurement Contract](gate-b-contract.md)
- [Canonical Architecture](../../../concepts/architecture.md)
- [Decisions Log](../../../decisions/decisions.md)
- [Roadmap](../../../roadmap.md)
