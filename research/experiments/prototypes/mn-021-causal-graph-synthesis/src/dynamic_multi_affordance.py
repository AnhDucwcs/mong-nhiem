"""Dynamic Multi-Agent Affordance GBNF Compiler for MN-021.

Dynamically compiles Context-Free Grammar (GBNF) logit masks for llama-server,
pruning actions targeting leased or contested entities, and steering models toward
valid dispatch, autonomous probing, or epistemic cross-inspection.
"""
from __future__ import annotations

from typing import List, Optional, Set


class DynamicMultiAffordanceCompiler:
    """Compiles state-dependent GBNF grammars with concurrency and epistemic masks."""

    @staticmethod
    def compile_grammar(
        valid_dispatch_targets: List[str],
        valid_probe_targets: List[str],
        contested_entities: Set[str],
        peer_leased_entities: Set[str],
        allow_resolve: bool = False,
    ) -> str:
        """Compile GBNF grammar string masking out unavailable actions and targets."""
        # 1. Filter dispatch targets: exclude leased by peer AND contested entities
        allowed_dispatch = [
            t for t in valid_dispatch_targets
            if t not in peer_leased_entities and t not in contested_entities
        ]

        # 2. Probe targets: can probe unleased entities
        allowed_probe = [
            t for t in valid_probe_targets
            if t not in peer_leased_entities
        ]

        # 3. Cross-inspect targets: specifically for contested entities
        allowed_cross_inspect = [
            t for t in contested_entities
            if t not in peer_leased_entities
        ]

        action_rules = []

        if allowed_dispatch:
            targets_alt = " | ".join(f'"{t}"' for t in allowed_dispatch)
            action_rules.append(f'action-dispatch ::= "ACTION: DISPATCH " ({targets_alt}) "\\n"')

        if allowed_probe:
            probes_alt = " | ".join(f'"{t}"' for t in allowed_probe)
            action_rules.append(f'action-probe ::= "ACTION: PROBE " ({probes_alt}) "\\n"')

        if allowed_cross_inspect:
            cross_alt = " | ".join(f'"{t}"' for t in allowed_cross_inspect)
            action_rules.append(f'action-cross ::= "ACTION: CROSS_INSPECT " ({cross_alt}) "\\n"')

        if allow_resolve:
            action_rules.append('action-resolve ::= "ACTION: RESOLVE\\n"')

        # Build root alternation
        root_choices = []
        if allowed_dispatch:
            root_choices.append("action-dispatch")
        if allowed_probe:
            root_choices.append("action-probe")
        if allowed_cross_inspect:
            root_choices.append("action-cross")
        if allow_resolve:
            root_choices.append("action-resolve")

        if not root_choices:
            # Fallback idle rule to prevent infinite generation
            return 'root ::= "ACTION: IDLE\\n"\n'

        root_rule = "root ::= " + " | ".join(root_choices) + "\n"
        grammar_body = "\n".join(action_rules) + "\n"
        return root_rule + grammar_body
