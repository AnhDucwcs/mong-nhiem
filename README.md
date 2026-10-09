# Mộng Nhiễm

Mộng Nhiễm researches reliable reasoning and state tracking for lightweight open-weights language models (<4B parameters) over extensive knowledge and context spaces ($32\text{k}+$ tokens).

The project adheres strictly to an invariant core principle: **no fine-tuning, no weight modification, and no architectural alteration to the model**. The model is maintained strictly as an unchanged black-box reasoning engine, while host-managed substrates guarantee deterministic context bounds, prompt sanitization, and safety invariants.

---

## Production Library (`src/mong_nhiem/`)

The core library is implemented using **100% Python Standard Library** with zero external runtime dependencies.

### Scoped Context & Scaffolding Subsystem (`mong_nhiem.context`)

Promoted into production under milestones **MN-009** and **MN-010**:

- **`ContextPacker`:** Deterministic Knapsack context packing algorithm that compresses extensive document streams ($2\text{k}-32\text{k}$ tokens) down to a strict $\le 512$-token native forward-pass ceiling. Features lexical salience ranking, natural boundary preservation (zero sentence-splitting mid-token), and complete prompt injection sanitization against ChatML, Llama 3 headers, and reasoning delimiters (`<think>...</think>`).
- **`CodebaseSlicer`:** AST-based code compression engine that generates function skeletons, stubs uncalled auxiliary helpers, and adaptively inlines short utility functions while maintaining $100\%$ valid Python syntax (`ast.parse`).
- **`IterativeCoordinator`:** Host-managed multi-turn context loop coordinator. Interleaves bounded model forward passes ($\le 512$ tokens per turn) with deterministic host-side context extraction to resolve sequential multi-hop dependencies ($A \rightarrow B \rightarrow C$).
- **`CircuitBreaker`:** Defensive safety subsystem enforcing a hard turn ceiling ($\le 3$ turns) and duplicate/cycle detection (`visited_targets` set hashing), guaranteeing zero infinite retrieval loops or runaway latency.
- **Graph & Tabular Slicers:** Breadth-first $k$-hop subgraph extraction ($O(V+E)$) and attribute projection for structured state tables.

---

## Research Milestone Progression

Research is organized under strict Gate criteria (Gate A Charter $\rightarrow$ Gate B Contract $\rightarrow$ Gate C Execution $\rightarrow$ Gate D Disposition Review). Experimental artifacts remain isolated in `research/experiments/` until earned promotion into `src/mong_nhiem/`.

| Milestone | Title | Track | Status | Primary Empirical Outcome |
| :--- | :--- | :---: | :---: | :--- |
| **MN-001** | Development Foundation | Foundation | **Completed** | Packaging, test harness, CI workflows, and canonical research structure. |
| **MN-002** | Model Qualification | Qualification | **Completed** | MCB v0.3.0 qualification benchmark. Qualified Llama 3.2 3B, Qwen3 4B, and Qwen 3.5 2B. |
| **MN-003** | Effective Context Capacity | ECC | **Completed** | Mapped empirical limits of direct native attention up to 16k tokens; identified state tracking collapse. |
| **MN-004** | State Representation Intervention | ECC | **Closed (Unsupported)** | Evaluated global state-transition ledgers; missed frozen support thresholds. |
| **MN-005** | State Tracking Intervention Selection | ECC | **Closed (Inconclusive)** | Multi-pass reconstruction audit; demonstrated ECC-006 workload limitations. |
| **MN-006** | Distributed State Integration | ECC | **Closed (Interface Blocked)** | Evaluated contiguous vs interleaved state locality under strict model qualification. |
| **MN-007** | State Recovery Operating Region | ECC | **Closed (Floor Regime)** | 108-case calibration proved in-context contiguous state recovery is unviable without support. |
| **MN-008** | External State Management | NCC | **Closed (Unsupported)** | Offloaded event replay to host engine; identified small-model conditional conjunction bounds. |
| **MN-009** | Scoped Context Delivery Engine | NCC Phase 1 | **Promoted** | 100% causal remedy on ECC-006, 100% injection immunity, and 22.9x downstream latency reduction. |
| **MN-010** | Iterative Context Working Set Loop | NCC Phase 2 | **Promoted** | 100% multi-hop resolution (30/30 vs 0/30 baseline), 100% budget adherence ($\le 512$ tokens), circuit breaker safety. |
| **MN-011** | Scaffolding-Assisted Context Frontier | ECC Reactivation | **Completed** | Proved $B^* \approx 512$ capacity-efficiency peak ($H_1$), 100% causal restoration on ECC-007 ($H_2$), and $60\times$ conversion advantage ($H_3$). |
| **MN-012** | Hierarchical Tool & Memory Integration | NCC Phase 3 | **Closed (Pivoted)** | Validated dual-tier memory; unassisted models suffer Horizon Jumping; activated pivoting gate. |
| **MN-013** | Backtracking & Error Self-Correction | NCC Phase 4 | **Closed (Quarantined)** | Achieved 100% trap recovery on resource contention via Memento rollback; proved amnesia deadlock on unguided rewind. |
| **MN-014** | Grammar-Constrained Decoding | NCC Phase 4 | **Active** | Native GBNF engine-level logit masking on llama-server to eliminate formatting token collapse and whitespace fragility. |


---

## Repository Layout

- `research/`: Canonical research knowledge base (directly viewable as an Obsidian vault).
  - `research/00-mong-nhiem.md`: Master entrypoint and navigational hub.
  - `research/concepts/`: Core theoretical frameworks ([`ecc-vs-ncc.md`](research/concepts/ecc-vs-ncc.md), [`architecture.md`](research/concepts/architecture.md)).
  - `research/decisions/`: Architectural Decision Records (ADRs).
  - `research/experiments/`: Sandbox prototypes and frozen empirical evidence.
- `src/mong_nhiem/`: Production package boundary (pure Python standard library).
- `tests/unit/`: Comprehensive test suite (420+ unit and integration tests passing).

---

## Getting Started & Development

Python 3.11+ is required.

```powershell
# Install editable package with development dependencies
python -m pip install -e ".[dev]"

# Linting and syntax formatting checks
ruff check .

# Run test suite
python -m pytest tests/unit/ -v
```

Before contributing or modifying architectural decisions, read [`research/00-mong-nhiem.md`](research/00-mong-nhiem.md), [`research/concepts/architecture.md`](research/concepts/architecture.md), and [`research/decisions/decisions.md`](research/decisions/decisions.md).
