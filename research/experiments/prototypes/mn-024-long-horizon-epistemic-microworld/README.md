# MN-024 — Long-Horizon Physical Microworld Scaling & Multi-Hop Causal Maintenance Under Continuous Entropy Decay

## 1. Overview

Milestone MN-024 expands the operational horizon of Mộng Nhiễm within the physical microworld domain, scaling autonomous multi-agent coordination from short discrete episodes ($\Delta t = 15$, $T \le 25$ ticks in MN-023) to extended long-horizon operations across two evaluation tiers:
- **Horizon Tier A (Nominal Long Horizon):** $T = 60$ ticks with causal anchor separation $\Delta t \ge 40$ ticks.
- **Horizon Tier B (Stress Ultra-Long Horizon):** $T = 100$ ticks with causal anchor separation $\Delta t \ge 80$ ticks.

MN-024 evaluates whether a lightweight 2-billion parameter model (`Qwen3.5-2B`) operating within a Host-Authoritative Microworld can:
1. Balance ongoing physical task progression with active mitigation of passive environmental entropy decay (e.g., heat dissipation, pressure loss, frequency drift).
2. Execute multi-hop causal dependency chains ($\ge 4$ sequential dependencies) without deadlock cycles.
3. Preserve critical causal anchor facts across extended multi-cycle AutoDream consolidations while strictly upholding the $\le 512$ token ceiling.
4. Guarantee zero physical invariant breaches, zero concurrency race collisions, zero epistemic information leakage, and $100\%$ action groundedness.

---

## 2. Directory Structure

```text
mn-024-long-horizon-epistemic-microworld/
├── README.md                          # Milestone overview and reproduction guide
├── charter.md                         # Formal Gate A research hypotheses (H1 to H6)
├── gate-b-contract.md                 # Frozen Gate B quantitative acceptance bounds (M1 to M10)
├── src/                               # Experimental implementation and scenarios
├── tests/                             # Unit tests for long-horizon physical invariants
├── reports/                           # Academic evaluation reports (post-run)
└── runs/                              # Sealed telemetry archives (Zero Loose File Bloat Protocol)
```

---

## 3. Production Dependencies

MN-024 consumes verified production modules directly from `src/mong_nhiem/`:
- `mong_nhiem.core.invariants.ConservationInvariantGuard`
- `mong_nhiem.core.vector_clock.VectorClock`
- `mong_nhiem.core.events.CausalEvent`
- `mong_nhiem.knowledge.causal_dag.CausalEventDAG`
- `mong_nhiem.knowledge.epistemic.EpistemicReconciler`
- `mong_nhiem.orchestration.arbiter.MultiResourceArbiter`
- `mong_nhiem.extensions.autodream.consolidator.FrontierBranchPruner`
- `mong_nhiem.extensions.autodream.fact_cards.FactCardProjector`
- `mong_nhiem.runtime.microworld.AuthoritativeMicroworld`

---

## 4. Empirical Evaluation Results & Reproduction

### 4.1 Evaluation Summary (Dual-Horizon $N=60$ Scenarios, 360 Episodes Per Track)

| Evaluation Track | Horizon Tier | Resolution Rate ($M_1$) | Cascade Completion ($M_6$) | Invariant Breaches ($M_4$) | Race Collisions ($M_5$) | Max Tokens ($M_7$) | Mean Latency ($M_8$) | Compaction ($M_9$) | Final Verdict |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Track 1 (Simulator)** | Tier A ($T=60$) | $100.00\%$ | $100.00\%$ | $0$ | $0$ | $55$ | $0.51\text{ ms}$ | $91.73\%$ | **PASS** |
| | Tier B ($T=100$) | $100.00\%$ | $100.00\%$ | $0$ | $0$ | $55$ | $0.51\text{ ms}$ | $91.76\%$ | **PASS** |
| **Track 2 (Real Qwen 2B)** | Tier A ($T=60$) | $100.00\%$ | $100.00\%$ | $0$ | $0$ | $55$ | $145.23\text{ ms}$ | $91.73\%$ | **PASS** |
| | Tier B ($T=100$) | $100.00\%$ | $100.00\%$ | $0$ | $0$ | $55$ | $144.68\text{ ms}$ | $91.76\%$ | **PASS** |

### 4.2 Reproduction Commands

```powershell
# 1. Run unit tests
python -m pytest research/experiments/prototypes/mn-024-long-horizon-epistemic-microworld/tests/ -v

# 2. Run Track 1 deterministic simulation
python research/experiments/prototypes/mn-024-long-horizon-epistemic-microworld/src/runner_track1.py

# 3. Launch llama-server on port 18502 (Qwen3.5-2B-Q4_K_M)
D:\Materials\llama.cpp\build\bin\Release\llama-server.exe -m D:\Code\mong-nhiem\artifacts\models\mn-002\Qwen3.5-2B-Q4_K_M.gguf --port 18502 -ngl 99 -c 2048

# 4. Run Track 2 real model inference
python research/experiments/prototypes/mn-024-long-horizon-epistemic-microworld/src/runner_track2.py
```

