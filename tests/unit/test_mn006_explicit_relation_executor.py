from __future__ import annotations

import hashlib
import json
import shutil
import sys
from copy import deepcopy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BASE = (
    ROOT
    / "research"
    / "experiments"
    / "prototypes"
    / "mn-006-distributed-state-integration"
)
SCRIPTS = BASE / "scripts"
sys.path.insert(0, str(SCRIPTS))

import run_mn006_baseline as baseline
import run_mn006_explicit_relation_direct_rule as runner
from mn006 import explicit_relation as diagnostic
from mn006 import explicit_relation_execution as execution
from mn006.fingerprinting import canonical_json_bytes
from mn006.label_selection import GRAMMAR_AB, parse_label

PLAN = BASE / "definition" / "explicit-relation-direct-rule-v1" / "plan.json"
REVIEW = BASE / "recurring-fixed-label-causal-review.md"
RUNS = BASE / "runs"


def _authority() -> dict[str, object]:
    return json.loads(PLAN.read_bytes())


def _stub_prerequisites(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        execution,
        "verify_s0_prerequisite",
        lambda *_args, **_kwargs: {
            "classification": "direct_copy_supported",
            "integrity_validated": True,
            "outcome": "protocol_valid",
            "run_id": "output-selection-s0-run-0001",
        },
    )
    monkeypatch.setattr(
        execution,
        "verify_s1_prerequisite",
        lambda *_args, **_kwargs: {
            "classification": "fixed_label_preference_recurred",
            "integrity_validated": True,
            "outcome": "protocol_valid",
            "run_id": "output-selection-s1-run-0001",
        },
    )
    monkeypatch.setattr(
        execution,
        "verify_causal_review",
        lambda *_args, **_kwargs: {
            "disposition": "next_minimal_diagnostic_identified",
            "path": diagnostic.CAUSAL_REVIEW_PATH,
            "sha256": diagnostic.EXPECTED_CAUSAL_REVIEW_SHA256,
        },
    )


def _build_from_authority(
    monkeypatch: pytest.MonkeyPatch, authority: dict[str, object]
) -> tuple[execution.ExplicitRelationRequest, ...]:
    _stub_prerequisites(monkeypatch)
    monkeypatch.setattr(execution, "_read_canonical_plan", lambda _path=PLAN: authority)
    return execution.build_request_plan()


def _records(outputs: dict[str, str]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for request in execution.build_request_plan():
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
        f"{root.name}/{path.relative_to(root).as_posix()}": hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
        for root in paths
        for path in root.rglob("*")
        if path.is_file()
    }


def _write(path: Path, value: object) -> None:
    path.write_bytes(canonical_json_bytes(value))


def test_identity_runtime_and_authority_hash_are_frozen() -> None:
    assert execution.RUN_ID == "explicit-relation-direct-rule-run-0001"
    assert execution.CONTRACT_VERSION == "mn006-explicit-relation-direct-rule-v1"
    assert (
        execution.EXPECTED_PLAN_SHA256
        == "dc40c15a896f5f0413783818c39593b8a9c34eeea3ef4ce284e1b311112bc80a"
    )
    assert (
        hashlib.sha256(PLAN.read_bytes()).hexdigest() == execution.EXPECTED_PLAN_SHA256
    )
    assert execution.CHAT_COMPLETIONS_ENDPOINT == "/v1/chat/completions"
    assert execution.REQUEST_PARAMETERS == {
        "chat_template_kwargs": {},
        "max_tokens": 16,
        "seed": 42,
        "temperature": 0.0,
    }
    assert baseline.INFERENCE["configured_context_size"] == 16896
    assert baseline.EXPECTED_RUNTIME == {
        "version": "0.2.0-dev",
        "build": "10566",
        "commit": "bb4caa754",
    }


def test_exact_two_authority_records_and_payloads_are_selected() -> None:
    requests = execution.build_request_plan()
    assert len(requests) == 2
    assert [request.request_ordinal for request in requests] == [1, 2]
    assert [request.relation for request in requests] == ["different", "equal"]
    assert [request.canonical_answer for request in requests] == ["B", "A"]
    assert [request.grammar_id for request in requests] == ["A_then_B", "A_then_B"]
    assert all(request.grammar == GRAMMAR_AB for request in requests)
    for request in requests:
        payload = execution.build_request_payload(request)
        assert payload == {
            "chat_template_kwargs": {},
            "grammar": request.grammar,
            "max_tokens": 16,
            "messages": [{"role": "user", "content": request.public_prompt}],
            "seed": 42,
            "temperature": 0.0,
        }
        assert "E01 STATE" not in request.public_prompt
        assert "E02 STATE" not in request.public_prompt
        assert "use this mapping" not in request.public_prompt.lower()


