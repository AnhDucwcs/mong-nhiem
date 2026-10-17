"""Epistemic observation masking and prompt leakage auditing for MN-024.

Strictly enforces observation boundaries:
- Public entities visible to all agents.
- Private entities visible only to authorized observers.
- Private secrets discoverable only through legitimate in-world actions.
- Audits prompts for Clause M3 epistemic leakage.
"""

from __future__ import annotations

import copy
import re
from typing import Any, Dict, List, Optional, Set


class EpistemicMaskEngine:
    """Manages subjective visibility horizons and audits prompt token leakage."""

    def __init__(
        self,
        agent_ids: List[str],
        public_entities: Set[str],
        agent_initial_visibility: Dict[str, Set[str]],
        private_secrets: Dict[str, Any],
    ) -> None:
        self.agent_ids = agent_ids
        self.public_entities = set(public_entities)
        self.agent_visibility = {
            aid: set(agent_initial_visibility.get(aid, set())) | set(public_entities)
            for aid in agent_ids
        }
        self.private_secrets = dict(private_secrets)
        self.known_secrets: Dict[str, Set[str]] = {aid: set() for aid in agent_ids}

    def project_subjective_view(
        self,
        agent_id: str,
        world_entities: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Dict[str, Any]]:
        """Filters the global world state down to the agent's legitimate observation mask."""
        visible_set = self.agent_visibility.get(agent_id, self.public_entities)
        subjective_view: Dict[str, Dict[str, Any]] = {}

        for ent_name, ent_state in world_entities.items():
            if ent_name in visible_set:
                ent_copy = copy.deepcopy(ent_state)
                # Strip private secrets unless agent legitimately discovered them
                for secret_key in self.private_secrets:
                    if secret_key in ent_copy:
                        if secret_key not in self.known_secrets[agent_id]:
                            ent_copy[secret_key] = "<REDACTED_SECRET>"
                subjective_view[ent_name] = ent_copy

        return subjective_view

    def grant_visibility(self, agent_id: str, entity_name: str) -> None:
        """Expands agent visibility horizon upon exploring a new physical subsystem."""
        if agent_id in self.agent_visibility:
            self.agent_visibility[agent_id].add(entity_name)

    def grant_secret(self, agent_id: str, secret_key: str) -> None:
        """Records legitimate causal discovery of a private secret by an agent."""
        if agent_id in self.known_secrets:
            self.known_secrets[agent_id].add(secret_key)

    def audit_leakage(self, agent_id: str, prompt_text: str) -> float:
        """Audits prompt buffer for Clause M3: Epistemic Information Leakage.

        Returns 1.0 if any unauthorized secret appears verbatim in prompt, 0.0 otherwise.
        """
        for secret_key, secret_val in self.private_secrets.items():
            if secret_key not in self.known_secrets[agent_id]:
                # If secret is serialized directly into prompt
                if str(secret_val) in prompt_text:
                    return 1.0
        return 0.0
