import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "research" / "experiments" / "prototypes" / "mn-004-state-representation-intervention" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import mn004_v4
import run_mn004_v4


def row(case_id: str, status: str = "complete", **extra: object) -> dict:
    return {"case_id": case_id, "completion_status": status, **extra}


def test_first_infrastructure_failure_stops_without_later_requests() -> None:
    attempted: list[int] = []

    def request(ordinal: int, _source: dict) -> dict:
        attempted.append(ordinal)
        return row(str(ordinal), "infrastructure_failure" if ordinal == 2 else "complete")

    records = mn004_v4.execute_fail_fast([{}, {}, {}], request)
    assert attempted == [1, 2]
    assert [record["case_id"] for record in records] == ["1", "2"]


def test_protocol_invalidity_also_stops_without_later_requests() -> None:
    records = mn004_v4.execute_fail_fast([{}, {}], lambda ordinal, _row: row(str(ordinal), "protocol_invalid"))
    assert len(records) == 1


def test_model_output_content_is_operationally_complete() -> None:
    record = row("case", "complete", finish_reason="length", raw_output="not an answer", evaluation={"passed": False, "score": 0.0})
    assert mn004_v4.phase_outcome("stage_a_untreated", [record], 1) == "stage_completed"


def test_first_failure_exposes_resource_signature_from_attachment() -> None:
    failed = row("case", "infrastructure_failure", failure_attachment={"stderr_tail": "CUDA error: out of memory", "process": {"returncode": -1}})
    assert mn004_v4.first_failure([row("prior"), failed]) is failed
    assert mn004_v4.has_resource_signature(failed)


def test_process_exit_code_is_retained_when_available() -> None:
    class Process:
        pid = 17

        @staticmethod
        def poll() -> int:
            return -9

    observed = run_mn004_v4.poll_after_failure(Process(), 0)
    assert observed["pid"] == 17 and observed["returncode"] == -9 and not observed["alive"]


def test_untreated_failure_blocks_ledger(monkeypatch) -> None:
    monkeypatch.setattr(mn004_v4, "latest_summary", lambda stage: {"operational_outcome": "untreated_environment_failure"} if stage == "stage_a_untreated" else None)
    assert not mn004_v4.stage_allowed("stage_b_ledger")


def test_completed_ledger_blocks_diagnostics(monkeypatch) -> None:
    def summary(stage: str) -> dict | None:
        return {"operational_outcome": "stage_completed"} if stage == "stage_a_untreated" else {"operational_outcome": "ledger_persistent_phase_completed"} if stage == "stage_b_ledger" else None

    monkeypatch.setattr(mn004_v4, "latest_summary", summary)
    assert not mn004_v4.stage_allowed("stage_c1_failed_case")


def test_stage_c1_and_c2_have_predeclared_ordering(monkeypatch) -> None:
    def c1_summary(stage: str) -> dict | None:
        return {"operational_outcome": "ledger_runtime_failure_reproduced"} if stage == "stage_b_ledger" else None

    monkeypatch.setattr(mn004_v4, "latest_summary", c1_summary)
    assert mn004_v4.stage_allowed("stage_c1_failed_case")
    monkeypatch.setattr(mn004_v4, "latest_summary", lambda stage: {"operational_outcome": "stage_completed", "predecessor_case_id": "ecc006-001"} if stage == "stage_c1_failed_case" else None)
    assert mn004_v4.stage_allowed("stage_c2_predecessor_then_failed_case")


def test_v4_authorizes_only_immutable_8k_rows() -> None:
    rows = mn004_v4.inventory()
    assert len(rows) == 24
    assert {row["requested_input_tokens"] for row in rows} == {8192}


def test_stage_b_outcome_uses_operational_failure_not_answer_score() -> None:
    completed = [row(str(index), "complete", evaluation={"passed": index % 2 == 0}) for index in range(24)]
    assert mn004_v4.phase_outcome("stage_b_ledger", completed, 24) == "ledger_persistent_phase_completed"
