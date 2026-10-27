# Mộng Nhiễm Living World: World Design, Scenario & Epistemic Specification

## 1. System Philosophy & Raison d'Être Invariant
The simulation enforces absolute separation between the Reasoning Engine (SLM) and the Physical Ground Truth (Host):
1. **Host World Engine (Ground Truth Authority):** Fully authoritative over physics, differential vitals, spatial collisions, sensory transmission, and state persistence.
2. **Small Language Model (Bounded Cognition):** Operates under partial observation (fog-of-war, wind advection, stale memory), emitting structured intent tokens bounded to $\le 512$ tokens and $< 1000\text{ ms}$ latency.
3. **Mộng Nhiễm Kernel (Cognitive Governance):** Audits, validates, and gates all SLM intents against physical invariants (`ReflexBreaker`, trajectory lookahead $\Delta t \ge 4$) before state commitment.

---

## 2. World Ontology & Entity Hierarchy

### 2.1 Macro Colony Aggregate ($\mathcal{S}_{\text{colony}}$)
- **Population:** $N = 24$ individuals (1 Alpha Scout, 7 Foragers, 16 Flock members).
- **Aggregate Indicators:**
  - $H_{\text{agg}} = \frac{1}{N} \sum_{i=1}^N H_i$ (Colony hunger index)
  - $\Theta_{\text{colony}} \in \{\text{NOMINAL}, \text{ELEVATED}, \text{CRITICAL}\}$ (Threat level)
  - $S_{\text{burrow}} \in [0, 200]\text{ u}$ (Shared food reserves inside burrow)
  - $C_{\text{burrow}} = 16$ (Maximum concurrent underground shelter capacity)

### 2.2 Micro Biological Entities ($\mathbf{s}_i$)
Each individual entity maintains physiological and cognitive state:
$$\mathbf{s}_i = \langle x_i, y_i, v_{x,i}, v_{y,i}, E_i, H_i, T_i, \Omega_i, \kappa_i, \mathcal{M}_i \rangle$$
Where:
- $(x_i, y_i) \in \mathbb{R}^2$: Spatial coordinate.
- $(v_{x,i}, v_{y,i}) \in \mathbb{R}^2$: Velocity vector ($\|v_i\| \le v_{\max}$).
- $E_i \in [0, 100]$: Energy / Stamina.
- $H_i \in [0, 100]$: Hunger (0 = satiated, 100 = starving).
- $T_i \in [0, 100]$: Thirst (0 = hydrated, 100 = dehydrated).
- $\Omega_i \in [0, 100]$: Vitality / Health.
- $\kappa_i \in \{0, 1\}$: Stealth / Cover flag (1 when inside thicket canopy).
- $\mathcal{M}_i$: AutoDream episodic FactCard working memory ($\le 512$ tokens).

### 2.3 Environmental Substrate & Static Biome
- **Central Freshwater Lake:** $\mathbf{p}_{\text{lake}} = [520, 360]$, radius $R_{\text{lake}} = 105\text{ px}$, capacity $300\text{ u}$.
- **Burrow Sanctuary:** $\mathbf{p}_{\text{burrow}} = [320, 520]$, outer radius $32\text{ px}$, entrance radius $11\text{ px}$.
- **Food Resources (4 Berry Bushes):**
  - $\text{Bush}_{\text{North}} = [520, 140]$, capacity $100\text{ u}$.
  - $\text{Bush}_{\text{East}} = [770, 370]$, capacity $100\text{ u}$.
  - $\text{Bush}_{\text{West}} = [260, 230]$, capacity $100\text{ u}$.
  - $\text{Bush}_{\text{South}} = [390, 560]$, capacity $100\text{ u}$.
- **Granite Rock Formations (7 Heterogeneous Obstacles with Varied Profiles):**
  - NW $[275, 130]$ ($65 \times 36\text{ px}$, Massive Mountain Ridge, $\theta=0.38\text{ rad}$)
  - NE $[740, 140]$ ($50 \times 19\text{ px}$, Elongated Jagged Spine, $\theta=-0.32\text{ rad}$)
  - West $[130, 360]$ ($36 \times 34\text{ px}$, Rounded Monolith, $\theta=0.10\text{ rad}$)
  - SE Main $[750, 590]$ ($54 \times 26\text{ px}$, Continental Rock Barrier, $\theta=0.18\text{ rad}$)
  - SE Outcrop $[815, 450]$ ($32 \times 19\text{ px}$, Sharp Angular Outcrop, $\theta=0.42\text{ rad}$)
  - SE Border $[845, 620]$ ($27 \times 22\text{ px}$, Compact Flank Boulder, $\theta=-0.35\text{ rad}$)
  - East Pebble $[670, 515]$ ($20 \times 17\text{ px}$, Minor Granite Pebble, $\theta=0.50\text{ rad}$)
