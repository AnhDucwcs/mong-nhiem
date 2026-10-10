# Prototype MN-017: Dynamic World Ticks & Hierarchical Planning

## 1. Milestone Overview

Milestone **MN-017** bridges Mộng Nhiễm from turn-synchronous isolated agent tasks to **concurrent, evolving environments** with independent world dynamics, directly preparing the substrate for Milestone **MN-018 (Stateful Simulated Microworld Evolution)**.

### Problems Addressed
1. **Passive Turn Synchrony**: In prior milestones (MN-001 through MN-016), world state mutated exclusively upon agent action dispatch. In real-world multi-entity simulations, environments exhibit asynchronous background flux (leases expire, resource levels drain, telemetry updates arrive).
2. **Goal Divergence & Horizon Jumping (Failure Mode 3 from MN-012)**: On complex multi-stage objectives ($T \ge 15-30$), small models ($<4\text{B}$) suffer from attention drift when exposed to the full mission specification, prematurely declaring success or skipping prerequisite steps.
3. **Context Inflation vs Environmental Concurrency**: Exposing raw multi-rate world event streams alongside global mission goals guarantees context overflow ($> 512$ tokens), destroying small-model reasoning capacity.

---

## 2. Core Architectural Components

- **`world_engine.py`**:
  - `WorldClock`: Manages discrete simulation time $t_{world}$ in integer ticks.
  - `WorldEntity`: State representation with monotonic version counter $v_{entity}$, TTL decay, and rate-of-decay mutators.
  - `DynamicWorldEngine`: Executes background tick transformations (lease decay, consumption, queue processing) independently of agent turns.
- **`hierarchical_planner.py`**:
  - `SubGoal`: Discrete milestone containing identifier, description, prerequisite predicates, and allowed actions.
  - `MissionGraph`: Directed Acyclic Graph of sub-goals enforcing strict topological completion order.
  - `HierarchicalPlanner`: Evaluates active goal satisfaction via Host symbolic predicates, advances the active pointer, and generates scoped context prompts ($\le 128$ tokens).
- **`concurrency_guard.py`**:
  - `StaleStateDetector`: Compares read version $v_{read}$ against current store version $v_{current}$.
  - `ConcurrencyGuard`: Reconciles state collisions, generates lightweight delta refresh payloads ($\le 64$ tokens), and blocks illegal mutations.
- **`dynamic_affordance_compiler.py`**:
  - Compiles GBNF grammars dynamically restricted to actions permissible under the *current active sub-goal* $G_k$, mathematically preventing the model from generating actions for future phases.
- **`orchestrator.py`**:
  - Unifies `WorldEngine`, `HierarchicalPlanner`, `ConcurrencyGuard`, and `CognitiveOrchestrator` into an end-to-end execution loop.

---

## 3. Reproduction & Execution Instructions

### Step 1: Run Automated Unit Tests
```bash
pytest -v research/experiments/prototypes/mn-017-dynamic-world-ticks/tests/
```

### Step 2: Generate Deterministic Benchmark Corpus
```bash
python research/experiments/prototypes/mn-017-dynamic-world-ticks/scripts/generate_corpus.py
```

### Step 3: Run Track 1 (Deterministic Simulator)
```bash
python research/experiments/prototypes/mn-017-dynamic-world-ticks/scripts/run_benchmark.py --track 1
```

### Step 4: Run Track 2 (Real Model Inference)
```bash
python research/experiments/prototypes/mn-017-dynamic-world-ticks/scripts/run_benchmark.py --track 2 --model artifacts/models/mn-002/Qwen3.5-2B-Q4_K_M.gguf
```

---

## 4. Empirical Verification & Gate Status

- **Track 1 (Deterministic State Simulator)**:
  - Arm 1 (Flat Baseline): 0/40 PASS (0.0%), 118 horizon jumping actions.
  - Arm 2 (Static Plan Control): 40/40 PASS (100.0%).
  - Arm 3 (Dual-Engine MN-017): 40/40 PASS (100.0%), 0 horizon jumping, 0 stale overwrites.
- **Track 2 (Real Model Inference — `Qwen3.5-2B-Q4_K_M.gguf`)**:
  - Arm 1 (Flat Baseline): 0/40 PASS (0.0%), 118 horizon jumping events.
  - Arm 2 (Static Plan Control): 0/40 PASS (0.0%), 40/40 premature resolution failures on Turn 1.
  - Arm 3 (Dual-Engine MN-017): 40/40 PASS (100.0%), 0 horizon jumping, 0 premature resolutions, 0 unmanaged stale overwrites, 31 intercepted version drifts recovered via delta notices.
  - Token Usage: Peak 253.0 tokens, Mean 137.8 tokens ($\le 384$ SLA).
  - SLA Latency: 534.4 ms ($< 1000\text{ ms}$ SLA).
- **Cross-Model Benchmark Comparison (Post-Affordance Pruning)**:
  - `Qwen3.5-2B-Q4_K_M.gguf`: **40/40 PASS (100.0%)** across all 3 domains, 502.8 ms latency.
  - `Llama-3.2-3B-Instruct-Q4_K_M.gguf`: **35/40 PASS (87.5%)** (Domain B: 15/15 [100%], Domain C: 10/10 [100%], Domain A: 10/15 [66.7%]), 294.6 ms latency.
  - `Qwen3-4B-Q4_K_M.gguf`: **38/40 PASS (95.0%)** (Domain A: 13/15 [86.7%], Domain B: 15/15 [100%], Domain C: 10/10 [100%]), 413.3 ms latency.
  - Cross-Model Mean Accuracy: Surged from 65.0% pre-patch to **94.2%** post-patch (+29.2% absolute gain), with zero unmanaged stale overwrites committed across all runs.
  - Detailed cross-model report: [`reports/mn017_cross_model_comparison_report.md`](reports/mn017_cross_model_comparison_report.md).
- **Gate Disposition**: `VERIFIED_PASS` — Gate D Review complete in [`gate-d-disposition-review.md`](gate-d-disposition-review.md).
