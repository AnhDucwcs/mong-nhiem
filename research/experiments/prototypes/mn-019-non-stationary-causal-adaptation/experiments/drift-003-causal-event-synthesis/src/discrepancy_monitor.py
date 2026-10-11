"""Schema Discrepancy & Evolution Monitor for Stage 3.

Detects topological shifts (EMERGE, MUTATE_SCHEMA, RETIRE) and generates
high-density prompt cards for the SLM Reasoner and AutoDream Memory Engine.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class SchemaAlert:
    """Alert notifying cognitive components of dynamic schema transition."""
    alert_type: str
    entity_id: str
    tick: int
    details: Dict[str, Any] = field(default_factory=dict)

    def render_card(self) -> str:
        if self.alert_type == "SCHEMA_EMERGE":
            etype = self.details.get("entity_type", "entity")
            props = " ".join(f"{k}={v}" for k, v in self.details.get("properties", {}).items())
            rels = " ".join(f"{k}:{v}" for k, v in self.details.get("relations", {}).items())
            rel_str = f" relations=[{rels}]" if rels else ""
            return f"[SCHEMA_ALERT: NEW ENTITY '{self.entity_id}' ({etype}) EMERGED at t={self.tick}: {props}{rel_str}]"

        if self.alert_type == "SCHEMA_MUTATE":
            mut_props = " ".join(f"{k}={v}" for k, v in self.details.get("mutated_properties", {}).items())
            mut_rels = " ".join(f"{k}:{v}" for k, v in self.details.get("mutated_relations", {}).items())
            return f"[SCHEMA_ALERT: ENTITY '{self.entity_id}' MUTATED at t={self.tick}: props=[{mut_props}] rels=[{mut_rels}]]"

        if self.alert_type == "SCHEMA_RETIRE":
            return f"[SCHEMA_ALERT: ENTITY '{self.entity_id}' DECOMMISSIONED/RETIRED at t={self.tick}]"

        return f"[SCHEMA_ALERT: {self.alert_type} on '{self.entity_id}' at t={self.tick}]"


class DiscrepancyMonitor:
    """Monitors real-time entity topologies and formats alerts."""

    def __init__(self) -> None:
        self.active_alerts: Dict[str, SchemaAlert] = {}
        self.alert_history: List[SchemaAlert] = []

    def ingest_schema_events(self, fired_events: List[Dict[str, Any]]) -> None:
        for ev in fired_events:
            atype = ev.get("type", "UNKNOWN")
            eid = ev.get("entity_id", "")
            tick = ev.get("tick", 0)

            alert = SchemaAlert(
                alert_type=atype,
                entity_id=eid,
                tick=tick,
                details=copy.deepcopy(ev),
            )
            key = f"{eid}:{atype}"
            self.active_alerts[key] = alert
            self.alert_history.append(alert)

            if atype == "SCHEMA_RETIRE":
                emerge_key = f"{eid}:SCHEMA_EMERGE"
                if emerge_key in self.active_alerts:
                    del self.active_alerts[emerge_key]

    def render_active_prompt_cards(self, max_cards: int = 3) -> str:
        if not self.active_alerts:
            return ""

        rendered = [alert.render_card() for alert in list(self.active_alerts.values())[-max_cards:]]
        return "\n".join(rendered)
