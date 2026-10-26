"""Dynamic Operator Intent GBNF Grammar Generator & Distiller.

Synthesizes bounded GBNF grammars with dynamic entity enums and provides
deterministic intent distillation for chaotic, self-correcting human operator speech.
100% Python Standard Library. Zero external dependencies.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class DistilledAction:
    """Structured action outcome distilled from natural language."""

    verb: str
    entity: str
    reasoning: str = ""


def build_operator_intent_gbnf(valid_entities: list[str]) -> str:
    """Builds formal GBNF grammar with dynamic entity enums and bounded reasoning."""
    entity_rule = " | ".join(f'"{e}"' for e in valid_entities)
    return (
        'root ::= reasoning "\\n" decision\n'
        'reasoning ::= "REASONING: " [^\\n]{1,80}\n'
        'decision ::= "ACTION: " verb " " entity\n'
        'verb ::= "OPEN" | "CLOSE" | "START" | "STOP" | "RESET"\n'
        f"entity ::= {entity_rule}\n"
    )


class OperatorIntentDistiller:
    """Distills noisy, contradictory human operator speech into single canonical action."""

    def __init__(self, valid_entities: list[str]) -> None:
        self.valid_entities = valid_entities

    def distill_intent(self, speech: str) -> DistilledAction:
        """Parses speech transcript, prioritizing recency and correcting negations."""
        cleaned = speech.strip()

        # Check for self-correction markers: "khoan", "nhầm", "đừng", "đổi", "thôi"
        correction_split = re.split(
            r"\b(?:à khoan|khoan|nhưng|đổi lại|thay vào đó|thôi)\b",
            cleaned,
            flags=re.IGNORECASE,
        )
        terminal_clause = correction_split[-1].strip()

        # Detect negation & double negation
        has_double_negation = bool(
            re.search(r"\bđừng\s+(?:có\s+mà\s+)?không\b", cleaned, flags=re.IGNORECASE)
        )

        # Entity grounding: Map colloquial terms to canonical entity enum
        entity = self.valid_entities[0] if self.valid_entities else "default"
        for candidate in self.valid_entities:
            if candidate in terminal_clause.lower():
                entity = candidate
                break
        else:
            # Semantic aliases
            if "phụ" in terminal_clause.lower() or "aux" in terminal_clause.lower():
                for candidate in self.valid_entities:
                    if "aux" in candidate.lower():
                        entity = candidate
                        break
            elif "2" in terminal_clause or "hai" in terminal_clause.lower():
                for candidate in self.valid_entities:
                    if "2" in candidate:
                        entity = candidate
                        break
            elif "1" in terminal_clause or "một" in terminal_clause.lower():
                for candidate in self.valid_entities:
                    if "1" in candidate:
                        entity = candidate
                        break

        # Action Verb grounding
        verb = "STOP"
        if has_double_negation:
            # "Đừng không ngắt" -> "Ngắt" -> STOP
            if any(term in cleaned.lower() for term in ("ngắt", "dừng", "đóng")):
                verb = "STOP"
            elif any(term in cleaned.lower() for term in ("mở", "bật")):
                verb = "START"
        else:
            if re.search(r"\b(?:mở|open|bật|start)\b", terminal_clause, re.IGNORECASE):
                verb = "OPEN"
            elif re.search(r"\b(?:đóng|close|khóa|lock)\b", terminal_clause, re.IGNORECASE):
                verb = "CLOSE"
            elif re.search(r"\b(?:ngắt|dừng|stop|hạ)\b", terminal_clause, re.IGNORECASE):
                verb = "STOP"

        return DistilledAction(
            verb=verb,
            entity=entity,
            reasoning=f"Resolved terminal clause: {terminal_clause[:60]}",
        )
