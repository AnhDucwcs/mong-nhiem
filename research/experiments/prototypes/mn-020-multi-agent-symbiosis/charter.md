# Gate A Research Charter: Milestone MN-020

## 1. Executive Summary & Problem Formulation

Milestone MN-020 addresses the **Multi-Agent Symbiosis Frontier** in small language models ($< 4\text{B}$). 

Prior milestones proved that a Host-Authoritative Dual-Engine architecture sustains 100.0% invariant integrity and 95.0% task resolution under continuous non-stationary drift (**MN-019**) for a **solitary** agent. However, in distributed microworlds where $M \ge 2$ autonomous reasoning agents interact with shared state objects concurrently:
1. Greedy action selection causes catastrophic race conditions and conflicting state writes.
2. Uncoordinated execution causes deadlock loops when both agents await the release of contested entities.
3. Natural language inter-agent communication immediately violates the hard token ceiling constraint ($\le 512$ tokens).

This charter establishes the formal Gate A hypotheses, controls, and falsification conditions for evaluating a **Host Concurrency Arbiter & Lease Manager** operating over homogeneous pairs of $2\times \text{Qwen3.5-2B}$ models on local commodity hardware.

---

## 2. Core Research Hypotheses & Falsification Thresholds

### Hypothesis 1 ($H_1$: Symbiotic Efficacy Advantage)
A Host-Authoritative Concurrency Arbiter providing dynamic lease-aware GBNF affordance masking and discrete signalling achieves superior multi-agent task resolution compared to uncoordinated execution:
$$\text{Success}(\text{Arm 3}) \ge 85.0\% \quad \text{and} \quad \Delta_{\text{Arm 3} - \text{Arm 2}} \ge +40.0\%$$
- **Falsification Threshold**: If Arm 3 achieves $< 85.0\%$ task completion across $N=60$ standardized multi-agent scenarios, $H_1$ is falsified.

### Hypothesis 2 ($H_2$: Zero Race Violation Invariant)
Host entity leases and Memento transaction rollback completely eliminate committed concurrent resource collisions:
$$\text{Committed Race Violations}(\text{Arm 3}) \equiv 0$$
- **Falsification Threshold**: If even a single committed race condition or unmanaged contradictory write reaches primary microworld state in Arm 3, $H_2$ is immediately falsified.

### Hypothesis 3 ($H_3$: Context Boundedness under Concurrency)
Scoped AutoDream Fact Card projections preserve bounded prompt token lengths for each individual agent without suffering from global state inflation:
$$\max_{t, m} T_{\text{prompt}}(t, m) \le 512\text{ tokens}$$
- **Falsification Threshold**: If any agent forward pass consumes $> 512$ prompt tokens, $H_3$ is falsified.

### Hypothesis 4 ($H_4$: Multi-Agent Episodic Compaction)
The distributed AutoDream consolidation engine maintains high episodic compaction when summarizing interleaved multi-actor event traces:
$$\text{Compaction Ratio} = 1.0 - \frac{\text{Consolidated Tokens}}{\text{Raw Telemetry Stream}} \ge 70.0\%$$
- **Falsification Threshold**: If mean compaction falls below $70.0\%$, $H_4$ is falsified.

---

## 3. Experimental Protocol & Controls

### Independent Variable: Architectural Governance Arms
1. **Arm 1 (Flat Baseline)**: Uncoordinated multi-agent dispatch without host leases or GBNF masking; full state dump passed to both agents.
2. **Arm 2 (Independent Control)**: Independent single-agent GBNF grammars operating on local sub-goals, but without host concurrency arbitration or resource leasing.
3. **Arm 3 (Host Symbiotic Governance)**: Host Concurrency Arbiter with optimistic entity leasing, dynamic multi-affordance GBNF masking, scoped AutoDream fact cards, and compound causal DAG tracking.

### Controlled Variables
- Primary Reasoning Model: Homogeneous $2\times \text{Qwen3.5-2B-Q4_K_M.gguf}$ querying local `llama-server.exe` (Port 18502).
- Decoding Temperature: $T = 0.0$ (greedy decoding for reproducible causal inference).
- Benchmark Corpus: $N = 60$ standardized multi-agent episodes ($N = 20$ per domain across Microgrid, Orbital, Fleet).
- Max Turns per Episode: $T_{\max} = 30$ compound ticks.
- Evidence Packaging: $100\%$ of episode audit logs compressed into `audit_logs.zip` per run via Python standard library `zipfile`.

---

## 4. Gate A Formal Review Verdict

**`GATE_A_CHARTER_APPROVED`**
Authorizes the formalization of Gate B Quantitative Acceptance Contracts and prototype implementation under strict quarantine in `research/experiments/prototypes/mn-020-multi-agent-symbiosis/`.
