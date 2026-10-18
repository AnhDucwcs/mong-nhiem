# Milestone Charter: MN-026 — Multi-Stage Cognitive Capstone Governance, Semantic Invariant Hardening, and Abductive Cross-Partition Causal Synthesis

## 1. Executive Summary & Research Motivation

Mộng Nhiễm is an open-source empirical research and operating platform engineered to endow Small Language Models (SLMs, $< 4\text{B}$) with robust, stateful, and causally sound operational capabilities over complex, non-stationary information spaces. In accordance with Mộng Nhiễm's foundational architectural principles:
1. **Raison d'Être Invariant:** The LLM is maintained strictly as an unchanged, black-box stochastic reasoning engine emitting structured actions; the Host maintains absolute authority over physical state integrity, access control, and provenance auditing.
2. **Minimalism & Resource Bounds:** Systems must operate reliably within strict local hardware constraints ($\le 4\text{GB}$ VRAM, prompt working memory $\le 512\text{ tokens}$, turn latency $< 1000\text{ ms}$). Speculative multi-model VRAM loading is rejected in favor of virtualized cognitive heterogeneity executed on a single qualified SLM instance.
3. **Controlled Experimental Testbed:** Microworlds serve as mathematically formal laboratory environments to isolate, stress-test, and falsify specific cognitive architecture hypotheses ($H_1, H_2, \dots$) prior to open-corpus expansion.

Previous research milestones verified isolated cognitive mechanisms:
- **MN-022:** Asynchronous Swarm Consensus and dynamic DAG pruning, but restricted to purely structural GBNF syntax filtering and uniform turn latencies.
- **MN-023:** Asymmetric observation masking, but restricted to localized, independent causal partitions.
- **MN-024:** Multi-hop causal maintenance over extended temporal horizons under continuous entropy decay.
- **MN-025:** Topological schema isomorphism and belief conflict reconciliation, exposing an emergent capacity for Rational Abstention that remained informal and uncontracted.

Milestone **MN-026** constitutes the **Grand Capstone & Hardening Milestone** of Mộng Nhiễm's Microworld and Distributed Cognitive Governance phase. Instead of monolithic composite testing from turn zero, MN-026 is partitioned into **four sequential empirical stages**:
1. **Stage 1 (Semantic Invariant Hardening & Virtual Latency Skew):** Rectifies MN-022's semantic blindness by deploying a Host Semantic Invariant Gate and evaluating asynchronous turn skew ($100\text{ ms} \leftrightarrow 800\text{ ms}$) on 1 SLM.
2. **Stage 2 (Hidden Inter-Partition Causal Coupling & Abductive Tracing):** Rectifies MN-023's local independence by introducing cross-partition invisible side-effects resolved via backward symptom-to-cause reachability.
3. **Stage 3 (Formal Dual-Objective Decision Contract):** Rectifies MN-025's ad-hoc abstention by formally contracting Physical Task Completion ($M_{\text{phys}}$) alongside Rational Decision Safety ($M_{\text{safe}}$).
4. **Stage 4 (Composite Capstone Stress-Test):** Synthesizes all mechanisms into a unified, high-stress cyber-physical microworld to definitively close the microworld phase.

---

## 2. Research Questions & Formal Hypotheses

### Primary Research Questions
- **RQ1 (Semantic Hallucination Interception):** Can a host-authoritative Semantic Invariant Gate intercept 100% of syntactically valid yet physically impossible action proposals without inflating the prompt working memory beyond 512 tokens?
- **RQ2 (Virtual Asymmetric Latency Resilience):** When multiple agent roles executed on a single SLM experience asymmetric cognitive delays ($100\text{ ms}$ reactive vs $800\text{ ms}$ deliberative), does the Host Lease Arbiter eliminate all concurrency collisions and race overwrites?
- **RQ3 (Abductive Cross-Partition Resolution):** When an unobserved root action in Partition A generates secondary physical distress in Partition B, can Host Abductive Causal Tracing synthesize symptom signals into actionable mitigation directives without cross-partition context pollution?
- **RQ4 (Dual-Objective Rational Restraint):** Under a balanced corpus of 50% solvable crises and 50% deceptive decoy/unsolvable traps, does the SLM achieve high physical task resolution while maintaining zero reckless actions on deceptive traps?

### Formal Mathematical Hypotheses

- **$H_1$ (Dual-Objective Physical Task Resolution):**
  Across all solvable scenarios ($N_{\text{solvable}} = 40$), Arm 3 achieves an authoritative physical task resolution rate:
  $$M_{\text{phys}}(\text{Arm 3}) = \frac{N_{\text{resolved}}}{N_{\text{solvable}}} \ge 85.0\% \quad (\text{Falsified if } M_{\text{phys}} < 85.0\%)$$
