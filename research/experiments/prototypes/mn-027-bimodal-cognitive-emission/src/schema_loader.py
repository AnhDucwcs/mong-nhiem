"""Generic Declarative Schema Loader & Invariant Synthesizer.

Parses domain-agnostic YAML/JSON configuration files, synthesizing Host invariants,
preconditions, continuous state traits, and entity definitions into active runtime memory.
100% Python Standard Library. Zero external dependencies.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class DeclarativeEntityDef:
    """Definition of a world entity."""

    name: str
    initial_properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DeclarativeInvariantDef:
    """Definition of an invariant or redline circuit breaker rule."""

    id: str
    condition: str  # e.g., "temperature >= 450" or "energy <= 10"
    target_metric: str
    threshold: float
    comparator: str
    trigger_action: str


@dataclass
class DeclarativePreconditionDef:
    """Definition of a semantic action precondition."""

    action_verb: str
    required_states: Dict[str, Any] = field(default_factory=dict)
    prohibited_states: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DeclarativeContinuousTraitDef:
    """Definition of a continuous parameter with real-time decay/growth."""

    name: str
    initial_value: float
    min_val: float = 0.0
    max_val: float = 100.0
    rate_per_sec: float = 0.0
    is_decay: bool = True


@dataclass
class CompiledWorldSchema:
    """Compiled schema ready for Host runtime binding."""

    schema_name: str
    entities: List[DeclarativeEntityDef] = field(default_factory=list)
    invariants: List[DeclarativeInvariantDef] = field(default_factory=list)
    preconditions: List[DeclarativePreconditionDef] = field(default_factory=list)
    continuous_traits: List[DeclarativeContinuousTraitDef] = field(default_factory=list)


class DeclarativeSchemaLoader:
    """Parses JSON or YAML subset schema files into active Host structures."""

    @classmethod
    def load_from_dict(cls, data: Dict[str, Any]) -> CompiledWorldSchema:
        """Compiles a dictionary specification into a CompiledWorldSchema."""
        schema_name = data.get("schema_name", "unnamed_schema")

        entities: List[DeclarativeEntityDef] = []
        for ent in data.get("entities", []):
            entities.append(
                DeclarativeEntityDef(
                    name=ent["name"],
                    initial_properties=dict(ent.get("properties", {})),
                )
            )

        invariants: List[DeclarativeInvariantDef] = []
        for inv in data.get("invariants", []):
            # Parse condition e.g. "temperature >= 450"
            cond = inv.get("condition", "")
            target_metric = inv.get("target_metric", "")
            threshold = float(inv.get("threshold", 0.0))
            comparator = inv.get("comparator", ">=")

            if cond and not target_metric:
                m = re.match(r"^\s*([A-Za-z0-9_]+)\s*(<=|>=|<|>|==|!=)\s*([0-9\.\-]+)\s*$", cond)
                if m:
                    target_metric = m.group(1)
                    comparator = m.group(2)
                    threshold = float(m.group(3))

            invariants.append(
                DeclarativeInvariantDef(
                    id=inv.get("id", f"inv_{len(invariants)}"),
                    condition=cond or f"{target_metric} {comparator} {threshold}",
                    target_metric=target_metric,
                    threshold=threshold,
                    comparator=comparator,
                    trigger_action=inv.get("trigger_action", "TRIGGER_SCRAM"),
                )
            )

        preconditions: List[DeclarativePreconditionDef] = []
        for prec in data.get("preconditions", []):
            preconditions.append(
                DeclarativePreconditionDef(
                    action_verb=prec["action_verb"],
                    required_states=dict(prec.get("required_states", {})),
                    prohibited_states=dict(prec.get("prohibited_states", {})),
                )
            )

        continuous_traits: List[DeclarativeContinuousTraitDef] = []
        for trait in data.get("continuous_traits", []):
            continuous_traits.append(
                DeclarativeContinuousTraitDef(
                    name=trait["name"],
                    initial_value=float(trait.get("initial_value", 100.0)),
                    min_val=float(trait.get("min_val", 0.0)),
                    max_val=float(trait.get("max_val", 100.0)),
                    rate_per_sec=float(trait.get("rate_per_sec", 0.0)),
                    is_decay=bool(trait.get("is_decay", True)),
                )
            )

        return CompiledWorldSchema(
            schema_name=schema_name,
            entities=entities,
            invariants=invariants,
            preconditions=preconditions,
            continuous_traits=continuous_traits,
        )

    @classmethod
    def load_from_file(cls, filepath: str) -> CompiledWorldSchema:
        """Loads and parses a JSON or simple YAML schema file."""
        with open(filepath, "r", encoding="utf-8") as fp:
            content = fp.read().strip()

        # Try JSON first
        if content.startswith("{"):
            data = json.loads(content)
            return cls.load_from_dict(data)

        # Basic native YAML subset parser for simple key-values and lists
        # If PyYAML is available, use it; otherwise parse native subset
        try:
            import yaml
            data = yaml.safe_load(content)
            return cls.load_from_dict(data)
        except ImportError:
            # Fallback parser for JSON or basic structured YAML
            data = cls._parse_simple_yaml(content)
            return cls.load_from_dict(data)

    @classmethod
    def _parse_simple_yaml(cls, text: str) -> Dict[str, Any]:
        """Minimal fallback parser for standard JSON-convertible structures."""
        # Convert simple YAML into JSON representation if simple
        # For full robust usage, JSON format is supported natively
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Parse basic dictionary
        result: Dict[str, Any] = {}
        current_list_key = None
        for line in text.splitlines():
            line_str = line.strip()
            if not line_str or line_str.startswith("#"):
                continue
            if ":" in line_str and not line_str.startswith("-"):
                k, v = line_str.split(":", 1)
                k = k.strip()
                v = v.strip()
                if v:
                    result[k] = v
                else:
                    result[k] = []
                    current_list_key = k
            elif line_str.startswith("-") and current_list_key:
                val = line_str[1:].strip()
                result[current_list_key].append(val)

        return result
