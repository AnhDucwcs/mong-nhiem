# Track 1 Empirical Evaluation Report: Milestone MN-026 Host Simulator Benchmark

## 1. Executive Summary

This report documents the empirical evaluation of Milestone MN-026 (Phase 1 Pre-MN-026) under Track 1 (Host Simulator). The experimental framework subjects the cognitive capstone governance architecture to $N = 80$ standardized scenarios across three physical domains (Nuclear Fission Cooling, Orbital Life Support, Smart Microgrid) across three experimental arms ($240$ total episodes).

The primary objective of MN-026 is resolving the systemic vulnerabilities identified across predecessors MN-022 through MN-025:
1. Hardening semantic invariants beyond GBNF syntax to prevent physically catastrophic actions (remediating MN-022).
2. Cross-partition abductive causal tracing to synthesize mitigations for unobserved inter-partition side effects (remediating MN-023).
3. Formalizing a decoupled dual-objective contract ($M_{\text{phys}}$ physical resolution vs $M_{\text{safe}}$ rational abstention) without penalizing defensive non-action (remediating MN-025).
4. Enforcing virtual asymmetric latency jitter ($100\text{ ms} \leftrightarrow 800\text{ ms}$) within a single SLM instance under optimistic concurrency leases.

The overall Track 1 evaluation verdict is **PASS**, satisfying 10 out of 10 clauses of the Gate B acceptance contract (`gate-b-contract.md`). The audit package is cryptographically archived as `audit_logs.zip` (SHA-256: `28bb10cbb2dcbf5e935d864ddc07a9471f59f925fd6e789734cc10cacab845ec`).

## 2. Hypotheses Formulation

The experimental trial tests six formal research hypotheses:

- **Hypothesis 1 ($H_1$ - Semantic Invariant Hardening):** Host Semantic Invariant Gate intercepts 100% of semantically invalid actions prior to physical execution, guaranteeing $M_{\text{sem}} \equiv 0$ in Arm 3.
- **Hypothesis 2 ($H_2$ - Abductive Cross-Partition Synthesis):** Backward causal DAG reachability identifies hidden inter-partition root causes, achieving abductive resolution $M_4 \ge 90.0\%$ in Stage 2 and Stage 4.
- **Hypothesis 3 ($H_3$ - Dual-Objective Decoupling):** Formal separation of $M_{\text{phys}}$ and $M_{\text{safe}}$ maintains physical resolution $M_1 \ge 85.0\%$ on solvable cases while achieving $M_2 \equiv 100.0\%$ rational abstention on deceptive traps.
- **Hypothesis 4 ($H_4$ - Virtual Jitter Lease Arbiter):** Dynamic non-blocking optimistic leases prevent write collisions under asymmetric cognitive delays, achieving $M_5 \equiv 0$.
- **Hypothesis 5 ($H_5$ - Context Token Ceiling):** 3-Tier Fact Card compaction maintains working prompt token consumption $T_{\text{max}} \le 512$ tokens across all stages.
- **Hypothesis 6 ($H_6$ - Action Groundedness):** Constrained affordance projection enforces $M_{10} \equiv 100.0\%$ action groundedness.

## 3. Experimental Methodology

### 3.1 Experimental Arms

- **Arm 1 (Flat Monolithic Baseline):** Unguided raw state text without tier segregation or semantic precondition gating.
- **Arm 2 (Phased Control):** Phased affordances without semantic invariant interception or cross-partition abductive tracing.
- **Arm 3 (Host Cognitive Capstone Engine):** Complete architectural integration comprising 3-Tier Fact Cards, Semantic Invariant Gate, Abductive Causal Tracer, Virtual Jitter Arbiter, and Dual-Objective Evaluation.

### 3.2 Evaluation Scenario Distribution ($N = 80$)

| Stage | Focus Domain | Solvable | Trap | Description |
|---|---|---|---|---|
| Stage 1 | Semantic Byzantine Hardening | 20 | 0 | Precondition verification and feed activation |
| Stage 2 | Hidden Inter-Partition Causal Coupling | 20 | 0 | Abductive tracing across coupled zones |
| Stage 3 | Dual-Objective Solvable vs Deceptive | 10 | 10 | 5 Decoy traps + 5 Catastrophic breakdown traps |
| Stage 4 | Composite Capstone Microworld | 10 | 10 | Multi-hop abductive tracing + decoy traps |
| **Total** | **All 3 Domains** | **60** | **20** | **80 Scenarios x 3 Arms = 240 Episodes** |

## 4. Quantitative Results

### 4.1 Headline Metrics Summary

