# MN-014: Grammar-Constrained Decoding & Structured Cognitive Routing

## Overview
- **Milestone:** MN-014
- **Track:** NCC Phase 4 — Robust Action Synthesis
- **Parent Charter:** [charter.md](charter.md)
- **Measurement Contract:** [gate-b-contract.md](gate-b-contract.md)
- **Primary Research Subject:** `Qwen3.5-2B-Q4_K_M.gguf` (Local `llama.cpp` runtime)
- **Status:** Active prototype design (Pre-Gate A/B)

---

## Motivation & Scientific Objective

MN-013 proved that Host-Directed Backtracking, Memento State Checkpointing, and Context Rewinding enable sub-4B models to achieve 100% recovery from environmental dead-ends (Domain B). However, MN-013 also exposed a critical operational vulnerability: **token-level syntax brittleness under unconstrained greedy decoding**.

In unconstrained decoding, `Qwen3.5-2B` occasionally generates tool dispatches with missing whitespace separators (e.g., `ACTION: DISPATCH calculate_tax_1:rate=22`), causing host regex parsers to treat the entire string as target and leave payload empty. This results in no-op mutations, false-positive premature resolve rejections at the Phase Gate, and loop breaker trips.

MN-014 addresses this root cause by introducing **Native GBNF Grammar-Constrained Decoding** at the `llama-server` engine layer. By enforcing a formal Context-Free Grammar directly during logit sampling, MN-014 guarantees 100% syntactically conforming action emissions with zero regex ambiguity, unifying grammar-guided decoding with host-directed state backtracking to achieve $\ge 85\%$ end-to-end task completion.

---

## Prototype Directory Structure

```text
mn-014-grammar-constrained-decoding/
├── README.md                  # Prototype entry point and architectural summary
├── charter.md                 # Gate A charter & falsifiable hypotheses
├── gate-b-contract.md         # Gate B measurement contract and acceptance rules
├── definition/
│   └── grammar/
│       └── action_grammar.gbnf # Formal GBNF grammar for llama.cpp constrained decoding
├── src/                       # Prototype runtime components (to be created)
│   ├── gbnf_client.py         # llama-server API client with grammar payloads
│   ├── coordinator.py         # Integrated coordinator (GBNF + Memento + Rewind)
│   └── phase_gate.py          # State verification interceptor
├── tests/                     # Unit & integration verification suite (to be created)
└── scripts/                   # Evaluation runner and freeze manifests (to be created)
```
