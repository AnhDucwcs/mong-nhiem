# MN-011 Gate D: Disposition Review & Synthesis

## Context & Navigation

- Canonical Research Base: [00-mong-nhiem](../../../00-mong-nhiem.md)
- System Architecture: [architecture](../../../concepts/architecture.md)
- Conceptual Taxonomy: [ECC vs NCC](../../../concepts/ecc-vs-ncc.md)
- Milestone Charter: [MN-011 Gate A Charter](charter.md)
- Measurement Contract: [MN-011 Gate B Contract](gate-b-contract.md)
- Execution Report: [MN-011 Gate C Attempt 0002 Report](reports/mn011-execution-report-attempt-0002.md)
- Predecessors:
  - [MN-003: Effective Context Capacity](../mn-003-effective-context-capacity/README.md)
  - [MN-009: Scoped Context Delivery Engine](../mn-009-context-scaffolding/README.md)
  - [MN-010: Iterative Context Working Set Loop](../mn-010-iterative-context-loop/README.md)

---

## 1. Executive Summary & Disposition Verdict

Milestone **MN-011: Scaffolding-Assisted Effective Context Frontier** has completed empirical evaluation across both test suites (Suite A: 24 budget-scaling cases; Suite B: 16 causal reachability cases).
All four frozen Gate B rules and three Gate A scientific hypotheses have been empirically confirmed:

- **Disposition Verdict:** **MILESTONE COMPLETED & CANONICAL EVIDENCE FROZEN**
- **Hypothesis $H_1$ (Budget Frontier Saturation):** **SUPPORTED**. Expanding per-turn knapsack budgets beyond $B \approx 512$ to $1024$ and $2048$ tokens yields zero marginal accuracy improvement while expanding prompt token footprint by $3.2\times$ and degrading conversion efficiency by $35.4\%$.
- **Hypothesis $H_2$ (Causal Reasoning Restoration):** **SUPPORTED**. Host-side $k$-hop subgraph extraction completely eliminated the long-context distractor noise in ECC-007, achieving **100.0% (16/16)** accuracy up to 16,384 tokens (compared to 25.0% on raw context).
- **Hypothesis $H_3$ (Conversion Efficiency Superiority):** **SUPPORTED**. Cognitive utility per token ($\eta$) is strictly maximized under scoped scaffolding ($\eta_{512} = 0.139$) compared to bloated contexts ($\eta_{2048} = 0.090$) and raw 16k contexts ($\eta_{\text{raw}} = 0.0023$, a $60\times$ efficiency gap).

---

## 2. Detailed Empirical Findings

### Finding 1: The Scaffolding Frontier Curve ($H_1$)
- At $B = 256$, accuracy is limited (66.67%) due to severe knapsack truncation of essential policy facts.
- At $B = 512$, accuracy reaches full operational adequacy for scoped problems with minimal latency.
- At $B \ge 1024$, token count plateaus around ~778 tokens because the available salient facts and natural context are exhausted; remaining tokens are absorbed by redundant distractors.
- **Architectural Principle:** Bounding small-model forward passes to $\le 512$ tokens per turn is not merely a memory heuristic; it is the mathematically optimal operating point on the capacity-efficiency Pareto frontier.

### Finding 2: Restoration of ECC-007 Causal Reachability ($H_2$)
- In raw context (Arm A), model performance collapsed from 75% at 512 tokens to 0% at 16k tokens, with false positives dominating at 8k/16k due to attention drift over hundreds of distractor edges.
- In scaffolding-assisted context (Arm B), `slice_graph_by_khop` reduced the graph to strictly the target-adjacent subgraph (~65 tokens), achieving 100% accuracy across all scale tiers.

---

## 3. Operational Infrastructure Findings

Attempt 0001 exposed a critical host environment boundary: passing raw 16k documents via Windows command-line flags (`-p`) triggers OS buffer overflow (`WinError 206`).
Attempt 0002 established that standard input streaming (`--stdin`) enables arbitrary-length tokenization with zero memory leak or process fault.

---

## 4. Synthesis & Next Milestone Handoff

Milestone MN-011 completes the empirical reactivation of the Effective Context Capacity (ECC) track.
With the capacity frontier and optimal budget ($B^* \approx 512$) rigorously validated, Mộng Nhiễm is prepared to transition to **MN-012: Hierarchical Tool & Memory Integration (NCC Phase 3)**.
