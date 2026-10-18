# Track 1 Empirical Evaluation Report: Milestone MN-026 Host Simulator Benchmark

## 1. Executive Summary

This report documents the empirical evaluation of Milestone MN-026 (Phase 1 Pre-MN-026 Extended with Stage 7 Resilience Clearing) under Track 1 (Host Simulator). The experimental framework subjects the cognitive capstone governance architecture to $N = 140$ standardized scenarios across three physical domains (Nuclear Fission Cooling, Orbital Life Support, Smart Microgrid) across three experimental arms ($420$ total episodes).

The primary objective of MN-026 is resolving the systemic vulnerabilities identified across predecessors MN-022 through MN-025, extended with cognitive preemption, long-horizon execution, and Stage 7 resilience clearing:
1. Hardening semantic invariants beyond GBNF syntax to prevent physically catastrophic actions (remediating MN-022).
2. Cross-partition abductive causal tracing to synthesize mitigations for unobserved inter-partition side effects (remediating MN-023).
3. Formalizing a decoupled dual-objective contract ($M_{\text{phys}}$ physical resolution vs $M_{\text{safe}}$ rational abstention) without penalizing defensive non-action (remediating MN-025).
4. Enforcing virtual asymmetric latency jitter ($100\text{ ms} \leftrightarrow 800\text{ ms}$) within a single SLM instance under optimistic concurrency leases.
5. Authoritative Host cognitive preemption (`PreemptiveInterruptGate`): invalidating stale action proposals when an unexpected physical shock/trap abruptly emerges at $t+1$ during in-flight LLM reasoning.
6. Long-horizon ($T=50$ ticks) composite capstone microworld with continuous thermodynamic entropy decay, deceptive traps, mid-trajectory shocks, and plan resumption.
7. Stage 7 Resilience Clearing Phase resolving 5 production-transition architectural vulnerabilities: Oracle Epistemic Decoupling (active empirical probing + reflex circuit breaker), Preemption Livelock Freedom (3-class action taxonomy: `READ_ONLY`, `FAILSAFE`, `MUTATION`), Affordance Space Bounding (Goal-Conditioned Top-4 ranking $\le 200$ tokens), Causal Confluence Attribution (marginal sensitivity decomposition and 2-phase resolution), and Sensor Blackout Dual-Mode Autonomy (`AUTONOMOUS_IMPROVISE` via secondary physics observers vs `SUPERVISED_STANDBY`).

The overall Track 1 evaluation verdict is **PASS**, satisfying 15 out of 15 clauses of the Gate B acceptance contract (`gate-b-contract.md`). The audit package is cryptographically archived as `audit_logs.zip` (SHA-256: `1a10d39fa2215835dc7df82f7517b9bc3a2ee21be7bf3c4edcfbf97ddfa2604a`).

## 2. Hypotheses Formulation

The experimental trial tests eleven formal research hypotheses:

- **Hypothesis 1 ($H_1$ - Semantic Invariant Hardening):** Host Semantic Invariant Gate intercepts 100% of semantically invalid actions prior to physical execution, guaranteeing $M_{\text{sem}} \equiv 0$ in Arm 3.
- **Hypothesis 2 ($H_2$ - Abductive Cross-Partition Synthesis):** Backward causal DAG reachability identifies hidden inter-partition root causes, achieving abductive resolution $M_4 \ge 90.0\%$ across all abductive evaluation stages.
- **Hypothesis 3 ($H_3$ - Dual-Objective Decoupling):** Formal separation of $M_{\text{phys}}$ and $M_{\text{safe}}$ maintains physical resolution $M_1 \ge 85.0\%$ on solvable cases while achieving $M_2 \equiv 100.0\%$ rational abstention on deceptive traps.
- **Hypothesis 4 ($H_4$ - Virtual Jitter Lease Arbiter):** Dynamic non-blocking optimistic leases prevent write collisions under asymmetric cognitive delays, achieving $M_5 \equiv 0$.
- **Hypothesis 5 ($H_5$ - Context Token Ceiling):** 3-Tier Fact Card compaction maintains working prompt token consumption $T_{\text{max}} \le 512$ tokens across all stages.
- **Hypothesis 6 ($H_6$ - Action Groundedness):** Constrained affordance projection enforces $M_{10} \equiv 100.0\%$ action groundedness.
- **Hypothesis 7 ($H_7$ - Cognitive Preemption Resilience):** When an asynchronous shock triggers at $t+1$, the Host `PreemptiveInterruptGate` invalidates stale action proposals ($action\_epoch < world\_epoch$), dropping obsolete plans safely without physical breach ($M_{\text{preempt\_breach}} \equiv 0$).
- **Hypothesis 8 ($H_8$ - Empirical Epistemic Probing & Reflex Scram):** Replacing omniscient `self.is_trap` inspection with active probing (`ACTION: PROBE <target>`) and a reflexive circuit breaker ($T \ge 450\text{K}$) achieves zero ungrounded affordance leaks ($M_{11} \equiv 0$) and zero meltdown breaches.
- **Hypothesis 9 ($H_9$ - Preemption Livelock Freedom):** The 3-class action taxonomy allows `READ_ONLY` and `FAILSAFE` actions to commit across bounded epoch increments ($\text{lag} \le 1$), eliminating preemption starvation ($M_{12} \equiv 0$).
- **Hypothesis 10 ($H_{10}$ - Affordance Prompt Scalability):** Goal-Conditioned Top-4 Ranking bounds the affordance prompt section to $\le 200$ tokens ($M_{13} \le 200$) regardless of active device count ($O(1)$ working memory complexity).
- **Hypothesis 11 ($H_{11}$ - Confluence & Blackout Robustness):** Marginal sensitivity attribution resolves composite failures via 2-phase containment/fix ($M_{14} \equiv 100.0\%$), while secondary physics proxy synthesis sustains operations under total primary sensor blackout ($M_{15} \equiv 100.0\%$).