- **$H_2$ (Dual-Objective Decision Safety / Rational Abstention):**
  Across all deceptive decoy and structurally unsolvable trap scenarios ($N_{\text{trap}} = 40$), Arm 3 achieves 100% safe abstention:
  $$M_{\text{safe}}(\text{Arm 3}) = \frac{N_{\text{abstained}}}{N_{\text{trap}}} \equiv 100.0\% \quad (\text{Falsified if } M_{\text{safe}} < 100.0\%)$$
- **$H_3$ (Semantic Invariant Breach Suppression):**
  Across all evaluated turns across all 4 stages, the number of committed physical invariant breaches caused by semantic hallucination equals zero:
  $$B_{\text{semantic}}(\text{Arm 3}) \equiv 0 \quad (\text{Falsified if } B_{\text{semantic}} > 0)$$
- **$H_4$ (Abductive Causal Resolution Efficacy):**
  In scenarios involving hidden cross-partition coupling, the rate of successful symptom-to-cause resolution satisfies:
  $$R_{\text{abductive}}(\text{Arm 3}) \ge 90.0\% \quad (\text{Falsified if } R_{\text{abductive}} < 90.0\%)$$
- **$H_5$ (Asynchronous Concurrency Safety Under Virtual Latency Jitter):**
  Under simulated asymmetric turn latency skew ($\tau_i \in [100\text{ ms}, 800\text{ ms}]$), committed concurrency collisions equal zero:
  $$C_{\text{collision}}(\text{Arm 3}) \equiv 0 \quad (\text{Falsified if } C_{\text{collision}} > 0)$$
- **$H_6$ (Cognitive Token Budget & Sub-Second Latency SLA):**
  Working prompt memory stays bounded at or below 512 tokens with sub-second mean turn inference latency:
  $$\max \text{Tokens}_t(\text{Arm 3}) \le 512\text{ tokens}, \quad \bar{T}_{\text{turn}}(\text{Arm 3}) < 1000\text{ ms}$$

---

## 3. Experimental Methodology & Arms Definition

### Controlled Experimental Arms

1. **Arm 1 (Monolithic Flat Baseline):**
   - Flat unsegmented system state prompts without 3-tier partitioning.
   - Raw greedy decoding without semantic gating, abductive tracing, or abstention affordances.
   - Evaluates baseline vulnerability to semantic hallucinations, cross-partition amnesia, and reckless trap execution.
2. **Arm 2 (Uncoordinated Control):**
   - Phased execution with GBNF structural grammar logit masking (`ACTION: <VERB> <TARGET>`).
   - Lacks the Host Semantic Invariant Gate (accepts any syntactically valid proposal) and lacks Abductive Causal Tracing (partitions remain epistemically blind to cross-partition dependencies).
3. **Arm 3 (Host Cognitive Capstone Engine):**
   - Full host cognitive governance on 1 SLM instance:
     - `SemanticInvariantGate`: Vector-clock and causal DAG precondition validation.
     - `AbductiveCausalTracer`: Backward reachability mapping symptoms to concealed root causes.
     - `VirtualAsymmetricJitterArbiter`: Optimistic lease arbitration with variable cognitive latency.
     - `DualObjectiveAffordanceEngine`: Explicit `ABSTAIN` / `REFUSE` affordances with Typed Fact Cards.

### Evaluation Tracks

- **Track 1 (Host Simulator — Mathematical & Topological Verification):**
  - Exhaustive state-space simulation across all $N = 80$ standardized scenarios ($240$ total episodes).
  - Verifies reachability, lease safety, and abductive inference mechanics.
- **Track 2 (Real Model Inference — Pure Open-Weights `Qwen3.5-2B` on `llama-server.exe`):**
  - Full neural inference runs on local hardware (port 18502) across all $N = 80$ scenarios ($240$ total episodes).
  - Verifies real inductive biases, token budget compliance ($\le 512$ tokens), and latency SLA ($< 1000\text{ ms}$).

---

## 4. Scope & Non-Goals

### In Scope
- Single open-weights language model (`Qwen3.5-2B-Q4_K_M.gguf`) hosted on local `llama-server.exe`.
- Virtual multi-role heterogeneity (Scout, Operator, Arbiter) executed via stateless forward passes.
- Standardized $N = 80$ scenarios across Nuclear Core Cooling, Orbital Life Support, and Regional Smart Microgrid.
- Dual-Objective quantitative evaluation ($M_{\text{phys}}$ and $M_{\text{safe}}$).
- Standard library `.zip` evidence packaging under the Zero Loose File Bloat Protocol.

### Non-Goals
- Concurrent loading of multiple heavy model weights into VRAM (deferred to sequential post-capstone validation).
- Interactive user interfaces or graphical game engines (strictly symbolic microworld state).
- Silent promotion of experimental code into `src/mong_nhiem/` prior to Phase 2 Gate D review.
