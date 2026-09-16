"""Frozen MN-006 attempt planning, evaluation, and integrity checks."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

from .fingerprinting import canonical_json_bytes, sha256_bytes
from .inventory import (
    INVENTORY_ROOT,
    INVENTORY_VERSION,
    PAIRED_CASES_PER_PROFILE,
    PROFILES,
    validate_materialized_inventory,
)
from .model import PARSER_VERSION, SCHEDULE_CONTIGUOUS, SCHEDULE_INTERLEAVED, Profile
from .oracle import parse_answer

ATTEMPT_ID = "attempt-0001"
EVIDENCE_SCHEMA_VERSION = "mn006-baseline-attempt-v1"
EXPECTED_INVENTORY_SHA256 = "8cdcf1e792f495c9a4ca57ddcda865769db01bad8cfab65c9afb4cd225ad2ec9"
EXPECTED_REQUEST_COUNT = PAIRED_CASES_PER_PROFILE * len(PROFILES) * 2


class MeasurementError(ValueError):
    """Raised when an attempt deviates from the frozen measurement contract."""


def load_json(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        return json.loads(handle.read().decode("utf-8"))


def write_new_canonical_json(path: Path, value: object) -> str:
    """Create one canonical evidence object without allowing overwrite."""
    payload = canonical_json_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(payload)
    observed = path.read_bytes()
    if observed != payload or sha256_bytes(observed) != sha256_bytes(payload):
        raise MeasurementError(f"canonical evidence write/readback mismatch: {path}")
    return sha256_bytes(payload)


def append_canonical_jsonl(path: Path, value: object) -> str:
    """Append exactly one canonical record to an immutable-in-practice raw log."""
    payload = canonical_json_bytes(value)
    with path.open("ab") as handle:
        handle.write(payload)
    return sha256_bytes(payload)


def _public_entries(manifest: dict[str, Any], profile: Profile) -> dict[str, dict[str, Any]]:
    entries = {
        entry["case_id"]: entry
        for entry in manifest["artifact_entries"]
        if entry["kind"] == "public_prompt" and entry["profile"] == profile.identifier
    }
    if len(entries) != PAIRED_CASES_PER_PROFILE * 2:
        raise MeasurementError(f"unexpected public prompt count for {profile.identifier}")
    return entries


def _evaluator_answers(inventory_root: Path, profile: Profile) -> dict[str, str]:
    bundle = load_json(inventory_root / "evaluator" / f"{profile.identifier}.json")
    if bundle.get("inventory_version") != INVENTORY_VERSION or bundle.get("parser_version") != PARSER_VERSION:
        raise MeasurementError(f"evaluator bundle version mismatch for {profile.identifier}")
    result = {record["case_id"]: record["canonical_answer"] for record in bundle["records"]}
    if len(result) != PAIRED_CASES_PER_PROFILE * 2:
        raise MeasurementError(f"unexpected evaluator record count for {profile.identifier}")
    return result


def _case_id(profile: Profile, ordinal: int, schedule_kind: str) -> str:
    return f"mn006-v1-{profile.identifier}-{ordinal:06d}-{schedule_kind}"


def build_request_plan(inventory_root: Path = INVENTORY_ROOT) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Read only public/evaluator inventory views in the frozen 128-request order."""
    manifest = validate_materialized_inventory(inventory_root)
    aggregate = manifest.get("aggregate_inventory_sha256")
    if aggregate != EXPECTED_INVENTORY_SHA256:
        raise MeasurementError("inventory aggregate fingerprint differs from frozen baseline contract")
    plan: list[dict[str, Any]] = []
    request_ordinal = 1
    for profile in PROFILES:
        public_entries = _public_entries(manifest, profile)
        answers = _evaluator_answers(inventory_root, profile)
        for underlying_ordinal in range(PAIRED_CASES_PER_PROFILE):
            schedule_order = (
                (SCHEDULE_CONTIGUOUS, SCHEDULE_INTERLEAVED)
                if underlying_ordinal % 2 == 0
                else (SCHEDULE_INTERLEAVED, SCHEDULE_CONTIGUOUS)
            )
            pair_id = f"mn006-v1-{profile.identifier}-{underlying_ordinal:06d}"
            for pair_order, schedule_kind in enumerate(schedule_order, start=1):
                case_id = _case_id(profile, underlying_ordinal, schedule_kind)
                entry = public_entries.get(case_id)
                answer = answers.get(case_id)
                if entry is None or answer is None:
                    raise MeasurementError(f"missing canonical inventory member: {case_id}")
                public_path = inventory_root / entry["relative_path"]
                payload = public_path.read_bytes()
                if sha256_bytes(payload) != entry["sha256"] or len(payload) != entry["byte_count"]:
                    raise MeasurementError(f"public prompt fingerprint mismatch: {case_id}")
                if b"\r\n" in payload:
                    raise MeasurementError(f"public prompt contains CRLF: {case_id}")
                plan.append(
                    {
                        "attempt_id": ATTEMPT_ID,
                        "case_id": case_id,
                        "canonical_answer": answer,
                        "execution_order_within_pair": pair_order,
                        "inventory_aggregate_sha256": aggregate,
                        "pair_id": pair_id,
                        "profile": profile.identifier,
                        "prompt_byte_count": len(payload),
                        "prompt_sha256": entry["sha256"],
                        "public_prompt_path": entry["relative_path"],
                        "request_ordinal": request_ordinal,
                        "schedule_kind": schedule_kind,
                        "underlying_case_ordinal": underlying_ordinal,
                    }
                )
                request_ordinal += 1
    if len(plan) != EXPECTED_REQUEST_COUNT:
        raise MeasurementError("frozen request plan count differs from 128")
    return manifest, plan


