# MN-010 Gate B: Measurement Contract & Evaluation Protocol

## Context & Navigation

- Canonical Research Base: [00-mong-nhiem](../../../00-mong-nhiem.md)
- System Architecture: [architecture](../../../concepts/architecture.md)
- Conceptual Taxonomy: [ECC vs NCC](../../../concepts/ecc-vs-ncc.md)
- Parent Milestone Charter: [MN-010 Gate A Charter](charter.md)
- Benchmark Corpus: [`definition/corpus-v1/cases.jsonl`](definition/corpus-v1/cases.jsonl)
- Execution Runner: [`scripts/mn010_executor.py`](scripts/mn010_executor.py)
- Execution Report: [MN-010 Gate C Execution Report](reports/mn010-execution-report.md)
- Disposition Review: [MN-010 Gate D Disposition Review](gate-d-disposition-review.md)

---

## 1. Objectives & Measurement Principles

This document freezes the empirical measurement contract for **MN-010: Iterative Context Working Set Loop**.
The objective is to empirically verify that host-managed iterative context dispatch allows lightweight language models (<4B parameters) to resolve sequential multi-hop dependencies across large knowledge corpora without exceeding per-turn working set token bounds ($\le 512$ tokens), without infinite loop divergence, and without fine-tuning or weight modification.

All evaluations adhere to four core principles:
1. **Black-Box Model Invariant:** The model is evaluated strictly as an external reasoning agent; zero internal attention weights or parameters are modified.
2. **Hard Token Accounting:** Token counts for every turn working set are verified via `llama-tokenize.exe` with `Llama-3.2-3B-Instruct-Q4_K_M.gguf`.
3. **Hermetic Sandbox Isolation:** Prototype implementation remains strictly within `research/experiments/prototypes/mn-010-iterative-context-loop/` prior to Gate D review.
4. **Deterministic Reproducibility:** Benchmark generation uses fixed seeds, with cryptographic verification via SHA-256 digests in [`definition/corpus-v1/manifest.json`](definition/corpus-v1/manifest.json).

---

## 2. Benchmark Corpus Design (30 Multi-Hop Cases)

The evaluation suite comprises 30 deterministic multi-hop reasoning cases across 3 domains:

| Problem Domain | Case Count | Hop Depth | Core Technical Invariant Evaluated |
| :--- | :---: | :---: | :--- |
| **Domain A: Codebase Dependency AST (`code_ast`)** | 10 | 2 - 3 hops | Transitive call chains (`entry_func -> helper_a -> target_b`). Single-shot packs only caller; iterative loop fetches downstream helpers on demand to resolve return values. |
| **Domain B: Knowledge Graph Paths (`knowledge_graph`)** | 10 | 2 - 3 hops | Multi-hop relational traversal (`Entity_A -[rel_1]-> Entity_B -[rel_2]-> Entity_C`). Evaluates whether iterative dispatch retrieves intermediate nodes before reaching target property. |
| **Domain C: System State & Config Tables (`state_table`)** | 10 | 2 - 3 hops | Indirected system registry tables (`Service -> ConfigKey -> SecretVault -> SecretValue`). Evaluates tabular row projection and key resolution across isolated state blocks. |

---

## 3. Comparative Evaluation Arms

- **Arm A (Single-Shot Scaffolding Baseline):** Context delivery as defined in MN-009, packing initial query and 1st-hop context into a single $\le 512$-token window. Because 2nd- and 3rd-hop facts are unobserved at initial dispatch, single-shot evaluation must guess or hallucinate downstream values.
- **Arm B (Iterative Working Set Loop - MN-010):** The model receives initial query and entry working set. It emits `ACTION: FETCH <target>` to pull next-hop context or `ACTION: RESOLVE <answer>` when confident. The host coordinator checks bounds, retrieves the target, repacks the working set ($\le 512$ tokens), and dispatches the next turn.

---

## 4. Five Frozen Acceptance Rules

To qualify for promotion recommendation at Gate D, the execution must satisfy all 5 frozen rules:

### Rule 1: Multi-Hop Resolution Efficacy
- **Requirement:** Arm B (Iterative Coordinator) must achieve $\ge 85\%$ accuracy ($26/30$ cases resolved correctly), while Arm A (Single-Shot Baseline) achieves $< 40\%$ accuracy due to horizon blindness.

### Rule 2: Hard Per-Turn Token Budget Ceiling
- **Requirement:** Exactly $100\%$ of generated turn prompts must satisfy:
  $$\text{TokenCount}(\text{turn\_prompt}) \le 512$$
- **Tolerance:** 0 overflow instances across all turns and cases.

### Rule 3: Loop Boundedness & Circuit Breaker Invariant
- **Requirement:**
  - $100\%$ of cases must terminate within $\le 3$ turns (`max_turns = 3`).
  - Zero runaway loops or non-terminating executions.
  - Repeated target fetches must trip the circuit breaker with `CYCLE_DETECTED`.

### Rule 4: Action Protocol Conformance
- **Requirement:** $100\%$ of model-coordinator interactions must parse deterministically using the defined flat regex grammar:
  - `ACTION: FETCH <target>`
  - `ACTION: RESOLVE <answer>`

### Rule 5: Host Coordination Latency
- **Requirement:** Host-side CPU coordination overhead (parsing + retrieval + packing) must average $< 50\text{ ms}$ per turn, and total execution latency must remain $< 1.5\text{s}$ per case.
