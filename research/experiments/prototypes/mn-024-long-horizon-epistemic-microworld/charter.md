# Gate A Research Charter: MN-024 — Long-Horizon Physical Microworld Scaling & Multi-Hop Causal Maintenance Under Continuous Entropy Decay

## 1. Executive Charter & Problem Statement

Milestone MN-023 demonstrated the empirical correctness of Host-Authoritative observation masking, discrete invariant gating, and short-range causal anchor retention ($\Delta t \ge 15$ ticks) on pure open-weights `Qwen3.5-2B`. However, real-world cyber-physical systems operate over extended operational lifetimes subject to continuous thermodynamic, electrical, and mechanical decay.

Milestone MN-024 investigates whether a lightweight Small Language Model ($\le 4\text{B}$) operating within a Host-Authoritative Epistemic Microworld can sustain long-horizon multi-agent coordination across extended discrete horizons ($T = 60 \to 100$ ticks) under:
1. **Passive Environmental Entropy Decay:** Subsystems experience progressive physical degradation (e.g., heat accumulation, pressure drop, frequency drift) unless actively counteracted by maintenance actions.
2. **Deep Multi-Hop Causal Dependency Chains ($\ge 4$ steps):** Physical objectives cannot be resolved in a single step; they require strict sequential preconditions spanning multiple distinct resources.
3. **Multi-Cycle Memory Compaction Under $512$-Token Ceiling:** Prompt buffers must survive multi-cycle AutoDream compaction without historical amnesia regarding early causal discoveries ($\Delta t \ge 40$ and $\Delta t \ge 80$ ticks).

---

## 2. Formal Research Hypotheses & Falsification Criteria

- **$H_1$ (Host Physical Invariant Preservation under Entropy Decay):** Host pre-condition gating eliminates physical law violations despite ongoing passive entropy decay.
  $$\text{Falsification Criterion: } \sum_{i=1}^N \text{Breaches}_i > 0$$

- **$H_2$ (Long-Horizon Causal Anchor Retention Across Multi-Cycle Consolidation):** Agents equipped with 3-tier fact card consolidation retain early causal anchors across extended horizons ($\Delta t \ge 40$ and $\Delta t \ge 80$), outperforming unpruned history ($\text{Arm 2}$) by at least $+50.0$ percentage points.
  $$\text{Falsification Criterion: } R_{\text{causal}}(\text{Arm 3}) - R_{\text{causal}}(\text{Arm 2}) < 0.50$$

- **$H_3$ (Continuous Epistemic Information Leakage Invariant):** Host observation masks prevent private entity states from entering unauthorized agent prompt buffers across the entire extended lifetime.
  $$\text{Falsification Criterion: } \Lambda_{\text{leakage}}(\text{Arm 3}) > 0.0$$

- **$H_4$ (Multi-Hop Causal Cascade Execution Rate):** Multi-resource arbitration ensures that multi-step causal dependency chains ($\ge 4$ steps) execute without deadlocks.
  $$\text{Falsification Criterion: } \text{CascadeRate}(\text{Arm 3}) < 0.80$$

- **$H_5$ (Asymmetric Non-Omniscient Action Groundedness):** The SLM never commits actions conditioning on private secrets prior to verified causal discovery in the microworld DAG.
  $$\text{Falsification Criterion: } F_{\text{grounded}}(\text{Arm 3}) < 1.0$$

- **$H_6$ (Sub-Second Turn Latency SLA on Pure 2B SLM):** Live SLM inference on pure `Qwen3.5-2B` maintains a mean turn latency strictly under $1000\text{ ms}$.
  $$\text{Falsification Criterion: } \bar{t}_{\text{turn}}(\text{Arm 3}) \ge 1000\text{ ms}$$

---

## 3. Experimental Methodology

### 3.1 Independent Variables (Experimental Arms)

1. **Arm 1 (Flat Omniscient Baseline):** Global unmasked world-state dump serialized into prompt. Actions dispatched without lease arbitration.
2. **Arm 2 (Unpruned Subjective Memory Control):** Observation masks applied, but all historical observations, gossip, and maintenance logs accumulate monotonically without tiering or frontier pruning.
3. **Arm 3 (Host Epistemic Microworld Architecture):** Incorporates `EpistemicMaskEngine`, 3-Tier Fact Card compaction (Tier 1 invariant anchors, Tier 2 causal frontier, Tier 3 affordances), `MultiResourceArbiter`, `EnvironmentalEntropyEngine`, and `EpistemicReconciler`.

### 3.2 Dual-Horizon Evaluation Corpus

- **Horizon Tier A (Nominal Long Horizon):** $T = 60$ ticks with causal separation $\Delta t \ge 40$ ticks.
- **Horizon Tier B (Stress Ultra-Long Horizon):** $T = 100$ ticks with causal separation $\Delta t \ge 80$ ticks.
- **Corpus Size:** $N = 60$ standardized scenarios ($M = 3$ concurrent agents: Scout, Engineer, Guard) spanning 3 deep physical domains:
  1. Fission Reactor Core Cooling & Containment ($N=20$)
  2. Deep-Space Orbital Habitat Atmospheric Recycling ($N=20$)
  3. Regional Smart Microgrid Cascading Fault Isolation ($N=20$)
- **Total Execution Volume:** $60\text{ cases} \times 3\text{ arms} = 180\text{ episodes}$ per track and horizon tier.

---

## 4. Hardware & Runtime Configuration

- **Host Machine:** Windows x86_64 workstation with NVIDIA CUDA acceleration.
- **Inference Runtime:** Local `llama-server.exe` on port `18502`.
- **Target Model:** `Qwen3.5-2B-Q4_K_M.gguf` (Quantized GGUF, 2.0B parameters).
- **Prompt Format:** ChatML template (`<|im_start|>system...<|im_end|>`).
- **Telemetry Archival:** Packaged into `audit_logs.zip` under Zero Loose File Bloat Protocol.
