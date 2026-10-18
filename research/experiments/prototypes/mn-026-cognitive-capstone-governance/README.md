# Milestone MN-026: Multi-Stage Cognitive Capstone Governance, Semantic Invariant Hardening, and Abductive Cross-Partition Causal Synthesis

## Overview

Milestone **MN-026** is the Grand Capstone prototype of Mộng Nhiễm's Microworld and Distributed Cognitive Governance research arc. It systematically resolves the open limitations of previous milestones (MN-022, MN-023, MN-024, MN-025) across 7 structured stages using 1 single frozen open-weights SLM (<4B) within a 4GB VRAM envelope:
1. **Stage 1 (Remediating MN-022):** Host Semantic Invariant Gate & Virtual Asymmetric Latency Jitter.
2. **Stage 2 (Remediating MN-023):** Hidden Inter-Partition Causal Coupling & Abductive Causal Tracing.
3. **Stage 3 (Remediating MN-025):** Dual-Objective Decision Contract ($M_{\text{phys}}$ on solvable cases vs $M_{\text{safe}}$ on deceptive traps).
4. **Stage 4 (Composite Capstone):** Unified Composite Microworld synthesizing multi-hop causal chains and deceptive decoys.
5. **Stage 5 (Cognitive Preemption):** Authoritative Host Preemptive Interrupt Gate (`PreemptiveInterruptGate`) invalidating stale action proposals ($action\_epoch < world\_epoch$) upon sudden $t+1$ mid-trajectory physical shocks.
6. **Stage 6 (Long-Horizon Microworld):** Extended 50-tick capstone microworld with continuous thermodynamic entropy decay, pipe rupture shocks, deceptive traps, and plan resumption.
7. **Stage 7 (Resilience Clearing Sub-Phase):** Production-transition resilience addressing 5 core vulnerabilities: Oracle Epistemic Decoupling (`ACTION: PROBE <target>` + $T \ge 450\text{K}$ reflex breaker), Preemption Livelock Freedom (3-class action taxonomy: `READ_ONLY`, `FAILSAFE`, `MUTATION`), Affordance Space Bounding (Goal-Conditioned Top-4 ranking $\le 200$ tokens), Causal Confluence Attribution ($\text{Contribution}(X_i) = |\partial Y / \partial X_i| \cdot \Delta X_i$ + 2-phase resolution), and Sensor Blackout Dual-Mode Autonomy (`AUTONOMOUS_IMPROVISE` via secondary physics observers vs `SUPERVISED_STANDBY`).

## Directory Structure

```text
mn-026-cognitive-capstone-governance/
├── README.md                          # Milestone overview and reproduction guide
├── charter.md                         # Formal Gate A charter and research questions
├── gate-b-contract.md                 # Frozen Gate B acceptance criteria (M1 to M15)
├── gate-d-disposition-review.md       # Gate D disposition review
├── pre-run-freeze-manifest.json       # SHA-256 pre-run cryptographic manifest
├── post-run-freeze-manifest.json      # SHA-256 post-run cryptographic manifest
├── run_all_models.py                  # Automated 3-model benchmark orchestrator
├── src/                               # Prototype architecture and runners
│   ├── semantic_gate.py               # Semantic invariant admission validator
│   ├── abductive_tracer.py            # Backward causal graph tracer & confluence decomposition
│   ├── virtual_jitter.py              # Asymmetric latency emulator
│   ├── preemptive_gate.py             # 3-Class Preemptive interrupt & epoch invalidation gate
│   ├── microworld_engine.py           # Multi-stage microworld runtime & fact cards
│   ├── benchmark_scenarios.py         # Standardized N=140 scenario definitions
│   ├── agent_worker.py                # Phased agent worker supporting ChatML / Llama-3
│   ├── evaluator.py                   # Deterministic Gate B contract evaluator (M1 to M15)
│   ├── runner_track1.py               # Automated Track 1 runner (Simulator - 420 episodes)
│   └── runner_track2.py               # Automated Track 2 runner (Real neural inference)
├── tests/                             # Unit tests for prototype engines
│   ├── test_mn026.py                  # Core unit tests (12 tests)
│   └── test_mn026_resilience.py       # Stage 7 resilience unit tests (6 tests)
├── reports/                           # Academic empirical reports
│   ├── mn-026-track1-report.md        # Track 1 Simulator report (15/15 PASS)
│   ├── mn-026-track2-report.md        # Track 2 Qwen 3.5 2B report (15/15 PASS)
│   ├── mn-026-track2-llama3-2-3b-report.md # Track 2 Llama 3.2 3B report (15/15 PASS)
│   ├── mn-026-track2-qwen3-4b-report.md    # Track 2 Qwen 3 4B report (15/15 PASS)
│   └── mn-026-cross-model-comparison-report.md # Cross-model comparison report (15/15 PASS)
└── runs/                              # Sealed run telemetry (audit_logs.zip)
```

## Reproduction Instructions

### 1. Execute Unit Tests
```powershell
python -m pytest research/experiments/prototypes/mn-026-cognitive-capstone-governance/tests/ -v
```

### 2. Execute Track 1 (Host Simulator — 420 episodes)
```powershell
python research/experiments/prototypes/mn-026-cognitive-capstone-governance/src/runner_track1.py
```

### 3. Execute Track 2 (All 3 Real Models — 1,260 episodes)
```powershell
python research/experiments/prototypes/mn-026-cognitive-capstone-governance/run_all_models.py
```
