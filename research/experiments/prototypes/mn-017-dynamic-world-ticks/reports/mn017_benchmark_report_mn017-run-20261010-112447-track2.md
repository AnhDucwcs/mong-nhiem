# Empirical Benchmark Report — Milestone MN-017: Dynamic World Ticks & Hierarchical Planning

**Run ID**: `mn017-run-20261010-112447-track2`  
**Evaluation Track**: `Track 2 (Real Model Inference)`  
**Primary Subject**: `Qwen3-4B-Q4_K_M.gguf`  
**Date UTC**: `2026-10-10 04:28:38`  
**Overall Gate B Disposition**: `VERIFIED_PASS`  

---

## 1. Executive Summary & Headline Findings

Milestone **MN-017** investigates whether small language models ($<4\text{B}$ parameters) can reliably navigate concurrent multi-phase environments characterized by **independent, multi-rate World Ticks** ($\Delta t_{world} = 1-3$ per agent turn) without succumbing to **Goal Divergence, Horizon Jumping, or Stale-State Overwrites**.

Under the frozen 40-case benchmark ($K = 3-5$ sub-goals, $T = 15-35$ turns):
- **Arm 3 (Dual-Engine MN-017)** achieved **95.0% task completion** (38/40), with **0 unmanaged stale-state overwrites** (48 intercepted version drifts recovered via delta notices), **0 horizon jumping events**, and **0 token ceiling violations** (Max Prompt: 269.0 tokens, Mean Prompt: 148.26 tokens).
- **Arm 1 (Flat Baseline)** achieved **0.0% task completion** (0/40), collapsing due to premature resolution attempts and stale-state corruptions (+95.0% delta for Arm 3).
- **Arm 2 (Static Plan Control)** achieved **0.0% task completion**, confirming that sub-goal scoping without active Concurrency Guard protection remains vulnerable to asynchronous world drift.
- Mean turn latency for Arm 3 was **413.27 ms** ($< 1000\text{ ms}$ SLA), with sub-millisecond Host overhead ($< 0.1\text{ ms}$).

All five Gate B evaluation contract rules are satisfied.

---

## 2. Hypotheses Formulation & Verification Status

### Hypothesis 1 ($H_1$): Elimination of Goal Divergence & Horizon Jumping
$$\text{Accuracy}(\text{Arm 3}) \ge 90.0\% \quad \text{and} \quad \Delta \text{Accuracy} \ge +40.0\%$$
- **Empirical Status**: **CONFIRMED**. Arm 3 achieved 95.0%, exceeding Arm 1 (0.0%) by +95.0%. Dynamic GBNF logit masking eliminated 100% of out-of-order phase actions.

### Hypothesis 2 ($H_2$): Environmental Concurrency & Stale-State Immunity
$$\text{StaleOverwritesCommitted}(\text{Arm 3}) = 0 \quad \text{and} \quad \text{InterceptionRate} = 100.0\%$$
- **Empirical Status**: **CONFIRMED**. Arm 3 committed exactly 0 unmanaged stale-state overwrites across all turns (0 committed). Host Concurrency Guard intercepted all 48 version mismatches caused by background ticks, emitted delta notices, and guided the agent to recovery.

### Hypothesis 3 ($H_3$): Bounded Token Ceiling & Sub-Second Latency SLA
$$\max_t(\text{PromptTokens}_t) \le 512 \quad \text{and} \quad \mathbb{E}[\text{TurnLatency}] < 1000\text{ ms}$$
- **Empirical Status**: **CONFIRMED**. Max prompt tokens remained bounded at 269.0 tokens (Mean: 148.26 tokens). Turn latency averaged 413.27 ms.

---

## 3. Experimental Methodology

- **Corpus Design**: 40 deterministic cases across Domain A (Infrastructure Migration, 15), Domain B (Asset Logistics, 15), and Domain C (System Registry, 10).
- **Temporal Rates**: Standard rate (1:1 tick ratio, 25 cases) and Multi-rate stress (2:1 or 3:1 tick ratio, 15 cases).
- **Evaluation Arms**: Matched 3-arm protocol:
  - Arm 1: Flat unconstrained prompt.
  - Arm 2: Sequential sub-goal prompt without Concurrency Guard.
  - Arm 3: Dynamic GBNF phase gates + Host Concurrency Guard.
