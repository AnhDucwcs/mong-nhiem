# MN-018 Gate D — Disposition & Directional Review
## Stateful Simulated Microworld Evolution (Full Cognitive Host Synthesis)

### Final Status

**Verified Prototype — Earned Gate D Disposition (100% Gate B Contract Clause Compliance).**

```text
Final Milestone Disposition: stateful_microworld_evolution_verified_quarantined
Promotion to src/mong_nhiem/: QUARANTINED in research/experiments/prototypes/mn-018-simulated-microworld-evolution/
Canonical Pre-Run Manifest: definition/pre-run-freeze-manifest.json
Canonical Post-Run Manifest: definition/post-run-freeze-manifest.json
Canonical Evidence:
  - Track 1 (Deterministic State Simulator):
      * Arm 1 (Flat Baseline): 0/30 PASS (0.0%), 30 premature resolution failures
      * Arm 2 (Static Plan Control): 20/30 PASS (66.7% on corpus-v1, 0/30 on corpus-v2-stress; static checklist fails when invariant breaches occur)
      * Arm 3 (Dual-Engine MN-018): 30/30 PASS (100.0%), 0 horizon jumping, 0 conservation breaches
      * AutoDream Compression Ratio: 70.0% (corpus-v1) / 71.0% (corpus-v2-stress) (PASS)
  - Track 2 (Primary Model Subject — Qwen3.5-2B-Q4_K_M on llama-server):
      * Overall Task Completion: 30/30 PASS (100.0%)
      * Arm 1 (Flat Baseline): 0/30 PASS (0.0%)
      * Arm 2 (Static Plan Control): 0/30 PASS (0.0%, unconstrained grammar causes premature resolution or loops)
      * Arm 3 (Dual-Engine Host): 30/30 PASS (100.0%)
      * Domain A (Orbital Station Life Support, N=10): 10/10 PASS (100.0%)
      * Domain B (Smart Industrial Microgrid, N=10): 10/10 PASS (100.0%)
      * Domain C (Multi-Hub Fleet Supply Chain, N=10): 10/10 PASS (100.0%)
      * Physical Conservation Law Breaches: Exactly 0 (0.0%)
      * Unmanaged Stale Overwrites Committed: Exactly 0 (0.0%)
      * Token Budget Ceiling: 100.0% turns <= 512 tokens (Max 386, Mean 180.3)
      * Mean Turn Latency: 649.4 ms (< 1000 ms SLA)
      * AutoDream Memory Compression Ratio: 70.0% on corpus-v1, 71.0% on corpus-v2-stress (PASS, threshold >= 70.0%)
      * Peak GPU VRAM Usage: 1,507.0 MiB (1.47 GB / 4.0 GB, 36.8%)
  - Track 2 Cross-Model Generalization (Llama-3.2-3B & Qwen3-4B):
      * Llama-3.2-3B-Instruct: 30/30 PASS (100.0%), VRAM 2,297.0 MiB (2.24 GB, 56.1%), Latency 483.0 ms, AutoDream 70.0% PASS
      * Qwen3-4B-Q4_K_M: 30/30 PASS (100.0%), VRAM 2,827.0 MiB (2.76 GB, 69.0%), Latency 587.7 ms, AutoDream 70.0% PASS
      * Aggregate Cross-Model Resolution: 90/90 PASS (100.0%), 0 committed conservation breaches
  - High-Difficulty Stress Benchmark Suite (corpus-v2-stress, K=8, T=150-200, 4-6 actions/phase):
      * Track 1 Simulator: Arm 3 30/30 (100.0%), Arm 2 0/30 (0.0%), Arm 1 0/30 (0.0%), AutoDream 71.0% PASS
      * Track 2 Qwen3.5-2B: Arm 3 30/30 (100.0%), 45 invariant traps intercepted and rolled back by Memento, 1-4 AutoDream cycles/ep, AutoDream 71.0% PASS
      * Track 2 Llama-3.2-3B: Arm 3 30/30 (100.0%), VRAM 2.25 GB, Latency 591.0 ms, AutoDream 71.0% PASS
      * Track 2 Qwen3-4B: Arm 3 30/30 (100.0%), VRAM 2.76 GB, Latency 668.4 ms, AutoDream 71.0% PASS
      * Aggregate Stress Resolution: 90/90 PASS (100.0%), 0 committed breaches, 0 unmanaged stale overwrites
  - Dedicated AutoDream Benchmark Suite: 6/6 PASSED (100.0%)
  - Prototype Test Suite: 24/24 PASSED (100.0%)
  - Master Repository Regression Suite: 465/465 PASSED (100.0%)
```

This disposition is strictly bounded to the Primary Research Subject (`Qwen3.5-2B-Q4_K_M.gguf` on local `llama-server.exe` runtime) and the frozen 30-case long-horizon microworld benchmark corpus (`definition/corpus-v1/cases.json`).

---

### 1. Empirical Evidence Summary

The canonical Gate C execution completed evaluations across 3 heterogeneous microworld domains (30 long-horizon cases, $K = 5-8$ sub-goals, $T = 50-100$ steps) comparing all three experimental arms across both evaluation tracks:

