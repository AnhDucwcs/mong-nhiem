from __future__ import annotations

import copy
import hashlib
import json
import re
import sys
from pathlib import Path

import pytest

SCRIPTS = (
    Path(__file__).resolve().parents[2]
    / "research"
    / "experiments"
    / "prototypes"
    / "mn-003-effective-context-capacity"
    / "experiments"
    / "ecc-001-context-retrieval"
    / "scripts"
)
sys.path.insert(0, str(SCRIPTS))

import ecc001


class FakeRuntime:
    @staticmethod
    def count_text(text: str) -> int:
        return len(re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE))

    def count_prompt(self, content: str) -> int:
        return self.count_text(content) + 12


def test_distractor_and_case_generation_are_deterministic() -> None:
    definition, cases = ecc001.load_definition()
    seed = definition["case_generation"]["seed"]
    first = ecc001.distractor(cases[0]["id"], 17, "A", seed)
    assert first == ecc001.distractor(cases[0]["id"], 17, "A", seed)
    assert cases[0]["answer"] not in first
    assert len(cases) == 20


def test_token_budget_and_evidence_position_are_stable() -> None:
    definition, cases = ecc001.load_definition()
    runtime = FakeRuntime()
    built = [ecc001.build_case(runtime, cases[0], target, definition) for target in (512, 1024, 2048)]
    repeated = ecc001.build_case(runtime, cases[0], 1024, definition)
    assert built[1] == repeated
    assert all(0 <= item.requested_input_tokens - item.actual_input_tokens <= 64 for item in built)
    assert all(abs(item.evidence_position_ratio - 0.5) <= 0.05 for item in built)
    assert max(item.evidence_position_ratio for item in built) - min(item.evidence_position_ratio for item in built) < 0.03


def test_context_overflow_is_rejected() -> None:
    definition, cases = ecc001.load_definition()
    invalid = copy.deepcopy(definition)
    invalid["token_budget"]["configured_context_size"] = 100
    with pytest.raises(ecc001.ContractError, match="exceeds context"):
        ecc001.build_case(FakeRuntime(), cases[0], 512, invalid)


@pytest.mark.parametrize(
    ("raw", "passed"),
    [("AX-4827", True), (" ax-4827. ", True), ("AX 4827", False), ("The code is AX-4827", False)],
)
def test_exact_answer_evaluator(raw: str, passed: bool) -> None:
    assert ecc001.evaluate("AX-4827", raw)[0] is passed


def test_fingerprint_is_canonical_and_sensitive() -> None:
    definition, _cases = ecc001.load_definition()
    inventory = ecc001.load_json(ecc001.DEFINITION / "cases.json")
    first = ecc001.fingerprint_values(definition, inventory)
    reordered = json.loads(json.dumps({key: definition[key] for key in reversed(definition)}))
    assert ecc001.fingerprint_values(reordered, inventory) == first
    changed = copy.deepcopy(inventory)
    changed["cases"][0]["answer"] = "AX-4828"
    assert ecc001.fingerprint_values(definition, changed) != first


def _curve_records(levels: list[int], passes: list[int]) -> list[dict]:
    return [
        {
            "requested_input_tokens": level,
            "evaluation": {"passed": index < passed},
            "error": None,
            "truncated": False,
            "actual_input_tokens": level - 1,
            "timing": {"total_ms": 10.0},
        }
        for level, passed in zip(levels, passes, strict=True)
        for index in range(20)
    ]


def test_summary_uses_contiguous_thresholds_and_flags_non_monotonicity() -> None:
    levels = [512, 1024, 2048, 4096]
    summary = ecc001.summarize(
        "run",
        _curve_records(levels, [20, 17, 19, 15]),
        levels,
        [f"case-{index}" for index in range(20)],
        True,
    )
    assert summary["non_monotonic"] is True
    assert summary["ecc"] == {
        "ECC95": 512,
        "ECC90": 512,
        "ECC80": 2048,
        "status": "resolved",
        "rule": "contiguous tested prefix; no interpolation",
    }


