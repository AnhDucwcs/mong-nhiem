"""Continuous physical environmental entropy decay engine for MN-024.

Simulates passive environmental degradation (heat accumulation, pressure dissipation, frequency drift)
that occurs across discrete long-horizon ticks unless actively counteracted by agent maintenance actions.
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List, Set, Tuple


class EnvironmentalEntropyEngine:
    """Simulates passive thermodynamic and electrical decay across discrete ticks."""

    def __init__(
        self,
        decay_rates: Dict[str, Dict[str, float]],
        safe_bounds: Dict[str, Dict[str, Tuple[float, float]]],
        warning_thresholds: Dict[str, Dict[str, float]],
    ) -> None:
        """
        Args:
            decay_rates: Entity -> Attribute -> Delta per tick (positive or negative).
            safe_bounds: Entity -> Attribute -> (min_val, max_val).
            warning_thresholds: Entity -> Attribute -> threshold triggering alarm in subjective prompt.
        """
        self.decay_rates = decay_rates
        self.safe_bounds = safe_bounds
        self.warning_thresholds = warning_thresholds
        self.total_breaches_detected = 0

    def apply_tick_decay(
        self,
        entities: Dict[str, Dict[str, Any]],
        mitigated_entities: Set[str],
    ) -> Tuple[bool, List[str]]:
        """Applies passive decay to entities unless actively mitigated in the current tick.

        Returns:
            Tuple[is_safe, list_of_breach_descriptions]
        """
        breaches: List[str] = []

        for ent_name, prop_decays in self.decay_rates.items():
            if ent_name not in entities:
                continue
            if ent_name in mitigated_entities:
                continue

            for prop, delta in prop_decays.items():
                if prop not in entities[ent_name]:
                    continue

                curr_val = float(entities[ent_name][prop])
                new_val = curr_val + delta
                entities[ent_name][prop] = round(new_val, 2)

                # Check safe bounds
                if ent_name in self.safe_bounds and prop in self.safe_bounds[ent_name]:
                    min_val, max_val = self.safe_bounds[ent_name][prop]
                    if new_val < min_val or new_val > max_val:
                        breach_desc = f"PHYSICAL_INVARIANT_BREACH: {ent_name}.{prop}={new_val:.2f} outside [{min_val}, {max_val}]"
                        breaches.append(breach_desc)
                        self.total_breaches_detected += 1

        return len(breaches) == 0, breaches

    def get_active_warnings(self, entities: Dict[str, Dict[str, Any]]) -> List[str]:
        """Returns subjective alarm notices for entities nearing dangerous thresholds."""
        warnings: List[str] = []
        for ent_name, prop_thresh in self.warning_thresholds.items():
            if ent_name not in entities:
                continue
            for prop, thresh in prop_thresh.items():
                if prop not in entities[ent_name]:
                    continue
                val = float(entities[ent_name][prop])
                # Check if threshold crossed
                rate = self.decay_rates.get(ent_name, {}).get(prop, 0.0)
                if rate > 0 and val >= thresh:
                    warnings.append(f"ALARM: {ent_name}.{prop} elevated to {val:.2f} (warning threshold {thresh:.2f})")
                elif rate < 0 and val <= thresh:
                    warnings.append(f"ALARM: {ent_name}.{prop} depleted to {val:.2f} (warning threshold {thresh:.2f})")
        return warnings