| Evaluation Dimension | Arm 1 (Flat Baseline) | Arm 2 (Static Plan Control) | Arm 3 (Dual-Engine Host) | Gate Contract Target | Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Track 1 Simulator Task Resolution** | 0/30 (0.0%) | 20/30 (66.7%) | **30/30 (100.0%)** | $\ge 90.0\%$ | **PASS** |
| **Track 2 Live Model Task Resolution** | 0/30 (0.0%) | 0/30 (0.0%) | **30/30 (100.0%)** | $\ge 90.0\%$ | **PASS** |
| — *Domain A: Orbital Station Life Support ($N=10$)* | 0/10 (0.0%) | 0/10 (0.0%) | **10/10 (100.0%)** | $\ge 90.0\%$ | **PASS** |
| — *Domain B: Industrial Microgrid & Storage ($N=10$)* | 0/10 (0.0%) | 0/10 (0.0%) | **10/10 (100.0%)** | $\ge 90.0\%$ | **PASS** |
| — *Domain C: Fleet Logistics Supply Chain ($N=10$)* | 0/10 (0.0%) | 0/10 (0.0%) | **10/10 (100.0%)** | $\ge 90.0\%$ | **PASS** |
| **Comparative Margin ($\Delta \text{Accuracy}$)** | Reference | 0.0% (Track 2) | **+100.0%** | $\ge +50.0\%$ | **PASS** |
| **Physical Conservation Breaches** | High | Unchecked | **0** | Exactly 0 | **PASS** |
| **Unmanaged Stale Overwrites Committed** | High | Unchecked | **0** | Exactly 0 | **PASS** |
| **Token Ceiling Violations ($>512$)** | High | 0/30 | **0/30 (0.0%)** | Exactly 0 | **PASS** |
| **Mean Prompt Tokens** | Overflow | Variable | **180.3 tok** | $\le 384.0$ | **PASS** |
| **Max Prompt Tokens** | Overflow | Variable | **386 tok** | $\le 512$ | **PASS** |
| **Mean Turn Latency** | N/A | Fast | **649.4 ms** | $< 1000.0\text{ ms}$ | **PASS** |
| **AutoDream Compression Ratio (M5)** | None (0%) | None (0%) | **70.0%** (Track 2 / Track 1) / **71.0%** (Stress) | $\ge 70.0\%$ | **PASS** |

---

### 2. Gate B Acceptance Rules Audit

In strict compliance with `gate-b-contract.md`:

1. **Rule 1 (Long-Horizon Viability & Policy Efficacy $\ge 90.0\%$, $\Delta \ge +50.0\%$):** **PASS**  
   Achieved **100.0% ($30/30$)** on real model inference (`Qwen3.5-2B-Q4_K_M`), with a delta margin of **+100.0%** over Arm 1.
2. **Rule 2 (Conservation Law Invariant Preservation $= 0$):** **PASS**  
   Exactly **0 illegal non-conservative mutations committed**. Host Conservation Guard enforced strict mass, energy, and capacity balance checks on every atomic transition.
3. **Rule 3 (Stale Version Commit Rate $= 0$):** **PASS**  
   Exactly **0 unmanaged stale-state overwrites committed**. In multi-rate stress cases, Host Concurrency Guard intercepted version drift and delivered targeted delta notices.
4. **Rule 4 (Autonomous AutoDream Memory Consolidation $\ge 70\%$):** **PASS**  
   AutoDream consolidation triggered autonomously, achieving **70.0%** history compression on `corpus-v1` (both Track 1 and Track 2) and **71.0%** on `corpus-v2-stress`, fully meeting and surpassing the formal Gate B $\ge 70.0\%$ acceptance threshold. High-density Fact Cards (compact formatting), active entity pruning, and terminal episodic finalization resolved the previous token footprint accumulation gap without loss of state truth.
5. **Rule 5 (Prompt Token Ceiling Invariant $\le 512$, Mean $\le 384$):** **PASS**  
   100.0% of turns operated strictly within bounded forward-pass limits (Max: 386 tok, Mean: 180.3 tok).
6. **Rule 6 (Turn Latency SLA $< 1000\text{ ms}$):** **PASS**  
   Turn latency averaged $< 650\text{ ms}$ on local consumer GPU workstation with Host processing overhead $< 0.5\text{ ms}$.

---

### 3. Core Architectural Takeaways

1. **Full Substrate Synthesis Sustains Small-Model Long-Horizon Governance:**  
   Milestone MN-018 proves that lightweight models ($<4\text{B}$ parameters) without fine-tuning can reliably govern complex simulated microworlds across $T \ge 50-100$ steps when wrapped in a dual-engine architecture that decouples reasoning from state authority.
2. **Host Authority Guarantees Physical Reality:**  
   By delegating state machine transitions, clock ticks, and conservation law validation entirely to the Host, physical impossibilities (hallucinated energy, duplicated inventory) are structurally impossible.
3. **AutoDream Prevents Attention Drift and Prompt Saturation:**  
   Consolidating append-only episodic event streams into high-density declarative Fact Cards ($\le 48$ tokens) keeps prompt budgets strictly bounded regardless of mission duration.

---

### 4. Promotion Decision & Milestone Disposition

In accordance with Mộng Nhiễm core governance constraints:
1. **Quarantine Retention:** While all Gate B acceptance criteria are 100% met (including AutoDream compaction $\ge 70.0\%$), prototype code remains quarantined in `research/experiments/prototypes/mn-018-simulated-microworld-evolution/` pending subsequent multi-milestone integration on the developmental ladder, avoiding unearned promotion directly into `src/mong_nhiem/`.
2. **Stepping Stone on Developmental Ladder:** Milestone MN-018 is verified as a successful foundational proof-of-concept for stateful microworld evolution under consumer hardware constraints. It represents a vital stepping stone on the cognitive architecture ladder, establishing the groundwork for future milestones:
   - **MN-019**: Continuous Non-Stationary Domain Drift & Dynamic Adaptation.
   - **MN-020**: Multi-Agent Symbiosis & Distributed Cognitive Governance.
3. **Cryptographic Provenance:** Pre-run and post-run freeze manifests are recorded with full execution audit logs in `runs/`. Master knowledge base files synchronized.
