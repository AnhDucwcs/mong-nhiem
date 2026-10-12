"""AutoDream cognitive compaction and memory consolidation extension."""

from __future__ import annotations

from .consolidator import AutoDreamConsolidator, FrontierBranchPruner
from .fact_cards import FactCardProjector

__all__ = [
    "AutoDreamConsolidator",
    "FactCardProjector",
    "FrontierBranchPruner",
]
