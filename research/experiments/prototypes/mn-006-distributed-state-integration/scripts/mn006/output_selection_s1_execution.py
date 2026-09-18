"""Frozen, non-model S1 execution contract for output-selection minimality."""
from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import output_selection as minimality
from . import output_selection_execution as s0_execution
from .fingerprinting import (
    canonical_json_bytes,
    canonical_text_bytes,
    canonical_text_sha256,
    sha256_bytes,
)
from .label_selection import GRAMMARS, LABELS, parse_label

EXPERIMENT_ROOT = Path(__file__).resolve().parents[2]
RUNS = EXPERIMENT_ROOT / "runs"
PLAN_PATH = EXPERIMENT_ROOT / "definition" / "output-selection-minimality-v1" / "plan.json"
S0_RUN_DIRECTORY = RUNS / minimality.S0_RUN_ID

S1_RUN_ID = minimality.S1_RUN_ID
S1_STAGE = minimality.S1_STAGE
CONTRACT_VERSION = minimality.CONTRACT_VERSION
EVIDENCE_SCHEMA_VERSION = "mn006-output-selection-s1-evidence-v1"
PARSER_VERSION = minimality.PARSER_VERSION
EVALUATOR_VERSION = "mn006-output-selection-s1-evaluator-v1"
RUNTIME_CONTRACT_VERSION = minimality.RUNTIME_CONTRACT_VERSION
EXPECTED_PLAN_SHA256 = minimality.EXPECTED_PLAN_SHA256
EXPECTED_REQUEST_COUNT = 4
REQUEST_ORDER_CONTRACT = "S1; canonical_plan_request_ordinal_ascending"
CHAT_COMPLETIONS_ENDPOINT = "/v1/chat/completions"
REQUEST_PARAMETERS = {
    "chat_template_kwargs": {},
    "max_tokens": 16,
    "seed": 42,
    "temperature": 0.0,
}


class S1ExecutionError(ValueError):
    """Raised when a future S1 execution deviates from frozen authority."""


def require_s1_run_identity(run_id: str) -> None:
    """Reject every run namespace except the single frozen S1 identity."""
    if run_id != S1_RUN_ID:
        raise S1ExecutionError("unknown or non-S1 diagnostic run identity")


def verify_s0_prerequisite(run_dir: Path = S0_RUN_DIRECTORY) -> dict[str, object]:
    """Require complete, integrity-valid S0 evidence with the exact frozen outcome."""
    try:
        summary = s0_execution.validate_s0_run_directory(run_dir)
    except (OSError, UnicodeError, ValueError) as error:
        raise S1ExecutionError("S1 prerequisite S0 evidence is missing, incomplete, or invalid") from error
    if summary.get("outcome") != "protocol_valid" or summary.get("classification") != "direct_copy_supported":
        raise S1ExecutionError("S1 is blocked unless canonical S0 is protocol-valid / direct_copy_supported")
    return {
        "classification": "direct_copy_supported",
        "integrity_validated": True,
        "outcome": "protocol_valid",
        "run_id": minimality.S0_RUN_ID,
    }


@dataclass(frozen=True)
class S1Request:
    """One executable S1 record loaded directly from the canonical plan."""

    authority: Mapping[str, object]

    @property
    def record_id(self) -> str:
        return str(self.authority["record_id"])

    @property
    def request_ordinal(self) -> int:
        return int(self.authority["request_ordinal"])

    @property
    def canonical_answer(self) -> str:
        return str(self.authority["canonical_answer"])

    @property
    def grammar(self) -> str:
        return str(self.authority["grammar"])

    @property
    def grammar_id(self) -> str:
        return str(self.authority["grammar_id"])

    @property
    def public_prompt(self) -> str:
        return str(self.authority["public_prompt"])

    @property
    def query_states(self) -> tuple[str, str]:
        states = self.authority.get("query_states")
        if not isinstance(states, list) or len(states) != 2:
            raise S1ExecutionError("S1 authority record has no valid state pair")
        return str(states[0]), str(states[1])

    @property
    def equal_state(self) -> bool:
        value = self.authority.get("equal_state")
        if not isinstance(value, bool):
            raise S1ExecutionError("S1 authority record has no valid equality relation")
        return value


