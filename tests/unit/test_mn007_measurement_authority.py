"""Static contract tests for MN-007 measurement authority and request order."""
from __future__ import annotations

import copy
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import pytest

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
import mn007_measurement_authority as authority

FROZEN_REQUEST_ORDER_SHA256 = (
    "93d578e5a24903e826f2ad0481a420d219e53be30e2e4a822d9c3fdc0a96b474"
)
FROZEN_AUTHORITY_CORE_SHA256 = (
    "576d501c13bf11efe4c8cbf2e246b2b60c1478b2dacf6a7ae3d7edf7bbddd139"
)
FROZEN_AUTHORITY_FILE_SHA256 = (
    "23d9cac39a023681e3816e02e6d8d317530a369d719a656c15e6752f91edeb23"
)


def request_order() -> list[str]:
    return authority.build_request_order()


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


def test_authority_file_validates_and_is_canonical() -> None:
    loaded = authority.validate_authority_artifact(authority.AUTHORITY_FILE)
    assert loaded["authority_id"] == authority.AUTHORITY_ID
    assert loaded["authority_version"] == authority.AUTHORITY_VERSION
    assert loaded["authority_core_sha256"] == FROZEN_AUTHORITY_CORE_SHA256
    file_bytes = authority.AUTHORITY_FILE.read_bytes()
    assert hashlib.sha256(file_bytes).hexdigest() == FROZEN_AUTHORITY_FILE_SHA256
    assert not file_bytes.startswith(b"\xef\xbb\xbf")
    assert b"\r\n" not in file_bytes
    assert file_bytes.endswith(b"\n")


def test_authority_self_reference_prohibition() -> None:
    core = authority.build_authority_core()
    assert "authority_core_sha256" not in core
    full = authority.build_authority()
    assert "authority_core_sha256" in full
    assert full["authority_core_sha256"] == FROZEN_AUTHORITY_CORE_SHA256


def test_authority_hash_determinism_and_mutation_sensitivity() -> None:
    core = authority.build_authority_core()
    base_hash = materialization.sha256_bytes(materialization.canonical_json_bytes(core))
    assert base_hash == FROZEN_AUTHORITY_CORE_SHA256

    mutated = copy.deepcopy(core)
    mutated["sampling"]["request_payload_schema"]["temperature"] = 0.1
    mut_hash = materialization.sha256_bytes(
        materialization.canonical_json_bytes(mutated)
    )
    assert mut_hash != base_hash

    mutated_runtime = copy.deepcopy(core)
    mutated_runtime["runtime"]["configured_context_size"] = 4096
    mut_runtime_hash = materialization.sha256_bytes(
        materialization.canonical_json_bytes(mutated_runtime)
    )
    assert mut_runtime_hash != base_hash


def test_exact_model_and_executable_fingerprints() -> None:
    core = authority.build_authority_core()
    assert core["model"]["sha256"] == authority.EXPECTED_MODEL_SHA256
    assert core["runtime"]["executable_sha256"] == authority.EXPECTED_EXECUTABLE_SHA256
    assert core["model"]["file"] == "Llama-3.2-3B-Instruct-Q4_K_M.gguf"
    assert core["runtime"]["build"] == "10566"
    assert core["runtime"]["commit"] == "bb4caa754"
    assert core["runtime"]["compiler"] == "MSVC 19.44.35217.0 for x64"


def test_server_command_and_offload_authority() -> None:
    core = authority.build_authority_core()
    cmd = core["runtime"]["server_command"]
    assert "-ngl" not in cmd
    assert "-fa" in cmd and cmd[cmd.index("-fa") + 1] == "on"
    assert "-c" in cmd and cmd[cmd.index("-c") + 1] == "16896"
    assert "-t" in cmd and cmd[cmd.index("-t") + 1] == "12"
    assert "-b" in cmd and cmd[cmd.index("-b") + 1] == "2048"
    assert "-np" in cmd and cmd[cmd.index("-np") + 1] == "1"
    assert "--temp" in cmd and cmd[cmd.index("--temp") + 1] == "0"
    assert "--seed" in cmd and cmd[cmd.index("--seed") + 1] == "42"
    assert "--no-cache-prompt" in cmd
    assert "--no-webui" in cmd
    assert "--metrics" in cmd


def test_sampling_classification_is_exhaustive() -> None:
    core = authority.build_authority_core()
    classification = core["sampling"]["classification"]
    expected_params = {
        "temperature",
        "seed",
        "max_tokens",
        "grammar",
        "messages",
        "chat_template_kwargs",
        "top_k",
        "top_p",
        "min_p",
        "typical_p",
        "repetition_penalty",
        "presence_penalty",
        "frequency_penalty",
        "mirostat",
        "stop",
    }
    assert set(classification) == expected_params
    assert (
        classification["temperature"] == "explicit_request_and_runtime_arg"
    )
    assert classification["seed"] == "explicit_request_and_runtime_arg"
    assert classification["max_tokens"] == "explicit_request_payload"
    assert classification["grammar"] == "explicit_request_payload"


def test_failure_taxonomy_and_no_retry_policy() -> None:
    core = authority.build_authority_core()
    failure = core["failure_semantics"]
    assert failure["state_taxonomy"] == [
        "not_started",
        "sent_unconfirmed",
        "response_received",
        "persisted",
        "evaluated",
        "invalid_ambiguous",
    ]
    assert failure["retry_policy"] == "prohibited_strictly_once_per_case"
    assert (
        failure["sent_unconfirmed_status"] == "measurement_or_design_blocked"
    )
    assert failure["interruption_policy"] == "abort_run_no_retry_fail_closed"
    assert (
        failure["persistence_failure_policy"]
        == "abort_run_do_not_evaluate_fail_closed"
    )
    assert (
        failure["malformed_output_scoring"]
        == "score_zero_point_zero_persisted_as_is"
    )
