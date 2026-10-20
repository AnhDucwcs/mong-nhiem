# Milestone Charter: MN-027 — Bimodal Cognitive Emission, Declarative Schema Synthesis & Real-Time Human Supervisory Control

## 1. Executive Summary & Research Motivation

Mộng Nhiễm is an open-source empirical research and operating platform engineered to endow Small Language Models (SLMs, $< 4\text{B}$) with robust, stateful, and causally sound operational capabilities over complex, non-stationary information spaces. In accordance with Mộng Nhiễm's foundational architectural principles:
1. **Raison d'Être Invariant:** The LLM is maintained strictly as an unchanged, black-box stochastic reasoning engine emitting structured actions; the Host maintains absolute authority over physical state integrity, access control, and provenance auditing.
2. **Minimalism & Resource Bounds:** Systems must operate reliably within strict local hardware constraints ($\le 4\text{GB}$ VRAM, prompt working memory $\le 512\text{ tokens}$, turn latency $< 1000\text{ ms}$).
3. **Controlled Experimental Testbed:** Microworlds serve as mathematically formal laboratory environments to isolate, stress-test, and falsify specific cognitive architecture hypotheses ($H_1, H_2, \dots$) prior to open-corpus expansion.

Previous research milestones verified isolated cognitive mechanisms:
- **MN-022 to MN-025:** Swarm consensus, asymmetric epistemic masking, multi-hop causal maintenance under continuous entropy decay, and cross-domain knowledge transfer.
- **MN-026:** Multi-stage cognitive capstone governance, semantic invariant hardening, abductive cross-partition causal synthesis, cognitive preemption, and dual-mode telemetry blackout autonomy (`AUTONOMOUS_IMPROVISE` vs `SUPERVISED_STANDBY`).

### The Human-Centric Cognitive Frontier
While MN-001 through MN-026 successfully established autonomous machine-to-machine closed loops, real-world deployment (personal desktop task assistants, interactive digital companions, industrial supervisory control, and game NPCs) introduces three fundamental architectural gaps:
1. **Machine-Only Action Bottleneck:** In prior milestones, SLMs emitted strictly operational actions (`ACTION: <verb> <target> [params]`). In human-in-the-loop applications, human operators receive raw machine tokens without communicative explanations, rationale, or persona engagement.
2. **Hardcoded Python Schema Bottleneck:** In prior milestones, every invariant, affordance, and entity required manual Python class instantiation (`SemanticPrecondition`, `RedlineRule`). Deploying Mộng Nhiễm as a domain-agnostic engine requires a generic declarative schema loader (YAML/JSON) to instantiate Host rules dynamically without modifying host code.
3. **Open-Loop Human Supervisory Intervention:** While MN-026 introduced `SUPERVISED_STANDBY` when sensors fail, the system lacked a structured communicative channel to explain *why* it halted and an inbound interface to receive corrective human preemption commands (`HUMAN_INTERRUPT`).
4. **Simulated vs Wall-Clock Disconnect:** In prior milestones, time advanced purely via synthetic discrete ticks ($t = 1, 2, 3$). Real-world applications require a Dual-Clock architecture bridging physical wall-clock time (`datetime`, monotonic timers, OS idle events) with discrete causal ticks, accompanied by continuous parameter decay and session persistence across restarts.

Milestone **MN-027** resolves these gaps by developing, evaluating, and standardizing the **Bimodal Cognitive Architecture** for small language models.

---

## 2. Five Core Architectural Pillars

1. **Bimodal Cognitive Emission Protocol:** Single-pass constrained generation emitting both an operational action for the Host and a communicative act for the human operator under a single GBNF grammar.
2. **Orthogonal Triadic Communicative Taxonomy:** Standardizing communicative acts into three mutually exclusive, collectively exhaustive classes based on Host state effect:
   - `INFORM`: Unidirectional informative broadcast or causal explanation. Host continues nominal execution ($T = 0.1$).
   - `QUERY`: Bidirectional solicitation. Host enters `SUPERVISED_STANDBY` and pauses execution loop awaiting human input ($T = 0.1$).
   - `EXPRESS`: Unconstrained socio-emotional persona expression or banter ($T = 0.5$). Host preserves operational state invariance.
3. **Dual-Clock Temporal Bridge (`TemporalBridge`):** Synchronizing real-world monotonic wall-clock intervals with Host causal ticks, supporting discrete benchmark stepping and live background scheduling.
4. **Continuous State Decay & Persistence (`ContinuousStateEngine`):** Mathematical parameter decay ($X(t) = X_0 \pm \lambda \cdot \Delta t$) triggering threshold invariants, paired with atomic JSON session state serialization.
5. **Declarative Schema Synthesis (`DeclarativeSchemaLoader`):** Pure standard-library YAML/JSON parsing compiling user-defined entities, invariants, and preconditions into active Host memory structures without code modification.

---

## 3. Research Questions & Formal Hypotheses

### Primary Research Questions
- **RQ1 (Bimodal Parse Determinism):** Can a unified GBNF grammar constrain a small open-weights model ($<4\text{B}$) to emit valid operational actions and communicative acts simultaneously with zero syntax parse failures?
- **RQ2 (Triadic Communicative Precision):** Under Dual-Layer Steering (Host prompt scaffolding + dynamic GBNF phase gating), does the SLM achieve $100.0\%$ classification accuracy across `INFORM`, `QUERY`, and `EXPRESS`?
- **RQ3 (Bimodal Token Efficiency):** Does a unified bimodal forward pass achieve $\ge 35.0\%$ token savings compared to an uncoordinated two-call sequential baseline (Call 1: Action, Call 2: Chat)?
- **RQ4 (Human Supervisory Preemption Fidelity):** When entering `SUPERVISED_STANDBY`, can the Host reliably parse a human operator's natural language command, advance the world epoch, and safely resume operations with $100.0\%$ recovery?
- **RQ5 (Real-Time Temporal Synchronization & Decay Precision):** Does the Dual-Clock bridge maintain real-time tick synchronization with $\le 15.0\text{ ms}$ jitter while executing continuous state decay without numerical drift?

