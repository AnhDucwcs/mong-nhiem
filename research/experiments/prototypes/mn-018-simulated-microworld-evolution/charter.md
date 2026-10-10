# Experiment Charter: Milestone MN-018
## Stateful Simulated Microworld Evolution (Full Cognitive Host Synthesis)

### 1. Context and Motivation

Project Mộng Nhiễm has progressively validated modular cognitive host substrates across milestones MN-009 through MN-017:
- MN-009 / MN-010: Context scaffolding and working set iteration.
- MN-011: Context frontier saturation ($B^* \approx 512$ tokens).
- MN-012: Dual-tier working memory partitions and declarative Fact Cards.
- MN-013: Host-authoritative Memento rollback and negative action steering.
- MN-014 / MN-015: Dynamic GBNF grammar compilation and affordance pruning.
- MN-016: Episodic event logging and autonomous AutoDream consolidation.
- MN-017: Multi-rate world ticks, hierarchical mission DAGs, and optimistic concurrency guards.

However, each substrate was evaluated under bounded, modular conditions ($T \le 25$ steps). Prior to MN-018, no empirical evaluation demonstrated whether a lightweight open-weights language model ($<4\text{B}$ parameters) can sustain long-horizon governance ($T \ge 50 - 100$ steps) over complex simulated microworlds under concurrent background environmental dynamics and physical conservation laws without human intervention or catastrophic state divergence.

### 2. Core Research Question

Can an un-fine-tuned, lightweight open-weights language model ($<4\text{B}$ parameters, specifically `Qwen3.5-2B-Q4_K_M`), coupled with the full Mộng Nhiễm Dual-Engine Cognitive Host, sustain, evolve, and reliably govern multi-entity simulated microworlds across extended discrete time horizons ($T \ge 50 - 100$ steps) under continuous background environmental concurrency, strict physical conservation laws, and local workstation latency constraints ($< 1000\text{ ms}$)?

### 3. Falsifiable Hypotheses

- **Hypothesis 1 (Long-Horizon Viability & Policy Efficacy, $H_1$):**
  $$\text{Accuracy}(\text{Arm 3}) \ge 90.0\% \quad (27/30 \text{ cases}) \quad \text{and} \quad \Delta \text{Accuracy} = \text{Accuracy}(\text{Arm 3}) - \text{Accuracy}(\text{Arm 1}) \ge +50.0\%$$
  Over extended horizons ($T = 50 - 100$ steps), Arm 3 (Full Cognitive Host Stack) reliably completes multi-entity missions, whereas Arm 1 (Flat Baseline) suffers catastrophic context overflow or state drift ($\le 10.0\%$).

- **Hypothesis 2 (Conservation Law Invariant Preservation, $H_2$):**
  $$\text{ConservationBreaches}(\text{Arm 3}) = 0.0\% \quad \text{and} \quad \text{StaleMutationRate}(\text{Arm 3}) = 0.0\%$$
  The Host Conservation Guard intercepts and prevents 100.0% of illegal state transitions that violate mass, energy, or resource bounds. Zero unmanaged stale-state overwrites are committed to the world store.

- **Hypothesis 3 (Autonomous AutoDream Episodic Memory Consolidation, $H_3$):**
  $$\text{HistoryCompressionRatio} \ge 70.0\% \quad \text{and} \quad \text{MemoryContradictions} = 0$$
  The host consolidates episodic event streams upon reaching trigger thresholds ($M \ge 15$ events or working context $\ge 400$ tokens), compressing raw logs into high-density fact cards ($\le 48$ tokens) without factual contradictions.

- **Hypothesis 4 (Bounded Inference Budget & Interactive Latency SLA, $H_4$):**
  $$\max_t(\text{PromptTokens}_t) \le 512 \quad \text{and} \quad \mathbb{E}[\text{PromptTokens}] \le 384$$
  $$\mathbb{E}[\text{TurnLatency}] < 1000\text{ ms} \quad \text{and} \quad \max(\text{HostOverhead}) < 10.0\text{ ms}$$
  100.0% of forward passes operate within the strict $\le 512$ token ceiling across all turns. Turn latencies remain sub-second on consumer-grade local GPU hardware.

### 4. Experimental Scope and Domain Topologies

The benchmark evaluates 30 heterogeneous long-horizon scenarios across three continuous microworld domains:
1. **Domain A: Autonomous Orbital Station Life Support** (10 cases):
   - Coupled subsystems: Solar Power Bus, Battery Storage, O2 Generation, CO2 Scrubbing, Coolant Thermal Loops.
   - Environmental dynamics: Orbital eclipses, solar flare radiation drift, metabolic oxygen consumption, mechanical valve leakage.
   - Conservation laws: Total Energy $\ge 0$, Oxygen ratio $O_2 \in [19.5, 23.5]\%$, Cabin Pressure $\ge 95\text{ kPa}$, Coolant volume conserved.
2. **Domain B: Smart Industrial Microgrid & Storage** (10 cases):
   - Coupled subsystems: Solar PV Array, Natural Gas Turbines, Battery Energy Storage System (BESS), Factory Industrial Load, Critical Hospital Ward.
   - Environmental dynamics: Solar cloud intermittency, sudden factory shift peak demand spikes, transformer thermal derating.
   - Conservation laws: Generation = Load + Storage Charging ($\Delta E = 0$), Critical Hospital Load uncurtailed ($P_{\text{hosp}} \ge P_{\text{req}}$), Battery SOC $\in [0, 100]\%$.
3. **Domain C: Multi-Hub Autonomous Fleet Supply Chain** (10 cases):
   - Coupled subsystems: Logistics Hubs ($N=3$), Autonomous Transport Drones ($N=6$), Priority Medical Payloads, Automated Recharging Docks.
   - Environmental dynamics: Weather headwinds, transit corridor blockages, dynamic delivery order arrivals.
   - Conservation laws: Total Inventory Conserved (Zero lost or duplicated payloads), Payload Mass $\le \text{MaxCapacity}$, Battery Charge $\ge 0\%$ at all times.

Three cases (Case 10, Case 20, Case 30) serve as extreme duration stress tests running for $T = 100$ discrete turns.

### 5. Research Protocol & Governance

In compliance with Mộng Nhiễm governance:
- All prototype implementation code remains strictly quarantined within `research/experiments/prototypes/mn-018-simulated-microworld-evolution/`.
- No modifications are made to `src/mong_nhiem/` during prototype evaluation.
- Pre-run and post-run cryptographic manifests guarantee reproducibility and prevent post-hoc tuning.
