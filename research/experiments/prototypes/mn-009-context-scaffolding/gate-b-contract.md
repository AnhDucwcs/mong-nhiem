# MN-009 Gate B: Measurement Contract & Evaluation Protocol

## Context & Navigation

- Canonical Research Base: [00-mong-nhiem](../../../00-mong-nhiem.md)
- System Architecture: [architecture](../../../concepts/architecture.md)
- Current Milestone State: [current-state](../../../current-state.md)
- Parent Milestone Charter: [MN-009 Gate A Charter](charter.md)
- Execution Runner: [`scripts/mn009_executor.py`](scripts/mn009_executor.py)
- Execution Report: [MN-009 Gate C Execution Report](reports/mn009-execution-report.md)
- Disposition Review: [MN-009 Gate D Disposition Review](gate-d-disposition-review.md)

---

## 1. Objectives & Measurement Principles

This document freezes the empirical measurement contract for **MN-009: Scoped Context Delivery Engine**.
The objective is to mathematically and empirically verify that host-side context scaffolding can compress extensive raw document streams ($2\text{k} - 32\text{k}$ tokens) down to a strict $\le 512$-token budget without semantic breakdown, broken syntax trees, or temporal inconsistency.

All evaluations adhere to three core principles:
1. **Hard Token Accounting:** Measurement relies strictly on the official offline `llama-tokenize.exe` binary with `Llama-3.2-3B-Instruct-Q4_K_M.gguf`.
2. **Hermetic Sandbox Isolation:** All prototype code resides within `research/experiments/prototypes/mn-009-context-scaffolding/`. The production package `src/mong_nhiem/` remains closed until Gate D approval.
3. **Deterministic Reproducibility:** The benchmark corpus is generated via fixed seeds, authenticated with SHA-256 digests in [`definition/corpus-v1/manifest.json`](definition/corpus-v1/manifest.json).

---

## 2. Evaluation Benchmark Corpus Design (30 Cases)

The evaluation suite comprises 30 independent cases (`mn009-case-0001` through `mn009-case-0030`), covering 5 context size tiers ($2\text{k}, 4\text{k}, 8\text{k}, 16\text{k}, 32\text{k}$ tokens) across 3 practical data structures:

| Problem Domain | Case Count | Scale Distribution | Core Technical Invariants Evaluated |
| :--- | :---: | :---: | :--- |
| **Domain A: Narrative & Event Stream (`text_stream`)** | 10 | 2k: 2, 4k: 2, 8k: 2, 16k: 2, 32k: 2 | - **Anchor-and-Spoke:** Preserves the opening 60-token executive anchor + original chronological order.<br>- **Causal Timeline:** Compresses multi-entity events into causal state updates.<br>- Eliminates pronoun detachment ("he", "the system") common in standard vector RAG. |
| **Domain B: Knowledge Graphs & State Tables (`graph_table`)** | 10 | 2k: 2, 4k: 2, 8k: 2, 16k: 2, 32k: 2 | - **Invariant Temporal Check:** $100\%$ active entities must have an explicit Latest State.<br>- **$k$-Hop Subgraph BFS ($k \le 2$):** Prunes 500-node networks down to $\le 8$ relevant nodes in $O(V+E)$.<br>- **Shortest Path Bridging:** Guarantees connection preservation between target entities.<br>- **Column/Row Projection:** Filters 50-row tables down to exact queried records. |
| **Domain C: Software Codebase AST (`code_ast`)** | 10 | 2k: 2, 4k: 2, 8k: 2, 16k: 2, 32k: 2 | - **AST Skeletoning:** Stubs 25 auxiliary functions to signatures + inferred returns + `...`.<br>- **Adaptive Inlining:** Retains complete function bodies if short ($\le 5$ lines).<br>- **Call Closure Pruning:** Omits uncalled helper functions via `omit_uncalled=True`.<br>- **Syntax Integrity:** Code must pass `ast.parse` with zero `SyntaxError`. |

---

## 3. Five Frozen Acceptance Support Rules

To qualify for promotion recommendation at Gate D, the execution must satisfy all 5 frozen rules:

### Rule 1: Hard Token Budget Ceiling
- **Requirement:** $100\%$ ($30/30$ cases) of packed outputs measured by `llama-tokenize.exe` must satisfy:
  $$\text{TokenCount}(\text{packed\_context}) \le 512$$
- **Tolerance:** 0 overflow cases allowed (Zero Overflow Tolerance).

### Rule 2: Boundary & AST Syntax Integrity
- **Requirement:**
  - 0 sentences cut midway (must end on valid punctuation or paragraph break).
  - $100\%$ of code outputs in Domain C must be valid Python code (`ast.parse` succeeds).

### Rule 3: Target Fact Salience Recall
- **Requirement:** At least $28/30$ cases ($93.3\%$) must retain target factual queries, latest states, or logic in the packed 512-token context.

### Rule 4: Host CPU Packaging Latency Gate
- **Requirement:** Packaging latency on host CPU must satisfy:
  $$\text{MeanLatency}_{\text{CPU}} < 15.0\text{ ms}$$
  $$\text{MaxLatency}_{\text{CPU}} < 35.0\text{ ms} \quad (\text{for 32k tokens})$$

### Rule 5: Prefix Cache Invariant
- **Requirement:** Uniform system header structure across cases to guarantee KV Cache reuse on `llama-server.exe`:
  $$\text{CacheHitRate} = 100\%$$

---

## 4. Benchmark Case Schema

Each case in [`definition/corpus-v1/cases.jsonl`](definition/corpus-v1/cases.jsonl) follows the strict schema:
```json
{
  "case_id": "mn009-case-0001",
  "category": "text_stream | graph_table | code_ast",
  "raw_token_count": 8192,
  "raw_content": "... [Complete unstructured text, code, or graph] ...",
  "query": "What is the final condition and location of Operative Alex?",
  "target_fact": "Operative Alex is SECURED at Sector-4.",
  "required_entities": ["Alex"],
  "oracle_answer": "SECURED at Sector-4"
}
```

---

## 5. Rejection Boundaries (Automatic Veto)

A milestone is automatically rejected at Gate D if any of the following occur:
1. Any case exceeds 512 tokens after packaging.
2. A `SyntaxError` or broken AST is produced in sliced code.
3. Violation of `Invariant Temporal Check`: A queried entity lacks an explicit latest state.
4. Salience recall falls below $28/30$.