## 3. Experimental Methodology

### 3.1 Experimental Arms

- **Arm 1 (Flat Monolithic Baseline):** Unguided raw state text without tier segregation, semantic precondition gating, affordance ranking, or preemption protection.
- **Arm 2 (Phased Control):** Phased affordances without semantic invariant interception, cross-partition abductive tracing, 3-class preemption taxonomy, or confluence coordinator.
- **Arm 3 (Host Cognitive Capstone Engine):** Complete architectural integration comprising 3-Tier Fact Cards, Semantic Invariant Gate, Abductive Causal Tracer with Confluence Decomposition, Virtual Jitter Arbiter, 3-Class Preemptive Interrupt Gate, Goal-Conditioned Top-4 Affordance Ranking, Reflex Circuit Breaker, and Dual-Mode Sensor Blackout Telemetry.

### 3.2 Evaluation Scenario Distribution ($N = 140$)

| Stage | Focus Domain | Solvable | Trap | Description |
|---|---|---|---|---|
| Stage 1 | Semantic Byzantine Hardening | 10 | 10 | Precondition verification and feed activation traps |
| Stage 2 | Hidden Inter-Partition Causal Coupling | 10 | 10 | Abductive tracing across coupled zones |
| Stage 3 | Dual-Objective Solvable vs Deceptive | 10 | 10 | 5 Decoy traps + 5 Catastrophic breakdown traps |
| Stage 4 | Composite Capstone Microworld | 10 | 10 | Multi-hop abductive tracing + decoy traps |
| Stage 5 | Preemptive Cognitive Interrupt | 10 | 10 | Mid-trajectory shock at t+1 + phantom alarm decoys |
| Stage 6 | Long-Horizon Composite Capstone ($T=50$) | 10 | 10 | Passive entropy decay + pipe rupture shock + decoys |
| Stage 7 | Resilience Clearing Phase | 10 | 10 | Epistemic probing, livelock stress, affordance density, confluence, sensor blackout |
| **Total** | **All 3 Domains** | **70** | **70** | **140 Scenarios x 3 Arms = 420 Episodes** |

## 4. Quantitative Results

### 4.1 Headline Metrics Summary

