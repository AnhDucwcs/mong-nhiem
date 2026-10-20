"""Generic Declarative Schema Loader & Invariant Synthesizer.

Parses domain-agnostic YAML/JSON configuration files, synthesizing Host invariants,
preconditions, continuous state traits, and entity definitions into active runtime memory.
100% Python Standard Library. Zero external dependencies.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DeclarativeEntityDef:
    """Definition of a world entity."""

    name: str
    initial_properties: dict[str, Any] = field(default_factory=dict)


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
    required_states: dict[str, Any] = field(default_factory=dict)
    prohibited_states: dict[str, Any] = field(default_factory=dict)


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
    entities: list[DeclarativeEntityDef] = field(default_factory=list)
    invariants: list[DeclarativeInvariantDef] = field(default_factory=list)
    preconditions: list[DeclarativePreconditionDef] = field(default_factory=list)
    continuous_traits: list[DeclarativeContinuousTraitDef] = field(default_factory=list)


class DeclarativeSchemaLoader:
    """Parses JSON or YAML subset schema files into active Host structures."""

    @classmethod
    def load_from_dict(cls, data: dict[str, Any]) -> CompiledWorldSchema:
        """Compiles a dictionary specification into a CompiledWorldSchema."""
        schema_name = data.get("schema_name", "unnamed_schema")

        entities: list[DeclarativeEntityDef] = []
        for ent in data.get("entities", []):
            entities.append(
                DeclarativeEntityDef(
                    name=ent["name"],
                    initial_properties=dict(ent.get("properties", {})),
                )
            )

        invariants: list[DeclarativeInvariantDef] = []
        for inv in data.get("invariants", []):
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
                    condition=cond,
                    target_metric=target_metric,
                    threshold=threshold,
                    comparator=comparator,
                    trigger_action=inv.get("trigger_action", "SCRAM"),
                )
            )

        preconditions: list[DeclarativePreconditionDef] = []
        for pre in data.get("preconditions", []):
            preconditions.append(
                DeclarativePreconditionDef(
                    action_verb=pre["action_verb"],
                    required_states=dict(pre.get("required_states", {})),
                    prohibited_states=dict(pre.get("prohibited_states", {})),
                )
            )

        continuous_traits: list[DeclarativeContinuousTraitDef] = []
        for tr in data.get("continuous_traits", []):
            continuous_traits.append(
                DeclarativeContinuousTraitDef(
                    name=tr["name"],
                    initial_value=float(tr.get("initial_value", 50.0)),
                    min_val=float(tr.get("min_val", 0.0)),
                    max_val=float(tr.get("max_val", 100.0)),
                    rate_per_sec=float(tr.get("rate_per_sec", 0.0)),
                    is_decay=tr.get("is_decay", True),
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
    def load_from_json_string(cls, json_str: str) -> CompiledWorldSchema:
        """Parses a raw JSON schema string."""
        data = json.loads(json_str)
        return cls.load_from_dict(data)

    @classmethod
    def load_from_file(cls, file_path: str) -> CompiledWorldSchema:
        """Loads a schema from JSON or lightweight YAML subset file."""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        if file_path.endswith(".json") or content.strip().startswith("{"):
            return cls.load_from_json_string(content)

        data = cls._parse_lightweight_yaml(content)
        return cls.load_from_dict(data)

    @classmethod
    def _parse_lightweight_yaml(cls, text: str) -> dict[str, Any]:
        """Simple pure standard library parser for key-value nested YAML subsets."""
        try:
            return json.loads(text)
        except (json.JSONDecodeError, ValueError):
            pass

        data: dict[str, Any] = {}
        current_section = None
        current_list: list[Any] | None = None

        for line in text.splitlines():
            line_str = line.strip()
            if not line_str or line_str.startswith("#"):
                continue

            if ":" in line_str and not line_str.startswith("-"):
                parts = line_str.split(":", 1)
                k = parts[0].strip()
                v = parts[1].strip()
                if not v:
                    current_section = k
                    current_list = []
                    data[current_section] = current_list
                else:
                    if v.isdigit():
                        data[k] = int(v)
                    else:
                        try:
                            data[k] = float(v)
                        except ValueError:
                            data[k] = v.strip("\"'")
            elif line_str.startswith("- ") and current_section:
                item_val = line_str[2:].strip()
                if current_list is not None:
                    current_list.append(item_val)

        return data
