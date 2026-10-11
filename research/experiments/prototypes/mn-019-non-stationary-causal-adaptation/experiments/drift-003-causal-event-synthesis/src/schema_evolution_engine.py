"""Dynamic Schema Evolution Engine for Stage 3.

Manages dynamic entity lifecycles (EMERGE, MUTATE_SCHEMA, RETIRE) and relational
edge bindings, recording all structural topological shifts into the CausalEventLog.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from causal_event_logger import CausalEventLog


@dataclass
class SchemaEvolutionRule:
    """Specification of an environmental structural schema transition."""
    rule_id: str
    lifecycle_action: str  # 'EMERGE', 'MUTATE_SCHEMA', 'RETIRE'
    target_entity_id: str
    trigger_type: str      # 'tick', 'state_condition'
    trigger_tick: Optional[int] = None
    trigger_condition: Optional[Dict[str, Any]] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    causal_hypothesis: str = ""
    is_executed: bool = False

    def is_triggered(self, current_tick: int, entities: Dict[str, Any]) -> bool:
        if self.is_executed:
            return False

        if self.trigger_type == "tick":
            return self.trigger_tick is not None and current_tick >= self.trigger_tick

        if self.trigger_type == "state_condition" and self.trigger_condition:
            eid = self.trigger_condition.get("entity_id")
            prop = self.trigger_condition.get("prop")
            op = self.trigger_condition.get("op", "==")
            val = self.trigger_condition.get("val")

            if eid in entities:
                entity = entities[eid]
                props = entity.properties if hasattr(entity, "properties") else entity
                curr_val = props.get(prop)
                if curr_val is not None and val is not None:
                    curr_float = float(curr_val)
                    target_float = float(val)
                    if op == ">=":
                        return curr_float >= target_float
                    elif op == "<=":
                        return curr_float <= target_float
                    elif op == "==":
                        return curr_float == target_float
                    elif op == ">":
                        return curr_float > target_float
                    elif op == "<":
                        return curr_float < target_float

        return False


class SchemaEvolutionEngine:
    """Host controller for structural schema evolution and dynamic entity topology."""

    def __init__(
        self,
        rules: Optional[List[SchemaEvolutionRule]] = None,
        event_logger: Optional[CausalEventLog] = None,
    ) -> None:
        self.rules: List[SchemaEvolutionRule] = rules or []
        self.event_logger: CausalEventLog = event_logger or CausalEventLog()
        self.emerged_entity_ids: List[str] = []
        self.retired_entity_ids: List[str] = []
        self.mutated_entity_ids: List[str] = []
        self.active_schema_alerts: List[Dict[str, Any]] = []

    def evaluate_step(
        self,
        current_tick: int,
        entities: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Evaluate and apply pending schema evolution rules at current tick."""
        fired_events = []

        for rule in self.rules:
            if rule.is_triggered(current_tick, entities):
                rule.is_executed = True
                eid = rule.target_entity_id

                if rule.lifecycle_action == "EMERGE":
                    pre_state = {}
                    payload = copy.deepcopy(rule.payload)
                    new_entity_type = payload.get("entity_type", "emergent_system")
                    new_props = payload.get("properties", {})
                    new_relations = payload.get("relations", {})
                    new_ttl = payload.get("ttl", None)

                    from microworld_engine import WorldEntity
                    emerged_entity = WorldEntity(
                        entity_id=eid,
                        entity_type=new_entity_type,
                        properties=new_props,
                        relations=new_relations,
                        version=1,
                        is_active=True,
                        ttl=new_ttl,
                    )
                    entities[eid] = emerged_entity
                    self.emerged_entity_ids.append(eid)
                    post_state = copy.deepcopy(emerged_entity.to_dict())

                    cevt = self.event_logger.record_event(
                        tick=current_tick,
                        event_type="EMERGE",
                        entity_id=eid,
                        pre_state=pre_state,
                        post_state=post_state,
                        delta_signature={"rule_id": rule.rule_id, "payload": payload},
                    )

                    alert = {
                        "type": "SCHEMA_EMERGE",
                        "tick": current_tick,
                        "entity_id": eid,
                        "entity_type": new_entity_type,
                        "properties": new_props,
                        "relations": new_relations,
                        "event_id": cevt.event_id,
                    }
                    self.active_schema_alerts.append(alert)
                    fired_events.append(alert)

                elif rule.lifecycle_action == "MUTATE_SCHEMA":
                    if eid in entities:
                        target = entities[eid]
                        pre_state = copy.deepcopy(target.to_dict())
                        mut_props = rule.payload.get("properties", {})
                        mut_rels = rule.payload.get("relations", {})

                        for k, v in mut_props.items():
                            target.properties[k] = v
                        for r_k, r_v in mut_rels.items():
                            target.relations[r_k] = r_v
                        target.version += 1

                        self.mutated_entity_ids.append(eid)
                        post_state = copy.deepcopy(target.to_dict())

                        cevt = self.event_logger.record_event(
                            tick=current_tick,
                            event_type="MUTATE_SCHEMA",
                            entity_id=eid,
                            pre_state=pre_state,
                            post_state=post_state,
                            delta_signature={"mutated_properties": mut_props, "mutated_relations": mut_rels},
                        )

                        alert = {
                            "type": "SCHEMA_MUTATE",
                            "tick": current_tick,
                            "entity_id": eid,
                            "mutated_properties": mut_props,
                            "mutated_relations": mut_rels,
                            "event_id": cevt.event_id,
                        }
                        self.active_schema_alerts.append(alert)
                        fired_events.append(alert)

                elif rule.lifecycle_action == "RETIRE":
                    if eid in entities:
                        target = entities[eid]
                        pre_state = copy.deepcopy(target.to_dict())
                        target.is_active = False
                        target.version += 1
                        self.retired_entity_ids.append(eid)
                        post_state = copy.deepcopy(target.to_dict())

                        cevt = self.event_logger.record_event(
                            tick=current_tick,
                            event_type="RETIRE",
                            entity_id=eid,
                            pre_state=pre_state,
                            post_state=post_state,
                            delta_signature={"reason": "DECOMMISSIONED_OR_EXPIRED"},
                        )

                        alert = {
                            "type": "SCHEMA_RETIRE",
                            "tick": current_tick,
                            "entity_id": eid,
                            "event_id": cevt.event_id,
                        }
                        self.active_schema_alerts.append(alert)
                        fired_events.append(alert)

        return fired_events
