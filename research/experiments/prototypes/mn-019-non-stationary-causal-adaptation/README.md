# MN-019: Continuous Non-Stationary Domain Drift & Dynamic Adaptation

## 1. Master Strategic Intent

Milestone MN-019 investigates small language model ($< 4\text{B}$ parameter) cognitive governance when the fundamental **stationary assumption** of the environment is relaxed. 

In MN-018, the small model successfully operated across extended horizons ($T \ge 150-200$ ticks) because the transition function $T(s, a) \to s'$ and physical conservation parameters were invariant. In real-world robotic, cyber-physical, and distributed infrastructure settings, operating environments undergo continuous non-stationary drift:
1. Physical conversion efficiencies degrade over time (mechanical wear, fouling, dust accumulation).
2. Latent impedances and friction shift dynamically.
3. Sudden parametric shocks and harmonic load oscillations alter system responsiveness.

MN-019 tests whether a **Dual-Engine Cognitive Host** equipping the model with real-time **Discrepancy Monitoring**, **Dynamic Affordance DAG Regeneration**, and **Lifelong AutoDream Causal Synthesis** can sustain high task resolution ($\ge 85.0\%$) and zero physical conservation breaches without model weight retraining.

---

## 2. Multi-Stage Experimental Architecture

Following the sequential quarantine methodology established in MN-003, MN-019 is partitioned into three hermetic sub-experiments executed sequentially:

| Stage ID | Focus Area | Core Research Question | Status |
| --- | --- | --- | :---: |
| **`drift-001-parametric-adaptation`** | Continuous Parametric Drift & Affordance Regeneration | Can real-time discrepancy tracking and dynamic GBNF affordance pruning prevent catastrophic invariant breaches under continuous wear/shock? | **VERIFIED / FROZEN** |
| **`drift-002-schema-evolution`** | Lifelong AutoDream & Dynamic Schema Evolution | How does declarative memory preserve $\ge 70.0\%$ compaction and bounded prompts ($\le 512$ tok) when novel entities and dynamic relational attributes emerge? | **NEXT STAGE** |
| **`drift-003-causal-event-synthesis`** | Causal Induction & Synthetic Macro-Event Generation | Can the system induce verified empirical causal invariants from history to proactively anticipate state transitions rather than purely reacting? | Pending Stage 2 PASS |

---

## 3. Governance and Promotion Boundaries

- **Quarantine Invariant:** All prototype code, benchmarks, definitions, and execution runs remain strictly quarantined in `research/experiments/prototypes/mn-019-non-stationary-causal-adaptation/`.
- **Zero Silent Promotion:** Zero code will be promoted into `src/mong_nhiem/` during sub-experiment execution. Promotion requires a formal Gate D disposition review across all three verified stages.
- **Academic Standards:** All artifacts adhere to `AGENTS.md` (100% technical English, LaTeX math formatting, zero decorative icons or emojis, and strict independent verification).