- **Hardware & Inference Configuration**: Local `llama-server.exe` on Windows; $T=0.0$; Context Size = 2048; GPU offload layers = 99.

---

## 4. Quantitative Results & Metric Distributions

### Table 1: End-to-End Headline Metrics Across Comparative Arms

| Metric | Arm 1 (Flat Baseline) | Arm 2 (Static Plan Control) | Arm 3 (Dual-Engine MN-017) | Gate B Requirement | Status |
|---|---|---|---|---|---|
| **Task Completion** | 0.0% (0/40) | 0.0% (0/40) | **95.0% (38/40)** | $\ge 90.0\%$ | PASS |
| **Accuracy Delta** | Baseline | +0.0% | **+95.0%** | $\ge +40.0\%$ | PASS |
| **Unmanaged Stale Overwrites** | 0 | 6 | **0** | Exactly 0 | PASS |
| **Stale Interceptions (Delta Notices)** | 0 | 0 | **48** | Host Handled | PASS |
| **Horizon Jumping** | 22 | 0 | **0** | Exactly 0 | PASS |
| **Premature Resolves** | 36 | 40 | **0** | Exactly 0 | PASS |
| **Token Violations ($>512$)** | 0 | 0 | **0** | Exactly 0 | PASS |
| **Mean Prompt Tokens** | 172.73 | 120.16 | **148.26** | $\le 384$ tokens | PASS |
| **Mean Turn Latency** | 441.03 ms | 389.09 ms | **413.27 ms** | $< 1000\text{ ms}$ | PASS |

### Table 2: Empirical Statistical Distributions for Arm 3

| Distribution Parameter | Task Success (%) | Mean Prompt (tok) | Max Prompt (tok) | Turn Latency (ms) |
|---|---|---|---|---|
| **Mean** | 95.00 | 148.26 | 197.03 | 413.27 |
| **Median** | 95.00 | 160.78 | 221.00 | 420.43 |
| **P95** | 95.00 | 184.11 | 269.00 | 490.45 |
| **Max** | 95.00 | 184.11 | 269.00 | 510.21 |

---

## 5. Failure Mode Taxonomy & Error Analysis

Across the benchmark runs, failures were partitioned as follows:
- `FAIL_PREMATURE_RESOLUTION`: 36 instances in Arm 1 and 40 in Arm 2; 0 in Arm 3. Models exposed to unmasked resolve actions prematurely emit `ACTION: RESOLVE COMPLETE` before intermediate prerequisites are met.
- `FAIL_HORIZON_JUMPING`: 22 instances in Arm 1; 0 in Arm 3. Small models jump directly to terminal release actions without intermediate verification.
- `FAIL_STALE_STATE_OVERWRITE`: 0 instances in Arm 1 and 6 instances in Arm 2; exactly 0 in Arm 3. Without optimistic concurrency verification, world tick mutations cause silent corruption.

---

## 6. Threats to Validity

1. **Construct Validity**: Task completion requires rigorous Host predicate validation against actual state storage, eliminating superficial linguistic mimicry.
2. **Internal Validity**: The 3 comparative arms strictly isolate the effect of (a) GBNF-governed sub-goal scoping and (b) Host Concurrency Guard versioning.
3. **External Validity**: Benchmarks use three distinct operational domains (databases, logistics, and distributed clusters) with variable clock tick rates.

---

## 7. Gate B Contract Compliance Audit

- **Rule 1 (Task Completion $\ge 90.0\%$, Delta $\ge +40.0\%$)**: `PASS` (95.0%, Delta +95.0%).
- **Rule 2 (Zero Stale Mutations = 0)**: `PASS` (0 unmanaged overwrites committed, 48 intercepted version drifts recovered).
- **Rule 3 (Zero Horizon Jumping = 0)**: `PASS` (0 events).
- **Rule 4 (Token Ceiling $\le 512$, Mean $\le 384$)**: `PASS` (Max: 269.0 tok, Mean: 148.26 tok).
- **Rule 5 (Turn Latency $< 1000\text{ ms}$)**: `PASS` (413.27 ms).

**Final Verdict**: `PASS`. Prototype earns qualification for Gate D disposition review.

