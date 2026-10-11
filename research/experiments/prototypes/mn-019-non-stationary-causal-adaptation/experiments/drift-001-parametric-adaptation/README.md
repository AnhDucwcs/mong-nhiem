# Stage 1: Continuous Parametric Drift Adaptation (`drift-001-parametric-adaptation`)

## 1. Overview and Operational Scope

Stage 1 evaluates the Dual-Engine Host's ability to maintain physical conservation law compliance and high task completion rates ($\ge 85.0\%$) when the underlying microworld transition parameters undergo continuous non-stationary drift.

To isolate parametric adaptation without confounding memory representation variables, Stage 1 maintains the verified, compact Fact Card schema from MN-018 (`[entity_id v{version} {key}:{val}]`). Dynamic schema evolution is strictly quarantined to Stage 2 (`drift-002-schema-evolution`).

---

## 2. Architectural Components

1. **Parametric Drift Microworld Engine (`src/microworld_engine.py`):**
   - Implements multi-rate simulation clocks and continuous drift dynamics: linear decay $\eta(t) = \eta_0 \cdot (1 - \lambda t)$, exponential decay $e^{-\lambda t}$, sudden step shocks, harmonic oscillations, and coupled cross-channel degradation.
   - Calculates two state updates per turn: nominal expected transition $\hat{s}_{t+1}$ and true actual transition $s_{t+1}$.
2. **Host Discrepancy Monitor (`src/discrepancy_monitor.py`):**
   - Computes real-time discrepancy vectors $D_t = |s_{t+1}^{\text{actual}} - s_{t+1}^{\text{nominal}}|$.
   - Flags parametric drift alerts when error exceeds calibrated channel thresholds ($\epsilon$).
   - Injects bounded, high-density drift alerts into context: `[DRIFT_ALERT: solar_panel eff:0.60 nominal:1.00]`.
3. **Dynamic Affordance DAG Regeneration (`src/dynamic_affordance.py`):**
   - Dynamically recompiles GBNF action grammars:
     - Prunes actions whose nominal execution would trigger physical conservation breaches under degraded parameters.
     - Injects compensatory affordances (e.g. auxiliary diversion, flow throttling).
4. **Conservation Guard & Transactional Memento Stack (`src/memento_stack.py`):**
   - Intercepts invariant violations before state commitment and performs atomic rollback.
5. **AutoDream Memory Consolidation (`src/autodream_engine.py`):**
   - Compresses episodic events into high-density Fact Cards, preserving $\ge 70.0\%$ compaction.

---

## 3. Evaluation Corpus Architecture ($N=60$)

The evaluation benchmark comprises 60 standardized scenarios spanning 4 heterogeneous domains ($N=15$ per domain):
- **Domain A (Orbital Life Support, $N=15$):** Deep-space cryogenic thermal control, cabin oxygen pressure, solar array dust decay.
- **Domain B (Smart Microgrid, $N=15$):** High-penetration renewable grid, battery impedance escalation, fluctuating wind shear.
- **Domain C (Cold-Chain Logistics Fleet, $N=15$):** Mobile electric transport, motor friction degradation, reefer thermal insulation puncture.
- **Domain D (Subsea Hydrothermal Node, $N=15$):** Deep marine hydrostatic equilibrium, thermoelectric fouling, salinity sensor drift.

Stratified by difficulty:
- **In-Distribution (ID, Cases 1–30):** Linear decay and isolated step shocks.
- **Out-of-Distribution (OOD, Cases 31–60):** Coupled exponential decay, harmonic oscillations, and cascading multi-shock clusters across ticks 20, 50, 90, 140, 180.
