# Milestone MN-026: Multi-Stage Cognitive Capstone Governance, Semantic Invariant Hardening, and Abductive Cross-Partition Causal Synthesis

## Overview

Milestone **MN-026** is the Grand Capstone prototype of Mộng Nhiễm's Microworld and Distributed Cognitive Governance research arc. It systematically resolves the open limitations of previous milestones (MN-022, MN-023, MN-024, MN-025) across 6 structured stages using 1 single frozen open-weights SLM (<4B) within a 4GB VRAM envelope:
1. **Stage 1 (Remediating MN-022):** Host Semantic Invariant Gate & Virtual Asymmetric Latency Jitter.
2. **Stage 2 (Remediating MN-023):** Hidden Inter-Partition Causal Coupling & Abductive Causal Tracing.
3. **Stage 3 (Remediating MN-025):** Dual-Objective Decision Contract ($M_{\text{phys}}$ on solvable cases vs $M_{\text{safe}}$ on deceptive traps).
4. **Stage 4 (Composite Capstone):** Unified Composite Microworld synthesizing multi-hop causal chains and deceptive decoys.
5. **Stage 5 (Cognitive Preemption):** Authoritative Host Preemptive Interrupt Gate (`PreemptiveInterruptGate`) invalidating stale action proposals ($action\_epoch < world\_epoch$) upon sudden $t+1$ mid-trajectory physical shocks.
6. **Stage 6 (Long-Horizon Microworld):** Extended 50-tick capstone microworld with continuous thermodynamic entropy decay, pipe rupture shocks, deceptive traps, and plan resumption.

## Directory Structure

```text
mn-026-cognitive-capstone-governance/
├── README.md                          # Milestone overview and reproduction guide
├── charter.md                         # Formal Gate A charter and research questions
├── gate-b-contract.md                 # Frozen Gate B acceptance criteria (M1 to M10)
├── gate-d-disposition-review.md       # Gate D disposition review
├── pre-run-freeze-manifest.json       # SHA-256 pre-run cryptographic manifest
├── post-run-freeze-manifest.json      # SHA-256 post-run cryptographic manifest
├── src/                               # Prototype architecture and runners
│   ├── semantic_gate.py               # Semantic invariant admission validator
│   ├── abductive_tracer.py            # Backward causal graph tracer
│   ├── virtual_jitter.py              # Asymmetric latency emulator
│   ├── preemptive_gate.py             # Preemptive interrupt & epoch invalidation gate
│   ├── microworld_engine.py           # Multi-stage microworld runtime & fact cards
│   ├── benchmark_scenarios.py         # Standardized N=120 scenario definitions
│   ├── agent_worker.py                # Phased agent worker supporting ChatML
│   ├── evaluator.py                   # Deterministic Gate B contract evaluator
│   ├── runner_track1.py               # Automated Track 1 runner (Simulator)
│   └── runner_track2.py               # Automated Track 2 runner (Real Qwen3.5-2B)
├── tests/                             # Unit tests for prototype engines
├── reports/                           # Academic empirical reports
└── runs/                              # Sealed run telemetry (audit_logs.zip)
```

## Reproduction Instructions

### 1. Execute Unit Tests
```powershell
python -m pytest research/experiments/prototypes/mn-026-cognitive-capstone-governance/tests/ -v
```

### 2. Execute Track 1 (Host Simulator — 360 episodes)
```powershell
python research/experiments/prototypes/mn-026-cognitive-capstone-governance/src/runner_track1.py
```

### 3. Execute Track 2 (Real Model Inference on Qwen 3.5 2B — 360 episodes)
Ensure `llama-server.exe` is running on port 18502:
```powershell
D:\Materials\llama.cpp\build\bin\Release\llama-server.exe -m D:\Code\mong-nhiem\artifacts\models\mn-002\Qwen3.5-2B-Q4_K_M.gguf --port 18502 -c 2048 -ngl 99
```
Then execute:
```powershell
python research/experiments/prototypes/mn-026-cognitive-capstone-governance/src/runner_track2.py
```
