# MN-014 Gate B: Measurement Contract & Evaluation Protocol

## Context & Navigation
- Canonical Knowledge Base: [00-mong-nhiem](../../../00-mong-nhiem.md)
- System Architecture: [architecture](../../../concepts/architecture.md)
- Parent Milestone Charter: [MN-014 Gate A Charter](charter.md)
- Primary Model: `Qwen3.5-2B-Q4_K_M.gguf` on local `llama.cpp` runtime
- Benchmark Corpus: `definition/corpus-v1/cases.jsonl` (Inherited from MN-013, 60 cases)

---

## 1. Objectives & Measurement Principles

This contract establishes the empirical evaluation protocol for **MN-014: Grammar-Constrained Decoding & Structured Cognitive Routing**.
The primary objective is to prove that native GBNF grammar constraints at the `llama-server` engine layer eliminate formatting token collapses and punctuation brittleness, enabling `Qwen3.5-2B` to achieve $\ge 85\%$ end-to-end task completion when integrated with the MN-013 host backtracking architecture.

All measurements must adhere to five frozen scientific principles:
1. **Black-Box Invariant:** `Qwen3.5-2B-Q4_K_M` remains strictly frozen (`temperature=0.0`, greedy single-pass). Logit constraints are applied dynamically by `llama-server` via the standard GBNF engine interface.
2. **Canonical Corpus Inheritance:** Evaluates the identical 60-case benchmark from MN-013 (SHA-256: `781ae28914227862da288c7663c6180230283d44e9763975b6df98abfbc3d297`).
3. **Hermetic Sandbox Isolation:** All prototype code, GBNF grammar files, and intermediate runs remain strictly within `research/experiments/prototypes/mn-014-grammar-constrained-decoding/`.
4. **Decoupled Disk Persistence:** Every model completion payload, parsed action, rollback event, and environment state snapshot is persisted to disk before scoring (`persist-before-evaluate` contract).
5. **Exact Parsing Determinism:** Action string parsing is strictly validated against the canonical grammar rules; any parsing ambiguity or unexpected delimiter is counted as a grammar violation.

---

## 2. GBNF Action Grammar Specification

The GBNF grammar (`definition/grammar/action_grammar.gbnf`) defines the exact space of permissible generations:

```gbnf
root ::= action

action ::= "ACTION: " ( read_action | inspect_action | dispatch_action | resolve_action )

read_action ::= "READ " target_id
inspect_action ::= "INSPECT " entity_id "." property_id
dispatch_action ::= "DISPATCH " tool_name " " payload
resolve_action ::= "RESOLVE " resolution_value

target_id ::= [a-zA-Z0-9_]+
entity_id ::= [a-zA-Z0-9_]+
property_id ::= [a-zA-Z0-9_]+
tool_name ::= [a-zA-Z0-9_]+
payload ::= [^\r\n]+
resolution_value ::= [^\r\n]+
```

### Key Structural Invariants:
- Mandatory whitespace (`" "`) after verb keywords (`READ `, `INSPECT `, `DISPATCH `, `RESOLVE `).
- Mandatory whitespace separating `tool_name` from `payload` in `dispatch_action`.
- Strict prohibition of unexpected preambles, chat prefixes, or markdown code fences.

---

## 3. Two-Arm Comparative Protocol

MN-014 evaluates two experimental arms on the identical 60-case workload:

1. **Arm A (MN-013 Baseline):**
   - Unconstrained greedy decoding (`llama-server` without grammar parameter).
   - Python host regex parsing (`_ACTION_REGEX`).
   - MN-013 Memento stack + Context Rewind + Phase Gate.
2. **Arm B (Full MN-014):**
   - Native GBNF grammar-constrained decoding (`llama-server` with `grammar` payload).
   - Deterministic structural parsing.
   - MN-013 Memento stack + Context Rewind + Phase Gate.

---

## 4. Five Frozen Acceptance Rules

To qualify for recommendation at Gate D disposition review, Arm B must satisfy all 5 frozen acceptance rules:

### Rule 1: End-to-End Task Completion Efficacy
- **Requirement:** `Qwen3.5-2B` under Arm B must achieve $\ge 85.0\%$ task completion ($\ge 51/60$ cases resolved correctly).
- **Comparison:** Arm A baseline must remain $< 50\%$ overall.

### Rule 2: Zero Parse & Grammar Failures
- **Requirement:** Exactly $100\%$ of emitted model responses must conform strictly to the GBNF grammar:
  $$\text{ParseFailureRate} = 0.0\% \quad (0 \text{ formatting collapses across all turns})$$

### Rule 3: Hard Per-Turn Token Budget Ceiling
- **Requirement:** Exactly $100\%$ of generated turn prompts must adhere to:
  $$\text{TokenCount}(\text{turn\_prompt}) \le 512$$
- Zero overflow occurrences across all turns and rollbacks under `llama-tokenize.exe`.

### Rule 4: Trap Recovery Efficacy
- **Requirement:** On the 30 injected trap cases across Domains A, B, and C, Arm B must achieve $\ge 80.0\%$ trap recovery ($\ge 24/30$ cases successfully resolved via host backtracking).

### Rule 5: Host Overhead & Decoding Latency
- **Requirement:** GBNF logit evaluation overhead must average $< 2.0\text{ ms}$ per generated token. Total turn completion latency must remain $< 1.0\text{s}$.

---

## 5. Directional Pivoting Gate & Failure Taxonomy

If Arm B fails to meet the Gate B criteria:
1. **Failure Mode 1: Grammar-Induced Perplexity Distortion ($> 15\%$ failure due to unnatural phrasing):**
   - *Diagnosis:* The grammar constraint restricts logits so severely that the model cannot express the correct entity name.
   - *Mandatory Pivot:* Loosen payload grammar to free-text while keeping prefix and delimiter strictly constrained.
2. **Failure Mode 2: Multi-Branch Search Exhaustion ($> 15\%$ step limit exceeded):**
   - *Diagnosis:* Grammar solves syntax but small model lacks heuristic to prioritize search branches.
   - *Mandatory Pivot:* Introduce dynamic affordance filtering, dynamically restricting `tool_name` choices in GBNF to valid candidates in the current state.
