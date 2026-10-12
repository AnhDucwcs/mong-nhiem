# MN-021: Federated Causal Graph Synthesis & Epistemic Discrepancy Reconciliation

## 1. Master Strategic Intent

Milestone MN-021 investigates small language model ($< 4\text{B}$ parameter) cognitive governance when scaling multi-agent collaboration to dynamic, partially observable open worlds.

While MN-020 proved that Host Concurrency Leases and Dynamic GBNF Affordance Masking eliminate $100\%$ of physical race conditions between $2\times \text{Qwen3.5-2B}$ models within closed, stationary episodes, open-world scaling presents three core cognitive barriers:
1. **The Cognitive Collapse of Total Sharing:** Unconditionally synchronizing all observations collapses distinct agents into a centralized entity, destroying cognitive diversity and independent local verification.
2. **Temporal Discrepancy & Non-Stationary Truth ($t$ vs $t+n$):** In dynamic worlds, an observation by Agent A at tick $t$ (`switch = CLOSED`) and a conflicting observation by Agent B at tick $t+n$ (`switch = OPEN`) can both be factually correct if an unobserved environmental shock $p$ occurred at $t_1 \in (t, t+n)$. Without temporal causal reconciliation, agents falsely perceive peer hallucination or state corruption.
3. **Flat Memory Saturation:** Flat AutoDream lists expand linearly with long horizons, violating the hard prompt token ceiling ($\le 512$ tokens).

MN-021 establishes a **Federated Causal Graph Substrate**:
- **Multi-Parent Causal Event DAG:** Represents narrative history as a topological graph of events, actions, and preconditions ($P_1 \land P_2 \dots \land P_k \xrightarrow{R} E_{\text{new}}$).
- **Stochastic World Shock Injector:** Injects realistic, low-frequency exogenous shocks ($25\%$ anomaly base rate) to measure black swan resilience without inducing paranoid hyper-vigilance.
- **Epistemic Boundaries & Private Beliefs:** Restricts agents to private local observations, compelling autonomous probing (`ACTION: PROBE <target>`).
- **Deterministic Host Epistemic Reconciler:** Executes a 3-step reconciliation algorithm (window slicing $[t_A, t_B]$, intervening event lookup, and causal transition edge creation $A \xrightarrow{p} B$).
- **Topological AutoDream Federation:** Hierarchical graph clustering delivering $k$-hop causal ancestry subgraphs strictly bounded under $\le 512$ tokens.

---

## 2. Evaluation Scope & Setup

- **Corpus Scale ($N=80$):** 60 nominal cases (75%) + 20 stochastic shock cases (25%) across 3 physical domains:
  1. Martian Biosphere Life Support ($N=27$)
  2. Subsea Hydrothermal Energy Grid ($N=27$)
  3. Orbital Constellation Relay ($N=26$)
- **Model Topology:** Homogeneous pair of $2\times \text{Qwen3.5-2B-Q4_K_M.gguf}$ querying local `llama-server.exe` on Port 18502 ($T=0.0$).
- **Evidence Packaging Protocol:** Standard library `audit_logs.zip` packing all 240 episode audit logs per track, preserving zero loose JSON files in Git.

---

## 3. Directory Layout

```
research/experiments/prototypes/mn-021-causal-graph-synthesis/
├── README.md                          # Master milestone overview & reproduction
├── charter.md                         # Formal Gate A research questions & hypotheses
├── gate-b-contract.md                 # Quantitative evaluation contract & acceptance bounds
├── pre-run-freeze-manifest.json       # Pre-execution cryptographic SHA-256 manifest
├── post-run-freeze-manifest.json      # Post-execution cryptographic SHA-256 manifest
├── schemas/                           # JSON schemas for DAG nodes, epistemic events, and summaries
├── src/                               # Engine: DAG, World Rules, Shock Injector, Reconciler, AutoDream
├── benchmarks/                        # Standardized corpus of 80 scenarios
├── tests/                             # Unit tests for all engine components
├── scripts/                           # Benchmark runner and audit validator
├── runs/                              # Sealed run directories containing audit_logs.zip and run_info.json
└── reports/                           # Academic peer-reviewed benchmark reports
```
