# Gate A Research Charter: Milestone MN-021

**Milestone Identifier:** MN-021 (Federated Causal Graph Synthesis & Epistemic Discrepancy Reconciliation)  
**Track:** NCC Phase 10 (Open-World Causal Federation & Epistemic Governance)  
**Target Subject Model:** Homogeneous pair of $2\times \text{Qwen3.5-2B-Q4_K_M.gguf}$  
**Date Formulated:** 2026-10-12  

---

## 1. Context and Problem Formulation

In Milestone MN-020, Host-Authoritative Concurrency Leases and Dynamic GBNF Affordance Masking eliminated $100\%$ of physical write collisions and race conditions between $2\times \text{Qwen3.5-2B}$ models within closed, stationary episodes. However, scaling multi-agent small language models to dynamic, partially observable open worlds exposes three core failure regimes:

1. **Cognitive Collapse of Total Knowledge Sharing:** Unconditional peer memory sharing forces distinct agents into a centralized shared perspective, eliminating independent local verification and exploratory cognitive diversity.
2. **Temporal Discrepancy & Non-Stationary Truth ($t$ vs $t+n$):** In dynamic environments, an observation by Agent A at tick $t$ (e.g., $S_A(t): \text{valve}=\text{OPEN}$) and a conflicting observation by Agent B at tick $t+n$ (e.g., $S_B(t+n): \text{valve}=\text{CLOSED}$) are both factually accurate if an unobserved environmental transition $p$ occurred at $t_1 \in (t, t+n)$. Without temporal-causal reconciliation, small models perceive peer hallucination or enter irrecoverable contradiction loops.
3. **Flat Memory Saturation & Prompt Degradation:** Flat list AutoDream memory compaction (`[entity_id v{ver} key:val]`) scales linearly with horizon length, threatening the $\le 512$ token forward-pass ceiling.

---

## 2. Formal Hypotheses Formulation

### Hypothesis 1 ($H_1$): Multi-Parent Causal Event Synthesis Efficacy
Structuring narrative history as a Multi-Parent Causal Event Directed Acyclic Graph ($DAG$), wherein candidate consequence events are synthesized from active parent causes and domain invariant rules ($P_1 \land \dots \land P_k \xrightarrow{R} E_{\text{new}}$), will achieve task completion $\ge 85.0\%$ under bounded forward passes ($\le 512$ tokens), whereas unstructured in-context memory baselines (Arm 1) will collapse ($\le 20.0\%$) due to historical amnesia and causal hallucination.

$$\text{Efficacy}(H_1): \quad \text{Resolution}(\text{Arm 3}) \ge 85.0\% \quad \land \quad \Delta_{\text{Arm 3} - \text{Arm 1}} \ge +65.0\%$$

### Hypothesis 2 ($H_2$): Deterministic Epistemic Reconciliation & Anomaly Identification
Host-authoritative temporal window slicing $[t_A, t_B]$ and intervening event DAG traversal will resolve $100\%$ of temporal observation discrepancies, distinguishing legitimate state evolutions ($A \xrightarrow{p} B$) from unobserved anomalies (`CONTESTED`), with zero committed physical invariant breaches.

$$\text{Reconciliation}(H_2): \quad \text{Accuracy}_{\text{classification}} \ge 95.0\% \quad \land \quad \text{Committed Breaches} \equiv 0$$

### Hypothesis 3 ($H_3$): Stochastic Shock Resilience Without Hyper-Vigilance
Introducing low-frequency stochastic world shocks at a realistic $25\%$ anomaly base rate ($20/80$ cases) will demonstrate high task resolution ($\ge 80.0\%$ on shock sub-suite, $\ge 85.0\%$ overall) under autonomous metacognitive probing (`ACTION: PROBE`), while preserving nominal execution efficiency on unshocked cases ($75\%$) without speculative probe hedging or latency inflation ($< 1000\text{ ms}$).

$$\text{Resilience}(H_3): \quad \text{Resolution}_{\text{shock}} \ge 80.0\% \quad \land \quad \text{Resolution}_{\text{nominal}} \ge 85.0\%$$

---

## 3. Falsification Criteria

Milestone MN-021 shall be falsified and rejected if ANY of the following bounds are breached:

1. **Resolution Failure:** Arm 3 end-to-end task completion falls below $85.0\%$ across the $N=80$ benchmark suite on either Track 1 (Simulator) or Track 2 (Real Model Inference).
2. **Coordination Insufficiency:** The performance delta over independent reactive control fails to meet the threshold: $\Delta_{\text{Arm 3} - \text{Arm 2}} < +40.0\%$.
3. **Physical Law Violation:** Any unintercepted physical conservation breach or invalid state transition is committed to the authoritative world state ($\text{Breaches} > 0$).
4. **Token Ceiling Breach:** Peak forward-pass prompt length exceeds the hard budget bound ($B > 512\text{ tokens}$).
5. **Memory Compaction Failure:** Topological AutoDream hierarchical graph compaction falls below the contract bound ($\text{Compaction} < 70.0\%$).
6. **Latency SLA Breach:** Mean forward turn latency on real inference exceeds $1000\text{ ms}$.
