"""Dynamic Schema Registry for runtime entity emergence and structural mutation."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


@dataclass
class EntitySchema:
    """Schema definition for an entity type."""

    type_name: str
    allowed_properties: Set[str] = field(default_factory=set)
    required_properties: Set[str] = field(default_factory=set)


class DynamicSchemaRegistry:
    """Host registry tracking runtime entity lifecycles (EMERGE, MUTATE, RETIRE)."""

    def __init__(self):
        self.schemas: Dict[str, EntitySchema] = {}
        self.entities: Dict[str, Dict[str, Any]] = {}
        self.relations: Dict[str, Dict[str, Set[str]]] = {}  # source_id -> {rel_name -> {target_ids}}
        self.retired_entities: Set[str] = set()

    def register_entity_type(
        self,
        type_name: str,
        allowed_properties: Optional[List[str]] = None,
        required_properties: Optional[List[str]] = None,
    ) -> EntitySchema:
        """Registers or updates an entity type schema."""
        schema = EntitySchema(
            type_name=type_name,
            allowed_properties=set(allowed_properties or []),
            required_properties=set(required_properties or []),
        )
        self.schemas[type_name] = schema
        return schema

    def emerge_entity(
        self,
        entity_id: str,
        entity_type: str,
        initial_properties: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Emerges a new entity instance into the world state."""
        if entity_id in self.entities and entity_id not in self.retired_entities:
            raise ValueError(f"Entity '{entity_id}' already active in schema registry.")

        props = copy.deepcopy(initial_properties or {})
        schema = self.schemas.get(entity_type)
        if schema and schema.required_properties:
            missing = schema.required_properties - set(props.keys())
            if missing:
                raise ValueError(f"Cannot emerge '{entity_id}': missing required properties: {sorted(missing)}")

        self.retired_entities.discard(entity_id)
        entity_record = {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "version": 1,
            "properties": props,
            "is_active": True,
        }
        self.entities[entity_id] = entity_record
        if entity_id not in self.relations:
            self.relations[entity_id] = {}
        return copy.deepcopy(entity_record)

    def retire_entity(self, entity_id: str, reason: str = "") -> None:
        """Retires an entity from active existence."""
        if entity_id in self.entities:
            self.entities[entity_id]["is_active"] = False
            self.entities[entity_id]["retirement_reason"] = reason
            self.retired_entities.add(entity_id)

    def mutate_schema(
        self,
        entity_id: str,
        add_properties: Optional[Dict[str, Any]] = None,
        remove_properties: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Mutates properties of an active entity, bumping version."""
        if entity_id not in self.entities or entity_id in self.retired_entities:
            raise KeyError(f"Entity '{entity_id}' is not active.")

        entity = self.entities[entity_id]
        if add_properties:
            entity["properties"].update(add_properties)
        if remove_properties:
            for prop in remove_properties:
                entity["properties"].pop(prop, None)

        entity["version"] += 1
        return copy.deepcopy(entity)

    def add_relation(self, source_id: str, relation_name: str, target_id: str) -> None:
        """Binds a directed relational edge from source to target."""
        if source_id not in self.relations:
            self.relations[source_id] = {}
        if relation_name not in self.relations[source_id]:
            self.relations[source_id][relation_name] = set()
        self.relations[source_id][relation_name].add(target_id)

    def remove_relation(self, source_id: str, relation_name: str, target_id: str) -> None:
        """Removes a directed relational edge."""
        if source_id in self.relations and relation_name in self.relations[source_id]:
            self.relations[source_id][relation_name].discard(target_id)

    def get_relations(self, source_id: str) -> Dict[str, List[str]]:
        """Returns map of relation_name -> list of target entity IDs."""
        rel_map = self.relations.get(source_id, {})
        return {r: sorted(list(targets)) for r, targets in rel_map.items()}

    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a deep copy of an entity record if active."""
        if entity_id in self.entities and entity_id not in self.retired_entities:
            return copy.deepcopy(self.entities[entity_id])
        return None

    def get_active_entities(self) -> Dict[str, Dict[str, Any]]:
        """Returns deep copies of all currently active entities."""
        return {
            eid: copy.deepcopy(rec)
            for eid, rec in self.entities.items()
            if eid not in self.retired_entities and rec.get("is_active", True)
        }

    def is_active(self, entity_id: str) -> bool:
        """Returns True if the entity exists and is active."""
        return entity_id in self.entities and entity_id not in self.retired_entities
