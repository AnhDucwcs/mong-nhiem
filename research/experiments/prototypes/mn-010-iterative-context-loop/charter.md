# MN-010 Gate A: Charter & Scientific Hypothesis

## Context & Navigation
- Canonical Knowledge Base: [00-mong-nhiem](../../../00-mong-nhiem.md)
- System Architecture: [architecture](../../../concepts/architecture.md)
- Conceptual Taxonomy: [ECC vs NCC](../../../concepts/ecc-vs-ncc.md)
- Roadmap: [roadmap](../../../roadmap.md)
- Predecessors:
  - [MN-008: External State Management](../mn-008-external-state-management/README.md)
  - [MN-009: Scoped Context Delivery Engine](../mn-009-context-scaffolding/README.md)

---

## 1. Problem Statement

MN-009 resolved the single-shot context bottleneck for small models (<4B), proving that restricting native forward passes to $\le 512$ tokens yields 100% accuracy and 22.9x faster inference over raw 16k/32k document streams.

However, single-shot context packing exhibits a fundamental architectural boundary: when a task requires sequential multi-hop dependency resolution (e.g. following transitive function calls $A \rightarrow B \rightarrow C$, or cross-document entity state linkage), a single 512-token working set cannot anticipate which second-order facts will be required until the first reasoning step is evaluated.

Small models collapse when forced to evaluate multi-hop dependencies in long raw contexts, and cannot self-regulate unconstrained autonomous CoT loops. An iterative host-coordinated working set dispatch mechanism is required.

---

## 2. Falsifiable Hypothesis

A host-managed **Iterative Context Working Set Coordinator**—interleaving bounded native model forward passes ($\le 512$ tokens per turn) with deterministic host-side context extraction over a structured external corpus—can solve multi-hop reasoning tasks ($\ge 2$ hops) across $32\text{k}+$ token knowledge spaces such that:

1. **Multi-Hop Efficacy:** Primary task accuracy achieves $\ge 85\%$ across matched multi-hop benchmarks where single-shot packing fails ($< 40\%$).
2. **Per-Turn Budget Invariant:** Exactly $100\%$ of iterative invocations respect the hard $\le 512$ token ceiling under the verified tokenizer.
3. **Loop Boundedness & Circuit Breaker:** Zero runaway executions; exactly $100\%$ of task completions terminate within a fixed bound ($\le 3$ turns), with automatic duplicate-query and cycle detection.
4. **Latency Ceiling:** End-to-end multi-hop execution time remains $< 1.5\text{s}$ total on consumer hardware (zero GPU memory overhead, pure CPU host coordination).

---

## 3. Scope & Non-Goals

### In Scope
- Discrete host coordinator executing turn-by-turn context dispatch.
- Structured action grammar for intermediate model intent (e.g. `FETCH(entity)` vs `RESOLVE(answer)`).
- Circuit breaker mechanisms protecting against infinite retrieval cycles.
- Multi-hop synthetic and real-world dependency benchmarks.

### Non-Goals
- No fine-tuning, weight modifications, or internal attention modifications to the underlying model.
- No general-purpose unbounded agentic loop frameworks (pure Ponytail minimal coordinator).
- No promotion into `src/mong_nhiem/` prior to Gate D disposition review.
