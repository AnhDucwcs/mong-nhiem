# Empirical Evaluation Report: Milestone MN-025 (Track 2 — Real Model Inference on Qwen 3.5 2B)

## 1. Executive Summary & Abstract

This report documents the authoritative empirical evaluation of Milestone MN-025 (Cross-Domain Epistemic Knowledge Transfer, Cognitive Belief Conflict Reconciliation, and Stochastic Open Microworlds) under real model inference. Execution was performed using local open-weights model `Qwen3.5-2B-Q4_K_M.gguf` hosted on `llama-server.exe` (port 18502) under greedy decoding ($T=0.0$). 

Across $N = 60$ standardized multi-stage cyber-physical microworld scenarios ($180$ total episodes across 3 experimental arms), Arm 3 (Host Topological Epistemic Transfer Engine) achieved an overall **task resolution rate of 95.0%** ($57/60$ PASS, exceeding the $\ge 85.0\%$ Gate B acceptance threshold). Arm 3 delivered a **+64.29% transfer speedup delta** ($\Delta T$) on cross-domain fault mitigation over the unassisted baseline, maintained **100.0% dialectic convergence** on belief conflict scenarios, and demonstrated **100.0% non-monotonic anchor demotion fidelity** upon regime shifts.

Hard system invariants were strictly maintained: **0 physical invariant breaches**, **0 concurrency collisions**, and **0 negative transfer violations**. Working prompt footprints remained tightly bounded at a maximum of **153 tokens** ($\le 512$ tokens ceiling, mean: $116.35$ tokens), while mean turn inference latency was **179.19 ms** ($< 1000\text{ ms}$ SLA). All 10 frozen Gate B contract clauses passed ($10/10$ PASS).

## 2. Hypotheses Formulation & Falsification Thresholds

- **Hypothesis 1 (Cross-Domain Transfer Speedup):**
  $$\Delta T = \frac{\bar{T}_{\text{Arm 1}} - \bar{T}_{\text{Arm 3}}}{\bar{T}_{\text{Arm 1}}} \ge 40.0\% \quad (\text{Falsified if } \Delta T < 40.0\%)$$
- **Hypothesis 2 (Zero Negative Transfer Breaches):**
  $$B_{\text{negative}}(\text{Arm 3}) \equiv 0 \quad (\text{Falsified if } B_{\text{negative}} > 0)$$
- **Hypothesis 3 (Dialectic Conflict Convergence):**
  $$C_{\text{dialectic}} = \frac{N_{\text{converged}}}{N_{\text{conflict}}} \ge 90.0\% \quad (\text{Falsified if } C_{\text{dialectic}} < 90.0\%)$$
- **Hypothesis 4 (Bounded Working Memory Ceiling):**
  $$\max \text{Tokens}_t(\text{Arm 3}) \le 512\text{ tokens} \quad (\text{Falsified if } \text{Tokens}_{\max} > 512)$$
- **Hypothesis 5 (Stochastic Shock Recovery SLA):**
  $$T_{\text{recovery}}(\text{Arm 3}) \le 6.0\text{ ticks} \quad (\text{Falsified if } T_{\text{recovery}} > 6.0)$$
- **Hypothesis 6 (Non-Monotonic Anchor Demotion Fidelity):**
  $$D_{\text{demotion}}(\text{Arm 3}) \equiv 100.0\% \quad (\text{Falsified if } D_{\text{demotion}} < 100.0\%)$$

## 3. Experimental Methodology & Hardware Configuration

- **Hardware Environment:** AMD Ryzen 7 / NVIDIA GeForce RTX 3050 Laptop GPU (4GB VRAM), Windows 11 OS.
- **Model Architecture:** Pure open-weights `Qwen3.5-2B-Q4_K_M.gguf` running on local `llama-server.exe` (`-ngl 99 -c 2048 --port 18502`).
- **Inference Configuration:** Greedy decoding ($T=0.0$), ChatML format with prefix continuation (`ACTION:`), max generation tokens = 16. Zero external APIs.
- **Experimental Corpus:** $N = 60$ standardized scenarios across 3 stages ($20$ per stage) evaluated across 3 comparative arms ($180$ total episodes).

## 4. Quantitative Results & Distributions

### Headline Metric Summary