- **Thickets (6 Multi-Tier Stealth Cover Zones):**
  - North $[390, 110]$ ($R=46\text{ px}$, stealth bonus $0.80$)
  - West $[210, 360]$ ($R=52\text{ px}$, stealth bonus $0.80$)
  - SE Corridor $[730, 470]$ ($R=42\text{ px}$, stealth bonus $0.80$)
  - SE Cluster $[850, 535]$ ($R=38\text{ px}$, stealth bonus $0.85$)
  - South Edge $[650, 615]$ ($R=34\text{ px}$, stealth bonus $0.75$)
  - NE Canopy $[860, 140]$ ($R=44\text{ px}$, stealth bonus $0.80$)
- **Dandelion Medicinal Grove:** $[560, 540]$, capacity $80\text{ u}$.
- **Geological Hazard (Sinkhole):** $[880, 270]$, radius $65\text{ px}$.
- **Predator Den Landmark:** $[910, 130]$, radius $26\text{ px}$.

---

## 3. Host World Laws (Physical & Differential Invariants)

### 3.1 Physiological Differential Dynamics
Vitals evolve deterministically per simulation tick $\Delta t$:
$$\frac{dE_i}{dt} = -\alpha_E - \beta_E \|v_i\| + \eta_{\text{feed}}$$
$$\frac{dH_i}{dt} = +\alpha_H - \delta_H \cdot \mathbb{I}_{\text{eating}}$$
$$\frac{dT_i}{dt} = +\alpha_T - \delta_T \cdot \mathbb{I}_{\text{drinking}}$$
Where $\alpha_E = 0.02$, $\beta_E = 0.015$, $\alpha_H = 0.035$, $\alpha_T = 0.030$. When $H_i > 85$ or $T_i > 85$, health decays: $\frac{d\Omega_i}{dt} = -0.05$.

### 3.2 Atmospheric Scent Advection-Diffusion
Pheromones and predator odor disperse according to 2D advection-diffusion:
$$\frac{\partial C}{\partial t} + \mathbf{v}_{\text{wind}} \cdot \nabla C = D \nabla^2 C - \lambda C$$
Where $\mathbf{v}_{\text{wind}} = (v_w \cos \theta_w, v_w \sin \theta_w)$ and decay factor $\lambda = 0.014\text{ s}^{-1}$.

### 3.3 Spatial Lookahead & Invariant Collision Guards
- **Impenetrable Rock Margin:** $\forall j, \|p_i - p_{\text{rock},j}\| \ge R_{\text{rock},j} + r_i$.
- **Predator Safety Separation:** $\|p_i - p_{\text{wolf}}\| \ge D_{\text{safety}} = 35\text{ px}$.
- **Hazard Void Boundary:** $\|p_i - p_{\text{sinkhole}}\| \ge R_{\text{sinkhole}} + r_i$.

---

## 4. Cognitive Architecture & Epistemic Limits

```
+-------------------------------------------------------------------------+
|                         HOST PHYSICAL GROUND TRUTH                      |
|  - Real Resource Stock: Bush_N = 0u, Bush_E = 100u, Bush_W = 100u       |
|  - True Predator Position: Wolf = [620, 280] (Ambush Behind Rock NE)   |
|  - Microclimate: Wind = 135 deg (SW), Rain = 0.0 mm/h                   |
+------------------------------------+------------------------------------+
                                     |
                                     v [Sensory Aperture]
                                     | - Vision Cone: R_v <= 140px, angle 120 deg
                                     | - Occlusion: In-Cover (80% stealth bonus)
                                     | - Wind Odor: Upwind detection only
                                     v
+-------------------------------------------------------------------------+
|                  ALPHA SCOUT SUBJECTIVE BELIEF (SLM STATE)             |
|  - Stale Observation: FactCard-02 ("Bush_N = 80u, safe grazing")        |
|  - Epistemic Blindspot: Predator unobserved (beyond line-of-sight)      |
|  - Intent Generation: SLM emits MOVE_TO [520, 140] via Corridor East    |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                   MỘNG NHIỄM INVARIANT GOVERNOR (HOST GATING)           |
|  - Step 1: TrajectoryLookahead(4 steps)                                 |
|  - Step 2: Invariant Check: dist(path, Wolf) = 28px < 35px threshold!   |
|  - Step 3: ReflexBreaker INTERCEPT -> REJECT MOVE_TO                     |
|  - Step 4: Fallback Safe Action: RETREAT_TO_THICKET [390, 110]          |
+-------------------------------------------------------------------------+
```