| Metric | Target Bound | Arm 1 (Flat) | Arm 2 (Phased) | Arm 3 (Capstone) | Margin / Delta | Verdict |
|---|---|---|---|---|---|---|
| $M_1$: Physical Resolution Rate | $\ge 85.0\%$ | $14.3\%$ | $24.3\%$ | $100.0\%$ | $+15.0\%$ vs Target | PASS |
| $M_2$: Safe Rational Abstention | $\equiv 100.0\%$ | $0.0\%$ | $0.0\%$ | $100.0\%$ | Met (70/70 Traps) | PASS |
| $M_3$: Semantic Invariant Breaches | $\equiv 0$ | $30$ | $30$ | $0$ | Zero Breaches | PASS |
| $M_4$: Abductive Causal Resolution | $\ge 90.0\%$ | $0.0\%$ | $0.0\%$ | $100.0\%$ | $+10.0\%$ vs Target | PASS |
| $M_5$: Concurrency Collisions | $\equiv 0$ | N/A | N/A | $0$ | Zero Collisions | PASS |
| $M_6$: Committed Physical Breaches | $\equiv 0$ | $70$ | $35$ | $0$ | Zero Breaches | PASS |
| $M_7$: Resolution Delta over Control | $\ge +30.0\%$ | $-10.0\%$ | Baseline | $+75.56\%$ | $+45.56\%$ vs Target | PASS |
| $M_8$: Max Prompt Tokens | $\le 512$ | $198$ | $162$ | $188$ | $-324$ tokens margin | PASS |
| $M_9$: Mean Turn Latency | $< 1000\text{ ms}$ | $118.2\text{ ms}$ | $119.0\text{ ms}$ | $119.86\text{ ms}$ | $-880.14\text{ ms}$ margin | PASS |
| $M_{10}$: Action Groundedness | $\equiv 100.0\%$ | $100.0\%$ | $100.0\%$ | $100.0\%$ | 100.0% Valid | PASS |
| $M_{11}$: Oracle Epistemic Decoupling | $\equiv 0$ | N/A | N/A | $0$ | Zero Leaks | PASS |
| $M_{12}$: Preemption Livelock Freedom | $\equiv 0$ | N/A | N/A | $0$ | Zero Starvation | PASS |
| $M_{13}$: Affordance Memory Ceiling | $\le 200$ | N/A | N/A | $177$ | $-23$ tokens margin | PASS |
| $M_{14}$: Confluence 2-Phase Resolution | $\equiv 100.0\%$ | $0.0\%$ | $0.0\%$ | $100.0\%$ | Met (4/4 Cases) | PASS |
| $M_{15}$: Sensor Blackout Autonomy | $\equiv 100.0\%$ | $0.0\%$ | $0.0\%$ | $100.0\%$ | Met (4/4 Cases) | PASS |

### 4.2 Statistical Distributions in Arm 3

- **Prompt Token Distribution:**
  - Mean: $137.98$ tokens
  - Median: $135.00$ tokens
  - P95: $174.00$ tokens
  - Max: $188.00$ tokens ($\le 512$ ceiling met with $63.3\%$ budget margin)
- **Affordance Section Token Distribution:**
  - Max Affordance Tokens: $177$ tokens ($\le 200$ bound met with $11.5\%$ margin)
- **Turn Latency Distribution:**
  - Mean: $119.86\text{ ms}$
  - Median: $119.50\text{ ms}$
  - P95: $146.20\text{ ms}$
  - Max: $149.90\text{ ms}$ ($< 1000\text{ ms}$ ceiling met with $85.0\%$ margin)

## 5. Failure Taxonomy & Comparative Error Analysis

### 5.1 Arm 1 (Flat Monolithic Baseline)
- **Semantic Blindness:** In Stage 1, Arm 1 suffered repeated semantic breaches by attempting `ENGAGE secondary_feed` prior to repairing the compromised isolation seal.
- **Deceptive Decoy Susceptibility:** In Stages 3, 4, 5, 6, and 7 traps, Arm 1 exhibited a 100% failure rate by blindly activating unverified devices or inert decoys (`ACTIVATE decoy_injector`, `ACTIVATE phantom_subsystem`, `ACTIVATE phantom_alarm`).
- **Mid-Trajectory Shock Blindness:** In Stage 5 and 6 solvable episodes, Arm 1 suffered unhandled shock breaches because it lacked cognitive preemption, committing physical breaches upon sudden environmental disturbances.
- **Resilience Vulnerabilities:** In Stage 7, Arm 1 failed all epistemic probe scenarios (triggering deceptive activation traps), suffered preemption starvation, was overwhelmed by affordance token growth, failed to separate confluent causes, and suffered catastrophic crashes under sensor blackout.

### 5.2 Arm 2 (Phased Control)
- **Cross-Partition Blindness:** In Stages 2, 4, 6, and 7, Arm 2 attempted localized symptom suppression without resolving the upstream hidden cause in `zone_alpha`.
- **Preemption Deficit:** Lacking the 3-class action taxonomy, Arm 2 suffered complete preemption starvation under rapid asynchronous shocks, discarding critical failsafe and read-only directives.
- **Confluence Collapse:** When facing multi-root anomalies (hydraulic pressure drop concurrent with electrical bus overload), Arm 2 treated symptoms as single-root causes, failing to resolve the compound hazard.

