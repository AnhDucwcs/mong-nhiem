# MN-011 Gate A: Charter & Scientific Hypothesis

## Context & Navigation

- Canonical Research Base: [00-mong-nhiem](../../../00-mong-nhiem.md)
- System Architecture: [architecture](../../../concepts/architecture.md)
- Conceptual Taxonomy: [ECC vs NCC](../../../concepts/ecc-vs-ncc.md)
- Roadmap: [roadmap](../../../roadmap.md)
- Predecessors:
  - [MN-003: Effective Context Capacity](../mn-003-effective-context-capacity/README.md) (Raw context capacity baseline)
  - [MN-009: Scoped Context Delivery Engine](../mn-009-context-scaffolding/README.md) (Single-shot knapsack scaffolding)
  - [MN-010: Iterative Context Working Set Loop](../mn-010-iterative-context-loop/README.md) (Iterative working set coordinator)

---

## 1. Problem Statement

Milestone **MN-003** established that lightweight open-weights language models (<4B parameters) experience catastrophic performance degradation under raw, direct-attention context scaling:
- On State Tracking (ECC-006), accuracy collapsed from 66.7% at 512 tokens to 16.7% at $\ge 2,048$ tokens and 0% at 8,192 tokens.
- On Causal Reasoning (ECC-007), long context introduced non-monotonic false positive anomalies at 8k tokens.
- Across all tasks, runtime latency scaled quadratically ($O(N^2)$) or super-linearly with context length, exhausting limited edge GPU memory.

Milestones **MN-009** and **MN-010** remedied these bottlenecks by constructing a host-managed context substrate in `src/mong_nhiem/context/`, bounding native forward passes to $\le 512$ tokens and achieving 100% accuracy on scoped retrieval and multi-hop dependency resolution.

However, a fundamental scientific question remains open:
**What is the true empirical capacity frontier of a lightweight model when operating under scaffolding assistance?**

Specifically, if host scaffolding guarantees structured boundaries and prompt sanitization:
1. Does expanding the per-turn knapsack budget $B$ beyond 512 tokens (e.g. to 1024 or 2048 tokens) enable superior reasoning on information-dense problems, or does it trigger attention dilution even with structured inputs?
2. Does host scaffolding provide complete immunity against the long-context causal degradation observed in ECC-007?
3. What is the mathematical relationship between fed context, utilized context, and reasoning outcome across model families (`Qwen3.5-2B`, `Llama-3.2-3B`, `Qwen3-4B`)?

---

## 2. Falsifiable Hypotheses

Milestone MN-011 evaluates three primary falsifiable hypotheses:

### Hypothesis 1: The Scaffolding Budget Inverted-U ($H_1$)
Downstream task accuracy across complex multi-variable reasoning exhibits an inverted-U or saturated plateau with respect to per-turn budget $B \in \{256, 512, 1024, 2048\}$:
- Expanding $B$ from 256 to 512 yields a statistically significant accuracy increase ($\Delta \ge +25\%$).
- Expanding $B$ from 512 to 1024 or 2048 yields diminishing or negative returns ($\Delta \le 0\%$), while increasing mean inference latency by $\ge 2.0\times$.
- **Falsification Condition:** If $B = 2048$ achieves a statistically significant accuracy gain ($\ge +15\%$) over $B = 512$ without attention distraction, $H_1$ is rejected.

### Hypothesis 2: Causal Reasoning Scaffolding Immunity ($H_2$)
When applied to matched multi-hop causal reachability graphs across 16k-token documents (inheriting the ECC-007 test suite), scaffolding-assisted context extraction completely eliminates raw-context false positives and achieves $\ge 95\%$ accuracy across all scale tiers ($512, 2\text{k}, 8\text{k}, 16\text{k}$).
- **Falsification Condition:** If scaffolding-assisted causal reasoning drops below $85\%$ at 8k or 16k context, $H_2$ is rejected.

### Hypothesis 3: Context Conversion Efficiency Superiority ($H_3$)
Context conversion efficiency $\eta = \frac{\text{Salient Tokens Utilized}}{\text{Prompt Tokens Injected}}$ is maximized under constrained scaffolding budgets ($B \le 512$), proving that small models achieve higher cognitive utility per FLOP under constrained, host-curated context windows than under expanded raw context windows.
- **Falsification Condition:** If unconstrained raw context ($16\text{k}$) exhibits equal or higher conversion efficiency than scoped scaffolding ($\le 512$), $H_3$ is rejected.

---

## 3. Scope & Non-Goals

### In Scope
- Re-evaluating ECC-006 (State Tracking) and ECC-007 (Causal Reasoning) under the production `src/mong_nhiem/context/` substrate.
- Parametric budget scaling evaluation across $B \in \{256, 512, 1024, 2048\}$ tokens.
- Cross-model comparative evaluation across `Qwen3.5-2B`, `Llama-3.2-3B`, and `Qwen3-4B`.
- Formal definition and empirical measurement of the Context Conversion Chain ($\text{Theoretical} \rightarrow \text{Fed} \rightarrow \text{Accessed} \rightarrow \text{Utilized} \rightarrow \text{Outcome}$).

### Non-Goals
- No model fine-tuning, LoRA training, or weight alteration.
- No modifications to the production package `src/mong_nhiem/` during the experimental phase.
- No unbounded agentic loop extensions (preserves the $\le 3$ turn circuit breaker invariant established in MN-010).