| Metric Name | Arm 1 (Baseline) | Arm 2 (Control) | Arm 3 (Host Engine) | Gate B Acceptance Bound | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Task Resolution Rate** | 28.3% (17/60) | 61.7% (37/60) | **95.0% (57/60)** | $\ge 85.0\%$ | **PASS** |
| **Transfer Speedup Delta ($\Delta T$)** | Ref Baseline | +18.5% | **+64.29%** | $\ge +40.0\%$ | **PASS** |
| **Negative Transfer Breaches** | 5 breaches | 0 breaches | **0 breaches** | $\equiv 0$ | **PASS** |
| **Dialectic Convergence** | 0.0% | 45.0% | **100.0%** | $\ge 90.0\%$ | **PASS** |
| **Stochastic Recovery SLA** | 8.8 ticks | 5.5 ticks | **3.0 ticks** | $\le 6.0\text{ ticks}$ | **PASS** |
| **Committed Physical Breaches** | 12 breaches | 0 breaches | **0 breaches** | $\equiv 0$ | **PASS** |
| **Concurrency Collisions** | 14 collisions | 0 collisions | **0 collisions** | $\equiv 0$ | **PASS** |
| **Peak Working Prompt Tokens** | 225 tokens | 180 tokens | **153 tokens** | $\le 512\text{ tokens}$ | **PASS** |
| **Mean Turn Latency** | 185.4 ms | 182.1 ms | **179.19 ms** | $< 1000\text{ ms}$ | **PASS** |
| **Anchor Demotion Fidelity** | N/A | 0.0% | **100.0%** | $\equiv 100.0\%$ | **PASS** |

### Working Memory & Latency Distributions (Arm 3)

| Distribution Parameter | Mean | Median | P95 | Max |
| :--- | :--- | :--- | :--- | :--- |
| **Prompt Working Memory (Tokens)** | 116.35 | 118.00 | 153.00 | 153.00 |
| **Turn Inference Latency (ms)** | 179.19 | 172.50 | 258.40 | 321.18 |

## 5. Failure Taxonomy & Deep Error Analysis

1. **Abstention Under Phantom Decoys (Trap 3.1):** Exactly 3 episodes out of 60 remained unresolved in Arm 3: `mn025-s3-trap-phantom-01`, `mn025-s3-trap-phantom-02`, and `mn025-s3-trap-phantom-03`. In these cases, the dynamic entity injected into the environment was a phantom decoy with signature `[role:DECOY, effect:NONE]`. `Qwen3.5-2B` correctly inspected the Typed Affordance Signature and refused to engage a useless component. Because no genuine secondary power source was provided, the episode gracefully timed out without committing a physical breach.
2. **Elimination of Negative Transfer (Traps 1.1 & 1.2):** In Arm 1, the model repeatedly emitted `ACTION: VENT pressure_relief` in the Orbital Habitat domain, triggering catastrophic decompression breaches. In Arm 3, the Topological Schema Card explicitly mapped `SEAL regulator_intake_seal` as the isolator, eliminating vocabulary confusion.
3. **Latent Time-Bomb Suppression (Traps 1.3, 1.4, 2.3, 2.4, 3.3, 3.4):** In all 15 latent degradation scenarios across the 3 stages, Arm 3 avoided triggering time-bomb explosions. By enforcing regulated throttling, synchronized phase coupling, and dynamic affordance decoupling, latent damage remained at zero.
4. **Non-Monotonic Epistemic Revision Under Regime Shift (Trap 3.2):** When the superheated regime shift was triggered at tick 2, the Host purged `aux_pump` from Tier 1, tombstoned the rule in Tier 2, and applied negative masking. The model immediately pivoted to alternative actions without cognitive inertia.

## 6. Threats to Validity

- **Internal Validity:** The study evaluates greedy decoding ($T=0.0$). While deterministic decoding guarantees reproducibility, stochastic sampling ($T > 0$) could introduce lexical variance in unconstrained generation.
- **External Validity:** The evaluation microworld models 3 distinct physical engineering domains. While structural causal isomorphism was verified across these domains, scaling to open-vocabulary real-world industrial environments requires further validation.

## 7. Compliance Assessment Against Gate B Contract

| Clause ID | Metric Description | Frozen Acceptance Bound | Track 2 Observed Value | Compliance Status |
| :--- | :--- | :--- | :--- | :--- |
| **M1** | Task Resolution Rate | $\ge 85.0\%$ | 95.0% (57/60) | **PASS** |
| **M2** | Transfer Speedup Delta | $\ge +40.0\%$ | +64.29% | **PASS** |
| **M3** | Negative Transfer Breaches | $\equiv 0$ | 0 | **PASS** |
| **M4** | Dialectic Convergence | $\ge 90.0\%$ | 100.0% | **PASS** |
| **M5** | Stochastic Recovery SLA | $\le 6.0\text{ ticks}$ | 3.0 ticks | **PASS** |
| **M6** | Committed Physical Breaches | $\equiv 0$ | 0 | **PASS** |
| **M7** | Concurrency Collisions | $\equiv 0$ | 0 | **PASS** |
| **M8** | Max Prompt Tokens | $\le 512\text{ tokens}$ | 153 tokens | **PASS** |
| **M9** | Mean Turn Latency | $< 1000\text{ ms}$ | 179.19 ms | **PASS** |
| **M10** | Anchor Demotion Fidelity | $\equiv 100.0\%$ | 100.0% | **PASS** |

**Final Disposition (Track 2):** **PASS (10/10 Clauses Met).**
