"""Asynchronous Microworld Simulation Engine governing cyber-physical microworld states."""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class SwarmScenario:
    scenario_id: str
    domain: str  # "smart_microgrid", "fleet_logistics", "cluster_scheduling"
    title: str
    num_agents: int  # 5
    max_ticks: int  # 25
    initial_state: Dict[str, Any]
    target_state: Dict[str, Any]
    resources: List[str]
    agent_goals: Dict[str, str]


class AsyncWorldEngine:
    """Authoritative physical simulation engine verifying invariants and executing state transitions."""

    def __init__(self, scenario: SwarmScenario) -> None:
        self.scenario = scenario
        self.current_tick: int = 0
        self.state: Dict[str, Any] = copy.deepcopy(scenario.initial_state)
        self.physical_breaches: int = 0
        self.completed_subgoals: Set[str] = set()
        self.history: List[Dict[str, Any]] = []

    def get_resource_states(self, leases_summary: Dict[str, Dict]) -> Dict[str, Dict[str, Any]]:
        """Returns entity fact cards reflecting current state and lease status."""
        summary: Dict[str, Dict[str, Any]] = {}
        for res in self.scenario.resources:
            rstate = leases_summary.get(res, {})
            val = self.state.get(res, "")
            summary[res] = {
                "val": val,
                "holder": rstate.get("holder"),
                "state": rstate.get("state", "FREE"),
                "version": rstate.get("version", 1),
            }
        return summary

    def get_valid_affordances(
        self,
        agent_id: str,
        held_leases: Set[str],
        allow_unleased_act: bool = False,
    ) -> List[str]:
        """Dynamically generates valid actions available to agent_id."""
        affordances: List[str] = []
        domain = self.scenario.domain

        # Priority 1: Action and release affordances for held resources
        for res in held_leases:
            is_done = False
            if domain == "smart_microgrid" and self.state.get(res) == 0:
                is_done = True
            elif domain == "fleet_logistics" and self.state.get(res) == "DELIVERED":
                is_done = True
            elif domain == "cluster_scheduling" and self.state.get(res) == "COMPLETED":
                is_done = True

            if is_done:
                affordances.append(f"ACTION: RELEASE {res}")
            else:
                if domain == "smart_microgrid":
                    affordances.append(f"ACTION: ACT {res} STABILIZE")
                elif domain == "fleet_logistics":
                    affordances.append(f"ACTION: ACT {res} TRANSFER")
                elif domain == "cluster_scheduling":
                    affordances.append(f"ACTION: ACT {res} SCHEDULE")
                affordances.append(f"ACTION: RELEASE {res}")

        # Priority 2: Lease affordances for unheld resources (Goal-Conditioned Sorting)
        goal_str = self.scenario.agent_goals.get(agent_id, "")
        target_res = [res for res in self.scenario.resources if res in goal_str]
        other_res = [res for res in self.scenario.resources if res not in goal_str]
        ordered_resources = target_res + other_res

        for res in ordered_resources:
            if res not in held_leases:
                affordances.append(f"ACTION: LEASE {res}")
                if allow_unleased_act:
                    if domain == "smart_microgrid":
                        affordances.append(f"ACTION: ACT {res} STABILIZE")
                    elif domain == "fleet_logistics":
                        affordances.append(f"ACTION: ACT {res} TRANSFER")
                    elif domain == "cluster_scheduling":
                        affordances.append(f"ACTION: ACT {res} SCHEDULE")

        # Priority 3: Fallback Wait
        affordances.append("ACTION: WAIT")

        return affordances

    def step_action(
        self,
        agent_id: str,
        action_type: str,
        target: str,
        param: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """Applies valid action mutation to the authoritative microworld."""
        domain = self.scenario.domain

        if action_type == "WAIT":
            return True, "WAITED"

        if action_type == "ACT":
            if target not in self.state:
                self.physical_breaches += 1
                return False, f"BREACH: Target '{target}' does not exist in world state"

            if domain == "smart_microgrid":
                # Stabilizes substation energy imbalance
                curr_val = self.state.get(target, 0)
                if isinstance(curr_val, (int, float)):
                    if curr_val > 0:
                        self.state[target] = max(0, curr_val - 20)
                    elif curr_val < 0:
                        self.state[target] = min(0, curr_val + 20)
                    else:
                        self.state[target] = 0
                    if self.state[target] == 0:
                        self.completed_subgoals.add(f"balanced_{target}")
                return True, f"STABILIZED_{target}_TO_{self.state[target]}"

            elif domain == "fleet_logistics":
                # Transfers cargo package through loading bay
                curr_status = self.state.get(target, "PENDING")
                if curr_status == "PENDING":
                    self.state[target] = "LOADED"
                elif curr_status == "LOADED":
                    self.state[target] = "DELIVERED"
                    self.completed_subgoals.add(f"delivered_{target}")
                return True, f"TRANSFERRED_{target}_TO_{self.state[target]}"

            elif domain == "cluster_scheduling":
                # Schedules stage execution
                curr_status = self.state.get(target, "QUEUED")
                if curr_status == "QUEUED":
                    self.state[target] = "RUNNING"
                elif curr_status == "RUNNING":
                    self.state[target] = "COMPLETED"
                    self.completed_subgoals.add(f"completed_{target}")
                return True, f"SCHEDULED_{target}_TO_{self.state[target]}"

        return True, "NOOP"

    def advance_tick(self) -> int:
        """Advances world tick by 1."""
        self.current_tick += 1
        return self.current_tick

    def is_resolved(self) -> bool:
        """Checks if all target conditions are satisfied."""
        domain = self.scenario.domain
        target = self.scenario.target_state

        for k, expected_v in target.items():
            actual_v = self.state.get(k)
            if actual_v != expected_v:
                return False
        return True
