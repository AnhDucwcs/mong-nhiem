# MN-010: Iterative Context Working Set Loop

## Research Track
**Native Context Capacity (NCC) Phase 2 — Substrate Expansion**

## Overview
MN-010 extends Mộng Nhiễm's verified single-shot context scaffolding engine ([MN-009](../mn-009-context-scaffolding/README.md) promoted to `src/mong_nhiem/context/`) into an **Iterative Context Working Set Loop**.

While MN-009 demonstrated that small models (<4B) achieve 100% extraction accuracy with 22.9x latency reduction when fed a bounded single-shot working set ($\le 512$ tokens), complex real-world queries over vast external corpora ($32\text{k}+$ tokens) frequently require multi-hop exploration (e.g. cross-referencing distributed facts, tracing function call hierarchies across multiple files).

MN-010 implements the full NCC triad:
$$\text{Large External Memory} + \text{Bounded Native Context} + \text{Iterative Access}$$

## Navigation
- [Gate A Charter](charter.md)
- [Canonical Architecture](../../../concepts/architecture.md)
- [ECC vs NCC Concepts](../../../concepts/ecc-vs-ncc.md)
- [Decisions](../../../decisions/decisions.md)
- [Roadmap](../../../roadmap.md)
