# MN-015 Gate B: Measurement Contract & Evaluation Protocol

## Context & Navigation
- Canonical Knowledge Base: [00-mong-nhiem](../../../00-mong-nhiem.md)
- System Architecture: [architecture](../../../concepts/architecture.md)
- Parent Milestone Charter: [MN-015 Gate A Charter](charter.md)
- Primary Model: `Qwen3.5-2B-Q4_K_M.gguf` on local `llama.cpp` runtime
- Benchmark Corpus: `definition/corpus-v1/cases.jsonl` (Inherited from MN-013/MN-014, 60 cases)

---

## 1. Objectives & Measurement Principles

This contract establishes the empirical evaluation protocol for **MN-015: Dynamic Affordance Constrained Decoding & Dual-Layer Steering**.
The primary objective is to prove that pairing an in-context Prompt Attention Prior with per-turn Dynamic GBNF Logit Masking overcomes Failure Mode 2 (Multi-Branch Search Exhaustion), enabling `Qwen3.5-2B` to achieve $\ge 85\%$ end-to-end task completion across the canonical 60-case benchmark, with Domain C System Registry surging from $15.0\% \rightarrow \ge 80.0\%$.

All measurements adhere to five frozen scientific principles:
1. **Black-Box Invariant:** `Qwen3.5-2B-Q4_K_M` remains strictly frozen (`temperature=0.0`, greedy decoding).
2. **Canonical Corpus Inheritance:** Evaluates the identical 60-case benchmark from MN-013/MN-014 (SHA-256: `781ae28914227862da288c7663c6180230283d44e9763975b6df98abfbc3d297`).
3. **Hermetic Sandbox Isolation:** All prototype code, dynamic compilers, and intermediate runs remain quarantined in `research/experiments/prototypes/mn-015-dynamic-affordance-decoding/`.
4. **Decoupled Disk Persistence:** Every model completion payload, dynamic grammar string, parsed action, rollback event, and environment state snapshot is persisted to disk before scoring (`persist-before-evaluate` contract).
5. **Exact Affordance Determinism:** Dynamic GBNF grammars must strictly permit only the active affordances calculated by the host state engine at each turn.

---

## 2. Dynamic GBNF Grammar Architecture

Unlike the static grammar of MN-014 (`identifier ::= [a-zA-Z0-9_]+`), MN-015 compiles an exact Context-Free Grammar per turn based on the active state snapshot $S_t$ and negative directives:

```gbnf
root ::= action ("\n" | "")

action ::= "ACTION: " ( read-action | inspect-action | dispatch-action | resolve-action )

read-action ::= "READ " valid-read-target
inspect-action ::= "INSPECT " valid-inspect-target
dispatch-action ::= "DISPATCH " valid-dispatch-call
resolve-action ::= "RESOLVE " valid-resolve-target

# Dynamic rules generated per turn:
valid-read-target ::= "target_1" | "target_2"
valid-inspect-target ::= "svc_b_51.status"
valid-dispatch-call ::= "activate_service svc_worker_b_51,CONSERVATIVE_PIPELINE"
valid-resolve-target ::= "svc_worker_b_51:CONSERVATIVE_PIPELINE"
```

If an action category has zero active affordances, that branch is omitted from the `action` production rule, mathematically setting its logit probability to $-\infty$.

---

## 3. Two-Arm Comparative Protocol

MN-015 evaluates two experimental arms on the identical 60-case workload:

1. **Arm 1 (MN-014 Baseline Standard):**
   - Static GBNF Grammar (`action_grammar.gbnf`).
   - Standard negative directive prompt upon rollback.
   - Evaluated task completion: $55.0\%$ ($33/60$ cases).

2. **Arm 2 (Dual-Layer Affordance Steering — Full MN-015):**
   - **Prompt Layer:** Injects compact affordance prior ($\le 15-20$ tokens) into the turn observation.
   - **Engine Layer:** Compiles and submits dynamic per-turn GBNF grammar to `llama-server`.
   - Host Memento state stack, context rewinding, and Phase Gate interceptor enabled.

---

## 4. Frozen Acceptance Rules (Gate B)

| Rule ID | Metric Name | Threshold | Operational Evaluation |
| :--- | :--- | :---: | :--- |
| **Rule 1** | **Overall Task Completion Efficacy** | $\ge 85.0\%$ | At least $51/60$ cases resolved cleanly within turn ceilings. |
| **Rule 2** | **Domain C (System Registry) Surge** | $\ge 80.0\%$ | At least $16/20$ Domain C cases resolved (vs $3/20$ in MN-014). |
| **Rule 3** | **Zero Parse & Grammar Failures** | Exactly $0.0\%$ | Exactly zero parse errors or malformed tokens across all turns. |
| **Rule 4** | **Hard Working Memory Ceiling** | $100\%$ compliance | $100\%$ generated prompts $\le 512$ tokens. |
| **Rule 5** | **Inference Latency & CPU Overhead** | Mean $< 1000\text{ ms}$ | Average turn latency $< 1000\text{ ms}$, GBNF compilation $< 1\text{ ms}$ CPU. |
