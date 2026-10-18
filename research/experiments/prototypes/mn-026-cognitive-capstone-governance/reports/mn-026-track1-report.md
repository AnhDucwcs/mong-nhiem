# Track 1 Empirical Evaluation Report: Milestone MN-026 Host Simulator Benchmark

## 1. Executive Summary

This report documents the empirical evaluation of Milestone MN-026 (Phase 1 Pre-MN-026 Extended) under Track 1 (Host Simulator). The experimental framework subjects the cognitive capstone governance architecture to $N = 120$ standardized scenarios across three physical domains (Nuclear Fission Cooling, Orbital Life Support, Smart Microgrid) across three experimental arms ($360$ total episodes).

The primary objective of MN-026 is resolving the systemic vulnerabilities identified across predecessors MN-022 through MN-025, extended with cognitive preemption and long-horizon execution:
1. Hardening semantic invariants beyond GBNF syntax to prevent physically catastrophic actions (remediating MN-022).
2. Cross-partition abductive causal tracing to synthesize mitigations for unobserved inter-partition side effects (remediating MN-023).
3. Formalizing a decoupled dual-objective contract ($M_{\text{phys}}$ physical resolution vs $M_{\text{safe}}$ rational abstention) without penalizing defensive non-action (remediating MN-025).
4. Enforcing virtual asymmetric latency jitter ($100\text{ ms} \leftrightarrow 800\text{ ms}$) within a single SLM instance under optimistic concurrency leases.
5. Authoritative Host cognitive preemption (`PreemptiveInterruptGate`): invalidating stale action proposals when an unexpected physical shock/trap abruptly emerges at $t+1$ during in-flight LLM reasoning.
6. Long-horizon ($T=50$ ticks) composite capstone microworld with continuous thermodynamic entropy decay, deceptive traps, mid-trajectory shocks, and plan resumption.

The overall Track 1 evaluation verdict is **PASS**, satisfying 10 out of 10 clauses of the Gate B acceptance contract (`gate-b-contract.md`). The audit package is cryptographically archived as `audit_logs.zip` (SHA-256: `0b3f62d28523795a763bfe7f1bde377bb5bece5eec8048f7e57731eb4ae47f1e`).

## 2. Hypotheses Formulation

The experimental trial tests seven formal research hypotheses:

- **Hypothesis 1 ($H_1$ - Semantic Invariant Hardening):** Host Semantic Invariant Gate intercepts 100% of semantically invalid actions prior to physical execution, guaranteeing $M_{\text{sem}} \equiv 0$ in Arm 3.
- **Hypothesis 2 ($H_2$ - Abductive Cross-Partition Synthesis):** Backward causal DAG reachability identifies hidden inter-partition root causes, achieving abductive resolution $M_4 \ge 90.0\%$ in Stage 2, Stage 4, and Stage 6.
- **Hypothesis 3 ($H_3$ - Dual-Objective Decoupling):** Formal separation of $M_{\text{phys}}$ and $M_{\text{safe}}$ maintains physical resolution $M_1 \ge 85.0\%$ on solvable cases while achieving $M_2 \equiv 100.0\%$ rational abstention on deceptive traps.
- **Hypothesis 4 ($H_4$ - Virtual Jitter Lease Arbiter):** Dynamic non-blocking optimistic leases prevent write collisions under asymmetric cognitive delays, achieving $M_5 \equiv 0$.
- **Hypothesis 5 ($H_5$ - Context Token Ceiling):** 3-Tier Fact Card compaction maintains working prompt token consumption $T_{\text{max}} \le 512$ tokens across all stages.
- **Hypothesis 6 ($H_6$ - Action Groundedness):** Constrained affordance projection enforces $M_{10} \equiv 100.0\%$ action groundedness.
- **Hypothesis 7 ($H_7$ - Cognitive Preemption Resilience):** When an asynchronous shock triggers at $t+1$, the Host `PreemptiveInterruptGate` invalidates stale action proposals ($action\_epoch < world\_epoch$), dropping obsolete plans safely without physical breach ($M_{\text{preempt\_breach}} \equiv 0$).

## 3. Experimental Methodology

### 3.1 Experimental Arms

