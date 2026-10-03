# MN-011 Gate B: Measurement Contract & Evaluation Protocol

## Context & Navigation

- Canonical Research Base: [00-mong-nhiem](../../../00-mong-nhiem.md)
- System Architecture: [architecture](../../../concepts/architecture.md)
- Conceptual Taxonomy: [ECC vs NCC](../../../concepts/ecc-vs-ncc.md)
- Milestone Charter: [MN-011 Gate A Charter](charter.md)
- Benchmark Corpus: [`definition/corpus-v1/cases.jsonl`](definition/corpus-v1/cases.jsonl)
- Execution Runner: [`scripts/mn011_executor.py`](scripts/mn011_executor.py)
- Execution Report: [MN-011 Gate C Execution Report](reports/mn011-execution-report-attempt-0001.md)
- Disposition Review: [MN-011 Gate D Disposition Review](gate-d-disposition-review.md)

---

## 1. Objectives & Measurement Principles

This document freezes the empirical measurement contract for **MN-011: Scaffolding-Assisted Effective Context Frontier**.
The objective is to empirically map the true Effective Context Capacity (ECC) frontier of lightweight language models (<4B parameters) when assisted by the production scaffolding substrate (`mong_nhiem.context`).

All evaluations adhere to four immutable principles:
1. **Model Invariant:** The model is evaluated strictly as an unchanged black-box reasoning engine. Zero fine-tuning, weight modification, or LoRA adaptations.
2. **Hard Token Accounting:** Measurement relies strictly on the official offline `llama-tokenize.exe` binary with `Llama-3.2-3B-Instruct-Q4_K_M.gguf` and `Qwen3.5-2B-Q4_K_M.gguf`.
3. **Hermetic Sandbox Isolation:** All prototype code resides within `research/experiments/prototypes/mn-011-scaffolding-context-frontier/`. The production package `src/mong_nhiem/` remains untouched.
4. **Pre-Run Freeze Authority:** The measurement contract, corpus, and executor script must be frozen in Git before executing any model inference runs.

---

## 2. Evaluation Benchmark Corpus Design (40 Cases)

The evaluation suite comprises 40 deterministic cases across two experimental suites:

### Suite A: Parametric Budget Scaling Frontier (24 Cases)
Evaluates 6 complex multi-entity state integration and dependency reasoning problems across 4 distinct knapsack budget tiers ($B \in \{256, 512, 1024, 2048\}$ tokens):
- $B = 256$: Constrained budget tier (testing lower-bound compression limits).
- $B = 512$: Standard production scaffolding tier (MN-009 / MN-010 baseline).
- $B = 1024$: Expanded working set tier.
- $B = 2048$: Extended working set tier.

### Suite B: Causal Reachability Scaffolding Restoration (16 Cases)
Re-evaluates the frozen ECC-007 causal reachability task across 4 context scale tiers ($512, 2\text{k}, 8\text{k}, 16\text{k}$ tokens):
- 4 cases per tier (2 positive reachability, 2 negative reachability).
- Compares **Arm A (Raw Unassisted Context)** vs **Arm B (Scaffolding-Assisted Context via `slice_graph_by_khop` and `ContextPacker`)**.

---

## 3. Four Frozen Acceptance Support Rules

To qualify for disposition synthesis at Gate D, the execution must evaluate the three frozen Gate A hypotheses against four explicit rules:

### Rule 1: Budget Frontier Scaling Verification ($H_1$)
- **Requirement:** Reasoning accuracy must plateau or peak at $B^* \approx 512$ tokens. Specifically:
  - Expanding $B$ from 256 to 512 must yield a significant accuracy increase ($\ge +20\%$).
  - Expanding $B$ from 512 to 1024 or 2048 must yield non-increasing accuracy ($\Delta \le 0\%$), with mean completion latency increasing by $\ge 1.8\times$.

### Rule 2: Causal Reasoning Scaffolding Restoration ($H_2$)
- **Requirement:** Scaffolding-assisted context delivery (Arm B) must achieve $\ge 93.75\%$ accuracy ($15/16$ or $16/16$) across the ECC-007 causal reachability suite, with zero false positives at 8k/16k context, resolving the raw-context degradation observed in MN-003.

### Rule 3: Hard Token Budget Invariant
- **Requirement:** $100\%$ ($40/40$ cases) of prompts packed by `ContextPacker` must satisfy:
  $$\text{TokenCount}(\text{packed\_prompt}) \le B_{\text{configured}}$$
- **Tolerance:** 0 overflow cases allowed.

### Rule 4: Context Conversion Efficiency Superiority ($H_3$)
- **Requirement:** Context conversion efficiency $\eta = \frac{\text{Salient Tokens Utilized}}{\text{Prompt Tokens Injected}}$ must be strictly higher under $B \le 512$ than under $B \ge 1024$ and raw 16k context:
  $$\eta_{B \le 512} > \eta_{B \ge 1024} > \eta_{\text{raw\_16k}}$$