### 4.1 Epistemic Asymmetry Equations
Let $\mathcal{W}$ be the ground truth world state and $\mathcal{B}_i$ be entity $i$'s subjective belief:
$$\mathcal{B}_i(t) = \text{Merge}\left(\mathcal{B}_i(t - \Delta t), \text{Obs}_i(\mathcal{W}(t))\right)$$
Where sensory observation $\text{Obs}_i$ is strictly constrained by the sensory mask $\mathbf{M}_i$:
$$\text{Obs}_i(x, y) = \begin{cases} \mathcal{W}(x, y) & \text{if } \|(x,y) - p_i\| \le R_{\text{vision}} \land \text{Visible}(p_i, (x,y)) \\ \emptyset & \text{otherwise} \end{cases}$$
If an area has not been surveyed recently:
$$\text{Confidence}(FactCard_k) = \exp(-\lambda_{\text{stale}} \cdot \Delta t_{\text{last\_seen}})$$

### 4.2 Selective SLM Invocation Invariants
SLM inference is triggered **ONLY** under defined condition gates:
1. **Colony Macro Planning:** Scheduled every $T_{\text{macro}} = 500\text{ ticks}$ ($\sim 10\text{ s}$).
2. **Surprise / Shock Spike:** Epistemic divergence $\|\mathcal{B}_{\text{leader}} - \text{Obs}_{\text{leader}}\| > \tau_{\text{surprise}}$ (e.g. reaching a depleted food bush).
3. **Predator Proximity Alert:** Unscreened predator enters sensory cone.
4. **Reflex Breaker Post-Incident Evaluation:** Host interdiction forces SLM to synthesize alternative path.

Passive flocking, boids alignment, obstacle steering, and continuous feeding are handled 100% deterministically by the Host with zero LLM/SLM token cost.

---

## 5. Demonstration Scenarios & Event Chains

### Scenario A: Localized Drought & Epistemic Skew Discovery
1. **T0 (Equilibrium):** Quorum foraging in North meadow; North Bush contains $100\text{ u}$.
2. **T1 (Environmental Shock):** Operator triggers drought shock; Host drops North Bush to $0\text{ u}$.
3. **T2 (Epistemic Divergence):** Panel B flags `EPISTEMIC SKEW` (Ground Truth: $0\text{ u}$ vs Scout Belief: $80\text{ u}$).
4. **T3 (Contact & Surprise Trigger):** Scout enters North bush perimeter ($R \le 42\text{ px}$), discovers discrepancy. Surprise triggers single SLM invocation ($142\text{ tokens}$).
5. **T4 (Resolution):** AutoDream updates FactCard-02 $\to$ Colony reroutes to West Bush $[260, 230]$.

### Scenario B: Wolf Ambush & Mộng Nhiễm Reflex Breaker
1. **T0 (Nominal Grazing):** Colony grazing in Eastern meadow.
2. **T1 (Predator Shock):** Operator spawns Wolf at $[620, 280]$ behind NE rock ridge.
3. **T2 (Cognitive Oversight):** Scout issues `ACTION: MOVE_TO [770, 370]`.
4. **T3 (Mộng Nhiễm Lookahead Interception):** Trajectory projection detects distance to predator $< 35\text{ px}$.
5. **T4 (Reflex Breaker Enforcement):** Host rejects candidate step, logs `GATED` arbitration event to Panel C, and forces swarm dispersion into Thicket cover $[720, 490]$ and Burrow $[320, 520]$.

### Scenario C: Microclimate Scent Shift & Standby Interposition
1. **T0 (Steady Wind):** Wind blowing Southwest ($135^\circ$); rabbit scents mask predator approach from the North.
2. **T1 (Atmospheric Shift):** Wind shifts to Northeast ($45^\circ$, $24\text{ km/h}$). Pheromone plumes reverse direction.
3. **T2 (Olfactory Warning):** Upwind scent particles reach Scout; alarm threshold exceeded.
4. **T3 (Human Standby):** Operator presses `Can Thiệp Standby`. Simulation freezes deterministically at tick $t^*$ for manual audit.
