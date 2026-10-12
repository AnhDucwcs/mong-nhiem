# MN-022: Asynchronous Multi-Agent Swarm Governance & Consensus Pruning

## Overview

Milestone MN-022 scales multi-agent cognitive governance from pairwise dyads ($M = 2$, lockstep synchronous) to asynchronous multi-agent swarms ($M \ge 5$) operating under stochastic network latency ($\tau_i \in [0, 5]$ ticks), out-of-order packet arrival, and partial Byzantine/noisy node faults.

The primary architectural breakthrough is the **Host Consensus Hub & Topological DAG Pruning Substrate**:
- Replaces naive quadratic gossip communication ($O(M^2)$) with star-topology consensus hub distribution ($O(M)$), strictly preserving the $\le 512$ token cognitive capacity ceiling.
- Enforces Distributed Multi-Resource Leases with discrete Time-To-Live (TTL) expiration and lock stealing.
- Employs a Multi-Parent Causal Event DAG with Vector Clock ordering to resolve out-of-order mutations and prune finalized DAG branches.
- Implements Byzantine Proposal Filtering to quarantine corrupted or conservation-violating actions at the host boundary without stalling peer agents.

## Directory Structure

```
mn-022-swarm-consensus-pruning/
├── README.md                           # This document
├── charter.md                          # Gate A charter and formal hypotheses
├── gate-b-contract.md                  # Frozen Gate B acceptance contract
├── gate-d-disposition-review.md        # Gate D architectural disposition
├── pre-run-freeze-manifest.json        # Pre-execution SHA-256 cryptographic manifest
├── post-run-freeze-manifest.json       # Post-execution SHA-256 cryptographic manifest
├── schemas/                            # JSON validation schemas
│   ├── swarm-event.schema.json
│   ├── swarm-lease.schema.json
│   └── run-summary.schema.json
├── src/                                # Core prototype modules (quarantined)
│   ├── async_world_engine.py           # Multi-domain asynchronous microworld simulation
│   ├── network_transport.py            # Latency queue and packet reordering model
│   ├── swarm_concurrency_arbiter.py    # TTL multi-resource lease manager
│   ├── consensus_pruner.py             # Vector clock causal DAG & branch pruner
│   ├── byzantine_filter.py             # Malformed & invalid action admission filter
│   ├── autodream_swarm.py              # Bounded topological context builder (<= 512 tok)
│   ├── agent_worker.py                 # Multi-model LLM inference worker (Qwen/Llama)
│   ├── orchestrator_swarm.py           # Swarm coordinator for Arms 1, 2, and 3
│   └── pack_evidence_zip.py            # Evidence zip archive packer
├── benchmarks/                         # Standardized evaluation corpus
│   └── corpus_v1_swarm.py              # N = 80 swarm benchmark scenarios (M = 5)
├── tests/                              # Unit and integration test suite
│   ├── test_async_world_engine.py
│   ├── test_network_transport.py
│   ├── test_swarm_arbiter.py
│   ├── test_consensus_pruner.py
│   ├── test_byzantine_filter.py
│   ├── test_autodream_swarm.py
│   └── test_orchestrator_swarm.py
├── scripts/                            # Benchmark execution scripts
│   ├── run_benchmark.py                # Dual-track runner for Track 1 and Track 2
│   ├── run_mixed_benchmark.py          # Heterogeneous multi-model swarm runner
│   └── validate_audit.py               # Archive verification script
├── reports/                            # Academic evaluation reports
│   ├── mn-022-track1-report.md
│   ├── mn-022-track2-report.md
│   └── mn-022-mixed-model-report.md
└── runs/                               # Archived execution telemetry (.zip)
```

## Reproduction & Verification Commands

1. **Run Unit & Integration Test Suite:**
   ```powershell
   pytest research/experiments/prototypes/mn-022-swarm-consensus-pruning/tests/ -v
   ```

2. **Run Track 1 (Host Simulator — $N = 80$):**
   ```powershell
   python research/experiments/prototypes/mn-022-swarm-consensus-pruning/scripts/run_benchmark.py --track 1 --cases 80
   ```

3. **Run Track 2 (Homogeneous $5 \times \text{Qwen3.5-2B}$ — $N = 80$):**
   ```powershell
   python research/experiments/prototypes/mn-022-swarm-consensus-pruning/scripts/run_benchmark.py --track 2 --cases 80 --port 18502
   ```

4. **Run Heterogeneous Cross-Model Swarm Evaluation:**
   ```powershell
   python research/experiments/prototypes/mn-022-swarm-consensus-pruning/scripts/run_mixed_benchmark.py --cases 80 --port 18502
   ```

5. **Verify Telemetry & Evidence Archive:**
   ```powershell
   python research/experiments/prototypes/mn-022-swarm-consensus-pruning/scripts/validate_audit.py
   ```