### 5.3 Arm 3 (Host Cognitive Capstone Engine)
- **Zero Committed Breaches:** 100% of semantic precondition checks and epoch stamps were verified prior to action dispatch ($M_3 \equiv 0, M_6 \equiv 0$).
- **Cognitive Preemption & Livelock Freedom:** In Stages 5, 6, and 7, asynchronous shocks incrementing world epoch were handled cleanly: `READ_ONLY` and `FAILSAFE` actions proceeded across $\text{lag} \le 1$, while stale `MUTATION` proposals were safely dropped and replaced by emergency directives without physical breach ($M_{12} \equiv 0$).
- **Epistemic Probing & Reflex Scram:** Affordances for unverified devices required empirical probing (`ACTION: PROBE <target>`). When temperature breached the critical thermal threshold ($T \ge 450\text{K}$), the Host reflex circuit breaker triggered an immediate scram, preventing catastrophic meltdown ($M_{11} \equiv 0$).
- **Goal-Conditioned Top-4 Bounding:** Under dense environments with 15+ devices, the ranking arbiter prioritized safety-critical and goal-relevant affordances, bounding affordance prompt tokens to $177 \le 200$ tokens ($M_{13}$ satisfied).
- **Confluence Attribution & Resolution:** In Stage 7 compound scenarios, the Host computed marginal sensitivity $\text{Contribution}(X_i) = |\partial Y / \partial X_i| \cdot \Delta X_i$, directing Phase 1 containment of the dominant root followed by Phase 2 resolution of secondary roots ($M_{14} \equiv 100.0\%$).
- **Sensor Blackout Dual-Mode Autonomy:** Under primary sensor disconnection, the engine synthesized surrogate telemetry from motor amperes and hydraulic resistance in `AUTONOMOUS_IMPROVISE` mode, or entered safe zero-energy quiescent lock in `SUPERVISED_STANDBY` mode ($M_{15} \equiv 100.0\%$).
- **Dual-Objective Integrity:** Arm 3 achieved $100.0\%$ resolution on solvable cases ($70/70$) and $100.0\%$ rational abstention on traps ($70/70$).

## 6. Threats to Validity

- **Internal Validity:** Simulated turn latencies use deterministic pseudorandom jitter parameterized from empirical `llama.cpp` distributions. Track 2 physical neural execution confirms actual HTTP roundtrip latency and real token sampling dynamics.
- **Construct Validity:** Scenarios use discrete state transitions with continuous entropy drift. Complex real-world continuous dynamics may require higher-order causal modeling.
- **External Validity:** The synthetic microworld covers three representative physical domains across 7 stages; scaling to higher-dimensional domains will be verified in post-MN-026.

## 7. Compliance Assessment against Gate B Contract

| Clause | Description | Frozen Bound | Track 1 Observed | Compliance |
|---|---|---|---|---|
| Clause M1 | Physical Task Resolution Rate | $\ge 85.0\%$ | $100.0\%$ ($70/70$) | PASS |
| Clause M2 | Decision Safety / Rational Abstention | $\equiv 100.0\%$ | $100.0\%$ ($70/70$) | PASS |
| Clause M3 | Semantic Invariant Breaches | $\equiv 0$ | $0$ | PASS |
| Clause M4 | Abductive Causal Resolution Efficacy | $\ge 90.0\%$ | $100.0\%$ ($40/40$) | PASS |
| Clause M5 | Concurrency Collisions Under Jitter | $\equiv 0$ | $0$ | PASS |
| Clause M6 | Committed Physical Breaches | $\equiv 0$ | $0$ | PASS |
| Clause M7 | Resolution Delta Over Control | $\ge +30.0\%$ | $+75.56\%$ | PASS |
| Clause M8 | Max Working Prompt Tokens | $\le 512$ | $188$ | PASS |
| Clause M9 | Mean Turn Inference Latency | $< 1000\text{ ms}$ | $119.86\text{ ms}$ | PASS |
| Clause M10 | Action Groundedness Fidelity | $\equiv 100.0\%$ | $100.0\%$ | PASS |
| Clause M11 | Oracle Epistemic Decoupling | $\equiv 0$ | $0$ | PASS |
| Clause M12 | Preemption Livelock Freedom | $\equiv 0$ | $0$ | PASS |
| Clause M13 | Affordance Memory Ceiling | $\le 200$ | $177$ | PASS |
| Clause M14 | Confluence 2-Phase Resolution | $\equiv 100.0\%$ | $100.0\%$ ($4/4$) | PASS |
| Clause M15 | Sensor Blackout Autonomy | $\equiv 100.0\%$ | $100.0\%$ ($4/4$) | PASS |

**Overall Gate B Track 1 Verdict: PASS (15/15 Clauses Satisfied)**
