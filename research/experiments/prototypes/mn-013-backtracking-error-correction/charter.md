# MN-013 Gate A: Charter & Scientific Hypotheses

## Context & Navigation
- Canonical Knowledge Base: [00-mong-nhiem](../../../00-mong-nhiem.md)
- System Architecture: [architecture](../../../concepts/architecture.md)
- Conceptual Taxonomy: [ECC vs NCC](../../../concepts/ecc-vs-ncc.md)
- Strategic Roadmap: [roadmap](../../../roadmap.md)
- Strategic Decisions: [decisions](../../../decisions/decisions.md)
- Predecessors:
  - [MN-010: Iterative Context Working Set Loop](../mn-010-iterative-context-loop/README.md)
  - [MN-011: Scaffolding-Assisted Context Frontier](../mn-011-scaffolding-context-frontier/README.md)
  - [MN-012: Hierarchical Tool & Memory Integration](../mn-012-hierarchical-tool-memory/README.md)
- Successors:
  - [MN-018: Stateful Simulated Microworld Evolution](../../../roadmap.md#mn-018--stateful-simulated-microworld-evolution)

---

## 1. Problem Statement

Empirical results from [MN-012 Gate C](../mn-012-hierarchical-tool-memory/gate-d-disposition-review.md) revealed an asymmetric capability landscape for small language models (<4B):
1. **Low-Level Tool Syntax is Solved:** With minimalist grounding exemplars, `Qwen3.5-2B-Q4_K_M` attained $100\%$ action grammar adherence (`ACTION: READ|INSPECT|DISPATCH|RESOLVE`) and $100\%$ AST syntax recovery on isolated mutation tasks.
2. **High-Level Trajectory Navigation Collapses:** Under branching environments where actions encounter environmental rejections (e.g. insufficient account balance, locked state flag, invalid precondition), the 2B model suffers from **Failure Mode 3: Goal Divergence & Horizon Jumping**. Lacking native lookahead or self-correction, the model either loops the rejected action or prematurely outputs `ACTION: RESOLVE` on incomplete state.
3. **The History Accumulation Dilemma:** In naive multi-turn agent frameworks, failed steps and error stack traces are appended directly into the prompt history. In small models, this causes exponential context inflation ($> 512$ tokens), diluting the task objective and triggering attention degradation.

To achieve robust autonomous behavior without modifying model weights or inflating context, Mộng Nhiễm requires a **Host-Directed Backtracking & Context Rewind Architecture**:
- **L2 Host-Side State Checkpoints:** The host maintains a bounded snapshot stack ($S_0, S_1, \dots, S_t$) in host memory (0 tokens in prompt context).
- **Context Rewind (Zero-Bloat Rollback):** Upon tool failure or dead-end detection, the host rolls the environment back to $S_{t-1}$ and surgically removes the rejected turn from the model's working context.
- **Negative Action Masking:** The host injects a compact constraint directive (`"REJECTED: <action>. Reason: <err>. Do NOT repeat."` $\approx 15$ tokens) into the subsequent turn prompt.
- **Phase-Gating Constraint:** Host blocks premature `ACTION: RESOLVE` if the target state predicate has not been satisfied, forcing the model to exhaust exploration.

---

## 2. Falsifiable Hypotheses

### Hypothesis 1 ($H_1$): Reversible Execution & Deadlock Recovery
Host-directed state rollback combined with negative action masking will enable `Qwen3.5-2B-Q4_K_M` to recover from environmental rejections and reach target task resolution with $\ge 80\%$ success on benchmark cases containing injected trap states, compared to $0\%$ under naive forward-only execution.

### Hypothesis 2 ($H_2$): Zero Context Bloat Invariant
Across multi-turn recovery sequences involving up to 3 backtracking operations ($T \le 7$ turns), 100% of generated per-turn prompts will strictly satisfy the token budget constraint:
$$\text{TokenCount}(\text{turn\_prompt}) \le 512$$
Context Rewind prevents prompt degradation by discarding aborted branch tokens from working memory.

### Hypothesis 3 ($H_3$): Deterministic Infinite Loop Suppression
Maintaining a host-side set of rejected actions $\mathcal{A}_{\text{rejected}}^{(S_t)}$ for each state node $S_t$ will deterministically reduce repetitive action loops to $0\%$ across all evaluation runs.

---

## 3. Scope & Non-Goals

### In Scope
1. **Primary Subject:** Canonical evaluation on `Qwen3.5-2B-Q4_K_M.gguf`.
2. **Host-Directed Checkpoint Stack:** L2 in-memory snapshot manager supporting `checkpoint()`, `rollback()`, and bounded stack depth ($K_{\max} = 3$).
3. **Context Rewind Engine:** Host context manager that discards rejected turn exchanges and substitutes a 15-token negative action mask.
4. **Phase-Gating Interceptor:** Host validator that rejects premature `ACTION: RESOLVE` calls when environment invariants remain unfulfilled.
5. **Evaluation Corpus:** 60 stateful cases with injected dead-ends across AST mutation, resource ledger contention, and system configuration dependencies.

### Non-Goals
1. **No Fine-Tuning or Model Weight Modification:** Model weights remain strictly frozen. The model functions as a stateless transition policy.
2. **No Combinatorial Tree-Search (MCTS):** MN-013 evaluates bounded linear backtracking ($K \le 3$), not full heuristic game-tree search.
3. **No Unconstrained Microworld Physics:** Continuous long-horizon simulation ($T \ge 20-50$) is reserved for MN-018.
4. **No Premature Promotion:** Prototype code remains within `research/experiments/prototypes/mn-013-backtracking-error-correction/` until formal Gate D disposition review.