def test_definition_satisfies_schema() -> None:
    definition, _ = ecc001.load_definition()
    assert ecc001.schema_errors(definition, "experiment-definition.schema.json") == []


def test_offline_validator_rejects_corrupted_evidence(tmp_path: Path) -> None:
    definition, cases = ecc001.load_definition()
    case = cases[0]
    content = "Context records:\nTARGET FACT: " + ecc001.relevant_fact(case) + "\n\nQuestion:\n" + ecc001.question(case)
    record = {
        "case_id": case["id"],
        "requested_input_tokens": 512,
        "actual_input_tokens": 480,
        "content_tokens": 468,
        "prompt_overhead_tokens": 12,
        "configured_context_size": 16896,
        "output_token_budget": 16,
        "context_tokens": 30,
        "evidence_start_token": 14,
        "evidence_position_ratio": 0.466667,
        "distractor_pairs": 0,
        "relevant_fact": ecc001.relevant_fact(case),
        "expected_answer": case["answer"],
        "context_sha256": hashlib.sha256(content.encode()).hexdigest(),
        "request": {
            "messages": [{"role": "user", "content": content}],
            "temperature": 0.0,
            "seed": 42,
            "max_tokens": 16,
            "chat_template_kwargs": {},
        },
        "output": {
            "raw_text": case["answer"],
            "normalized_text": ecc001.normalize_answer(case["answer"]),
            "response": {
                "choices": [{"message": {"content": case["answer"]}}],
                "usage": {"prompt_tokens": 480},
            },
        },
        "evaluation": {"passed": True, "score": 1.0},
        "truncated": False,
        "timing": {"total_ms": 10.0},
        "error": None,
    }
    run = tmp_path / "run"
    run.mkdir()
    metadata = {
        "run_id": "ecc-001-test",
        "created_at": "2026-08-27T00:00:00+00:00",
        "experiment": {"id": definition["id"], "version": definition["version"]},
        "definition_fingerprint": ecc001.definition_fingerprint(),
        "repository": {"commit": "1234567", "dirty": False},
        "model": {"key": "test", "name": "test", "file": "test.gguf", "size_bytes": 1, "sha256": "0" * 64, "qualified_by": "test"},
        "runtime": {"backend": "test", "version": "test", "build": "1", "commit": "abc", "raw_version_output": "test"},
        "hardware": {"os": "test", "cpu": "test", "ram_bytes": 1, "gpu": None, "vram_bytes": None, "driver": None, "cuda": None},
        "inference": {"temperature": 0.0, "seed": 42, "configured_context_size": 16896, "output_tokens": 16, "threads": 1, "batch_size": 1, "parallel_slots": 1, "flash_attention": False, "prompt_cache": False, "chat_template_kwargs": {}},
        "selection": {"context_levels": [512], "case_ids": [case["id"]], "complete_definition_coverage": False},
        "command": {"server": [], "runner": []},
    }
    summary = ecc001.summarize("ecc-001-test", [record], [512], [case["id"]], False)
    ecc001.dump_json(run / "metadata.json", metadata)
    (run / "results.jsonl").write_text(json.dumps(record) + "\n", encoding="utf-8")
    ecc001.dump_json(run / "summary.json", summary)
    assert ecc001.validate_run(run) == summary

    metadata["selection"]["complete_definition_coverage"] = True
    ecc001.dump_json(run / "metadata.json", metadata)
    with pytest.raises(ecc001.ContractError, match="complete-coverage flag"):
        ecc001.validate_run(run)

    metadata["selection"]["complete_definition_coverage"] = False
    ecc001.dump_json(run / "metadata.json", metadata)
    summary["total_results"] = 2
    ecc001.dump_json(run / "summary.json", summary)
    with pytest.raises(ecc001.ContractError, match="stored summary is not reproducible"):
        ecc001.validate_run(run)