def test_plan_tampering_and_unknown_run_ids_are_rejected(tmp_path: Path) -> None:
    tampered = tmp_path / "plan.json"
    tampered.write_bytes(
        PLAN.read_bytes().replace(b"Relation: different", b"Relation: equal", 1)
    )
    with pytest.raises(execution.ExplicitRelationExecutionError, match="SHA-256"):
        execution.build_request_plan(plan_path=tampered)
    for run_id in (
        "output-selection-s0-run-0001",
        "output-selection-s1-run-0001",
        "label-selection-d1-run-0001",
        "D2",
        "attempt-0003",
        "explicit-relation-direct-rule-run-0002",
    ):
        with pytest.raises(execution.ExplicitRelationExecutionError, match="unknown"):
            execution.require_run_identity(run_id)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda authority: authority.update(contract_version="wrong"),
        lambda authority: authority.update(run_id="wrong"),
        lambda authority: authority["records"].pop(),
        lambda authority: authority["records"].reverse(),
        lambda authority: authority["records"][0].update(relation="equal"),
        lambda authority: authority["records"][0].update(canonical_answer="A"),
        lambda authority: authority["records"][0].update(
            public_prompt="Relation: different\n"
        ),
        lambda authority: authority["records"][0].update(public_prompt_sha256="0" * 64),
        lambda authority: authority["records"][0].update(
            grammar='root ::= "B" | "A"\n'
        ),
    ],
)
def test_semantic_authority_mutations_are_rejected(
    monkeypatch: pytest.MonkeyPatch, mutation: object
) -> None:
    authority = deepcopy(_authority())
    mutation(authority)  # type: ignore[operator]
    with pytest.raises(execution.ExplicitRelationExecutionError):
        _build_from_authority(monkeypatch, authority)


def test_canonical_prerequisites_and_review_are_mechanically_valid() -> None:
    assert execution.verify_s0_prerequisite() == {
        "classification": "direct_copy_supported",
        "integrity_validated": True,
        "outcome": "protocol_valid",
        "run_id": "output-selection-s0-run-0001",
    }
    assert execution.verify_s1_prerequisite() == {
        "classification": "fixed_label_preference_recurred",
        "integrity_validated": True,
        "outcome": "protocol_valid",
        "run_id": "output-selection-s1-run-0001",
    }
    assert (
        execution.verify_causal_review()["disposition"]
        == "next_minimal_diagnostic_identified"
    )
    assert (
        hashlib.sha256(REVIEW.read_bytes()).hexdigest()
        == execution.EXPECTED_CAUSAL_REVIEW_SHA256
    )


def test_missing_or_wrongly_classified_s0_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    with pytest.raises(
        execution.ExplicitRelationExecutionError, match="S0 prerequisite"
    ):
        execution.verify_s0_prerequisite(tmp_path / "missing")
    monkeypatch.setattr(
        execution.s0_execution,
        "validate_s0_run_directory",
        lambda _path: {
            "outcome": "protocol_valid",
            "classification": "fixed_label_preference_persisted",
        },
    )
    with pytest.raises(
        execution.ExplicitRelationExecutionError, match="direct_copy_supported"
    ):
        execution.verify_s0_prerequisite(tmp_path)


def test_corrupted_s0_integrity_is_rejected(tmp_path: Path) -> None:
    copied = tmp_path / "s0"
    shutil.copytree(execution.S0_RUN_DIRECTORY, copied)
    (copied / "results.jsonl").write_bytes(
        (copied / "results.jsonl").read_bytes() + b"\n"
    )
    with pytest.raises(
        execution.ExplicitRelationExecutionError, match="S0 prerequisite"
    ):
        execution.verify_s0_prerequisite(copied)


def test_missing_or_wrongly_classified_s1_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    with pytest.raises(
        execution.ExplicitRelationExecutionError, match="S1 prerequisite"
    ):
        execution.verify_s1_prerequisite(tmp_path / "missing")
    monkeypatch.setattr(
        execution.s1_execution,
        "validate_s1_run_directory",
        lambda *_args, **_kwargs: {
            "outcome": "protocol_valid",
            "classification": "direct_relation_supported",
        },
    )
    with pytest.raises(
        execution.ExplicitRelationExecutionError,
        match="fixed_label_preference_recurred",
    ):
        execution.verify_s1_prerequisite(tmp_path)


