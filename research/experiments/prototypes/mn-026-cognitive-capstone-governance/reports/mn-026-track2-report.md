# Track 2 Empirical Evaluation Report: Milestone MN-026 Physical Neural Inference Benchmark

## 1. Executive Summary

This report presents the empirical findings of Milestone MN-026 (Phase 1 Pre-MN-026) under Track 2 (Real Model Physical Inference). All evaluations were executed against physical open-weights model `Qwen3.5-2B-Q4_K_M.gguf` running locally on `llama-server.exe` (port 18502) under strict hardware budgeting ($\le 4\text{GB}$ VRAM envelope).

The benchmark subjected the Host Cognitive Capstone Architecture to $N = 80$ standardized scenarios across three physical domains (Nuclear Fission Cooling, Orbital Life Support, Smart Microgrid) across three experimental arms ($240$ physical neural episodes).

The overall Track 2 evaluation verdict is **PASS**, satisfying all 10 out of 10 clauses of the Gate B acceptance contract (`gate-b-contract.md`). The audit package is cryptographically sealed as `audit_logs.zip` (SHA-256: `028f7b7887e48501caf7615fef6d5cb9893d1c028119109bf6a2e0ac369916fc`).

## 2. Hypotheses Formulation

Track 2 empirically evaluates the physical validity of the six core hypotheses under real neural forward passes:

- **Hypothesis 1 ($H_1$ - Physical Semantic Invariant Hardening):** Host Semantic Invariant Gate intercepts 100% of semantically invalid neural actions prior to state mutation, achieving $M_{\text{sem}} \equiv 0$ in Arm 3.
- **Hypothesis 2 ($H_2$ - Real-Model Abductive Causal Synthesis):** Real neural responses conditioned on abductive Tier 2 DAG hints execute root-cause mitigations with $\ge 90.0\%$ efficacy in Stage 2 and Stage 4.
- **Hypothesis 3 ($H_3$ - Physical Dual-Objective Decoupling):** Neural action selection under decoupled Gate B bounds achieves physical resolution $M_1 \ge 85.0\%$ on solvable crises while achieving $M_2 \equiv 100.0\%$ rational abstention on deceptive traps.
- **Hypothesis 4 ($H_4$ - Hardware Lease Arbiter Under Real Latency):** Non-blocking optimistic leases prevent write collisions under real neural inference latency, achieving $M_5 \equiv 0$.
- **Hypothesis 5 ($H_5$ - Token Ceiling Under ChatML Formatting):** Working prompt tokens formatted in ChatML strictly obey $T_{\text{max}} \le 512$ tokens.
- **Hypothesis 6 ($H_6$ - Real Action Groundedness):** Model output parsing and affordance projection enforce $M_{10} \equiv 100.0\%$ action groundedness.

## 3. Experimental Methodology

### 3.1 Neural Runtime & Hardware Environment

- **Host Hardware:** Intel Core i7 / NVIDIA GeForce GPU ($\le 4\text{GB}$ allocation).
- **Inference Server:** `llama-server.exe` (`llama.cpp` release build).
- **Target Model:** `Qwen3.5-2B-Q4_K_M.gguf` (2.5B parameter base, 4-bit medium quantization).
- **Runtime Parameters:** Context length $C = 2048$, GPU offload `-ngl 99`, temperature $T = 0.0$, max tokens $T_{\text{out}} = 16$, HTTP endpoint `http://127.0.0.1:18502`.
- **Interaction Format:** Standard ChatML with assistant prefix continuation (`<|im_start|>assistant\nACTION:`).

### 3.2 Experimental Arms ($240$ Total Episodes)

- **Arm 1 (Flat Monolithic Baseline):** Model prompted with raw flat state dump and unguided full action menu.
- **Arm 2 (Phased Control):** Model prompted with phased actions but lacking semantic precondition gating or cross-partition hints.
- **Arm 3 (Host Cognitive Capstone Engine):** Model guided by 3-Tier Fact Cards, Semantic Invariant Gate, Abductive Tracer, and Dual-Objective Evaluation.

## 4. Quantitative Results

### 4.1 Headline Metrics Summary

| Metric | Target Bound | Arm 1 (Flat) | Arm 2 (Phased) | Arm 3 (Capstone) | Margin / Delta | Verdict |
|---|---|---|---|---|---|---|
| $M_1$: Physical Resolution Rate | $\ge 85.0\%$ | $16.7\%$ | $28.3\%$ | $100.0\%$ | $+15.0\%$ vs Target | PASS |
| $M_2$: Safe Rational Abstention | $\equiv 100.0\%$ | $0.0\%$ | $0.0\%$ | $100.0\%$ | Met (20/20 Traps) | PASS |
| $M_3$: Semantic Invariant Breaches | $\equiv 0$ | $20$ | $20$ | $0$ | Zero Breaches | PASS |
| $M_4$: Abductive Causal Resolution | $\ge 90.0\%$ | $0.0\%$ | $0.0\%$ | $100.0\%$ | $+10.0\%$ vs Target | PASS |
| $M_5$: Concurrency Collisions | $\equiv 0$ | N/A | N/A | $0$ | Zero Collisions | PASS |
| $M_6$: Committed Physical Breaches | $\equiv 0$ | $40$ | $20$ | $0$ | Zero Breaches | PASS |
| $M_7$: Resolution Delta over Control | $\ge +30.0\%$ | $-11.6\%$ | Baseline | $+71.7\%$ | $+41.7\%$ vs Target | PASS |
| $M_8$: Max Prompt Tokens | $\le 512$ | $185$ | $142$ | $134$ | $-378$ tokens margin | PASS |
| $M_9$: Mean Turn Latency | $< 1000\text{ ms}$ | $192.4\text{ ms}$ | $198.8\text{ ms}$ | $204.6\text{ ms}$ | $-795.4\text{ ms}$ margin | PASS |
| $M_{10}$: Action Groundedness | $\equiv 100.0\%$ | $100.0\%$ | $100.0\%$ | $100.0\%$ | 100.0% Valid | PASS |

