"""Dynamic Operator Intent GBNF Grammar Generator & Distiller.

Synthesizes bounded GBNF grammars with dynamic entity enums and provides
deterministic intent distillation for chaotic, self-correcting human operator speech
across Vietnamese, English, and technical code-switching.
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


def build_operator_intent_gbnf(
    valid_entities: list[str],
    valid_verbs: list[str] | None = None,
) -> str:
    """Builds formal GBNF grammar with dynamic entity enums and bounded reasoning."""
    verbs = valid_verbs or [
        "OPEN",
        "CLOSE",
        "START",
        "STOP",
        "RESET",
        "COOL",
        "ISOLATE",
        "VENT",
        "SEAL",
        "SWITCH",
        "PURGE",
    ]
    entity_rule = " | ".join(f'"{e}"' for e in valid_entities)
    verb_rule = " | ".join(f'"{v}"' for v in verbs)
    return (
        'root ::= reasoning "\\n" decision\n'
        'reasoning ::= "REASONING: " [^\\n]{1,120}\n'
        'decision ::= "ACTION: " verb " " entity\n'
        f"verb ::= {verb_rule}\n"
        f"entity ::= {entity_rule}\n"
    )


class OperatorIntentDistiller:
    """Distills noisy, contradictory human operator speech into single canonical action."""

    def __init__(
        self,
        valid_entities: list[str],
        valid_verbs: list[str] | None = None,
    ) -> None:
        self.valid_entities = valid_entities
        self.valid_verbs = valid_verbs or [
            "OPEN",
            "CLOSE",
            "START",
            "STOP",
            "RESET",
            "COOL",
            "ISOLATE",
            "VENT",
            "SEAL",
            "SWITCH",
            "PURGE",
        ]

    def distill_intent(self, speech: str) -> DistilledAction:
        """Parses speech transcript, prioritizing recency, resolving negations and sarcasm."""
        cleaned = speech.strip()

        # Step 1: Handle Sarcasm / Rhetorical Negation in English
        # e.g., "Yeah right, like opening valve one is gonna save us now! Forget that nonsense, vent the backup chamber immediately!"
        if re.search(r"\byeah right\b|\blike [a-z0-9_]+ is gonna save us\b|\bforget that\b", cleaned, re.IGNORECASE):
            parts = re.split(r"[!?.]\s*", cleaned)
            for part in reversed(parts):
                if part and not re.search(r"\byeah right\b|\bforget that\b", part, re.IGNORECASE):
                    terminal_clause = part.strip()
                    break
            else:
                terminal_clause = cleaned
        # Step 2: Handle Counterfactuals & Conditionals
        # e.g. "Nếu mà áp suất chạm 80 thì mới xả khẩn cấp, còn hiện tại đang 60 thì chỉ mở con van phụ thôi"
        elif re.search(r"\bnếu\s+(?:mà\s+)?.*?\bthì\s+(?:mới\s+)?.*?[,;]?\s*(?:còn|nhưng)\b", cleaned, re.IGNORECASE):
            parts = re.split(r"\b(?:còn|nhưng|thay vào đó)\b", cleaned, flags=re.IGNORECASE)
            terminal_clause = parts[-1].strip()
        # Step 3: Handle Self-Correction & Cancellation Markers
        else:
            correction_split = re.split(
                r"\b(?:à khoan|khoan|nhưng|đổi lại|thay vào đó|mà thôi|à nhầm|nhầm|scratch that|hold on|disregard|forget protocol|bypass protocol|cancel|stop stop)\b",
                cleaned,
                flags=re.IGNORECASE,
            )
            terminal_clause = correction_split[-1].strip()

        # Step 4: Detect Double Negation ("Đừng có mà không bơm" -> BẮT BUỘC BƠM)
        has_double_negation = bool(
            re.search(r"\bđừng\s+(?:có\s+mà\s+)?không\b", cleaned, flags=re.IGNORECASE)
        )

        # Step 5: Entity Grounding
        entity = self._ground_entity(terminal_clause, cleaned)

        # Step 6: Verb Grounding
        verb = self._ground_verb(terminal_clause, cleaned, has_double_negation)

        return DistilledAction(
            verb=verb,
            entity=entity,
            reasoning=f"Resolved terminal directive: {terminal_clause[:80]}",
        )

    def _ground_entity(self, terminal_clause: str, full_speech: str) -> str:
        """Grounds natural colloquial entity references to canonical schema enum."""
        t_low = terminal_clause.lower()
        full_low = full_speech.lower()

        # Direct match in terminal clause
        for candidate in self.valid_entities:
            cand_low = candidate.lower()
            if cand_low in t_low or cand_low.replace("_", " ") in t_low:
                return candidate

        # Semantic aliases / Domain vernacular
        alias_map = {
            "lò 2": "reactor_2",
            "lò phản ứng 2": "reactor_2",
            "reactor 2": "reactor_2",
            "van phụ": "aux_valve",
            "con van phụ": "aux_valve",
            "aux valve": "aux_valve",
            "trạm phụ": "aux_substation",
            "trạm biến áp phụ": "aux_substation",
            "aux substation": "aux_substation",
            "backup chamber": "backup_chamber",
            "khoang dự phòng": "backup_chamber",
            "sector beta": "sector_beta",
            "khoang beta": "sector_beta",
            "beta": "sector_beta",
            "bơm dự phòng": "backup_pump",
            "con bơm dự phòng": "backup_pump",
            "backup pump": "backup_pump",
            "bình oxy 2": "oxygen_tank_2",
            "bình oxy số 2": "oxygen_tank_2",
            "oxygen tank 2": "oxygen_tank_2",
            "tank b": "tank_b",
            "backup node": "backup_node",
            "valve 1": "valve_1",
            "van 1": "valve_1",
            "valve 2": "valve_2",
            "van 2": "valve_2",
        }

        for alias, target in alias_map.items():
            if alias in t_low and target in self.valid_entities:
                return target

        # Check full speech if not found in terminal clause
        for alias, target in alias_map.items():
            if alias in full_low and target in self.valid_entities:
                return target

        return self.valid_entities[0] if self.valid_entities else "default"

    def _ground_verb(self, terminal_clause: str, full_speech: str, has_double_negation: bool) -> str:
        """Grounds operational action verb from terminal directive."""
        t_low = terminal_clause.lower()

        if has_double_negation:
            # "Đừng có mà không bơm nước làm mát" -> COOL
            if any(term in full_speech.lower() for term in ("bơm nước", "làm mát", "cool")):
                return "COOL"
            if any(term in full_speech.lower() for term in ("mở", "open", "bật", "start")):
                return "START" if "START" in self.valid_verbs else "OPEN"
            if any(term in full_speech.lower() for term in ("ngắt", "dừng", "stop", "đóng", "close")):
                return "STOP" if "STOP" in self.valid_verbs else "CLOSE"

        # Explicit action verbs (supports Vietnamese with/without diacritics & English)
        if re.search(r"\b(?:cô lập|co lap|isolate|cách ly|cach ly)\b", t_low):
            return "ISOLATE"
        if re.search(r"\b(?:vent|thông gió|thong gio|xả khí|xa khi)\b", t_low):
            return "VENT"
        if re.search(r"\b(?:seal|niêm phong|niem phong|khóa kín|khoa kin)\b", t_low):
            return "SEAL"
        if re.search(r"\b(?:switch|chuyển qua|chuyen qua|đổi sang|doi sang|chuyển|chuyen)\b", t_low):
            return "SWITCH"
        if re.search(r"\b(?:purge|xả sạch|xa sach|xả gấp|xa gap)\b", t_low):
            return "PURGE"
        if re.search(r"\b(?:bơm nước|bom nuoc|bơm|bom|làm mát|lam mat|cool)\b", t_low):
            return "COOL"
        if re.search(r"\b(?:mở|mo|open|bật|bat|start)\b", t_low):
            return "OPEN"
        if re.search(r"\b(?:đóng|dong|close|khóa|khoa|lock)\b", t_low):
            return "CLOSE"
        if re.search(r"\b(?:ngắt|ngat|dừng|dung|stop|tắt|tat|hạ|ha|trip)\b", t_low):
            return "STOP"
        if re.search(r"\b(?:reset|khởi động lại|khoi dong lai|restart)\b", t_low):
            return "RESET"

        return self.valid_verbs[0] if self.valid_verbs else "NOMINAL"
