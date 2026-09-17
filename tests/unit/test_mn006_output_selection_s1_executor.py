from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = (
    ROOT
    / "research"
    / "experiments"
    / "prototypes"
    / "mn-006-distributed-state-integration"
    / "scripts"
)
sys.path.insert(0, str(SCRIPTS))

import run_mn006_baseline as baseline
import run_mn006_output_selection_s1 as runner
from mn006 import output_selection as minimality
from mn006 import output_selection_s1_execution as execution
from mn006.fingerprinting import canonical_json_bytes
from mn006.label_selection_execution import validate_d1_run_directory
from mn006.measurement import validate_attempt_directory

RUNS = ROOT / "research" / "experiments" / "prototypes" / "mn-006-distributed-state-integration" / "runs"
PLAN = (
    ROOT
    / "research"
    / "experiments"
    / "prototypes"
    / "mn-006-distributed-state-integration"
    / "definition"
    / "output-selection-minimality-v1"
    / "plan.json"
)


def _records(outputs: dict[str, str]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for request in execution.build_s1_request_plan():
        raw_output = outputs[request.record_id]
        records.append(
            {
                **execution.plan_entry(request),
                "evaluation": execution.evaluate_raw_output(request, raw_output),
                "infrastructure_status": "complete",
                "raw_output": raw_output,
            }
        )
    return records


def _snapshot(paths: tuple[Path, ...]) -> dict[str, str]:
    return {
        f"{root.name}/{path.relative_to(root).as_posix()}": hashlib.sha256(path.read_bytes()).hexdigest()
        for root in paths
        for path in root.rglob("*")
        if path.is_file()
    }


def _write(path: Path, value: object) -> None:
    path.write_bytes(canonical_json_bytes(value))


def test_s1_identity_runtime_contract_and_authority_hash_are_frozen() -> None:
    assert execution.S1_RUN_ID == "output-selection-s1-run-0001"
    assert execution.CONTRACT_VERSION == "mn006-output-selection-minimality-v1"
    assert execution.EXPECTED_PLAN_SHA256 == "8180ea423a05eeb2930b84cee6102fd94595e13856f1a91e1afe4d599bb8e827"
    assert execution.CHAT_COMPLETIONS_ENDPOINT == "/v1/chat/completions"
    assert hashlib.sha256(PLAN.read_bytes()).hexdigest() == execution.EXPECTED_PLAN_SHA256
    assert execution.REQUEST_PARAMETERS == {
        "chat_template_kwargs": {},
        "max_tokens": 16,
        "seed": 42,
        "temperature": 0.0,
    }
    assert execution.REQUEST_PARAMETERS["max_tokens"] == baseline.INFERENCE["output_tokens"]
    assert execution.REQUEST_PARAMETERS["seed"] == baseline.INFERENCE["seed"]
    assert execution.REQUEST_PARAMETERS["temperature"] == baseline.INFERENCE["temperature"]
    assert baseline.INFERENCE["configured_context_size"] == 16896
    assert baseline.EXPECTED_RUNTIME == {"version": "0.2.0-dev", "build": "10566", "commit": "bb4caa754"}


def test_canonical_s0_prerequisite_is_mechanically_verified() -> None:
    assert execution.verify_s0_prerequisite() == {
        "classification": "direct_copy_supported",
        "integrity_validated": True,
        "outcome": "protocol_valid",
        "run_id": "output-selection-s0-run-0001",
    }


@pytest.mark.parametrize(
    "summary",
    [
        {"outcome": "protocol_valid", "classification": "fixed_label_preference_persisted"},
        {"outcome": "infrastructure_invalid", "classification": None},
    ],
)
def test_nonqualifying_s0_summary_is_rejected(monkeypatch: pytest.MonkeyPatch, summary: dict[str, object]) -> None:
    monkeypatch.setattr(execution.s0_execution, "validate_s0_run_directory", lambda _path: summary)
    with pytest.raises(execution.S1ExecutionError, match="S1 is blocked"):
        execution.verify_s0_prerequisite()


def test_missing_incomplete_or_corrupt_s0_evidence_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(execution.S1ExecutionError, match="missing, incomplete, or invalid"):
        execution.verify_s0_prerequisite(tmp_path / "missing")

    incomplete = tmp_path / "incomplete"
    incomplete.mkdir()
    _write(incomplete / "metadata.json", {"run_id": minimality.S0_RUN_ID})
    with pytest.raises(execution.S1ExecutionError, match="missing, incomplete, or invalid"):
        execution.verify_s0_prerequisite(incomplete)

    corrupt = tmp_path / "corrupt"
    shutil.copytree(RUNS / minimality.S0_RUN_ID, corrupt)
    (corrupt / "results.jsonl").write_bytes(b"corrupt\n")
    with pytest.raises(execution.S1ExecutionError, match="missing, incomplete, or invalid"):
        execution.verify_s0_prerequisite(corrupt)


def test_authority_plan_is_loaded_exactly_and_s0_is_excluded() -> None:
    requests = execution.build_s1_request_plan()
    assert len(requests) == 4
    assert [request.request_ordinal for request in requests] == [1, 2, 3, 4]
    assert [request.query_states for request in requests] == [("S1", "S2"), ("S1", "S1"), ("S2", "S2"), ("S2", "S1")]
    assert [request.equal_state for request in requests] == [False, True, True, False]
    assert [request.canonical_answer for request in requests] == ["B", "A", "A", "B"]
    assert [request.grammar_id for request in requests] == ["A_then_B"] * 4
    assert [request.public_prompt for request in requests] == [
        "E01 STATE = S1\nE02 STATE = S2\nOutput A if the states are equal.\nOutput B if the states are different.\nOutput exactly one label: A or B.\n",
        "E01 STATE = S1\nE02 STATE = S1\nOutput A if the states are equal.\nOutput B if the states are different.\nOutput exactly one label: A or B.\n",
        "E01 STATE = S2\nE02 STATE = S2\nOutput A if the states are equal.\nOutput B if the states are different.\nOutput exactly one label: A or B.\n",
        "E01 STATE = S2\nE02 STATE = S1\nOutput A if the states are equal.\nOutput B if the states are different.\nOutput exactly one label: A or B.\n",
    ]
    assert all(request.authority["stage"] == minimality.S1_STAGE for request in requests)
    assert all("S0" not in request.record_id and "D1" not in request.record_id for request in requests)
    assert execution.REQUEST_ORDER_CONTRACT == "S1; canonical_plan_request_ordinal_ascending"


def test_tampered_or_unknown_authority_is_rejected(tmp_path: Path) -> None:
    tampered = tmp_path / "plan.json"
    tampered.write_bytes(PLAN.read_bytes().replace(b"E01 STATE = S1", b"E01 STATE = S2", 1))
    with pytest.raises(execution.S1ExecutionError, match="SHA-256"):
        execution.build_s1_request_plan(tampered)
    for run_id in ("attempt-0003", minimality.S0_RUN_ID, "label-selection-d1-run-0001", "label-selection-d2-run-0001", "unknown"):
        with pytest.raises(execution.S1ExecutionError, match="unknown"):
            execution.require_s1_run_identity(run_id)


def test_payloads_come_from_authority_records_only() -> None:
    for request in execution.build_s1_request_plan():
        payload = execution.build_request_payload(request)
        assert payload == {
            "chat_template_kwargs": {},
            "grammar": 'root ::= "A" | "B"\n',
            "max_tokens": 16,
            "messages": [{"role": "user", "content": request.public_prompt}],
            "seed": 42,
            "temperature": 0.0,
        }
        assert request.public_prompt.endswith("\n") and "\r\n" not in request.public_prompt
        assert request.grammar.endswith("\n") and request.grammar.count("\n") == 1


def test_future_preflight_reuses_frozen_runtime_helpers_without_network(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    model = tmp_path / "qualified.gguf"
    server = tmp_path / "llama-server.exe"
    model.write_bytes(b"fixture")
    server.write_bytes(b"fixture")
    calls: list[tuple[str, object]] = []

    monkeypatch.setattr(baseline, "file_sha256", lambda path: baseline.EXPECTED_MODEL_SHA256)
    monkeypatch.setattr(runner.subprocess, "run", lambda *args, **kwargs: type("Result", (), {"stdout": b""})())
    monkeypatch.setattr(baseline, "environment_snapshot", lambda: {"fixture": "environment"})
    monkeypatch.setattr(
        baseline,
        "require_clean_environment",
        lambda environment, base_url: calls.append(("environment", (environment, base_url))),
    )
    runtime = {"backend": "llama.cpp", "version": "0.2.0-dev", "build": "10566", "commit": "bb4caa754"}
    monkeypatch.setattr(baseline, "runtime_identity", lambda path: runtime)

    requests, environment, observed_runtime, base_url = runner._require_preflight(model, server)
    assert len(requests) == 4
    assert environment == {"fixture": "environment"}
    assert observed_runtime == runtime
    assert base_url == "http://127.0.0.1:18501"
    assert calls == [("environment", ({"fixture": "environment"}, base_url))]


def test_dry_construction_is_s1_only_network_free_and_immutable(monkeypatch: pytest.MonkeyPatch) -> None:
    retained = (
        RUNS / "attempt-0001",
        RUNS / "attempt-0002",
        RUNS / "label-selection-d1-run-0001",
        RUNS / minimality.S0_RUN_ID,
        PLAN.parent,
    )
    before = _snapshot(retained)
    monkeypatch.setattr(baseline, "post", lambda *args, **kwargs: pytest.fail("dry construction must not make HTTP requests"))
    monkeypatch.setattr(runner.subprocess, "Popen", lambda *args, **kwargs: pytest.fail("dry construction must not start a server"))
    entries = runner.dry_construction()
    after = _snapshot(retained)
    assert after == before
    assert len(entries) == 4
    assert [entry["request_ordinal"] for entry in entries] == [1, 2, 3, 4]
    assert {entry["stage"] for entry in entries} == {minimality.S1_STAGE}
    assert not (RUNS / minimality.S1_RUN_ID).exists()
    assert not (RUNS / f".{minimality.S1_RUN_ID}.pending").exists()
    assert not (RUNS / f"{minimality.S1_RUN_ID}.infrastructure-invalid").exists()
    assert not (RUNS / "attempt-0003").exists()
    assert not (SCRIPTS / "run_mn006_label_selection_d2.py").exists()


def test_incomplete_or_infrastructure_invalid_records_never_receive_semantic_classification() -> None:
    requests = execution.build_s1_request_plan()
    incomplete = _records({request.record_id: request.canonical_answer for request in requests})[:-1]
    summary = execution.summarize_s1_records(incomplete, requests)
    assert summary["outcome"] == "infrastructure_invalid"
    assert summary["classification"] is None
    failed = _records({request.record_id: request.canonical_answer for request in requests})
    failed[0]["infrastructure_status"] = "failed"
    summary = execution.summarize_s1_records(failed, requests)
    assert summary["outcome"] == "infrastructure_invalid"
    assert summary["classification"] is None
    reordered = list(reversed(_records({request.record_id: request.canonical_answer for request in requests})))
    summary = execution.summarize_s1_records(reordered, requests)
    assert summary["outcome"] == "infrastructure_invalid"
    assert summary["classification"] is None


def test_semantic_classification_reuses_frozen_s1_classifier(monkeypatch: pytest.MonkeyPatch) -> None:
    requests = execution.build_s1_request_plan()
    outputs = {request.record_id: request.canonical_answer for request in requests}
    seen: dict[str, tuple[dict[str, str], str]] = {}

    def classifier(raw_outputs: dict[str, str], *, s0_classification: str) -> str:
        seen["call"] = raw_outputs, s0_classification
        return "classifier_called"

    monkeypatch.setattr(minimality, "classify_s1", classifier)
    summary = execution.summarize_s1_records(_records(outputs), requests)
    assert summary["classification"] == "classifier_called"
    assert seen["call"] == (outputs, "direct_copy_supported")


@pytest.mark.parametrize(
    ("outputs", "classification"),
    [
        (lambda requests: {request.record_id: request.canonical_answer for request in requests}, "direct_relation_supported"),
        (lambda requests: {request.record_id: "A" for request in requests}, "fixed_label_preference_recurred"),
        (lambda requests: {request.record_id: "A." for request in requests}, "direct_relation_malformed_or_invalid"),
        (lambda requests: {request.record_id: ("A" if request.request_ordinal in (1, 2, 4) else "B") for request in requests}, "direct_relation_inconclusive"),
    ],
)
def test_synthetic_complete_fixtures_keep_frozen_s1_outcomes(outputs: object, classification: str) -> None:
    requests = execution.build_s1_request_plan()
    raw_outputs = outputs(requests)  # type: ignore[operator]
    summary = execution.summarize_s1_records(_records(raw_outputs), requests)
    assert summary["outcome"] == "protocol_valid"
    assert summary["classification"] == classification


def test_complete_directory_validates_but_incomplete_directory_is_rejected(tmp_path: Path) -> None:
    requests = execution.build_s1_request_plan()
    complete = tmp_path / execution.S1_RUN_ID
    complete.mkdir()
    s0_prerequisite = execution.verify_s0_prerequisite()
    metadata = {
        "run_id": execution.S1_RUN_ID,
        "contract": execution.contract_metadata("executor-commit"),
        "s0_prerequisite": s0_prerequisite,
    }
    records = _records({request.record_id: request.canonical_answer for request in requests})
    summary = execution.summarize_s1_records(records, requests)
    _write(complete / "metadata.json", metadata)
    (complete / "results.jsonl").write_bytes(b"".join(canonical_json_bytes(record) for record in records))
    raw = complete / "raw"
    raw.mkdir()
    (raw / "llama-server.stdout.txt").write_bytes(b"")
    (raw / "llama-server.stderr.txt").write_bytes(b"")
    _write(complete / "server-lifecycle.json", {"started": True})
    _write(complete / "summary.json", summary)
    _write(
        complete / "integrity.json",
        {"artifact_sha256": execution.artifact_hashes(complete), "plan_sha256": execution.EXPECTED_PLAN_SHA256, "run_id": execution.S1_RUN_ID},
    )
    assert execution.validate_s1_run_directory(complete)["classification"] == "direct_relation_supported"

    incomplete = tmp_path / "incomplete"
    incomplete.mkdir()
    _write(incomplete / "metadata.json", metadata)
    (incomplete / "results.jsonl").write_bytes(b"")
    _write(incomplete / "summary.json", execution.summarize_s1_records([], requests))
    with pytest.raises(execution.S1ExecutionError, match="incomplete"):
        execution.validate_s1_run_directory(incomplete)


def test_prior_measurements_s0_and_d1_evidence_remain_valid() -> None:
    assert validate_attempt_directory(RUNS / "attempt-0001", attempt_id="attempt-0001")["outcome"] == "protocol_valid"
    assert validate_attempt_directory(RUNS / "attempt-0002", attempt_id="attempt-0002")["outcome"] == "protocol_valid"
    assert validate_d1_run_directory(RUNS / "label-selection-d1-run-0001")["classification"] == "fixed_label_preference_supported"
    assert execution.verify_s0_prerequisite()["classification"] == "direct_copy_supported"
