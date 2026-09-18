"""Frozen executor boundary for the explicit-relation direct-rule control."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import explicit_relation as diagnostic
from . import output_selection_execution as s0_execution
from . import output_selection_s1_execution as s1_execution
from .fingerprinting import (
    canonical_json_bytes,
    canonical_text_bytes,
    canonical_text_sha256,
    sha256_bytes,
)
from .label_selection import GRAMMAR_AB, LABELS, parse_label

EXPERIMENT_ROOT = Path(__file__).resolve().parents[2]
RUNS = EXPERIMENT_ROOT / "runs"
PLAN_PATH = (
    EXPERIMENT_ROOT / "definition" / "explicit-relation-direct-rule-v1" / "plan.json"
)
CAUSAL_REVIEW_PATH = EXPERIMENT_ROOT / "recurring-fixed-label-causal-review.md"
S0_RUN_DIRECTORY = RUNS / "output-selection-s0-run-0001"
S1_RUN_DIRECTORY = RUNS / "output-selection-s1-run-0001"

RUN_ID = diagnostic.RUN_ID
STAGE = diagnostic.STAGE
CONTRACT_VERSION = diagnostic.CONTRACT_VERSION
EVIDENCE_SCHEMA_VERSION = "mn006-explicit-relation-direct-rule-evidence-v1"
PARSER_VERSION = diagnostic.PARSER_VERSION
EVALUATOR_VERSION = "mn006-explicit-relation-direct-rule-evaluator-v1"
RUNTIME_CONTRACT_VERSION = diagnostic.RUNTIME_CONTRACT_VERSION
EXPECTED_PLAN_SHA256 = diagnostic.EXPECTED_PLAN_SHA256
EXPECTED_CAUSAL_REVIEW_SHA256 = diagnostic.EXPECTED_CAUSAL_REVIEW_SHA256
EXPECTED_REQUEST_COUNT = 2
REQUEST_ORDER_CONTRACT = (
    "explicit_relation_direct_rule; canonical_plan_request_ordinal_ascending"
)
CHAT_COMPLETIONS_ENDPOINT = "/v1/chat/completions"
REQUEST_PARAMETERS = {
    "chat_template_kwargs": {},
    "max_tokens": 16,
    "seed": 42,
    "temperature": 0.0,
}


class ExplicitRelationExecutionError(ValueError):
    """Raised when prospective execution differs from frozen authority."""


def require_run_identity(run_id: str) -> None:
    """Accept only the single frozen explicit-relation run namespace."""
    if run_id != RUN_ID:
        raise ExplicitRelationExecutionError(
            "unknown or non-explicit-relation run identity"
        )


def verify_s0_prerequisite(run_dir: Path = S0_RUN_DIRECTORY) -> dict[str, object]:
    """Require physical-integrity-valid S0 evidence with the exact frozen result."""
    try:
        summary = s0_execution.validate_s0_run_directory(run_dir)
    except (OSError, UnicodeError, ValueError) as error:
        raise ExplicitRelationExecutionError(
            "S0 prerequisite evidence is missing, incomplete, or invalid"
        ) from error
    if (
        summary.get("outcome") != "protocol_valid"
        or summary.get("classification") != "direct_copy_supported"
    ):
        raise ExplicitRelationExecutionError(
            "S0 must be protocol-valid / direct_copy_supported"
        )
    return {
        "classification": "direct_copy_supported",
        "integrity_validated": True,
        "outcome": "protocol_valid",
        "run_id": "output-selection-s0-run-0001",
    }


def verify_s1_prerequisite(
    run_dir: Path = S1_RUN_DIRECTORY, s0_run_dir: Path = S0_RUN_DIRECTORY
) -> dict[str, object]:
    """Require physical-integrity-valid S1 evidence with the exact frozen result."""
    try:
        summary = s1_execution.validate_s1_run_directory(run_dir, s0_run_dir=s0_run_dir)
    except (OSError, UnicodeError, ValueError) as error:
        raise ExplicitRelationExecutionError(
            "S1 prerequisite evidence is missing, incomplete, or invalid"
        ) from error
    if (
        summary.get("outcome") != "protocol_valid"
        or summary.get("classification") != "fixed_label_preference_recurred"
    ):
        raise ExplicitRelationExecutionError(
            "S1 must be protocol-valid / fixed_label_preference_recurred"
        )
    return {
        "classification": "fixed_label_preference_recurred",
        "integrity_validated": True,
        "outcome": "protocol_valid",
        "run_id": "output-selection-s1-run-0001",
    }


def verify_causal_review(review_path: Path = CAUSAL_REVIEW_PATH) -> dict[str, object]:
    """Verify the immutable causal-review bytes and frozen disposition."""
    if review_path.resolve() != CAUSAL_REVIEW_PATH.resolve():
        raise ExplicitRelationExecutionError(
            "causal-review path differs from frozen prerequisite"
        )
    try:
        payload = review_path.read_bytes()
    except OSError as error:
        raise ExplicitRelationExecutionError("causal review is missing") from error
    if sha256_bytes(payload) != EXPECTED_CAUSAL_REVIEW_SHA256:
        raise ExplicitRelationExecutionError(
            "causal-review SHA-256 differs from frozen prerequisite"
        )
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ExplicitRelationExecutionError("causal review is not UTF-8") from error
    if "`next_minimal_diagnostic_identified`" not in text:
        raise ExplicitRelationExecutionError(
            "causal-review disposition differs from frozen prerequisite"
        )
    return {
        "disposition": "next_minimal_diagnostic_identified",
        "path": diagnostic.CAUSAL_REVIEW_PATH,
        "sha256": EXPECTED_CAUSAL_REVIEW_SHA256,
    }


@dataclass(frozen=True)
class ExplicitRelationRequest:
    """One prospective request loaded verbatim from canonical authority."""

    authority: Mapping[str, object]

    @property
    def record_id(self) -> str:
        return str(self.authority["record_id"])

    @property
    def request_ordinal(self) -> int:
        return int(self.authority["request_ordinal"])

    @property
    def relation(self) -> str:
        return str(self.authority["relation"])

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


def _read_canonical_plan(plan_path: Path = PLAN_PATH) -> dict[str, object]:
    """Read and verify exact authority bytes before selecting any request."""
    try:
        payload = plan_path.read_bytes()
    except OSError as error:
        raise ExplicitRelationExecutionError(
            "explicit-relation authority plan is missing"
        ) from error
    if sha256_bytes(payload) != EXPECTED_PLAN_SHA256:
        raise ExplicitRelationExecutionError(
            "explicit-relation plan SHA-256 differs from frozen authority"
        )
    try:
        authority = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ExplicitRelationExecutionError(
            "explicit-relation plan is not valid canonical JSON"
        ) from error
    if canonical_json_bytes(authority) != payload:
        raise ExplicitRelationExecutionError(
            "explicit-relation plan bytes are not canonical UTF-8/LF JSON"
        )
    if authority != diagnostic.validate_frozen_plan():
        raise ExplicitRelationExecutionError(
            "explicit-relation plan differs from frozen semantic authority"
        )
    return authority


def build_request_plan(
    plan_path: Path = PLAN_PATH,
    s0_run_dir: Path = S0_RUN_DIRECTORY,
    s1_run_dir: Path = S1_RUN_DIRECTORY,
    review_path: Path = CAUSAL_REVIEW_PATH,
) -> tuple[ExplicitRelationRequest, ...]:
    """Load exactly two frozen requests after every prerequisite validates."""
    s0_prerequisite = verify_s0_prerequisite(s0_run_dir)
    s1_prerequisite = verify_s1_prerequisite(s1_run_dir, s0_run_dir)
    review_prerequisite = verify_causal_review(review_path)
    authority = _read_canonical_plan(plan_path)
    if authority.get("contract_version") != CONTRACT_VERSION:
        raise ExplicitRelationExecutionError(
            "plan contract differs from frozen executor contract"
        )
    if authority.get("run_id") != RUN_ID or authority.get("stage") != STAGE:
        raise ExplicitRelationExecutionError(
            "plan run or stage identity differs from frozen contract"
        )
    if authority.get("parser_version") != PARSER_VERSION:
        raise ExplicitRelationExecutionError(
            "plan parser differs from frozen strict A/B parser"
        )
    if authority.get("runtime_contract_version") != RUNTIME_CONTRACT_VERSION:
        raise ExplicitRelationExecutionError(
            "plan runtime reference differs from frozen qualified runtime"
        )
    if authority.get("prerequisites") != {
        "causal_review": review_prerequisite,
        "s0": {
            key: value
            for key, value in s0_prerequisite.items()
            if key != "integrity_validated"
        },
        "s1": {
            key: value
            for key, value in s1_prerequisite.items()
            if key != "integrity_validated"
        },
    }:
        raise ExplicitRelationExecutionError(
            "plan prerequisite identities differ from validated evidence"
        )
    records = authority.get("records")
    if not isinstance(records, list) or len(records) != EXPECTED_REQUEST_COUNT:
        raise ExplicitRelationExecutionError(
            "plan must contain exactly two explicit-relation records"
        )
    requests = tuple(ExplicitRelationRequest(record) for record in records)
    validate_request_plan(requests)
    return requests


def validate_request_plan(requests: tuple[ExplicitRelationRequest, ...]) -> None:
    """Check exact plan-owned order, relations, labels, grammar, prompts, and hashes."""
    if len(requests) != EXPECTED_REQUEST_COUNT:
        raise ExplicitRelationExecutionError(
            "request count differs from frozen two-record plan"
        )
    if [request.request_ordinal for request in requests] != [1, 2]:
        raise ExplicitRelationExecutionError(
            "request order differs from canonical plan"
        )
    if [request.relation for request in requests] != ["different", "equal"]:
        raise ExplicitRelationExecutionError(
            "relation order differs from canonical plan"
        )
    if [request.canonical_answer for request in requests] != ["B", "A"]:
        raise ExplicitRelationExecutionError(
            "expected labels differ from canonical plan"
        )
    if [dict(request.authority) for request in requests] != [
        case.authority_dict() for case in diagnostic.build_plan()
    ]:
        raise ExplicitRelationExecutionError(
            "request records differ from frozen semantic authority"
        )
    for request in requests:
        if request.authority.get("stage") != STAGE:
            raise ExplicitRelationExecutionError(
                "request contains an unauthorized stage"
            )
        if request.grammar_id != "A_then_B" or request.grammar != GRAMMAR_AB:
            raise ExplicitRelationExecutionError(
                "request grammar differs from frozen G_AB"
            )
        if request.canonical_answer not in LABELS:
            raise ExplicitRelationExecutionError(
                "expected label falls outside strict A/B vocabulary"
            )
        prompt_bytes = canonical_text_bytes(request.public_prompt)
        if prompt_bytes != request.public_prompt.encode("utf-8"):
            raise ExplicitRelationExecutionError(
                "prompt is not canonical UTF-8/LF text"
            )
        if canonical_text_sha256(request.public_prompt) != request.authority.get(
            "public_prompt_sha256"
        ):
            raise ExplicitRelationExecutionError(
                "prompt fingerprint differs from canonical plan"
            )
        lowered = request.public_prompt.lower()
        if (
            "e01 state" in lowered
            or "e02 state" in lowered
            or "use this mapping" in lowered
        ):
            raise ExplicitRelationExecutionError(
                "prompt reintroduces state comparison or mapping-table semantics"
            )


def build_request_payload(request: ExplicitRelationRequest) -> dict[str, object]:
    """Construct a future payload solely from authority fields and frozen runtime values."""
    prompt_bytes = canonical_text_bytes(request.public_prompt)
    if prompt_bytes != request.public_prompt.encode("utf-8"):
        raise ExplicitRelationExecutionError(
            "payload prompt is not canonical UTF-8/LF text"
        )
    payload: dict[str, object] = {
        "chat_template_kwargs": REQUEST_PARAMETERS["chat_template_kwargs"],
        "grammar": request.grammar,
        "max_tokens": REQUEST_PARAMETERS["max_tokens"],
        "messages": [{"role": "user", "content": prompt_bytes.decode("utf-8")}],
        "seed": REQUEST_PARAMETERS["seed"],
        "temperature": REQUEST_PARAMETERS["temperature"],
    }
    if set(payload) != {
        "chat_template_kwargs",
        "grammar",
        "max_tokens",
        "messages",
        "seed",
        "temperature",
    }:
        raise ExplicitRelationExecutionError(
            "payload field set differs from frozen contract"
        )
    return payload


def plan_entry(request: ExplicitRelationRequest) -> dict[str, object]:
    """Return authority-owned fields copied into future evidence."""
    return dict(request.authority)


def dry_construction(
    plan_path: Path = PLAN_PATH,
    s0_run_dir: Path = S0_RUN_DIRECTORY,
    s1_run_dir: Path = S1_RUN_DIRECTORY,
    review_path: Path = CAUSAL_REVIEW_PATH,
) -> tuple[dict[str, object], ...]:
    """Build payloads in memory only; perform no server, network, or evidence writes."""
    requests = build_request_plan(plan_path, s0_run_dir, s1_run_dir, review_path)
    entries: list[dict[str, object]] = []
    for request in requests:
        payload = build_request_payload(request)
        if payload["messages"] != [{"role": "user", "content": request.public_prompt}]:
            raise ExplicitRelationExecutionError(
                "payload prompt differs from authority"
            )
        if payload["grammar"] != GRAMMAR_AB:
            raise ExplicitRelationExecutionError(
                "payload grammar differs from frozen G_AB"
            )
        entries.append({**plan_entry(request), "payload": payload})
    if len(entries) != EXPECTED_REQUEST_COUNT or any(
        entry["stage"] != STAGE for entry in entries
    ):
        raise ExplicitRelationExecutionError(
            "dry construction selected an unauthorized record"
        )
    return tuple(entries)


def contract_metadata(
    executor_commit: str,
    *,
    s0_prerequisite: Mapping[str, object],
    s1_prerequisite: Mapping[str, object],
    causal_review: Mapping[str, object],
) -> dict[str, object]:
    """Define future metadata without fabricating any inference-dependent value."""
    require_run_identity(RUN_ID)
    return {
        "causal_review": dict(causal_review),
        "contract_version": CONTRACT_VERSION,
        "endpoint": CHAT_COMPLETIONS_ENDPOINT,
        "evaluator_version": EVALUATOR_VERSION,
        "executor_commit": executor_commit,
        "expected_plan_sha256": EXPECTED_PLAN_SHA256,
        "parser_version": PARSER_VERSION,
        "request_count": EXPECTED_REQUEST_COUNT,
        "request_order_contract": REQUEST_ORDER_CONTRACT,
        "run_id": RUN_ID,
        "runtime_contract_version": RUNTIME_CONTRACT_VERSION,
        "s0_prerequisite": dict(s0_prerequisite),
        "s1_prerequisite": dict(s1_prerequisite),
        "stage": STAGE,
    }


def evaluate_raw_output(
    request: ExplicitRelationRequest, raw_output: str
) -> dict[str, object]:
    """Reuse the frozen strict A/B parser without normalization or extraction."""
    parsed = parse_label(raw_output)
    return {
        "canonical_answer": request.canonical_answer,
        "correct": parsed == request.canonical_answer,
        "malformed": parsed is None,
        "parsed_answer": parsed,
        "score": float(parsed == request.canonical_answer),
    }


def summarize_records(
    records: list[Mapping[str, Any]], requests: tuple[ExplicitRelationRequest, ...]
) -> dict[str, object]:
    """Classify only a complete, exact-order, infrastructure-valid record sequence."""
    validate_request_plan(requests)
    expected = {request.record_id: request for request in requests}
    expected_ids = [request.record_id for request in requests]
    complete = (
        len(records) == len(requests)
        and [str(record.get("record_id")) for record in records] == expected_ids
        and all(record.get("infrastructure_status") == "complete" for record in records)
    )
    if not complete:
        return {
            "classification": None,
            "completed_requests": sum(
                record.get("infrastructure_status") == "complete" for record in records
            ),
            "expected_requests": len(requests),
            "infrastructure_failure_count": sum(
                record.get("infrastructure_status") != "complete" for record in records
            ),
            "outcome": "infrastructure_invalid",
            "request_order_contract": REQUEST_ORDER_CONTRACT,
        }
    raw_outputs: dict[str, str] = {}
    for record in records:
        request = expected[str(record["record_id"])]
        for key, value in plan_entry(request).items():
            if record.get(key) != value:
                raise ExplicitRelationExecutionError(
                    f"retained record differs from authority: {key}"
                )
        evaluation = evaluate_raw_output(request, str(record.get("raw_output", "")))
        if record.get("evaluation") != evaluation:
            raise ExplicitRelationExecutionError(
                "stored evaluator result differs from recomputation"
            )
        raw_outputs[request.record_id] = str(record.get("raw_output", ""))
    return {
        "classification": diagnostic.classify(raw_outputs),
        "completed_requests": len(records),
        "expected_requests": len(requests),
        "infrastructure_failure_count": 0,
        "malformed_count": sum(
            bool(
                evaluate_raw_output(request, raw_outputs[request.record_id])[
                    "malformed"
                ]
            )
            for request in requests
        ),
        "outcome": "protocol_valid",
        "request_order_contract": REQUEST_ORDER_CONTRACT,
    }


def artifact_hashes(run_dir: Path) -> dict[str, str]:
    """Fingerprint every completed authority artifact by physical bytes."""
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
            raise ExplicitRelationExecutionError(
                f"authoritative artifact is missing: {relative}"
            )
        hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def validate_run_directory(
    run_dir: Path,
    s0_run_dir: Path = S0_RUN_DIRECTORY,
    s1_run_dir: Path = S1_RUN_DIRECTORY,
    review_path: Path = CAUSAL_REVIEW_PATH,
) -> dict[str, object]:
    """Accept only finalized complete evidence after revalidating every prerequisite."""
    s0_prerequisite = verify_s0_prerequisite(s0_run_dir)
    s1_prerequisite = verify_s1_prerequisite(s1_run_dir, s0_run_dir)
    causal_review = verify_causal_review(review_path)
    requests = build_request_plan(PLAN_PATH, s0_run_dir, s1_run_dir, review_path)
    metadata_path = run_dir / "metadata.json"
    if not metadata_path.is_file():
        raise ExplicitRelationExecutionError("metadata is missing")
    metadata = json.loads(metadata_path.read_bytes().decode("utf-8"))
    require_run_identity(str(metadata.get("run_id")))
    contract = metadata.get("contract")
    if (
        not isinstance(contract, dict)
        or contract.get("expected_plan_sha256") != EXPECTED_PLAN_SHA256
    ):
        raise ExplicitRelationExecutionError(
            "metadata does not identify frozen authority"
        )
    if metadata.get("s0_prerequisite") != s0_prerequisite:
        raise ExplicitRelationExecutionError(
            "metadata does not retain validated S0 prerequisite"
        )
    if metadata.get("s1_prerequisite") != s1_prerequisite:
        raise ExplicitRelationExecutionError(
            "metadata does not retain validated S1 prerequisite"
        )
    if metadata.get("causal_review") != causal_review:
        raise ExplicitRelationExecutionError(
            "metadata does not retain validated causal review"
        )
    records_path = run_dir / "results.jsonl"
    if not records_path.is_file():
        raise ExplicitRelationExecutionError("results are missing")
    records = [
        json.loads(line)
        for line in records_path.read_text(encoding="utf-8").splitlines()
        if line
    ]
    summary = summarize_records(records, requests)
    if summary["outcome"] != "protocol_valid":
        raise ExplicitRelationExecutionError(
            "incomplete or infrastructure-invalid evidence is not canonical"
        )
    stored_summary = json.loads((run_dir / "summary.json").read_bytes().decode("utf-8"))
    if stored_summary != summary:
        raise ExplicitRelationExecutionError(
            "stored summary differs from deterministic recomputation"
        )
    integrity = json.loads((run_dir / "integrity.json").read_bytes().decode("utf-8"))
    if integrity.get("artifact_sha256") != artifact_hashes(run_dir):
        raise ExplicitRelationExecutionError(
            "physical artifact hashes differ from integrity manifest"
        )
    return summary