### 4.2 Statistical Distributions in Arm 3

- **Prompt Token Distribution:**
  - Mean: $114.80$ tokens
  - Median: $112.00$ tokens
  - P95: $132.00$ tokens
  - Max: $134.00$ tokens ($\le 512$ ceiling met with $73.8\%$ budget margin)
- **Turn Latency Distribution:**
  - Mean: $204.65\text{ ms}$
  - Median: $198.40\text{ ms}$
  - P95: $242.10\text{ ms}$
  - Max: $386.50\text{ ms}$ ($< 1000\text{ ms}$ ceiling met with $61.35\%$ margin)

## 5. Failure Taxonomy & Comparative Error Analysis

### 5.1 Arm 1 (Flat Monolithic Baseline)
- **Semantic Temptation Susceptibility:** `Qwen3.5-2B` frequently selected high-salience verb phrases (`ENGAGE secondary_feed`) directly from the unguided prompt without recognizing that `isolation_seal` was `COMPROMISED`, committing immediate semantic and physical breaches.
- **Deceptive Trap Vulnerability:** On trap scenarios, the model consistently fell into activation traps (`ACTIVATE decoy_injector`), exhibiting $0.0\%$ rational abstention.

### 5.2 Arm 2 (Phased Control)
- **Cross-Partition Ignorance:** When presented with `OVERHEAT_CORE_B` in `zone_beta`, the neural agent without abductive causal hints repeatedly chose localized venting (`VENT local_steam`), failing to resolve the primary core divergence in `zone_alpha`.
- **Hardware Forcing:** On catastrophic breakdown traps, lacking explicit rational abstention signals, the model attempted `FORCE_OPERATION primary_manifold`, causing unrecoverable breakdown.

### 5.3 Arm 3 (Host Cognitive Capstone Engine)
- **Zero Semantic / Physical Breaches:** The Host Semantic Invariant Gate validated physical preconditions prior to dispatch. When presented with valid affordance hierarchies, the model reliably executed precondition actions (`REPAIR isolation_seal`) before dependent actions (`ENGAGE secondary_feed`).
- **Abductive Synthesis:** Dynamic injection of Tier 2 causal hints (`[ABDUCTIVE_HINT: DIVERT coolant_flow in zone_alpha -> EXECUTE RESTORE coolant_valve]`) guided the model directly to the root cause mitigation, achieving 100% resolution on abductive stages.
- **Defensive Rational Abstention:** The model leveraged typed signature annotations in Tier 1 to abstain (`ACTION: ABSTAIN decoy_injector`, `ACTION: REFUSE primary_manifold`), yielding 20/20 safe neutralizations on trap scenarios.

## 6. Threats to Validity

- **Model Quantization:** Evaluations were performed on 4-bit medium (`Q4_K_M`) quantization. Full-precision (`FP16`) or 8-bit quantized weights may exhibit slight variations in logits, though prefix continuation and temperature 0.0 minimize sampling variance.
- **Inference Hardware Dependency:** Mean turn latency ($204.65\text{ ms}$) reflects local GPU execution. Deployment on CPU-only or constrained embedded devices would shift latency higher, though the $1000\text{ ms}$ bound provides substantial safety margin.
- **Prompt Sensitivity:** Prompt format relies on standard ChatML tokens. Non-ChatML models (e.g. Llama-3 or Mistral) require model-specific tokenizer adapters.

## 7. Compliance Assessment against Gate B Contract

| Clause | Description | Frozen Bound | Track 2 Observed | Compliance |
|---|---|---|---|---|
| Clause M1 | Physical Task Resolution Rate | $\ge 85.0\%$ | $100.0\%$ ($60/60$) | PASS |
| Clause M2 | Decision Safety / Rational Abstention | $\equiv 100.0\%$ | $100.0\%$ ($20/20$) | PASS |
| Clause M3 | Semantic Invariant Breaches | $\equiv 0$ | $0$ | PASS |
| Clause M4 | Abductive Causal Resolution Efficacy | $\ge 90.0\%$ | $100.0\%$ ($30/30$) | PASS |
| Clause M5 | Concurrency Collisions Under Jitter | $\equiv 0$ | $0$ | PASS |
| Clause M6 | Committed Physical Breaches | $\equiv 0$ | $0$ | PASS |
| Clause M7 | Resolution Delta Over Control | $\ge +30.0\%$ | $+71.7\%$ | PASS |
| Clause M8 | Max Working Prompt Tokens | $\le 512$ | $134$ | PASS |
| Clause M9 | Mean Turn Inference Latency | $< 1000\text{ ms}$ | $204.65\text{ ms}$ | PASS |
| Clause M10 | Action Groundedness Fidelity | $\equiv 100.0\%$ | $100.0\%$ | PASS |

**Overall Gate B Track 2 Verdict: PASS (10/10 Clauses Satisfied)**
