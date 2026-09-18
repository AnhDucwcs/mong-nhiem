from __future__ import annotations

import hashlib
import json
import socket
import subprocess
import sys
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "research/experiments/prototypes/mn-006-distributed-state-integration"
SCRIPTS = BASE / "scripts"
sys.path.insert(0, str(SCRIPTS))

import run_mn006_baseline as baseline
import run_mn006_direct_state_vector_qualification as runner
from mn006 import direct_state_vector as qualification
from mn006 import direct_state_vector_execution as execution
from mn006.fingerprinting import canonical_json_bytes


def _snapshot() -> dict[str, str]:
    roots = [BASE / "runs", BASE / "definition"]
    roots.extend(
        path
        for path in BASE.parent.iterdir()
        if path.name.startswith(("mn-003", "mn-004", "mn-005"))
    )
    paths = [
        path
        for root in roots
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    ]
    paths.extend([execution.REDESIGN_PATH, execution.GATE_PATH])
    return {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(paths)
    }


def _environment() -> dict:
    return {
        "gpu": {
            "gpu_query": {"available": True},
            "compute_query": {"available": True},
            "gpus": [{"name": "synthetic-test-fixture"}],
            "compute_processes": [],
        },
        "local_model_processes": [],
    }


def _metadata() -> dict:
    return {
        "run_id": execution.RUN_ID,
        "repository": {"commit": "synthetic-test-commit", "dirty": False},
        "contract": execution.contract_metadata(
            "synthetic-test-commit",
            redesign=execution.verify_redesign_prerequisite(),
            inventory=execution.verify_inventory_prerequisite(),
        ),
        "runtime": {
            **baseline.EXPECTED_RUNTIME,
            "backend": "llama.cpp",
            "executable": str(baseline.DEFAULT_SERVER),
        },
        "runtime_parameters": deepcopy(baseline.INFERENCE),
        "model": {
            "path": str(baseline.DEFAULT_MODEL),
            "sha256": baseline.EXPECTED_MODEL_SHA256,
            "subject": "llama-3.2-3b",
        },
        "server_command": baseline.server_command(
            baseline.DEFAULT_SERVER, baseline.DEFAULT_MODEL
        ),
        "start_environment": _environment(),
    }


