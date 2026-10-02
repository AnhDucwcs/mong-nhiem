# Effective Context Capacity (ECC) vs Native Context Capacity (NCC)

Mộng Nhiễm establishes a strict invariant principle across all research directions: **no fine-tuning, no weight modification, and no architectural alteration to the underlying model.** 

The model is maintained strictly as an unchanged, black-box reasoning engine:

```text
                  ┌───────────────────────┐
External world ──►│ Context Layer / Engine│
                  └──────────┬────────────┘
                             │ (working set)
                             ▼
                  ┌───────────────────────┐
                  │     Model (Frozen)    │
                  │       UNCHANGED       │
                  └──────────┬────────────┘
                             │
                             ▼
                  ┌───────────────────────┐
                  │ External Working State│
                  └───────────────────────┘
```

All innovation resides entirely in the system surrounding the model. This isolation is essential for causal attribution: if the model were fine-tuned or weights modified, it would become impossible to separate gains produced by representation/weight changes from gains produced by external context mechanisms. Furthermore, evaluating across multiple heterogeneous models ensures discovered principles reflect generalizable external context management rather than idiosyncratic model-specific artifacts.

---

## 1. Effective Context Capacity (ECC) — Utilization

ECC originates from a pragmatic limitation: models exhibit large nominal context windows on paper, but their capacity to execute reliable, useful operations over that context is substantially lower.

When a model must locate needle information deep in a context, synthesize distributed facts, maintain multi-step constraints, or carry out sequential deduction, performance degrades sharply long before the nominal context ceiling is reached.

Therefore:
- **ECC does not attempt to expand the context window.**
- **ECC aims to maximize the proportion of the native context window that is utilized effectively.**

### The External Context Management Layer
Rather than passively dumping raw prompts into the model's window, ECC interposes an external management layer that:
- Deconstructs raw context into structured, atomic units;
- Tracks and maintains entity state externally;
- Selectively retrieves relevant facts per invocation;
- Preserves critical constraints across multiple steps;
- Filters out irrelevant noise and distractor tokens;
- Reorganizes context around task-specific dependencies rather than chronological transcripts.

### Core Research Question
> *"Given the same model and fixed native context bounds, can an external context management layer increase the volume of useful information the model actually operates over?"*

### The Context Utilization Chain
Maximizing utilization is distinct from simple prompt tuning or naive retrieval. It requires isolating the conversion stages of context delivery:

$$\text{Theoretical Capacity} \longrightarrow \text{Fed Context} \longrightarrow \text{Accessed Context} \longrightarrow \text{Correctly Utilized Context} \longrightarrow \text{Final Outcome}$$

ECC investigates which external mechanisms genuinely maximize transition efficiency across these stages to produce reliable reasoning rather than superficial prompt variations.

---

## 2. Native Context Capacity (NCC) — Expansion via Substrate

NCC pursues a significantly more ambitious objective. Where ECC accepts the model's native context window as a fixed boundary and optimizes utilization within it, NCC asks:

> *"Can we construct a system that enables the model to operate reliably over an information space vastly larger than its native effective context, without modifying the model or its weights?"*

### Effective vs Native Attention Expansion
NCC does not simulate or attempt to force 1M tokens through a model's native self-attention. Forcing massive token volumes through dense attention is neither viable on local hardware nor causally robust.

Instead, NCC constructs an **External Context Substrate**:

```text
                 ┌───────────────────────────┐
                 │   External Context Corpus │
                 │        (Very Large)       │
                 └─────────────┬─────────────┘
                               │
                     retrieval / selection
                               │
                               ▼
                 ┌───────────────────────────┐
                 │   Model's Bounded Native  │
                 │          Context          │
                 │       (Working Set)       │
                 └─────────────┬─────────────┘
                               │
                           reasoning
                               │
                               ▼
                 ┌───────────────────────────┐
                 │ External State / Working  │
                 │          Memory           │
                 └─────────────┬─────────────┘
                               │
                               └───────────► Next Iteration Loop
```

The model never needs to observe the entire corpus simultaneously. The external system maintains the vast information space, supplying the model with only the bounded working set required for its immediate reasoning step.

### Substrate Paradigm
$$\text{Large External Memory} + \text{Bounded Native Context} + \text{Iterative Access}$$


### Core Research Question
> *"How can we engineer an external memory and context substrate that enables a model to work reliably over information volumes far exceeding its native effective context?"*
