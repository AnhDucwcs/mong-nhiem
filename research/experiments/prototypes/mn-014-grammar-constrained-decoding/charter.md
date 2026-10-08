# MN-014 Gate A: Charter & Scientific Hypotheses

## Context & Navigation
- Canonical Knowledge Base: [00-mong-nhiem](../../../00-mong-nhiem.md)
- System Architecture: [architecture](../../../concepts/architecture.md)
- Conceptual Taxonomy: [ECC vs NCC](../../../concepts/ecc-vs-ncc.md)
- Strategic Roadmap: [roadmap](../../../roadmap.md)
- Strategic Decisions: [decisions](../../../decisions/decisions.md)
- Predecessors:
  - [MN-012: Hierarchical Tool & Memory Integration](../mn-012-hierarchical-tool-memory/README.md)
  - [MN-013: Backtracking & Error Self-Correction](../mn-013-backtracking-error-correction/README.md)
- Successors:
  - [MN-Final: Stateful Simulated Microworld Evolution](../../../roadmap.md#north-star-horizon-mn-final--stateful-simulated-microworld-evolution)

---

## 1. Problem Statement

Across MN-012 and MN-013, Mộng Nhiễm established two fundamental architectural pillars for small language models (<4B):
1. **Host-Managed Dual-Tier Memory (MN-012):** Ephemeral L1 prompt working context is strictly bounded to $\le 512$ tokens, while persistent state transitions are tracked in host L2 memory.
2. **Host-Directed Backtracking (MN-013):** Bounded snapshot stacks ($S_t \rightarrow S_{t-1}$) in host RAM and surgical context rewinding with negative directives achieve $100\%$ trap recovery on complex resource allocation branches (Domain B).

However, empirical execution under MN-013 revealed a decisive operational bottleneck:
**Unconstrained Greedy Decoding Formatting Fragility.**
When sampling tokens freely ($T=0.0$), sub-4B models exhibit subtle tokenization variances:
- Omission of whitespace separators between tool target and argument payloads (e.g., `ACTION: DISPATCH calculate_tax_1:rate=22` instead of `ACTION: DISPATCH calculate_tax_1 rate=22`).
- Ambiguous delimiters (colons vs spaces vs commas) causing host regex parsers to misclassify arguments, leading to no-op environment mutations.
- Premature Phase Gate rejections when the model calls `ACTION: RESOLVE` on an un-mutated environment, followed by cyclic token repetition and circuit breaker trip.

Attempting to solve this via increasingly complex host-side regex heuristics is an anti-pattern (violating the Ponytail Principle). The correct architectural remedy is to enforce grammar constraints directly at the inference engine layer.

**MN-014 introduces Native GBNF (Grammar-Based Context-Free Grammar) Constrained Decoding** within `llama-server`. By masking invalid token logits dynamically at each decoding step, GBNF guarantees 100% syntactically perfect action emissions, bridging the gap between small model generation and host state execution.

---

## 2. Falsifiable Hypotheses

### Hypothesis 1 ($H_1$): Grammar Determinism & Zero Parse Failures
Constraining `Qwen3.5-2B-Q4_K_M` with an authoritative GBNF grammar at the `llama-server` completion interface will eliminate $100\%$ of delimiter omissions, token concatenations, and regex parse ambiguities, achieving:
$$\text{ParseFailureRate}(\text{GBNF}) = 0.0\%$$
across all generated turns in the 60-case benchmark.

### Hypothesis 2 ($H_2$): End-to-End Task Resolution Efficacy ($\ge 85\%$)
Coupling GBNF grammar-constrained decoding with the proven MN-013 Memento rollback stack, context rewind, and Phase Gate interceptor will elevate `Qwen3.5-2B` end-to-end task completion from $36.7\%$ (MN-013 baseline) to:
$$\text{TaskCompletionRate}(\text{MN-014 Arm B}) \ge 85.0\% \quad (51/60 \text{ cases})$$
by eliminating the non-trap false rejections and cycle trips caused by malformed tool parameters.

### Hypothesis 3 ($H_3$): Zero Prompt Overhead & Negligible Inference Cost
GBNF grammar decoding executes via CPU/GPU logit masking during token generation, requiring zero prompt tokens:
$$\Delta \text{PromptTokens}(\text{GBNF}) = 0$$
Average per-token decoding overhead under GBNF will remain $< 2.0\text{ ms}$, preserving sub-second turn latency ($< 800\text{ ms}$/turn).

---

## 3. Scope & Non-Goals

### In Scope
1. **Primary Subject:** Canonical evaluation on `Qwen3.5-2B-Q4_K_M.gguf`.
2. **Authoritative GBNF Grammar:** Formal BNF specification defining `root ::= action`, enforcing verb keywords (`READ`, `INSPECT`, `DISPATCH`, `RESOLVE`), mandatory whitespace separators, and structured entity/key-value argument patterns.
3. **Integration with llama-server:** Passing grammar specifications via the `/completion` endpoint `grammar` field.
4. **Full Cognitive Stack Integration:** Unifying GBNF decoding + Memento snapshot stack ($K_{\max}=3$) + Context Rewind ($\le 512$ tokens) + Phase Gate state verification.
5. **Frozen Benchmark:** Evaluating the 60-case benchmark inherited from MN-013 (20 Code AST, 20 Resource Ledger, 20 System Registry).

### Non-Goals
1. **No Custom Model Fine-Tuning:** The model weights remain 100% frozen.
2. **No Ad-Hoc Regex Patching:** Python host regex logic remains simple and standard; syntax compliance is guaranteed by the engine.
3. **No Unconstrained Multi-Agent Swarms:** Agent roles remain focused on single-agent host-directed cognitive execution.
4. **No Premature Promotion:** Prototype code remains within `research/experiments/prototypes/mn-014-grammar-constrained-decoding/` until formal Gate D disposition review.