def _read_canonical_plan(plan_path: Path = PLAN_PATH) -> dict[str, object]:
    """Read exact plan bytes first; never reconstruct a loose authority plan."""
    payload = plan_path.read_bytes()
    if sha256_bytes(payload) != EXPECTED_PLAN_SHA256:
        raise S1ExecutionError("output-selection plan SHA-256 differs from frozen authority")
    try:
        authority = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise S1ExecutionError("output-selection plan is not valid canonical JSON") from error
    if canonical_json_bytes(authority) != payload:
        raise S1ExecutionError("output-selection plan physical bytes are not canonical UTF-8/LF JSON")
    if authority != minimality.validate_frozen_plan():
        raise S1ExecutionError("output-selection plan differs from frozen semantic authority")
    return authority


def build_s1_request_plan(
    plan_path: Path = PLAN_PATH, s0_run_dir: Path = S0_RUN_DIRECTORY
) -> tuple[S1Request, ...]:
    """Load exactly the four authorized S1 records after mechanical S0 verification."""
    verify_s0_prerequisite(s0_run_dir)
    authority = _read_canonical_plan(plan_path)
    if authority.get("contract_version") != CONTRACT_VERSION:
        raise S1ExecutionError("plan contract version differs from S1 contract")
    if authority.get("parser_version") != PARSER_VERSION:
        raise S1ExecutionError("plan parser version differs from S1 contract")
    if authority.get("runtime_contract_version") != RUNTIME_CONTRACT_VERSION:
        raise S1ExecutionError("plan runtime contract version differs from S1 contract")
    dependencies = authority.get("stage_dependencies")
    if dependencies != {
        minimality.S0_STAGE: "eligible_for_separate_future_execution",
        S1_STAGE: "eligible_only_if_S0_classification_is_direct_copy_supported",
    }:
        raise S1ExecutionError("plan stage dependencies differ from frozen minimality gate")
    records = authority.get("records")
    if not isinstance(records, list):
        raise S1ExecutionError("plan records must be a list")
    s0_records = [record for record in records if record.get("stage") == minimality.S0_STAGE]
    s1_records = [record for record in records if record.get("stage") == S1_STAGE]
    if len(records) != 8 or len(s0_records) != 4 or len(s1_records) != EXPECTED_REQUEST_COUNT:
        raise S1ExecutionError("plan stage coverage differs from frozen S0/S1 authority")
    if any(record.get("stage") not in {minimality.S0_STAGE, S1_STAGE} for record in records):
        raise S1ExecutionError("plan contains an unknown executable stage")
    requests = tuple(S1Request(record) for record in s1_records)
    validate_s1_request_plan(requests)
    return requests


def validate_s1_request_plan(requests: tuple[S1Request, ...]) -> None:
    """Assert exact plan-owned S1 order, state pairs, labels, grammar, and prompts."""
    if len(requests) != EXPECTED_REQUEST_COUNT:
        raise S1ExecutionError("S1 request count differs from frozen four-request plan")
    if [request.request_ordinal for request in requests] != [1, 2, 3, 4]:
        raise S1ExecutionError("S1 request order differs from canonical plan")
    if [request.query_states for request in requests] != [("S1", "S2"), ("S1", "S1"), ("S2", "S2"), ("S2", "S1")]:
        raise S1ExecutionError("S1 state-pair order differs from canonical plan")
    if [request.equal_state for request in requests] != [False, True, True, False]:
        raise S1ExecutionError("S1 equality relation differs from canonical plan")
    if [request.canonical_answer for request in requests] != ["B", "A", "A", "B"]:
        raise S1ExecutionError("S1 canonical labels differ from direct equality rule")
    if any(request.grammar_id != "A_then_B" for request in requests):
        raise S1ExecutionError("S1 must use only G_AB")
    expected_cases = minimality.build_s1_plan()
    if [dict(request.authority) for request in requests] != [case.authority_dict() for case in expected_cases]:
        raise S1ExecutionError("S1 plan records differ from frozen authority records")
    for request in requests:
        if request.grammar != GRAMMARS["A_then_B"] or not request.grammar.endswith("\n"):
            raise S1ExecutionError("S1 request grammar differs from frozen G_AB")
        if request.canonical_answer != ("A" if request.equal_state else "B"):
            raise S1ExecutionError("S1 direct equality rule differs from frozen authority")
        prompt_bytes = canonical_text_bytes(request.public_prompt)
        if prompt_bytes != request.public_prompt.encode("utf-8"):
            raise S1ExecutionError("S1 prompt is not canonical UTF-8/LF text")
        if canonical_text_sha256(request.public_prompt) != request.authority.get("public_prompt_sha256"):
            raise S1ExecutionError("S1 prompt fingerprint differs from canonical plan")


