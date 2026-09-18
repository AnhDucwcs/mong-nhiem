"""Deterministic static-contract tests for the MN-007 calibration corpus."""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import pytest

MN007_SCRIPTS = (
    Path(__file__).resolve().parents[2]
    / "research"
    / "experiments"
    / "prototypes"
    / "mn-007-state-recovery-operating-region"
    / "scripts"
)
if str(MN007_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(MN007_SCRIPTS))

import mn007_materialization as materialization


def test_seed_derivation_is_exact_and_uses_unit_separator() -> None:
    digest = materialization.seed_digest(
        scope="case",
        cell_id=materialization.CELLS[0].cell_id,
        pair_slot=0,
        case_ordinal=1,
        purpose="expected-vector",
    )
    assert digest == "0a71644c5ee3f84b8ad60115faf9ce3896d9cf1ac3e6fb9a6a681d5eca8fb736"
    assert materialization.US == "\x1f"
    with pytest.raises(materialization.MaterializationError):
        materialization.seed_digest(
            scope="case-pair",
            cell_id=materialization.CELLS[0].cell_id,
            pair_slot=0,
            case_ordinal=1,
            purpose="entity-rank",
        )


def test_case_id_and_schedule_contract() -> None:
    assert materialization.cell_case_id(materialization.CELLS[0], 1).endswith("-c01")
    assert materialization.cell_case_id(materialization.CELLS[-1], 18).endswith("-c18")
    assert [cell.source_distances for cell in materialization.CELLS] == [
        (3, 0),
        (6, 3),
        (3, 0),
        (12, 9),
        (3, 0),
        (18, 15),
    ]
    assert [cell.source_query_blocks for cell in materialization.CELLS] == [
        (2, 3),
        (1, 2),
        (4, 5),
        (1, 2),
        (6, 7),
        (1, 2),
    ]


def test_full_corpus_coverage_balances_and_replay() -> None:
    semantic, public, evaluator = materialization.generate_records()
    assert len(semantic) == len(public) == len(evaluator) == 108
    assert [record["global_ordinal"] for record in semantic] == list(range(1, 109))
    for cell in materialization.CELLS:
        records = [record for record in semantic if record["cell_id"] == cell.cell_id]
        assert len(records) == 18
        assert [tuple(record["query_final_states"]) for record in records] == list(materialization.VECTOR_ORDER) * 2
        assert Counter(record["query_orientation"] for record in records) == {
            "source_order": 9,
            "reverse_source_order": 9,
        }
        for record in records:
            assert record["state_assignment_counts"] == {
                "S0": cell.entity_count,
                "S1": cell.entity_count,
                "S2": cell.entity_count,
            }
            replayed = materialization.replay(record["event_stream"], record["active_entities"])
            assert tuple(replayed[entity] for entity in record["query_entities"]) == tuple(record["query_final_states"])


def test_public_prompt_is_strictly_separate_from_evaluator_truth() -> None:
    semantic, public, evaluator = materialization.generate_records()
    for semantic_record, public_record, evaluator_record in zip(semantic, public, evaluator, strict=True):
        prompt = public_record["prompt"]
        assert semantic_record["case_id"] not in prompt
        assert semantic_record["difficulty"]["placement"] not in prompt
        assert semantic_record["semantic_history_id"] not in prompt
        assert ",".join(semantic_record["query_final_states"]) not in prompt
        assert public_record["prompt_sha256"] == materialization.sha256_bytes(prompt.encode("utf-8"))
        assert "expected_vector" not in public_record
        assert evaluator_record["expected_vector"] == semantic_record["query_final_states"]


def test_strict_vector_parser_accepts_only_canonical_forms() -> None:
    assert materialization.parse_vector("S0,S2\n") == ("S0", "S2")
    for malformed in ("S0, S2", "S0,S2.", "s0,s2", "S0", "S0,S1,S2", "E01=S0,E02=S2"):
        assert materialization.parse_vector(malformed) is None


def test_validator_rejects_missing_duplicate_and_leaking_records() -> None:
    semantic, public, evaluator = materialization.generate_records()
    with pytest.raises(materialization.MaterializationError, match="108"):
        materialization.validate_records(semantic[:-1], public[:-1], evaluator[:-1])
    duplicate = [dict(record) for record in semantic]
    duplicate[-1]["case_id"] = duplicate[0]["case_id"]
    with pytest.raises(materialization.MaterializationError, match="unique"):
        materialization.validate_records(duplicate, public, evaluator)
    leaked = [dict(record) for record in public]
    leaked[0]["prompt"] += "\nexpected_vector=S0,S0\n"
    with pytest.raises(materialization.MaterializationError, match="public prompt differs"):
        materialization.validate_records(semantic, leaked, evaluator)


def test_canonical_artifacts_are_byte_identical_and_lf_only(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first_manifest = materialization.write_artifacts(first)
    second_manifest = materialization.write_artifacts(second)
    assert first_manifest == second_manifest
    materialization.compare_artifact_trees(first, second)
    assert {path.name for path in first.iterdir()} == set(materialization.ARTIFACT_FILENAMES)
    for name in materialization.ARTIFACT_FILENAMES:
        payload = first.joinpath(name).read_bytes()
        assert not payload.startswith(b"\xef\xbb\xbf")
        assert b"\r\n" not in payload
        assert payload.endswith(b"\n")


def test_validator_rejects_physical_byte_tampering(tmp_path: Path) -> None:
    root = tmp_path / "corpus"
    materialization.write_artifacts(root)
    root.joinpath("public-prompts.jsonl").write_bytes(
        root.joinpath("public-prompts.jsonl").read_bytes() + b" "
    )
    with pytest.raises(materialization.MaterializationError, match="physical bytes"):
        materialization.validate_materialized(root)
