# Milestone MN-018: Stateful Simulated Microworld Evolution

## Overview

Milestone **MN-018** (**Stateful Simulated Microworld Evolution**) represents a foundational cognitive host milestone in project Mộng Nhiễm. It brings together all cognitive substrates developed and verified across MN-009 through MN-017 into an integrated Dual-Engine Cognitive Host:
- Dynamic multi-rate world simulation and background environmental shocks.
- Host-authoritative physical conservation laws and invariant verification.
- Hierarchical mission DAG decomposition with symbolic Host predicate gates.
- Optimistic concurrency guards with monotonic versioning and delta notices.
- Dynamic GBNF grammar compilation with active affordance pruning.
- SHA-256 append-only episodic event logs and autonomous AutoDream consolidation.
- Host Memento state checkpointing, rollback, and negative action steering.

## Architecture

```
                    +-------------------------------------------------+
                    |             Host Environment (Authoritative)    |
                    |                                                 |
                    |   +------------------+   +-------------------+  |
                    |   | World Clock      |-->| Physics Sim Engine|  |
                    |   | (Multi-rate tick)|   | (Telemetry decay) |  |
                    |   +------------------+   +-------------------+  |
                    |                                    |            |
                    |                                    v            |
                    |                          +-------------------+  |
                    |                          | Entity State Store|  |
                    |                          +-------------------+  |
                    |                             |             |     |
                    |               +-------------+             |     |
                    |               |                           v     |
                    |               v             +-----------------+ |
                    |      +------------------+   | Concurrency &   | |
                    |      | Conservation Law |   | Version Guard   | |
                    |      | Invariant Guard  |   +-----------------+ |
                    |      +------------------+                 |     |
                    |               |                           |     |
                    |               v                           v     |
                    |      +------------------+   +-----------------+ |
                    |      | Memento Rollback |   | Mission DAG &   | |
                    |      | & Neg Directive  |   | Predicate Gates | |
                    |      +------------------+   +-----------------+ |
                    |                                           |     |
                    |   +------------------+                    v     |
                    |   | AutoDream Engine |<--[Event Stream]---+     |
                    |   | & Episodic Store |                          |
                    |   +------------------+                          |
                    +-------------------|-----------------------------+
                                        | Context Prompt <= 512 tok
                                        v
                    +-------------------------------------------------+
                    |       Stateless LLM Reasoning Engine (<4B)      |
                    |     (Qwen3.5-2B / Llama-3.2-3B / Qwen3-4B)      |
                    |             GBNF Logit Constrained              |
                    +-------------------------------------------------+
```

## Directory Structure

- `charter.md`: Formal research questions, hypotheses, and scope.
- `gate-b-contract.md`: Quantitative acceptance criteria and SLA thresholds.
- `src/`: Host-authoritative engine implementations:
  - `microworld_engine.py`: Physics simulation, multi-rate clocks, and conservation invariants.
  - `hierarchical_planner.py`: Multi-stage long-horizon mission DAG.
  - `concurrency_guard.py`: Version validation and atomic delta notice emitter.
  - `dynamic_affordance.py`: Dynamic GBNF compiler with active affordance pruning.
  - `episodic_memory.py`: Append-only SHA-256 episodic event log.
  - `autodream_engine.py`: Autonomous memory consolidation and Fact Card extraction.
  - `memento_stack.py`: State rollback and negative action masking.
  - `orchestrator.py`: Unified Dual-Engine host coordinator.
- `scripts/`:
  - `generate_corpus.py`: Generates the 30 long-horizon microworld benchmark cases ($T = 50 - 100$).
  - `run_benchmark.py`: Runs Track 1 and Track 2 evaluation benchmarks with cryptographic freeze manifest generation.
- `tests/`: Comprehensive unit tests verifying all host invariants and engine logic.
- `definition/`:
  - `corpus-v1/cases.json`: Frozen 30 evaluation cases.
  - `pre-run-freeze-manifest.json`: Pre-execution cryptographic manifest.
  - `post-run-freeze-manifest.json`: Post-execution cryptographic manifest.
- `reports/`: Empirical evaluation reports and academic benchmark analysis.
- `gate-d-disposition-review.md`: Post-evaluation architectural review and promotion recommendations.

## Reproduction Instructions

1. Run unit test suite:
   ```bash
   pytest research/experiments/prototypes/mn-018-simulated-microworld-evolution/tests/
   ```
2. Generate corpus:
   ```bash
   python research/experiments/prototypes/mn-018-simulated-microworld-evolution/scripts/generate_corpus.py
   ```
3. Generate pre-run freeze manifest:
   ```bash
   python research/experiments/prototypes/mn-018-simulated-microworld-evolution/scripts/run_benchmark.py --freeze pre
   ```
4. Run Track 1 (deterministic simulator benchmark):
   ```bash
   python research/experiments/prototypes/mn-018-simulated-microworld-evolution/scripts/run_benchmark.py --track 1
   ```
5. Run Track 2 (real LLM inference via `llama-server.exe`):
   ```bash
   python research/experiments/prototypes/mn-018-simulated-microworld-evolution/scripts/run_benchmark.py --track 2 --model Qwen3.5-2B --port 8080
   ```
6. Run High-Difficulty Stress Benchmark (`corpus-v2-stress`, $T=150-200$, $K=8$):
   ```bash
   python research/experiments/prototypes/mn-018-simulated-microworld-evolution/scripts/generate_stress_corpus.py
   python research/experiments/prototypes/mn-018-simulated-microworld-evolution/scripts/run_benchmark.py --corpus corpus-v2-stress --track 1
   python research/experiments/prototypes/mn-018-simulated-microworld-evolution/scripts/run_benchmark.py --corpus corpus-v2-stress --track 2 --model Qwen3.5-2B --port 8080
   python research/experiments/prototypes/mn-018-simulated-microworld-evolution/scripts/run_benchmark.py --corpus corpus-v2-stress --track 2 --model Llama-3.2-3B --port 8080
   python research/experiments/prototypes/mn-018-simulated-microworld-evolution/scripts/run_benchmark.py --corpus corpus-v2-stress --track 2 --model Qwen3-4B --port 8080
   ```
