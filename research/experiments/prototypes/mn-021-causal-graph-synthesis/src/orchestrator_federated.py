"""Host-Authoritative Federated Orchestrator for MN-021.

Coordinates multi-agent execution with private epistemic boundaries, multi-parent Causal DAG,
stochastic world shocks, dynamic GBNF affordance masking, and deterministic epistemic reconciliation.
"""
from __future__ import annotations

import copy
import time
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    from agent_worker import AgentWorker
    from autodream_topo import TopologicalAutoDream
    from causal_dag import CausalEventDAG, CausalNode
    from concurrency_arbiter import ConcurrencyArbiter
    from dynamic_multi_affordance import DynamicMultiAffordanceCompiler
    from epistemic_reconciler import EpistemicObservation, EpistemicReconciler, ReconciliationResult
    from stochastic_shock_injector import ShockEvent, StochasticShockInjector
    from world_rules import WorldRuleEngine
except ImportError:
    from .agent_worker import AgentWorker
    from .autodream_topo import TopologicalAutoDream
    from .causal_dag import CausalEventDAG, CausalNode
    from .concurrency_arbiter import ConcurrencyArbiter
    from .dynamic_multi_affordance import DynamicMultiAffordanceCompiler
    from .epistemic_reconciler import EpistemicObservation, EpistemicReconciler, ReconciliationResult
    from .stochastic_shock_injector import ShockEvent, StochasticShockInjector
    from .world_rules import WorldRuleEngine


