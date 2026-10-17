"""Epistemic observation masking and information horizon enforcement.

Guarantees Clause M3: Epistemic Information Leakage Score == 0.0.
Prevents unobserved private world state or hidden secrets from leaking into unauthorized agent prompts.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Set


class EpistemicMaskEngine:
    """Manages subjective perception boundaries and information horizon invariants."""

    def __init__(
        self,
        agent_ids: List[str],
        public_entities: Optional[Set[str]] = None,
        agent_initial_visibility: Optional[Dict[str, Set[str]]] = None,
        private_secrets: Optional[Dict[str, str]] = None,
    ) -> None:
        self.agent_ids = agent_ids
        self.public_entities: Set[str] = set(public_entities or [])
        self.agent_visibility: Dict[str, Set[str]] = {
            aid: set(self.public_entities) for aid in agent_ids
        }
        if agent_initial_visibility:
            for aid, entities in agent_initial_visibility.items():
                if aid in self.agent_visibility:
                    self.agent_visibility[aid].update(entities)

        # secret_name -> secret_value
        self.private_secrets: Dict[str, str] = dict(private_secrets or {})
        # agent_id -> set of secret_names legitimately observed/known
        self.known_secrets: Dict[str, Set[str]] = {aid: set() for aid in agent_ids}

    def grant_visibility(self, agent_id: str, entity_id: str) -> None:
        """Expands agent's spatial observation mask upon physical entry or sensor activation."""
        if agent_id in self.agent_visibility:
            self.agent_visibility[agent_id].add(entity_id)

    def grant_secret(self, agent_id: str, secret_name: str) -> None:
        """Legitimately reveals a secret to an agent following an explicit in-world discovery action."""
        if agent_id in self.known_secrets and secret_name in self.private_secrets:
            self.known_secrets[agent_id].add(secret_name)

    def filter_state_for_agent(
        self,
        agent_id: str,
        world_entities: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Dict[str, Any]]:
        """Projects ground-truth world state onto the subjective epistemic horizon of agent_id.
        
        Entities outside the agent's observation mask are completely hidden.
        Hidden secret properties are masked unless legitimately granted.
        """
        allowed_entities = self.agent_visibility.get(agent_id, self.public_entities)
        subjective_view: Dict[str, Dict[str, Any]] = {}

        for eid, edata in world_entities.items():
            if eid in allowed_entities:
                filtered_props = dict(edata)
                # Mask secret properties if agent does not know them
                for sname, sval in self.private_secrets.items():
                    if sname in filtered_props and sname not in self.known_secrets.get(agent_id, set()):
                        filtered_props[sname] = "<MASKED_UNKNOWN>"
                subjective_view[eid] = filtered_props

        return subjective_view

    def audit_leakage(self, agent_id: str, prompt_text: str) -> float:
        """Audits prompt text against all unobserved secrets for agent_id.
        
        Returns:
            0.0 if clean (zero leakage).
            Count of leaked private secret tokens if contaminated.
        """
        leaks = 0.0
        known = self.known_secrets.get(agent_id, set())

        for sname, sval in self.private_secrets.items():
            if sname not in known:
                # If the exact secret value or secret token appears in prompt, flag as breach
                if str(sval).lower() in prompt_text.lower():
                    leaks += 1.0

        return leaks
