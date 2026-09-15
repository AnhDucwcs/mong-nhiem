"""Canonical, non-model materialization for the frozen MN-006 v1 baseline inventory."""
from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .audits import answer_proxy_audit, positional_audit
from .fingerprinting import (
    canonical_json_bytes,
    canonical_json_sha256,
    canonical_text_bytes,
    sha256_bytes,
)
from .generation import generate_pair
from .model import (
    GENERATOR_VERSION,
    PARSER_VERSION,
    PROFILE_LEVEL_1,
    PROFILE_LEVEL_2,
    SEMANTIC_CONTRACT_VERSION,
    VALIDATOR_VERSION,
    CasePair,
    GeneratedCase,
    Profile,
)
from .serialization import authority_record, evaluator_record, serialize_public_text
from .validation import validate_pair


class InventoryError(ValueError):
    """Raised when canonical inventory construction or physical authority differs."""


ROOT = Path(__file__).resolve().parents[2]
INVENTORY_VERSION = "mn006-v1-baseline-inventory-1"
INVENTORY_ROOT = ROOT / "definition" / "baseline-inventory-v1"
ROOT_SEED = "mn006-v1-baseline-inventory"
PAIRED_CASES_PER_PROFILE = 32
ORDINALS = tuple(range(PAIRED_CASES_PER_PROFILE))
PROFILES = (PROFILE_LEVEL_1, PROFILE_LEVEL_2)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise InventoryError(message)


def generated_pairs(profile: Profile) -> tuple[CasePair, ...]:
    """Return the complete mechanically selected inventory stratum."""
    return tuple(generate_pair(profile, ordinal, ROOT_SEED) for ordinal in ORDINALS)


def _members(pair: CasePair) -> tuple[GeneratedCase, GeneratedCase]:
    return pair.contiguous, pair.interleaved


def _relative_public_path(case: GeneratedCase) -> str:
    return f"public/{case.core.profile.identifier}/{case.case_id}.txt"


def _relative_evaluator_path(profile: Profile) -> str:
    return f"evaluator/{profile.identifier}.json"


def _relative_authority_path(profile: Profile) -> str:
    return f"authority/{profile.identifier}.json"


def _artifact_entry(relative_path: str, kind: str, payload: bytes, profile: str, case_id: str | None = None) -> dict[str, object]:
    entry: dict[str, object] = {
        "byte_count": len(payload),
        "kind": kind,
        "profile": profile,
        "relative_path": relative_path,
        "sha256": sha256_bytes(payload),
    }
    if case_id is not None:
        entry["case_id"] = case_id
    return entry


def _profile_artifacts(profile: Profile, pairs: tuple[CasePair, ...]) -> tuple[dict[str, bytes], list[dict[str, object]], dict[str, object]]:
    payloads: dict[str, bytes] = {}
    entries: list[dict[str, object]] = []
    members = tuple(case for pair in pairs for case in _members(pair))
    evaluator_records: list[dict[str, Any]] = []
    authority_records: list[dict[str, Any]] = []
    for pair in pairs:
        validate_pair(pair)
    for case in sorted(members, key=lambda item: item.case_id):
        public_payload = canonical_text_bytes(serialize_public_text(case))
        _require(b"\r\n" not in public_payload, "canonical public prompt contains CRLF")
        authority = authority_record(case)
        hashes = authority["generation_metadata"]["canonical_hashes"]
        _require(hashes["public_text_sha256"] == sha256_bytes(public_payload), "authority public prompt hash differs")
        public_path = _relative_public_path(case)
        payloads[public_path] = public_payload
        entries.append(_artifact_entry(public_path, "public_prompt", public_payload, profile.identifier, case.case_id))
        evaluator_records.append(evaluator_record(case))
        authority_records.append(authority)
    evaluator_payload = canonical_json_bytes(
        {
            "inventory_version": INVENTORY_VERSION,
            "parser_version": PARSER_VERSION,
            "profile": profile.identifier,
            "records": evaluator_records,
        }
    )
    authority_payload = canonical_json_bytes(
        {
            "inventory_version": INVENTORY_VERSION,
            "profile": profile.identifier,
            "records": authority_records,
        }
    )
    _require(b"\r\n" not in evaluator_payload and b"\r\n" not in authority_payload, "canonical JSON contains CRLF")
    evaluator_path = _relative_evaluator_path(profile)
    authority_path = _relative_authority_path(profile)
    payloads[evaluator_path] = evaluator_payload
    payloads[authority_path] = authority_payload
    entries.extend(
        (
            _artifact_entry(evaluator_path, "evaluator_bundle", evaluator_payload, profile.identifier),
            _artifact_entry(authority_path, "authority_bundle", authority_payload, profile.identifier),
        )
    )
    proxy = answer_proxy_audit(pairs)
    positional = positional_audit(pairs, require_full_slot_coverage=True)
    summary = {
        "answer_proxy_audit": proxy,
        "authority_record_count": len(authority_records),
        "case_ids": [case.case_id for case in sorted(members, key=lambda item: item.case_id)],
        "evaluator_record_count": len(evaluator_records),
        "ordinal_range": [ORDINALS[0], ORDINALS[-1]],
        "paired_case_count": len(pairs),
        "pair_ids": [pair.contiguous.core.pair_id for pair in pairs],
        "positional_audit": positional,
        "profile": profile.identifier,
        "public_prompt_count": len(members),
        "validation_status": "passed",
    }
    return payloads, entries, summary