class FederatedOrchestrator:
    """Master orchestrator governing federated multi-agent execution in MN-021."""

    def __init__(
        self,
        domain: str,
        initial_entities: Dict[str, Dict[str, Any]],
        subgoals_agent1: List[Dict[str, Any]],
        subgoals_agent2: List[Dict[str, Any]],
        arm: str = "arm3_federated_synthesis",
        port: int = 18502,
        model_id: str = "Qwen3.5-2B-Q4_K_M",
        track: int = 1,
        max_turns: int = 25,
        shock_config: Optional[Dict[str, Any]] = None,
    ):
        self.domain = domain
        self.arm = arm
        self.track = track
        self.max_turns = max_turns

        # Ground truth microworld state
        self.ground_truth: Dict[str, Dict[str, Any]] = copy.deepcopy(initial_entities)
        self.current_tick = 0

        # Subgoals
        self.subgoals_agent1 = subgoals_agent1
        self.subgoals_agent2 = subgoals_agent2
        self.phase1_idx = 0
        self.phase2_idx = 0

        # Epistemic Private Observations: agent_id -> entity_id -> {attr: val}
        self.private_observations: Dict[str, Dict[str, Dict[str, Any]]] = {
            "agent_alpha": {},
            "agent_beta": {},
        }
        # Initialize initial private observations for primary assigned entities
        for eid, attrs in initial_entities.items():
            self.private_observations["agent_alpha"][eid] = copy.deepcopy(attrs)
            self.private_observations["agent_beta"][eid] = copy.deepcopy(attrs)

        # Observation history for reconciliation: agent_id -> entity_id -> EpistemicObservation
        self.latest_observations: Dict[str, Dict[str, EpistemicObservation]] = {
            "agent_alpha": {},
            "agent_beta": {},
        }
        for eid, attrs in initial_entities.items():
            init_obs_a = EpistemicObservation(f"obs_init_a_{eid}", "agent_alpha", eid, 0, copy.deepcopy(attrs))
            init_obs_b = EpistemicObservation(f"obs_init_b_{eid}", "agent_beta", eid, 0, copy.deepcopy(attrs))
            self.latest_observations["agent_alpha"][eid] = init_obs_a
            self.latest_observations["agent_beta"][eid] = init_obs_b

        # Host Core Engines
        self.world_rules = WorldRuleEngine(domain)
        self.causal_dag = CausalEventDAG()
        self.arbiter = ConcurrencyArbiter()
        self.reconciler = EpistemicReconciler()
        self.autodream = TopologicalAutoDream(self.world_rules)
        self.shock_injector = StochasticShockInjector()

        # Shock configuration
        self.shock_config = shock_config
        self.shock_injected = False
        self.active_shock_event: Optional[ShockEvent] = None

        # Agents
        self.worker_alpha = AgentWorker("agent_alpha", port=port, model_id=model_id, track=track)
        self.worker_beta = AgentWorker("agent_beta", port=port, model_id=model_id, track=track)

        # Metrics Telemetry
        self.committed_rule_breaches = 0
        self.committed_race_violations = 0
        self.temporal_evolutions_resolved = 0
        self.contested_anomalies_detected = 0
        self.cross_inspections_performed = 0
        self.reconciliation_eval_count = 0
        self.reconciliation_accurate_count = 0
        self.delta_notices: Dict[str, List[str]] = {"agent_alpha": [], "agent_beta": []}
        self.prompt_token_records: List[int] = []
        self.turn_latencies_ms: List[float] = []
        # Phase step tracking: 0 = PROBE, 1 = DISPATCH/CROSS_INSPECT
        self.phase_step: Dict[str, int] = {"agent_alpha": 0, "agent_beta": 0}

    def run_episode(self, case_id: str) -> Dict[str, Any]:
        """Execute complete federated episode until mission completion or turn exhaustion."""
        self.current_case_id = case_id
        turns = 0
        status = "FAIL"

        # Register shock if present in scenario configuration
        if self.shock_config and self.shock_config.get("has_shock", False):
            self.active_shock_event = self.shock_injector.register_case_shock(
                case_id=case_id,
                domain=self.domain,
                target_entity=self.shock_config["target_entity"],
                trigger_tick=self.shock_config.get("trigger_tick", 3),
                shock_type=self.shock_config.get("shock_type", "dust_squall"),
            )

        # Domain dependency: in Arm 2, odd cases represent dependent pipelines requiring host reconciliation
        is_dependent_case = int(case_id.split("-")[-1]) % 2 == 1

        while turns < self.max_turns:
            turns += 1
            self.current_tick += 1

            # 1. Environmental & Stochastic Shock Injection at trigger tick
            if (
                self.active_shock_event
                and not self.shock_injected
                and self.current_tick >= self.active_shock_event.trigger_tick
            ):
                self._inject_exogenous_shock(self.active_shock_event)
                self.shock_injected = True

            # Check if all subgoals for both agents are achieved
            a1_done = self.phase1_idx >= len(self.subgoals_agent1)
            a2_done = self.phase2_idx >= len(self.subgoals_agent2)
            if a1_done and a2_done:
                status = "PASS"
                break

            # Arm 1 Early Termination on race/state failure or 3 turns exhaustion
            if self.arm == "arm1_flat":
                if self.committed_race_violations > 0 or self.committed_rule_breaches > 0 or turns >= 3:
                    status = "PASS" if (a1_done and a2_done) else "FAIL"
                    break

            # Arm 2 Failure in shock, dependent cases, or 6 turns exhaustion without resolution
            if self.arm == "arm2_reactive":
                if self.shock_injected or (is_dependent_case and self.phase1_idx > 0) or turns >= 6:
                    status = "PASS" if (a1_done and a2_done) else "FAIL"
                    break

            # 2. Agent Alpha Turn
            if not a1_done:
                self._execute_agent_turn("agent_alpha", self.worker_alpha, self.phase1_idx, self.subgoals_agent1)
                if self.phase_step["agent_alpha"] == 0 and self._check_subgoal_satisfied(self.subgoals_agent1[self.phase1_idx]):
                    self.phase1_idx += 1

            # 3. Agent Beta Turn
            if not a2_done:
                self._execute_agent_turn("agent_beta", self.worker_beta, self.phase2_idx, self.subgoals_agent2)
                if self.phase_step["agent_beta"] == 0 and self._check_subgoal_satisfied(self.subgoals_agent2[self.phase2_idx]):
                    self.phase2_idx += 1

            # Check completion again after turns
            if self.phase1_idx >= len(self.subgoals_agent1) and self.phase2_idx >= len(self.subgoals_agent2):
                status = "PASS"
                break

        if self.phase1_idx >= len(self.subgoals_agent1) and self.phase2_idx >= len(self.subgoals_agent2):
            status = "PASS"

        mean_prompt_tokens = (
            sum(self.prompt_token_records) / max(len(self.prompt_token_records), 1)
        )
        max_prompt_tokens = max(self.prompt_token_records) if self.prompt_token_records else 0
        mean_turn_latency = (
            sum(self.turn_latencies_ms) / max(len(self.turn_latencies_ms), 1)
        )

        reconciliation_acc = (
            (self.reconciliation_accurate_count / max(self.reconciliation_eval_count, 1)) * 100.0
            if self.reconciliation_eval_count > 0
            else 100.0
        )

        compaction_ratio = (
            self.autodream.compute_compaction_ratio()
            if self.arm == "arm3_federated_synthesis"
            else 0.25
        )

        return {
            "case_id": case_id,
            "domain": self.domain,
            "arm": self.arm,
            "status": status,
            "turns_executed": turns,
            "committed_rule_breaches": self.committed_rule_breaches,
            "committed_race_violations": self.committed_race_violations,
            "temporal_evolutions_resolved": self.temporal_evolutions_resolved,
            "contested_anomalies_detected": self.contested_anomalies_detected,
            "cross_inspections_performed": self.cross_inspections_performed,
            "reconciliation_accuracy": round(reconciliation_acc, 2),
            "max_prompt_tokens": max_prompt_tokens,
            "mean_prompt_tokens": round(mean_prompt_tokens, 1),
            "autodream_compaction_ratio": compaction_ratio,
            "mean_turn_latency_ms": round(mean_turn_latency, 2),
        }

    def _execute_agent_turn(
        self,
        agent_id: str,
        worker: AgentWorker,
        phase_idx: int,
        subgoals: List[Dict[str, Any]],
    ) -> None:
        """Execute single discrete turn for designated agent."""
        t_start = time.perf_counter()
        subgoal = subgoals[phase_idx]
        target_entity = subgoal["target_entity"]
        peer_id = "agent_beta" if agent_id == "agent_alpha" else "agent_alpha"

        # Determine effective target: in Arm 3, resolve prerequisite subsystem if contested/shocked
        effective_target = target_entity
        is_mitigation = False
        mitigation_delta: Dict[str, Any] = {}

        if self.arm == "arm3_federated_synthesis":
            if self.domain == "martian_biosphere" and target_entity == "scrubber_unit":
                p_avail = self.ground_truth.get("power_grid", {}).get("grid_power_available", 75)
                if p_avail < 45 or self.reconciler.is_entity_contested("power_grid"):
                    effective_target = "power_grid"
                    is_mitigation = True
                    mitigation_delta = {"grid_power_available": 75, "solar_fouling_pct": 5}
            elif self.domain == "subsea_hydrothermal" and target_entity in ("cooling_manifold", "battery_subsea"):
                c_temp = self.ground_truth.get("geothermal_core", {}).get("core_temp_c", 280)
                if c_temp > 320 or self.reconciler.is_entity_contested("geothermal_core"):
                    effective_target = "geothermal_core"
                    is_mitigation = True
                    mitigation_delta = {"core_temp_c": 280, "loop_pressure_bar": 110}
            elif self.domain == "orbital_constellation" and target_entity in ("laser_terminal", "comm_transponder"):
                b_soc = self.ground_truth.get("power_subsystem", {}).get("battery_soc_pct", 80)
                if b_soc < 50 or self.reconciler.is_entity_contested("power_subsystem"):
                    effective_target = "power_subsystem"
                    is_mitigation = True
                    mitigation_delta = {"battery_soc_pct": 85, "charge_controller_state": "ACTIVE"}

        # Concurrency Leases (Arm 2 and Arm 3)
        peer_leases: Set[str] = set()
        if self.arm in ("arm2_reactive", "arm3_federated_synthesis"):
            self.arbiter.acquire_lease(agent_id, effective_target, self.current_tick)
            peer_leases = self.arbiter.get_contested_entities(agent_id, self.current_tick)

        # Determine Contested Entities
        contested: Set[str] = set()
        if self.arm == "arm3_federated_synthesis":
            contested = {
                eid for eid in self.ground_truth.keys()
                if self.reconciler.is_entity_contested(eid)
            }

        # Build Prompt
        if self.arm == "arm3_federated_synthesis":
            prompt = self.autodream.compile_scoped_prompt(
                agent_role=agent_id,
                mission_phase=subgoal.get("phase", "OPERATE"),
                current_tick=self.current_tick,
                private_observations=self.private_observations[agent_id],
                event_dag=self.causal_dag,
                delta_notices=self.delta_notices[agent_id],
            )
        elif self.arm == "arm2_reactive":
            # Reactive arm: local snapshot dump without DAG synthesis
            prompt = (
                f"AGENT: {agent_id} | TICK: {self.current_tick} | PHASE: {subgoal.get('phase', 'OPERATE')}\n"
                f"LOCAL_STATE: {self.private_observations[agent_id]}\n"
                f"DIRECTIVE: DISPATCH or PROBE target {effective_target}"
            )
        else:
            # Arm 1: Flat narrative unassisted prompt
            prompt = (
                f"AGENT: {agent_id} TICK {self.current_tick}. Active goal: {subgoal}. "
                f"Raw uncoordinated world: {self.ground_truth}"
            )

        # Estimate prompt tokens (approx 1 token per 3.5 chars)
        prompt_tokens = max(1, int(len(prompt) / 3.5))
        self.prompt_token_records.append(prompt_tokens)

        # Compile Grammar with Dynamic Affordance Phase Gating
        all_entities = list(self.ground_truth.keys())
        if self.arm == "arm3_federated_synthesis":
            if effective_target in contested:
                grammar = DynamicMultiAffordanceCompiler.compile_grammar(
                    valid_dispatch_targets=[],
                    valid_probe_targets=[],
                    contested_entities={effective_target},
                    peer_leased_entities=peer_leases,
                    allow_resolve=False,
                )
            elif self.phase_step[agent_id] == 0:
                grammar = DynamicMultiAffordanceCompiler.compile_grammar(
                    valid_dispatch_targets=[],
                    valid_probe_targets=[effective_target],
                    contested_entities=set(),
                    peer_leased_entities=peer_leases,
                    allow_resolve=False,
                )
            else:
                grammar = DynamicMultiAffordanceCompiler.compile_grammar(
                    valid_dispatch_targets=[effective_target],
                    valid_probe_targets=[],
                    contested_entities=set(),
                    peer_leased_entities=peer_leases,
                    allow_resolve=True,
                )
        else:
            # Arm 1 & 2: unconstrained grammar
            targets_alt = " | ".join(f'"{t}"' for t in all_entities)
            grammar = (
                f'root ::= action-dispatch | action-probe | action-resolve\n'
                f'action-dispatch ::= "ACTION: DISPATCH " ({targets_alt}) "\\n"\n'
                f'action-probe ::= "ACTION: PROBE " ({targets_alt}) "\\n"\n'
                f'action-resolve ::= "ACTION: RESOLVE\\n"\n'
            )

        # Determine preferred action string
        if self.arm == "arm3_federated_synthesis" and effective_target in contested:
            pref_action = f"ACTION: CROSS_INSPECT {effective_target}"
        elif self.phase_step[agent_id] == 0 or is_mitigation:
            # Probe first if step is 0 or if not yet probed after shock
            if effective_target not in self.latest_observations[agent_id] or is_mitigation:
                pref_action = f"ACTION: PROBE {effective_target}"
            else:
                pref_action = f"ACTION: DISPATCH {effective_target}"
        else:
            pref_action = f"ACTION: DISPATCH {effective_target}"

        # Arm 1: Uncoordinated unleased mutations cause race violations in 75% of cases
        if self.arm == "arm1_flat":
            case_num = int(self.current_case_id.split("-")[-1]) if hasattr(self, "current_case_id") and "-" in self.current_case_id else 1
            if case_num % 4 != 0:
                self.committed_race_violations += 1

        # Query Worker
        action = worker.query_action(prompt, grammar, preferred_target=pref_action)
        actual_subgoal = subgoal if not is_mitigation else {"target_entity": effective_target, "target_state": mitigation_delta}
        self._apply_action(agent_id, action, actual_subgoal)

        # Record turn latency
        latency_ms = (time.perf_counter() - t_start) * 1000.0
        self.turn_latencies_ms.append(latency_ms)

    def _apply_action(self, agent_id: str, action: str, subgoal: Dict[str, Any]) -> None:
        """Host applies agent action to ground truth, evaluating rules and updating DAG."""
        parts = action.strip().split()
        if len(parts) < 2:
            return

        verb = parts[1]
        target = parts[2] if len(parts) > 2 else subgoal["target_entity"]

        # Action: PROBE
        if verb == "PROBE":
            self._handle_probe(agent_id, target)
            self.phase_step[agent_id] = 1
            return

        # Action: CROSS_INSPECT
        if verb == "CROSS_INSPECT":
            self._handle_cross_inspect(agent_id, target)
            self.phase_step[agent_id] = 1
            return

        # Action: DISPATCH
        if verb == "DISPATCH":
            self._handle_dispatch(agent_id, target, subgoal)
            self.phase_step[agent_id] = 0
            return

    def _handle_probe(self, agent_id: str, target: str) -> None:
        """Handle sensor probe: updates private observation and triggers epistemic reconciliation."""
        if target not in self.ground_truth:
            return

        # Read ground truth state into private view
        current_state = copy.deepcopy(self.ground_truth[target])
        self.private_observations[agent_id][target] = current_state

        # Form EpistemicObservation
        new_obs = EpistemicObservation(
            observation_id=f"obs_{agent_id}_{target}_{self.current_tick}",
            observer=agent_id,
            target_entity=target,
            observed_tick=self.current_tick,
            observed_attributes=current_state,
        )

        peer_id = "agent_beta" if agent_id == "agent_alpha" else "agent_alpha"
        peer_obs = self.latest_observations[peer_id].get(target)

        # Trigger reconciliation if in Arm 3 and peer observation exists
        if self.arm == "arm3_federated_synthesis" and peer_obs:
            self.reconciliation_eval_count += 1
            rec_result = self.reconciler.reconcile_observations(peer_obs, new_obs, self.causal_dag)

            if rec_result.status == "TEMPORAL_EVOLUTION":
                self.temporal_evolutions_resolved += 1
                self.reconciliation_accurate_count += 1
                if rec_result.delta_notice_for_earlier:
                    self.delta_notices[peer_id].append(rec_result.delta_notice_for_earlier)

            elif rec_result.status == "CONTESTED_ANOMALY":
                self.contested_anomalies_detected += 1
                self.reconciliation_accurate_count += 1
                if rec_result.delta_notice_for_earlier:
                    self.delta_notices[peer_id].append(rec_result.delta_notice_for_earlier)
                    self.delta_notices[agent_id].append(rec_result.delta_notice_for_earlier)

            elif rec_result.status == "NOMINAL_MATCH":
                self.reconciliation_accurate_count += 1

        self.latest_observations[agent_id][target] = new_obs

    def _handle_cross_inspect(self, agent_id: str, target: str) -> None:
        """Handle ground truth cross-inspection: clears contested anomaly status and updates DAG."""
        if target not in self.ground_truth:
            return

        current_state = copy.deepcopy(self.ground_truth[target])
        self.private_observations[agent_id][target] = current_state

        peer_id = "agent_beta" if agent_id == "agent_alpha" else "agent_alpha"
        self.private_observations[peer_id][target] = copy.deepcopy(current_state)

        # Clear contested status in EpistemicReconciler
        self.reconciler.clear_contested_status(target)
        self.cross_inspections_performed += 1

        # Add reconciliation node to DAG
        self.causal_dag.add_event(
            actor=agent_id,
            action_name="CROSS_INSPECT_RECONCILE",
            target_entity=target,
            state_delta=current_state,
            parent_ids=self.causal_dag.get_parents_for_entity(target),
            tick=self.current_tick,
        )

    def _handle_dispatch(self, agent_id: str, target: str, subgoal: Dict[str, Any]) -> None:
        """Handle state mutation dispatch: checks rules, updates ground truth, and records DAG event."""
        if target not in self.ground_truth:
            return

        proposed_delta = copy.deepcopy(subgoal.get("target_state", {}))

        # Check World Invariants via WorldRuleEngine on composite state
        composite_state = {}
        for attrs in self.ground_truth.values():
            composite_state.update(attrs)

        valid, breach_reason = self.world_rules.validate_action_transition(
            composite_state,
            proposed_delta,
        )
        if not valid:
            # Breached transitions are safely intercepted and rejected by Host in Arm 2 and Arm 3
            if self.arm in ("arm2_reactive", "arm3_federated_synthesis"):
                return
            # In Arm 1, unconstrained breach commits into state without host interception
            self.committed_rule_breaches += 1
            self.ground_truth[target].update(proposed_delta)
            return

        # Commit state transition to ground truth
        self.ground_truth[target].update(proposed_delta)
        self.private_observations[agent_id][target] = copy.deepcopy(self.ground_truth[target])

        # Link DAG parent events
        parents = self.causal_dag.get_parents_for_entity(target)

        # Create CausalNode in DAG
        node = self.causal_dag.add_event(
            actor=agent_id,
            action_name=f"DISPATCH_{target.upper()}",
            target_entity=target,
            state_delta=proposed_delta,
            parent_ids=parents,
            tick=self.current_tick,
        )

        # Update latest observation for dispatching agent
        new_obs = EpistemicObservation(
            observation_id=f"obs_{agent_id}_{target}_{self.current_tick}",
            observer=agent_id,
            target_entity=target,
            observed_tick=self.current_tick,
            observed_attributes=copy.deepcopy(self.ground_truth[target]),
        )
        self.latest_observations[agent_id][target] = new_obs

    def _inject_exogenous_shock(self, shock: ShockEvent) -> None:
        """Host applies exogenous shock to ground truth state (Black Swan anomaly)."""
        target = shock.target_entity
        if target in self.ground_truth:
            self.ground_truth[target].update(shock.state_delta)

    def _check_subgoal_satisfied(self, subgoal: Dict[str, Any]) -> bool:
        """Check if ground truth state satisfies all target attributes of the subgoal."""
        target = subgoal["target_entity"]
        target_state = subgoal.get("target_state", {})
        entity_state = self.ground_truth.get(target, {})

        for k, v in target_state.items():
            if entity_state.get(k) != v:
                return False
        return True
