"""Continuous State Decay Engine & Session State Persistence.

Models linear and parametric continuous state progression over elapsed time.
Triggers threshold invariant events and serializes atomic session state to disk.
100% Python Standard Library. Zero external dependencies.
"""

from __future__ import annotations

import json
import os
import tempfile
import time
from dataclasses import dataclass
from typing import Any


@dataclass
class ContinuousVariable:
    """Represents a continuous numerical entity property governed by decay or growth."""

    name: str
    current_value: float
    min_val: float = 0.0
    max_val: float = 100.0
    rate_per_unit_time: float = 0.0  # Positive for decay, negative for accumulation
    is_decay: bool = True  # True if value drops over time, False if it increases


@dataclass
class ThresholdTrigger:
    """Condition that fires an event when a continuous variable crosses a bound."""

    variable_name: str
    threshold: float
    comparison: str  # "<=", ">=", "<", ">"
    trigger_action: str
    fired: bool = False


class ContinuousStateEngine:
    """Manages continuous state updates, threshold checks, and atomic disk persistence."""

    def __init__(self) -> None:
        self.variables: dict[str, ContinuousVariable] = {}
        self.triggers: list[ThresholdTrigger] = []
        self.last_update_timestamp: float = time.time()

    def register_variable(
        self,
        name: str,
        initial_value: float,
        min_val: float = 0.0,
        max_val: float | None = None,
        rate_per_unit: float = 0.0,
        is_decay: bool = True,
    ) -> None:
        """Registers a new continuous variable."""
        val = float(initial_value)
        if max_val is not None:
            effective_max = float(max_val)
        else:
            effective_max = max(100.0, val * 2.0 if val > 0 else 100.0)

        self.variables[name] = ContinuousVariable(
            name=name,
            current_value=val,
            min_val=float(min_val),
            max_val=effective_max,
            rate_per_unit_time=float(rate_per_unit),
            is_decay=is_decay,
        )

    def register_trigger(
        self,
        variable_name: str,
        threshold: float,
        comparison: str,
        trigger_action: str,
    ) -> None:
        """Registers a threshold boundary trigger."""
        self.triggers.append(
            ThresholdTrigger(
                variable_name=variable_name,
                threshold=float(threshold),
                comparison=comparison,
                trigger_action=trigger_action,
                fired=False,
            )
        )

    def step_time(self, delta_time: float) -> list[str]:
        """Advances time by delta_time, updates variables, and returns fired trigger actions."""
        fired_actions: list[str] = []

        for var in self.variables.values():
            if var.rate_per_unit_time > 0:
                change = var.rate_per_unit_time * delta_time
                if var.is_decay:
                    var.current_value = max(var.min_val, var.current_value - change)
                else:
                    var.current_value = min(var.max_val, var.current_value + change)
                var.current_value = round(var.current_value, 2)

        for trig in self.triggers:
            if trig.variable_name not in self.variables:
                continue
            val = self.variables[trig.variable_name].current_value
            cond_met = False

            if trig.comparison == "<=":
                cond_met = val <= trig.threshold
            elif trig.comparison == ">=":
                cond_met = val >= trig.threshold
            elif trig.comparison == "<":
                cond_met = val < trig.threshold
            elif trig.comparison == ">":
                cond_met = val > trig.threshold

            if cond_met and not trig.fired:
                trig.fired = True
                fired_actions.append(trig.trigger_action)
            elif not cond_met and trig.fired:
                # Reset trigger if condition ceases to hold
                trig.fired = False

        self.last_update_timestamp = time.time()
        return fired_actions

    def set_variable(self, name: str, value: float) -> None:
        """Manually overrides or updates a continuous variable."""
        if name in self.variables:
            var = self.variables[name]
            var.current_value = round(max(var.min_val, min(var.max_val, float(value))), 2)

    def get_variable(self, name: str) -> float | None:
        """Returns the current value of a continuous variable."""
        if name in self.variables:
            return self.variables[name].current_value
        return None

    def export_state_dict(self) -> dict[str, Any]:
        """Returns a JSON-serializable snapshot of continuous state."""
        return {
            "timestamp": self.last_update_timestamp,
            "variables": {
                name: {
                    "value": var.current_value,
                    "min": var.min_val,
                    "max": var.max_val,
                    "rate": var.rate_per_unit_time,
                    "is_decay": var.is_decay,
                }
                for name, var in self.variables.items()
            },
            "triggers": [
                {
                    "var": t.variable_name,
                    "thresh": t.threshold,
                    "comp": t.comparison,
                    "action": t.trigger_action,
                    "fired": t.fired,
                }
                for t in self.triggers
            ],
        }

    def import_state_dict(self, data: dict[str, Any]) -> None:
        """Restores continuous state from a snapshot dictionary."""
        self.last_update_timestamp = data.get("timestamp", time.time())
        vars_data = data.get("variables", {})
        self.variables.clear()
        for name, info in vars_data.items():
            self.variables[name] = ContinuousVariable(
                name=name,
                current_value=float(info["value"]),
                min_val=float(info.get("min", 0.0)),
                max_val=float(info.get("max", 100.0)),
                rate_per_unit_time=float(info.get("rate", 0.0)),
                is_decay=info.get("is_decay", True),
            )

        trigs_data = data.get("triggers", [])
        self.triggers.clear()
        for t in trigs_data:
            self.triggers.append(
                ThresholdTrigger(
                    variable_name=t["var"],
                    threshold=float(t["thresh"]),
                    comparison=t["comp"],
                    trigger_action=t["action"],
                    fired=t.get("fired", False),
                )
            )

    def save_to_disk_atomic(self, file_path: str) -> None:
        """Atomically saves state to disk using a temporary file and replace."""
        target_dir = os.path.dirname(os.path.abspath(file_path))
        os.makedirs(target_dir, exist_ok=True)

        data = self.export_state_dict()
        with tempfile.NamedTemporaryFile("w", dir=target_dir, delete=False, encoding="utf-8") as tf:
            json.dump(data, tf, indent=2)
            temp_name = tf.name

        os.replace(temp_name, file_path)

    def load_from_disk(self, file_path: str) -> bool:
        """Loads state from disk if file exists."""
        if not os.path.exists(file_path):
            return False
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.import_state_dict(data)
        return True
