"""Dynamic GBNF Context-Free Grammar Compiler for MN-015.

Compiles state-conditioned Affordances objects into exact, minimal Context-Free Grammars
for engine-level logit masking in llama.cpp in < 0.1 ms CPU time.
"""
from __future__ import annotations

from typing import List
from protocol import Affordances

# Static fallback grammar if affordances are empty
STATIC_FALLBACK_GBNF = """root ::= action ("\\n" | "")
action ::= "ACTION: " ( read-action | inspect-action | dispatch-action | resolve-action )
read-action ::= "READ " identifier
inspect-action ::= "INSPECT " identifier "." identifier
dispatch-action ::= "DISPATCH " identifier " " payload
resolve-action ::= "RESOLVE " payload
identifier ::= [a-zA-Z0-9_]+
payload ::= [^\\r\\n]+
"""


def compile_dynamic_gbnf(affordances: Affordances) -> str:
    """Compile active affordances into a minimal, strictly conforming GBNF grammar.
    
    Args:
        affordances: Affordances dataclass containing active reads, inspects, dispatches, resolves.
        
    Returns:
        GBNF grammar string enforcing only the active action candidates.
    """
    if affordances.is_empty():
        return STATIC_FALLBACK_GBNF

    action_branches: List[str] = []
    sub_rules: List[str] = []

    # 1. READ branch
    if affordances.reads:
        action_branches.append("read-action")
        literals = " | ".join(f'"{_escape_gbnf(r)}"' for r in affordances.reads)
        sub_rules.append(f'read-action ::= "READ " valid-read-target\nvalid-read-target ::= {literals}')

    # 2. INSPECT branch
    if affordances.inspects:
        action_branches.append("inspect-action")
        literals = " | ".join(f'"{_escape_gbnf(i)}"' for i in affordances.inspects)
        sub_rules.append(f'inspect-action ::= "INSPECT " valid-inspect-target\nvalid-inspect-target ::= {literals}')

    # 3. DISPATCH branch
    if affordances.dispatches:
        action_branches.append("dispatch-action")
        dispatch_calls = []
        for tool, payload in affordances.dispatches:
            full_call = f"{tool} {payload}".strip()
            dispatch_calls.append(f'"{_escape_gbnf(full_call)}"')
        literals = " | ".join(dispatch_calls)
        sub_rules.append(f'dispatch-action ::= "DISPATCH " valid-dispatch-call\nvalid-dispatch-call ::= {literals}')

    # 4. RESOLVE branch
    if affordances.resolves:
        action_branches.append("resolve-action")
        literals = " | ".join(f'"{_escape_gbnf(r)}"' for r in affordances.resolves)
        sub_rules.append(f'resolve-action ::= "RESOLVE " valid-resolve-target\nvalid-resolve-target ::= {literals}')

    if not action_branches:
        return STATIC_FALLBACK_GBNF

    if len(action_branches) == 1:
        action_rule = f'action ::= "ACTION: " {action_branches[0]}'
    else:
        action_rule = f'action ::= "ACTION: " ( {" | ".join(action_branches)} )'

    rules = [
        'root ::= action ("\\n" | "")',
        action_rule,
    ] + sub_rules

    return "\n\n".join(rules) + "\n"


def _escape_gbnf(s: str) -> str:
    """Escape special characters inside GBNF string literals."""
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '')
