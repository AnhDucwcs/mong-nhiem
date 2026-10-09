# MN-015: Dynamic Affordance Constrained Decoding & Dual-Layer Steering

## Status: Completed & Closed — Dual-Layer Affordance Steering Standard Proven

> [!NOTE] Strategic Continuity & Empirical Success
> This milestone has been completed and verified under **Gate C execution** and closed under **Gate D disposition review** ([`gate-d-disposition-review.md`](gate-d-disposition-review.md)).
> - **Overall Task Completion:** **100.0% (60/60 PASS)** on real model inference (`Qwen3.5-2B-Q4_K_M.gguf`).
> - **Domain C Resolution:** Surged from $15.0\%$ to **100.0% (20/20 PASS)** (+85.0% absolute gain).
> - **Trap Recovery:** **100.0% (30/30 PASS)** with 0 deadlock cycles (down from 15 in MN-014).
> - **Parse Failures:** Exactly **0.0% (0/216 turns)**.
> - **Hard Working Budget:** **100% compliance** ($\le 512$ tokens, Max: 396 tokens, Mean: 318.5 tokens).
> - **Execution Report:** [`reports/mn015-execution-report.md`](reports/mn015-execution-report.md).

---

## 1. Problem Statement & Empirical Origin

In **MN-014**, Mộng Nhiễm proved that Native GBNF (Grammar-Based Context-Free Grammar) logit masking at the `llama-server` engine layer eliminates $100\%$ of syntax and formatting failures ($0.0\%$ parse errors across 197 turns) on a frozen lightweight model (`Qwen3.5-2B-Q4_K_M`), driving overall task completion from $33.3\%$ to $55.0\%$.

However, Gate D disposition review established a decisive architectural boundary:
**Static Grammar Solves Syntax, but Cannot Solve Combinatorial State Search (Failure Mode 2).**

- Under static GBNF (`identifier ::= [a-zA-Z0-9_]+`), the grammar allows *any* alphanumeric string.
- In complex stateful environments (Domain C: System Registry with mutual exclusion locks), when an action is rejected and state rolled back, the model continues generating syntactically perfect action directives targeting locked or unavailable services.
- This induces **Multi-Branch Search Exhaustion**: the 2B model exhausts its turn limit (7 turns) attempting syntactically valid yet semantically dead-end actions, resulting in only $15.0\%$ task completion on Domain C.

---

## 2. Selected Architecture: Dual-Layer Affordance Steering

To bridge the remaining performance gap from $55.0\% \rightarrow \ge 85.0\%$, MN-015 unites two complementary mechanisms into a unified **Dual-Layer Affordance Steering** architecture:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        Host State Engine (L2 RAM)                      │
│                Calculates Active Affordances at Turn t                 │
│         Affordances(S_t) = {svc_worker_b_51, svc_gateway_50, ...}      │
└───────────────────┬────────────────────────────────┬───────────────────┘
                    │                                │
         (1) Bounded Prompt Injection     (2) Dynamic GBNF Compilation
                    │                                │
                    ▼                                ▼
┌───────────────────────────────────────┐ ┌──────────────────────────────┐
│  L1 Working Memory Context (<=512 tok)│ │ Engine Logit Mask (llama.cpp)│
│  "Affordances: [svc_worker_b_51, ...]"│ │ valid-target ::= "svc_b"...  │
│  ==> Biases Self-Attention Priors     │ │ ==> Hard Logit Ceiling (-inf)│
└───────────────────┬───────────────────┘ └──────────────┬───────────────┘
                    │                                    │
                    └─────────────────┬──────────────────┘
                                      ▼
                      ┌───────────────────────────────┐
                      │    Qwen3.5-2B (Frozen Engine) │
                      │  Deterministic State Mutation │
                      └───────────────────────────────┘
```

### Layer 1: Prompt Attention Prior (L1 Working Context $\le 15-20$ tokens)
- The host inspects the current L2 state snapshot $S_t$ and extracts the list of currently unlocked, executable affordances.
- A single, compact line is injected into the turn prompt:
  ```text
  Available Affordances: [activate:svc_worker_b_51, set_config:svc_gateway_50]
  ```
- **Cognitive Purpose:** Seeds the model's self-attention heads with the exact valid token sequences. Without this prompt prior, masking out the model's top-1 preference at the logit layer forces sampling from the distribution tail, causing *Perplexity Distortion* (unnatural, stuttering token emissions).

### Layer 2: Dynamic Engine Logit Masking (Runtime GBNF CFG)
- Concurrently, the host compiles a dynamic GBNF grammar specifically for that turn's completion request:
  ```gbnf
  root ::= action ("\n" | "")
  action ::= "ACTION: " ( read-action | inspect-action | dispatch-action | resolve-action )
  valid-service ::= "svc_worker_b_51" | "svc_gateway_50"
  dispatch-action ::= "DISPATCH activate_service " valid-service
  ...
  ```
- **System Purpose:** Provides a hard mathematical boundary at the logit level ($-\infty$ probability for locked services). Even if the model exhibits attention drift, it is mathematically impossible to emit an illegal action.

---

## 3. Adherence to the Ponytail Principle (Why This Is Minimal)

While combining prompt guidance and logit masking might appear redundant at first glance, it is the **minimal orthogonal solution** that addresses real execution mechanics:

1. **Prompt Only:** Prone to small-model attention drift and hallucination (MN-012/MN-013 evidence).
2. **Logit Masking Only:** Prone to perplexity distortion and tail sampling collapse when the model has zero attention prior.
3. **Dual-Layer Synergy:**
   - Both layers derive from the exact same host state function: `get_active_affordances(env)`.
   - Requires zero new dependencies and zero extra model forward passes.
   - Total prompt cost: $\approx 15-20$ tokens (well within the $\le 512$-token hard ceiling).
   - Host compilation overhead: $< 0.1\text{ ms}$ CPU string formatting.

---

## 4. Objectives & Target Acceptance Criteria

- **Target Overall Task Completion:** $\ge 85.0\%$ across the canonical 60-case benchmark ($51/60$ cases resolved).
- **Target Domain C Resolution:** Surge from $15.0\%$ to $\ge 80.0\%$ on system registry configurations.
- **Target Trap Recovery:** $\ge 85.0\%$ across all 30 dead-end traps.
- **Zero Parse Failures:** Maintain $0.0\%$ CFG parse errors.
- **Hard Working Budget:** Maintain $100\%$ turns $\le 512$ tokens.
- **Milestone Success Gate:** Qualify for formal Gate D promotion into `src/mong_nhiem/context/`.

---

## 5. Strategic Predecessors & Successors

- **Predecessor:** [MN-014: Grammar-Constrained Decoding](../mn-014-grammar-constrained-decoding/README.md) (Standard GBNF logit sampling established, ADR-0014).
- **Successor:** [MN-Final: Stateful Simulated Microworld Evolution](../../../roadmap.md#north-star-horizon-mn-final--stateful-simulated-microworld-evolution) (Long-horizon world continuity over $T \ge 20-50$ steps).