def evaluate_raw_output(raw_text: str, canonical_answer: str) -> dict[str, object]:
    """Apply only the frozen strict answer parser and exact evaluator."""
    parsed = parse_answer(raw_text)
    return {
        "canonical_answer": canonical_answer,
        "correct": parsed == canonical_answer,
        "malformed": parsed is None,
        "parsed_answer": parsed,
        "score": float(parsed == canonical_answer),
    }


def exact_one_sided_pvalue(b: int, c: int) -> float | None:
    """Return frozen P[X >= b] for discordant paired cases only when directional."""
    if b <= c:
        return None
    discordant = b + c
    return sum(math.comb(discordant, value) for value in range(b, discordant + 1)) / (2**discordant)


def _profile_summary(records: list[dict[str, Any]], profile: Profile) -> dict[str, object]:
    expected = PAIRED_CASES_PER_PROFILE * 2
    if len(records) != expected:
        raise MeasurementError(f"incomplete record set for {profile.identifier}")
    by_case = {record["case_id"]: record for record in records}
    if len(by_case) != expected:
        raise MeasurementError(f"duplicate case record for {profile.identifier}")
    contiguous_correct = 0
    interleaved_correct = 0
    transitions = {"C_correct_I_correct": 0, "C_correct_I_incorrect": 0, "C_incorrect_I_correct": 0, "C_incorrect_I_incorrect": 0}
    for ordinal in range(PAIRED_CASES_PER_PROFILE):
        contiguous = by_case[_case_id(profile, ordinal, SCHEDULE_CONTIGUOUS)]
        interleaved = by_case[_case_id(profile, ordinal, SCHEDULE_INTERLEAVED)]
        c_passed = bool(contiguous["evaluation"]["correct"])
        i_passed = bool(interleaved["evaluation"]["correct"])
        contiguous_correct += int(c_passed)
        interleaved_correct += int(i_passed)
        transition = (
            "C_correct_I_correct" if c_passed and i_passed else
            "C_correct_I_incorrect" if c_passed else
            "C_incorrect_I_correct" if i_passed else
            "C_incorrect_I_incorrect"
        )
        transitions[transition] += 1
    b = transitions["C_correct_I_incorrect"]
    c = transitions["C_incorrect_I_correct"]
    p_value = exact_one_sided_pvalue(b, c)
    contiguous_malformed = sum(record["evaluation"]["malformed"] for record in records if record["schedule_kind"] == SCHEDULE_CONTIGUOUS)
    interleaved_malformed = sum(record["evaluation"]["malformed"] for record in records if record["schedule_kind"] == SCHEDULE_INTERLEAVED)
    signal = contiguous_correct >= 24 and b > c and p_value is not None and p_value <= 0.05
    return {
        "N_pairs": PAIRED_CASES_PER_PROFILE,
        "candidate_locality_failure_signal": signal,
        "classification": "candidate_locality_failure_signal" if signal else "no_usable_locality_failure_signal_under_v1_baseline",
        "contiguous": {"correct": contiguous_correct, "exact_accuracy": contiguous_correct / PAIRED_CASES_PER_PROFILE, "malformed": contiguous_malformed},
        "interleaved": {"correct": interleaved_correct, "exact_accuracy": interleaved_correct / PAIRED_CASES_PER_PROFILE, "malformed": interleaved_malformed},
        "paired_delta": (interleaved_correct - contiguous_correct) / PAIRED_CASES_PER_PROFILE,
        "paired_locality_effect": (b - c) / PAIRED_CASES_PER_PROFILE,
        "paired_test": {"b_C_correct_I_incorrect": b, "c_C_incorrect_I_correct": c, "discordant_pairs": b + c, "one_sided_exact_p_value": p_value},
        "transitions": transitions,
    }


