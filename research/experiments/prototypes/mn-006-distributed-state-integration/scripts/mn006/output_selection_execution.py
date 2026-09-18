"""Frozen, non-model S0 execution contract for output-selection minimality."""
from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import output_selection as minimality
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

S0_RUN_ID = minimality.S0_RUN_ID
S0_STAGE = minimality.S0_STAGE
CONTRACT_VERSION = minimality.CONTRACT_VERSION
EVIDENCE_SCHEMA_VERSION = "mn006-output-selection-s0-evidence-v1"
PARSER_VERSION = minimality.PARSER_VERSION
EVALUATOR_VERSION = "mn006-output-selection-s0-evaluator-v1"
RUNTIME_CONTRACT_VERSION = minimality.RUNTIME_CONTRACT_VERSION
EXPECTED_PLAN_SHA256 = minimality.EXPECTED_PLAN_SHA256
EXPECTED_REQUEST_COUNT = 4
REQUEST_ORDER_CONTRACT = "S0; canonical_plan_request_ordinal_ascending"
CHAT_COMPLETIONS_ENDPOINT = "/v1/chat/completions"
REQUEST_PARAMETERS = {
    "chat_template_kwargs": {},
    "max_tokens": 16,
    "seed": 42,
    "temperature": 0.0,
}


class S0ExecutionError(ValueError):
    """Raised when a future S0 execution deviates from frozen authority."""


def require_s0_run_identity(run_id: str) -> None:
    """Reject every run namespace except the single frozen S0 identity."""
    if run_id != S0_RUN_ID:
        raise S0ExecutionError("unknown or non-S0 diagnostic run identity")


@dataclass(frozen=True)
class S0Request:
    """One executable S0 record loaded directly from the canonical plan."""

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
    def target_label(self) -> str:
        return str(self.authority["target_label"])


def _read_canonical_plan(plan_path: Path = PLAN_PATH) -> dict[str, object]:
    """Read exact bytes first; never reconstruct authority from a loose plan."""
    payload = plan_path.read_bytes()
    if sha256_bytes(payload) != EXPECTED_PLAN_SHA256:
        raise S0ExecutionError("output-selection plan SHA-256 differs from frozen authority")
    try:
        authority = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise S0ExecutionError("output-selection plan is not valid canonical JSON") from error
    if canonical_json_bytes(authority) != payload:
        raise S0ExecutionError("output-selection plan physical bytes are not canonical UTF-8/LF JSON")
    if authority != minimality.validate_frozen_plan():
        raise S0ExecutionError("output-selection plan differs from the frozen semantic authority")
    return authority


def build_s0_request_plan(plan_path: Path = PLAN_PATH) -> tuple[S0Request, ...]:
    """Load exactly the four authorized S0 records; S1 remains non-executable."""
    authority = _read_canonical_plan(plan_path)
    if authority.get("contract_version") != CONTRACT_VERSION:
        raise S0ExecutionError("plan contract version differs from S0 contract")
    if authority.get("parser_version") != PARSER_VERSION:
        raise S0ExecutionError("plan parser version differs from S0 contract")
    if authority.get("runtime_contract_version") != RUNTIME_CONTRACT_VERSION:
        raise S0ExecutionError("plan runtime contract version differs from S0 contract")
    dependencies = authority.get("stage_dependencies")
    if dependencies != {
        S0_STAGE: "eligible_for_separate_future_execution",
        minimality.S1_STAGE: "eligible_only_if_S0_classification_is_direct_copy_supported",
    }:
        raise S0ExecutionError("plan stage dependencies differ from frozen minimality gate")
    records = authority.get("records")
    if not isinstance(records, list):
        raise S0ExecutionError("plan records must be a list")
    s0_records = [record for record in records if record.get("stage") == S0_STAGE]
    s1_records = [record for record in records if record.get("stage") == minimality.S1_STAGE]
    if len(records) != 8 or len(s0_records) != EXPECTED_REQUEST_COUNT or len(s1_records) != 4:
        raise S0ExecutionError("plan stage coverage differs from frozen S0/S1 authority")
    if any(record.get("stage") not in {S0_STAGE, minimality.S1_STAGE} for record in records):
        raise S0ExecutionError("plan contains an unknown executable stage")
    requests = tuple(S0Request(record) for record in s0_records)
    validate_s0_request_plan(requests)
    return requests


