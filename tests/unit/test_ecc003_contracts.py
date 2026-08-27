from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "research" / "experiments" / "prototypes" / "mn-003-effective-context-capacity" / "experiments" / "ecc-003-evidence-position-sensitivity" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import ecc003


class FakeRuntime:
    @staticmethod
    def count_text(text: str) -> int:
        return len(re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE))

    def count_prompt(self, content: str) -> int:
        return self.count_text(content) + 12


def test_middle_reuses_ecc002_generator_sequence() -> None:
    definition, cases = ecc003.load_definition()
    case, seed = cases[0], definition["case_generation"]["seed"]
    _context, content, _prefix, _metadata = ecc003.compose(case, 9, "middle", seed)
    _old_context, old_content, _old_prefix = ecc003.ecc002.compose(ecc003.generator_case(case), 9, seed)
    assert content == old_content


def test_position_builder_is_deterministic_and_within_tolerance() -> None:
    definition, cases = ecc003.load_definition()
    runtime = FakeRuntime()
    levels = definition["independent_variables"]["requested_input_tokens"]["levels"]
    for position in ("early", "middle", "late"):
        built = [ecc003.build_case(runtime, cases[0], target, position, definition) for target in levels]
        assert all(0 <= item.requested_input_tokens - item.actual_input_tokens <= 160 for item in built)
        target = ecc003.position_spec(definition, position)["target_ratio"]
        assert all(abs(item.evidence_position_ratio - target) <= 0.05 for item in built)
        assert built[1] == ecc003.build_case(runtime, cases[0], levels[1], position, definition)


def test_target_is_unmarked_and_failure_classifier_identifies_distractor() -> None:
    definition, cases = ecc003.load_definition()
    case = cases[0]
    context, _content, _prefix, metadata = ecc003.compose(case, 5, "late", definition["case_generation"]["seed"])
    assert "TARGET FACT" not in context
    selected = metadata[0]
    failure = ecc003.classify_failure(case, selected["answer"], 5, "late", definition)
    assert failure == {"kind": "distractor_code", "selected_distractor": selected}
    assert ecc003.classify_failure(case, "not a code", 5, "late", definition) == {"kind": "other_output"}


def test_context_overflow_is_rejected() -> None:
    definition, cases = ecc003.load_definition()
    invalid = copy.deepcopy(definition)
    invalid["token_budget"]["configured_context_size"] = 100
    with pytest.raises(ecc003.ContractError, match="exceeds context"):
        ecc003.build_case(FakeRuntime(), cases[0], 512, "middle", invalid)


@pytest.mark.parametrize(("raw", "passed"), [("AL-8001", True), (" al-8001. ", True), ("AL 8001", False), ("Code AL-8001", False)])
def test_exact_answer_evaluator(raw: str, passed: bool) -> None:
    assert ecc003.ecc002.evaluate("AL-8001", raw)[0] is passed


def test_fingerprint_is_canonical_and_sensitive() -> None:
    definition, _ = ecc003.load_definition()
    cases = ecc003.load_json(ecc003.DEFINITION / "cases.json")
    first = ecc003.fingerprint_values(definition, cases)
    assert ecc003.fingerprint_values(dict(reversed(list(definition.items()))), cases) == first
    changed = copy.deepcopy(cases)
    changed["cases"][0]["generator_case_id"] = "ecc002-999"
    assert ecc003.fingerprint_values(definition, changed) != first


def _records(levels: list[int]) -> list[dict]:
    rows = []
    passes = {"early": [20, 20], "middle": [18, 16], "late": [20, 19]}
    for position, scores in passes.items():
        for level, score in zip(levels, scores, strict=True):
            for index in range(20):
                passed = index < score
                rows.append({"case_id": f"case-{index}", "requested_input_tokens": level, "requested_evidence_position": position, "evaluation": {"passed": passed}, "error": None, "truncated": False, "actual_input_tokens": level - 1, "timing": {"total_ms": float(index + 1)}, "failure": None if passed else {"kind": "other_output"}})
    return rows


