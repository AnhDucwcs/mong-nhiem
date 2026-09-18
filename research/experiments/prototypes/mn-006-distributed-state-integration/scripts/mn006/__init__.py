"""Deterministic, non-model infrastructure for the frozen MN-006 v1 workload.

This package creates and validates individual paired cases.  It deliberately
does not choose an inventory, call a model, or implement an intervention.
"""

from .generation import generate_pair
from .model import (
    ANSWERS,
    INITIAL_STATE,
    PROFILE_LEVEL_1,
    PROFILE_LEVEL_2,
    STATES,
    CasePair,
    GeneratedCase,
    Profile,
)
from .oracle import decide, derive, parse_answer, replay
from .validation import ValidationError, validate_case, validate_pair

__all__ = [
    "ANSWERS",
    "INITIAL_STATE",
    "PROFILE_LEVEL_1",
    "PROFILE_LEVEL_2",
    "STATES",
    "CasePair",
    "GeneratedCase",
    "Profile",
    "ValidationError",
    "decide",
    "derive",
    "generate_pair",
    "parse_answer",
    "replay",
    "validate_case",
    "validate_pair",
]