def validate_s0_request_plan(requests: tuple[S0Request, ...]) -> None:
    """Assert plan-owned S0 order, labels, grammar, and prompt bytes exactly."""
    if len(requests) != EXPECTED_REQUEST_COUNT:
        raise S0ExecutionError("S0 request count differs from frozen four-request plan")
    if [request.request_ordinal for request in requests] != [1, 2, 3, 4]:
        raise S0ExecutionError("S0 request order differs from canonical plan")
    if [request.target_label for request in requests] != ["A", "B", "B", "A"]:
        raise S0ExecutionError("S0 target-label order differs from canonical plan")
    if [request.grammar_id for request in requests] != ["A_then_B", "B_then_A", "A_then_B", "B_then_A"]:
        raise S0ExecutionError("S0 grammar-order assignment differs from canonical plan")
    if [request.canonical_answer for request in requests] != ["A", "B", "B", "A"]:
        raise S0ExecutionError("S0 canonical labels differ from explicit plan targets")
    expected_cases = minimality.build_s0_plan()
    if [dict(request.authority) for request in requests] != [case.authority_dict() for case in expected_cases]:
        raise S0ExecutionError("S0 plan records differ from frozen authority records")
    for request in requests:
        if request.grammar_id not in GRAMMARS or request.grammar != GRAMMARS[request.grammar_id]:
            raise S0ExecutionError("S0 request grammar differs from the canonical grammar identity")
        if request.grammar not in GRAMMARS.values() or not request.grammar.endswith("\n"):
            raise S0ExecutionError("S0 request grammar is not a frozen A/B grammar")
        prompt_bytes = canonical_text_bytes(request.public_prompt)
        if prompt_bytes != request.public_prompt.encode("utf-8"):
            raise S0ExecutionError("S0 prompt is not canonical UTF-8/LF text")
        if canonical_text_sha256(request.public_prompt) != request.authority.get("public_prompt_sha256"):
            raise S0ExecutionError("S0 prompt fingerprint differs from canonical plan")


def build_request_payload(request: S0Request) -> dict[str, object]:
    """Construct the future request from one plan record and frozen runtime fields."""
    if request.canonical_answer not in LABELS or request.target_label != request.canonical_answer:
        raise S0ExecutionError("S0 request canonical label does not copy its frozen target")
    prompt_bytes = canonical_text_bytes(request.public_prompt)
    if prompt_bytes != request.public_prompt.encode("utf-8"):
        raise S0ExecutionError("S0 payload prompt is not canonical UTF-8/LF text")
    payload: dict[str, object] = {
        "chat_template_kwargs": REQUEST_PARAMETERS["chat_template_kwargs"],
        "grammar": request.grammar,
        "max_tokens": REQUEST_PARAMETERS["max_tokens"],
        "messages": [{"role": "user", "content": prompt_bytes.decode("utf-8")}],
        "seed": REQUEST_PARAMETERS["seed"],
        "temperature": REQUEST_PARAMETERS["temperature"],
    }
    if set(payload) != {"chat_template_kwargs", "grammar", "max_tokens", "messages", "seed", "temperature"}:
        raise S0ExecutionError("S0 payload field set differs from frozen contract")
    return payload


def plan_entry(request: S0Request) -> dict[str, object]:
    """Return only plan-owned fields that must be copied into later evidence."""
    return dict(request.authority)


def dry_construction(plan_path: Path = PLAN_PATH) -> tuple[dict[str, object], ...]:
    """Build future S0 payloads only; this function performs no I/O beyond authority reads."""
    requests = build_s0_request_plan(plan_path)
    entries: list[dict[str, object]] = []
    for request in requests:
        payload = build_request_payload(request)
        if payload["messages"] != [{"role": "user", "content": request.public_prompt}]:
            raise S0ExecutionError("S0 payload prompt differs from its canonical plan record")
        if payload["grammar"] != request.grammar:
            raise S0ExecutionError("S0 payload grammar differs from its canonical plan record")
        entries.append({**plan_entry(request), "payload": payload})
    if len(entries) != EXPECTED_REQUEST_COUNT:
        raise S0ExecutionError("S0 dry construction differs from frozen request count")
    if any(entry["stage"] != S0_STAGE for entry in entries):
        raise S0ExecutionError("S0 dry construction attempted a non-S0 stage")
    return tuple(entries)


