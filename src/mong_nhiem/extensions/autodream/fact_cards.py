"""Topological Fact Card Projector strictly bounded by cognitive token ceilings."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple


class FactCardProjector:
    """Projects multi-entity world states into dense, token-bounded Fact Cards."""

    def __init__(self, default_token_ceiling: int = 512):
        self.default_token_ceiling = default_token_ceiling

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Heuristic token estimator matching BPE tokenization (~3.6 chars/token)."""
        words = text.split()
        return max(len(words), int(len(text) / 3.6))

    def render_card(
        self,
        entity_id: str,
        version: int = 1,
        properties: Optional[Dict[str, Any]] = None,
        holder: Optional[str] = None,
        is_expired: bool = False,
    ) -> str:
        """Renders an individual entity state as a single compact Fact Card.
        
        Format: [entity_id v{version} holder:{holder} prop1:val1 prop2:val2]
        """
        props = properties or {}
        parts = [entity_id, f"v{version}"]
        if holder is not None:
            parts.append(f"holder:{holder}")
        if is_expired:
            parts.append("EXPIRED")

        for k, v in sorted(props.items()):
            if isinstance(v, float):
                v_str = f"{v:.2f}".rstrip("0").rstrip(".")
            else:
                v_str = str(v)
            parts.append(f"{k}:{v_str}")

        return f"[{' '.join(parts)}]"

    def project_fact_cards(
        self,
        entities: Dict[str, Dict[str, Any]],
        token_ceiling: Optional[int] = None,
        header: Optional[str] = None,
    ) -> Tuple[str, int]:
        """Projects a collection of entities into a multi-line fact card block within budget.
        
        Args:
            entities: Map of entity_id -> entity attribute dict (may contain 'version', 'properties', 'holder', etc.)
            token_ceiling: Maximum allowed tokens (defaults to self.default_token_ceiling).
            header: Optional header title line.
            
        Returns:
            (formatted_text, estimated_token_count)
        """
        ceiling = token_ceiling or self.default_token_ceiling
        lines: List[str] = []
        if header:
            lines.append(header)

        for entity_id, data in sorted(entities.items()):
            ver = data.get("version", 1)
            holder = data.get("holder")
            expired = data.get("is_expired", False)
            props = data.get("properties") or {
                k: v for k, v in data.items() if k not in ("version", "holder", "is_expired", "entity_id")
            }
            card = self.render_card(entity_id, ver, props, holder, expired)
            lines.append(f"  {card}")

        rendered = "\n".join(lines)
        tokens = self.estimate_tokens(rendered)

        # Budget enforcement: If exceeding token ceiling, prune lowest priority cards
        if tokens > ceiling and len(lines) > 2:
            truncated_lines: List[str] = []
            if header:
                truncated_lines.append(lines[0])
            for line in lines[1:]:
                test_block = "\n".join(truncated_lines + [line, "  [...TRUNCATED_FOR_CAPACITY...]"])
                if self.estimate_tokens(test_block) > ceiling:
                    truncated_lines.append("  [...TRUNCATED_FOR_CAPACITY...]")
                    break
                truncated_lines.append(line)
            rendered = "\n".join(truncated_lines)
            tokens = self.estimate_tokens(rendered)

        return rendered, tokens