def _manifest_without_aggregate(entries: list[dict[str, object]], profiles: list[dict[str, object]]) -> dict[str, object]:
    return {
        "artifact_entries": sorted(entries, key=lambda item: str(item["relative_path"])),
        "generator_version": GENERATOR_VERSION,
        "inventory_version": INVENTORY_VERSION,
        "ordinal_sequence": list(ORDINALS),
        "paired_case_count": PAIRED_CASES_PER_PROFILE * len(PROFILES),
        "profile_summaries": profiles,
        "root_seed": ROOT_SEED,
        "schema_version": SEMANTIC_CONTRACT_VERSION,
        "serialized_prompt_count": PAIRED_CASES_PER_PROFILE * len(PROFILES) * 2,
        "validator_version": VALIDATOR_VERSION,
        "workload_contract_version": SEMANTIC_CONTRACT_VERSION,
    }


def expected_artifacts() -> tuple[dict[str, bytes], dict[str, object]]:
    """Build every canonical payload in memory, with no filesystem traversal or model work."""
    payloads: dict[str, bytes] = {}
    entries: list[dict[str, object]] = []
    summaries: list[dict[str, object]] = []
    for profile in PROFILES:
        profile_payloads, profile_entries, summary = _profile_artifacts(profile, generated_pairs(profile))
        payloads.update(profile_payloads)
        entries.extend(profile_entries)
        summaries.append(summary)
    manifest = _manifest_without_aggregate(entries, summaries)
    manifest["aggregate_inventory_sha256"] = canonical_json_sha256(manifest)
    payloads["manifest.json"] = canonical_json_bytes(manifest)
    return payloads, manifest


def write_exact_bytes(path: Path, payload: bytes) -> str:
    """Write canonical authority bytes once, then prove physical readback identity."""
    path.parent.mkdir(parents=True, exist_ok=True)
    expected_hash = sha256_bytes(payload)
    if path.exists():
        observed = path.open("rb").read()
        if observed != payload:
            raise InventoryError(f"refusing to overwrite divergent canonical artifact: {path}")
    else:
        with path.open("wb") as handle:
            handle.write(payload)
    with path.open("rb") as handle:
        readback = handle.read()
    if readback != payload or sha256_bytes(readback) != expected_hash:
        raise InventoryError(f"physical canonical byte/hash round-trip failed: {path}")
    if b"\r\n" in readback:
        raise InventoryError(f"canonical artifact contains CRLF bytes: {path}")
    return expected_hash


def materialize_inventory(root: Path = INVENTORY_ROOT) -> dict[str, object]:
    """Materialize the frozen inventory using binary authority I/O and validate it."""
    payloads, manifest = expected_artifacts()
    for relative_path, payload in sorted(payloads.items()):
        write_exact_bytes(root / relative_path, payload)
    validated = validate_materialized_inventory(root)
    if validated != manifest:
        raise InventoryError("materialized inventory manifest differs from frozen expected manifest")
    return manifest


def validate_materialized_inventory(root: Path = INVENTORY_ROOT) -> dict[str, object]:
    """Reconstruct expected authority and compare every physical artifact byte-for-byte."""
    payloads, expected_manifest = expected_artifacts()
    expected_paths = set(payloads)
    actual_paths = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
    }
    if actual_paths != expected_paths:
        raise InventoryError("materialized inventory paths differ from frozen layout")
    for relative_path, expected in payloads.items():
        path = root / relative_path
        with path.open("rb") as handle:
            actual = handle.read()
        if actual != expected:
            raise InventoryError(f"materialized artifact bytes differ: {relative_path}")
        if sha256_bytes(actual) != sha256_bytes(expected):
            raise InventoryError(f"materialized artifact fingerprint differs: {relative_path}")
        if b"\r\n" in actual:
            raise InventoryError(f"materialized artifact contains CRLF: {relative_path}")
    manifest = payloads["manifest.json"]
    if sha256_bytes(manifest) != sha256_bytes((root / "manifest.json").open("rb").read()):
        raise InventoryError("physical manifest fingerprint differs")
    return expected_manifest


def manifest_fingerprint(manifest: Mapping[str, object]) -> str:
    """Return the non-self-referential aggregate authority fingerprint."""
    aggregate = manifest.get("aggregate_inventory_sha256")
    if not isinstance(aggregate, str):
        raise InventoryError("inventory manifest lacks aggregate fingerprint")
    return aggregate
