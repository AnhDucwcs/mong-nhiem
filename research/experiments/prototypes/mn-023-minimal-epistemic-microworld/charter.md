# Milestone Charter: MN-023 — Minimal Controlled Microworld & Epistemic Invariant Verification Under Asymmetric Information

## 1. Executive Summary & Research Motivation

Mộng Nhiễm is an open-source empirical research and operating platform engineered to endow Small Language Models (SLMs, $< 4\text{B}$) with robust, stateful, and causally sound operational capabilities. In accordance with Mộng Nhiễm's foundational architectural principles:
1. **Raison d'Être Invariant:** The LLM is an isolated, stochastic reasoning engine emitting structured actions; the Host maintains absolute, single-source-of-truth authority over physical state integrity, access control, and provenance auditing.
2. **Clear Component Boundaries & General Reusability:** System components (world runtime, arbiters, causal DAGs, episodic memory) must exhibit strict decoupling, high testability, and direct integration into the production runtime (`src/mong_nhiem/`). Components are domain-agnostic and are NOT inherently bound to video game scenarios.
3. **Controlled Experimental Testbed:** A *Microworld* is a mathematically formal, controlled laboratory environment designed to isolate, stress-test, and falsify specific system behavior hypotheses. It is neither a final consumer product nor an interactive game engine. Success is evaluated strictly against quantitative research hypotheses ($H_1, H_2, \dots$), acceptance bounds, and empirical evidence logs—never by subjective game completeness.

Previous milestones developed and proved isolated coordination and memory mechanisms:
- MN-018: Host-managed continuous microworld evolution across extended discrete horizons.
- MN-020: Distributed pairwise concurrency arbitration and dynamic affordance masking.
- MN-021: Multi-Parent Causal Event DAGs and Epistemic Discrepancy Reconciliation.
- MN-022: Star-topology swarm governance, non-blocking TTL resource leases, and causal frontier pruning.

However, an imperative scientific gap remains: **Proving the mathematical correctness of world-state integrity and agent epistemics when multiple autonomous agents act concurrently under partial observation, hidden secrets, and asymmetric or conflicting information.**

Milestone MN-023 establishes a **Minimal Controlled Epistemic Microworld** to rigorously falsify and prove:
- Out-of-model authoritative state tracking with zero omniscient leakage.
- Decentralized multi-agent coordination under asymmetric and incomplete information.
- Preservation of subjective belief divergence without premature or false consensus.
- Long-horizon causal integrity and bounded episodic memory ($\le 512\text{ tokens}$).

---

## 2. Research Questions & Formal Hypotheses

### Primary Research Questions

- **RQ1 (Zero Epistemic Leakage):** Can host-authoritative context projections guarantee that an autonomous agent never observes, infers, or exploits unobserved private world state, hidden secrets, or information restricted to other agents?
- **RQ2 (Causal Invariant Under Asymmetric Beliefs):** When multiple agents act concurrently based on incomplete or mutually contradictory beliefs ($B_i \neq B_j$), does the host concurrency arbiter and invariant guard prevent 100% of physical state corruptions and race collisions?
- **RQ3 (Epistemic Criticality Under Pruning):** Does topological AutoDream memory consolidation prune routine interaction histories while preserving 100% of decision-critical causal anchors (secrets, broken promises, discovered clues), sustaining Epistemic Recall $\ge 90.0\%$ under a strict $\le 512\text{ token}$ prompt ceiling?
- **RQ4 (Causal Pivot Propagation):** When an agent executes a pivotal causal action (e.g., revealing a hidden truth, altering a shared dependency), does the Host Causal Event DAG propagate state ripples strictly along verified topological reachability paths?

### Formal Hypotheses

- **$H_1$ (Zero Information Leakage Invariant):** Across all agents $i \in \{1, \dots, M\}$ and all ticks $t \in [0, T_{\max}]$, the agent's prompt context satisfies the Information Horizon Invariant:
  $$K_i(t) \subseteq \text{Observed}_i(t) \cup \text{Inferred}_i(t) \subsetneq \mathcal{W}(t)$$
  with an Epistemic Leakage Score $\equiv 0.0$ (Zero leakage of private facts/secrets belonging to other entities).