def test_corrupted_s1_integrity_is_rejected(tmp_path: Path) -> None:
    copied = tmp_path / "s1"
    shutil.copytree(execution.S1_RUN_DIRECTORY, copied)
    (copied / "summary.json").write_bytes(
        (copied / "summary.json").read_bytes() + b"\n"
    )
    with pytest.raises(
        execution.ExplicitRelationExecutionError, match="S1 prerequisite"
    ):
        execution.verify_s1_prerequisite(copied)


def test_causal_review_hash_and_disposition_are_both_required(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tampered = tmp_path / "review.md"
    tampered.write_bytes(REVIEW.read_bytes() + b"x")
    monkeypatch.setattr(execution, "CAUSAL_REVIEW_PATH", tampered)
    with pytest.raises(execution.ExplicitRelationExecutionError, match="SHA-256"):
        execution.verify_causal_review(tampered)
    wrong_disposition = tmp_path / "review-wrong.md"
    wrong_disposition.write_text(
        "Disposition: `different_disposition`\n", encoding="utf-8", newline="\n"
    )
    monkeypatch.setattr(execution, "CAUSAL_REVIEW_PATH", wrong_disposition)
    monkeypatch.setattr(
        execution,
        "EXPECTED_CAUSAL_REVIEW_SHA256",
        hashlib.sha256(wrong_disposition.read_bytes()).hexdigest(),
    )
    with pytest.raises(execution.ExplicitRelationExecutionError, match="disposition"):
        execution.verify_causal_review(wrong_disposition)


def test_strict_parser_and_frozen_classifier_are_reused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    requests = execution.build_request_plan()
    assert parse_label(" B \n") == "B"
    assert all(
        parse_label(value) is None for value in ("a", "b", "A.", "Answer: A", "A B")
    )
    outputs = {request.record_id: request.canonical_answer for request in requests}
    seen: dict[str, dict[str, str]] = {}

    def classifier(raw_outputs: dict[str, str]) -> str:
        seen["outputs"] = raw_outputs
        return "classifier_called"

    monkeypatch.setattr(diagnostic, "classify", classifier)
    summary = execution.summarize_records(_records(outputs), requests)
    assert summary["classification"] == "classifier_called"
    assert seen["outputs"] == outputs


@pytest.mark.parametrize(
    ("values", "classification"),
    [
        (("B", "A"), "explicit_relation_direct_rule_supported"),
        (("A", "A"), "fixed_label_preference_persisted"),
        (("A.", "A"), "explicit_relation_malformed_or_invalid"),
        (("B", "B"), "explicit_relation_inconclusive"),
    ],
)
def test_synthetic_complete_patterns_keep_frozen_semantics(
    values: tuple[str, str], classification: str
) -> None:
    requests = execution.build_request_plan()
    outputs = {
        request.record_id: value
        for request, value in zip(requests, values, strict=True)
    }
    summary = execution.summarize_records(_records(outputs), requests)
    assert summary["outcome"] == "protocol_valid"
    assert summary["classification"] == classification


def test_incomplete_or_infrastructure_invalid_evidence_has_no_semantic_classification() -> (
    None
):
    requests = execution.build_request_plan()
    outputs = {request.record_id: request.canonical_answer for request in requests}
    incomplete = _records(outputs)[:-1]
    assert execution.summarize_records(incomplete, requests)["classification"] is None
    failed = _records(outputs)
    failed[0]["infrastructure_status"] = "failed"
    summary = execution.summarize_records(failed, requests)
    assert summary["outcome"] == "infrastructure_invalid"
    assert summary["classification"] is None


def test_dry_construction_is_network_free_directory_free_and_immutable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    retained = (
        RUNS / "attempt-0001",
        RUNS / "attempt-0002",
        RUNS / "label-selection-d1-run-0001",
        execution.S0_RUN_DIRECTORY,
        execution.S1_RUN_DIRECTORY,
        RUNS / execution.RUN_ID,
        BASE / "definition" / "output-selection-minimality-v1",
        PLAN.parent,
        REVIEW.parent,
    )
    before = _snapshot(retained)
    monkeypatch.setattr(
        baseline,
        "post",
        lambda *args, **kwargs: pytest.fail("dry construction must not use network"),
    )
    monkeypatch.setattr(
        runner.subprocess,
        "Popen",
        lambda *args, **kwargs: pytest.fail("dry construction must not start a server"),
    )
    entries = runner.dry_construction()
    after = _snapshot(retained)
    assert before == after
    assert [entry["relation"] for entry in entries] == ["different", "equal"]
    assert [entry["canonical_answer"] for entry in entries] == ["B", "A"]
    assert execution.validate_run_directory(RUNS / execution.RUN_ID)["classification"] == "fixed_label_preference_persisted"
    assert not runner._pending_directory().exists()
    assert not runner._invalid_directory().exists()
    assert not (RUNS / "attempt-0003").exists()
    assert not (SCRIPTS / "run_mn006_label_selection_d2.py").exists()


def test_future_preflight_reuses_runtime_helpers_without_network(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    model = tmp_path / "qualified.gguf"
    server = tmp_path / "llama-server.exe"
    model.write_bytes(b"fixture")
    server.write_bytes(b"fixture")
    calls: list[tuple[str, object]] = []
    monkeypatch.setattr(
        baseline, "file_sha256", lambda _path: baseline.EXPECTED_MODEL_SHA256
    )
    monkeypatch.setattr(
        runner.subprocess,
        "run",
        lambda *args, **kwargs: type("Result", (), {"stdout": b""})(),
    )
    monkeypatch.setattr(
        baseline, "environment_snapshot", lambda: {"fixture": "environment"}
    )
    monkeypatch.setattr(
        baseline,
        "require_clean_environment",
        lambda environment, base_url: calls.append(
            ("environment", (environment, base_url))
        ),
    )
    runtime = {
        "backend": "llama.cpp",
        "version": "0.2.0-dev",
        "build": "10566",
        "commit": "bb4caa754",
    }
    monkeypatch.setattr(baseline, "runtime_identity", lambda _path: runtime)
    temporary_runs = tmp_path / "runs"
    temporary_runs.mkdir()
    monkeypatch.setattr(runner, "RUNS", temporary_runs)
    result = runner._require_preflight(model, server)
    assert len(result[0]) == 2
    assert result[4] == {"fixture": "environment"}
    assert result[5] == runtime
    assert result[6] == "http://127.0.0.1:18501"
    assert calls == [("environment", ({"fixture": "environment"}, result[6]))]


def test_complete_prospective_directory_validates_and_incomplete_is_rejected(
    tmp_path: Path,
) -> None:
    requests = execution.build_request_plan()
    complete = tmp_path / execution.RUN_ID
    complete.mkdir()
    s0 = execution.verify_s0_prerequisite()
    s1 = execution.verify_s1_prerequisite()
    review = execution.verify_causal_review()
    metadata = {
        "causal_review": review,
        "contract": execution.contract_metadata(
            "executor-commit",
            s0_prerequisite=s0,
            s1_prerequisite=s1,
            causal_review=review,
        ),
        "run_id": execution.RUN_ID,
        "s0_prerequisite": s0,
        "s1_prerequisite": s1,
    }
    outputs = {request.record_id: request.canonical_answer for request in requests}
    records = _records(outputs)
    summary = execution.summarize_records(records, requests)
    _write(complete / "metadata.json", metadata)
    (complete / "results.jsonl").write_bytes(
        b"".join(canonical_json_bytes(record) for record in records)
    )
    raw = complete / "raw"
    raw.mkdir()
    (raw / "llama-server.stdout.txt").write_bytes(b"")
    (raw / "llama-server.stderr.txt").write_bytes(b"")
    _write(complete / "server-lifecycle.json", {"started": True})
    _write(complete / "summary.json", summary)
    _write(
        complete / "integrity.json",
        {
            "artifact_sha256": execution.artifact_hashes(complete),
            "plan_sha256": execution.EXPECTED_PLAN_SHA256,
            "run_id": execution.RUN_ID,
        },
    )
    assert (
        execution.validate_run_directory(complete)["classification"]
        == "explicit_relation_direct_rule_supported"
    )

    incomplete = tmp_path / "incomplete"
    incomplete.mkdir()
    _write(incomplete / "metadata.json", metadata)
    (incomplete / "results.jsonl").write_bytes(b"")
    _write(incomplete / "summary.json", execution.summarize_records([], requests))
    with pytest.raises(execution.ExplicitRelationExecutionError, match="incomplete"):
        execution.validate_run_directory(incomplete)