### Formal Mathematical Hypotheses

- **$H_1$ (Bimodal Parse & Format Determinism):**
  Across all evaluated turns in the benchmark corpus ($N=60$), Arm 3 achieves perfect syntax determinism:
  $$P_{\text{bimodal}}(\text{Arm 3}) = \frac{N_{\text{valid\_syntax}}}{N_{\text{total\_turns}}} \equiv 100.0\% \quad (\text{Falsified if } P_{\text{bimodal}} < 100.0\%)$$

- **$H_2$ (Triadic Communicative Act Classification Accuracy):**
  Across all communicative utterances, Arm 3 achieves absolute classification accuracy without semantic mislabeling:
  $$M_3(\text{Arm 3}) = \frac{N_{\text{correct\_class}}}{N_{\text{total\_comm}}} \equiv 100.0\% \quad (\text{Falsified if } M_3 < 100.0\%)$$

- **$H_3$ (Token Efficiency Delta over Two-Call Control):**
  Compared to the decoupled two-call baseline (Arm 2), the integrated bimodal pass (Arm 3) reduces total token consumption by at least $35.0\%$:
  $$\Delta_{\text{tokens}} = \frac{\text{Tokens}_{\text{Arm 2}} - \text{Tokens}_{\text{Arm 3}}}{\text{Tokens}_{\text{Arm 2}}} \ge 35.0\% \quad (\text{Falsified if } \Delta_{\text{tokens}} < 35.0\%)$$

- **$H_4$ (Human Supervisory Preemption Recovery Efficacy):**
  In all scenarios entering `SUPERVISED_STANDBY` upon sensor loss or critical contention, human supervisory injection restores nominal operation with 100% success:
  $$R_{\text{human}}(\text{Arm 3}) = \frac{N_{\text{recovered}}}{N_{\text{standby}}} \equiv 100.0\% \quad (\text{Falsified if } R_{\text{human}} < 100.0\%)$$

- **$H_5$ (Temporal Synchronization & Drift Bound):**
  Under live wall-clock execution, real-time tick scheduling jitter satisfies:
  $$\Delta \tau_{\text{drift}} = |\tau_{\text{actual}} - \tau_{\text{target}}| \le 15.0\text{ ms} \quad (\text{Falsified if } \Delta \tau_{\text{drift}} > 15.0\text{ ms})$$

- **$H_6$ (Cognitive Token Budget & Sub-Second Latency SLA):**
  Working prompt memory stays bounded at or below 512 tokens with sub-second turn latency:
  $$\max \text{Tokens}_t(\text{Arm 3}) \le 512\text{ tokens}, \quad \bar{T}_{\text{turn}}(\text{Arm 3}) < 1000\text{ ms} \quad (\text{Target } < 500\text{ ms})$$

---

## 4. Experimental Methodology & Comparative Arms

### Three Matched Experimental Arms

1. **Arm 1 (Flat Unconstrained Baseline):**
   - Raw unconstrained prompt without bimodal GBNF grammar, declarative schema loading, or preemption management.
   - Generates freeform text requiring heuristic regex parsing.
2. **Arm 2 (Decoupled Two-Call Control):**
   - Sequential two-call pipeline:
     - Call 1: Action generation via standard action GBNF.
     - Call 2: Communicative response generation conditioned on Call 1 output.
   - Measures token bloat, latency multiplication, and KV cache pressure under decoupled execution.
3. **Arm 3 (Integrated Bimodal Cognitive Host):**
   - Unified single-pass bimodal emission governed by `BimodalProtocol` GBNF.
   - Generic schema synthesis (`schema.yaml`).
   - Real-world dual-clock timing (`TemporalBridge`).
   - Human supervisory preemption bridge (`HumanSupervisoryBridge`).

### Evaluation Corpus ($N = 60$ Scenarios across 3 Domains)

- **Domain A: Cyber-Physical & SCADA Supervision ($N = 20$):**
  - Mission: Telemetry monitoring, sensor blackout detection, and valve isolation.
  - Primary Communicative Modes: `INFORM` (telemetry reports), `QUERY` (standby human confirmation).
- **Domain B: Personal Desktop Task Assistant ($N = 20$):**
  - Mission: Task deadline tracking, resource conflict resolution, and human command override.
  - Primary Communicative Modes: `QUERY` (schedule collision), `INFORM` (task completion), `HUMAN_INTERRUPT` (preemption).
- **Domain C: Stateful Interactive Companion / Pet ($N = 20$):**
  - Mission: Energy/hunger decay tracking, activity pacing, and social bonding.
  - Primary Communicative Modes: `EXPRESS` ($T=0.5$ humor/banter), `INFORM` (status reports), threshold invariant triggers.

### Dual-Track Execution Protocol

- **Track 1 (Host Simulator):**
  - $N=60 \times 3\text{ arms} = 180\text{ episodes}$ executed on deterministic mock backend to verify mathematical invariants, state transitions, and preemption safety.
- **Track 2 (Real Model Neural Inference):**
  - $N=60 \times 3\text{ arms} = 180\text{ episodes}$ executed on local `llama-server.exe` (port 18502) using primary research subject `Qwen3.5-2B-Q4_K_M.gguf` under strict hardware limits ($\le 4\text{GB}$ VRAM, ChatML formatting, greedy decoding $T=0.0$ for logic / $T=0.5$ for express).
- Total Execution Volume: $360\text{ episodes}$.
