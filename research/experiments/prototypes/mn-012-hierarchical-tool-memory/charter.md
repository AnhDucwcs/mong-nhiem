# MN-012 Gate A: Charter & Scientific Hypotheses

## Context & Navigation
- Canonical Knowledge Base: [00-mong-nhiem](../../../00-mong-nhiem.md)
- System Architecture: [architecture](../../../concepts/architecture.md)
- Conceptual Taxonomy: [ECC vs NCC](../../../concepts/ecc-vs-ncc.md)
- Strategic Roadmap: [roadmap](../../../roadmap.md)
- Strategic Decisions: [decisions](../../../decisions/decisions.md)
- Predecessors:
  - [MN-009: Scoped Context Delivery Engine](../mn-009-context-scaffolding/README.md)
  - [MN-010: Iterative Context Working Set Loop](../mn-010-iterative-context-loop/README.md)
  - [MN-011: Scaffolding-Assisted Context Frontier](../mn-011-scaffolding-context-frontier/README.md)
- Successors:
  - [MN-013: Backtracking & Error Self-Correction](../../../roadmap.md#mn-013--backtracking--error-self-correction)
  - [MN-Final: Stateful Simulated Microworld Evolution](../../../roadmap.md#north-star-horizon-mn-final--stateful-simulated-microworld-evolution)

---

## 1. Problem Statement

Across MN-009, MN-010, and MN-011, Mộng Nhiễm established the empirical foundation of the Substrate Expansion paradigm:
1. Small language models (<4B) collapse when forced to evaluate long unconstrained context ($>8\text{k}$ tokens), but achieve 100% accuracy and sub-second inference when native context forward passes are strictly bounded to an optimal working set $B^* \approx 512$ tokens.
2. The iterative context coordinator (MN-010) successfully enabled multi-hop dependency resolution ($A \rightarrow B \rightarrow C$) under a passive, read-only action grammar (`ACTION: FETCH <target>`).

However, transitioning from static lookup to stateful cognitive agency exposes a critical capability gap:
- **Passive vs Active Interaction:** Real-world problem solving and simulated world evolution require active tool manipulation (`READ`, `INSPECT`, `DISPATCH`) that produces environmental side-effects, state transitions, and structured observations.
- **Context Pollution vs State Persistence:** If past action histories, intermediate tool outputs, and environment states are accumulated directly inside the prompt context, the context quickly explodes beyond the 512-token capacity frontier, triggering attention degradation and format drift. Conversely, if history is aggressively pruned, the model suffers from state amnesia across consecutive turns.

To resolve this dilemma, the cognitive substrate requires a **Dual-Tier Hierarchical Memory Architecture**:
- **L1 (Ephemeral Working Set):** Prompt context strictly bounded to $\le 512$ tokens, containing only the immediate task query, active entity focus, and the latest observation.
- **L2 (Persistent State Ledger):** Host-managed external store (on disk/memory), maintaining cumulative transaction history, entity state tables, and environment invariants.

Furthermore, MN-012 serves as an explicit **Failure-Isolation Station**: we isolate the challenges of tool calling, argument serialization, and memory synchronization before introducing backtracking algorithms (MN-013) or continuous microworld simulation (MN-Final).

---

## 2. Falsifiable Hypotheses

### Hypothesis 1 ($H_1$): Tool Grammar Reliability & Format Invariance
A deterministic regex-based action grammar (`ACTION: TOOL <tool_name>(<args>)` and `ACTION: RESOLVE <answer>`) achieves $\ge 90\%$ protocol adherence and execution validity on `Qwen3.5-2B-Q4_K_M` across multi-turn dispatch sequences ($T \le 5$ turns), completely preventing conversational preamble drift and JSON syntax collapse.

### Hypothesis 2 ($H_2$): Hierarchical Memory Continuity & State Invariant Preservation
A dual-tier memory partition—decoupling an L1 prompt working set ($\le 512$ tokens) from an L2 host state ledger—preserves $100\%$ state consistency across 5-turn stateful mutation sequences, resolving the target goal without suffering prompt bloat or attention collapse.

### Hypothesis 3 ($H_3$): Directional Pivoting Gate & Failure Isolation
If lightweight models exhibit systematic format collapse or execution hallucination ($> 10\%$ failure rate) under structured tool calling, MN-012 will act as an authoritative failure-isolation boundary to trigger an architectural pivot (e.g., transition to GBNF-constrained decoding or host-directed tool scaffolding) before escalating complexity to MN-013 (Backtracking) or MN-Final (Microworld).

---

## 3. Scope & Non-Goals

### In Scope
1. **Primary Subject:** Canonical evaluation on `Qwen3.5-2B-Q4_K_M.gguf`.
2. **Tool Execution Engine:** Deterministic host-side tool contracts:
   - `READ`: Fetch targeted document or code entity segment.
   - `INSPECT`: Query specific property/field from external registry.
   - `DISPATCH`: Execute state mutation or environment transition.
   - `RESOLVE`: Conclude multi-turn execution with ground-truth answer.
3. **Dual-Tier Memory Manager:**
   - L1: Working Set context packager ($\le 512$ tokens, verified by tokenizer).
   - L2: Persistent JSON/SQLite state ledger maintaining multi-turn continuity.
4. **Benchmark Suite:** 30 stateful multi-turn evaluation cases ($T \le 5$ turns).

### Non-Goals
1. **No Autonomous Backtracking or Rollback:** Handling action failure, backtracking across rejected branches, and heuristic recovery is strictly reserved for MN-013.
2. **No Unconstrained Open-World Simulation:** Full microworld physics and long-horizon evolution ($T \ge 20-50$) are reserved for MN-Final.
3. **Zero Model Weight Modification:** No fine-tuning, LoRA adapters, or internal attention modifications. The model remains a frozen black box.
4. **No Premature Promotion:** Prototype code remains within `research/experiments/prototypes/mn-012-hierarchical-tool-memory/` until formal Gate D disposition review.