- **Arm 1 (Flat Monolithic Baseline):** Unguided raw state text without tier segregation, semantic precondition gating, or preemption protection.
- **Arm 2 (Phased Control):** Phased affordances without semantic invariant interception, cross-partition abductive tracing, or preemption gate.
- **Arm 3 (Host Cognitive Capstone Engine):** Complete architectural integration comprising 3-Tier Fact Cards, Semantic Invariant Gate, Abductive Causal Tracer, Virtual Jitter Arbiter, Preemptive Interrupt Gate, and Dual-Objective Evaluation.

### 3.2 Evaluation Scenario Distribution ($N = 120$)

| Stage | Focus Domain | Solvable | Trap | Description |
|---|---|---|---|---|
| Stage 1 | Semantic Byzantine Hardening | 10 | 10 | Precondition verification and feed activation traps |
| Stage 2 | Hidden Inter-Partition Causal Coupling | 10 | 10 | Abductive tracing across coupled zones |
| Stage 3 | Dual-Objective Solvable vs Deceptive | 10 | 10 | 5 Decoy traps + 5 Catastrophic breakdown traps |
| Stage 4 | Composite Capstone Microworld | 10 | 10 | Multi-hop abductive tracing + decoy traps |
| Stage 5 | Preemptive Cognitive Interrupt | 10 | 10 | Mid-trajectory shock at t+1 + phantom alarm decoys |
| Stage 6 | Long-Horizon Composite Capstone ($T=50$) | 10 | 10 | Passive entropy decay + pipe rupture shock + decoys |
| **Total** | **All 3 Domains** | **60** | **60** | **120 Scenarios x 3 Arms = 360 Episodes** |

## 4. Quantitative Results

### 4.1 Headline Metrics Summary

| Metric | Target Bound | Arm 1 (Flat) | Arm 2 (Phased) | Arm 3 (Capstone) | Margin / Delta | Verdict |
|---|---|---|---|---|---|---|
| $M_1$: Physical Resolution Rate | $\ge 85.0\%$ | $16.7\%$ | $25.0\%$ | $100.0\%$ | $+15.0\%$ vs Target | PASS |
| $M_2$: Safe Rational Abstention | $\equiv 100.0\%$ | $0.0\%$ | $0.0\%$ | $100.0\%$ | Met (60/60 Traps) | PASS |
| $M_3$: Semantic Invariant Breaches | $\equiv 0$ | $30$ | $30$ | $0$ | Zero Breaches | PASS |
| $M_4$: Abductive Causal Resolution | $\ge 90.0\%$ | $0.0\%$ | $0.0\%$ | $100.0\%$ | $+10.0\%$ vs Target | PASS |
| $M_5$: Concurrency Collisions | $\equiv 0$ | N/A | N/A | $0$ | Zero Collisions | PASS |
| $M_6$: Committed Physical Breaches | $\equiv 0$ | $60$ | $30$ | $0$ | Zero Breaches | PASS |
| $M_7$: Resolution Delta over Control | $\ge +30.0\%$ | $-8.3\%$ | Baseline | $+75.0\%$ | $+45.0\%$ vs Target | PASS |
| $M_8$: Max Prompt Tokens | $\le 512$ | $198$ | $156$ | $169$ | $-343$ tokens margin | PASS |
| $M_9$: Mean Turn Latency | $< 1000\text{ ms}$ | $118.5\text{ ms}$ | $119.2\text{ ms}$ | $120.34\text{ ms}$ | $-879.66\text{ ms}$ margin | PASS |
| $M_{10}$: Action Groundedness | $\equiv 100.0\%$ | $100.0\%$ | $100.0\%$ | $100.0\%$ | 100.0% Valid | PASS |

### 4.2 Statistical Distributions in Arm 3

- **Prompt Token Distribution:**
  - Mean: $124.01$ tokens
  - Median: $122.00$ tokens
  - P95: $158.00$ tokens
  - Max: $169.00$ tokens ($\le 512$ ceiling met with $67.0\%$ budget margin)
- **Turn Latency Distribution:**
  - Mean: $120.34\text{ ms}$
  - Median: $120.10\text{ ms}$
  - P95: $146.50\text{ ms}$
  - Max: $149.80\text{ ms}$ ($< 1000\text{ ms}$ ceiling met with $85.0\%$ margin)

