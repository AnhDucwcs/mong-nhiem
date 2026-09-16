#!/usr/bin/env python3
"""Execute only the prospectively frozen MN-006 grammar-constrained baseline."""

from __future__ import annotations

from pathlib import Path

from mn006.measurement import EXPECTED_INVENTORY_SHA256
from mn006.model import PARSER_VERSION
from mn006.response_channel import (
    FIXED_ANSWER_GRAMMAR,
    RESPONSE_CHANNEL_CONTRACT_VERSION,
)
from run_mn006_baseline import DEFAULT_MODEL, DEFAULT_SERVER, run_attempt
from run_mn006_baseline import build_request_payload as _baseline_payload

ATTEMPT_ID = "attempt-0002"
EVIDENCE_SCHEMA_VERSION = "mn006-response-channel-grammar-attempt-v1"
RUNTIME_CONTRACT_VERSION = "mn006-baseline-runtime-v1"
EVALUATOR_VERSION = "mn006-evaluator-v1"

ATTEMPT_CONTRACT = {
    "attempt_id": ATTEMPT_ID,
    "evaluator_version": EVALUATOR_VERSION,
    "expected_inventory_sha256": EXPECTED_INVENTORY_SHA256,
    "expected_model_subject": "llama-3.2-3b",
    "parser_version": PARSER_VERSION,
    "response_channel_contract_version": RESPONSE_CHANNEL_CONTRACT_VERSION,
    "response_grammar": FIXED_ANSWER_GRAMMAR,
    "runtime_contract_version": RUNTIME_CONTRACT_VERSION,
}


def build_request_payload(prompt_bytes: bytes) -> dict[str, object]:
    """Construct the sole authorized future request-channel revision."""
    return _baseline_payload(prompt_bytes, grammar=FIXED_ANSWER_GRAMMAR)


def run(model: Path = DEFAULT_MODEL, server: Path = DEFAULT_SERVER) -> Path:
    """Run future `attempt-0002`; invocation is separately authorized from this executor commit."""
    return run_attempt(
        attempt_id=ATTEMPT_ID,
        evidence_schema_version=EVIDENCE_SCHEMA_VERSION,
        response_channel_contract_version=RESPONSE_CHANNEL_CONTRACT_VERSION,
        grammar=FIXED_ANSWER_GRAMMAR,
        contract_metadata=ATTEMPT_CONTRACT,
        model=model,
        server=server,
    )


def main() -> None:
    print(run())


if __name__ == "__main__":
    main()
