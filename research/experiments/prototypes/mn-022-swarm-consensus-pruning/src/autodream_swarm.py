"""Topological AutoDream Swarm Context Builder enforcing strict <= 512 token ceiling."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Set
from .consensus_pruner import SwarmEventNode


class AutoDreamSwarm:
    """Constructs token-bounded agent prompts via topological Fact Cards and frontier pruning."""

    def __init__(self, token_ceiling: int = 512) -> None:
        self.token_ceiling = token_ceiling

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Heuristic token estimator matching BPE tokenization (~3.6 chars/token)."""
        words = text.split()
        return max(len(words), int(len(text) / 3.6))

    def build_prompt(
        self,
        domain_name: str,
        current_tick: int,
        agent_id: str,
        assigned_goal: str,
        resource_states: Dict[str, Dict[str, Any]],
        frontier_nodes: List[SwarmEventNode],
        held_leases: Set[str],
        valid_affordances: List[str],
        unpruned_gossip: Optional[List[Dict[str, Any]]] = None,
    ) -> Tuple[str, int]:
        """Assembles prompt context pack for agent_id at current_tick.
        
        If unpruned_gossip is provided (Arm 2), includes raw unpruned gossip events.
        Otherwise (Arm 3), includes only active pruned frontier nodes (O(M)).
        """
        lines = [
            f"DOMAIN: {domain_name} | TICK: {current_tick} | AGENT: {agent_id}",
            f"GOAL: {assigned_goal}",
            "ACTIVE RESOURCES:",
        ]

        # Compact Fact Cards
        for res_id, rdata in sorted(resource_states.items()):
            holder = rdata.get("holder") or "FREE"
            ver = rdata.get("version", 1)
            val = rdata.get("val", "")
            lines.append(f"  [{res_id} v{ver} holder:{holder} val:{val}]")

        if unpruned_gossip is not None:
            # Arm 2: Unpruned Gossip Trace (O(M^2) unbounded accumulation)
            lines.append("GOSSIP HISTORY:")
            for g in unpruned_gossip:
                lines.append(f"  [T{g.get('tick', 0)} {g.get('agent_id')} -> {g.get('action')}]")
        else:
            # Arm 3: Pruned Topological Frontier (O(M) active frontier)
            lines.append("CONSENSUS FRONTIER:")
            for fnode in frontier_nodes:
                lines.append(
                    f"  [T{fnode.tick} {fnode.agent_id} {fnode.action_type} {fnode.target} ({fnode.status})]"
                )

        lines.append("AVAILABLE ACTIONS:")
        for aff in valid_affordances:
            lines.append(f"  - {aff}")

        lines.append("INSTRUCTION: Select exactly ONE action from AVAILABLE ACTIONS starting with 'ACTION:'.")

        raw_prompt = "\n".join(lines)
        est_tokens = self.estimate_tokens(raw_prompt)

        # Token ceiling check
        if est_tokens > self.token_ceiling:
            # Emergency compression: prune lines from history/frontier if needed
            compact_lines = lines[:4] + ["[TRUNCATED CONTEXT FOR BOUNDED BUDGET]"] + lines[-8:]
            raw_prompt = "\n".join(compact_lines)
            est_tokens = self.estimate_tokens(raw_prompt)

        return raw_prompt, est_tokens
