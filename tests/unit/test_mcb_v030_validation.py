from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "research" / "experiments" / "baselines" / "mn-002-model-qualification" / "scripts"
ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

import mcb
import mcb_v030
import validate_mcb_v030


def test_frozen_selection_matches_committed_evidence() -> None:
    evidence = json.loads((ROOT / "reports" / "mcb-v0.3.0-validation.json").read_text(encoding="utf-8"))
    selected = validate_mcb_v030.selected_runs()
    assert {model: path.name for model, path in selected.items()} == evidence["selected_runs"]


def test_future_directory_is_not_part_of_frozen_selection(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    evidence = json.loads((ROOT / "reports" / "mcb-v0.3.0-validation.json").read_text(encoding="utf-8"))
    monkeypatch.setattr(mcb, "RUNS", tmp_path)
    for run_id in evidence["selected_runs"].values():
        source = ROOT / "runs" / run_id
        destination = tmp_path / run_id
        destination.mkdir()
        for name in ("metadata.json", "summary.json"):
            (destination / name).write_bytes((source / name).read_bytes())
    future = tmp_path / "future-mcb-v030"
    future.mkdir()
    (future / "metadata.json").write_text("{}", encoding="utf-8")
    (future / "summary.json").write_text("{}", encoding="utf-8")
    assert {model: path.name for model, path in validate_mcb_v030.selected_runs().items()} == evidence["selected_runs"]


def test_config_and_template_contracts_are_versioned() -> None:
    config = json.loads((ROOT / "configs" / "mcb-v0.3.0.json").read_text(encoding="utf-8"))
    assert config["benchmark_version"] == "0.3.0"
    assert mcb_v030.definition_fingerprint() == "2ac24df4e6cca12e13da577fb48db5da8e39d89cf3646ef705ea7679b4548f7a"


def test_missing_or_wrong_evidence_run_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(mcb, "RUNS", tmp_path)
    with pytest.raises(RuntimeError, match="missing"):
        validate_mcb_v030.selected_runs()