def build_request_payload(request: S1Request) -> dict[str, object]:
    """Construct the future request from one plan record and frozen runtime fields."""
    if request.canonical_answer not in LABELS or request.canonical_answer != ("A" if request.equal_state else "B"):
        raise S1ExecutionError("S1 canonical label does not match its frozen equality relation")
    prompt_bytes = canonical_text_bytes(request.public_prompt)
    if prompt_bytes != request.public_prompt.encode("utf-8"):
        raise S1ExecutionError("S1 payload prompt is not canonical UTF-8/LF text")
    payload: dict[str, object] = {
        "chat_template_kwargs": REQUEST_PARAMETERS["chat_template_kwargs"],
        "grammar": request.grammar,
        "max_tokens": REQUEST_PARAMETERS["max_tokens"],
        "messages": [{"role": "user", "content": prompt_bytes.decode("utf-8")}],
        "seed": REQUEST_PARAMETERS["seed"],
        "temperature": REQUEST_PARAMETERS["temperature"],
    }
    if set(payload) != {"chat_template_kwargs", "grammar", "max_tokens", "messages", "seed", "temperature"}:
        raise S1ExecutionError("S1 payload field set differs from frozen contract")
    return payload


def plan_entry(request: S1Request) -> dict[str, object]:
    """Return plan-owned fields that must be copied into later evidence."""
    return dict(request.authority)


def dry_construction(
    plan_path: Path = PLAN_PATH, s0_run_dir: Path = S0_RUN_DIRECTORY
) -> tuple[dict[str, object], ...]:
    """Build future S1 payloads only; this performs no server, network, or evidence writes."""
    requests = build_s1_request_plan(plan_path, s0_run_dir)
    entries: list[dict[str, object]] = []
    for request in requests:
        payload = build_request_payload(request)
        if payload["messages"] != [{"role": "user", "content": request.public_prompt}]:
            raise S1ExecutionError("S1 payload prompt differs from its canonical plan record")
        if payload["grammar"] != GRAMMARS["A_then_B"]:
            raise S1ExecutionError("S1 payload grammar differs from frozen G_AB")
        entries.append({**plan_entry(request), "payload": payload})
    if len(entries) != EXPECTED_REQUEST_COUNT or any(entry["stage"] != S1_STAGE for entry in entries):
        raise S1ExecutionError("S1 dry construction attempted a non-S1 stage")
    return tuple(entries)


def contract_metadata(executor_commit: str) -> dict[str, object]:
    """Prospective metadata written before a future execution starts."""
    require_s1_run_identity(S1_RUN_ID)
    return {
        "contract_version": CONTRACT_VERSION,
        "endpoint": CHAT_COMPLETIONS_ENDPOINT,
        "evaluator_version": EVALUATOR_VERSION,
        "expected_plan_sha256": EXPECTED_PLAN_SHA256,
        "parser_version": PARSER_VERSION,
        "request_count": EXPECTED_REQUEST_COUNT,
        "request_order_contract": REQUEST_ORDER_CONTRACT,
        "run_id": S1_RUN_ID,
        "runtime_contract_version": RUNTIME_CONTRACT_VERSION,
        "s0_prerequisite": {"classification": "direct_copy_supported", "run_id": minimality.S0_RUN_ID},
        "stage": S1_STAGE,
        "executor_commit": executor_commit,
    }


def evaluate_raw_output(request: S1Request, raw_output: str) -> dict[str, object]:
    """Reuse the frozen strict A/B parser; host logic only scores retained output."""
    parsed = parse_label(raw_output)
    return {
        "canonical_answer": request.canonical_answer,
        "correct": parsed == request.canonical_answer,
        "malformed": parsed is None,
        "parsed_answer": parsed,
        "score": float(parsed == request.canonical_answer),
    }


