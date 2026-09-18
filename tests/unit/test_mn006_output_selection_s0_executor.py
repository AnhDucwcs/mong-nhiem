from __future__ import annotations

import hashlib
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
import run_mn006_output_selection_s0 as runner
from mn006 import output_selection as minimality
from mn006 import output_selection_execution as execution
from mn006 import output_selection_s1_execution as s1_execution
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
    for request in execution.build_s0_request_plan():
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


def test_s0_identity_runtime_contract_and_authority_hash_are_frozen() -> None:
    assert execution.S0_RUN_ID == "output-selection-s0-run-0001"
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


def test_authority_plan_is_loaded_exactly_and_s1_is_excluded() -> None:
    requests = execution.build_s0_request_plan()
    assert len(requests) == 4
    assert [request.request_ordinal for request in requests] == [1, 2, 3, 4]
    assert [request.target_label for request in requests] == ["A", "B", "B", "A"]
    assert [request.grammar_id for request in requests] == ["A_then_B", "B_then_A", "A_then_B", "B_then_A"]
    assert [request.canonical_answer for request in requests] == ["A", "B", "B", "A"]
    assert all(request.authority["stage"] == minimality.S0_STAGE for request in requests)
    assert all("S1" not in request.record_id for request in requests)
    assert execution.REQUEST_ORDER_CONTRACT == "S0; canonical_plan_request_ordinal_ascending"


def test_tampered_or_unknown_authority_is_rejected(tmp_path: Path) -> None:
    tampered = tmp_path / "plan.json"
    tampered.write_bytes(PLAN.read_bytes().replace(b"Target label: A", b"Target label: B", 1))
    with pytest.raises(execution.S0ExecutionError, match="SHA-256"):
        execution.build_s0_request_plan(tampered)
    with pytest.raises(execution.S0ExecutionError, match="unknown"):
        execution.require_s0_run_identity("attempt-0003")
    with pytest.raises(execution.S0ExecutionError, match="unknown"):
        execution.require_s0_run_identity(minimality.S1_RUN_ID)


def test_payloads_come_from_authority_records_only() -> None:
    for request in execution.build_s0_request_plan():
        payload = execution.build_request_payload(request)
        assert payload == {
            "chat_template_kwargs": {},
            "grammar": request.grammar,
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


def test_dry_construction_is_s0_only_network_free_and_immutable(monkeypatch: pytest.MonkeyPatch) -> None:
    retained = (
        RUNS / "attempt-0001",
        RUNS / "attempt-0002",
        RUNS / "label-selection-d1-run-0001",
        RUNS / execution.S0_RUN_ID,
        RUNS / minimality.S1_RUN_ID,
        PLAN.parent,
    )
    before = _snapshot(retained)
    monkeypatch.setattr(baseline, "post", lambda *args, **kwargs: pytest.fail("dry construction must not make HTTP requests"))
    entries = runner.dry_construction()
    after = _snapshot(retained)
    assert after == before
    assert len(entries) == 4
    assert [entry["request_ordinal"] for entry in entries] == [1, 2, 3, 4]
    assert {entry["stage"] for entry in entries} == {minimality.S0_STAGE}
    assert execution.validate_s0_run_directory(RUNS / execution.S0_RUN_ID)["classification"] == "direct_copy_supported"
    assert s1_execution.validate_s1_run_directory(RUNS / minimality.S1_RUN_ID)["classification"] == "fixed_label_preference_recurred"
    assert not (RUNS / "attempt-0003").exists()
    assert (SCRIPTS / "run_mn006_output_selection_s1.py").is_file()
    assert not (SCRIPTS / "run_mn006_label_selection_d2.py").exists()


def test_incomplete_or_infrastructure_invalid_records_never_receive_semantic_classification() -> None:
    requests = execution.build_s0_request_plan()
    incomplete = _records({request.record_id: request.canonical_answer for request in requests})[:-1]
    summary = execution.summarize_s0_records(incomplete, requests)
    assert summary["outcome"] == "infrastructure_invalid"
    assert summary["classification"] is None
    failed = _records({request.record_id: request.canonical_answer for request in requests})
    failed[0]["infrastructure_status"] = "failed"
    summary = execution.summarize_s0_records(failed, requests)
    assert summary["outcome"] == "infrastructure_invalid"
    assert summary["classification"] is None


def test_semantic_classification_reuses_frozen_s0_classifier(monkeypatch: pytest.MonkeyPatch) -> None:
    requests = execution.build_s0_request_plan()
    outputs = {request.record_id: request.canonical_answer for request in requests}
    seen: dict[str, dict[str, str]] = {}

    def classifier(raw_outputs: dict[str, str]) -> str:
        seen["raw_outputs"] = raw_outputs
        return "classifier_called"

    monkeypatch.setattr(minimality, "classify_s0", classifier)
    summary = execution.summarize_s0_records(_records(outputs), requests)
    assert summary["classification"] == "classifier_called"
    assert seen["raw_outputs"] == outputs


@pytest.mark.parametrize(
    ("outputs", "classification"),
    [
        (lambda requests: {request.record_id: request.canonical_answer for request in requests}, "direct_copy_supported"),
        (lambda requests: {request.record_id: "A" for request in requests}, "fixed_label_preference_persisted"),
        (lambda requests: {request.record_id: "A" if request.grammar_id == "A_then_B" else "B" for request in requests}, "grammar_order_asymmetry_observed"),
        (lambda requests: {request.record_id: "A." for request in requests}, "direct_copy_malformed_or_invalid"),
    ],
)
def test_synthetic_complete_fixtures_keep_frozen_s0_outcomes(outputs: object, classification: str) -> None:
    requests = execution.build_s0_request_plan()
    raw_outputs = outputs(requests)  # type: ignore[operator]
    summary = execution.summarize_s0_records(_records(raw_outputs), requests)
    assert summary["outcome"] == "protocol_valid"
    assert summary["classification"] == classification


def test_complete_directory_validates_but_incomplete_directory_is_rejected(tmp_path: Path) -> None:
    requests = execution.build_s0_request_plan()
    complete = tmp_path / execution.S0_RUN_ID
    complete.mkdir()
    metadata = {"run_id": execution.S0_RUN_ID, "contract": execution.contract_metadata("executor-commit")}
    records = _records({request.record_id: request.canonical_answer for request in requests})
    summary = execution.summarize_s0_records(records, requests)
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
        {"artifact_sha256": execution.artifact_hashes(complete), "plan_sha256": execution.EXPECTED_PLAN_SHA256, "run_id": execution.S0_RUN_ID},
    )
    assert execution.validate_s0_run_directory(complete)["classification"] == "direct_copy_supported"

    incomplete = tmp_path / "incomplete"
    incomplete.mkdir()
    _write(incomplete / "metadata.json", metadata)
    (incomplete / "results.jsonl").write_bytes(b"")
    _write(incomplete / "summary.json", execution.summarize_s0_records([], requests))
    with pytest.raises(execution.S0ExecutionError, match="incomplete"):
        execution.validate_s0_run_directory(incomplete)


def test_prior_measurements_and_d1_evidence_remain_valid() -> None:
    assert validate_attempt_directory(RUNS / "attempt-0001", attempt_id="attempt-0001")["outcome"] == "protocol_valid"
    assert validate_attempt_directory(RUNS / "attempt-0002", attempt_id="attempt-0002")["outcome"] == "protocol_valid"
    assert validate_d1_run_directory(RUNS / "label-selection-d1-run-0001")["classification"] == "fixed_label_preference_supported"