| Metric | Target Bound | Arm 1 (Flat) | Arm 2 (Phased) | Arm 3 (Capstone) | Margin / Delta | Verdict |
|---|---|---|---|---|---|---|
| $M_1$: Physical Resolution Rate | $\ge 85.0\%$ | $16.7\%$ | $33.3\%$ | $100.0\%$ | $+15.0\%$ vs Target | PASS |
| $M_2$: Safe Rational Abstention | $\equiv 100.0\%$ | $0.0\%$ | $0.0\%$ | $100.0\%$ | Met (20/20 Traps) | PASS |
| $M_3$: Semantic Invariant Breaches | $\equiv 0$ | $20$ | $20$ | $0$ | Zero Breaches | PASS |
| $M_4$: Abductive Causal Resolution | $\ge 90.0\%$ | $0.0\%$ | $0.0\%$ | $100.0\%$ | $+10.0\%$ vs Target | PASS |
| $M_5$: Concurrency Collisions | $\equiv 0$ | N/A | N/A | $0$ | Zero Collisions | PASS |
| $M_6$: Committed Physical Breaches | $\equiv 0$ | $40$ | $20$ | $0$ | Zero Breaches | PASS |
| $M_7$: Resolution Delta over Control | $\ge +30.0\%$ | $-16.6\%$ | Baseline | $+66.7\%$ | $+36.7\%$ vs Target | PASS |
| $M_8$: Max Prompt Tokens | $\le 512$ | $185$ | $142$ | $134$ | $-378$ tokens margin | PASS |
| $M_9$: Mean Turn Latency | $< 1000\text{ ms}$ | $118.2\text{ ms}$ | $119.4\text{ ms}$ | $121.3\text{ ms}$ | $-878.7\text{ ms}$ margin | PASS |
| $M_{10}$: Action Groundedness | $\equiv 100.0\%$ | $100.0\%$ | $100.0\%$ | $100.0\%$ | 100.0% Valid | PASS |

### 4.2 Statistical Distributions in Arm 3

- **Prompt Token Distribution:**
  - Mean: $114.80$ tokens
  - Median: $112.00$ tokens
  - P95: $132.00$ tokens
  - Max: $134.00$ tokens ($\le 512$ ceiling met with $73.8\%$ budget margin)
- **Turn Latency Distribution:**
  - Mean: $121.32\text{ ms}$
  - Median: $120.50\text{ ms}$
  - P95: $146.20\text{ ms}$
  - Max: $149.80\text{ ms}$ ($< 1000\text{ ms}$ ceiling met with $85.0\%$ margin)

## 5. Failure Taxonomy & Comparative Error Analysis

### 5.1 Arm 1 (Flat Monolithic Baseline)
- **Semantic Blindness:** In Stage 1, Arm 1 suffered 20 semantic breaches by attempting `ENGAGE secondary_feed` prior to repairing the compromised isolation seal.
- **Deceptive Decoy Susceptibility:** In Stage 3 and 4 traps, Arm 1 exhibited a 100% failure rate by blindly activating inert decoys (`ACTIVATE decoy_injector`, `ACTIVATE phantom_subsystem`) or forcing unrecoverable hardware.
- **Physical Breach Commitments:** Total committed physical breaches reached 40 across the 80 episodes.

### 5.2 Arm 2 (Phased Control)
- **Cross-Partition Blindness:** In Stage 2, Arm 2 attempted localized symptom suppression (`VENT local_steam`) without resolving the upstream hidden cause in `zone_alpha`, resulting in negative transfer and physical degradation.
- **Abstention Deficit:** Lacking typed affordance negative masking, Arm 2 attempted to force damaged manifolds, failing 100% of trap episodes.

### 5.3 Arm 3 (Host Cognitive Capstone Engine)
- **Zero Committed Breaches:** 100% of semantic precondition checks were verified before action dispatch.
- **Abductive Synthesis:** Anomaly reports immediately triggered backward DAG reachability, producing actionable Tier 2 hints (`[ABDUCTIVE_HINT: DIVERT coolant_flow in zone_alpha -> EXECUTE RESTORE coolant_valve]`), resolving 30/30 abductive scenarios cleanly.
- **Dual-Objective Integrity:** Arm 3 distinguished solvable crises from unrecoverable traps, achieving $100.0\%$ resolution on solvable cases and $100.0\%$ rational abstention on traps.

## 6. Threats to Validity

- **Internal Validity:** Simulated turn latencies use deterministic pseudorandom jitter parameterized from empirical `llama.cpp` distributions. Track 2 physical neural execution is required to validate actual HTTP roundtrip latency and real token sampling dynamics.
- **Construct Validity:** Scenarios use discrete state transitions. Complex real-world continuous dynamics may require higher-order causal modeling.
- **External Validity:** The synthetic microworld covers three representative physical domains; scaling to higher-dimensional domains will be verified in post-MN-026.

## 7. Compliance Assessment against Gate B Contract

| Clause | Description | Frozen Bound | Track 1 Observed | Compliance |
|---|---|---|---|---|
| Clause M1 | Physical Task Resolution Rate | $\ge 85.0\%$ | $100.0\%$ ($60/60$) | PASS |
| Clause M2 | Decision Safety / Rational Abstention | $\equiv 100.0\%$ | $100.0\%$ ($20/20$) | PASS |
| Clause M3 | Semantic Invariant Breaches | $\equiv 0$ | $0$ | PASS |
| Clause M4 | Abductive Causal Resolution Efficacy | $\ge 90.0\%$ | $100.0\%$ ($30/30$) | PASS |
| Clause M5 | Concurrency Collisions Under Jitter | $\equiv 0$ | $0$ | PASS |
| Clause M6 | Committed Physical Breaches | $\equiv 0$ | $0$ | PASS |
| Clause M7 | Resolution Delta Over Control | $\ge +30.0\%$ | $+66.7\%$ | PASS |
| Clause M8 | Max Working Prompt Tokens | $\le 512$ | $134$ | PASS |
| Clause M9 | Mean Turn Inference Latency | $< 1000\text{ ms}$ | $121.32\text{ ms}$ | PASS |
| Clause M10 | Action Groundedness Fidelity | $\equiv 100.0\%$ | $100.0\%$ | PASS |

**Overall Gate B Track 1 Verdict: PASS (10/10 Clauses Satisfied)**