def summarize_attempt(records: list[dict[str, Any]], plan: list[dict[str, Any]]) -> dict[str, object]:
    """Recompute all frozen summaries from immutable request records."""
    expected_by_ordinal = {entry["request_ordinal"]: entry for entry in plan}
    observed_by_ordinal = {record.get("request_ordinal"): record for record in records}
    infrastructure_records = [record for record in records if record.get("infrastructure_status") != "complete"]
    complete = len(records) == len(plan) and set(observed_by_ordinal) == set(expected_by_ordinal) and not infrastructure_records
    profiles: dict[str, object] = {}
    if complete:
        for profile in PROFILES:
            records_for_profile = [record for record in records if record["profile"] == profile.identifier]
            profiles[profile.identifier] = _profile_summary(records_for_profile, profile)
    return {
        "attempt_id": ATTEMPT_ID,
        "completed_requests": sum(record.get("infrastructure_status") == "complete" for record in records),
        "expected_requests": len(plan),
        "infrastructure_failure_count": len(infrastructure_records),
        "outcome": "protocol_valid" if complete else "infrastructure_invalid",
        "profiles": profiles,
        "request_order_contract": "level_1_then_level_2; ordinal_ascending; even=C_then_I; odd=I_then_C",
    }


def result_fingerprint(path: Path) -> str:
    """Hash an immutable stored result artifact by physical bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_attempt_directory(run_dir: Path, inventory_root: Path = INVENTORY_ROOT) -> dict[str, object]:
    """Validate stored records and summary solely from retained files and frozen authority."""
    manifest, plan = build_request_plan(inventory_root)
    metadata = load_json(run_dir / "metadata.json")
    if metadata.get("attempt_id") != ATTEMPT_ID or metadata.get("inventory_aggregate_sha256") != manifest["aggregate_inventory_sha256"]:
        raise MeasurementError("attempt metadata does not identify frozen inventory")
    records_path = run_dir / "results.jsonl"
    records = [json.loads(line) for line in records_path.read_text(encoding="utf-8").splitlines() if line]
    for record, expected in zip(records, plan, strict=True):
        for field in ("request_ordinal", "case_id", "pair_id", "profile", "schedule_kind", "prompt_sha256", "inventory_aggregate_sha256"):
            if record.get(field) != expected[field]:
                raise MeasurementError(f"record plan mismatch for {field}: {record.get('request_ordinal')}")
        evaluation = evaluate_raw_output(record.get("raw_output", ""), expected["canonical_answer"])
        if record.get("evaluation") != evaluation:
            raise MeasurementError(f"record evaluator mismatch: {expected['case_id']}")
    recomputed = summarize_attempt(records, plan)
    stored = load_json(run_dir / "summary.json")
    if stored != recomputed:
        raise MeasurementError("stored summary differs from recomputation")
    return recomputed
