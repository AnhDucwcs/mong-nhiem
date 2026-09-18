"""Frozen, plan-driven execution contract for direct-state-vector qualification."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import run_mn006_baseline as baseline

from . import direct_state_vector as qualification
from .fingerprinting import (
    canonical_json_bytes,
    canonical_text_bytes,
    canonical_text_sha256,
    sha256_bytes,
)
from .inventory import INVENTORY_ROOT, validate_materialized_inventory
from .model import ENTITY_IDS, SourceEvent
from .oracle import replay

EXPERIMENT_ROOT = Path(__file__).resolve().parents[2]
RUNS = EXPERIMENT_ROOT / "runs"
PLAN_PATH = (
    EXPERIMENT_ROOT
    / "definition"
    / "direct-state-vector-qualification-v1"
    / "plan.json"
)
REDESIGN_PATH = EXPERIMENT_ROOT / "measurement-interface-redesign.md"
GATE_PATH = EXPERIMENT_ROOT / "direct-state-vector-construct-validity-gate.md"
EXPECTED_GATE_SHA256 = (
    "72eeb1e50d9450deff54d5acc45d71d110d8426d3a0ab8da30deb788b6cbee6f"
)
EXPECTED_RUNTIME_PARAMETERS_SHA256 = (
    "bee3d60780bf32a9e9670fb7553e875975c3b6ec88e57b75385e3db60b99d714"
)
REPOSITORY_ROOT = EXPERIMENT_ROOT.parents[3]

RUN_ID = qualification.RUN_ID
STAGE = qualification.STAGE
CONTRACT_VERSION = qualification.CONTRACT_VERSION
QUALIFICATION_CONTRACT_VERSION = qualification.QUALIFICATION_CONTRACT_VERSION
PARSER_VERSION = qualification.PARSER_VERSION
EVALUATOR_VERSION = qualification.EVALUATOR_VERSION
RUNTIME_CONTRACT_VERSION = qualification.RUNTIME_CONTRACT_VERSION
EXPECTED_PLAN_SHA256 = qualification.EXPECTED_PLAN_SHA256
EXPECTED_REDESIGN_SHA256 = qualification.EXPECTED_REDESIGN_SHA256
EXPECTED_INVENTORY_SHA256 = qualification.EXPECTED_INVENTORY_SHA256
EVIDENCE_SCHEMA_VERSION = "mn006-direct-state-vector-qualification-evidence-v1"
EXPECTED_REQUEST_COUNT = 18
Q0_COUNT = 9
Q1_COUNT = 9
REQUEST_ORDER_CONTRACT = "Q0_lexicographic_order_then_Q1_lexicographic_order"
CHAT_COMPLETIONS_ENDPOINT = "/v1/chat/completions"


def request_parameters() -> dict[str, object]:
    """Use the baseline runtime source; reject drift against its frozen fingerprint."""
    if (
        sha256_bytes(canonical_json_bytes(baseline.INFERENCE))
        != EXPECTED_RUNTIME_PARAMETERS_SHA256
    ):
        raise DirectStateVectorExecutionError(
            "baseline runtime parameters differ from frozen runtime"
        )
    return {
        "chat_template_kwargs": dict(baseline.INFERENCE["chat_template_kwargs"]),
        "max_tokens": baseline.INFERENCE["output_tokens"],
        "seed": baseline.INFERENCE["seed"],
        "temperature": baseline.INFERENCE["temperature"],
    }


def verify_static_repository() -> None:
    """Read repository identity and evidence absence without spawning Git or any process.

    Dry construction permits the current implementation edits. The real preflight
    separately requires a completely clean Git worktree and synchronized branch.
    """
    git_path = REPOSITORY_ROOT / ".git"
    if git_path.is_file():
        git_path = (
            REPOSITORY_ROOT / git_path.read_text().strip().removeprefix("gitdir: ")
        ).resolve()
    if (
        (git_path / "HEAD").read_text().strip()
        != "ref: refs/heads/codex/mn-006-distributed-state-integration"
    ):
        raise DirectStateVectorExecutionError(
            "repository branch differs from qualification branch"
        )
    require_no_evidence()


def require_no_evidence(runs: Path = RUNS) -> None:
    for name in (RUN_ID, f".{RUN_ID}.pending", f"{RUN_ID}.infrastructure-invalid"):
        if (runs / name).exists():
            raise DirectStateVectorExecutionError(
                "qualification evidence or execution residue already exists"
            )


class DirectStateVectorExecutionError(ValueError):
    """Raised when a prospective qualification differs from frozen authority."""


def require_run_identity(run_id: str) -> None:
    """Allow only the single frozen direct-state-vector qualification identity."""
    if run_id != RUN_ID:
        raise DirectStateVectorExecutionError(
            "unknown or non-qualification run identity"
        )


def verify_redesign_prerequisite(path: Path = REDESIGN_PATH) -> dict[str, object]:
    """Verify the immutable redesign decision by path, bytes, and disposition."""
    if path.resolve() != REDESIGN_PATH.resolve():
        raise DirectStateVectorExecutionError(
            "measurement-interface redesign path differs from frozen prerequisite"
        )
    try:
        payload = path.read_bytes()
    except OSError as error:
        raise DirectStateVectorExecutionError(
            "measurement-interface redesign is missing"
        ) from error
    if sha256_bytes(payload) != EXPECTED_REDESIGN_SHA256:
        raise DirectStateVectorExecutionError(
            "measurement-interface redesign SHA-256 differs from frozen prerequisite"
        )
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise DirectStateVectorExecutionError(
            "measurement-interface redesign is not UTF-8"
        ) from error
    if "`single_measurement_interface_candidate_identified`" not in text:
        raise DirectStateVectorExecutionError(
            "measurement-interface redesign disposition differs"
        )
    if "**direct ordered two-entity final-state vector**" not in text:
        raise DirectStateVectorExecutionError(
            "measurement-interface redesign selected interface differs"
        )
    return {
        "disposition": "single_measurement_interface_candidate_identified",
        "path": qualification.REDESIGN_RELATIVE_PATH,
        "selected_interface": "direct ordered two-entity final-state vector",
        "sha256": EXPECTED_REDESIGN_SHA256,
    }


def verify_inventory_prerequisite() -> dict[str, object]:
    """Revalidate the unchanged canonical semantic inventory before payload construction."""
    manifest = validate_materialized_inventory(INVENTORY_ROOT)
    if manifest.get("aggregate_inventory_sha256") != EXPECTED_INVENTORY_SHA256:
        raise DirectStateVectorExecutionError(
            "canonical baseline inventory fingerprint differs"
        )
    return {
        "aggregate_inventory_sha256": EXPECTED_INVENTORY_SHA256,
        "integrity_validated": True,
        "inventory_version": "mn006-v1-baseline-inventory-1",
    }


@dataclass(frozen=True)
class QualificationRequest:
    """One future request taken verbatim from the physical authority record."""

    authority: Mapping[str, object]
    semantic_case: qualification.DirectStateVectorCase

    @property
    def record_id(self) -> str:
        return str(self.authority["record_id"])

    @property
    def request_ordinal(self) -> int:
        return int(self.authority["request_ordinal"])

    @property
    def layer(self) -> str:
        return str(self.authority["layer"])

    @property
    def expected_vector(self) -> tuple[str, str]:
        value = self.authority.get("expected_vector")
        if not isinstance(value, list) or len(value) != 2:
            raise DirectStateVectorExecutionError(
                "authority record lacks an ordered expected vector"
            )
        return str(value[0]), str(value[1])

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
    def source(self) -> Mapping[str, object] | None:
        value = self.authority.get("source")
        if value is not None and not isinstance(value, Mapping):
            raise DirectStateVectorExecutionError("authority source is malformed")
        return value


def _read_canonical_plan(plan_path: Path = PLAN_PATH) -> dict[str, object]:
    """Read physical authority bytes before consulting any derived semantic helper."""
    if plan_path.resolve() != PLAN_PATH.resolve():
        raise DirectStateVectorExecutionError(
            "authority path differs from canonical qualification path"
        )
    try:
        payload = plan_path.read_bytes()
    except OSError as error:
        raise DirectStateVectorExecutionError(
            "direct-state-vector authority plan is missing"
        ) from error
    if sha256_bytes(payload) != EXPECTED_PLAN_SHA256:
        raise DirectStateVectorExecutionError(
            "direct-state-vector authority plan SHA-256 differs"
        )
    try:
        authority = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise DirectStateVectorExecutionError(
            "direct-state-vector authority plan is not valid UTF-8 JSON"
        ) from error
    if canonical_json_bytes(authority) != payload:
        raise DirectStateVectorExecutionError(
            "direct-state-vector authority plan bytes are not canonical UTF-8/LF JSON"
        )
    if canonical_json_bytes(authority) != canonical_json_bytes(
        qualification.validate_frozen_plan()
    ):
        raise DirectStateVectorExecutionError(
            "physical authority plan differs from frozen semantic authority"
        )
    return authority


def _source_events(source: Mapping[str, object]) -> tuple[SourceEvent, ...]:
    events = source.get("source_events")
    if not isinstance(events, list):
        raise DirectStateVectorExecutionError(
            "Q1 source has no authority event records"
        )
    converted: list[SourceEvent] = []
    for event in events:
        if not isinstance(event, Mapping):
            raise DirectStateVectorExecutionError("Q1 source event is malformed")
        converted.append(
            SourceEvent(
                event_id=str(event["event_id"]),
                global_ordinal=int(event["global_ordinal"]),
                entity_id=str(event["entity_id"]),
                assigned_state=str(event["assigned_state"]),
            )
        )
    return tuple(converted)


def _validate_q1_authority(request: QualificationRequest) -> None:
    """Replay exact authority-owned Q1 facts and preserve the frozen leakage guard."""
    source = request.source
    if source is None:
        raise DirectStateVectorExecutionError("Q1 record lacks source facts")
    query_entities = source.get("query_entities")
    permutation = source.get("entity_permutation")
    histories = source.get("entity_histories")
    if (
        not isinstance(query_entities, list)
        or len(query_entities) != 2
        or len(set(query_entities)) != 2
    ):
        raise DirectStateVectorExecutionError(
            "Q1 query identities differ from authority contract"
        )
    if not isinstance(permutation, list) or sorted(permutation) != sorted(ENTITY_IDS):
        raise DirectStateVectorExecutionError(
            "Q1 entity permutation differs from contiguous primary contract"
        )
    if not isinstance(histories, Mapping) or set(histories) != set(ENTITY_IDS):
        raise DirectStateVectorExecutionError(
            "Q1 entity histories differ from authority contract"
        )
    events = _source_events(source)
    if len(events) != 24 or [event.global_ordinal for event in events] != list(
        range(1, 25)
    ):
        raise DirectStateVectorExecutionError("Q1 event count or ordinal order differs")
    if [event.entity_id for event in events] != [
        entity for entity in permutation for _ in range(3)
    ]:
        raise DirectStateVectorExecutionError(
            "Q1 schedule is not authority-owned contiguous order"
        )
    if source.get("schedule_kind") != "contiguous_control":
        raise DirectStateVectorExecutionError("Q1 contains a non-contiguous schedule")
    if source.get("profile") != qualification.Q1_PROFILE:
        raise DirectStateVectorExecutionError(
            "Q1 profile differs from frozen authority"
        )
    if Counter(event.assigned_state for event in events) != Counter(
        {"S0": 8, "S1": 8, "S2": 8}
    ):
        raise DirectStateVectorExecutionError(
            "Q1 state-assignment frequency differs from frozen leakage guard"
        )
    replayed = replay(events, ENTITY_IDS)
    expected = tuple(replayed.entity_states[str(entity)] for entity in query_entities)
    if expected != request.expected_vector:
        raise DirectStateVectorExecutionError(
            "Q1 replay oracle differs from authority expected vector"
        )
    if qualification.vector_text(request.expected_vector) in request.public_prompt:
        raise DirectStateVectorExecutionError(
            "Q1 prompt exposes the serialized expected vector"
        )
    lowered = request.public_prompt.casefold()
    if any(
        token in lowered
        for token in (
            "canonical",
            "derived",
            "provenance",
            "target answer",
            "final-state field",
        )
    ):
        raise DirectStateVectorExecutionError(
            "Q1 prompt exposes authority or oracle metadata"
        )
    if "final" in "\n".join(event.event_id for event in events).casefold():
        raise DirectStateVectorExecutionError("Q1 event is marked as final")


def build_request_plan(
    plan_path: Path = PLAN_PATH,
    redesign_path: Path = REDESIGN_PATH,
) -> tuple[QualificationRequest, ...]:
    """Select all and only the 18 physical authority records after fail-closed validation."""
    redesign = verify_redesign_prerequisite(redesign_path)
    inventory = verify_inventory_prerequisite()
    if sha256_bytes(GATE_PATH.read_bytes()) != EXPECTED_GATE_SHA256:
        raise DirectStateVectorExecutionError("construct-validity gate SHA-256 differs")
    authority = _read_canonical_plan(plan_path)
    if canonical_json_bytes(authority) != canonical_json_bytes(
        qualification.validate_frozen_plan()
    ):
        raise DirectStateVectorExecutionError(
            "authority differs from frozen complete contract"
        )
    if authority.get("contract_version") != CONTRACT_VERSION:
        raise DirectStateVectorExecutionError(
            "interface contract differs from frozen authority"
        )
    if (
        authority.get("qualification_contract_version")
        != QUALIFICATION_CONTRACT_VERSION
    ):
        raise DirectStateVectorExecutionError(
            "qualification contract differs from frozen authority"
        )
    if authority.get("run_id") != RUN_ID or authority.get("stage") != STAGE:
        raise DirectStateVectorExecutionError(
            "run identity or stage differs from frozen authority"
        )
    if authority.get("runtime_contract_version") != RUNTIME_CONTRACT_VERSION:
        raise DirectStateVectorExecutionError(
            "runtime reference differs from frozen authority"
        )
    parser = authority.get("parser")
    if (
        not isinstance(parser, Mapping)
        or parser.get("parser_version") != PARSER_VERSION
    ):
        raise DirectStateVectorExecutionError(
            "parser reference differs from frozen authority"
        )
    if authority.get("state_vocabulary") != list(qualification.STATE_VOCABULARY):
        raise DirectStateVectorExecutionError(
            "state vocabulary differs from frozen authority"
        )
    if (
        authority.get("grammar") != qualification.DIRECT_STATE_VECTOR_GRAMMAR
        or authority.get("grammar_id") != "ordered_two_state_vector_v1"
    ):
        raise DirectStateVectorExecutionError("grammar differs from frozen authority")
    if authority.get("prerequisites") != {
        "measurement_interface_redesign": {
            "disposition": redesign["disposition"],
            "path": redesign["path"],
            "sha256": redesign["sha256"],
        },
        "semantic_inventory": {
            "aggregate_sha256": inventory["aggregate_inventory_sha256"],
            "inventory_version": inventory["inventory_version"],
        },
    }:
        raise DirectStateVectorExecutionError(
            "authority prerequisites differ from validated prerequisites"
        )
    records = authority.get("records")
    if not isinstance(records, list) or len(records) != EXPECTED_REQUEST_COUNT:
        raise DirectStateVectorExecutionError(
            "authority must contain exactly eighteen records"
        )
    cases = qualification.build_plan()
    requests = tuple(
        QualificationRequest(record, case)
        for record, case in zip(records, cases, strict=True)
    )
    validate_request_plan(requests)
    return requests


def validate_request_plan(requests: Sequence[QualificationRequest]) -> None:
    """Assert exact 9+9 authority order, payload fields, replay, and leakage constraints."""
    if len(requests) != EXPECTED_REQUEST_COUNT:
        raise DirectStateVectorExecutionError(
            "qualification request count differs from frozen 18-record plan"
        )
    if [request.request_ordinal for request in requests] != list(range(1, 19)):
        raise DirectStateVectorExecutionError(
            "qualification request order differs from frozen authority"
        )
    if [request.layer for request in requests[:Q0_COUNT]] != [
        qualification.Q0_LAYER
    ] * Q0_COUNT or [request.layer for request in requests[Q0_COUNT:]] != [
        qualification.Q1_LAYER
    ] * Q1_COUNT:
        raise DirectStateVectorExecutionError(
            "Q0/Q1 layer order or count differs from frozen authority"
        )
    if [request.expected_vector for request in requests[:Q0_COUNT]] != list(
        qualification.VECTOR_ORDER
    ) or [request.expected_vector for request in requests[Q0_COUNT:]] != list(
        qualification.VECTOR_ORDER
    ):
        raise DirectStateVectorExecutionError(
            "per-layer ordered vector coverage differs from frozen authority"
        )
    if [dict(request.authority) for request in requests] != [
        case.authority_dict() for case in qualification.build_plan()
    ]:
        raise DirectStateVectorExecutionError(
            "authority records differ from frozen semantic plan"
        )
    for request in requests:
        if (
            request.grammar_id != "ordered_two_state_vector_v1"
            or request.grammar != qualification.DIRECT_STATE_VECTOR_GRAMMAR
            or not request.grammar.endswith("\n")
        ):
            raise DirectStateVectorExecutionError(
                "request grammar differs from frozen vector grammar"
            )
        prompt_bytes = canonical_text_bytes(request.public_prompt)
        if prompt_bytes != request.public_prompt.encode("utf-8"):
            raise DirectStateVectorExecutionError(
                "request prompt is not canonical UTF-8/LF"
            )
        if canonical_text_sha256(request.public_prompt) != request.authority.get(
            "public_prompt_sha256"
        ):
            raise DirectStateVectorExecutionError(
                "request prompt fingerprint differs from authority"
            )
        if request.layer == qualification.Q0_LAYER:
            if request.source is not None:
                raise DirectStateVectorExecutionError(
                    "Q0 must not contain state-history source facts"
                )
        else:
            _validate_q1_authority(request)


def build_request_payload(request: QualificationRequest) -> dict[str, object]:
    """Construct the one future chat payload solely from physical authority fields."""
    if dict(request.authority) != request.semantic_case.authority_dict():
        raise DirectStateVectorExecutionError(
            "request changed after authority validation"
        )
    parameters = request_parameters()
    prompt_bytes = canonical_text_bytes(request.public_prompt)
    if prompt_bytes != request.public_prompt.encode("utf-8"):
        raise DirectStateVectorExecutionError(
            "payload prompt is not canonical UTF-8/LF"
        )
    payload: dict[str, object] = {
        "chat_template_kwargs": parameters["chat_template_kwargs"],
        "grammar": request.grammar,
        "max_tokens": parameters["max_tokens"],
        "messages": [{"role": "user", "content": prompt_bytes.decode("utf-8")}],
        "seed": parameters["seed"],
        "temperature": parameters["temperature"],
    }
    if set(payload) != {
        "chat_template_kwargs",
        "grammar",
        "max_tokens",
        "messages",
        "seed",
        "temperature",
    }:
        raise DirectStateVectorExecutionError(
            "payload field set differs from frozen runtime contract"
        )
    return payload


def plan_entry(request: QualificationRequest) -> dict[str, object]:
    return {
        **dict(request.authority),
        "layer_ordinal": ((request.request_ordinal - 1) % 9) + 1,
    }


def dry_construction(
    plan_path: Path = PLAN_PATH,
    redesign_path: Path = REDESIGN_PATH,
) -> tuple[dict[str, object], ...]:
    """Materialize all exact payloads in memory only; no network, process, or evidence write."""
    verify_static_repository()
    requests = build_request_plan(plan_path, redesign_path)
    entries = tuple(
        {**plan_entry(request), "payload": build_request_payload(request)}
        for request in requests
    )
    if (
        len(entries) != EXPECTED_REQUEST_COUNT
        or sum(entry["layer"] == qualification.Q0_LAYER for entry in entries)
        != Q0_COUNT
        or sum(entry["layer"] == qualification.Q1_LAYER for entry in entries)
        != Q1_COUNT
    ):
        raise DirectStateVectorExecutionError(
            "dry construction selected unauthorized qualification records"
        )
    return entries


def contract_metadata(
    executor_commit: str,
    *,
    redesign: Mapping[str, object],
    inventory: Mapping[str, object],
) -> dict[str, object]:
    require_run_identity(RUN_ID)
    return {
        "contract_version": CONTRACT_VERSION,
        "endpoint": CHAT_COMPLETIONS_ENDPOINT,
        "evaluator_version": EVALUATOR_VERSION,
        "executor_commit": executor_commit,
        "expected_plan_sha256": EXPECTED_PLAN_SHA256,
        "gate_sha256": EXPECTED_GATE_SHA256,
        "parser_version": PARSER_VERSION,
        "qualification_contract_version": QUALIFICATION_CONTRACT_VERSION,
        "request_count": EXPECTED_REQUEST_COUNT,
        "request_order_contract": REQUEST_ORDER_CONTRACT,
        "run_id": RUN_ID,
        "runtime_contract_version": RUNTIME_CONTRACT_VERSION,
        "stage": STAGE,
        "inventory_prerequisite": dict(inventory),
        "redesign_prerequisite": dict(redesign),
    }


def evaluate_raw_output(
    request: QualificationRequest, raw_output: str
) -> dict[str, object]:
    """Reuse the frozen strict vector parser and exact evaluator for every layer."""
    if dict(request.authority) != request.semantic_case.authority_dict():
        raise DirectStateVectorExecutionError("evaluator input differs from authority")
    result = qualification.score(request.semantic_case, raw_output)
    return {**result, "score": float(bool(result["correct"]))}


def summarize_records(
    records: Sequence[Mapping[str, Any]], requests: Sequence[QualificationRequest]
) -> dict[str, object]:
    """Classify only a full, ordered, infrastructure-valid retained sequence."""
    validate_request_plan(requests)
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
            "qualification_status": "infrastructure_invalid",
            "request_order_contract": REQUEST_ORDER_CONTRACT,
        }
    outputs: dict[str, str] = {}
    for request, record in zip(requests, records, strict=True):
        for key, value in plan_entry(request).items():
            if record.get(key) != value:
                raise DirectStateVectorExecutionError(
                    f"retained record differs from authority: {key}"
                )
        evaluation = evaluate_raw_output(request, str(record.get("raw_output", "")))
        if record.get("evaluation") != evaluation:
            raise DirectStateVectorExecutionError(
                "stored vector evaluation differs from frozen recomputation"
            )
        outputs[request.record_id] = str(record.get("raw_output", ""))
    summary = qualification.classify_results(outputs)
    return {
        **summary,
        "completed_requests": len(records),
        "expected_requests": len(requests),
        "infrastructure_failure_count": 0,
        "request_order_contract": REQUEST_ORDER_CONTRACT,
    }


def artifact_hashes(run_dir: Path) -> dict[str, str]:
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
            raise DirectStateVectorExecutionError(
                f"authoritative artifact is missing: {relative}"
            )
        hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def validate_run_directory(
    run_dir: Path, plan_path: Path = PLAN_PATH, redesign_path: Path = REDESIGN_PATH
) -> dict[str, object]:
    """Accept only complete canonical evidence after all authority checks recompute."""
    if run_dir.name != RUN_ID:
        raise DirectStateVectorExecutionError(
            "only canonical run identity is accepted; pending evidence is noncanonical"
        )
    return validate_complete_artifacts(run_dir, plan_path, redesign_path)


def _read_json(path: Path) -> dict[str, Any]:
    payload = path.read_bytes()
    value = json.loads(payload)
    if not isinstance(value, dict) or canonical_json_bytes(value) != payload:
        raise DirectStateVectorExecutionError(f"noncanonical JSON bytes: {path.name}")
    return value


def validate_runtime_metadata(metadata: Mapping[str, Any]) -> None:
    request_parameters()
    runtime = metadata.get("runtime", {})
    if any(
        runtime.get(key) != value for key, value in baseline.EXPECTED_RUNTIME.items()
    ):
        raise DirectStateVectorExecutionError("runtime identity differs")
    if (
        runtime.get("executable") != str(baseline.DEFAULT_SERVER)
        or runtime.get("backend") != "llama.cpp"
    ):
        raise DirectStateVectorExecutionError("runtime executable differs")
    model = metadata.get("model", {})
    if (
        model.get("sha256") != baseline.EXPECTED_MODEL_SHA256
        or model.get("path") != str(baseline.DEFAULT_MODEL)
        or model.get("subject") != "llama-3.2-3b"
    ):
        raise DirectStateVectorExecutionError("model identity differs")
    if metadata.get("runtime_parameters") != baseline.INFERENCE:
        raise DirectStateVectorExecutionError("runtime parameters differ")
    if metadata.get("server_command") != baseline.server_command(
        baseline.DEFAULT_SERVER, baseline.DEFAULT_MODEL
    ):
        raise DirectStateVectorExecutionError("server command differs")
    if metadata.get("repository", {}).get("dirty") is not False:
        raise DirectStateVectorExecutionError("execution repository was not clean")
    environment = metadata.get("start_environment", {})
    gpu = environment.get("gpu", {})
    if (
        not gpu.get("gpu_query", {}).get("available")
        or not gpu.get("compute_query", {}).get("available")
        or not gpu.get("gpus")
    ):
        raise DirectStateVectorExecutionError(
            "mandatory preflight GPU telemetry is missing"
        )
    if (
        gpu.get("compute_processes") != []
        or environment.get("local_model_processes") != []
    ):
        raise DirectStateVectorExecutionError("preflight environment was not clean")


def validate_complete_artifacts(
    run_dir: Path, plan_path: Path = PLAN_PATH, redesign_path: Path = REDESIGN_PATH
) -> dict[str, object]:
    """Validate finished physical artifacts before promotion; never accepts partial data."""
    expected_files = {
        "metadata.json",
        "results.jsonl",
        "summary.json",
        "integrity.json",
        "server-lifecycle.json",
        "raw/llama-server.stdout.txt",
        "raw/llama-server.stderr.txt",
    }
    if {
        path.relative_to(run_dir).as_posix()
        for path in run_dir.rglob("*")
        if path.is_file()
    } != expected_files:
        raise DirectStateVectorExecutionError(
            "completed artifact set is missing or contains unexpected files"
        )
    redesign = verify_redesign_prerequisite(redesign_path)
    inventory = verify_inventory_prerequisite()
    requests = build_request_plan(plan_path, redesign_path)
    metadata_path = run_dir / "metadata.json"
    if not metadata_path.is_file():
        raise DirectStateVectorExecutionError("metadata is missing")
    metadata = _read_json(metadata_path)
    require_run_identity(str(metadata.get("run_id")))
    validate_runtime_metadata(metadata)
    if metadata.get("contract") != contract_metadata(
        str(metadata.get("repository", {}).get("commit", "")),
        redesign=redesign,
        inventory=inventory,
    ):
        raise DirectStateVectorExecutionError(
            "metadata contract differs from frozen qualification contract"
        )
    records_path = run_dir / "results.jsonl"
    if not records_path.is_file():
        raise DirectStateVectorExecutionError("results are missing")
    lines = records_path.read_bytes().splitlines(keepends=True)
    records = [json.loads(line) for line in lines]
    if any(
        canonical_json_bytes(record) != line
        for record, line in zip(records, lines, strict=True)
    ):
        raise DirectStateVectorExecutionError(
            "results are not canonical UTF-8/LF JSONL"
        )
    for request, record in zip(requests, records):
        if record.get("evidence_schema_version") != EVIDENCE_SCHEMA_VERSION:
            raise DirectStateVectorExecutionError("record evidence schema differs")
        if record.get("raw_request_payload") != build_request_payload(request):
            raise DirectStateVectorExecutionError("retained request payload differs")
        if (
            record.get("run_id") != RUN_ID
            or record.get("runtime") != metadata["runtime"]
            or record.get("model") != metadata["model"]
        ):
            raise DirectStateVectorExecutionError(
                "record run/runtime/model identity differs"
            )
        response = record.get("response")
        if (
            not isinstance(response, dict)
            or json.loads(record["raw_response_payload_utf8"]) != response
        ):
            raise DirectStateVectorExecutionError(
                "raw response differs from retained response"
            )
        if response["choices"][0]["message"].get("content", "") != record.get(
            "raw_output"
        ):
            raise DirectStateVectorExecutionError("raw output differs from response")
        if (
            not isinstance(record.get("expected_prompt_tokens"), int)
            or record.get("usage") != response.get("usage")
            or record.get("expected_prompt_tokens")
            != response.get("usage", {}).get("prompt_tokens")
        ):
            raise DirectStateVectorExecutionError("token metadata differs")
        if record.get("finish_reason") != response["choices"][0].get(
            "finish_reason"
        ) or not isinstance(record.get("timing"), dict):
            raise DirectStateVectorExecutionError(
                "finish/timing metadata missing or inconsistent"
            )
        if record.get("error") is not None:
            raise DirectStateVectorExecutionError(
                "completed record retains an infrastructure error"
            )
    summary = summarize_records(records, requests)
    if summary["outcome"] != "protocol_valid":
        raise DirectStateVectorExecutionError(
            "incomplete or infrastructure-invalid evidence is not canonical"
        )
    stored_summary = _read_json(run_dir / "summary.json")
    if stored_summary != summary:
        raise DirectStateVectorExecutionError(
            "stored summary differs from deterministic recomputation"
        )
    lifecycle = _read_json(run_dir / "server-lifecycle.json")
    if (
        lifecycle.get("started") is not True
        or lifecycle.get("expected_termination") is not True
    ):
        raise DirectStateVectorExecutionError(
            "server lifecycle is incomplete or abnormal"
        )
    if (
        lifecycle.get("failure") is not None
        or lifecycle.get("health_at_ready", {}).get("reachable") is not True
        or lifecycle.get("health_after_cleanup", {}).get("reachable") is not False
    ):
        raise DirectStateVectorExecutionError(
            "server lifecycle health or cleanup failure"
        )
    if lifecycle.get("command") != metadata["server_command"] or not isinstance(
        lifecycle.get("pid"), int
    ):
        raise DirectStateVectorExecutionError("server lifecycle identity differs")
    for field in (
        "environment_at_ready",
        "environment_before_cleanup",
        "end_environment",
    ):
        if not isinstance(lifecycle.get(field), dict):
            raise DirectStateVectorExecutionError(
                "lifecycle environment capture is missing"
            )
    end = lifecycle["end_environment"]
    if (
        end.get("local_model_processes") != []
        or end.get("gpu", {}).get("compute_processes") != []
    ):
        raise DirectStateVectorExecutionError(
            "controlled cleanup left a model or compute process"
        )
    integrity = _read_json(run_dir / "integrity.json")
    if (
        integrity.get("run_id") != RUN_ID
        or integrity.get("plan_sha256") != EXPECTED_PLAN_SHA256
    ):
        raise DirectStateVectorExecutionError("integrity manifest identity differs")
    if integrity.get("artifact_sha256") != artifact_hashes(run_dir):
        raise DirectStateVectorExecutionError(
            "physical artifact hashes differ from integrity manifest"
        )
    return summary
