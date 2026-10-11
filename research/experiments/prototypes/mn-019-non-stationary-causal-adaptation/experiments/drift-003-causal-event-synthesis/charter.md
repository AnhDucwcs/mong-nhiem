# Stage 3 Gate A Research Charter (`drift-003-causal-event-synthesis`)

## 1. Executive Summary & Research Question

Can a lightweight language model ($< 4\text{B}$ parameters, evaluated on `Qwen3.5-2B-Q4_K_M.gguf`), governed by a Dual-Engine Cognitive Host equipped with **DAG Causal Rule Induction**, **Isolated Counterfactual Sandbox Projections**, and **Proactive Affordance Gating**, proactively navigate latent causal traps and non-stationary environment couplings without relying on reactive error rollback?

---

## 2. Formal Hypotheses Formulation

1. **Hypothesis $H_1$ (Efficacy under Non-Stationary Causal Coupling):**  
   Under 60 standardized benchmark cases containing hidden downstream side effects and latent coupling traps, Arm 3 (Counterfactual Causal Synthesis Host) achieves overall task resolution:
   $$\text{SR}_{\text{Arm3}} \ge 85.0\% \quad (51/60)$$
   and decisively out-resolves Arm 2 (Reactive Host Control) and Arm 1 (Flat Baseline):
   $$\Delta_{\text{Arm3} - \text{Arm2}} \ge +40.0\%, \quad \Delta_{\text{Arm3} - \text{Arm1}} \ge +80.0\%$$
   *Falsification Threshold:* $\text{SR}_{\text{Arm3}} < 85.0\%$, or $\Delta_{\text{Arm3} - \text{Arm2}} < +40.0\%$.

2. **Hypothesis $H_2$ (Out-of-Distribution Causal Generalizability):**  
   On Out-of-Distribution scenarios ($N=30$) with novel latent causal couplings and unobserved failure cascades, Arm 3 maintains:
   $$\text{SR}_{\text{OOD}} \ge 80.0\% \quad (24/30)$$
   *Falsification Threshold:* $\text{SR}_{\text{OOD}} < 80.0\%$.

3. **Hypothesis $H_3$ (Proactive Trap Avoidance & Invariant Integrity):**  
   Arm 3 proactively intercepts and bypasses $\ge 80.0\%$ of latent causal traps before execution, preventing state corruption and maintaining zero committed conservation breaches or illegal schema violations:
   $$\sum N_{\text{committed\_violations}} = 0, \quad \frac{N_{\text{proactive\_bypass}}}{N_{\text{traps}}} \ge 0.80$$
   *Falsification Threshold:* Any committed violation ($> 0$), or proactive bypass rate $< 80.0\%$.

4. **Hypothesis $H_4$ (Declarative Causal Compaction & SLA Compliance):**  
   AutoDream episodic memory consolidation synthesizes structured Causal Invariant Cards while preserving compaction ratio $\ge 70.0\%$, forward prompt token ceiling $\le 512$ tokens (mean $\le 384$ tokens), and mean turn latency $< 1000\text{ ms}$:
   $$\text{Compaction} \ge 70.0\%, \quad \max(\text{Prompt Tokens}) \le 512, \quad \text{mean}(\text{Latency}) < 1000\text{ ms}$$
   *Falsification Threshold:* Compaction $< 70.0\%$, Max prompt tokens $> 512$, or mean turn latency $\ge 1000\text{ ms}$.

---

## 3. Scope & Non-Goals

- **In Scope:**
  - Causal rule induction from the hash-chained `CausalEventLog` DAG.
  - Isolated counterfactual candidate rollouts using `simulate_counterfactual_step`.
  - Proactive GBNF grammar affordance pruning to eliminate latent causal traps before dispatch.
  - Causal Invariant Card synthesis in AutoDream memory.
  - Track 1 deterministic simulation across 60 standardized cases in 4 domains.
- **Out of Scope:**
  - Model weight fine-tuning or gradient backpropagation (zero-shot host inference invariant).
  - Promotion of experimental prototype code into `src/mong_nhiem/` (quarantined until Gate D disposition).
