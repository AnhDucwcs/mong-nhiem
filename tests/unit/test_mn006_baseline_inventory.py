from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "research" / "experiments" / "prototypes" / "mn-006-distributed-state-integration" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from mn006.audits import answer_proxy_audit, positional_audit
from mn006.fingerprinting import (
    canonical_json_bytes,
    canonical_text_bytes,
    sha256_bytes,
)
from mn006.inventory import (
    INVENTORY_VERSION,
    ORDINALS,
    PAIRED_CASES_PER_PROFILE,
    PROFILES,
    ROOT_SEED,
    InventoryError,
    expected_artifacts,
    generated_pairs,
    materialize_inventory,
    validate_materialized_inventory,
    write_exact_bytes,
)


def test_frozen_inventory_rule_has_exact_counts_balance_and_structural_coverage() -> None:
    assert ROOT_SEED == "mn006-v1-baseline-inventory"
    assert ORDINALS == tuple(range(32))
    assert PAIRED_CASES_PER_PROFILE == 32
    for profile in PROFILES:
        pairs = generated_pairs(profile)
        assert len(pairs) == 32
        proxy = answer_proxy_audit(pairs)
        positional = positional_audit(pairs, require_full_slot_coverage=True)
        assert proxy["answer_counts"] == {"VALID": 16, "INVALID": 16}
        assert positional["entity_count"] == profile.entity_count


def test_expected_artifacts_have_sorted_manifest_and_exact_prompt_counts() -> None:
    payloads, manifest = expected_artifacts()
    assert manifest["inventory_version"] == INVENTORY_VERSION
    assert manifest["paired_case_count"] == 64
    assert manifest["serialized_prompt_count"] == 128
    assert manifest["ordinal_sequence"] == list(range(32))
    entries = manifest["artifact_entries"]
    assert entries == sorted(entries, key=lambda item: item["relative_path"])
    public_paths = [path for path in payloads if path.startswith("public/")]
    assert len(public_paths) == 128
    assert all(b"\r\n" not in payloads[path] for path in payloads)


def test_materialization_round_trips_every_authoritative_byte(tmp_path: Path) -> None:
    manifest = materialize_inventory(tmp_path)
    assert validate_materialized_inventory(tmp_path) == manifest
    for path in tmp_path.rglob("*"):
        if path.is_file():
            payload = path.open("rb").read()
            assert b"\r\n" not in payload
            assert payload.endswith(b"\n")


def test_binary_write_refuses_divergent_existing_authority(tmp_path: Path) -> None:
    path = tmp_path / "authority.json"
    first = canonical_json_bytes({"b": 1, "a": ["S0"]})
    assert write_exact_bytes(path, first) == sha256_bytes(first)
    path.write_bytes(b"not canonical\n")
    with pytest.raises(InventoryError, match="refusing to overwrite"):
        write_exact_bytes(path, first)


def test_canonical_text_and_json_resist_crlf_before_binary_materialization(tmp_path: Path) -> None:
    logical_text = "All entities begin in S0.\nE01 STATE = S1\n"
    canonical_lf = canonical_text_bytes(logical_text)
    canonical_from_crlf = canonical_text_bytes(logical_text.replace("\n", "\r\n"))
    assert canonical_lf == canonical_from_crlf
    text_path = tmp_path / "public.txt"
    assert write_exact_bytes(text_path, canonical_lf) == sha256_bytes(canonical_lf)
    assert text_path.read_bytes() == canonical_lf
    assert b"\r\n" not in text_path.read_bytes()
    json_payload = canonical_json_bytes({"z": "S2", "a": ["VALID", "INVALID"]})
    json_path = tmp_path / "authority.json"
    assert write_exact_bytes(json_path, json_payload) == sha256_bytes(json_payload)
    assert json_path.read_bytes() == json_payload
    assert b"\r\n" not in json_path.read_bytes()
