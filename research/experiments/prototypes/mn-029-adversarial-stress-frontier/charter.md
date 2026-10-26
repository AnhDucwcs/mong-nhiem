# Gate A Research Charter: Milestone MN-029

## 1. Context & Problem Statement

Prior Mộng Nhiễm milestones (MN-001 through MN-028) established empirical governance for small language models ($\le 4\text{B}$) under deterministic, synchronized microworlds. In those environments:
1. Environment physics froze deterministically while the SLM completed its $150\text{ ms} - 250\text{ ms}$ inference turn.
2. Sensor telemetry reflected ground truth with zero stuck-at hardware faults.
3. Preconditions were validated strictly at step $T_0$ without evaluating multi-step cascading traps.
4. Human supervisory input adhered to well-formed, non-contradictory command strings.
5. Emitted operational actions and communicative prose were assumed to be semantically aligned.
6. Multi-agent concurrency arbiters prevented race conditions but did not evaluate circular `STANDBY` livelocks.

Milestone MN-029 evaluates the hypothesis that unconstrained SLMs coupled with 1-step static pre-condition gates fail catastrophically when subjected to asynchronous physical mutations, multi-step lookahead traps, byzantine sensor equifinality, bimodal semantic divergence, and FFI boundary stress. It formulates and tests Host-authoritative architectural defenses that enforce absolute state integrity without increasing latency beyond the $1000\text{ ms}$ SLA or working memory beyond $512\text{ tokens}$.

---

## 2. Formal Research Questions ($Q_1 \to Q_9$)

- **$Q_1$ (Delayed Cascading Dilemma):** Can forward invariant simulation ($k=4$ steps) in the native Host core prevent an SLM from selecting actions that satisfy $T_0$ preconditions but irrevocably deadlock the physical system at $T+4$?
- **$Q_2$ (Mid-Inference State Invalidation):** Does a Commit-Time Live State Double-Check Gate eliminate physical boundary breaches when high-velocity state degradation occurs during the SLM's $200\text{ ms}$ inference interval?
- **$Q_3$ (Byzantine Sensor & Equifinality Trap):** Does enforcing mandatory diagnostic `PROBE` preconditions prevent premature catastrophic actuation when abductive DAG traversal yields conflicting root causes under stuck sensor telemetry?
- **$Q_4$ (Chaotic Human Operator ASR):** Can a bounded reasoning-first GBNF grammar with dynamic entity enums accurately distill contradictory, self-correcting human speech transcripts into the intended terminal action?
- **$Q_5$ (Sub-Threshold Cumulative Drift):** Does a continuous telemetry residual accumulator prevent long-horizon catastrophic failure by retaining sub-threshold micro-fluctuations otherwise pruned by episodic compaction?
- **$Q_6$ (Bimodal Action-Communication Desync):** Can a Host-authoritative structured intent arbiter detect and intercept semantic contradictions between emitted machine actions and communicative prose with $0.0\%$ false-positive rate on complex natural language?
- **$Q_7$ (Multi-Agent Cyclic Livelock):** Does a cyclic wait-for dependency detector cleanly resolve deadlocks caused by mutually dependent valid `STANDBY` actions across concurrent agents?
- **$Q_8$ (FFI Boundary Robustness & Soak Stability):** Does a panic-safe, Copy-on-Write C-ABI wrapper guarantee $0.0\text{ MB}$ memory leakage and zero process crashes over $100,000$ consecutive continuous state engine ticks?
- **$Q_9$ (Three-Way Transactional Crash Recovery):** Does a three-way transactional epoch protocol (Rust State $\leftrightarrow$ Python DAG $\leftrightarrow$ Llama.cpp Slot Cache) ensure clean recovery to tick $N-1$ without state corruption following mid-tick process termination?

---

## 3. Mathematical Hypotheses Formulation ($H_1 \to H_9$)

- **$H_1$ (Lookahead Projection):** Let $A(S_t)$ be the set of $T_0$-admissible actions. Let $\Phi(S_t, a, k)$ project state trajectory across $k=4$ steps. An invariant check $\bigwedge_{i=1}^k \mathcal{I}(\Phi(S_t, a, i))$ prunes trajectory deadlocks, increasing long-horizon survival from $0.0\%$ to $\ge 95.0\%$.
- **$H_2$ (Commit-Time Validation):** Let $t_{\text{call}}$ be the prompt dispatch timestamp and $t_{\text{ret}}$ be the completion timestamp ($\Delta t \approx 200\text{ ms}$). Enforcing $\mathcal{I}(S(t_{\text{ret}}), a)$ at commit time guarantees zero invariant breaches ($B = 0$).
- **$H_3$ (Diagnostic Probe Forcing):** When the abductive explanation set $|\mathcal{E}| > 1$ and sensor confidence $C(s) < 1.0$, masking all mutating actions and injecting $\text{Affordance}(\text{PROBE})$ achieves $100.0\%$ diagnostic disambiguation.
- **$H_4$ (Reasoning-First Dynamic Enum):** Constraining GBNF generation to `REASONING: [^\n]{1,80}\nACTION: <verb> <enum>` achieves $\ge 95.0\%$ intent extraction accuracy on colloquial, self-negating operator transcripts.
- **$H_5$ (Cumulative Residual Accumulation):** Maintaining rolling integral $R_i = \int_{t-W}^t |x_i(\tau) - \bar{x}_i|\,d\tau$ elevates sub-threshold drift to a top-priority Fact Card, preventing $100.0\%$ of cumulative structural failures.
- **$H_6$ (Structured Intent Arbiter):** Mapping emitted communication to categorical intent tags (`COMMUNICATE [<CLASS>:<INTENT>]: "..."`) achieves $100.0\%$ detection of contradictory action-communication pairs with $0.0\%$ false positives on contrastive natural language.
- **$H_7$ (Cyclic Wait Preemption):** Tracking the directed wait graph $G_W = (V, E)$ and forcing priority preemption when cycle length $\ge 3\text{ ticks}$ eliminates $100.0\%$ of multi-agent livelocks.
- **$H_8$ (Zero-Leak Transactional FFI):** Enforcing strict pointer validation, `!dt.is_finite()`, and CoW scratchpads guarantees zero unwinding panics and $\Delta\text{RSS} < 0.5\text{ MB}$ over $100,000$ iterations.
- **$H_9$ (Three-Way Epoch Invalidation):** Synchronizing `epoch_id` across state engines and triggering `POST /slots/{slot_id}?action=erase` upon crash recovery eliminates $100.0\%$ of stale KV attention contamination.

---

## 4. Architectural Invariants & Governance

1. **Raison d'Être Invariant:** The SLM remains an isolated reasoning engine emitting candidate tokens under GBNF grammars. The Host retains absolute authority over state integrity, invariant enforcement, and physical actuation.
2. **Anti-Falsification Protocol:** All 9 adversarial scenarios must be executed against the unhardened baseline first. Failure baseline traces must be archived in `runs/` before any defensive patch is marked verified.
3. **Budget Ceilings:** Mean turn latency $< 1000\text{ ms}$, peak working memory $\le 512\text{ tokens}$, zero loose JSON files in Git repository.
