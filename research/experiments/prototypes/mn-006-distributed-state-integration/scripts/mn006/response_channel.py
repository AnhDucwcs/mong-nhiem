"""Static contract helpers for the prospective MN-006 output constraint."""
from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any

RESPONSE_CHANNEL_CONTRACT_VERSION = "mn006-response-channel-grammar-v1"
GRAMMAR_FIELD = "grammar"
FIXED_ANSWER_GRAMMAR = 'root ::= "VALID" | "INVALID"\n'


class ResponseChannelError(ValueError):
    """Raised when a prospective response-channel payload changes more than grammar."""


def constrained_payload(baseline_payload: Mapping[str, Any]) -> dict[str, Any]:
    """Copy one baseline request and add the single frozen global grammar field."""
    if GRAMMAR_FIELD in baseline_payload:
        raise ResponseChannelError("baseline payload must not already contain a grammar")
    payload = deepcopy(dict(baseline_payload))
    payload[GRAMMAR_FIELD] = FIXED_ANSWER_GRAMMAR
    return payload


def validate_constrained_payload(
    baseline_payload: Mapping[str, Any], constrained: Mapping[str, Any]
) -> None:
    """Assert that a prospective attempt changes exactly the output-language field."""
    if constrained.get(GRAMMAR_FIELD) != FIXED_ANSWER_GRAMMAR:
        raise ResponseChannelError("payload does not use the frozen fixed answer grammar")
    observed = {key: value for key, value in constrained.items() if key != GRAMMAR_FIELD}
    if observed != dict(baseline_payload):
        raise ResponseChannelError("response-channel payload changed a non-grammar field")
