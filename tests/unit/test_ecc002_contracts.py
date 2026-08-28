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
    / "ecc-002-confusable-context-retrieval"
    / "scripts"
)
sys.path.insert(0, str(SCRIPTS))

import ecc002


class FakeRuntime:
    @staticmethod
    def count_text(text: str) -> int:
        return len(re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE))

    def count_prompt(self, content: str) -> int:
        return self.count_text(content) + 12


def test_confusable_records_are_deterministic_uniform_and_unique() -> None:
    definition, cases = ecc002.load_definition()
    case, seed = cases[0], definition["case_generation"]["seed"]
    assert ecc002.distractor(case, 17, "A", seed) == ecc002.distractor(case, 17, "A", seed)
    context, _content, _prefix = ecc002.compose(case, 40, seed)
    lines = context.splitlines()[1:]
    assert len(lines) == len(set(lines)) == 81
    assert context.count(case["entity"]) == 1
    assert context.count(case["answer"]) == 1
    assert "TARGET FACT" not in context
    assert all(re.fullmatch(r"Registry entry: Project [A-Za-z]+-[0-9]{4} has access code [A-Z]{2}-[0-9]{4}\.", line) for line in lines)


def test_token_budget_and_evidence_position_are_stable() -> None:
    definition, cases = ecc002.load_definition()
    built = [ecc002.build_case(FakeRuntime(), cases[0], target, definition) for target in (512, 1024, 2048)]
    assert built[1] == ecc002.build_case(FakeRuntime(), cases[0], 1024, definition)
    assert all(0 <= value.requested_input_tokens - value.actual_input_tokens <= 96 for value in built)
    assert all(abs(value.evidence_position_ratio - 0.5) <= 0.05 for value in built)
    assert max(value.evidence_position_ratio for value in built) - min(value.evidence_position_ratio for value in built) < 0.03


def test_context_overflow_is_rejected() -> None:
    definition, cases = ecc002.load_definition()
    invalid = copy.deepcopy(definition)
    invalid["token_budget"]["configured_context_size"] = 100
    with pytest.raises(ecc002.ContractError, match="exceeds context"):
        ecc002.build_case(FakeRuntime(), cases[0], 512, invalid)


@pytest.mark.parametrize(("raw", "passed"), [("AL-8001", True), (" al-8001. ", True), ("AL 8001", False), ("The code is AL-8001", False)])
def test_exact_answer_evaluator(raw: str, passed: bool) -> None:
    assert ecc002.evaluate("AL-8001", raw)[0] is passed


def test_fingerprint_is_canonical_and_sensitive() -> None:
    definition, _ = ecc002.load_definition()
    cases = ecc002.load_json(ecc002.DEFINITION / "cases.json")
    first = ecc002.fingerprint_values(definition, cases)
    reordered = json.loads(json.dumps({key: definition[key] for key in reversed(definition)}))
    assert ecc002.fingerprint_values(reordered, cases) == first
    changed = copy.deepcopy(cases)
    changed["cases"][0]["answer"] = "AL-9001"
    assert ecc002.fingerprint_values(definition, changed) != first


def _curve_records(levels: list[int], passes: list[int]) -> list[dict]:
    return [{"requested_input_tokens": level, "evaluation": {"passed": index < passed_count}, "error": None, "truncated": False, "actual_input_tokens": level - 1, "timing": {"total_ms": float(index + 1)}} for level, passed_count in zip(levels, passes, strict=True) for index in range(20)]


def test_summary_uses_contiguous_thresholds_and_right_censoring() -> None:
    levels = [512, 1024, 2048, 4096]
    degraded = ecc002.summarize("run", _curve_records(levels, [20, 17, 19, 15]), levels, [f"case-{index}" for index in range(20)], True)
    assert degraded["non_monotonic"] is True
    assert degraded["ecc"] == {"ECC95": 512, "ECC90": 512, "ECC80": 2048, "status": "resolved", "right_censored_thresholds": [], "rule": "contiguous tested prefix; no interpolation"}
    bounded = ecc002.summarize("run", _curve_records(levels, [20, 20, 20, 20]), levels, [f"case-{index}" for index in range(20)], True)
    assert bounded["ecc"]["right_censored_thresholds"] == ["ECC95", "ECC90", "ECC80"]
    assert bounded["ecc"]["status"] == "right_censored"
    assert bounded["levels"][0]["runtime"] == {"count": 20, "median_total_ms": 10.5, "min_total_ms": 1.0, "max_total_ms": 20.0}


def test_definition_satisfies_schema() -> None:
    definition, _ = ecc002.load_definition()
    assert ecc002.schema_errors(definition, "experiment-definition.schema.json") == []


def test_offline_validator_rejects_corrupted_evidence(tmp_path: Path) -> None:
    definition, cases = ecc002.load_definition()
    case = cases[0]
    built = ecc002.build_case(FakeRuntime(), case, 512, definition)
    record = {
        **{key: value for key, value in ecc002.built_case_dict(built).items() if key != "content"},
        "configured_context_size": 16896, "output_token_budget": 16,
        "request": {"messages": [{"role": "user", "content": built.content}], "temperature": 0.0, "seed": 42, "max_tokens": 16, "chat_template_kwargs": {}},
        "output": {"raw_text": case["answer"], "normalized_text": ecc002.normalize_answer(case["answer"]), "response": {"choices": [{"message": {"content": case["answer"]}}], "usage": {"prompt_tokens": built.actual_input_tokens}}},
        "evaluation": {"passed": True, "score": 1.0}, "truncated": False, "timing": {"total_ms": 10.0}, "error": None,
    }
    run = tmp_path / "run"
    run.mkdir()
    metadata = {"run_id": "ecc-002-test", "created_at": "2026-08-27T00:00:00+00:00", "experiment": {"id": definition["id"], "version": definition["version"]}, "definition_fingerprint": ecc002.definition_fingerprint(), "repository": {"commit": "1234567", "dirty": False}, "model": {"key": "test", "name": "test", "file": "test.gguf", "size_bytes": 1, "sha256": "0" * 64, "qualified_by": "test"}, "runtime": {"backend": "test", "version": "test", "build": "1", "commit": "abc", "raw_version_output": "test"}, "hardware": {"os": "test", "cpu": "test", "ram_bytes": 1, "gpu": None, "vram_bytes": None, "driver": None, "cuda": None}, "inference": {"temperature": 0.0, "seed": 42, "configured_context_size": 16896, "output_tokens": 16, "threads": 1, "batch_size": 1, "parallel_slots": 1, "flash_attention": False, "prompt_cache": False, "chat_template_kwargs": {}}, "selection": {"context_levels": [512], "case_ids": [case["id"]], "complete_definition_coverage": False}, "command": {"server": [], "runner": []}}
    summary = ecc002.summarize("ecc-002-test", [record], [512], [case["id"]], False)
    ecc002.dump_json(run / "metadata.json", metadata)
    (run / "results.jsonl").write_text(json.dumps(record) + "\n", encoding="utf-8")
    ecc002.dump_json(run / "summary.json", summary)
    assert ecc002.validate_run(run) == summary
    record["context_sha256"] = hashlib.sha256(b"corrupted").hexdigest()
    (run / "results.jsonl").write_text(json.dumps(record) + "\n", encoding="utf-8")
    with pytest.raises(ecc002.ContractError, match="request hash mismatch"):
        ecc002.validate_run(run)
