# Charter: Stage 1 — Continuous Parametric Drift Adaptation (`drift-001-parametric-adaptation`)

## 1. Executive Summary & Gate A Research Statement

- **Milestone Parent:** MN-019 (Continuous Non-Stationary Domain Drift & Dynamic Adaptation)
- **Sub-Experiment ID:** `drift-001-parametric-adaptation`
- **Primary Research Question:** Can a Dual-Engine Cognitive Host equipping a lightweight small language model (`Qwen3.5-2B-Q4_K_M`, $< 4\text{B}$) with real-time Discrepancy Monitoring and Dynamic Affordance Regeneration sustain high task resolution ($\ge 85.0\%$) and zero committed physical conservation breaches when microworld transition dynamics undergo continuous non-stationary parametric drift ($N=60$ across 4 heterogeneous domains), without model fine-tuning?

---

## 2. Formal Hypotheses Formulation

1. **Hypothesis $H_1$ (Resilience under Coupled Non-Stationary Drift):**  
   Under continuous parametric drift across 60 scenarios in 4 heterogeneous domains, Arm 3 (Dynamic Dual-Engine Host with Discrepancy Monitoring and Dynamic Affordance Regeneration) will achieve an overall task success rate:
   $$\text{SR}_{\text{Arm3}} \ge 85.0\% \quad (51/60)$$
   demonstrating a statistically decisive margin over static controls:
   $$\Delta_{\text{Arm3} - \text{Arm2}} \ge +50.0\%, \quad \Delta_{\text{Arm3} - \text{Arm1}} \ge +80.0\%$$
   *Falsification Criteria:* Falsified if $\text{SR}_{\text{Arm3}} < 85.0\%$ or if the comparative margin over Arm 2 falls below $+50.0\%$.

2. **Hypothesis $H_2$ (Out-of-Distribution Generalizability):**  
   On the 30 Out-of-Distribution (OOD) scenarios characterized by coupled exponential decay, harmonic load oscillations, and cascading compound shock clusters, Arm 3 will maintain:
   $$\text{SR}_{\text{OOD}} \ge 80.0\% \quad (24/30)$$
   *Falsification Criteria:* Falsified if $\text{SR}_{\text{OOD}} < 80.0\%$.

3. **Hypothesis $H_3$ (Physical Conservation Invariant Preservation):**  
   Across all 60 scenarios and all turns ($T = 150 - 250$ ticks), the Host Conservation Guard will intercept 100% of drift-induced delayed traps and execute atomic rollback via Memento, resulting in:
   $$N_{\text{committed\_breaches}} = 0$$
   *Falsification Criteria:* Falsified if $N_{\text{committed\_breaches}} > 0$.

4. **Hypothesis $H_4$ (Resource Budget and Latency SLA Invariance):**  
   Throughout all execution episodes, the forward-pass prompt token length and turn latency will remain strictly bounded:
   $$\max(\text{Prompt Tokens}) \le 512, \quad \text{mean}(\text{Prompt Tokens}) \le 384, \quad \text{mean}(\text{Latency}) < 1000\text{ ms}$$
   *Falsification Criteria:* Falsified if any turn prompt exceeds 512 tokens or mean latency exceeds $1000\text{ ms}$.

---

## 3. Experimental Methodology & Arms

- **Arm 1 (Flat Baseline):** Unconstrained model output without GBNF grammar or Host Discrepancy Monitoring.
- **Arm 2 (Static Memory Control):** MN-018 architecture (Static GBNF DAG + AutoDream) operating under nominal physical assumptions without drift detection or affordance mutation.
- **Arm 3 (Dynamic Dual-Engine Host):** Host Discrepancy Monitor calculating $D_t = |s_{\text{actual}} - s_{\text{nominal}}|$, active GBNF affordance pruning under degraded parameters, compensatory affordance injection, and Memento rollback.

---

## 4. Subject Model & Workstation Specification

- **Primary Evaluated Model:** `Qwen3.5-2B-Q4_K_M.gguf`
- **Runtime:** `llama-server.exe` (context window: 2,048 tokens, temperature: 0.0, seed: 42)
- **Workstation Configuration:** NVIDIA GeForce RTX 3050 Laptop GPU (4,096 MiB VRAM), AMD Ryzen 7 5800H, Windows 11.