def _records(outputs: list[str] | None = None) -> list[dict]:
    requests = execution.build_request_plan()
    outputs = outputs or [
        qualification.vector_text(request.expected_vector) for request in requests
    ]
    metadata = _metadata()
    result = []
    for request, output in zip(requests, outputs, strict=True):
        response = {
            "choices": [{"message": {"content": output}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 5},
        }
        result.append(
            {
                **execution.plan_entry(request),
                "run_id": execution.RUN_ID,
                "evidence_schema_version": execution.EVIDENCE_SCHEMA_VERSION,
                "infrastructure_status": "complete",
                "error": None,
                "raw_output": output,
                "evaluation": execution.evaluate_raw_output(request, output),
                "raw_request_payload": execution.build_request_payload(request),
                "response": response,
                "raw_response_payload_utf8": json.dumps(response),
                "expected_prompt_tokens": 100,
                "usage": response["usage"],
                "finish_reason": "stop",
                "timing": {"total_ms": 1},
                "runtime": metadata["runtime"],
                "model": metadata["model"],
            }
        )
    return result


def _write_fixture(root: Path) -> None:
    root.mkdir()
    (root / "raw").mkdir()
    metadata = _metadata()
    records = _records()
    lifecycle = {
        "command": metadata["server_command"],
        "pid": 123,
        "started": True,
        "expected_termination": True,
        "failure": None,
        "health_at_ready": {"reachable": True},
        "health_after_cleanup": {"reachable": False},
    }
    lifecycle.update(
        {
            key: _environment()
            for key in (
                "environment_at_ready",
                "environment_before_cleanup",
                "end_environment",
            )
        }
    )
    for name, value in {
        "metadata.json": metadata,
        "server-lifecycle.json": lifecycle,
        "summary.json": execution.summarize_records(
            records, execution.build_request_plan()
        ),
    }.items():
        (root / name).write_bytes(canonical_json_bytes(value))
    (root / "results.jsonl").write_bytes(
        b"".join(canonical_json_bytes(record) for record in records)
    )
    for name in ("llama-server.stdout.txt", "llama-server.stderr.txt"):
        (root / "raw" / name).write_bytes(b"synthetic fixture; no model was used\n")
    runner._write_integrity(root)


def test_authority_drives_all_eighteen_payloads() -> None:
    authority = json.loads(execution.PLAN_PATH.read_bytes())
    assert (
        hashlib.sha256(execution.PLAN_PATH.read_bytes()).hexdigest()
        == "5a487200b0dd72275d37482bc0c3c5cd09feed483419223005519b5034064bbc"
    )
    requests = execution.build_request_plan()
    assert [dict(request.authority) for request in requests] == authority["records"]
    assert len(requests) == 18
    assert [request.layer for request in requests] == [qualification.Q0_LAYER] * 9 + [
        qualification.Q1_LAYER
    ] * 9
    for request in requests:
        payload = execution.build_request_payload(request)
        assert payload == {
            **execution.request_parameters(),
            "grammar": request.authority["grammar"],
            "messages": [
                {"role": "user", "content": request.authority["public_prompt"]}
            ],
        }
        assert execution.plan_entry(request)["layer_ordinal"] in range(1, 10)


@pytest.mark.parametrize(
    "identity",
    [
        "unknown",
        "direct-state-vector-qualification-run-0002",
        "locality-run-0001",
        "D1",
        "D2",
        "attempt-0003",
        "output-selection-s0-run-0001",
        "output-selection-s1-run-0001",
    ],
)
def test_unknown_run_identity_rejected(identity: str) -> None:
    with pytest.raises(execution.DirectStateVectorExecutionError, match="identity"):
        execution.require_run_identity(identity)


def test_physical_plan_path_and_hash_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tampered = tmp_path / "plan.json"
    tampered.write_bytes(execution.PLAN_PATH.read_bytes() + b" ")
    with pytest.raises(execution.DirectStateVectorExecutionError, match="path"):
        execution.build_request_plan(tampered)
    monkeypatch.setattr(execution, "PLAN_PATH", tampered)
    with pytest.raises(execution.DirectStateVectorExecutionError, match="SHA-256"):
        execution.build_request_plan(tampered)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda a: a.update(contract_version="wrong"),
        lambda a: a.update(qualification_contract_version="wrong"),
        lambda a: a.update(run_id="wrong"),
        lambda a: a.update(runtime_contract_version="wrong"),
        lambda a: a["parser"].update(parser_version="wrong"),
        lambda a: a["records"].pop(),
        lambda a: a["records"].reverse(),
        lambda a: a["records"][0].update(layer=qualification.Q1_LAYER),
        lambda a: a["records"][0].update(expected_vector=["S2", "S2"]),
        lambda a: a["records"][0].update(public_prompt="wrong\n"),
        lambda a: a["records"][0].update(public_prompt_sha256="0" * 64),
        lambda a: a["records"][0].update(grammar='root ::= "S0,S0"\n'),
        lambda a: a["records"][9]["source"]["entity_histories"].update(E01=["S1"]),
        lambda a: a["records"][9]["source"]["query_entities"].reverse(),
        lambda a: a["records"][9]["source"]["source_events"][0].update(
            assigned_state="S0"
        ),
        lambda a: a["no_leakage_audit"].update(authority_metadata_not_rendered=False),
        lambda a: a["records"][9]["source"].update(schedule_kind="interleaved"),
    ],
)
def test_all_semantic_authority_mutations_rejected(
    monkeypatch: pytest.MonkeyPatch, mutation
) -> None:
    authority = json.loads(execution.PLAN_PATH.read_bytes())
    mutation(authority)
    monkeypatch.setattr(execution, "_read_canonical_plan", lambda _: authority)
    with pytest.raises(execution.DirectStateVectorExecutionError):
        execution.build_request_plan()


