# Gate B Evaluation Contract: Milestone MN-025

## 1. Frozen Evaluation Clauses ($M_1 \to M_{10}$)

This evaluation contract formally freezes the quantitative acceptance criteria for Milestone MN-025 across all three sub-stages (Stage 1 Transfer, Stage 2 Belief Conflict, Stage 3 Stochastic Dynamic Topology). Evaluation is executed under Dual-Track protocol (Track 1 Host Simulator, Track 2 Real Model Inference on local `Qwen3.5-2B-Q4_K_M.gguf`).

| Clause ID | Metric Description | Frozen Acceptance Bound | Mandatory / Optional | Falsification Trigger | Technical Rationale & Mathematical Justification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **M1** | Cross-Domain Task Resolution Rate | $\ge 85.0\%$ | Mandatory | $S_{\text{transfer}} < 85.0\%$ | Validates zero-shot domain generalization without target-specific fine-tuning or prompt bloat. |
| **M2** | Transfer Speedup Delta ($\Delta T$) | $\ge +40.0\%$ | Mandatory | $\Delta T < 40.0\%$ | Based on Taylor & Stone (2009). Eliminating at least two trial-and-error probing hops in 4-hop cascades guarantees statistical significance ($p < 0.001$). |
| **M3** | Negative Transfer Breach Rate | $\equiv 0$ breaches | Mandatory | $B_{\text{negative}} > 0$ | Host Invariant Guard must intercept $100\%$ of erroneous domain analogies before state corruption occurs. |
| **M4** | Dialectic Conflict Convergence | $\ge 90.0\%$ | Mandatory | $C_{\text{dialectic}} < 90.0\%$ | Asymmetric agent perspectives must converge to consensus ($d(\mathcal{G}_A, \mathcal{G}_B) \to 0$) without entering infinite deadlock cycles. |
| **M5** | Stochastic Recovery SLA | $\le 6$ ticks | Mandatory | $T_{\text{recovery}} > 6$ ticks | System must restore physical parameters to safety margins within 6 ticks following non-linear Poisson shocks. |
| **M6** | Committed Physical Breaches | $\equiv 0$ | Mandatory | $B_{\text{physical}} > 0$ | Absolute safety invariant: Zero tolerance for physical boundary violations across both immediate actions and latent delayed-onset time-bomb traps ($T \ge T_{\text{crit}}$). |
| **M7** | Committed Concurrency Collisions | $\equiv 0$ | Mandatory | $C_{\text{collisions}} > 0$ | Host MultiResourceArbiter must enforce mutual exclusion and eliminate race collisions under multi-agent conflict. |
| **M8** | Working Prompt Token Ceiling | $\le 512$ tokens | Mandatory | $\text{Tokens}_{\max} > 512$ | Strict working memory boundedness via 3-Tier Fact Card compaction (target $\le 200$ tokens). |
| **M9** | Sub-Second Turn Latency | $< 1000\text{ ms}$ | Mandatory | $\bar{L}_{\text{turn}} \ge 1000\text{ ms}$ | Operational feasibility on single local GPU/CPU hardware. |
| **M10** | Non-Monotonic Anchor Demotion | $\equiv 100.0\%$ | Mandatory | $D_{\text{demotion}} < 100.0\%$ | All falsified Tier 1 anchors must be purged and tombstoned immediately upon regime shift with zero cognitive inertia. |

## 2. Operational Rules & Anti-Falsification Invariants

In strict adherence to `AGENTS.md`:
1. **Independent Post-Generation Verification:** Automated runner summaries and reports must be verified directly against underlying raw execution traces (`audit_logs.zip`).
2. **Strict Clause-by-Clause Falsification:** If ANY metric breaches a contract bound, the corresponding clause MUST be marked `FAIL`. No asterisks, footnotes, or soft rationalizations are permitted.
3. **Zero Retroactive Threshold Alteration:** Frozen thresholds cannot be relaxed or altered post-run.
4. **Zero Loose File Bloat Protocol:** All episode execution traces must be archived into standard library `audit_logs.zip` archives with zero loose JSON logs committed to Git.
5. **Hardware Isolation:** Execution is performed on local `llama-server.exe` running `Qwen3.5-2B-Q4_K_M.gguf` on port 18502 (zero external cloud API calls).
