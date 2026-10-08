# MN-012 Gate C: Execution & Verification Report

## Metadata
- Prototype: `MN-012: Hierarchical Tool & Memory Integration`
- Track: `NCC Phase 3 — Cognitive Orchestration`
- Evaluated Benchmark: `definition/corpus-v1/cases.jsonl` (60 cases, SHA-256: `c0a4cf353cc1f11ea4223d03dc6f04f3fd893f5d88ac1c0a925ba9c859d1d784`)
- Primary Model: `Qwen3.5-2B-Q4_K_M.gguf`
- Execution Run ID: `mn012-execution-run-0001`
- Mode: `Track 1 (Deterministic Simulator & Invariant Stress Verification)`
- Freeze Status: `FROZEN` under [`definition/freeze-manifest.json`](../definition/freeze-manifest.json)

---

## 1. Executive Summary

MN-012 verifies the transition from passive multi-hop context retrieval (MN-010) to active, stateful tool interaction under a dual-tier memory partition:
- **L1 Working Set Memory:** Prompt context strictly bounded to $\le 512$ tokens via `ContextPacker`.
- **L2 Persistent State Store:** Host-managed state engine tracking cumulative environment state, entity properties, transaction histories, and domain invariants.
- **Action Grammar:** Flat regex protocol (`READ`, `INSPECT`, `DISPATCH`, `RESOLVE`).

Across all 60 benchmark cases spanning 3 domains, the evaluation demonstrates the clear distinction between deterministic host orchestration and small-model raw instruction following:
- **Track 1 (Deterministic Simulator):** Achieved **100.0% task resolution (60/60)** on Arm B versus **0.0% (0/60)** on Arm A, with 100% budget compliance ($\le 512$ tokens) and host overhead $< 0.15\text{ ms}$/turn.
- **Track 2 (Real Model Inference — Qwen 3.5 2B):** Achieved **0.0% task resolution (0/60)** due to zero-shot placeholder repetition (`ACTION: READ <target_id>`) tripping host circuit breakers, directly triggering the pre-registered **Failure Mode 1 (Format Collapse) & Failure Mode 2 (Argument Grounding)** pivoting gates.

---

## 2. Evaluation Across Five Frozen Gate B Rules

| Gate B Acceptance Rule | Target Threshold | Track 1 (Simulator) Arm B | Track 2 (Qwen 3.5 2B) Arm B | Verdict |
| :--- | :---: | :---: | :---: | :---: |
| **Rule 1: Task Completion Efficacy** | Arm B $\ge 85\%$ ($51/60$), Arm A $< 20\%$ | **$100.0\%$ ($60/60$)** | **$0.0\%$ ($0/60$)** | Track 1: PASS / Track 2: PIVOT |
| **Rule 2: Hard Token Budget Ceiling** | $100\%$ turns $\le 512$ tokens | **$100.0\%$** (Max: 316, Mean: 242.1) | **$100.0\%$** (Max: 261, Mean: 247.3) | **PASS** |
| **Rule 3: Action Protocol Conformance** | $100\%$ valid regex parses | **$100.0\%$** (0 format collapses) | **$11.7\%$** (7/60 emitted valid action verbs, 53/60 collapsed) | Track 1: PASS / Track 2: PIVOT |
| **Rule 4: State Invariant Preservation** | $100\%$ invariant compliance | **$100.0\%$** (0 illegal mutations) | **$100.0\%$** (0 illegal mutations committed to L2) | **PASS** |
| **Rule 5: Host Coordination Overhead** | Mean overhead $< 10\text{ ms}$/turn | **$< 0.15\text{ ms}$** per turn | **$< 0.20\text{ ms}$** per turn (excl. forward pass) | **PASS** |

---

## 3. Track 2 Root Cause & Failure Taxonomy Analysis

Under [`gate-b-contract.md`](../gate-b-contract.md) Section 6, the empirical failure of Track 2 on raw zero-shot Qwen3.5-2B maps to two concrete failure modes:

1. **Failure Mode 1: Format & Placeholder Collapse (Rule 3 Failure):**
   - *Observation:* When presented with abstract system prompt instructions (`- To read a function: ACTION: READ <target_id>`), the 2B model literally copies the syntactic placeholder (`<target_id>`) rather than binding the concrete entity name from the prompt's L1 context.
   - *Host Circuit Breaker Interception:* The host rejects the unknown target (`ENTITY_NOT_FOUND: <target_id>`). When the model repeats the ungrounded placeholder in Turn 2, the host circuit breaker halts the execution via `TRIPPED_CYCLE_DETECTED` / `TRIPPED_REJECTION_LIMIT`.
2. **Failure Mode 2: Lack of Grounded Entity Anchoring (Rule 1 Failure):**
   - *Diagnostic Validation:* When tested with a single concrete 1-shot in-context demonstration, Qwen 3.5 2B immediately bound the entity correctly (`ACTION: READ calculate_tax_1`), proving the model possesses the lexical capability but requires in-context grounding or GBNF grammar constraints rather than abstract BNF rules.

---

## 4. Empirical Conclusion & Gate D Recommendations

1. **Track 1 Freezing Status:** Host orchestration architecture (L1 working set compiler, L2 persistent state ledger, Circuit Breaker, AST & Conservation Invariants) is 100% verified and frozen under `freeze-manifest.json`.
2. **Track 2 Empirical Finding:** Pure zero-shot regex prompting without in-context grounding is insufficient for unconstrained 2B parameter models.
3. **Pivoting Gate Activation:** Gate D must formalize the requirement for GBNF grammar-constrained decoding and 1-shot entity slot grounding before promoting the autonomous tool coordinator into production `src/mong_nhiem/`.
