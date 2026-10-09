# MN-015 Gate A: Charter & Scientific Hypotheses

## Context & Navigation
- Canonical Knowledge Base: [00-mong-nhiem](../../../00-mong-nhiem.md)
- System Architecture: [architecture](../../../concepts/architecture.md)
- Conceptual Taxonomy: [ECC vs NCC](../../../concepts/ecc-vs-ncc.md)
- Strategic Roadmap: [roadmap](../../../roadmap.md)
- Strategic Decisions: [decisions](../../../decisions/decisions.md)
- Predecessors:
  - [MN-013: Backtracking & Error Self-Correction](../mn-013-backtracking-error-correction/README.md)
  - [MN-014: Grammar-Constrained Decoding](../mn-014-grammar-constrained-decoding/README.md)
- Successors:
  - [MN-Final: Stateful Simulated Microworld Evolution](../../../roadmap.md#north-star-horizon-mn-final--stateful-simulated-microworld-evolution)

---

## 1. Problem Statement

In **MN-014**, Mộng Nhiễm established Native GBNF Grammar-Constrained Decoding at the engine layer (`llama-server`), definitively proving that engine-level logit masking eliminates $100\%$ of syntactic parsing and formatting failures ($0.0\%$ parse errors across 197 turns) and elevates overall task resolution from $33.3\%$ to $55.0\%$.

However, Gate D disposition review identified a critical fundamental limit:
**Static Grammar Solves Syntax, but Cannot Solve Combinatorial State Search (Failure Mode 2).**

- Under static GBNF (`identifier ::= [a-zA-Z0-9_]+`), the grammar allows *any* alphanumeric token string.
- In complex multi-branch environments (Domain C: System Registry with mutual exclusion locks), when a primary action branch fails and state rolls back, unassisted greedy decoding generates syntactically valid yet semantically dead-end action candidates (e.g., repeatedly targeting locked or offline services).
- This induces **Multi-Branch Search Exhaustion**: the 2B model exhausts its maximum turn budget ($T=7$) attempting syntactically valid yet illegal actions, collapsing Domain C task completion to only $15.0\%$ ($3/20$ cases).

**MN-015 introduces Dual-Layer Affordance Steering:**
1. **Layer 1 (Prompt Attention Prior):** Host provides a compact ($\le 15-20$ tokens) list of active affordances in the working observation block, seeding attention heads so $P(\text{affordance}) \gg 0$ to prevent *Perplexity Distortion*.
2. **Layer 2 (Dynamic Engine Logit Masking):** Host dynamically compiles a minimal Context-Free Grammar tailored per turn from the active environment state $S_t$, setting logits of inactive actions to $-\infty$.
3. **Ponytail Minimality:** Both layers are generated from a single Host function `get_active_affordances(env, state)` with $O(1)$ amortized complexity, zero new dependencies, and $< 0.1\text{ ms}$ CPU overhead.

---

## 2. Falsifiable Hypotheses

### Hypothesis 1 ($H_1$): Dynamic Affordance Search Resolution ($\ge 85\%$)
Constraining `Qwen3.5-2B-Q4_K_M` with Dual-Layer Affordance Steering will eliminate illegal branch exploration, lifting overall task completion across the canonical 60-case benchmark from $55.0\%$ (MN-014) to:
$$\text{TaskCompletionRate}(\text{MN-015}) \ge 85.0\% \quad (51/60 \text{ cases})$$
and surging Domain C (System Registry) completion from $15.0\%$ ($3/20$) to:
$$\text{DomainC\_Completion} \ge 80.0\% \quad (16/20 \text{ cases})$$

### Hypothesis 2 ($H_2$): Perplexity Distortion Suppression via Dual-Layer Synergy
Providing the explicit prompt affordance prior prevents out-of-distribution logit clipping and tail-sampling collapse, keeping mean turn latency $\le 500\text{ ms}$, eliminating repetitive stuttering token generation, and preserving sub-second execution speed.

### Hypothesis 3 ($H_3$): Invariant Preservation & Zero Grammar Leaks
Dynamic per-turn GBNF grammar generation maintains $100\%$ syntactic validity, achieving:
$$\text{ParseFailureRate} = 0.0\%$$
with $100\%$ of turn prompts strictly adhering to the working set memory budget ($\le 512$ tokens).

---

## 3. Scope & Non-Goals

### In Scope
1. **Primary Subject:** Canonical evaluation on `Qwen3.5-2B-Q4_K_M.gguf`.
2. **Affordance Engine:** Deterministic host-side affordance calculation filtering out locked services, depleted resources, and previously rejected actions.
3. **Dynamic GBNF Compiler:** High-speed string compiler formatting per-turn BNF grammar constraints passed to `llama-server.exe` `/completion`.
4. **Dual-Track Protocol:** Track 1 (Deterministic Simulator, 60 cases) + Track 2 (Real Model Inference, 60 cases).

### Non-Goals
1. **No Model Fine-Tuning:** The weights of `Qwen3.5-2B` remain frozen and unmodified.
2. **No Unbounded Agentic Loops:** Retains hard $\le 7$ turn circuit breaker ceiling and duplicate cycle detection.
3. **No Heavy External Graph Libraries:** 100% Python Standard Library implementation.
