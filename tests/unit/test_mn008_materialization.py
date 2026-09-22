"""Unit tests for MN-008 Gate C Phase 1 materialization and preflight validation."""
from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = (
    REPO_ROOT
    / "research"
    / "experiments"
    / "prototypes"
    / "mn-008-external-state-management"
    / "scripts"
)
sys.path.insert(0, str(SCRIPTS_DIR))

import mn008_materialization as mat


@pytest.fixture
def corpus_data():
    sem, pub, eva = mat.build_entire_corpus()
    return sem, pub, eva


def test_corpus_size_and_identifiers(corpus_data):
    sem, pub, eva = corpus_data
    assert len(sem) == 24
    assert len(pub) == 24
    assert len(eva) == 24

    for i in range(24):
        expected_id = f"mn008-case-{i + 1:04d}"
        assert sem[i]["case_id"] == expected_id
        assert pub[i]["case_id"] == expected_id
        assert eva[i]["case_id"] == expected_id
        assert sem[i]["case_ordinal"] == i
        assert pub[i]["case_ordinal"] == i
        assert eva[i]["case_ordinal"] == i


def test_latin_square_balance_and_symmetry(corpus_data):
    sem, _, eva = corpus_data

    # 1. State pairs balance: each binary combination must appear in exactly 6 cases
    pair_counts = Counter(tuple(case["target_pair"]) for case in sem)
    assert len(pair_counts) == 4
    for pair in mat.STATE_PAIRS:
        assert pair_counts[pair] == 6, f"State pair {pair} count is {pair_counts[pair]}, expected 6"

    # 2. Target action balance: each action token must be the oracle target in exactly 6 cases
    action_counts = Counter(case["target_action"] for case in eva)
    assert len(action_counts) == 4
    for action in mat.ACTION_VOCABULARY:
        assert action_counts[action] == 6, f"Action {action} count is {action_counts[action]}, expected 6"

    # 3. Shift symmetry: shift = case_ordinal % 4
    for i, case in enumerate(sem):
        assert case["shift"] == i % 4
        assert case["wave"] == i // 4
        mapping = mat.get_counterbalanced_mapping(i)
        target_pair = tuple(case["target_pair"])
        assert mapping[target_pair] == case["target_action"]


def test_host_state_engine_and_anti_tautology(corpus_data):
    sem, _, _ = corpus_data

    for case in sem:
        events = case["event_stream"]
        assert len(events) == 15

        # Verify host replay
        replayed = mat.host_replay(events, mat.ACTIVE_ENTITIES)
        assert replayed["E1"] == case["target_pair"][0]
        assert replayed["E2"] == case["target_pair"][1]

        # Verify scoped snapshot
        snapshot = mat.host_scoped_snapshot(events, mat.QUERIED_ENTITIES)
        assert snapshot == f"E1={case['target_pair'][0]}; E2={case['target_pair'][1]}"
        assert case["host_snapshot"] == snapshot

        # Anti-tautology: snapshot contains ONLY raw entity states, no action tokens or rules
        for action in mat.ACTION_VOCABULARY:
            assert action not in snapshot, f"Action token {action} leaked into snapshot: {snapshot}"
        assert "IF" not in snapshot
        assert "THEN" not in snapshot
        assert "ACTION" not in snapshot


def test_rule_table_canonical_order(corpus_data):
    _, pub, _ = corpus_data

    for case in pub:
        arm_c_prompt = case["arm_c_stage2_prompt"]
        lines = [line.strip() for line in arm_c_prompt.splitlines() if line.strip().startswith("- IF")]
        assert len(lines) == 4

        # Invariant: Rules must appear in the exact canonical order of STATE_PAIRS
        expected_prefixes = [
            f"- IF E1={s1} AND E2={s2} THEN" for s1, s2 in mat.STATE_PAIRS
        ]
        for line, prefix in zip(lines, expected_prefixes, strict=True):
            assert line.startswith(prefix), f"Line {line} did not match prefix {prefix}"


def test_arm_c_prompt_token_budget_hard_gate(corpus_data):
    """Hard Preflight Gate: every Arm C Stage 2 prompt must measure strictly < 100 tokens."""
    _, pub, _ = corpus_data

    llama_tokenize = Path(r"D:\Materials\llama.cpp\build\bin\Release\llama-tokenize.exe")
    model = REPO_ROOT / "artifacts" / "models" / "mn-002" / "Llama-3.2-3B-Instruct-Q4_K_M.gguf"

    if not (llama_tokenize.exists() and model.exists()):
        pytest.skip("llama-tokenize.exe or model GGUF not found on host")

    for case in pub:
        prompt_text = case["arm_c_stage2_prompt"]

        # Raw prompt tokens
        cmd_raw = [
            str(llama_tokenize),
            "-m",
            str(model),
            "-p",
            prompt_text,
            "--show-count",
            "--no-bos",
        ]
        res_raw = subprocess.run(cmd_raw, capture_output=True, text=True, check=True)
        count_raw = None
        for line in res_raw.stdout.splitlines():
            if "Total number of tokens:" in line:
                count_raw = int(line.split(":")[-1].strip())
        assert count_raw is not None
        assert (
            count_raw < mat.MAX_ARM_C_PROMPT_TOKENS
        ), f"Case {case['case_id']} raw tokens {count_raw} >= {mat.MAX_ARM_C_PROMPT_TOKENS}"

        # Chat-templated tokens (user header + prompt + assistant header)
        templated = (
            f"<|start_header_id|>user<|end_header_id|>\n\n"
            f"{prompt_text}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
        )
        cmd_tmpl = [
            str(llama_tokenize),
            "-m",
            str(model),
            "-p",
            templated,
            "--show-count",
            "--no-bos",
        ]
        res_tmpl = subprocess.run(cmd_tmpl, capture_output=True, text=True, check=True)
        count_tmpl = None
        for line in res_tmpl.stdout.splitlines():
            if "Total number of tokens:" in line:
                count_tmpl = int(line.split(":")[-1].strip())
        assert count_tmpl is not None
        assert (
            count_tmpl < mat.MAX_ARM_C_PROMPT_TOKENS
        ), f"Case {case['case_id']} templated tokens {count_tmpl} >= {mat.MAX_ARM_C_PROMPT_TOKENS}"


def test_deterministic_reproducibility_and_manifest_validation(tmp_path):
    # Materialize to temp dir
    manifest_tmp = mat.materialize_corpus(tmp_path)
    result_tmp = mat.validate_corpus(tmp_path)
    assert result_tmp["status"] == "VALID"

    # Materialize to second temp dir and assert exact byte equality
    tmp_path_2 = tmp_path / "second"
    mat.materialize_corpus(tmp_path_2)

    for filename in mat.ARTIFACT_FILENAMES:
        b1 = (tmp_path / filename).read_bytes()
        b2 = (tmp_path_2 / filename).read_bytes()
        assert b1 == b2, f"Byte divergence in {filename}"
        assert b1.endswith(b"\n"), f"File {filename} does not end with LF"
        assert b"\r\n" not in b1, f"File {filename} contains CRLF"


def test_production_corpus_validation():
    # Validate canonical definition files at DEFINITION_ROOT
    result = mat.validate_corpus(mat.DEFINITION_ROOT)
    assert result["status"] == "VALID"
    assert result["case_count"] == 24
