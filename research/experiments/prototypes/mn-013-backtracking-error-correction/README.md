# MN-013: Backtracking & Error Self-Correction

## Research Track
**Native Context Capacity (NCC) Phase 3 — Cognitive Orchestration**

## Overview
MN-013 directly resolves the critical bottleneck discovered in [MN-012](../mn-012-hierarchical-tool-memory/README.md) Gate C (Failure Mode 3: Goal Divergence and Horizon Jumping under <4B models).

In MN-012, while `Qwen3.5-2B-Q4_K_M` attained 100% tool grammar adherence and successfully resolved AST syntax errors, it suffered systematic failure whenever an action encountered an environmental dead-end or tool rejection. Small models lack native internal planning horizons: when an action fails, they either repeat the invalid action iteratively (deadlock) or jump precipitously to `ACTION: RESOLVE` with incomplete state. Furthermore, appending error histories directly into the prompt triggers rapid context degradation and breaches the optimal 512-token working frontier.

MN-013 introduces a **Host-Directed Backtracking & Context Rewind Architecture**:
1. **L2 In-Memory Memento Stack:** Host coordinator takes deep-copy snapshots of the environment state before each stateful mutation.
2. **Context Rewind (Zero-Bloat Rollback):** Upon tool rejection or precondition failure, the host rolls back world state to $S_{t-1}$ and purges the erroneous turn from the working prompt context.
3. **Negative Action Masking:** Injects a single bounded negative directive (`"Action X failed (reason Y). Do NOT repeat X."` $\approx 15$ tokens) into the turn prompt, preventing action repetition while keeping total prompt tokens strictly $\le 512$.

## Primary Research Subject
- **`Qwen3.5-2B-Q4_K_M.gguf`** (Canonical Primary Model, qualified under MCB v0.3.0 and validated across MN-008 through MN-012).
- Secondary Generalization Baselines: `Llama-3.2-3B-Instruct-Q4_K_M.gguf`, `Qwen3-4B-Q4_K_M.gguf`.

## Navigation
- [Gate A Charter](charter.md)
- [Gate B Measurement Contract](gate-b-contract.md)
- [Predecessor: MN-012 Disposition Review](../mn-012-hierarchical-tool-memory/gate-d-disposition-review.md)
- [Canonical Architecture](../../../concepts/architecture.md)
- [Decisions Log](../../../decisions/decisions.md)
- [Roadmap](../../../roadmap.md)
