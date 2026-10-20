"""Bimodal Cognitive Emission Protocol & Grammar Compiler.

Constrains small language models (<4B) to emit single-pass operational actions
alongside triadic communicative acts (INFORM, QUERY, EXPRESS) under GBNF grammar.
100% Python Standard Library. Zero external dependencies.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class CommClass(str, Enum):
    """Orthogonal Triadic Communicative Taxonomy based on Host State Effect."""

    INFORM = "INFORM"  # Unidirectional report/explanation; Host continues nominal loop
    QUERY = "QUERY"  # Bidirectional solicitation; Host halts into SUPERVISED_STANDBY
    EXPRESS = "EXPRESS"  # Unconstrained socio-emotional persona expression (T=0.5)


@dataclass(frozen=True)
class BimodalEmission:
    """Structured representation of a dual-channel operational/communicative output."""

    action_verb: str
    action_params: Dict[str, str] = field(default_factory=dict)
    comm_class: CommClass = CommClass.INFORM
    comm_message: str = ""
    raw_text: str = ""
    valid: bool = True
    parse_error: Optional[str] = None

    @property
    def full_action_str(self) -> str:
        """Reconstruct canonical ACTION string."""
        if not self.action_params:
            return self.action_verb
        params = " ".join(f"{k}={v}" for k, v in self.action_params.items())
        return f"{self.action_verb} {params}"


class BimodalParser:
    """Deterministic, sub-millisecond parser for bimodal emission format."""

    _ACTION_RE = re.compile(r"^ACTION:\s*([A-Za-z_]+)(?:\s+(.*?))?$", re.MULTILINE)
    _COMM_RE = re.compile(
        r"^COMMUNICATE\s*\[\s*(INFORM|QUERY|EXPRESS)\s*\]\s*:\s*[\"']?(.*?)[\"']?$",
        re.MULTILINE,
    )

    @classmethod
    def parse(cls, text: str) -> BimodalEmission:
        """Parses a bimodal completion into structured action and communicative act."""
        if not text:
            return BimodalEmission(
                action_verb="ABSTAIN",
                valid=False,
                parse_error="Empty completion text",
                raw_text=text,
            )

        cleaned = text.strip()
        action_match = cls._ACTION_RE.search(cleaned)
        comm_match = cls._COMM_RE.search(cleaned)

        if not action_match:
            return BimodalEmission(
                action_verb="SYNTAX_ERROR",
                valid=False,
                parse_error="Missing or malformed ACTION header",
                raw_text=cleaned,
            )

        if not comm_match:
            return BimodalEmission(
                action_verb="SYNTAX_ERROR",
                valid=False,
                parse_error="Missing or malformed COMMUNICATE header",
                raw_text=cleaned,
            )

        verb = action_match.group(1).strip()
        param_str = action_match.group(2) or ""
        params: Dict[str, str] = {}
        for token in param_str.split():
            if "=" in token:
                k, v = token.split("=", 1)
                params[k.strip()] = v.strip()
            else:
                params[token.strip()] = "true"

        comm_class_str = comm_match.group(1).strip()
        comm_message = comm_match.group(2).strip()

        return BimodalEmission(
            action_verb=verb,
            action_params=params,
            comm_class=CommClass(comm_class_str),
            comm_message=comm_message,
            raw_text=cleaned,
            valid=True,
            parse_error=None,
        )


def compile_bimodal_gbnf_grammar(
    allowed_verbs: Optional[List[str]] = None,
    allowed_comm_classes: Optional[List[CommClass]] = None,
) -> str:
    """Compiles a Context-Free GBNF Grammar constraining single-pass bimodal emission."""
    if allowed_verbs:
        verb_alts = " | ".join(f'"{v}"' for v in allowed_verbs)
        verb_rule = f"action-verb ::= {verb_alts}"
    else:
        verb_rule = 'action-verb ::= [A-Z_]+'

    if allowed_comm_classes:
        comm_alts = " | ".join(f'"{c.value}"' for c in allowed_comm_classes)
        comm_class_rule = f"comm-type ::= {comm_alts}"
    else:
        comm_class_rule = 'comm-type ::= "INFORM" | "QUERY" | "EXPRESS"'

    grammar = f"""root ::= action-line "\\n" comm-line
action-line ::= "ACTION: " action-verb action-args?
action-args ::= (" " [a-zA-Z0-9_=.:/-]+)+
{verb_rule}
comm-line ::= "COMMUNICATE [" comm-type "]: \\"" message-body "\\""
{comm_class_rule}
message-body ::= [^"\\r\\n]+
"""
    return grammar
