from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "research" / "experiments" / "prototypes" / "mn-006-distributed-state-integration" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from mn006.measurement import (
    ATTEMPT_ID,
    EXPECTED_INVENTORY_SHA256,
    EXPECTED_REQUEST_COUNT,
    build_request_plan,
    evaluate_raw_output,
    exact_one_sided_pvalue,
    summarize_attempt,
    validate_attempt_directory,
    write_new_canonical_json,
)
from mn006.model import SCHEDULE_CONTIGUOUS


def record_for_plan(entry: dict[str, object], raw_output: str) -> dict[str, object]:
    return {
        **entry,
        "evaluation": evaluate_raw_output(raw_output, str(entry["canonical_answer"])),
        "infrastructure_status": "complete",
        "raw_output": raw_output,
    }


def opposite(answer: str) -> str:
    return "INVALID" if answer == "VALID" else "VALID"


def test_frozen_plan_has_exact_order_and_inventory_identity() -> None:
    manifest, plan = build_request_plan()
    assert manifest["aggregate_inventory_sha256"] == EXPECTED_INVENTORY_SHA256
    assert len(plan) == EXPECTED_REQUEST_COUNT == 128
    assert [entry["request_ordinal"] for entry in plan] == list(range(1, 129))
    assert plan[0]["schedule_kind"] == "contiguous_control"
    assert plan[1]["schedule_kind"] == "interleaved"
    assert plan[2]["schedule_kind"] == "interleaved"
    assert plan[3]["schedule_kind"] == "contiguous_control"


def test_exact_parser_and_paired_summary_follow_frozen_directional_rule() -> None:
    _manifest, plan = build_request_plan()
    records: list[dict[str, object]] = []
    for entry in plan:
        answer = str(entry["canonical_answer"])
        if entry["profile"] == "level_1_light_interleaved":
            raw = answer if entry["schedule_kind"] == SCHEDULE_CONTIGUOUS else opposite(answer)
        else:
            raw = opposite(answer)
        records.append(record_for_plan(entry, raw))
    summary = summarize_attempt(records, plan)
    level_1 = summary["profiles"]["level_1_light_interleaved"]
    level_2 = summary["profiles"]["level_2_primary_interleaved"]
    assert summary["outcome"] == "protocol_valid"
    assert level_1["classification"] == "candidate_locality_failure_signal"
    assert level_1["transitions"]["C_correct_I_incorrect"] == 32
    assert level_1["paired_test"]["one_sided_exact_p_value"] == 2**-32
    assert level_2["classification"] == "no_usable_locality_failure_signal_under_v1_baseline"
    assert evaluate_raw_output("VALID.", "VALID")["malformed"] is True
    assert exact_one_sided_pvalue(2, 1) == 0.5
    assert exact_one_sided_pvalue(1, 2) is None


def test_validator_recomputes_stored_valid_attempt(tmp_path: Path) -> None:
    manifest, plan = build_request_plan()
    records = [record_for_plan(entry, str(entry["canonical_answer"])) for entry in plan]
    metadata = {"attempt_id": ATTEMPT_ID, "inventory_aggregate_sha256": manifest["aggregate_inventory_sha256"]}
    write_new_canonical_json(tmp_path / "metadata.json", metadata)
    (tmp_path / "results.jsonl").write_text(
        "".join(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n" for record in records),
        encoding="utf-8",
        newline="\n",
    )
    write_new_canonical_json(tmp_path / "summary.json", summarize_attempt(records, plan))
    assert validate_attempt_directory(tmp_path)["outcome"] == "protocol_valid"
