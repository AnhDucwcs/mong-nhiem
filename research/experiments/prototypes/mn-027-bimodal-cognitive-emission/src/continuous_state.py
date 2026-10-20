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
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple


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
        self.variables: Dict[str, ContinuousVariable] = {}
        self.triggers: List[ThresholdTrigger] = []
        self.last_update_timestamp: float = time.time()

    def register_variable(
        self,
        name: str,
        initial_value: float,
        min_val: float = 0.0,
        max_val: float = 100.0,
        rate_per_unit: float = 0.0,
        is_decay: bool = True,
    ) -> None:
        """Registers a new continuous variable."""
        self.variables[name] = ContinuousVariable(
            name=name,
            current_value=float(initial_value),
            min_val=float(min_val),
            max_val=float(max_val),
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

    def step_time(self, delta_time: float) -> List[str]:
        """Advances time by delta_time, updates variables, and returns fired trigger actions."""
        fired_actions: List[str] = []

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
            condition_met = False
            if trig.comparison == "<=" and val <= trig.threshold:
                condition_met = True
            elif trig.comparison == "<" and val < trig.threshold:
                condition_met = True
            elif trig.comparison == ">=" and val >= trig.threshold:
                condition_met = True
            elif trig.comparison == ">" and val > trig.threshold:
                condition_met = True

            if condition_met and not trig.fired:
                trig.fired = True
                fired_actions.append(trig.trigger_action)
            elif not condition_met:
                trig.fired = False  # Reset trigger if value recovered

        self.last_update_timestamp = time.time()
        return fired_actions

    def mutate_variable(self, name: str, delta: float) -> float:
        """Directly modifies a continuous variable by delta (e.g. user feed/recharge)."""
        if name not in self.variables:
            raise KeyError(f"Unknown continuous variable: {name}")
        var = self.variables[name]
        var.current_value = max(var.min_val, min(var.max_val, var.current_value + delta))
        var.current_value = round(var.current_value, 2)
        return var.current_value

    def format_fact_card(self) -> str:
        """Formats active continuous variables into a compact state fact card (<= 35 tokens)."""
        tokens = [f"{k}:{v.current_value:.1f}" for k, v in sorted(self.variables.items())]
        return f"[TRAITS {' '.join(tokens)}]"

    def save_to_disk(self, filepath: str) -> None:
        """Atomically persists session state to JSON on disk."""
        data = {
            "timestamp": time.time(),
            "variables": {
                k: {
                    "current_value": v.current_value,
                    "min_val": v.min_val,
                    "max_val": v.max_val,
                    "rate_per_unit_time": v.rate_per_unit_time,
                    "is_decay": v.is_decay,
                }
                for k, v in self.variables.items()
            },
        }

        dirname = os.path.dirname(filepath) or "."
        os.makedirs(dirname, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(dir=dirname, suffix=".tmp")
        try:
            with open(fd, "w", encoding="utf-8") as fp:
                json.dump(data, fp, indent=2)
            if os.path.exists(filepath):
                os.replace(tmp_path, filepath)
            else:
                os.rename(tmp_path, filepath)
        except Exception:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

    def load_from_disk(self, filepath: str, apply_elapsed_decay: bool = True) -> float:
        """Loads state from disk and optionally applies decay for elapsed wall-clock time.

        Returns:
            Elapsed seconds since previous session shutdown.
        """
        if not os.path.exists(filepath):
            return 0.0

        with open(filepath, "r", encoding="utf-8") as fp:
            data = json.load(fp)

        saved_time = data.get("timestamp", time.time())
        elapsed = max(0.0, time.time() - saved_time)

        for k, v in data.get("variables", {}).items():
            self.register_variable(
                name=k,
                initial_value=v["current_value"],
                min_val=v["min_val"],
                max_val=v["max_val"],
                rate_per_unit=v["rate_per_unit_time"],
                is_decay=v["is_decay"],
            )

        if apply_elapsed_decay and elapsed > 0.0:
            self.step_time(elapsed)

        return elapsed