def test_redesign_hash_disposition_interface_and_gate_verified(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert (
        execution.verify_redesign_prerequisite()["disposition"]
        == "single_measurement_interface_candidate_identified"
    )
    assert (
        execution.verify_inventory_prerequisite()["aggregate_inventory_sha256"]
        == qualification.EXPECTED_INVENTORY_SHA256
    )
    wrong = tmp_path / "redesign.md"
    wrong.write_bytes(b"wrong decision")
    monkeypatch.setattr(execution, "REDESIGN_PATH", wrong)
    with pytest.raises(execution.DirectStateVectorExecutionError, match="SHA-256"):
        execution.verify_redesign_prerequisite(wrong)
    monkeypatch.setattr(
        execution,
        "EXPECTED_REDESIGN_SHA256",
        hashlib.sha256(wrong.read_bytes()).hexdigest(),
    )
    with pytest.raises(execution.DirectStateVectorExecutionError, match="disposition"):
        execution.verify_redesign_prerequisite(wrong)


def test_authority_owned_replay_and_leakage_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request = execution.build_request_plan()[9]
    monkeypatch.setattr(
        execution,
        "replay",
        lambda *_: SimpleNamespace(
            entity_states={entity: "S2" for entity in qualification.ENTITY_IDS}
        ),
    )
    with pytest.raises(
        execution.DirectStateVectorExecutionError, match="replay oracle"
    ):
        execution._validate_q1_authority(request)
    monkeypatch.undo()
    authority = deepcopy(request.authority)
    authority["public_prompt"] += "canonical target answer S0,S0\n"
    with pytest.raises(execution.DirectStateVectorExecutionError, match="exposes"):
        execution._validate_q1_authority(
            execution.QualificationRequest(authority, request.semantic_case)
        )


def test_dry_path_is_process_network_model_and_evidence_free(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    before = _snapshot()
    monkeypatch.setattr(execution, "RUNS", tmp_path)
    monkeypatch.setattr(runner, "RUNS", tmp_path)
    monkeypatch.setattr(execution, "require_no_evidence", lambda _runs=None: None)

    def forbidden(*_args, **_kwargs):
        pytest.fail(
            "static construction invoked an external process, network, or model access"
        )

    for method in ("Popen", "run", "check_output"):
        monkeypatch.setattr(subprocess, method, forbidden)
    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(baseline, "post", forbidden)
    monkeypatch.setattr(baseline, "file_sha256", forbidden)
    monkeypatch.setattr(baseline, "environment_snapshot", forbidden)
    payloads = runner.dry_construction()
    assert len(payloads) == 18
    assert _snapshot() == before
    assert not (tmp_path / execution.RUN_ID).exists()
    assert not runner._pending_directory().exists()
    assert not runner._invalid_directory().exists()


@pytest.mark.parametrize(
    "name",
    [
        execution.RUN_ID,
        f".{execution.RUN_ID}.pending",
        f"{execution.RUN_ID}.infrastructure-invalid",
    ],
)
def test_existing_execution_residue_rejected(tmp_path: Path, name: str) -> None:
    (tmp_path / name).mkdir()
    with pytest.raises(
        execution.DirectStateVectorExecutionError, match="already exists"
    ):
        execution.require_no_evidence(tmp_path)


@pytest.mark.parametrize(
    "raw",
    [
        "S0, S1",
        "E01=S0,E02=S1",
        "S0,S0 explanation",
        "s0,s0",
        "S0,S1,S2",
        "S0",
        "S0;S1",
    ],
)
def test_strict_parser_integration(raw: str) -> None:
    request = execution.build_request_plan()[0]
    assert execution.evaluate_raw_output(request, raw)["malformed"] is True


@pytest.mark.parametrize(
    "ordinal,output,expected",
    [
        (None, None, "direct_state_vector_interface_qualified"),
        (0, "S2,S2", "direct_state_vector_interface_blocked"),
        (17, "S0,S0", "direct_state_vector_interface_blocked"),
        (5, "S0, S1", "direct_state_vector_interface_blocked"),
    ],
)
def test_exact_18_of_18_and_each_layer_required(ordinal, output, expected) -> None:
    requests = execution.build_request_plan()
    outputs = [
        qualification.vector_text(request.expected_vector) for request in requests
    ]
    if ordinal is not None:
        outputs[ordinal] = output
    summary = execution.summarize_records(_records(outputs), requests)
    assert summary["classification"] == expected
    assert summary["outcome"] == "protocol_valid"


def test_incomplete_or_failed_run_never_invokes_semantic_classifier(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    requests = execution.build_request_plan()
    records = _records()
    monkeypatch.setattr(
        qualification,
        "classify_results",
        lambda *_: pytest.fail("classifier called for invalid run"),
    )
    for partial in (records[:9], records[9:], records[:-1]):
        assert execution.summarize_records(partial, requests)["classification"] is None
    records[0]["infrastructure_status"] = "failed"
    assert (
        execution.summarize_records(records, requests)["outcome"]
        == "infrastructure_invalid"
    )


def test_frozen_classifier_and_evaluator_are_called(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    requests = execution.build_request_plan()
    records = _records()
    seen = []
    original = qualification.classify_results

    def spy(outputs):
        seen.append(outputs)
        return original(outputs)

    monkeypatch.setattr(qualification, "classify_results", spy)
    execution.summarize_records(records, requests)
    assert len(seen) == 1 and len(seen[0]) == 18
    monkeypatch.setattr(
        qualification,
        "score",
        lambda *_: {
            "correct": False,
            "malformed": False,
            "parsed_vector": ["S1", "S1"],
        },
    )
    assert execution.evaluate_raw_output(requests[0], "S0,S0")["correct"] is False


def test_complete_prospective_fixture_and_tampered_raw_record(tmp_path: Path) -> None:
    run = tmp_path / execution.RUN_ID
    _write_fixture(run)
    assert (
        execution.validate_run_directory(run)["classification"]
        == "direct_state_vector_interface_qualified"
    )
    records = [
        json.loads(line) for line in (run / "results.jsonl").read_bytes().splitlines()
    ]
    records[0]["raw_request_payload"]["seed"] = 43
    (run / "results.jsonl").write_bytes(
        b"".join(canonical_json_bytes(record) for record in records)
    )
    with pytest.raises(
        execution.DirectStateVectorExecutionError, match="request payload"
    ):
        execution.validate_run_directory(run)
    with pytest.raises(execution.DirectStateVectorExecutionError, match="pending"):
        execution.validate_run_directory(tmp_path / f".{execution.RUN_ID}.pending")


def test_runtime_parameters_cannot_drift(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(baseline.INFERENCE, "temperature", 0.1)
    with pytest.raises(
        execution.DirectStateVectorExecutionError, match="runtime parameters"
    ):
        execution.request_parameters()


@pytest.mark.parametrize(
    "violation",
    [None, "dirty", "remote", "model", "runtime", "environment", "endpoint"],
)
def test_real_preflight_fails_closed_with_all_external_operations_mocked(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, violation
) -> None:
    monkeypatch.setattr(execution, "require_no_evidence", lambda _runs=None: None)
    model = tmp_path / "qualified.gguf"
    server = tmp_path / "qualified-server.exe"
    model.write_bytes(b"synthetic placeholder, no model")
    server.write_bytes(b"synthetic placeholder, not executable")
    monkeypatch.setattr(baseline, "DEFAULT_MODEL", model)
    monkeypatch.setattr(baseline, "DEFAULT_SERVER", server)
    monkeypatch.setattr(
        baseline,
        "file_sha256",
        lambda _: "wrong" if violation == "model" else baseline.EXPECTED_MODEL_SHA256,
    )

    def git(*args):
        if args[0] == "status":
            return "dirty" if violation == "dirty" else ""
        if args[0] == "ls-remote":
            return "wrong ref" if violation == "remote" else "synthetic-test-commit ref"
        return (
            "origin/codex/mn-006-distributed-state-integration"
            if "--abbrev-ref" in args
            else "synthetic-test-commit"
        )

    monkeypatch.setattr(runner, "_git", git)

    def identity(_):
        if violation == "runtime":
            raise baseline.AttemptInfrastructureError("runtime differs")
        return {
            **baseline.EXPECTED_RUNTIME,
            "backend": "llama.cpp",
            "executable": str(server),
        }

    monkeypatch.setattr(baseline, "runtime_identity", identity)
    monkeypatch.setattr(baseline, "environment_snapshot", _environment)

    def environment(*_):
        if violation == "environment":
            raise baseline.AttemptInfrastructureError("competing process")

    monkeypatch.setattr(baseline, "require_clean_environment", environment)
    monkeypatch.setattr(
        subprocess, "Popen", lambda *_a, **_k: pytest.fail("preflight started a server")
    )
    monkeypatch.setattr(
        baseline, "post", lambda *_a, **_k: pytest.fail("preflight issued generation")
    )
    if violation == "endpoint":
        monkeypatch.setattr(execution, "CHAT_COMPLETIONS_ENDPOINT", "/wrong")
    if violation is None:
        assert len(runner._require_preflight()["requests"]) == 18
    else:
        with pytest.raises(
            (
                execution.DirectStateVectorExecutionError,
                baseline.AttemptInfrastructureError,
            )
        ):
            runner._require_preflight()


def test_gate_prerequisite_hash_is_required(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(execution, "EXPECTED_GATE_SHA256", "0" * 64)
    with pytest.raises(execution.DirectStateVectorExecutionError, match="gate SHA"):
        execution.build_request_plan()


@pytest.mark.parametrize("failure_at", [None, 1, 10])
def test_future_lifecycle_with_synthetic_transport_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure_at
) -> None:
    requests = execution.build_request_plan()
    metadata = _metadata()
    monkeypatch.setattr(runner, "RUNS", tmp_path)
    monkeypatch.setattr(
        runner,
        "_require_preflight",
        lambda: {
            "requests": requests,
            "metadata": metadata,
            "base_url": "synthetic://fixture",
        },
    )

    class Process:
        pid = 123
        stopped = False

        def poll(self):
            return 0 if self.stopped else None

        def terminate(self):
            self.stopped = True

        def wait(self, **_kwargs):
            return 0

    process = Process()
    monkeypatch.setattr(subprocess, "Popen", lambda *_args, **_kwargs: process)
    monkeypatch.setattr(baseline, "wait_for_server", lambda *_: {"reachable": True})
    monkeypatch.setattr(
        baseline, "health", lambda *_: {"reachable": not process.stopped}
    )
    monkeypatch.setattr(runner, "_ready_environment", lambda *_: _environment())
    monkeypatch.setattr(baseline, "environment_snapshot", _environment)
    monkeypatch.setattr(baseline, "require_clean_environment", lambda *_: None)
    monkeypatch.setattr(baseline, "prompt_tokens", lambda *_: 100)
    submitted = []

    def synthetic_post(_url, endpoint, payload, **_kwargs):
        submitted.append(payload)
        assert endpoint == "/v1/chat/completions"
        if len(submitted) == failure_at:
            raise TimeoutError("synthetic interruption")
        output = qualification.vector_text(requests[len(submitted) - 1].expected_vector)
        response = {
            "choices": [{"message": {"content": output}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 5},
        }
        return json.dumps(response).encode(), response

    monkeypatch.setattr(baseline, "post", synthetic_post)
    path = runner.run()
    assert process.stopped
    assert len(submitted) == (18 if failure_at is None else failure_at)
    assert not runner._pending_directory().exists()
    if failure_at is None:
        assert path.name == execution.RUN_ID
        assert (
            execution.validate_run_directory(path)["classification"]
            == "direct_state_vector_interface_qualified"
        )
    else:
        assert path == runner._invalid_directory()
        assert (
            json.loads((path / "summary.json").read_bytes())["classification"] is None
        )
        assert not (tmp_path / execution.RUN_ID).exists()
