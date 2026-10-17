# MN-025: Cross-Domain Epistemic Knowledge Transfer, Cognitive Belief Conflict Reconciliation, and Stochastic Open Microworlds

## Strategic Intent & Executive Overview

Milestone MN-025 advances Mộng Nhiễm from solitary within-domain long-horizon microworld tracking to multi-stage cognitive generalization. While previous milestones (MN-023, MN-024) demonstrated that small language models (<4B) achieve constant-space $O(1)$ memory scaling (55 tokens) across extended horizons ($T=100$), actions were grounded in static, pre-configured domain environments.

MN-025 investigates three sequential cognitive frontiers evaluated on a single open-weights model (`Qwen3.5-2B-Q4_K_M.gguf`) hosted on local `llama-server.exe`:
1. **Stage 1 (Cross-Domain Epistemic Knowledge Transfer):** Evaluates whether an abstract 4-hop causal mitigation topology ($f: \mathcal{G}_{\text{src}} \to \mathcal{G}_{\text{tgt}}$) learned in a Source Domain (Nuclear Fission Reactor) accelerates fault mitigation in novel Target Domains (Orbital Habitat Life Support, Regional Smart Microgrid) across completely disjoint surface vocabularies, subjected to immediate negative transfer traps and latent time-bomb cavitation/resonance degradation traps.
2. **Stage 2 (Cognitive Belief Conflict Reconciliation):** Evaluates dialectic debate and tie-breaking when identical SLM agents form contradictory belief states ($\mathcal{G}_A \neq \mathcal{G}_B$) due to masked historical observations, subjected to stubborn deadlock traps, hallucinated compromise traps, and latent unexpressed assumption lockups.
3. **Stage 3 (Open-World Stochastic Shocks & Dynamic Topology):** Evaluates non-linear step-function Poisson shocks and zero-shot affordance utilization of newly registered entities, subjected to phantom entity decoys, non-monotonic anchor demotion, and latent thermal runaway sleepers.

## Architectural Separation & Invariant Governance

Mộng Nhiễm strictly enforces the Host Authority Invariant:
- **LLM Reasoning Engine:** The model operates strictly as an isolated, prompt-bounded reasoning engine emitting structured actions (`ACTION: <VERB> <TARGET>`).
- **Host Authoritative Microworld:** The Host maintains absolute authority over physical state transitions, discrete time advances, resource leases, and conservation invariant verification (`ConservationInvariantGuard`).
- **3-Tier Fact Card Working Memory:**
  - *Tier 1 (Invariant Anchors):* Verified structural schema rules and cryptographic state hashes ($p=1.0$).
  - *Tier 2 (Causal Frontier):* Active, bounded working memory with auto-pruning and non-monotonic anchor demotion ($TTL \le 4$).
  - *Tier 3 (Valid Affordances):* Host-filtered dynamic action menu with Typed Affordance Signatures.

## Experimental Corpus & Evaluation Topology

- **Evaluation Corpus:** $N = 60$ standardized scenarios across 3 stages ($N=20$ per stage):
  - 10 Nominal Scenarios (50.0%)
  - 5 Immediate Adversarial Trap Scenarios (25.0%)
  - 5 Latent Time-Bomb Degradation Scenarios (25.0%)
- **Experimental Arms:**
  - **Arm 1 (Monolithic Cold-Start Baseline):** Flat unspecialized prompt without topological schema.
  - **Arm 2 (Phased Baseline Control):** Phased Scout-Actuator cycle without cross-domain schema transfer.
  - **Arm 3 (Host Topological Epistemic Transfer Engine):** Phased Scout-Actuator cycle armed with Topological Schema Cards, Epistemic Reconciler, and Dynamic Schema Registry.
- **Model Topology:** Pure homogeneous local open-weights `Qwen3.5-2B-Q4_K_M.gguf` on `llama-server.exe` (port 18502, ChatML format, greedy decoding $T=0.0$).

## Reproduction & Execution

```powershell
# 1. Run unit test suite
pytest -v research/experiments/prototypes/mn-025-cross-domain-epistemic-transfer/tests/

# 2. Run Track 1 Host Simulator
python research/experiments/prototypes/mn-025-cross-domain-epistemic-transfer/src/runner_track1.py

# 3. Run Track 2 Real Model Inference
python research/experiments/prototypes/mn-025-cross-domain-epistemic-transfer/src/runner_track2.py
```
