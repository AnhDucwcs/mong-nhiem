# MN-027: Bimodal Cognitive Emission, Declarative Schema Synthesis & Real-Time Human Supervisory Control

## Overview

Milestone **MN-027** investigates the transition from purely autonomous machine-to-machine closed microworlds to real-time human-centric cognitive architecture. It evaluates whether a single-pass constrained GBNF grammar can reliably govern **Bimodal Cognitive Emission**—emitting both operational machine actions (`ACTION: ...`) and structured communicative acts (`COMMUNICATE [<CLASS>]: "..."`) within a single sub-512 token forward pass—while integrating declarative YAML/JSON schema synthesis, dual-clock temporal synchronization, continuous parameter decay, and human-in-the-loop supervisory preemption.

## Core Architectural Modules

1. **`BimodalProtocol` (`src/bimodal_protocol.py`):**
   - Compiles unified GBNF grammar constraining single-pass bimodal generation.
   - Enforces the Triadic Communicative Taxonomy: `INFORM`, `QUERY`, `EXPRESS`.
   - Deterministic sub-millisecond AST parser (`BimodalParser`).
2. **`TemporalBridge` (`src/temporal_bridge.py`):**
   - Dual-Clock scheduling: `SIMULATED` (discrete synthetic stepping) vs `REAL_TIME` (wall-clock monotonic intervals).
   - Bridges real-time elapsed intervals to discrete Host causal ticks with $\le 15\text{ ms}$ jitter.
3. **`ContinuousStateEngine` (`src/continuous_state.py`):**
   - Implements bounded parameter decay/accumulation: $X(t + \Delta t) = \text{clamp}(X(t) \pm \lambda \cdot \Delta t, X_{\min}, X_{\max})$.
   - Triggers threshold invariants and serializes session state to atomic JSON on disk.
4. **`DeclarativeSchemaLoader` (`src/schema_loader.py`):**
   - Generic YAML/JSON parser compiling external entity definitions, invariants, and preconditions into active Host structures.
5. **`HumanSupervisoryBridge` (`src/human_preemption.py`):**
   - Resolves `SUPERVISED_STANDBY` states via human operator natural language commands.
   - Advances `world_epoch` to preempt stale in-flight SLM actions safely.

## Reproduction & Benchmark Execution

### 1. Unit Tests
```powershell
pytest research/experiments/prototypes/mn-027-bimodal-cognitive-emission/tests/test_mn027.py -v
```

### 2. Track 1: Host Simulator (180 Episodes)
```powershell
python research/experiments/prototypes/mn-027-bimodal-cognitive-emission/src/runner_track1.py
```

### 3. Track 2: Real Model Inference on Qwen 3.5 2B (180 Episodes)
Ensure `llama-server.exe` is running on port 18502 with `Qwen3.5-2B-Q4_K_M.gguf`:
```powershell
python research/experiments/prototypes/mn-027-bimodal-cognitive-emission/src/runner_track2.py
```