def test_summary_derives_position_metrics_and_contiguous_ecc() -> None:
    definition, _ = ecc003.load_definition()
    levels = [512, 1024]
    summary = ecc003.summarize("run", _records(levels), levels, ["early", "middle", "late"], [f"case-{index}" for index in range(20)], True, definition)
    assert summary["position_metrics"][1] == {"requested_input_tokens": 1024, "accuracy_by_position": {"early": 1.0, "middle": 0.8, "late": 0.95}, "position_gap": 0.19999999999999996, "middle_penalty": 0.17499999999999993}
    middle = next(item for item in summary["positions"] if item["position"] == "middle")
    assert middle["ecc"]["ECC95"] == 512
    assert summary["failure_analysis"]["other_output_failures"] == 7


def test_definition_satisfies_schema() -> None:
    definition, _ = ecc003.load_definition()
    assert ecc003.schema_errors(definition, "experiment-definition.schema.json") == []


def test_offline_validator_rejects_corrupted_generator_evidence(tmp_path: Path) -> None:
    definition, cases = ecc003.load_definition()
    case = cases[0]
    built = ecc003.build_case(FakeRuntime(), case, 512, "middle", definition)
    record = {**{key: value for key, value in ecc003.built_case_dict(built).items() if key != "content"}, "configured_context_size": 16896, "output_token_budget": 16, "request": {"messages": [{"role": "user", "content": built.content}], "temperature": 0.0, "seed": 42, "max_tokens": 16, "chat_template_kwargs": {}}, "output": {"raw_text": case["answer"], "normalized_text": ecc003.ecc002.normalize_answer(case["answer"]), "response": {"choices": [{"message": {"content": case["answer"]}}], "usage": {"prompt_tokens": built.actual_input_tokens}}}, "evaluation": {"passed": True, "score": 1.0}, "failure": None, "truncated": False, "timing": {"total_ms": 10.0}, "error": None}
    run = tmp_path / "run"
    run.mkdir()
    metadata = {"run_id": "ecc-003-test", "created_at": "2026-08-27T00:00:00+00:00", "experiment": {"id": definition["id"], "version": definition["version"]}, "definition_fingerprint": ecc003.definition_fingerprint(), "repository": {"commit": "1234567", "dirty": False}, "model": {"key": "test", "name": "test", "file": "test.gguf", "size_bytes": 1, "sha256": "0" * 64, "qualified_by": "test"}, "runtime": {"backend": "test", "version": "test", "build": "1", "commit": "abc", "raw_version_output": "test"}, "hardware": {"os": "test", "cpu": "test", "ram_bytes": 1, "gpu": None, "vram_bytes": None, "driver": None, "cuda": None}, "inference": {"temperature": 0.0, "seed": 42, "configured_context_size": 16896, "output_tokens": 16, "threads": 1, "batch_size": 1, "parallel_slots": 1, "flash_attention": False, "prompt_cache": False, "chat_template_kwargs": {}}, "selection": {"context_levels": [512], "evidence_positions": ["middle"], "case_ids": [case["id"]], "complete_definition_coverage": False}, "command": {"server": [], "runner": []}}
    summary = ecc003.summarize("ecc-003-test", [record], [512], ["middle"], [case["id"]], False, definition)
    ecc003.dump_json(run / "metadata.json", metadata)
    (run / "results.jsonl").write_text(json.dumps(record) + "\n", encoding="utf-8")
    ecc003.dump_json(run / "summary.json", summary)
    assert ecc003.validate_run(run) == summary
    record["distractor_records"] = []
    (run / "results.jsonl").write_text(json.dumps(record) + "\n", encoding="utf-8")
    with pytest.raises(ecc003.ContractError, match="generator output"):
        ecc003.validate_run(run)
