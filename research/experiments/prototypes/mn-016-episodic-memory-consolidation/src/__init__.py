"""MN-016: AutoDream Memory Consolidation & Context Pressure Protection Prototype."""

from .provenance import EventProvenance, EpisodicEvent, EpisodicStream
from .conflict_resolver import DeterministicConflictResolver, EntityState
from .consolidation_lock import ConsolidationLock, ConsolidationState
from .auto_dream_trigger import AutonomousAutoDreamTrigger, TriggerConfig, TriggerResult
from .dream_engine import HostDreamEngine
from .recall_coordinator import AutoDreamCoordinator, AutoDreamResult

__all__ = [
    "EventProvenance",
    "EpisodicEvent",
    "EpisodicStream",
    "DeterministicConflictResolver",
    "EntityState",
    "ConsolidationLock",
    "ConsolidationState",
    "AutonomousAutoDreamTrigger",
    "TriggerConfig",
    "TriggerResult",
    "HostDreamEngine",
    "AutoDreamCoordinator",
    "AutoDreamResult",
]
