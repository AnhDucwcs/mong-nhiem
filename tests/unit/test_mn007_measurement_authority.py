"""Static contract tests for MN-007 measurement authority and request order."""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

MN007_DIR = (
    Path(__file__).resolve().parents[2]
    / "research"
    / "experiments"
    / "prototypes"
    / "mn-007-state-recovery-operating-region"
)
MN007_SCRIPTS = MN007_DIR / "scripts"
if str(MN007_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(MN007_SCRIPTS))

import mn007_materialization as materialization

FROZEN_REQUEST_ORDER_SHA256 = (
    "93d578e5a24903e826f2ad0481a420d219e53be30e2e4a822d9c3fdc0a96b474"
)


def request_order() -> list[str]:
    return [
        f"{cell.cell_id}-c{k:02d}"
        for k in range(1, 19)
        for cell in materialization.CELLS
    ]


def test_request_order_length_and_coverage() -> None:
    order = request_order()
    assert len(order) == 108
    assert len(set(order)) == 108
    by_cell = Counter(case_id.rsplit("-c", 1)[0] for case_id in order)
    assert by_cell == {cell.cell_id: 18 for cell in materialization.CELLS}


def test_request_order_strata_balance() -> None:
    order = request_order()
    for wave_idx in range(18):
        wave = order[wave_idx * 6 : (wave_idx + 1) * 6]
        wave_cells = [case_id.rsplit("-c", 1)[0] for case_id in wave]
        assert wave_cells == [cell.cell_id for cell in materialization.CELLS]
        wave_ordinals = [case_id.rsplit("-c", 1)[1] for case_id in wave]
        assert len(set(wave_ordinals)) == 1
        assert wave_ordinals[0] == f"{wave_idx + 1:02d}"


def test_request_order_fingerprint() -> None:
    order = request_order()
    text = "\n".join(order) + "\n"
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    assert digest == FROZEN_REQUEST_ORDER_SHA256


def test_request_order_joins_materialized_public_prompts() -> None:
    prompts_path = (
        MN007_DIR / "definition" / "calibration-corpus-v1" / "public-prompts.jsonl"
    )
    lines = prompts_path.read_text(encoding="utf-8").strip().split("\n")
    corpus_ids = {json.loads(line)["case_id"] for line in lines}
    assert set(request_order()) == corpus_ids