def summarize_s1_records(records: list[Mapping[str, Any]], requests: tuple[S1Request, ...]) -> dict[str, object]:
    """Classify only a complete infrastructure-valid S1 record sequence."""
    validate_s1_request_plan(requests)
    expected = {request.record_id: request for request in requests}
    observed_ids = [str(record.get("record_id")) for record in records]
    expected_ids = [request.record_id for request in requests]
    complete = (
        len(records) == len(requests)
        and observed_ids == expected_ids
        and all(record.get("infrastructure_status") == "complete" for record in records)
    )
    if not complete:
        return {
            "classification": None,
            "completed_requests": sum(record.get("infrastructure_status") == "complete" for record in records),
            "expected_requests": len(requests),
            "infrastructure_failure_count": sum(record.get("infrastructure_status") != "complete" for record in records),
            "outcome": "infrastructure_invalid",
            "request_order_contract": REQUEST_ORDER_CONTRACT,
        }
    raw_outputs: dict[str, str] = {}
    for record in records:
        request = expected[str(record["record_id"])]
        for key, value in plan_entry(request).items():
            if record.get(key) != value:
                raise S1ExecutionError(f"S1 retained record differs from authority: {key}")
        evaluation = evaluate_raw_output(request, str(record.get("raw_output", "")))
        if record.get("evaluation") != evaluation:
            raise S1ExecutionError("S1 stored evaluator result differs from recomputation")
        raw_outputs[request.record_id] = str(record.get("raw_output", ""))
    return {
        "classification": minimality.classify_s1(raw_outputs, s0_classification="direct_copy_supported"),
        "completed_requests": len(records),
        "expected_requests": len(requests),
        "infrastructure_failure_count": 0,
        "malformed_count": sum(bool(evaluate_raw_output(request, raw_outputs[request.record_id])["malformed"]) for request in requests),
        "outcome": "protocol_valid",
        "request_order_contract": REQUEST_ORDER_CONTRACT,
    }


def artifact_hashes(run_dir: Path) -> dict[str, str]:
    """Fingerprint completed authority artifacts by physical bytes in sorted order."""
    required = (
        "metadata.json",
        "raw/llama-server.stderr.txt",
        "raw/llama-server.stdout.txt",
        "results.jsonl",
        "server-lifecycle.json",
        "summary.json",
    )
    hashes: dict[str, str] = {}
    for relative in required:
        path = run_dir / relative
        if not path.is_file():
            raise S1ExecutionError(f"S1 authoritative artifact is missing: {relative}")
        hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def validate_s1_run_directory(run_dir: Path, s0_run_dir: Path = S0_RUN_DIRECTORY) -> dict[str, object]:
    """Accept only a finalized complete S1 run after revalidating canonical S0."""
    s0_prerequisite = verify_s0_prerequisite(s0_run_dir)
    requests = build_s1_request_plan(s0_run_dir=s0_run_dir)
    metadata_path = run_dir / "metadata.json"
    if not metadata_path.is_file():
        raise S1ExecutionError("S1 metadata is missing")
    metadata = json.loads(metadata_path.read_bytes().decode("utf-8"))
    require_s1_run_identity(str(metadata.get("run_id")))
    if metadata.get("contract", {}).get("expected_plan_sha256") != EXPECTED_PLAN_SHA256:
        raise S1ExecutionError("S1 metadata does not identify the frozen plan")
    if metadata.get("s0_prerequisite") != s0_prerequisite:
        raise S1ExecutionError("S1 metadata does not retain the validated S0 prerequisite")
    records_path = run_dir / "results.jsonl"
    if not records_path.is_file():
        raise S1ExecutionError("S1 results are missing")
    records = [json.loads(line) for line in records_path.read_text(encoding="utf-8").splitlines() if line]
    summary = summarize_s1_records(records, requests)
    if summary["outcome"] != "protocol_valid":
        raise S1ExecutionError("incomplete or infrastructure-invalid S1 evidence is not a canonical complete run")
    stored_summary = json.loads((run_dir / "summary.json").read_bytes().decode("utf-8"))
    if stored_summary != summary:
        raise S1ExecutionError("S1 stored summary differs from deterministic recomputation")
    integrity = json.loads((run_dir / "integrity.json").read_bytes().decode("utf-8"))
    if integrity.get("artifact_sha256") != artifact_hashes(run_dir):
        raise S1ExecutionError("S1 physical artifact hashes differ from integrity manifest")
    return summary