def contract_metadata(executor_commit: str) -> dict[str, object]:
    """Prospective metadata written before a future execution starts."""
    require_s0_run_identity(S0_RUN_ID)
    return {
        "contract_version": CONTRACT_VERSION,
        "endpoint": CHAT_COMPLETIONS_ENDPOINT,
        "evaluator_version": EVALUATOR_VERSION,
        "expected_plan_sha256": EXPECTED_PLAN_SHA256,
        "parser_version": PARSER_VERSION,
        "request_count": EXPECTED_REQUEST_COUNT,
        "request_order_contract": REQUEST_ORDER_CONTRACT,
        "run_id": S0_RUN_ID,
        "runtime_contract_version": RUNTIME_CONTRACT_VERSION,
        "stage": S0_STAGE,
        "executor_commit": executor_commit,
    }


def evaluate_raw_output(request: S0Request, raw_output: str) -> dict[str, object]:
    """Reuse the frozen strict A/B parser; host logic only scores retained output."""
    parsed = parse_label(raw_output)
    return {
        "canonical_answer": request.canonical_answer,
        "correct": parsed == request.canonical_answer,
        "malformed": parsed is None,
        "parsed_answer": parsed,
        "score": float(parsed == request.canonical_answer),
    }


def summarize_s0_records(records: list[Mapping[str, Any]], requests: tuple[S0Request, ...]) -> dict[str, object]:
    """Classify only a complete infrastructure-valid S0 record sequence."""
    validate_s0_request_plan(requests)
    expected = {request.record_id: request for request in requests}
    observed_ids = [str(record.get("record_id")) for record in records]
    complete = (
        len(records) == len(requests)
        and set(observed_ids) == set(expected)
        and len(set(observed_ids)) == len(requests)
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
                raise S0ExecutionError(f"S0 retained record differs from authority: {key}")
        evaluation = evaluate_raw_output(request, str(record.get("raw_output", "")))
        if record.get("evaluation") != evaluation:
            raise S0ExecutionError("S0 stored evaluator result differs from recomputation")
        raw_outputs[request.record_id] = str(record.get("raw_output", ""))
    return {
        "classification": minimality.classify_s0(raw_outputs),
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
            raise S0ExecutionError(f"S0 authoritative artifact is missing: {relative}")
        hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def validate_s0_run_directory(run_dir: Path) -> dict[str, object]:
    """Accept only a finalized complete S0 run; partial evidence is never canonical."""
    requests = build_s0_request_plan()
    metadata_path = run_dir / "metadata.json"
    if not metadata_path.is_file():
        raise S0ExecutionError("S0 metadata is missing")
    metadata = json.loads(metadata_path.read_bytes().decode("utf-8"))
    require_s0_run_identity(str(metadata.get("run_id")))
    if metadata.get("contract", {}).get("expected_plan_sha256") != EXPECTED_PLAN_SHA256:
        raise S0ExecutionError("S0 metadata does not identify the frozen plan")
    records_path = run_dir / "results.jsonl"
    if not records_path.is_file():
        raise S0ExecutionError("S0 results are missing")
    records = [json.loads(line) for line in records_path.read_text(encoding="utf-8").splitlines() if line]
    summary = summarize_s0_records(records, requests)
    if summary["outcome"] != "protocol_valid":
        raise S0ExecutionError("incomplete or infrastructure-invalid S0 evidence is not a canonical complete run")
    stored_summary = json.loads((run_dir / "summary.json").read_bytes().decode("utf-8"))
    if stored_summary != summary:
        raise S0ExecutionError("S0 stored summary differs from deterministic recomputation")
    integrity = json.loads((run_dir / "integrity.json").read_bytes().decode("utf-8"))
    if integrity.get("artifact_sha256") != artifact_hashes(run_dir):
        raise S0ExecutionError("S0 physical artifact hashes differ from integrity manifest")
    return summary
