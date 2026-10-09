# Gate A Charter — Milestone MN-016: AutoDream Memory Consolidation & Context Pressure Protection

## 1. Context & Motivation

Milestones **MN-009** through **MN-015** established the foundational building blocks of Scoped Context Scaffolding, Iterative Working Sets, Backtracking with Negative Action Masking, Grammar-Constrained Decoding, and Dual-Layer Affordance Steering.

While MN-015 achieved 100.0% task resolution on short-horizon tasks ($T \le 6-8$ turns), scaling Mộng Nhiễm toward persistent simulated environments ($T \ge 20-50+$ steps) immediately encounters the **Context Budget Barrier**:
1. **The Invariant Budget Constraint**: Small models (<4B parameters) collapse in attention accuracy and reasoning coherence beyond 512 tokens (proven across MN-003, MN-008, and MN-011). Thus, the forward-pass ceiling is strictly locked at $\le 512$ tokens.
2. **Historical Amnesia vs Context Explosion**:
   - A naive FIFO sliding window purges historical turns, causing the agent to forget decisions or state changes made at $T=3$ when evaluating conditions at $T=35$.
   - Naive chronological history accumulation inflates context ($> 2048$ tokens), destroying turn latency ($> 3000\text{ ms}$) and inducing severe hallucinations.
3. **The Raison d'Être of Mộng Nhiễm**:
   - The LLM is strictly an isolated **Reasoning Engine**, emitting structured action proposals (`ACTION: ...`).
   - The Host is the sole authority over **State Integrity, Ground Truth, and Memory Consolidation**.
   - GBNF enforces syntax; the Host enforces truth and provenance.

**MN-016 establishes the `autoDream` memory consolidation architecture** for autonomous small-model cognitive orchestration by introducing:
- **Autonomous Three-Gate Cadence**: Tick Gate ($\Delta T \ge 25$) $\rightarrow$ Mutation Gate ($M \ge 10$) $\rightarrow$ Lock Gate (`.consolidate-lock`).
- **Emergency Context Budget Pressure Interceptor**: Triggers immediate memory compaction whenever working memory reaches $\ge 400$ tokens ($\approx 78\%$ saturation), guaranteeing zero context overflow.
- **Host-Authoritative 4-Phase Consolidation**: Orient $\rightarrow$ Gather (with SHA-256 provenance hashes) $\rightarrow$ Consolidate (deterministic state replay & contradiction elimination) $\rightarrow$ Prune & Index (`INDEX.md` $\le 128$ tokens).
- **Demand-Driven Recall Affordance**: Task agent pulls specific entity cards ($\le 48$ tokens) on demand via GBNF-governed `ACTION: RECALL <entity_id>`.

---

## 2. Falsifiable Hypotheses

### Hypothesis 1: Long-Horizon Temporal Consistency & Amnesia Elimination ($H_1$)
Under Host-Authoritative AutoDream consolidation and GBNF-governed recall affordances, small models (`Qwen3.5-2B-Q4_K_M`) will achieve **$\ge 90.0\%$ task completion** across extended multi-session horizons ($T = 20-50$ steps), delivering an absolute gain of **$\ge +50.0\%$** over unassisted FIFO sliding window baselines by eliminating historical amnesia.

### Hypothesis 2: Absolute Budget Ceiling & Zero Overflow Invariant ($H_2$)
With the Emergency Context Budget Pressure Interceptor active at $\ge 400$ tokens, **exactly 100.0% of forward-pass turns** across the entire 40-case long-horizon benchmark will strictly adhere to the native prompt ceiling $\le 512$ tokens (mean prompt budget $\le 384$ tokens).

### Hypothesis 3: Zero-Hallucination Memory Integrity & Sub-Second Latency SLA ($H_3$)
Because memory updates and contradiction resolutions are computed deterministically by the Host from verified environment return values rather than LLM text generation:
- The factual contradiction rate in persisted memory cards will be **exactly 0.0%**.
- Host consolidation overhead will remain **$< 1.0\text{ ms}$** per cycle.
- Mean turn latency for the Task Agent will remain **$< 1000\text{ ms}$** on local `llama-server.exe` hardware.

---

## 3. Scope & Non-Goals

### In Scope
1. Implementation of `ConsolidationLock` (file mutex, stale lock detection, rollback support).
2. Implementation of `AutonomousAutoDreamTrigger` (Tick Gate, Mutation Gate, Lock Gate, Emergency Pressure Interceptor).
3. Implementation of `ProvenanceTracker` and `DeterministicConflictResolver` (authoritative state replay, contradiction pruning).
4. Implementation of `HostMemoryEngine` (4-phase consolidation lifecycle, entity cards $\le 48$ tokens, `INDEX.md` $\le 128$ tokens).
5. Implementation of `RecallCoordinator` integrating `ACTION: RECALL <id>` into `CognitiveOrchestrator` via dynamic GBNF.
6. 40-case long-horizon synthetic benchmark ($T=20-50$) across 3 domains (Code Refactoring, Ledger Operations, System Registry).
7. Dual-track evaluation: Track 1 (Simulator) and Track 2 (Real Model Inference on `Qwen3.5-2B`).

### Explicit Non-Goals
1. No fine-tuning, LoRA, or weight alterations to language models.
2. No external runtime dependencies (zero third-party vector databases, embeddings, or heavyweight frameworks; 100% Python Standard Library).
3. No speculative dynamic microworld physics or autonomous multi-agent simulation (deferred to MN-017 and MN-Final).
4. No code promotion to `src/mong_nhiem/` prior to Gate D disposition review.