- **$H_2$ (World State Invariant & Concurrency Safety):** Under concurrent agent execution with contradictory subjective beliefs ($B_i \neq B_j$), committed world-state mutations exhibit zero physical conservation breaches ($B = 0$) and zero unmanaged race collisions ($C = 0$).
- **$H_3$ (Long-Horizon Causal Anchor Retention Superiority):** Arm 3 achieves an Anchor Retention Rate exceeding Arm 2 by $\Delta R_{\text{causal}} \ge +50.0\%$ across extended temporal separation ($\Delta t \ge 15$ ticks) under strict prompt bounds ($\le 512\text{ tokens}$).
- **$H_4$ (Epistemic Discrepancy Reconciliation Efficacy):** Arm 3 successfully resolves $\ge 80.0\%$ of conflicting multi-agent belief discrepancies using causal provenance temporal graphs ($[t_A, t_B]$), while Arm 2 deadlocks or generates amnesia loops ($\le 20.0\%$).
- **$H_5$ (Non-Omniscient Action Groundedness):** Across all evaluated episodes, $100.0\%$ of agent actions are strictly grounded in that agent's prior subjective observations and causal message receipts ($F_{\text{grounded}} \equiv 100.0\%$), with zero telepathic exploitation of unobserved hidden secrets.
- **$H_6$ (Cognitive Token Budget & Sub-Second Latency):** Mean turn inference latency across all local open-weights SLM evaluations (`Qwen3.5-2B`) remains $< 1000\text{ ms}$, with maximum prompt token count $\max(T_{\text{prompt}}) \le 512\text{ tokens}$.

---

## 3. Experimental Methodology & Arms Definition

### Controlled Experimental Arms

1. **Arm 1 (Flat Omniscient Baseline):**
   - Unmanaged flat state prompts.
   - Tests vulnerability to information contamination, hallucinated secrets, and uncoordinated race conditions.
2. **Arm 2 (Unpruned Subjective Memory Control):**
   - Agents receive private observations, but interaction histories are accumulated without causal branch pruning or epistemic anchoring.
   - Tests context ceiling blowup ($> 512\text{ tokens}$) and recency bias amnesia.
3. **Arm 3 (Host Epistemic Microworld & Causal Architecture):**
   - Authoritative Host Microworld runtime with strict access boundaries.
   - 3-Tier Causal Memory: Tier 1 (Anchor Facts), Tier 2 (Dynamic Personality/Epistemic Traits), Tier 3 (Ephemeral AutoDream Buffer).
   - Multi-Parent Causal Event DAG with Vector Clock tracking.
   - Byzantine Admission Gate + Multi-Resource Lease Arbiter.

### Evaluation Tracks

- **Track 1 (Host Simulator — Deterministic Verification):**
  - Exhaustive state-space simulation ($N = 60$ standardized scenarios) verifying mathematical invariant satisfaction, absence of state corruption, and reachability.
- **Track 2 (Real Model Inference — $3\times\text{Qwen3.5-2B}$ on `llama-server.exe`):**
  - Full neural inference runs evaluating prompt constraint adherence ($\le 512\text{ tokens}$), epistemic leakage, task resolution, and latency ($< 1000\text{ ms}$).

---

## 4. Scope & Non-Goals

### In Scope
- Minimal multi-agent configuration: $M = 3$ heterogeneous autonomous agents.
- Ground-truth hidden states: Private credentials, hidden inventory items, undisclosed event provenance.
- Asymmetric observation channels: Agents observe only local spatial cells or direct message deliveries.
- Controlled causal pivot events: Deliberate actions triggering cascading preconditions across dependent entities.
- Direct consumption of production packages from `src/mong_nhiem/` (zero prototype duplication).
- Cryptographic evidence archival: 100% packaged in `audit_logs.zip` (Zero Loose File Bloat Protocol).

### Non-Goals
- Full interactive game engine implementation: Focus strictly on cognitive and epistemic correctness.
- Large swarms ($M > 10$): Bounded to minimal discriminative scale ($M = 3-5$).
- Continuous audio/visual asset rendering: Bounded to discrete symbolic microworld states.
- Silent promotion into `src/mong_nhiem/`: All experimental code remains quarantined in prototype directory until formal Gate D disposition review.
