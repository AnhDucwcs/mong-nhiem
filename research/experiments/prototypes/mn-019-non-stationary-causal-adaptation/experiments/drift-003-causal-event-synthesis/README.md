# Stage 3: Counterfactual Causal Event Synthesis & Proactive Invariant Induction (`drift-003-causal-event-synthesis`)

## 1. Overview & Research Intent

Stage 3 represents the culmination of Milestone MN-019. While Stage 1 (`drift-001`) resolved continuous parametric drift reactively and Stage 2 (`drift-002`) resolved structural topological entity emergence, Stage 3 addresses **causal non-stationarity and latent coupling**.

In cyber-physical systems, microworlds, and real-world operations, actions frequently carry hidden downstream side effects, non-linear coupling thresholds, and irreversible trap dynamics:
1. **Latent Causal Traps:** Candidate actions that appear valid under local schemas may induce catastrophic failures (thermal runaway, cavitation, blackout, power starvation) if triggered under specific coupled latent conditions.
2. **Proactive Causal Rule Induction:** Rather than blindly executing candidate actions and relying on post-hoc reactive rollbacks (which fail in cascading or non-reversible domains), the Host mines the hash-chained `CausalEventLog` DAG to induce verified causal invariants:
   $$\text{Pre-Condition}(c) \land do(a) \implies \Delta s_{\text{target}} \land \Delta s_{\text{latent}}$$
3. **Non-Destructive Counterfactual Rollouts:** The Host projects hypothetical candidate action rollouts using an isolated sandbox hook (`simulate_counterfactual_step`) without committing state changes to the primary world.
4. **Proactive Affordance Gating:** Latent causal traps are preemptively pruned from the active GBNF grammar, and high-level Causal Invariant Cards (`[CAUSAL_RULE ...]`) are consolidated into AutoDream episodic memory.

---

## 2. Experimental Arms

- **Arm 1 (Flat Baseline):** Unconstrained model output without GBNF grammar constraints or causal reasoning.
- **Arm 2 (Reactive Host Control):** The reactive system from Stage 1 and Stage 2 with Discrepancy Monitoring and Memento Rollback, but **without Counterfactual Causal Synthesis**. Hits latent causal traps reactively before discovering their infeasibility, suffering rollback penalties.
- **Arm 3 (Counterfactual Causal Synthesis Host):** Full proactive architecture featuring DAG Causal Induction, Sandbox Rollouts, Proactive GBNF Affordance Gating, and AutoDream Causal Invariant Consolidation.

---

## 3. Reproduction & Execution Instructions

```bash
# 1. Run unit test suite
pytest tests/ -v

# 2. Run deterministic Track 1 benchmark (60 cases across 4 domains)
python scripts/run_benchmark.py --track 1 --corpus definition/cases.json --limit 60

# 3. Independent audit verification (enforces Gate B Contract M1–M9)
python scripts/validate_audit.py runs/<run_id>/

# 4. Generate academic report
python scripts/populate_reports.py runs/<run_id>/ --out reports/drift-003-results.md

# 5. Generate cryptographic manifests
python scripts/generate_manifests.py
```
