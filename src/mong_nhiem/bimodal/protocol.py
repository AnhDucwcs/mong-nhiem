"""Bimodal Cognitive Emission Protocol & Parser.

Constrains small language models (<4B) to emit single-pass operational actions
alongside triadic communicative acts (INFORM, QUERY, EXPRESS) under GBNF grammar.
100% Python Standard Library. Zero external dependencies.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum


class CommClass(str, Enum):
    """Orthogonal Triadic Communicative Taxonomy based on Host State Effect."""

    INFORM = "INFORM"  # Unidirectional report/explanation; Host continues nominal loop
    QUERY = "QUERY"  # Bidirectional solicitation; Host halts into SUPERVISED_STANDBY
    EXPRESS = "EXPRESS"  # Unconstrained socio-emotional persona expression (T=0.5)


@dataclass(frozen=True)
class BimodalEmission:
    """Structured representation of a dual-channel operational/communicative output."""

    action_verb: str
    action_params: dict[str, str] = field(default_factory=dict)
    comm_class: CommClass = CommClass.INFORM
    comm_intent: str | None = None
    comm_message: str = ""
    raw_text: str = ""
    valid: bool = True
    parse_error: str | None = None

    @property
    def full_action_str(self) -> str:
        """Reconstruct canonical ACTION string."""
        if not self.action_params:
            return self.action_verb
        params = " ".join(f"{k}={v}" for k, v in self.action_params.items())
        return f"{self.action_verb} {params}"


class BimodalParser:
    """Deterministic, sub-millisecond parser for bimodal emission format."""

    _ACTION_RE = re.compile(r"^ACTION:\s*([A-Za-z_]+)(?:[ \t]+([^\r\n]*))?$", re.MULTILINE)
    _COMM_RE = re.compile(
        r"^COMMUNICATE\s*\[\s*(INFORM|QUERY|EXPRESS)(?::([A-Za-z0-9_]+))?\s*\]\s*:\s*[\"']?([^\r\n]*?)[\"']?$",
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
        params: dict[str, str] = {}
        for token in param_str.split():
            if "=" in token:
                k, v = token.split("=", 1)
                params[k.strip()] = v.strip()
            else:
                params[token.strip()] = "true"

        comm_class_str = comm_match.group(1).strip()
        comm_intent = comm_match.group(2).strip() if comm_match.group(2) else None
        comm_message = comm_match.group(3).strip()

        return BimodalEmission(
            action_verb=verb,
            action_params=params,
            comm_class=CommClass(comm_class_str),
            comm_intent=comm_intent,
            comm_message=comm_message,
            raw_text=cleaned,
            valid=True,
            parse_error=None,
        )
