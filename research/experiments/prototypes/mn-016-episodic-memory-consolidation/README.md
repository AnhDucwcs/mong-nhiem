# MN-016: Episodic Memory & Long-Horizon Event Consolidation

## Status: Completed & Verified — Host-Authoritative AutoDream Substrate

> [!NOTE] Empirical Milestone Disposition
> This milestone has completed all empirical evaluations under **Gate C execution** and achieved full compliance across all 5 quantitative acceptance criteria under **Gate D disposition review** ([`gate-d-disposition-review.md`](gate-d-disposition-review.md)).
> - **Overall Task Resolution:** **100.0% (40/40 PASS)** on real model inference (`Qwen3.5-2B-Q4_K_M.gguf` via `llama-server.exe`).
> - **Amnesia Remediation:** **+100.0% absolute delta** over Arm 1 FIFO baseline ($40/40$ vs $0/40$).
> - **Token Budget Invariant:** **100.0% compliance** with the $\le 512$ token forward-pass ceiling (Max: 334 tokens, Mean: 111.0 tokens).
> - **Sub-second Turn Latency:** Mean turn latency of **64.9 ms** on local GPU runtime ($< 1000$ ms SLA).
> - **Factual Contradictions:** Exactly **0.0% (0 contradictions)** across all persisted memory cards.
> - **Canonical Report:** [`reports/mn016_benchmark_report_mn016-run-20261009-210120-track2.md`](reports/mn016_benchmark_report_mn016-run-20261009-210120-track2.md).

---

## 1. Problem Statement & Historical Amnesia

In long-horizon autonomous operation ($T = 20-50$ steps), lightweight language models (<4B) face two catastrophic failure modes:

1. **Sliding Window Historical Amnesia (FIFO Truncation):**  
   To prevent exceeding the native context window ($\le 512$ tokens), standard agent frameworks truncate oldest turns. When a function signature, account state, or service lease is mutated at $T=2$, eviction at $T=8$ leaves the agent completely blind at $T=35$, resulting in $0.0\%$ task completion (reproduced in Arm 1).
2. **Sub-4B Summarization Hallucination:**  
   Delegating memory consolidation to an unconstrained LLM subagent results in severe hallucination, dropping critical negation constraints and inventing phantom state transitions on sub-4B models.

---

## 2. Core Architecture: Host-Authoritative AutoDream

MN-016 establishes a strictly host-authoritative memory consolidation architecture designed specifically for the core mission of Mộng Nhiễm:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   MODEL (LLM) — PURE REASONING ENGINE                  │
│  - Stateless: does not own state, never writes directly to DB          │
│  - Bounded context consumption (<= 512 tokens)                         │
│  - Emits STRUCTURED ACTION PROPOSALS (ACTION: ...) via GBNF            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Action Proposal
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                HOST SYSTEM — SOLE AUTHORITY OVER INTEGRITY             │
│  1. Validates preconditions and action structure                       │
│  2. Executes actions in verified environment, computes SHA-256 hashes  │
│  3. Updates episodic memory using DETERMINISTIC STATE REPLAY RULES     │
│  4. Resolves state conflicts strictly from AUTHORITATIVE TOOL SOURCES  │
│  5. Delivers strictly SCOPED WORKING CONTEXT on demand (<= 512 tokens) │
└────────────────────────────────────────────────────────────────────────┘
```

### Architectural Substrates

1. **Host-Authoritative Ground Truth (`src/provenance.py`):**
   - Tool execution returns (`ToolResult.state_delta`) are hashed via SHA-256 and appended to an immutable episodic stream. The LLM never writes ungrounded facts to memory.
2. **Deterministic Conflict Resolution (`src/conflict_resolver.py`):**
   - Resolves entity attributes via monotonic causal replay over validated event streams. Purges contradictory and superseded facts deterministically, formatting compact Fact Cards ($\le 48$ tokens).
3. **Autonomous Dual-Trigger Gates (`src/auto_dream_trigger.py`):**
   - Replaces 24-hour biological wall-clock time with discrete machine ticks ($\Delta T \ge 25$) and state mutation flux ($M \ge 10$).
   - **Emergency Context Budget Pressure Interceptor:** Immediately triggers consolidation when working prompt tokens reach $\ge 400$ tokens ($\approx 78\%$ saturation), preventing context overflow under burst mutation sequences.
4. **4-Phase Consolidation Engine (`src/dream_engine.py`):**
   - Phase 1: Orient (Read `INDEX.md` and existing entity cards).
   - Phase 2: Gather (Collect recent verified events since last consolidation tick).
   - Phase 3: Consolidate (Execute deterministic state replay and update entity cards).
   - Phase 4: Prune & Index (Re-generate bounded `INDEX.md` $\le 128$ tokens and release `.consolidate-lock`).
5. **Demand-Driven Recall Coordinator (`src/recall_coordinator.py`):**
   - Governs task execution by injecting bounded `MEMORY_INDEX` into the working prompt and constraining model outputs via dynamic GBNF grammars that afford `ACTION: RECALL <entity_id>` prior to action execution.

---

## 3. Empirical Evaluation Across 3 Operational Arms

The evaluation was conducted on **40 deterministic long-horizon cases** ($T = 20-50$ steps) partitioned across:
- **Domain A:** Multi-Phase Code Refactoring (15 cases)
- **Domain B:** Multi-Vault Asset Ledger & Audit (15 cases)
- **Domain C:** Distributed System Registry & Leases (10 cases)

### Multi-Arm Comparative Summary (Track 2 — `Qwen3.5-2B-Q4_K_M.gguf`)

| Arm | Architecture | Accuracy | Amnesia Failures | Token Violations (>512) | Mean Tokens | Latency |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Arm 1** | Sliding Window FIFO Baseline | 0.0% (0/40) | 40/40 (100%) | 0/40 | 51.0 | 0.0 ms |
| **Arm 2** | Cadence-Only AutoDream Control | 62.5% (25/40) | 0/40 | 15/40 (37.5%) | 137.5 | 0.0 ms |
| **Arm 3** | Dual-Trigger Host AutoDream (MN-016) | **100.0% (40/40)** | **0/40 (0.0%)** | **0/40 (0.0%)** | **111.0** | **64.9 ms** |

---

## 4. Gate D Disposition & Successor Handoff

- **Disposition:** `host_authoritative_autodream_empirically_proven`.
- **Quarantine Notice:** In accordance with Mộng Nhiễm governance rules, experimental code remains quarantined in `research/experiments/prototypes/mn-016-episodic-memory-consolidation/` until full production integration in subsequent synthesis milestones.
- **Successor Handoff (MN-017):**
  - **MN-017 (Dynamic World Ticks & Hierarchical Planning):** Builds on MN-016's episodic substrate to introduce multi-rate simulation clocks and hierarchical goal decomposition, leading to **MN-Final (MN-018: Stateful Simulated Microworld Evolution)**.
