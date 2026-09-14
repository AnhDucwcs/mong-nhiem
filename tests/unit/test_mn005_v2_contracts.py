from __future__ import annotations

import inspect
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "research" / "experiments" / "prototypes" / "mn-005-state-tracking-intervention-selection" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import mn005
import mn005_v2 as v2
import run_mn005_v2 as run


def response(text: str, prompt_tokens: int = 5) -> dict[str, object]:
    return {"choices": [{"finish_reason": "stop", "message": {"role": "assistant", "content": text}}], "usage": {"prompt_tokens": prompt_tokens, "completion_tokens": 1, "total_tokens": prompt_tokens + 1}}


def source() -> dict[str, object]:
    return {"context": "Context event log:\nState update: Unit Test 1 changed to RED.", "arm_a": "Context event log:\nState update: Unit Test 1 changed to RED.\n\nQuestion:\nWhat is the current state of Unit Test 1? Return only the state.", "source_sha256": "unit-test-source"}


def case() -> dict[str, object]:
    return {"id": "ecc006-001", "entity": "Unit Test 1", "updates": ["RED", "BLUE", "AMBER", "GREEN"], "answer": "GREEN"}


def test_gate_b_v2_definition_and_cap() -> None:
    definition, cases, _ecc = v2.load_definition()
    assert definition["budgets"] == {"arm_a": 16, "stage_a": 80, "stage_b": 16}
    assert [item["id"] for item in cases] == list(v2.CASE_IDS)
    assert definition["support"] == mn005.load_definition()[0]["support"]


def test_frozen_artifact_counts_and_strict_fit() -> None:
    assert v2.EXPECTED_ARM_B_ARTIFACT_TOKENS == 71
    assert v2.EXPECTED_ARM_C_ARTIFACT_TOKENS == {"ecc006-001": 52, "ecc006-002": 51, "ecc006-003": 50, "ecc006-004": 53, "ecc006-005": 50, "ecc006-006": 48}
    v2.assert_strict_fit("control", 71)
    for name, count in v2.EXPECTED_ARM_C_ARTIFACT_TOKENS.items():
        v2.assert_strict_fit(name, count)
    with pytest.raises(v2.ContractError, match="strict-fit"):
        v2.assert_strict_fit("oversize", 73)


def test_persist_before_validation(tmp_path: Path) -> None:
    exchange = {"request_payload": {"max_tokens": 80}, "response": {"choices": [], "usage": {"prompt_tokens": 5}}, "finish_reason": None, "planned_prompt_tokens": 5, "completion_tokens": None, "total_tokens": None, "started_at": "t0", "ended_at": "t1", "latency_ms": 1.0}
    path = run.persist_response(tmp_path, 7, "ecc006-001", "B", "stage-a", exchange, {"pid": 1, "command": ["server"]})
    assert path.is_file()
    with pytest.raises(v2.ContractError):
        run.validate_received_response(exchange)


def test_arm_b_mismatch_never_submits_stage_b(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls: list[str] = []
    monkeypatch.setattr(run, "source_for_execution", lambda *_args: source())
    monkeypatch.setattr(run, "persist_response", lambda *_args, **_kwargs: tmp_path / "persisted.json")
    monkeypatch.setattr(run, "validate_received_response", lambda exchange: exchange["raw_text"])
    def fake_request(_client: object, _content: str, _maximum: int, _definition: dict[str, object]) -> dict[str, object]:
        calls.append(_content)
        return {"raw_text": "pad=wrong", "finish_reason": "stop", "latency_ms": 1.0}
    monkeypatch.setattr(run, "request", fake_request)
    definition, _cases, ecc = v2.load_definition()
    with pytest.raises(v2.ContractError, match="active-control artifact"):
        run.two_call_record(object(), definition, case(), ecc, {"source_sha256": "unused"}, "B", 7, tmp_path / "artifacts", tmp_path / "raw", {"pid": 1, "command": ["server"]})
    assert len(calls) == 1


def test_arm_b_exact_grammar_submits_stage_b(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls: list[str] = []
    monkeypatch.setattr(run, "source_for_execution", lambda *_args: source())
    monkeypatch.setattr(run, "persist_response", lambda *_args, **_kwargs: tmp_path / "persisted.json")
    monkeypatch.setattr(run, "validate_received_response", lambda exchange: exchange["raw_text"])
    outputs = iter([v2.CONTROL_ARTIFACT, "GREEN"])
    def fake_request(_client: object, content: str, _maximum: int, _definition: dict[str, object]) -> dict[str, object]:
        calls.append(content)
        return {"raw_text": next(outputs), "finish_reason": "stop", "latency_ms": 1.0}
    monkeypatch.setattr(run, "request", fake_request)
    definition, _cases, ecc = v2.load_definition()
    record = run.two_call_record(object(), definition, case(), ecc, {"source_sha256": "unused"}, "B", 8, tmp_path / "artifacts", tmp_path / "raw", {"pid": 1, "command": ["server"]})
    assert len(calls) == 2
    assert record["evaluation"]["passed"]


def test_arm_c_malformed_artifact_is_transported_literally(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    contents: list[str] = []
    monkeypatch.setattr(run, "source_for_execution", lambda *_args: source())
    monkeypatch.setattr(run, "persist_response", lambda *_args, **_kwargs: tmp_path / "persisted.json")
    monkeypatch.setattr(run, "validate_received_response", lambda exchange: exchange["raw_text"])
    outputs = iter(["not a reconstruction", "GREEN"])
    def fake_request(_client: object, content: str, _maximum: int, _definition: dict[str, object]) -> dict[str, object]:
        contents.append(content)
        return {"raw_text": next(outputs), "finish_reason": "stop", "latency_ms": 1.0}
    monkeypatch.setattr(run, "request", fake_request)
    definition, _cases, ecc = v2.load_definition()
    record = run.two_call_record(object(), definition, case(), ecc, {"source_sha256": "unused"}, "C", 9, tmp_path / "artifacts", tmp_path / "raw", {"pid": 1, "command": ["server"]})
    assert "<artifact>\nnot a reconstruction\n</artifact>" in contents[1]
    assert not record["stage_a_diagnostic"]["format_valid"]


def test_first_valid_attempt_policy_and_no_retry_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(mn005, "RUNS", tmp_path)
    (tmp_path / "attempt-0001").mkdir()
    (tmp_path / "attempt-0001" / "summary.json").write_text('{"attempt_status":"experiment_invalid"}\n', encoding="utf-8")
    assert v2.next_attempt_id() == "attempt-0002"
    assert not v2.has_canonical_attempt()
    assert "retry" not in inspect.getsource(run.execute).casefold()


def test_exact_evaluator_is_unchanged() -> None:
    item = case()
    assert v2.final_evaluation(item, "GREEN", "stop")["passed"]
    assert not v2.final_evaluation(item, "BLUE", "stop")["passed"]