## 5. Failure Taxonomy & Comparative Error Analysis

### 5.1 Arm 1 (Flat Monolithic Baseline)
- **Semantic Blindness:** In Stage 1, Arm 1 suffered repeated semantic breaches by attempting `ENGAGE secondary_feed` prior to repairing the compromised isolation seal.
- **Deceptive Decoy Susceptibility:** In Stages 3, 4, 5, and 6 traps, Arm 1 exhibited a 100% failure rate by blindly activating inert decoys (`ACTIVATE decoy_injector`, `ACTIVATE phantom_subsystem`, `ACTIVATE phantom_alarm`).
- **Mid-Trajectory Shock Blindness:** In Stage 5 and 6 solvable episodes, Arm 1 suffered unhandled shock breaches because it lacked the cognitive preemption mechanism, committing physical breaches upon sudden environmental changes.

### 5.2 Arm 2 (Phased Control)
- **Cross-Partition Blindness:** In Stages 2, 4, and 6, Arm 2 attempted localized symptom suppression without resolving the upstream hidden cause in `zone_alpha`.
- **Preemption Deficit:** Lacking `PreemptiveInterruptGate`, Arm 2 had no mechanism to drop stale proposals or execute emergency scram/isolation directives, failing all Stage 5 and Stage 6 shock episodes.

### 5.3 Arm 3 (Host Cognitive Capstone Engine)
- **Zero Committed Breaches:** 100% of semantic precondition checks and epoch stamps were verified before action dispatch.
- **Cognitive Preemption:** In Stage 5 and 6, when shocks emerged at $t+1$, in-flight stale proposals were intercepted and dropped without physical state mutation, while Tier 1/2 directives guided immediate emergency mitigation followed by plan resumption.
- **Long-Horizon Plan Resumption:** In Stage 6, after isolating the pipe rupture, Arm 3 resumed the multi-hop causal plan, stabilizing core temperature at 285K and preventing thermal runaway under continuous passive entropy decay.
- **Dual-Objective Integrity:** Arm 3 achieved $100.0\%$ resolution on solvable cases ($60/60$) and $100.0\%$ rational abstention on traps ($60/60$).

## 6. Threats to Validity

- **Internal Validity:** Simulated turn latencies use deterministic pseudorandom jitter parameterized from empirical `llama.cpp` distributions. Track 2 physical neural execution confirms actual HTTP roundtrip latency and real token sampling dynamics.
- **Construct Validity:** Scenarios use discrete state transitions with continuous entropy drift. Complex real-world continuous dynamics may require higher-order causal modeling.
- **External Validity:** The synthetic microworld covers three representative physical domains across 6 stages; scaling to higher-dimensional domains will be verified in post-MN-026.

## 7. Compliance Assessment against Gate B Contract

| Clause | Description | Frozen Bound | Track 1 Observed | Compliance |
|---|---|---|---|---|
| Clause M1 | Physical Task Resolution Rate | $\ge 85.0\%$ | $100.0\%$ ($60/60$) | PASS |
| Clause M2 | Decision Safety / Rational Abstention | $\equiv 100.0\%$ | $100.0\%$ ($60/60$) | PASS |
| Clause M3 | Semantic Invariant Breaches | $\equiv 0$ | $0$ | PASS |
| Clause M4 | Abductive Causal Resolution Efficacy | $\ge 90.0\%$ | $100.0\%$ ($30/30$) | PASS |
| Clause M5 | Concurrency Collisions Under Jitter | $\equiv 0$ | $0$ | PASS |
| Clause M6 | Committed Physical Breaches | $\equiv 0$ | $0$ | PASS |
| Clause M7 | Resolution Delta Over Control | $\ge +30.0\%$ | $+75.0\%$ | PASS |
| Clause M8 | Max Working Prompt Tokens | $\le 512$ | $169$ | PASS |
| Clause M9 | Mean Turn Inference Latency | $< 1000\text{ ms}$ | $120.34\text{ ms}$ | PASS |
| Clause M10 | Action Groundedness Fidelity | $\equiv 100.0\%$ | $100.0\%$ | PASS |

**Overall Gate B Track 1 Verdict: PASS (10/10 Clauses Satisfied)**
