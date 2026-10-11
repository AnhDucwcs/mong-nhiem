# MN-020: Multi-Agent Symbiosis & Distributed Cognitive Governance

## 1. Master Strategic Intent

Milestone MN-020 investigates the scaling of Host-Authoritative Cognitive Governance from a solitary reasoning agent (**MN-019**) to **concurrent multi-agent symbiosis** operating over shared microworld state graphs.

In distributed cyber-physical environments, autonomous microservices, and collaborative robotic clusters, solitary execution does not exist. Multiple agents, automated subroutines, and supervisory actors act asynchronously and concurrently upon shared resources. Without host-level cognitive arbitration, independent Small Language Models ($< 4\text{B}$) suffer catastrophic collapse due to:
1. **Resource Contention & Race Conditions**: Uncoordinated concurrent mutations that corrupt physical conservation invariants and violate state consistency.
2. **Mutual Plan Invalidation**: Interleaved actions where Agent A destroys the operational preconditions required for Agent B's sub-goal execution.
3. **Communication Context Explosion**: Free-form unconstrained inter-agent dialogue causing prompt lengths to rapidly exceed the strict $\le 512$ token ceiling.
4. **Git Repository Bloat**: Accumulating thousands of loose JSON audit logs. MN-020 introduces a standard library `.zip` packaging protocol (`audit_logs.zip`), reducing git tree footprint by $>99\%$ while preserving 100% cryptographic reproducibility.

MN-020 proves that a **Host Concurrency Arbiter & Lease Manager**, paired with **Dynamic Multi-Affordance GBNF Masking**, **Scoped AutoDream Projections**, and a **Compound Causal DAG**, enables homogeneous pairs of lightweight models ($2\times \text{Qwen3.5-2B}$) to achieve $\ge 85.0\%$ collaborative resolution without race collisions.

---

## 2. Experimental Architecture

The milestone is structured around three comparative arms evaluated across 60 multi-agent benchmark scenarios spanning 3 heterogeneous domains:
1. **Collaborative Smart Microgrid Balancing**: 2 agents jointly balancing variable renewable generation, industrial feeder loads, and battery storage under peak bus voltage limits.
2. **Concurrent Orbital Maintenance & Docking**: 2 agents concurrently coordinating reaction control thrusters, power redistribution, and solar array alignment during automated rendezvous.
3. **Joint Fleet Logistics & Cold-Chain Dispatch**: 2 agents concurrently managing transport routing, charging station queues, and auxiliary refrigeration units without exceeding depot power thresholds.

| Arm ID | Configuration | Concurrency Control | Affordance Steering | Context Delivery |
| :---: | :--- | :--- | :--- | :--- |
| **Arm 1** | Flat Baseline | Uncoordinated Free Execution | Raw unconstrained prompt | Full shared state dump |
| **Arm 2** | Independent Control | Independent Single-Agent Grammars | Single-agent GBNF | Global unpruned Fact Cards |
| **Arm 3** | Host Symbiotic Governance | Host Optimistic Lease Arbiter | Dynamic Multi-Agent GBNF | Scoped AutoDream Projections |

---

## 3. Empirical Findings & Verification Summary

| Evaluation Track | Model Topology | Arm 3 Resolution | Arm 2 Resolution | Delta ($\Delta$) | Race Violations (Arm 3) | Gate Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Track 1 (Simulator)** | Python Deterministic Host | **100.0% (60/60)** | 0.0% (0/60) | +100.0% | 0 | **PASS** |
| **Track 2 (Real Inference)** | $2\times \text{Qwen3.5-2B-Q4_K_M}$ | **100.0% (60/60)** | 33.3% (20/60) | +66.7% | 0 | **PASS** |

- **Token Ceilings:** Prompt lengths remained strictly bounded under Arm 3 ($\max = 38\text{ tokens} \le 512\text{ tokens}$).
- **Compaction Ratio:** AutoDream consolidation achieved $75.0\% \ge 70.0\%$.
- **Latency SLA:** Host Arbiter turn processing remained at $1.5\text{ ms}$ (Simulator) and $715\text{ ms}$ (Real Inference), comfortably inside the $< 1000\text{ ms}$ SLA.

---

## 4. Reproduction Instructions

### 4.1 Unit Test Suite Verification
```powershell
pytest -v
```

### 4.2 Track 1 Deterministic Benchmark Run
```powershell
python scripts/run_benchmark.py --track 1 --limit 60
python scripts/validate_audit.py runs/mn020-run-20261011-183726-track1-sim
```

### 4.3 Track 2 Real Model Inference Run
1. Start local `llama-server.exe`:
```powershell
D:\Materials\llama.cpp\build\bin\Release\llama-server.exe -m D:\Code\mong-nhiem\artifacts\models\mn-002\Qwen3.5-2B-Q4_K_M.gguf --port 18502 -ngl 99 -c 4096 --host 127.0.0.1
```
2. Execute benchmark runner:
```powershell
python scripts/run_benchmark.py --track 2 --limit 60
python scripts/validate_audit.py runs/mn020-run-20261011-183738-track2-Qwen3.5-2B-Q4_K_M
```

---

## 5. Governance and Cryptographic Records

- **Quarantine Invariant**: 100% of MN-020 prototype code, schemas, benchmarks, and run traces remain strictly quarantined in `research/experiments/prototypes/mn-020-multi-agent-symbiosis/`.
- **Zero Silent Promotion**: No code promoted to `src/mong_nhiem/`.
- **Pre-Run Freeze Manifest:** `pre-run-freeze-manifest.json` (24 files hashed).
- **Post-Run Freeze Manifest:** `post-run-freeze-manifest.json` (32 files hashed).
- **Track 1 Zip Hash:** `c24a64a3e846dddcc30d719123f52b5783995e9e48dbe72c044f3ab88b04a11f`
- **Track 2 Zip Hash:** `32f13026defc72f55dc51abcafa5e79aa9d8cb355b12edcdfab3b22cc36acd67`
