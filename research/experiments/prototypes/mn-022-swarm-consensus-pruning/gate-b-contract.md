# Gate B Evaluation Contract: MN-022 — Asynchronous Multi-Agent Swarm Governance & Consensus Pruning

## 1. Frozen Evaluation Protocol

- **Evaluation Corpus:** $N = 80$ standardized multi-agent swarm scenarios ($M = 5$ agents) across 3 physical domains:
  - Domain 1: Smart Microgrid Swarm Load Balancing ($N = 27$)
  - Domain 2: Multi-Depot Autonomous Fleet Logistics ($N = 27$)
  - Domain 3: Distributed High-Performance Cluster Scheduling ($N = 26$)
- **Network Latency Envelope:** Packet propagation delay $\tau_i \in [0, 5]$ ticks, with stochastic arrival order and $10\%$ out-of-order reordering.
- **Experimental Arms:**
  - **Arm 1 (Flat Baseline):** Uncoordinated asynchronous agents operating without host consensus, leases, or pruning.
  - **Arm 2 (Unpruned Gossip Control):** Direct peer-to-peer event gossip leading to $O(M^2)$ context bloat and unmanaged lock contention.
  - **Arm 3 (Host Consensus Hub & DAG Pruning):** Star-topology consensus, Vector Clock causal DAG, TTL Multi-Resource Leases, AutoDream Swarm $O(M)$ fact card pruning, and Byzantine filtering.
- **Evaluation Tracks:**
  - **Track 1:** Deterministic Host Simulator ($N = 80$ cases $\times 3$ arms $= 240$ episodes).
  - **Track 2:** Real Open-Weights SLM Inference with homogeneous $5 \times \text{Qwen3.5-2B}$ on local `llama-server.exe` ($N = 80$ cases $\times 3$ arms $= 240$ episodes).
  - **Heterogeneous Stress Track:** Mixed swarm of 5 agents across diverse model architectures (Qwen3.5-2B, Qwen3-4B, Llama-3.2-3B).

## 2. Quantitative Acceptance Clauses

| Clause ID | Metric Description | Frozen Acceptance Bound | Mandatory / Optional | Falsification Trigger |
| :---: | :--- | :---: | :---: | :--- |
| **M1** | Swarm Task Resolution Rate (Arm 3) | $\ge 85.0\%$ | Mandatory | Score $< 85.0\%$ on Track 1 or Track 2 |
| **M2** | Coordination Superiority Delta ($\Delta_{\text{Arm 3} - \text{Arm 2}}$) | $\ge +40.0\%$ | Mandatory | Margin $< +40.0\%$ |
| **M3** | Committed Physical Invariant Breaches | $\equiv 0$ | Mandatory | Any invalid mutation committed to world state |
| **M4** | Committed Race Collisions | $\equiv 0$ | Mandatory | Any concurrent conflicting lease mutation |
| **M5** | Per-Agent Prompt Token Ceiling | $\le 512\text{ tokens}$ | Mandatory | Any prompt exceeding $512$ tokens |
| **M6** | AutoDream Swarm Compaction Ratio | $\ge 70.0\%$ | Mandatory | Compaction $< 70.0\%$ against raw gossip |
| **M7** | Mean Turn Latency SLA | $< 1000\text{ ms}$ | Mandatory | Average turn time $\ge 1000\text{ ms}$ on SLM |
| **M8** | Cryptographic Manifest & Evidence Archival | $100\%$ Conformance | Mandatory | Any unhashed file or loose JSON log |

## 3. Operational Rules & Anti-Falsification Invariants

1. **Zero Loose File Bloat Protocol:** All episode execution traces must be archived into standard `audit_logs.zip` archives before manifest freezing. No individual episode `.json` files may be committed to Git.
2. **Cryptographic Sealing:** All code, benchmark definitions, schemas, and configurations must be hashed with SHA-256 into `pre-run-freeze-manifest.json` before benchmark execution. Post-run results and archives must be sealed in `post-run-freeze-manifest.json`.
3. **Independent Line-by-Line Audit:** Every metric in generated academic reports must be directly verified against raw execution telemetry in `audit_logs.zip` before approval.
4. **Strict Verdict Attribution:** If any mandatory clause is not satisfied, the milestone disposition must be classified as `FAIL` or `CONDITIONAL`. No retroactive threshold adjustments are permitted.
5. **Full Prototype Quarantine:** Zero prototype code may be promoted to `src/mong_nhiem/` during MN-022.
